# Research notes: Prior art & journal positioning

**Status:** exploratory research, 2026-08-03; all citations verified with URLs. Feeds PLAN §1.6 (related work) and the new §1.7 (positioning). Authors are economic historians; target is an economics journal; the persuasion goal is showing economists that systematic collection + prediction evaluation works outside applied micro.

## Prior-art inventory

### Closest methodological neighbour: Armstrong & Sotala / MIRI dataset
- Armstrong & Sotala (2012/2015), "How We're Predicting AI — or Failing To" (https://intelligence.org/files/PredictingAI.pdf); Armstrong, Sotala & Ó hÉigeartaigh (2014), JETAI 26(3) (https://www.tandfonline.com/doi/abs/10.1080/0952813X.2014.895105).
- ~257 AI predictions (95 timelines) from the 1950s on; found expert ≈ non-expert, 15–25-year clustering ("Maes–Garreau"). Dataset still downloadable at AI Impacts (https://aiimpacts.org/miri-ai-predictions-dataset/).
- **Cautionary tale:** AI Impacts documented a data error in the 2012 paper — the expert/non-expert similarity claim didn't survive re-analysis (https://aiimpacts.org/error-in-armstrong-and-sotala-2012/). Coding quality and audit trails are exactly what our verification-log design defends against; cite this.
- Differences: AI-timelines only; no outcome evaluation; no preregistration; no DOI archiving; never in an economics venue.

### The narrative we systematize: Mokyr, Vickers & Ziebarth (2015)
JEP 29(3): 31–50 (https://www.aeaweb.org/articles?id=10.1257%2Fjep.29.3.31). Illustrative quotation, no dataset. **Rhetorical anchor: "Mokyr, Vickers and Ziebarth told the story; we build the sampling frame and keep score."**

### Frey–Osborne and its published retrospective evaluations (validation targets for our F–O row)
- Georgieff & Milanez (2021), OECD WP 255, "What happened to jobs at high risk of automation?" — 21 countries, no net destruction; high-risk occupations grew 6% vs 18% low-risk (https://www.oecd.org/en/publications/what-happened-to-jobs-at-high-risk-of-automation_10bc97f4-en.html).
- Coelli & Borland (2019), Melbourne Institute WP 10/19 — F-O risk explains little of 2013–2018 US occupation change (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3472764).
- ITIF/Atkinson (2022) — risk-vs-outcome correlation ~0.26; insurance underwriters (highest risk) grew 16.4% (https://itif.org/publications/2022/09/30/oops-the-predicted-47-percent-of-job-loss-from-ai-didnt-happen/).
- Frey & Osborne's own reappraisal, Brown J. World Affairs 30(1) 2023/24 (https://bjwa.brown.edu/30-1/generative-ai-and-the-future-of-work-a-reappraisal/) — a first-class **revisit** row.

### Methodological standards & precedents
- Tetlock (2005) *Expert Political Judgment* + Good Judgment Project — canonical forecast-scoring machinery; we adapt it to *retrospectively found archival* predictions (needs the survivorship/inclusion apparatus Tetlock never did).
- Woirol (1996), *The Technological Unemployment and Structural Unemployment Debates* (Greenwood) — standard history of the 1930s and 1960s debates; a source-finding aid for strata E3–E4 (https://books.google.com/books/about/The_Technological_Unemployment_and_Struc.html?id=z6nA4t-NV58C).
- One-off forecast evaluations that our project generalizes: Turner (2008) & Herrington (2021) on Limits to Growth; Keilman (2001) on UN population projections (Population Studies 55(2)); Sabin (2013) *The Bet* on Simon–Ehrlich — plus the resolution-sensitivity finding that **Ehrlich would have won ~61% of rolling ten-year windows 1910–2007** (https://humanprogress.org/luck-or-insight-the-simon-ehrlich-bet-re-examined/) — the perfect motivating example for explicit resolution windows and the timing-slack sensitivity.
- Farmer & Lafond (2016), Research Policy 45(3) — hindcasting 53 technology cost curves; complementary (trend vs verbal predictions).
- Forecast-evaluation infrastructure that already exists in economics — but only short-horizon quantitative macro: Timmermann (2007) IMF Staff Papers (WEO evaluation); Loungani (2001) IJF ("record of failure is virtually unblemished" on recessions); Philadelphia Fed SPF real-time evaluation programme. **Gap sentence: nobody maintains a database of long-horizon structural predictions.**

### Pessimists Archive (2026 status)
Site resolves (https://pessimistsarchive.org/), active mainly via Substack (https://newsletter.pessimistsarchive.org/, e.g. "Robots Have Been About to Take All the Jobs for 100 Years"). Curated advocacy collection: no fixed corpus, criteria, schema, versioning, or DOI, and an editorial thesis (panics were silly). **Use as motivation + source leads (clippings → primary sources), never as data.** Differentiation gift: we also count the predictions that came true.

### Modern exposure indices (the contemporary `exposure_risk` stratum)
Felten/Raj/Seamans AIOE (SMJ 2021; data https://github.com/AIOE-Data/AIOE); Webb (2020) patent-overlap measure; Eloundou et al. "GPTs are GPTs" (Science 384, 2024); Anthropic Economic Index (ongoing usage — not just exposure — data; https://www.anthropic.com/economic-index). These are conditional capability claims; F-O 2013 shows exposure claims eventually become gradeable.

## Journal positioning (recommended strategy)

**Two-paper structure, three tiers:**

1. **Companion data descriptor → *Scientific Data*** (Nature Portfolio). Publishes economic-history data descriptors (e.g. Austrian Silesia 1837–1910 dataset, Sci Data 7, 2020: https://www.nature.com/articles/s41597-020-0546-z). Standardized format (Background/Methods/Data Records/Technical Validation/Usage Notes), DOI deposit required, no analytical claims — locks in the open-science identity without burning the result.
2. **Flagship → *AER: Insights*** (primary target). Model: Kelly, Papanikolaou, Seru & Taddy (2021), "Measuring Technological Innovation over the Long Run" (https://www.aeaweb.org/articles?id=10.1257%2Faeri.20190499) — proof the AER family accepts novel long-run text-based measurement + descriptive findings in ~6,000 words with data on GitHub. Lead with ONE sharp finding (e.g. directional accuracy common, magnitude/timing accuracy rare). Bar-setter for "measurement + result at the very top": Autor, Chin, Salomons & Seegmiller, QJE 2024, "New Frontiers: The Origins and Content of New Work, 1940–2018" (https://academic.oup.com/qje/article-abstract/139/3/1399/7630187). Fallback at tier 1.5: **Economic Journal** standard article (the old "Features" section no longer exists as a submission type).
3. **Backups:** *Explorations in Economic History* (explicit data/methods track — 2023 special issue "Methodological Advances in the Extraction and Analysis of Historical Data"; near-certain fit, guaranteed floor); *Journal of Economic History* (if the AI-era argument is foregrounded); *International Journal of Forecasting* for a **separate** rubric-methods paper (splits, not downgrades).
4. **Amplification (not submission):** later solicited JEP piece in the Mokyr et al. 2015 / Autor 2015 lineage; AEA P&P short if invited.

**Not recommended as primary:** JEP/JEL (no original-research datasets / surveys only), AEJ:Applied/Macro & JEEA (identification/structural formats), JEBO (off-theme), *Futures* (the ghetto the project wants to escape).

**Cover-letter positioning line:** economics already institutionalizes forecast evaluation (WEO, SPF, Loungani) — but only for short-horizon macro numbers; the predictions that shape technology policy are long-horizon structural claims, so far evaluated only one at a time (Georgieff & Milanez on Frey–Osborne; Turner/Herrington on Limits to Growth; Keilman on the UN). Tech-panic-tracker generalizes that one-off genre into a database, the way Tetlock generalized pundit-checking into a science.
