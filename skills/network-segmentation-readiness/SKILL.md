---
name: network-segmentation-readiness
description: "Gates a restructure of a small network before any command is issued: trust zones, local DNS resolver placement, and remote access. Collects inventory, proves management access survives, and stages the migration. Use when splitting a flat network, moving DHCP to a local resolver, or adding VPN access."
metadata:
  category: network
---
# Network Segmentation Readiness

The failure this prevents is specific and common: the change succeeds, and the operator can no longer reach the device that would let them undo it.

The first output is always read-only — inventory, risks, staged plan, validation, rollback. Configuration comes after the platform, the current topology, the rollback path, console access, and the maintenance window are all known, and not before.

## Use this skill when

- A flat network is being split into trusted, server, IoT, guest, or management zones
- DHCP clients are being moved to a local DNS resolver, or filtering is being introduced
- Remote access is being added — a VPN tunnel, an overlay network, or a forwarded port
- A planned change might lock the operator out of the gateway, switch, access point, resolver, or VPN endpoint
- An informal restructuring idea needs to become a staged migration with validation evidence at each step

## Do not use this skill when

- A candidate configuration already exists and needs reviewing before it is pushed — that is a pre-deploy gate against a written artifact, not a planning pass
- A device is already misbehaving and the need is evidence about live state
- The network is a cloud VPC, subnet, or peering design — cloud network architecture owns addressing and connectivity there, and none of the physical-layer or console-access reasoning applies
- The design question is capacity, throughput, or hardware selection rather than trust boundaries and reachability
- The change is a single-device setting with no zone, resolver, or reachability consequence

## Required inputs

Collect all of this before giving implementation steps. A missing row is a question to ask, not a default to assume.

| Area | What to establish |
| --- | --- |
| Internet edge | The modem or ONT, and whether the ISP device is bridged or still routing |
| Gateway | What routes, firewalls, serves DHCP, and terminates remote access |
| Switching | Which ports are uplinks, access ports, trunks, or unmanaged |
| Wireless | Which SSIDs map to which networks, and whether APs are wired or mesh |
| Addressing | Which subnets exist, and which ranges conflict with networks the operator connects from remotely |
| DNS and DHCP | Which service hands out leases today, and which resolver address it advertises |
| Management | How the operator reaches gateway, switch, and AP *after* the change |
| Recovery | What can be reverted locally, physically, if DNS, DHCP, routing, or remote access breaks |

## Constraints

These are gates, not preferences. Each one fails the plan closed.

- **No configuration without a confirmed platform and a written rollback.** Firewall, NAT, VLAN, DHCP, and remote-access syntax differ enough between platforms and firmware versions that a plausible-looking command from the wrong one is worse than no command.
- **Out-of-band or same-room console access is confirmed before** changing management VLANs, trunk ports, firewall default policy, or DHCP/DNS settings. "There is a console port" is not confirmation; reaching it is.
- **A working path to the internet survives** any resolver or default-route change. The recovery path must not depend on the thing being changed.
- **Management interfaces are never exposed to the public internet** — not the gateway UI, not the resolver, not SSH, not the NAS console, not the VPN management surface.
- **IoT, guest, camera, and lab-server networks are separate trust zones** until the operator explicitly decides otherwise. Collapsing them is a decision, not a default.

## Trust zones

Start from intent. Vendor syntax comes after the zones and their default policies are agreed.

| Zone | Typical contents | Default policy |
| --- | --- | --- |
| Trusted | Laptops, phones, admin workstations | Reaches shared services; reaches management only when needed |
| Servers | NAS, automation hosts, lab machines, the resolver | Accepts narrow inbound flows from trusted clients |
| IoT | TVs, plugs, cameras, speakers | Internet only, plus explicit named exceptions |
| Guest | Visitor devices | Internet only, no reachability into any other zone |
| Management | Gateway, switches, APs, controllers | Reachable only from trusted admin devices |
| Remote | VPN or overlay clients | The same access as trusted, or narrower — never broader |

Before proposing VLAN IDs or subnets, confirm all five:

1. The gateway does inter-VLAN routing *and* filtering between zones.
2. The switch supports the tagged and untagged port behaviour the plan needs.
3. The APs can map each SSID to its zone.
4. The operator knows which physical port and which SSID they are connected through **during** the change.
5. The management zone stays reachable after the trunk and SSID changes land.

**Addressing decision:** avoid `192.168.0.0/24` and `192.168.1.0/24` on any network the operator will reach remotely. They are the default on consumer routers, hotel Wi-Fi, and office guest networks, so a remote client on one of those cannot route to a home network using the same range — the tunnel establishes and nothing behind it is reachable. Pick ranges that are unlikely to collide at both ends.

**Naming decision:** use `home.arpa` for local names (RFC 8375, reserved for exactly this). Ad hoc suffixes like `.local` collide with multicast DNS and `.lan` leaks to public resolvers.

## Resolver readiness

A local resolver is introduced as a dependency, which means it is also a new single point of failure. In order:

1. Give it a reserved address before any DHCP option points at it.
2. Confirm it resolves both public names and local `home.arpa` names.
3. Keep the gateway or a second resolver reachable as a fallback.
4. Change one client or one zone and validate before touching every DHCP scope.
5. Write down which zones may bypass filtering, and why.
6. Check the blocklists against captive portals, employer VPNs, firmware update endpoints, and any medical or security device on the network.

Validation evidence, per test client: the expected DHCP lease; the expected resolver address; a successful public lookup; a successful `home.arpa` lookup; a blocked test domain blocked *only* in the zones intended; and management interfaces unreachable from guest and IoT.

## Remote access readiness

Decide what the tunnel may reach before generating keys or opening a port.

| Mode | Use when | Watch for |
| --- | --- | --- |
| Split tunnel, one subnet | Remote admin of specific hosts | Keep the advertised route list narrow |
| Split tunnel, selected services | Access to named apps | Needs precise firewall rules, not just routes |
| Full tunnel | Untrusted networks and travel | Bandwidth and DNS become your responsibility |
| Overlay network | Simpler access with identity controls | Still needs an access-control review |

Do not recommend a forwarded port until all five are confirmed: the endpoint is patched and maintained; the port reaches the VPN service only, never an admin UI; dynamic DNS, public IP behaviour, and whether the ISP uses CGNAT are all understood; peer keys can be revoked individually; and connection logs can show who connected and when.

## Workflow

Small, reversible, validated at each step.

1. Snapshot current topology, addressing, DHCP, DNS, and firewall rules. This is the rollback target.
2. Reserve infrastructure addresses — gateway, resolver, controller, APs, storage, VPN endpoint.
3. Create the new zone without moving anything into it.
4. Move one test client. Validate DHCP, resolution, routing, internet, and block behaviour.
5. Add named firewall exceptions for the flows that validation proved are needed.
6. Move one low-risk device group. Re-validate.
7. Add remote access with the narrowest route set and policy that satisfies the use case.
8. Document final state, exceptions, and rollback in the vocabulary of the platform's own UI or CLI.

## Common pitfalls

- Leaving DHCP enabled on a consumer router repurposed as an access point, so two servers answer the same broadcast
- Adding an allow-all rule "temporarily" and never removing it

## Output contract

- Inventory table, with unknowns marked as unknown rather than assumed
- Zone plan: each zone, its contents, its default policy, and the named exceptions
- The reachability proof: how the operator reaches management during and after each step
- Staged sequence, each step with its validation evidence and its rollback
- Risks that remain after the plan, and what would detect each one

## Examples

**Wrong:** "Create VLANs 10, 20, 30 on the gateway, tag the trunk to the switch, and map the SSIDs." Correct-looking, and if the admin workstation is on the port being converted to a trunk, the next command has no path to the device.

**Right:** Inventory first. The operator is on a wired port on switch port 8, untagged, management. That port stays untagged and in the management zone through the entire migration, and it is the documented recovery path. Zones are created empty. One test client moves. Only then does the SSID mapping change — and the admin workstation's path is verified again before the trunk conversion.
