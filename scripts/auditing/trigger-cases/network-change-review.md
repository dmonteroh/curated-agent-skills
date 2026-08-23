# Trigger Cases: network-change-review

## Positive (should activate)
- prompt: "Here's the config we're pasting into the core switch tomorrow night. Check it before the window opens."
  expect_activate: yes

- prompt: "Our Ansible role generates router config from a template. I want a pre-flight gate that fails the run on anything dangerous."
  expect_activate: yes

- prompt: "Review this ACL before we bind it — I want to be sure about the direction and the mask form."
  expect_activate: yes

- prompt: "Does this candidate config reference any access-list or route-map that isn't actually defined anywhere?"
  expect_activate: yes

- prompt: "We're changing the VTY config on 40 devices. What has to be confirmed before we start, and what would block it?"
  expect_activate: yes

- prompt: "A model generated this IOS snippet. Is it safe to apply as-is?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "BGP to our upstream just dropped and I need to figure out why right now."
  expect_activate: no

- prompt: "Review this Terraform security group and VPC route table before we apply it."
  expect_activate: no

- prompt: "Check this Kubernetes NetworkPolicy before it goes into the cluster."
  expect_activate: no

- prompt: "I need a proper IOS parser that builds an accurate config model, not pattern warnings."
  expect_activate: no

- prompt: "Should we use OSPF or BGP internally? Just the design question, nothing is written yet."
  expect_activate: no
