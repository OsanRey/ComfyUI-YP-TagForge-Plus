const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
function el(tag, attrs = {}) { return { tag, ...attrs, children: [], append(item) { this.children.push(item); }, prepend(item) { this.children.unshift(item); }, replaceChildren(...items) { this.children = items; }, remove() {} }; }
class Textarea {
    constructor(text) { this.value = text; this.selectionStart = 5; this.scrollTop = 0; }
    focus() { context.document.activeElement = this; }
    setSelectionRange(start, end) { this.selectionStart = start; this.selectionEnd = end; }
    dispatchEvent() {}
}
class Base {
    constructor(element) {
        this.element = element; this.settings = { enable: true, delimiter: ',', addSpace: true };
        this.dropdownController = { dropdown: el(), visible: false, items: [],
            show(items) { this.items = items; this.visible = true; }, hide() { this.visible = false; } };
        this.helper = { getCursorOffset: () => ({ top: 10, left: 10 }) };
        this.textProcessor = { processTagValue: result => result.value.replace(/_/g, ' ') };
        this.dropdownRenderer = { createDropdownItems: (rows, info, click) => rows.map(result => {
            const item = el(); item.click = () => click({ target: { closest: () => null } }, result); return item;
        }) };
    }
    handleClick() { this.dropdownController.hide(); }
    handleInput() { this.dropdownController.hide(); }
    handleKeyDown(event) { if (event.key === 'Escape') this.dropdownController.hide(); }
    destroy() {}
}
let respond;
const context = { TagCompleter: Base, app: { ui: { settings: { getSettingValue: (key, fallback) => fallback } } },
    document: { activeElement: null }, mk_name: x => x, mkEl: el,
    api_post: () => new Promise(resolve => { respond = resolve; }),
    HTMLTextAreaElement: Textarea, Event: class {},
};
vm.createContext(context);
for (const file of ['prompt_format.js', 'plus_completer.js']) {
    const source = fs.readFileSync(path.join(__dirname, '../web', file), 'utf8').replace(/^import .*;\s*/gm, '').replace(/export /g, '');
    vm.runInContext(source, context);
}
vm.runInContext('globalThis.Plus = PlusCompleter;', context);
const data = { translate: 'оверсайз рубашка', results: [{ value: 'oversized_clothes', text: 'oversized_clothes', similarity: 0.3181 }] };
(async () => {
    const input = new Textarea('(oversized shirt:1.2), highres'); input.focus();
    const c = new context.Plus(input);
    const request = c.showRelated(); respond(data); await request;
    const sourceLink = c.relatedHeader.children.find(child => child.href);
    assert.equal(sourceLink.href, 'https://danbooru.donmai.us/wiki_pages/oversized_shirt');
    assert.equal(sourceLink.target, '_blank');
    assert.ok(c.relatedHeader.children.some(child => child.textContent === 'оверсайз рубашка'));
    assert.equal(c.dropdownController.items.length, 1);
    c.dropdownController.items[0].click();
    assert.equal(input.value, '(oversized shirt:1.2), oversized clothes, highres');
    assert.equal(input.value.slice(0, input.selectionStart), '(oversized shirt:1.2), oversized clothes, ', 'caret belongs after separator');
    assert.equal(c.dropdownController.visible, false);
    for (const tail of ['', ',', ',   ', ', next tag']) {
        input.value = `oversized shirt${tail}`; input.selectionStart = 3; input.focus();
        const inserting = c.showRelated(); respond(data); await inserting;
        c.dropdownController.items[0].click();
        assert.equal(input.value.slice(0, input.selectionStart), 'oversized shirt, oversized clothes, ');
        assert.equal(input.value.slice(input.selectionStart), tail.includes('next') ? 'next tag' : '');
    }
    input.value = 'oversized shirt, oversized clothes'; input.selectionStart = 3; input.focus();
    const again = c.showRelated(); respond(data); await again;
    c.dropdownController.items[0].click();
    assert.equal(input.value, 'oversized shirt, oversized clothes', 'do not duplicate existing related tags');
    assert.ok(input.selectionEnd > input.selectionStart, 'select existing tag instead');
    input.selectionStart = 3;
    const stale = c.showRelated(); c.handleKeyDown({ key: 'Escape' }); respond(data); await stale;
    assert.equal(c.dropdownController.visible, false, 'Escape must cancel pending related results');
    const editing = c.showRelated(); input.value = 'new text'; c.handleInput({}); respond(data); await editing;
    assert.equal(c.dropdownController.visible, false, 'stale results must not reopen after typing');
    console.log('Related tags: source preservation, insertion, duplicate selection and stale-response handling passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
