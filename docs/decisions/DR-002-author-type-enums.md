# DR-002 — Split `author_type`: financial institutions and think tanks

**Date:** 2026-08-26 · **Status:** accepted · **Closes:** OPEN-QUESTIONS 9

## Decision

Three values are added to the `author_type` vocabulary, effective vocabulary version `0.2-draft`:

| Value | Definition |
|---|---|
| `financial_institution` | Bank, asset manager, or insurer research arm publishing forecasts (e.g. Goldman Sachs Global Investment Research). |
| `think_tank_private` | Privately funded non-profit policy research institute (ITIF, Brookings, RAND). |
| `think_tank_govt` | Government-funded or government-affiliated policy research institute (JRC, national productivity commissions). |

Two existing definitions are amended (values unchanged): `consultancy` no longer claims financial-institution research arms, and `think_tank` is marked a legacy umbrella to be avoided in favour of the split values.

**Boundary rule.** An intergovernmental organisation forecasting in its official capacity stays `igo` even when the forecast is financial in character — the IMF's 2024 exposure estimate is `igo`, not `financial_institution`. The distinguishing test is the institution's mandate, not the content of the claim.

## Rationale

H3 in the analysis plan compares accuracy across author types, so the taxonomy has to separate institutions whose incentives plausibly differ. Folding Goldman Sachs into `consultancy` merged a sell-side research note with a client-facing consulting product; folding both public and private policy institutes into one `think_tank` merged funding structures that H3 might well distinguish. Splitting now costs nothing; splitting later would not be possible.

**Timing matters.** The constitution makes controlled vocabularies append-only *after Registration 1*. This change lands before Registration 1, which is why the two definition amendments are permissible at all — after Reg 1 only additions would be, and the `consultancy` and `think_tank` wording would have been frozen as written.

## Consequences

- `data/vocab/enum_definitions.csv`: three rows appended, two definitions amended.
- `schemas/datapackage.json`: the enum extended in **both** `authors.author_type` and `prediction_authors.author_type_at_prediction`.
- `docs/codebook.md` regenerated (CI enforces staleness).
- Pilot rows use the new values: Goldman Sachs 2023 → `financial_institution`; ITIF 2022 → `think_tank_private`.
- **Open, for Ben:** `source_type` has no financial-institution value; a Goldman *Global Economics Analyst* note is currently typed `consultancy_report`, whose definition explicitly covers financial institutions. Either that is fine or `source_type` needs its own split before Registration 1.
