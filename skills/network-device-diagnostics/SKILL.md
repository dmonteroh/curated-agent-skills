---
name: network-device-diagnostics
description: "Triages a live router, switch, or host link read-only: BGP session state, route exchange, interface errors, drops, and duplex or speed mismatches. Produces an evidence record, not a fix. Use when a network device is misbehaving now and every mutating action must wait for a change window."
metadata:
  category: network
---
# Network Device Diagnostics

Provides a read-only triage loop for a network device that is already misbehaving. The product is evidence — what the device reports, at what time, compared against what it reported before — so that a change window starts from fact rather than from a guess.

## Use this skill when

- A BGP neighbour is stuck in Idle, Connect, Active, OpenSent, or OpenConfirm, or is flapping
- A BGP session is Established but expected prefixes are missing or unexpected prefixes are present
- An interface reports CRCs, runts, giants, input or output drops, resets, or link flaps
- A host, VLAN, or segment has loss, latency spikes, or intermittent reachability and the link layer is a candidate
- A change window needs before/after counter or session evidence

## Do not use this skill when

- The artifact under review is a candidate configuration that has not been pushed yet — that is a pre-deploy review, not a live triage
- The link is a cloud hybrid tunnel and the question is topology, redundancy, or what to alert on, rather than why the session is down right now
- Device counters and session state are clean and the symptom persists — the problem is above the link, and service-level or application diagnosis owns what follows
- You are authorized to change the device and want the fix rather than the evidence; this skill's output stops at the reviewed action list
- No live device output is obtainable, first-hand or supplied — every step here reads state, and a triage with no state to read produces invention

## Required inputs

- The symptom as observed, with the time it started and how it was noticed
- Access to read device state, or transcripts supplied by someone who has it
- The scope of what may be touched, and who approves a change window

## Workflow

1. **Name the exact object before running anything.** For a session: neighbour address, address family, VRF, local ASN, remote ASN. For a link: the interface *and* its far end, on the far-end device. A triage scoped to "the router" reads the wrong table on the first command.
   - Output: the object identified, written down, with the far end or peer named.
2. **Capture the first read together with the last-change state.** Session state plus the last reset reason and matching log lines; or interface counters plus the time they were last cleared.
   - Constraint: record the baseline *before* clearing any counter. A cleared counter with no baseline destroys the evidence the rest of this workflow compares against.
   - Output: raw output stored verbatim, timestamped.
3. **Route to the symptom table** — `## BGP session symptoms` or `## Interface and link symptoms` below — and run only the checks that symptom names.
   - Output: the first-check results for that symptom.
4. **Prove the lower layer before concluding about the higher one.** Transport to the peer source address before route policy. Signal and media before congestion. Concluding "policy is filtering" while the TCP session never completed is the most common wasted change window.
   - Decision: if the lower layer fails, stop and report there; the higher-layer question is not yet askable.
   - Output: which layer the evidence isolates.
5. **Re-capture after a stated interval and compare increments.** A counter is evidence only as a delta over a named interval; an absolute total mixes today's fault with two years of history. A session's uptime is evidence only against the reset reason that preceded it.
   - Decision: if nothing incremented over the interval, the symptom is not currently reproducing — say so rather than acting on historical state.
   - Output: the delta, and the interval it was measured over.
6. **Sort every candidate action into read-only or change-window** per `## Constraints`, and report. This skill ends here.
   - Output: the evidence record per `## Output contract`.

## BGP session symptoms

| State | First checks |
| --- | --- |
| Established, prefix count present | Route exchange is up. Inspect inbound and outbound policy, then table selection. |
| Established, zero prefixes | Inbound policy, max-prefix limit, what the peer says it advertised, and whether the AFI/SAFI you are reading is the one carrying the routes. |
| Active | The TCP session is not completing. Check routing to the peer, the update source, ACLs, and control-plane policy — in that order. |
| Connect | TCP is in progress. Check the path and whether the remote side is listening on 179. |
| OpenSent / OpenConfirm | TCP works and the negotiation is failing. Check ASN on both sides, authentication, timers, capabilities, and the logs. |
| Idle | Neighbour disabled, config missing, blocked by policy, or in backoff. Read the logs before assuming the peer is at fault. |

Prove transport to the **peer source address**, not to the peer's loopback by assumption. If the session is sourced from a loopback, confirm both directions route to the loopback addresses and that the neighbour config names the update source you think it does.

Use AS-path regex with token boundaries. `_65001_` matches AS 65001 as a token; bare `65001` also matches 650012 and unrelated text.

Some platforms need extra configuration before received-route output exists. **Missing received-route output is not proof that no routes arrived** — and adding that configuration mid-incident is a change, not a diagnostic.

## Interface and link symptoms

| Counter | Meaning | Where to look first |
| --- | --- | --- |
| CRC | Received frame checksum failed | Cable, fiber cleanliness, optic, duplex mismatch |
| input errors | Aggregate receive-side errors | Read the sub-counters before concluding anything |
| runts | Frames below minimum Ethernet size | Duplex mismatch, collision domain, faulty NIC |
| giants | Frames above expected MTU | MTU mismatch or a jumbo-frame boundary |
| input drops | Device could not accept inbound packets | Burst, oversubscription, CPU path, queue pressure |
| output drops | Egress queue discarded packets | Congestion, QoS policy, undersized uplink |
| resets | Interface hardware reset | Flapping, keepalive, driver, optic, power |
| collisions | Ethernet collision counter | Half duplex or a negotiation mismatch |

**Receive-side errors describe the signal arriving on that side.** They are not an accusation against the port that reports them, which is why both ends are captured in step 1 — the far end's transmit path is the usual cause.

**Separate input drops from output drops before acting.** They lead to different branches: input drops to burst and queue pressure, output drops to congestion, QoS, and uplink sizing. Compare the interface rate against its capacity before touching queue tuning — prove the link is congested first.

**Output drops are congestion before they are ever a cable.** Treating them as a physical fault replaces working hardware and leaves the symptom.

Prefer auto-negotiation where both sides support it. If one side must be pinned, pin both and record why. Never leave fixed speed/duplex on one side against auto on the other.

## Constraints

Read-only is the default, and the following are change-window actions with a written justification — never diagnostic steps:

- Clearing a BGP session, or clearing interface counters before a baseline exists
- Changing neighbour authentication, timers, update source, route-maps, or prefix-lists
- Enabling additional received-route storage
- Relaxing a firewall rule, ACL, or control-plane policy to see whether it is the cause
- Changing speed, duplex, or MTU on a live link

Removing a filter to test whether the filter is the problem converts a single-neighbour fault into an outage and destroys the evidence at the same time. Read hit counters, logs, and path state instead. If a reset is approved, use the least disruptive option the platform supports — soft reconfiguration or route refresh before a hard clear — and record why it is safe.

## Common pitfalls

- Clearing counters before recording a baseline
- Reading one end of a link and concluding which end is faulty
- Treating historical CRCs as an active problem without a time window
- Assuming `Active` means the remote side is down
- Ignoring VRF, address family, or update-source differences
- Hard-resetting a peer before reading the last reset reason and the logs

## Output contract

- The object diagnosed: neighbour + AFI + VRF, or interface + far end
- Raw captured output, stored verbatim alongside any structured parse
- The measurement interval, and the deltas observed across it
- Which layer the evidence isolates, and which layers were ruled out with what
- Actions split into two lists: already performed (read-only) and requiring a change window (each with its justification)
- What could not be determined, and what access or output would settle it

## Examples

**Symptom: "BGP to the transit provider is down."**

Wrong: clear the neighbour, see if it comes back. The session re-establishes, the reset reason is gone, and the cause is now unknowable.

Right: name the neighbour, AFI, and VRF. Capture summary state and `Last reset` reason. State is `Active` → transport, not policy. Ping the peer from the configured update source, not from the default. Report: session down, transport failing from the update source, last reset "peer closed the session", change-window action list is one item — nothing yet, pending the provider's side.

**Symptom: "The office internet is slow but the LAN is fine."**

Capture WAN interface errors and drops, then LAN uplink utilization and output drops. Clean counters on both, with the symptom still present, ends this skill: the evidence isolates the problem above the link.

## References

- Corrected parsing patterns for session summary and interface output, with the block-slicing rationale: `references/output-parsing.md`
