---
name: office-files
description: "Work with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspect structure, extract text/tables, produce diffs, and generate clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files."
category: docs
---

# Office Files (DOCX / PPTX / XLSX)

This skill handles common workflows for OOXML office files.

## Use this skill when

- You need to read/extract content from `.docx`, `.pptx`, or `.xlsx`
- You need to compare two versions of an office file (visual/textual diff)
- You need to turn an office file into a human-readable summary (Markdown)
- You need quick, deterministic structure inspection (sheets/slides/parts)

## Do not use this skill when

- The file is not OOXML (e.g. `.doc`, `.xls`, `.ppt`)
- You need high-fidelity editing with tracked changes / advanced formatting (request a template or use a dedicated doc workflow)

## Safety Rules (Default)

- Prefer read-only extraction/inspection.
- Never destroy the original file; write outputs next to it or to a temp path.
- If proposing edits, require a verification step (open in Office/LibreOffice) before declaring success.

## Quickstart (Scripts)

All scripts are stdlib-only and work without external Python deps.

- Inspect package structure:
  ```bash
  python3 office-files/scripts/office_inspect.py path/to/file.docx
  ```
- Extract to Markdown:
  ```bash
  python3 office-files/scripts/office_extract.py path/to/file.pptx --format md > out.md
  ```
- Extract to JSON (for downstream tooling):
  ```bash
  python3 office-files/scripts/office_extract.py path/to/file.xlsx --format json > out.json
  ```
- Diff two office files (text diff):
  ```bash
  python3 office-files/scripts/office_diff.py old.docx new.docx
  ```

## Output Contract

When asked to work with an office file, produce:

- What you did (inspect/extract/diff)
- What you found (key structure + content summary)
- Any uncertainty (missing evidence, unsupported features)
- Next steps (how to verify, how to capture missing states)

## References (Optional)

- `references/ooxml-overview.md`
- `references/docx-notes.md`
- `references/pptx-notes.md`
- `references/xlsx-notes.md`
- `references/safety-guidelines.md`
