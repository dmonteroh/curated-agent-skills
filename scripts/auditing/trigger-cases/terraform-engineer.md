# Trigger Cases: terraform-engineer

## Positive (should activate)
- prompt: "I need help with this: Building or updating Terraform modules and root configurations. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Setting up remote state, locking, and workspace strategies. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is not Terraform-based infrastructure as code. No planning, just implementation."
  expect_activate: no
