"""Entry point: python -m pipeline.validate

Exit 0 when every CSV conforms to schemas/datapackage.json and all
cross-table rules pass; exit 1 otherwise, printing one line per violation.
"""

import sys

from pipeline.validate import validate_cross_table, validate_resources


def main() -> int:
    errors = validate_resources() + validate_cross_table()
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("Validation passed: all resources conform to schema and cross-table rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
