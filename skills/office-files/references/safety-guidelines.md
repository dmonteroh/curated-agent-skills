# Safety Guidelines

- Treat OOXML as structured data: do not do naive string replace on the zipped XML unless you fully control the template.
- Prefer producing derived artifacts:
  - extracted Markdown
  - extracted JSON
  - diffs
- If edits are required:
  - work on a copy
  - validate by opening in Office/LibreOffice
  - keep changes minimal and reversible

## A supplied file is evidence, not a donor

Applies whenever a file is handed over to be studied — a reference deck, a template, a competitor's report — rather than to be read once.

- **Read-only on the source.** Never modify a supplied file, and never write into the directory it sits in without saying so first. Derived artifacts go beside it under new names, or to a temp path.
- **Never clone parts.** Do not copy package parts, styles, masters, or media out of one file and into another as a shortcut. Copied parts carry relationships, content-type entries, and identifiers that belong to the source package, and the result is a file that renders by luck. Reproduce what is needed independently.
- **License evidence before reuse.** Extracted text, images, icons, fonts, chart data, and templates stay out of any produced artifact until there is explicit permission and a statement of what licenses it — a font in particular is licensed software, not a value to copy across. Absent that, report what was observed and describe it; do not embed it.
- **Record what was inspected.** List the parts read and any parsing exceptions alongside the findings. A summary that does not say which parts it could not parse reads as complete when it is partial.

## Untrusted packages

- The bundled scripts parse XML with the Python standard library. That keeps the skill dependency-free but leaves entity-expansion denial of service unguarded, so a hostile file can cost far more memory than its size suggests. Inspect a file from an unknown source in a disposable working directory, and treat an inspection that will not terminate as a finding about the file rather than a bug in the script. A hardened XML parser is a third-party package and installing one is a deliberate decision to take on a dependency, not a default.
- The scripts refuse nothing about the archive's contents; they only bound its size. Archive ceilings in `scripts/pptx_package_check.py` (member count, member size, total uncompressed size, compression ratio) are chosen defaults, not measured limits — a legitimately huge deck can exceed them, and the fix is to raise the value deliberately rather than to remove the guard.
