#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const {
  parseArgs,
  readText,
  resolveAbsolute,
  writeText,
} = require("./utils");

function usage() {
  console.error("Usage: node finalize-report.js --workspace <dir> [--draft <path>] [--output <path>]");
  process.exit(1);
}

const FINAL_VISUAL_STATES = new Set([
  "approved-inline-mermaid",
  "approved-rendered",
  "skipped",
]);

function assertNoAbsoluteFilesystemImageLinks(text) {
  const matches = [...text.matchAll(/!\[[^\]]*\]\((\/[^)\s]+)\)/g)].map((m) => m[1]);
  const offenders = matches.filter((target) => target.startsWith("/"));
  if (offenders.length > 0) {
    throw new Error(
      `draft contains absolute filesystem image links; use report-relative paths instead (${[...new Set(offenders)].slice(0, 3).join(", ")})`
    );
  }
}

function updateFlowClosure(text) {
  const thesisStatusMatch = text.match(/^- thesis_status: .*$/m);
  const thesisStatusLine = thesisStatusMatch ? thesisStatusMatch[0] : "- thesis_status: completed";
  const deckStatusMatch = text.match(/^- deck_status: .*$/m);
  const deckStatusLine = deckStatusMatch ? deckStatusMatch[0] : "- deck_status: not-started";

  const completedMatch = text.match(
    /## Completed In This Pass\s*\n([\s\S]*?)(?=\n## Deferred|\n## Waiting On User|\n## Next Action|$)/m
  );
  const completedBullets = completedMatch
    ? completedMatch[1]
        .split(/\r?\n/)
        .map((line) => line.trimEnd())
        .filter((line) => /^- /.test(line))
    : [];

  const dedupedCompleted = [...new Set(completedBullets)];
  if (!dedupedCompleted.includes("- exported final report to `exports/report-final.md`")) {
    dedupedCompleted.push("- exported final report to `exports/report-final.md`");
  }

  return [
    "# Flow Closure",
    "",
    "- status: completed",
    thesisStatusLine.replace(/: .*/, ": completed"),
    "- article_status: completed",
    "- visual_status: integrated",
    deckStatusLine,
    "- export_status: completed",
    "",
    "## Completed In This Pass",
    "",
    ...dedupedCompleted,
    "",
    "## Deferred",
    "",
    "- local runtime validation / benchmark",
    "",
    "## Waiting On User",
    "",
    "- none",
    "",
    "## Next Action",
    "",
    "- Final report exported to `exports/report-final.md`; next optional step is local validation / benchmark if needed.",
    "",
  ].join("\n");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const workspace = resolveAbsolute(args.workspace);
  if (!workspace) {
    usage();
  }

  const draftPath = resolveAbsolute(args.draft) || path.join(workspace, "drafts/report.md");
  const outputPath = resolveAbsolute(args.output) || path.join(workspace, "exports/report-final.md");
  const diagramPath = path.join(workspace, "notes/diagram-structures.md");
  const factCheckPath = path.join(workspace, "notes/fact-check.md");
  const reportThesisPath = path.join(workspace, "notes/report-thesis.md");
  const selectionBundlePath = path.join(workspace, "notes/selection-bundle.md");
  const sourceBriefPath = path.join(workspace, "source/source.md");
  const codeVerificationPath = path.join(workspace, "notes/code-verification.md");
  const visualInventoryPath = path.join(workspace, "notes/visual-inventory.md");
  const flowClosurePath = path.join(workspace, "notes/flow-closure.md");

  const draft = readText(draftPath);

  assertNoAbsoluteFilesystemImageLinks(draft);

  if (draft.includes("[!visual-placeholder]")) {
    throw new Error("draft still contains visual placeholder blocks; resolve them before finalizing");
  }

  if (draft.includes("```mermaid") && !fs.existsSync(diagramPath)) {
    throw new Error("draft contains Mermaid diagrams but notes/diagram-structures.md is missing");
  }

  if (!fs.existsSync(factCheckPath)) {
    throw new Error("notes/fact-check.md is missing");
  }

  if (!fs.existsSync(reportThesisPath)) {
    throw new Error("notes/report-thesis.md is missing");
  }

  const reportThesis = readText(reportThesisPath);
  for (const requiredPattern of [
    /^- report_mode:\s*(?!TODO\b).+/m,
    /^- target_reader:\s*(?!TODO\b).+/m,
    /^- core_question:\s*(?!TODO\b).+/m,
    /^- single_sentence_thesis:\s*(?!TODO\b).+/m,
  ]) {
    if (!requiredPattern.test(reportThesis)) {
      throw new Error("report thesis gate not passed; complete notes/report-thesis.md before finalizing");
    }
  }

  const factCheck = readText(factCheckPath);
  if (!/^- overall_result: pass$/m.test(factCheck)) {
    throw new Error("fact-check gate not passed; update notes/fact-check.md before finalizing");
  }

  const sourceBrief = fs.existsSync(sourceBriefPath) ? readText(sourceBriefPath) : "";
  const codeVerificationRequired =
    /^- code_verification_required:\s*(true|required|yes)$/m.test(sourceBrief) ||
    /^- source_availability:\s*(open-source|source-available)$/m.test(sourceBrief);

  if (codeVerificationRequired) {
    if (!fs.existsSync(codeVerificationPath)) {
      throw new Error("source-available project requires notes/code-verification.md before finalizing");
    }
    const codeVerification = readText(codeVerificationPath);
    if (!/^- overall_result: pass$/m.test(codeVerification)) {
      throw new Error("code-verification gate not passed; update notes/code-verification.md before finalizing");
    }
  }

  if (fs.existsSync(visualInventoryPath)) {
    const visualInventory = readText(visualInventoryPath);
    const statuses = [...visualInventory.matchAll(/status:\s*([a-z-]+)\b/g)].map((match) => match[1]);
    const invalidStatuses = statuses.filter((status) => !FINAL_VISUAL_STATES.has(status));
    if (invalidStatuses.length > 0) {
      throw new Error(
        `visual inventory still contains unapproved items (${[...new Set(invalidStatuses)].join(", ")}); require explicit user confirmation before finalizing`
      );
    }

    const approvedCount = statuses.filter((status) => status.startsWith("approved-")).length;
    const skippedOnly = statuses.length > 0 && approvedCount === 0 && statuses.every((status) => status === "skipped");
    const selectionBundle = fs.existsSync(selectionBundlePath) ? readText(selectionBundlePath) : "";
    const textOnlyByUser = /^- visual_strategy:\s*text-only-by-user$/m.test(selectionBundle);
    const textOnlyEvidenceMatch = selectionBundle.match(/^- text_only_evidence:\s*(.+)$/m);
    const textOnlyEvidence = textOnlyEvidenceMatch ? textOnlyEvidenceMatch[1].trim() : "";
    const hasTextOnlyEvidence =
      textOnlyEvidence.length > 0 &&
      textOnlyEvidence !== "null" &&
      textOnlyEvidence !== "TODO" &&
      textOnlyEvidence !== '""' &&
      textOnlyEvidence !== "''";

    if (textOnlyByUser && !hasTextOnlyEvidence) {
      throw new Error(
        "selection bundle uses text-only-by-user without text_only_evidence; record the user's explicit text-only request before finalizing"
      );
    }
    if (skippedOnly && !textOnlyByUser) {
      throw new Error(
        "all planned visuals are marked skipped while visual strategy is not text-only-by-user; keep at least one approved visual or explicitly switch the bundle to text-only-by-user"
      );
    }
  }

  writeText(outputPath, draft);

  if (fs.existsSync(flowClosurePath)) {
    writeText(flowClosurePath, updateFlowClosure(readText(flowClosurePath)));
  }

  console.log(outputPath);
}

main();
