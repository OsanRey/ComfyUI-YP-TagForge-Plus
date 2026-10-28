const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../web/prompt_format.js'), 'utf8').replace(/export /g, '');
class Textarea {
    constructor() { this._value = ''; this.selectionStart = 0; this.scrollTop = 10; this.events = []; }
    get value() { return this._value; }
    set value(value) { this._value = value; }
    setSelectionRange(a, b) { this.selectionStart = a; this.selectionEnd = b; }
    dispatchEvent(event) { this.events.push(event.type); }
}
const c = { HTMLTextAreaElement: Textarea, Event: class { constructor(type) { this.type = type; } } };
vm.createContext(c); vm.runInContext(source, c);
assert.equal(c.formatPrompt('  1girl,,  blue eyes , ,highres  '), '1girl, blue eyes, highres, ');
assert.equal(c.formatPrompt('a,,b,', { trailingComma: false }), 'a, b');
assert.equal(c.formatPrompt('\n  1girl,solo\n\n highres,,\n'), '1girl, solo, \n\nhighres, ');
assert.equal(c.formatPrompt('(blue eyes,red hair:1.2),, <lora:model:0.7>, __outfit__, {a|b}'), '(blue eyes,red hair:1.2), <lora:model:0.7>, __outfit__, {a|b}, ');
assert.equal(c.formatPrompt('name_\\(series\\),, highres'), 'name_\\(series\\), highres, ');
assert.equal(c.formatPrompt('a\\,b,, c'), 'a\\,b, c, ');
assert.equal(c.shouldFormat('0,0,1,1', { inputName: 'block_vector' }), false);
assert.equal(c.shouldFormat('{"a":1,"b":2}', { inputName: 'json' }), false);
assert.equal(c.shouldFormat('a,b', { nodeType: 'Markdown' }), false);
assert.equal(c.shouldFormat('1girl,solo', { inputName: 'prompt_text' }), true);
assert.equal(c.shouldFormat('bra, red bra', { inputName: 'prompt_text' }), true);
assert.equal(c.tagAtCursor('1girl, (oversized shirt:1.2), solo', 17).tag, 'oversized_shirt');
assert.equal(c.tagAtCursor('foo_\\(series\\), highres', 5).tag, 'foo_(series)');
assert.equal(c.tagAtCursor('<lora:model:0.7>', 6), null);
assert.equal(c.tagAtCursor('__outfit__', 4), null);
const present = c.promptTagSet('1girl, (blue eyes:1.2), foo_\\(series\\), highres');
assert.ok(present.has('blue_eyes'));
assert.ok(present.has('foo_(series)'));
assert.ok(present.has('1girl'));
assert.equal(present.has('girl'), false, 'only whole tags should be marked as present');
const element = new Textarea(); element.value = 'a,b';
c.applyTextareaText(element, 'a, b, ');
assert.equal(element.value, 'a, b, ');
assert.deepEqual(element.events, ['input', 'change']);
assert.equal(element.scrollTop, 10);
assert.equal(c.applyTextareaText(element, 'a, b, '), false);
console.log('Formatting, syntax preservation, cursor tags and Vue input events: passed');
