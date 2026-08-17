# Trigger Cases: cloud-architect

## Positive (should activate)
- prompt: "I need help with this: Designing a cloud system or migrating to cloud. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing services and shaping the platform (networking, IAM, data, compute). Can you guide me?"
  expect_activate: yes

- prompt: "We're keeping our datacenter and moving half the workloads to Azure. What's the right way to link the two — VPN or a dedicated circuit — and how do we make it redundant?"
  expect_activate: yes

- prompt: "The colo-to-VPC link went down twice last month and nobody noticed until users did. How should that connection be shaped and watched?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is limited to CI/CD pipeline design or deployment automation. No planning, just implementation."
  expect_activate: no

- prompt: "Redesign the VLANs and switch stack in our office network. Nothing here is going to the cloud."
  expect_activate: no
