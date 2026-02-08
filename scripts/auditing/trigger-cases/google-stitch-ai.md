# Trigger Cases: google-stitch-ai

## Positive (should activate)
- prompt: "I need help with this: A `DESIGN.md` is needed to capture a Stitch project’s design language. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A prompt needs enhancement for Stitch or similar UI generators. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request needs user research, product strategy, or a full UX design brief. No planning, just implementation."
  expect_activate: no
