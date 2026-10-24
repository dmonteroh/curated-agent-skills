# Trigger Cases: refactor-clean

## Positive (should activate)
- prompt: "An agent generated a custom date picker and a hand-rolled debounce for us last week. Before I spend time tidying them, should either of them exist at all?"
  expect_activate: yes

- prompt: "Clean up just what my branch touched before I open the PR — same behaviour, nothing outside the diff."
  expect_activate: yes

- prompt: "clean up this messy invoice function without breaking it"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "The order_processing.py module has grown into a 600-line mess with copy-pasted discount logic in five places. Can you refactor it to remove the duplication, one small step at a time, running the existing tests after each step so we know behavior hasn't changed?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I inherited this billing service and the calculate_invoice function has nested ifs about eight levels deep. Please simplify it gradually without changing what it outputs. Add characterization tests first if coverage is thin, then refactor in small commits-sized steps."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Refactor the payment workflow to remove duplicated validation logic, taking small behavior-preserving steps and running the existing tests after each change."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Clean up the repeated permission checks across these modules, keeping the public behavior identical and using tests as a safety net throughout."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Rewrite this parser to be three times faster. I'll benchmark it afterwards and I don't need the output to match what it does today."
  expect_activate: no

- prompt: "Add a new feature to the order_processing module that supports coupon codes stacked with loyalty discounts, including tests."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Please review the UserController class and tell me which parts are duplicated or overly complex. Don't change anything, I just want a written code review."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Rename the variable `d` to `discount` across the whole repo and fix the formatting with prettier."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Redesign the ReportGenerator so it outputs JSON instead of text, and restructure the code however you need to; behavior changes are fine."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Rewrite our Python 2 billing service to Python 3 and update the deprecated library calls."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Investigate why the nightly sync job is timing out in production and fix the performance regression."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Migrate this service from REST to GraphQL and update all client integrations."
  expect_activate: no
  tags: [generated, gen:codex]
