# Optional-Capability Provider Contract

Applies when an MCP server wraps one or more optional, swappable backend providers (a search index, an embeddings backend, a code-intelligence tool) rather than a single fixed integration. Providers differ in what they can do; the contract makes that difference explicit and checkable instead of leaking into ad hoc `if` checks at each call site.

## Split operations into a required set and an optional set

- Define a small required operation set every provider must implement, plus a separate optional set a provider may or may not back.
- Choose the required set as the honest common denominator across the providers actually expected, not the richest provider's feature set. Making a rich-provider-only operation required either excludes providers that cannot back it, or forces them to stub it with a fake implementation that lies about what actually happened.

## Providers advertise exactly what they back

- Require every provider to declare, as a machine-checkable set constructed at instantiation, exactly which capabilities it implements.
- Assert the required capabilities at construction time — fail immediately if a provider claims to exist but does not back the required set, rather than discovering the gap on first use.
- Pin that construction-time assertion with its own test, so a provider that silently drops a required capability during refactoring fails the suite instead of surfacing as a runtime surprise later.

## Unadvertised calls throw, never no-op

- Calling an operation the provider did not advertise throws a typed, named error (for example, `CAPABILITY_UNSUPPORTED`) — never a silent no-op or an empty success.
- A silent no-op is indistinguishable from "ran and legitimately found nothing." That ambiguity corrupts every caller's ability to reason about the result: a caller cannot tell "the provider doesn't support this" from "the provider tried and there was nothing there."

## A closed error-code set with one designated non-fatal code

- Define a closed, enumerated set of error codes for the provider layer rather than open-ended exception types or ad hoc strings.
- Designate exactly one code as the non-fatal "degrade and continue" signal — the one callers are expected to catch and fall back from (for example, to a local or grep-based path). Every other code is fatal to that call.
- One verified source's set: `PROVIDER_UNAVAILABLE` (the non-fatal one — the provider is down or unreachable, caller degrades), `PROVIDER_NOT_CONSENTED`, `CAPABILITY_UNSUPPORTED`, `SOURCE_NOT_REGISTERED`, `PROVIDER_TIMEOUT`, `PROVIDER_ERROR`. Treat the specific six as a worked example, not a mandated count — the source asserts only that the set must be closed and must include exactly one non-fatal code, not that six is the right number.

## Consent as two orthogonal axes, neither auto-granted

- Model consent separately for: (a) installing or enabling the provider at all, and (b) allowing this provider to receive content when it operates non-locally (network egress).
- Enforce the egress-consent check inside the contract itself — at the point capability is invoked — not left to each call site to remember. A call made without consent throws rather than silently proceeding.
- A provider that runs entirely locally can skip the egress axis: nothing leaves the machine, so there is nothing to consent to on that axis.

## The host stays fully functional with the provider off

- The provider contract is strictly an enhancement layer, never a hard dependency: the host must work with the provider disabled.
- When no provider is selected, the resolution mechanism returns `null` — not a stub or mock implementation. A `null` gives callers an explicit, checkable "off" state; a stub that silently does nothing hides the fact that a feature is unavailable.
