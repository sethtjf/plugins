---
name: deliver
description: Execute one well-scoped item to completion locally in the main session — plan it, delegate implementation to the `implementer` subagent, verify, commit on a branch, and open a PR. The local counterpart to launching a cloud agent session. Use when the user wants to do a triaged item locally (from roundup's local lane or directly), "deliver #N", "implement this here", or "land this locally".
argument-hint: "Issue #, PR to continue, or a scoped task description"
---

# Deliver

Local delivery loop: **you (the director) plan and integrate; the `implementer`
subagent writes the code.** This is the local mirror of a cloud agent session —
same triaged item, executed here instead of in the cloud, ending in a PR.

You (the main session) should be running a strong planning model. Do NOT write
the implementation yourself — decompose the work and delegate each chunk to the
`implementer` subagent, then review and integrate.

## Subagents

This skill uses two subagents. Resolve each once, in this order:

1. **Plugin or repo agent**: an agent named `implementer` / `test-runner` (the
   `workflow` plugin ships both, listed as `workflow:implementer` and
   `workflow:test-runner`; a repo may define its own in `.claude/agents/`).
   Prefer the repo's own if both exist — it knows the repo's commands.
2. **Fallback**: the runtime's general-purpose subagent, with the contract below
   pasted at the top of its prompt.

- **implementer contract**: you cannot see the director's conversation; work
  only from this prompt and the repo. Implement exactly what is asked — no
  unrelated refactors or renames. If the task is underspecified or wrong, stop
  and report instead of guessing. Follow the repo's `AGENTS.md` / `CLAUDE.md`
  and existing patterns. Never bypass hooks or branch protection, and never run
  destructive operations (force-push, history rewrite, `rm -rf`, dropping data).
  Run the narrowest checks for what you changed. Report: summary, files touched
  (`path:line` for key edits), verification commands and results, and
  follow-ups/blockers.
- **test-runner contract**: verify, never edit. Use the repo's own commands
  (from the prompt, `AGENTS.md` / `CLAUDE.md`, the task runner, or CI
  workflows); do not invent them. Report: commands run, PASS/FAIL per suite with
  counts, each failure's test name, location, and key message, environment
  problems kept apart from real failures, and a suggested cause without fixing.

## Input

One well-scoped item:
- a GitHub issue number (`gh issue view <n>` for context + acceptance criteria),
- an existing PR/branch to continue, or
- a free-form task description.

If the item is under-specified or ambiguous, STOP and scope it first — use a
read-only scoping subagent (`local-subagent` in
[references/BACKENDS.md](references/BACKENDS.md); in Claude Code the `Explore`
agent) for a feasibility/implementation brief, or ask the user. Do not delegate
implementation of a fuzzy task.

If the user would rather not drive it here, offer the cloud alternative: detect
backends per [references/BACKENDS.md](references/BACKENDS.md), and offer one
option per available cloud backend plus a copy-paste brief. Launch only on
approval, then stop — this skill is for local delivery.

## Workflow

### 1. Plan
Read the issue and the relevant code (directly or via a read-only scoping
subagent). Produce a short implementation plan and write concrete steps to the
runtime's todo/task tool. Break the work into **independent, self-contained
chunks** wherever possible.

### 2. Set up the branch
Find the default branch (`gh repo view --json defaultBranchRef`; never assume
`main`). Create a feature branch off its up-to-date tip before any edits (never
work on the default branch). Match existing branch naming.

### 3. Delegate implementation
For each chunk, spawn the **implementer** with a self-contained prompt: the
task, acceptance criteria, relevant repo-relative paths, and constraints. It
cannot see this conversation.

- **Parallel background** implementers for genuinely independent chunks — but
  they share one working tree, so never let two touch the same files at once.
- **Foreground** for anything requiring live tool approval, or when chunks are
  sequential/dependent.
- Background subagents can't prompt for permissions. Pre-approve the commands
  they need in the runtime's permission settings (Claude Code: allow rules such
  as `Bash(<cmd>:*)`), or run them in the foreground. Re-run a permission-denied
  background chunk in the foreground to grant access.

Review each implementer's report before integrating. Re-delegate follow-ups as
needed; you own correctness.

### 4. Verify
Run the narrowest relevant checks for what changed (lint, typecheck, build,
targeted tests), using the repo's own commands. Delegate this to the
**test-runner** — fan out independent suites as parallel background runs, or run
one foreground. It reports pass/fail with failure details but never edits.
Iterate — re-delegate fixes to the implementer — until green or a genuine
blocker surfaces.

### 5. Commit
Commit on the feature branch following the repo's commit conventions
(`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or the style of recent
`git log`). Honor the repo's commit-message and attribution rules. If pre-commit
hooks modify files, stage them and retry.

### 6. Open the PR
Push the branch and open a PR with `gh pr create`. Follow the repo's PR template
and title conventions if it has them; otherwise a `## Summary` + `## Test plan`
body. Include `Closes #N` when delivering an issue. Then link back on the issue:
`gh issue comment <n>` with the PR URL and
`gh issue edit <n> --add-label "in-progress"` (create the label if missing) —
mirroring how roundup records session linkage for dedup.

Do NOT push or open the PR until verification passes and the user has approved,
per the safety rules. Never force-push, rewrite history, or bypass hooks.

### 7. Report
Summarize: branch, PR URL, files touched, verification result, and any
follow-ups. Tick off the todo plan as you go.

## Relationship to other primitives

- **roundup** triages and routes an item into this local lane.
- A **cloud session** on an available backend (see BACKENDS.md) is the remote
  alternative for the same kind of item.
- **handoff** (if installed) compacts context if you need to pass this work to
  another session mid-flight.
