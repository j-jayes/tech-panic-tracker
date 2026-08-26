# Tech-Panic Tracker

**Two centuries of predictions about technology replacing human labour — collected systematically, classified, and evaluated against what actually happened.**

Since at least the industrial revolution, economists, futurists, governments, and consultancies have predicted that machines would replace human workers. This project builds a preregistered, open dataset of those predictions (~1800 to today), classifies each one (level, technology generality, time horizon, mechanism, author type, specificity), and evaluates every prediction whose horizon has elapsed against employment outcome data, using a graded, evidence-cited rubric.

**Authors:** Jonathan Jayes, Ben Schneider

## Status

Pre-registration planning phase. See [docs/PLAN.md](docs/PLAN.md) for the full project design and [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) for open decisions.

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | Project plan, codebook, decision log, research notes |
| `protocol/` | Search, extraction, and evaluation protocols; OSF preregistration drafts; versioned LLM prompts |
| `data/processed/` | The canonical dataset (CSV; schema-validated) |
| `data/vocab/` | Controlled vocabularies (technologies, enums) |
| `data/logs/` | Search, screening, and verification logs |
| `schemas/` | frictionless Table Schema (`datapackage.json`) |
| `pipeline/` | Extraction/validation pipeline (Python) |
| `analysis/` | Analysis scripts (run end-to-end from `data/processed/`) |
| `specs/` | spec-kit feature specifications |

## Principles

Governed by the [project constitution](.specify/memory/constitution.md): every published record is human-verified with full provenance; locked records are immutable; verdicts cite evidence; counts are generated from logs, never hand-typed; data is CC-BY 4.0 and code MIT.

## Licenses

- Code: [MIT](LICENSE)
- Data, codebook, protocols: [CC-BY 4.0](LICENSE-DATA)

## Conflicts of interest

Neither author has a financial interest in any institution whose predictions are graded in this dataset. (Re-attested at each release.)
