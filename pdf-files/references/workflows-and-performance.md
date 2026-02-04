# Workflows and Performance Reference

## Extract figures and images

### Method 1: pdfimages (fast)

```bash
pdfimages -all document.pdf images/img
```

### Method 2: pypdfium2 with image processing

```python
import pypdfium2 as pdfium
import numpy as np

def extract_figures(pdf_path):
    pdf = pdfium.PdfDocument(pdf_path)
    for page in pdf:
        bitmap = page.render(scale=3.0)
        image = bitmap.to_pil()
        image_array = np.array(image)
        mask = np.any(image_array != [255, 255, 255], axis=2)
        _ = mask
```

## Batch PDF processing with error handling

```python
import glob
import logging
from pypdf import PdfReader, PdfWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_pdfs(input_dir, operation="merge"):
    pdf_files = glob.glob(f"{input_dir}/*.pdf")

    if operation == "merge":
        writer = PdfWriter()
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Processed: {pdf_file}")
            except Exception as exc:
                logger.error(f"Failed to process {pdf_file}: {exc}")
        with open("batch_merged.pdf", "wb") as output:
            writer.write(output)

    if operation == "extract_text":
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                text = "".join(page.extract_text() or "" for page in reader.pages)
                output_file = pdf_file.replace(".pdf", ".txt")
                with open(output_file, "w", encoding="utf-8") as output:
                    output.write(text)
                logger.info(f"Extracted text from: {pdf_file}")
            except Exception as exc:
                logger.error(f"Failed to extract text from {pdf_file}: {exc}")
```

## Advanced PDF cropping

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

writer.add_page(page)
with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

## Performance optimization tips

- Use streaming approaches instead of loading entire PDFs in memory.
- Use `qpdf --split-pages` for very large PDFs.
- Process pages individually with `pypdfium2` for rendering.
- For text extraction, prefer `pdftotext -bbox-layout` or `pdfplumber` on complex layouts.
- For previews, use low-resolution renders and reserve high-resolution output for final artifacts.

## Memory management example

```python
from pypdf import PdfReader, PdfWriter

def process_large_pdf(pdf_path, chunk_size=10):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for start_idx in range(0, total_pages, chunk_size):
        end_idx = min(start_idx + chunk_size, total_pages)
        writer = PdfWriter()
        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])
        with open(f"chunk_{start_idx // chunk_size}.pdf", "wb") as output:
            writer.write(output)
```
