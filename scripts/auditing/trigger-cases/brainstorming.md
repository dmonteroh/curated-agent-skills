# Trigger Cases: brainstorming

## Positive (should activate)
- prompt: "I'm not sure which architecture to choose. Can you help me decide between options?"
  expect_activate: yes

- prompt: "Requirements are still fuzzy. Let's do a quick design brief before coding."
  expect_activate: yes

- prompt: "I want to build something to help my team stop losing track of customer feedback, but I honestly don't know if it should be a tool, a dashboard, or just a better process. Can you ask me what you need to know and help me figure out a direction?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I feel like our internal docs are a mess and I want to fix it, but I don't know whether that means a wiki migration, a cleanup sprint, or a new tool. Help me think it through and end with a short plan."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We need to refresh our small business’s online presence, but I can’t tell whether we need a new website, better social content, or a newsletter. Talk it through with me, challenge my assumptions, and outline a simple plan."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "I’m not sure how to improve my team’s onboarding process—maybe documentation, mentorship, or a more structured first week. Ask clarifying questions, compare those approaches, and propose a short implementation plan."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "got a vague app idea help me figure out what it even is"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "Implement this exact API endpoint now; requirements are final and no design work is needed."
  expect_activate: no

- prompt: "I already know exactly what I want: a Flask API with endpoints /users and /orders backed by Postgres. Please scaffold it in the current directory."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Here's our finalized product spec for the customer feedback tool. Break it into tickets with estimates for the next two sprints."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Ask me a few quick questions to confirm which Python version and OS I'm on so you can fix this install error."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "I know I want to launch a weekly email newsletter for independent designers. Write the first four issues and a publishing calendar."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Please facilitate a retrospective for my team using this agenda and turn the notes into action items."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Help me decide whether to accept this job offer by calculating the salary difference and commute costs."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
