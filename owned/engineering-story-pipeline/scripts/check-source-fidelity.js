#!/usr/bin/env node

const path = require("path");
const {
  extractCodeLikeTokens,
  extractExplicitQuestionList,
  extractMarkdownStructure,
  headingSimilarity,
  parseArgs,
  parseContractMarkdown,
  readText,
  resolveAbsolute,
  writeText,
} = require("./utils");

const HEADING_THRESHOLD = 0.42;

function usage() {
  console.error("Usage: node check-source-fidelity.js --workspace <workspace-dir> [--contract <file>] [--draft <file>] [--output <file>]");
  process.exit(1);
}

function normalizeResultLevel(warnings, failures) {
  if (failures.length > 0) {
    return "fail";
  }
  if (warnings.length > 0) {
    return "pass with noted deltas";
  }
  return "pass";
}

function bestHeadingMatches(contractHeadings, draftHeadings) {
  const mappings = [];
  for (const contractHeading of contractHeadings) {
    let best = null;
    for (const draftHeading of draftHeadings) {
      const score = headingSimilarity(contractHeading, draftHeading);
      if (!best || score > best.score) {
        best = { contractHeading, draftHeading, score };
      }
    }
    mappings.push(best || { contractHeading, draftHeading: null, score: 0 });
  }
  return mappings;
}

function buildDraftTargets(structure) {
  const targets = [];
  for (const section of structure.sections) {
    targets.push({
      key: `top:${section.heading}`,
      type: "top",
      heading: section.heading,
      parentHeading: null,
      scoreLabel: section.heading,
      section,
    });

    for (const subheading of section.subheadings) {
      targets.push({
        key: `sub:${section.heading}:${subheading.heading}`,
        type: "sub",
        heading: subheading.heading,
        parentHeading: section.heading,
        scoreLabel: `${section.heading} > ${subheading.heading}`,
        section: subheading,
      });
    }
  }
  return targets;
}

function bestTargetMatches(contractHeadings, draftTargets) {
  return contractHeadings.map((contractHeading) => {
    let best = null;
    for (const target of draftTargets) {
      const score = headingSimilarity(contractHeading, target.heading);
      if (!best || score > best.score) {
        best = {
          contractHeading,
          draftHeading: target.heading,
          score,
          type: target.type,
          parentHeading: target.parentHeading,
          key: target.key,
          target,
        };
      }
    }
    return best || {
      contractHeading,
      draftHeading: null,
      score: 0,
      type: null,
      parentHeading: null,
      key: null,
      target: null,
    };
  });
}

function renderReport({
  contractPath,
  draftPath,
  result,
  summary,
  warnings,
  failures,
  mappings,
  titleNote,
}) {
  const headingLines = mappings.map((mapping) => {
    if (!mapping.draftHeading) {
      return `- ${mapping.contractHeading} -> MISSING`;
    }
    const qualifier = mapping.type === "sub"
      ? `${mapping.parentHeading} > ${mapping.draftHeading}`
      : mapping.draftHeading;
    return `- ${mapping.contractHeading} -> ${qualifier} (score ${mapping.score.toFixed(2)})`;
  });

  return [
    "# Source Fidelity Check",
    "",
    `- source_contract: ${contractPath}`,
    `- draft_file: ${draftPath}`,
    `- overall_result: ${result}`,
    `- generated_at: ${new Date().toISOString()}`,
    "",
    "## Summary",
    "",
    `- ${summary}`,
    ...(titleNote ? [`- ${titleNote}`] : []),
    "",
    "## Failures",
    "",
    ...(failures.length ? failures.map((item) => `- ${item}`) : ["- none"]),
    "",
    "## Warnings",
    "",
    ...(warnings.length ? warnings.map((item) => `- ${item}`) : ["- none"]),
    "",
    "## Heading Mapping",
    "",
    ...(headingLines.length ? headingLines : ["- none"]),
    "",
  ].join("\n");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const workspace = resolveAbsolute(args.workspace);
  const contractPath =
    resolveAbsolute(args.contract) ||
    (workspace ? path.join(workspace, "notes", "source-contract.md") : null);
  const draftPath =
    resolveAbsolute(args.draft) ||
    (workspace ? path.join(workspace, "drafts", "article.md") : null);
  const outputPath =
    resolveAbsolute(args.output) ||
    (workspace ? path.join(workspace, "notes", "source-fidelity-check.md") : null);

  if (!contractPath || !draftPath || !outputPath) {
    usage();
  }

  const contract = parseContractMarkdown(readText(contractPath));
  const draft = extractMarkdownStructure(readText(draftPath));
  const draftTargets = buildDraftTargets(draft);
  const warnings = [];
  const failures = [];

  const contractTitle = contract.metadata.source_title || "";
  let titleNote = "";
  if (contractTitle && draft.title) {
    const titleScore = headingSimilarity(contractTitle, draft.title);
    if (titleScore < 0.35) {
      warnings.push(`Draft title diverges from source title: "${contractTitle}" -> "${draft.title}".`);
      titleNote = `title drift noted: "${contractTitle}" -> "${draft.title}"`;
    }
  }

  const contractQuestions = contract.questions.filter((item) => item !== "none detected");
  const draftQuestions = extractExplicitQuestionList(draft.lines);
  if (contractQuestions.length > 0) {
    if (draftQuestions.length !== contractQuestions.length) {
      failures.push(
        `Explicit question count changed from ${contractQuestions.length} to ${draftQuestions.length}.`,
      );
    } else {
      const lowConfidencePairs = contractQuestions.filter((item, index) => {
        const other = draftQuestions[index] || "";
        return headingSimilarity(item, other) < 0.28;
      });
      if (lowConfidencePairs.length > 0) {
        warnings.push("Explicit question wording drifted enough that manual review is still needed.");
      }
    }
  }

  const contractHeadings = contract.topSections;
  const mappings = bestTargetMatches(contractHeadings, draftTargets);

  for (const mapping of mappings) {
    if (!mapping.draftHeading || mapping.score < HEADING_THRESHOLD) {
      failures.push(`Top-level section "${mapping.contractHeading}" no longer has a review-equivalent draft section.`);
      continue;
    }

    if (mapping.type === "sub") {
      warnings.push(
        `Top-level source section "${mapping.contractHeading}" now appears as a subsection under "${mapping.parentHeading}".`,
      );
    }
  }

  const draftToContract = new Map();
  for (const mapping of mappings) {
    if (!mapping.draftHeading || mapping.score < HEADING_THRESHOLD) {
      continue;
    }
    const group = draftToContract.get(mapping.key) || [];
    group.push(mapping.contractHeading);
    draftToContract.set(mapping.key, group);
  }

  for (const [draftKey, contractGroup] of draftToContract.entries()) {
    if (contractGroup.length > 1) {
      const mapping = mappings.find((item) => item.key === draftKey);
      const draftLabel = mapping && mapping.type === "sub"
        ? `${mapping.parentHeading} > ${mapping.draftHeading}`
        : (mapping ? mapping.draftHeading : draftKey);
      failures.push(
        `Independent source sections were merged into one draft section "${draftLabel}": ${contractGroup.join(", ")}.`,
      );
    }
  }

  for (const anchor of contract.figureAnchors) {
    const mapping = mappings.find((item) => item.contractHeading === anchor.section);
    if (!mapping || !mapping.draftHeading || mapping.score < HEADING_THRESHOLD) {
      failures.push(
        `Figure anchor "${anchor.value || anchor.kind}" lost its original section boundary "${anchor.section}".`,
      );
      continue;
    }

    const draftSection = mapping.target ? mapping.target.section : null;
    if (!draftSection) {
      failures.push(`Draft section "${mapping.draftHeading}" for figure anchor "${anchor.section}" is missing.`);
      continue;
    }

    const hasSameImage = anchor.kind === "image"
      && draftSection.images.some((image) => image.value === anchor.value);
    const hasVisualPlaceholder = draftSection.mermaidCount > 0 || draftSection.placeholderCount > 0;

    if (hasSameImage) {
      continue;
    }

    if (anchor.kind === "image" && hasVisualPlaceholder) {
      warnings.push(
        `Image anchor "${anchor.value}" was replaced by a local placeholder or Mermaid in "${mapping.draftHeading}".`,
      );
      continue;
    }

    if (anchor.kind === "mermaid" && hasVisualPlaceholder) {
      continue;
    }

    failures.push(
      `Figure anchor "${anchor.value || anchor.kind}" no longer has a corresponding image or placeholder in "${mapping.draftHeading}".`,
    );
  }

  const draftText = draft.lines.join("\n");
  for (const claim of contract.mustKeepClaims.filter((item) => item !== "none detected")) {
    const tokens = extractCodeLikeTokens(claim);
    if (tokens.length === 0) {
      continue;
    }
    const missing = tokens.filter((token) => !draftText.includes(token));
    if (missing.length === tokens.length) {
      warnings.push(`Must-keep claim may have drifted; none of its code-like anchors remain in draft: ${claim}`);
    }
  }

  const result = normalizeResultLevel(warnings, failures);
  const summary =
    result === "fail"
      ? "The draft is not review-equivalent to the source and should be revised before visuals or export."
      : result === "pass with noted deltas"
        ? "The draft stays semantically close enough to continue, but the noted deltas still need review."
        : "The draft remains review-equivalent to the source.";

  const report = renderReport({
    contractPath,
    draftPath,
    result,
    summary,
    warnings,
    failures,
    mappings,
    titleNote,
  });

  writeText(outputPath, report);
  console.log(`Wrote ${outputPath}`);
  if (result === "fail") {
    process.exitCode = 2;
  }
}

main();
