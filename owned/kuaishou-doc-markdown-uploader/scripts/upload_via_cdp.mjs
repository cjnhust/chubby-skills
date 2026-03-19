import fs from "node:fs/promises";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

import {
  CdpConnection,
  attachToFirstPageTarget,
  getFreePort,
  killChrome,
  launchChrome,
  makeTempProfileDir,
  removeDir,
  waitForChromeDebugPort,
} from "./cdp_lib.mjs";
import { insertHtmlBlocks, readCurrentUrl } from "./editor_injection.mjs";

function parseArgs(argv) {
  const args = {
    bundleJson: "",
    docsUrl: "https://docs.corp.kuaishou.com/home",
    keepBrowserOpen: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const current = argv[index];
    if (current === "--bundle-json") {
      args.bundleJson = argv[index + 1] ?? "";
      index += 1;
      continue;
    }
    if (current === "--docs-url") {
      args.docsUrl = argv[index + 1] ?? args.docsUrl;
      index += 1;
      continue;
    }
    if (current === "--keep-browser-open") {
      args.keepBrowserOpen = true;
      continue;
    }
  }
  if (!args.bundleJson) {
    throw new Error("Missing required --bundle-json argument.");
  }
  return args;
}

function assertDocsUrl(urlText) {
  const url = new URL(urlText);
  if (url.protocol !== "https:" || url.hostname !== "docs.corp.kuaishou.com") {
    throw new Error(`Refusing to upload to non-Kuaishou Docs host: ${urlText}`);
  }
}

async function prompt(question) {
  const rl = readline.createInterface({ input, output });
  try {
    await rl.question(`${question}\n`);
  } finally {
    rl.close();
  }
}

async function closeBrowser(cdp, chromeProcess) {
  try {
    await cdp.send("Browser.close", {}, { timeoutMs: 5000 });
  } catch {
    await killChrome(chromeProcess);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  assertDocsUrl(args.docsUrl);

  const bundle = JSON.parse(await fs.readFile(args.bundleJson, "utf-8"));
  if (!Array.isArray(bundle.blocks) || bundle.blocks.length === 0) {
    throw new Error("Bundle JSON does not contain any uploadable blocks.");
  }

  const profileDir = await makeTempProfileDir();
  const port = await getFreePort();
  const chromeProcess = await launchChrome({
    url: args.docsUrl,
    port,
    profileDir,
  });

  let cdp = null;
  try {
    const wsUrl = await waitForChromeDebugPort(port, 20000);
    cdp = await CdpConnection.connect(wsUrl, 15000);
    const { sessionId } = await attachToFirstPageTarget(cdp, port, "https://docs.corp.kuaishou.com");
    await cdp.send("Page.enable", {}, { sessionId });
    await cdp.send("Runtime.enable", {}, { sessionId });

    console.log("[browser] opened isolated Chrome profile");
    console.log("[safety] login manually in that window; no cookies or tokens are read");
    console.log("[workflow] keep the target doc in the same tab and click into the editor body");

    await prompt("完成登录并将光标放到云文档正文区域后，回到这里按 Enter 开始上传。");

    const currentUrl = await readCurrentUrl(cdp, sessionId);
    assertDocsUrl(currentUrl);

    const results = await insertHtmlBlocks(cdp, sessionId, bundle.blocks);
    console.log(
      `[uploaded] blocks=${results.length} images=${bundle.stats?.image_count ?? "?"} mode=${results[0]?.mode ?? "unknown"}`,
    );

    if (args.keepBrowserOpen) {
      console.log(`[profile-dir] preserved at ${profileDir}`);
      console.log("[browser] left open for manual review");
      return;
    }

    await prompt("请在浏览器里复核结果。确认后回到这里按 Enter，关闭临时浏览器并清理临时 profile。");
    await closeBrowser(cdp, chromeProcess);
    await removeDir(profileDir);
  } catch (error) {
    console.error(`[upload-error] ${error.message}`);
    console.error(`[profile-dir] ${profileDir}`);
    throw error;
  } finally {
    if (cdp) {
      cdp.close();
    }
  }
}

try {
  await main();
} catch {
  process.exit(2);
}
