# Trigger Cases: production-audit

## Positive (should activate)
- prompt: "is this ready to ship?"
  expect_activate: yes

- prompt: "We're demoing to the design partner on Thursday. Go through the repo and tell me what's actually going to bite us."
  expect_activate: yes

- prompt: "CI is green but that doesn't tell me much. What's the real risk if we deploy this branch tonight?"
  expect_activate: yes

- prompt: "The billing feature merged this morning. Do a risk pass over it before it goes out."
  expect_activate: yes

- prompt: "What did we miss before launch? I want a list I can hand to the team tomorrow."
  expect_activate: yes

- prompt: "Audit this checkout flow and tell me whether to hold the release — and don't upload our code to anything."
  expect_activate: yes

## Negative (should not activate)
- prompt: "I'm designing our merge-and-deploy gates. Which failures should hard-block a release and which should only warn, and what happens when a gate's signal never arrives?"
  expect_activate: no

- prompt: "I'm halfway through writing this auth middleware. Review the code I've got so far for security bugs."
  expect_activate: no

- prompt: "We need a signed PCI compliance attestation before the audit next month."
  expect_activate: no

- prompt: "Run a full security assessment of the platform — threat model, findings with severity and evidence, remediation plan with owners."
  expect_activate: no

- prompt: "There's no repo or deployment yet, just a product spec. Tell me if it's production ready."
  expect_activate: no
