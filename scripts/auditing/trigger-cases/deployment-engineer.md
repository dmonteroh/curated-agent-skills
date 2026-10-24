# Trigger Cases: deployment-engineer

## Positive (should activate)
- prompt: "Our release sat waiting nine hours last night: the approver was on holiday and the canary metric never reported either way. What should a gate do when its signal just never arrives?"
  expect_activate: yes

- prompt: "We're dropping a column next release. How do I stage that so we can still roll the app back if the deploy goes bad?"
  expect_activate: yes

- prompt: "Our pipeline minifies and repacks the bundle after the tests pass. The upload succeeded and the artifact loads fine, but the page came up blank in prod. How do we gate that step so it can't happen again?"
  expect_activate: yes

- prompt: "We compress the model before it goes to the inference server, so the output is never byte-identical to what we tested. What is the release supposed to compare?"
  expect_activate: yes

- prompt: "I need CI/CD for our Go microservice on Kubernetes. Please create the pipeline that builds the image, runs unit and integration tests, deploys to staging, then does a canary release to prod with automatic rollback on failed health checks."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our team ships a Next.js web app to Vercel/AWS and deploys are a mess. Can you build an automated pipeline with tests gating the build, progressive traffic shifting for new releases, and a quick revert button or script if something breaks?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "need pipeline build test deploy canary and easy rollback"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Configure GitHub Actions and deployment tooling so every release is built and tested automatically, rolls out to a small percentage of users first, and can be reverted quickly."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Should we serve these images as WebP or AVIF, and what quality setting gets us under 200KB?"
  expect_activate: no

- prompt: "Help me decide whether this should be one table or three, and which columns need indexes."
  expect_activate: no

- prompt: "Write unit tests for the payment module in src/billing so we reach 80% coverage."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write the App Store listing copy and screenshots plan for our v2.0 launch."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Our last release broke login in production. Can you do a postmortem of what went wrong and write up the incident timeline?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up infrastructure monitoring, alerting, and dashboards for our production application."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Migrate the app’s build system from Webpack to Vite and reduce build times."
  expect_activate: no
  tags: [generated, gen:codex]
