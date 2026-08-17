# Trigger Cases: skill-benchmark-harness

## Positive (should activate)
- prompt: "I just wrote this thing and the only case for it is that it reads well. Show me it actually changes what the agent produces."
  expect_activate: yes

- prompt: "Half the assertions on this checklist pass no matter what. Which of them carry any signal at all?"
  expect_activate: yes

- prompt: "Since we started loading this file the agent seems worse at the easy cases. Can we check that properly rather than arguing about it?"
  expect_activate: yes

- prompt: "I have two iterations of the same guidance and I want them compared on the same set of eval prompts."
  expect_activate: yes

- prompt: "A reviewer asked me what this actually changes about the output and all I have is an opinion."
  expect_activate: yes

## Negative (should not activate)
- prompt: "The harness always loads it and there's no way to run without it."
  expect_activate: no

- prompt: "I want to measure whether the output reads more elegantly with it loaded."
  expect_activate: no

- prompt: "Its whole content is a list of our internal service names the model couldn't possibly know. Does the agent read it?"
  expect_activate: no

- prompt: "It governs how the agent talks in conversation. There's no file or artifact at the end of a run."
  expect_activate: no

- prompt: "The open question is whether we should be running this on the bigger model or the small one."
  expect_activate: no
