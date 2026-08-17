# Remote Capability Exposure

Applies when a local, already-trusted process (an agent daemon, dev tool, or CLI) is deliberately exposed to a remote or third-party caller. This is a different threat model from client-server web auth: the "client" may be acting on untrusted instructions (a hostile prompt or page), and the goal is to make the powerful surface structurally unreachable, not merely access-checked.

## Separate surfaces by socket, not by middleware

- Bind two separate listeners rather than gating one listener with an authorization check.
- The local-only listener carries the full, unrestricted command set and is bound to loopback; it is never exposed off-machine.
- The remote-facing listener is bound only when remote access is actually requested (and torn down when it ends); it carries a locked-down path allowlist.
- A caller who reaches the exposed address cannot route to the private paths at all — they simply do not exist on that socket. A caller who stumbles onto the public URL gets a 404, not a permission denial: this is a structurally stronger boundary than a single check that a routing bug could bypass.

## Command allowlist on the exposed surface

- The remote-facing endpoint accepts only a fixed, named set of capability-driving commands.
- Deny management commands outright on the exposed surface — the ones that would reconfigure or reveal the server itself — even for an otherwise-valid caller.

## Token ladder with descending power and TTL

- Issue credentials as a ladder: a short-lived, one-time setup credential is exchanged for a longer-lived, narrower-scoped session credential.
- Keep the top of the ladder (a root or full-power credential) out of the exposed surface entirely — reject it outright if it ever arrives there, regardless of validity.
- Give any narrower-purpose credential (for example, a stream-only token) its own tight TTL and restrict which endpoints accept it.
- Any specific TTL or expiry value is a chosen default, not a measured one — pick numbers that bound the blast radius of a leaked credential for the surface at hand, and state them as chosen when writing them into a design.
- One worked example, carried from the source as its own chosen defaults rather than a measured or universal figure: a one-time setup credential expiring in 5 minutes, exchanged for a session credential valid 24 hours (configurable), with a separate stream-only credential capped at 30 minutes and rejected outright at the command endpoint regardless of validity. Use it to calibrate relative scale (setup keys live minutes, session tokens live around a day, narrow-purpose tokens live well under an hour and are endpoint-restricted) — not as values to copy verbatim into an unrelated system.

## Capability tiers as the unit of grant

- Grant capability through a small set of named, scoped tiers rather than a single all-or-nothing token.
- One verified source uses four tiers — `read`, `write`, `admin`, `meta` — with the default mint covering `read` and `write` together, not a single least-privilege tier; `admin` (and `meta`) require an explicit action at grant time to unlock.
- Treat the tier count and names as one worked example, not a fixed taxonomy: choose tier names and a default grant that fit the surface being exposed, and require an explicit step to reach the highest tier(s). Do not carry the specific names `read`/`write`/`admin`/`meta` into an unrelated system as if they were a standard — restate the principle (a small named ladder, an elevated tier gated behind an explicit grant step, no auto-escalation to the top).

## Supporting controls worth carrying alongside the above

- Log every rejection on the exposed surface with a reason code, source, and timestamp; rate-cap the log itself so a flood of rejected requests cannot become its own denial-of-service or fill the disk. (One source's chosen cap: 60 writes/minute — a chosen default, not a measured one; size it to the deployment.)
- Scope ownership of mutable resources per caller, not per token class: any caller may read a shared resource, but only the caller that created it may write to it; pre-existing resources default to owner-only writes.
- Validate any caller-supplied URL against an SSRF blocklist (localhost/private-range targets) before acting on it, on every command that causes the server to fetch or navigate to a caller-given address.

## Source

`docs/REMOTE_BROWSER_ACCESS.md`, a third-party project design doc surfaced through this repo's skill-intake extraction pipeline (`tmp/new-skills/_extracted/feeds/auth-implementation-patterns.md`). The capability-tier names and default grant above are stated as this source states them; an earlier draft of this finding used different tier names (`observe`/`interact`/`mutate`/`restore`) that do not appear in the source and were corrected before landing here.
