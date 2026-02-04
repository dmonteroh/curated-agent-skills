# Command-Line Tools Reference

## poppler-utils (GPL-2 License)

### Extract text with bounding boxes

```bash
pdftotext -bbox-layout document.pdf output.xml
```

### Convert pages to images

```bash
pdftoppm -png -r 300 document.pdf output_prefix
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res_pages
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

### Extract embedded images

```bash
pdfimages -j -p document.pdf page_images
pdfimages -list document.pdf
pdfimages -all document.pdf images/img
```

## qpdf (Apache License)

### Split, merge, and extract pages

```bash
qpdf --split-pages=3 input.pdf output_group_%02d.pdf
qpdf input.pdf --pages input.pdf 1,3-5,8,10-end -- extracted.pdf
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 doc3.pdf 2,4 -- combined.pdf
```

### Optimize and repair

```bash
qpdf --linearize input.pdf optimized.pdf
qpdf --optimize-level=all input.pdf compressed.pdf
qpdf --check input.pdf
qpdf --fix-qdf damaged.pdf repaired.pdf
qpdf --show-all-pages input.pdf > structure.txt
```

### Encryption workflows

```bash
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf
qpdf --show-encryption encrypted.pdf
qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf
```
