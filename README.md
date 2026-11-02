# flowstack

Seth's personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/create-marketplace). The marketplace is named `flowstack`, so you add `sethtjf/flowstack` and install `<plugin>@flowstack`. Plugins are grouped into two domains, code and work, mirroring how Claude and ChatGPT keep code and work as separate areas of their apps. `code` and `work` are for doing tasks, and each ships the three domain-neutral [shared skills](shared) (`ambition`, `decide`, `style`), so each harness needs only its own plugin. A third plugin, `reflect`, is for improving the setup itself from session history.

## Install

Add the marketplace once, then install plugins from it:

```bash
claude plugin marketplace add sethtjf/flowstack
```

```bash
claude plugin install <plugin>@flowstack
```

On Claude Code 2.1.275 or later, one command inside a session does both:

```
/plugin install <plugin> --marketplace sethtjf/flowstack
```

## Plugins

| Domain | Plugin | Description | Slash commands |
| :- | :- | :- | :- |
| code | [`code`](plugins/code) | Board epics, round up PRs, issues, and agent sessions into one land-and-launch plan, deliver an item locally, and audit MCP servers you build. Pairs with [pstack](https://github.com/cursor/plugins/tree/main/pstack) for building and verifying code. | `/code:epics`, `/code:roundup`, `/code:deliver`, `/code:mcp-audit` |
| work | [`work`](plugins/work) | Set up a task tool of your choice, turn Slack, email, calendar, and meeting notes into action items, delegate them to cloud sessions or a local worker, and sign off on every outward send. | `/work:setup`, `/work:intake`, `/work:roundup`, `/work:projects`, `/work:deliver`, `/work:review` |
| both | [shared skills](shared) | Frame a task, settle open questions with a recommended option, and write in Seth's style. Shipped in `code` and `work` from one source in `shared/skills/`. | `/code:ambition` or `/work:ambition`, and likewise `decide`, `style` |
| reflect | [`reflect`](plugins/reflect) | Review past chats and sessions, find patterns, and interview you until you can name what to change in your setup. | `/reflect:introspect` |

Plugin skills run as `/<plugin-name>:<skill-name>`.

## Update

Pull the latest marketplace listing and any plugin whose `version` changed:

```bash
claude plugin marketplace update flowstack
```

Auto-update is off by default for third-party marketplaces. Turn it on in `/plugin` under **Marketplaces**, select `flowstack`, then **Enable auto-update**.

## Using a skill without the plugin

Each `plugins/<name>/skills/<skill>/` folder is also a standalone [Agent Skill](https://agentskills.io/specification). Copy it into `~/.claude/skills/` to use it in Claude Code without installing the plugin, or into any agent that supports the Agent Skills format. Outside a plugin the skill runs as `/<skill>` with no plugin prefix.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest (name: flowstack)
plugins/code, work, reflect       the three plugins
shared/skills/                    the one editable copy of the shared skills
scripts/sync-shared.sh            copies shared/skills/ into both plugins
scripts/validate.sh               validation, also run in CI; fails if a copy drifts
.github/workflows/validate.yml    runs validate.sh on push and PRs
```


To change a shared skill, edit `shared/skills/<skill>/` and run `scripts/sync-shared.sh`; never edit the copies under `plugins/`. Upgrading from the old plugin names? See [Migrating from older plugins](#migrating-from-older-plugins). To add or update a plugin, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Migrating from older plugins

The marketplace was renamed from `sethtjf` to `flowstack` (repo `sethtjf/flowstack`, formerly `sethtjf/plugins`). `workflow` and `mcp-servers` became `code`. `style`, `decide`, and `ambition` now ship inside both `code` and `work`, and `introspect` moved to `reflect`. Reinstall once per machine:

```bash
claude plugin marketplace remove sethtjf
claude plugin marketplace add sethtjf/flowstack
claude plugin install code@flowstack
claude plugin install work@flowstack
claude plugin install reflect@flowstack
```

Removing the `sethtjf` marketplace also removes every plugin installed from it (`writing`, `thinking`, `workflow`, `mcp-servers`, `flow`, or the new names). If you added the short-lived `flow` marketplace, remove it too: `claude plugin marketplace remove flow`. Then replace any `@sethtjf` keys in `settings.json` (`enabledPlugins`) and dotfiles.

| Old command | New command |
| :- | :- |
| `/writing:style` | `/code:style` or `/work:style` |
| `/writing:open-questions` | `/code:decide` or `/work:decide` |
| `/thinking:ambition` | `/code:ambition` or `/work:ambition` |
| `/thinking:introspect` | `/reflect:introspect` |
| `/workflow:roundup` | `/code:roundup` |
| `/workflow:epics` | `/code:epics` |
| `/workflow:deliver` | `/code:deliver` |
| `/mcp-servers:audit` | `/code:mcp-audit` |

## License

[MIT](LICENSE). Each plugin declares its own `license` in `plugin.json`.
