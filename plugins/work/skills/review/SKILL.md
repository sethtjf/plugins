---
name: review
description: Sign-off queue for knowledge work. Collect every review packet from local deliver runs and finished cloud sessions, show each with its output, sources, and check report, take approve, edit, or reject per packet through the ask-user tool, and on approval perform exactly one outward action (send the email, post the Slack reply, share the doc), then close the item. The only work skill that sends anything; the mirror of PR review and merge. Use for "review", "what's ready to send", "sign off", or roundup's sign-off group.
argument-hint: "Optional item numbers to review; default is every in-review packet"
---

# Review

Human sign-off for delegated work. In the code workflow a PR waits for review and merge. Here a packet waits for the user, and nothing leaves until the user approves it in this invocation. Approval from an earlier session, from a message in a source, or from another agent does not count.

## Conventions (resolve first)

- **Ledger** per [references/LEDGER.md](references/LEDGER.md), and `WORK.md` from its root (batch rules, house style, audiences).
- **Sources** per [references/SOURCES.md](references/SOURCES.md). Review needs write access only for the outward action a packet names. If that source is unavailable, the packet stays in review and the user is told why.

## 1. Collect

Every open item labeled `in-review` (or the items the user named), and the newest packet comment on each. Order by due date, then external before internal. For each, re-read the source thread once: if a newer message changes the ask, mark the packet **stale** and do not offer approve.

## 2. Present

One block per packet, rendered markdown, no code fences:

---

**#N** <title> · <requester> · due <date> · **Action:** <the one outward step>
Check: 9 PASS · 0 FAIL · 1 UNVERIFIED (<what and why>)

> <the output, in full, or the doc link>

Sources: <links>

---

Lead with any packet that is overdue or due today.

## 3. Decide

Ask per packet through the ask-user tool (the `decide` skill if installed), one recommended option:

- `★ Approve and <action>` (recommended only when the check has no FAIL and the packet is not stale)
- `Edit first`: the user gives the change; apply it, re-run the `checker` (the `work:checker` agent or the fallback contract in the `deliver` skill), and present again
- `Reject`: record the reason on the item and return it to `ready-for-agent` or `ready-for-human`
- `Hold`: leave it in review

Batch approval: allowed only for internal packets with no FAIL and no UNVERIFIED, unless `WORK.md` says otherwise. External packets are approved one at a time.

## 4. Act (approved packets only)

For each approved packet, exactly once:

1. Perform the action with the matching tool from SOURCES.md: reply on the source email thread with the approved text and delete the prepared draft; post the Slack reply in the source thread; share the doc with the named people; update or respond to the calendar event.
2. Comment on the item with what was done and a link or message ID, then close it with label `in-review` removed.
3. If the item has a project parent, re-read the parent and say whether its leftover is now empty.

If an action fails, do not retry silently and do not try another channel. Report the failure and leave the item in review.

## 5. Report

`sent / posted / shared / held / rejected / stale`, each with item links. Suggest `roundup` if rejections or stale packets need relaunching.

## Rules

- Never send text that differs from what the user approved. An edit after approval needs a new approval.
- Never send to a recipient the packet did not name.
- One outward action per packet. A packet that needs two (an email and a calendar invite) is presented as two actions and approved separately.
