#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      continue;
    }

    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }

    args[key] = next;
    i += 1;
  }
  return args;
}

function resolveAbsolute(inputPath, cwd = process.cwd()) {
  if (!inputPath) {
    return null;
  }
  return path.isAbsolute(inputPath) ? inputPath : path.resolve(cwd, inputPath);
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function writeText(filePath, text) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, text, "utf8");
}

function maybeWriteText(filePath, text, options = {}) {
  const { force = false, marker = null } = options;
  if (!fs.existsSync(filePath)) {
    writeText(filePath, text);
    return { action: "created" };
  }

  const current = readText(filePath);
  const canOverwrite = force || (marker && current.includes(marker));
  if (!canOverwrite) {
    return { action: "skipped" };
  }

  if (current === text) {
    return { action: "unchanged" };
  }

  writeText(filePath, text);
  return { action: "updated" };
}

function copyFile(sourcePath, targetPath, options = {}) {
  const { force = false } = options;
  ensureDir(path.dirname(targetPath));
  const existed = fs.existsSync(targetPath);

  if (!existed || force) {
    fs.copyFileSync(sourcePath, targetPath);
    return { action: existed ? "updated" : "created" };
  }

  const sourceText = readText(sourcePath);
  const targetText = readText(targetPath);
  if (sourceText === targetText) {
    return { action: "unchanged" };
  }

  return { action: "skipped" };
}

function slugify(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "writing";
}

function stripBullet(line) {
  return line.replace(/^\s*(?:[-*+]|\d+\.)\s+/, "").trim();
}

function stripCodeFences(line) {
  return line.replace(/```/g, "").trim();
}

function normalizeHeading(value) {
  return String(value || "")
    .replace(/^#+\s*/, "")
    .replace(/^\d+(?:\.\d+)*\s*/, "")
    .replace(/[`*_]/g, "")
    .replace(/[()（）[\]【】{}]/g, " ")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .toLowerCase();
}

function headingSignature(value) {
  return normalizeHeading(value).replace(/\s+/g, "");
}

function bigrams(value) {
  const source = headingSignature(value);
  if (!source) {
    return [];
  }
  if (source.length === 1) {
    return [source];
  }
  const result = [];
  for (let index = 0; index < source.length - 1; index += 1) {
    result.push(source.slice(index, index + 2));
  }
  return result;
}

function headingSimilarity(left, right) {
  const a = headingSignature(left);
  const b = headingSignature(right);
  if (!a || !b) {
    return 0;
  }
  if (a === b) {
    return 1;
  }
  if (a.includes(b) || b.includes(a)) {
    return 0.92;
  }

  const aPairs = bigrams(a);
  const bPairs = bigrams(b);
  const aCount = new Map();
  for (const pair of aPairs) {
    aCount.set(pair, (aCount.get(pair) || 0) + 1);
  }

  let overlap = 0;
  for (const pair of bPairs) {
    const count = aCount.get(pair) || 0;
    if (count > 0) {
      overlap += 1;
      aCount.set(pair, count - 1);
    }
  }

  return (2 * overlap) / (aPairs.length + bPairs.length);
}

function extractMarkdownStructure(text) {
  const lines = text.split(/\r?\n/);
  const titleMatch = lines.find((line) => /^#\s+/.test(line));
  const title = titleMatch ? titleMatch.replace(/^#\s+/, "").trim() : "";
  const sections = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const match = line.match(/^##\s+(.+)$/);
    if (!match) {
      continue;
    }

    sections.push({
      heading: match[1].trim(),
      line: index + 1,
      startIndex: index,
    });
  }

  for (let index = 0; index < sections.length; index += 1) {
    const current = sections[index];
    const next = sections[index + 1];
    current.endIndex = next ? next.startIndex - 1 : lines.length - 1;
    current.content = lines.slice(current.startIndex, current.endIndex + 1);
    current.subheadings = [];
    current.images = [];
    current.mermaidCount = 0;
    current.placeholderCount = 0;
    let inMermaid = false;
    let activeSubheading = null;
    for (let cursor = current.startIndex; cursor <= current.endIndex; cursor += 1) {
      const contentLine = lines[cursor];
      const subheadingMatch = contentLine.match(/^###\s+(.+)$/);
      if (subheadingMatch) {
        const subsection = {
          heading: subheadingMatch[1].trim(),
          line: cursor + 1,
          startIndex: cursor,
          endIndex: current.endIndex,
          images: [],
          mermaidCount: 0,
          placeholderCount: 0,
          parentHeading: current.heading,
        };

        if (activeSubheading) {
          activeSubheading.endIndex = cursor - 1;
        }
        current.subheadings.push(subsection);
        activeSubheading = subsection;
      }

      if (/^```mermaid\s*$/.test(contentLine.trim())) {
        inMermaid = true;
        current.mermaidCount += 1;
        if (activeSubheading) {
          activeSubheading.mermaidCount += 1;
        }
      } else if (inMermaid && /^```\s*$/.test(contentLine.trim())) {
        inMermaid = false;
      }

      if (/\[!visual-placeholder\]/.test(contentLine)) {
        current.placeholderCount += 1;
        if (activeSubheading) {
          activeSubheading.placeholderCount += 1;
        }
      }

      const obsidianImage = contentLine.match(/!\[\[([^\]]+)\]\]/);
      if (obsidianImage) {
        const entry = {
          type: "image",
          value: path.basename(obsidianImage[1].trim()),
          line: cursor + 1,
        };
        current.images.push(entry);
        if (activeSubheading) {
          activeSubheading.images.push(entry);
        }
      }

      const markdownImages = [...contentLine.matchAll(/!\[[^\]]*]\(([^)]+)\)/g)];
      for (const image of markdownImages) {
        const entry = {
          type: "image",
          value: path.basename(image[1].trim()),
          line: cursor + 1,
        };
        current.images.push(entry);
        if (activeSubheading) {
          activeSubheading.images.push(entry);
        }
      }
    }

    if (activeSubheading) {
      activeSubheading.endIndex = current.endIndex;
    }
  }

  return { lines, title, sections };
}

function extractExplicitQuestionList(lines) {
  const trigger = lines.findIndex((line) => /(回答|关注|重点回答).*(问题|事项|目标)/.test(line));
  if (trigger < 0) {
    return [];
  }

  const items = [];
  let started = false;
  for (let index = trigger + 1; index < lines.length; index += 1) {
    const line = lines[index];
    if (!started && !line.trim()) {
      continue;
    }

    if (/^\s*(?:[-*+]|\d+\.)\s+/.test(line)) {
      items.push(stripBullet(line));
      started = true;
      continue;
    }

    if (started && !line.trim()) {
      continue;
    }

    if (started) {
      break;
    }
  }

  return items;
}

function firstParagraph(lines) {
  const result = [];
  let started = false;
  for (const line of lines) {
    if (/^#/.test(line.trim())) {
      continue;
    }

    if (!started && !line.trim()) {
      continue;
    }

    if (!line.trim()) {
      if (started) {
        break;
      }
      continue;
    }

    started = true;
    result.push(line.trim());
    if (result.join(" ").length > 220) {
      break;
    }
  }

  return result.join(" ").trim();
}

function collectBulletsWithinRange(lines, startIndex, endIndex) {
  const bullets = [];
  for (let index = startIndex; index <= endIndex; index += 1) {
    const line = lines[index];
    if (/^\s*(?:[-*+]|\d+\.)\s+/.test(line)) {
      bullets.push(stripBullet(line));
    }
  }
  return bullets;
}

function extractMustKeepClaims(structure) {
  const keywordPattern = /目标态结论|非目标|硬约束|兼容策略|风险与回滚|关键设计决策/;
  const claims = [];
  for (const section of structure.sections) {
    if (!keywordPattern.test(section.heading)) {
      continue;
    }

    const bullets = collectBulletsWithinRange(
      structure.lines,
      section.startIndex,
      section.endIndex,
    );
    for (const bullet of bullets.slice(0, 8)) {
      claims.push(bullet);
    }
  }

  return Array.from(new Set(claims));
}

function parseSelectionBundle(text) {
  const bundle = {};
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^\s*-\s*([a-zA-Z0-9_]+):\s*(.+?)\s*$/);
    if (!match) {
      continue;
    }
    bundle[match[1]] = match[2];
  }
  return bundle;
}

function extractCodeLikeTokens(text) {
  const tokens = new Set();
  const codeMatches = text.matchAll(/`([^`]+)`/g);
  for (const match of codeMatches) {
    tokens.add(match[1]);
  }

  const asciiMatches = text.matchAll(/[A-Za-z_][A-Za-z0-9:_/-]{2,}/g);
  for (const match of asciiMatches) {
    tokens.add(match[0]);
  }
  return Array.from(tokens);
}

function parseContractSectionMap(sectionLines) {
  return sectionLines
    .filter((line) => /^\s*-\s+/.test(line))
    .map((line) => stripBullet(line).split(" :: ")[0].trim())
    .filter(Boolean);
}

function parseContractFigureAnchors(sectionLines) {
  return sectionLines
    .filter((line) => /^\s*-\s+/.test(line))
    .map((line) => stripBullet(line))
    .map((line) => {
      const parts = line.split(" :: ").map((part) => part.trim());
      return {
        section: parts[0] || "",
        kind: parts[1] || "",
        value: parts[2] || "",
      };
    })
    .filter((item) => item.section && item.kind);
}

function parseContractMarkdown(text) {
  const lines = text.split(/\r?\n/);
  const top = {};
  let current = null;

  for (const line of lines) {
    const sectionMatch = line.match(/^##\s+(.+)$/);
    if (sectionMatch) {
      current = sectionMatch[1].trim();
      top[current] = [];
      continue;
    }

    if (!current) {
      continue;
    }

    top[current].push(line);
  }

  const metadata = {};
  const headerBullets = [];
  for (const line of lines) {
    if (/^##\s+/.test(line)) {
      break;
    }
    if (/^\s*-\s+/.test(line)) {
      headerBullets.push(stripBullet(line));
    }
  }
  for (const bullet of headerBullets) {
    const [key, ...rest] = bullet.split(":");
    if (!key || rest.length === 0) {
      continue;
    }
    metadata[key.trim()] = rest.join(":").trim();
  }

  return {
    metadata,
    positioning: (top["Positioning"] || []).filter(Boolean).map(stripBullet),
    questions: (top["Explicit Question List"] || []).filter((line) => /^\s*-\s+/.test(line)).map(stripBullet),
    topSections: parseContractSectionMap(top["Top-Level Sections"] || []),
    majorSections: (top["Major Second-Level Sections"] || []).filter((line) => /^\s*-\s+/.test(line)).map(stripBullet),
    figureAnchors: parseContractFigureAnchors(top["Figure Anchors"] || []),
    mustKeepClaims: (top["Must-Keep Claims"] || []).filter((line) => /^\s*-\s+/.test(line)).map(stripBullet),
  };
}

module.exports = {
  collectBulletsWithinRange,
  copyFile,
  ensureDir,
  extractCodeLikeTokens,
  extractExplicitQuestionList,
  extractMarkdownStructure,
  extractMustKeepClaims,
  firstParagraph,
  headingSimilarity,
  maybeWriteText,
  normalizeHeading,
  parseArgs,
  parseContractMarkdown,
  parseSelectionBundle,
  readText,
  resolveAbsolute,
  slugify,
  stripBullet,
  stripCodeFences,
  writeText,
};
