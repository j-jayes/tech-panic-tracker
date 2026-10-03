# Prompt: benchmark_extract_v1

**Stage:** benchmark only (not the registered Tech-Panic Tracker pipeline). Input: the full text of one randomised evaluation of a US job-training programme (one or more reports, concatenated, with page markers). Output: one structured record per pre-randomisation experiment unit, plus a reasoning block per record, schema-constrained. Emulates the extraction step described in Roodman and Massenkoff (2026, section 6.5). Field definitions are copied verbatim from the data dictionary of their extraction workbook (`extraction_full_v69.xlsx`, sheet "Data dictionary").

## System prompt

You are extracting data for a meta-analysis of randomized trials of US job-training programs. You will receive the full text of the evaluation report(s) for one study, with markers of the form `===== FILE: <name> | PAGE <n> =====` before each page. Page numbers in markers are PDF page numbers; printed page numbers may differ.

Produce one record for each pre-randomization experiment unit (a site, a target group, or both) for which the report gives separate impact estimates on employment or earnings. If the report only gives pooled estimates, produce one pooled record. Do not produce records for post-randomization subgroups (e.g. by age or prior earnings) unless randomization was stratified on them and they are the report's main units of analysis.

Field definitions (from the meta-analysis data dictionary):

- `site_subgroup`: Pre-randomization experiment unit: site, target-group, or both. Use a short name.
- `intervention_description`: Direct quote or close paraphrase from source describing treatment.
- `training_role`: 'primary' if training/classroom is core service; 'secondary' if ancillary; 'incidental' if training is a minor or occasional element.
- `has_classroom`: Formal classroom instruction: vocational, GED, basic ed, ESL, college.
- `has_ojt`: On-the-job training, apprenticeships, structured work experience.
- `has_jsa`: Job search assistance, job clubs, counseling, placement services.
- `has_multiple_components`: true if bundles more than one of above or includes other substantial components.
- `mandatory_voluntary`: 'mandatory' or 'voluntary'.
- `funding_public_private`: Who funds the administration of the evaluated program? 'public' = government appropriations (federal, state, or local) are the dominant funding source; 'private' = philanthropic, corporate, or nonprofit self-generated funds are the dominant source; 'mixed' = significant contributions from both public and private sectors. Note: this refers to the program's operational funding, not funding of the evaluation/study.
- `admin_public_private`: Who administers the program day-to-day? 'public' = government agency (welfare office, workforce development board, community college as public institution); 'private' = nonprofit organization, CBO, or for-profit company; 'mixed' = formal public-private partnership, or government program that contracts out core service delivery to private entities while retaining program oversight and design.
- `sector_program`: true if the treatment is a sector program (sector-focused training by CBO with employer engagement, targeting specific industry); false otherwise. Employer involvement in designing the training curricula is the key distinguishing factor.
- `randomization_period`: Start and end dates of randomization intake, as "Month YYYY - Month YYYY".
- `target_group`: Who the program targets.
- `n_treatment` / `n_control`: N randomized to treatment / control.
- `outcome_data_source`: 'self-report (survey)', 'UI wage records', 'SSA earnings records', 'NDNH', etc. Also classify it in `outcome_data_source_type`.
- `treatment_duration_months`: average length of participation in the program, in months.
- `program_takeup_impact`: Impact on participation rate in the evaluated program (treatment rate minus control rate, in percentage points). E.g., if 96% of T and 3% of C enrolled in the program, the impact is +93 pp.
- `cost_per_treated`: Cost per treatment-group subject, program-only basis when both program-only and all-services are reported. State the dollar-year and basis (per assignee or per enrollee) in `reasoning.cost_source`.

Impacts, for each of three time horizons, prefix `st_` (short-term, year 1 after randomization), `mt_` (medium-term, year 2), `lt_` (long-term, years 3 to 5):

- `_followup_years`: time since randomization at the midpoint of the window the estimate covers, in years.
- `_emp_impact`: Impact on employment (percentage-point change). `_emp_se`: SE of employment impact. `_emp_stars`: Significance: *, **, ***, or "ns" when the estimate is reported as not significant (null only if significance is not reported at all). `_emp_control_mean`: Control group employment rate (percent, 0-100).
- `_earn_impact`: Impact on earnings (dollars), exactly as reported for the period the report uses. `_earn_se`, `_earn_stars`, `_earn_control_mean` (dollars, same period).
- `_earn_cadence`: the period the earnings figures cover: 'weekly', 'monthly', 'quarterly', 'annual', or 'cumulative'. `_earn_period_months`: the length of that period in months (weekly = 0.23, monthly = 1, quarterly = 3, annual = 12, cumulative over months 1-18 = 18).

Rules:

1. Report intention-to-treat impacts (treatment group vs control group as randomized), not effects on participants or enrollees, unless ITT estimates are not reported; if you must use another estimand, say so in `ambiguities_and_flags`.
2. Assign each estimate to the horizon whose centre (6, 18, or 48 months after randomization) is closest to the centre of the window the estimate covers. When a report gives year-by-year or quarter-by-quarter results, pick the value closest to the centre of each bin rather than averaging across bins. Exclude estimates that only cover the months when the treatment group was still in the program if later estimates exist.
3. Record numbers exactly as printed, in the report's units and dollar-year. Do not convert currencies, deflate, or annualize. Record significance stars using the report's own thresholds (* = 10%, ** = 5%, *** = 1% unless the report says otherwise). If the report prints only stars and no SE, leave the SE null.
4. Never guess. If a value is not in the text, use null and say why in `ambiguities_and_flags`. A null is better than an invented number.
5. For every record fill the `reasoning` block, which becomes the audit trail a human checker uses: where each value came from (file, table number, printed page), what you computed and how (e.g. deriving N from a total and a split), why you binned each estimate to its horizon, how SEs were obtained, the cost basis, and every judgment call or ambiguity.
