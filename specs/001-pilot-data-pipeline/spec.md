# Feature Specification: Pilot Data Pipeline (P1)

**Feature Branch**: `001-pilot-data-pipeline`

**Created**: 2026-08-03

**Status**: Draft

**Input**: PLAN.md Phase P1 — validate the schema, codebook, and rubric end-to-end on the 46-item landmark seed corpus before OSF Registration 1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate any dataset state in one command (Priority: P1)

As a PI, I run one command and learn whether every CSV in `data/processed/` conforms to the schema and cross-table rules, so that invalid data can never silently accumulate.

**Why this priority**: Constitution Principle VII; every later story depends on it.

**Independent Test**: Corrupt one field in a fixture copy of `predictions.csv` (bad enum, missing verified_by on a verified row, orphan FK) and confirm validation fails with a message naming file, row, and rule; confirm the pristine dataset passes.

**Acceptance Scenarios**:

1. **Given** header-only CSVs, **When** `python -m pipeline.validate` runs, **Then** it exits 0.
2. **Given** a row with `record_status=verified` and empty `verified_by`, **When** validation runs, **Then** it exits non-zero naming the row and the rule.
3. **Given** an `evaluations` row with an ordinal verdict and no `outcome_evidence` row, **When** validation runs, **Then** it fails citing the evidence rule.

### User Story 2 - Enter the pilot corpus with provenance (Priority: P2)

As a coder, I enter the 46 landmark predictions (docs/research/landmark-seed-list.md) as `sources`/`authors`/`predictions` rows (retrieval_track=pilot_seed, extraction_method=human_manual), with verbatim quotes and locators, and the three unverified-verbatim items held at `draft`.

**Independent Test**: After entry, validation passes; a generated summary reports ≥46 predictions across all five era strata; every non-draft row has verified_by/verified_date.

**Acceptance Scenarios**:

1. **Given** the seed list, **When** entry is complete, **Then** each era stratum E1–E5 has ≥5 predictions and each prediction has a source URL or archive locator.
2. **Given** the Frey–Osborne-derived items (Deloitte 2014, PwC 2017, WDR 2016, ILO 2016), **When** entered, **Then** their `derived_from_prediction_id` points at the F–O row.

### User Story 3 - Run ~10 trial evaluations to stress-test the rubric (Priority: P3)

As the PIs, we independently evaluate ~10 horizon-elapsed pilot predictions (incl. WEF 2020, Hinton 2016, Simon 1960, Jenkins–Sherman 1979, Gartner 2017) under `protocol/evaluation-rubric.md`, log evidence rows, and compare verdicts — revising band edges/rubric wording where we disagree.

**Independent Test**: ≥10 evaluations with ≥1 evidence row each pass validation; a disagreement memo (docs/decisions/) records every rubric ambiguity found and its resolution.

**Acceptance Scenarios**:

1. **Given** WEF 2020 ("85m displaced / 97m created by 2025"), **When** both PIs evaluate independently, **Then** both verdicts + evidence are recorded and any divergence produces a rubric-revision decision entry.

### User Story 4 - LLM extraction dry run (Priority: P4)

As a PI, I run detect_v1 + extract_v1 on 5 full-text pilot sources (e.g. Ricardo ch. 31, Keynes 1930, Wiener letter, Triple Revolution memo, Frey–Osborne) and verify the drafts field-by-field, populating `verification_log.csv`, to measure first-pass LLM accuracy and fix prompt weaknesses.

**Independent Test**: verification_log contains field-level rows for all 5 documents; a summary reports per-field change rates; prompt revision notes filed if any field's change rate > 30%.

### Edge Cases

- Partial dates (`1930`) must survive round-tripping through validation.
- Quotes containing commas, quotes, and newlines must be CSV-safe (quoted, UTF-8).
- A prediction with `estimate_type=range` and null `magnitude_value` must validate.
- `revisits` referencing a source that is itself a prediction's source must not be flagged as duplicate.
- OCR-mangled verbatim quotes are entered as-is with `[illegible]` markers, not corrected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `python -m pipeline.validate` MUST validate all `data/processed/` + `data/logs/` + `data/vocab/` CSVs against `schemas/datapackage.json` (frictionless) and exit non-zero on any failure.
- **FR-002**: A pandera/cross-table layer MUST enforce: FK integrity; verified/locked rows require verifier fields; ordinal verdicts require ≥1 evidence row; `clearly_*` verdicts require official/census/academic evidence; `archive_url` required when `url` set; partial-date patterns; exactly one primary technology per prediction; `horizon_end_year ≥ horizon_start_year`.
- **FR-003**: A generator MUST render `docs/codebook.md` from `schemas/datapackage.json` + `data/vocab/*.csv` (constitution Principle VI: generated, not hand-typed).
- **FR-004**: A summary command MUST report record counts by table, era stratum, tier, claim_type, and record_status.
- **FR-005**: CI (GitHub Actions) MUST run FR-001/FR-002 + pytest on every push touching `data/` or `schemas/`.
- **FR-006**: The LLM dry-run harness MUST call the Claude API with prompts loaded from `protocol/prompts/`, record exact model snapshot ID, and write drafts only to `data/interim/`.

### Key Entities

Per `schemas/datapackage.json`: sources, authors, prediction_authors, technologies, prediction_technologies, predictions, evaluations, outcome_evidence, revisits, coders + 3 logs.

## Success Criteria *(mandatory)*

- **SC-001**: Validation catches 100% of a seeded 10-error mutation fixture set.
- **SC-002**: ≥46 pilot predictions entered and passing validation, all five eras covered.
- **SC-003**: ≥10 dual-PI trial evaluations completed; every rubric ambiguity resolved in a logged decision.
- **SC-004**: LLM dry-run field-level agreement measured and reported for 5 documents.
- **SC-005**: Codebook v1.0 generated; schema changes during pilot logged in docs/decisions/.

## Assumptions

- Python 3.12 venv (`.venv`) gains project deps (frictionless, pandera, pandas, pytest, anthropic) — pyproject.toml to be created.
- Pilot data entry is human-manual (spreadsheet or CSV editing) — no entry UI in scope.
- Anthropic API key available via environment variable for the dry run (never committed).
- The screening cap / Track A search tooling is OUT of scope for this feature (that is feature 002, post-Reg-1 planning).
