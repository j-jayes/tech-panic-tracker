# Extraction Protocol (DRAFT v0.1 — to be frozen at OSF Registration 1)

Companion to `docs/PLAN.md` §5. Prompts live in `protocol/prompts/` (versioned files); this document defines the pipeline and reliability design.

## 1. Pipeline stages

| # | Stage | Actor | Output | Rule |
|---|---|---|---|---|
| 1 | Ingest | pipeline | normalized full text in `data/raw/`; OCR engine + quality flag logged per document | copyrighted texts stay out of git (see `data/raw/README.md`) |
| 2 | Candidate detection | LLM, prompt `detect_vN` | candidate spans + confidence, to `data/interim/` | tuned for **high recall**; false positives are cheap |
| 3 | Structured extraction | LLM, prompt `extract_vN` | JSON records mirroring `predictions.csv`, to `data/interim/` | JSON-schema-constrained; verbatim quote + locator mandatory — hallucinated quotes fail stage 4 by construction |
| 4 | Human verification | named coder | verified rows in `data/processed/`; every field correction to `verification_log.csv` | only humans move records past `draft` |
| 5 | Lock | pipeline + coder | `record_status = locked` | after schema validation + dedup pass; immutable thereafter |

## 2. Versioning rules

- Prompt files are semver-named (`detect_v1.md`, `extract_v1.md`); every record stores `llm_prompt_version` and the **exact dated model snapshot ID** in `llm_model`.
- A frozen regression set of ~25 documents (spanning all five era strata and the main source types; assembled in P1) is re-run on any prompt or model change; diffs reviewed by both authors before adoption.
- Prompt/model changes after Registration 1 are logged amendments (constitution Principle IV).

## 3. Reliability design (preregistered)

Framing (goes verbatim into Reg 1): *"LLM output is treated as a first-draft suggestion; the analytic dataset consists solely of human-verified records. We report LLM-draft agreement for transparency, and human–human agreement as the validity statistic."*

- **LLM–human agreement:** per-field share unchanged at verification, from `verification_log.csv`; Gwet's AC1 / Krippendorff's α for categorical fields. Reported in the methods section; the full log publishes with the dataset.
- **Human–human reliability:** independent double-coding by the two authors on a random **20% of predictions (min n = 100)**; **Krippendorff's α per field**; target **α ≥ 0.80**; any field < 0.667 triggers codebook revision + re-coding of that field corpus-wide.
- **Detection recall check:** ~30 randomly sampled included sources fully hand-read; candidate-detection miss rate reported as a limitation statistic.

## 4. Coding aids (from pilot research)

- **Apocryphal-quote warning list**: see `docs/research/landmark-seed-list.md` — Bennis factory-and-dog (fake), Reuther/Ford robots-buy-cars (folklore), Simon 1960-not-1965, Leontief truncation, Keynes misreading, McKinsey 800m headline vs 75–375m evaluable figures. Verify quotes against Quote Investigator / primary sources before `verified`.
- **Citation lineage**: check whether a quantified claim derives from an upstream study (Frey–Osborne family) and set `derived_from_prediction_id`.
- **Reported speech**: newspaper quoting a predictor → author = predictor, source = outlet, `is_secondary_report = true`, chase primary (one documented attempt).
