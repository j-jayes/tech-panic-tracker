# Implementation Plan: Pilot Data Pipeline (001)

**Spec**: [spec.md](spec.md) · **Constitution**: `.specify/memory/constitution.md` · **Created**: 2026-08-03

## Technical context

- Python 3.12 (existing `.venv`); add `pyproject.toml` with deps: `frictionless`, `pandera`, `pandas`, `pytest`, `anthropic`, `python-dotenv`.
- Canonical schema: `schemas/datapackage.json` (already written). pandera adds only what frictionless cannot express.
- No database, no UI: CSVs are the store; commands are `python -m pipeline.<cmd>`.

## Structure

```
pipeline/
├── __init__.py
├── validate/
│   ├── __init__.py          # python -m pipeline.validate entry
│   ├── frictionless_check.py
│   └── cross_table.py       # pandera + custom FK/evidence/status rules
├── codebook.py              # python -m pipeline.codebook → docs/codebook.md
├── summary.py               # python -m pipeline.summary → counts by stratum/tier/status
└── llm/
    ├── run_detect.py        # detect_vN over data/raw/ → data/interim/
    └── run_extract.py       # extract_vN over candidates → data/interim/
tests/
├── fixtures/                # pristine mini-dataset + 10-error mutation set (SC-001)
├── test_frictionless.py
├── test_cross_table.py
└── test_codebook.py
.github/workflows/validate.yml
```

## Implementation order

1. **pyproject.toml + deps** — pin versions; `pip install -e .`.
2. **frictionless_check.py** — load datapackage, validate all resources; clear per-row error reporting. (US1)
3. **cross_table.py** — rules FR-002 as individually-named checks; each check is a pytest-parameterizable function. (US1)
4. **tests + mutation fixtures** — build the 10-error fixture set first, TDD the validators against it. (SC-001)
5. **CI workflow** — actions/setup-python, run validate + pytest on push/PR touching data|schemas|pipeline.
6. **codebook.py** — render markdown: one section per table (fields, types, constraints), one per enum (from enum_definitions.csv joined to datapackage values — fail if a value lacks a definition), technologies table. (FR-003)
7. **summary.py** — pandas groupbys; era stratum derived from prediction_date year bins (1800-1870/…/1995-). (FR-004)
8. **Pilot data entry** (US2) — not code: both PIs enter the 46 seed items; the three verbatim-unverified items stay `draft`. Validation + summary gate completion.
9. **llm/run_detect.py + run_extract.py** (US4) — anthropic SDK; model snapshot ID recorded from API response; JSON-schema-constrained extraction (tool use); writes only to `data/interim/`; a small verify helper appends field diffs to `verification_log.csv` as the human reviews.
10. **Trial evaluations** (US3) — manual, gated by validation; disagreement memo template in `docs/decisions/DR-template.md`.

## Constitution gates

- Principle I/II: `llm/` writes only to `data/interim/`; `created_by`/`llm_model` mandatory in drafts.
- Principle VI: codebook + summary are generated; CI fails if `docs/codebook.md` is stale (regenerate-and-diff check).
- Principle VII: CI green required to merge anything touching `data/processed/`.

## Risks

- frictionless FK checks across resources can be slow/finicky → implement FKs in `cross_table.py` with pandas joins instead; keep frictionless for types/enums/patterns.
- CSV quoting of long verbatim quotes: standardize on `csv.QUOTE_MINIMAL`, UTF-8 (no BOM), `\n` inside quoted fields allowed; add a round-trip test.
- Era-stratum derivation from partial dates: year = first 4 chars; test `1930` and `1930-06`.

## Verification

`pytest` green; `python -m pipeline.validate` exit 0 on pristine and non-zero on each mutation fixture; `python -m pipeline.codebook` output committed and diff-clean in CI; summary shows all five strata populated after US2.
