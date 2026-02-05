# Fillable Form Fields Workflow

## Purpose

Provides a deterministic process for identifying fillable fields in a PDF and writing validated values to those fields.

## Required inputs

- `input.pdf`
- Desired `output.pdf` location
- Values to populate in `field_values.json`
- Commands assume the working directory is the skill root (`pdf-files/`).

## Steps

### 1) Detect fillable fields

- Command: `python3 ./scripts/check_fillable_fields.py input.pdf`
- Output: stdout indicating whether fields exist.
- Decision: if no fields exist, switch to `forms-visual-annotations.md`.

### 2) Extract field metadata

- Command: `python3 ./scripts/extract_form_field_info.py input.pdf fields.json`
- Output: `fields.json` with field metadata.

Schema excerpt:

```json
[
  {
    "field_id": "last_name",
    "page": 1,
    "rect": [left, bottom, right, top],
    "type": "text"
  },
  {
    "field_id": "agree_terms",
    "page": 1,
    "type": "checkbox",
    "checked_value": "/Yes",
    "unchecked_value": "/Off"
  }
]
```

### 3) Prepare `field_values.json`

Create a JSON array that maps field IDs to values. For checkboxes and radio groups, use the valid `checked_value` or `radio_options` values from `fields.json`.

```json
[
  {
    "field_id": "last_name",
    "description": "Applicant last name",
    "page": 1,
    "value": "Simpson"
  },
  {
    "field_id": "agree_terms",
    "description": "Terms acknowledgment",
    "page": 1,
    "value": "/Yes"
  }
]
```

### 4) Fill the PDF

- Command: `python3 ./scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf`
- Output: `output.pdf` with filled form fields.
- Verification: open `output.pdf` and confirm values render correctly.

### 5) Validate results

- Confirm the output displays in at least one viewer.
- If a viewer shows empty values, retry in another viewer and report the discrepancy.
