"""Mask platform-verified solved challenges so the spawner stops re-queuing them.

Reads solve_status_scan.json (produced via the platform API scan) and sets
state='needs_input' with an explicit reason for every solved challenge.  The
framework never auto-spawns needs_input rows, so this stops wasteful respawns
of already-solved challenges (e.g. after a swarm is cancelled).

Usage:
  python tools/mask_solved_challenges.py [--apply]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / ".runtime" / "challenge_state.sqlite3"
SCAN = ROOT / "solve_status_scan.json"
REASON = "coordinator: platform-accepted solve; do not respawn"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not SCAN.is_file():
        print(f"missing scan file: {SCAN}")
        return 2
    scan = json.loads(SCAN.read_text(encoding="utf-8"))
    solved = [item for item in scan if item.get("solved")]
    print(f"solved according to platform: {len(solved)}")

    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    masked, already, missing = [], [], []
    for item in solved:
        native_id = item["id"]
        row = connection.execute(
            "select name, state from challenges where native_id = ?", (native_id,)
        ).fetchone()
        if row is None:
            missing.append(item["t"])
            continue
        if row["state"] == "needs_input":
            already.append(row["name"])
            continue
        masked.append(f"{row['name']} ({row['state']} -> needs_input)")
        if args.apply:
            connection.execute(
                "update challenges set state = 'needs_input', reason = ?, updated_at = strftime('%s','now') "
                "where native_id = ?",
                (REASON, native_id),
            )
    if args.apply:
        connection.commit()

    print("masked:" if args.apply else "would mask:")
    for line in masked:
        print("  ", line)
    print(f"already masked: {', '.join(already) if already else '-'}")
    if missing:
        print(f"not in db: {missing}")
    print("APPLIED" if args.apply else "DRY RUN (pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
