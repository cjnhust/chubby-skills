import { evaluate, sleep } from "./cdp_lib.mjs";

function stripTags(htmlText) {
  return htmlText.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

function buildInsertExpression({ html, plainText }) {
  const payload = JSON.stringify({ html, plainText });
  return `(() => {
    const payload = ${payload};

    function deepActive(doc) {
      let currentDoc = doc;
      while (currentDoc) {
        let active = currentDoc.activeElement;
        if (!active) return null;
        while (active && active.shadowRoot && active.shadowRoot.activeElement) {
          active = active.shadowRoot.activeElement;
        }
        if (active && active.tagName === "IFRAME") {
          try {
            currentDoc = active.contentWindow.document;
            continue;
          } catch (_err) {
            return active;
          }
        }
        return active;
      }
      return null;
    }

    function isVisible(el) {
      if (!el) return false;
      const rects = typeof el.getClientRects === "function" ? el.getClientRects() : [];
      return rects.length > 0 || el === document.body;
    }

    function isEditable(el) {
      if (!el) return false;
      if (el.isContentEditable) return true;
      if (el.tagName === "TEXTAREA") return true;
      if (el.tagName === "INPUT") {
        const type = String(el.type || "text").toLowerCase();
        return !["button", "checkbox", "radio", "file", "hidden", "submit"].includes(type);
      }
      if (el.getAttribute && el.getAttribute("role") === "textbox") return true;
      return false;
    }

    function findFallback(rootDoc) {
      const selectors = [
        "[contenteditable='true']",
        "[contenteditable='']",
        ".ProseMirror",
        "[role='textbox']",
        "textarea",
        "input[type='text']",
      ];
      for (const selector of selectors) {
        const nodes = Array.from(rootDoc.querySelectorAll(selector));
        const node = nodes.find((candidate) => isEditable(candidate) && isVisible(candidate));
        if (node) return node;
      }
      return null;
    }

    const target = (() => {
      const active = deepActive(document);
      if (isEditable(active) && isVisible(active)) {
        return active;
      }
      return findFallback(document);
    })();

    if (!target) {
      return { ok: false, reason: "NO_EDITABLE_TARGET" };
    }

    target.focus();

    if ((target.tagName === "TEXTAREA" || target.tagName === "INPUT") && !target.isContentEditable) {
      const start = target.selectionStart ?? target.value.length;
      const end = target.selectionEnd ?? target.value.length;
      target.setRangeText(payload.plainText, start, end, "end");
      target.dispatchEvent(new Event("input", { bubbles: true }));
      target.dispatchEvent(new Event("change", { bubbles: true }));
      return { ok: true, mode: "plain-text", tag: target.tagName };
    }

    const ownerDoc = target.ownerDocument || document;
    const selection = ownerDoc.getSelection ? ownerDoc.getSelection() : window.getSelection();
    if (!selection) {
      return { ok: false, reason: "NO_SELECTION" };
    }
    if (selection.rangeCount === 0) {
      const range = ownerDoc.createRange();
      range.selectNodeContents(target);
      range.collapse(false);
      selection.removeAllRanges();
      selection.addRange(range);
    }

    let usedExecCommand = false;
    try {
      if (ownerDoc.execCommand) {
        usedExecCommand = !!ownerDoc.execCommand("insertHTML", false, payload.html);
      }
    } catch (_err) {
      usedExecCommand = false;
    }

    if (!usedExecCommand) {
      const range = selection.getRangeAt(0);
      range.deleteContents();
      const fragment = range.createContextualFragment(payload.html);
      const lastNode = fragment.lastChild;
      range.insertNode(fragment);
      if (lastNode) {
        const afterRange = ownerDoc.createRange();
        afterRange.setStartAfter(lastNode);
        afterRange.collapse(true);
        selection.removeAllRanges();
        selection.addRange(afterRange);
      }
    }

    try {
      target.dispatchEvent(
        new InputEvent("input", {
          bubbles: true,
          inputType: "insertFromPaste",
          data: payload.plainText,
        }),
      );
    } catch (_err) {
      target.dispatchEvent(new Event("input", { bubbles: true }));
    }
    target.dispatchEvent(new Event("change", { bubbles: true }));

    return {
      ok: true,
      mode: usedExecCommand ? "execCommand" : "range",
      tag: target.tagName,
      className: String(target.className || ""),
    };
  })()`;
}

export async function insertHtmlBlocks(cdp, sessionId, blocks) {
  const results = [];
  for (let index = 0; index < blocks.length; index += 1) {
    const html = blocks[index];
    const plainText = stripTags(html);
    const result = await evaluate(cdp, sessionId, buildInsertExpression({ html, plainText }), 60000);
    if (!result?.ok) {
      const reason = result?.reason ?? "UNKNOWN_INSERT_FAILURE";
      throw new Error(`Editor insertion failed at block ${index}: ${reason}`);
    }
    results.push(result);
    await sleep(35);
  }
  return results;
}

export async function readCurrentUrl(cdp, sessionId) {
  return await evaluate(cdp, sessionId, "location.href");
}
