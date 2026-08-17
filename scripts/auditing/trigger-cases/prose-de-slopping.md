# Trigger Cases: prose-de-slopping

## Positive (should activate)
- prompt: "This README reads like a machine wrote it — every paragraph opens the same way — and it has to ship today."
  expect_activate: yes

- prompt: "Go through this release note and mark where it sounds generated. I'm not sure I want to change anything yet, I just want to see it."
  expect_activate: yes

- prompt: "Here's a post I wrote myself and here's the draft. Bring the draft into the same voice."
  expect_activate: yes

- prompt: "I wrote half this doc and generated the other half, and you can see exactly where the seam is."
  expect_activate: yes

## Negative (should not activate)
- prompt: "There's one stray 'delve' in here and otherwise it's all my own writing. Scrub it anyway?"
  expect_activate: no

- prompt: "Write me the launch announcement from these five bullet points."
  expect_activate: no

- prompt: "Get this past the AI-detection checker my university uses."
  expect_activate: no

- prompt: "Tidy up the awkward phrasing in these interview transcript quotes before we print them."
  expect_activate: no

- prompt: "Here are eighteen of my published posts. Work out my house voice from them and write it up so we can reuse it on everything we publish."
  expect_activate: no
