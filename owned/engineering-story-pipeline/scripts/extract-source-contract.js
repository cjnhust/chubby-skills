#!/usr/bin/env node

const path = require("path");
const {
  extractExplicitQuestionList,
  extractMarkdownStructure,
  extractMustKeepClaims,
  firstParagraph,
  parseArgs,
  readText,
  resolveAbsolute,
  writeText,
} = require("./utils");

function usage() {
  console.error("Usage: node extract-source-contract.js --workspace <workspace-dir> [--source <file>] [--output <file>]");
  process.exit(1);
}

function renderContract(sourcePath, structure) {
  const questions = extractExplicitQuestionList(structure.lines);
  const mustKeepClaims = extractMustKeepClaims(structure);
  const figureAnchors = [];

  for (const section of structure.sections) {
    if (section.mermaidCount > 0) {
      figureAnchors.push(`- ${section.heading} :: mermaid :: count ${section.mermaidCount}`);
    }

    if (section.placeholderCount > 0) {
      figureAnchors.push(`- ${section.heading} :: placeholder :: count ${section.placeholderCount}`);
    }

    for (const image of section.images) {
      figureAnchors.push(`- ${section.heading} :: image :: ${image.value}`);
    }
  }

  const topSections = structure.sections.map((section) => `- ${section.heading} :: line ${section.line}`);
  const majorSections = structure.sections
    .filter((section) => section.subheadings.length > 0)
    .map((section) => {
      const subheadingText = section.subheadings.map((item) => item.heading).join(" | ");
      return `- ${section.heading} :: ${subheadingText}`;
    });

  return [
    "# Source Contract",
    "",
    `- source_file: ${sourcePath}`,
    `- source_title: ${structure.title || "UNKNOWN"}`,
    `- extracted_at: ${new Date().toISOString()}`,
    "",
    "## Positioning",
    "",
    `- ${firstParagraph(structure.lines) || "TODO"}`,
    "",
    "## Explicit Question List",
    "",
    ...(questions.length ? questions.map((item) => `- ${item}`) : ["- none detected"]),
    "",
    "## Top-Level Sections",
    "",
    ...topSections,
    "",
    "## Major Second-Level Sections",
    "",
    ...(majorSections.length ? majorSections : ["- none detected"]),
    "",
    "## Figure Anchors",
    "",
    ...(figureAnchors.length ? figureAnchors : ["- none detected"]),
    "",
    "## Must-Keep Claims",
    "",
    ...(mustKeepClaims.length ? mustKeepClaims.map((item) => `- ${item}`) : ["- none detected"]),
    "",
    "## Presentation Flex",
    "",
    "- heading wording may be normalized without changing meaning",
    "- prose may become lists or tables inside the same review boundary",
    "- nearby paragraphs may be split or merged locally if the same review boundary is preserved",
    "- adjacent Mermaid placeholders may be added near an existing image slot",
    "",
  ].join("\n");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const workspace = resolveAbsolute(args.workspace);
  const sourcePath =
    resolveAbsolute(args.source) ||
    (workspace ? path.join(workspace, "source", "source.md") : null);
  const outputPath =
    resolveAbsolute(args.output) ||
    (workspace ? path.join(workspace, "notes", "source-contract.md") : null);

  if (!sourcePath || !outputPath) {
    usage();
  }

  const structure = extractMarkdownStructure(readText(sourcePath));
  const rendered = renderContract(sourcePath, structure);
  writeText(outputPath, rendered);
  console.log(`Wrote ${outputPath}`);
}

main();
