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
    handleClick() { this.dismissDropdown(); }
    handlePointerDown() { this.dismissDropdown(); }
    handleInput() { this.dismissDropdown(); }
    handleKeyDown(event) { if (event.key === 'Escape') this.dismissDropdown(); }
    dismissDropdown() { this.invalidateSearch(); this.dropdownController.hide(); }
    invalidateSearch() {}
    destroy() {}
}
let respond, requestCount = 0;
const clickTimers = new Map();
let nextTimer = 0;
const context = { TagCompleter: Base, app: { ui: { settings: { getSettingValue: (key, fallback) => fallback } } },
    document: new EventTarget(), AbortController, mk_name: x => x, mkEl: el,
    api_post: () => new Promise(resolve => { requestCount++; respond = resolve; }),
    HTMLTextAreaElement: Textarea, Event: class {},
    setTimeout: callback => { clickTimers.set(++nextTimer, callback); return nextTimer; },
    clearTimeout: id => clickTimers.delete(id),
};
vm.createContext(context);
for (const file of ['prompt_format.js', 'plus_completer.js']) {
    const source = fs.readFileSync(path.join(__dirname, '../web', file), 'utf8').replace(/^import .*;\s*/gm, '').replace(/export /g, '');
    vm.runInContext(source, context);
}
vm.runInContext('globalThis.Plus = PlusCompleter;', context);
const data = { translate: 'оверсайз рубашка', results: [{ value: 'oversized_clothes', text: 'oversized_clothes', similarity: 0.3181 }] };
const pointer = { isPrimary: true, button: 0, pointerId: 1, clientX: 10, clientY: 10 };
function sendPointer(type, coordinates = {}) {
    context.document.dispatchEvent(Object.assign(new Event(type), pointer, coordinates));
}
function click(c, detail = 1) {
    c.handlePointerDown(pointer);
    sendPointer('pointerup');
    c.handleClick({ detail });
}
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
    input.selectionStart = 3;
    const leaving = c.showRelated();
    c.dismissDropdown();
    respond(data); await leaving;
    assert.equal(c.dropdownController.visible, false, 'dismissing while loading must discard the related response');
    assert.equal(c.relatedMode, false);
    input.value = 'hugging from behind, highres'; input.selectionStart = 5;
    const aliasRequest = c.showRelated();
    respond({ matchedTag: 'hug_from_behind', results: [{ value: 'hug', text: 'hug', similarity: 0.15 }] });
    await aliasRequest;
    const aliasLink = c.relatedHeader.children.find(child => child.href);
    assert.equal(aliasLink.href, 'https://danbooru.donmai.us/wiki_pages/hug_from_behind');
    assert.ok(aliasLink.textContent.includes('hugging_from_behind → hug_from_behind'));
    c.dropdownController.items[0].click();
    assert.equal(input.value, 'hugging from behind, hug, highres');
    input.value = 'black and white'; input.selectionStart = 5;
    const multiple = c.showRelated();
    respond({ matchedTags: ['greyscale', 'monochrome'],
        results: [{ value: 'lineart', text: 'lineart', similarity: 0.15, sourceTag: 'monochrome' }] });
    await multiple;
    assert.deepEqual(Array.from(c.relatedHeader.children).filter(child => child.href).map(child => child.textContent),
        ['📖 greyscale', '📖 monochrome']);
    assert.match(c.dropdownController.items[0].children[0].title, /monochrome/);
    const beforeDrag = requestCount;
    input.setSelectionRange(0, input.value.length);
    click(c);
    assert.equal(requestCount, beforeDrag, 'the click event at the end of a drag must not start a lookup');
    assert.equal(clickTimers.size, 0);
    assert.equal(c.dropdownController.visible, false);
    input.setSelectionRange(5, 5);
    c.handlePointerDown(pointer);
    sendPointer('pointermove', { clientX: 40, clientY: 35 });
    sendPointer('pointerup', { clientX: 10, clientY: 10 });
    c.handleClick({ detail: 1 });
    assert.equal(clickTimers.size, 0, 'dragging stays suppressed if the caret collapses and the pointer returns');
    c.handlePointerDown(pointer);
    sendPointer('pointerup', { clientX: 85 });
    c.handleClick({ detail: 1 });
    assert.equal(clickTimers.size, 0, 'the release position detects movement even without a move event');
    c.handlePointerDown(pointer);
    sendPointer('pointercancel');
    c.handleClick({ detail: 1 });
    assert.equal(clickTimers.size, 0, 'a canceled pointer cannot open related tags');
    c.handlePointerDown(pointer);
    c.handleClick({ detail: 1, clientX: 85, clientY: 10 });
    assert.equal(clickTimers.size, 0, 'click coordinates detect a drag when pointerup is missing');
    c.handlePointerDown(pointer);
    c.handleClick({ detail: 1, clientX: 10, clientY: 10 });
    assert.equal(clickTimers.size, 1, 'a stationary click can arrive without pointerup');
    c.dismissDropdown();
    input.setSelectionRange(0, input.value.length);
    c.handleClick({ detail: 1 });
    assert.equal(clickTimers.size, 0, 'a click without pointer events still respects selected text');
    input.setSelectionRange(5, 5);
    c.handleClick({ detail: 0 });
    assert.equal(clickTimers.size, 1, 'a forwarded click can arrive without any pointer events');
    c.dismissDropdown();
    click(c);
    assert.equal(requestCount, beforeDrag, 'wait briefly for a potential second press');
    assert.equal(clickTimers.size, 1);
    c.handlePointerDown(pointer);
    assert.equal(clickTimers.size, 0, 'the next pointer press cancels the first click');
    input.setSelectionRange(0, 9);
    sendPointer('pointerup');
    c.handleClick({ detail: 2 });
    assert.equal(clickTimers.size, 0, 'a double-click used for word selection must not start a lookup');
    input.setSelectionRange(5, 5);
    click(c, 2);
    assert.equal(clickTimers.size, 0, 'double-click is ignored even before the browser updates selection');
    click(c);
    const [id, callback] = clickTimers.entries().next().value;
    clickTimers.delete(id);
    const lookup = callback();
    assert.equal(requestCount, beforeDrag + 1, 'a click that places the caret still looks up related tags');
    respond(data); await lookup;
    assert.equal(c.dropdownController.visible, true);
    console.log('Related tags: source preservation, insertion, duplicate selection and stale-response handling passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
