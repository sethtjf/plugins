# flow

Seth's skills for a working session, ordered the way a session runs: frame the task, triage the repo's work, build, write, and reflect. Building and verifying code is left to [pstack](https://github.com/cursor/plugins/tree/main/pstack), which this plugin is meant to sit beside. `deliver` covers the build step in repos without pstack.

## Skills

| Phase | Skill | Command | Use when |
| :- | :- | :- | :- |
| Frame | `ambition` | `/flow:ambition` | "Make this more ambitious", "What would a world-class version look like?" |
| Frame | `decide` | `/flow:decide` | "Clear the open questions" in a spec, plan, or PR |
| Triage | `roundup` | `/flow:roundup` | "Review open PRs", "What's in flight?", "Plan attack on the backlog" |
| Triage | `epics` | `/flow:epics` | "What epics are open?", "Finish or start next?" |
| Build | `deliver` | `/flow:deliver #N` | "Deliver #42", "Implement this here", roundup's local lane, when pstack is not in use |
| Write | `style` | `/flow:style` | Writing or reviewing prose in Seth's style |
| Reflect | `introspect` | `/flow:introspect` | "Look back over my sessions", a retrospective |

### Frame

**`ambition`** restates the literal ask, climbs the outcome ladder (understand, decide, replace the process), answers the depth questions (expert gap, rawest input, real instruments, outside judge), and assembles a crew of disciplines with methods, not personas. It returns one rewritten prompt, what the bigger version gives up, and the access it still needs, then asks which version to run. Based on Felix Rieseberg, ["How to be more ambitious: A tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (13 Oct 2026). It skips the speed axis by default; edit its axes table to change that.

**`decide`** turns a set of open questions into recorded decisions. It answers what the evidence settles, defaults what does not matter, asks the rest through the ask-user tool with one recommended option each, and ends with a table of every question, its resolution, and whether the answer came from you, the code, or a default. In Claude Code it asks through `AskUserQuestion`, up to 4 independent questions per call; with no multiple-choice tool it writes numbered options with the recommended one first. It applies rule 4 of `style`, so change both together.

### Triage

**`roundup`** gathers open PRs, open issues, and agent sessions on every available backend into one graph of which PR closes which issue and which session owns which PR. It proposes one plan with two verbs: **land** in-flight work (merge, close, relabel, stop orphaned sessions) and **launch** new work (a cloud session, local delivery, or a read-only scoping subagent per issue). It reads the repo's default branch, merge setup, and deployment health signal instead of assuming them, and a failed default-branch run pauses new launches. It is read-only until you approve.

**`epics`** boards every open epic, labeled or not, and sorts each into occupied, close, finish, underway, blocked, start, or park. It recommends at most three next actions, ranking leftover children of an underway epic ahead of new epics, and can write first messages for new sessions.

Both detect which agent backends the session can use (Devin through its MCP server, Claude Code cloud sessions, or a local subagent) and use only those that pass a read check. Detection rules and per-backend calls are in each skill's `references/BACKENDS.md`. Requirements: GitHub access through the GitHub MCP server or the `gh` CLI. Default labels are `epic`, `ready-for-agent`, and `ready-for-human`; other names are mapped and reported.

### Build

**`deliver`** takes one well-scoped item to an open PR in this session. The main session plans and integrates, the `implementer` subagent writes the code, and the `test-runner` subagent runs the repo's own checks without editing. It works on a feature branch, follows the repo's commit and PR conventions, and pushes only after checks pass and you approve. In a repo set up for pstack, use `/poteto-mode` instead.

| Agent | Does |
| :- | :- |
| `implementer` | Writes the code for one delegated chunk and reports files touched and checks run. Stays in scope and never force-pushes or bypasses hooks. |
| `test-runner` | Runs the repo's lint, typecheck, build, and test commands for a scope and reports pass/fail. Read-only. |

Both run on `sonnet`. A repo's own `implementer` or `test-runner` in `.claude/agents/` wins; with neither, `deliver` uses a general-purpose subagent with the same contract.

### Write

**`style`** holds Seth's 30 writing rules (response format, punctuation, voice, structure, precision, code, pushback) and a draft-review procedure that lists each change by rule number. The same rules run as an always-on claude.ai personal preference; the skill is for agents that load skills. Rule 15 names the reader's field (legal technology). Rule numbers are referenced by the review procedure, so renumber both together. Where pstack's `unslop` or `technical-writing` conflict with it, `style` wins.

### Reflect

**`introspect`** finds your history (past-chat tools, Claude Code cloud sessions, a claude.ai export, or local transcripts), shows 6 to 10 patterns with counts and quotes, and runs 3 to 5 interview rounds until you agree with a one-sentence target. It then extracts principles, a problem list, or a written retrospective. History sources are listed in priority order in its Step 1. Unlike pstack's `/reflect`, which tunes the agent, it is about you.

`ambition` and `introspect` started as claude.ai account skills (`ambition-pass` and `introspect`); keep both copies in sync.

## Install

```bash
claude plugin marketplace add sethtjf/flow
```

```bash
claude plugin install flow@flow
```

**Skill only:** copy any `skills/<skill>/` folder into `~/.claude/skills/`, `.claude/skills/`, or any agent that supports the [Agent Skills](https://agentskills.io/specification) format. Outside the plugin it runs as `/<skill>`, so rename the folder and the `name` in `SKILL.md` if that clashes with another skill.
