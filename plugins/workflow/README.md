# workflow

Skills for managing work in a GitHub repo from a coding-agent session. Each skill reads the repo's own conventions (remote, labels, ADR folder, verify commands) before it acts, so the same skill works in any repo.

## Skills

| Skill | Command | Use when |
| :- | :- | :- |
| `epics` | `/workflow:epics` | "What epics are open?", "Which are almost done?", "Finish or start next?" |
| `roundup` | `/workflow:roundup` | "Review open PRs", "What's in flight?", "Plan attack on the backlog" |

### roundup

Gathers open PRs, open issues, and agent sessions on every available backend into one graph of which PR closes which issue and which session owns which PR. It then proposes one plan with two verbs: **land** in-flight work (merge, close, relabel, stop orphaned sessions) and **launch** new work (a cloud session, local delivery, or a read-only scoping subagent per issue). It reads the repo's default branch, merge setup (merge queue, auto-merge, or direct), and deployment health signal instead of assuming them. A failed default-branch run pauses new launches. It is read-only until you approve, and after approval it submits and launches once and returns without polling CI.

### epics

Boards every open epic, both labeled `epic` and epic-sized work without the label, and sorts each into occupied, close, finish, underway, blocked, start, or park. It recommends at most three next actions, with leftover children of an underway epic ranked ahead of new epics. It is read-only until you pick an option. Then it can write copy-paste first messages for new sessions, one per chosen epic.

To check whether an epic is already in progress elsewhere, and to launch new sessions from the briefs, the skill first detects which agent backends the session can use: Devin through its MCP server, Claude Code cloud sessions, or a local subagent. It uses only those that pass a read check. Nothing launches without your approval, and copy-paste briefs are always offered. The detection rules and per-backend calls are in `references/BACKENDS.md` inside each skill. `roundup` uses the same detection for finding sessions to reconcile, launching new work, and stopping orphaned sessions.

Requirements: GitHub access through the GitHub MCP server or the `gh` CLI. The default labels are `epic`, `ready-for-agent`, and `ready-for-human`. If the repo uses other names, the skill maps them and says which mapping it used.

## Install

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install workflow@sethtjf
```

**Skill only:** copy `skills/epics/` or `skills/roundup/` into `~/.claude/skills/`, `.claude/skills/`, or any agent that supports the [Agent Skills](https://agentskills.io/specification) format. Outside the plugin they run as `/epics` and `/roundup`.
