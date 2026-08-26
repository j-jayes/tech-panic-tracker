# DR-004 — Protocol parameters confirmed for the pilot

**Date:** 2026-08-26 · **Status:** accepted (provisional values now confirmed; frozen at the stated registration) · **Closes:** OPEN-QUESTIONS 5, 6, 7, 10, 11

## Decisions

**Screening cap = 2,000 hits per stratum × database** (search protocol §1.3, D11). Confirmed. Precedent: a prior paper by one of the authors used a 1,000-hit cap per search term and found it sufficient to characterise the yield; 2,000 doubles that headroom for the modern strata, which are the only ones expected to hit the cap. Over-cap cells are randomly sampled within stratum × year with a seeded script and sampling weights carried into every corpus statistic. **Revisit after P1** once per-database yields are measured — if E5 cells routinely return 10⁵ hits, the binding constraint is the sampling design, not the cap. Frozen at Registration 1.

**Verdict band edges kept as drafted** — ratio *r* = realised/claimed at the horizon year, two-sided and log-symmetric: 2/3–3/2 `clearly_correct`; 0.4–2/3 or 3/2–2.5 `mostly_correct`; 0.1–0.4 or 2.5–10 `mixed`; beyond that with direction intact `mostly_wrong`; direction contradicted `clearly_wrong`. Horizon defaults likewise unchanged ("soon" = 10 years, "within a generation" = 30, "in our lifetime" = 40). These are **explicitly provisional**: the pilot's trial evaluations exist to stress-test them, and the bands may be adjusted once we have seen how real predictions fall across them. The rubric is frozen at **Registration 2**, before any verdict counts toward a published statistic; any post-Reg-2 change requires reporting under both pre- and post-amendment rules.

**Evaluation cohort date `evaluated_as_of = 2026-12-31`.** Confirmed. Every verdict states the cohort date; later cohorts append rows rather than overwriting, so a prediction can move from `too_early_to_tell` to a graded verdict without destroying the earlier judgement.

**H1–H5 accepted provisionally** in their PLAN §8.2 directional forms (horizon length, technology generality, author type, mechanism specification, calibration). Both authors own them before Registration 2; they are the registered family for Benjamini–Hochberg correction, and anything else is exploratory.

**Journal strategy agreed** (PLAN §1.7): a *Scientific Data* companion data descriptor, *AER: Insights* as the flagship target, *Economic Journal* as fallback, *Explorations in Economic History* / *JEH* as backups, and a methods paper on the rubric to *IJF* if the rubric proves independently interesting.

## Rationale

These five were carried as "provisional values in place — confirm or change". Confirming them unblocks the pilot; recording them here makes the confirmation auditable, and — more importantly — records *which are still movable and when they stop being movable*. The cap and the bands are the two parameters where post-hoc adjustment would be most tempting and most damaging, which is exactly why their freeze points are named.

## Consequences

- `protocol/search-protocol.md` and `protocol/evaluation-rubric.md` keep their drafted values; both remain DRAFT until their registrations.
- The pilot's trial evaluations are conducted under the draft rubric and are labelled as such wherever they appear — they are not registered verdicts.
- If pilot evidence moves the bands, the change is logged as a new decision record before Registration 2, with the pilot verdicts recomputed under both.
