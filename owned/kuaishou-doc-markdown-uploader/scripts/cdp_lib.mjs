import { spawn } from "node:child_process";
import { EventEmitter } from "node:events";
import fs from "node:fs/promises";
import net from "node:net";
import os from "node:os";
import path from "node:path";

const CHROME_CANDIDATES = {
  darwin: [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ],
  win32: [
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  ],
  default: [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
  ],
};

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getFreePort() {
  return await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close((closeErr) => {
        if (closeErr) {
          reject(closeErr);
          return;
        }
        resolve(address.port);
      });
    });
    server.on("error", reject);
  });
}

export async function makeTempProfileDir(prefix = "kuaishou-doc-chrome-") {
  return await fs.mkdtemp(path.join(os.tmpdir(), prefix));
}

export async function removeDir(dirPath) {
  await fs.rm(dirPath, { recursive: true, force: true });
}

export async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

export async function findChromeExecutable() {
  const envPath = process.env.KUAISHOU_DOCS_CHROME_PATH;
  if (envPath && (await fileExists(envPath))) {
    return envPath;
  }

  const candidates =
    CHROME_CANDIDATES[process.platform] ?? CHROME_CANDIDATES.default;
  for (const candidate of candidates) {
    if (await fileExists(candidate)) {
      return candidate;
    }
  }
  return null;
}

export async function launchChrome({
  url,
  port,
  profileDir,
  headless = false,
}) {
  const chromePath = await findChromeExecutable();
  if (!chromePath) {
    throw new Error(
      "Chrome executable not found. Install Chrome or set KUAISHOU_DOCS_CHROME_PATH.",
    );
  }

  const args = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    "--new-window",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-sync",
    "--disable-popup-blocking",
    "--disable-features=PasswordManagerEnabled,AutofillServerCommunication,MediaRouter",
  ];
  if (headless) {
    args.push("--headless=new");
  }
  args.push(url);

  return spawn(chromePath, args, {
    stdio: "ignore",
  });
}

export async function killChrome(chromeProcess) {
  if (!chromeProcess || chromeProcess.killed) {
    return;
  }
  chromeProcess.kill("SIGTERM");
  await sleep(500);
  if (!chromeProcess.killed) {
    chromeProcess.kill("SIGKILL");
  }
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
  return await response.json();
}

export async function waitForChromeDebugPort(port, timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      const version = await fetchJson(`http://127.0.0.1:${port}/json/version`);
      if (version.webSocketDebuggerUrl) {
        return version.webSocketDebuggerUrl;
      }
    } catch {
      await sleep(200);
      continue;
    }
    await sleep(100);
  }
  throw new Error(`Timed out waiting for Chrome debug port ${port}.`);
}

export async function listTargets(port) {
  return await fetchJson(`http://127.0.0.1:${port}/json/list`);
}

export class CdpConnection extends EventEmitter {
  constructor(webSocketUrl) {
    super();
    this.webSocketUrl = webSocketUrl;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  static async connect(webSocketUrl, timeoutMs = 15000) {
    const connection = new CdpConnection(webSocketUrl);
    await connection.open(timeoutMs);
    return connection;
  }

  async open(timeoutMs) {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error("Timed out opening CDP websocket."));
      }, timeoutMs);

      this.ws = new WebSocket(this.webSocketUrl);
      this.ws.addEventListener("open", () => {
        clearTimeout(timer);
        resolve();
      });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(String(event.data));
        if (message.id) {
          const pending = this.pending.get(message.id);
          if (!pending) {
            return;
          }
          this.pending.delete(message.id);
          if (message.error) {
            pending.reject(new Error(message.error.message || "CDP command failed."));
            return;
          }
          pending.resolve(message.result ?? {});
          return;
        }
        if (message.method) {
          this.emit(message.method, message.params ?? {});
        }
      });
      this.ws.addEventListener("error", (error) => {
        clearTimeout(timer);
        reject(error.error || error);
      });
      this.ws.addEventListener("close", () => {
        for (const pending of this.pending.values()) {
          pending.reject(new Error("CDP websocket closed."));
        }
        this.pending.clear();
      });
    });
  }

  async send(method, params = {}, options = {}) {
    const id = this.nextId++;
    const payload = { id, method, params };
    if (options.sessionId) {
      payload.sessionId = options.sessionId;
    }

    return await new Promise((resolve, reject) => {
      const timeoutMs = options.timeoutMs ?? 30000;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP timeout for ${method}`));
      }, timeoutMs);
      this.pending.set(id, {
        resolve: (result) => {
          clearTimeout(timer);
          resolve(result);
        },
        reject: (error) => {
          clearTimeout(timer);
          reject(error);
        },
      });
      this.ws.send(JSON.stringify(payload));
    });
  }

  close() {
    if (this.ws && this.ws.readyState < WebSocket.CLOSING) {
      this.ws.close();
    }
  }
}

export async function attachToFirstPageTarget(cdp, port, preferredUrlPrefix = "") {
  const started = Date.now();
  while (Date.now() - started < 15000) {
    const targets = await listTargets(port);
    const pageTarget =
      targets.find(
        (target) =>
          target.type === "page" &&
          (!preferredUrlPrefix || String(target.url || "").startsWith(preferredUrlPrefix)),
      ) || targets.find((target) => target.type === "page");
    if (pageTarget) {
      const attached = await cdp.send("Target.attachToTarget", {
        targetId: pageTarget.id,
        flatten: true,
      });
      return { targetId: pageTarget.id, sessionId: attached.sessionId };
    }
    await sleep(200);
  }
  throw new Error("Failed to locate a page target in Chrome.");
}

export async function evaluate(cdp, sessionId, expression, timeoutMs = 30000) {
  const result = await cdp.send(
    "Runtime.evaluate",
    {
      expression,
      returnByValue: true,
      awaitPromise: true,
    },
    { sessionId, timeoutMs },
  );
  return result.result?.value;
}
