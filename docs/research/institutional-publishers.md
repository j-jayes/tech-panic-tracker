# Research notes: Institutional publisher inventory

**Status:** exploratory research, 2026-08-03. Verified via web search/fetch; every claim carries its source URL. Feeds `protocol/search-protocol.md` Track B (expert-source sweeps). Two sites (weforum.org, bls.gov) return HTTP 403 to automated fetchers — index pages verified via search results; enumerate manually or via Playwright with a real browser profile.

## Key operational findings

1. **weforum.org and bls.gov block automated fetching (HTTP 403)** — plan manual browsing or Playwright with a real browser profile for those two.
2. **BLS is the only institution with a formal published self-evaluation program** of its own projections — a ready-made methodology template for our evaluation protocol (see MLR evaluation articles below).
3. **Forrester and Gartner headline numbers are recoverable from free press releases** even though the underlying reports are client-paywalled.
4. **Frey–Osborne 2013 is the upstream source** for the Deloitte 2014, PwC 2017, World Bank WDR 2016, and ILO ASEAN 2016 estimates — model this as a **citation lineage** (`derived_from_prediction_id`), not independent predictions, or the corpus double-counts one methodology five times.

## Inventory

### IGOs

**World Economic Forum** — *Future of Jobs Report*, editions 2016, 2018, 2020, 2023, 2025 (series index: https://www.weforum.org/publications/series/future-of-jobs/ — 403 to bots). Free PDFs. Flagship claims: 2016 net −5.1m jobs by 2020 (https://www.weforum.org/press/2016/01/five-million-jobs-by-2020-the-real-challenge-of-the-fourth-industrial-revolution/); 2018: 75m displaced / 133m created by 2022 (net +58m); 2020: 85m/97m by 2025; 2023: net −14m over 5 years; 2025: 92m displaced / 170m created by 2030 (net +78m) (https://www.weforum.org/press/2025/01/future-of-jobs-report-2025-78-million-new-job-opportunities-by-2030-but-urgent-upskilling-needed-to-prepare-workforces/). **Serially revised numbers → prime revisits material.** PDFs: 2018 https://www3.weforum.org/docs/WEF_Future_of_Jobs_2018.pdf, 2023 https://www3.weforum.org/docs/WEF_Future_of_Jobs_2023.pdf, 2025 https://reports.weforum.org/docs/WEF_Future_of_Jobs_Report_2025.pdf

**OECD** — *Employment Outlook* (annual since 1983; 2019 "Future of Work" edition: 14% of jobs could disappear within 15–20 years, 32% radically transformed — https://www.oecd.org/en/publications/2019/04/oecd-employment-outlook-2019_0d35ae00.html). Working papers: Arntz/Gregory/Zierahn 2016 (WP 189): only ~9% highly automatable — the task-based rebuttal to Frey–Osborne (https://www.oecd.org/en/publications/the-risk-of-automation-for-jobs-in-oecd-countries_5jlz9h56dvq7-en.html); Nedelkoska & Quintini 2018 (WP 202): 14% high risk, 32% significant change (https://www.oecd.org/en/publications/automation-skills-use-and-training_2e2f4eea-en.html). Free, enumerable.

**ILO** — numbered Working Papers. *ASEAN in Transformation* 2016 (Chang & Huynh): 56% of ASEAN-5 jobs at high risk over two decades (https://www.ilo.org/publications/asean-transformation). Gmyrek/Berg/Bescond WP 96 (2023): augmentation dominates; 24% of clerical tasks highly exposed (https://www.ilo.org/sites/default/files/wcmsp5/groups/public/@dgreports/@inst/documents/publication/wcms_890761.pdf). WP 140 (2025): refined global exposure index (https://webapps.ilo.org/static/english/intserv/working-papers/wp140/index.html).

**World Bank** — *World Development Report*: WDR 2016 "Digital Dividends": two-thirds of developing-country jobs susceptible to automation (https://documents1.worldbank.org/curated/en/961621467994698644/pdf/102724-WDR-WDR2016Overview-ENGLISH-WebResBox-394840B-OUO-9.pdf); WDR 2019 reversal: "fears that robots will take away jobs… appear to be unfounded on balance" (https://www.worldbank.org/en/publication/wdr2019). **An institution contradicting itself across 3 years → reassurance + revisit material.**

**IMF** — SDN/2024/001 (Cazzaniga et al., Jan 2024): ~40% of global employment exposed to AI, ~60% in advanced economies (https://www.imf.org/en/publications/staff-discussion-notes/issues/2024/01/14/gen-ai-artificial-intelligence-and-the-future-of-work-542379).

**European Commission / JRC** — automation & robots project outputs (https://joint-research-centre.ec.europa.eu/projects-and-activities/employment/automation-and-robots_en); *Work in the Digital Era* 2025 critically reassesses mass-unemployment narratives (https://op.europa.eu/en/publication-detail/-/publication/09d26a7f-91dd-11f0-97c8-01aa75ed71a1/language-en).

### Government

**US BLS** — Employment Projections program (10-year projections since ~1960; OOH since 1949; pre-1960 outlooks judgmental not numerical — https://www.bls.gov/opub/mlr/1999/05/art3full.pdf). **Self-evaluations**: https://www.bls.gov/emp/evaluations/methods.htm; MLR examples: 1984–95 evaluation https://www.bls.gov/opub/mlr/1997/09/art4full.pdf; 1988–2000 evaluation https://www.bls.gov/opub/mlr/2003/10/art2full.pdf. Findings: broad trends fairly accurate, conservative bias, accuracy not improving. Data downloads: https://www.bls.gov/emp/data/occupational-data.htm (site 403s to bots).

**US National Commission on Technology, Automation, and Economic Progress (1966)** — *Technology and the American Economy* + technical appendices. HathiTrust: https://catalog.hathitrust.org/Record/007424268 (appendices https://catalog.hathitrust.org/Record/007426165); ERIC ED023803: https://eric.ed.gov/?id=ED023803. Concluded tech change was NOT the major cause of unemployment — canonical government reassurance verdict on the 1960s automation scare.

**UK** — UKCES *Future of Work: Jobs and Skills in 2030* (2014, scenario-based): https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/303334/er84-the-future-of-work-evidence-report.pdf; BEIS Select Committee *Automation and the Future of Work* (2019): https://publications.parliament.uk/pa/cm201719/cmselect/cmbeis/1093/1093.pdf; Taylor Review 2017 (context, not forecasts): https://www.gov.uk/government/publications/good-work-the-taylor-review-of-modern-working-practices

### Consultancies & financial institutions

**McKinsey Global Institute** — *A Future That Works* (Jan 2017): ~50% of work activities technically automatable; half could be automated by ~2055 (±20 years — note the self-declared uncertainty band); <5% of occupations fully automatable (https://www.mckinsey.com/featured-insights/digital-disruption/harnessing-automation-for-a-future-that-works). *Jobs Lost, Jobs Gained* (Dec 2017): up to 800m displaced by 2030, up to 375m occupational switches (PDF: https://www.mckinsey.com/~/media/mckinsey/industries/public%20and%20social%20sector/our%20insights/what%20the%20future%20of%20work%20will%20mean%20for%20jobs%20skills%20and%20wages/mgi%20jobs%20lost-jobs%20gained_report_december%202017.pdf). Gen-AI report (Jun 2023): activities absorbing 60–70% of employee time automatable (https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier). No formal series index.

**Goldman Sachs** — Briggs & Kodnani, Global Economics Analyst, 26 Mar 2023: 300m FTE jobs exposed; 2/3 of US/EU jobs partially exposed; +7% global GDP (summary https://www.goldmansachs.com/insights/articles/generative-ai-could-raise-global-gdp-by-7-percent; public PDF mirror https://www.gspublishing.com/content/research/en/reports/2023/03/27/d64e052b-0f6e-45d7-967b-d7be35fabd16.pdf). Series client-only.

**PwC** — UK Economic Outlook automation section (Mar 2017): up to 30% of UK jobs at high risk by early 2030s (US 38%) (https://www.pwc.co.uk/economic-services/ukeo/pwcukeo-section-4-automation-march-2017-v2.pdf); *Will robots really steal our jobs?* (2018, 29 countries, three waves to mid-2030s) (https://www.pwc.com/hu/hu/kiadvanyok/assets/pdf/impact_of_automation_on_jobs.pdf).

**Deloitte** — *Agiletown: London Futures* (Nov 2014, with Frey & Osborne): 35% of UK jobs at high risk within 10–20 years (https://www2.deloitte.com/content/dam/Deloitte/uk/Documents/uk-futures/london-futures-agiletown.pdf).

**Forrester** — *Future of Jobs Forecast* since ~2017. 2017: 24.7m US jobs displaced / 14.9m added by 2027 (https://www.forrester.com/press-newsroom/forrester-predicts-automation-will-displace-24-7-million-jobs-and-add-14-9-million-jobs-by-2027/); 2022: 11m US jobs by 2032; Europe 12m by 2040; APAC 63m by 2040. Recent walk-back: ~6% of US jobs automated by 2030, "job apocalypse overstated" (https://investor.forrester.com/news-releases/news-release-details/forrester-ai-led-job-disruption-will-escalate-while-fears-job). Reports paywalled; press releases free.

**Gartner** — Dec 2017: by 2020 AI creates 2.3m / eliminates 1.8m jobs; net +2m by 2025 (https://www.gartner.com/en/newsroom/press-releases/2017-12-13-gartner-says-by-2020-artificial-intelligence-will-create-more-jobs-than-it-eliminates) — **an evaluable, dated, quantified reassurance prediction now past horizon**. May 2026: AI creates more jobs than it eliminates beginning 2028 (https://www.gartner.com/en/newsroom/press-releases/2026-05-13-gartner-hr-research-reveals-ai-will-create-more-jobs-than-it-eliminates-beginning-in-2028).

### Think tanks & academic centres

**Brookings** — Muro/Maxim/Whiton Jan 2019: ~25% of US employment (36m jobs) high exposure (https://www.brookings.edu/articles/automation-and-artificial-intelligence-how-machines-affect-people-and-places/).

**RAND** — irregular AI-topic reports (https://www.rand.org/topics/artificial-intelligence.html); 2025: "AI Is Making Jobs, Not Taking Them" (https://www.rand.org/pubs/commentary/2025/10/ai-is-making-jobs-not-taking-them.html).

**Pew Research** — *AI, Robotics, and the Future of Jobs* (Aug 2014): 1,896 experts, 48% predicted significant displacement by 2025 (https://www.pewresearch.org/internet/2014/08/06/future-of-jobs/) — an **aggregator of named expert predictions**, mineable as raw material.

**Oxford Martin (Frey & Osborne 2013)** — 47% of US employment at high risk of computerisation "perhaps over the next decade or two" (https://www.oxfordmartin.ox.ac.uk/downloads/academic/The_Future_of_Employment.pdf). Upstream parent of most 2014–2017 estimates.

**MIT Task Force on the Work of the Future** — final report Nov 2020 (Autor & Mindell): "a robot-driven jobs apocalypse is not on the immediate horizon" (https://workofthefuture-taskforce.mit.edu/wp-content/uploads/2021/01/2020-Final-Report4.pdf) — flagship academic reassurance.

**Stanford HAI AI Index** — annual since 2017, Economy chapter tracks *observed* AI labour-market outcomes (https://hai.stanford.edu/ai-index) — an outcome-evidence source more than a prediction source.

## Summary table

| Institution | Type | Series | Years | Access | Enumerable |
|---|---|---|---|---|---|
| WEF | igo | Future of Jobs | 2016–2025 (5 eds) | Free PDF | Yes (403 to bots) |
| OECD | igo | Employment Outlook; SEM WPs | 1983–; 2016, 2018 | Free | Yes |
| ILO | igo | Working Papers | 2016, 2023, 2025 | Free | Yes (numbered) |
| World Bank | igo | WDR | 2016, 2019 | Free | Yes |
| IMF | igo | Staff Discussion Notes | 2024 | Free | Yes |
| EC/JRC | igo | Science for Policy | 2019– | Free | Yes |
| US BLS | government_agency | Employment Projections + self-evaluations | 1949/1960– | Free (403 to bots) | Yes |
| US 1966 Commission | government_agency | one-off | 1966 | HathiTrust | Yes |
| UK Gov | government_agency | UKCES/BEIS/foresight | 2014–2019 | Free | Yes |
| McKinsey MGI | consultancy | ad hoc flagships | 2017– | Free | Partial |
| Goldman Sachs | consultancy* | Global Econ Analyst | 2023 | Mirror PDF | No |
| PwC | consultancy | UKEO + standalone | 2017–2018 | Free | Partial |
| Deloitte | consultancy | UK Futures | 2014–2015 | Free | Partial |
| Forrester | consultancy | Future of Jobs Forecast | 2017– | PRs free | PRs only |
| Gartner | consultancy | Predicts PRs | 2017– | PRs free | PRs only |
| Brookings | think_tank | Metro Program | 2019 | Free | Partial |
| RAND | think_tank | AI topic | 2017– | Free | Yes |
| Pew | think_tank | expert canvassings | 2014– | Free | Yes |
| Oxford Martin | academic | working paper | 2013 | Free | Yes |
| MIT WotF | academic | task force | 2019–2020 | Free | Yes |
| Stanford HAI | academic | AI Index | 2017– | Free | Yes |

*Goldman Sachs is a financial institution; treat under consultancy or add enum value — see OPEN-QUESTIONS.
