# sethtjf plugins

Seth's personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/create-marketplace). The marketplace is named `sethtjf`, so every install ID reads `<plugin>@sethtjf`.

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

| Plugin | Description | Slash command |
| :- | :- | :- |
| [`mcp-servers`](plugins/mcp-servers) | Audits an MCP server's source against a 48-check best-practices rubric. Returns a 0–100 score, a letter grade, and a located change list. | `/mcp-servers:audit [path]` |
| [`workflow`](plugins/workflow) | Board open GitHub epics, round up PRs, issues, and agent sessions into one land-and-launch plan, and deliver an item locally. | `/workflow:epics`, `/workflow:roundup`, `/workflow:deliver` |

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
plugins/<name>/                   one directory per plugin
scripts/validate.sh               validation, also run in CI
.github/workflows/validate.yml    runs validate.sh on push and PRs
```

The repo is named `plugins` and contains a `plugins/` directory, so on GitHub a plugin lives at `plugins/plugins/<name>`. Inside the repo, every `source` is `./plugins/<name>`.

To add or update a plugin, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Each plugin declares its own `license` in `plugin.json`.
