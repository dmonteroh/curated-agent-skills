# Trigger Cases: collision-b

## Positive (should activate)
- prompt: "Plan a three-course dinner menu for eight guests."
  expect_activate: yes
- prompt: "Suggest a wine pairing for a roast chicken dinner."
  expect_activate: yes
- prompt: "Build a grocery list for a dinner party this weekend."
  expect_activate: yes
- prompt: "Shared prompt used by both fixture skills for the collision test."
  expect_activate: yes
- prompt: "Shared negative prompt claimed positive by the other fixture skill."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Reset the CI cache and rerun the failing pipeline."
  expect_activate: no
- prompt: "Compile the quarterly sales spreadsheet into a single tab."
  expect_activate: no
- prompt: "Translate this paragraph into Portuguese for the newsletter."
  expect_activate: no
- prompt: "Reboot the staging server and confirm the health check passes."
  expect_activate: no
- prompt: "Write unit tests for the checkout total calculator."
  expect_activate: no
