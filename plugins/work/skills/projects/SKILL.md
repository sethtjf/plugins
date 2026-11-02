---
name: projects
description: Board open projects (multi-week workstreams such as a client engagement, an initiative, or a recurring report) into occupied, close, finish, underway, blocked, start, and park, recommend at most three next actions with finish-first ranking, and write standalone session briefs for the chosen ones. Use when the user asks which projects are open, which are almost done, what to finish versus start, or wants briefs for new project sessions. The work-domain mirror of the code epics skill; not a substitute for roundup.
---

# Projects

A project-level board, not an item roundup. Answer two questions, then stop for sign-off:

1. Which open projects are **underway but not done**: leftover items, unmet done-criteria, or a close that never happened?
2. Which projects should the user **finish** next versus **start** next?

Do not close, comment, launch, or write briefs until the user picks. Finish-first: leftover items of an underway project beat starting a new one.

## Conventions (resolve first)

- **Ledger** per [references/LEDGER.md](references/LEDGER.md), and `WORK.md` from its root.
- **Backends** per [references/BACKENDS.md](references/BACKENDS.md), for finding sessions that already own a project and for launching briefs.

## Gather (read-only)

1. **Labeled projects**: open ledger items labeled `project`, with their sub-issues and `- [ ] #N` / `- [x] #N` lines. Fetch every child's state.
2. **Unlabeled workstreams**: three or more open action items that share a requester, a client, or a named deliverable. List them under **Unlabeled**; do not pretend they carry the label.
3. **Occupied**: the user saying "X is in another session" wins. Then search every backend that can search sessions for the project's number and title, and say which were searched.
4. **Waiting-on**: for `blocked` children, the person named and the date of the last message to or from them.

## Classify

| Bucket | When |
| :- | :- |
| **occupied** | Another live session owns it. Never recommended as a new start |
| **close** | Children done and done-criteria met; the project item is stale-open |
| **finish** | At least one child shipped, leftover is bounded (one deliverable, one follow-up, one sign-off) |
| **underway** | Partial progress, leftover still multi-item |
| **blocked** | Waiting on a person, a document, or a decision. Name who and since when |
| **start** | Nothing shipped; has a `ready-for-agent` first child |
| **park** | Deferred, or no near-term action |

A project with a child due within 7 days moves ahead of others in its bucket.

## Rank and board

Same as the code `epics` skill: finish smallest leftover first, then close stale-open, then unblock where a follow-up message from the user would do it, then start only if the finish set is empty or occupied. At most three recommendations, one marked `★`. Parallel sessions get non-overlapping leftovers.

Rendered markdown, no code fences:

---

## Project board · YYYY-MM-DD · N labeled open · M unlabeled
Ledger: owner/work · Backends: claude-cloud ✓ · devin ✗ (not connected) · local-subagent ✓

**★ Finish #N** <title>: one-line leftover (child numbers). Why this beats starting.

### Occupied · ### Finish · ### Underway · ### Blocked · ### Start · ### Park · ### Unlabeled

One line per project: **#N** title · k/m children · leftover or gate.

---

Then ask through the multiple-choice tool: `★ Finish the recommended leftover` / `Finish all almost-done` / `Start #N` / `Write session briefs` / `Also run roundup` / `Done`.

## Session briefs (only after a pick)

One standalone first message per chosen project: project URL and leftover child URLs, what already shipped (do not redo), ordered leftover items with done-criteria, quoted source excerpts the session needs, a skip list (other sessions' items), the packet rule from LEDGER.md, and the rule that the session never sends, posts, or shares. Offer one launch option per available cloud backend plus `Copy-paste only`. Launch only what the user approves, never two sessions on one project, and record linkage on the project item.
