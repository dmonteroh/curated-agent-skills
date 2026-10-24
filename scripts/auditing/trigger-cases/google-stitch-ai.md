# Trigger Cases: google-stitch-ai

## Positive (should activate)
- prompt: "All I have is a rough idea — a mobile settings screen with profile, notifications and a dark mode toggle. Can you turn that into a proper Stitch-ready prompt?"
  expect_activate: yes

- prompt: "I have a Stitch project called \"Fintech Dashboard Mobile\" with about eight screens. Can you pull the design and write up a summary of its visual style: colors, typography, corner radii, spacing, and the overall mood?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Look at my Google Stitch project for the meal-planning app and write a design system document that captures its look and feel, so I can hand it to a contractor."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Can you extract the design language from my Stitch project 'Travel Booking v2' and give me a paragraph I can paste into future Stitch prompts so new screens stay consistent?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review my Google Stitch project and write a concise style guide covering the layout, colors, typography, spacing, visual hierarchy, and component patterns."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Look at the screens in my Google Stitch project and turn their aesthetic into detailed prompts I can reuse to generate matching new pages in Stitch."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "write better stitch prompts from my project design"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)

- prompt: "Convert the screens in my Stitch project into React components with Tailwind classes and wire up routing between them."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a brand guidelines document for my company from scratch. We don't have any designs yet, just a mission statement and a target audience."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Compare Figma and Google Stitch for a small team and tell me which one is better for rapid prototyping, with pros and cons."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Audit the accessibility of my Stitch screens and list contrast, keyboard navigation, and screen-reader issues."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a brand strategy and voice-and-tone document inspired by the company behind this Stitch project."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Use my Stitch design as a reference and recreate the same interface exactly in Figma."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
