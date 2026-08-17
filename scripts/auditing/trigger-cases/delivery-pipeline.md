# Trigger Cases: delivery-pipeline

## Positive (should activate)
- prompt: "A change request just landed. It reads like a small tweak but it touches the auth middleware — how much process does it actually deserve?"
  expect_activate: yes

- prompt: "I want you to stop and get my sign-off before you write any code, and again before anything gets committed."
  expect_activate: yes

- prompt: "Every fix, feature and refactor here follows a different improvised sequence. I want one phase order that scales up and down."
  expect_activate: yes

- prompt: "Last week you wrote a three-page plan for a typo fix and then edited a public interface with no plan at all. Fix that imbalance."
  expect_activate: yes

- prompt: "Take this spec and carry it all the way from request through to a commit, stopping where I need to weigh in."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Nobody will be around tonight to approve anything — this has to run start to finish unattended."
  expect_activate: no

- prompt: "How do I split this across four agents working at the same time without them overwriting each other's files?"
  expect_activate: no

- prompt: "I just want to read through the code and answer a question. Nothing here gets committed."
  expect_activate: no

- prompt: "Here's a pull request from an outside contributor. Go through it and tell me what's wrong with it."
  expect_activate: no
