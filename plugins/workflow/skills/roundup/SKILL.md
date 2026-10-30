---
name: roundup
description: Round up all outstanding work for the repo — open PRs, open issues, and in-flight agent sessions on every available backend (Devin, Claude Code cloud, and others) — into a single issue↔PR↔session graph, then produce one prioritized attack plan that lands in-flight work and launches new work. Use when the user wants to review open PRs, plan attack on open issues, reconcile in-flight agent sessions, clean up the backlog, or do a "roundup". Not for "what epics are open / finish vs start" — that is the epics skill.
---

# Roundup

Reconcile **everything in flight and in the backlog** into one picture, then hand the user a single glanceable attack plan they can sign off on. One graph, two verbs:

- **Land** — finish existing work: merge / close / relabel open PRs, fix missing issue links, clean up sessions.
- **Launch** — start new work from the backlog: launch a cloud session on an available backend, deliver an item locally (the `deliver` skill, if installed), or spin up a read-only scoping subagent per actionable issue.

The full per-item plan lives in the runtime's todo/task tool; a concise **Roundup** goes to chat for sign-off. Do NOT take write actions (merge, close, comment, relabel, launch, stop a session) until the user approves.

## Default execution model: submit and return

Roundup is a coordinator, not a CI watcher. After approval, default to asynchronous progress:

- Submit approved PRs once (merge queue, auto-merge, or direct merge, per the repo's merge setup); report them as **queued** or **merged** rather than waiting for merge-group CI or deployment.
- Launch work that is independent of newly submitted PRs immediately. Keep only directly dependent launches in **WAITING**.
- Do not run `gh run watch`, sleep loops, or repeated status polling in the main session. One lightweight status snapshot after writes is enough.
- Return control to the user with queued / launched / waiting state while GitHub Actions and cloud sessions continue independently.
- Wait synchronously only when the user explicitly asks to "wait until merged/deployed", "land fully", or otherwise requests strict completion.

A pending CI or release run is not a failure and must not monopolize the main session. A completed failed latest default-branch CI or release run remains a global blocker as described below.

## Repo conventions (resolve first)

- **Repo**: `owner/name` from `git remote -v` (`origin`). Never assume.
- **Default branch**: `gh repo view --json defaultBranchRef`. Never assume `main`.
- **Merge setup**: whether the default branch requires a merge queue, and which merge methods are allowed (`gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed`, plus branch protection or rulesets if readable). Submit PRs the way the repo requires.
- **Deployment health signal**: if the repo documents one (`AGENTS.md`, `CLAUDE.md`, `.github/workflows/`, a `deploy-blocker`-style label), use it. Otherwise use the latest completed default-branch CI or release run.
- **Review policy**: whether ready PRs carry a formal approval. Some repos merge with an empty `reviewDecision`; read the repo's guidance instead of requiring approval by default.
- **Backends**: detect which agent backends this session can search, launch, and stop sessions on, per [references/BACKENDS.md](references/BACKENDS.md). Record the one-line result; later steps use only what it found.

When prompting for decisions, always use the interactive multiple-choice tool (not free-form chat) and mark one recommended option with `★` plus a why in its description. No such tool → numbered list in chat with the recommendation marked.

## Workflow

### 1. Gather everything (always a full sweep)
However the request is phrased, gather all three entity types — the cross-reference is the whole value.

- **PRs**: `gh pr list --state open --json number,title,headRefName,author,isDraft,createdAt,updatedAt,labels,url,body,mergeable,reviewDecision,statusCheckRollup`
- **Issues**: `gh issue list --state open --json number,title,body,labels,url,comments,assignees,milestone`
- **Sessions**: on every available backend that can search sessions, list sessions for this repo, most-recently-updated first. Say which backends were searched.
- **Deployment health**: take one snapshot of the signal from the conventions step (for a run-based signal, `gh run list --branch <default> --limit 20`). PR CI / prebuild / merge-queue green is **not** default-branch evidence. If the latest completed run failed, treat it as a global blocker; if a newer run is pending, report `pending · last completed run failed` or `pending · last completed run healthy` without waiting.

A completed failed default-branch CI or release run is the canonical **global blocker**. Surface it first and pause Launch by default, allowing unrelated progress only with explicit user override. Recovery is proven when a later successful default-branch run containing the fix completes; observe that on a later status check or Roundup.

### 2. Analyze (fan out for scale, read-only)
≤10 actionable items: analyze inline. More: spawn parallel **read-only** subagents (`local-subagent`) over batches of issues (specification quality, files touched, feasibility, blockers) and PRs (are review comments addressed?). Subagents in this phase **never edit** — they share one working tree. For ambiguous PRs, `gh pr view <n> --comments`; for unclear sessions, the backend's follow-up call.

### 3. Build the work graph
Draw edges: **PR↔issue** (`Closes/Fixes #N`, branch names, title overlap); **PR↔session** (backend branch prefixes from BACKENDS.md, session URLs/IDs in body/comments); **issue↔session** (session links in comments, search matches); **blocking** (`blocked by #N` / `depends on #N` — across verbs: a launch may be blocked by a PR that must land first).

Flag mismatches: PRs with no session, sessions with no PR, merged work whose issue stayed open, completed PRs missing their issue reference.

### 4. Classify each node
An issue linked to an open PR or a live session (on any backend) is **not** its own launch candidate — show it with its linked PR/session so you never launch a duplicate.

**PR statuses**: `ready-to-merge` (non-draft, mergeable, required checks passing, no blocking review, review comments addressed; apply the repo's review policy; bot `COMMENTED` reviews aren't blockers unless they raise unresolved correctness/security issues) · `needs-review` · `needs-fixes` · `stale` · `superseded` · `close`.

**Issue lanes** (no in-flight PR/session; decide from content, sanity-check labels):

| Lane | When |
|------|------|
| **cloud** | Well-specified, self-contained → a session on an available cloud backend. Pick the backend per the default order in BACKENDS.md and show it on the item |
| **local** | Well-specified, but the user wants it done here → the `deliver` skill if installed, otherwise this session. The user's call, never the default |
| **subagent** | Under-specified → read-only scoping subagent (feasibility + implementation brief; never edits) |
| **human** | Needs design, product judgment, or risky/irreversible decisions |
| **skip** | `needs-info`, `wontfix`, duplicate, non-actionable — surface with a one-line reason |

If no cloud backend is available, the cloud lane becomes copy-paste briefs (`brief`). Say so in the headline.

**Session statuses** (normalize each backend's states): `running`, `waiting` (on a person), `idle` / `suspended`, `finished`, `errored`, `orphaned` (no linked PR or issue). An idle or suspended session still linked to open work is **stale**: list it and let the user decide.

### 5. Build per-launch briefs
For each cloud/subagent item: issue summary, acceptance criteria, relevant files, constraints. Cloud briefs use repo-relative paths only (the session runs on a different filesystem) and name the repo and base branch. Subagent briefs state the task is read-only scoping.

### 6. Track the full plan
Write every concrete action into the todo/task tool (submit PR #N, comment+close #M, launch session for #Z on `<backend>`, stop stale session, …). Mark cross-verb-blocked launches `waiting on #N`. Distinguish actions this invocation controls from external outcomes: once GitHub accepts a queue submission, complete the **submit** todo and represent the eventual merge/deployment as monitored external state rather than leaving the main task in progress. This is the source of truth. If a durable copy is useful, write it to the OS temp dir — never the working tree.

### 7. Surface the Roundup

Decision-first, not entity-first. Rendered markdown, **no code fences**. Default surface = headline + action-grouped thread list only; entity tables and dependency graph are opt-in drill-downs. The user should know exactly what to do next, in order, without joining rows across tables.

**Layer 1 — headline** (≤7 lines, `Recommended:` first, omit empty lines):

**Recommended:** Merge #123 #131, launch 2 cloud sessions (devin), stop 1 orphan
**Default branch:** healthy at abc1234 · pending at def5678 · or · **BLOCKED:** latest completed CI/release run failed at abc1234
**Backends:** devin ✓ · claude-cloud ✗ (not connected) · local-subagent ✓
**Blockers:** #202 waiting on #126 (failing lint)
**PRs:** 3 ready-to-merge · 1 needs-fixes · **Issues:** 8 open — 3 in-flight · 2 cloud-ready · **Sessions:** 4 running · 1 orphaned

**Layer 2 — action-grouped thread list**: bold group headers + one single-line bullet per thread (driving id, short title, concrete action, linked entities + blockers inline). Bullets, never leading-space indentation. Omit empty groups. Groups in order:

**DEFAULT-BRANCH BLOCKER**
- **main** CI / Release — `land fix → observe a later successful default-branch run` · latest completed run failed at abc1234 · all other Launch actions paused

**LAND — ready now**
- **#123** Fix auth timeout — `merge` · closes #45 · session devin-abc (idle)

**DECIDE — needs you**
- **#126** Embedder refactor — `fix lint → merge` · closes #78

**LAUNCH — new work**
- **#203** Flaky webhook retries — `cloud session (devin)`
- **#118** Tidy config loader — `deliver locally` (well-specified; user driving it here)

**WAITING**
- **#202** Add ColBERT scoring — `cloud after #126 merges` · directly blocked by #126

**MONITOR**
- session devin-def `running 10m` → #200 Add retry logic
- session claude session_01… `running 4m` → #201 Cache warmup
- PR #123 `queued` · CI continues asynchronously

**CLEAN UP**
- session devin-xyz `orphaned 3d` → stop

**Layer 3 — drill-downs (opt-in via the Extras question, never by default)**: full per-entity tables (PRs: # / title / status / linked issues / session / action · Issues: # / title / in-flight? / lane / blocked-by / action · Sessions: backend / id / status / since / linked PR / issue / action) and a cluster-based dependency graph for complex blocking chains.

### 8. Prompt with a scoped question chain
One question per section with actionable items, each via the multiple-choice tool with cherry-pickable options and one `★` default chosen from the actual plan:

0. **Default branch** (if blocked by a completed failure): `★ Pause Launch; fix CI/release first` / `Proceed with selected unrelated work` / `Let me inspect failures`. Dequeuing already-approved queued PRs still requires explicit approval.
1. **PRs** (if landable): `★ Submit all N ready PRs (#…)` / `Submit selected — let me pick` / `Skip PRs`
2. **Launches** (if candidates): `★ Launch all K independent items (X cloud on <backend> + Y subagent)` / `Launch cloud only` / `Use a different backend` (only when more than one cloud backend is available) / `Deliver selected locally` / `Let me pick` / `Skip`. Show directly dependent items as waiting, not as launchable.
3. **Cleanup** (if orphans/mismatches/closeables): `★ Do all cleanup (…)` / `Skip cleanup`
4. **Extras** (always): `Show full entity tables` / `Show the dependency graph` / `★ Proceed` / `Let me adjust first`

Batch all applicable questions into a single prompt if the environment supports it; otherwise ask sequentially. Do NOT execute any write action until the chain completes.

### 9. On approval: submit Land → launch independent work → return

**Default-branch health gate:** if the latest completed default-branch CI or release run failed, **pause all Launches by default**. Landing the CI/release fix and cleanup is allowed; unrelated Launch requires explicit override. Do not wait for a later run to complete in this invocation.

1. **Immediate Land actions** — perform approved comments, closes, issue-link fixes, relabeling, and session cleanup (each backend's stop call).
2. **Submit PRs** — the way the repo's merge setup requires: add to the merge queue, enable auto-merge, or merge with an allowed method. Once accepted, mark the submit actions complete and report state. Do not wait for merge-group CI, merge, or deployment.
3. **Partition Launch**:
   - If the latest completed default-branch run succeeded, launch items independent of newly submitted PRs now: cloud → the chosen backend's launch call; local → the `deliver` skill; subagent → a background read-only `local-subagent`.
   - Keep items directly dependent on queued PRs in **WAITING**. If the dependency changes deployed behavior, require a later observed full deployment success containing the merge before releasing the launch.
   - If the latest completed default-branch run failed, keep all Launch items waiting unless the user explicitly approved unrelated progress.
4. **Record linkage** — for every launched issue, `gh issue comment <n>` with the backend and session ID/URL (or subagent note) and `gh issue edit <n> --add-label "in-progress"` (create the label if missing).
5. **Take one snapshot** — optionally read queue/PR/deployment status once after writes. Never use `gh run watch`, sleep loops, repeated polling, or wait on pending external work in the default mode.
6. **Return promptly** — summarize `queued / merged / launched / waiting / cleanup`. A queue submission is not "merged"; label it accurately. If there are no Launch candidates, there is never a reason to wait for deployment.

On a later status check or Roundup:

1. Inspect queued PRs and the latest completed default-branch CI or release run once.
2. Drop work whose PR merged, note auto-closed issues, and release directly dependent launches only when their required merge and default-branch run evidence exists.
3. If the latest completed default-branch CI or release run failed, add the run/root cause to the graph and apply the global blocker policy.
4. If CI or release is still pending after a last completed success, report it as pending and return without polling.

**Strict completion override:** only when the user explicitly requests waiting until merge/deployment may the main session block on external checks. Keep that exception scoped to the requested PRs/runs; it is not the Roundup default.

Tick off immediate actions as each completes. Represent queued and waiting external outcomes accurately rather than keeping the coordinator occupied.

### 10. Prompt for the follow-up
Print a short summary (queued / launched / waiting), then prompt again via the multiple-choice tool, tailored to what remains: `★ Continue independent work` / `Check queued PRs once` / `Check launched sessions once` / `Re-run roundup` / `Done for now`. A status check is one snapshot, never a polling loop.

Destructive/irreversible actions (closing PRs/issues, stopping sessions) always require explicit approval per the safety rules.
