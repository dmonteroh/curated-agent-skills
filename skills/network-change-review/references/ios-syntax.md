# IOS / IOS-XE syntax layer

The syntax half of the review for Cisco IOS and IOS-XE. The ordered gate in the skill body is vendor-neutral; this file supplies the forms that gate matches against on IOS-family devices. On other platforms the layers still apply and these patterns do not — substitute the platform's equivalents rather than assuming a translation.

## Configuration mode hierarchy

```text
Router> enable
Router# show running-config
Router# configure terminal
Router(config)# interface GigabitEthernet0/1
Router(config-if)# description UPLINK-TO-CORE
Router(config-if)# no shutdown
Router(config-if)# exit
Router(config)# end
Router# show running-config interface GigabitEthernet0/1
```

`running-config` is active memory. `startup-config` is what survives a reload. They are separate objects, and a change is only in the first one until it is explicitly copied.

**Do not persist because a command was accepted.** Acceptance means the parser understood the syntax, not that the change is correct. Validate behaviour first, then `copy running-config startup-config` once post-change checks pass. This is workflow step 9 in the skill body and it is the rule most often violated by generated config, which habitually appends the save as the last line of a snippet.

## Read-only collection

Safe to run during review or during an incident; none of these changes state.

```text
show version
show inventory
show processes cpu sorted
show memory statistics
show logging
show running-config | section line vty
show running-config | section interface
show running-config | section router bgp
show ip interface brief
show interfaces
show interfaces status
show vlan brief
show mac address-table
show spanning-tree
show ip route
show ip protocols
show ip access-lists
show route-map
show ip prefix-list
```

Collect the specific section under review rather than a full config dump. A running config carries secrets, customer names, and private topology, and a ticket or an external tool is not a place to put them.

## Wildcard masks

IOS ACLs and several routing statements take a wildcard mask — the bit-complement of the subnet mask, not the subnet mask itself.

| Subnet mask | Wildcard mask | Hosts matched |
| --- | --- | --- |
| 255.255.255.255 | 0.0.0.0 | exactly one |
| 255.255.255.252 | 0.0.0.3 | 4 |
| 255.255.255.240 | 0.0.0.15 | 16 |
| 255.255.255.0 | 0.0.0.255 | 256 |
| 255.255.0.0 | 0.0.255.255 | 65,536 |

The failure is silent and wide. `permit tcp 192.0.2.0 255.255.255.0 any eq 443` written where `0.0.0.255` belongs does not error — it matches an enormously larger range than intended, and the ACL appears to work because the traffic it was written for still passes. Check every mask in an ACL or `network` statement against this table before the change window.

## ACL form

```text
ip access-list extended WEB-IN
  10 permit tcp 192.0.2.0 0.0.0.255 any eq 443
  999 deny ip any any log
```

Every ACL carries an implicit `deny ip any any` at the end. The explicit logged deny at 999 exists only to make misses observable — add it when the operational goal includes seeing what was dropped, and confirm the log volume the device will generate is safe first.

## Interface hygiene

```text
interface GigabitEthernet0/1
 description UPLINK-TO-CORE
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk native vlan 999
 no shutdown
```

Explicit `switchport mode` rather than relying on negotiation; an allowed-VLAN list rather than the default all; a native VLAN that is documented and unused for data. On routed interfaces, confirm the mask, the peer's addressing, and the routing process — link state means the physical layer is up, not that forwarding is correct.

## Change-window verification

Match the check to the change; a generic ping proves almost nothing.

```text
show running-config | section interface GigabitEthernet0/1
show interfaces GigabitEthernet0/1
show logging | include GigabitEthernet0/1|changed state|line protocol
show ip route <prefix>
show ip access-lists <name>
```

For routing changes, capture neighbour state and route tables on **both sides** of the change, before and after. For ACL changes, compare hit counters from a planned test source — a ping from an arbitrary host exercises a different rule than the one under review, and passing it proves nothing about the rule that changed.
