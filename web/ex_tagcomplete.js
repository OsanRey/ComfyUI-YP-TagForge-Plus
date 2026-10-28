import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";
import { settings } from "./settings.js";
import { PlusCompleter } from "./plus_completer.js";
import { findTextareaFromWidget, mk_name, api_post } from "./utils.js";
import { formatPrompt, shouldFormat, applyTextareaText } from "./prompt_format.js";

const attached = new WeakMap(), instances = new Map(), mounted = new WeakSet();
const value = (key, fallback) => app.ui.settings.getSettingValue(mk_name(key), fallback);
const enabled = () => value("enable", true);

function nodeInfo(element) {
    const row = element.closest?.('[data-testid="node-widget"]');
    const host = element.closest?.('[data-node-id]');
    const id = host?.getAttribute("data-node-id");
    const node = app.graph?.getNodeById?.(id);
    return {
        nodeType: node?.comfyClass ?? node?.type ?? "",
        inputName: element.getAttribute("data-widget-name") || element.name
            || row?.querySelector("label")?.textContent || "",
    };
}

function eligible(element, info) {
    return element instanceof HTMLTextAreaElement && !element.readOnly && !element.disabled
        && !/code|script|expression|block_vector|json|yaml|resolution|preview|filename|path/i.test(info.inputName ?? "")
        && !/Power Puter|Note|Markdown/i.test(info.nodeType ?? "");
}

function attach(element, info = nodeInfo(element)) {
    if (attached.has(element) || !eligible(element, info)) return;
    const completer = new PlusCompleter(element);
    attached.set(element, info); instances.set(element, completer);
    const blur = () => {
        if (!enabled() || !value("formatEnabled", true) || !value("formatOnBlur", true)) return;
        if (completer.dropdownController.isMouseInteracting()) return;
        if (shouldFormat(element.value, info)) applyTextareaText(element, formatPrompt(element.value, {
            trailingComma: value("trailingComma", true), trim: value("trimSpaces", true),
        }));
    };
    completer.plusBlur = blur;
    element.addEventListener("blur", blur);
    if (element.isConnected) mounted.add(element);
}

// Disable competing handlers through their own settings; preserve source files.
const competitors = ["jupo.TagForge.enable", "AutocompletePlus.Autocompletion.Enable",
    "AutocompletePlus.RelatedTags.Enable", "AutocompletePlus.AutoFormatter.EnableAutoFormat"];
const backupKey = "yp.TagForgePlus.previousExtensions";
async function coordinateExtensions(active) {
    const store = app.ui.settings;
    let backup = {};
    try { backup = JSON.parse(localStorage.getItem(backupKey) ?? "{}"); } catch {}
    for (const id of competitors) {
        const current = store.getSettingValue(id);
        if (current == null) continue;
        if (active && current !== false) {
            if (!(id in backup)) backup[id] = current;
            await store.setSettingValue(id, false);
        } else if (!active && id in backup && current === false) {
            await store.setSettingValue(id, backup[id]);
            delete backup[id];
        }
    }
    localStorage.setItem(backupKey, JSON.stringify(backup));
}

const inheritedEnableChange = settings.enable.onChange;
settings.enable.onChange = async active => {
    await inheritedEnableChange(active);
    await coordinateExtensions(active);
    if (!active) for (const completer of instances.values()) completer.dropdownController.hide();
};

function setting(key, name, defaultValue, type = "boolean", attrs) {
    return { id: mk_name(key), name, category: ["YP TagForge Plus", "Форматирование и связи", name],
        type, defaultValue, ...(attrs ? { attrs } : {}) };
}

await settings.load();
app.registerExtension({
    name: "YP.TagForgePlus",
    settings: [...settings.getList(),
        setting("formatEnabled", "Форматирование промпта", true),
        setting("formatOnBlur", "Форматировать при выходе из поля", true),
        setting("trailingComma", "Запятая и пробел в конце строки", true),
        setting("trimSpaces", "Убирать пустые строки по краям", true),
        setting("relatedEnabled", "Связанные теги по клику", true),
        setting("relatedCount", "Количество связанных тегов", 20, "slider", { min: 5, max: 100, step: 5 }),
    ],
    init() {
        const original = ComfyWidgets.STRING;
        ComfyWidgets.STRING = function(node, name, data) {
            const result = original.apply(this, arguments);
            if (data?.[1]?.multiline && data[1].tagcomplete !== false && data[1]["pysssss.autocomplete"] !== false) {
                const element = findTextareaFromWidget(result?.widget);
                if (element) attach(element, { nodeType: node.comfyClass ?? node.type, inputName: name });
            }
            return result;
        };
        document.addEventListener("focusin", event => {
            const element = event.target;
            if (!(element instanceof HTMLTextAreaElement)) return;
            if (!element.matches(".comfy-multiline-input") && !element.closest(
                '.lg_domwidget,.comfyui-dom-widget,.dom-widget,[data-testid="node-widget"],[data-node-id]')) return;
            attach(element);
        });
        document.addEventListener("keydown", event => {
            if (!enabled() || !value("formatEnabled", true) || !event.altKey || !event.shiftKey || event.code !== "KeyF") return;
            const element = event.target;
            if (!attached.has(element) || !eligible(element, attached.get(element))) return;
            event.preventDefault(); event.stopPropagation();
            applyTextareaText(element, formatPrompt(element.value, {
                trailingComma: value("trailingComma", true), trim: value("trimSpaces", true),
            }));
        }, true);
        const observer = new MutationObserver(() => {
            for (const [element, completer] of instances) {
                if (element.isConnected) mounted.add(element);
                else if (mounted.has(element)) {
                    element.removeEventListener("blur", completer.plusBlur);
                    completer.destroy(); instances.delete(element); attached.delete(element);
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    },
    async setup() {
        await coordinateExtensions(enabled());
        if (!enabled()) return;
        await api_post("load_main", { filename: value("mainTagsFile", settings.mainFile.defaultValue) });
        await api_post("load_extra", { filename: value("extraTagsFile", settings.extraFile.defaultValue) });
        await api_post("load_translate", { filename: value("translateFile", settings.translateFile.defaultValue) });
    },
});
