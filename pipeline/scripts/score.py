#!/usr/bin/env python3
"""
score.py — L2L Migration Score calculator.

Usage:
    python score.py \
        --cve-count 4 \
        --test-coverage 0.72 \
        --api-coverage 0.5 \
        --complexity-violations 3 \
        --framework-current false

Reads weights from pipeline/l2l.config.json (relative to this script's
grandparent directory, i.e. the L2L repo root).

Saves the result to pipeline/scores/score_<timestamp>.json and
prints the JSON to stdout.
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(SCRIPT_DIR)          # pipeline/
REPO_ROOT = os.path.dirname(PIPELINE_DIR)           # L2L repo root
CONFIG_PATH = os.path.join(PIPELINE_DIR, "l2l.config.json")
SCORES_DIR = os.path.join(PIPELINE_DIR, "scores")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_weights() -> dict:
    """Load scoring weights from l2l.config.json."""
    if not os.path.exists(CONFIG_PATH):
        sys.exit(f"ERROR: config not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    weights = config.get("scoring", {})
    required = [
        "cve_weight",
        "test_coverage_weight",
        "api_enablement_weight",
        "complexity_weight",
        "framework_currency_weight",
    ]
    for key in required:
        if key not in weights:
            sys.exit(f"ERROR: missing scoring.{key} in l2l.config.json")
    total = sum(weights[k] for k in required)
    if total != 100:
        sys.exit(f"ERROR: scoring weights sum to {total}, must sum to 100")
    return weights


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_cve(cve_count: int, weight: int) -> int:
    """
    Full points for 0 CVEs. Each CVE deducts weight/10 points,
    floored at 0.
    """
    if cve_count <= 0:
        return weight
    deduction = min(cve_count * math.ceil(weight / 10), weight)
    return max(0, weight - deduction)


def score_coverage(coverage: float, weight: int) -> int:
    """Linear: coverage fraction × weight, rounded to nearest int."""
    coverage = max(0.0, min(1.0, coverage))
    return round(coverage * weight)


def score_api(api_coverage: float, weight: int) -> int:
    """Linear: api_coverage fraction × weight."""
    api_coverage = max(0.0, min(1.0, api_coverage))
    return round(api_coverage * weight)


def score_complexity(violations: int, weight: int) -> int:
    """Full points for 0 violations. Each violation costs weight/10."""
    if violations <= 0:
        return weight
    deduction = min(violations * math.ceil(weight / 10), weight)
    return max(0, weight - deduction)


def score_framework(current: bool, weight: int) -> int:
    """Binary: full points if framework migration complete, else 0."""
    return weight if current else 0


def label(score: int) -> str:
    if score <= 25:
        return "Critical"
    if score <= 50:
        return "At Risk"
    if score <= 75:
        return "Modernizing"
    return "Modern"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Calculate L2L Migration Score from audit metrics."
    )
    p.add_argument(
        "--cve-count",
        type=int,
        required=True,
        metavar="INT",
        help="Number of open CVEs found during audit.",
    )
    p.add_argument(
        "--test-coverage",
        type=float,
        required=True,
        metavar="FLOAT",
        help="Contract test coverage as a fraction 0.0–1.0.",
    )
    p.add_argument(
        "--api-coverage",
        type=float,
        required=True,
        metavar="FLOAT",
        help="REST API surface coverage as a fraction 0.0–1.0.",
    )
    p.add_argument(
        "--complexity-violations",
        type=int,
        required=True,
        metavar="INT",
        help="Number of methods with cyclomatic complexity > 5.",
    )
    p.add_argument(
        "--framework-current",
        type=parse_bool,
        required=True,
        metavar="BOOL",
        help="true if framework migration to target_stack is complete.",
    )
    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = build_parser().parse_args()
    weights = load_weights()

    cve_score         = score_cve(args.cve_count, weights["cve_weight"])
    test_score        = score_coverage(args.test_coverage, weights["test_coverage_weight"])
    api_score         = score_api(args.api_coverage, weights["api_enablement_weight"])
    complexity_score  = score_complexity(args.complexity_violations, weights["complexity_weight"])
    framework_score   = score_framework(args.framework_current, weights["framework_currency_weight"])

    total = cve_score + test_score + api_score + complexity_score + framework_score
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    result = {
        "score": total,
        "breakdown": {
            "cve_score":        cve_score,
            "test_score":       test_score,
            "api_score":        api_score,
            "complexity_score": complexity_score,
            "framework_score":  framework_score,
        },
        "label":     label(total),
        "timestamp": now,
        "inputs": {
            "cve_count":             args.cve_count,
            "test_coverage":         args.test_coverage,
            "api_coverage":          args.api_coverage,
            "complexity_violations": args.complexity_violations,
            "framework_current":     args.framework_current,
        },
    }

    # Save to pipeline/scores/
    os.makedirs(SCORES_DIR, exist_ok=True)
    safe_ts = now.replace(":", "-").replace("+", "Z")
    out_path = os.path.join(SCORES_DIR, f"score_{safe_ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Print to stdout
    print(json.dumps(result, indent=2))
    print(f"\nSaved → {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
