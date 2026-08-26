"""Dataset summary: record counts by table, era stratum, tier, claim type, status.

Run: python -m pipeline.summary
"""

from __future__ import annotations

import sys

import pandas as pd

from pipeline.validate.cross_table import load_tables

ERA_BINS = [(1800, 1869, "E1 1800-1870"), (1870, 1919, "E2 1870-1920"), (1920, 1954, "E3 1920-1955"), (1955, 1994, "E4 1955-1995"), (1995, 2100, "E5 1995-")]


def era_of(partial_date: str) -> str:
    try:
        year = int(str(partial_date)[:4])
    except ValueError:
        return "unknown"
    for lo, hi, label in ERA_BINS:
        if lo <= year <= hi:
            return label
    return "pre-1800"


def main() -> int:
    tables = load_tables()
    print("Record counts:")
    for name, df in sorted(tables.items()):
        print(f"  {name}: {len(df)}")
    preds = tables["predictions"]
    if not preds.empty:
        for col, label in [("specificity_tier", "tier"), ("claim_type", "claim type"), ("record_status", "status"), ("panic_valence", "valence")]:
            print(f"\nPredictions by {label}:")
            print(preds[col].value_counts().to_string())
        print("\nPredictions by era stratum:")
        print(preds["prediction_date"].map(era_of).value_counts().to_string())
    else:
        print("\npredictions.csv is empty (header only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
