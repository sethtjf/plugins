# mcp-servers

This plugin grades an MCP server's source code against a 48-check best-practices rubric. It produces a 0–100 score, a letter grade, and a list of specific changes to make, each tied to a file and line. The audit is read-only and never calls the server's tools.

## Contents

```
mcp-servers/
├── .claude-plugin/plugin.json
├── README.md
└── skills/audit/
    ├── SKILL.md                    # procedure, ground rules, scoring summary
    ├── references/
    │   ├── RUBRIC.md               # the 48 checks and their pass criteria
    │   └── OUTPUT.md               # input and output formats and field rules
    ├── scripts/
    │   ├── catalog_metrics.py      # tool-catalog statistics from tools/list output
    │   └── score.py                # validation, scoring, priorities, report assembly
    └── assets/
        ├── rubric.json             # weights, caps, version gates (scoring source of truth)
        └── audit.schema.json       # JSON Schema for mcp-audit.json
```

The folder `skills/audit/` is a complete [Agent Skills](https://agentskills.io/specification) skill by itself. To use it in a tool that supports skills but not plugins, copy that folder on its own.

## Install

**Claude Code, from the `flow` marketplace:**

```bash
claude plugin marketplace add sethtjf/flow
```

```bash
claude plugin install mcp-servers@flow
```

On Claude Code 2.1.275 or later, one command inside a session does both:

```
/plugin install mcp-servers --marketplace sethtjf/flow
```

**Claude Code, a single session** from a clone of `sethtjf/flow`:

```bash
claude --plugin-dir ./plugins/mcp-servers
```

**Skill only:** copy `skills/audit/` into `~/.claude/skills/` (all projects), `.claude/skills/` (one repo), or the skills directory of any agent that supports the Agent Skills format. Outside the plugin it runs as `/audit`, so rename the folder and the `name` in `SKILL.md` if that clashes with another skill.

## Use

Ask for an audit in natural language ("audit this MCP server", "grade the server in `packages/mcp`"), or invoke the skill directly with `/mcp-servers:audit [path]`.

Outputs go to `mcp-audit/` at the root of the audited code:

| File | Purpose |
|---|---|
| `mcp-audit.md` | Human-readable report: summary, scorecard, changes, metrics, method, open questions |
| `mcp-audit.json` | Machine-readable score and change list, matching `assets/audit.schema.json` |
| `tools.json`, `metrics.json` | Extracted catalog and its statistics |
| `checks.json`, `changes.json` | The agent's per-check results and proposed changes, which feed `score.py` |

## Requirements

- `python3` 3.9 or later. The scripts use only the standard library.
- Optional: Node.js, so `npx @modelcontextprotocol/inspector --cli` can extract the live tool list from stdio servers.

## Scoring

The 11 category weights sum to 100. Checks that don't apply (`na`) drop out, and their weight is redistributed. Checks that require a newer protocol version than the server targets become zero-weight advisories. Five cap conditions limit the score to 69 regardless of everything else:

- an invalid input schema
- a tool that writes but claims to be read-only
- a tool list that changes per connection
- missing token audience validation
- token passthrough

Grades: A 90–100, B 80–89, C 70–79, D 60–69, F below 60.

`score.py` does all of the arithmetic, so the same inputs always produce the same score. It also assigns priorities (P0, P1, P2) and an upper-bound `score_delta` to each change.

## Running the scripts by hand

```bash
python3 -I skills/audit/scripts/catalog_metrics.py mcp-audit/tools.json --out mcp-audit/metrics.json
python3 -I skills/audit/scripts/score.py mcp-audit
```

`score.py` exits 1 and lists every problem if `checks.json` or `changes.json` is incomplete or inconsistent.

## Customizing

- **Weights and caps:** edit `assets/rubric.json`, and keep `references/RUBRIC.md` in step with it.
- **Thresholds:** the per-tool pass and partial cutoffs are in `rubric.json`. The near-duplicate threshold (`NEAR_DUP_THRESHOLD`) and the token heuristics are in `catalog_metrics.py` and `RUBRIC.md`.
- **Versioning:** bump `rubric_version` whenever you change weights or checks, so you can tell which rubric produced an old audit.
