# Trigger Cases: below-floor

## Positive (should activate)
- prompt: "Plan a weekend hiking trip through the nearby hills."
  expect_activate: yes
- prompt: "Suggest three good campsites within two hours of the city."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Deploy the latest build to the production cluster."
  expect_activate: no
