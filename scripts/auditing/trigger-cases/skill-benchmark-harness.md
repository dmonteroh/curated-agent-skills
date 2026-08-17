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

- prompt: "It doesn't write a document — it's about which tools the agent reaches for and in what order. We keep the full tool-call log. Can we check whether it's actually being followed?"
  expect_activate: yes

- prompt: "It behaves when I tell it to use the checklist. I want to know whether it still does when the prompt never mentions it, and what happens when I ask for the opposite."
  expect_activate: yes

- prompt: "We're picking between two coding agents for the same backlog. Run them head-to-head on the same tasks and grade them off the same checklist, instead of everyone arguing about which one feels smarter."
  expect_activate: yes

- prompt: "Before we move the team onto the newer model, I want it and the current one measured on our own eval prompts, same guidance loaded in both."
  expect_activate: yes

## Negative (should not activate)
- prompt: "The harness always loads it and there's no way to run without it."
  expect_activate: no

- prompt: "I want to measure whether the output reads more elegantly with it loaded."
  expect_activate: no

- prompt: "Its whole content is a list of our internal service names the model couldn't possibly know. Does the agent read it?"
  expect_activate: no

- prompt: "It only changes how the agent phrases things mid-conversation. Nothing is written out, it calls no tools, and our runner keeps no log we could read back afterwards."
  expect_activate: no

- prompt: "Forget our repo for a second — which of these two models is just better overall? I need a recommendation for the team by Friday."
  expect_activate: no
