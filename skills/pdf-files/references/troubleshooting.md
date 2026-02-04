# Troubleshooting Reference

## Encrypted PDFs

```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

## Corrupted PDFs

```bash
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

## Text extraction issues

If text extraction yields empty output, treat the PDF as scanned and switch to image conversion or OCR.

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    return "".join(pytesseract.image_to_string(image) for image in images)
```
