# Trigger Cases: ui-visual-validator

## Positive (should activate)
- prompt: "I need help with this: Confirming a UI change is actually correct (not just 'different'). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Catching visual regressions before merge/release. Can you guide me?"
  expect_activate: yes

- prompt: "I built this modal and I'm also the one signing it off before release. Is that fine, and what does the sign-off actually have to cover?"
  expect_activate: yes

- prompt: "Here are screenshots of the Japanese build. Our translator says the headings are breaking mid-phrase — can you tell me what's wrong from these?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Designing a UI or exploring new layouts. No planning, just implementation."
  expect_activate: no

- prompt: "Open checkout in a real browser, click through the whole flow, and tell me what errors show up in the console and network tab."
  expect_activate: no

- prompt: "Run an automated accessibility scanner against this page and give me the violations it reports."
  expect_activate: no
