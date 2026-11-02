# sethtjf plugins

Seth's personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/create-marketplace). The marketplace is named `sethtjf`, after its author, so you add `sethtjf/plugins` and install `<plugin>@sethtjf`. Plugins are grouped into two domains, code and work, mirroring how Claude and ChatGPT keep code and work as separate areas of their apps. There are two plugins, `code` and `work`. Each ships the four domain-neutral [shared skills](shared) (`ambition`, `decide`, `style`, `introspect`), so each harness needs only its own plugin.

## Install

Add the marketplace once, then install plugins from it:

```bash
claude plugin marketplace add sethtjf/plugins
```

```bash
claude plugin install <plugin>@sethtjf
```

On Claude Code 2.1.275 or later, one command inside a session does both:

```
/plugin install <plugin> --marketplace sethtjf/plugins
```

## Plugins

| Domain | Plugin | Description | Slash commands |
| :- | :- | :- | :- |
| code | [`code`](plugins/code) | Board epics, round up PRs, issues, and agent sessions into one land-and-launch plan, deliver an item locally, and audit MCP servers you build. Pairs with [pstack](https://github.com/cursor/plugins/tree/main/pstack) for building and verifying code. | `/code:epics`, `/code:roundup`, `/code:deliver`, `/code:mcp-audit` |
| work | [`work`](plugins/work) | Set up a task tool of your choice, turn Slack, email, calendar, and meeting notes into action items, delegate them to cloud sessions or a local worker, and sign off on every outward send. | `/work:setup`, `/work:intake`, `/work:roundup`, `/work:projects`, `/work:deliver`, `/work:review` |
| both | [shared skills](shared) | Frame a task, settle open questions with a recommended option, write in Seth's style, and reflect on past sessions. Shipped in both plugins from one source in `shared/skills/`. | `/code:ambition` or `/work:ambition`, and likewise `decide`, `style`, `introspect` |

Plugin skills run as `/<plugin-name>:<skill-name>`.

## Update

Pull the latest marketplace listing and any plugin whose `version` changed:

```bash
claude plugin marketplace update sethtjf
```

Auto-update is off by default for third-party marketplaces. Turn it on in `/plugin` under **Marketplaces**, select `sethtjf`, then **Enable auto-update**.

## Using a skill without the plugin

Each `plugins/<name>/skills/<skill>/` folder is also a standalone [Agent Skill](https://agentskills.io/specification). Copy it into `~/.claude/skills/` to use it in Claude Code without installing the plugin, or into any agent that supports the Agent Skills format. Outside a plugin the skill runs as `/<skill>` with no plugin prefix.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest (name: sethtjf)
plugins/code/, plugins/work/      the two plugins
shared/skills/                    the one editable copy of the shared skills
scripts/sync-shared.sh            copies shared/skills/ into both plugins
scripts/validate.sh               validation, also run in CI; fails if a copy drifts
.github/workflows/validate.yml    runs validate.sh on push and PRs
```


To change a shared skill, edit `shared/skills/<skill>/` and run `scripts/sync-shared.sh`; never edit the copies under `plugins/`. Upgrading from the old plugin names? See [Migrating from older plugins](#migrating-from-older-plugins). To add or update a plugin, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Migrating from older plugins

`workflow` and `mcp-servers` became `code`, and the `writing` and `thinking` skills now ship inside both `code` and `work`. Update the marketplace, remove the old plugins, and install the new ones once per machine:

```bash
claude plugin marketplace update sethtjf
claude plugin uninstall writing@sethtjf
claude plugin uninstall thinking@sethtjf
claude plugin uninstall workflow@sethtjf
claude plugin uninstall mcp-servers@sethtjf
claude plugin install code@sethtjf
claude plugin install work@sethtjf
```

If you installed `flow@sethtjf` or `mcp-servers@sethtjf` while those existed, uninstall them too. If you added the marketplace under the short-lived name `flow`, run `claude plugin marketplace remove flow` and `claude plugin marketplace add sethtjf/plugins` first.

| Old command | New command |
| :- | :- |
| `/writing:style` | `/code:style` or `/work:style` |
| `/writing:open-questions` | `/code:decide` or `/work:decide` |
| `/thinking:ambition` | `/code:ambition` or `/work:ambition` |
| `/thinking:introspect` | `/code:introspect` or `/work:introspect` |
| `/workflow:roundup` | `/code:roundup` |
| `/workflow:epics` | `/code:epics` |
| `/workflow:deliver` | `/code:deliver` |
| `/mcp-servers:audit` | `/code:mcp-audit` |

## License

[MIT](LICENSE). Each plugin declares its own `license` in `plugin.json`.
