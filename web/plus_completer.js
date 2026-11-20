import { app } from "../../scripts/app.js";
import { TagCompleter } from "./completer/tag_completer.js";
import { api_post, mk_name, mkEl } from "./utils.js";
import { tagAtCursor, promptTagSet, applyTextareaText } from "./prompt_format.js";

const option = (key, fallback) => app.ui.settings.getSettingValue(mk_name(key), fallback);

export class PlusCompleter extends TagCompleter {
    setRelatedHeading(tag, translation, status, matchedTags = [tag]) {
        const links = matchedTags.map(matchedTag => mkEl("a.yp-tagforge-plus-source-link", {
            textContent: matchedTag === tag || matchedTags.length > 1 ? `📖 ${matchedTag}` : `📖 ${tag} → ${matchedTag}`,
            href: `https://danbooru.donmai.us/wiki_pages/${encodeURIComponent(matchedTag)}`,
            target: "_blank", rel: "noopener noreferrer", title: "Открыть тег на Danbooru",
            onclick: event => event.stopPropagation(),
        }));
        const parts = [mkEl("span", { textContent: "Связанные с:" })];
        if (matchedTags.length > 1) parts.push(mkEl("span", { textContent: `${tag} →` }));
        parts.push(...links);
        if (translation) parts.push(mkEl("span.yp-tagforge-plus-pill.yp-tagforge-plus-translation", { textContent: translation }));
        if (status) parts.push(mkEl("span", { textContent: status }));
        this.relatedHeader.replaceChildren(...parts);
    }
    handlePointerDown(event) {
        super.handlePointerDown(event);
        this.clickPointerListeners?.abort();
        this.clickGesture = null;
        if (event.isPrimary === false || event.button !== 0) return;

        const gesture = this.clickGesture = {
            pointerId: event.pointerId, clientX: event.clientX, clientY: event.clientY,
            released: false, dragged: false, canceled: false,
        };
        const listeners = this.clickPointerListeners = new AbortController();
        const options = { capture: true, signal: listeners.signal };
        const trackMovement = pointer => {
            if (pointer.pointerId === gesture.pointerId && this.movedFromPress(gesture, pointer)) {
                gesture.dragged = true;
            }
        };
        document.addEventListener("pointermove", trackMovement, options);
        document.addEventListener("pointerup", pointer => {
            if (pointer.pointerId !== gesture.pointerId) return;
            trackMovement(pointer);
            gesture.released = true;
            listeners.abort();
        }, options);
        document.addEventListener("pointercancel", pointer => {
            if (pointer.pointerId !== gesture.pointerId) return;
            gesture.canceled = true;
            listeners.abort();
        }, options);
    }
    movedFromPress(gesture, event) {
        return Math.hypot(event.clientX - gesture.clientX, event.clientY - gesture.clientY) >= 4;
    }
    removeEventListeners() {
        this.clickPointerListeners?.abort();
        super.removeEventListeners();
    }
    handleClick(event) {
        const gesture = this.clickGesture;
        this.clickGesture = null;
        this.clickPointerListeners?.abort();
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedMode = false;
        super.handleClick(event);
        // A click can reach the textarea without the full pointer event sequence.
        const moved = gesture && !gesture.released && event.detail > 0 && this.movedFromPress(gesture, event);
        if (gesture?.dragged || gesture?.canceled || moved || event.detail > 1 ||
            this.element.selectionStart !== this.element.selectionEnd ||
            !this.settings.enable || !option("relatedEnabled", true)) return;
        // A second press can start word-by-word selection from this click.
        this.relatedClickTimeout = setTimeout(() => {
            if (document.activeElement === this.element && this.element.selectionStart === this.element.selectionEnd) {
                return this.showRelated();
            }
        }, 300);
    }
    invalidateSearch() {
        clearTimeout(this.relatedClickTimeout);
        super.invalidateSearch();
    }
    handleInput(event) {
        this.relatedMode = false;
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedHeader?.remove();
        super.handleInput(event);
    }
    async update() {
        if (!this.settings.enable || this.relatedMode || document.activeElement !== this.element) return;
        return super.update();
    }
    handleKeyDown(event) {
        if (event.key === "Escape") clearTimeout(this.relatedClickTimeout);
        if (this.settings.enable && option("relatedEnabled", true) && event.ctrlKey && event.shiftKey && event.code === "Space") {
            event.preventDefault(); event.stopPropagation(); this.showRelated(); return;
        }
        super.handleKeyDown(event);
    }
    showDropdown(results, info) {
        if (!this.settings.enable || this.relatedMode || document.activeElement !== this.element) return;
        this.relatedHeader?.remove();
        super.showDropdown(results, { ...info, existingTags: promptTagSet(this.element.value, this.settings.artistPrefix) });
    }
    async showRelated() {
        clearTimeout(this.relatedClickTimeout);
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
            const matchedTags = data.matchedTags?.length ? data.matchedTags : [data.matchedTag ?? range.tag];
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
                    this.element.setSelectionRange(before.length + 2 + value.length + 2, before.length + 2 + value.length + 2);
                }
                this.relatedRequest++;
                this.dropdownController.hide();
            });
            results.forEach((result, index) => {
                items[index].append(mkEl("span.yp-tagforge-plus-pill", {
                    textContent: `${(result.similarity * 100).toFixed(2)}%`,
                    title: matchedTags.length > 1 && result.sourceTag
                        ? `Пересечение по Жаккару с тегом ${result.sourceTag}.`
                        : "Пересечение публикаций по Жаккару. Порядок учитывает распространённость тегов.",
                }));
            });
            this.setRelatedHeading(range.tag, data.translate, data.error ?? (results.length
                ? `· ${results.length}` : "подходящих связей нет"), matchedTags);
            this.dropdownController.show(items, this.helper.getCursorOffset());
        } catch (error) {
            if (current()) this.relatedHeader.textContent = `Не удалось загрузить связанные теги: ${error.message}`;
        }
    }
    dismissDropdown() {
        this.relatedRequest = (this.relatedRequest ?? 0) + 1;
        this.relatedMode = false;
        this.relatedHeader?.remove();
        super.dismissDropdown();
    }
}
