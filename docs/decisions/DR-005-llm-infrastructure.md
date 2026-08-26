# DR-005 — LLM provider, model pinning, and secret handling

**Date:** 2026-08-26 · **Status:** accepted · **Closes:** OPEN-QUESTIONS 12, 16

## Decisions

**Provider and model.** LLM-assisted extraction uses the **Google Gemini API**, default model **`gemini-3.7-flash`**, temperature 0, with Pydantic-constrained structured output. The API is enabled on GCP project `jonathanjayes-com` (billing enabled), and the key is restricted to the Generative Language API alone.

**Model pinning.** Calls name an exact model id, never a floating alias such as `gemini-flash-latest`. Every extraction output records the `model_version` the API actually served alongside the id requested, plus the prompt version and a SHA-256 of the input passage. A corpus drafted under two model snapshots is analysable only if each record says which one drafted it. Changing the default model requires a new decision record and a re-run of the frozen regression set (extraction protocol §5).

**Secrets.** `GEMINI_API_KEY` lives in two places and nowhere else: a git-ignored local `.env`, and a GitHub Actions repository secret of the same name. `.env.example` documents the variable without its value. Keys are never committed, never pasted into prompts, and never written into `data/`.

**Infrastructure as code.** Every step that created this setup — API enablement, key creation, key restriction, secret upload — is recorded as a runnable command in [`docs/infrastructure.md`](../infrastructure.md), not as institutional memory. The same file carries the deferred OSF project-creation steps.

**Entry point.** The `.claude/skills/gemini-extract/` skill is the single supported way to run an extraction: it reads the system prompt from `protocol/prompts/extract_v1.md` at runtime, writes only to `data/interim/`, and warns when `quote_verbatim` is not a substring of the input.

## Rationale

Gemini was chosen for cost at the flash tier — the corpus is expected to run to thousands of passages, and detection (stage 2) is high-recall by design, so it processes far more text than it keeps — and for native structured output, which lets the schema, not a parser, enforce the enum vocabulary. Constraining generation to the Pydantic model removes an entire class of failure (invented enum values, renamed fields) that would otherwise surface as validation errors after the fact.

Pinning matters more here than in most projects. The registered protocol commits us to a stated model; if the alias silently rolls forward, the preregistration no longer describes what ran, and the LLM–human agreement rates computed in the reliability report would pool incomparable snapshots.

## Consequences

- `pyproject.toml`: the `llm` extra is now `google-genai`, `pydantic`, `python-dotenv` (previously `anthropic`).
- `.env.example` committed; `.env` git-ignored; GitHub secret set.
- A smoke test on the Simon 1960 quotation returned a well-formed record — and confidently dated it **1965**, the standard misattribution that `docs/research/landmark-seed-list.md` exists to correct. The pilot notebook uses this as the worked example of why Principle I requires human verification of every field rather than spot checks.
