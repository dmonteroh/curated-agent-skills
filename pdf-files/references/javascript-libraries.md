# JavaScript Libraries Reference

## pdf-lib (MIT License)

### Load and manipulate an existing PDF

```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function manipulatePDF() {
  const existingPdfBytes = fs.readFileSync('input.pdf');
  const pdfDoc = await PDFDocument.load(existingPdfBytes);

  const pageCount = pdfDoc.getPageCount();
  console.log(`Document has ${pageCount} pages`);

  const newPage = pdfDoc.addPage([600, 400]);
  newPage.drawText('Added by pdf-lib', {
    x: 100,
    y: 300,
    size: 16,
  });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync('modified.pdf', pdfBytes);
}
```

### Create a PDF from scratch

```javascript
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import fs from 'fs';

async function createPDF() {
  const pdfDoc = await PDFDocument.create();

  const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  const page = pdfDoc.addPage([595, 842]);
  const { width, height } = page.getSize();

  page.drawText('Invoice #12345', {
    x: 50,
    y: height - 50,
    size: 18,
    font: helveticaBold,
    color: rgb(0.2, 0.2, 0.8),
  });

  page.drawRectangle({
    x: 40,
    y: height - 100,
    width: width - 80,
    height: 30,
    color: rgb(0.9, 0.9, 0.9),
  });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync('created.pdf', pdfBytes);
}
```

## pdfjs-dist (Apache License)

### Render a page to a canvas

```javascript
import * as pdfjsLib from 'pdfjs-dist';

pdfjsLib.GlobalWorkerOptions.workerSrc = './pdf.worker.js';

async function renderPDF() {
  const loadingTask = pdfjsLib.getDocument('document.pdf');
  const pdf = await loadingTask.promise;

  const page = await pdf.getPage(1);
  const viewport = page.getViewport({ scale: 1.5 });

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.height = viewport.height;
  canvas.width = viewport.width;

  await page.render({ canvasContext: context, viewport }).promise;
  document.body.appendChild(canvas);
}
```

### Extract text with coordinates

```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function extractText() {
  const loadingTask = pdfjsLib.getDocument('document.pdf');
  const pdf = await loadingTask.promise;
  const page = await pdf.getPage(1);
  const textContent = await page.getTextContent();

  const textWithCoords = textContent.items.map(item => ({
    text: item.str,
    x: item.transform[4],
    y: item.transform[5],
    width: item.width,
    height: item.height,
  }));

  console.log(textWithCoords);
  return textWithCoords;
}
```
