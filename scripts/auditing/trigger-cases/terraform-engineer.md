# Trigger Cases: terraform-engineer

## Positive (should activate)
- prompt: "We're standing up an Oracle Cloud tenancy. I need reusable modules for the compartment, a VCN and a couple of compute instances, with remote state in object storage."
  expect_activate: yes

- prompt: "Half our estate is on AWS and the new team is on OCI. How do I configure both providers in one root config without the credentials leaking across?"
  expect_activate: yes

- prompt: "terraform s3 backend with locking for prod"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I need a Terraform module for an AWS VPC with public and private subnets across three AZs, NAT gateways, and outputs for subnet IDs. Then wire it into a dev and prod environment using the same module with different CIDR ranges."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please restructure our repo so we have environments/dev, environments/staging, and environments/prod directories, each calling shared modules in modules/. Right now everything is in one main.tf with a bunch of count hacks."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Add Terraform code to provision an Azure resource group, virtual network, and AKS cluster, storing state remotely in an Azure Storage backend."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Refactor this AWS infrastructure into reusable Terraform modules and wire them into separate sandbox and production root configurations."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Debug the failing Terraform plan in our GCP environment and update the modules so dev and prod can use different machine sizes."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Write a Dockerfile and docker-compose file for our Node.js API with a Postgres container for local development."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you write an Ansible playbook that installs nginx on our existing Ubuntu servers and deploys a templated config file?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Set up a GitHub Actions workflow that runs unit tests and lints our Python code on every pull request."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a Kubernetes Deployment and Service YAML for my app, plus a Helm chart skeleton. The cluster already exists."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you write a Python script using boto3 to list all unattached EBS volumes across our AWS regions and print their sizes?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a CloudFormation template that deploys an AWS VPC and ECS service."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a Bash script that creates AWS networking resources equivalent to our current Terraform setup."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
