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

## Negative (should not activate)
- prompt: "This is an internal batch job with no exposed API and no client library. Review how the end users experience it."
  expect_activate: no

- prompt: "Is this service's architecture sound? Walk the data flow and the failure modes."
  expect_activate: no

- prompt: "I don't have time for you to dig into anything — just give me a quick gut-feel score on our API in the next two minutes."
  expect_activate: no
