function buildTrustedActors(owner, trustedMaintainers) {
  return new Set(
    [owner, ...(trustedMaintainers || "").split(/[\s,]+/)]
      .map((value) => value.trim())
      .filter(Boolean),
  );
}

function buildRuntime({ github, context, core, trustedMaintainers, gateContext }) {
  const owner = context.repo.owner;
  const repo = context.repo.repo;
  const repoFullName = `${owner}/${repo}`;
  const codexActors = new Set([
    "chatgpt-codex-connector[bot]",
    "chatgpt-codex-connector",
  ]);
  const cleanBodyPatterns = [
    /didn't find any major issues/i,
    /did not find any major issues/i,
    /\bbreezy\b/i,
  ];
  const trustedActors = buildTrustedActors(owner, trustedMaintainers);

  async function setStatus(sha, state, description, targetUrl) {
    if (!gateContext) {
      throw new Error("gateContext is required to set commit statuses");
    }
    await github.rest.repos.createCommitStatus({
      owner,
      repo,
      sha,
      state,
      context: gateContext,
      description,
      target_url: targetUrl,
    });
  }

  function isSameRepoPullRequest(pr) {
    return pr?.head?.repo?.full_name === repoFullName;
  }

  function bodyLooksClean(body) {
    return cleanBodyPatterns.some((pattern) => pattern.test(body || ""));
  }

  function reviewedCommitMatchesHead(reviewedCommit, headSha) {
    if (!reviewedCommit || !headSha) {
      return false;
    }
    const normalizedReviewed = reviewedCommit.toLowerCase();
    const normalizedHead = headSha.toLowerCase();
    return (
      normalizedReviewed === normalizedHead ||
      normalizedHead.startsWith(normalizedReviewed) ||
      normalizedReviewed.startsWith(normalizedHead)
    );
  }

  function actorIsRelevantForGate(login) {
    return codexActors.has(login || "") || trustedActors.has(login || "");
  }

  function actorCanTriggerEvaluation(login) {
    return codexActors.has(login || "") || trustedActors.has(login || "");
  }

  async function listPullRequestReviews(pullNumber) {
    return github.paginate(github.rest.pulls.listReviews, {
      owner,
      repo,
      pull_number: pullNumber,
      per_page: 100,
    });
  }

  async function listPullRequestReviewComments(pullNumber) {
    return github.paginate(github.rest.pulls.listReviewComments, {
      owner,
      repo,
      pull_number: pullNumber,
      per_page: 100,
    });
  }

  async function listReviewThreads(pullNumber) {
    const threads = [];
    let cursor = null;
    while (true) {
      const result = await github.graphql(
        `
          query($owner: String!, $repo: String!, $pullNumber: Int!, $cursor: String) {
            repository(owner: $owner, name: $repo) {
              pullRequest(number: $pullNumber) {
                reviewThreads(first: 100, after: $cursor) {
                  nodes {
                    isResolved
                    comments(first: 100) {
                      nodes {
                        author {
                          login
                        }
                        pullRequestReview {
                          fullDatabaseId
                          state
                          url
                          commit {
                            oid
                          }
                        }
                      }
                    }
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                }
              }
            }
          }
        `,
        { owner, repo, pullNumber, cursor },
      );

      const connection = result.repository.pullRequest.reviewThreads;
      threads.push(...connection.nodes);
      if (!connection.pageInfo.hasNextPage) {
        return threads;
      }
      cursor = connection.pageInfo.endCursor;
    }
  }

  async function listPullRequestCommits(pullNumber) {
    return github.paginate(github.rest.pulls.listCommits, {
      owner,
      repo,
      pull_number: pullNumber,
      per_page: 100,
    });
  }

  async function currentHeadHasTrustedApproval(pullNumber, headSha) {
    const reviews = await listPullRequestReviews(pullNumber);
    const latestTrustedReviewByActor = new Map();
    for (const review of reviews) {
      const login = review.user?.login || "";
      if (!trustedActors.has(login)) {
        continue;
      }
      if (!reviewedCommitMatchesHead(review.commit_id || "", headSha)) {
        continue;
      }
      latestTrustedReviewByActor.set(login, review);
    }
    return [...latestTrustedReviewByActor.values()].some(
      (review) => String(review.state || "").toUpperCase() === "APPROVED",
    );
  }

  async function currentHeadIsTrustedSubmission(pr) {
    if (!trustedActors.has(pr.user?.login || "")) {
      return false;
    }
    const commits = await listPullRequestCommits(pr.number);
    return commits.every((commit) => {
      const candidateLogins = [commit.author?.login, commit.committer?.login].filter(Boolean);
      return candidateLogins.length > 0 && candidateLogins.every((login) => trustedActors.has(login));
    });
  }

  async function currentHeadCodexReview(pullNumber, headSha) {
    const reviewComments = await listPullRequestReviewComments(pullNumber);
    const reviewCommentCounts = new Map();
    for (const comment of reviewComments) {
      const reviewId = comment.pull_request_review_id;
      if (!reviewId) {
        continue;
      }
      reviewCommentCounts.set(reviewId, (reviewCommentCounts.get(reviewId) || 0) + 1);
    }

    const reviews = (await listPullRequestReviews(pullNumber)).slice().reverse();
    const currentHeadReviews = [];
    for (const review of reviews) {
      const login = review.user?.login || "";
      if (!codexActors.has(login)) {
        continue;
      }
      if (!reviewedCommitMatchesHead(review.commit_id || "", headSha)) {
        continue;
      }
      currentHeadReviews.push(review);
    }

    if (currentHeadReviews.length === 0) {
      return null;
    }

    const activeCurrentHeadReviewIds = new Set(
      currentHeadReviews
        .filter((review) => String(review.state || "").toUpperCase() !== "DISMISSED")
        .map((review) => String(review.id)),
    );
    const unresolvedThread = (await listReviewThreads(pullNumber)).find((thread) => {
      if (thread.isResolved) {
        return false;
      }
      return thread.comments.nodes.some((comment) => {
        const login = comment.author?.login || "";
        const reviewId = String(comment.pullRequestReview?.fullDatabaseId || "");
        const reviewedCommit = comment.pullRequestReview?.commit?.oid || "";
        return (
          codexActors.has(login) &&
          activeCurrentHeadReviewIds.has(reviewId) &&
          reviewedCommitMatchesHead(reviewedCommit, headSha)
        );
      });
    });
    if (unresolvedThread) {
      const targetUrl =
        unresolvedThread.comments.nodes.find((comment) => {
          const login = comment.author?.login || "";
          const reviewId = String(comment.pullRequestReview?.fullDatabaseId || "");
          const reviewedCommit = comment.pullRequestReview?.commit?.oid || "";
          return (
            codexActors.has(login) &&
            activeCurrentHeadReviewIds.has(reviewId) &&
            reviewedCommitMatchesHead(reviewedCommit, headSha)
          );
        })?.pullRequestReview?.url || `https://github.com/${repoFullName}/pull/${pullNumber}`;
      return {
        acceptable: false,
        description: "Current-head Codex review still has unresolved inline findings",
        targetUrl,
      };
    }

    for (const review of currentHeadReviews) {
      const state = String(review.state || "").toUpperCase();
      if (state === "DISMISSED") {
        continue;
      }
      if (state === "CHANGES_REQUESTED") {
        return {
          acceptable: false,
          description: "Current-head Codex review requested changes",
          targetUrl: review.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
        };
      }

      const hasInlineComments = (reviewCommentCounts.get(review.id) || 0) > 0;
      if (hasInlineComments) {
        return {
          acceptable: false,
          description: "Current-head Codex review still has inline findings; rerun review after resolving them",
          targetUrl: review.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
        };
      }
      if (state === "APPROVED") {
        return {
          acceptable: true,
          targetUrl: review.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
        };
      }
      if (!bodyLooksClean(review.body || "")) {
        return {
          acceptable: false,
          description: "Current-head Codex review still has summary-only findings",
          targetUrl: review.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
        };
      }

      return {
        acceptable: true,
        targetUrl: review.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
      };
    }

    return null;
  }

  async function enableWithRetry(pr) {
    for (let attempt = 1; attempt <= 6; attempt += 1) {
      try {
        await github.graphql(
          `
            mutation EnableAutoMerge($pullRequestId: ID!) {
              enablePullRequestAutoMerge(
                input: {
                  pullRequestId: $pullRequestId
                  mergeMethod: SQUASH
                }
              ) {
                pullRequest {
                  number
                  autoMergeRequest {
                    enabledAt
                  }
                }
              }
            }
          `,
          { pullRequestId: pr.node_id },
        );
        core.info(`Enabled auto-merge for PR #${pr.number}`);
        return;
      } catch (error) {
        const message = String(error.message || error);
        if (message.includes("is already enabled for auto-merge")) {
          core.info(`Auto-merge already enabled for PR #${pr.number}`);
          return;
        }
        if (message.includes("unstable status") && attempt < 6) {
          core.info(`PR #${pr.number} still unstable; retrying in 5s (attempt ${attempt}/6)`);
          await new Promise((resolve) => setTimeout(resolve, 5000));
          continue;
        }
        throw error;
      }
    }
  }

  return {
    repoFullName,
    codexActors,
    trustedActors,
    setStatus,
    isSameRepoPullRequest,
    reviewedCommitMatchesHead,
    actorIsRelevantForGate,
    actorCanTriggerEvaluation,
    currentHeadHasTrustedApproval,
    currentHeadIsTrustedSubmission,
    currentHeadCodexReview,
    enableWithRetry,
  };
}

module.exports = {
  buildRuntime,
};
