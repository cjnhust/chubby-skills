const { buildRuntime } = require("./codex_review_common.cjs");

async function run({ github, context, core, trustedMaintainers }) {
  const runtime = buildRuntime({
    github,
    context,
    core,
    trustedMaintainers,
  });

  let pr = null;
  if (context.eventName === "pull_request_review") {
    const review = context.payload.review;
    const incomingPr = context.payload.pull_request;
    if (!review || !incomingPr || !runtime.actorCanTriggerEvaluation(review.user?.login || "")) {
      core.info("Ignoring unrelated review event.");
      return;
    }
    if (
      runtime.codexActors.has(review.user?.login || "") &&
      !runtime.reviewedCommitMatchesHead(review.commit_id || "", incomingPr.head?.sha || "")
    ) {
      core.info(
        `Ignoring Codex review for commit ${review.commit_id || "<missing>"} because current head is ${incomingPr.head?.sha || "<missing>"}`,
      );
      return;
    }
    pr = incomingPr;
  } else if (context.eventName === "pull_request_target" || context.eventName === "pull_request") {
    pr = context.payload.pull_request;
  }

  if (!pr || pr.draft || pr.base?.ref !== "main" || pr.head?.repo?.full_name !== `${context.repo.owner}/${context.repo.repo}`) {
    core.info("Skipping draft, external, or non-main PR.");
    return;
  }

  const codexReview = await runtime.currentHeadCodexReview(pr.number, pr.head.sha);
  if (!codexReview) {
    core.info("Current head does not yet have a Codex review; not arming auto-merge.");
    return;
  }
  if (!codexReview.acceptable) {
    core.info(`${codexReview.description}; not arming auto-merge.`);
    return;
  }

  const trustedSubmission = await runtime.currentHeadIsTrustedSubmission(pr);
  const trustedApproval = trustedSubmission
    ? true
    : await runtime.currentHeadHasTrustedApproval(pr.number, pr.head.sha);
  if (!trustedApproval) {
    core.info("Current head is not trusted and lacks trusted approval; not arming auto-merge.");
    return;
  }

  await runtime.enableWithRetry(pr);
}

module.exports = {
  run,
};
