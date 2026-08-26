# Research notes: Historical archives & API access (with live trial queries)

**Status:** exploratory research, 2026-08-03. All trial queries were actually executed on that date; hit counts are real. Feeds `protocol/search-protocol.md` Track A database selection. Environment caveat: loc.gov Cloudflare-challenges requests from datacenter IPs — re-run those trials from a university/residential network.

## Substantive findings from the live trials

- **"Technological unemployment" appears in the US Congressional Record on 21 Feb 1928** (Bound CR vol. 69 pt. 3, granule GPO-CRECB-1928-pt3-v69-16-1) — *pre-dating Keynes's famous 1930 coinage*. 604 total hits in CREC/CRECB.
- **Google Ngram shows the phrase surging ~1925–1933** (live JSON series, en-2019 corpus) — consistent with an E3 panic wave beginning before Keynes.
- **UK Hansard: 79 contributions** mention the phrase, 1803–present (e.g. 13 Nov 1967 written answer on computerization; 8 Sep 2016 Fourth Industrial Revolution debate).
- **HathiTrust full-text: 8,226 full-view results** for the phrase (UI scrape; no API contract).
- **Internet Archive advancedsearch matched only 98** — because it searches **metadata only, not OCR text**: a critical protocol caveat.

## Archive-by-archive assessment

| Archive | Years | API | Auth | Reproducible? | Live trial |
|---|---|---|---|---|---|
| Chronicling America (loc.gov) | 1756–1963 | loc.gov JSON API — **legacy chroniclingamerica.loc.gov API is dead** (retired 2025; https://www.loc.gov/item/prn-25-045, migration: https://loc.gov/ndnp/migration) | None (rate ~20 req/min, 1-hr block; https://www.loc.gov/apis/json-and-yaml/working-within-limits/) | Yes | 403/Cloudflare from datacenter IP — re-run on campus |
| HathiTrust FTS | ~1500– | **None** (UI only) | n/a | UI counts citable, not API-stable | **8,226** full-view hits |
| **HTRC Extracted Features v2.0** | –2020 snapshot | rsync dataset, 17.1M volumes, 4TB (https://analytics.hathitrust.org/deriveddatasets) | None | **Yes — fixed dataset, gold standard**; caveat: per-page token lists, multi-word phrases only as co-occurrence proxies | n/a |
| Internet Archive | all | advancedsearch.php — **metadata only** | None | Yes (metadata-level only) | **98** |
| Google Books API | ~1500– | volumes API | Free Google Cloud key (1,000 req/day) | No (index churn) — discovery only | 429 on shared quota |
| **Google Ngram** | 1500–2019/22 | JSON endpoint (no key) + **bulk v3 exports** (https://storage.googleapis.com/books/ngrams/books/datasetsv3.html, CC BY 3.0) | None | **Yes via downloaded dataset** — our normalizing denominator | live series returned |
| ProQuest Hist. Newspapers (NYT 1851–, WSJ 1889–, Guardian 1791–…) | 1791– | TDM Studio only (paid add-on; text stays in platform) | Institutional | Within-platform | not possible |
| Gale (Times 1785–2019, Economist 1843–2020, Making of the Modern World 1450–1914) | see left | Digital Scholar Lab only | Institutional | Within-platform | not possible |
| British Newspaper Archive (~90M pages) | 1700s–2000s | **None** (long-declined feature request) | Personal sub | No — manual track; BL Labs dataset requests possible (https://blogs.bl.uk/thenewsroom/text-mining/) | not possible |
| JSTOR | 1600s– | **Constellate SUNSET 2025-07-01** (https://labs.jstor.org/blog/constellate-an-experiment-and-retrospective/); replacement = Text Analysis Support dataset requests (https://about.jstor.org/whats-in-jstor/text-mining-support) | Institutional | As dated dataset snapshot | not possible |
| EconLit (EBSCO/Ovid) | 1886– | Vendor API; **abstracts/metadata only** | Institutional | Platform-dependent | not possible |
| FRASER (St. Louis Fed) | 1790s– | fraser.stlouisfed.org/api (OAI-PMH too) | **Free key** (https://research.stlouisfed.org/docs/api/fraser/) | Yes; mostly PD gov docs | endpoint live, key missing |
| UK Hansard | 1803– | hansard-api.parliament.uk | **None** | **Yes**; Open Parliament Licence; bulk XML 1803–2005 (https://www.hansard-archive.parliament.uk/; rsync mirror data.theyworkforyou.com::parldata) | **79** |
| Congressional Record (GovInfo + congress.gov) | 1873– | **api.govinfo.gov/search** (POST, cursor-paginated) + api.congress.gov/v3 | Free key (DEMO_KEY worked live) | **Yes — best-in-class**; PD; bulk ZIPs | **604**, earliest 1928 |
| Trove (Australia) | 1803–1950s | api.trove.nla.gov.au/v3 | Free key, **expires after 12 months** (note in reproducibility plan) | Yes; GLAM Workbench tooling | 401 without key |
| Europeana (incl. Europeana Newspapers) | varies | api.europeana.eu (`qf=TEXT_FULLTEXT:`) | Free key | Yes | 401 without key |
| NYT Article Search / Archive API | 1851– | metadata/snippets only; TimesMachine has no API | Free key (~500 req/day) | Yes (metadata layer) | not run |

## Implication for the registered search protocol (Track A)

**Registered reproducible anchors:** GovInfo/Congressional Record, UK Hansard, Chronicling America (loc.gov JSON, from institutional IP), Trove, FRASER, Europeana, plus the two **fixed datasets** — HTRC Extracted Features and Google Ngram v3 exports (strongest reproducibility; use for normalized panic-wave series). Internet Archive registerable but declared metadata-level only.

**Manual-documented-search track** (query string + date + screenshot + result-count logging): HathiTrust FTS UI, ProQuest (or versioned TDM Studio notebooks), Gale Digital Scholar Lab, British Newspaper Archive, JSTOR dataset requests, EconLit, NYT TimesMachine.

Note this **changes the PLAN §4.1 database split**: HathiTrust moves from "registered API search" to "manual-documented + HTRC-dataset computation"; Congressional Record/Hansard/FRASER (not in the original draft list) become first-class registered sources — they are also exactly where *government and parliamentary* predictions live.

## Credentials to obtain (all free unless noted)

| Credential | Signup |
|---|---|
| Congress.gov API key | https://api.congress.gov/sign-up/ |
| GovInfo API key (api.data.gov family) | https://api.govinfo.gov/docs/ |
| Trove API key (renew annually) | https://trove.nla.gov.au/about/create-something/using-api |
| FRASER/FRED API key | https://fredaccount.stlouisfed.org/apikeys |
| Europeana API key | https://pro.europeana.eu/page/get-api |
| NYT Developer key | https://developer.nytimes.com |
| Google Cloud key (Books API; discovery only) | https://console.cloud.google.com |
| HathiTrust/HTRC account (EF rsync itself is open) | https://analytics.hathitrust.org |
| ProQuest TDM Studio (institutional, paid) | via library: https://about.proquest.com/en/products-services/TDM-Studio/ |
| Gale Digital Scholar Lab (institutional, paid) | via library / Gale rep |
| British Newspaper Archive (personal sub) + BL Labs request | https://www.britishnewspaperarchive.co.uk |
| JSTOR Text Analysis Support | via institutional JSTOR access |
| EBSCO API profile for EconLit | via EBSCO rep |

## Playwright note

No Playwright MCP server is connected to the current Claude Code session (checked 2026-08-03); Node `npx playwright` v1.62.1 is installed but without browsers. For the archives that block bots (weforum.org, bls.gov, loc.gov-from-datacenter) and the subscription UIs (HathiTrust FTS, ProQuest, Gale, BNA), add the Playwright MCP server (`claude mcp add playwright -- npx @playwright/mcp@latest`) or run `npx playwright install chromium` and drive it from scripts — logged-in institutional sessions will be needed for the subscription platforms.
