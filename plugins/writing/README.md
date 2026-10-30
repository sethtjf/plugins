# writing

This plugin carries Seth's writing style as a skill: 30 rules covering response format, punctuation, voice, structure, precision, code references, and pushback. Claude loads it when writing or editing prose, and it can review an existing draft and list each change by rule number.

The same rules also run as an always-on claude.ai personal preference. The skill is for Claude Code and other agents that load skills rather than account preferences.

## Contents

```
writing/
├── .claude-plugin/plugin.json
├── README.md
└── skills/style/
    └── SKILL.md    # the 30 rules plus a draft-review procedure
```

## Install

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install writing@sethtjf
```

**Skill only:** copy `skills/style/` into `~/.claude/skills/`. Outside the plugin it runs as `/style`, so rename the folder and the `name` in `SKILL.md` if that clashes with another skill.

## Use

Ask Claude to write or edit something in your style, or to review a draft ("check this against my writing rules"). Invoke it directly with `/writing:style`.

## Customizing

Rule 15 names the reader's field (legal technology). Change it if you use the skill for other audiences. Rule numbers are referenced by the review procedure, so renumber both together.
