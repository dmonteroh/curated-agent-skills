# Trigger Cases: cost-optimization

## Positive (should activate)

- prompt: "aws bill too high help cut it"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Our AWS bill jumped to $84k last month and finance is asking questions. Can you go through our Cost Explorer export in ./billing and tell me where we're wasting money, which instances are oversized, and whether Savings Plans make sense?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need a FinOps plan for our GCP org: identify idle VMs and unattached disks, rightsize the GKE node pools, recommend committed use discounts, and set up labels so we can chargeback costs to each engineering team."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Set up a FinOps program: tag costs to teams, allocate shared services, identify waste, and recommend reserved instances or savings plans."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Reduce our monthly cloud bill without impacting production. Find underutilized compute, oversized databases, orphaned storage, and the best discount commitments to purchase."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Review our cloud invoices and usage data, rightsize workloads, and build dashboards showing each engineering team’s monthly spend and savings."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Our SaaS subscription costs are out of hand. Help me audit the Slack, Notion, and Zoom licenses and find unused seats."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a Python script to parse our invoice PDFs from the cloud vendor and load the totals into the accounting spreadsheet for bookkeeping."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up a CI/CD pipeline in GitHub Actions that builds our Docker image and deploys it to EKS on every merge to main."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Build a dashboard that shows application uptime, latency, and error rates by team."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Migrate our production workloads from AWS to Google Cloud with minimal downtime."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Design a disaster-recovery strategy for our cloud services, including backups, failover, and recovery-time targets."
  expect_activate: no
  tags: [generated, gen:codex]
