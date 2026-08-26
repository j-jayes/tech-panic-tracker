# Research notes: Outcome-data inventory (long-run employment series & crosswalks)

**Status:** exploratory research, 2026-08-03. Verified with URLs. Feeds `protocol/evaluation-rubric.md` §6.1 (outcome matching) and the pilot's evidence collection.

## Headline conclusions

1. **US long-run occupation series = IPUMS OCC1950.** Decennial census microdata 1850–present harmonized to the 1950 occupation scheme (https://usa.ipums.org/usa/volii/occ_ind.shtml); OCC2010 from 1950 forward; annual extension via IPUMS CPS (OCC2010, 1962–). Known breaks to model, not ignore: 1940 (gainful-worker → labor-force concept), 1970/1980 (census occupation reclassifications).
2. **BLS OEWS is NOT a time series** — BLS explicitly warns against year-over-year comparisons (3-year pooled panels, SOC vintage breaks 1999 / 2010–12 / 2019–21, SIC→NAICS 2002, model-based estimates from May 2021: https://www.bls.gov/opub/mlr/2019/article/model-based-estimates-for-the-occupational-employment-statistics-program.htm). Use OEWS for point-in-time levels; CPS/census for trends.
3. **BLS self-evaluations are the methodological template** for our evaluation protocol — four concrete articles:
   - Veneri 1997, "Evaluating the 1995 BLS occupational employment projections", MLR Sep 1997 — direction-of-change hit rates, absolute % error, **comparison to a naive no-change benchmark** (exactly our H6 design): https://www.bls.gov/opub/mlr/1997/article/evaluating-the-1995-bls-occupational-employment-projections.htm
   - Rosenthal 1999, "The quality of BLS projections: a historical account", MLR May 1999: https://www.bls.gov/opub/mlr/1999/05/art3full.pdf
   - Alpert & Auyer 2003, "Evaluating the BLS 1988–2000 employment projections", MLR Oct 2003 — error decomposition; "reasonably accurate… conservative tilt": https://www.bls.gov/opub/mlr/2003/10/art2full.pdf
   - Byun, Henderson & Toossi 2015, MLR Nov 2015 — BLS beats naive for most variables: https://www.bls.gov/opub/mlr/2015/article/evaluation-of-bls-employment-labor-force-and-macroeconomic-projections.htm
4. **The full crosswalk chain exists in published files:** HISCO (built on ISCO-68) ↔ OCC1950 via the Mourits crosswalk (DOI 10.17026/dans-zap-qxmc, 1,675→229 categories — detail loss documented: https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/dans-zap-qxmc); ISCO-08↔SOC2010 (https://www.bls.gov/soc/isco_soc_crosswalk.xls); SOC2010↔SOC2018 (https://www.bls.gov/soc/2018/crosswalks.htm). No direct ISCO-08↔SOC2018 — chain via SOC2010 (ONS does the same).
5. **UK:** I-CeM microdata 1851–1911 (UKDS study 7481: https://datacatalogue.ukdataservice.ac.uk/studies/study/7481); Cambridge Group occupational structure c.1379–1911 (PST coding, https://www.campop.geog.cam.ac.uk/research/occupations/; interactive: https://www.economiespast.org); Vision of Britain for published census tables 1841– (https://www.visionofbritain.org.uk). Modern: ONS **discontinued LFS EMP04**; use Nomis APS (aps168, free REST API: https://www.nomisweb.co.uk/datasets/aps168); recent LFS response-collapse noise flagged by ONS.
6. **Cross-country:** ILOSTAT (ISCO, ~1990s–, free, bulk/SDMX/Rilostat, no key: https://ilostat.ilo.org/data/); Eurostat EU-LFS aggregates 1983– free API (microdata needs slow research accreditation); GGDC 10-Sector/ETD (https://www.rug.nl/ggdc/overview-databases/?lang=en); Our World in Data long-run sectoral shares with CSV/API (https://ourworldindata.org/grapher/share-employment-agriculture-industry-services).

## Famous-case series (pilot evidence)

- **Bank tellers:** OEWS 43-3071 annual (URL pattern https://www.bls.gov/oes/2019/may/oes433071.htm, swap year); pre-1988 census OCC1950. Bessen's account: https://www.imf.org/external/pubs/ft/fandd/2015/03/bessen.htm — tellers grew ~500k→~600k during peak ATM diffusion, then fell sharply after ~2010: the canonical "half-wrong, then right late" case for the timing-slack sensitivity.
- **Telephone operators:** Feigenbaum & Gross, QJE 139(3) 2024, "Answering the Call of Automation" — replication data with paper (https://academic.oup.com/qje/article-abstract/139/3/1879/7614605; NBER w28061) — also a model for occupation-level automation evaluation.
- **Hand-loom weavers:** 1841/1851 census abstracts (Vision of Britain); ~400k c.1840 per Royal Commission on Hand-Loom Weavers; Cambridge Group PST for the arc.
- **Longshoremen:** OCC1950 series 1850–1980 via IPUMS; **no distinct modern SOC code** (folded into 53-7062) — one of the documented "locus dies before horizon" cases (§6.1 note in PLAN).
- **Agriculture share:** OWID long-run (England to 1300): https://ourworldindata.org/grapher/share-of-the-labor-force-employed-in-agriculture

## Three biggest gaps (limitations section material)

1. **No annual US occupation series before the 1960s** — decennial only, with level breaks at 1940 and 1970/80; horizons landing between censuses resolve at the nearest census (the `resolution_year_used` snap rule).
2. **Occupation detail dies where famous cases need it** — crosswalk hops destroy fine detail (HISCO→OCC1950 collapses 1,675→229); many predictions will be evaluable only at a coarser occupation group than stated. Disclose per-evaluation via `series_or_table_id`.
3. **UK modern occupation data currently degraded** (EMP04 discontinued, LFS response collapse); pre-1841 is reconstruction with wide uncertainty.

## Registrations to start now

| What | Where | Speed |
|---|---|---|
| IPUMS account + API key (covers USA, CPS, International) | https://usa.ipums.org + https://account.ipums.org/api_keys | instant (International approval ~1-2 days) |
| BLS Public Data API v2 key | https://data.bls.gov/registrationEngine/ | instant, free |
| UK Data Service account (I-CeM, Cambridge Group deposits) | https://ukdataservice.ac.uk | quick (Special Licence version: weeks — start early if needed) |
| Eurostat microdata accreditation (only if EU-LFS microdata needed) | https://ec.europa.eu/eurostat/web/microdata/collections-research/european-union-labour-force-survey | 1–2 months, slowest |
| None needed | ILOSTAT, OECD Data Explorer, GGDC, OWID, Nomis, IISH Dataverse | — |

Operational note: bls.gov serves 403 to scripted fetchers — use the official API or a browser user-agent for MLR PDFs/flat files.
