# Visual Annotation Workflow (Non-Fillable Forms)

## Purpose

Defines the process for filling PDFs without fillable fields by placing text annotations at precise coordinates.

## Required inputs

- `input.pdf`
- Output image directory
- `fields.json` describing bounding boxes and values
- Desired `output.pdf`
- Commands assume the working directory is the skill root (`pdf-files/`).

## Requirements

- Run steps in order to keep image and PDF coordinate systems aligned.
- Bounding boxes must not overlap text labels.

## Steps

### 1) Render pages to images

- Command: `python3 ./scripts/convert_pdf_to_images.py input.pdf output_dir/`
- Output: `page_*.png` images for each page.

### 2) Define `fields.json`

Create a JSON file that includes page metadata and form field bounding boxes. Bounding boxes use image coordinates `[left, top, right, bottom]` with origin at the top-left.

```json
{
  "pages": [
    {
      "page_number": 1,
      "image_width": 1000,
      "image_height": 1300
    }
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Applicant last name",
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "text": "Johnson",
        "font_size": 14,
        "font_color": "000000"
      }
    },
    {
      "page_number": 1,
      "description": "Age checkbox",
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],
      "entry_bounding_box": [140, 525, 155, 540],
      "entry_text": {
        "text": "X"
      }
    }
  ]
}
```

### 3) Create validation images

- Command: `python3 ./scripts/create_validation_image.py 1 fields.json output_dir/page_1.png validation.png`
- Output: `validation.png` with red entry boxes and blue label boxes.

### 4) Validate bounding boxes

- Command: `python3 ./scripts/check_bounding_boxes.py fields.json`
- Output: `SUCCESS` if boxes are valid.
- Verification: inspect `validation.png` to confirm red boxes cover only input areas.

### 5) Fill the PDF with annotations

- Command: `python3 ./scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf`
- Output: `output.pdf` with annotations added.

### 6) Verify placement

- Open `output.pdf` and confirm placement, font size, and legibility.
- If placement is off, adjust bounding boxes, regenerate validation images, and rerun the fill step.
