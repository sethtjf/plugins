# Shared skills

These three skills are domain-neutral, so both the [`code`](../plugins/code) and [`work`](../plugins/work) plugins ship them. This folder is the only copy to edit. After an edit, run `scripts/sync-shared.sh` to copy each skill into both plugins; `scripts/validate.sh` fails if a plugin's copy differs from the source here.

| Skill | In code | In work | Use when |
| :- | :- | :- | :- |
| `ambition` | `/code:ambition` | `/work:ambition` | "Make this more ambitious", "What would a world-class version look like?" |
| `decide` | `/code:decide` | `/work:decide` | "Clear the open questions" in a spec, plan, or PR |
| `style` | `/code:style` | `/work:style` | Writing or reviewing prose in Seth's style |

With both plugins installed, each skill appears twice, once per namespace. The copies are identical, so either command does the same thing.

### Frame

**`ambition`** restates the literal ask, climbs the outcome ladder (understand, decide, replace the process), answers the depth questions (expert gap, rawest input, real instruments, outside judge), and assembles a crew of disciplines with methods, not personas. It returns one rewritten prompt, what the bigger version gives up, and the access it still needs, then asks which version to run. Based on Felix Rieseberg, ["How to be more ambitious: A tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (13 Oct 2026). It skips the speed axis by default; edit its axes table to change that.

**`decide`** turns a set of open questions into recorded decisions. It answers what the evidence settles, defaults what does not matter, asks the rest through the ask-user tool with one recommended option each, and ends with a table of every question, its resolution, and whether the answer came from you, the code, or a default. In Claude Code it asks through `AskUserQuestion`, up to 4 independent questions per call; with no multiple-choice tool it writes numbered options with the recommended one first. It applies rule 4 of `style`, so change both together.

### Write

**`style`** holds Seth's 30 writing rules (response format, punctuation, voice, structure, precision, code, pushback) and a draft-review procedure that lists each change by rule number. The same rules run as an always-on claude.ai personal preference; the skill is for agents that load skills. Rule 15 names the reader's field (legal technology). Rule numbers are referenced by the review procedure, so renumber both together. Where pstack's `unslop` or `technical-writing` conflict with it, `style` wins.

`ambition` started as the claude.ai account skill `ambition-pass`; keep both copies in sync. `introspect` moved to the [`reflect`](../plugins/reflect) plugin.
