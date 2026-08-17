# Trigger Cases: prompt-injection-defense

## Positive (should activate)
- prompt: "Our agent browses the open web and also has shell access on the same box. I need to think hard about what an attacker can do with that combination."
  expect_activate: yes

- prompt: "Which of this agent's tools can carry attacker-controlled text into its context? I want the ingress paths enumerated."
  expect_activate: yes

- prompt: "Should the detector hard-block the request or just flag it, and is one classifier ever allowed to make that call alone?"
  expect_activate: yes

- prompt: "The agent writes plans and notes to disk that later sessions load straight into their prompts. Is that a hole?"
  expect_activate: yes

- prompt: "How do I actually evaluate whether our defenses work, rather than assuming they do because nothing has gone wrong yet?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Our agent reads untrusted pages but has no tools and can't change anything, and that setup is fixed."
  expect_activate: no

- prompt: "Everything the agent sees this session comes from me directly and nothing is written down for next time."
  expect_activate: no

- prompt: "We need to fix the auth on this endpoint and clear a couple of dependency CVEs before the audit."
  expect_activate: no

- prompt: "Sign off that our agent can't be hijacked by text it reads off the web."
  expect_activate: no

- prompt: "Pick a good confidence threshold for the detector. We only have normal traffic to tune against, no attack samples."
  expect_activate: no
