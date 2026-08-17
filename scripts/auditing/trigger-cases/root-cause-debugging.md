# Trigger Cases: root-cause-debugging

## Positive (should activate)
- prompt: "The refinement endpoint returns 200 with an empty body. Nothing in the logs, no exception anywhere. Can you work out what's actually happening?"
  expect_activate: yes

- prompt: "I've tried three fixes for this hang and none of them stuck — it just moves somewhere else. Find the real cause instead of patching symptoms."
  expect_activate: yes

- prompt: "The worker marks the job complete but the file never lands in the bucket, and nothing throws. Figure out why and put a test around it so it can't come back."
  expect_activate: yes

- prompt: "Users say their saved settings revert after a reload. I can't reproduce it from the API but they can from the app. Dig in and prove what's causing it."
  expect_activate: yes

- prompt: "Something between the config loader and the HTTP client is dropping our base-URL override. I can't tell which side owns it. Track it down."
  expect_activate: yes

- prompt: "This crashes about one run in five with a different stack trace each time. Same input. What's going on?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The build fails with 'Argument of type string is not assignable to parameter of type number' at src/cart.ts:42. Fix it."
  expect_activate: no

- prompt: "Checkout p95 went from 120ms to 900ms after last week's release. Find where the time is going and get it back down."
  expect_activate: no

- prompt: "Three different tests fail on every CI run and they all pass locally when I run them one at a time. Sort the suite out."
  expect_activate: no

- prompt: "Walk me through how the retry middleware works — I need to understand the flow before I touch anything."
  expect_activate: no

- prompt: "Here's my finished vendor-data extraction. Give it a hard skeptical review before I send it to the client."
  expect_activate: no
