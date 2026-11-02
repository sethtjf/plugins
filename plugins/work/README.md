# work

The knowledge-work mirror of the code workflow. Code starts from filed issues, rounds them up, delegates to coding agents, and lands reviewed PRs. Work starts from Slack, email, calendar, and meeting notes, turns them into action items, delegates to cloud sessions or a local worker, and lands outputs only after you sign off.

## Skills

| Skill | Command | Mirrors | Use when |
| :- | :- | :- | :- |
| `intake` | `/work:intake` | filing issues | "What came in?", "What do I owe people?", start of day |
| `roundup` | `/work:roundup` | `roundup` | "What's in flight?", "What should I delegate?" |
| `projects` | `/work:projects` | `epics` | "Which projects are almost done?", "Finish or start next?" |
| `deliver` | `/work:deliver #N` | `deliver` | "Draft this here", roundup's local lane |
| `review` | `/work:review` | PR review and merge | "What's ready to send?", "Sign off" |

The loop: `intake` writes action items to the ledger. `roundup` sorts them into cloud, local, scope, human, and skip lanes and launches approved work. Cloud sessions and `deliver` end by attaching a review packet (the output, its sources, and a check report) to the item. `review` shows each packet, and only on your approval sends the email, posts the Slack reply, or shares the doc. No other skill sends anything.

## Agents

| Agent | Used by | Does |
| :- | :- | :- |
| `worker` | `deliver` | Drafts one output from the sources it is given. Marks anything it cannot source as `[UNSOURCED]`. Never sends. |
| `checker` | `deliver`, `review` | Verifies each claim against its source, plus recipients, attachments, and done-criteria. Reports PASS, FAIL, or UNVERIFIED. Read-only. |

## Setup

1. **Ledger.** Create a private GitHub repo for action items (for example `you/work`). Cloud sessions launch against it. See `skills/*/references/LEDGER.md` for the item shape, labels, and packet format, and for using a Sheet, Slack list, or Markdown file instead.
2. **`WORK.md`** at the ledger root (optional; `intake` offers to write one): your role, clients and teams, channels and email labels to watch or exclude, who may see what, house style per audience, and batch-approval rules.
3. **Connectors.** Slack, Gmail, Google Calendar, Granola, and Google Drive. Each skill checks which ones respond and says when a sweep was partial.

Shared skills from the `flow` plugin (`ambition`, `decide`, `style`, `introspect`) are used when installed. Without `decide`, the skills call the runtime's ask-user tool directly.

## Install

```bash
claude plugin install work@sethtjf
```

**Skill only:** copy any `skills/<name>/` folder into `~/.claude/skills/`. Each carries its own copies of `LEDGER.md`, `SOURCES.md`, and `BACKENDS.md`.
