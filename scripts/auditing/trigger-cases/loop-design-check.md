# Trigger Cases: loop-design-check

## Positive (should activate)
- prompt: "I want an agent running every night that fixes whatever tests are failing. What do I need to nail down before I switch it on?"
  expect_activate: yes

- prompt: "We have a loop going and I'm worried it just spins forever burning tokens. How would I tell before it costs us a fortune?"
  expect_activate: yes

- prompt: "The exit condition right now is basically 'the report looks good'. Is that going to work?"
  expect_activate: yes

- prompt: "The same agent writes the fix and then decides whether the fix is acceptable. Is that a problem?"
  expect_activate: yes

- prompt: "I've been kicking this off by hand for a month and I want to put it on a schedule. What's missing before I do that?"
  expect_activate: yes

- prompt: "It's meant to keep our inventory alerts current — there's no end state, it just keeps going. How should that be shaped so it doesn't fire on every tiny fluctuation?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The agent shipped fine last month and now it skips tool calls and makes results up. I need to find which part of our stack is doing it."
  expect_activate: no

- prompt: "I need a background daemon for our CLI that survives across invocations, doesn't spawn duplicates, and shuts itself down when idle."
  expect_activate: no

- prompt: "Just this once, rename that config key everywhere in the repo."
  expect_activate: no

- prompt: "Split this refactor across four workers and tell me which files each one is allowed to touch."
  expect_activate: no

- prompt: "We keep re-deriving the same three selectors every time someone asks for this scrape. Can we write it down once as a script with a saved fixture?"
  expect_activate: no
