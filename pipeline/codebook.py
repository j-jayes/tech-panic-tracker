"""Generate docs/codebook.md from schemas/datapackage.json + data/vocab/.

Constitution Principle VI: the codebook is generated, never hand-maintained.
Run: python -m pipeline.codebook [--strict]
  --strict: fail if any enum value lacks a definition in enum_definitions.csv
            (activates once all definitions are written; warn-only until then).
"""

from __future__ import annotations

import json
import sys
from datetime import date

import pandas as pd

from pipeline import DATAPACKAGE, REPO_ROOT

VOCAB = REPO_ROOT / "data" / "vocab"
OUT = REPO_ROOT / "docs" / "codebook.md"


def build_codebook() -> tuple[str, list[str]]:
    descriptor = json.loads(DATAPACKAGE.read_text(encoding="utf-8"))
    defs = pd.read_csv(VOCAB / "enum_definitions.csv", dtype=str, keep_default_na=False)
    def_map = {(r["enum_name"], r["value"]): r["definition"] for _, r in defs.iterrows()}
    # Field aliases share the base field's definitions
    aliases = {
        "second_verdict": "verdict",
        "author_type_at_prediction": "author_type",
        "second_decision": "decision",
        "track": "retrieval_track",
    }
    for alias, base in aliases.items():
        for (name, value), d in list(def_map.items()):
            if name == base:
                def_map.setdefault((alias, value), d)
    tech = pd.read_csv(VOCAB / "technologies.csv", dtype=str, keep_default_na=False)

    missing: list[str] = []
    lines = [
        "# Tech-Panic Tracker Codebook",
        "",
        f"**GENERATED FILE — do not edit by hand.** Regenerate with `python -m pipeline.codebook`. Source of truth: `schemas/datapackage.json` + `data/vocab/`. Generated {date.today().isoformat()}.",
        "",
        "Prose coding rules (inclusion criteria, revisit-vs-new-prediction rule, apocryphal-quote hazards, worked examples) live in `docs/PLAN.md` and `protocol/`; this file documents the machine schema.",
        "",
    ]

    for res in descriptor["resources"]:
        lines += [f"## Table: `{res['name']}`", "", f"Path: `{res['path'].lstrip('./')}`", "", "| Field | Type | Required | Constraints / definition |", "|---|---|---|---|"]
        for f in res["schema"]["fields"]:
            c = f.get("constraints", {})
            required = "yes" if c.get("required") else ""
            notes = []
            if "enum" in c:
                notes.append("enum (see below)")
            if "pattern" in c:
                notes.append(f"pattern `{c['pattern']}`")
            if f.get("description"):
                notes.append(f["description"])
            lines.append(f"| `{f['name']}` | {f['type']} | {required} | {'; '.join(notes)} |")
        lines.append("")
        # enum value tables
        for f in res["schema"]["fields"]:
            enum = f.get("constraints", {}).get("enum")
            if not enum:
                continue
            lines += [f"### `{res['name']}.{f['name']}` values", "", "| Value | Definition |", "|---|---|"]
            for v in enum:
                d = def_map.get((f["name"], v), "")
                if not d:
                    missing.append(f"{f['name']}={v}")
                    d = "*(definition pending)*"
                lines.append(f"| `{v}` | {d} |")
            lines.append("")

    lines += ["## Controlled vocabulary: technologies", "", "| tech_id | Label | Generality | Parent | First commercial year | Definition |", "|---|---|---|---|---|---|"]
    for _, r in tech.iterrows():
        lines.append(f"| `{r['tech_id']}` | {r['label']} | {r['generality']} | {r['parent_tech_id']} | {r['first_commercial_year']} | {r['definition']} |")
    lines.append("")
    return "\n".join(lines), sorted(set(missing))


def main() -> int:
    strict = "--strict" in sys.argv
    content, missing = build_codebook()
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT}")
    if missing:
        print(f"{len(missing)} enum value(s) lack definitions in enum_definitions.csv:")
        for m in missing:
            print(f"  {m}")
        if strict:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
