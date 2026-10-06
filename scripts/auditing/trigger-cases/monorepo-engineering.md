# Trigger Cases: monorepo-engineering

## Positive (should activate)

- prompt: "We have about 40 TypeScript packages in one repo and CI takes 35 minutes because everything rebuilds on every PR. Can you set up the monorepo with pnpm workspaces and Turborepo so only affected packages build, and add caching?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our monorepo has turned into a mess: packages import each other's internals and there are circular deps between auth, billing and core. Help me restructure it with clear boundaries and enforce allowed dependency directions."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I'm consolidating 12 separate Python services and 5 shared libraries into one repo. Propose a layout, tooling (uv workspaces or Bazel/Pants), and CODEOWNERS so each team owns its area without blocking the others."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Set up Nx in this repo with module boundary rules, tags per team (web, platform, data), and affected-only test/lint targets in GitHub Actions."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review our workspace layout under packages/ and apps/. We have 60+ packages with version drift on shared dependencies. Reorganize them, hoist common deps, and set up internal package versioning so teams can release independently."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "monorepo builds too slow set up turborepo caching"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)

- prompt: "Write a GitHub Actions workflow that builds and publishes a single npm package to the registry when I push a version tag."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Upgrade React from 17 to 18 in this app and fix the breaking changes in the components."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Explain the difference between semantic versioning ranges ^ and ~ in package.json and when to pin exact versions."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me organize the folders inside my single Express app: controllers, services, models, and utils. It's one package, not a workspace."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Our Docker image for one service is slow to build. Can you optimize the Dockerfile layers and caching?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Resolve this merge conflict in package-lock.json between my branch and main."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]
