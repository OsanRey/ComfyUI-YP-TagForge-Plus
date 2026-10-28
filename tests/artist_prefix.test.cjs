const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = {};
vm.createContext(context);
for (const file of ['completer/tag_completer_settings.js', 'completer/text_processor.js', 'completer/search_engine.js', 'prompt_format.js']) {
    const source = fs.readFileSync(path.join(__dirname, '../web', file), 'utf8').replace(/^import .*;\s*/gm, '').replace(/export /g, '');
    vm.runInContext(source, context);
}
vm.runInContext('globalThis.processor = new TextProcessor(); globalThis.search = new SearchEngine(); globalThis.options = TagCompleterSettings;', context);
const artist = { value: 'some_artist', categoryName: 'Artist', category: '1' };
const plain = { customPrefixes: [], fullTerm: 'some' };
assert.equal(context.processor.createInsertValue(artist, plain, ''), '@some artist, ');
assert.equal(context.processor.processTagValue({ ...artist, categoryName: 'Character' }, plain), 'some artist');
assert.equal(context.processor.processTagValue({ ...artist, value: '@some_artist' }, plain), '@some artist');
assert.equal(context.processor.processTagValue(artist, { customPrefixes: ['@'] }), '@ some artist', 'explicit custom prefix must not duplicate @');
const typed = context.search.parseSearchTerm('@wlop');
assert.equal(typed.term, 'wlop'); assert.equal(typed.fullTerm, '@wlop');
assert.ok(typed.categoryFilters.includes('Artist'));
assert.equal(context.processor.getReplaceLength(typed), -5, 'replace typed @ together with the partial tag');
assert.ok(context.promptTagSet('(@wlop:1.2), highres', '@').has('wlop'));
context.options.artistPrefix = '';
assert.equal(context.processor.processTagValue(artist, plain), 'some artist');
context.options.artistPrefix = 'by ';
assert.equal(context.processor.processTagValue(artist, plain), 'by some artist');
assert.equal(context.search.parseSearchTerm('by some').term, 'some');
assert.ok(context.promptTagSet('by some artist, highres', 'by ').has('some_artist'));
console.log('Artist prefix: category-only insertion, custom/disabled prefixes, typed @, deduplication and existing tags passed');
