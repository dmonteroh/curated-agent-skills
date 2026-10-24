# Trigger Cases: clean

## Positive (should activate)
- prompt: "Help me plan a birthday party for my nephew next month."
  expect_activate: yes
- prompt: "What restaurants nearby serve good ramen tonight?"
  expect_activate: yes
- prompt: "I want to repaint the fence this weekend, any tips?"
  expect_activate: yes
- prompt: "Suggest a workout routine for someone recovering from a knee injury."
  expect_activate: yes
- prompt: "Recommend a good beginner sourdough recipe with a starter guide."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Compile the quarterly sales spreadsheet into a single tab."
  expect_activate: no
- prompt: "Translate this paragraph into Portuguese for the newsletter."
  expect_activate: no
- prompt: "Reboot the staging server and confirm the health check passes."
  expect_activate: no
- prompt: "Write unit tests for the checkout total calculator."
  expect_activate: no
- prompt: "Give me sourdough baking troubleshooting tips for a dense loaf."
  expect_activate: no
  tags: [near-miss]
