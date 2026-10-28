const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const pending = [], shown = [], errors = [];
const context = { AbortController, loadCSS() {}, console: { error: (...args) => errors.push(args) },
    api_post: (route, body, options) => new Promise(resolve => pending.push({ body, signal: options.signal, resolve })) };
vm.createContext(context);
for (const file of ['tag_completer_settings.js', 'text_processor.js', 'search_engine.js', 'tag_completer.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../web/completer', file), 'utf8')
        .replace(/^import .*;\s*/gm, '').replace(/export /g, ''), context);
}
vm.runInContext('globalThis.make = () => { const c = Object.create(TagCompleter.prototype); c.settings = TagCompleterSettings; c.searchEngine = new SearchEngine(); c.textProcessor = new TextProcessor(); return c; };', context);
const c = context.make();
c.element = { value: 'on', selectionStart: 2, selectionEnd: 2 };
c.helper = { getBeforeCursor: () => c.element.value.slice(0, c.element.selectionStart) };
let hidden = 0, scheduled = 0;
c.dropdownController = { hide() { hidden++; } };
c.showDropdown = (results, info) => shown.push({ results, term: info.term });
c.debouncedUpdate = () => scheduled++;
function type(text) { c.element.value = text; c.element.selectionStart = c.element.selectionEnd = text.length; c.handleInput({}); }
(async () => {
    const first = c.update();
    type('onbe');
    const latest = c.update();
    assert.equal(pending.length, 2, 'do not drop the latest query while an older request is pending');
    assert.equal(pending[0].signal.aborted, true);
    assert.equal(pending[1].body.term, 'onbe');
    pending[1].resolve([{ value: 'on_bed' }]); await latest;
    const hidesAfterLatest = hidden;
    pending[0].resolve([]); await first;
    assert.equal(shown.at(-1).term, 'onbe');
    assert.equal(shown.at(-1).results[0].value, 'on_bed');
    assert.equal(hidden, hidesAfterLatest, 'an older response must not close the newer suggestions');
    type('blue'); const delayed = c.update();
    type('blueeyes');
    pending[2].resolve([{ value: 'blue_hair' }]); await delayed;
    assert.equal(shown.length, 1, 'typing invalidates old results before the debounce fires');
    const exact = c.update();
    pending[3].resolve([{ value: 'blue_eyes' }]); await exact;
    assert.equal(shown.at(-1).results[0].value, 'blue_eyes');
    type('onbe'); const beforeClick = c.update();
    c.handleClick({}); const hidesAfterClick = hidden;
    pending[4].resolve([{ value: 'on_bed' }]); await beforeClick;
    assert.equal(hidden, hidesAfterClick, 'stale autocomplete must not interfere with a related-tag panel');
    assert.equal(shown.length, 2);
    assert.ok(scheduled >= 4);
    assert.equal(errors.length, 0);
    console.log('Search updates: fast typing, omitted separators, out-of-order responses and click invalidation passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
