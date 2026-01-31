# PDF Files - Implementation Playbook

Use this playbook when you need a deterministic workflow (especially for forms and scanned PDFs).

## First Decision: Digital vs Scanned

- Digital/text PDF:
  - Prefer text extraction (pdftotext/pdfplumber) for speed.
- Scanned/image PDF:
  - Convert pages to images and use OCR (external tool) if required.

## Default Deliverables

- A derived artifact you can inspect:
  - `output.md` (text), `output.csv`/`output.xlsx` (tables), or page images
- A short summary of what was extracted.
- A verification step (open rendered images / open the resulting PDF).

## Form Filling Workflow (Two Paths)

### Path A: Fillable fields exist

1) Detect fields:
- Run: `python3 pdf-files/scripts/check_fillable_fields.py input.pdf`

2) Inspect field names/metadata:
- Run: `python3 pdf-files/scripts/extract_form_field_info.py input.pdf > fields.json`

3) Fill by field name:
- Run: `python3 pdf-files/scripts/fill_fillable_fields.py input.pdf output.pdf data.json`

4) Verify:
- Open `output.pdf` and confirm values render and are not clipped.

### Path B: No fillable fields (visual placement)

1) Render pages to images:
- Run: `python3 pdf-files/scripts/convert_pdf_to_images.py input.pdf out_dir/`

2) Determine bounding boxes for each value.

3) Validate bounding boxes visually:
- Run: `python3 pdf-files/scripts/create_validation_image.py out_dir/page_1.png fields.json validation.png`

4) Fill by annotations at coordinates:
- Run: `python3 pdf-files/scripts/fill_pdf_form_with_annotations.py input.pdf output.pdf fields.json`

5) Verify:
- Open `output.pdf` and confirm placement and font size.

## Troubleshooting

- Text extraction returns empty:
  - likely a scanned PDF; switch to image conversion + OCR.
- Filled fields don't show in some viewers:
  - some PDFs need appearance streams; verify in multiple viewers.
- Misaligned annotation placement:
  - coordinate transforms differ by page size/rotation; re-check `fields.json` and rerender validation images.

## Deep Dives

- Advanced tools and recipes: `pdf-files/references/reference.md`
- Detailed form guidance and scripts: `pdf-files/references/forms.md`
