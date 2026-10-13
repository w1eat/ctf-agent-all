"""Finalize package readiness for attachment-only challenges.

The preparation worker did not process queued packages in this run, so this
script performs the same final step prepare_challenge_package performs:
for challenges whose attachment rows are all state=ready and whose files
exist on disk under the package dir, persist state=ready.

Challenges that require a runtime environment (hasRuntime) are skipped: they
must go through start_environment/set_environment first.

Usage:
  python tools/mark_ready_from_attachments.py [--apply]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / ".runtime" / "challenge_state.sqlite3"
RECORDS = ROOT / ".runtime" / "challenge_records.json"
FINALIZABLE = {"waiting_for_decision", "waiting_for_package", "preparing", "needs_input"}


def runtime_ids() -> dict[str, bool]:
    if not RECORDS.is_file():
        return {}
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    items = records if isinstance(records, list) else records.get("items") or []
    out = {}
    for item in items:
        ident = str(item.get("id") or item.get("native_id") or "")
        if ident:
            out[ident] = bool(item.get("hasRuntime"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    runtime = runtime_ids()
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    challenges = connection.execute(
        "select name, native_id, state, package_dir, reason from challenges order by name"
    ).fetchall()

    promoted, skipped_env, skipped_missing, already = [], [], [], []
    for challenge in challenges:
        state = challenge["state"]
        if state == "ready":
            already.append(challenge["name"])
            continue
        if state not in FINALIZABLE:
            continue
        has_runtime = runtime.get(challenge["native_id"], False)
        attachments = connection.execute(
            "select * from attachments where native_id = ?", (challenge["native_id"],)
        ).fetchall()
        if has_runtime:
            skipped_env.append(challenge["name"])
            continue
        if not attachments:
            skipped_missing.append(challenge["name"] + " (no attachments)")
            continue
        package_dir = Path(challenge["package_dir"])
        verified = 0
        for attachment in attachments:
            relative = str(attachment["relative_path"] or "")
            path = (package_dir / relative) if relative else None
            if attachment["state"] == "ready" and path and path.is_file():
                verified += 1
        if verified != len(attachments):
            skipped_missing.append(
                f"{challenge['name']} ({verified}/{len(attachments)} ready)"
            )
            continue
        promoted.append(challenge["name"])
        if args.apply:
            connection.execute(
                "update challenges set state = 'ready', reason = '' where native_id = ?",
                (challenge["native_id"],),
            )
    if args.apply:
        connection.commit()

    print(f"promote-to-ready ({len(promoted)}):")
    for name in promoted:
        print("  ", name)
    print(f"skipped-needs-environment ({len(skipped_env)}):")
    for name in skipped_env:
        print("  ", name)
    print(f"skipped-not-packaged ({len(skipped_missing)}):")
    for name in skipped_missing:
        print("  ", name)
    print(f"already-ready ({len(already)}): {', '.join(already)}")
    print("APPLIED" if args.apply else "DRY RUN (pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
