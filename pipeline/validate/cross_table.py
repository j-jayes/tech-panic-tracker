"""Cross-table rules frictionless cannot express (FR-002).

Implemented with plain pandas joins (not pandera): each rule is a named
function returning a list of error strings, so pytest can exercise rules
individually and error messages name file, row key, and rule.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline import REPO_ROOT

PROCESSED = REPO_ROOT / "data" / "processed"
VOCAB = REPO_ROOT / "data" / "vocab"

ORDINAL_VERDICTS = {"clearly_correct", "mostly_correct", "mixed", "mostly_wrong", "clearly_wrong"}
CLEARLY = {"clearly_correct", "clearly_wrong"}
STRONG_EVIDENCE = {"official_statistics", "census_series", "academic_study"}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_tables(processed: Path = PROCESSED, vocab: Path = VOCAB) -> dict[str, pd.DataFrame]:
    tables = {p.stem: _read(p) for p in processed.glob("*.csv")}
    tables["technologies"] = _read(vocab / "technologies.csv")
    return tables


def _fk(child: pd.DataFrame, col: str, parent: pd.DataFrame, pcol: str, child_name: str, allow_empty: bool = True) -> list[str]:
    if child.empty or col not in child.columns:
        return []
    values = child[col]
    mask = ~values.isin(set(parent[pcol])) if not parent.empty else values != ""
    if allow_empty:
        mask &= values != ""
    return [f"{child_name}.{col}: orphan value '{v}' (rule: fk_{child_name}_{col})" for v in values[mask]]


def rule_foreign_keys(t: dict[str, pd.DataFrame]) -> list[str]:
    errors: list[str] = []
    errors += _fk(t["predictions"], "source_id", t["sources"], "source_id", "predictions", allow_empty=False)
    errors += _fk(t["predictions"], "derived_from_prediction_id", t["predictions"], "prediction_id", "predictions")
    errors += _fk(t["prediction_authors"], "prediction_id", t["predictions"], "prediction_id", "prediction_authors", allow_empty=False)
    errors += _fk(t["prediction_authors"], "author_id", t["authors"], "author_id", "prediction_authors", allow_empty=False)
    errors += _fk(t["prediction_technologies"], "prediction_id", t["predictions"], "prediction_id", "prediction_technologies", allow_empty=False)
    errors += _fk(t["prediction_technologies"], "tech_id", t["technologies"], "tech_id", "prediction_technologies", allow_empty=False)
    errors += _fk(t["technologies"], "parent_tech_id", t["technologies"], "tech_id", "technologies")
    errors += _fk(t["evaluations"], "prediction_id", t["predictions"], "prediction_id", "evaluations", allow_empty=False)
    errors += _fk(t["outcome_evidence"], "evaluation_id", t["evaluations"], "evaluation_id", "outcome_evidence", allow_empty=False)
    errors += _fk(t["revisits"], "prediction_id", t["predictions"], "prediction_id", "revisits", allow_empty=False)
    errors += _fk(t["revisits"], "revisit_source_id", t["sources"], "source_id", "revisits", allow_empty=False)
    for table in ("predictions", "evaluations", "revisits"):
        errors += _fk(t[table], "created_by", t["coders"], "coder_id", table, allow_empty=False)
        errors += _fk(t[table], "verified_by", t["coders"], "coder_id", table)
    return errors


def rule_verified_requires_verifier(t: dict[str, pd.DataFrame]) -> list[str]:
    errors = []
    for name in ("predictions", "evaluations", "revisits"):
        df = t[name]
        if df.empty:
            continue
        bad = df[(df["record_status"].isin({"verified", "locked"})) & ((df["verified_by"] == "") | (df["verified_date"] == ""))]
        key = df.columns[0]
        errors += [f"{name}.{row[key]}: status '{row['record_status']}' but missing verified_by/verified_date (rule: verified_requires_verifier)" for _, row in bad.iterrows()]
    return errors


def rule_verdict_requires_evidence(t: dict[str, pd.DataFrame]) -> list[str]:
    ev, oe = t["evaluations"], t["outcome_evidence"]
    if ev.empty:
        return []
    errors = []
    evidence_by_eval = oe.groupby("evaluation_id")["evidence_type"].agg(set) if not oe.empty else pd.Series(dtype=object)
    for _, row in ev[ev["verdict"].isin(ORDINAL_VERDICTS)].iterrows():
        types = evidence_by_eval.get(row["evaluation_id"], set())
        if not types:
            errors.append(f"evaluations.{row['evaluation_id']}: ordinal verdict '{row['verdict']}' with no outcome_evidence row (rule: verdict_requires_evidence)")
        elif row["verdict"] in CLEARLY and not (types & STRONG_EVIDENCE):
            errors.append(f"evaluations.{row['evaluation_id']}: '{row['verdict']}' requires official_statistics/census_series/academic_study evidence (rule: clearly_requires_strong_evidence)")
    return errors


def rule_url_requires_archive(t: dict[str, pd.DataFrame]) -> list[str]:
    df = t["sources"]
    if df.empty:
        return []
    bad = df[(df["url"] != "") & (df["archive_url"] == "")]
    return [f"sources.{row['source_id']}: url set but archive_url empty (rule: url_requires_archive)" for _, row in bad.iterrows()]


def rule_one_primary_technology(t: dict[str, pd.DataFrame]) -> list[str]:
    df = t["prediction_technologies"]
    if df.empty:
        return []
    primaries = df[df["is_primary"].str.lower().isin({"true", "1"})].groupby("prediction_id").size()
    listed = df.groupby("prediction_id").size()
    errors = []
    for pred_id in listed.index:
        n = int(primaries.get(pred_id, 0))
        if n != 1:
            errors.append(f"prediction_technologies.{pred_id}: {n} primary technologies, expected exactly 1 (rule: one_primary_technology)")
    return errors


def rule_horizon_order(t: dict[str, pd.DataFrame]) -> list[str]:
    df = t["predictions"]
    if df.empty:
        return []
    both = df[(df["horizon_start_year"] != "") & (df["horizon_end_year"] != "")]
    bad = both[both["horizon_end_year"].astype(int) < both["horizon_start_year"].astype(int)]
    return [f"predictions.{row['prediction_id']}: horizon_end_year < horizon_start_year (rule: horizon_order)" for _, row in bad.iterrows()]


ALL_RULES = [
    rule_foreign_keys,
    rule_verified_requires_verifier,
    rule_verdict_requires_evidence,
    rule_url_requires_archive,
    rule_one_primary_technology,
    rule_horizon_order,
]


def validate_cross_table(processed: Path = PROCESSED, vocab: Path = VOCAB) -> list[str]:
    tables = load_tables(processed, vocab)
    errors: list[str] = []
    for rule in ALL_RULES:
        errors += rule(tables)
    return errors
