const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
let removed = false;
const context = { window: { innerWidth: 1400, innerHeight: 1000, scrollX: 0, scrollY: 0 },
    mkEl: () => ({ style: {}, append() {}, remove() { removed = true; } }) };
vm.createContext(context);
for (const file of ['dropdown_layout.js', 'virtual_dropdown_controller.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../web/completer', file), 'utf8')
        .replace(/^import .*;\s*/gm, '').replace(/export /g, '')
        + (file.includes('controller') ? '\nglobalThis.Controller = VirtualDropdownController;' : ''), context);
}
const c = Object.create(context.Controller.prototype);
const clone = width => ({ style: {}, children: [{ style: {}, classList: { contains: () => true } }],
    getBoundingClientRect() {
        assert.equal(this.style.flexWrap, 'nowrap');
        assert.equal(this.children[0].style.minWidth, '260px');
        return { width };
    } });
c.allItems = [600, 980].map(width => ({ element: { cloneNode: () => clone(width) } }));
c.dropdown = { style: {}, append() {}, querySelector: () => null,
    get clientWidth() { return parseFloat(this.style.width); } };
c.viewport = { style: {} }; c.settings = { dropdownWidth: 800 }; c.itemHeight = 40;
c.fitRowHeights = () => {};
c.updateDropdownPosition({ top: 100, left: 1200 });
assert.equal(c.dropdown.style.width, '1004px', 'expand for the widest result plus scrollbar');
assert.equal(c.dropdown.style.left, '386px', 'keep expanded popup on screen');
assert.ok(removed, 'measurement clones must be removed');
context.window.innerWidth = 900;
c.updateDropdownPosition({ top: 100, left: 200 });
assert.equal(c.dropdown.style.width, '880px', 'screen bounds take priority over unwrapped width');
c.contentWidth = null;
c.allItems = [{ element: { cloneNode: () => clone(500) } }];
c.updateDropdownPosition({ top: 100, left: 10 });
assert.equal(c.dropdown.style.width, '800px', 'short lists retain configured baseline width');
console.log('Automatic popup width, hidden row measurement, baseline and viewport bounds: passed');
