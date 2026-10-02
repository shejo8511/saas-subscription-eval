"""Enforce independent line/branch thresholds from coverage.py's JSON report."""

import json
import sys
from pathlib import Path


def check(report: dict, minimum: float = 80.0) -> dict[str, float]:
    totals = report["totals"]
    result = {}
    for label, covered, total in (
        ("lines", "covered_lines", "num_statements"),
        ("branches", "covered_branches", "num_branches"),
    ):
        denominator = totals[total]
        if not denominator and label == "lines":
            raise ValueError("No application code measured")
        percent = 100.0 * totals[covered] / denominator if denominator else 100.0
        result[label] = percent
        if percent < minimum:
            raise ValueError(f"{label}: {percent:.2f}% < {minimum}%")
    return result


if __name__ == "__main__":
    try:
        print(json.dumps(check(json.loads(Path(sys.argv[1]).read_text()))))
    except (ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
