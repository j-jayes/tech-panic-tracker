# Open questions — need author input

Running list of decisions I could not (or should not) make autonomously. Date opened: 2026-08-03. Last pruned: 2026-08-26. Remove items as they're decided (log material ones in `docs/decisions/`). **Item numbers are stable** — decided items are struck from the list rather than renumbered, so references in decision records keep working.

## Decided on 2026-08-26

Items 1–12, 14, 15 and 16 are closed. See:

- **[DR-001](decisions/DR-001-administrative.md)** — affiliations, repository URL, OSF ownership, timeline, archive access (closes 1, 2, 3, 4, 14)
- **[DR-002](decisions/DR-002-author-type-enums.md)** — `financial_institution`, `think_tank_private`, `think_tank_govt` added (closes 9)
- **[DR-003](decisions/DR-003-era-strata.md)** — era strata justified per boundary (closes 8 **except** the E2/E3 boundary, now item 21 below)
- **[DR-004](decisions/DR-004-protocol-confirmations.md)** — screening cap, verdict bands, cohort date, H1–H5, journal strategy (closes 5, 6, 7, 10, 11)
- **[DR-005](decisions/DR-005-llm-infrastructure.md)** — Gemini API, model pinning, secret handling (closes 12, 16)
- **[DR-006](decisions/DR-006-file-naming.md)** — file naming convention and skill

Item 15 (Playwright) is **resolved**: a Playwright MCP server is now connected, and was used during the pilot to read bot-blocked publisher pages.

## Still open

### Access & infrastructure

13. **UK Data Service account** (I-CeM, Cambridge Group deposits) — start early; the Special Licence variant takes weeks if ever needed.
17. **Chronicling America trials** returned 403 from this datacenter IP — re-run the live trial from a university or home network to confirm throughput before Reg 1 freezes it as a registered source.

### For Ben specifically

21. **E2/E3 boundary: move 1920 → 1928?** No scholarly support was found for 1920; the term's first print use (February 1928), the Hoover Committee's 1929 scare quotes, the peer-reviewed "Debate on Technological Unemployment (1928-1933)" dating, and Bix's 1929 all converge on 1928. Full evidence in [DR-003](decisions/DR-003-era-strata.md). Substantive enough that both PIs should own it; decide before Registration 1.
22. **Which archives does the University of Oslo license?** ProQuest Historical Newspapers (and TDM Studio?), Gale *Times* / *Economist* archives (and Digital Scholar Lab?), JSTOR, EconLit, British Newspaper Archive. This determines how much of Tier B is feasible and whether text-mining budgets are needed. With no Lund affiliation the default is open-access-first (DR-001), so every gap here becomes a stated coverage limitation.
23. **`source_type` has no financial-institution value.** A Goldman Sachs *Global Economics Analyst* note is currently typed `consultancy_report`, whose definition does cover financial institutions — but `author_type` now splits them (DR-002). Either accept the asymmetry or split `source_type` too, before Registration 1 freezes the vocabulary.

### Substantive research follow-ups

18. Three seed items need primary verbatim confirmation before leaving `draft`: Paul Douglas 1930 (*American Federationist*, HathiTrust), Emil Lederer (ILO 1938 translation), Nora–Minc ~30% banking figure (MIT Press 1980). **None is in the pilot corpus** — they stay out until confirmed.
19. E2 (1870–1920) is the thinnest stratum — targets listed in `docs/research/landmark-seed-list.md` (US Industrial Commission vol. 19, Powderly, Gunton/Atkinson, TUC proceedings). Note the DR-003 finding that E2 may be genuinely thin in the professional literature rather than merely under-retrieved.
20. Decide whether public-domain pilot full texts (Ricardo, Keynes 1930 UK-PD status check!, Wiener letter) may be committed to `data/raw/` as exceptions, or all kept external. (Keynes 1930: PD status differs by jurisdiction — check before committing.)
24. **Compton 1938 verbatim is unconfirmed.** The pilot record quotes the claim as relayed by *MIT Technology Review*'s 2024 retrospective; the December 1938 *Technology Review* original has not been consulted. The row carries `primary_source_status = secondary_only` and must not leave `draft` until someone reads the issue.
