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

const SOURCE_CAPTURE_STATUSES = new Set([
  "artifacted",
  "failed",
  "not-required",
]);

const APPROVED_RENDER_LEAFS = new Set([
  "baoyu-image-gen",
  "baoyu-article-illustrator",
  "baoyu-infographic",
  "baoyu-cover-image",
  "baoyu-xhs-images",
  "baoyu-comic",
  "baoyu-slide-deck",
]);

const VISUAL_COUNT_DECISION_SOURCES = new Set(["user", "planner"]);

function isMeaningfulValue(value) {
  if (value == null) return false;
  const normalized = String(value).trim();
  return (
    normalized.length > 0 &&
    normalized !== "TODO" &&
    normalized !== "null" &&
    normalized !== "pending" &&
    normalized !== "not-required" &&
    normalized !== '""' &&
    normalized !== "''"
  );
}

function parseIndentedBlocks(text, startRegex) {
  const lines = text.split(/\r?\n/);
  const blocks = [];
  let current = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (startRegex.test(trimmed)) {
      if (current) blocks.push(current);
      current = { __header: trimmed };
      continue;
    }

    if (!current) continue;
    const fieldMatch = trimmed.match(/^- ([a-zA-Z0-9_-]+):\s*(.*)$/);
    if (fieldMatch) {
      current[fieldMatch[1]] = fieldMatch[2];
    }
  }

  if (current) blocks.push(current);
  return blocks;
}

function splitPathList(value) {
  return String(value)
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function assertSourceScopeAndCaptureGates(workspace, sourceBriefPath, sourceCatalogPath) {
  const sourceBrief = fs.existsSync(sourceBriefPath) ? readText(sourceBriefPath) : "";
  if (!/^- scope_status:\s*confirmed$/m.test(sourceBrief)) {
    throw new Error("scope gate not passed; update source/source.md with - scope_status: confirmed before finalizing");
  }

  if (!fs.existsSync(sourceCatalogPath)) return;
  const sourceCatalog = readText(sourceCatalogPath);
  const entries = parseIndentedBlocks(sourceCatalog, /^- S\d+\b/);
  const urlEntries = entries.filter((entry) => /^https?:\/\//.test(entry.url || ""));

  for (const entry of urlEntries) {
    const captureStatus = String(entry.capture_status || "").trim();

    if (!SOURCE_CAPTURE_STATUSES.has(captureStatus)) {
      throw new Error(
        `source capture gate not passed for ${entry.__header}; record capture_status in source/source-catalog.md before finalizing`
      );
    }

    if (captureStatus === "artifacted") {
      const hasArtifacts = [entry.raw_artifact, entry.normalized_artifact].some(isMeaningfulValue);
      if (!hasArtifacts) {
        throw new Error(
          `source capture gate not passed for ${entry.__header}; artifacted URLs must record raw_artifact or normalized_artifact`
        );
      }
    }

    if (captureStatus === "failed" && !isMeaningfulValue(entry.capture_failure)) {
      throw new Error(
        `source capture gate not passed for ${entry.__header}; failed URL capture must record capture_failure`
      );
    }
  }
}

function assertApprovedVisualProvenance(workspace, visualInventoryPath, options = {}) {
  if (!fs.existsSync(visualInventoryPath)) return;
  const visualInventory = readText(visualInventoryPath);
  const entries = parseIndentedBlocks(visualInventory, /^- id:\s*.+$/);
  const planningStatusMatch = visualInventory.match(/^- planning_status:\s*(.+)$/m);
  const imageCountMatch = visualInventory.match(/^- image_count:\s*(.+)$/m);
  const decisionSourceMatch = visualInventory.match(/^- count_decision_source:\s*(.+)$/m);
  const countRationaleMatch = visualInventory.match(/^- count_rationale:\s*(.+)$/m);
  const planningStatus = planningStatusMatch ? planningStatusMatch[1].trim() : "";
  const imageCountRaw = imageCountMatch ? imageCountMatch[1].trim() : "";
  const decisionSource = decisionSourceMatch ? decisionSourceMatch[1].trim() : "";
  const countRationale = countRationaleMatch ? countRationaleMatch[1].trim() : "";
  const skipPlanningGate = options.skipPlanningGate === true;

  if (!skipPlanningGate) {
    if (planningStatus !== "confirmed") {
      throw new Error("visual planning gate not passed; set - planning_status: confirmed in notes/visual-inventory.md before finalizing");
    }
    if (!/^\d+$/.test(imageCountRaw) || Number(imageCountRaw) <= 0) {
      throw new Error("visual planning gate not passed; set a positive integer image_count in notes/visual-inventory.md before finalizing");
    }
    if (!VISUAL_COUNT_DECISION_SOURCES.has(decisionSource)) {
      throw new Error("visual planning gate not passed; set count_decision_source to user or planner in notes/visual-inventory.md before finalizing");
    }
    if (!isMeaningfulValue(countRationale)) {
      throw new Error("visual planning gate not passed; record count_rationale in notes/visual-inventory.md before finalizing");
    }
    if (Number(imageCountRaw) !== entries.length) {
      throw new Error(
        `visual planning gate not passed; image_count (${imageCountRaw}) must match the number of planned visuals (${entries.length})`
      );
    }
  }

  for (const entry of entries) {
    if (entry.status === "approved-inline-mermaid") {
      if (entry.approval_source !== "user") {
        throw new Error(
          `${entry.__header} is approved-inline-mermaid without approval_source: user; do not self-upgrade visuals before export`
        );
      }
    }

    if (entry.status === "approved-rendered") {
      if (!APPROVED_RENDER_LEAFS.has(entry.render_via || "")) {
        throw new Error(
          `${entry.__header} uses unsupported render_via for approved-rendered (${entry.render_via || "missing"}); only leaf visual skills may satisfy rendered approval`
        );
      }
      if (!isMeaningfulValue(entry.rendered_path)) {
        throw new Error(`${entry.__header} is approved-rendered without rendered_path`);
      }
      if (!isMeaningfulValue(entry.prompt_artifacts)) {
        throw new Error(`${entry.__header} is approved-rendered without prompt_artifacts`);
      }
      if (entry.approval_source !== "user") {
        throw new Error(`${entry.__header} is approved-rendered without approval_source: user`);
      }

      const renderedPath = path.resolve(workspace, entry.rendered_path);
      if (!fs.existsSync(renderedPath)) {
        throw new Error(`${entry.__header} rendered_path does not exist (${entry.rendered_path})`);
      }

      for (const artifactPath of splitPathList(entry.prompt_artifacts)) {
        const resolvedArtifact = path.resolve(workspace, artifactPath);
        if (!fs.existsSync(resolvedArtifact)) {
          throw new Error(`${entry.__header} prompt_artifact does not exist (${artifactPath})`);
        }
      }
    }
  }
}

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

  const selectionBundlePath = path.join(workspace, "notes/selection-bundle.md");
  const selectionBundle = fs.existsSync(selectionBundlePath) ? readText(selectionBundlePath) : "";
  const annotatedDraftPath = path.join(workspace, "drafts/report-annotated.md");
  const prefersAnnotatedDraft =
    /^- report_edition:\s*annotated$/m.test(selectionBundle) && fs.existsSync(annotatedDraftPath);

  const draftPath =
    resolveAbsolute(args.draft) ||
    (prefersAnnotatedDraft ? annotatedDraftPath : path.join(workspace, "drafts/report.md"));
  const outputPath = resolveAbsolute(args.output) || path.join(workspace, "exports/report-final.md");
  const diagramPath = path.join(workspace, "notes/diagram-structures.md");
  const factCheckPath = path.join(workspace, "notes/fact-check.md");
  const reportThesisPath = path.join(workspace, "notes/report-thesis.md");
  const sourceBriefPath = path.join(workspace, "source/source.md");
  const sourceCatalogPath = path.join(workspace, "source/source-catalog.md");
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

  assertSourceScopeAndCaptureGates(workspace, sourceBriefPath, sourceCatalogPath);

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

    assertApprovedVisualProvenance(workspace, visualInventoryPath, {
      skipPlanningGate: textOnlyByUser && skippedOnly,
    });
  } else {
    assertApprovedVisualProvenance(workspace, visualInventoryPath);
  }

  writeText(outputPath, draft);

  if (fs.existsSync(flowClosurePath)) {
    writeText(flowClosurePath, updateFlowClosure(readText(flowClosurePath)));
  }

  console.log(outputPath);
}

main();
