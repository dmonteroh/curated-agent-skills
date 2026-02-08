# Trigger Cases: dotnet-core

## Positive (should activate)
- prompt: "I need help with this: Building or modifying ASP.NET Core services (Minimal APIs or controllers). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Implementing authentication/authorization, DI, configuration, health checks. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The work is in another language/runtime. No planning, just implementation."
  expect_activate: no
