# Pilot corpus entry scripts

The scripts that wrote the P1 pilot rows into `data/processed/`. They are idempotent
and rerunnable from the repository root:

```bash
.venv/bin/python analysis/pilot-corpus/enter_pilot.py .        # authors, sources, predictions, junctions
.venv/bin/python analysis/pilot-corpus/enter_evaluations.py .  # evaluations, evidence, revisits (appends)
.venv/bin/python -m pipeline.validate
```

`enter_pilot.py` rewrites the tables it owns, so it is safe to run repeatedly.
`enter_evaluations.py` **appends**, so run it once against freshly written tables.

`wayback.json` caches the Wayback Machine snapshot resolved for each source URL, so
that re-running the entry script does not depend on the availability of the archive
API. Every source with a `url` must have an `archive_url` (validation rule
`url_requires_archive`); one snapshot in this file, for the Ure 1835 text, was
triggered by hand because none existed.

All rows are written with `record_status = draft` and `created_by = cc` (the AI
coder in `coders.csv`). Promoting a record past `draft` is a human action and also
writes `verification_log` rows - see the constitution, Principle I.
