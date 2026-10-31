---
name: ambition
description: Rework a task or prompt to be more ambitious along altitude, depth, and range before doing it. Use when asked to make work more ambitious, go deeper, raise the bar, or say what a world-class version would look like.
---

# Ambition pass

This skill takes a task as stated and produces a more ambitious version of it before any work starts. It is based on Felix Rieseberg, "How to be more ambitious: A tutorial for humans with models" (13 Oct 2026, https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/).

The premise: model capability is uneven, and the limiting factor is usually the scope and method the human asks for, not what the model can do. Most requests ask for the literal artifact (a deck, a fix, a report). The ambitious version asks for the outcome the artifact serves, done with expert methods, informed by fields the task does not obviously touch.

## When to use

- The user says "make this more ambitious", "go deeper", "raise the bar", "what would a world-class version look like", or invokes this skill by name (`/thinking:ambition`).
- The user hands over a substantial task and asks how to approach it.

Do not run it unprompted on small, well-scoped requests. A one-line email edit does not need an ambition pass.

## The four axes

| Axis | Question | Use when |
|---|---|---|
| Speed | Same work, less time? | Default. Skip it here. It needs no reframing. |
| Altitude | What outcome is this task in service of? | The work feeds a decision, a recurring process, or a meeting. Weak fit for creative work. |
| Depth | How would the best practitioner in the field do this? | Quality and correctness matter more than coverage. |
| Range | Which other fields have methods that apply? | The problem is novel, stuck, or the output must persuade or delight. |

Pick the axes that fit. Not every task needs all three.

## Procedure

### 1. Restate the literal ask and its deliverable

One line: what was asked for, and what artifact it produces.

### 2. Altitude: climb the outcome ladder

Ask "what is supposed to happen after this is delivered?" and repeat. Write a ladder of three rungs, each a concrete prompt:

1. **Understand.** Replace "update the artifact" with "explain what changed, why, and what to do about it", fed with as much raw context as can be obtained.
2. **Decide.** Identify the few decisions the artifact exists to support, rank them by urgency, and draft options with arguments for and against each.
3. **Replace the process.** State the purpose the recurring artifact or process serves. Design a better mechanism for that purpose, backtest it against history to show it would have caught things earlier, and propose running it in parallel with the existing process for one cycle.

Signals altitude fits: there will be meetings about this work, or the same task keeps recurring.

Then list the **enablers** the higher rung needs to run without a human feeding it task after task: data access (connectors, logs, exports), mappings between systems (e.g. release version to commit), and environments to reproduce and verify results. Missing enablers are often the real first task.

### 3. Depth: do what the expert does, not what the expert sounds like

Work through these and write the specific answer for this task, not a generic one:

- **Expert gap.** What would a top practitioner do here that the user did not ask for?
- **Rawest input.** What is the least-processed source they would start from, instead of the summary or dashboard already in hand?
- **Instruments.** Which methods and tools would they use? Insist on the real instruments (a database, a statistical model, a profiler, a test harness), not the same old output in professional vocabulary. If a markdown table appears where a model or query belongs, that is the failure mode.
- **Unreasonable target.** Set a target well past the stated one (e.g. 200ms instead of 5s). Treat it as achievable. If progress stalls, keep going rather than declaring it impossible.
- **Challenge a belief.** Name one thing the user or organization takes as true. Try to reproduce it from raw data, adversarially.
- **New knowledge.** Once inside the data, look for something not yet known: a leading signal, a hidden segment, a causal driver. Validate it on held-out data.
- **Outside judge.** Name what, other than the model or the user, will show the result is right: a test suite, a benchmark, a backtest, a reproduction on a clean machine, a domain expert. Do not let the model grade its own work. Prefer a judge the model can run itself for fast feedback.

The guiding constraint is deeper, not bigger. More pages or more features is not depth.

### 4. Range: assemble the crew

1. **Nouns to verbs.** Rewrite the deliverable as what it has to accomplish. "A deck" becomes "get busy people to believe a cause-and-effect story and decide under uncertainty in 30 minutes." The verbs reveal which fields are relevant. (Technique from Tom Kelley and Jonathan Littman, *The Art of Innovation*.)
2. **Pick the crew.** Assume the stakes are absurdly high. Name 4 to 7 disciplines a team would recruit, including at least one adversarial seat (short seller, forensic accountant, penetration tester, opposing counsel, peer reviewer).
3. **Translate each seat into methods.** For each discipline, write what it would *do*: the research step, the tool, the check. Never what it would *sound like*. "Write like a short seller" is role play and adds nothing. "Do the short seller's diligence: find the claim most likely to be false and try to falsify it" is range.

When subagents are available, each seat can run as its own parallel workstream with a defined input and output.

### 5. Check preconditions

Ambitious work needs a computer that can install software, and access to the relevant data. List what is available in this session and what is missing (connectors, credentials, files, compute). Say plainly which parts of the plan are blocked until a missing piece exists.

### 6. Deliver

Output, in this order:

1. **Literal ask** (one line).
2. **Recommended version**: a single rewritten prompt that combines the chosen axes, ready to execute.
3. **Ladder and options**: the altitude rungs, depth answers, and range crew, compact, so the user can dial ambition up or down.
4. **What it gives up**: cost, time, risk, or scope creep the ambitious version introduces versus the literal ask.
5. **Preconditions**: enablers and missing access.

Then ask which version to run through the ask-user tool (`AskUserQuestion` in Claude Code, or the app's multiple-choice equivalent): offer the literal ask, the recommended version, and one step up or down the ladder, with the recommended version marked and a one-line reason. With no such tool, list numbered options with the recommended one first. Skip the question if the user already said to proceed, and run the recommended version.

## Failure modes

- **Role play instead of method.** Personas change tone, not results. Every seat and every "expert" must map to an action or instrument.
- **Bigger instead of deeper.** Expanding scope without changing method or inputs is not ambition.
- **Self-grading.** A plan without an external check is not finished.
- **Altitude on creative work.** Outcome-laddering a poem or a design exploration usually flattens it. Use range instead.
- **Ignoring enablers.** A higher-altitude plan that still needs a human to paste in data every week has not moved up.
- **Premature "impossible".** If the model says a target cannot be met, require evidence of the specific blocker before accepting it.

## Prompt template for depth

Use this (wording is this skill's, not the article's) when the user wants a deeper version of a specific prompt:

```text
I want this task done deeper, not larger. Before doing it:
1. What would the best practitioner in this field do here that I have not asked for?
2. What is the least-processed source material they would start from, in place of what I gave you?
3. Which specific methods and tools would they use?
4. What, other than you or me, would confirm the result is correct?
Then rewrite my request to ask for exactly that.
```