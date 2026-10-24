# Trigger Cases: load-and-capacity-planning

## Positive (should activate)
- prompt: "Marketing expects double our normal traffic on launch day. How do we prove the checkout service can take it before then?"
  expect_activate: yes

- prompt: "We have no idea at what request rate this API starts falling over. Can you design a test that finds the breaking point?"
  expect_activate: yes

- prompt: "Our Postgres disk grows about 40 GB a month. When does it fill up, and when should we add capacity?"
  expect_activate: yes

- prompt: "How many pods do we need to serve 3,000 requests per second with one node allowed to fail, and where should the HPA trigger sit?"
  expect_activate: yes

- prompt: "Write a k6 script that ramps to peak load, holds it, and fails the run if p95 goes over 500ms."
  expect_activate: yes

- prompt: "Does our service leak memory under sustained traffic? I want an overnight soak test and a way to read the result."
  expect_activate: yes

- prompt: "load test the search api before black friday"
  expect_activate: yes
  tags: [off-register]

## Negative (should not activate)
- prompt: "Add structured logging and alerts to this API so we find out when it breaks."
  expect_activate: no

- prompt: "Checkout p95 crept from 200ms to 900ms over the past month. Profile it and tell me where the time goes."
  expect_activate: no
  tags: [near-miss]

- prompt: "Our cloud bill doubled. Which services should we rightsize or move to cheaper tiers?"
  expect_activate: no
  tags: [near-miss]

- prompt: "Benchmark these two JSON parsing functions and tell me which is faster."
  expect_activate: no
  tags: [near-miss]

- prompt: "Write a postmortem for last Tuesday's outage from the timeline I pasted."
  expect_activate: no

- prompt: "Migrate our CI pipeline from Jenkins to GitHub Actions."
  expect_activate: no

- prompt: "Explain how Kubernetes horizontal pod autoscaling works conceptually for a training deck."
  expect_activate: no
