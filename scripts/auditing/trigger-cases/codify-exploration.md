# Trigger Cases: codify-exploration

## Positive (should activate)
- prompt: "That extraction was right. I've now asked you for the same incident list three times this week — stop re-deriving it from scratch every time."
  expect_activate: yes

- prompt: "You're about to work out the same selectors and field names for this feed that you figured out yesterday."
  expect_activate: yes

- prompt: "This summary has to come out identical every run, and if the parsing quietly drifted I would never notice."
  expect_activate: yes

- prompt: "We'll want this same pull again next month. Make it something that replays rather than a fresh guess each session."
  expect_activate: yes

## Negative (should not activate)
- prompt: "I just wanted the open PR count on that repo today. Got it, thanks — nothing else needed."
  expect_activate: no

- prompt: "The flow places an order and then cancels it. I want that whole sequence automated end to end."
  expect_activate: no

- prompt: "What's worth keeping here isn't the steps, it's the list of what each field actually means. Where should those notes live?"
  expect_activate: no

- prompt: "The script and its captured sample already exist for this one — just run it and give me the output."
  expect_activate: no
