# Dictionary review tools

Run from the extension directory:

```sh
python tools/dictionary_review/audit.py --output /path/to/review-output
```

This reads every canonical tag in the bundled main CSV and quality-tag CSV. It writes `inventory.csv`, `pending.csv` and `summary.json`. It does not edit the dictionary unless `--apply` is passed. The queue is ordered by source post count, not by an estimated translation confidence.

`glossary.tsv` contains explicit Russian definitions. `rules.py` contains bounded color/garment agreement rules and named exceptions. `reviewed` means the current dictionary matches one of these explicit definitions or rules. It does not mean a generic machine translation was accepted. Preserved artist handles and original names/titles have separate statuses and are not counted as reviewed Russian translations.

`--apply` updates only tags covered by the explicit definitions and rules. Before using it with a personally edited dictionary, save a copy; this maintainer tool does not distinguish personal overrides from bundled entries. The normal pencil editor continues to write directly to the selected CSV.

Add terminology only after checking its tag-specific meaning. For ambiguous terms consult the source site's wiki; never translate artist handles or franchise titles word by word. Legacy labels outside the explicit rules remain pending. Generated inventories can contain local edits and should not be committed.
