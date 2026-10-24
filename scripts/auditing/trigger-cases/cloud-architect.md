# Trigger Cases: cloud-architect

## Positive (should activate)
- prompt: "We're keeping our datacenter and moving half the workloads to Azure. What's the right way to link the two — VPN or a dedicated circuit — and how do we make it redundant?"
  expect_activate: yes

- prompt: "The colo-to-VPC link went down twice last month and nobody noticed until users did. How should that connection be shaped and watched?"
  expect_activate: yes

- prompt: "azure setup plan vpn to our hq plus dr"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We're moving our order management platform from our on-prem data center to AWS. Can you design the landing zone for it: account structure, VPC layout, how we connect back to the office data center, IAM approach, and a DR plan with RTO of 1 hour?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We're a 200-person company with a single office server room, and we want to host our customer portal in AWS. Write up how accounts should be organized, network segments, Site-to-Site VPN or Direct Connect to the office, who gets what permissions, and backup/failover."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Propose the target AWS infrastructure model for a regulated workload, with production/nonproduction account separation, network segmentation, VPN or Direct Connect options, identity governance, and DR runbooks."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Redesign the VLANs and switch stack in our office network. Nothing here is going to the cloud."
  expect_activate: no

- prompt: "Write Terraform modules to deploy the VPC, subnets, and NAT gateways we already designed for our AWS production account."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Compare Azure DevOps and GitHub Actions for our CI/CD pipelines and recommend one with a migration plan for our build jobs."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review this existing IAM policy JSON and tell me whether it's too permissive for an S3 bucket."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Create an incident-response playbook for ransomware affecting workloads already deployed in Azure."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Draft a disaster-recovery plan for our on-premises VMware environment, including backup retention and alternate-site recovery."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
