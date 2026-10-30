# writing

This plugin carries Seth's writing style as two skills. `style` holds 30 rules covering response format, punctuation, voice, structure, precision, code references, and pushback. Claude loads it when writing or editing prose, and it can review an existing draft and list each change by rule number. `open-questions` applies rule 4 to a whole set of open questions: it answers what the evidence settles, defaults what does not matter, asks the rest through the ask-user tool with one recommended option each, and records the decisions.

The same rules also run as an always-on claude.ai personal preference. The skill is for Claude Code and other agents that load skills rather than account preferences.

## Contents

```
writing/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── style/
    │   └── SKILL.md            # the 30 rules plus a draft-review procedure
    └── open-questions/
        └── SKILL.md            # collect, triage, ask, and record open questions
```

## Install

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install writing@sethtjf
```

**Skill only:** copy `skills/style/` or `skills/open-questions/` into `~/.claude/skills/`. Outside the plugin they run as `/style` and `/open-questions`, so rename the folder and the `name` in `SKILL.md` if that clashes with another skill.

## Use

Ask Claude to write or edit something in your style, or to review a draft ("check this against my writing rules"). Invoke it directly with `/writing:style`.

Ask Claude to "clear the open questions" in a spec, plan, or PR, or invoke `/writing:open-questions`. In Claude Code it asks through `AskUserQuestion`, up to 4 independent questions per call. In apps with a different multiple-choice tool it uses that tool, and with no tool it writes numbered options with the recommended one first. It ends with a table of every question, its resolution, and whether the answer came from you, the code, or a default.

## Customizing

Rule 15 names the reader's field (legal technology). Change it if you use the skill for other audiences. Rule numbers are referenced by the review procedure, so renumber both together.
