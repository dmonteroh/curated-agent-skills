# Trigger Cases: mle-workflow

## Positive (should activate)
- prompt: "We have a churn model that works in a notebook. What has to happen before it can actually serve predictions to customers?"
  expect_activate: yes

- prompt: "Our offline numbers looked great and the live results are terrible. Where do I start looking?"
  expect_activate: yes

- prompt: "How should we decide whether the new model version is allowed to replace the one in production?"
  expect_activate: yes

- prompt: "The recommender has been live six months, nobody has checked it, and I don't know whether the features have drifted underneath it."
  expect_activate: yes

- prompt: "We need to be able to put the previous model back within minutes if this one misbehaves. How should that be set up?"
  expect_activate: yes

- prompt: "Someone copied the feature engineering into the serving code months ago and I think the two have quietly diverged."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Given how much labeled data we have, should we do LoRA or a full fine-tune?"
  expect_activate: no

- prompt: "I need to build a clean training set out of these support tickets — dedupe them, get them labeled, and hold a chunk back."
  expect_activate: no

- prompt: "Just get me a quick chart of signups by week for the board deck."
  expect_activate: no

- prompt: "The classifier is really five if-statements on account age and spend. Does it need the same treatment?"
  expect_activate: no

- prompt: "We want to know whether the new instructions make the assistant summarize better. There's no model here, just a prompt file."
  expect_activate: no
