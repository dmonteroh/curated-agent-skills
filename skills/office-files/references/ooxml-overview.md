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
