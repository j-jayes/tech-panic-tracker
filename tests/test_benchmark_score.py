"""Scoring rules for the extraction benchmark (analysis/pilot-draft/benchmark/score.py)."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis" / "pilot-draft" / "benchmark"))
import score as s  # noqa: E402


def test_parse_cadence_gold_patterns():
    cases = {
        "annual (Quarters 2-5, UI wage records)": 12,
        "monthly (averaged over months 10-18)": 1,
        "cumulative over months 1-12 (Year 1, derived by subtraction from NDNH)": 12,
        "cumulative over Q5-Q6 (months 13-18, NDNH)": 6,
        "cumulative over Q1-Q4 (Year 1, NDNH)": 12,
        "weekly": 12 / 52,
    }
    for text, months in cases.items():
        assert math.isclose(s.parse_cadence_months(text), months)
    assert s.parse_cadence_months(None) is None


def test_align_prefers_exact_then_overlap():
    gold = ["Adult women", "Adult men", "Female out-of-school youths", "Male out-of-school youths"]
    model = [{"site_subgroup": "Adult men (22+)"}, {"site_subgroup": "Adult Women"}, {"site_subgroup": "Male youth"}, {"site_subgroup": "Female youth"}]
    pairs = {g: m for g, m, *_ in s.align_rows("National JTPA Study", gold, model)}
    assert pairs == {0: 1, 1: 0, 2: 3, 3: 2}


def test_align_single_gold_row_picks_pooled_and_flags_extras():
    model = [{"site_subgroup": "Boston", "n_treatment": 10}, {"site_subgroup": "Pooled sample", "n_treatment": 30}]
    pairs = s.align_rows("Year Up", ["Full sample (8 offices pooled)"], model)
    assert (0, 1, "exact", 1.0) in pairs or any(p[:2] == (0, 1) for p in pairs)
    assert any(p[2] == "extra" and p[1] == 0 for p in pairs)


def test_align_unmatched_rows():
    pairs = s.align_rows("P", ["Houston men", "El Paso women"], [{"site_subgroup": "Houston men"}])
    methods = sorted(p[2] for p in pairs)
    assert methods == ["exact", "gold_missing"]


def test_kappa():
    assert math.isclose(s.kappa([1, 1, 0, 0], [1, 0, 0, 0]), 0.5)
    assert math.isnan(s.kappa([1, 1], [1, 1]))


def test_null_outcomes():
    row = {}
    assert s.score_cell("n_treatment", None, None, row, row)["outcome"] == "both_null"
    assert s.score_cell("n_treatment", 100, None, row, row)["outcome"] == "abstained"
    assert s.score_cell("n_treatment", None, 100, row, row)["outcome"] == "extra_value"


def test_tolerances():
    row = {}
    assert s.score_cell("n_treatment", 1000, 1015, row, row)["outcome"] == "match"
    assert s.score_cell("n_treatment", 1000, 1030, row, row)["outcome"] == "mismatch"
    assert s.score_cell("st_emp_impact", 2.9, 3.3, row, row)["outcome"] == "match"
    assert s.score_cell("st_emp_impact", 2.9, 3.6, row, row)["outcome"] == "mismatch"


def test_earnings_annualised_before_comparison():
    g_row = {"st_earn_cadence": "quarterly"}
    m_row = {"st_earn_cadence": "annual", "st_earn_period_months": 12}
    out = s.score_cell("st_earn_impact", 250, 1000, g_row, m_row)
    assert out["outcome"] == "match" and "annualised" in out["note"]


def test_stars_blank_means_not_significant_when_impact_present():
    assert s.score_cell("st_emp_stars", None, "ns", {"st_emp_impact": 1.0}, {"st_emp_impact": 1.1})["outcome"] == "match"
    assert s.signsig(3.0, 1.0, None) == "pos_sig"
    assert s.signsig(-1.0, None, None) == "ns"
    assert s.signsig(-5.0, None, "**") == "neg_sig"


def test_randomization_period():
    assert s.score_cell("randomization_period", "February 1976 – March 1979", "Feb 1976 - Mar 1979", {}, {})["outcome"] == "match"
    assert s.score_cell("randomization_period", "approximately 2003–2005", "2003 - 2005", {}, {})["outcome"] == "match"
    assert s.score_cell("randomization_period", "June 2011 – June 2013", "June 2011 - December 2013", {}, {})["outcome"] == "mismatch"
