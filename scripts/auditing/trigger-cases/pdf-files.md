# Trigger Cases: pdf-files

## Positive (should activate)
- prompt: "I need help with this: Extracting text or tables from PDFs. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Rendering pages to images for review, OCR, or coordinate work. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Inputs are not PDF files. No planning, just implementation."
  expect_activate: no
