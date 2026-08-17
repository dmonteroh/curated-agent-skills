# Trigger Cases: agent-harness-portability

## Positive (should activate)
- prompt: "This instruction file claims it works with any coding agent, but it has only ever been run under one. How do I actually check that claim?"
  expect_activate: yes

- prompt: "We wrote our whole instruction corpus against one agent and now need it to work under a second one too."
  expect_activate: yes

- prompt: "Our AGENTS.md names specific tools and hardcodes absolute paths. I doubt any of that survives a change of agent."
  expect_activate: yes

- prompt: "Someone handed me a support matrix saying we cover three agents. No versions on it, no dates. Is it worth anything?"
  expect_activate: yes

- prompt: "The same markdown files get read directly by three different agents rather than compiled per agent — what has to be kept out of them?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "We only ever support one agent and never plan to add another. I want to tighten the wording of its tool instructions."
  expect_activate: no

- prompt: "The helper script bundled with this skill dies with a missing-file error when the agent runs it."
  expect_activate: no

- prompt: "What's the maximum length allowed for a skill description in Claude Code frontmatter?"
  expect_activate: no
