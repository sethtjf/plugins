# Agent backends

How to find out which places this session can hand work to, and how to use each one. Do this once per invocation, before any step that searches or launches sessions.

## Detect

1. **Match by suffix.** MCP tool names carry a prefix the user chose when installing the server (`mcp__devin__…`, `mcp__Devin_MCP__…`). Match on the tool-name suffix in the table, never the full name. If the runtime lists a matching tool as deferred (name only, no schema), load it before use (in Claude Code, `ToolSearch` with `select:<name>`).
2. **Confirm with one read.** A listed tool is not proof of access: the server may need sign-in or may be disconnected. Make the backend's cheap read call. Count the backend as available only if it returns without an auth or connection error.
3. **Record the result** as one line before continuing, for example: `Backends: devin ✓ · claude-cloud ✓ · local-subagent ✓`. Name a backend that was listed but failed its read as `✗ (needs sign-in)` or `✗ (not connected)` so the user can fix it.

If nothing is available, the fallback is copy-paste briefs. That is always available and always offered.

## Backends

| Backend | Present when the session has | Read check | Search sessions | Launch | Follow up | Stop |
| :- | :- | :- | :- | :- | :- | :- |
| `devin` | tools ending `devin_session_create`, `devin_session_search`, `devin_session_interact` | `devin_session_search` with a narrow query | `devin_session_search` | `devin_session_create` with the brief as the prompt | `devin_session_interact` (get status, send message) | `devin_session_interact` (terminate or archive) |
| `claude-cloud` | tools ending `create_session`, `list_sessions`, `send_message` from a `claude-code-remote` server (present only inside a Claude Code cloud session) | `list_sessions` with a small `limit` | `list_sessions`, then `get_session` on candidates | `create_session` with the brief as `prompt` and the repo URL as `source_url` | `send_message`, `get_session` | `interrupt_session` (stop a turn), `archive_session` (end it) |
| `local-subagent` | the runtime's own subagent tool (Claude Code: `Agent`) | none needed | not applicable | spawn a subagent in this session with the brief | its final report returns to this session | not applicable |
| `brief` | always | none | not applicable | print the brief for the user to paste | the user's call | not applicable |

Do not add a backend from memory. A row belongs here only after its tool names have been seen in a real session.

### Backend quirks

- **devin:** search matches exact words in titles and messages, not meaning. Run a few short queries in parallel (`#1743`, the epic's title words, a likely tag such as `epic-1743`), and use the `tags` filter when the repo tags sessions. Search results omit the `devin-` prefix that `devin_session_interact` requires, so add it before follow-up calls.
- **claude-cloud:** `list_sessions` includes the session running this skill. Exclude it. Results span every repo the account uses, so match on the issue or epic number or title, not on recency.
- **Branch names:** Devin pushes `devin/*` branches and Claude Code cloud sessions push `claude/*` branches. A PR on one of those branches came from that backend; look for the session ID or URL in the PR body or comments.

### When a found session occupies an item

Count a session as occupying an item only if it is running or waiting on a person. A finished, archived, or expired session does not. A session suspended or idle for inactivity is **stale**: list it as stale with its last update time and let the user decide. Never launch a second session on that item without saying so.

## Rules

- **Launch only on the user's say-so.** Cloud sessions cost money and act on the repo. Show the backend per item and get explicit approval before any launch call.
- **One brief, any backend.** Write the brief backend-neutral and self-contained. The backend changes only how it is sent.
- **Prefer what the user named.** "Send it to Devin" picks `devin` if it is available. If it is not, say so and offer the alternatives instead of substituting silently.
- **Default order** when the user has no preference: the cloud backend the user already has sessions on, then any other available cloud backend, then `brief`. Use `local-subagent` only for scoping or read-only work, or when the user asks to do it here.
- **Report what launched.** For each launch, give the backend, the session ID or URL it returned, and the item it covers.
