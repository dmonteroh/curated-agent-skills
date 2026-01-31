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
