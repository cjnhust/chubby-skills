const { buildRuntime } = require("./codex_review_common.cjs");

async function run({ github, context, core, trustedMaintainers, validationOnly = false }) {
  const runtime = buildRuntime({
    github,
    context,
    core,
    trustedMaintainers,
    gateContext: "codex-review-gate",
    validationOnly,
  });

  async function evaluateGate(pr, fallbackTargetUrl) {
    const headSha = pr.head.sha;
    const codexReview = await runtime.currentHeadCodexReview(pr.number, headSha);
    if (!codexReview) {
      await runtime.setStatus(
        headSha,
        "pending",
        "Waiting for current-head Codex review",
        pr.html_url,
      );
      core.info(`Set codex-review-gate=pending on ${headSha} because no current-head Codex review exists yet`);
      return;
    }

    if (!codexReview.acceptable) {
      await runtime.setStatus(
        headSha,
        "failure",
        codexReview.description,
        codexReview.targetUrl || pr.html_url,
      );
      core.info(`Set codex-review-gate=failure on ${headSha} because ${codexReview.description}`);
      return;
    }

    await runtime.setStatus(
      headSha,
      "success",
      "Current head has a Codex review",
      codexReview.targetUrl || fallbackTargetUrl || pr.html_url,
    );
    core.info(`Set codex-review-gate=success on ${headSha}`);
  }

  if (context.eventName === "pull_request_target" || context.eventName === "pull_request") {
    const pr = context.payload.pull_request;
    if (!pr || pr.draft || !runtime.isSameRepoPullRequest(pr)) {
      core.info("Skipping gate evaluation for draft or external PR.");
      return;
    }
    await evaluateGate(pr, pr.html_url);
    return;
  }

  if (context.eventName === "pull_request_review") {
    const review = context.payload.review;
    const pr = context.payload.pull_request;
    if (!review || !pr || !runtime.isSameRepoPullRequest(pr) || !runtime.actorIsRelevantForGate(review.user?.login || "")) {
      core.info("Ignoring unrelated pull_request_review event.");
      return;
    }
    if (
      runtime.codexActors.has(review.user?.login || "") &&
      !runtime.reviewedCommitMatchesHead(review.commit_id || "", pr.head.sha)
    ) {
      core.info(
        `Ignoring Codex review for commit ${review.commit_id || "<missing>"} because current head is ${pr.head.sha}`,
      );
      return;
    }
    await evaluateGate(pr, review.html_url || pr.html_url);
  }
}

module.exports = {
  run,
};
