# reflect

Improve your setup over time from your own session history. Where `code` and `work` are for doing a task, `reflect` looks back across many sessions to find what to change in how you work with Claude: skills, style rules, CLAUDE.md, and habits.

## Skills

| Skill | Command | Use when |
| :- | :- | :- |
| `introspect` | `/reflect:introspect` | "Look back over my sessions", "What patterns do you see?", a retrospective |

**`introspect`** finds your history (past-chat tools, Claude Code cloud sessions, a claude.ai export, or local transcripts), shows 6 to 10 patterns with counts and quotes, and runs 3 to 5 interview rounds until you agree with a one-sentence target. It then extracts principles, a problem list, or a written retrospective. History sources are listed in priority order in its Step 1. Unlike pstack's `/reflect`, which tunes the agent, it is about you.

It started as the claude.ai account skill `introspect`; keep both copies in sync.

## Install

```bash
claude plugin install reflect@sethtjf
```

**Skill only:** copy `skills/introspect/` into `~/.claude/skills/`. Outside the plugin it runs as `/introspect`.
