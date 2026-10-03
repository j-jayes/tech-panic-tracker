"""Pydantic models for the extraction benchmark.

The field set is the core subset of the data dictionary in Roodman and
Massenkoff's extraction workbook (extraction_full_v69.xlsx), plus three
additions that make scoring arithmetic rather than string-matching:
`*_stars` (gold SEs are mostly missing), `*_earn_period_months` (so earnings
can be annualised), and `outcome_data_source_type`.
"""

from __future__ import annotations

import copy
from typing import Literal, Optional

from pydantic import BaseModel, Field

Stars = Literal["ns", "*", "**", "***"]  # "ns" = reported, not significant; null = not reported
Cadence = Literal["weekly", "monthly", "quarterly", "annual", "cumulative"]
OutcomeSourceType = Literal["survey", "ui_wage_records", "ndnh", "ssa", "other_admin", "mixed"]


class CellRefs(BaseModel):
    """Condensed version of the gold workbook's Reasoning Table."""

    training_role_reasoning: str
    classification_reasoning: str
    design_cell_references: str = Field(description="Where randomization period, N and target group came from: file, table, page")
    impact_cell_references: str = Field(description="Table and page for each ST/MT/LT number")
    time_horizon_reasoning: str = Field(description="Why each estimate was assigned to its horizon")
    se_derivation: str
    cost_source: str = Field(description="Cost figure, dollar-year, per-assignee or per-enrollee basis, location")
    ambiguities_and_flags: str


class StudyRecord(BaseModel):
    site_subgroup: str
    intervention_description: str
    training_role: Literal["primary", "secondary", "incidental"]
    has_classroom: bool
    has_ojt: bool
    has_jsa: bool
    has_multiple_components: bool
    mandatory_voluntary: Literal["mandatory", "voluntary"]
    funding_public_private: Literal["public", "private", "mixed"]
    admin_public_private: Literal["public", "private", "mixed"]
    sector_program: bool
    randomization_period: Optional[str]
    target_group: Optional[str]
    n_treatment: Optional[int]
    n_control: Optional[int]
    outcome_data_source: Optional[str]
    outcome_data_source_type: Optional[OutcomeSourceType]
    treatment_duration_months: Optional[float]
    program_takeup_impact: Optional[float]
    cost_per_treated: Optional[float]

    st_followup_years: Optional[float]
    st_emp_impact: Optional[float]
    st_emp_se: Optional[float]
    st_emp_stars: Optional[Stars]
    st_emp_control_mean: Optional[float]
    st_earn_impact: Optional[float]
    st_earn_se: Optional[float]
    st_earn_stars: Optional[Stars]
    st_earn_control_mean: Optional[float]
    st_earn_cadence: Optional[Cadence]
    st_earn_period_months: Optional[float]

    mt_followup_years: Optional[float]
    mt_emp_impact: Optional[float]
    mt_emp_se: Optional[float]
    mt_emp_stars: Optional[Stars]
    mt_emp_control_mean: Optional[float]
    mt_earn_impact: Optional[float]
    mt_earn_se: Optional[float]
    mt_earn_stars: Optional[Stars]
    mt_earn_control_mean: Optional[float]
    mt_earn_cadence: Optional[Cadence]
    mt_earn_period_months: Optional[float]

    lt_followup_years: Optional[float]
    lt_emp_impact: Optional[float]
    lt_emp_se: Optional[float]
    lt_emp_stars: Optional[Stars]
    lt_emp_control_mean: Optional[float]
    lt_earn_impact: Optional[float]
    lt_earn_se: Optional[float]
    lt_earn_stars: Optional[Stars]
    lt_earn_control_mean: Optional[float]
    lt_earn_cadence: Optional[Cadence]
    lt_earn_period_months: Optional[float]

    reasoning: CellRefs


class ExtractionOutput(BaseModel):
    """Pass 1."""

    records: list[StudyRecord]


class Change(BaseModel):
    site_subgroup: str
    field: str
    old: Optional[str]
    new: Optional[str]
    reason: str


class ReviewOutput(BaseModel):
    """Pass 2: full corrected record set plus the change log."""

    records: list[StudyRecord]
    changes: list[Change]
    review_notes: str


def strict_json_schema(model: type[BaseModel]) -> dict:
    """OpenAI-style strict schema: $defs inlined, every object closed, all keys required."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return resolve(copy.deepcopy(defs[node["$ref"].split("/")[-1]]))
            out = {k: resolve(v) for k, v in node.items() if k not in ("title", "default")}
            if out.get("type") == "object" and "properties" in out:
                out["additionalProperties"] = False
                out["required"] = list(out["properties"])
            return out
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    return resolve(schema)
