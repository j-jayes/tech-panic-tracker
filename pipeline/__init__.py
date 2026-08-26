"""Tech-Panic Tracker pipeline package.

Commands:
    python -m pipeline.validate   # schema + cross-table validation (constitution VII)
    python -m pipeline.codebook   # regenerate docs/codebook.md (constitution VI)
    python -m pipeline.summary    # record counts by table / era / tier / status
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATAPACKAGE = REPO_ROOT / "schemas" / "datapackage.json"
