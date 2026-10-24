# Trigger Cases: agent-feedback-ui

## Positive (should activate)
- prompt: "You generated eight candidate chart layouts. I want to score each one and leave a short note before you carry on."
  expect_activate: yes

- prompt: "These four rendered mockups can't be judged from a text description — I need them side by side at full size so I can pick one."
  expect_activate: yes

- prompt: "For each of these ten generated headlines give me a 1-5 rating field and a comment box, then take the whole set back at once."
  expect_activate: yes

- prompt: "If I dislike every candidate I want to reject the batch and get a fresh set, without you asking me about them one at a time in chat."
  expect_activate: yes

- prompt: "I generated 12 logo variants in ./logos/. Can you spin up a little local web page that shows them all, lets me give each a 1-5 star rating and type a comment, and then read my ratings back as JSON when I hit submit?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need to compare two UI mockups, v1.png and v2.png. Launch a simple webpage with both shown next to each other, a preference toggle, and a text box for why. After I submit, tell me what I chose, using the data it collects."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Open a local webpage where I can compare each pair of logo options side by side, pick a winner, explain why, and send the results back to the agent."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Build a simple local review UI for these generated answers: I need to mark each as approve/reject, optionally edit a comment, and have you read my decisions afterward."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "open a browser form for rating these images and read my notes back"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

## Negative (should not activate)
- prompt: "Just ask me straight: do I want option A or option B? One word answer."
  expect_activate: no

- prompt: "Interview me about what I want out of this dashboard, following up based on whatever I say."
  expect_activate: no

- prompt: "My ratings are already sitting in results.json from the last round — read those and continue."
  expect_activate: no

- prompt: "Build me a production React feedback widget with star ratings that I can embed on my public website and store in Postgres."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you rank these three logo ideas yourself and explain which one is best? Just give me your opinion in the chat, no need to build anything."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a Google Forms-style survey questionnaire with 10 questions to send to our customers by email, and give me the text of the questions."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Make a public web app where customers can rate our new feature and submit feedback over the next month."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Use an automated model to score these responses for correctness and export the scores without asking a human to review them."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Open a browser preview of these images and let me navigate with next/previous buttons; I only need to inspect them, not record judgments."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
