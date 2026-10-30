#!/usr/bin/env python3
"""Compute catalog metrics for an MCP server audit.

Usage:
    python3 -I catalog_metrics.py <tools.json> [--out metrics.json]

<tools.json> is either {"tools": [...]} (a tools/list result) or a bare list of
tool definitions. Prints metrics JSON to stdout, or writes it to --out.

Token estimates are characters / 4: relative sizes, not exact counts.
Near-duplicate pairs (Jaccard >= 0.6 over name + description words, stopwords
removed) are review candidates, not automatic failures.
"""
import argparse
import itertools
import json
import re
import statistics
import sys

NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
WORD_RE = re.compile(r"[a-z0-9]+")
STOP = {
    "a", "an", "the", "of", "to", "for", "in", "on", "and", "or", "by", "with",
    "is", "this", "that", "it", "from", "as", "be", "returns", "return", "get",
    "use", "when", "you", "your", "can", "will", "all", "any",
}
ANNOTATION_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")
NEAR_DUP_THRESHOLD = 0.6


def words(text):
    return {w for w in WORD_RE.findall(text.lower()) if w not in STOP}


def prop_paths(schema, prefix=""):
    """Yield (path, subschema) for every property, recursing into objects and arrays."""
    if not isinstance(schema, dict):
        return
    for name, sub in (schema.get("properties") or {}).items():
        path = f"{prefix}{name}"
        yield path, sub
        yield from prop_paths(sub, path + ".")
        if isinstance(sub, dict) and isinstance(sub.get("items"), dict):
            yield from prop_paths(sub["items"], path + "[].")


def max_depth(schema, depth=0):
    if not isinstance(schema, dict):
        return depth
    children = list((schema.get("properties") or {}).values())
    if isinstance(schema.get("items"), dict):
        children.append(schema["items"])
    if not children:
        return depth
    return max(max_depth(c, depth + 1) for c in children)


def prefix_of(name):
    m = re.match(r"^([A-Za-z0-9]+)[_.-]", name)
    return m.group(1).lower() if m else None


def load_tools(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        if "tools" in data:
            return data["tools"]
        if isinstance(data.get("result"), dict) and "tools" in data["result"]:
            return data["result"]["tools"]  # raw JSON-RPC response
        raise SystemExit(f"error: {path} has no 'tools' array")
    if isinstance(data, list):
        return data
    raise SystemExit(f"error: {path} is not a tool list")


def analyze(tools):
    recs, counts = [], {}
    for t in tools:
        name = t.get("name", "")
        desc = t.get("description") or ""
        schema = t.get("inputSchema")
        props = list(prop_paths(schema)) if isinstance(schema, dict) else []
        ann = t.get("annotations") or {}
        counts[name] = counts.get(name, 0) + 1
        recs.append({
            "name": name,
            "est_tokens": len(json.dumps(t)) // 4,
            "name_grammar_ok": bool(NAME_RE.match(name)),
            "has_title": bool(t.get("title") or ann.get("title")),
            "description_chars": len(desc),
            "input_schema_is_object": isinstance(schema, dict) and schema.get("type") == "object",
            "input_schema_depth": max_depth(schema) if isinstance(schema, dict) else None,
            "props_total": len(props),
            "props_missing_description": [
                p for p, s in props if not (isinstance(s, dict) and s.get("description"))
            ],
            "has_output_schema": isinstance(t.get("outputSchema"), dict),
            "annotations_missing": [k for k in ANNOTATION_KEYS if k not in ann],
            "prefix": prefix_of(name),
        })

    toks = [r["est_tokens"] for r in recs] or [0]
    bags = [(t.get("name", ""), words(t.get("name", "") + " " + (t.get("description") or "")))
            for t in tools]
    near = []
    for (a, wa), (b, wb) in itertools.combinations(bags, 2):
        if wa and wb:
            j = len(wa & wb) / len(wa | wb)
            if j >= NEAR_DUP_THRESHOLD:
                near.append({"a": a, "b": b, "jaccard": round(j, 3)})

    n = max(len(tools), 1)
    return {
        "tool_count": len(tools),
        "est_tokens_total": sum(toks),
        "est_tokens_median": statistics.median(toks),
        "est_tokens_max": max(toks),
        "prefix_coverage": round(sum(1 for r in recs if r["prefix"]) / n, 3),
        "name_grammar_pass_rate": round(sum(r["name_grammar_ok"] for r in recs) / n, 3),
        "title_rate": round(sum(r["has_title"] for r in recs) / n, 3),
        "output_schema_rate": round(sum(r["has_output_schema"] for r in recs) / n, 3),
        "full_annotation_rate": round(sum(not r["annotations_missing"] for r in recs) / n, 3),
        "duplicate_names": sorted(nm for nm, c in counts.items() if c > 1),
        "near_duplicates": sorted(near, key=lambda x: -x["jaccard"]),
        "tools": recs,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tools_json")
    ap.add_argument("--out")
    args = ap.parse_args()
    result = analyze(load_tools(args.tools_json))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"wrote {args.out}: {result['tool_count']} tools, "
              f"~{result['est_tokens_total']} tokens, "
              f"{len(result['near_duplicates'])} near-duplicate pairs", file=sys.stderr)
    else:
        json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
