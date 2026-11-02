---
name: roundup
description: Round up all outstanding knowledge work (open ledger action items, review packets waiting for sign-off, and in-flight agent sessions on every available backend) into one item-to-source-to-output-to-session graph, then produce one plan that lands finished work and launches new work to cloud sessions, local delivery, or scoping. Use when the user wants a work roundup, asks "what's in flight", "what should I delegate", "plan my day's work", or wants to reconcile delegated sessions. Not for "which projects to finish vs start" (that is the projects skill) or turning new messages into items (that is intake).
---

# Roundup (work)

Reconcile everything in flight and in the ledger into one picture, then hand the user a single plan to sign off on. One graph, two verbs:

- **Land**: finish existing work. Send approved-ready packets to `review`, close items whose source thread shows them done, fix missing linkage, stop orphaned sessions.
- **Launch**: start new work. A cloud session on an available backend, local delivery with the `deliver` skill, or a read-only scoping subagent.

This is the work-domain mirror of the code `roundup`. It is read-only until the user approves. After approval it launches once and returns without polling.

## Conventions (resolve first)

- **Ledger** and `WORK.md` per [references/LEDGER.md](references/LEDGER.md). No `ledger:` block: offer `/work:setup` and stop.
- **Sources** per [references/SOURCES.md](references/SOURCES.md). Roundup reads sources only to check whether an item is already done (a later reply in the source thread) or newly urgent.
- **Backends** per [references/BACKENDS.md](references/BACKENDS.md). Record the one-line result. Cloud sessions launch against the ledger repo when `cloud_access` is `direct`; otherwise they get the brief alone and return the packet in their final message.
- **Fresh intake**: if the newest `intake` run is older than one working day, say so in the headline and offer `Run intake first` as the first question.

When prompting for decisions, use the interactive multiple-choice tool and mark one option recommended with a one-line why. No such tool: a numbered list with the recommendation first.

## 1. Gather (always a full sweep)

- **Items**: every open `action-item` in the ledger, with labels, comments, and linked sources.
- **Packets**: every open item in `in-review` and the newest `<!-- work:packet -->` on each, plus packets in the final message of finished `return-packet` sessions (copy each to its item and set `in-review`).
- **Sessions**: on every backend that can search sessions, list sessions that mention ledger items (by item ID, title, or the ledger repo), most recent first. Say which backends were searched.
- **Done signals**: for each open item with an external requester, one read of the source thread for a later reply from the user that settles it.

## 2. Build the graph

Edges: item to source (links in the body), item to session (linkage comments, session titles, branch names per BACKENDS.md), item to packet, item to project (sub-issues or `- [ ] #N`), and blocking (`blocked by #N`, or a `blocked` comment naming a person).

Flag mismatches: sessions with no item, items `in-progress` with no live session or local owner, packets with no `Check` section, items whose source thread shows them done but are still open.

## 3. Classify

An item linked to a live session or an `in-review` packet is not a launch candidate. Show it with its owner.

**Item lanes** (decide from content, sanity-check labels):

| Lane | When |
| :- | :- |
| **cloud** | Clear deliverable, sources sufficient, nothing only the user can say: a session on an available cloud backend with a standalone brief |
| **local** | The user wants it done here: the `deliver` skill. The user's call, never the default |
| **scope** | Under-specified: a read-only subagent writes done-criteria and a plan, then the item returns to the next roundup |
| **human** | Relationship, negotiation, judgment, or anything in the user's own voice that `WORK.md` reserves |
| **skip** | Done, not the user's, or no longer relevant: a one-line reason, closed only on approval |

**Packet statuses**: `ready-for-sign-off` (check has no FAIL; UNVERIFIED items listed) · `needs-fixes` (any FAIL) · `stale` (a newer source message changes the ask).

**Session statuses**: normalize to `running`, `waiting`, `idle`, `finished`, `errored`, `orphaned`. A finished session with no packet is a mismatch: its output never reached the ledger.

**Global blocker**: an item with `External: yes` due within 24 hours (or overdue) that has no `ready-for-sign-off` packet. Surface it first. Pause unrelated launches by default; the user can override.

## 4. Briefs

For each cloud or scope launch, write a brief that stands alone. The session may not have the user's Slack or Gmail, so quote the source excerpts it needs in full (within `WORK.md`'s confidentiality rules), and include:

- The ledger item URL, title, requester, due date, and done-criteria.
- The source excerpts, each with its link.
- The output format (email body, Slack reply, doc) and the audience.
- Where to put the result: a `<!-- work:packet -->` comment on the item in the shape LEDGER.md gives, then status `in-review`; or, when `cloud_access` is `return-packet`, the packet as the final message. If the session has Gmail, it may also create a Gmail draft and name its ID.
- The rule: **never send, post, share, invite, or reply to anyone.** Sign-off happens in `review`.
- A self-check before posting the packet: every factual claim tied to a quoted source, or marked `[UNSOURCED]`.

## 5. Surface the roundup

Rendered markdown, no code fences. Decision first.

**Recommended:** Sign off 3 packets, launch 2 cloud sessions (claude-cloud), close 1 done item
**Blocker:** #41 Send Acme the revised SOW · due today · no packet
**Ledger:** owner/work · **Backends:** devin ✓ · claude-cloud ✓ · local-subagent ✓
**Items:** 12 open, 4 in flight, 3 cloud-ready · **Packets:** 3 ready, 1 needs fixes · **Sessions:** 2 running, 1 orphaned

Then one single-line bullet per item under bold group headers, empty groups omitted, in this order: **BLOCKER**, **SIGN OFF** (packets ready for `review`), **DECIDE** (needs the user), **LAUNCH**, **WAITING**, **MONITOR**, **CLEAN UP**.

## 6. Prompt

One question per section that has items, each with one recommended option, batched if the tool allows:

1. **Blocker** (if any): `★ Deliver #N locally now` / `Launch it to cloud` / `I'll handle it myself`
2. **Sign off** (if packets ready): `★ Run review on N packets` / `Let me pick` / `Skip`
3. **Launches**: `★ Launch all K (X cloud on <backend> + Y scope)` / `Deliver selected locally` / `Let me pick` / `Skip`
4. **Cleanup**: `★ Do all cleanup` / `Skip`

No write until the chain completes.

## 7. On approval

1. Cleanup: close done items with a comment naming the source that settled them; fix linkage; stop orphaned sessions.
2. Launch: send each brief on the chosen backend; local items go to `deliver`; scope items go to a background read-only subagent.
3. Record linkage on every launched item (comment with backend and session ID or URL, label `in-progress`).
4. Sign off: hand the approved packet list to the `review` skill.
5. Return with `launched / waiting / handed to review / closed`. Never poll. A later roundup picks up finished sessions.

Closing items and stopping sessions always need explicit approval.
