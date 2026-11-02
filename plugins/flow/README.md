# flow

The domain-neutral skills Seth uses in every session, whether in the code domain (Claude Code, alongside the [`code`](../code) plugin and [pstack](https://github.com/cursor/plugins/tree/main/pstack)) or the work domain (alongside the `work` plugin). Install it next to whichever domain plugin the harness is for.

## Skills

| Phase | Skill | Command | Use when |
| :- | :- | :- | :- |
| Frame | `ambition` | `/flow:ambition` | "Make this more ambitious", "What would a world-class version look like?" |
| Frame | `decide` | `/flow:decide` | "Clear the open questions" in a spec, plan, or PR |
| Write | `style` | `/flow:style` | Writing or reviewing prose in Seth's style |
| Reflect | `introspect` | `/flow:introspect` | "Look back over my sessions", a retrospective |

Triage and delivery are domain-specific and live in the domain plugins: `/code:roundup`, `/code:epics`, and `/code:deliver` for code.

### Frame

**`ambition`** restates the literal ask, climbs the outcome ladder (understand, decide, replace the process), answers the depth questions (expert gap, rawest input, real instruments, outside judge), and assembles a crew of disciplines with methods, not personas. It returns one rewritten prompt, what the bigger version gives up, and the access it still needs, then asks which version to run. Based on Felix Rieseberg, ["How to be more ambitious: A tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (13 Oct 2026). It skips the speed axis by default; edit its axes table to change that.

**`decide`** turns a set of open questions into recorded decisions. It answers what the evidence settles, defaults what does not matter, asks the rest through the ask-user tool with one recommended option each, and ends with a table of every question, its resolution, and whether the answer came from you, the code, or a default. In Claude Code it asks through `AskUserQuestion`, up to 4 independent questions per call; with no multiple-choice tool it writes numbered options with the recommended one first. It applies rule 4 of `style`, so change both together.

### Write

**`style`** holds Seth's 30 writing rules (response format, punctuation, voice, structure, precision, code, pushback) and a draft-review procedure that lists each change by rule number. The same rules run as an always-on claude.ai personal preference; the skill is for agents that load skills. Rule 15 names the reader's field (legal technology). Rule numbers are referenced by the review procedure, so renumber both together. Where pstack's `unslop` or `technical-writing` conflict with it, `style` wins.

### Reflect

**`introspect`** finds your history (past-chat tools, Claude Code cloud sessions, a claude.ai export, or local transcripts), shows 6 to 10 patterns with counts and quotes, and runs 3 to 5 interview rounds until you agree with a one-sentence target. It then extracts principles, a problem list, or a written retrospective. History sources are listed in priority order in its Step 1. Unlike pstack's `/reflect`, which tunes the agent, it is about you.

`ambition` and `introspect` started as claude.ai account skills (`ambition-pass` and `introspect`); keep both copies in sync.

## Install

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install flow@sethtjf
```

**Skill only:** copy any `skills/<skill>/` folder into `~/.claude/skills/`, `.claude/skills/`, or any agent that supports the [Agent Skills](https://agentskills.io/specification) format. Outside the plugin it runs as `/<skill>`, so rename the folder and the `name` in `SKILL.md` if that clashes with another skill.
