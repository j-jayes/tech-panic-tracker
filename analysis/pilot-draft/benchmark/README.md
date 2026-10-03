# Extraction benchmark

Code behind `analysis/pilot-draft/llm-extraction-benchmark.qmd`. It replicates the
language-model extraction in Roodman and Massenkoff (2026), *An Evidence Review of Worker
Retraining* (Anthropic Economic Index), on ten of their 56 studies with five models, and
scores each model against their published extraction workbook
(`github.com/droodman/job-training-meta-analysis`, `data/extraction_full_v69.xlsx`).

This is a method benchmark. Nothing here writes to `data/processed/`, and the prompts
(`protocol/prompts/benchmark_*.md`) are not part of the registered Tech-Panic Tracker pipeline.

## Run order

```bash
uv pip install -e ".[llm]"                                              # google-genai, httpx, openpyxl, ...
.venv/bin/python analysis/pilot-draft/benchmark/fetch_sources.py         # PDFs + gold workbook -> data/raw/
.venv/bin/python analysis/pilot-draft/benchmark/prepare_text.py          # page-marked text (+ OCR) -> data/interim/benchmark/text/
.venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --dry-run
.venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py        # 5 models x 10 studies x 2 passes
.venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --jev  # classification-only entrant
.venv/bin/python analysis/pilot-draft/benchmark/score.py                 # -> analysis/pilot-draft/data/benchmark-*.csv
quarto render analysis/pilot-draft/llm-extraction-benchmark.qmd
.venv/bin/python -m pytest tests/test_benchmark_score.py
```

Needs `GEMINI_API_KEY` and `OPEN_ROUTER_KEY` in `.env`, plus `pdftotext`/`pdftoppm` (poppler).
Runs are skipped when their output exists; `--force` re-runs. Every call is appended to
`data/interim/benchmark/calls.jsonl`; `--budget-usd` (default 47) caps OpenRouter spend,
counting the key's billed usage.

## Files

| File | Role |
|---|---|
| `manifest.csv` | the ten studies, source files (file-naming slugs) and URLs |
| `schema.py` | Pydantic record schema; `strict_json_schema()` for OpenAI-style strict mode |
| `prepare_text.py` | `pdftotext -layout` per page; garbled pages transcribed by Gemini 3.7 Flash (cached per page in `data/interim/benchmark/ocr/`) |
| `providers.py` | Gemini, OpenRouter and Jev clients; call log; budget guard |
| `run_extraction.py` | two-pass loop (extract, then adversarial review), Jev run |
| `score.py` | row alignment, cell scoring, kappa, summaries |

## Deviations recorded during the run (22 September 2026)

- Gemini 3.8 Flash on the direct Gemini API returned sustained 503 (overloaded) errors; the
  runner falls back to the same model through OpenRouter's Google route and records the route
  per run. OCR used Gemini 3.7 Flash through OpenRouter for the same reason.
- Anthropic refuses JSON-schema response formats with more than 16 nullable fields (the schema
  has 42), strict or not; Claude Opus 5 receives the schema as a forced tool call instead.
- OpenAI and Anthropic reasoning models reject `temperature` when parameters are required, so
  they run at provider defaults; the others run at temperature 0.
- The registered prompt text is sent after the source document in the user message, behind a
  short shared system message, so that the two passes share a cacheable prefix.
- The Minority Female Single Parent Demonstration was replaced by WorkAdvance because its
  summary volume is not openly available. Couch (1992), which supplies two NSW earnings series
  in the gold data, is not openly available; those cells are excluded from scoring.
