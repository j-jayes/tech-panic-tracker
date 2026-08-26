# Infrastructure

Every external service this project depends on, with the commands that created it. Nothing here should exist only as institutional memory: a collaborator with the right accounts should be able to rebuild the whole setup from this file.

Decisions behind these choices: [DR-005](decisions/DR-005-llm-infrastructure.md) (LLM provider, model pinning, secrets), [DR-001](decisions/DR-001-administrative.md) (repository, OSF, access).

---

## 1. Local development environment

```bash
uv venv --python 3.12 .venv
uv pip install -e ".[dev,llm]"

.venv/bin/python -m pipeline.validate      # schema + cross-table rules
.venv/bin/python -m pytest -q              # validation-rule tests
.venv/bin/python -m pipeline.codebook      # regenerate docs/codebook.md
.venv/bin/python -m pipeline.summary       # corpus counts
```

Rendering the pilot notebook additionally needs Quarto (≥1.8, which bundles Typst), R (≥4.3) with `ggplot2`, `dplyr`, `readr`, `scales`, `ggrepel`, `knitr`, and a Chrome or Chromium install for Mermaid diagram rendering.

```bash
quarto render analysis/pilot-draft/tech-panic-pilot.qmd
```

## 2. Secrets

| Variable | Local | CI |
|---|---|---|
| `GEMINI_API_KEY` | `.env` (git-ignored) | GitHub Actions repository secret |

`.env.example` lists every variable the project reads, without values. Copy it to `.env` and fill in. **Never** commit `.env`, paste a key into a prompt, or write one into `data/`.

## 3. Gemini API

Enabled on GCP project `jonathanjayes-com` (billing account already attached). Reproduce with:

```bash
gcloud services enable generativelanguage.googleapis.com --project jonathanjayes-com

gcloud services api-keys create \
  --display-name="tech-panic-tracker" \
  --api-target=service=generativelanguage.googleapis.com \
  --project=jonathanjayes-com

# the create call prints a key resource name; read the secret string with:
gcloud services api-keys get-key-string \
  projects/<PROJECT_NUMBER>/locations/global/keys/<KEY_UUID> \
  --format='value(keyString)'
```

Store the result:

```bash
printf 'GEMINI_API_KEY=%s\n' "$KEY" >> .env
printf '%s' "$KEY" | gh secret set GEMINI_API_KEY --repo j-jayes/tech-panic-tracker
```

Verify the key can see the models:

```bash
set -a && . ./.env && set +a
curl -s -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200" | head
```

**Model policy.** Default `gemini-3.7-flash`, temperature 0, pinned exactly — never `gemini-flash-latest` or any other floating alias. Each extraction output records the `model_version` the API served. Changing the default requires a decision record and a re-run of the frozen regression set.

**Cost.** Extraction runs are per-passage and small; the detection stage is the volume driver. Before any full-corpus run, estimate token volume from the pilot's measured per-passage cost and set a budget alert on the billing account rather than discovering the spend afterwards.

**Rotation.** `gcloud services api-keys delete <resource-name>` then repeat the create/store steps above, updating both `.env` and the GitHub secret. Rotate if a key ever reaches a log, a screenshot, or a commit.

## 4. GitHub

Repository: <https://github.com/j-jayes/tech-panic-tracker>. CI (`.github/workflows/validate.yml`) runs schema validation, the test suite, and a codebook staleness check on every push — a hand-edited `docs/codebook.md` fails the build by design, because Principle VI requires generated artefacts to be generated.

## 5. OSF — not yet created

The project is to be created under Jonathan's account (DR-001) and linked to GitHub and Zenodo. This is deferred pending a token; the steps are:

1. Create a personal access token at <https://osf.io/settings/tokens> with the `osf.full_write` scope. Store it as `OSF_TOKEN` in `.env` (and as a GitHub secret only if automation ever needs it).
2. Create the project:

   ```bash
   set -a && . ./.env && set +a
   curl -s -X POST https://api.osf.io/v2/nodes/ \
     -H "Authorization: Bearer $OSF_TOKEN" \
     -H "Content-Type: application/vnd.api+json" \
     -d '{"data":{"type":"nodes","attributes":{
           "title":"Tech-Panic Tracker",
           "category":"project",
           "description":"A systematic, preregistered, open dataset of predictions about technology replacing human labour, 1800-present, classified and evaluated.",
           "public":false}}}'
   ```

   The response carries the node id (`data.id`); record it here and in `CITATION.cff` once minted.
3. Add Ben as a contributor (`POST /v2/nodes/<id>/contributors/` with his OSF user id), link the GitHub repository as an add-on, and connect Zenodo for DOI minting on release (P7).
4. Registrations are created from this node: **Registration 1** (collection and coding protocol) after the pilot, **Registration 2** (evaluation and analysis plan) after collection is locked and before any verdict counts.

## 6. Archives and data sources — registrations still open

Free API keys still to register are listed in [`docs/research/archives-and-apis.md`](research/archives-and-apis.md) and [`outcome-data-inventory.md`](research/outcome-data-inventory.md): congress.gov, GovInfo, Trove (annual renewal), FRASER/FRED, Europeana, NYT, IPUMS, BLS v2. Each goes in `.env` under the name used by the retrieval script that needs it, and gets a line in `.env.example`.

Institutional access is open-access-first (DR-001): Tier A registered APIs and public-domain archives carry the systematic search; subscription databases are used only where the University of Oslo licenses them.
