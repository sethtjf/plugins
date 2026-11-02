# Ledger

The ledger is where action items live between skills. It plays the role GitHub issues play in the `code` skills: `intake` writes items, `roundup` and `projects` read them, `deliver` and cloud sessions attach review packets to them, and `review` closes them.

The ledger is whatever task or project tool the user chose in `setup`. The skills speak in seven operations and six statuses. The `ledger:` block in `WORK.md` maps them onto the chosen tool. When a skill says "label `in-progress`" or "comment on the item", perform it through that mapping.

## Resolve

1. **Find `WORK.md`**, first match wins: a path the user names, `$WORK_MD`, `./WORK.md`, then `~/.claude/WORK.md`.
2. **Read its `ledger:` block.** If `WORK.md` or the block is missing, stop and offer the `setup` skill (`/work:setup`). Do not pick a ledger silently.
3. **Confirm with one read**: run the mapped `list_open` with a small limit. If it fails with an auth or connection error, say which tool failed and offer `setup` again. Do not fall back to another tool on your own.
4. **State it** in the first line of output: `Ledger: linear (team ENG, project "Work") ✓`.

## Operations

| Operation | Does |
| :- | :- |
| `list_open` | Open items, with status, parent, and due date |
| `get` | One item with its body and comments |
| `create` | New item with title, body, status, optional parent |
| `comment` | Append a comment to an item |
| `set_status` | Move an item to one of the statuses below |
| `link_parent` | Make an item the child of a project |
| `close` | Mark done, with a closing comment |

A tool that lacks comments (a sheet, some lists) maps `comment` to a `notes` column or a linked doc per item, and says so in `WORK.md`.

## Statuses

| Status | Meaning | Code equivalent |
| :- | :- | :- |
| `ready-for-agent` | Well-specified enough to delegate | same label |
| `ready-for-human` | Needs the user's judgment, relationships, or voice | same label |
| `in-progress` | A session or local `deliver` owns it; the owner is in a comment | same label |
| `in-review` | A review packet is attached and waiting for sign-off | open PR |
| `blocked` | Waiting on someone; the comment names who and since when | same label |
| `done` | Closed by `review` or by a cleanup the user approved | closed issue |

Items are typed `action-item` or `project` (a multi-week workstream with children, the `epic` equivalent). Map the type to whatever the tool has: an issue type, a label, a parent/child relation, or a `type` column.

## Adapters

`setup` fills the `ledger:` block from one of these. Match tools by name suffix, never the full name, and load deferred tools before use.

| Adapter | Tools ending in | Statuses map to | Notes |
| :- | :- | :- | :- |
| `github` | `list_issues`, `issue_read`, `issue_write`, `add_issue_comment` | Labels | Use a private repo that holds only the ledger. Cloud sessions can launch against it directly. |
| `google-sheets` | `get_values`, `append_values`, `update_values` | A `status` column | One row per item; columns `id, type, title, status, parent, due, requester, external, sources, notes, packet`. `packet` links a doc. |
| `slack-list` | `slack_read_list`, `slack_add_list_record`, `slack_update_list_record`, `slack_create_list` | A status field | Same fields as the sheet. Packets go in a linked doc. |
| `markdown` | Drive `read_file_content` and `update_file`, or local file tools | A `status:` line per item | Simplest; concurrent writers can collide, so cloud sessions return packets in their final message instead of writing. |
| `discovered` | Any other connected server whose tools create and list tasks, issues, or tickets (for example a project tracker) | That tool's own states | `setup` reads the tool schemas, proposes the mapping, and records exact tool names in `WORK.md` after the user confirms. |

Do not add an adapter row from memory. A row belongs in the table only after its tool names have been seen in a real session. Anything else goes through `discovered`.

## `WORK.md` ledger block

```yaml
ledger:
  adapter: github            # or google-sheets, slack-list, markdown, discovered
  container: owner/work      # repo, sheet ID and tab, list ID, file path, or team/project
  url: https://github.com/owner/work
  operations:                # exact tool names; required for discovered, optional otherwise
    list_open: mcp__github__list_issues
    create: mcp__github__issue_write
  statuses:                  # our status -> the tool's label, state, or column value
    ready-for-agent: ready-for-agent
    in-review: in-review
    done: closed
  types:
    project: label:project
  comments: native           # or notes-column, or linked-doc
  cloud_access: direct       # direct if cloud sessions can reach this ledger, else return-packet
```

## Item shape

Title: verb first, specific ("Send Acme the revised SOW", not "Acme SOW"). Body:

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

Keep `Context` to what a worker needs. Link to sensitive material rather than pasting it, unless `WORK.md` says the ledger may hold it. In a tool with fields, put requester, due, and external in fields and the rest in the description.

## Review packet

A packet is one comment (or the linked doc, per `comments:`) that starts with the marker `<!-- work:packet -->`:

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

Whoever writes the packet sets `in-review`. A newer packet supersedes an older one on the same item. When `cloud_access` is `return-packet`, a cloud session puts the packet in its final message and the next `roundup` copies it to the item.

## Linkage

When work starts on an item, comment with the owner (`deliver` in this session, or the backend and session ID or URL) and set `in-progress`. This is how the next `roundup` avoids launching a duplicate.
