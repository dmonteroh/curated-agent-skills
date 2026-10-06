# Trigger Cases: database-migration-orm

## Positive (should activate)

- prompt: "We have a Prisma project with about 40M rows in the orders table. I need to rename the column `total` to `total_cents` and change it from decimal to integer, without downtime. Can you write the migration files so the old app version keeps working during deploy?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Using Entity Framework Core, I need to split the `Customer.FullName` column into `FirstName` and `LastName`. Production traffic can't be interrupted. Walk me through the expand/contract migrations and write them."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I want to drop the legacy `users.phone_old` column from our Prisma schema. The app is live and I'm not sure if the running code still reads it. How do I stage the migrations safely so nothing breaks during rollout?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "add nullable column to prisma without downtime"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Using TypeORM migrations, split the change from `orders.total` integer to decimal into safe expand/backfill/contract migrations so production stays available throughout."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write Sequelize migration files to rename `customers.phone` to `phone_number` with a no-downtime rollout that supports both application versions during deployment."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Add a non-null `organization_id` foreign key to the existing `projects` table through Entity Framework migrations, using a safe staged approach for a live database."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you seed the dev database with 200 fake users and some orders using a Prisma seed script?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me optimize this slow TypeORM query that joins orders, items and customers. It takes 8 seconds."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Design a new database schema from scratch for a booking app, as an ER diagram with tables and relationships. No ORM code yet."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Our Django app needs a new column on the profile table. Write the raw SQL ALTER statement I can run manually in psql, no migration framework."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Upgrade our Prisma version and regenerate the client, but do not create or apply any migrations."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Refactor the TypeORM entity classes to use clearer property names while leaving the existing database tables and columns untouched."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Add a `status` column directly in the production database with a manual SQL command; we are not using ORM migration files for this change."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
