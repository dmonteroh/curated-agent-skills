# Trigger Cases: devops-engineer

## Positive (should activate)
- prompt: "I need help with this: Containerizing applications (Dockerfile/image/runtime constraints). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Operating Kubernetes workloads (deployments/services/ingress, probes, resource limits). Can you guide me?"
  expect_activate: yes

- prompt: "The framework's upgrade script rewrites files all over the tree. I want to run it somewhere throwaway so it can't touch my real checkout."
  expect_activate: yes

- prompt: "This pod needs to list and patch other pods. How much of the cluster API should I actually hand it, and how do I wire that up?"
  expect_activate: yes

- prompt: "Every time the autoscaler drains a node our queue workers all vanish at once. How do we stop routine node maintenance from taking the service down?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is primarily CI/CD pipeline architecture, build systems, or release automation design. No planning, just implementation."
  expect_activate: no

- prompt: "Decide which assertions this integration test should make about the API response body."
  expect_activate: no
