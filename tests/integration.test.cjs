const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
class Textarea {
    constructor() { this.value = '1girl,,solo'; this.selectionStart = 0; this.scrollTop = 0; this.isConnected = true; this.handlers = {}; }
    addEventListener(name, handler) { this.handlers[name] = handler; }
    removeEventListener(name) { delete this.handlers[name]; }
    getAttribute() { return null; }
    matches() { return true; }
    closest() { return null; }
    setSelectionRange() {}
    dispatchEvent() { this.notified = true; }
}
const values = new Map([
    ['jupo.TagForge.enable', true], ['AutocompletePlus.Autocompletion.Enable', true],
    ['AutocompletePlus.RelatedTags.Enable', true], ['AutocompletePlus.AutoFormatter.EnableAutoFormat', true],
]);
const listeners = {}, storage = new Map(), writes = [], live = [];
const settings = { enable: { onChange: async () => {} }, mainFile: { defaultValue: 'merged.csv' },
    extraFile: { defaultValue: 'extra.csv' }, translateFile: { defaultValue: 'ru.csv' },
    load: async () => {}, getList: () => [] };
const c = { HTMLTextAreaElement: Textarea, Event: class {},
    document: { body: {}, addEventListener(name, fn) { listeners[name] = fn; } },
    MutationObserver: class { constructor(fn) { c.cleanup = fn; } observe() {} },
    settings, mk_name: x => `yp.TagForgePlus.${x}`, api_post: async (route, data) => { writes.push({ route, data }); },
    findTextareaFromWidget: w => w.inputEl,
    localStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) },
    app: { ui: { settings: { getSettingValue: (id, fallback) => values.get(id) ?? fallback,
        setSettingValue: async (id, value) => { values.set(id, value); } } },
        registerExtension(ext) { c.extension = ext; } },
    ComfyWidgets: { STRING: () => ({ widget: { inputEl: new Textarea() } }) },
    PlusCompleter: class { constructor(element) { this.element = element; this.dropdownController = { isMouseInteracting: () => false, hide() {} }; live.push(this); }
        destroy() { this.destroyed = true; } },
};
vm.createContext(c);
vm.runInContext(fs.readFileSync(path.join(__dirname, '../web/prompt_format.js'), 'utf8').replace(/export /g, ''), c);
const source = fs.readFileSync(path.join(__dirname, '../web/ex_tagcomplete.js'), 'utf8').replace(/^import .*;\s*/gm, '');
(async () => {
    await vm.runInContext(`(async()=>{${source}})()`, c);
    c.extension.init(); await c.extension.setup();
    for (const id of ['jupo.TagForge.enable', 'AutocompletePlus.Autocompletion.Enable', 'AutocompletePlus.RelatedTags.Enable', 'AutocompletePlus.AutoFormatter.EnableAutoFormat']) assert.equal(values.get(id), false);
    assert.equal(writes.length, 3);
    const modern = new Textarea(); listeners.focusin({ target: modern });
    modern.handlers.blur(); assert.equal(modern.value, '1girl, solo, '); assert.equal(modern.notified, true);
    const preview = new Textarea(); preview.readOnly = true; listeners.focusin({ target: preview });
    assert.equal(live.length, 1, 'readonly previews must not receive a completer or formatter');
    const { widget } = c.ComfyWidgets.STRING({ type: 'Prompt' }, 'code', ['STRING', { multiline: true }]);
    assert.equal(widget.inputEl.handlers.blur, undefined, 'code widgets must be skipped');
    modern.isConnected = false; c.cleanup(); assert.equal(live[0].destroyed, true);
    await settings.enable.onChange(false);
    assert.equal(values.get('jupo.TagForge.enable'), true);
    assert.equal(values.get('AutocompletePlus.RelatedTags.Enable'), true);
    console.log('Modern field attachment, readonly/code exclusions, formatting events, cleanup and extension coordination: passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
