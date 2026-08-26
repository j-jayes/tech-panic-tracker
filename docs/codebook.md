# Tech-Panic Tracker Codebook

**GENERATED FILE — do not edit by hand.** Regenerate with `python -m pipeline.codebook`. Source of truth: `schemas/datapackage.json` + `data/vocab/`. Generated 2026-08-26.

Prose coding rules (inclusion criteria, revisit-vs-new-prediction rule, apocryphal-quote hazards, worked examples) live in `docs/PLAN.md` and `protocol/`; this file documents the machine schema.

## Table: `sources`

Path: `data/processed/sources.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `source_id` | string | yes | pattern `^src_[a-z0-9]+$` |
| `title` | string | yes |  |
| `container_title` | string |  |  |
| `pub_date` | string |  | pattern `^\d{4}(-\d{2})?(-\d{2})?$`; Partial dates allowed: YYYY, YYYY-MM, or YYYY-MM-DD |
| `source_type` | string | yes | enum (see below) |
| `venue_country` | string |  | pattern `^[A-Z]{2}$` |
| `language_original` | string |  | pattern `^[a-z]{2}$` |
| `is_translation` | boolean |  |  |
| `url` | string |  |  |
| `archive_url` | string |  | Permalink (Wayback/HathiTrust/etc.); required whenever url is set (pandera rule) |
| `doi` | string |  |  |
| `retrieval_track` | string | yes | enum (see below) |
| `search_query_id` | string |  |  |
| `parent_source_id` | string |  |  |
| `duplicates_of` | string |  |  |
| `accessed_date` | date |  |  |
| `full_text_location` | string |  |  |
| `notes` | string |  |  |

### `sources.source_type` values

| Value | Definition |
|---|---|
| `journal_article` | Peer-reviewed journal article |
| `working_paper` | Working/discussion paper |
| `book` | Monograph |
| `book_chapter` | Chapter in edited volume |
| `government_report` | Report by a government body |
| `igo_report` | Report by an intergovernmental organization |
| `consultancy_report` | Report by a consultancy or financial institution |
| `think_tank_report` | Report by a think tank |
| `newspaper_article` | Newspaper item |
| `magazine_article` | Magazine/periodical item |
| `speech_transcript` | Speech, lecture, press conference, or interview transcript |
| `testimony` | Parliamentary/congressional testimony or debate |
| `pamphlet` | Pamphlet, petition, letter, or broadside |
| `blog_post` | Blog/newsletter/social post |
| `other` | Fits no category; explain in notes |

### `sources.retrieval_track` values

| Value | Definition |
|---|---|
| `database` | Found via a registered Track A database query |
| `snowball` | Found via citation chasing from a seed |
| `expert_source` | Found via institutional publisher sweep |
| `pilot_seed` | Hand-collected landmark item (P1 pilot) |

## Table: `authors`

Path: `data/processed/authors.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `author_id` | string | yes | pattern `^auth_[a-z0-9]+$` |
| `display_name` | string | yes |  |
| `author_type` | string | yes | enum (see below); Canonical/most-associated type; analyses use prediction_authors.author_type_at_prediction |
| `orcid_or_viaf` | string |  |  |
| `notes` | string |  |  |

### `authors.author_type` values

| Value | Definition |
|---|---|
| `academic` | University or research-institute researcher (as of prediction date) |
| `government_agency` | National/subnational government body or official speaking for it |
| `igo` | Intergovernmental organization (OECD, ILO, IMF, World Bank, WEF) |
| `consultancy` | Commercial consultancy or analyst firm (financial-institution research arms take financial_institution from v0.2) |
| `think_tank` | Legacy umbrella for non-profit policy research institutes; prefer think_tank_private or think_tank_govt from v0.2 |
| `journalist` | Reporter, columnist, or popular non-fiction writer |
| `futurist` | Professional forecaster/commentator outside academia and industry |
| `industry_executive` | Executive or investor in a technology-producing or -using firm |
| `labor_organization` | Union, workers' association, or labour movement figure |
| `politician` | Elected or campaigning political figure |
| `anonymous_institutional` | Unsigned institutional voice (editorials, anonymous reports) |
| `financial_institution` | Bank, asset manager, or insurer research arm publishing forecasts (Goldman Sachs Global Investment Research); an IGO forecasting in its official capacity stays igo |
| `think_tank_private` | Privately funded non-profit policy research institute (ITIF, Brookings, RAND) |
| `think_tank_govt` | Government-funded or government-affiliated policy research institute (JRC, national productivity commissions) |
| `other` | Fits no category; explain in notes |

## Table: `prediction_authors`

Path: `data/processed/prediction_authors.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `prediction_id` | string | yes |  |
| `author_id` | string | yes |  |
| `author_role` | string | yes | enum (see below) |
| `author_type_at_prediction` | string | yes | enum (see below) |

### `prediction_authors.author_role` values

| Value | Definition |
|---|---|
| `sole` | Only author |
| `lead` | First/lead author of several |
| `coauthor` | Non-lead co-author |
| `institutional` | Institution credited as author |

### `prediction_authors.author_type_at_prediction` values

| Value | Definition |
|---|---|
| `academic` | University or research-institute researcher (as of prediction date) |
| `government_agency` | National/subnational government body or official speaking for it |
| `igo` | Intergovernmental organization (OECD, ILO, IMF, World Bank, WEF) |
| `consultancy` | Commercial consultancy or analyst firm (financial-institution research arms take financial_institution from v0.2) |
| `think_tank` | Legacy umbrella for non-profit policy research institutes; prefer think_tank_private or think_tank_govt from v0.2 |
| `journalist` | Reporter, columnist, or popular non-fiction writer |
| `futurist` | Professional forecaster/commentator outside academia and industry |
| `industry_executive` | Executive or investor in a technology-producing or -using firm |
| `labor_organization` | Union, workers' association, or labour movement figure |
| `politician` | Elected or campaigning political figure |
| `anonymous_institutional` | Unsigned institutional voice (editorials, anonymous reports) |
| `financial_institution` | Bank, asset manager, or insurer research arm publishing forecasts (Goldman Sachs Global Investment Research); an IGO forecasting in its official capacity stays igo |
| `think_tank_private` | Privately funded non-profit policy research institute (ITIF, Brookings, RAND) |
| `think_tank_govt` | Government-funded or government-affiliated policy research institute (JRC, national productivity commissions) |
| `other` | Fits no category; explain in notes |

## Table: `technologies`

Path: `data/vocab/technologies.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `tech_id` | string | yes | pattern `^[a-z0-9_]+$` |
| `label` | string | yes |  |
| `generality` | string | yes | enum (see below) |
| `parent_tech_id` | string |  |  |
| `first_commercial_year` | integer |  |  |
| `definition` | string | yes |  |
| `vocab_version` | string | yes |  |

### `technologies.generality` values

| Value | Definition |
|---|---|
| `narrow` | Single-purpose technology (ATM, power loom) |
| `domain` | Spans one broad activity domain (industrial robots, expert systems) |
| `general_purpose` | Pervasive across sectors with complementary innovation (electricity, computing, AI) |

## Table: `prediction_technologies`

Path: `data/processed/prediction_technologies.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `prediction_id` | string | yes |  |
| `tech_id` | string | yes |  |
| `is_primary` | boolean | yes |  |

## Table: `predictions`

Path: `data/processed/predictions.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `prediction_id` | string | yes | pattern `^pred_[a-z0-9]+$` |
| `source_id` | string | yes |  |
| `quote_verbatim` | string | yes |  |
| `quote_locator` | string | yes |  |
| `prediction_date` | string | yes | pattern `^\d{4}(-\d{2})?(-\d{2})?$` |
| `claim_summary` | string | yes |  |
| `claim_type` | string | yes | enum (see below) |
| `level` | string | yes | enum (see below) |
| `geography` | string |  | ISO 3166 alpha-2 codes ;-separated, or GLOBAL |
| `geography_text` | string |  | Historical region as stated when no ISO code fits |
| `occupation_code` | string |  |  |
| `occupation_system` | string |  | enum (see below) |
| `industry_code` | string |  |  |
| `industry_system` | string |  | enum (see below) |
| `direction` | string | yes | enum (see below) |
| `magnitude_type` | string |  | enum (see below) |
| `estimate_type` | string |  | enum (see below) |
| `magnitude_value` | number |  |  |
| `magnitude_low` | number |  |  |
| `magnitude_high` | number |  |  |
| `magnitude_headline` | number |  |  |
| `magnitude_unit` | string |  |  |
| `specificity_tier` | string | yes | enum (see below) |
| `horizon_stated_text` | string |  |  |
| `horizon_type` | string | yes | enum (see below) |
| `horizon_start_year` | integer |  |  |
| `horizon_end_year` | integer |  |  |
| `horizon_operationalized` | boolean |  |  |
| `mechanism_specified` | boolean | yes |  |
| `mechanism_text` | string |  |  |
| `mechanism_type` | string |  | enum (see below) |
| `is_conditional` | boolean |  |  |
| `panic_valence` | string | yes | enum (see below) |
| `is_secondary_report` | boolean |  |  |
| `primary_source_status` | string |  | enum (see below) |
| `derived_from_prediction_id` | string |  | Citation lineage: set when this prediction's estimate derives from an upstream study (e.g. PwC 2017 from Frey-Osborne 2013); such predictions are not independent |
| `extraction_method` | string | yes | enum (see below) |
| `llm_model` | string |  | Exact dated model snapshot ID, never a floating alias |
| `llm_prompt_version` | string |  |  |
| `created_by` | string | yes |  |
| `created_date` | date | yes |  |
| `verified_by` | string |  |  |
| `verified_date` | date |  |  |
| `record_status` | string | yes | enum (see below) |

### `predictions.claim_type` values

| Value | Definition |
|---|---|
| `employment_outcome` | Asserts jobs will be lost/created/transformed in quantity |
| `exposure_risk` | Asserts a share of jobs is at risk/susceptible/exposed, without asserting realised loss (Frey-Osborne style) |
| `capability_milestone` | Asserts machines will be able to perform some human work by a horizon, without an employment quantity |

### `predictions.level` values

| Value | Definition |
|---|---|
| `task` | Specific tasks within jobs |
| `firm` | A named firm or workplace |
| `occupation` | A named occupation |
| `industry` | A named industry/sector |
| `country_region` | A country or sub-national region economy-wide |
| `global` | World economy |

### `predictions.occupation_system` values

| Value | Definition |
|---|---|
| `soc2018` | US Standard Occupational Classification 2018 |
| `hisco` | Historical International Standard Classification of Occupations |
| `none` | No occupation code applicable |

### `predictions.industry_system` values

| Value | Definition |
|---|---|
| `naics2022` | North American Industry Classification System 2022 |
| `sic1987` | US Standard Industrial Classification 1987 |
| `none` | No industry code applicable |

### `predictions.direction` values

| Value | Definition |
|---|---|
| `displacement` | Gross claim: technology will displace workers in the stated locus |
| `creation` | Gross claim: technology will create jobs in the stated locus |
| `net_negative` | Net claim: overall employment falls |
| `net_positive` | Net claim: overall employment rises (more created than destroyed) |
| `transformation_neutral` | Work changes character without an asserted quantity change (boundary case) |
| `ambiguous` | Direction not determinable from the text |

### `predictions.magnitude_type` values

| Value | Definition |
|---|---|
| `percent_of_jobs` | Share of jobs/employment |
| `absolute_jobs` | Absolute number of jobs/workers |
| `share_of_tasks` | Share of tasks/work activities |
| `qualitative_total` | Qualitative claim of total/near-total replacement |
| `qualitative_partial` | Qualitative claim of partial replacement |
| `none` | No magnitude stated |

### `predictions.estimate_type` values

| Value | Definition |
|---|---|
| `point` | Single-number claim |
| `range` | Explicit low-high interval or scenario band |
| `scenario_conditional` | Magnitude conditional on named scenario/policy |
| `none` | No numeric estimate |

### `predictions.specificity_tier` values

| Value | Definition |
|---|---|
| `T1_quantified` | Explicit magnitude AND explicit horizon |
| `T2_semi_quantified` | Magnitude XOR horizon explicit |
| `T3_directional` | Clear direction and locus, no numbers |
| `T4_rhetorical` | Vague alarm or reassurance with no operationalizable claim |

### `predictions.horizon_type` values

| Value | Definition |
|---|---|
| `explicit_year` | Names a calendar year |
| `explicit_duration` | Names a duration (within twenty years) |
| `vague_phrase` | Vague temporal phrase (soon, within a generation) |
| `conditional` | Horizon conditional on events/policy |
| `none` | No temporal reference |

### `predictions.mechanism_type` values

| Value | Definition |
|---|---|
| `cost_substitution` | Machine cheaper than labour at same output |
| `capability_parity` | Machine reaches human capability level |
| `scale_speed` | Machine speed/scale advantages |
| `deskilling` | Technology reduces skill requirements, enabling substitution |
| `demand_shift` | Demand-side changes triggered by the technology |
| `other` | Mechanism stated but fits no category |

### `predictions.panic_valence` values

| Value | Definition |
|---|---|
| `alarm` | Presented as a warning/threat |
| `reassurance` | Presented as debunking or calming replacement fears |
| `neutral_forecast` | Presented as dispassionate projection |

### `predictions.primary_source_status` values

| Value | Definition |
|---|---|
| `primary_located` | Primary source found and used |
| `secondary_only` | Only the secondary report located after documented attempt |
| `not_chased` | Primary chase not yet attempted |

### `predictions.extraction_method` values

| Value | Definition |
|---|---|
| `llm_assisted` | LLM draft, human-verified |
| `human_manual` | Coded directly by a human |

### `predictions.record_status` values

| Value | Definition |
|---|---|
| `draft` | LLM or human draft, not yet verified; lives in interim only |
| `verified` | Human-verified against source text |
| `locked` | Immutable; corrections via new row + deprecated |
| `deprecated` | Superseded by a correction row |

## Table: `evaluations`

Path: `data/processed/evaluations.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `evaluation_id` | string | yes | pattern `^eval_[a-z0-9]+$` |
| `prediction_id` | string | yes |  |
| `verdict` | string | yes | enum (see below) |
| `verdict_rationale` | string | yes |  |
| `resolution_year_used` | integer |  |  |
| `evaluated_as_of` | date | yes |  |
| `evaluator_id` | string | yes |  |
| `second_evaluator_id` | string |  |  |
| `second_verdict` | string |  | enum (see below) |
| `blinding_status` | string | yes | enum (see below) |
| `evaluator_confidence` | string |  | enum (see below) |
| `attribution_confidence` | string |  | enum (see below); Exploratory only; never gates a verdict |
| `reading_defaulted` | boolean |  | True when the gross-vs-net default reading was applied |
| `created_by` | string | yes |  |
| `created_date` | date | yes |  |
| `verified_by` | string |  |  |
| `verified_date` | date |  |  |
| `record_status` | string | yes | enum (see below) |

### `evaluations.verdict` values

| Value | Definition |
|---|---|
| `clearly_correct` | Direction, rough magnitude (ratio 2/3-3/2), and timing all borne out |
| `mostly_correct` | Direction correct; magnitude or timing off by <= one band (ratio 0.4-2/3 or 3/2-2.5) |
| `mixed` | Partially realised (ratio 0.1-0.4 or 2.5-10, or right direction wrong locus) |
| `mostly_wrong` | Direction weakly wrong or magnitude off by > one band (ratio <0.1 or >10) |
| `clearly_wrong` | Direction contradicted or claimed outcome plainly did not occur in horizon |
| `too_early_to_tell` | Horizon extends beyond evaluation cohort year |
| `unfalsifiable` | No operationalizable claim even after horizon defaults |
| `insufficient_evidence` | Falsifiable but no adequate outcome data found; data search logged |

### `evaluations.second_verdict` values

| Value | Definition |
|---|---|
| `clearly_correct` | Direction, rough magnitude (ratio 2/3-3/2), and timing all borne out |
| `mostly_correct` | Direction correct; magnitude or timing off by <= one band (ratio 0.4-2/3 or 3/2-2.5) |
| `mixed` | Partially realised (ratio 0.1-0.4 or 2.5-10, or right direction wrong locus) |
| `mostly_wrong` | Direction weakly wrong or magnitude off by > one band (ratio <0.1 or >10) |
| `clearly_wrong` | Direction contradicted or claimed outcome plainly did not occur in horizon |
| `too_early_to_tell` | Horizon extends beyond evaluation cohort year |
| `unfalsifiable` | No operationalizable claim even after horizon defaults |
| `insufficient_evidence` | Falsifiable but no adequate outcome data found; data search logged |

### `evaluations.blinding_status` values

| Value | Definition |
|---|---|
| `blinded` | Evaluator saw only the redacted packet and did not recognise the prediction |
| `partially_blinded` | Evaluator suspects but is not certain of the source |
| `unblindable` | Prediction identifiable from the claim itself (landmark items) |

### `evaluations.evaluator_confidence` values

| Value | Definition |
|---|---|
| `high` | Evaluator confident in the verdict |
| `medium` | Some judgment calls involved |
| `low` | Verdict rests on thin or ambiguous evidence |

### `evaluations.attribution_confidence` values

| Value | Definition |
|---|---|
| `high` | Strong evidence the technology drove the outcome |
| `medium` | Plausible but contested attribution |
| `low` | Outcome likely driven by other factors |
| `not_assessed` | Attribution not examined |

### `evaluations.record_status` values

| Value | Definition |
|---|---|
| `draft` | LLM or human draft, not yet verified; lives in interim only |
| `verified` | Human-verified against source text |
| `locked` | Immutable; corrections via new row + deprecated |
| `deprecated` | Superseded by a correction row |

## Table: `outcome_evidence`

Path: `data/processed/outcome_evidence.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `evidence_id` | string | yes | pattern `^evid_[a-z0-9]+$` |
| `evaluation_id` | string | yes |  |
| `evidence_type` | string | yes | enum (see below) |
| `dataset_name` | string |  |  |
| `series_or_table_id` | string |  |  |
| `citation` | string | yes |  |
| `url` | string |  |  |
| `value_summary` | string | yes |  |
| `covers_years` | string |  |  |
| `notes` | string |  |  |

### `outcome_evidence.evidence_type` values

| Value | Definition |
|---|---|
| `official_statistics` | Government statistical series (BLS, ONS, ILOSTAT...) |
| `census_series` | Population census occupation/industry tabulations or microdata |
| `industry_association` | Industry body or firm-reported statistics |
| `academic_study` | Peer-reviewed retrospective study |
| `news_retrospective` | Journalistic retrospective account |
| `other` | Fits no category; explain in notes |

## Table: `revisits`

Path: `data/processed/revisits.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `revisit_id` | string | yes | pattern `^rev_[a-z0-9]+$` |
| `prediction_id` | string | yes |  |
| `revisit_source_id` | string | yes |  |
| `revisit_date` | string |  | pattern `^\d{4}(-\d{2})?(-\d{2})?$` |
| `revisit_stance` | string | yes | enum (see below) |
| `quote_verbatim` | string | yes |  |
| `quote_locator` | string | yes |  |
| `created_by` | string | yes |  |
| `created_date` | date | yes |  |
| `verified_by` | string |  |  |
| `verified_date` | date |  |  |
| `record_status` | string | yes | enum (see below) |

### `revisits.revisit_stance` values

| Value | Definition |
|---|---|
| `reaffirmed` | Author restates the claim with same or greater confidence |
| `moderated` | Author weakens magnitude or confidence |
| `deadline_extended` | Author pushes the horizon later |
| `retracted` | Author explicitly withdraws the claim |
| `reversed` | Author asserts the opposite |
| `silent_contradiction` | Author later writes something incompatible without acknowledgment |

### `revisits.record_status` values

| Value | Definition |
|---|---|
| `draft` | LLM or human draft, not yet verified; lives in interim only |
| `verified` | Human-verified against source text |
| `locked` | Immutable; corrections via new row + deprecated |
| `deprecated` | Superseded by a correction row |

## Table: `coders`

Path: `data/processed/coders.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `coder_id` | string | yes |  |
| `name` | string | yes |  |
| `role` | string | yes | enum (see below) |

### `coders.role` values

| Value | Definition |
|---|---|
| `pi` | Principal investigator |
| `ra` | Research assistant |
| `llm` | Language-model coder configuration |

## Table: `search_log`

Path: `data/logs/search_log.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `query_id` | string | yes |  |
| `track` | string | yes | enum (see below) |
| `database` | string | yes |  |
| `era_stratum` | string |  | enum (see below) |
| `query_string` | string | yes |  |
| `filters` | string |  |  |
| `date_run` | date | yes |  |
| `n_results` | integer |  |  |
| `n_exported` | integer |  |  |
| `sampled` | boolean |  | True when the stratified sampling cap applied |
| `sampling_fraction` | number |  |  |
| `sampling_seed` | integer |  |  |
| `exporter` | string |  |  |

### `search_log.track` values

| Value | Definition |
|---|---|
| `database` | Found via a registered Track A database query |
| `snowball` | Found via citation chasing from a seed |
| `expert_source` | Found via institutional publisher sweep |

### `search_log.era_stratum` values

| Value | Definition |
|---|---|
| `E1` | 1800-1870: the machinery question |
| `E2` | 1870-1920: mechanisation and the machine age |
| `E3` | 1920-1955: technological unemployment debate |
| `E4` | 1955-1995: automation, cybernation, microelectronics |
| `E5` | 1995-present: computerisation and AI |

## Table: `screening_log`

Path: `data/logs/screening_log.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `screening_id` | string | yes |  |
| `source_id` | string | yes |  |
| `stage` | string | yes | enum (see below) |
| `decision` | string | yes | enum (see below) |
| `exclusion_reason` | string |  | enum (see below) |
| `screener_id` | string | yes |  |
| `dual_screened` | boolean |  |  |
| `second_screener_id` | string |  |  |
| `second_decision` | string |  | enum (see below) |
| `date` | date | yes |  |

### `screening_log.stage` values

| Value | Definition |
|---|---|
| `S1_title` | Title/snippet screen |
| `S2_fulltext` | Full-text screen |
| `S3_extraction` | Prediction extraction |

### `screening_log.decision` values

| Value | Definition |
|---|---|
| `include` | Passes this screening stage |
| `exclude` | Excluded at this stage (reason recorded) |

### `screening_log.exclusion_reason` values

| Value | Definition |
|---|---|
| `no_prediction` | No forward-looking claim present |
| `not_labor_replacement` | Forward-looking but no employment-quantity/capability claim |
| `out_of_scope_language` | Not English and no published English translation |
| `out_of_period` | Before 1800 |
| `duplicate` | Reprint/syndication of an already-screened source |
| `inaccessible` | Full text unobtainable after documented attempts |

### `screening_log.second_decision` values

| Value | Definition |
|---|---|
| `include` | Passes this screening stage |
| `exclude` | Excluded at this stage (reason recorded) |

## Table: `verification_log`

Path: `data/logs/verification_log.csv`

| Field | Type | Required | Constraints / definition |
|---|---|---|---|
| `log_id` | string | yes |  |
| `record_id` | string | yes |  |
| `table_name` | string | yes |  |
| `field` | string | yes |  |
| `llm_value` | string |  |  |
| `human_value` | string |  |  |
| `changed` | boolean | yes |  |
| `coder_id` | string | yes |  |
| `date` | date | yes |  |

## Controlled vocabulary: technologies

| tech_id | Label | Generality | Parent | First commercial year | Definition |
|---|---|---|---|---|---|
| `steam_power` | Steam power | general_purpose |  | 1776 | Stationary and mobile steam engines as motive power for industry and transport |
| `power_loom` | Power loom | narrow | steam_power | 1785 | Mechanised weaving loom displacing hand-loom weavers |
| `shearing_frame` | Shearing frame / gig mill | narrow |  | 1787 | Cloth-finishing machinery targeted by Luddite protests |
| `spinning_machinery` | Spinning machinery | narrow |  | 1769 | Water frame, spinning jenny, mule and successors |
| `agricultural_machinery` | Agricultural machinery | domain |  | 1834 | Reapers, threshers, harvesters and general farm mechanisation |
| `labour_saving_machinery` | Labour-saving machinery (unspecified) | domain |  |  | Umbrella category used when a source names no specific machine; 19th-century 'the machinery question' |
| `electricity` | Electricity / electrification | general_purpose |  | 1882 | Electric power generation and distribution as a production input |
| `telephone_automatic_exchange` | Automatic telephone exchange | narrow | electricity | 1892 | Strowger and successor automatic switching, displacing telephone operators |
| `tractor` | Tractor | narrow |  | 1902 | Internal-combustion farm traction, displacing horses and farm labour |
| `assembly_line` | Assembly line / mass production | domain |  | 1913 | Moving assembly line and Fordist production methods |
| `mechanization_general` | Mechanisation (unspecified) | domain |  |  | Umbrella for interwar 'rationalisation'/mechanisation claims naming no single machine |
| `computing` | Computing | general_purpose |  | 1951 | Electronic digital computers as a general technology class |
| `automation_general` | Automation (unspecified) | domain | computing | 1947 | Umbrella for 1950s-70s 'automation'/'cybernation' claims naming no specific system |
| `numerical_control` | Numerical control machine tools | narrow | automation_general | 1958 | NC/CNC machine tools in manufacturing |
| `industrial_robot` | Industrial robot | domain | automation_general | 1961 | Programmable manipulators in manufacturing (Unimate and successors) |
| `containerization` | Containerisation | domain |  | 1956 | Standardised shipping containers, displacing longshore labour |
| `atm` | Automated teller machine | narrow | computing | 1967 | Cash-dispensing and self-service banking terminals |
| `microelectronics` | Microelectronics / the microchip | general_purpose | computing | 1971 | Semiconductor microprocessors as a pervasive input (late-1970s 'chips' scare) |
| `word_processor` | Word processor | narrow | computing | 1976 | Dedicated and software word processing, displacing typists/secretaries |
| `telematics` | Telematics | domain | computing | 1978 | Computing + telecommunications convergence (Nora-Minc framing) |
| `expert_system` | Expert system | domain | artificial_intelligence | 1980 | Rule-based decision systems of the 1980s AI wave |
| `personal_computer` | Personal computer | domain | computing | 1977 | Desktop computing in offices |
| `internet` | Internet / e-commerce | general_purpose | computing | 1995 | Networked digital communication and commerce |
| `artificial_intelligence` | Artificial intelligence | general_purpose | computing |  | Machine performance of tasks requiring intelligence; umbrella for ML, expert systems, generative AI |
| `machine_learning` | Machine learning | domain | artificial_intelligence |  | Statistical learning systems incl. deep learning; basis of 2010s automation-risk estimates |
| `self_driving_vehicle` | Autonomous vehicle | domain | artificial_intelligence |  | Self-driving cars and trucks, displacing drivers |
| `generative_ai` | Generative AI | domain | artificial_intelligence | 2022 | Large language and diffusion models (ChatGPT era) |
