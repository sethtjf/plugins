---
name: open-questions
description: Clear a set of open questions by answering what you can yourself and asking the user the rest through the ask-user tool (AskUserQuestion or the app's multiple-choice equivalent), 2-4 options each with one recommended. Use when a spec, plan, PR, or conversation has open questions, TBDs, or unresolved decisions, or when asked to "clear", "resolve", or "walk through" open questions.
---

# Open Questions

Turn a pile of open questions into recorded decisions. Answer what the evidence answers, default what does not matter, and ask the user only the questions whose answer changes the work, each as a multiple-choice question with one recommended option.

## 1. Collect

Gather every open question from the source the user points at, or from the current work if they name none:

- An "Open questions" section in a spec, design doc, or plan.
- `TBD`, `TODO(decide)`, `?`, and "we need to decide" markers in docs or code.
- Unresolved review threads on a PR.
- Questions you or the user raised earlier in the conversation that never got an answer.

Rewrite each one as a single decision ("Which queue backs the export job?"), not a topic ("Queueing"). Split compound questions. Merge duplicates.

## 2. Triage

Sort each question into one of three bins before asking anything:

| Bin | Test | Action |
| :- | :- | :- |
| Answerable | The repo, docs, earlier conversation, or a quick check settles it. | Answer it yourself and cite the file, line, link, or message. |
| Default | A reasonable default exists and either answer leads to the same next step, or the choice is cheap to reverse. | Pick the default and state it as an assumption. |
| Ask | The answer changes what you build, costs real time to reverse, or is a preference only the user holds. | Ask the user (step 4). |

When unsure between Default and Ask, ask if the step cannot be undone, and default otherwise.

## 3. Order

Ask blocking questions first. If one answer would make other questions moot or change their options, ask it alone and wait for the answer before writing the dependent questions. Independent questions can go together.

## 4. Ask

### Pick the tool

Use the first one that exists in the current app:

1. **`AskUserQuestion`** (Claude Code). Each call takes 1 to 4 questions, and each question takes a `question`, a `header` of at most 12 characters, 2 to 4 `options` with a `label` and a `description`, and `multiSelect`. Batch up to 4 independent questions per call. Put the recommended option first and end its label with ` (Recommended)`. The tool adds an "Other" free-text choice itself, so do not add one.
2. **Another multiple-choice decision tool** (for example `request_decision` in Claude projects, which takes one question, 2 to 4 options, a `recommended` index, and a `reason`). Follow its own limits. If it takes one question per call, ask the blocking question first and keep working on the recommended option while you wait, unless that step cannot be undone.
3. **No tool.** Write the questions as text in the fallback format below.

### Write each question

- One decision per question, verb first, in the user's terms rather than code names.
- 2 to 4 options that are mutually exclusive and each a real choice. Do not pad with straw options.
- Each option says what happens if chosen, in one line: "Postgres `LISTEN/NOTIFY`: no new infra, but no retries."
- Exactly one option is recommended, with a one-line reason that names what it gives up.
- Include the evidence the user needs to choose (a number, a file, a constraint) in the question or option text. Do not make them go look.
- Use `multiSelect` only when several options can be true together, such as "Which targets ship in v1?"

### Fallback format

```markdown
**1. Which queue backs the export job?**
1. Postgres `LISTEN/NOTIFY` (recommended): no new infrastructure. Gives up built-in retries.
2. SQS: retries and dead-lettering. Adds an AWS dependency and IAM setup.
3. In-process worker: simplest. Jobs are lost on deploy.

**2. ...**
```

Number questions and options so the user can answer "1.2, 2.1". Put the recommended option first and label it "(recommended)".

## 5. Record

When answers come back:

1. If an answer is "Other" free text, treat it as the decision. If it raises a new question, triage it (step 2) and ask again only if it lands in Ask.
2. Write each decision back to the source. In a doc, move the item from "Open questions" to a "Decisions" list with the answer and the date. In code, replace the `TBD` marker. On a PR, reply to and resolve the thread.
3. Apply the decisions to the work in progress.
4. Report one table covering every question from step 1:

| # | Question | Resolution | Source |
| :- | :- | :- | :- |
| 1 | Which queue backs the export job? | Postgres `LISTEN/NOTIFY` | User |
| 2 | Is the export capped at 10k rows? | Yes, `MAX_EXPORT_ROWS` in `config/export.ts:12` | Answered from code |
| 3 | CSV header casing? | snake_case, matching the import format | Default |

List any question still open below the table with what it is waiting on. If none remain, say so in one sentence.
