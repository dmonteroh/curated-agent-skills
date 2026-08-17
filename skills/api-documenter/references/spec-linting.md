# Spec Linting Reference

Turns "the spec was reviewed" into a check that can fail. A linting ruleset runs over the spec document, applies a published base ruleset plus the house rules written here, and exits non-zero when a rule at error severity is violated — so a spec that drifts from the house conventions cannot merge quietly.

The rule schema shown is Stoplight Spectral's (`.spectral.yaml`), and `casing` and `pattern` are its built-in functions. The three-part shape — a selector, an assertion, a severity — carries over to any linter that selects nodes out of the spec document.

## Ruleset shape

```yaml
extends: ["spectral:oas"]

rules:
  # Contract completeness — inherited rules, raised to failing severity.
  operation-operationId: error
  operation-security-defined: error
  operation-success-response: error
  info-description: error
  operation-description: warn

  # House conventions — rules the base ruleset does not carry.
  path-params-snake-case:
    description: Path parameters should be snake_case
    severity: warn
    given: "$.paths[*].parameters[?(@.in == 'path')].name"
    then:
      function: pattern
      functionOptions:
        match: "^[a-z][a-z0-9_]*$"

  schema-properties-camel-case:
    description: Schema properties should be camelCase
    severity: warn
    given: "$.components.schemas[*].properties[*]~"
    then:
      function: casing
      functionOptions:
        type: camel
```

## Writing a custom rule

A rule is three decisions:

- **`given` — the JSONPath expression selecting the nodes the rule judges.** Selecting the wrong node set is the usual cause of a rule that appears to pass because it matched nothing. Note the difference between the two selectors above: `$.paths[*].parameters[?(@.in == 'path')].name` filters path parameters and selects their `name` *values*, while the trailing `~` in `$.components.schemas[*].properties[*]~` selects property *keys* rather than the schema objects underneath them. A rule that means to judge names but selects objects will never fire.
- **`then.function` plus `functionOptions` — the assertion.** `casing` takes a `type` (`camel`, `pascal`, `kebab`, `snake`, `macro`) and is the right choice for naming conventions, because it encodes the convention by name instead of by regex. `pattern` takes `match` or `notMatch` and covers everything a casing type cannot express: required prefixes, forbidden words, version segments in paths.
- **`severity` — whether a violation stops the pipeline.** Only `error` fails the run; `warn`, `info`, and `hint` report and pass.

Which severity a rule gets is a chosen default, not a derived one: contract-completeness rules (an operation with no `operationId`, no declared security, or no success response) at `error`, because they break generated SDKs and mislead integrators; house naming conventions at `warn` until the existing spec is clean, then raised. Introducing a naming rule at `error` against a spec that already violates it in fifty places produces a red pipeline nobody can fix that day, and the rule gets deleted rather than satisfied.

## Rules worth having before any house rule

- **`operationId` on every operation.** SDK generators derive method names from it; without it, generated method names churn on every regeneration and every consumer's call sites break.
- **Security declared per operation.** Otherwise an endpoint documented in prose as protected carries no machine-readable statement of that, and the generated client sends no credential.
- **At least one success response per operation.** An operation with only error responses documents no contract at all.
- **Descriptions present** on the spec itself and on each operation — the field most often left as generator boilerplate.

## Verifying a rule

Run the linter over a spec that is known to violate the new rule and confirm both a non-zero exit and the rule's own name in the output. A ruleset that has never failed has not been tested, and a rule whose `given` matches nothing is indistinguishable from a rule that passes.

If the linter is not available in the environment, say so, fall back to a manual pass against the same rule list, and report the spec as manually reviewed — never as linted.

## A second gate: media-type allowlisting

Where the toolchain runs a second linter over the same spec (Redocly's `redocly.yaml` is one), the non-overlapping check worth configuring there is a media-type allowlist: enumerate the request and response media types the API actually serves, so an operation that quietly documents `text/plain` or a stale vendor type fails the lint instead of reaching a consumer. Pair it with invalid-example detection, which validates the examples embedded in the spec against their own schemas.
