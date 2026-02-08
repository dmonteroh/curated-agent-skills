# Trigger Cases: svelte

## Positive (should activate)
- prompt: "I need help with this: Writing or refactoring Svelte 5 components (runes, snippets, directives). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Working in a SvelteKit app (routing, layouts, load functions, form actions). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project is React/Next/Angular (use stack-specific skills). No planning, just implementation."
  expect_activate: no
