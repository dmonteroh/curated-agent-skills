# Trigger Cases: mermaid-expert

## Positive (should activate)

- prompt: "Can you draw a Mermaid sequence diagram showing how a user logs in with OAuth2 through our web app, the auth server, and the resource API? I want to paste it into our README."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please create an entity relationship diagram in Mermaid for a blog database with users, posts, comments, and tags, including cardinalities and primary/foreign keys."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Make a Mermaid flowchart of the CI/CD pipeline described in .github/workflows/deploy.yml so I can embed it in the docs markdown."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "mermaid flowchart for password reset flow"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Create a Mermaid flowchart for our customer-support ticket triage process that I can paste into a Markdown README."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write a Mermaid ER diagram for an online store with customers, orders, products, and order items."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Please turn this deployment workflow into a Mermaid flowchart that renders in GitHub Markdown."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you write a PNG-rendering script using Graphviz that exports our service dependency graph to an image file?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a SQL schema (CREATE TABLE statements) for a blog with users, posts, comments, and tags."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Explain in plain prose how OAuth2 authorization code flow works, no diagrams needed."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Create a Gantt chart or project timeline in a spreadsheet for our Q4 launch plan."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Describe what the arrows in a UML sequence diagram mean, like solid versus dashed lines, I'm studying for an exam."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Make a Lucidchart diagram of our incident-escalation workflow."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Build an interactive React component that visualizes the order-processing pipeline."
  expect_activate: no
  tags: [generated, gen:codex]
