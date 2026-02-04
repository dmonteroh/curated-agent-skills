# XLSX Notes

Key parts:

- `xl/workbook.xml`: sheet list
- `xl/_rels/workbook.xml.rels`: maps relationship IDs to sheet XML targets
- `xl/worksheets/sheet*.xml`: sheet contents
- `xl/sharedStrings.xml`: string table (optional)

Cell values:

- `c` nodes have attributes:
  - `r`: cell ref (e.g. `A1`)
  - `t`: cell type (`s` = shared string, `inlineStr` = inline string)
- Value usually under `v`.

This skill extracts a "preview" grid and best-effort text; it does not recalculate formulas.
