import { mkEl } from "../utils.js";
import { TagCompleterSettings } from "./tag_completer_settings.js";
import { dropdownLayout } from "./dropdown_layout.js";

// ==============================================
// 仮想スクロール対応ドロップダウンコントローラ
// ==============================================

export class VirtualDropdownController {
    constructor(textareaElement) {
        this.settings = TagCompleterSettings;
        
        this.textareaElement = textareaElement;
        this.dropdown = mkEl("div.yp-tagforge-plus");
        this.viewport = mkEl("div.yp-tagforge-plus-viewport");
        this.container = mkEl("div.yp-tagforge-plus-container");
        this.paddingTop = mkEl("div.yp-tagforge-plus-padding-top");
        this.paddingBottom = mkEl("div.yp-tagforge-plus-padding-bottom");
        
        // 仮想スクロール設定
        this.itemHeight = 40; // 各アイテムの固定高さ
        this.visibleCount = 50; // 表示するアイテム数
        this.bufferSize = 3; // 前後の余剰アイテム数
        
        // 状態管理
        this.allItems = [];
        this.visibleItems = [];
        this.startIndex = 0;
        this.endIndex = 0;
        this.currentIndex = 0;
        this.isMousedownOnDropdown = false;
        this.isHoveringOnDropdown = false;
        
        // スクロール制御用フラグ
        this.isUserScrolling = false;
        this.userScrollTimeout = null;
        this.lastScrollTop = 0;
        
        this.setupDOM();
        this.setupEventListeners();
    }

    // ------------------------------------------
    // DOM構造を構築
    // ------------------------------------------
    setupDOM() {
        // ドロップダウン構造: dropdown > viewport > container
        this.container.append(this.paddingTop);
        this.container.append(...this.visibleItems);
        this.container.append(this.paddingBottom);
        
        this.viewport.append(this.container);
        this.dropdown.append(this.viewport);
        
        // スタイル設定 - 初期値のみ設定
        this.viewport.style.overflow = "auto";
        this.viewport.style.overflowX = "hidden";
        this.viewport.style.overflowAnchor = "none"; // Chrome用
    }

    // ------------------------------------------
    // イベントリスナー設定
    // ------------------------------------------
    setupEventListeners() {
        // スクロールイベント
        this.viewport.addEventListener("scroll", (...args) => this.handleScroll(...args));
        
        // ユーザースクロール検出
        this.viewport.addEventListener("wheel", (...args) => this.handleWheel(...args), { passive: true });
        this.viewport.addEventListener("touchstart", (...args) => this.handleTouchStart(...args), { passive: true });
        this.viewport.addEventListener("touchmove", (...args) => this.handleTouchMove(...args), { passive: true });
        
        // マウスイベント
        this.setupDropdownMouseEvents();
    }

    // ------------------------------------------
    // ホイールイベント（ユーザースクロール検出）
    // ------------------------------------------
    handleWheel(e) {
        this.markUserScrolling();
    }

    // ------------------------------------------
    // タッチイベント（ユーザースクロール検出）
    // ------------------------------------------
    handleTouchStart(e) {
        this.markUserScrolling();
    }

    handleTouchMove(e) {
        this.markUserScrolling();
    }

    // ------------------------------------------
    // ユーザースクロール状態をマーク
    // ------------------------------------------
    markUserScrolling() {
        this.isUserScrolling = true;
        
        // タイムアウトをクリア
        if (this.userScrollTimeout) {
            clearTimeout(this.userScrollTimeout);
        }
        
        // 500ms後にユーザースクロール状態を解除
        this.userScrollTimeout = setTimeout(() => {
            this.isUserScrolling = false;
        }, 500);
    }

    // ------------------------------------------
    // ビューポート高さを計算
    // ------------------------------------------
    fitRowHeights(reset = false) {
        const oldHeight = this.itemHeight;
        const scrollRow = this.viewport.scrollTop / oldHeight;
        // Measure natural wrapping at the current popup width, then keep a
        // uniform slot height so virtual scrolling still uses exact offsets.
        let height = reset ? 40 : this.itemHeight;
        for (const item of this.visibleItems) item.element.style.height = "auto";
        for (const item of this.visibleItems) {
            height = Math.max(height, Math.ceil(item.element.getBoundingClientRect().height));
        }
        this.itemHeight = height;
        for (const item of this.visibleItems) item.element.style.height = `${height}px`;
        this.container.style.height = `${this.allItems.length * height}px`;
        this.paddingTop.style.height = `${this.startIndex * height}px`;
        this.paddingBottom.style.height = `${Math.max(0, this.allItems.length - this.endIndex - 1) * height}px`;
        if (height !== oldHeight) this.viewport.scrollTop = scrollRow * height;
    }

    calculateViewportHeight() {
        const actualItemCount = Math.min(this.allItems.length, this.visibleCount);
        return actualItemCount * this.itemHeight;
    }

    // ------------------------------------------
    // スクロールハンドラ
    // ------------------------------------------
    handleScroll() {
        if (!this.allItems.length) return;
        
        const currentScrollTop = this.viewport.scrollTop;
        
        // スクロール方向を検出
        const isScrollingDown = currentScrollTop > this.lastScrollTop;
        this.lastScrollTop = currentScrollTop;
        
        // ユーザーがスクロール中の場合、選択状態は更新しない
        if (this.isUserScrolling) {
            this.updateVirtualScrollOnly();
            return;
        }
        
        // アイテム数が表示件数以下の場合はスクロール処理不要
        if (this.allItems.length <= this.visibleCount) {
            return;
        }
        
        const newStartIndex = Math.floor(currentScrollTop / this.itemHeight);
        
        // バッファを考慮した範囲計算
        const actualStartIndex = Math.max(0, newStartIndex - this.bufferSize);
        const actualEndIndex = Math.min(
            this.allItems.length - 1,
            newStartIndex + this.visibleCount + this.bufferSize
        );
        
        if (actualStartIndex !== this.startIndex || actualEndIndex !== this.endIndex) {
            this.startIndex = actualStartIndex;
            this.endIndex = actualEndIndex;
            this.updateVisibleItems();
        }
    }

    // ------------------------------------------
    // 仮想スクロールのみ更新（選択状態は変更しない）
    // ------------------------------------------
    updateVirtualScrollOnly() {
        if (this.allItems.length <= this.visibleCount) return;
        
        const currentScrollTop = this.viewport.scrollTop;
        const newStartIndex = Math.floor(currentScrollTop / this.itemHeight);
        
        const actualStartIndex = Math.max(0, newStartIndex - this.bufferSize);
        const actualEndIndex = Math.min(
            this.allItems.length - 1,
            newStartIndex + this.visibleCount + this.bufferSize
        );
        
        if (actualStartIndex !== this.startIndex || actualEndIndex !== this.endIndex) {
            this.startIndex = actualStartIndex;
            this.endIndex = actualEndIndex;
            this.updateVisibleItemsOnly();
        }
    }

    // ------------------------------------------
    // 表示アイテムのみ更新（選択状態は更新しない）
    // ------------------------------------------
    updateVisibleItemsOnly() {
        // 通常の仮想スクロール処理
        const topPadding = this.startIndex * this.itemHeight;
        const bottomPadding = (this.allItems.length - this.endIndex - 1) * this.itemHeight;
        
        this.paddingTop.style.height = `${topPadding}px`;
        this.paddingBottom.style.height = `${bottomPadding}px`;
        
        // 表示アイテム取得
        this.visibleItems = this.allItems.slice(this.startIndex, this.endIndex + 1);
        
        // DOM更新
        const itemElements = this.visibleItems.map(item => {
            const element = item.element;
            element.style.height = `${this.itemHeight}px`;
            element.style.display = "flex";
            element.style.alignItems = "center";
            element.style.boxSizing = "border-box";
            element.style.width = "100%";
            return element;
        });
        
        // コンテナ更新
        this.container.replaceChildren(
            this.paddingTop,
            ...itemElements,
            this.paddingBottom
        );
        
        // 選択状態のみ更新（scrollIntoViewは呼ばない）
        this.fitRowHeights();
        if (this.lastPosition) this.updateDropdownPosition(this.lastPosition);
        this.updateItemSelectionWithoutScroll();
    }

    // ------------------------------------------
    // 表示アイテム更新
    // ------------------------------------------
    updateVisibleItems() {
        // アイテム数が少ない場合は全て表示
        if (this.allItems.length <= this.visibleCount) {
            this.paddingTop.style.height = '0px';
            this.paddingBottom.style.height = '0px';
            
            this.visibleItems = this.allItems;
            
            // DOM更新 - イベントリスナーを保持するため元の要素を使用
            const itemElements = this.visibleItems.map(item => {
                const element = item.element; // cloneNode(true)ではなく元の要素を使用
                element.style.height = `${this.itemHeight}px`;
                element.style.display = "flex";
                element.style.alignItems = "center";
                element.style.boxSizing = "border-box";
                element.style.width = "100%";
                return element;
            });
            
            this.container.replaceChildren(...itemElements);
            this.fitRowHeights();
            if (this.lastPosition) this.updateDropdownPosition(this.lastPosition);
            this.updateItemSelection();
            return;
        }

        // 通常の仮想スクロール処理
        const topPadding = this.startIndex * this.itemHeight;
        const bottomPadding = (this.allItems.length - this.endIndex - 1) * this.itemHeight;
        
        this.paddingTop.style.height = `${topPadding}px`;
        this.paddingBottom.style.height = `${bottomPadding}px`;
        
        // 表示アイテム取得
        this.visibleItems = this.allItems.slice(this.startIndex, this.endIndex + 1);
        
        // DOM更新 - イベントリスナーを保持するため元の要素を使用
        const itemElements = this.visibleItems.map(item => {
            const element = item.element; // cloneNode(true)ではなく元の要素を使用
            element.style.height = `${this.itemHeight}px`;
            element.style.display = "flex";
            element.style.alignItems = "center";
            element.style.boxSizing = "border-box";
            element.style.width = "100%";
            return element;
        });
        
        // コンテナ更新
        this.container.replaceChildren(
            this.paddingTop,
            ...itemElements,
            this.paddingBottom
        );
        
        this.fitRowHeights();
        if (this.lastPosition) this.updateDropdownPosition(this.lastPosition);
        this.updateItemSelection();
    }

    // ------------------------------------------
    // ドロップダウンを表示
    // ------------------------------------------
    show(items, position) {
        this.itemHeight = 40;
        this.rowWidth = null;
        this.allItems = items.map((item, index) => ({
            element: item,
            originalIndex: index
        }));
        
        this.contentWidth = null;
        this.currentIndex = 0;
        this.startIndex = 0;
        this.endIndex = Math.min(this.visibleCount + this.bufferSize * 2 - 1, this.allItems.length - 1);
        
        // 全体の高さ設定
        const totalHeight = this.allItems.length * this.itemHeight;
        this.container.style.height = `${totalHeight}px`;

        // 先にDOMに追加してサイズ計算を可能にする
        if (!this.dropdown.parentElement) {
            document.body.append(this.dropdown);
        }
        
        this.updateVisibleItems();
        this.updateDropdownPosition(position);
    }

    // ------------------------------------------
    // ドロップダウンを非表示
    // ------------------------------------------
    hide() {
        if (!this.dropdown.parentElement) return;
        
        // スタイルをリセットして、次回表示時に影響が出ないようにする
        this.viewport.style.height = "";
        this.viewport.style.maxHeight = "";
        this.container.style.height = "";
        this.dropdown.style.left = "";
        this.dropdown.style.top = "";
        
        this.allItems = [];
        this.visibleItems = [];
        this.currentIndex = 0;
        this.startIndex = 0;
        this.endIndex = 0;
        this.isMousedownOnDropdown = false;
        this.isHoveringOnDropdown = false;
        this.isUserScrolling = false;
        this.dropdown.remove();
    }

    // ------------------------------------------
    // 表示状態を確認
    // ------------------------------------------
    isVisible() {
        return this.dropdown.parentElement !== null;
    }

    // ------------------------------------------
    // 現在のアイテム数を取得
    // ------------------------------------------
    getItemCount() {
        return this.allItems.length;
    }

    // ------------------------------------------
    // 現在のインデックスを取得
    // ------------------------------------------
    getCurrentIndex() {
        return this.currentIndex;
    }

    // ------------------------------------------
    // 現在の結果を取得
    // ------------------------------------------
    getCurrentResults() {
        return this.allItems;
    }

    // ------------------------------------------
    // インデックスを設定
    // ------------------------------------------
    setCurrentIndex(index) {
        if (!this.allItems.length) return;
        
        this.currentIndex = Math.max(0, Math.min(index, this.allItems.length - 1));
        this.scrollToCurrentItem();
        this.updateItemSelection();
    }

    // ------------------------------------------
    // 上に移動
    // ------------------------------------------
    navigateUp() {
        if (!this.allItems.length) return;
        
        this.currentIndex = this.currentIndex <= 0 
            ? this.allItems.length - 1 
            : this.currentIndex - 1;
        
        this.scrollToCurrentItem();
        this.updateItemSelection();
    }

    // ------------------------------------------
    // 下に移動
    // ------------------------------------------
    navigateDown() {
        if (!this.allItems.length) return;
        
        this.currentIndex = this.currentIndex >= this.allItems.length - 1 
            ? 0 
            : this.currentIndex + 1;
        
        this.scrollToCurrentItem();
        this.updateItemSelection();
    }

    // ------------------------------------------
    // ページ単位で移動
    // ------------------------------------------
    navigatePage(direction, pageSize) {
        if (!this.allItems.length) return;
        
        this.currentIndex = direction > 0 
            ? Math.min(this.allItems.length - 1, this.currentIndex + pageSize)
            : Math.max(0, this.currentIndex - pageSize);
        
        this.scrollToCurrentItem();
        this.updateItemSelection();
    }

    // ------------------------------------------
    // 現在のアイテムまでスクロール（キーボード操作用）
    // ------------------------------------------
    scrollToCurrentItem() {
        // ユーザーがスクロール中は自動スクロールしない
        if (this.isUserScrolling) {
            return;
        }

        // アイテム数が少ない場合はスクロール不要
        if (this.allItems.length <= this.visibleCount) {
            this.updateItemSelection();
            return;
        }

        const targetScrollTop = this.currentIndex * this.itemHeight;
        const viewportHeight = this.viewport.clientHeight;
        const currentScrollTop = this.viewport.scrollTop;
        
        // アイテムが見える範囲にない場合のみスクロール
        if (targetScrollTop < currentScrollTop) {
            this.viewport.scrollTop = targetScrollTop;
        } else if (targetScrollTop + this.itemHeight > currentScrollTop + viewportHeight) {
            this.viewport.scrollTop = targetScrollTop + this.itemHeight - viewportHeight;
        }
    }

    // ------------------------------------------
    // アイテムの選択状態を更新（scrollIntoViewなし）
    // ------------------------------------------
    updateItemSelectionWithoutScroll() {
        const selectedClassName = "yp-tagforge-plus-item--selected";
        
        if (this.allItems.length <= this.visibleCount) {
            // アイテム数が少ない場合
            const containerItems = this.container.querySelectorAll(".yp-tagforge-plus-item");
            containerItems.forEach((item, index) => {
                const isSelected = index === this.currentIndex;
                item.classList.toggle(selectedClassName, isSelected);
            });
        } else {
            // 仮想スクロール時
            const containerItems = this.container.querySelectorAll(".yp-tagforge-plus-item");
            containerItems.forEach((item, index) => {
                const actualIndex = this.startIndex + index;
                const isSelected = actualIndex === this.currentIndex;
                item.classList.toggle(selectedClassName, isSelected);
            });
        }
    }

    // ------------------------------------------
    // アイテムの選択状態を更新
    // ------------------------------------------
    updateItemSelection() {
        // ユーザーがスクロール中は scrollIntoView を実行しない
        if (this.isUserScrolling) {
            this.updateItemSelectionWithoutScroll();
            return;
        }

        const selectedClassName = "yp-tagforge-plus-item--selected";
        
        if (this.allItems.length <= this.visibleCount) {
            // アイテム数が少ない場合
            const containerItems = this.container.querySelectorAll(".yp-tagforge-plus-item");
            containerItems.forEach((item, index) => {
                const isSelected = index === this.currentIndex;
                item.classList.toggle(selectedClassName, isSelected);
                
                if (isSelected) {
                    item.scrollIntoView({
                        block: "nearest", 
                        behavior: "smooth", 
                        inline: "nearest"
                    });
                }
            });
        } else {
            // 仮想スクロール時
            const containerItems = this.container.querySelectorAll(".yp-tagforge-plus-item");
            containerItems.forEach((item, index) => {
                const actualIndex = this.startIndex + index;
                const isSelected = actualIndex === this.currentIndex;
                item.classList.toggle(selectedClassName, isSelected);
                
                if (isSelected) {
                    item.scrollIntoView({
                        block: "nearest", 
                        behavior: "smooth", 
                        inline: "nearest"
                    });
                }
            });
        }
    }

    // ------------------------------------------
    // 選択中のアイテムを取得
    // ------------------------------------------
    getSelectedItem() {
        if (!this.allItems.length || this.currentIndex < 0 || this.currentIndex >= this.allItems.length) {
            return null;
        }
        return this.allItems[this.currentIndex].element;
    }

    // ------------------------------------------
    // マウス状態を確認
    // ------------------------------------------
    isMouseInteracting() {
        return this.isMousedownOnDropdown || this.isHoveringOnDropdown;
    }

    // ------------------------------------------
    // ドロップダウンの高さを取得
    // ------------------------------------------
    getDropdownHeight() {
        return this.viewport.clientHeight;
    }

    // ------------------------------------------
    // ドロップダウンの位置を更新
    // ------------------------------------------
    measureContentWidth() {
        // Measure every result, including rows outside the virtual viewport.
        // Clones preserve fonts and pills without moving interactive originals.
        const measure = mkEl("div");
        measure.style.cssText = "position:fixed;left:-100000px;top:0;visibility:hidden;pointer-events:none;width:max-content";
        const rows = this.allItems.map(({ element }) => {
            const row = element.cloneNode(true);
            Object.assign(row.style, { width: "max-content", maxWidth: "none", height: "auto", flexWrap: "nowrap", transition: "none" });
            for (const child of row.children) {
                Object.assign(child.style, { flex: "0 0 auto", width: "max-content", maxWidth: "none" });
                if (child.classList.contains("yp-tagforge-plus-text")) child.style.minWidth = "260px";
            }
            return row;
        });
        measure.append(...rows);
        this.dropdown.append(measure);
        try {
            // Include popup borders/padding and room for the vertical scrollbar.
            return Math.ceil(Math.max(0, ...rows.map(row => row.getBoundingClientRect().width))) + 24;
        } finally {
            measure.remove();
        }
    }

    updateDropdownPosition(position) {
        if (!position) return;
        this.lastPosition = position;
        // The setting is the baseline; grow only when this result list needs it.
        this.contentWidth ??= this.measureContentWidth();
        const desiredWidth = Math.max(this.settings.dropdownWidth || 720, this.contentWidth);
        // Width affects wrapping, so measure the related header after sizing.
        this.dropdown.style.width = `${Math.min(desiredWidth, Math.max(0, window.innerWidth - 20))}px`;
        const width = this.dropdown.clientWidth;
        this.fitRowHeights(width !== this.rowWidth);
        this.rowWidth = width;
        const headerHeight = this.dropdown.querySelector(".yp-tagforge-plus-related-heading")?.offsetHeight ?? 0;
        const layout = dropdownLayout({ position, viewportWidth: window.innerWidth, viewportHeight: window.innerHeight,
            scrollX: window.scrollX, scrollY: window.scrollY, width: desiredWidth,
            headerHeight,
            contentHeight: this.allItems.length * this.itemHeight });
        this.viewport.style.height = `${layout.listHeight}px`;
        this.viewport.style.maxHeight = `${layout.listHeight}px`;
        this.dropdown.style.width = `${layout.width}px`;
        this.dropdown.style.left = `${layout.left}px`;
        this.dropdown.style.top = `${layout.top}px`;
    }


    // ------------------------------------------
    // マウスイベント処理
    // ------------------------------------------
    setupDropdownMouseEvents() {
        document.addEventListener("mousedown", (e) => {
            if (this.dropdown.contains(e.target)) {
                this.isMousedownOnDropdown = true;
                this.handleScrollbarClick(e);
            } else {
                this.isMousedownOnDropdown = false;
            }
        });

        document.addEventListener("mouseup", () => {
            this.isMousedownOnDropdown = false;
        });

        this.dropdown.addEventListener("mouseenter", () => {
            this.isHoveringOnDropdown = true;
        });

        this.dropdown.addEventListener("mouseleave", () => {
            this.isHoveringOnDropdown = false;
        });
    }

    handleScrollbarClick(e) {
        const dropdown = this.viewport;
        const rect = dropdown.getBoundingClientRect();
        const scrollbarWidth = dropdown.offsetWidth - dropdown.clientWidth;
        const isScrollbarClick = e.clientX >= rect.right - scrollbarWidth;

        if (isScrollbarClick) {
            e.preventDefault();
            setTimeout(() => {
                this.textareaElement.focus();
            }, 0);
        }
    }

    // ------------------------------------------
    // クリーンアップ
    // ------------------------------------------
    destroy() {
        if (this.userScrollTimeout) {
            clearTimeout(this.userScrollTimeout);
        }
        this.hide();
        this.isMousedownOnDropdown = false;
        this.isHoveringOnDropdown = false;
    }
}
