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

- prompt: "will my claude.md work in cursor and codex too fix whatever breaks"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We have a skill folder with a SKILL.md that uses allowed-tools frontmatter and the Task tool. Audit it for portability to other coding agents and fix anything that's Claude-specific."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Audit this assistant instruction file for portability across Cursor, Claude Code, GitHub Copilot, and Codex, then revise any directives that rely on tool names, agent roles, or features that the other assistants do not support."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Review our Codex-specific workflow guide against Cursor and Copilot capabilities. Identify instructions that will fail elsewhere and rewrite them into portable equivalents."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "We only ever support one agent and never plan to add another. I want to tighten the wording of its tool instructions."
  expect_activate: no

- prompt: "The helper script bundled with this skill dies with a missing-file error when the agent runs it."
  expect_activate: no

- prompt: "What's the maximum length allowed for a skill description in Claude Code frontmatter?"
  expect_activate: no

- prompt: "Explain the difference between Claude Code hooks and subagents and when I'd use each."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Check whether my Python script's dependencies will work on both Linux and macOS and fix the ones that won't."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Review my CLAUDE.md for clarity and redundancy and tighten the wording. It only needs to work in Claude Code."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Compare the quality of code changes produced by Codex, Cursor, and Claude Code on the same benchmark repository."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Review whether our AI assistant instructions follow our company security policy and remove unsafe permissions."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Port this application from a Codex-generated codebase to one that runs on GitHub Codespaces."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
