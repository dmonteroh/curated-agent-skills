---
name: customer-billing-ops
description: "Resolves one named customer's billing problem: fixes identity to a single account, classifies the case into one of five buckets against stated observables, acts in reversibility order so money moves last, and hands off a fixed record naming the product gap behind the ticket. Use for live customer billing operations — duplicate charges, failed renewals, refund requests, cancellations with no self-serve path."
metadata:
  category: business-operations
---

# Customer billing operations

The procedure exists because the fast answer to a billing complaint — refund it — is often the wrong one, and is always the least reversible one.

## Use this skill when

- A customer reports that billing is broken, asks for a refund, disputes a charge, or says they cannot cancel.
- A specific account shows duplicate subscriptions, an accidental charge, a failed renewal, or a payment stuck part-way through.
- A support complaint has to be resolved against one account's actual subscription, invoice, or payment-method state.
- A customer's plan, seat count, or annual-versus-monthly arrangement has to be established before anyone answers them.

## Do not use this skill when

- The task is to **build** billing rather than operate it — invoicing, dunning schedules, proration arithmetic, webhook handling, or integrating a payment provider. That is backend implementation and service-contract design, and none of the decisions below apply to it.
- The question is **pricing or packaging strategy**, or revenue analysis across the customer base. This procedure acts on one customer's billing state and produces no cross-customer view.
- The request is a **data-subject erasure or retention question** that happens to touch billing records. That is a privacy-retention job answered by a retention rule with a stated legal basis; its hard case — an erasure request against invoices a tax authority requires the company to keep — is not a billing action at all and is not decided here.
- The same symptom is **affecting many customers at once**. That is an incident, not a billing ticket. Per-customer remediation happens after the incident is contained, not instead of containing it.

## Required inputs

- At least one identifier for the customer, and a way to reach the billing provider's own records for that identifier.
- The customer's own account of what they were trying to do, kept separate from the billing record — their account is a claim, the record is evidence.
- The organization's own limits on who may issue refunds, credits, and cancellations. Where those limits are stricter than the boundary below, they win; nothing here grants authority the organization has not.

The billing provider's records are the primary source. Email threads, issue trackers, and support tickets are supporting evidence — they establish intent, never state.

## Autonomy boundary

*This whole section is authored, not sourced. The source says "do not refund blindly" but never states whether the agent may issue the refund at all once the case is classified. Absent a stated rule, the ambiguity resolves toward acting, which is the wrong direction for an irreversible money operation.*

May be done without a human:

- Reading and summarizing billing state, and stating the classification with the observable that selected it.
- Restoring the customer's own reach — sending the self-serve portal or cancellation link, or re-enabling access the account is already entitled to.
- Drafting the customer follow-up, the handoff record, and the product-gap item.

Requires a named human to approve before it happens:

- Any refund, credit, discount, or write-off, of any size.
- Cancelling, downgrading, or changing the seat count of a subscription the customer has not explicitly asked to have changed.
- Changing a payment method on the customer's behalf.
- Any action at all where two buckets matched and their licensed actions conflicted, or where identity could not be pinned to one account.

The product of this procedure is a classified case with a prepared action and a drafted message — not an executed money movement. An agent that issues the refund itself has removed the one review step that catches a misclassification, and a misclassified refund is not recoverable by the same route it was issued.

## Constraints

- Never emit secret or API keys, full card numbers, or customer personal data beyond what the recipient of the handoff needs to act. The handoff goes to a colleague, not to an auditor.
- For annual plans, team plans, and anything mid-proration, establish the contract shape before acting. A refund computed against the wrong cycle shape is a second error on top of the first.

## Workflow

### Step 1 — Resolve to exactly one account

Start from the strongest identifier available and work down only as far as needed: billing-provider customer ID, then subscription ID, then invoice ID, then billing email, then a support identifier the organization maps back to billing. Stop at the first one that resolves.

Output: an identity summary carrying active subscriptions, cancelled subscriptions, invoices, and any anomaly — above all, more than one active subscription against the same payer.

If two identifiers resolve to two different accounts, or none resolves to one, stop here. Nothing below is safe on an unresolved identity, and no classification is assertable against it.

### Step 2 — Classify against a stated observable

Classify before any state change, never after, and aim for exactly one bucket — where two genuinely hold, the rule further down decides what follows. The selecting observable is what must be true **in the billing record**, never what the customer said happened: that is the input to the ticket, not evidence for it.

| Bucket | Selecting observable | Licensed action |
|---|---|---|
| Accidental duplicate purchase | Two or more active subscriptions on the same payer for the same or an overlapping plan, sharing one payment method and one billing contact, each at a seat quantity of one. | Cancel the extras; refund only the duplicated charge. |
| Deliberate multi-seat or team purchase | Any one of: the subscriptions differ in seat quantity; they carry different billing contacts; at least one is an explicit organization, team, or seat-based plan. | Preserve every seat; explain the billing model; offer consolidation, never impose it. |
| Failed or incomplete payment | A subscription sitting in a past-due, unpaid, or incomplete state with no successful invoice against it — or whose most recent invoice failed and was never recovered. | Restore a payment path the customer can drive themselves; recover or void the failed cycle. |
| Missing self-serve control | Billing state is internally consistent, and what the customer is trying to do — cancel, downgrade, change payment method, retrieve an invoice — has no path they can reach without a human. | Return the control: portal access, cancellation path, invoice access. |
| Product failure or trust break | Billing state is consistent and the control existed, and the charge covers a period in which the product did not deliver what was paid for, or the customer never authorized the charge at all. | Refund the specific affected charge, acknowledge the failure, and log it. |

*The five selecting observables are authored, not sourced.* The source named these five buckets and their consequent actions but supplied no test that chooses between them; the observables above are inferred from its own worked cases and are this skill's own rule. Treat them as a starting calibration for a given billing model, not as a fixed standard — but fix them before classifying, not while classifying.

The licensed action is what the classification permits, not what may be executed unsupervised; the autonomy boundary above still gates every one of them.

**When two buckets both match.** They can, and the pairs behave differently:

- Where the licensed actions do not conflict, run both. A customer with a failed payment and no reachable portal is both the third bucket and the fourth, and fixing the payment state and returning the control are one repair seen from two sides.
- Where they conflict, the conflict is always about whether money moves or a subscription ends. Run only the reversible part, hold the rest, and put the choice to the customer or to a human.
- Named default, authored: when the duplicate observable and the team observable both hold, treat it as a team purchase. Cancelling seats a team actually bought is not something the customer can undo from their side; leaving a duplicate standing for one more exchange is.

### Step 3 — Act in reversibility order, and stop when the problem is solved

Work down this list, never up it. Each rung is harder to undo than the one above, and most cases are resolved before the money rung is reached.

1. Restore the customer's own self-serve control.
2. Correct the broken billing state — cancel the extra subscription, recover or void the failed cycle, fix the seat count.
3. Refund only the specific affected charge, never the relationship.
4. Record the classification, the observable that selected it, and why this action follows from it.
5. Send the customer follow-up.

Skipping ahead to the money closes the ticket without returning the customer's ability to fix the same thing tomorrow, and without ever establishing why they could not fix it themselves.

### Step 4 — Name the product gap as a separate item

Customer remediation and root cause are two outputs, not one. A resolved ticket is not a fixed product, and closing the ticket is exactly the moment the gap stops being visible.

Gaps that produce these tickets: no self-serve billing portal; no usage or rate-limit visibility; no explanation of plans and seats at the point of purchase; no cancellation path; no guard against a second identical purchase.

Where the missing surface is a control the billing provider already offers as a hosted feature, name that as the fix rather than a custom build — a hosted portal ships sooner than an account-management screen and cannot drift out of sync with the provider's own state.

*Authored gate, not sourced:* the product-gap field is never blank. It holds either a named missing surface routed to the product backlog as its own item, or the explicit claim "no gap — a reachable control already existed," which the rest of the handoff must support. The source asked for the gap to be "called out explicitly," which is satisfiable by silence.

### Step 5 — Emit the handoff

Produce the record below, then stop.

## Output contract

Six sections, in this order:

```text
CUSTOMER
- name or billing email, and the identifier that resolved

BILLING STATE
- active subscriptions, invoice and renewal state, anomalies

DECISION
- the bucket, the observable that selected it, and why the action follows
- if two buckets matched: both, and how the conflict was resolved

ACTION TAKEN
- what was done, and what is held pending whose approval

FOLLOW-UP
- the short message to send the customer, drafted not sent

PRODUCT GAP
- the missing surface as a backlog item, or the explicit no-gap claim
```

## Examples

**Weak — the customer's words used as the classification:**

> Customer reports being double-charged for the Pro plan. Refunded both charges and cancelled the second subscription. Apologized.

Nothing here was checked. If the second subscription carried a different billing contact, a team just lost a seat and a paid month, and the record does not show that anyone looked.

**Strong — the observable stated, the conflict resolved, the money held:**

> DECISION: Two active Pro subscriptions on the same payer. Both carry seat quantity 1 and share one payment method, which selects *accidental duplicate purchase* — but the second carries a different billing contact (ops@ rather than the founder's address), which independently selects *deliberate team purchase*. Both matched and their actions conflict, so the team default applies: no seat is cancelled and no charge is refunded pending the customer's answer.
> ACTION TAKEN: Portal link sent so the customer can see and manage both subscriptions themselves. Refund of one duplicated charge prepared and held for approval, conditional on the customer confirming the second was not intentional.
> PRODUCT GAP: Checkout does not warn when the same payer starts a second subscription on a plan they already hold. Filed to the product backlog as its own item.
