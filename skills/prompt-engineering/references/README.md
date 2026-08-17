# Prompt Engineering References Index

- `references/frontier-model-prompting.md`: Prompting current-generation reasoning models (literal instruction-following, reasoning via configuration with per-provider controls, structured outputs, agentic prompting, migrating prompts between model generations). Read this first when targeting a frontier model.
- `references/prompt-caching-layout.md`: Cache-friendly prompt layout — stability ordering, silent invalidators, verification.
- `references/system-prompts.md`: System prompt structure, section syntax, untrusted-content boundaries, constraint tiers, and testing.

- `references/chain-of-thought-basics.md`: When to use chain-of-thought and core patterns (classic / non-reasoning models).
- `references/chain-of-thought-advanced.md`: Decomposition, verification, and adaptive depth patterns.
- `references/chain-of-thought-templates.md`: Domain templates and evaluation checks.

- `references/few-shot-selection.md`: Example selection strategies and decision points.
- `references/few-shot-construction.md`: Formatting and example construction best practices.
- `references/few-shot-context.md`: Example budget priorities, truncation, and caching trade-offs.

- `references/prompt-optimization-workflow.md`: Baseline setup, grading methods (mechanical, rubric, LLM judge), and the iterative refinement loop.
- `references/prompt-optimization-experiments.md`: A/B testing, metrics, nondeterminism handling, and experiment axes beyond prompt text.
- `references/prompt-optimization-efficiency.md`: Token, latency, and cost reduction tactics.

- `references/eval-coverage.md`: Coverage discipline for LLM-backed units that ship — gate/periodic tiers, a build-checked registry, structural assertions for judgment units, two-directional gates, the model-judge calibration protocol behind them (labelled set, sealed split, separate TPR/TNR, bias correction, advisory-only fallback), aggregation and voting rules (self-consistency), and the result-record shape.
- `references/harness-porting.md`: Porting one authored instruction set to a second agent runtime — the four rewrite classes, registry validation, and tests parameterized over targets.

- `references/prompt-templates-architecture.md`: Template building blocks and modular composition.
- `references/prompt-templates-patterns.md`: Common task templates (classification, extraction, generation, transformation).
- `references/prompt-templates-advanced.md`: Inheritance, validation, caching, and multi-turn patterns.
