# Trigger Cases: plan-review

## Positive (should activate)
- prompt: "Here's the implementation plan before anyone writes a line of code. Go through it properly and tell me what's wrong with it."
  expect_activate: yes

- prompt: "This spec has grown well past the original ask and nobody has examined whether that scope is justified."
  expect_activate: yes

- prompt: "I don't want a pile of opinions dumped at the end — give me decisions on this design doc that I can sign off or reject."
  expect_activate: yes

- prompt: "The last pass over this codebase raised six issues and four of them weren't real. I need findings gated on quoted evidence this time."
  expect_activate: yes

- prompt: "The design is written up but nobody has put a single alternative next to it. Can we fix that before it goes to implementation?"
  expect_activate: yes

- prompt: "is this plan even the right thing to build or too big"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I wrote up a plan in docs/plan-cache-layer.md for adding Redis caching to our product search endpoint. Before I start coding, can you poke at it? I want to know if caching is even the right fix for the slowness, what else we could do, and whether I'm trying to do too much in one PR."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before my team starts on the plan to rewrite the billing module in Go, sanity check it with me. Is the rewrite targeting the actual pain (the slow invoice generation), what options besides a rewrite exist, and are we bundling too many things?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Here's my implementation plan for migrating our auth from session cookies to JWTs (pasted below). Please review it before I write any code: are we solving the real problem, are there simpler alternatives, and is the scope too big or too small?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We're about to build a custom job queue for our email sending. Plan is in PLAN.md. Can you challenge it? I'd like to hear whether we should just use an existing tool, and whether the scope is sensible for a first milestone."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I drafted a 6-step plan to add multi-tenant support to our app. Nothing is coded yet. Can you critique it from the top: is multi-tenancy the right problem given what customers asked for, what are the alternatives, and should we cut scope for v1?"
  expect_activate: yes
  tags: [generated, gen:claude]

## Negative (should not activate)
- prompt: "The change is already written. Tell me whether the diff is correct."
  expect_activate: no

- prompt: "I don't know what we should build yet — help me think through the options."
  expect_activate: no

- prompt: "The plan is to bump the request timeout from 30s to 60s in the config file."
  expect_activate: no

- prompt: "The architect made the call and it's final. Just implement it as written."
  expect_activate: no

- prompt: "Now that the plan in PLAN.md is approved, please implement step 1: add the Redis client wrapper and the cache get/set helpers."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a step-by-step implementation plan for adding CSV export to the reports page. I haven't planned anything yet."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you proofread my implementation plan for typos and clean up the formatting of the headings and bullet lists? Don't change the content."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Compare Redis and Memcached for caching, with pros and cons of each in terms of performance and operational cost."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]
