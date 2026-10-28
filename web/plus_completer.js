import { app } from "../../scripts/app.js";
import { TagCompleter } from "./completer/tag_completer.js";
import { api_post, mk_name, mkEl } from "./utils.js";
import { tagAtCursor, promptTagSet, applyTextareaText } from "./prompt_format.js";

const option = (key, fallback) => app.ui.settings.getSettingValue(mk_name(key), fallback);

export class PlusCompleter extends TagCompleter {
    setRelatedHeading(tag, translation, status) {
        const link = mkEl("a.yp-tagforge-plus-source-link", {
            textContent: `📖 ${tag}`,
            href: `https://danbooru.donmai.us/wiki_pages/${encodeURIComponent(tag)}`,
            target: "_blank", rel: "noopener noreferrer", title: "Открыть тег на Danbooru",
            onclick: event => event.stopPropagation(),
        });
        const parts = [mkEl("span", { textContent: "Связанные с:" }), link];
        if (translation) parts.push(mkEl("span.yp-tagforge-plus-pill.yp-tagforge-plus-translation", { textContent: translation }));
        if (status) parts.push(mkEl("span", { textContent: status }));
        this.relatedHeader.replaceChildren(...parts);
    }
    handleClick(event) {
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedMode = false;
        super.handleClick(event);
        if (this.settings.enable && option("relatedEnabled", true)) this.showRelated();
    }
    handleInput(event) {
        this.relatedMode = false;
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedHeader?.remove();
        super.handleInput(event);
    }
    async update() {
        if (this.relatedMode) return;
        if (document.activeElement !== this.element) return this.dropdownController.hide();
        return super.update();
    }
    handleKeyDown(event) {
        if (event.key === "Escape") {
            this.relatedRequest = (this.relatedRequest ?? 0) + 1;
            this.relatedMode = false;
        }
        if (this.settings.enable && option("relatedEnabled", true) && event.ctrlKey && event.shiftKey && event.code === "Space") {
            event.preventDefault(); event.stopPropagation(); this.showRelated(); return;
        }
        super.handleKeyDown(event);
    }
    showDropdown(results, info) {
        if (this.relatedMode) return;
        this.relatedHeader?.remove();
        super.showDropdown(results, { ...info, existingTags: promptTagSet(this.element.value, this.settings.artistPrefix) });
    }
    async showRelated() {
        const range = tagAtCursor(this.element.value, this.element.selectionStart);
        if (!range) return;
        const prefix = String(this.settings.artistPrefix ?? "").toLowerCase().replace(/\s+/g, "_");
        if (prefix && range.tag.startsWith(prefix)) range.tag = range.tag.slice(prefix.length);
        if (!range.tag) return;
        this.relatedMode = true;
        const request = this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        const snapshot = this.element.value;
        const current = () => this.settings.enable && request === this.relatedRequest && this.element.value === snapshot
            && document.activeElement === this.element;
        this.relatedHeader?.remove();
        this.relatedHeader = mkEl("div.yp-tagforge-plus-related-heading");
        this.setRelatedHeading(range.tag, "", "загрузка…");
        this.dropdownController.dropdown.prepend(this.relatedHeader);
        this.dropdownController.show([], this.helper.getCursorOffset());
        try {
            const data = await api_post("related", { tag: range.tag, limit: option("relatedCount", 20) });
            if (!current()) return;
            const results = data.results ?? [];
            const info = { term: "", customPrefixes: [], categoryFilters: [], existingTags: promptTagSet(snapshot, this.settings.artistPrefix) };
            const items = this.dropdownRenderer.createDropdownItems(results, info, (event, result) => {
                if (event.target.closest?.(".yp-tagforge-plus-wikiLink")) return;
                if (this.element.value !== snapshot) return this.dropdownController.hide();
                const candidate = String(result.value).trim().replace(/\s+/g, "_").toLowerCase();
                const existing = [...snapshot.matchAll(/[^,\n]+/g)].find(match =>
                    promptTagSet(match[0], this.settings.artistPrefix).has(candidate));
                this.element.focus();
                if (existing) {
                    this.element.setSelectionRange(existing.index, existing.index + existing[0].length);
                } else {
                    const value = this.textProcessor.processTagValue(result, info);
                    const before = snapshot.slice(0, range.end).trimEnd();
                    const after = snapshot.slice(range.end);
                    const suffix = after.startsWith(",") ? after.replace(/^,\s*/, ", ") : `, ${after}`;
                    applyTextareaText(this.element, `${before}, ${value}${suffix}`);
                    this.element.setSelectionRange(before.length + 2 + value.length, before.length + 2 + value.length);
                }
                this.relatedRequest++;
                this.dropdownController.hide();
            });
            results.forEach((result, index) => {
                items[index].append(mkEl("span.yp-tagforge-plus-pill", {
                    textContent: `${(result.similarity * 100).toFixed(2)}%`,
                }));
            });
            this.setRelatedHeading(range.tag, data.translate, data.error ?? (results.length
                ? `· ${results.length}` : "нет связей в локальной базе"));
            this.dropdownController.show(items, this.helper.getCursorOffset());
        } catch (error) {
            if (current()) this.relatedHeader.textContent = `Не удалось загрузить связанные теги: ${error.message}`;
        }
    }
    destroy() {
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedHeader?.remove();
        super.destroy();
    }
}
