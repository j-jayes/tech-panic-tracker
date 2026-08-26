"""Pydantic models for LLM-assisted extraction (pipeline stage 3).

The field set mirrors the content fields of `predictions.csv` as defined in
`schemas/datapackage.json`, and the coding rules for each field live in
`protocol/prompts/extract_v1.md` — that prompt is the source of truth and is
read at runtime, never duplicated here.

Provenance and status fields (`prediction_id`, `source_id`, `extraction_method`,
`created_by`, `created_date`, `record_status`, `verified_*`) are deliberately
absent: the model does not get to assert them. The pipeline stamps them, and a
human moves the record past `draft`.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

ClaimType = Literal["employment_outcome", "exposure_risk", "capability_milestone"]
Level = Literal["task", "firm", "occupation", "industry", "country_region", "global"]
Direction = Literal[
    "displacement",
    "creation",
    "net_negative",
    "net_positive",
    "transformation_neutral",
    "ambiguous",
]
MagnitudeType = Literal[
    "percent_of_jobs",
    "absolute_jobs",
    "share_of_tasks",
    "qualitative_total",
    "qualitative_partial",
    "none",
]
EstimateType = Literal["point", "range", "scenario_conditional", "none"]
SpecificityTier = Literal[
    "T1_quantified", "T2_semi_quantified", "T3_directional", "T4_rhetorical"
]
HorizonType = Literal[
    "explicit_year", "explicit_duration", "vague_phrase", "conditional", "none"
]
MechanismType = Literal[
    "cost_substitution",
    "capability_parity",
    "scale_speed",
    "deskilling",
    "demand_shift",
    "other",
]
PanicValence = Literal["alarm", "reassurance", "neutral_forecast"]
OccupationSystem = Literal["soc2018", "hisco", "none"]
IndustrySystem = Literal["naics2022", "sic1987", "none"]


class SuggestedTechnology(BaseModel):
    """A tech_id from data/vocab/technologies.csv. Exactly one is primary."""

    tech_id: str
    is_primary: bool


class ExtractionRecord(BaseModel):
    """One draft predictions.csv record extracted from a candidate passage."""

    # Quote and provenance within the source
    quote_verbatim: str = Field(
        description="Exact prediction text, character-for-character, OCR errors kept."
    )
    quote_locator: str = Field(description="Page/column/paragraph. Never invented.")
    prediction_date: Optional[str] = Field(
        default=None, description="YYYY, YYYY-MM, or YYYY-MM-DD."
    )

    # The claim
    claim_summary: str
    claim_type: ClaimType
    level: Level
    geography: Optional[str] = None
    geography_text: Optional[str] = None
    occupation_code: Optional[str] = None
    occupation_system: Optional[OccupationSystem] = None
    industry_code: Optional[str] = None
    industry_system: Optional[IndustrySystem] = None
    direction: Direction

    # Magnitude
    magnitude_type: Optional[MagnitudeType] = None
    estimate_type: Optional[EstimateType] = None
    magnitude_value: Optional[float] = None
    magnitude_low: Optional[float] = None
    magnitude_high: Optional[float] = None
    magnitude_headline: Optional[float] = None
    magnitude_unit: Optional[str] = None

    specificity_tier: SpecificityTier

    # Horizon — never defaulted at extraction time; the evaluation protocol does that.
    horizon_stated_text: Optional[str] = None
    horizon_type: HorizonType
    horizon_start_year: Optional[int] = None
    horizon_end_year: Optional[int] = None

    # Mechanism
    mechanism_specified: bool
    mechanism_text: Optional[str] = None
    mechanism_type: Optional[MechanismType] = None

    is_conditional: Optional[bool] = None
    panic_valence: PanicValence
    is_secondary_report: Optional[bool] = None

    # Coder-facing
    coder_notes: str = Field(
        description="Anything uncertain, ambiguous, or needing human attention. "
        "Flag suspected misquotation or paraphrase of a famous claim here."
    )
    suggested_technologies: list[SuggestedTechnology] = Field(default_factory=list)


class NoPredictionFound(BaseModel):
    """Returned when the passage contains no in-scope prediction."""

    contains_prediction: Literal[False]
    reason: str


class ExtractionResult(BaseModel):
    """What the model returns: either a record, or a reasoned refusal."""

    contains_prediction: bool
    record: Optional[ExtractionRecord] = None
    reason_if_absent: Optional[str] = Field(
        default=None,
        description="When contains_prediction is false, why — e.g. retrospective "
        "statement, wage claim only, technology-replacing-technology.",
    )
