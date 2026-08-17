# Hybrid Connectivity Reference

Use this when any workload in scope must reach an on-premises datacenter, colo, or branch network. It carries the connectivity-type decision and the topology behind step 5 (networking), the HA pattern behind step 8 (reliability), and the link-health signals behind step 9 (observability).

Provenance: generalized from a single third-party hybrid-networking skill drop. That source published vendor bandwidth caps, circuit tiers, and SLA percentages as flat facts with no citation, so every trade-off below is stated qualitatively instead. **No figure in this file is measured, and none is carried forward from that source.**

## Decide the connectivity type before freezing CIDRs

Private connectivity to on-premises is not a yes/no answer. Two options, with genuinely different consequences:

| | Internet-routed IPSec VPN | Dedicated private circuit |
| --- | --- | --- |
| Path | Public internet, encrypted tunnel | Private cross-connect via the provider or a carrier |
| Latency | Varies with internet conditions; jitter is not controllable | Lower, and materially more consistent |
| Bandwidth | Capped per tunnel by the provider's tunnel limit; scale by adding tunnels plus ECMP | Much higher ceiling, bought as a circuit tier |
| Cost | Low recurring cost | Materially higher recurring cost, plus carrier and cross-connect charges |
| Lead time | Hours; self-service | Weeks; a carrier, a facility, and a cross-connect are involved |

Decision:

- If the requirement is predictable latency, or sustained throughput beyond what a small number of tunnels carries, choose a dedicated circuit — and order it during discovery, because its lead time and not the build work sets the phase plan.
- If bandwidth needs are moderate, traffic is bursty, or the link exists only for a migration phase or a branch office, choose VPN.
- When a dedicated circuit is primary, keep a VPN as the backup path. A dedicated circuit is a single facility until proven otherwise.
- Record the choice, the rejected option, and the driver in the architecture decision summary. It constrains topology, recurring cost, and the phase schedule, and reversing it means re-provisioning.

The same two options by provider:

| Provider | Internet-routed VPN | Dedicated private circuit |
| --- | --- | --- |
| AWS | Site-to-Site VPN | Direct Connect |
| Azure | VPN Gateway (site-to-site) | ExpressRoute |
| GCP | Cloud VPN (HA VPN variant) | Cloud Interconnect (Dedicated or Partner) |
| OCI | IPSec VPN Connect (through a DRG) | FastConnect (through a DRG) |

Per-tunnel bandwidth caps, circuit tiers, and published availability SLAs differ per provider and change over time. Read them from the provider's current documentation when sizing, and never carry a remembered figure into a design document.

## Topology: terminate on-premises once, into a hub

Connect on-premises to a transit hub and fan out from the hub to per-environment networks. Do not run a separate circuit or tunnel per environment.

```
On-premises datacenter
        |
   VPN or dedicated circuit (two of them; see HA below)
        |
   Transit hub  (AWS Transit Gateway / Azure Virtual WAN or hub VNet /
                 GCP Network Connectivity Center / OCI DRG)
        |
        +-- Production VPC/VNet
        +-- Staging VPC/VNet
        +-- Development VPC/VNet
```

Why this matters to the rest of the design: the environment isolation established in step 4 survives contact with hybrid traffic only if it is enforced as routing policy at the hub. A circuit per environment multiplies recurring cost and lead time, and turns every new environment into a networking project.

Variants:

- **Multi-region:** one circuit from the on-premises edge into each region's hub, with peering between hubs — not one circuit backhauled across regions.
- **Multi-cloud:** a separate private link per provider from the same on-premises edge. There is no cross-provider transit hub; the on-premises network is the meeting point.

## High availability: two paths, dynamic routing, tested failover

- Two tunnels or circuits, terminating on **different on-premises devices in different facilities**. Two tunnels to the same router is one failure domain wearing a disguise.
- BGP on every production path. A static route cannot fail over, so a static route on a hybrid path is an outage waiting for its trigger.
- ECMP where the provider supports it, so both paths carry traffic and a nominal standby cannot sit silently broken for months.
- Verify failover by draining one path deliberately and watching traffic move. An untested second path is an assumption, not redundancy. Validate advertised prefixes, failover behavior, and MTU assumptions in the same drill.

## Address and routing hygiene

- Confirm non-overlapping CIDRs across on-premises and every cloud network **before** the first circuit is ordered. An overlap found after the link is live is remediated by renumbering or NAT, both expensive at that point.
- Record both BGP ASNs: the on-premises ASN (typically a private ASN) and the cloud-side ASN, which is provider-assigned on some services and configurable on others — read it from the provider rather than assuming a default value.
- Enable route propagation on the hub route tables, and filter advertised prefixes in both directions so the cloud does not learn the entire on-premises estate, or the reverse.

## Link health belongs in the observability plan

The golden signals in step 9 measure the application. They do not measure the link, and a degraded link surfaces as unexplained application latency unless the link is instrumented separately:

- Tunnel or circuit state (up/down) **per tunnel**, never aggregated — an aggregate hides the loss of redundancy.
- Bytes in/out per tunnel, so saturation is visible before users find it.
- Packet loss and latency across the link.
- BGP session state, plus advertised and received prefix counts.

Alerting split, consistent with page-on-symptoms and ticket-on-causes:

- Both paths down: page.
- One path down while its peer is up: ticket. Redundancy is gone and nothing user-visible has happened yet — that is the entire reason to measure per tunnel.
- BGP session flapping, or a received-prefix count that changes with no change request behind it: ticket and investigate. It usually precedes a routing incident.

## When the session is down: triage order for a hybrid link

The signals above say a link is degraded. This is the order to work it, and it differs from generic device triage in one structural way: **you only own one end.** The provider's side is unreadable, so every check below is written to isolate whether the fault is on the half you can see before opening a ticket that will otherwise bounce back.

1. **Establish which object is down.** Tunnel state and BGP session state are different things and they disagree in a diagnostic way: a tunnel up with BGP down is a routing or policy problem on one side; a tunnel down takes BGP with it and the question is transport. Read both before forming a hypothesis.
2. **Identify the address family and VRF carrying the prefixes**, not just the peer address. A session reported Established while the expected prefixes are missing is usually a different AFI than the one being read.
3. **Capture the last reset reason and the matching log lines before any reset.** On a hybrid path the reason frequently names the far end ("peer closed the session", "hold timer expired"), which is the difference between a ticket the provider accepts and one they return.
4. **Prove transport to the peer source address** — the address the tunnel actually sources from, not the gateway's primary or a loopback assumed by convention. Mismatched update source is a common outcome of a rebuild on the on-premises side.
5. **Check prefix policy before concluding transport failed.** Both directions filter; a filter change on either end presents as a session that is up and useless. Compare advertised and received prefix counts against what the change record says should be there.
6. **Only then open the provider ticket**, carrying the tunnel state, BGP state, last reset reason, transport result, and prefix counts. A ticket without these gets the same five questions back.

Never clear the session as a first diagnostic step. It destroys the reset reason — the single most useful field for a fault whose cause is on the end you cannot read — and on a redundant pair it can move traffic onto the path you were about to investigate.

If both ends are yours and the fault is device-level rather than link-level, this ordering stops here: what follows is read-only evidence collection against the device itself, which is a different procedure with a different output.

## Common pitfalls

- Treating private connectivity as a yes/no answer when the real decision is VPN versus dedicated, with different cost, latency, and lead-time consequences.
- Clearing a BGP session to "see if it comes back" before the last reset reason is captured.
- Ordering a dedicated circuit after the implementation plan is committed, then discovering its lead time owns the critical path.
- Calling a single tunnel highly available.
- Discovering a CIDR overlap after the link is live.
- Instrumenting the applications and not the link.
