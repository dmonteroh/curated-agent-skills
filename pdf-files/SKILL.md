---
name: pdf-files
description: "Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents."
category: docs
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Files

Provides deterministic, verifiable workflows for extracting text or tables, converting pages to images, and filling PDF forms. Produces traceable artifacts and explicit verification notes.

## Use this skill when

- Extracting text or tables from PDFs
- Rendering pages to images for review, OCR, or coordinate work
- Inspecting or filling PDF forms (fillable fields or visual placement)
- Verifying that a filled PDF renders correctly

## Do not use this skill when

- Inputs are not PDF files
- Layout or typography editing is required (use a design tool instead)
- A task only needs plain text already provided

## Trigger phrases

- "extract text from a PDF"
- "convert PDF pages to images"
- "find fillable form fields"
- "fill out this PDF form"
- "validate a filled PDF"

## Required inputs

- PDF file path(s)
- Desired output artifacts (text, tables, images, filled PDF)
- Output directory or file names
- Form field values (if filling)
- Constraints (read-only, no network, retention limits)

## Workflow

### 1) Intake and safety

- Actions: confirm PDF paths, create output paths, preserve originals.
- Output: input list, output plan, and working copy locations (if needed).

### 2) Inspect and classify

- Actions: determine whether the PDF is text-based or scanned and check for fillable fields.
- Command: `python3 pdf-files/scripts/check_fillable_fields.py input.pdf`
- Output: classification (text vs scanned; fillable vs non-fillable) and chosen path.
- Decision:
  - If fillable fields exist, follow `references/forms-fillable-fields.md`.
  - If no fillable fields and the task is to fill a form, follow `references/forms-visual-annotations.md`.

### 3) Extract or render

- Actions: extract text/tables with available local tools, or render pages to images.
- Command: `python3 pdf-files/scripts/convert_pdf_to_images.py input.pdf output_dir/`
- Output: extracted text/tables or `page_*.png` images with recorded paths.

### 4) Fill forms (if needed)

- Actions: use the appropriate form workflow to create field JSON and an output PDF.
- Output: `field_values.json` or `fields.json`, plus filled PDF.

### 5) Verify outputs

- Actions: open rendered images or filled PDF and confirm expected content/placement.
- Output: verification notes (viewer used, pages checked, pass/fail).

## Scripts and dependencies

Dependencies: Python 3, `pypdf`, `pdf2image`, `Pillow`. `pdf2image` requires Poppler binaries available on `PATH`.

- `scripts/check_fillable_fields.py`
  - Usage: `python3 pdf-files/scripts/check_fillable_fields.py input.pdf`
  - Output: stdout indicates whether fields exist.
  - Verification: include stdout in the report.

- `scripts/extract_form_field_info.py`
  - Usage: `python3 pdf-files/scripts/extract_form_field_info.py input.pdf fields.json`
  - Output: `fields.json` with field metadata.
  - Verification: spot-check page numbers and field IDs.

- `scripts/fill_fillable_fields.py`
  - Usage: `python3 pdf-files/scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf`
  - Output: filled `output.pdf`.
  - Verification: open the output PDF and confirm field values.

- `scripts/convert_pdf_to_images.py`
  - Usage: `python3 pdf-files/scripts/convert_pdf_to_images.py input.pdf output_dir/`
  - Output: `page_*.png` images.
  - Verification: open at least one page image.

- `scripts/create_validation_image.py`
  - Usage: `python3 pdf-files/scripts/create_validation_image.py page_number fields.json input.png output.png`
  - Output: validation image with bounding boxes.
  - Verification: confirm red/blue boxes align with intended areas.

- `scripts/check_bounding_boxes.py`
  - Usage: `python3 pdf-files/scripts/check_bounding_boxes.py fields.json`
  - Output: success/failure messages.
  - Verification: require `SUCCESS` before continuing.

- `scripts/fill_pdf_form_with_annotations.py`
  - Usage: `python3 pdf-files/scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf`
  - Output: filled `output.pdf` with annotations.
  - Verification: open the output PDF and confirm placement.

## Common pitfalls

- Empty text extraction indicates a scanned PDF; switch to image conversion or OCR.
- Field IDs or page numbers mismatch; regenerate `fields.json` and recheck.
- Bounding boxes intersect or misalign; regenerate validation images and rerun checks.
- Filled values appear blank in some viewers; verify in another viewer.

## Examples

### Example 1: Text extraction

Input: `contract.pdf`
Output artifacts: `contract.md`
Verification: preview `contract.md` for completeness.

### Example 2: Fillable form

Input: `form.pdf`
Output artifacts: `fields.json`, `field_values.json`, `filled-form.pdf`
Verification: open `filled-form.pdf` and confirm values render.

## Output contract

Provide results using this format:

```
Summary:
Inputs:
Decisions:
Outputs:
Verification:
Notes:
```

## Trigger test

- "Extract text from this PDF and summarize the sections."
- "Fill out this PDF form and verify the output."

## Resources

- Playbook: `resources/implementation-playbook.md`
- References index: `references/README.md`
