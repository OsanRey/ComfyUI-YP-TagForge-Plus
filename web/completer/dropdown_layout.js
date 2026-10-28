// Document-pixel coordinates, constrained to the visible browser viewport.
export function dropdownLayout({ position, viewportWidth, viewportHeight, scrollX = 0, scrollY = 0,
    width = 720, headerHeight = 0, contentHeight = 0 }) {
    const margin = 10;
    const popupWidth = Math.min(Math.max(320, Number(width) || 720), Math.max(0, viewportWidth - margin * 2));
    const anchorTop = Number(position.top ?? scrollY + margin);
    const lineHeight = Math.max(16, Number(position.lineHeight) || 24);
    const below = Math.max(0, scrollY + viewportHeight - margin - anchorTop);
    const above = Math.max(0, anchorTop - lineHeight - scrollY - margin);
    const desired = headerHeight + contentHeight + 2;
    const openAbove = below < desired && above > below;
    const height = Math.min(desired, openAbove ? above : below);
    const left = Math.max(scrollX + margin, Math.min(Number(position.left ?? scrollX + margin),
        scrollX + viewportWidth - popupWidth - margin));
    const top = Math.max(scrollY + margin, openAbove ? anchorTop - lineHeight - height : anchorTop);
    return { width: popupWidth, left, top, listHeight: Math.max(0, height - headerHeight - 2) };
}
