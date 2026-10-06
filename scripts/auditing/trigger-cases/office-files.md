# Trigger Cases: office-files

## Positive (should activate)
- prompt: "PowerPoint says this deck needs repairing every time we open it. Can you work out what's actually broken inside the file?"
  expect_activate: yes

- prompt: "I reordered the slides in this pptx last week. When I pull the text out with a script the slides come back in the wrong order — what am I doing wrong?"
  expect_activate: yes

- prompt: "The client sent a deck as a style reference. Pull out its structure, fonts and colours for me, and don't touch the original."
  expect_activate: yes

- prompt: "Can you read through Q3_board_deck.pptx and give me a slide-by-slide summary? I only have ten minutes before the meeting."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I have two versions of our vendor contract, contract_v3.docx and contract_v4_redlined.docx. Compare them and list every substantive change in the clauses on liability and termination."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "summarize roadmap.pptx"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Read the three attached Word contracts and produce a table showing how their termination clauses differ."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Extract the main findings and recommendations from this Excel survey-results workbook."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Take the master and colour palette out of that reference deck and build me a new twelve-slide pitch from them."
  expect_activate: no

- prompt: "Rewrite this contract in Word with tracked changes so legal can see every edit I made."
  expect_activate: no

- prompt: "Write a Python script using openpyxl that generates a monthly expense spreadsheet with formulas for subtotals and a chart. I want to run it myself later."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Summarize this PDF annual report for me: annual_report_2025.pdf. Just the highlights from the financial section."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Explain the difference between VLOOKUP and XLOOKUP in Excel and when to use each."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Create a PowerPoint deck from these meeting notes for next week's client presentation."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Update the formulas and formatting in this Excel budget workbook to include the new regional forecasts."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Read this screenshot of a spreadsheet and list the numbers in the revenue column."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
