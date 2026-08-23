# Trigger Cases: office-files

## Positive (should activate)
- prompt: "I need help with this: The user needs to read/extract content from `.docx`, `.pptx`, or `.xlsx`. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The user needs to compare two versions of an office file (visual/textual diff). Can you guide me?"
  expect_activate: yes

- prompt: "PowerPoint says this deck needs repairing every time we open it. Can you work out what's actually broken inside the file?"
  expect_activate: yes

- prompt: "I reordered the slides in this pptx last week. When I pull the text out with a script the slides come back in the wrong order — what am I doing wrong?"
  expect_activate: yes

- prompt: "The client sent a deck as a style reference. Pull out its structure, fonts and colours for me, and don't touch the original."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The file is not OOXML (e.g. `.doc`, `.xls`, `.ppt`). No planning, just implementation."
  expect_activate: no

- prompt: "Take the master and colour palette out of that reference deck and build me a new twelve-slide pitch from them."
  expect_activate: no

- prompt: "Rewrite this contract in Word with tracked changes so legal can see every edit I made."
  expect_activate: no
