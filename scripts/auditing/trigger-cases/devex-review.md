# Trigger Cases: devex-review

## Positive (should activate)
- prompt: "We launch this public API in two weeks. Will a developer who has never seen it get to a working call without pain?"
  expect_activate: yes

- prompt: "Here's the design doc for our new CLI. Before we build it, I want to know how it will feel to the people who have to use it."
  expect_activate: yes

- prompt: "Before I commit to a ship date I need a concrete, evidence-backed list of the friction a first-time integrator hits with our SDK."
  expect_activate: yes

- prompt: "Our quickstart is where people bounce off. Judge it as the onboarding path it actually is, not as documentation in the abstract."
  expect_activate: yes

- prompt: "Our team is shipping a beta REST API for shipping labels. Please evaluate time-to-first-hello-world for a third-party dev: signup, API key, auth, first request. Give me a score and list the biggest onboarding blockers."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "how easy is our new sdk to get started with for outside devs"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Before we launch the SDK, assess its time-to-first-success for developers who have never seen it. Test installation, configuration, documentation, examples, and error messages, then recommend fixes."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Evaluate the developer experience of adopting our beta API before release, focusing on how intuitive the docs and sample code are and how much friction developers encounter getting started."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "This is an internal batch job with no exposed API and no client library. Review how the end users experience it."
  expect_activate: no

- prompt: "Is this service's architecture sound? Walk the data flow and the failure modes."
  expect_activate: no

- prompt: "I don't have time for you to dig into anything — just give me a quick gut-feel score on our API in the next two minutes."
  expect_activate: no

- prompt: "Write a quickstart guide for our new Python SDK that takes a developer from install to first API call in under five minutes."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Benchmark the latency and throughput of our new API under 1,000 concurrent requests and report p95 numbers."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Run a security review of the new API's authentication flow to see whether an outside developer could misuse the API keys."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Compare the feature sets and pricing of our CLI against competing developer tools."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a migration guide to help existing customers move from version 1 of the SDK to version 2."
  expect_activate: no
  tags: [generated, gen:codex]
