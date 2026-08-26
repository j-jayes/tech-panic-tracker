# Tasks: Pilot Data Pipeline (001)

**Plan**: [plan.md](plan.md) · Status legend: [ ] pending · [x] done

## Phase A — Validation core (US1)

- [x] T001 Create `pyproject.toml`; deps installed into `.venv` (note: pandera dropped — cross-table rules use plain pandas joins, per plan.md risk note)
- [x] T002 Mutation tests implemented as on-the-fly tmp fixtures in `tests/test_validation.py` covering 6 cross-table rules — *remaining for pilot: bad-enum, bad-partial-date, weak-evidence-for-clearly, duplicate-PK cases (frictionless layer)*
- [x] T003 `pipeline/validate/frictionless_check.py` (trusted-context fix for absolute paths)
- [x] T004 `pipeline/validate/cross_table.py` — 6 named rules
- [x] T005 `python -m pipeline.validate` entry; verified: passes pristine, fails mutations with named rules
- [x] T006 `tests/test_validation.py` — 8/8 passing (2026-08-03)
- [x] T007 `.github/workflows/validate.yml` written — *unverified on GitHub Actions until first push*

## Phase B — Generated artifacts (FR-003/004)

- [x] T008 `pipeline/codebook.py` → `docs/codebook.md` generated; all enum values defined (warn/--strict modes; field aliases resolve to base definitions)
- [x] T009 `pipeline/summary.py` — counts by table/era/tier/claim_type/status
- [x] T010 CI staleness check included in workflow

## Phase C — Pilot corpus entry (US2; both PIs)

- [ ] T011 Enter E1 items 1–7 (sources, authors, prediction_authors, predictions, prediction_technologies)
- [ ] T012 Enter E2 items 8–12
- [ ] T013 Enter E3 items 13–19 (Douglas 1930 + Lederer 1938 as `draft` pending primary verbatim)
- [ ] T014 Enter E4 items 20–28 (Nora-Minc as `draft` pending MIT-translation check)
- [ ] T015 Enter E5 items 29–46; set `derived_from_prediction_id` on Deloitte/PwC/WDR/ILO rows → F–O 2013; set claim_type=exposure_risk where applicable (F–O, PwC, IMF)
- [ ] T016 Chase primary verbatim for the three draft items (HathiTrust: American Federationist Aug 1930; ILO 1938 Lederer; MIT Press 1980 Nora-Minc employment chapter)
- [ ] T017 Cross-verify partner's entries (each PI verifies the other's rows; set verified_by)

## Phase D — Trial evaluations (US3)

- [ ] T018 Select ~10 horizon-elapsed items (incl. WEF 2020, Hinton 2016, Simon 1960, Jenkins–Sherman 1979, Gartner 2017, Rifkin 1995, Kennedy-era 1962 framing, Compton 1938, 1966 Commission, Frey–Osborne exposure-track)
- [ ] T019 Collect outcome evidence per item (per docs/research/outcome-data-inventory.md; start IPUMS/BLS registrations first)
- [ ] T020 Independent dual evaluation by both PIs; record both verdicts + evidence rows
- [ ] T021 Disagreement memo → docs/decisions/DR-00X; revise rubric band edges/wording; log every change
- [ ] T022 Run summary + validation; tag repo `pilot-complete`

## Phase E — LLM dry run (US4)

- [ ] T023 `pipeline/llm/run_detect.py` (detect_v1; writes data/interim/; snapshot ID from API response)
- [ ] T024 `pipeline/llm/run_extract.py` (extract_v1; JSON-schema-constrained via tool use)
- [ ] T025 Dry run on 5 full-text sources (Ricardo ch.31, Keynes 1930, Wiener 1949 letter, Triple Revolution 1964, Frey–Osborne 2013)
- [ ] T026 Field-by-field human verification → verification_log.csv; per-field change-rate report; prompt revision notes (→ detect_v2/extract_v2 if any field >30% changed)

## Exit criteria (→ P2 Preregister I)

Codebook v1.0 generated · ≥46 predictions all-era validated · ≥10 dual evaluations + resolved disagreements · LLM agreement measured · schema-change decisions logged · per-database yield measurements scheduled into feature 002 (search harness)
