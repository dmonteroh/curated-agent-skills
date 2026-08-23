# Trigger Cases: brand-discovery

## Positive (should activate)
- prompt: "We're rebranding the studio and I want to properly work out what we stand for. It'll take a few sessions, not one call."
  expect_activate: yes

- prompt: "Can you interview me and my co-founder separately about the company's identity and then show us where we actually disagree?"
  expect_activate: yes

- prompt: "Everything about our brand lives in my head. I need a written thing I can hand a designer and a copywriter so they stop asking me what we're like."
  expect_activate: yes

- prompt: "We started the brand doc last week and got as far as who we're for. Where did we leave off?"
  expect_activate: yes

- prompt: "Take me through a proper brand discovery — purpose, audience, personality, the lot — one question at a time, and save it as we go."
  expect_activate: yes

- prompt: "Our voice is inconsistent because nobody ever wrote down what the brand is. Can we fix that at the root?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Interview me about how I use our internal expense tool day to day and where it slows me down."
  expect_activate: no

- prompt: "Pick fonts and colours for the landing page. It just needs to look decent by Friday."
  expect_activate: no

- prompt: "The brand guidelines were signed off in March. Use them to write the About page."
  expect_activate: no

- prompt: "Quick gut check — is 'Northbeam' a decent name for a coffee roaster? Two lines is fine."
  expect_activate: no

- prompt: "Who are our three biggest competitors and what are they charging?"
  expect_activate: no
