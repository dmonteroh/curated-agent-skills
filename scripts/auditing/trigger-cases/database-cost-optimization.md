# Trigger Cases: database-cost-optimization

## Positive (should activate)

- prompt: "Our AWS RDS bill jumped to $14k/month. Can you go through our Terraform in infra/databases/ and the CloudWatch metrics exports in ./metrics to find oversized instances and read replicas nobody is querying, and give me a rollback step for each change you propose?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review our Aurora clusters for cost savings: idle replicas, over-provisioned IOPS, old manual snapshots piling up, gp2 volumes that could be gp3. For each, tell me exactly how to undo it if something breaks."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Can you analyze the MongoDB Atlas cluster configs in this repo and the usage CSV I dropped in ./reports, then identify clusters that are too big, unused secondary nodes, and wasted storage? I want a savings estimate plus an undo procedure per item."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "cut rds costs find idle replicas"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Audit our managed database fleet for oversized instances, idle read replicas, and excess storage, then recommend cost reductions with a tested rollback plan for every change."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Create and execute a conservative database cost-optimization plan. Validate utilization before downsizing or deleting anything, and include backups and rollback steps."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Review production database spend and safely rightsize instances, remove truly unused replicas, and reclaim wasted storage; document how to undo each action."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Our Postgres queries on the orders table are slow. Can you look at the EXPLAIN output and suggest indexes to speed things up?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me reduce our Kubernetes compute costs by right-sizing node pools and the pod resource requests in our deployments."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Delete all rows older than 90 days from the events table to shrink it, and write the SQL for it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Our S3 bucket costs are too high. Find old objects and set up lifecycle rules to move them to Glacier, with a way to restore them."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up automated backups and disaster-recovery replication for all of our databases."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Migrate our self-hosted PostgreSQL clusters to a managed database service with minimal downtime."
  expect_activate: no
  tags: [generated, gen:codex]
