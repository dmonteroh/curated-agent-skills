# Trigger Cases: plan-review

## Positive (should activate)
- prompt: "Here's the implementation plan before anyone writes a line of code. Go through it properly and tell me what's wrong with it."
  expect_activate: yes

- prompt: "This spec has grown well past the original ask and nobody has examined whether that scope is justified."
  expect_activate: yes

- prompt: "I don't want a pile of opinions dumped at the end — give me decisions on this design doc that I can sign off or reject."
  expect_activate: yes

- prompt: "The last pass over this codebase raised six issues and four of them weren't real. I need findings gated on quoted evidence this time."
  expect_activate: yes

- prompt: "The design is written up but nobody has put a single alternative next to it. Can we fix that before it goes to implementation?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The change is already written. Tell me whether the diff is correct."
  expect_activate: no

- prompt: "I don't know what we should build yet — help me think through the options."
  expect_activate: no

- prompt: "The plan is to bump the request timeout from 30s to 60s in the config file."
  expect_activate: no

- prompt: "The architect made the call and it's final. Just implement it as written."
  expect_activate: no
