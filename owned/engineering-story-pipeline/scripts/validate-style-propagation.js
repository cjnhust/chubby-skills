#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const {
  parseArgs,
  parseSelectionBundle,
  readText,
  resolveAbsolute,
} = require("./utils");

function usage() {
  console.error(
    "Usage: node validate-style-propagation.js --workspace <workspace-dir> [--bundle <file>] [--strict] [--json]"
  );
  process.exit(1);
}

function exists(filePath) {
  try {
    fs.accessSync(filePath);
    return true;
  } catch {
    return false;
  }
}

function walk(dirPath) {
  const results = [];
  if (!exists(dirPath)) {
    return results;
  }

  for (const entry of fs.readdirSync(dirPath, { withFileTypes: true })) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      results.push(...walk(fullPath));
      continue;
    }
    results.push(fullPath);
  }

  return results;
}

function addCheck(checks, level, name, detail) {
  checks.push({ level, name, detail });
}

function summarize(checks) {
  const counts = { pass: 0, warn: 0, fail: 0 };
  for (const check of checks) {
    counts[check.level] += 1;
  }
  return counts;
}

function normalized(value) {
  return String(value || "").trim().toLowerCase();
}

function expectedSkillsForProfile(profile) {
  switch (profile) {
    case "launch-keynote":
    case "launch-narrative":
      return ["baoyu-slide-deck", "baoyu-article-illustrator", "baoyu-cover-image"];
    case "lively-explainer":
      return ["baoyu-slide-deck", "baoyu-article-illustrator", "baoyu-cover-image"];
    case "editorial-analytic":
      return ["baoyu-slide-deck", "baoyu-article-illustrator", "baoyu-infographic"];
    case "comic-teaching":
      return ["baoyu-comic"];
    case "serious-engineering":
    default:
      return ["baoyu-slide-deck", "baoyu-article-illustrator", "baoyu-cover-image"];
  }
}

function collectArtifacts(workspace) {
  const files = walk(workspace);
  return {
    coverPrompts: files.filter((filePath) => filePath.endsWith(path.join("prompts", "cover.md"))),
    infographicPrompts: files.filter((filePath) => filePath.endsWith(path.join("prompts", "infographic.md"))),
    slideOutlines: files.filter(
      (filePath) =>
        path.basename(filePath) === "outline.md" &&
        filePath.includes(`${path.sep}slide-deck${path.sep}`)
    ),
    slidePrompts: files.filter(
      (filePath) =>
        filePath.includes(`${path.sep}prompts${path.sep}`) &&
        /^\d{2}-slide-.*\.md$/i.test(path.basename(filePath))
    ),
    articlePrompts: files.filter(
      (filePath) =>
        filePath.includes(`${path.sep}prompts${path.sep}`) &&
        /^\d{2}-(?!slide-).+\.md$/i.test(path.basename(filePath))
    ),
  };
}

function requireContentMarkers(checks, filePath, markers, label) {
  const content = readText(filePath);
  const missing = markers.filter((marker) => !content.includes(marker));
  if (missing.length > 0) {
    addCheck(
      checks,
      "fail",
      `${label} markers`,
      `${filePath} is missing required markers: ${missing.join(", ")}`
    );
    return content;
  }
  addCheck(checks, "pass", `${label} markers`, `${filePath} contains required style markers.`);
  return content;
}

function extractHexColors(text) {
  return Array.from(
    new Set((text.match(/#[0-9A-Fa-f]{3,8}/g) || []).map((item) => item.toLowerCase()))
  );
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const workspace = resolveAbsolute(args.workspace);
  const bundlePath =
    resolveAbsolute(args.bundle) ||
    (workspace ? path.join(workspace, "notes", "selection-bundle.md") : null);
  const strict = Boolean(args.strict);
  const json = Boolean(args.json);

  if (args.help) {
    usage();
  }

  if (!workspace || !bundlePath) {
    usage();
  }

  const checks = [];

  if (!exists(workspace)) {
    addCheck(checks, "fail", "workspace", `Workspace does not exist: ${workspace}`);
    finish(workspace, bundlePath, checks, json, strict);
    return;
  }
  addCheck(checks, "pass", "workspace", `Workspace exists: ${workspace}`);

  if (!exists(bundlePath)) {
    addCheck(checks, "fail", "selection bundle", `Bundle file not found: ${bundlePath}`);
    finish(workspace, bundlePath, checks, json, strict);
    return;
  }

  const bundle = parseSelectionBundle(readText(bundlePath));
  const profile = bundle.visual_profile || bundle.selected_theme || null;
  const styleOverride =
    bundle.visual_style_override &&
    bundle.visual_style_override !== "null" &&
    bundle.visual_style_override !== "false"
      ? bundle.visual_style_override
      : null;
  const confirmed = normalized(bundle.confirmed) === "true";

  addCheck(checks, profile ? "pass" : "fail", "visual profile", profile ? `Profile: ${profile}` : "Missing visual_profile/selected_theme in selection bundle.");
  addCheck(checks, "pass", "style override", styleOverride ? `Explicit style override present.` : "No explicit style override recorded.");

  if (confirmed && profile) {
    for (const skill of expectedSkillsForProfile(profile)) {
      const configPath = path.join(workspace, ".baoyu-skills", skill, "EXTEND.md");
      addCheck(
        checks,
        exists(configPath) ? "pass" : "fail",
        `${skill} config`,
        exists(configPath)
          ? `Found workspace config: ${configPath}`
          : `Missing expected workspace config: ${configPath}`
      );
    }
  } else {
    addCheck(
      checks,
      "warn",
      "workspace config completeness",
      "Selection bundle is not confirmed or has no profile; config completeness check is advisory only."
    );
  }

  const artifacts = collectArtifacts(workspace);
  const artifactTexts = [];

  if (artifacts.coverPrompts.length === 0) {
    addCheck(checks, "warn", "cover prompt", "No saved prompts/cover.md found.");
  }
  for (const filePath of artifacts.coverPrompts) {
    artifactTexts.push(
      requireContentMarkers(checks, filePath, ["Palette:", "Rendering:", "Color scheme:"], "cover prompt")
    );
  }

  if (artifacts.slideOutlines.length === 0) {
    addCheck(checks, "warn", "slide outline", "No slide-deck outline.md found.");
  }
  for (const filePath of artifacts.slideOutlines) {
    artifactTexts.push(
      requireContentMarkers(checks, filePath, ["STYLE INSTRUCTIONS"], "slide outline")
    );
  }

  if (artifacts.infographicPrompts.length === 0) {
    addCheck(checks, "warn", "infographic prompt", "No saved prompts/infographic.md found.");
  }
  for (const filePath of artifacts.infographicPrompts) {
    artifactTexts.push(
      requireContentMarkers(checks, filePath, ["Style", "Layout"], "infographic prompt")
    );
  }

  if (artifacts.articlePrompts.length === 0) {
    addCheck(checks, "warn", "article prompts", "No saved article-illustrator prompt files found.");
  }
  for (const filePath of artifacts.articlePrompts) {
    artifactTexts.push(
      requireContentMarkers(checks, filePath, ["STYLE", "COLORS"], "article prompt")
    );
  }

  if (styleOverride) {
    const overrideColors = extractHexColors(styleOverride);
    const combinedArtifacts = artifactTexts.join("\n").toLowerCase();
    if (overrideColors.length === 0) {
      addCheck(
        checks,
        "warn",
        "override color verification",
        "Explicit style override does not contain machine-verifiable hex colors. Semantic verification remains process-based."
      );
    } else {
      const missingColors = overrideColors.filter((color) => !combinedArtifacts.includes(color));
      addCheck(
        checks,
        missingColors.length === 0 ? "pass" : "fail",
        "override color propagation",
        missingColors.length === 0
          ? `All override colors were found in saved artifacts: ${overrideColors.join(", ")}`
          : `Override colors missing from saved artifacts: ${missingColors.join(", ")}`
      );
    }
  }

  finish(workspace, bundlePath, checks, json, strict);
}

function finish(workspace, bundlePath, checks, json, strict) {
  const counts = summarize(checks);
  const hasFailures = counts.fail > 0;
  const hasWarnings = counts.warn > 0;

  if (json) {
    process.stdout.write(
      JSON.stringify(
        {
          workspace,
          bundle: bundlePath,
          summary: counts,
          checks,
        },
        null,
        2
      ) + "\n"
    );
  } else {
    const lines = [
      `Workspace: ${workspace}`,
      `Bundle: ${bundlePath}`,
      `Summary: pass=${counts.pass} warn=${counts.warn} fail=${counts.fail}`,
      "Checks:",
      ...checks.map((check) => `- [${check.level.toUpperCase()}] ${check.name}: ${check.detail}`),
    ];
    process.stdout.write(lines.join("\n") + "\n");
  }

  if (hasFailures || (strict && hasWarnings)) {
    process.exit(2);
  }
}

main();
