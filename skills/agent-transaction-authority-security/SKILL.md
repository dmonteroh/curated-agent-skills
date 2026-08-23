---
name: agent-transaction-authority-security
description: "Provides a layered control procedure for autonomous agents that can move value — trades, swaps, transfers, treasury operations — with every limit enforced outside the model rather than inside its prompt: authority enumeration, spend caps, pre-send simulation, circuit breakers, account isolation, protected routing, audit logging. Use when an agent holds transaction authority."
metadata:
  category: security
---
# LLM Trading Agent Security

Provides a control procedure for the case where a wrong or hijacked model output becomes an irreversible loss of funds. The individual controls are ordinary; what makes them hold is that each one lives in deterministic code the model cannot edit, is never asked to consult, and cannot talk past. A limit written into a system prompt or a tool description is a suggestion, and the threat model here includes text that argues with suggestions.

The source material is a set of controls without an order or a stated rationale. Rules added beyond it are marked *(Authored)*.

## Use this skill when

- An agent signs, submits, or authorizes transactions on its own
- Auditing a trading bot, execution assistant, or treasury automation that acts without a human in the loop
- Designing the boundary between an agent's decisions and the account that funds them
- Giving a model access to order placement, swaps, payments, transfers, or allowance grants
- Deciding what an agent is permitted to do after a loss, an error, or a result it did not expect

## Do not use this skill when

- The agent has no execution authority — read-only market analysis, research, or advisory output. There is no value-moving action to gate, and the controls here would be ceremony
- The ask is the injection defense itself: enumerating which inputs reach the context, normalizing before detecting, deciding whether a layer warns or blocks. Composing detection layers over untrusted content is its own discipline. This skill assumes that work happens elsewhere and is built so the money survives its failure
- The ask is key storage, rotation, backend selection, or leak response. Credential handling is a separate discipline; this skill only requires that a key arrives from outside the code and that its absence stops startup
- The ask is a full security assessment — threat model, findings table with quoted evidence, prioritized remediation with owners. This is a control set for one surface, not an audit
- The question is whether the strategy makes money, or whether a given trade is a good idea. Every control here is indifferent to that: it bounds the damage of a wrong decision without judging the decision *(Authored: the source states no such boundary, but without it the skill fires on ordinary trading-strategy questions it has nothing to say about.)*

## Workflow

Run the controls in this order. Each one assumes the one before it is already standing. *(Authored: the source presents these as an unordered set; the ordering is imposed here so a cap is not designed before it is known what needs capping, and so nothing downstream depends on a control that does not exist yet.)*

1. **Enumerate every action that moves value, before designing any control.**
   - List each tool, endpoint, or capability the agent can invoke that transfers, spends, commits, or encumbers funds. Include authorizations that move nothing at the time: granting a third party a standing allowance to withdraw later is a value-moving action, and it is the one most often left off the list *(Authored: the source treats allowance grants only as a text pattern to watch for, not as an item on the authority inventory.)*
   - For each capability, name the deterministic gate standing between the model's decision and the dispatch, and say where that gate's code lives.
   - Stop condition: a capability with no gate is the finding. Report it and do not proceed to design the later controls around it.
   - Output: an authority table — capability, what it can move, its gate, where the gate lives.

2. **Cap the spend outside the model.**
   - Enforce a per-action ceiling and at least one rolling-window ceiling in code the model neither edits nor is asked to check. A cap the model is merely told about is lifted by one convincing sentence in a page it read.
   - Commit the spend against the window *before* the action is dispatched, never on the success path *(Authored: the source records the spend inside its check without stating the rule; an action that times out or is dropped in flight can still settle, so authority it consumed must not be handed back by a failed response.)*
   - Over-cap is a refusal, not a clamp: never reduce the amount to fit the ceiling and send it anyway *(Authored: the source raises but does not rule out the clamp; silently resizing an action the operator never approved substitutes the gate's judgment for theirs.)*
   - Derive both ceilings from the funds the strategy is meant to risk in that window. Any figure carried in from another deployment is a placeholder, not a recommendation.
   - Output: the two ceilings, where they are enforced, when they are committed relative to dispatch, and the basis each was chosen on.

3. **Simulate before sending, against a caller-supplied minimum.**
   - Dry-run the exact action against current state and compare the simulated result to a minimum acceptable outcome that the caller supplied.
   - A missing minimum is a hard refusal, not a default. An action sent with no expected floor cannot be checked against anything, and a default floor supplied by the gate is a number nobody chose.
   - Abort on shortfall. Re-simulate if anything changed between the simulation and the dispatch — a simulation is a statement about the state it ran against, and nothing more *(Authored: the source sets an expiry on the action but never states the re-simulation rule.)*
   - Output: the simulated result, the supplied minimum, and the decision.

4. **Install a circuit breaker that halts on loss and on invalid state.**
   - Halt on a run of consecutive losing actions, and on drawdown beyond a bound over a rolling window. Both the run length and the drawdown bound are per-deployment choices with no general value behind them.
   - Halt on invalid internal state as well: if the window's opening baseline is zero or negative, the drawdown ratio is meaningless, and a breaker that divides by it stops protecting anything without ever reporting that it did.
   - A halted breaker clears on an explicit human action, never on elapsed time *(Authored: the source halts but never says how a halt ends; a timer re-arms the agent into the same conditions that tripped it, which is how one bad hour becomes several.)*
   - Output: the halt conditions, and the named action that clears a halt.

5. **Isolate the executing account.**
   - The agent signs from a dedicated account funded with the working balance for the session only, never a primary treasury. The blast radius of a total compromise then equals a number somebody chose deliberately.
   - The signing key arrives from the environment or a secret manager. Its absence is a refusal to start, not a fallback to something else.
   - Output: what the execution account holds, how it is topped up, and what happens on a missing key.

6. **Route the dispatch so it is not exploitable in transit.**
   - Where the submission path exposes pending actions publicly before they settle, they are visible to anyone who profits from acting first. Use a protected or private submission route where one exists for that path.
   - Set a tolerance for adverse price movement and an expiry after which the action is void rather than executable later against unrelated state. Both are per-strategy choices; the source's values were chosen constants.
   - Output: the routing decision, the tolerance, and the expiry, each with the strategy it belongs to.

7. **Log every decision, including the ones that did not execute.**
   - Record refusals, cap breaches, simulation aborts, and breaker halts beside successful sends, with the input that produced each.
   - A log of successful sends only cannot answer the question an incident actually asks, which is what the agent *tried* to do.
   - Output: the event set logged, and where it is written.

## Examples

**Wrong beside right — where the cap lives.**

- Wrong: the ceiling is stated in the system prompt ("never spend more than the daily limit") and repeated in the tool description. A poisoned feed, a hostile page, or a plain misreading lifts it, and the trace shows the model reasoning its way to why this case was different.
- Right: the execution path refuses an over-ceiling amount before anything is signed, raises, and logs the refusal. The model can be argued into anything; it cannot be argued into a different code path.

**One gate, in code.** Transport-agnostic: `ledger`, `simulate`, `dispatch`, and `breaker` are supplied by the caller, so the same gate wraps an exchange order, an on-chain swap, or a payment API call. Standard library only.

```python
from decimal import Decimal

# Placeholders, not recommendations: no derivation stands behind either figure.
# Set both from the funds this strategy is meant to risk in that window.
PER_ACTION_CEILING = Decimal("500")
WINDOW_CEILING = Decimal("2000")


class Refused(Exception):
    """Every gate failure is a refusal: nothing here clamps, defaults, or retries."""


class ValueGate:
    """Gates one value-moving action. Takes no instruction from model output —
    the caller supplies the action, the amount and the minimum; never the ceilings."""

    def __init__(self, ledger, simulate, dispatch, breaker):
        self.ledger = ledger
        self.simulate = simulate
        self.dispatch = dispatch
        self.breaker = breaker

    def execute(self, action, amount: Decimal, minimum_out):
        if self.breaker.halted:
            raise Refused("breaker halted; clearing it is a human action")
        if minimum_out is None:
            raise Refused("no expected minimum supplied, so nothing can be checked")
        if amount > PER_ACTION_CEILING:
            raise Refused(f"{amount} over the per-action ceiling {PER_ACTION_CEILING}")
        window = self.ledger.window_total()
        if window + amount > WINDOW_CEILING:
            raise Refused(f"{window} + {amount} over the window ceiling {WINDOW_CEILING}")
        simulated = self.simulate(action)
        if simulated < minimum_out:
            raise Refused(f"simulated {simulated} below required minimum {minimum_out}")
        self.ledger.commit(amount)  # before dispatch, never on the success path
        return self.dispatch(action)
```

Verify the ordering rather than assuming it: a test in which `dispatch` raises must still leave the spend recorded on the ledger. If it does not, the commit has drifted onto the success path and a dropped-but-settled action will spend the window twice.

## Common pitfalls

- Writing the spend limit into the prompt or the tool description instead of the code path
- Recording the spend on the success path, so an action that failed loudly and settled quietly leaves the window under-counted
- Sending with a gate-supplied default minimum when the caller gave none
- Simulating once and dispatching later against state that has moved
- Clearing a tripped breaker on a timer, or by restarting the process
- Signing from the treasury account "for now"
- Logging only successful sends
- Blocking on a keyword list over incoming text and calling that the injection defense. It fires on ordinary language about transfers and approvals, and any encoding of the payload walks straight past it. This is the one control in the source material that is cut here rather than generalized

## Output contract

When this skill runs, respond with:

- Authority table: every value-moving capability, what it can move, its gate, and where that gate lives
- Ungated capabilities listed first — that is the finding, not a footnote
- Cap policy: both ceilings, where enforced, when committed relative to dispatch, and the basis each was chosen on
- Simulation policy: what is simulated, what supplies the minimum, and what happens when it is absent
- Breaker conditions, and the named action that clears a halt
- Execution account: what it holds and how the signing key reaches it
- Routing, tolerance, and expiry, per strategy
- The logged event set, refusals included
- Residual risk: what these controls do not defend against. The injection layer and the key-handling layer are outside this skill, and their failure is not covered by anything above
