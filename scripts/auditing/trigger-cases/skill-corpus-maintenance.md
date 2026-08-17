# Trigger Cases: skill-corpus-maintenance

## Positive (should activate)
- prompt: "I've got about sixty skills in my agent setup now and half of them I don't remember writing. Can we go through the whole lot and work out what's still pulling its weight?"
  expect_activate: yes

- prompt: "Almost every one of my skills tells the agent to run the tests before pushing. That feels like it should live in the rules file once instead of being repeated fifteen times."
  expect_activate: yes

- prompt: "A lot of these were written a year ago and name CLI flags that don't exist anymore. I want a proper sweep for anything stale or duplicated across the set."
  expect_activate: yes

- prompt: "I inherited this agent config from someone who left. Nobody here knows what half these instruction files are for or whether anything still needs them."
  expect_activate: yes

- prompt: "We started this review last month and it got cut off partway through. Can you pick it up from where it stopped rather than starting from scratch?"
  expect_activate: yes

- prompt: "Just pulled in twelve more skills from a shared repo. Do any of them collide with what I already had installed?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Every session is about a third full before I type a word. Break down what's eating that and what I can cut to win tokens back."
  expect_activate: no

- prompt: "I just finished writing this one skill. Can you check it against our quality checklist before I commit it?"
  expect_activate: no

- prompt: "I want to prove this skill actually changes what the agent produces. Run the same tasks with it and without it and compare the results."
  expect_activate: no

- prompt: "Our onboarding guide and our contributing guide repeat a lot of the same material. Can you tidy that up?"
  expect_activate: no

- prompt: "I have three skills total. Just read them and tell me what you think."
  expect_activate: no
