# Trigger Cases: devops-engineer

## Positive (should activate)
- prompt: "I need help with this: Containerizing applications (Dockerfile/image/runtime constraints). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Operating Kubernetes workloads (deployments/services/ingress, probes, resource limits). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is primarily CI/CD pipeline architecture, build systems, or release automation design. No planning, just implementation."
  expect_activate: no
