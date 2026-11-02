# flow

Seth's personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/create-marketplace). The marketplace and repo are both named `flow`, so you add `sethtjf/flow` and install `<plugin>@flow`. Plugins are grouped into two domains, code and work, mirroring how Claude and ChatGPT keep code and work as separate areas of their apps. `flow` holds the domain-neutral skills both domains use, so each harness installs `flow` plus its domain plugins.

## Install

Add the marketplace once, then install plugins from it:

```bash
claude plugin marketplace add sethtjf/flow
```

```bash
claude plugin install <plugin>@flow
```

On Claude Code 2.1.275 or later, one command inside a session does both:

```
/plugin install <plugin> --marketplace sethtjf/flow
```

## Plugins

| Domain | Plugin | Description | Slash commands |
| :- | :- | :- | :- |
| shared | [`flow`](plugins/flow) | Frame a task, settle open questions with a recommended option, write in Seth's style, and reflect on past sessions. | `/flow:ambition`, `/flow:decide`, `/flow:style`, `/flow:introspect` |
| code | [`code`](plugins/code) | Board epics, round up PRs, issues, and agent sessions into one land-and-launch plan, and deliver an item locally. Pairs with [pstack](https://github.com/cursor/plugins/tree/main/pstack) for building and verifying code. | `/code:epics`, `/code:roundup`, `/code:deliver` |
| code | [`mcp-servers`](plugins/mcp-servers) | For building MCP servers. Audits a server's source against a 48-check best-practices rubric and returns a 0–100 score, a letter grade, and a located change list. | `/mcp-servers:audit [path]` |
| work | [`work`](plugins/work) | Set up a task tool of your choice, turn Slack, email, calendar, and meeting notes into action items, delegate them to cloud sessions or a local worker, and sign off on every outward send. | `/work:setup`, `/work:intake`, `/work:roundup`, `/work:projects`, `/work:deliver`, `/work:review` |

Plugin skills run as `/<plugin-name>:<skill-name>`.

## Update

Pull the latest marketplace listing and any plugin whose `version` changed:

```bash
claude plugin marketplace update flow
```

Auto-update is off by default for third-party marketplaces. Turn it on in `/plugin` under **Marketplaces**, select `flow`, then **Enable auto-update**.

## Using a skill without the plugin

Each `plugins/<name>/skills/<skill>/` folder is also a standalone [Agent Skill](https://agentskills.io/specification). Copy it into `~/.claude/skills/` to use it in Claude Code without installing the plugin, or into any agent that supports the Agent Skills format. Outside a plugin the skill runs as `/<skill>` with no plugin prefix.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest (name: flow)
plugins/<name>/                   one directory per plugin
scripts/validate.sh               validation, also run in CI
.github/workflows/validate.yml    runs validate.sh on push and PRs
```


Moving from the old `sethtjf` marketplace? See [Migrating from `sethtjf`](#migrating-from-sethtjf). To add or update a plugin, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Migrating from `sethtjf`

The marketplace was renamed from `sethtjf` to `flow`, `writing` and `thinking` were merged into `flow`, and `workflow` became `code`. Reinstall once per machine:

```bash
claude plugin marketplace remove sethtjf
claude plugin marketplace add sethtjf/flow
claude plugin install flow@flow
claude plugin install code@flow
claude plugin install mcp-servers@flow
```

Then replace any `@sethtjf` keys in `settings.json` (`enabledPlugins`) and dotfiles.

| Old command | New command |
| :- | :- |
| `/writing:style` | `/flow:style` |
| `/writing:open-questions` | `/flow:decide` |
| `/thinking:ambition` | `/flow:ambition` |
| `/thinking:introspect` | `/flow:introspect` |
| `/workflow:roundup` | `/code:roundup` |
| `/workflow:epics` | `/code:epics` |
| `/workflow:deliver` | `/code:deliver` |
| `/mcp-servers:audit` | unchanged |

## License

[MIT](LICENSE). Each plugin declares its own `license` in `plugin.json`.
