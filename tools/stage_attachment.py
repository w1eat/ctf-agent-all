"""Stage a browser-downloaded attachment into a challenge package.

Usage:
  python tools/stage_attachment.py --challenge <name-or-slug> --attachment-id <id> --staged <path-to-staged-file>

The script:
  1. resolves the challenge package dir + expected metadata from the coordinator state DB
  2. copies the staged file to <package>/distfiles/<original filename>
  3. verifies size/sha256 against registered metadata
  4. marks the attachment row ready with relative_path/sha256/bytes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / ".runtime" / "challenge_state.sqlite3"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--attachment-id", required=True)
    parser.add_argument("--staged", required=True)
    parser.add_argument("--name", default="")
    args = parser.parse_args()

    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    row = connection.execute(
        "select package_dir, name from challenges where name = ? or slug = ?",
        (args.challenge, args.challenge),
    ).fetchone()
    if row is None:
        print(f"challenge not found: {args.challenge}")
        return 2
    package_dir = Path(row["package_dir"])
    attachment = connection.execute(
        "select * from attachments where attachment_id = ?",
        (args.attachment_id,),
    ).fetchone()
    if attachment is None:
        print(f"attachment not registered: {args.attachment_id}")
        return 2
    metadata = json.loads(attachment["metadata_json"] or "{}")
    original = args.name or attachment["name"] or metadata.get("fileName") or attachment["attachment_id"]
    original = Path(str(original)).name
    expected_size = metadata.get("byte_length") or metadata.get("byteLength") or metadata.get("size")
    expected_sha = str(metadata.get("sha256") or "").strip().casefold()

    staged = Path(args.staged)
    if not staged.is_absolute():
        staged = ROOT / staged
    if not staged.is_file():
        print(f"staged file missing: {staged}")
        return 2

    actual_size = staged.stat().st_size
    actual_sha = sha256_file(staged)
    if expected_size is not None and int(expected_size) != actual_size:
        print(f"size mismatch: expected {expected_size} got {actual_size}")
        return 3
    if expected_sha and expected_sha != actual_sha:
        print(f"sha256 mismatch: expected {expected_sha} got {actual_sha}")
        return 3

    distfiles = package_dir / "distfiles"
    distfiles.mkdir(parents=True, exist_ok=True)
    destination = distfiles / original
    shutil.copy2(staged, destination)
    relative = destination.relative_to(package_dir).as_posix()

    connection.execute(
        """
        update attachments
           set state = 'ready', relative_path = ?, sha256 = ?, bytes = ?, reason = ''
         where attachment_id = ?
        """,
        (relative, actual_sha, actual_size, args.attachment_id),
    )
    connection.commit()
    print(f"staged {relative} ({actual_size} bytes) for {row['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
