#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const {
  copyFile,
  ensureDir,
  maybeWriteText,
  parseArgs,
  readText,
  resolveAbsolute,
  slugify,
  writeText,
} = require("./utils");

function usage() {
  console.error("Usage: node init-workspace.js --source <file.md> [--workspace <dir>] [--force]");
  process.exit(1);
}

function renderSelectionBundleTemplate() {
  return [
    "# Selection Bundle",
    "",
    "- selected_theme: serious-engineering",
    "- writing_posture: serious-engineering",
    "- visual_profile: serious-engineering",
    "- confirmed: false",
    "",
    "## Why This Fits",
    "",
    "- TODO",
    "",
    "## Alternatives Considered",
    "",
    "- launch-narrative",
    "  - TODO",
    "- editorial-analytic",
    "  - TODO",
    "",
    "## Notes",
    "",
    "- TODO",
    "",
  ].join("\n");
}

function renderVisualInventoryTemplate() {
  return [
    "# Visual Inventory",
    "",
    "## Existing Assets",
    "",
    "- path: TODO",
    "- evidence_role: TODO",
    "- action: reuse-as-is | reference-for-redraw | structure-only | source-only",
    "",
    "## Planned Visuals",
    "",
    "- section: TODO",
    "- visual_type: none | flowchart | framework | comparison | infographic | cover | slide-only",
    "- source_anchor: TODO",
    "- status: pending",
    "",
  ].join("\n");
}

function renderFlowClosureTemplate() {
  return [
    "# Flow Closure",
    "",
    "- status: paused-for-review",
    "- article_status: not-started",
    "- visual_status: not-started",
    "- deck_status: not-started",
    "- export_status: not-started",
    "",
    "## Completed In This Pass",
    "",
    "- TODO",
    "",
    "## Deferred",
    "",
    "- TODO",
    "",
    "## Waiting On User",
    "",
    "- TODO",
    "",
    "## Next Action",
    "",
    "- TODO",
    "",
  ].join("\n");
}

function renderSourceContractTemplate(sourcePath) {
  return [
    "# Source Contract",
    "",
    `- source_file: ${sourcePath || "TODO"}`,
    "- source_title: TODO",
    "",
    "## Positioning",
    "",
    "- TODO",
    "",
    "## Explicit Question List",
    "",
    "- TODO",
    "",
    "## Top-Level Sections",
    "",
    "- TODO",
    "",
    "## Major Second-Level Sections",
    "",
    "- TODO",
    "",
    "## Figure Anchors",
    "",
    "- TODO",
    "",
    "## Must-Keep Claims",
    "",
    "- TODO",
    "",
    "## Presentation Flex",
    "",
    "- heading wording may be normalized without changing meaning",
    "- prose may become lists or tables inside the same review boundary",
    "",
  ].join("\n");
}

function renderSourceFidelityTemplate() {
  return [
    "# Source Fidelity Check",
    "",
    "- overall_result: pending",
    "",
    "## Summary",
    "",
    "- TODO",
    "",
  ].join("\n");
}

function deriveWorkspace(sourcePath) {
  const basename = path.basename(sourcePath, path.extname(sourcePath));
  const slug = slugify(basename);
  return path.join(path.dirname(sourcePath), `${slug}-workspace`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const force = Boolean(args.force);
  const sourcePath = resolveAbsolute(args.source);
  const workspace = resolveAbsolute(args.workspace) || (sourcePath ? deriveWorkspace(sourcePath) : null);

  if (!workspace) {
    usage();
  }

  const created = [];
  const skipped = [];
  const dirs = [
    workspace,
    path.join(workspace, "source"),
    path.join(workspace, "drafts"),
    path.join(workspace, "notes"),
    path.join(workspace, ".baoyu-skills"),
    path.join(workspace, "prompts"),
    path.join(workspace, "illustrations"),
    path.join(workspace, "comic"),
    path.join(workspace, "cover-image"),
    path.join(workspace, "slide-deck"),
    path.join(workspace, "exports"),
  ];

  for (const dir of dirs) {
    ensureDir(dir);
  }

  const noteWrites = [
    [path.join(workspace, "notes", "selection-bundle.md"), renderSelectionBundleTemplate()],
    [path.join(workspace, "notes", "visual-inventory.md"), renderVisualInventoryTemplate()],
    [path.join(workspace, "notes", "flow-closure.md"), renderFlowClosureTemplate()],
    [path.join(workspace, "notes", "source-contract.md"), renderSourceContractTemplate(sourcePath)],
    [path.join(workspace, "notes", "source-fidelity-check.md"), renderSourceFidelityTemplate()],
  ];

  for (const [target, content] of noteWrites) {
    const result = maybeWriteText(target, content, { force });
    (result.action === "skipped" ? skipped : created).push(`${result.action}: ${target}`);
  }

  if (sourcePath) {
    const sourceTarget = path.join(workspace, "source", "source.md");
    const sourceCopy = copyFile(sourcePath, sourceTarget, { force });
    (sourceCopy.action === "skipped" ? skipped : created).push(`${sourceCopy.action}: ${sourceTarget}`);

    const draftTarget = path.join(workspace, "drafts", "article.md");
    const draftExisted = fs.existsSync(draftTarget);
    if (!draftExisted || force) {
      writeText(draftTarget, readText(sourcePath));
      created.push(`${draftExisted ? "updated" : "created"}: ${draftTarget}`);
    } else {
      skipped.push(`skipped: ${draftTarget}`);
    }
  } else {
    const draftTarget = path.join(workspace, "drafts", "article.md");
    if (!fs.existsSync(draftTarget)) {
      writeText(draftTarget, "# Draft Article\n");
      created.push(`created: ${draftTarget}`);
    }
  }

  console.log([
    `Workspace: ${workspace}`,
    created.length ? `Created or updated:\n- ${created.join("\n- ")}` : "Created or updated:\n- none",
    skipped.length ? `Skipped:\n- ${skipped.join("\n- ")}` : "Skipped:\n- none",
  ].join("\n\n"));
}

main();
