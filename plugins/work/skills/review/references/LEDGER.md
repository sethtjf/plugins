# Ledger

The ledger is where action items live between skills. It plays the role GitHub issues play in the `code` skills: `intake` writes items, `roundup` and `projects` read them, `deliver` and cloud sessions attach review packets to them, and `review` closes them.

## Default backend: GitHub issues in a private repo

Use a private repository that holds only the ledger (for example `<owner>/work`). Claude Code cloud sessions and Devin both launch against a repository, so this gives the same launch, linkage, and dedup the code `roundup` uses. Resolve the repo once per invocation: the user's statement wins, then the `ledger:` line in `WORK.md`, then ask.

Never use a code repository as the ledger. Never make the ledger repo public.

## Item shape

One issue per action item. Title: verb first, specific ("Send Acme the revised SOW", not "Acme SOW"). Body:

```markdown
**Requester:** <name, and how they asked: Slack DM, email, meeting>
**Due:** <YYYY-MM-DD, or "none stated">
**External:** <yes if the output goes outside the firm or team, else no>
**Done when:** <one or two observable criteria>

## Sources
- <link to each source message, thread, event, or doc>

## Context
<two to six sentences: what was asked, what is already known, constraints>
```

Keep `Context` to what a worker needs. Link to sensitive material rather than pasting it, unless `WORK.md` says the ledger may hold it.

## Labels

| Label | Meaning | Code equivalent |
| :- | :- | :- |
| `action-item` | One deliverable task | issue |
| `project` | A multi-week workstream; children are linked as sub-issues or `- [ ] #N` lines | `epic` |
| `ready-for-agent` | Well-specified enough to delegate | same |
| `ready-for-human` | Needs Seth's judgment, relationships, or voice | same |
| `in-progress` | A session or local `deliver` owns it; the owner is in a comment | same |
| `in-review` | A review packet is attached and waiting for sign-off | open PR |
| `blocked` | Waiting on someone; the comment names who and since when | same |

If the repo uses other names, map them once and say which mapping you used. Create a missing label only when a write step needs it.

## Review packet

A packet is one issue comment that starts with the marker `<!-- work:packet -->`:

```markdown
<!-- work:packet -->
**Action:** <exactly one outward step: send email to X, reply in Slack thread Y, share doc Z with W, or "none, internal only">
**Prepared as:** <Gmail draft ID, Slack draft, Drive or Docs link, or "inline below">

## Output
<the full text to be sent, or a link to the document>

## Sources
- <each source used, with the claim it supports>

## Check
<the checker's report: PASS / FAIL / UNVERIFIED per claim>
```

Whoever writes the packet adds `in-review` and removes `in-progress`. A newer packet supersedes an older one on the same item.

## Linkage

When work starts on an item, comment with the owner (`deliver` in this session, or the backend and session ID or URL) and add `in-progress`. This is how the next `roundup` avoids launching a duplicate.

## Other backends

If `WORK.md` names a different ledger (a Google Sheet, a Slack list, or a Markdown file), keep the same fields as columns or sections, use a `status` field in place of labels, and put packets in a linked doc. Say in the first line of output which ledger is in use.
