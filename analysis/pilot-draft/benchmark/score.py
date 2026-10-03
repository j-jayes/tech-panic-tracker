#!/usr/bin/env python3
"""Score every model run against the Roodman-Massenkoff extraction and write the report tables.

    .venv/bin/python analysis/pilot-draft/benchmark/score.py

Reads data/interim/benchmark/runs/ and the gold workbook in data/raw/; writes
tracked CSVs to analysis/pilot-draft/data/benchmark-*.csv.
"""

from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
GOLD_XLSX = REPO_ROOT / "data" / "raw" / "roodman-massenkoff-2026-extraction-full-v69.xlsx"
RUNS = REPO_ROOT / "data" / "interim" / "benchmark" / "runs"
TEXT = REPO_ROOT / "data" / "interim" / "benchmark" / "text"
CALLS = REPO_ROOT / "data" / "interim" / "benchmark" / "calls.jsonl"
OUT = HERE.parent / "data"

MODEL_ORDER = ["gemini-3.8-flash", "gemini-3.1-pro", "claude-opus-5", "gpt-5.6-terra", "deepseek-v4.1-flash"]
H = ["st", "mt", "lt"]
CATEGORICAL = ["training_role", "mandatory_voluntary", "funding_public_private", "admin_public_private", "outcome_data_source_type"]
BINARY = ["has_classroom", "has_ojt", "has_jsa", "has_multiple_components", "sector_program"]
FIELD_GROUP = {
    **{f: "classification" for f in ["training_role", "mandatory_voluntary", "funding_public_private", "admin_public_private"] + BINARY},
    **{f: "design" for f in ["randomization_period", "n_treatment", "n_control", "outcome_data_source_type", "treatment_duration_months", "program_takeup_impact"]},
    **{f"{h}_emp_{k}": "employment" for h in H for k in ["impact", "se", "stars", "control_mean"]},
    **{f"{h}_earn_{k}": "earnings" for h in H for k in ["impact", "se", "stars", "control_mean"]},
    "cost_per_treated": "cost",
}
SCORED = list(FIELD_GROUP)
IMPACTS = [f"{h}_{o}_impact" for h in H for o in ["emp", "earn"]]

# Gold cells whose source the models were not given: the NSW earnings series for
# AFDC women and young dropouts come from Couch (1992), which is not openly available.
UNAVAILABLE = [("National Supported Work Demonstration", r"AFDC|dropout", r"_earn_")]

STOP = {"the", "of", "and", "site", "sites", "program", "programs", "group", "sample", "full", "vs", "all", "a", "in", "at"}


# --- normalisation ---------------------------------------------------------------

def isnull(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and v.strip() == "")


def tokens(s: str, drop: set[str]) -> set[str]:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    out = set()
    for t in re.split(r"[^a-z0-9]+", s):
        if not t or t in STOP or t in drop:
            continue
        out.add(t[:-1] if len(t) > 3 and t.endswith("s") else t)
    return out


def parse_cadence_months(s) -> float | None:
    """Months covered by one gold earnings figure, from the free-text cadence string."""
    if isnull(s):
        return None
    s = str(s).lower().strip()
    if s.startswith("annual"):
        return 12.0
    if s.startswith("monthly"):
        return 1.0
    if s.startswith("weekly"):
        return 12 / 52
    if s.startswith("quarterly"):
        return 3.0
    m = re.search(r"months?\s*(\d+)\s*[-–]\s*(\d+)", s)
    if m:
        return float(int(m.group(2)) - int(m.group(1)) + 1)
    m = re.search(r"q(\d+)\s*[-–]\s*q?(\d+)", s)
    if m:
        return 3.0 * (int(m.group(2)) - int(m.group(1)) + 1)
    m = re.search(r"over (\d+) quarters", s)
    if m:
        return 3.0 * int(m.group(1))
    return None


MODEL_CADENCE_MONTHS = {"weekly": 12 / 52, "monthly": 1.0, "quarterly": 3.0, "annual": 12.0}


def model_period_months(rec: dict, h: str) -> float | None:
    p = rec.get(f"{h}_earn_period_months")
    if not isnull(p) and p > 0:
        return float(p)
    return MODEL_CADENCE_MONTHS.get(rec.get(f"{h}_earn_cadence") or "")


def outcome_source_type(s) -> str | None:
    if isnull(s):
        return None
    s = str(s).lower()
    hits = set()
    if re.search(r"survey|self-report|interview", s):
        hits.add("survey")
    if re.search(r"\bndnh\b|new hires", s):
        hits.add("ndnh")
    elif re.search(r"\bui\b|unemployment insurance", s):
        hits.add("ui_wage_records")
    if re.search(r"\bssa\b|social security", s):
        hits.add("ssa")
    if len(hits) > 1:
        return "mixed"
    return hits.pop() if hits else "other_admin"


MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_period(s):
    """-> ((y, m|None), (y, m|None)) or None."""
    if isnull(s):
        return None
    s = str(s).lower()
    found = re.findall(r"(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?((?:19|20)\d\d)", s)
    if not found:
        return None
    pts = [(int(y), MONTHS.get(mo)) for mo, y in found]
    return pts[0], pts[-1]


def stars_norm(stars, impact) -> str | None:
    if not isnull(stars):
        return str(stars).strip() if str(stars).strip() in ("*", "**", "***") else "ns"
    return "ns" if not isnull(impact) else None


def signsig(impact, se, stars) -> str | None:
    if isnull(impact):
        return None
    if not isnull(se) and se > 0:
        sig = abs(impact / se) >= 1.645  # 10% level, matching the one-star threshold
    else:
        st = stars_norm(stars, impact)
        sig = st in ("*", "**", "***")
    if not sig:
        return "ns"
    return "pos_sig" if impact > 0 else "neg_sig"


# --- cell scoring ------------------------------------------------------------

def close(g: float, m: float, abs_tol: float | None = None, rel_tol: float | None = None) -> bool:
    if abs_tol is not None and abs(g - m) <= abs_tol + 1e-9:
        return True
    if rel_tol is not None and abs(g - m) <= rel_tol * max(abs(g), 1e-9) + 1e-9:
        return True
    return False


def score_cell(field: str, g, m, g_row: dict, m_row: dict) -> dict:
    """Returns outcome plus the normalised values that were compared."""
    h = field[:2]
    note = ""
    # normalise both sides
    if field in BINARY:
        gn = None if isnull(g) else bool(int(float(g)))
        mn = None if isnull(m) else bool(m)
    elif field == "outcome_data_source_type":
        gn = outcome_source_type(g_row.get("outcome_data_source"))
        mn = None if isnull(m) else m
    elif field in CATEGORICAL:
        gn = None if isnull(g) else str(g).strip().lower()
        mn = None if isnull(m) else str(m).strip().lower()
    elif field.endswith("_stars"):
        imp = field.replace("_stars", "_impact")
        gn = stars_norm(g, g_row.get(imp))
        mn = stars_norm(m, m_row.get(imp))
    elif field == "randomization_period":
        gn, mn = parse_period(g), parse_period(m)
    else:
        gn = None if isnull(g) else float(g)
        mn = None if isnull(m) else float(m)
        if field.endswith("emp_control_mean") and gn is not None and mn is not None:
            if gn <= 1 < mn:
                gn, note = gn * 100, "gold fraction rescaled"
            elif mn <= 1 < gn:
                mn, note = mn * 100, "model fraction rescaled"
        if "_earn_" in field and gn is not None and mn is not None:
            gm, mm = parse_cadence_months(g_row.get(f"{h}_earn_cadence")), model_period_months(m_row, h)
            raw_match = close(gn, mn, rel_tol=0.05 if not field.endswith("_se") else 0.10)
            if gm and mm:
                gn, mn = gn * 12 / gm, mn * 12 / mm
                note = f"annualised (gold x{12/gm:g}, model x{12/mm:g}); raw {'match' if raw_match else 'mismatch'}"
            else:
                note = f"compared raw (cadence unparsed: gold={gm}, model={mm})"

    if gn is None and mn is None:
        outcome = "both_null"
    elif mn is None:
        outcome = "abstained"
    elif gn is None:
        outcome = "extra_value"
    else:
        if field in BINARY or field in CATEGORICAL or field.endswith("_stars"):
            ok = gn == mn
        elif field == "randomization_period":
            (gs, ge), (ms, me) = gn, mn
            if all(x[1] for x in (gs, ge, ms, me)):
                ok = abs((gs[0] * 12 + gs[1]) - (ms[0] * 12 + ms[1])) <= 1 and abs((ge[0] * 12 + ge[1]) - (me[0] * 12 + me[1])) <= 1
            else:
                ok = gs[0] == ms[0] and ge[0] == me[0]
        elif field in ("n_treatment", "n_control"):
            ok = close(gn, mn, rel_tol=0.02)
        elif field == "treatment_duration_months":
            ok = close(gn, mn, abs_tol=1.0)
        elif field.endswith("emp_se"):
            ok = close(gn, mn, abs_tol=0.5)
        elif field.endswith("earn_se"):
            ok = close(gn, mn, rel_tol=0.10)
        elif "_earn_" in field or field == "cost_per_treated":
            ok = close(gn, mn, rel_tol=0.05)
        else:  # percentage points: employment impacts, control means, take-up
            ok = close(gn, mn, abs_tol=0.5, rel_tol=0.05)
        outcome = "match" if ok else "mismatch"
    fmt = lambda v: "" if v is None else (f"{v[0]}-{v[1]}" if isinstance(v, tuple) else str(round(v, 4) if isinstance(v, float) else v))
    return {"outcome": outcome, "gold_norm": fmt(gn), "model_norm": fmt(mn), "note": note}


# --- alignment ---------------------------------------------------------------

def align_rows(project: str, gold_units: list[str], model_recs: list[dict]) -> list[tuple[int | None, int | None, str, float]]:
    """Returns (gold_idx, model_idx, method, score) tuples covering every gold and model row."""
    drop = tokens(project, set())
    gt = [tokens(u, drop) for u in gold_units]
    mt = [tokens(r["site_subgroup"], drop) for r in model_recs]
    pairs, used_g, used_m = [], set(), set()
    cands = []
    for i, a in enumerate(gt):
        for j, b in enumerate(mt):
            if a and b:
                sc = len(a & b) / min(len(a), len(b))
                if a == b:
                    sc = 2.0
                cands.append((sc, -i, -j, i, j))
    for sc, _, _, i, j in sorted(cands, reverse=True):
        if sc < 0.5 or i in used_g or j in used_m:
            continue
        pairs.append((i, j, "exact" if sc == 2.0 else "overlap", round(min(sc, 1.0), 2)))
        used_g.add(i)
        used_m.add(j)
    rest_g = [i for i in range(len(gold_units)) if i not in used_g]
    rest_m = [j for j in range(len(model_recs)) if j not in used_m]
    if len(gold_units) == 1 and rest_g and rest_m:
        if len(rest_m) == 1:
            pairs.append((0, rest_m[0], "singleton", 0.0))
        else:
            pooled = [j for j in rest_m if re.search(r"pool|all|full|total|overall", model_recs[j]["site_subgroup"], re.I)]
            j = pooled[0] if pooled else max(rest_m, key=lambda k: model_recs[k].get("n_treatment") or 0)
            pairs.append((0, j, "pooled_guess", 0.0))
        used_g.add(0)
        used_m.add(pairs[-1][1])
    pairs += [(i, None, "gold_missing", 0.0) for i in range(len(gold_units)) if i not in used_g]
    pairs += [(None, j, "extra", 0.0) for j in range(len(model_recs)) if j not in used_m]
    return pairs


# --- statistics --------------------------------------------------------------

def kappa(g: list, m: list) -> float:
    g, m = np.asarray(g, dtype=object), np.asarray(m, dtype=object)
    if len(g) == 0:
        return float("nan")
    cats = sorted(set(g) | set(m), key=str)
    po = float(np.mean(g == m))
    pe = sum(float(np.mean(g == c)) * float(np.mean(m == c)) for c in cats)
    return float("nan") if pe >= 1 else (po - pe) / (1 - pe)


# --- loading -----------------------------------------------------------------

def load_gold() -> pd.DataFrame:
    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        man = list(csv.DictReader(f))
    g = pd.read_excel(GOLD_XLSX, sheet_name="Data Table")
    g = g[g.project.isin([s["project"] for s in man])].copy()
    g["study_id"] = g.project.map({s["project"]: s["study_id"] for s in man})
    return g.reset_index(drop=True)


def load_runs() -> list[dict]:
    runs = []
    for p in sorted(RUNS.glob("*/*/pass*.json")):
        d = json.loads(p.read_text())
        d["model_key"] = p.parent.name
        runs.append(d)
    return runs


def unavailable(project: str, unit: str, field: str) -> bool:
    return any(project == p and re.search(u, unit) and re.search(f, field) for p, u, f in UNAVAILABLE)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    gold = load_gold()
    runs = load_runs()
    cells, align = [], []
    for run in runs:
        sid, mk, ps = run["study_id"], run["model_key"], run["pass"]
        g = gold[gold.study_id == sid]
        gunits = g.site_subgroup.tolist()
        recs = run["result"]["records"]
        for gi, mj, method, sc in align_rows(g.project.iloc[0], gunits, recs):
            align.append({"study_id": sid, "model": mk, "pass": ps, "gold_site_subgroup": gunits[gi] if gi is not None else "",
                          "model_site_subgroup": recs[mj]["site_subgroup"] if mj is not None else "", "method": method, "score": sc})
            if gi is None:
                continue
            grow = g.iloc[gi].to_dict()
            mrow = recs[mj] if mj is not None else {}
            for f in SCORED:
                base = {"study_id": sid, "project": grow["project"], "gold_site_subgroup": grow["site_subgroup"], "model": mk, "pass": ps,
                        "field": f, "field_group": FIELD_GROUP[f], "gold_value": grow.get(f if f != "outcome_data_source_type" else "outcome_data_source"),
                        "model_value": mrow.get(f) if mj is not None else None}
                if unavailable(grow["project"], grow["site_subgroup"], f):
                    cells.append({**base, "outcome": "source_unavailable", "gold_norm": "", "model_norm": "", "note": "gold from Couch (1992), not supplied"})
                elif mj is None:
                    cells.append({**base, "outcome": "gold_missing" if not isnull(base["gold_value"]) or f == "outcome_data_source_type" else "both_null",
                                  "gold_norm": "", "model_norm": "", "note": "no aligned model record"})
                else:
                    cells.append({**base, **score_cell(f, grow.get(f), mrow.get(f), grow, mrow)})
    cells = pd.DataFrame(cells)
    align = pd.DataFrame(align)

    # sign-and-significance agreement on impact cells where both sides report an impact
    ss = []
    for run in runs:
        sid, mk, ps = run["study_id"], run["model_key"], run["pass"]
        g = gold[gold.study_id == sid]
        recs = run["result"]["records"]
        for gi, mj, *_ in align_rows(g.project.iloc[0], g.site_subgroup.tolist(), recs):
            if gi is None or mj is None:
                continue
            grow, mrow = g.iloc[gi].to_dict(), recs[mj]
            for f in IMPACTS:
                if unavailable(grow["project"], grow["site_subgroup"], f):
                    continue
                gc = signsig(None if isnull(grow.get(f)) else float(grow[f]), None if isnull(grow.get(f.replace("impact", "se"))) else float(grow[f.replace("impact", "se")]), grow.get(f.replace("impact", "stars")))
                mc = signsig(mrow.get(f), mrow.get(f.replace("impact", "se")), mrow.get(f.replace("impact", "stars")))
                if gc and mc:
                    ss.append({"study_id": sid, "model": mk, "pass": ps, "gold_site_subgroup": grow["site_subgroup"], "field": f, "gold_class": gc, "model_class": mc, "agree": gc == mc})
    ss = pd.DataFrame(ss)

    def metrics(df: pd.DataFrame) -> dict:
        n_match = (df.outcome == "match").sum()
        n_mis = (df.outcome == "mismatch").sum()
        gold_nonnull = df.outcome.isin(["match", "mismatch", "abstained", "gold_missing"]).sum()
        return {"n_gold_cells": int(gold_nonnull), "n_match": int(n_match), "n_mismatch": int(n_mis),
                "n_abstained": int((df.outcome == "abstained").sum()), "n_gold_missing": int((df.outcome == "gold_missing").sum()),
                "n_extra_value": int((df.outcome == "extra_value").sum()),
                "accuracy": n_match / (n_match + n_mis) if n_match + n_mis else np.nan,
                "coverage": (n_match + n_mis) / gold_nonnull if gold_nonnull else np.nan,
                "recall": n_match / gold_nonnull if gold_nonnull else np.nan}

    calls = pd.DataFrame([json.loads(l) for l in CALLS.read_text().splitlines()]) if CALLS.exists() else pd.DataFrame()
    summary, groups, fk = [], [], []
    for (mk, ps), df in cells.groupby(["model", "pass"]):
        a = align[(align.model == mk) & (align["pass"] == ps)]
        usage = pd.DataFrame([r["usage"] | {"route": r.get("route", "")} for r in runs if r["model_key"] == mk and r["pass"] == ps])
        s = ss[(ss.model == mk) & (ss["pass"] == ps)] if len(ss) else ss
        bins = df[df.field.isin(BINARY) & (df.outcome.isin(["match", "mismatch"]))]
        summary.append({"model": mk, "pass": ps, "n_studies_run": int(a.study_id.nunique()),
                        "n_gold_rows": int(gold.shape[0]), "n_matched_rows": int(a.method.isin(["exact", "overlap", "singleton", "pooled_guess"]).sum()),
                        "n_extra_rows": int((a.method == "extra").sum()), **metrics(df),
                        "signsig_n": int(len(s)), "signsig_agreement": float(s.agree.mean()) if len(s) else np.nan,
                        "kappa_binary_pooled": kappa(bins.gold_norm.tolist(), bins.model_norm.tolist()),
                        "input_tokens": int(usage.input_tokens.sum()), "output_tokens": int(usage.output_tokens.sum()),
                        "reasoning_tokens": int(usage.reasoning_tokens.sum()), "cost_usd": float(usage.cost_usd.fillna(0).sum()),
                        "latency_s": float(usage.latency_s.sum()), "n_via_openrouter": int((usage.route == "openrouter").sum()) if "route" in usage else 0})
        for grp, dg in df.groupby("field_group"):
            groups.append({"model": mk, "pass": ps, "field_group": grp, **metrics(dg)})
        for f in CATEGORICAL + BINARY:
            d = df[(df.field == f) & df.outcome.isin(["match", "mismatch"])]
            fk.append({"model": mk, "pass": ps, "field": f, "n": len(d), "agreement": float((d.outcome == "match").mean()) if len(d) else np.nan,
                       "kappa": kappa(d.gold_norm.tolist(), d.model_norm.tolist())})
    summary = pd.DataFrame(summary)

    # pass-1 -> pass-2 changes, cell by cell
    key = ["study_id", "gold_site_subgroup", "model", "field"]
    c1 = cells[cells["pass"] == 1].set_index(key).outcome
    c2 = cells[cells["pass"] == 2].set_index(key).outcome
    both = pd.concat([c1.rename("o1"), c2.rename("o2")], axis=1).dropna().reset_index()
    good = lambda o: o == "match"
    delta = []
    for mk, d in both.groupby("model"):
        n_changes = sum(len(r["result"].get("changes", [])) for r in runs if r["model_key"] == mk and r["pass"] == 2)
        delta.append({"model": mk, "n_changes_logged": n_changes,
                      "fixed": int(((~d.o1.map(good)) & d.o2.map(good)).sum()),
                      "broke": int((d.o1.map(good) & (~d.o2.map(good))).sum()),
                      "accuracy_pass1": summary.query("model == @mk and `pass` == 1").accuracy.squeeze(),
                      "accuracy_pass2": summary.query("model == @mk and `pass` == 2").accuracy.squeeze(),
                      "recall_pass1": summary.query("model == @mk and `pass` == 1").recall.squeeze(),
                      "recall_pass2": summary.query("model == @mk and `pass` == 2").recall.squeeze()})

    # Jev
    jev = []
    for p in sorted(RUNS.glob("*/jev-1.13/answers.json")):
        d = json.loads(p.read_text())
        g = gold[gold.study_id == d["study_id"]].set_index("site_subgroup")
        for u in d["units"]:
            grow = g.loc[u["site_subgroup"]]
            for f, ans in (u["answers"] or {}).items():
                gv = grow[f]
                if isnull(gv):
                    continue
                gv = ("yes" if int(float(gv)) else "no") if f in BINARY else str(gv).lower()
                jev.append({"study_id": d["study_id"], "gold_site_subgroup": u["site_subgroup"], "field": f, "gold": gv,
                            "jev": ans.get("choice"), "p_gold": (ans.get("probabilities") or {}).get(gv, np.nan),
                            "confidence": ans.get("confidence"), "match": ans.get("choice") == gv})
    jev = pd.DataFrame(jev)
    if len(jev):
        jev_f = jev.groupby("field").agg(n=("match", "size"), accuracy=("match", "mean"), mean_p_gold=("p_gold", "mean"),
                                         kappa=("match", lambda s: kappa(jev.loc[s.index, "gold"].tolist(), jev.loc[s.index, "jev"].tolist()))).reset_index()
        jev_f.to_csv(OUT / "benchmark-jev.csv", index=False)
        jev.to_csv(OUT / "benchmark-jev-cells.csv", index=False)

    # text preparation stats
    man = pd.read_csv(HERE / "manifest.csv")
    tstats = []
    for sid in man.study_id:
        pj = TEXT / f"{sid}.pages.json"
        if pj.exists():
            pages = json.loads(pj.read_text())["pages"]
            txt = (TEXT / f"{sid}.txt").read_text(encoding="utf-8")
            tstats.append({"study_id": sid, "n_pages": len(pages), "n_ocr_pages": sum(p["source"] == "gemini_ocr" for p in pages),
                           "n_chars": len(txt), "gold_rows": int((gold.study_id == sid).sum())})
    man = man.merge(pd.DataFrame(tstats), on="study_id", how="left")
    man["gold_randomization_midpoint"] = man.study_id.map(gold.groupby("study_id").randomization_midpoint.first())
    man["gold_sector_program"] = man.study_id.map(gold.groupby("study_id").sector_program.max())

    # Model-model agreement on the studies every model completed, per pass: each pair of
    # aligned model records scored with the same tolerances used against the reference.
    pair_rows, consensus = [], []
    PAIR_FIELDS = [f for f in SCORED if f != "outcome_data_source_type"]
    for ps in (1, 2):
        done = {}
        for r in runs:
            if r["pass"] == ps:
                done.setdefault(r["study_id"], {})[r["model_key"]] = r
        for sid, by_model in done.items():
            if set(by_model) != set(MODEL_ORDER):
                continue
            g = gold[gold.study_id == sid]
            gunits = g.site_subgroup.tolist()
            aligned = {}
            for mk, r in by_model.items():
                recs = r["result"]["records"]
                for gi, mj, *_ in align_rows(g.project.iloc[0], gunits, recs):
                    if gi is not None and mj is not None:
                        aligned.setdefault(gi, {})[mk] = recs[mj]
            for gi, recs_by_model in aligned.items():
                if len(recs_by_model) < len(MODEL_ORDER):
                    continue
                grow = g.iloc[gi].to_dict()
                for f in PAIR_FIELDS:
                    if unavailable(grow["project"], grow["site_subgroup"], f):
                        continue
                    ks = MODEL_ORDER
                    pair_ok = []
                    for i in range(len(ks)):
                        for j in range(i + 1, len(ks)):
                            a, b = recs_by_model[ks[i]], recs_by_model[ks[j]]
                            ga = dict(a)
                            for h in H:
                                ga[f"{h}_earn_cadence"] = a.get(f"{h}_earn_cadence")
                            o = score_cell(f, a.get(f), b.get(f), ga, b)["outcome"]
                            if o in ("match", "mismatch"):
                                pair_ok.append(o == "match")
                                pair_rows.append({"pass": ps, "study_id": sid, "field": f, "field_group": FIELD_GROUP[f],
                                                  "model_a": ks[i], "model_b": ks[j], "match": o == "match"})
                    vs_gold = [score_cell(f, grow.get(f), recs_by_model[k].get(f), grow, recs_by_model[k])["outcome"] for k in ks]
                    if all(o in ("match", "mismatch") for o in vs_gold) and pair_ok:
                        consensus.append({"pass": ps, "study_id": sid, "gold_site_subgroup": grow["site_subgroup"], "field": f,
                                          "field_group": FIELD_GROUP[f], "models_unanimous": all(pair_ok),
                                          "n_models_match_gold": sum(o == "match" for o in vs_gold)})
    pd.DataFrame(pair_rows).to_csv(OUT / "benchmark-model-pairs.csv", index=False)
    pd.DataFrame(consensus).to_csv(OUT / "benchmark-consensus.csv", index=False)

    wb = pd.read_excel(GOLD_XLSX, sheet_name=None)
    full = wb["Data Table"].dropna(subset=["project"])
    dd = wb["Data dictionary"]
    pd.DataFrame([{
        "gold_rows_total": len(full), "gold_projects_total": full.project.nunique(),
        "reasoning_rows_total": len(wb["Reasoning Table"].dropna(subset=["project"])),
        "impact_estimate_rows_total": len(wb["Impact Estimates"].dropna(subset=["project"])),
        "data_table_columns": full.shape[1], "reasoning_columns": wb["Reasoning Table"].shape[1],
        "dictionary_fields": int(pd.to_numeric(dd.iloc[:, 0], errors="coerce").notna().sum()),
        "gold_rows_benchmark": len(gold), "scored_fields": len(SCORED),
    }]).to_csv(OUT / "benchmark-gold-meta.csv", index=False)
    rs = wb["Reasoning Table"]
    rs[rs.project.isin(gold.project)].to_csv(OUT / "benchmark-gold-reasoning.csv", index=False)

    pd.DataFrame([{"study_id": r["study_id"], "model": r["model_key"], "pass": r["pass"], "route": r.get("route", "gemini" if r["model_requested"].startswith("gemini") else "openrouter"),
                   "structured_mode": r.get("structured_mode"), "provider": r.get("provider"), "model_version": r.get("model_version"),
                   **r["usage"], "n_records": len(r["result"]["records"]), "n_changes": len(r["result"].get("changes", []))} for r in runs]).to_csv(OUT / "benchmark-runs.csv", index=False)
    cells.to_csv(OUT / "benchmark-cell-scores.csv", index=False)
    align.to_csv(OUT / "benchmark-alignment.csv", index=False)
    summary.to_csv(OUT / "benchmark-summary.csv", index=False)
    pd.DataFrame(groups).to_csv(OUT / "benchmark-field-groups.csv", index=False)
    pd.DataFrame(fk).to_csv(OUT / "benchmark-field-kappa.csv", index=False)
    pd.DataFrame(delta).to_csv(OUT / "benchmark-pass-delta.csv", index=False)
    ss.to_csv(OUT / "benchmark-signsig.csv", index=False)
    man.to_csv(OUT / "benchmark-manifest.csv", index=False)
    if len(calls):
        calls.to_csv(OUT / "benchmark-calls.csv", index=False)
    keep = ["study_id", "project", "site_subgroup", "sources"] + [f for f in SCORED if f in gold.columns] + ["outcome_data_source"] + [f"{h}_earn_cadence" for h in H]
    gold[keep].to_csv(OUT / "benchmark-gold-subset.csv", index=False)
    print(summary[["model", "pass", "n_studies_run", "n_matched_rows", "accuracy", "coverage", "recall", "signsig_agreement", "kappa_binary_pooled", "cost_usd"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
