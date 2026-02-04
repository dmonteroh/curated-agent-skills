# DOCX Notes

Key parts:

- `word/document.xml`: main body text
- `word/comments.xml`: comments (optional)
- `word/footnotes.xml`, `word/endnotes.xml`: notes (optional)

Text nodes:

- `w:t`: text
- `w:tab`: tab
- `w:br`: line break
- Paragraphs: `w:p`

If you need high-fidelity changes (tracked changes, formatting preservation), use a dedicated doc workflow/tooling; this skill focuses on robust extraction and diffs.
