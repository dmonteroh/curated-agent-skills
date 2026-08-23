# Trigger Cases: ui-demo

## Positive (should activate)
- prompt: "Can you record a short walkthrough video of the new invoice flow? It's going on the onboarding page and the audience is non-technical."
  expect_activate: yes

- prompt: "I need a screen recording that shows a user creating a project, inviting a teammate, and switching to dark mode — something I can drop straight into the release notes."
  expect_activate: yes

- prompt: "We recorded a demo of the settings page last quarter but the layout has changed since. Re-shoot it against the current build."
  expect_activate: yes

- prompt: "My demo recording script keeps dying halfway through — the video just shows the same page sitting there for twenty seconds and then it ends. What am I doing wrong?"
  expect_activate: yes

- prompt: "Make me a tutorial video of the reporting dashboard for a stakeholder presentation on Thursday. It needs a visible cursor and captions."
  expect_activate: yes

- prompt: "Record the checkout flow end to end at a pace someone who has never used the product could follow, and save it as checkout-demo."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Here are before and after screenshots of the pricing page. Did the padding change land correctly, and did anything else regress?"
  expect_activate: no

- prompt: "Open the app in a real browser, click through the whole signup flow, and tell me whether anything errors in the console or fails in the network tab."
  expect_activate: no

- prompt: "Run an accessibility scan over the dashboard and give me the WCAG violations it reports."
  expect_activate: no

- prompt: "The settings screen feels cluttered and nobody finds the export button. Can you propose a better layout and write up the component spec?"
  expect_activate: no

- prompt: "Record a terminal session showing how to install our CLI and configure a profile, so I can embed it in the README."
  expect_activate: no
