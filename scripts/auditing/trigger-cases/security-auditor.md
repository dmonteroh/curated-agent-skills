# Trigger Cases: security-auditor

## Positive (should activate)
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

- prompt: "threat model our api and find vulns"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Snyk and Semgrep dumped 140 findings on our Django monolith. Triage them: figure out which are real, which are false alarms, and build a threat model so we know what actually matters. Then plan the fixes."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review the security of our Kubernetes-hosted API before launch. Identify realistic attack paths, investigate weaknesses, separate exploitable issues from harmless configurations, and propose fixes."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Assess our internal admin system for security risks. I need a threat model, verified vulnerability findings with evidence, and recommended fixes ranked by severity and effort."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Build me an exhaustive attack tree covering every conceivable threat against the entire platform, no particular objective in mind."
  expect_activate: no

- prompt: "Wire up the Stripe checkout on our new pricing page and get the webhook handler working."
  expect_activate: no

- prompt: "I found a login form on some company's site. There's no bounty program but poke at its password reset and see what falls out."
  expect_activate: no

- prompt: "Fix the failing login test in auth_test.py. The token expiry assertion is off by one hour because of timezone handling."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Set up a GitHub Actions workflow that runs our unit tests and builds the Docker image on every pull request."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Refactor the user service to use dependency injection and add type hints throughout, without changing behavior."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Explain what a threat model is and how STRIDE differs from PASTA. I'm preparing a training slide and don't need any analysis of my code."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you run a vulnerability scanner against our web app and send me the raw results?"
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
