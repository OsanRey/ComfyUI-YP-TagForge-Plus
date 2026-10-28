import { mk_name, api_get, api_post } from "./utils.js";
import { TagCompleter } from "./completer/tag_completer.js";

// ==============================================
// 設定オブジェクト
// ==============================================

export const settings = {
    // 登録用のリストを返す
    getList() {
        return Object.values(this)
            .filter(v => v && typeof v === "object" && !Array.isArray(v))
            .slice()
            .reverse();
    },

    // APIからファイル一覧を読み込み、設定を更新
    async load() {
        try {
            const mainFiles = await api_get("get_main_files");
            const extraFiles = await api_get("get_extra_files");
            const translateFiles = ["None"].concat(await api_get("get_translate_files").then(files => files.filter(f => f !== "None")));

            this.mainFile.options = mainFiles;
            this.mainFile.defaultValue = mainFiles.includes("danbooru_e621_merged.csv") ? "danbooru_e621_merged.csv" : mainFiles[0] ?? "";

            this.extraFile.options = ["None", ...extraFiles];
            this.extraFile.defaultValue = extraFiles[0] ?? "None";

            this.translateFile.options = translateFiles;
            this.translateFile.defaultValue = translateFiles.includes("Ru_translated.csv") ? "Ru_translated.csv" : "None";
        } catch (error) {
            console.warn("[TagComplete] Failed to load settings:", error);
        }
    },

    // ------------------------------------------
    // 以下、各種設定
    // ------------------------------------------
    dropdownWidth: {
        name: "Ширина окна тегов (px)",
        id: mk_name("dropdownWidth"),
        category: ["YP TagForge Plus", "Размер окна", "Ширина окна тегов (px)"],
        type: "slider", defaultValue: 720,
        attrs: { min: 320, max: 1600, step: 20 },
        onChange: value => TagCompleter.updateSetting("dropdownWidth", Number(value)),
    },
    enable: {
        name: "Enable",
        id: mk_name("enable"),
        category: ["YP TagForge Plus", "General", "Enable"],
        type: "boolean",
        defaultValue: true,
        onChange: async (value) => {
            TagCompleter.updateSetting("enable", value);
            await api_post("toggle_enable", { value: value })
        },
    },

    mainFile: {
        name: "Choose Main File",
        id: mk_name("mainTagsFile"),
        category: ["YP TagForge Plus", "Tag Files", "Choose Main File"],
        type: "combo",
        defaultValue: "",
        options: [],
        onChange: async (value) => {
            await api_post("load_main", { filename: value });
        },
    },

    extraFile: {
        name: "Choose Extra File",
        id: mk_name("extraTagsFile"),
        category: ["YP TagForge Plus", "Tag Files", "Choose Extra File"],
        type: "combo",
        defaultValue: "",
        options: [],
        onChange: async (value) => {
            await api_post("load_extra", { filename: value });
        },
    },

    translateFile: {
        name: "Choose Translate File",
        id: mk_name("translateFile"),
        category: ["YP TagForge Plus", "Tag Files", "Choose Translate File"],
        type: "combo",
        defaultValue: "None",
        options: ["None"],
        onChange: async (value) => {
            await api_post("load_translate", { filename: value });
        },
    },

    delimiter: {
        name: "Delimiter",
        id: mk_name("delimiter"),
        category: ["YP TagForge Plus", "Completion", "Delimiter"],
        type: "combo",
        defaultValue: ",",
        options: [
            { text: "Comma (,)", value: "," },
            { text: "Period (.)", value: "." },
            { text: "None", value: "" },
        ],
        onChange: (value) => {
            TagCompleter.updateSetting("delimiter", value);
        },
    },

    addSpace: {
        name: "Add 'Space' after delimiter",
        id: mk_name("insertSpace"),
        category: ["YP TagForge Plus", "Completion", "Add Space after delimiter"],
        type: "boolean",
        defaultValue: true,
        onChange: (value) => {
            TagCompleter.updateSetting("addSpace", value);
        },
    },

    suggestionCount: {
        name: "Max Suggestions to Display",
        id: mk_name("suggestionCount"),
        category: ["YP TagForge Plus", "Completion", "Max Suggestions to Display"],
        type: "slider",
        defaultValue: 20,
        attrs: { min: 0, max: 200, step: 1 },
        tooltip: "0: Show all avaliable suggestion.",
        onChange: async (value) => {
            await api_post("set_suggestion_count", { value: value });
        },
    },

    wikiLink: {
        name: "Кнопка 📖 — страница тега",
        id: mk_name("wikiLink"),
        category: ["YP TagForge Plus", "Completion", "Wiki Link Button"],
        type: "boolean",
        defaultValue: true,
        tooltip: "Показать книжку для перехода на страницу тега.",
        onChange: (value) => {
            TagCompleter.updateSetting("wikiLink", value);
        },
    },

    artistPrefix: {
        name: "Префикс артистов",
        id: mk_name("artistPrefix"),
        category: ["YP TagForge Plus", "Completion", "Префикс артистов"],
        type: "text", defaultValue: "@",
        tooltip: "Автоматически добавляется перед тегом Artist при вставке. Пустое поле отключает префикс.",
        onChange: value => TagCompleter.updateSetting("artistPrefix", String(value ?? "")),
    },
    replaceUnderbar: {
        name: "Replace '_' with 'Space'",
        id: mk_name("replaceUnderbar"),
        category: ["YP TagForge Plus", "Completion", "Replace Underscore"],
        type: "boolean",
        defaultValue: true,
        onChange: (value) => {
            TagCompleter.updateSetting("replaceUnderbar", value);
        },
    },

    delay: {
        name: "Completion Delay (ms)",
        id: mk_name("completionDelay"),
        category: ["YP TagForge Plus", "Completion", "Completion Delay"],
        type: "slider",
        defaultValue: 50,
        attrs: { min: 0, max: 200, step: 10 },
        onChange: (value) => {
            TagCompleter.updateSetting("delay", value);
        },
    },

    embeddings: {
        name: "Enable Embeddings",
        id: mk_name("enableEmbeddings"),
        category: ["YP TagForge Plus", "Sources", "Enable Embeddings"],
        type: "boolean",
        defaultValue: false,
        onChange: async (value) => {
            await api_post("load_embeddings", { value : value });
        },
    },

    loras: {
        name: "Enable LoRAs",
        id: mk_name("enableLoras"),
        category: ["YP TagForge Plus", "Sources", "Enable LoRAs"],
        type: "boolean",
        defaultValue: false,
        onChange: async (value) => {
            await api_post("load_loras", { value: value });
        },
    },

    wildcards: {
        name: "Enable Wildcards",
        id: mk_name("enableWildcards"),
        category: ["YP TagForge Plus", "Sources", "Enable Wildcards"],
        type: "boolean",
        defaultValue: true,
        onChange: async (value) => {
            await api_post("load_wildcards", { value: value });
        },
    },

    restirctAlias: {
        name: "Restrict Alias",
        id: mk_name("restrict Alias"),
        category: ["YP TagForge Plus", "Completion", "Restrict Alias"],
        type: "boolean",
        defaultValue: false,
        tooltip: "If enabled, aliases are only sohwn when an exact match is found.",
        onChange: async (value) => {
            await api_post("set_restrict_alias", { value: value });
        },
    },

}
