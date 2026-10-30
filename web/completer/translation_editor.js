import { mkEl, api_post } from "../utils.js";

export function addTranslationEditor(item, result) {
    if (!result.value || !["danbooru", "e621"].includes(result.site)) return;
    const pencil = mkEl("button.yp-tagforge-plus-edit-translation", {
        type: "button", textContent: "✎", title: "Изменить перевод в словаре",
        "aria-label": `Изменить перевод ${result.value}`,
        onmousedown: event => { event.preventDefault(); event.stopPropagation(); },
        onclick: event => { event.stopPropagation(); openEditor(); },
    });
    item.append(pencil);
    function openEditor() {
        if (item.querySelector(".yp-tagforge-plus-translation-editor")) return;
        const previousFocus = document.activeElement;
        const input = mkEl("input", { type: "text", value: result.translate ?? "", maxlength: "2000",
            "aria-label": `Перевод ${result.value}` });
        const error = mkEl("span.yp-tagforge-plus-edit-error", { role: "status" });
        const close = () => { form.remove(); previousFocus?.focus({ preventScroll: true }); resize(); };
        const save = mkEl("button", { type: "submit", textContent: "✓", title: "Сохранить" });
        const cancel = mkEl("button", { type: "button", textContent: "×", title: "Отмена", onclick: close });
        const form = mkEl("form.yp-tagforge-plus-translation-editor", {
            onclick: event => event.stopPropagation(),
            onmousedown: event => event.stopPropagation(),
            onkeydown: event => {
                event.stopPropagation();
                if (event.key === "Escape") { event.preventDefault(); if (!save.disabled) close(); }
            },
            onsubmit: async event => {
                event.preventDefault(); event.stopPropagation();
                if (save.disabled) return;
                save.disabled = true; cancel.disabled = true; input.disabled = true; error.textContent = "";
                try {
                    const data = await api_post("save_translation", { tag: result.value, translation: input.value });
                    result.translate = data.translation;
                    const labels = [...item.querySelectorAll(".yp-tagforge-plus-translation")];
                    const label = mkEl("span.yp-tagforge-plus-pill.yp-tagforge-plus-translation", {
                        textContent: result.translate,
                    });
                    if (labels.length) labels[0].replaceWith(label);
                    else item.querySelector(".yp-tagforge-plus-text").after(label);
                    labels.slice(1).forEach(old => old.remove());
                    close();
                } catch (failure) {
                    error.textContent = failure.message;
                    save.disabled = false; cancel.disabled = false; input.disabled = false;
                    input.focus(); resize();
                }
            },
        }, [input, save, cancel, error]);
        item.append(form);
        input.focus(); input.select(); resize();
    }
    function resize() {
        item.dispatchEvent(new CustomEvent("yp-translation-resize", { bubbles: true }));
    }
}
