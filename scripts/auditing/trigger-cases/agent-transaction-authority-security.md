# Trigger Cases: agent-transaction-authority-security

## Positive (should activate)
- prompt: "I'm building a bot that lets GPT decide the trades and then actually submits them. What has to be in place before I fund it?"
  expect_activate: yes

- prompt: "Our agent has a wallet and can swap tokens on its own. Review it — I want to know what stops it draining the account."
  expect_activate: yes

- prompt: "Where should the daily spend limit live? Right now it's a line in the system prompt."
  expect_activate: yes

- prompt: "The agent lost four trades in a row last night and just kept going. How should it have stopped itself?"
  expect_activate: yes

- prompt: "We want to give the assistant access to our treasury so it can rebalance. Talk me through how to scope that safely."
  expect_activate: yes

- prompt: "Should the bot dry-run a swap before it sends it, and what does it compare the result against?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The agent just reads market data and writes me a summary. It can't place orders. Any security concerns?"
  expect_activate: no

- prompt: "Our agent scrapes forums and news sites into its context. How do I stop a hostile page from steering it?"
  expect_activate: no

- prompt: "Where should we keep the wallet private key, and how often should it be rotated?"
  expect_activate: no

- prompt: "Do a full security review of the whole platform — threat model, findings with severity, remediation plan."
  expect_activate: no

- prompt: "Is a momentum strategy or mean reversion better for this pair right now?"
  expect_activate: no
