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

function slugify(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "research-report";
}

module.exports = {
  ensureDir,
  maybeWriteText,
  parseArgs,
  readText,
  resolveAbsolute,
  slugify,
  writeText,
};
