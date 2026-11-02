# Audit Inputs and Outputs

The audit writes three input files into the audit directory (`mcp-audit/` by default). `scripts/score.py` validates them, computes the score, assigns priorities and IDs, and assembles the outputs. Don't hand-compute scores, priorities, or `score_delta`.

## Input: `checks.json`

Write one entry for every check in `references/RUBRIC.md`, 48 in total. A missing check fails validation.

```json
{
  "server": {
    "name": "acme-mcp",
    "path": "packages/mcp-server",
    "language": "TypeScript",
    "sdk": "@modelcontextprotocol/sdk",
    "sdk_version": "1.x.y",
    "transports": ["stdio", "streamable-http"],
    "protocol_version": "2026-07-28",
    "extraction": "runtime",
    "catalogs": ["tools.json"]
  },
  "checks": [
    {
      "id": "DSC-1",
      "result": "partial",
      "score": 0.72,
      "confidence": "verified",
      "note": "13 of 18 tools lead with API terms, e.g. contacts_update: 'PATCH /contacts/{id}'"
    },
    {
      "id": "ANN-1",
      "result": "fail",
      "score": 0.4,
      "confidence": "static",
      "note": "email_send claims readOnlyHint: true (src/tools/email.ts:31); 10 tools set no readOnlyHint",
      "cap_triggered": true
    },
    {
      "id": "AUTH-1",
      "result": "na",
      "note": "stdio-only server"
    }
  ]
}
```

Field rules:

- `server.protocol_version` is `YYYY-MM-DD`, or `null` if it can't be determined. If it's `null`, every version-gated check becomes advisory.
- `result` is one of `pass`, `partial`, `fail`, `na`, or `advisory`. Use `na` only when the check can't apply. `score.py` sets `advisory` itself for version-gated checks. You may also set it by hand for a check that is out of scope for this server, with a reason in `note`.
- `score` is required for per-tool checks. It is the fraction of tools that pass, from 0.0 to 1.0, and `score.py` derives `result` from it using the thresholds in `assets/rubric.json`. For server-wide checks, `score` is optional and only refines a `partial`.
- `confidence` is `verified` (observed at runtime, or unambiguous in code) or `static` (inferred from code you couldn't exercise). It's required unless the result is `na`.
- `note` is a single line of evidence or reason, and it's required.
- `cap_triggered` goes only on CAP checks, and only when the cap condition is met. It can be true even on a per-tool check that otherwise scores well, for example when one tool lies about `readOnlyHint`.
- `spec_violation` is set when the failure breaks a MUST or MUST NOT in the targeted spec version. It makes any change that addresses the check P0.

## Input: `changes.json`

This is a JSON array. Every check that comes out `partial` or `fail`, and every check with `cap_triggered` or `spec_violation`, must be covered by at least one change. Group changes that share a root cause.

```json
[
  {
    "title": "Mark email_send as a write and set destructive hints",
    "check_ids": ["ANN-1", "ANN-2"],
    "tools": ["email_send"],
    "locations": [{ "file": "src/tools/email.ts", "line": 31 }],
    "evidence": "annotations: { readOnlyHint: true }",
    "change": "Set readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true on email_send. Sending is a non-idempotent external write.",
    "patch": "--- a/src/tools/email.ts\n+++ b/src/tools/email.ts\n@@ -31 +31 @@\n-  annotations: { readOnlyHint: true },\n+  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },",
    "effort": "S",
    "breaking": false
  }
]
```

Field rules:

- `change` must be specific enough to implement without rereading the rubric. "Improve the description" fails this test. "Replace the description of `contacts_update` with: 'Change fields on an existing contact. Use contacts_upsert when the contact may not exist yet.'" passes.
- `locations` lists at least one `{file, line}`. If something is missing entirely, point at the place where it should be added, such as the registration site.
- Include `patch` (a unified diff) only for small, mechanical edits like an annotation, a description, or a schema field. Leave it out for redesigns.
- Set `breaking: true` for anything that renames, removes, or merges a tool, or that changes required arguments.
- `effort` is `S` (under an hour), `M` (under a day), or `L` (more than a day).
- Don't set `id`, `priority`, `score_delta`, or `clears_caps` yourself. `score.py` assigns them:
  - `priority`: P0 if any referenced check has `cap_triggered` or `spec_violation`. P1 if any referenced check is weight 3 and not passing. Otherwise P2.
  - `score_delta`: the gain in the uncapped score if every check the change references moved to a full pass. It's an upper bound, measured on the uncapped score so that changes can still be ranked while a cap holds the overall score down.
  - `clears_caps`: the triggered caps this change addresses. The cap lifts only once every triggered cap is cleared.
- Within each priority, changes are ordered by whether they clear caps, then by `score_delta`.

## Input: `metrics.json`

This is the output of `scripts/catalog_metrics.py`, and it's optional. If present, it's embedded in the final JSON and summarized in the scorecard.

## Output: `mcp-audit.json`

`score.py` assembles this file from the three inputs. Its shape is defined in `assets/audit.schema.json`. Top-level keys are `rubric_version`, `server`, `score`, `metrics`, and `changes`.

## Output: `mcp-audit.md`

`score.py` writes `scorecard.md`, which contains the Scorecard, Changes, and Catalog metrics sections. Write `mcp-audit.md` around it in this order:

1. **Summary.** One paragraph giving the score, the grade, any cap reasons, and the three changes with the largest `score_delta`.
2. **Scorecard, Changes, Catalog metrics.** Paste the contents of `scorecard.md` verbatim.
3. **Method and limits.** How the catalog was extracted, which checks are `static`, which catalogs (principals or configs) weren't covered, and any tools whose schemas couldn't be resolved.
4. **Open questions.** Design decisions that the code alone can't settle, for example whether two overlapping tools serve different audiences.
