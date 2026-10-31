# thinking

This plugin holds two skills about how to approach work rather than how to deliver it. `ambition` takes a task as stated and returns a more ambitious version before any work starts. `introspect` reviews your own history with Claude and interviews you until you can say what you want from it, then extracts it.

Both started as claude.ai account skills (`ambition-pass` and `introspect`). The plugin copies apply the [`writing`](../writing) style rules, ask questions through the multiple-choice tool with a recommended option, and let `introspect` read Claude Code cloud sessions.

## Contents

```
thinking/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── ambition/
    │   └── SKILL.md            # altitude, depth, and range rework of a task
    └── introspect/
        └── SKILL.md            # history review, mirror interview, extraction
```

## Install

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install thinking@sethtjf
```

**Skill only:** copy `skills/ambition/` or `skills/introspect/` into `~/.claude/skills/`. Outside the plugin they run as `/ambition` and `/introspect`.

## Use

**`/thinking:ambition`**: hand it a task or prompt, or say "make this more ambitious". It restates the literal ask, climbs the outcome ladder (understand, decide, replace the process), answers the depth questions (expert gap, rawest input, real instruments, outside judge), and assembles a crew of disciplines with methods, not personas. It returns one rewritten prompt, what the bigger version gives up, and the access it still needs, then asks which version to run. Based on Felix Rieseberg, ["How to be more ambitious: A tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (13 Oct 2026).

**`/thinking:introspect`**: ask to look back over your chats or sessions, or to run a retrospective. It finds your history (past-chat tools, Claude Code cloud sessions, a claude.ai export, or local transcripts), shows 6 to 10 patterns with counts and quotes, and runs 3 to 5 interview rounds until you agree with a one-sentence target. It confirms the target, then extracts principles, a problem list, or a written retrospective.

## Customizing

`introspect` lists history sources in priority order in Step 1. Add or reorder sources there. `ambition` skips the speed axis by default; edit the axes table to change which axes it considers.
