# Trigger Cases: devops-engineer

## Positive (should activate)
- prompt: "The framework's upgrade script rewrites files all over the tree. I want to run it somewhere throwaway so it can't touch my real checkout."
  expect_activate: yes

- prompt: "This pod needs to list and patch other pods. How much of the cluster API should I actually hand it, and how do I wire that up?"
  expect_activate: yes

- prompt: "Every time the autoscaler drains a node our queue workers all vanish at once. How do we stop routine node maintenance from taking the service down?"
  expect_activate: yes

- prompt: "One of our containers keeps ending up in CrashLoopBackOff with OOMKilled. Here's the deployment YAML. Please figure out the right memory limits and add liveness and readiness probes so it recovers cleanly."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I'm on call for the payments platform starting Monday. Can you help me write a runbook and a readiness checklist covering alerting, dashboards, rollback steps, and escalation paths for our k8s workloads?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "nodes notready again whats wrong"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Review the production Kubernetes clusters for unhealthy pods, restart loops, node pressure, and capacity risks, then remediate anything that threatens availability."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Set up a daily operational readiness check for our container platform, including node health, resource headroom, failed deployments, and alert coverage."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Decide which assertions this integration test should make about the API response body."
  expect_activate: no

- prompt: "Write a GitHub Actions workflow that builds our Go service, runs unit tests, and pushes the image to ECR on every merge to main."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review my React component for accessibility problems and suggest how to refactor it to use hooks."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Explain the difference between a Kubernetes Deployment and a StatefulSet. I'm studying for the CKA exam and want a conceptual overview."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Implement a CI/CD pipeline that builds container images, runs tests, and deploys them automatically."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Design a new microservices architecture for our application and recommend how to split the monolith."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Reduce our cloud bill by identifying unused storage volumes, stale snapshots, and oversized databases."
  expect_activate: no
  tags: [generated, gen:codex]
