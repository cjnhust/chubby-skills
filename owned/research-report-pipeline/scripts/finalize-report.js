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

function updateFlowClosure(text) {
  let updated = text
    .replace(/^- status: .*$/m, "- status: completed")
    .replace(/^- article_status: .*$/m, "- article_status: completed")
    .replace(/^- visual_status: .*$/m, "- visual_status: integrated")
    .replace(/^- export_status: .*$/m, "- export_status: completed");

  updated = updated.replace(
    /## Deferred[\s\S]*?(?=\n## Waiting On User|\n## Next Action|$)/m,
    [
      "## Deferred",
      "",
      "- local runtime validation / benchmark",
      "",
    ].join("\n")
  );

  updated = updated.replace(
    /## Waiting On User[\s\S]*?(?=\n## Next Action|$)/m,
    [
      "## Waiting On User",
      "",
      "- none",
      "",
    ].join("\n")
  );

  updated = updated.replace(
    /## Next Action[\s\S]*$/m,
    [
      "## Next Action",
      "",
      "- Final report exported to `exports/report-final.md`; next optional step is local validation / benchmark if needed.",
      "",
    ].join("\n")
  );

  if (!updated.includes("exported final report")) {
    updated = updated.replace(
      /## Completed In This Pass\s*\n([\s\S]*?)(?=\n## Deferred|\n## Waiting On User|\n## Next Action|$)/m,
      (match, sectionBody) =>
        [
          "## Completed In This Pass",
          "",
          sectionBody.trimEnd(),
          "- exported final report to `exports/report-final.md`",
          "",
        ].join("\n")
    );
  }

  return updated;
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
  const sourceBriefPath = path.join(workspace, "source/source.md");
  const codeVerificationPath = path.join(workspace, "notes/code-verification.md");
  const visualInventoryPath = path.join(workspace, "notes/visual-inventory.md");
  const flowClosurePath = path.join(workspace, "notes/flow-closure.md");

  const draft = readText(draftPath);

  if (draft.includes("[!visual-placeholder]")) {
    throw new Error("draft still contains visual placeholder blocks; resolve them before finalizing");
  }

  if (draft.includes("```mermaid") && !fs.existsSync(diagramPath)) {
    throw new Error("draft contains Mermaid diagrams but notes/diagram-structures.md is missing");
  }

  if (!fs.existsSync(factCheckPath)) {
    throw new Error("notes/fact-check.md is missing");
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
  }

  writeText(outputPath, draft);

  if (fs.existsSync(flowClosurePath)) {
    writeText(flowClosurePath, updateFlowClosure(readText(flowClosurePath)));
  }

  console.log(outputPath);
}

main();
