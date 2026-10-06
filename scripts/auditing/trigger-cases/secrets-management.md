# Trigger Cases: secrets-management

## Positive (should activate)

- prompt: "how rotate db password in prod without downtime"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We just found out a contractor's laptop was stolen and it had our AWS access keys in ~/.aws/credentials. Walk me through what to revoke, how to rotate, and how to check CloudTrail for misuse."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our GitHub Actions workflows currently use a long-lived deploy token stored as a repo secret that every maintainer can read. How should I restructure this so secrets are scoped, rotated, and not exposed in logs?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our team shares passwords in a Slack channel and keeps some in a spreadsheet. Help me pick and roll out a proper secrets management setup for laptops, CI, and servers, including who gets read access."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Audit how passwords, API keys, and tokens are stored and accessed across our CI/CD pipelines, production servers, and developer laptops, then propose a rotation and leak-response plan."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Create a secrets-management policy covering where credentials live, which roles and services can read them, how often they rotate, and the steps to take if one is exposed."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Design a secure workflow for injecting API keys and tokens into builds and servers without committing them to code, including ownership, rotation, and emergency revocation."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Write a login form with email and password fields, including client-side validation for password strength and a show/hide toggle."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Set up OAuth2 login with Google for my Express app, including the callback route and session handling."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "I forgot my own laptop login password on Fedora and I'm locked out. How do I reset it from the recovery mode?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you generate a strong random 32-character string I can use as a test fixture API key in my unit tests? It's fake data, nothing real."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Please review my Terraform for the VPC and security groups and point out any overly permissive ingress rules."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up single sign-on and MFA for all employee access to internal applications."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a data-retention policy for customer records and application logs."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Help me reset the password for my cloud account after I forgot it."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
