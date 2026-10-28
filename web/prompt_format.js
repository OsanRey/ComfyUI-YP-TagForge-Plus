// Prompt cleanup inspired by Autocomplete Plus (MIT, newtextdoc1111).
// Unlike splitting on every comma, preserve syntax inside brackets/LoRAs.
export function formatPrompt(text, { trailingComma = true, trim = true } = {}) {
    if (text == null) return text;
    const lines = String(text).replace(/\r\n/g, "\n").split("\n");
    let stack = [], escaped = false;
    const formatted = lines.map(line => {
        const parts = []; let part = "";
        for (const char of line) {
            if (escaped) { part += char; escaped = false; continue; }
            if (char === "\\") { part += char; escaped = true; continue; }
            if ("([{<".includes(char)) stack.push({"(":")", "[":"]", "{":"}", "<":">"}[char]);
            else if (char === stack.at(-1)) stack.pop();
            if (char === "," && !stack.length) { if (part.trim()) parts.push(part.trim()); part = ""; }
            else part += char;
        }
        if (part.trim()) parts.push(part.trim());
        let result = parts.join(", ");
        if (result && trailingComma && !stack.length) result += ", ";
        return result;
    });
    if (trim) {
        while (formatted.length && !formatted[0]) formatted.shift();
        while (formatted.length && !formatted.at(-1)) formatted.pop();
    }
    return formatted.join("\n");
}

export function shouldFormat(text, info = {}) {
    const name = String(info.inputName ?? "");
    const type = String(info.nodeType ?? "");
    if (/code|script|expression|block_vector|json|yaml|resolution|preview|filename|path/i.test(name)
        || /Power Puter|Note|Markdown/i.test(type)) return false;
    if (!text.trim()) return true;
    const values = text.trim().split(",").map(value => value.trim()).filter(Boolean);
    if (values.length && values.every(value => /^(?:[A-Za-z]|[+-]?\d+(?:\.\d+)?)$/.test(value))) return false;
    if (/^\s*[{[]\s*["']/.test(text)) return false;
    return text.includes(",") || /prompt|tags|positive|negative|text|master/i.test(name)
        || /^[\w-]+$/.test(text.trim());
}

export function tagAtCursor(text, cursor) {
    if (cursor == null || !text) return null;
    let start = cursor, end = cursor;
    while (start > 0 && !",\n".includes(text[start - 1])) start--;
    while (end < text.length && !",\n".includes(text[end])) end++;
    const raw = text.slice(start, end).trim();
    if (!raw || /[<>{}|]|__/.test(raw)) return null;
    const tag = raw.replace(/\\\(/g, "\uE000").replace(/\\\)/g, "\uE001")
        .replace(/^[\s([\]]+/, "").replace(/(?::[+-]?[\d.]+)?[)\]\s]*$/, "")
        .replace(/\uE000/g, "(").replace(/\uE001/g, ")").trim().replace(/\s+/g, "_").toLowerCase();
    return tag ? { tag, start, end } : null;
}

export function promptTagSet(text, artistPrefix = "") {
    const tags = new Set();
    const prefix = String(artistPrefix).toLowerCase().replace(/\s+/g, "_");
    for (const match of String(text ?? "").matchAll(/[^,\n]+/g)) {
        const range = tagAtCursor(text, match.index + Math.floor(match[0].length / 2));
        if (range) {
            tags.add(range.tag);
            if (prefix && range.tag.startsWith(prefix)) tags.add(range.tag.slice(prefix.length));
        }
    }
    return tags;
}

export function applyTextareaText(element, value) {
    if (element.value === value) return false;
    const cursor = element.selectionStart ?? 0;
    const scrollTop = element.scrollTop;
    // Use native setter so Vue's next input event updates the widget and workflow.
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")?.set;
    if (setter) setter.call(element, value); else element.value = value;
    element.setSelectionRange(Math.min(cursor, value.length), Math.min(cursor, value.length));
    element.scrollTop = scrollTop;
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
}
