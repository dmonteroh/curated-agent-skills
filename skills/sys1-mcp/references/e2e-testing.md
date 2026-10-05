# System One decisions in browser end-to-end tests

Read this when a browser test needs a semantic decision about visible text or a choice among observed controls. The browser driver owns navigation, input, waits, and evidence collection. The model receives text and typed questions through the local daemon's `/v1/systemone` HTTP route, the same wire contract Jev and Clef use, so a test written against it runs unchanged against any of them. The model is whatever backend the daemon serves (Laya on this host). Sources below were opened on 2026-09-27.

## What the Jev projects actually do

| Primary example | Mechanism | Laya adaptation |
| --- | --- | --- |
| [jev-e2e](https://github.com/perixtar/jev-e2e) | Jev selects from observed controls. Playwright executes actions and checks explicit expectations independently. Results include evidence, and saved controls can replay without a model call. | Send a bounded control list to `/predict`. Map the returned label to a Playwright locator. Keep the assertion independent of the control choice. |
| [jevcumber](https://github.com/RubyBrewsday/jevcumber) | Jev resolves a Gherkin step against actual buttons, fields, links, and step literals. A reviewed lockfile replays resolved steps. Missing controls require a new resolution. | Cache reviewed control IDs or locators per step. Treat a changed mapping as a reviewable test change. |
| [Jev Browser semantic verification](https://github.com/tontoko/jev-browser/blob/main/docs/semantic-verification.md) | A semantic matcher compares fresh locator evidence and reports uncertain or changed evidence. Exact properties use native assertions. | Add a narrow semantic assertion for observed text. Re-read the locator before accepting the decision, and report the text, question, checkpoint, and score on failure. |

These are Jev implementations, not measured Laya results. Their architecture transfers because Laya accepts the same three typed question forms. Their thresholds, label capacity, and accuracy do not transfer. In particular, this server warns that `choice` distributions become sharply overconfident at 11 or more labels ([server.py](../../../sys1-mcp/src/sys1_mcp/server.py)).

## Call the warm daemon from a test

The installed daemon serves `https://localhost:8765` on this host ([README.md](../../../README.md), TLS). Set `SYS1_URL` to its `/v1/systemone` route, or to another System One endpoint your test process can reach. The process must trust that server's certificate. Do not bypass certificate verification.

`POST /v1/systemone` accepts `{"state": ..., "questions": ..., "model": "base"}` and runs `sys1_ask` ([daemon.py](../../../sys1-mcp/src/sys1_mcp/daemon.py), `systemone`). It is plain HTTP JSON, so a Playwright test needs no MCP client. For the other tools, `POST /predict` accepts `{"tool": "sys1_relevant", "arguments": {...}}`.

```ts
import { expect, test } from '@playwright/test';

test('records whether the alert explains the email problem', async ({ page }) => {
  const url = process.env.SYS1_URL;
  if (!url) throw new Error('Set SYS1_URL to the daemon /v1/systemone URL');

  // The browser supplies observed evidence. The model never reads the page itself.
  const alert = page.getByRole('alert');
  await expect(alert).toBeVisible();
  const observed = await alert.innerText();

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      state: observed,
      questions: {
        about_email: {
          type: 'noul',
          instructions: 'Does this alert explain a problem with the email field?',
        },
      },
      model: 'base',
    }),
  });
  if (!response.ok) throw new Error(`/v1/systemone returned HTTP ${response.status}`);
  const result = await response.json();
  if (result.truncation?.truncated !== false || result.truncation?.prefix_truncated) {
    throw new Error('The model did not confirm it read the full assertion input');
  }
  const probability = result.answers?.about_email?.noul;
  if (typeof probability !== 'number') throw new Error('The model returned no noul answer');
  // Playwright records runtime annotations in the test report.
  test.info().annotations.push({
    type: 'sys1-observation',
    description: JSON.stringify({ observed, probability, model: result.model, checkpoint: result.checkpoint }),
  });
});
```

This example records a judgment through [Playwright's runtime annotations](https://playwright.dev/docs/test-annotations). It does not turn the score into a pass. Use test data that may appear in reports and the daemon's call log ([README.md](../../../README.md), Call logging). The existing skill has no threshold fitted to browser assertions, and `noul` can misread some yes/no wording. Compare the answer with known pass, fail, and near-miss cases before choosing a pass threshold. Keep `model` and the exact question fixed once calibrated. A score between accepted pass and fail bands is inconclusive, not success.

For change-aware selection of which Playwright tests to run, call `sys1_select_tests` with the discovered test IDs and diff chunks before starting Playwright. It defaults to a full-suite run while recording relevance scores. Its contract and threshold evaluation are in [agent-workflows.md](agent-workflows.md); semantic assertions inside a running test still use the `/v1/systemone` pattern above.

## Let the model choose a control

Build candidates from the current Playwright page or a scoped region. Give each candidate an ID stable within the observation, role, accessible name, and current state. Put the test step and that candidate table in `state`. Ask one `choice` question with candidate IDs and `none` as the criteria. Keep at most ten labels including `none`, because the Laya backend sharpens distributions at eleven ([server.py](../../../sys1-mcp/src/sys1_mcp/server.py), `_add_margins`). Narrow a crowded page by region or element type before asking. Never silently omit a plausible control.

```json
{
  "state": "Step: Open the billing settings.\nVisible controls in Settings dialog:\nb1 button Billing\nb2 button Notifications\nb3 button Save",
  "questions": {
    "target": {
      "type": "choice",
      "instructions": "Which visible control carries out the step?",
      "criteria": {
        "b1": "Billing button in Settings dialog",
        "b2": "Notifications button in Settings dialog",
        "b3": "Save button in Settings dialog",
        "none": "No listed control carries out the step"
      }
    }
  },
  "model": "base"
}
```

Map `answers.target.choice` to a locator in code. Stop on `none`, missing IDs, truncation, or stale evidence. Treat a small margin as inconclusive until a threshold is fitted. Check that the selected locator is still visible and enabled before Playwright clicks it. Keep action preconditions and outcome assertions in Playwright. Do not use the model's opinion that a flow is complete as the sole completion check.

For repeated tests, store a reviewed step-to-control mapping. Replay it without a model call while the control still matches. If the control disappears, propose a fresh mapping and show the diff for review. This is an adaptation of the lockfile and replay patterns in [jevcumber](https://github.com/RubyBrewsday/jevcumber) and [jev-e2e](https://github.com/perixtar/jev-e2e), not a feature of the current sys1-mcp server.

## Make semantic assertions reliable

Use ordinary Playwright assertions for URL, HTTP status, element presence, values, counts, and exact text. Use the model only for wording whose meaning matters and can vary. Read the target text immediately before the question, then read it again before accepting the verdict. If it changed, mark the result inconclusive and collect a trace.

Create a labeled set with real passing text, broken text, paraphrases, empty evidence, and near misses. Run each candidate question on every served model (on Laya, `base` and `typed-decisions`), and record each returned model, checkpoint, distribution, and truncation report. Choose thresholds from that set, then check them on separate cases. The current server's Playwright assertion quality has not been measured. Its `/v1/systemone` route was verified live on 2026-10-02 against the Laya backend.
