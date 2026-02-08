# Trigger Cases: cloud-architect

## Positive (should activate)
- prompt: "I need help with this: Designing a cloud system or migrating to cloud. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing services and shaping the platform (networking, IAM, data, compute). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is limited to CI/CD pipeline design or deployment automation. No planning, just implementation."
  expect_activate: no
