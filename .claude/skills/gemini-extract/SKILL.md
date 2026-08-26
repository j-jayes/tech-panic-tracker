---
name: gemini-extract
description: Run the registered extract_v1 prompt over a source passage using the Gemini API with a Pydantic-constrained structured output, producing a draft predictions record with full provenance. Use for the P1 LLM dry run, for extraction demos, and whenever a passage needs turning into a structured prediction record.
---

# LLM-assisted extraction with Gemini

Stage 3 of the extraction pipeline (`protocol/extraction-protocol.md`). Turns one candidate passage into one draft `predictions.csv` record, schema-constrained so the model cannot invent field names or enum values.

## Run it

```bash
.venv/bin/python .claude/skills/gemini-extract/scripts/extract.py \
  --text-file data/interim/passages/frey-2019-technology-trap-p304.txt \
  --meta      data/interim/passages/frey-2019-technology-trap-p304.meta.json
```

`--dry-run` builds the prompt and JSON schema and prints their sizes without calling the API — use it after editing the prompt or the model.

## Defaults

| | |
|---|---|
| model | `gemini-3.7-flash` — pinned exactly, never a floating alias like `gemini-flash-latest` |
| temperature | `0` |
| output | `data/interim/extractions/{stem}-{timestamp}.json` (git-ignored) |
| credentials | `GEMINI_API_KEY` from `.env` (local) or the GitHub Actions secret (CI) |

Every output file records `model_requested`, the `model_version` the API actually served, `prompt_version`, the input file path, and a SHA-256 of the passage. That is what makes a record traceable to the exact call that drafted it; **do not** strip these when copying results elsewhere.

## What the pieces are

- **`scripts/models.py`** — the Pydantic model. Field set mirrors the content fields of `predictions.csv` in `schemas/datapackage.json`; enums are `Literal` types taken from `data/vocab/enum_definitions.csv`. It deliberately omits `prediction_id`, `source_id`, `created_by`, `record_status`, and the verification fields: the model does not get to assert its own provenance.
- **`scripts/extract.py`** — reads the system prompt **from `protocol/prompts/extract_v1.md` at runtime**. The registered prompt is the source of truth; never paste a copy into the script, or the registration stops describing what actually ran.
- **`ExtractionResult`** wraps either a record or a reasoned refusal (`contains_prediction: false` plus `reason_if_absent`), so an out-of-scope passage — a retrospective statement, a wage-only claim — produces an auditable "no" rather than a fabricated record.

## Rules

1. **Output is always a draft.** `record_status` stays `draft`; only a human moves a record to `verified`, and every field is checked against the source (constitution, Principle I). Nothing in `data/interim/` is ever analysed.
2. **This script never writes to `data/processed/`.** Promoting a draft is a separate, human step that also writes `verification_log` rows.
3. **Pass text, not PDFs.** Extract the passage first (`pdftotext -f N -l N file.pdf out.txt`) so the exact input is hashable and re-runnable.
4. **Check the quote.** The script warns when `quote_verbatim` is not a substring of the input passage. Treat that warning as a blocker, not a note — a paraphrased quote fails Principle II.
5. **Horizons are not defaulted here.** The prompt forbids it and the evaluation protocol applies defaults later, under a rubric that is registered separately.
6. **Pin the model in the record.** If the default model changes, log it in `docs/decisions/` — an analysis that mixes model snapshots without recording which is which cannot be reproduced.
