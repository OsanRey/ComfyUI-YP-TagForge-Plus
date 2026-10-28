const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = {};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, '../web/completer/virtual_dropdown_controller.js'), 'utf8')
    .replace(/^import .*;\s*/gm, '').replace('export class', 'globalThis.Controller = class'), context);
const c = Object.create(context.Controller.prototype);
let naturalHeight = 76;
c.itemHeight = 40;
c.viewport = { scrollTop: 640 };
c.container = { style: {} }; c.paddingTop = { style: {} }; c.paddingBottom = { style: {} };
c.allItems = Array.from({ length: 200 }); c.startIndex = 12; c.endIndex = 61;
c.visibleItems = [{ element: { style: {}, getBoundingClientRect: () => ({ height: naturalHeight }) } },
    { element: { style: {}, getBoundingClientRect: () => ({ height: 40 }) } }];
c.fitRowHeights();
assert.equal(c.itemHeight, 76, 'wrapped tags must increase the virtual row height');
assert.equal(c.visibleItems[1].element.style.height, '76px');
assert.equal(c.container.style.height, `${200 * 76}px`);
assert.equal(c.paddingTop.style.height, `${12 * 76}px`);
assert.equal(c.paddingBottom.style.height, `${138 * 76}px`);
assert.equal(c.viewport.scrollTop / c.itemHeight, 16, 'retain the same scroll anchor after expanding rows');
naturalHeight = 40;
c.fitRowHeights(true);
assert.equal(c.itemHeight, 40, 'widening popup should allow shorter rows again');
assert.equal(c.viewport.scrollTop, 640);
console.log('Wrapped rows, virtual offsets, scroll anchoring and resize remeasurement: passed');
