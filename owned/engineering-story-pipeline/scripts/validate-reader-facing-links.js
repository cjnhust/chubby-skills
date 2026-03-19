#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { parseArgs, resolveAbsolute, readText } = require("./utils");

function usage() {
  console.error("Usage: node validate-reader-facing-links.js --file <article.md>");
  process.exit(1);
}

function findAbsoluteImageLinks(text) {
  return [...text.matchAll(/!\[[^\]]*\]\((\/[^)\s]+)\)/g)].map((m) => m[1]);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const filePath = resolveAbsolute(args.file);
  if (!filePath) {
    usage();
  }

  if (!fs.existsSync(filePath)) {
    throw new Error(`file does not exist: ${filePath}`);
  }

  const text = readText(filePath);
  const offenders = [...new Set(findAbsoluteImageLinks(text))];

  if (offenders.length > 0) {
    console.error("Found absolute filesystem image links:");
    for (const offender of offenders) {
      console.error(`- ${offender}`);
    }
    process.exit(2);
  }

  console.log(filePath);
}

main();
