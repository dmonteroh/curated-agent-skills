# Trigger Cases: network-device-diagnostics

## Positive (should activate)
- prompt: "Our BGP session to the transit provider has been flapping since this morning. Where do I start?"
  expect_activate: yes

- prompt: "The neighbor is stuck in Active and I don't know whether it's us or them. What do I check, in what order?"
  expect_activate: yes

- prompt: "Switch port Gi0/24 is showing CRCs and the counter keeps climbing. Is that the cable or the far end?"
  expect_activate: yes

- prompt: "Users on one VLAN report intermittent drops. The interface has output drops but the link is up — how do I tell congestion from a hardware fault?"
  expect_activate: yes

- prompt: "The session says Established but we're receiving zero prefixes. What evidence do I collect before touching anything?"
  expect_activate: yes

- prompt: "I need before-and-after interface counters for tonight's change window. How should I capture them so the comparison is valid?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Here's the config we're pushing to the edge router tomorrow. Review it for anything dangerous before the window opens."
  expect_activate: no

- prompt: "We're deciding between an ExpressRoute circuit and a VPN for the datacenter link, and how many tunnels we need. What's the right topology?"
  expect_activate: no

- prompt: "The interface counters are completely clean and the session is stable, but the API is still slow for users in the branch office."
  expect_activate: no

- prompt: "Just go ahead and clear the BGP session and reconfigure the timers so it stops flapping."
  expect_activate: no

- prompt: "Plan out the VLAN split for our office so cameras and laptops stop sharing a subnet."
  expect_activate: no
