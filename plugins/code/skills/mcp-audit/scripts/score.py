#!/usr/bin/env python3
"""Validate audit inputs, compute the score, and assemble the audit outputs.

Usage:
    python3 -I score.py <audit_dir> [--rubric path/to/rubric.json]

Reads from <audit_dir>:
    checks.json    required  server facts + one result per rubric check
    changes.json   required  proposed changes (may be an empty list)
    metrics.json   optional  output of catalog_metrics.py

Writes to <audit_dir>:
    mcp-audit.json  final machine-readable audit
    scorecard.md    scorecard, change list, and metrics sections for the report

Exits 1 and prints every problem if the inputs are invalid. Nothing is written
in that case. Fix the inputs and rerun.
"""
import argparse
import json
import os
import re
import sys

RESULTS = {"pass", "partial", "fail", "na", "advisory"}
CONFIDENCE = {"verified", "static"}
EFFORT = {"S", "M", "L"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
DEFAULT_RUBRIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "rubric.json")


def load_json(path, required=True):
    if not os.path.exists(path):
        if required:
            raise SystemExit(f"error: missing {path}")
        return None
    with open(path) as f:
        return json.load(f)


def round_half_up(x):
    return int(x + 0.5)


class Rubric:
    def __init__(self, data):
        self.data = data
        self.cap_score = data["cap_score"]
        self.grades = sorted(data["grades"], key=lambda g: -g["min"])
        self.thresholds = data["per_tool_thresholds"]
        self.categories = data["categories"]
        self.checks = {}
        for cat in self.categories:
            for c in cat["checks"]:
                self.checks[c["id"]] = dict(c, category=cat["id"])

    def grade(self, score):
        for g in self.grades:
            if score >= g["min"]:
                return g["grade"]
        return self.grades[-1]["grade"]


def derive_per_tool_result(score, thresholds):
    if score >= thresholds["pass"]:
        return "pass"
    if score >= thresholds["partial"]:
        return "partial"
    return "fail"


def normalize_checks(rubric, checks_doc, errors):
    """Return {check_id: normalized result} after validation and version gating."""
    server = checks_doc.get("server") or {}
    pv = server.get("protocol_version")
    if pv is not None and not DATE_RE.match(str(pv)):
        errors.append(f"server.protocol_version must be YYYY-MM-DD or null, got {pv!r}")
        pv = None

    seen = {}
    for i, c in enumerate(checks_doc.get("checks") or []):
        cid = c.get("id")
        where = f"checks[{i}] ({cid})"
        if cid not in rubric.checks:
            errors.append(f"{where}: unknown check id")
            continue
        if cid in seen:
            errors.append(f"{where}: duplicate result for {cid}")
            continue
        spec = rubric.checks[cid]
        result = c.get("result")
        if result not in RESULTS:
            errors.append(f"{where}: result must be one of {sorted(RESULTS)}")
            continue
        conf = c.get("confidence")
        if result not in ("na",) and conf not in CONFIDENCE:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}")
        if c.get("cap_triggered") and not spec.get("cap"):
            errors.append(f"{where}: cap_triggered set on a check that has no cap")
        if not c.get("note"):
            errors.append(f"{where}: note is required (one line of evidence or reason)")

        score = c.get("score")
        if score is not None and not (isinstance(score, (int, float)) and 0 <= score <= 1):
            errors.append(f"{where}: score must be a number in [0, 1]")
            continue

        norm = {
            "id": cid,
            "title": spec["title"],
            "category": spec["category"],
            "weight": spec["weight"],
            "per_tool": spec["per_tool"],
            "result": result,
            "score": None,
            "confidence": conf,
            "note": c.get("note", ""),
            "cap_triggered": bool(c.get("cap_triggered")),
            "spec_violation": bool(c.get("spec_violation")),
            "version_gated": False,
        }

        min_v = spec.get("min_version")
        if min_v and result != "na" and (pv is None or pv < min_v):
            norm["version_gated"] = True
            norm["result"] = "advisory"
            norm["requires_version"] = min_v

        if norm["result"] in ("na", "advisory"):
            norm["score"] = None
            if norm["result"] == "advisory" and score is not None:
                norm["advisory_score"] = score
        elif spec["per_tool"]:
            if score is None:
                errors.append(f"{where}: per-tool check needs score = fraction of tools passing")
                continue
            norm["score"] = float(score)
            derived = derive_per_tool_result(score, rubric.thresholds)
            if result != derived:
                norm["normalized_from"] = result
            norm["result"] = derived
        else:
            base = {"pass": 1.0, "partial": 0.5, "fail": 0.0}[result]
            if score is not None:
                if result == "pass" and score < 1:
                    errors.append(f"{where}: pass must not carry a score below 1")
                if result == "fail" and score > 0:
                    errors.append(f"{where}: fail must not carry a score above 0")
                if result == "partial" and not (0 < score < 1):
                    errors.append(f"{where}: partial score must be strictly between 0 and 1")
                base = float(score)
            norm["score"] = base

        seen[cid] = norm

    for cid in rubric.checks:
        if cid not in seen:
            errors.append(f"missing result for {cid} (use result 'na' with a note if it does not apply)")
    return seen


def compute(rubric, results, overrides=None):
    """Compute overall score. overrides: set of check ids to treat as fully passing."""
    overrides = overrides or set()
    cats = []
    for cat in rubric.categories:
        possible = earned = 0.0
        for c in cat["checks"]:
            r = results[c["id"]]
            if r["result"] in ("na", "advisory"):
                continue
            s = 1.0 if c["id"] in overrides else r["score"]
            possible += c["weight"]
            earned += c["weight"] * s
        cats.append({"cat": cat, "possible": possible, "frac": (earned / possible) if possible else None})

    active_weight = sum(x["cat"]["weight"] for x in cats if x["frac"] is not None)
    raw = 0.0
    for x in cats:
        if x["frac"] is None or not active_weight:
            x["effective_weight"] = 0.0
            x["earned"] = 0.0
            continue
        x["effective_weight"] = x["cat"]["weight"] * 100.0 / active_weight
        x["earned"] = x["effective_weight"] * x["frac"]
        raw += x["earned"]

    cap_reasons = [
        f"{r['id']} ({r['title']}): {r['note']}" for r in results.values()
        if r["cap_triggered"] and r["result"] not in ("na", "advisory") and r["id"] not in overrides
    ]
    capped_value = min(raw, rubric.cap_score) if cap_reasons else raw
    return {"raw": raw, "value": capped_value, "cap_reasons": cap_reasons, "categories": cats}


def priority_for(change, results):
    refs = [results[cid] for cid in change["check_ids"] if cid in results]
    live = [r for r in refs if r["result"] not in ("na", "advisory")]
    if any(r["cap_triggered"] or r["spec_violation"] for r in live):
        return "P0"
    if any(r["weight"] == 3 and r["result"] != "pass" for r in live):
        return "P1"
    return "P2"


def validate_changes(changes, rubric, results, errors, warnings):
    if not isinstance(changes, list):
        errors.append("changes.json must be a JSON array")
        return []
    out = []
    for i, ch in enumerate(changes):
        where = f"changes[{i}] ({ch.get('title', 'untitled')})"
        ok = True
        for field in ("title", "evidence", "change"):
            if not isinstance(ch.get(field), str) or not ch[field].strip():
                errors.append(f"{where}: {field} is required")
                ok = False
        ids = ch.get("check_ids")
        if not isinstance(ids, list) or not ids:
            errors.append(f"{where}: check_ids must be a non-empty list")
            ok = False
        else:
            for cid in ids:
                if cid not in rubric.checks:
                    errors.append(f"{where}: unknown check id {cid}")
                    ok = False
                elif (cid in results and results[cid]["result"] == "pass"
                      and not results[cid]["cap_triggered"] and not results[cid]["spec_violation"]):
                    warnings.append(f"{where}: references {cid}, which passed")
        locs = ch.get("locations")
        if not isinstance(locs, list) or not locs:
            errors.append(f"{where}: locations must list at least one {{file, line}}")
            ok = False
        else:
            for loc in locs:
                if not isinstance(loc, dict) or not loc.get("file"):
                    errors.append(f"{where}: each location needs a file")
                    ok = False
                elif "line" in loc and not (isinstance(loc["line"], int) and loc["line"] >= 1):
                    errors.append(f"{where}: location line must be a positive integer")
                    ok = False
        if ch.get("effort") not in EFFORT:
            errors.append(f"{where}: effort must be one of {sorted(EFFORT)}")
            ok = False
        if not isinstance(ch.get("breaking"), bool):
            errors.append(f"{where}: breaking must be true or false")
            ok = False
        if ok:
            out.append(ch)

    referenced = {cid for ch in out for cid in ch["check_ids"]}
    for r in results.values():
        if r["id"] in referenced:
            continue
        if r["result"] in ("partial", "fail"):
            errors.append(f"{r['id']} is {r['result']} but no change addresses it")
        elif r["result"] == "pass" and (r["cap_triggered"] or r["spec_violation"]):
            errors.append(f"{r['id']} has cap_triggered or spec_violation but no change addresses it")
    return out


def render_scorecard(final):
    s = final["score"]
    lines = ["## Scorecard", ""]
    lines.append(f"**Overall: {s['overall']} / 100 ({s['grade']})**"
                 + (f", capped from {s['raw']:.1f}. Clearing every cap restores the uncapped score."
                    if s["capped"] else ""))
    if s["cap_reasons"]:
        lines += ["", "Cap reasons:"] + [f"- {c}" for c in s["cap_reasons"]]
    lines += ["", "| Category | Weight | Effective weight | Earned | Not passing |",
              "|---|---|---|---|---|"]
    for c in s["categories"]:
        failing = ", ".join(ch["id"] for ch in c["checks"] if ch["result"] in ("partial", "fail")) or "none"
        status = f"{c['earned']:.1f}" if c["effective_weight"] else "n/a"
        lines.append(f"| {c['id']} {c['title']} | {c['weight']} | {c['effective_weight']:.1f} | {status} | {failing} |")
    if s["advisory"]:
        lines += ["", "Advisory (zero weight): " + ", ".join(s["advisory"])]

    lines += ["", "## Changes", ""]
    if not final["changes"]:
        lines.append("No changes proposed.")
    for p in ("P0", "P1", "P2"):
        group = [c for c in final["changes"] if c["priority"] == p]
        if not group:
            continue
        lines += [f"### {p}", ""]
        for c in group:
            locs = ", ".join(f"`{l['file']}" + (f":{l['line']}" if l.get("line") else "") + "`"
                             for l in c["locations"])
            lines.append(f"#### {c['id']}: {c['title']}")
            lines.append("")
            lines.append(f"- Checks: {', '.join(c['check_ids'])}")
            if c.get("tools"):
                lines.append(f"- Tools: {', '.join('`' + t + '`' for t in c['tools'])}")
            lines.append(f"- Locations: {locs}")
            lines.append(f"- Effort: {c['effort']}. Breaking: {'yes' if c['breaking'] else 'no'}. "
                         f"Uncapped score gain if fully fixed: up to +{c['score_delta']:.1f}")
            if c["clears_caps"]:
                lines.append(f"- Clears cap: {', '.join(c['clears_caps'])}")
            lines.append(f"- Evidence: {c['evidence']}")
            lines.append(f"- Change: {c['change']}")
            if c.get("patch"):
                lines += ["", "```diff", c["patch"].rstrip("\n"), "```"]
            lines.append("")

    m = final.get("metrics")
    if m:
        lines += ["## Catalog metrics", "",
                  "| Metric | Value |", "|---|---|",
                  f"| Tools | {m.get('tool_count')} |",
                  f"| Estimated tokens (total / median / max) | {m.get('est_tokens_total')} / "
                  f"{m.get('est_tokens_median')} / {m.get('est_tokens_max')} |",
                  f"| Prefix coverage | {m.get('prefix_coverage')} |",
                  f"| Name grammar pass rate | {m.get('name_grammar_pass_rate')} |",
                  f"| outputSchema rate | {m.get('output_schema_rate')} |",
                  f"| Fully annotated rate | {m.get('full_annotation_rate')} |",
                  f"| Duplicate names | {', '.join(m.get('duplicate_names') or []) or 'none'} |"]
        nd = m.get("near_duplicates") or []
        if nd:
            lines += ["", "Near-duplicate candidates:", ""] + [
                f"- `{d['a']}` / `{d['b']}` (Jaccard {d['jaccard']})" for d in nd[:25]]
            if len(nd) > 25:
                lines.append(f"- ...and {len(nd) - 25} more in metrics.json")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audit_dir")
    ap.add_argument("--rubric", default=DEFAULT_RUBRIC)
    args = ap.parse_args()

    rubric = Rubric(load_json(args.rubric))
    checks_doc = load_json(os.path.join(args.audit_dir, "checks.json"))
    changes_in = load_json(os.path.join(args.audit_dir, "changes.json"))
    metrics = load_json(os.path.join(args.audit_dir, "metrics.json"), required=False)

    errors, warnings = [], []
    results = normalize_checks(rubric, checks_doc, errors)
    changes = validate_changes(changes_in, rubric, results, errors, warnings)
    if errors:
        print(f"{len(errors)} problem(s) in audit inputs:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    base = compute(rubric, results)
    overall = round_half_up(base["value"])
    for ch in changes:
        fixed = compute(rubric, results, overrides=set(ch["check_ids"]))
        # Gain in the uncapped score, so changes stay comparable while a cap is in force.
        ch["score_delta"] = round(max(fixed["raw"] - base["raw"], 0.0), 1)
        ch["clears_caps"] = sorted(
            cid for cid in ch["check_ids"]
            if results[cid]["cap_triggered"] and results[cid]["result"] not in ("na", "advisory"))
        ch["priority"] = priority_for(ch, results)
    changes.sort(key=lambda c: (PRIORITY_ORDER[c["priority"]], -len(c["clears_caps"]), -c["score_delta"], c["title"]))
    for n, ch in enumerate(changes, 1):
        ch["id"] = f"CHG-{n:03d}"

    categories = []
    for x in base["categories"]:
        cat = x["cat"]
        categories.append({
            "id": cat["id"],
            "title": cat["title"],
            "weight": cat["weight"],
            "effective_weight": round(x["effective_weight"], 2),
            "earned": round(x["earned"], 2),
            "checks": [results[c["id"]] for c in cat["checks"]],
        })

    key_order = ["id", "priority", "title", "check_ids", "tools", "locations", "evidence",
                 "change", "patch", "effort", "breaking", "score_delta", "clears_caps"]
    final = {
        "rubric_version": rubric.data["rubric_version"],
        "server": checks_doc.get("server") or {},
        "score": {
            "overall": overall,
            "raw": round(base["raw"], 2),
            "grade": rubric.grade(overall),
            "capped": bool(base["cap_reasons"]),
            "cap_reasons": base["cap_reasons"],
            "advisory": [r["id"] for r in results.values() if r["result"] == "advisory"],
            "categories": categories,
        },
        "metrics": metrics,
        "changes": [{k: ch[k] for k in key_order if k in ch} for ch in changes],
    }

    with open(os.path.join(args.audit_dir, "mcp-audit.json"), "w") as f:
        json.dump(final, f, indent=2)
    with open(os.path.join(args.audit_dir, "scorecard.md"), "w") as f:
        f.write(render_scorecard(final))

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(f"score {overall}/100 ({final['score']['grade']})"
          + (" [capped]" if final["score"]["capped"] else "")
          + f", {len(changes)} changes "
          + "(" + ", ".join(f"{p}: {sum(c['priority'] == p for c in changes)}" for p in ("P0", "P1", "P2")) + ")")


if __name__ == "__main__":
    main()
