# Open questions — need author input

Running list of decisions I could not (or should not) make autonomously. Date opened: 2026-08-03. Remove items as they're decided (log material ones in `docs/decisions/`).

## Administrative

1. **Ben Schneider's affiliation + email + ORCID** for `CITATION.cff` (currently name-only), and Jonathan's ORCID/affiliation line. Also: which institutional affiliation goes on the paper (matters for archive access, #7).
2. **GitHub repo URL**: `CITATION.cff` guesses `github.com/jonathan-jayes/tech-panic-tracker` — correct or fix. Is the repo public yet / when should it be?
3. **OSF project**: who creates it, under which account(s); link Zenodo + GitHub when created.
4. **Timeline/budget**: PLAN has no dates against P1–P7 and no LLM API budget. Rough quarter-level targets would discipline scoping. Any RA support, or strictly two-PI?

## Protocol decisions (provisional values in place — confirm or change)

5. **Screening cap = 2,000 hits per stratum × database** (decision D11, `protocol/search-protocol.md` §1.3) — provisional per your instruction; revisit after P1 yield measurements.
6. **Verdict band edges** (2/3–3/2 clearly correct; 0.4–2.5 mostly; 0.1–10 mixed) and horizon defaults ("soon"=10y, "generation"=30y, "lifetime"=40y) are my proposals — pilot stress-tests them (T018–T021), but sanity-check as economists before Reg 2.
7. **Evaluation cohort date**: `evaluated_as_of = 2026-12-31` assumed. Confirm.
8. **Era strata boundaries** (1800–1870–1920–1955–1995–) — confirm before Reg 1.
9. **`author_type` for financial institutions** (Goldman Sachs, IMF-as-forecaster): currently folded into `consultancy`/`igo`. Add a `financial_institution` enum value, or keep? (Vocabulary is append-only after Reg 1 — decide before.)
10. **H1–H5 directional forms** are placeholders written by me (PLAN §8.2) — you two must own them before Registration 2.
11. **Journal strategy sign-off**: Scientific Data companion + AER: Insights flagship + EEH backup (PLAN §1.7, research doc) — agree/adjust before writing begins.

## Access & infrastructure (action items, mostly registrations)

12. **Free API keys to register** (any account works; store in `.env`, never commit): congress.gov, GovInfo, Trove (annual renewal!), FRASER/FRED, Europeana, NYT, IPUMS (+ API key), BLS v2. Signup URLs in `docs/research/archives-and-apis.md` and `outcome-data-inventory.md`.
13. **UK Data Service account** (I-CeM, Cambridge Group deposits) — start early; the Special Licence variant takes weeks if ever needed.
14. **Institutional subscriptions**: which does your institution license — ProQuest Historical Newspapers (+ TDM Studio?), Gale Times/Economist archives (+ Digital Scholar Lab?), JSTOR, EconLit, British Newspaper Archive? This determines how much of Tier B is feasible and whether TDM budgets are needed.
15. **Playwright**: no Playwright MCP server is connected to this Claude Code environment (checked). To let me drive bot-blocked sites (weforum.org, bls.gov, loc.gov-from-datacenter) and logged-in archive UIs, add it: `claude mcp add playwright -- npx @playwright/mcp@latest` (browsers install on first run). Until then those sites are manual.
16. **Anthropic API key + model choice** for the P1 LLM dry run (T023–T026); agree a spend cap.
17. **Chronicling America trials** returned 403 from this datacenter IP — re-run the live trial from a university/home network to confirm throughput before Reg 1 freezes it as a registered source.

## Substantive research follow-ups (flagged in research docs)

18. Three seed items need primary verbatim confirmation before leaving `draft`: Paul Douglas 1930 (*American Federationist*, HathiTrust), Emil Lederer (ILO 1938 translation), Nora–Minc ~30% banking figure (MIT Press 1980).
19. E2 (1870–1920) is the thinnest stratum — targets listed in `docs/research/landmark-seed-list.md` (US Industrial Commission vol. 19, Powderly, Gunton/Atkinson, TUC proceedings).
20. Decide whether public-domain pilot full texts (Ricardo, Keynes 1930 UK-PD status check!, Wiener letter) may be committed to `data/raw/` as exceptions, or all kept external. (Keynes 1930: PD status differs by jurisdiction — check before committing.)
