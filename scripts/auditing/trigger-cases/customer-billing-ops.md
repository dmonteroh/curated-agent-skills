# Trigger Cases: customer-billing-ops

## Positive (should activate)
- prompt: "A customer emailed saying we charged her twice for the same plan this month and she wants it refunded. Can you work out what actually happened on her account and what we should do?"
  expect_activate: yes

- prompt: "This user says there is no way to cancel anywhere in the product and they are threatening a chargeback. Sort out their subscription and tell me what to send back."
  expect_activate: yes

- prompt: "Pull up billing for accounts@northwind.example — they show two active subscriptions and I have no idea whether that is deliberate."
  expect_activate: yes

- prompt: "An annual renewal failed last week and the customer says nobody told them. What state is the account in and what do we send?"
  expect_activate: yes

- prompt: "Someone on our Pro plan bought three separate subscriptions one at a time instead of adding seats. Should we refund two of them?"
  expect_activate: yes

- prompt: "Customer wants their money back for last month because our export feature was down the whole time they paid for it. Walk me through what to do."
  expect_activate: yes

## Negative (should not activate)
- prompt: "I need to build the subscription service — design the dunning retry schedule, the proration maths, and the webhook handlers for payment events."
  expect_activate: no

- prompt: "Checkout has been failing for everyone for the last forty minutes and roughly two hundred customers are affected. What now?"
  expect_activate: no

- prompt: "A user filed a deletion request and we still hold seven years of their invoices for the tax authority. What are we allowed to erase?"
  expect_activate: no

- prompt: "We're thinking of dropping the three-tier plan structure and moving to usage-based pricing next quarter. Talk me through it."
  expect_activate: no

- prompt: "Give me last quarter's revenue split by plan and tell me which tier is churning fastest."
  expect_activate: no
