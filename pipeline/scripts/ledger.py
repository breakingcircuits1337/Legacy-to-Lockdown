#!/usr/bin/env python3
"""
ledger.py — L2L Change Ledger generator.

Reads all L2L[*] git commit messages from the target repo (defined in
pipeline/l2l.config.json under "target_repo_path"), parses each commit's
phase, module, summary, and CVE list, and writes
pipeline/L2L_CHANGE_LEDGER.json.

Commit message format (enforced by core.md rules):
    L2L[PHASE]: <module> — <summary> — CVEs: <CVE-ID,CVE-ID or NONE>

Usage:
    python ledger.py
    python ledger.py --score-baseline 22 --score-final 74
    python ledger.py --target-path /absolute/path/to/repo
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT    = os.path.dirname(PIPELINE_DIR)
CONFIG_PATH  = os.path.join(PIPELINE_DIR, "l2l.config.json")
LEDGER_PATH  = os.path.join(PIPELINE_DIR, "L2L_CHANGE_LEDGER.json")

# Matches: L2L[TRANSFORM]: ProductController — migrated Log4j — CVEs: CVE-2019-17571,CVE-2022-23302
# Also matches NONE for CVEs and tolerates em-dash or plain hyphen as separator.
COMMIT_RE = re.compile(
    r"L2L\[(?P<phase>[A-Z]+)\]:\s*"
    r"(?P<module>[^—\-]+?)\s*[—\-]+\s*"
    r"(?P<summary>.+?)\s*[—\-]+\s*"
    r"CVEs?:\s*(?P<cves>.+)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        sys.exit(f"ERROR: config not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_target_path(config: dict, override: str | None) -> str:
    if override:
        path = override
    else:
        raw = config.get("target_repo_path", "")
        if not raw:
            sys.exit("ERROR: target_repo_path not set in l2l.config.json")
        path = os.path.normpath(os.path.join(REPO_ROOT, raw))
    if not os.path.isdir(path):
        sys.exit(f"ERROR: target repo not found at {path}")
    return path


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def git_log(repo_path: str) -> list[dict]:
    """
    Return all commits whose subject matches the L2L commit format.
    Each entry: {"sha": str, "subject": str}
    """
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%H\t%s", "--all"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ERROR: git log failed in {repo_path}:\n{exc.stderr}")

    commits = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        if subject.startswith("L2L["):
            commits.append({"sha": sha.strip(), "subject": subject.strip()})
    return commits


def parse_commit(commit: dict) -> dict | None:
    """Parse a single L2L commit into a structured entry. Returns None on parse failure."""
    m = COMMIT_RE.match(commit["subject"])
    if not m:
        return None

    raw_cves = m.group("cves").strip()
    if raw_cves.upper() == "NONE":
        cves = []
    else:
        cves = [c.strip() for c in re.split(r"[,\s]+", raw_cves) if c.strip()]

    return {
        "phase":           m.group("phase").strip().upper(),
        "module":          m.group("module").strip(),
        "summary":         m.group("summary").strip(),
        "cves_remediated": cves,
        "commit_sha":      commit["sha"],
    }


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------

def latest_score(label: str) -> int | None:
    """Read the most recent score file from pipeline/scores/ and return the score."""
    scores_dir = os.path.join(PIPELINE_DIR, "scores")
    if not os.path.isdir(scores_dir):
        return None
    files = sorted(
        [f for f in os.listdir(scores_dir) if f.endswith(".json")],
    )
    if not files:
        return None
    # First file = baseline, last file = final
    target = files[0] if label == "baseline" else files[-1]
    path = os.path.join(scores_dir, target)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("score")
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate L2L_CHANGE_LEDGER.json from git history."
    )
    p.add_argument(
        "--target-path",
        metavar="PATH",
        default=None,
        help="Override target_repo_path from l2l.config.json.",
    )
    p.add_argument(
        "--score-baseline",
        type=int,
        default=None,
        metavar="INT",
        help="Baseline score (overrides auto-detection from scores/).",
    )
    p.add_argument(
        "--score-final",
        type=int,
        default=None,
        metavar="INT",
        help="Final score (overrides auto-detection from scores/).",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    config = load_config()
    target_path = resolve_target_path(config, args.target_path)

    raw_commits = git_log(target_path)
    entries = []
    for commit in raw_commits:
        parsed = parse_commit(commit)
        if parsed:
            entries.append(parsed)
        else:
            print(
                f"WARN: could not parse commit {commit['sha'][:8]}: {commit['subject']}",
                file=sys.stderr,
            )

    # Deduplicate modules (keep last occurrence — most recent transform wins)
    seen_modules: set[str] = set()
    unique_modules: list[str] = []
    for e in reversed(entries):
        if e["module"] not in seen_modules:
            seen_modules.add(e["module"])
            unique_modules.append(e["module"])

    all_cves: list[str] = []
    for e in entries:
        all_cves.extend(e["cves_remediated"])
    cves_remediated_total = len(set(all_cves))

    score_baseline = args.score_baseline if args.score_baseline is not None else latest_score("baseline")
    score_final    = args.score_final    if args.score_final    is not None else latest_score("final")
    score_delta    = (score_final - score_baseline) if (score_baseline is not None and score_final is not None) else None

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    ledger = {
        "generated": now,
        "project":   config.get("project_name", "unknown"),
        "summary": {
            "modules_migrated":  len(unique_modules),
            "cves_remediated":   cves_remediated_total,
            "score_baseline":    score_baseline,
            "score_final":       score_final,
            "score_delta":       score_delta,
        },
        "entries": entries,
    }

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    print(json.dumps(ledger, indent=2))
    print(f"\nSaved → {LEDGER_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
