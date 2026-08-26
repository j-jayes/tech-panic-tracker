# Evaluation Rubric (DRAFT v0.1 — to be frozen at OSF Registration 2, before any verdict is assigned)

Companion to `docs/PLAN.md` §6. This is the credibility-critical protocol: no verdict may be recorded before this document is registered. Outcome-data sources: `docs/research/outcome-data-inventory.md`.

## 1. Verdict basis

Outcome-based (decision D10): did the predicted employment state occur in the stated locus and horizon, regardless of cause. `attribution_confidence` is exploratory only. Where a claim is ambiguous between gross and net, the default reading is **net employment in the stated locus**, flagged `reading_defaulted = true`. Worked example: ATM-era teller predictions (Bessen: tellers grew ~500k→~600k during peak ATM diffusion, then fell after ~2010).

## 2. Outcome matching priority

1. Official series matched via occupation/industry codes — IPUMS OCC1950 (US 1850–, decennial), IPUMS CPS OCC2010 (annual 1962–), BLS OEWS (point-in-time levels only — NOT trends, per BLS's own warning), BLS CES (industry, 1939–), UK: I-CeM 1851–1911, Cambridge Group PST, Nomis APS; cross-country: ILOSTAT.
2. Academic retrospectives (e.g. Feigenbaum & Gross QJE 2024 for telephone operators; Georgieff & Milanez OECD 2021 for Frey–Osborne).
3. Industry statistics.
4. None adequate → `insufficient_evidence`, failed search logged.

`resolution_year_used` snaps to nearest data-availability year (census decades pre-1940); the snap is recorded. Crosswalk chain: HISCO↔OCC1950 (Mourits, DOI 10.17026/dans-zap-qxmc) ↔ OCC2010 ↔ SOC2018; ISCO-08↔SOC2010↔SOC2018 (BLS files). Where the crosswalk coarsens the locus, record the evaluated series in `series_or_table_id` and note the coarsening.

## 3. Horizon defaults (lookup table)

| Stated phrase class | Default horizon |
|---|---|
| "soon", "near future", "shortly", "imminent" | 10 years |
| "within a generation" | 30 years |
| "in our lifetime(s)" | 40 years |
| "by end of century / decade" | literal |
| explicit duration/year | literal |
| "eventually", "someday", "long run" | `unfalsifiable`; exception: explicit magnitude → 50-year convention + sensitivity flag |

Every defaulted case sets `horizon_operationalized = true`; analyses run with/without.

## 4. Verdict bands (claim_type = employment_outcome)

Quantified (T1/T2): ratio *r* = realised/claimed magnitude at `horizon_end_year`, two-sided, log-symmetric:

| *r* | Verdict |
|---|---|
| 2/3 – 3/2 | clearly_correct |
| 0.4 – 2/3 or 3/2 – 2.5 | mostly_correct |
| 0.1 – 0.4 or 2.5 – 10, or right direction wrong locus | mixed |
| < 0.1 or > 10, direction not contradicted | mostly_wrong |
| direction contradicted | clearly_wrong |

Denominator for "X% of jobs": employment stock **at horizon year** (sensitivity: prediction-year stock). Ranges: outcome inside stated interval → clearly_correct; otherwise score against nearer endpoint; `magnitude_headline` scored separately under point rules (registered secondary). Directional (T3): capped at mostly_correct. T4 → unfalsifiable unless defaults rescue. **Timing slack sensitivity:** recompute at horizon_end + 25% of horizon length.

## 5. claim_type-specific tracks (never pooled)

- **exposure_risk**: differential test — did occupations the source ranked high-exposure decline (employment or growth) relative to low-exposure occupations over the horizon? Requires a published occupation-level ranking (Frey–Osborne, OECD have them); aggregate-only exposure claims → `unfalsifiable` on this track. Validation anchors for the F–O row: Georgieff & Milanez 2021; Coelli & Borland 2019; ITIF 2022.
- **capability_milestone**: did the capability materialise commercially by horizon (adoption data, technical retrospectives)? E.g. Simon 1960, Hinton 2016 (radiologists — falsified on timing; Hinton's 2025 concession is a `revisits` row).

## 6. Too-early logic

Cohort 1: `evaluated_as_of = 2026-12-31`. `horizon_end_year` > 2026 → `too_early_to_tell` except early resolution (already fully realised → clearly_correct; required milestone already missed → clearly_wrong). ≥50% horizon elapsed → optional exploratory trajectory note (non-ordinal). Future cohorts (2031, …) append new evaluation rows.

## 7. Blinding & bias controls

Redacted packets (claim_summary, level, geography, codes, horizon, magnitude; author/venue/quote masked); `blinding_status` recorded honestly; verdict distribution by blinding status as robustness. Second evaluator (the other author) independently scores 20% of evaluations; quadratic-weighted κ reported. Rationale must cite evidence rows and the operationalised claim, never the author. Every ordinal verdict ≥1 evidence row; `clearly_*` requires official_statistics/census_series/academic_study.

## 8. Naive-baseline skill score (registered secondary, H6)

For each evaluable quantified prediction: construct (a) persistence forecast and (b) linear trend from the 10 pre-prediction years of the same outcome series; score both under the same bands; report share of predictions beating their naive counterpart, by author type and era. Template: BLS's own projection evaluations (Veneri 1997; Alpert & Auyer 2003; Byun et al. 2015 — which benchmark BLS against naive models).
