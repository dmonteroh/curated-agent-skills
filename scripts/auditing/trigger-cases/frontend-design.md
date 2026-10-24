# Trigger Cases: frontend-design

## Positive (should activate)
- prompt: "Our dashboard has a fixed sidebar and header, but the whole window scrolls instead of just the content pane. Can you rebuild the shell so scrolling lands in the right place?"
  expect_activate: yes

- prompt: "The settings screen looked great with placeholder text. With real customer data the names wrap into three lines and one long URL blows the column out. Make it hold up."
  expect_activate: yes

- prompt: "The play icons in our toolbar look a hair off-centre, and the panel swap animation snaps if you click fast. Tighten the polish pass."
  expect_activate: yes

- prompt: "I'm giving a conference talk in two weeks. Build me the slides as a single HTML file I can run from my laptop, with keyboard navigation."
  expect_activate: yes

- prompt: "My web deck looks fine on the big monitor but on the projector half the slides get a scrollbar and the last bullet is cut off. Fix it."
  expect_activate: yes

- prompt: "Can you build me a landing page for my indie coffee roastery? I want a hero section with a big image, a product grid, and a newsletter signup. Make it feel warm and premium, and use plain HTML/CSS with a little JS."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Design and code a login/signup card component in Svelte with floating labels, a password strength meter, and subtle transitions. I want it to look modern and ready to drop into my app."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Implement a sleek ecommerce product-detail page in Next.js with an image gallery, variant selectors, sticky purchase panel, and mobile styling."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Create a production-ready dashboard interface in HTML and CSS for a project-management app, including sidebar navigation, KPI cards, charts, and a responsive layout."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "build a sleek todo app ui in react"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "Turn my notes into a .pptx I can email to the exec team — it has to open in PowerPoint on their machines."
  expect_activate: no

- prompt: "Write a Python script that scrapes product prices from an e-commerce site and saves them to a CSV file."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you review my Express API routes and tell me where the authentication middleware could be bypassed?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Create a Figma-style design brief and color palette recommendation for a fintech brand. No code needed, just the written guidelines."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you write the copy for my landing page: headline, subheadings, and feature descriptions for a budgeting app? I'll have someone else build it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Review our existing website for accessibility problems and provide a prioritized report without changing the UI."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Make a clickable prototype in Figma for an onboarding flow."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
