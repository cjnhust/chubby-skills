function buildTrustedActors(owner, trustedMaintainers) {
  return new Set(
    [owner, ...(trustedMaintainers || "").split(/[\s,]+/)]
      .map((value) => value.trim())
      .filter(Boolean),
  );
}

function buildRuntime({ github, context, core, trustedMaintainers, gateContext, validationOnly = false }) {
  const owner = context.repo.owner;
  const repo = context.repo.repo;
  const repoFullName = `${owner}/${repo}`;
  const codexActors = new Set([
    "chatgpt-codex-connector[bot]",
    "chatgpt-codex-connector",
  ]);
  const trustedActors = buildTrustedActors(owner, trustedMaintainers);

  async function setStatus(sha, state, description, targetUrl) {
    if (!gateContext) {
      throw new Error("gateContext is required to set commit statuses");
    }
    if (validationOnly) {
      core.info(
        `[validation] Would set ${gateContext}=${state} on ${sha}: ${description} (${targetUrl || "no target url"})`,
      );
      return;
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

  async function currentHeadCodexReview(pullNumber, headSha) {
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

    const latestCurrentHeadReview = currentHeadReviews[0];
    const latestCurrentHeadReviewState = String(latestCurrentHeadReview.state || "").toUpperCase();
    if (latestCurrentHeadReviewState === "DISMISSED") {
      return {
        acceptable: false,
        description: "Latest current-head Codex review was dismissed; rerun review on the current head",
        targetUrl: latestCurrentHeadReview.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
      };
    }
    if (latestCurrentHeadReviewState === "CHANGES_REQUESTED") {
      return {
        acceptable: false,
        description: "Latest current-head Codex review requested changes",
        targetUrl: latestCurrentHeadReview.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
      };
    }
    return {
      acceptable: true,
      targetUrl: latestCurrentHeadReview.html_url || `https://github.com/${repoFullName}/pull/${pullNumber}`,
    };
  }

  async function enableWithRetry(pr) {
    if (validationOnly) {
      core.info(`[validation] Would enable auto-merge for PR #${pr.number}`);
      return;
    }
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
    currentHeadCodexReview,
    enableWithRetry,
  };
}

module.exports = {
  buildRuntime,
};
