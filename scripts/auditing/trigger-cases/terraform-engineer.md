# Trigger Cases: terraform-engineer

## Positive (should activate)
- prompt: "I need help with this: Building or updating Terraform modules and root configurations. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Setting up remote state, locking, and workspace strategies. Can you guide me?"
  expect_activate: yes

- prompt: "We're standing up an Oracle Cloud tenancy. I need reusable modules for the compartment, a VCN and a couple of compute instances, with remote state in object storage."
  expect_activate: yes

- prompt: "Half our estate is on AWS and the new team is on OCI. How do I configure both providers in one root config without the credentials leaking across?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is not Terraform-based infrastructure as code. No planning, just implementation."
  expect_activate: no
