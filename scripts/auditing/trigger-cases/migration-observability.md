# Trigger Cases: migration-observability

## Positive (should activate)
- prompt: "I need help with this: Running a production migration/backfill/cutover that can’t be “fire and forget”. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Dashboards/alerts and objective gates (pause, slow down, rollback, proceed) are required. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The change is a tiny, low-risk schema tweak with trivial rollback. No planning, just implementation."
  expect_activate: no
