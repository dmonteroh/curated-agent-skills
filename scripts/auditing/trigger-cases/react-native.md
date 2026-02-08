# Trigger Cases: react-native

## Positive (should activate)
- prompt: "I need help with this: Building React Native features/components. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Implementing navigation (Expo Router / React Navigation). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project is React web or Next.js only. No planning, just implementation."
  expect_activate: no
