# Trigger Cases: ui-design

## Positive (should activate)
- prompt: "We're building an internal invoicing tool. There's no brand, no colours, no reference material, and honestly I don't know what I want it to look like. Where do we start?"
  expect_activate: yes

- prompt: "You showed me three directions and I picked the second one. The header feels heavy and the cards are louder than the data — let's do another round on it."
  expect_activate: yes

- prompt: "Audit our checkout flow against WCAG AA. Start with a scanner pass so we know what's already flagged, then go through the criteria a tool can't decide, and rank what comes back by severity."
  expect_activate: yes

- prompt: "Keyboard users tell me that once they tab past the fold, the sticky header sits on top of whatever is focused. Is that an actual WCAG failure, and what's the fix?"
  expect_activate: yes

- prompt: "I'm building a mobile app for tracking houseplant watering. Before I write any code, can you map out the screens, the main components, a basic design system (colors, type, spacing), and the accessibility requirements?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before we build the checkout experience, produce a UI/UX specification covering the cart, shipping, payment, confirmation screens, error paths, component patterns, and inclusive-design rules."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Help us define the product design for a SaaS analytics dashboard: layout for each view, interactions between views, component states, responsive behavior, and keyboard/screen-reader support."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "need a ui plan for a recipe app screens and components"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "Marketing signed off on the brand kit last month. Just apply those tokens to the new screens — don't propose anything else."
  expect_activate: no

- prompt: "Attaching a screenshot of the dashboard we shipped this morning. Compare it against the mock and tell me what looks wrong."
  expect_activate: no

- prompt: "Implement the login form component in React with email and password fields, validation, and error messages using our existing Button and Input components."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Convert this finished Figma export into pixel-accurate HTML and Tailwind CSS."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Plan the architecture of the backend services for my app: databases, queues, and API boundaries."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a marketing strategy and launch email campaign for a new patient appointment-booking portal."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Run usability testing on our existing appointment portal and summarize the findings."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Implement the frontend for our meal-delivery app in React, including responsive CSS and API integration."
  expect_activate: no
  tags: [generated, gen:codex]
