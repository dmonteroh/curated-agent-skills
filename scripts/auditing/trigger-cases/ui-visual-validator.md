# Trigger Cases: ui-visual-validator

## Positive (should activate)
- prompt: "I built this modal and I'm also the one signing it off before release. Is that fine, and what does the sign-off actually have to cover?"
  expect_activate: yes

- prompt: "Here are screenshots of the Japanese build. Our translator says the headings are breaking mid-phrase — can you tell me what's wrong from these?"
  expect_activate: yes

- prompt: "Here are before and after screenshots of the checkout page at 375px, 768px, and 1440px. Can you compare them and tell me whether the new button layout introduced any visual regressions?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I refactored the pricing cards to use CSS grid. Please load the staging page at https://staging.example.com/pricing and verify it still looks right across breakpoints, including overflow, wrapping, and spacing."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review the responsive screenshots for the profile page after the card update and flag anything visually broken at each breakpoint."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "check the new layout on mobile tablet desktop for visual bugs"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

## Negative (should not activate)
- prompt: "Open checkout in a real browser, click through the whole flow, and tell me what errors show up in the console and network tab."
  expect_activate: no

- prompt: "Run an automated accessibility scanner against this page and give me the violations it reports."
  expect_activate: no

- prompt: "Design a new color palette and spacing scale for our app's dark mode and give me the design tokens."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Take a screenshot of the login page and save it to the docs folder for the README. I just need the image, not a review."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Make the pricing page responsive for mobile by adding the needed media queries."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Profile the dashboard page load and tell me why the first contentful paint is slow."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Check whether the new navigation links work correctly on every screen size."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Redesign the settings page layout to improve the mobile experience."
  expect_activate: no
  tags: [generated, gen:codex]
