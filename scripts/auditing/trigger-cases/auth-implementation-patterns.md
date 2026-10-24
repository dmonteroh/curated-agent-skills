# Trigger Cases: auth-implementation-patterns

## Positive (should activate)

- prompt: "Can you review our Express auth middleware? We issue JWTs on login and I'm worried about how we handle refresh token rotation and expiry."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Implement session-based login for our Django app with secure cookies, CSRF protection, logout that invalidates the session server-side, and a permission check so only team owners can delete projects."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We're adding OIDC single sign-on with Okta for enterprise customers. Can you wire up the authorization code flow with PKCE and map Okta groups to our internal roles?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Audit our session handling and make sure expired tokens cannot still access protected pages."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Add role-based permissions so admins can manage users while regular members can only view their own projects."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Build the access-control middleware for our API, including per-route permission checks."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "jwt refresh keeps failing check my auth"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)

- prompt: "Can you write a database migration that adds a last_login_at column and backfills it from the activity log table?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me design a signup page UI with a nice form layout, responsive styling and a hero image using Tailwind."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you help me SSH into the production server with a key pair and configure the sshd settings so password login is disabled?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a Python function that hashes and verifies file checksums with SHA-256 so we can detect corrupted downloads."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up email notifications that welcome new users after they create an account."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create an analytics dashboard showing daily active users and conversion from signup to purchase."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Integrate a payment provider so customers can subscribe and manage billing."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
