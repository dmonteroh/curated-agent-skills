# Trigger Cases: tutorial-engineer

## Positive (should activate)

- prompt: "I'm putting together onboarding material for our team. Write a hands-on tutorial that teaches FastAPI from scratch: hello world first, then path/query params, Pydantic models, dependency injection, and finally auth and a database."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need a walkthrough tutorial for our internal event-bus library (it's in ./src/eventbus). Start with publishing a single event, then subscribers, filtering, retries, and dead-letter queues. Make it something a new hire can follow along with in an afternoon."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write a beginner-to-intermediate tutorial for Tailwind CSS aimed at backend devs who hate CSS. Each section should have code they can type and see the result, building up to a full responsive landing page."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "write a hands on guide to prisma orm starting simple"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Develop a step-by-step tutorial for using Terraform with AWS: start by provisioning one bucket, then add variables, modules, and remote state."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write a progressive tutorial for the Stripe API in Python, starting with authentication and a basic payment, then expanding to webhooks and subscriptions."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write a practical beginner-to-advanced guide that teaches developers how to use React Query, with runnable examples that build on each other."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you explain how Python's asyncio event loop works under the hood? I want a conceptual explanation of the scheduler, not a coding exercise."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Review my FastAPI app in ./app and tell me what's wrong with how I'm using dependency injection and Pydantic models."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a quick-start section of at most five lines showing how to install and import the eventbus library, for the top of the README."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Compare PostgreSQL, MySQL, and SQLite for a new SaaS product, including a recommendation for different deployment sizes."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Debug this error in my Next.js application and explain the smallest code change needed to fix it."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a one-page cheat sheet of common Git commands for experienced developers."
  expect_activate: no
  tags: [generated, gen:codex]
