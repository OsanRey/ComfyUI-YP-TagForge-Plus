<p align="center"><img src="assets/banner.svg" alt="YP TagForge Plus" width="800"></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-94d5ad" alt="MIT"></a>
  <img src="https://img.shields.io/badge/ComfyUI-prompt%20tools-94d5ad" alt="ComfyUI prompt tools">
  <a href="README.ru.md">Русский</a>
</p>

# YP TagForge Plus

Tag suggestions, Russian translations, related tags and prompt formatting for ComfyUI text fields.

## Features

- **Danbooru + e621 suggestions:** tags, aliases, artists, characters and copyright categories, with a local Russian translation dictionary.
- **Search without separators:** `onbe` finds `on_bed`; `blueeyes` finds `blue_eyes`.
- **Related tags:** click a tag already in your prompt or press **Ctrl+Shift+Space**. Results include translations and a similarity score.
- **Artist prefixes:** automatically insert `@` before Artist tags, use another prefix or disable it with an empty setting.
- **Prompt formatting:** clean up repeated commas and surrounding spaces on blur, or manually with **Alt+Shift+F**.
- **Readable lists:** alternating row backgrounds, full tag names with wrapping, plain-text translations and book links to tag pages.
- **Inline translation editing:** correct translations directly in the selected CSV dictionary using the pencil button.
- **Existing-tag detection:** tags already in the prompt appear dimmer, including tags with weights or spaces in place of underscores.
- **Window sizing:** adjustable base width with automatic expansion for longer rows; height follows the result count and available screen space.
- **Node support:** classic text widgets, Nodes 2.0 and promoted Subgraph fields.

Search uses local CSV snapshots. Book links open the tag's external page; suggestions do not require a live connection to Danbooru or e621.

## Install

From ComfyUI's `custom_nodes` directory:

```bash
git clone https://github.com/OsanRey/ComfyUI-YP-TagForge-Plus.git
python -m pip install -r ComfyUI-YP-TagForge-Plus/requirements.txt
```

Use the Python environment that runs ComfyUI. Restart ComfyUI, then press **Ctrl+F5** in the browser. Open **Settings → YP TagForge Plus**.

## Quick start

1. Click an editable prompt field and type a few letters.
2. Use **↑ / ↓** to choose a suggestion and **Enter / Tab** to insert it. Mouse selection also works.
3. Click inside an existing tag to browse related tags.
4. Click **📖** to open the tag page in a new tab.

With the default insertion settings, selecting a suggestion gives:

```text
onbe       → on bed,
blueeyes   → blue eyes,
wlop       → @wlop,
```

Underscore conversion and the separator after insertion are configurable. Category filters such as `--Artist` narrow the search; `++` prefixes can add custom text to an inserted tag.

## Settings

| Setting | Behavior |
| --- | --- |
| **Enable** | Enable the extension. |
| **Main / extra / translation file** | Select local CSV data sources. |
| **Artist prefix** | Prefix for Artist tags; default `@`, empty disables it. |
| **Replace '_' with 'Space'** | Convert inserted tag underscores to spaces. |
| **Delimiter / Add Space** | Configure the separator added after a suggestion. |
| **Max Suggestions to Display** | Number of search suggestions; 0 requests all available matches. |
| **Related tag count** | Number of related-tag results. |
| **Tag window width (px)** | Base popup width, from 320 to 1600 px. The window expands for longer rows within screen bounds. |
| **Prompt formatting** | Enable prompt formatting. |
| **Format on blur** | Format automatically when the field loses focus. |
| **Trailing comma and space** | Add a trailing comma and space. |

Window height is automatic. Results that do not fit on screen remain available by scrolling. Settings apply without reloading the page.

## Related tags

Related results are ranked by Jaccard similarity using tag co-occurrence data. Selecting a result adds it after the source tag. If it is already present, the existing text is selected instead of being inserted again.

Related data covers Danbooru. Some artists, rare tags and e621-only tags have no related entries. The first lookup builds a local disk index at `data/related.sqlite3`; later lookups use that index. Changing the source CSV rebuilds it automatically.

## Editing translations

Translations can be edited directly in suggestion and related-tag rows using the subtle pencil button. Save with ✓ or Enter; cancel with × or Escape. Changes update the selected translation CSV itself and become searchable immediately. Select a translation dictionary in settings before editing.

## Formatting

```text
Before: 1girl,,solo,  highres
After:  1girl, solo, highres,
```

Formatting retains weights, escaped parentheses, LoRA expressions and wildcard syntax. It does not guess tag boundaries in text without separators: `blue eyes` remains one tag. Read-only previews, code fields and numeric vectors are skipped.

## Compatibility

When enabled, the extension turns off competing completion and formatting handlers through their settings. Turning it off restores those previous settings in the same browser. This avoids overlapping popups and duplicate insertions.

The extension works independently. Add tag CSV files to `tags/` and translation CSV files to `translate/`; reload the page to update the available file list. There are no automatic data downloads at startup.

## Development

Tests cover formatting, artist prefixes, popup sizing, existing tags, related-tag insertion, data indexing and field integration. CI also checks Python and JavaScript syntax.

For bug reports, include your ComfyUI/frontend versions and a short example of the expected insertion or search result.

## License

[MIT](LICENSE). Required copyright notices are included in [licenses/](licenses/).
