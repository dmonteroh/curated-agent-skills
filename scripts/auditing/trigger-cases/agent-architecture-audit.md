# Trigger Cases: agent-architecture-audit

## Positive (should activate)
- prompt: "The assistant used to answer these correctly and now it doesn't. Same model, same prompts. I have no idea which part of our stack broke it."
  expect_activate: yes

- prompt: "It works perfectly when I hit the provider API directly and falls apart inside our wrapper. Where do I even start looking?"
  expect_activate: yes

- prompt: "The system prompt says it must call the lookup tool before answering and about half the time it just answers anyway."
  expect_activate: yes

- prompt: "Our logs contain the right answer and users are seeing mangled output. Something between generation and the screen is chewing it up."
  expect_activate: yes

- prompt: "We added a memory layer three weeks ago and now it drags in unrelated old conversations, and when users correct it the correction doesn't stick."
  expect_activate: yes

- prompt: "Two of our agents run on the same model with nearly the same prompt and behave completely differently. Can you work out why?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "I want an agent that runs every night and fixes whatever tests are failing. How do I stop it going off the rails?"
  expect_activate: no

- prompt: "Run the eval prompts with and without the guidance file loaded and tell me whether it actually changed the output."
  expect_activate: no

- prompt: "This one request blew up with a timeout from the provider. What happened on that call?"
  expect_activate: no

- prompt: "We already know where it is — the notes store keeps accepting things the agent read off a web page. How should the write rules work?"
  expect_activate: no

- prompt: "Add an architecture audit step to the release checklist so it runs on every deploy."
  expect_activate: no
