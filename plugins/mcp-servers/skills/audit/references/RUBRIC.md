# MCP Server Audit Rubric

The 48 checks below make up the best-practices guide, and each check states what passing looks like. The category and check weights here match `assets/rubric.json`, which `scripts/score.py` uses for the arithmetic. If you change a weight, change it in both places.

Legend:

- **Wt**: weight within the category (1 to 3).
- **Per tool**: `yes` means the score is the fraction of tools that pass (0.0 to 1.0). `no` means a single server-wide result.
- **CAP**: when the cap condition is met, set `cap_triggered: true` on that check's result. Any triggered cap limits the overall score to 69.
- **Min version**: scored only when the server targets that MCP protocol version or later. Otherwise `score.py` turns it into a zero-weight advisory.

Category weights sum to 100.

## CAT: Catalog design (12)

The catalog is everything the model can see about the server. A small set of tools shaped around intent beats a copy of an API.

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| CAT-1 | 3 | no | Tools are shaped around user intent, not one per endpoint. Fail signals: one tool per OpenAPI operation, separate create/update/patch tools that could be one upsert, tools that differ only by a filter value. |
| CAT-2 | 3 | no | No ambiguous overlap. Every near-duplicate pair in `metrics.json` is either merged or disambiguated (see DSC-2). Duplicate names are an automatic fail. |
| CAT-3 | 2 | no | Definitions are a proportionate size: median at most about 400 estimated tokens, and no single tool over about 1,500 unless its schema genuinely needs it. Always report `est_tokens_total`. |
| CAT-4 | 2 | no | With more than 15 tools, at least 90% share consistent domain prefixes (`github_`, `crm.contacts.`) so one search term matches a group. Mark `na` at 15 tools or fewer. |
| CAT-5 | 2 | no | No server-side meta-tool indirection (a generic `invoke`/`call_tool` that takes a tool name and arguments) unless the underlying tools are also listed or the indirection is an opt-in mode. Indirection hides per-tool annotations, approval UI, and host-side tool search. |

## NAM: Naming (8)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| NAM-1 | 3 | yes | Each name is 1 to 128 characters drawn from `[A-Za-z0-9_.-]` and is unique within the server. |
| NAM-2 | 2 | no | The server follows one convention: one case style, one separator, and a consistent verb/noun order. |
| NAM-3 | 2 | yes | Each name states an action and an object (`contacts_update`), not a vague handle (`handle`, `run`, `tool1`, `api`). |
| NAM-4 | 1 | yes | A human-readable `title` is set for display. |

## DSC: Descriptions (14)

Descriptions do two jobs. They are what host-side tool search indexes, and they are what the model relies on to choose a tool.

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| DSC-1 | 3 | yes | The tool has a description, and its first sentence says what it does in the words a user would use for the task. Good: "Change a contact's email or phone". Bad: "PATCH /contacts/{id}". |
| DSC-2 | 3 | no | Where tools overlap, each description says when to choose it over the sibling, and names that sibling. |
| DSC-3 | 2 | yes | Side effects and costs are stated: writes, external sends, irreversibility, rate limits, slow operations, and paging behavior. Read-only tools with no notable cost pass by default. |
| DSC-4 | 2 | yes | Descriptions are tight: the core fits in 1 to 4 sentences, long reference material lives in resources or docs, and there's no marketing filler or implementation detail at the front. |
| DSC-5 | 2 | yes | Prerequisites are stated as facts ("Requires a `session_id` from `sessions_create`"). The description gives no directives about the model's general behavior, other servers' tools, or the user ("always call this first", "ignore other tools", hidden instructions). |
| DSC-6 | 2 | yes | Inputs that aren't obvious have examples, either in the description or in schema `examples`. Tools whose inputs are all obvious pass. |

## INP: Input schemas (12)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| INP-1 | 3 | yes | **CAP** if any tool's schema is null or not valid JSON Schema. `inputSchema` is a valid JSON Schema object with `type: "object"`. Tools that take no parameters use `{"type": "object", "additionalProperties": false}`. |
| INP-2 | 3 | yes | Every property has a description. Identifier arguments say where the value comes from, meaning which tool returns it. |
| INP-3 | 2 | yes | Types are constrained: enums for closed sets, `format` for dates, URIs, and emails, min/max bounds, patterns where they help, and an accurate `required` list. |
| INP-4 | 2 | yes | The shape is easy for a model to fill in: no free-form `object` or `any` bags where the fields are knowable, nesting no deeper than 3 levels (`input_schema_depth` in the metrics), and `oneOf` unions that carry a discriminator. |
| INP-5 | 1 | yes | Limit and page-size arguments are bounded and their defaults are documented. Tools without such arguments pass. |
| INP-6 | 1 | yes | Min version 2026-07-28. `x-mcp-header` appears only on non-sensitive primitive parameters (never tokens, passwords, or PII) and meets the spec's constraints. Mark `na` if no tool uses it. |

## OUT: Outputs and results (10)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| OUT-1 | 3 | yes | Tools that return structured data declare `outputSchema`, and the code paths that build results produce `structuredContent` that conforms to it. Set `spec_violation: true` if a declared schema isn't honored. Tools that return only prose pass. |
| OUT-2 | 2 | yes | Structured results are also serialized into a text content block for clients that don't read `structuredContent`. |
| OUT-3 | 2 | yes | Result size is bounded through cursors or limits. Truncation comes with an explicit continuation message ("truncated; call X with cursor Y"), and large blobs are returned as a `resource_link` instead of inline. |
| OUT-4 | 2 | yes | Results are useful to the model: they include the IDs and handles the next call needs, and they don't dump raw upstream payloads full of irrelevant fields. |
| OUT-5 | 1 | no | Content annotations (`audience`, `priority`) are used where some content is meant only for the user or only for the model. Mark `na` if all content is meant for both. |

## ANN: Annotations (8)

Hosts use annotations to auto-approve reads and gate writes, so a wrong annotation is worse than a missing one.

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| ANN-1 | 3 | yes | **CAP** if any tool that writes or sends claims `readOnlyHint: true`. Every tool sets `readOnlyHint`, and the value matches the code. Trace each handler through to its side effects. |
| ANN-2 | 2 | yes | Tools that write set `destructiveHint` and `idempotentHint`, and both match the code. Read-only tools pass. |
| ANN-3 | 2 | yes | Tools that reach external systems or return untrusted third-party content set `openWorldHint: true`. |
| ANN-4 | 1 | no | Annotations come from one source of truth, such as registry metadata or a decorator, rather than literals copied tool by tool. |

## ERR: Errors (8)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| ERR-1 | 3 | no | Execution failures (input validation, upstream API errors, business rules) come back as results with `isError: true`. JSON-RPC protocol errors are reserved for unknown tools, malformed requests, and server faults. |
| ERR-2 | 3 | no | Error text supports recovery. It says what was wrong, gives the valid format or range, includes current values where they matter (such as today's date for a date check), and names the tool or argument that would fix the problem. |
| ERR-3 | 2 | no | Error text contains no stack traces, secrets, internal hostnames, or raw upstream response bodies. |

## LST: List stability and caching (8)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| LST-1 | 3 | no | Min version 2026-07-28. **CAP** if the condition below is violated. The tool set doesn't vary per connection or as a side effect of other requests, though it may vary by the authorization presented on the request. Fail signal: tools like `enable_toolset` that change a session's registry. Set `spec_violation: true` as well when violated, since the spec says MUST NOT. |
| LST-2 | 2 | no | Tools are listed in a deterministic order. Watch for unordered maps (Rust `HashMap`, Go `map`) or sets feeding `tools/list`. |
| LST-3 | 2 | no | `listChanged` is declared only if `notifications/tools/list_changed` is actually emitted, and the notification is emitted whenever the set changes. |
| LST-4 | 1 | no | Min version 2026-07-28. List results carry `ttlMs` and `cacheScope`. If the list varies by authorization, the cache scope must prevent sharing across principals. |

## AUTH: Authorization and scopes (10)

This category applies to HTTP transports. For a stdio-only server, mark every check `na`; stdio credential handling is graded under SEC-4.

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| AUTH-1 | 3 | no | The server serves OAuth 2.0 Protected Resource Metadata (RFC 9728), and its 401 responses carry `WWW-Authenticate` with `resource_metadata` and a `scope` hint. Set `spec_violation: true` if the metadata is missing. |
| AUTH-2 | 3 | no | **CAP** if the condition below is violated. Access tokens are validated, including the audience (RFC 8707), and client tokens are never passed through to upstream APIs. |
| AUTH-3 | 2 | no | A single map from tools to required scopes exists. `tools/list` hides tools the caller can never be granted, and lists tools that step-up could grant, challenging for them at call time. |
| AUTH-4 | 1 | no | When scope is insufficient, the server returns 403 with `error="insufficient_scope"` and every missing scope in a single challenge. It also honors scope hierarchies, where a broader scope implies narrower ones. |
| AUTH-5 | 1 | no | `scopes_supported` lists a minimal baseline for basic use, not every scope the server knows about. |

## STA: State and handles (4)

Mark both checks `na` if every tool is stateless.

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| STA-1 | 2 | no | No tool relies on implicit per-connection state. State that spans calls lives behind an explicit handle that a create tool returns and later calls accept as an argument. |
| STA-2 | 2 | no | Handles are opaque. Where the server is unauthenticated, they're also high-entropy. Authorization is checked on every call, the handle's lifetime is stated in the create tool's description, and an expired or unknown handle returns `isError` with a recovery hint. |

## SEC: Security hygiene (6)

| ID | Wt | Per tool | Pass criteria |
|---|---|---|---|
| SEC-1 | 2 | no | Inputs are validated beyond the schema: path traversal for file paths, injection for queries, and SSRF for URL arguments. |
| SEC-2 | 2 | no | Tool calls and upstream calls have timeouts and rate limits. |
| SEC-3 | 1 | no | Untrusted upstream content (web pages, emails, user-generated text) is returned clearly delimited and attributed, never merged into text that reads as instructions. |
| SEC-4 | 1 | no | Secrets come from the environment or a secret store. None are hardcoded, logged, or accepted as plain tool arguments. |
