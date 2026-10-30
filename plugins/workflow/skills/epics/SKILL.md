---
name: epics
description: Board open epics — which are underway vs finished-enough to close, which leftover children to complete, and which epic to start next. Use when the user asks what epics are open, which are almost done, what to finish vs start, which epic to pick up, which epics are owned by other sessions, or wants first-message briefs for new epic sessions. Not a substitute for roundup (PRs/sessions/backlog land-launch).
---

# Epics

Product-level board, not a PR roundup. Answer two questions, then stop for
sign-off:

1. Which open epics are **underway but not done** — leftover children, leftover
   AC, or a close that never happened?
2. Which epics should we **finish** next vs **start** next?

Do **not** merge, close, comment, dispatch, or write session briefs until the
user picks. Finish-first: leftover children of an underway epic beat starting a
new one.

Roundup (the `roundup` skill, if this repo has it) is the issue↔PR↔session
land/launch graph. If the user asked for a roundup, use that skill. If they
asked "what epics", stay here. A roundup that needs launch priority may *read*
this board, but it does not replace it.

## Repo conventions (resolve first)

- **Repo**: `owner/name` from `git remote -v` (`origin`). Never assume.
- **Labels**: default to `epic`, `ready-for-agent`, `ready-for-human`. If the
  repo uses different names (check `gh label list` or the tracker's label
  list), map them once and say which mapping you used.
- **ADRs**: `docs/adr/` if present; otherwise skip the ADR step.
- **Verify commands**: read `AGENTS.md` / `CLAUDE.md` / `Justfile` /
  `package.json` for the repo's lint, typecheck, and test commands. Session
  briefs must quote the real commands, not placeholders.

## Gather (read-only)

Prefer GitHub MCP (`list_issues` / `issue_read`); `gh issue list --label epic`
has been empty in some agent environments even when labeled epics exist.

1. **Labeled epics.** Open issues with the epic label. For each: `issue_read`
   method `get` (body, labels, `has_children`, `sub_issues_summary`) and
   `get_sub_issues`.
2. **Body graph.** Some epics never became GitHub sub-issues. Parse `- [ ] #N`
   / `- [x] #N`, "Slices", "Implementation graph", "Approval sequence", and
   "Delivery sequence". Fetch those issues' state even when `has_children` is
   false.
3. **Unlabeled workstreams.** After the labeled set, scan for epic-sized work
   that would otherwise vanish:
   - Title starts with `epic(`
   - An issue named as `Parent:` by several open children
   - A `ready-for-human` HITL leftover of a large feat
   List these under **Unlabeled** — do not pretend they carry the epic label.
4. **Occupied sessions.** User-stated "X is in another session" always wins.
   If the runtime can list other agent sessions (Claude Code remote sessions,
   Devin sessions, Cursor cloud agents), search them for epic numbers / titles.
   Occupied epics are listed, never recommended as a new start.
5. **ADRs.** `ships-as:` (or equivalent) on ADRs that name the epic or its
   children — use them to explain blockers, not to invent work.

## Classify each epic

Use children **and** leftover AC. A 5/9 child close with a prod-flip still
open is not done. A 4/5 child close with one `ready-for-agent` leftover is
`finish`.

| Bucket | When |
|--------|------|
| **occupied** | Other live session (user-stated or discovered). Exclude from finish/start recommendations. |
| **close** | Children done and remaining AC is already shipped; the epic issue is stale-open. |
| **finish** | ≥1 child/slice shipped, leftover is bounded (one issue, a sweep, a rename, a flag flip). Highest leverage. |
| **underway** | Partial progress, leftover is still a multi-slice epic. Staff only if the user wants that stream. |
| **blocked** | `ready-for-human`, ADR gate, or blocked by another epic/session. Name the gate. |
| **start** | No meaningful shipped slice; has implementable `ready-for-agent` work. |
| **park** | Explicitly deferred, or long-haul infra with no near-term agent slice. |

Related epics (host vs teardown, e.g. build-the-new-runtime vs
delete-the-old-loop) are sequential, not parallel, unless leftover sets are
disjoint. Spell the edge: who owns the gate, who waits.

Do not fold one epic into another because they share a noun. Two epics that
both mention "search" or "ingestion" are still two epics.

## Rank

1. **Finish** occupied-excluded `finish` epics, smallest leftover first.
2. **Close** stale-open epics (comment+close only after user ok).
3. **Unblock** a `blocked` epic only when the gate is a verify/flip this
   session can do without stealing an occupied stream.
4. **Start** only if the finish set is empty, already occupied, or the user
   has spare parallel sessions. Prefer the `start` epic whose first child is
   `ready-for-agent` and unblocked.
5. **Park** stays park.

Recommend **at most three** next actions. One of them is `★`. Parallel
sessions must get **non-overlapping leftovers** (no two sessions delete the
same package or flip the same prod flag).

## Board format

Rendered markdown, **no code fences**. Lead with the `★` recommendation.

---

## Epic board — YYYY-MM-DD · N labeled open · M unlabeled

**★ Finish #N** — one-line leftover (issue numbers). Why this beats starting.

### Occupied
- **#N** title — other session; leftover in one clause

### Finish
- **#N** title — k/m children · leftover **#A**, **#B** · skip **#C** (deferred)

### Underway
- **#N** title — k/m · what remains

### Blocked
- **#N** title — gate (issue/ADR) · what unblocks

### Start
- **#N** title — first implementable child · why not yet

### Park
- **#N** title — one-line reason

### Unlabeled
- **#N** title — why it is epic-sized anyway

### Do not
- Occupied epics, deferred issues, and collisions with in-flight sessions

---

Then **immediately** ask how to proceed (interactive multiple-choice if the
runtime has it; otherwise a numbered list). Flag one `★`:

- `★ Finish the recommended leftover` — staff `finish` epics; do not start new
- `Finish all almost-done` — every `finish` row, one session per epic
- `Start #N` — only a `start` row, and only if finish is empty or occupied
- `Write session briefs` — copy-paste first messages for the chosen epics
- `Also run roundup` — land/launch PRs; epic board stays as ranked
- `Done` — stop; no writes

Do not dispatch or edit GitHub until the user chooses.

## Session briefs (only after they pick)

One copy-paste first message per chosen epic. Each brief must stand alone in a
fresh session:

- Parent epic URL + leftover child URLs (and ADRs)
- What already shipped (do not redo)
- Ordered leftover slices
- **Skip** list (deferred children, other sessions' leftovers, unrelated epics)
- Close hygiene: `Closes #child` on the leftover PR; **do not** `Closes #epic`
  until leftover AC is gone. Do not close a parent from a GitHub Development
  link that was never meant to finish it
- Collision rules: packages, flags, and teardowns owned by a sibling session
- Verify: the repo's required lint / typecheck commands in full, plus test
  commands scoped to touched packages (from the conventions step)
- First concrete action (read issue X, then the smallest PR)

## Close hygiene (when executing)

- A leftover-child PR closes the **child**, not the epic, unless that child was
  the last open AC
- Re-open an epic/child GitHub auto-closed from a stale Development link
- `ready-for-human` stays human until the gate in the issue is actually met
- After finishing a child, re-read the parent before closing it
