# Python Libraries Reference

## pypdfium2 (Apache/BSD License)

Python bindings for PDFium, useful for fast rendering and text extraction.

### Render PDF to images

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0, rotation=0)
image = bitmap.to_pil()
image.save("page_1.png", "PNG")

for index, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    image = bitmap.to_pil()
    image.save(f"page_{index + 1}.jpg", "JPEG", quality=90)
```

### Extract text

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for index, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {index + 1} text length: {len(text)} chars")
```

## pdfplumber (MIT License)

### Extract text with coordinates

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    for char in page.chars[:10]:
        print(f"Char: '{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

### Table extraction with custom settings

```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15,
    }
    tables = page.extract_tables(table_settings)
```

## reportlab (BSD License)

### Create a report with tables

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

data = [
    ["Product", "Q1", "Q2", "Q3", "Q4"],
    ["Widgets", "120", "135", "142", "158"],
    ["Gadgets", "85", "92", "98", "105"],
]

doc = SimpleDocTemplate("report.pdf")
elements = []
styles = getSampleStyleSheet()
elements.append(Paragraph("Quarterly Sales Report", styles["Title"]))

table = Table(data)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 14),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)
doc.build(elements)
```
