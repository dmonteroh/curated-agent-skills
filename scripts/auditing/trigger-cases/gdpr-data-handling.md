# Trigger Cases: gdpr-data-handling

## Positive (should activate)

- prompt: "I'm building a patient registration app for a clinic network in Germany and France. It needs to be GDPR compliant: record consent with timestamps and purpose, let patients export their data, handle erasure requests, enforce retention periods, and have a workflow for logging and reporting breaches within 72 hours. Can you scaffold it in Django with Postgres?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Create a Node/TypeScript service for an HR system that holds employee personal data for our offices across the EU. Include lawful basis tracking per data field, subject access request handling with deadlines, deletion and anonymization jobs, configurable retention policies, and a data breach register that generates the supervisory authority notification."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Build me a membership app for a Spanish nonprofit that stores members' contact details and donation history. It must follow EU data protection law: explicit opt-in consent for newsletters, a self-service page where members can download or delete their data, retention rules that purge lapsed members after 3 years, and a process for handling breaches."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "need app to store eu customer data with consent and deletion requests"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Make our customer platform GDPR-compliant for EU users, including consent records, data-subject access requests, erasure, retention rules, and breach notification workflows."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Update the app so it can lawfully handle Europeans’ personal data under EU privacy requirements: collect valid consent, export user data on request, delete accounts, enforce retention periods, and manage security incidents."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Audit and implement the product changes needed for GDPR compliance around personal-data consent, access requests, deletion requests, data retention, and breach handling."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Build a CRM app for my sales team in the US that stores leads, contact info and deal stages. Include pipelines and email reminders."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you set up a SIEM-style dashboard that detects intrusion attempts on our servers and alerts on suspicious logins?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a script that encrypts a PostgreSQL database backup with AES-256 and uploads it to S3 nightly."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review this existing Express app and tell me whether its login flow is vulnerable to SQL injection or session fixation."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Make our US customer-data workflow comply with CCPA and CPRA, including California consumer requests and sale/sharing opt-outs."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create an incident dashboard that alerts engineering whenever an application error rate spikes."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
