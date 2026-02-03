---
name: pdf-files
description: "Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents."
category: docs
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Files

This skill focuses on deterministic, verifiable PDF workflows. Prefer producing derived artifacts (text/markdown/images) and explicit verification steps.

## Use this skill when

- Extracting text or tables from a PDF
- Converting PDFs to images for review/OCR
- Detecting and filling PDF forms (fillable fields or visual placement)
- Validating that a filled PDF renders correctly

## Do not use this skill when

- The file is not a PDF
- You need to edit layout/typography like a design tool (PDF is not a great editing format)

## Safety Rules (Default)

- Never overwrite the original file.
- Prefer read-only inspection/extraction before attempting edits.
- Always include a verification step (open rendered pages / open output PDF).

## Quickstart (Scripts)

- Detect fillable fields:
  ```bash
  python3 pdf-files/scripts/check_fillable_fields.py input.pdf
  ```
- Extract form field metadata:
  ```bash
  python3 pdf-files/scripts/extract_form_field_info.py input.pdf > fields.json
  ```
- Fill fillable fields:
  ```bash
  python3 pdf-files/scripts/fill_fillable_fields.py input.pdf output.pdf data.json
  ```
- Convert pages to images (for review / OCR / bounding boxes):
  ```bash
  python3 pdf-files/scripts/convert_pdf_to_images.py input.pdf out_dir/
  ```
- Fill via visual annotations (when no fillable fields):
  ```bash
  python3 pdf-files/scripts/fill_pdf_form_with_annotations.py input.pdf output.pdf fields.json
  ```
- Bounding box validation helpers:
  ```bash
  python3 pdf-files/scripts/check_bounding_boxes.py ...
  python3 pdf-files/scripts/create_validation_image.py ...
  ```

## Output Contract

When working with PDFs, produce:

- What you did (inspect/extract/fill/convert)
- What artifacts you generated (paths)
- What you found (text summary / tables / form fields)
- Verification steps and results

## Resources (Optional)

- End-to-end workflows: `resources/implementation-playbook.md`
- Advanced tooling/recipes: `references/reference.md`
- Form filling deep-dive: `references/forms.md`
