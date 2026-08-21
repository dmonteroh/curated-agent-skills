# Trigger Cases: security-auditor

## Positive (should activate)
- prompt: "I need help with this: Running security audits or risk assessments. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reviewing SDLC security controls, CI/CD, or compliance readiness. Can you guide me?"
  expect_activate: yes

- prompt: "Assume the attacker's goal is reading another tenant's documents. Walk me through every route that gets them there."
  expect_activate: yes

- prompt: "We can fund two of these five hardening items this quarter. Which two shut down the most ways in?"
  expect_activate: yes

- prompt: "Semgrep gave me 40 hits on this open-source project. Which ones would actually get accepted by their disclosure program instead of closed as informative?"
  expect_activate: yes

- prompt: "Our PCI assessment is in six weeks. Work out what card data the checkout service ends up keeping and whether anything unmasked reaches the logs."
  expect_activate: yes

- prompt: "Conduct comprehensive security audit of microservices architecture with DevSecOps integration"
  expect_activate: yes

- prompt: "Implement zero-trust authentication system with multi-factor authentication and risk-based access"
  expect_activate: yes

- prompt: "Design security pipeline with SAST, DAST, and container scanning for CI/CD workflow"
  expect_activate: yes

- prompt: "Create GDPR-compliant data processing system with privacy by design principles"
  expect_activate: yes

- prompt: "Perform threat modeling for cloud-native application with Kubernetes deployment"
  expect_activate: yes

- prompt: "Implement secure API gateway with OAuth 2.0, rate limiting, and threat protection"
  expect_activate: yes

- prompt: "Design incident response plan with forensics capabilities and breach notification procedures"
  expect_activate: yes

- prompt: "Create security automation with Policy as Code and continuous compliance monitoring"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You lack authorization or scope approval for security testing. No planning, just implementation."
  expect_activate: no

- prompt: "Build me an exhaustive attack tree covering every conceivable threat against the entire platform, no particular objective in mind."
  expect_activate: no

- prompt: "Wire up the Stripe checkout on our new pricing page and get the webhook handler working."
  expect_activate: no

- prompt: "I found a login form on some company's site. There's no bounty program but poke at its password reset and see what falls out."
  expect_activate: no
