import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import {
  CdpConnection,
  attachToFirstPageTarget,
  evaluate,
  getFreePort,
  launchChrome,
  makeTempProfileDir,
  removeDir,
  waitForChromeDebugPort,
} from "./cdp_lib.mjs";
import { insertHtmlBlocks } from "./editor_injection.mjs";

const TEST_IMAGE =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WH1B20AAAAASUVORK5CYII=";

async function main() {
  const fixtureDir = await fs.mkdtemp(path.join(os.tmpdir(), "kuaishou-doc-selftest-"));
  const profileDir = await makeTempProfileDir("kuaishou-doc-selftest-profile-");
  const htmlPath = path.join(fixtureDir, "editor.html");
  const fixtureHtml = `<!doctype html>
<html>
  <body>
    <div
      id="editor"
      contenteditable="true"
      style="min-height:320px;padding:20px;border:1px solid #ccc;font-family:Helvetica"
    ></div>
    <script>
      const editor = document.getElementById("editor");
      editor.focus();
      const range = document.createRange();
      range.selectNodeContents(editor);
      range.collapse(false);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    </script>
  </body>
</html>`;
  await fs.writeFile(htmlPath, fixtureHtml, "utf-8");

  const port = await getFreePort();
  const chromeProcess = await launchChrome({
    url: `file://${htmlPath}`,
    port,
    profileDir,
  });

  let cdp = null;
  try {
    const wsUrl = await waitForChromeDebugPort(port, 20000);
    cdp = await CdpConnection.connect(wsUrl, 15000);
    const { sessionId } = await attachToFirstPageTarget(cdp, port, "file://");
    await cdp.send("Page.enable", {}, { sessionId });
    await cdp.send("Runtime.enable", {}, { sessionId });

    await evaluate(
      cdp,
      sessionId,
      `(() => {
        const editor = document.getElementById("editor");
        editor.focus();
        const range = document.createRange();
        range.selectNodeContents(editor);
        range.collapse(false);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      })()`,
    );

    const blocks = [
      "<h1>Title</h1>",
      `<p>Paragraph <strong>bold</strong> <img alt="pixel" src="${TEST_IMAGE}" /></p>`,
      "<ul><li>One</li><li>Two</li></ul>",
      "<pre><code>const value = 1;</code></pre>",
    ];
    await insertHtmlBlocks(cdp, sessionId, blocks);

    const editorHtml = await evaluate(cdp, sessionId, `document.getElementById("editor").innerHTML`);
    if (
      !String(editorHtml).includes("Title") ||
      !String(editorHtml).includes(TEST_IMAGE) ||
      !String(editorHtml).includes("<ul>") ||
      !String(editorHtml).includes("const value = 1;")
    ) {
      throw new Error(`Unexpected editor HTML after insertion: ${editorHtml}`);
    }

    console.log("[selftest] injection pipeline passed");
  } finally {
    if (cdp) {
      try {
        await cdp.send("Browser.close", {}, { timeoutMs: 5000 });
      } catch {
        // ignore
      }
      cdp.close();
    }
    await removeDir(profileDir);
    await removeDir(fixtureDir);
  }
}

try {
  await main();
} catch (error) {
  console.error(`[selftest-error] ${error.message}`);
  process.exit(2);
}
