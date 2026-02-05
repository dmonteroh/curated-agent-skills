# PDF Files - Implementation Playbook

Provides a deterministic workflow for PDF extraction, rendering, and form filling. Use this playbook to standardize outputs and verification steps.

Commands assume the working directory is the skill root (`pdf-files/`).

## First decision: digital vs scanned

- Digital/text PDF:
  - Prefer local text extraction tools for speed (for example, `pdftotext` or `pdfplumber`).
- Scanned/image PDF:
  - Render pages to images and use OCR if required.

## Default deliverables

- A derived artifact that can be inspected:
  - `output.md` (text), `output.csv`/`output.xlsx` (tables), or page images
- A short summary of what was extracted.
- A verification step (open rendered images or the resulting PDF).

## Form filling workflow (two paths)

### Path A: Fillable fields exist

1) Detect fields:
- Run: `python3 ./scripts/check_fillable_fields.py input.pdf`

2) Inspect field names/metadata:
- Run: `python3 ./scripts/extract_form_field_info.py input.pdf fields.json`

3) Fill by field name:
- Run: `python3 ./scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf`

4) Verify:
- Open `output.pdf` and confirm values render and are not clipped.

### Path B: No fillable fields (visual placement)

1) Render pages to images:
- Run: `python3 ./scripts/convert_pdf_to_images.py input.pdf out_dir/`

2) Determine bounding boxes for each value.

3) Validate bounding boxes visually:
- Run: `python3 ./scripts/create_validation_image.py 1 fields.json out_dir/page_1.png validation.png`

4) Fill by annotations at coordinates:
- Run: `python3 ./scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf`

5) Verify:
- Open `output.pdf` and confirm placement and font size.

## Troubleshooting

- Text extraction returns empty:
  - Likely a scanned PDF; switch to image conversion + OCR.
- Filled fields do not show in some viewers:
  - Some PDFs need appearance streams; verify in multiple viewers.
- Misaligned annotation placement:
  - Coordinate transforms differ by page size/rotation; re-check `fields.json` and regenerate validation images.

## Deep dives

- Advanced tools and recipes: `references/README.md`
- Detailed form guidance and scripts: `references/forms-fillable-fields.md` and `references/forms-visual-annotations.md`
