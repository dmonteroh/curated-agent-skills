# Trigger Cases: network-segmentation-readiness

## Positive (should activate)
- prompt: "Everything at home is on one flat subnet — cameras, laptops, the NAS. I want to split it up without bricking my access."
  expect_activate: yes

- prompt: "I'm putting a Pi-hole in and pointing DHCP at it. What should I check before I change the scope?"
  expect_activate: yes

- prompt: "Planning to add WireGuard so I can reach the lab from outside. What do I need to decide before I generate keys or forward a port?"
  expect_activate: yes

- prompt: "If I convert the port my desktop is plugged into to a trunk, do I lose the switch? How do I sequence this safely?"
  expect_activate: yes

- prompt: "I want a guest SSID that can't see anything else on the network. Walk me through the plan and how I'd verify it."
  expect_activate: yes

- prompt: "Redesign the VLANs and switch stack in our office network. Nothing here is going to the cloud."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Here's the finished firewall config for the gateway. Review it for dangerous commands before I apply it."
  expect_activate: no

- prompt: "The WAN interface is showing errors and the internet keeps dropping. What do I check?"
  expect_activate: no

- prompt: "Design the VPC subnets, route tables, and peering for our AWS landing zone."
  expect_activate: no

- prompt: "Which switch should I buy — is 2.5GbE worth it over gigabit for my uplinks?"
  expect_activate: no

- prompt: "Change the DNS server on this one laptop to 1.1.1.1."
  expect_activate: no
