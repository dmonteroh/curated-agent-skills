# Trigger Cases: brand-voice

## Positive (should activate)
- prompt: "Here are twelve of my posts and two essays. Work out how I actually write so drafts stop sounding like a press release."
  expect_activate: yes

- prompt: "Can you build a reusable style reference from our founder's newsletter that the whole team can write against?"
  expect_activate: yes

- prompt: "I want everything we publish to sound like the same person. Start from what we've already shipped."
  expect_activate: yes

- prompt: "Read the old customer emails that actually got replies and tell me what my voice is, in something I can paste into later chats."
  expect_activate: yes

- prompt: "Our docs and my personal posts read like two different companies. Work out which is which before we write anything new."
  expect_activate: yes

- prompt: "Before we draft the launch thread, pin down my writing style from my last twenty posts."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Clean this draft up, it reads like a chatbot wrote it."
  expect_activate: no

- prompt: "You already figured out how I write earlier in this chat. Just write the LinkedIn post."
  expect_activate: no

- prompt: "I haven't written anything yet — just invent a voice for us that sounds smart and technical."
  expect_activate: no

- prompt: "Write me five tweets announcing the new pricing."
  expect_activate: no

- prompt: "Which of these two taglines tests better with enterprise buyers?"
  expect_activate: no
