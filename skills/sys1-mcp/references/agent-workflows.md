# System One agent workflows

Read this when an agent needs to select tests, check task completion, consider a cached answer, or trim a handoff brief. These tools compose the existing `sys1_ask` and `sys1_classify` decisions on the backend's `trace` model (`typed-decisions` on Laya). They add no HTTP endpoint: MCP clients call the tool name, and HTTP clients POST `{"tool": "...", "arguments": {...}}` to `/predict` ([daemon.py](../../../sys1-mcp/src/sys1_mcp/daemon.py)). A single `sys1_ask` also has its own System One route, `POST /v1/systemone`.

The workflows began as proposals in [the expansion note](../../../temp/expansion/laya-agent-use-cases.md). Jev examples suggest the architecture. They do not calibrate this deployment's model. Treat returned probabilities as measurements to evaluate, not as portable confidence thresholds. Each response names the serving checkpoint when it made a model call.

## Change-aware E2E selection

`sys1_select_tests(diff_chunks, tests, changed_files?, threshold?)` accepts 1–8 nonempty diff chunks and up to 128 discovered tests. A test has `id`, `path`, `title`, and optional `description`. Use a stable Playwright test ID or title-path pair. The tool asks the same relevance question for each test against each chunk, then keeps the highest score per test. `changed_files` should contain repo-relative paths. A directly changed spec always stays in `run_ids`.

Without `threshold`, `mode` is `full_suite`, `run_ids` contains every test, and `ranked_ids` and `scores` show what the model would prioritize. This observation mode is the starting point. With a caller-calibrated threshold, `mode: selected` permits a subset. Model errors, truncated input, oversized batches, or zero selected tests return the full suite with a reason. The tool only selects test IDs. Playwright runs the tests and supplies the actual result.

```json
{"tool":"sys1_select_tests","arguments":{"diff_chunks":["src/billing.ts changes how duplicate charges are displayed"],"tests":[{"id":"billing:duplicate","path":"tests/billing.spec.ts","title":"shows a duplicate charge"},{"id":"search:basic","path":"tests/search.spec.ts","title":"searches products"}],"changed_files":["src/billing.ts"]}}
```

Record the ranking beside full-suite outcomes over a history of changes. Label any test that failed or was changed because of a commit as affected, then measure missed affected tests and runtime at candidate thresholds. Supply a threshold only after a held-out history supports the desired miss rate. This follows [jev-playwright](https://github.com/arthurfiorette/jev-playwright), including its warning about silent zero-test success.

## Postcondition evidence

`sys1_verify_outcome(goal, tool_result, evidence, checks?)` takes the requested outcome, the tool's claim or receipt, and independent observation after the operation. `checks` is a list of `{name, passed}` exact checks. Any failed check returns `status: contradicted` without a model call. Empty evidence returns `needs_evidence`. A full model call returns `status: observation`, a `suggested` label among supported, pending, contradicted, and unknown, and the whole probability distribution. Truncation or model failure returns `inconclusive`.

Keep identifiers, file existence, API state, and permissions as exact checks. A `supported` suggestion helps ask whether the evidence matches the goal. It is not proof that an operation succeeded. For example, a queued-job receipt belongs in `tool_result`, while a subsequent read of the finished report belongs in `evidence`. This adapts the semantic postcondition and evidence examples in [Jev by Example](https://github.com/ReallyArtificial/jev-by-example).

## Cache reuse boundary

`sys1_cache_fit(new_request, cached_request, cached_answer, new_scope, cached_scope, expires_at, reuse_threshold?)` compares the two nonempty scope dictionaries exactly before any model call. Put tenant, account, date range, filters, and other isolation keys there. `expires_at` is an ISO 8601 timestamp with timezone. A scope difference or elapsed expiry returns `action: recompute`, `model_called: false`.

When exact checks pass, the model ranks same, different, and uncertain intent and qualifiers. Without a caller-calibrated `reuse_threshold`, the tool still returns `recompute`. Use its scores for observation. With a threshold, it returns `reuse` only when the same option wins, its probability reaches the threshold, and no input was truncated. A failed model call also recomputes. The caller owns the cache key, actual expiry policy, and recomputation. The [Jev by Example cache case](https://github.com/ReallyArtificial/jev-by-example) motivates near-duplicate pairs whose scope changes.

## Context packing

`sys1_pack_context(task, candidates, pinned_ids, budget_tokens, novelty_threshold?)` accepts 1–32 candidates as `{id, text, tokens}`. Count `tokens` with the target agent's tokenizer before calling. The tool enforces a hard sum over those supplied counts. `pinned_ids` names user constraints, prohibitions, unresolved failures, required source locations, and the requested output. The tool rejects a budget smaller than the pinned total rather than dropping one.

The model ranks remaining candidates for task relevance, then compares their novelty against pinned context or the highest-relevance fitting candidate. The ranking uses `relevance × (0.5 + 0.5 × novelty)`. The `0.5` weight is a chosen default, not a calibrated cutoff. The tool adds fitting candidates in that order and drops exact duplicate text. It asks again whether each candidate adds information absent from the context retained so far.

The `selected` result keeps original IDs, text, and counts. `scores` and `skipped` explain the choice. A caller-calibrated `novelty_threshold` may remove low-novelty candidates. Without one, novelty changes order but does not silently discard context. Failed or truncated novelty checks do not exclude a candidate that fits.

Review the result against the full brief on tasks with known required facts. Count lost obligations, missing evidence, and wasted tokens before enabling a novelty threshold. The pinned-obligation rule follows the handoff and log-compaction failures documented by [Jev by Example](https://github.com/ReallyArtificial/jev-by-example) and [jev-agent-kit](https://github.com/walidboulanouar/jev-agent-kit).

## Screening stays separate

Call `sys1_screen` for fetched pages, tool output, or files that might contain instructions aimed at an agent. Its `directed`, `injection`, `sensitive_data`, and `harm` scores answer a different question from these four workflows. None of the workflow tools grants permission for a proposed action or makes untrusted instructions authoritative ([server.py](../../../sys1-mcp/src/sys1_mcp/server.py), `SCREEN_QUESTIONS`).
