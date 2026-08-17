# OOXML Overview (DOCX / PPTX / XLSX)

OOXML files (`.docx`, `.pptx`, `.xlsx`) are ZIP containers with XML parts.

Common patterns:

- `[Content_Types].xml`: content-type registry for parts.
- `_rels/.rels`: root relationships.
- Each app has its own folder:
  - Word: `word/`
  - PowerPoint: `ppt/`
  - Excel: `xl/`

Typical extraction strategy:

- Open ZIP
- Identify key parts
- Parse XML and collect text

Namespaces:

- WordprocessingML (`w:`)
- DrawingML (`a:`)
- SpreadsheetML

Keep extraction robust by:

- ignoring formatting nodes
- focusing on text nodes (`w:t`, `a:t`)

## Parts are wired by relationships, not by naming

Every part that references another does so through a `.rels` file beside it: `<dir>/_rels/<part>.rels` describes `<dir>/<part>`, and `_rels/.rels` describes the package root. A reference is an `Id`, and the `Id` resolves to a `Target`.

- A `Target` resolves **relative to the part that owns the `.rels` file**, unless it begins with `/`, which makes it package-absolute. The same `Target` string therefore names different parts in different `.rels` files.
- A `TargetMode="External"` relationship points outside the package. It resolves to no member and is not a missing part.
- A member with no inbound relationship is orphaned: it is in the archive and not in the document. A relationship whose target is not a member is broken: the document expects content the archive does not carry.

Filename patterns (`slide1.xml`, `sheet1.xml`) are how applications happen to name parts, not where order or membership is recorded. Where a question is about order, membership, or what a part points at, the graph is the evidence and the glob is a shortcut that is right by coincidence. `xlsx-notes.md` applies this to sheet order; `pptx-notes.md` applies it to slide order.
