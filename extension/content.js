(() => {
    "use strict";

    const SITE = (() => {
        const h = location.hostname;
        if (h === "mail.google.com") return "GMAIL";
        if (h === "web.whatsapp.com") return "WHATSAPP";
        if (h === "www.instagram.com" || h === "instagram.com") return "INSTAGRAM";
        return "UNKNOWN";
    })();

    const DEBOUNCE_MS = 900;
    let timer = null;
    let activeBox = null;
    let requestId = 0;

    console.log("Toxicity Softener loaded on", SITE);

    function isEditable(el) {
        return !!el && (el.matches?.("textarea") || el.isContentEditable === true || el.getAttribute?.("contenteditable") === "true");
    }

    function textOf(el) {
        if (!el) return "";
        if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) return el.value.trim();
        return (el.innerText || el.textContent || "").replace(/\u200b/g, "").trim();
    }

    function isSearch(el) {
        const a = (el.getAttribute?.("aria-label") || "").toLowerCase();
        const p = (el.getAttribute?.("placeholder") || "").toLowerCase();
        return a.includes("search") || p.includes("search");
    }

    function isLikelyInstagramComment(el) {
        if (SITE !== "INSTAGRAM" || !el) return false;
        const a = (el.getAttribute?.("aria-label") || "").toLowerCase();
        const p = (el.getAttribute?.("placeholder") || "").toLowerCase();
        const name = (el.getAttribute?.("name") || "").toLowerCase();
        const hint = `${a} ${p} ${name}`;
        if (hint.includes("comment")) return true;
        // Instagram comment composers are normally inside a post/article
        // or a comments dialog. Do not require a specific class name because
        // Instagram changes its generated class names frequently.
        return !!el.closest('article, [role="dialog"]');
    }

    function findBox(target) {
        if (!target || !(target instanceof Element)) return null;
        let box = null;

        if (SITE === "GMAIL") {
            box = target.closest('div[contenteditable="true"][role="textbox"], textarea');
        } else if (SITE === "WHATSAPP") {
            box = target.closest('div[contenteditable="true"][role="textbox"], div[contenteditable="true"]');
        } else if (SITE === "INSTAGRAM") {
            box = target.closest(
                'textarea, [role="textbox"], div[contenteditable="true"], [contenteditable="plaintext-only"], input[type="text"]'
            );
        }

        if (!box || !isEditable(box) || isSearch(box)) return null;

        // Instagram has several textboxes on the same page. Explicit comment
        // labels and post/dialog ancestry are strong signals for the comment box.
        if (SITE === "INSTAGRAM" && !isLikelyInstagramComment(box)) return null;

        // Avoid editable elements that are clearly not a composer.
        if (box.closest("header") && SITE !== "WHATSAPP") return null;
        return box;
    }

    function findBestBox() {
        const selectors = SITE === "GMAIL"
            ? ['div[contenteditable="true"][role="textbox"]', 'textarea']
            : SITE === "WHATSAPP"
                ? ['div[contenteditable="true"][role="textbox"]', 'div[contenteditable="true"]']
                : ['textarea', '[role="textbox"]', 'div[contenteditable="true"]', '[contenteditable="plaintext-only"]', 'input[type="text"]'];

        for (const selector of selectors) {
            const nodes = [...document.querySelectorAll(selector)];
            for (let i = nodes.length - 1; i >= 0; i--) {
                const node = nodes[i];
                if (isEditable(node) && !isSearch(node) &&
                    (SITE !== "INSTAGRAM" || isLikelyInstagramComment(node)) &&
                    textOf(node).length >= 0) return node;
            }
        }
        return null;
    }

    function sendToBackground(message, box) {
        const myId = ++requestId;
        console.log("Analyzing:", message);

        chrome.runtime.sendMessage({ type: "ANALYZE_TEXT", message }, response => {
            if (myId !== requestId) return;

            if (chrome.runtime.lastError) {
                console.error("Extension runtime error:", chrome.runtime.lastError.message);
                return;
            }
            if (!response?.success) {
                console.error("Backend connection failed:", response?.error || "No response");
                return;
            }

            const current = textOf(box);
            if (current !== message) return;
            showPopup(response.result, box);
        });
    }

    function clearPopup() {
        document.getElementById("toxicity-softener-shadow-host")?.remove();
    }

    function showPopup(result, box) {
        clearPopup();

        const host = document.createElement("div");
        host.id = "toxicity-softener-shadow-host";
        host.style.position = "fixed";
        host.style.right = "18px";
        host.style.bottom = "18px";
        host.style.zIndex = "2147483647";
        host.style.all = "initial";
        document.documentElement.appendChild(host);

        const shadow = host.attachShadow({ mode: "open" });
        const style = document.createElement("style");
        style.textContent = `
            * { box-sizing:border-box; font-family:Arial,sans-serif; }
            .box { width:360px; background:#fff; color:#222; border:1px solid #ddd; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,.25); padding:16px; }
            .title { font-size:18px; font-weight:700; margin-bottom:10px; }
            .row { margin:6px 0; }
            .suggestion { background:#f5f6f8; padding:10px; border-radius:8px; margin:12px 0; line-height:1.4; white-space:pre-wrap; }
            .actions { display:flex; gap:8px; }
            button { border:0; border-radius:7px; padding:8px 13px; cursor:pointer; font-size:14px; }
            .use { background:#0d6efd; color:#fff; }
            .close { background:#6c757d; color:#fff; }
            .low { color:#198754; } .borderline { color:#d99000; } .high { color:#dc3545; }
        `;
        shadow.appendChild(style);

        const boxEl = document.createElement("div");
        boxEl.className = "box";
        const levelClass = String(result.toxicity || "LOW").toLowerCase();
        const probability = Number(result.toxicity_probability);
        const probabilityText = Number.isFinite(probability) ? probability.toFixed(3) : "N/A";

        boxEl.innerHTML = `
            <div class="title">Toxicity Softener</div>
            <div class="row"><strong>Toxicity:</strong> <span class="${levelClass}">${escapeHTML(result.toxicity || "LOW")}</span></div>
            <div class="row"><strong>Probability:</strong> ${probabilityText}</div>
            <div class="suggestion"><strong>Suggestion:</strong><br>${escapeHTML(result.suggestion || result.original || "")}</div>
            <div class="actions">
                ${result.action === "SOFTEN" || result.action === "OFFER_SOFTENING" ? '<button class="use" id="use">Use Suggestion</button>' : ''}
                <button class="close" id="close">Close</button>
            </div>
        `;
        shadow.appendChild(boxEl);

        boxEl.querySelector("#close")?.addEventListener("click", clearPopup);
        boxEl.querySelector("#use")?.addEventListener("click", () => {
            const suggestion = String(result.suggestion || "");
            if (!insertText(box, suggestion)) {
                console.error("Could not insert suggestion into composer.");
                return;
            }
            clearPopup();
        });
    }

    function escapeHTML(value) {
        const d = document.createElement("div");
        d.textContent = String(value ?? "");
        return d.innerHTML;
    }

    function dispatchInput(el, text) {
        try { el.dispatchEvent(new InputEvent("input", { bubbles:true, inputType:"insertText", data:text })); }
        catch (_) { el.dispatchEvent(new Event("input", { bubbles:true })); }
        el.dispatchEvent(new Event("change", { bubbles:true }));
    }

    function setNativeValue(el, value) {
        const proto = Object.getPrototypeOf(el);
        const descriptor = Object.getOwnPropertyDescriptor(proto, "value");
        if (descriptor?.set) descriptor.set.call(el, value); else el.value = value;
    }

    function insertText(el, text) {
        if (!el || !document.contains(el)) {
            el = findBestBox();
        }
        if (!el) return false;

        el.focus();

        // Textareas (Instagram commonly uses this path).
        if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
            setNativeValue(el, text);
            try { el.setSelectionRange(text.length, text.length); } catch (_) {}
            dispatchInput(el, text);
            return el.value === text;
        }

        // Contenteditable: use the browser editing command first so React/Angular
        // controlled editors receive an actual editing operation.
        try {
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(el);
            sel.removeAllRanges();
            sel.addRange(range);
            if (document.execCommand("insertText", false, text)) {
                dispatchInput(el, text);
                return textOf(el) === text;
            }
        } catch (e) {
            console.warn("execCommand insertion failed", e);
        }

        // DOM fallback for editors that do not expose execCommand.
        try {
            el.replaceChildren(document.createTextNode(text));
            dispatchInput(el, text);
            return textOf(el) === text;
        } catch (e) {
            console.error("DOM insertion failed", e);
            return false;
        }
    }

    function handleInput(event) {
        const box = findBox(event.target);
        if (!box) return;
        activeBox = box;
        const text = textOf(box);

        clearTimeout(timer);
        clearPopup();
        requestId++;

        if (!text) return;
        timer = setTimeout(() => sendToBackground(text, box), DEBOUNCE_MS);
    }

    document.addEventListener("input", handleInput, true);
    document.addEventListener("compositionend", handleInput, true);
    document.addEventListener("focusin", (event) => {
        const box = findBox(event.target);
        if (box) activeBox = box;
    }, true);

    // Instagram can create the comment editor after the user opens a post or
    // comments panel. MutationObserver keeps the extension aware of those
    // dynamically-created editors without depending on Instagram class names.
    // SPA navigation can replace the composer without reloading the page.
    const observer = new MutationObserver(() => {
        if (!activeBox || !document.contains(activeBox)) activeBox = findBestBox();
    });
    observer.observe(document.documentElement, { childList:true, subtree:true });

    console.log("Toxicity Softener Gmail / WhatsApp / Instagram integration initialized.");
})();
