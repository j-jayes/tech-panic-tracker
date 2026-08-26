"""Validation tests: pristine dataset passes; seeded mutations are caught.

Mutation fixtures are built on the fly by copying data/ into tmp_path and
corrupting one thing at a time (spec 001, SC-001 — the full 10-error fixture
set lands with the pilot; these cover the cross-table rules implemented so far).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from pipeline import REPO_ROOT
from pipeline.validate.cross_table import load_tables, ALL_RULES, validate_cross_table
from pipeline.validate.frictionless_check import validate_resources


def test_pristine_dataset_validates():
    assert validate_resources() == []
    assert validate_cross_table() == []


@pytest.fixture()
def tmp_data(tmp_path: Path) -> tuple[Path, Path]:
    processed = tmp_path / "processed"
    vocab = tmp_path / "vocab"
    shutil.copytree(REPO_ROOT / "data" / "processed", processed)
    shutil.copytree(REPO_ROOT / "data" / "vocab", vocab)
    return processed, vocab


def _append(csv: Path, row: dict):
    df = pd.read_csv(csv, dtype=str, keep_default_na=False)
    df = pd.concat([df, pd.DataFrame([{c: row.get(c, "") for c in df.columns}])])
    df.to_csv(csv, index=False)


BASE_PRED = {
    "prediction_id": "pred_test1", "source_id": "src_test1", "quote_verbatim": "q", "quote_locator": "p. 1",
    "prediction_date": "1930", "claim_summary": "s", "claim_type": "employment_outcome", "level": "occupation",
    "direction": "displacement", "specificity_tier": "T3_directional", "horizon_type": "none",
    "mechanism_specified": "false", "panic_valence": "alarm", "extraction_method": "human_manual",
    "created_by": "jj", "created_date": "2026-08-03", "record_status": "draft",
}


def test_orphan_source_fk_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "predictions.csv", BASE_PRED)  # src_test1 does not exist
    errors = validate_cross_table(processed, vocab)
    assert any("fk_predictions_source_id" in e for e in errors)


def test_verified_without_verifier_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "sources.csv", {"source_id": "src_test1", "title": "t", "source_type": "book", "retrieval_track": "pilot_seed"})
    _append(processed / "predictions.csv", {**BASE_PRED, "record_status": "verified"})
    errors = validate_cross_table(processed, vocab)
    assert any("verified_requires_verifier" in e for e in errors)


def test_ordinal_verdict_without_evidence_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "sources.csv", {"source_id": "src_test1", "title": "t", "source_type": "book", "retrieval_track": "pilot_seed"})
    _append(processed / "predictions.csv", BASE_PRED)
    _append(processed / "evaluations.csv", {
        "evaluation_id": "eval_test1", "prediction_id": "pred_test1", "verdict": "mostly_wrong",
        "verdict_rationale": "r", "evaluated_as_of": "2026-12-31", "evaluator_id": "jj",
        "blinding_status": "unblindable", "created_by": "jj", "created_date": "2026-08-03", "record_status": "draft",
    })
    errors = validate_cross_table(processed, vocab)
    assert any("verdict_requires_evidence" in e for e in errors)


def test_url_without_archive_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "sources.csv", {"source_id": "src_test1", "title": "t", "source_type": "book", "retrieval_track": "pilot_seed", "url": "https://example.com"})
    errors = validate_cross_table(processed, vocab)
    assert any("url_requires_archive" in e for e in errors)


def test_two_primary_technologies_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "sources.csv", {"source_id": "src_test1", "title": "t", "source_type": "book", "retrieval_track": "pilot_seed"})
    _append(processed / "predictions.csv", BASE_PRED)
    for tech in ("atm", "computing"):
        _append(processed / "prediction_technologies.csv", {"prediction_id": "pred_test1", "tech_id": tech, "is_primary": "true"})
    errors = validate_cross_table(processed, vocab)
    assert any("one_primary_technology" in e for e in errors)


def test_horizon_order_caught(tmp_data):
    processed, vocab = tmp_data
    _append(processed / "sources.csv", {"source_id": "src_test1", "title": "t", "source_type": "book", "retrieval_track": "pilot_seed"})
    _append(processed / "predictions.csv", {**BASE_PRED, "horizon_start_year": "1950", "horizon_end_year": "1940"})
    errors = validate_cross_table(processed, vocab)
    assert any("horizon_order" in e for e in errors)


def test_every_rule_is_exercised():
    exercised = {"rule_foreign_keys", "rule_verified_requires_verifier", "rule_verdict_requires_evidence", "rule_url_requires_archive", "rule_one_primary_technology", "rule_horizon_order"}
    assert {r.__name__ for r in ALL_RULES} == exercised
