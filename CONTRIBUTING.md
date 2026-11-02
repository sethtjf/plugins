# Adding or updating a plugin

Each plugin lives in `plugins/<name>/` and has one entry in `.claude-plugin/marketplace.json`. `scripts/validate.sh` checks that the two agree. CI runs the same script on every push and pull request.

## Add a plugin

1. **Unzip into `plugins/<name>/`.** Afterwards `plugins/<name>/.claude-plugin/plugin.json` must exist. If the zip has a wrapping folder (`plugins/<name>/<name>/.claude-plugin/...`), flatten it:

   ```bash
   unzip ~/Downloads/<name>.zip -d plugins/<name>
   ```

   ```bash
   ls plugins/<name>/.claude-plugin/plugin.json
   ```

2. **Set `license` and `version` in `plugin.json`.** Use `"license": "MIT"` to match the repo unless the plugin needs something else. Start at `"version": "0.1.0"` or keep the version the plugin shipped with.

3. **Add the marketplace entry** to the `plugins` array in `.claude-plugin/marketplace.json`:

   ```json
   { "name": "<name>", "source": "./plugins/<name>", "description": "One sentence on what it does." }
   ```

   - `name` must equal `name` in `plugins/<name>/.claude-plugin/plugin.json`. A mismatch fails at install with "Plugin not found in marketplace."
   - `source` is relative to the repo root, starts with `./`, and has no `..`.
   - Do not put `version` here. Keep it only in `plugin.json`.

4. **Validate:**

   ```bash
   scripts/validate.sh
   ```

5. **Add a row to the Plugins table in `README.md`:** name, description, and slash command (`/<name>:<skill>` for each skill).

6. **Commit and open a PR.** When it merges to `main`, the `tag-releases` workflow creates a `<name>--v<version>` tag and a GitHub release for the new plugin. You don't run `claude plugin tag` by hand. `validate.yml` has already checked that `plugin.json` and the marketplace entry agree.

## Update a plugin

1. Make the change under `plugins/<name>/`.
2. **Bump `version` in `plugin.json`.** Installed users keep their cached copy until the version string changes, so an unbumped change never reaches them.
3. Run `scripts/validate.sh`, update the README row if the description or commands changed, and commit. The merge to `main` tags and releases the new version.

## Rules the validator enforces

| Rule | Why |
| :- | :- |
| Every `source` directory exists | `claude plugin validate` passes a missing directory. Install then fails with `Source path does not exist`. |
| Entry `name` equals `plugin.json` `name` | Otherwise install fails with "Plugin not found in marketplace." |
| `source` starts with `./`, no `..` | Relative sources resolve from the repo root and cannot leave it. |
| Every `plugins/*` directory has an entry | Catches a plugin that was unzipped but never listed. |
| `license` and `version` set in `plugin.json` | Anthropic's plugin directory rejects plugins without a license. Version drives updates. |
| No `version` in the marketplace entry | When both are set, `plugin.json` wins without warning. |
| Skill `name` matches its folder, lowercase letters, digits, and single hyphens, at most 64 chars | [Agent Skills spec](https://agentskills.io/specification). |
| Marketplace name is not reserved | `claude plugin marketplace add` refuses official Anthropic names such as `claude-plugins-official`. |

## Test an install locally

From the repo root:

```bash
claude plugin marketplace add ./
```

```bash
claude plugin install <name>@flow
```

A marketplace added from a local path loads plugin files in place, so edits show up at the next session start or after `/reload-plugins` without a version bump. Remove it with `claude plugin marketplace remove flow` before adding the GitHub copy.
