# Trigger Cases: pdf-files

## Positive (should activate)

- prompt: "I've got a 40-page vendor contract at ./contracts/acme_msa.pdf. Can you extract all the text from it and save it to a .txt file so I can search through it?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "There's a table of quarterly revenue on pages 6-8 of report_q3.pdf. Pull those tables out into a CSV I can open in Excel."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need to fill out the W-9 form I downloaded (w9.pdf). Name is Dana Whitfield, business name Whitfield Design LLC, and the address is 412 Alder St, Portland, OR 97205. Fill in the fields and save it as w9_filled.pdf."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "pull the tables out of statement.pdf"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Convert pages 3–8 of this invoice PDF into separate high-resolution PNG images."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Fill out the attached rental application PDF using the details in this message, then return the completed PDF."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Extract the names, dates, and amounts from every table in these scanned PDF statements."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you convert my Word document thesis.docx into a nicely formatted LaTeX file?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Summarize the main arguments of the essay I pasted below in three bullet points."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Resize and compress all the JPEG photos in my vacation folder so they're under 500 KB each."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you explain what the PDF/A standard is and why archives prefer it over regular PDFs?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Build a React component that lets users upload a PDF and shows a progress bar during upload. No need to read the PDF contents, just the upload UI."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Fill in the missing values in the 'age' column of my pandas DataFrame using the median, then export the table to an Excel file."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Redesign this PDF brochure with a more modern visual style."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
