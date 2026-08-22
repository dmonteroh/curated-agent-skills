---
name: office-files
description: "Works with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspects structure, extracts text/tables, produces diffs, and generates clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files."
metadata:
  category: docs
---
# Office Files (DOCX / PPTX / XLSX)

Provides workflows for inspecting, extracting, and diffing OOXML office files.

## Use this skill when

- The user needs to read/extract content from `.docx`, `.pptx`, or `.xlsx`
- The user needs to compare two versions of an office file (visual/textual diff)
- The user needs to turn an office file into a human-readable summary (Markdown)
- The task needs quick, deterministic structure inspection (sheets/slides/parts)
- A `.pptx` needs its real slide order, its relationship graph resolved, or a package-integrity check — it opens with a repair prompt, images are missing, or slides that should be there do not appear
- A supplied file is being studied as evidence — a reference deck, a template, a competitor's report — and nothing may be written back to it

## Do not use this skill when

- The file is not OOXML (e.g. `.doc`, `.xls`, `.ppt`)
- The task requires high-fidelity editing with tracked changes or advanced formatting (request a template or use a dedicated doc workflow)
- The deliverable is a new document, deck, or workbook built from a studied file's parts — this skill produces evidence about a file, never a file assembled out of someone else's package

## Required inputs

- Path(s) to the `.docx`, `.pptx`, or `.xlsx` files
- Desired output format (`md` or `json`) when extracting
- Intended action: inspect, extract, or diff

## Constraints

- Works on local files only; no network assumptions.
- Uses stdlib-only scripts; no external dependencies.

## Safety Rules

- Prefer read-only extraction/inspection.
- Never destroy the original file; write outputs next to it or to a temp path.
- If proposing edits, require a verification step (open in Office/LibreOffice) before declaring success.
- A file supplied to be studied stays read-only, and its parts are never copied into another file. Extracted text, images, fonts, and templates need explicit permission and license evidence before they appear in anything produced. Detail: `references/safety-guidelines.md`.

## Quickstart (Scripts)

Required: Python 3 with access to the local filesystem.
Run from the skill folder; paths below are relative to it.

- Inspect package structure:
  ```bash
  python3 scripts/office_inspect.py path/to/file.docx
  ```
- Extract to Markdown:
  ```bash
  python3 scripts/office_extract.py path/to/file.pptx --format md > out.md
  ```
- Extract to JSON (for downstream tooling):
  ```bash
  python3 scripts/office_extract.py path/to/file.xlsx --format json > out.json
  ```
- Diff two office files (text diff):
  ```bash
  python3 scripts/office_diff.py old.docx new.docx
  ```
- Resolve PPTX slide order and check package integrity:
  ```bash
  python3 scripts/pptx_package_check.py deck.pptx
  ```
  Add `--json` for a machine-readable report. Exit status: 0 clean, 1 findings, 2 unreadable package.

Verification: open any generated or modified file in Office or LibreOffice and compare it against the reported Findings. The check fails if the application shows a repair prompt on open, or if a slide, sheet, or section named in Findings is absent from the opened file; report the artifact as incomplete rather than declaring success.

## Workflow

1. Confirm inputs and file types.
   - If any file is not `.docx`, `.pptx`, or `.xlsx`, stop and request a supported format.
   - Output: a short summary of file paths and detected types.
2. Choose the action (inspect, extract, diff, or check).
   - If the user needs structure only, run `office_inspect.py`.
   - If the user needs content, run `office_extract.py` with `--format md|json`.
   - If the user needs comparison, run `office_diff.py`.
   - If the file is a `.pptx` and the question is its slide order or whether the package is intact, run `pptx_package_check.py` first — see "PPTX package inspection" below.
   - Output: the command selected and why.
3. Execute the script and capture results.
   - If the file is password-protected, corrupted, or otherwise unreadable, stop and request an unlocked copy.
   - Output: key findings (sections, slides, sheets, tables, or diffs) plus any warnings.
4. Summarize and propose next steps.
   - If content is missing or unclear, ask for a higher-fidelity source or confirm limits.
   - Output: a concise summary and verification guidance.

## PPTX package inspection

A `.pptx` is a ZIP whose parts are wired together by relationship files. Naming is a convention of whatever application wrote it; the wiring is the document.

**Resolve the relationship graph; do not assume sequential filenames.** Slide order is the document order of the `p:sldId` entries in `ppt/presentation.xml`, each resolved through `ppt/_rels/presentation.xml.rels` to a slide part. A `.rels` target resolves relative to the part that owns the `.rels` file, unless it starts with `/`. So `slide7.xml` may be the second slide in a deck that was reordered, and a slide part left behind by a deletion sits in the archive with nothing pointing at it. Reporting `slide1, slide2, slide3…` as the deck's order is a guess that reads like a finding, and it is wrong exactly when it matters — on a deck someone has edited.

**A slide part that exists is not a slide that shows.** Report from the resolved order. An unreferenced slide part is a finding, not the next slide. A hidden slide (`show="0"`) is in the package and not in the delivered presentation; say which.

Run `scripts/pptx_package_check.py` for both jobs at once: it prints the resolved order with hidden slides marked, then the integrity findings. `scripts/office_inspect.py` lists package members and does not resolve order — use it to see what is in the archive, not to say what the deck contains.

What the check reports, and what each finding means:

| Class | Finding | Reading |
| --- | --- | --- |
| Error | XML that does not parse; a relationship target that is not in the package; a `p:sldId` resolving to nothing or to a non-slide relationship; a duplicated slide id; a slide with no correct content-type override; a slide with anything other than exactly one layout relationship | The package is internally inconsistent. A deck that opens with a repair prompt should produce at least one of these; a deck that opens clean and still produces one means the reading is wrong, not the deck. |
| Warning | A slide part the presentation does not list; media or notes parts with no inbound relationship | Usually editing residue — deleted slides and unused images that were never pruned. Report them; they are not damage and are not to be "fixed" by editing the file. |

Decision points:

- If the check reports errors, stop before extracting content and report the package state first. Text pulled out of an inconsistent package is content of unknown completeness.
- If the check reports only warnings, extraction proceeds; carry the warnings into Gaps/limits.
- If a question is about what a slide points at — its layout, its images, its charts, its notes — read that slide's own `.rels` file. The slide part alone does not name them.
- If a color is a scheme token (`accent1`, `dk2`), report the token. A hex value that was not read from the color scheme is invented.

Part maps and the full graph-resolution procedure: `references/pptx-notes.md`. The general relationship rule, which applies to `.docx` and `.xlsx` equally: `references/ooxml-overview.md`.

## Common pitfalls

- Assuming charts or embedded images are extracted as text; call out missing visual data.
- Presenting a deck summary as complete without saying which parts failed to parse or were skipped.

## Examples

- Input: "Summarize `sales.pptx` into Markdown."
  - Action: `office_extract.py sales.pptx --format md`
  - Output: Markdown summary of slide titles and bullet points.
- Input: "Compare `v1.docx` and `v2.docx`."
  - Action: `office_diff.py v1.docx v2.docx`
  - Output: Text diff of changes with a short narrative summary.
- Input: "PowerPoint keeps asking to repair `quarterly.pptx`."
  - Action: `pptx_package_check.py quarterly.pptx`
  - Output: the resolved slide order, then the findings — for example one error, a slide whose layout relationship is missing, and one warning, a slide part the presentation no longer lists. The error explains the repair prompt; the warning is residue from a deleted slide.
  - Contrast: reading the same deck as `slide1, slide2, slide3` off the archive listing reports three slides in the wrong order and misses both findings entirely.

## Output format

Report using this template:

- Action: inspect | extract | diff | check
- Files: `<paths>`
- Findings: key structure/content/diff highlights
- Gaps/limits: missing visuals, unsupported elements, or uncertainties
- Next steps: verification or follow-up requests

## Output contract

When asked to work with an office file:

- Use the Output format template above.
- Ensure Gaps/limits captures missing visuals or unsupported elements.

## References

- `references/README.md`
