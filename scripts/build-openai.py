#!/usr/bin/env python3
"""Generate the OpenAI (ChatGPT and Codex) plugin configs from the Claude ones.

The Claude manifests are the only copies to edit:

  .claude-plugin/marketplace.json            -> .agents/plugins/marketplace.json
  plugins/<name>/.claude-plugin/plugin.json  -> plugins/<name>/plugin.json

The generated files follow OpenAI's portable Agent Plugins format
(https://developers.openai.com/plugins/build/plugins.md). Skills are not
copied: ChatGPT and Codex discover plugins/<name>/skills/<skill>/SKILL.md
from the same folders Claude Code uses. Agents (plugins/<name>/agents/)
have no OpenAI plugin equivalent and are left out. The portable schema
allows no extra top-level keys, so the generated files carry no
"do not edit" marker; scripts/validate.sh enforces it instead.

Usage:
  scripts/build-openai.py          write the generated files
  scripts/build-openai.py --check  exit 1 if any generated file is stale
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

# OpenAI-only settings with no Claude equivalent. Category values are shown
# in the ChatGPT and Codex plugin directory.
OPENAI = {
    "code": {"displayName": "Code", "category": "Coding"},
    "work": {
        "displayName": "Work",
        "category": "Productivity",
        "onboardingSkill": "./skills/setup/SKILL.md",
    },
    "reflect": {"displayName": "Reflect", "category": "Productivity"},
}

# Root plugin.json fields copied from .claude-plugin/plugin.json as-is.
PORTABLE_FIELDS = (
    "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords",
)


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    """Return {path: text} for every generated file."""
    market = load(ROOT / ".claude-plugin" / "marketplace.json")
    owner = market.get("owner", {}).get("name", market["name"])
    out = {}
    entries = []

    for entry in market["plugins"]:
        name = entry["name"]
        source = entry["source"]
        if not isinstance(source, str):
            raise SystemExit(f"{name}: only local ./ sources are supported")
        if name not in OPENAI:
            raise SystemExit(
                f"{name}: add an OPENAI entry (displayName, category) "
                "in scripts/build-openai.py"
            )
        extra = OPENAI[name]
        pdir = ROOT / source
        claude = load(pdir / ".claude-plugin" / "plugin.json")

        interface = {
            "displayName": extra["displayName"],
            "shortDescription": entry["description"],
            "longDescription": claude["description"],
            "developerName": claude.get("author", {}).get("name", owner),
            "category": extra["category"],
        }
        if "homepage" in claude:
            interface["websiteURL"] = claude["homepage"]

        openai = {"interface": interface}
        if "onboardingSkill" in extra:
            skill = pdir / extra["onboardingSkill"]
            if not skill.is_file():
                raise SystemExit(f"{name}: onboardingSkill {skill} not found")
            openai["onboardingSkill"] = extra["onboardingSkill"]

        manifest = {"$schema": PLUGIN_SCHEMA}
        manifest.update({k: claude[k] for k in PORTABLE_FIELDS if k in claude})
        manifest["extensions"] = {"com.openai": openai}
        out[pdir / "plugin.json"] = dump(manifest)

        entries.append({
            "name": name,
            "source": {"source": "local", "path": source},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": extra["category"],
        })

    out[ROOT / ".agents" / "plugins" / "marketplace.json"] = dump({
        "name": market["name"],
        "interface": {"displayName": market["name"]},
        "plugins": entries,
    })
    return out


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for path, text in build().items():
        rel = path.relative_to(ROOT)
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current == text:
            continue
        if check:
            stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote: {rel}")
    if stale:
        for rel in stale:
            print(f"FAIL: {rel} is stale; run scripts/build-openai.py", file=sys.stderr)
        sys.exit(1)
    if check:
        print("OpenAI configs match")


if __name__ == "__main__":
    main()
