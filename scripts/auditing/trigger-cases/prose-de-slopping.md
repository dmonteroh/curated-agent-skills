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

- prompt: "make this sound less like chatgpt"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Please edit the following product description so it doesn't read like AI slop. Cut the filler and the stacked adjectives, vary the sentence rhythm, but leave the specs alone since those are accurate: 'Elevate your mornings with our revolutionary, state-of-the-art stainless steel kettle. Seamlessly blending style and functionality, it boasts a 1.7L capacity and 3-minute boil time. Experience the difference today!'"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "A coworker sent me this Slack announcement and it's obviously generated. Can you make it sound like an actual human wrote it? Keep the dates and the Friday deadline exactly as they are. 'We are excited to announce that our Q3 planning session will take place on Oct 14. It is important to note that all teams should submit their roadmaps by Friday. Let's collaborate to unlock our full potential!'"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Edit this blog post to sound like a real person wrote it; don’t overhaul passages that already read naturally."
  expect_activate: yes
  tags: [generated, gen:codex]

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

- prompt: "Can you write a short paragraph in an obviously robotic, corporate AI voice, full of 'delve' and 'tapestry'? It's for a parody sketch I'm writing."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Proofread this paragraph for typos and grammar errors only. Don't change the wording or style at all."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Make this text harder for AI detectors to flag, even if you need to change the meaning and structure completely."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Write me a cover letter for a patient coordinator job. I have eight years of night-shift nursing experience at a hospital."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Summarize this 2,000-word article into five bullet points I can paste into a newsletter."
  expect_activate: no
  tags: [generated, gen:claude]
