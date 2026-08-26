# Search Protocol (DRAFT v0.2 — to be frozen at OSF Registration 1)

Companion to `docs/PLAN.md` §4. Empirical grounding: `docs/research/archives-and-apis.md` (live API trials, 2026-08-03) and `docs/research/institutional-publishers.md`. Query strings below are **drafts**; the pilot (P1) measures per-database yields before the strings and caps are frozen.

## 1. Track A — registered database search

### 1.1 Database roster (revised after live API trials)

**Tier A — registered, reproducible (open API or fixed dataset):**

| Database | Access | Role |
|---|---|---|
| GovInfo (Congressional Record 1873–) | api.govinfo.gov/search, free key | US government/testimony predictions; best-in-class reproducibility |
| UK Hansard (1803–) | hansard-api.parliament.uk, no key | UK parliamentary predictions |
| Chronicling America (1756–1963) | loc.gov JSON API, no key (run from institutional IP; ~20 req/min) | US newspapers, strata E1–E3 |
| Trove (1803–1950s) | api.trove.nla.gov.au v3, free key (renew annually) | Anglophone newspapers outside US/UK |
| FRASER (1790s–) | fraser.stlouisfed.org/api, free key | US economic documents, BLS bulletins |
| Europeana Newspapers | api.europeana.eu, free key | supplementary European English-language items |
| Internet Archive | advancedsearch.php, no key — **declared metadata-level only** | discovery |
| HTRC Extracted Features v2.0 | rsync, fixed 17.1M-volume dataset | term-frequency time series (books) |
| Google Ngram v3 exports | bulk download, CC BY 3.0 | normalizing denominator for panic-wave series |

**Tier B — manual documented search (no API contract; log query string + filters + date + result count + screenshot):**
HathiTrust full-text UI (8,226 live hits for "technological unemployment" — high-value, no API), ProQuest Historical Newspapers (or versioned TDM Studio notebooks), Gale (Times Digital Archive 1785–2019, Economist Historical Archive 1843–2020, Making of the Modern World), British Newspaper Archive, JSTOR (Constellate sunset 2025-07; use Text Analysis Support dataset requests), EconLit (abstracts only), NYT (Article Search API for the registerable metadata layer; TimesMachine manually).

Google Scholar and Google Books are **not** search databases in this protocol (irreproducible); they serve Track B discovery only.

### 1.2 Era-stratified query blocks (drafts)

Queries cross a technology-terms block with a displacement-terms block, phrased per era stratum:

| Stratum | Period | Technology terms (draft) | Displacement terms (draft) |
|---|---|---|---|
| E1 | 1800–1870 | "labour-saving machinery", "labor-saving machinery", "the machinery question", "power loom", "self-acting" | "thrown out of work", "superfluous workmen", "displace labour", "distress of the operatives", "supersede manual labour" |
| E2 | 1870–1920 | "mechanisation"/"mechanization", "the machine age", "automatic machinery" | "displacement of labour"/"labor", "machinery and unemployment", "do away with workmen" |
| E3 | 1920–1955 | "technological unemployment", "mechanization", "automation" (from ~1947), "push-button factory", "robot" (from 1921) | "men replaced by machines", "permanent unemployment", "displaced by the machine" |
| E4 | 1955–1995 | "automation", "cybernation", "computers", "robotics", "microelectronics", "word processor" | "jobs destroyed", "workless", "end of work", "silicon collar", "technological unemployment" |
| E5 | 1995–present | "computerisation", "artificial intelligence", "machine learning", "robots", "generative AI", "AI" | "jobs at risk", "job losses", "automation of jobs", "replace workers", "technological unemployment" |

Empirical anchor from the live trials: "technological unemployment" appears in the Congressional Record from **21 Feb 1928** and the Ngram series surges ~1925–1933 — the E3 stratum boundary and terms are consistent with the data.

### 1.3 Volume management (registered stratified sampling)

- Screening cap: **2,000 hits per stratum × database cell** (provisional — final value set from P1 pilot capacity measurements; decision D11).
- Cells over the cap: simple random sample within stratum × year, drawn by a seeded, scripted procedure; store `sampled`, `sampling_fraction`, `sampling_seed` in `search_log`; propagate weights into all corpus statistics.
- Cells under the cap: exhaustive screening.

### 1.4 Per-era retrieval validation

For each stratum, a fixed random sample of archive pages (Chronicling America for newspapers; HTRC volumes for books) is hand-read; the query miss rate per era is estimated and published beside the panic-wave series.

## 2. Track B — snowball & expert sources (PRISMA-S conventions)

1. **Seeds:** the pilot landmark list (`docs/research/landmark-seed-list.md`) + the institutional publisher inventory (`docs/research/institutional-publishers.md`).
2. **Citation chasing:** forward + backward, max 2 generations per seed; every hop logged with `parent_source_id`.
3. **Publisher sweeps:** for enumerable series, screen ALL editions — WEF Future of Jobs (2016, 2018, 2020, 2023, 2025), OECD Employment Outlook automation chapters, WDR 2016/2019, ILO WPs, BLS projections (which are themselves evaluable predictions), plus consultancy press-release archives (Forrester, Gartner — headline numbers free even where reports are paywalled).
4. **Discovery aids (not sources of record):** Pessimists Archive clippings (chase to primary), Pew expert canvassings (named predictions inside), Google Scholar/Books.
5. **Citation lineage:** derivative estimates (Deloitte 2014, PwC 2017, WDR 2016, ILO ASEAN 2016 all derive from Frey–Osborne 2013) recorded via `derived_from_prediction_id` — they are not independent predictions.

## 3. Screening

- S1 title/snippet → S2 full text → S3 extraction; decisions + `exclusion_reason` to `screening_log.csv`.
- 10% of S1/S2 decisions dual-screened independently by the second author; disagreement rate reported.
- Reported-speech rule and dedup rules per PLAN §4.3–4.4.

## 4. Credentials checklist (obtain before P3; all free unless noted)

congress.gov key · GovInfo key · Trove key (annual renewal) · FRASER key · Europeana key · NYT key · IPUMS key (outcome data) · BLS API key (outcome data) · UKDS account · institutional: ProQuest TDM Studio (paid), Gale Digital Scholar Lab (paid), JSTOR TAS, EBSCO/EconLit. Signup URLs in `docs/research/archives-and-apis.md`.
