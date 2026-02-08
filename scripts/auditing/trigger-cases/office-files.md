# Trigger Cases: office-files

## Positive (should activate)
- prompt: "I need help with this: The user needs to read/extract content from `.docx`, `.pptx`, or `.xlsx`. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The user needs to compare two versions of an office file (visual/textual diff). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The file is not OOXML (e.g. `.doc`, `.xls`, `.ppt`). No planning, just implementation."
  expect_activate: no
