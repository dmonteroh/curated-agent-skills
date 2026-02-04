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

## Trigger phrases

- "extract text from a docx"
- "summarize this powerpoint"
- "diff these two excel files"
- "inspect the structure of this office file"

## Required inputs

- Path(s) to the `.docx`, `.pptx`, or `.xlsx` files
- Desired output format (`md` or `json`) when extracting
- Intended action: inspect, extract, or diff

## Safety Rules (Default)

- Prefer read-only extraction/inspection.
- Never destroy the original file; write outputs next to it or to a temp path.
- If proposing edits, require a verification step (open in Office/LibreOffice) before declaring success.

## Quickstart (Scripts)

All scripts are stdlib-only and work without external Python deps.
Required: Python 3 with access to the local filesystem.

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

Verification: if you generate a modified file or derived artifact, open it in Office or LibreOffice to confirm the content matches expectations.

## Workflow

1. Confirm inputs and file types.
   - If any file is not `.docx`, `.pptx`, or `.xlsx`, stop and request a supported format.
   - Output: a short summary of file paths and detected types.
2. Choose the action (inspect, extract, or diff).
   - If the user needs structure only, run `office_inspect.py`.
   - If the user needs content, run `office_extract.py` with `--format md|json`.
   - If the user needs comparison, run `office_diff.py`.
   - Output: the command selected and why.
3. Execute the script and capture results.
   - Output: key findings (sections, slides, sheets, tables, or diffs) plus any warnings.
4. Summarize and propose next steps.
   - If content is missing or unclear, ask for a higher-fidelity source or confirm limits.
   - Output: a concise summary and verification guidance.

## Common pitfalls

- Treating legacy formats (`.doc`, `.xls`, `.ppt`) as OOXML; ask for conversion first.
- Assuming charts or embedded images are extracted as text; call out missing visual data.
- Skipping verification after generating a derived artifact.

## Examples

- Input: "Summarize `sales.pptx` into Markdown."
  - Action: `office_extract.py sales.pptx --format md`
  - Output: Markdown summary of slide titles and bullet points.
- Input: "Compare `v1.docx` and `v2.docx`."
  - Action: `office_diff.py v1.docx v2.docx`
  - Output: Text diff of changes with a short narrative summary.

## Output format

Report using this template:

- Action: inspect | extract | diff
- Files: `<paths>`
- Findings: key structure/content/diff highlights
- Gaps/limits: missing visuals, unsupported elements, or uncertainties
- Next steps: verification or follow-up requests

## Trigger test

- "Extract all tables from this `.xlsx` and summarize them."
- "Inspect the structure of this `.docx` and list sections."

## Output Contract

When asked to work with an office file, produce:

- What you did (inspect/extract/diff)
- What you found (key structure + content summary)
- Any uncertainty (missing evidence, unsupported features)
- Next steps (how to verify, how to capture missing states)

## References (Optional)

- `references/README.md`
