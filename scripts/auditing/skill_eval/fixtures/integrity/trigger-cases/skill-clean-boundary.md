# Trigger Cases: skill-clean-boundary

## Positive (should activate)
- prompt: "Give me guidance for handling an operational rollback scenario calmly"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Suggest a recipe substitution for buttermilk in pancakes"
  expect_activate: no
