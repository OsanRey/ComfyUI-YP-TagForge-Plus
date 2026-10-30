const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let request, fail = false, resized = 0, focused = 0;
class Element {
    constructor(selector, attrs = {}, children = []) {
        this.selector = selector; Object.assign(this, attrs); this.children = [];
        this.value = attrs.value ?? ''; this.append(...children);
    }
    append(...items) { for (const item of items) { item.parent = this; this.children.push(item); } }
    remove() { if (this.parent) this.parent.children.splice(this.parent.children.indexOf(this), 1); }
    replaceWith(item) { const p = this.parent, i = p.children.indexOf(this); item.parent = p; p.children[i] = item; }
    after(item) { item.parent = this.parent; this.parent.children.splice(this.parent.children.indexOf(this) + 1, 0, item); }
    querySelectorAll(selector) { return this.children.filter(child => child.selector.split('.').includes(selector.slice(1))); }
    querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
    focus() { context.document.activeElement = this; focused++; }
    select() { this.selected = true; }
    dispatchEvent() { resized++; }
}
const event = () => ({ prevented: false, stopped: false, preventDefault() { this.prevented = true; }, stopPropagation() { this.stopped = true; } });
const context = { document: { activeElement: { focus() { focused++; } } }, CustomEvent: class {},
    mkEl: (...args) => new Element(...args),
    api_post: async (route, body) => { request = { route, body }; if (fail) throw Error('Read only'); return { translation: body.translation.trim() }; } };
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, '../web/completer/translation_editor.js'), 'utf8')
    .replace(/^import .*;\s*/gm, '').replace(/export /g, ''), context);
(async () => {
    const item = new Element('div', {}, [new Element('div.yp-tagforge-plus-text'), new Element('span.yp-tagforge-plus-translation')]);
    const result = { site: 'danbooru', value: 'shirt', translate: 'old' };
    context.addTranslationEditor(item, result);
    const pencil = item.querySelector('.yp-tagforge-plus-edit-translation');
    const click = event(); pencil.onclick(click); assert.ok(click.stopped);
    let form = item.querySelector('.yp-tagforge-plus-translation-editor');
    const [input, save, cancel, error] = form.children;
    assert.equal(input.value, 'old'); assert.ok(input.selected);
    input.value = 'рубашка';
    await form.onsubmit(event());
    assert.equal(request.route, 'save_translation'); assert.equal(request.body.tag, 'shirt');
    assert.equal(result.translate, 'рубашка');
    assert.equal(item.querySelector('.yp-tagforge-plus-translation').textContent, 'рубашка');
    assert.equal(item.querySelector('.yp-tagforge-plus-translation-editor'), null);
    pencil.onclick(event()); form = item.querySelector('.yp-tagforge-plus-translation-editor');
    fail = true; form.children[0].value = 'new'; await form.onsubmit(event());
    assert.equal(form.children[3].textContent, 'Read only');
    assert.equal(form.children[1].disabled, false); assert.equal(result.translate, 'рубашка');
    const escape = event(); escape.key = 'Escape'; form.onkeydown(escape);
    assert.ok(escape.stopped && escape.prevented); assert.equal(item.querySelector('.yp-tagforge-plus-translation-editor'), null);
    assert.ok(resized >= 4 && focused >= 4);
    const wildcard = new Element('div'); context.addTranslationEditor(wildcard, { site: null, value: 'x' });
    assert.equal(wildcard.children.length, 0);
    console.log('Translation editor: inline save, cancellation, error recovery and event isolation passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
