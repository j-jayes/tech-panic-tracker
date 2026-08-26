# DR-001 — Administrative: authorship, repository, OSF, timeline, access

**Date:** 2026-08-26 · **Status:** accepted · **Closes:** OPEN-QUESTIONS 1, 2, 3, 4, 14

## Decision

**Authorship and affiliation.** Ben Schneider is a historian in the Department of Archaeology, Conservation and History (IAKH), University of Oslo; contact `benjamin.schneider@iakh.uio.no`. Jonathan Jayes is contactable at `jonathan.jayes@nexergroup.com` and is no longer affiliated with Lund University. `CITATION.cff` records both; ORCIDs remain to be added.

**Repository.** The canonical code repository is `https://github.com/j-jayes/tech-panic-tracker` (the `jonathan-jayes` guess in `CITATION.cff` was wrong and has been corrected).

**OSF.** The OSF project is created under Jonathan's account and linked to the GitHub repository and to Zenodo for DOI minting. Creation is *deferred* pending an OSF personal access token; the exact steps are documented in [`docs/infrastructure.md`](../infrastructure.md) so the action is reproducible rather than remembered.

**Team and timeline.** Two PIs, no research assistants. The project makes extensive, disclosed use of AI assistance for search, drafting, and LLM-assisted extraction; every record still passes 100% human verification before leaving `draft` (constitution, Principle I). Target: a **working paper draft by the end of 2026**. Quarter-level targets are recorded against P1–P7 in [`PLAN.md` §9](../PLAN.md).

**Archive access.** With no Lund affiliation, Tier B subscription sources are reachable only through Ben's University of Oslo entitlements. The default is therefore **open-access first**: Tier A registered APIs and public-domain archives carry the systematic search, and subscription databases are used only where Oslo licenses them (to be confirmed — see OPEN-QUESTIONS 22). Any stratum whose coverage depends on a subscription we do not hold is reported as a coverage limitation rather than quietly under-searched.

## Rationale

These are administrative facts, not analytical choices; they are logged because `CITATION.cff`, the preregistration, and the data package all depend on them, and because the access constraint (open-access first) has a real methodological consequence — it shapes which strata are searchable and therefore belongs in the limitations section of the paper, not just in a mailbox.

## Consequences

- `CITATION.cff` updated (repository URL, Ben's affiliation and email).
- The paper's data-availability and limitations sections must state the open-access-first constraint.
- OSF project creation is a tracked, documented task rather than an assumed one.
