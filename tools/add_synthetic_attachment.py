"""Attach a locally-generated file to an already-registered challenge package.

Used when a challenge has no downloadable attachment and no remote environment
(e.g. the payload lives in the challenge description), but the preparation
pipeline still requires a ready attachment for the package to reach READY.

Usage:
  python tools/add_synthetic_attachment.py --challenge "Base !!!!" \
      --filename description.txt --from-description
  python tools/add_synthetic_attachment.py --challenge foo \
      --filename hint.txt --content-file path/to/local/file
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / ".runtime" / "challenge_state.sqlite3"
RECORDS = ROOT / ".runtime" / "challenge_records.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def description_for(name: str) -> str:
    if not RECORDS.is_file():
        return ""
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    items = records if isinstance(records, list) else records.get("items") or []
    for item in items:
        for key in ("name", "title"):
            if str(item.get(key, "")).strip() == name.strip():
                return str(item.get("description") or item.get("desc") or "")
    for item in items:
        for key in ("name", "title"):
            if name.strip() and name.strip() in str(item.get(key, "")):
                return str(item.get("description") or item.get("desc") or "")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--content-file", default="")
    parser.add_argument("--from-description", action="store_true")
    parser.add_argument("--display-name", default="")
    parser.add_argument("--attachment-id", default="")
    args = parser.parse_args()

    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    challenge = connection.execute(
        "select * from challenges where name = ? or slug = ?",
        (args.challenge, args.challenge),
    ).fetchone()
    if challenge is None:
        print(f"challenge not found: {args.challenge}")
        return 2
    challenge_cols = challenge.keys()
    print("challenge columns:", list(challenge_cols))

    if args.content_file:
        content = Path(args.content_file).read_bytes()
    elif args.from_description:
        text = description_for(challenge["name"]) or description_for(args.challenge)
        if "description" in challenge_cols and not text:
            text = str(challenge["description"] or "")
        if not text:
            print("could not resolve description text")
            return 2
        content = text.encode("utf-8")
    else:
        print("need --content-file or --from-description")
        return 2

    package_dir = Path(challenge["package_dir"])
    distfiles = package_dir / "distfiles"
    distfiles.mkdir(parents=True, exist_ok=True)
    destination = distfiles / args.filename
    destination.write_bytes(content)
    relative = destination.relative_to(package_dir).as_posix()
    sha = sha256_bytes(content)

    attachment_cols = [r[1] for r in connection.execute("pragma table_info(attachments)")]
    now = time.time()
    attachment_id = args.attachment_id or f"synthetic-{uuid.uuid4().hex[:16]}"
    metadata = {
        "fileName": args.filename,
        "file_name": args.filename,
        "byteLength": len(content),
        "byte_length": len(content),
        "source_url": "",
        "synthetic": True,
    }
    values = {
        "run_id": challenge["run_id"] if "run_id" in challenge_cols else "",
        "native_id": challenge["native_id"] if "native_id" in challenge_cols else "",
        "challenge_slug": challenge["slug"] if "slug" in challenge_cols else "",
        "attachment_id": attachment_id,
        "name": args.display_name or args.filename,
        "target": "",
        "source_url": "",
        "state": "ready",
        "relative_path": relative,
        "sha256": sha,
        "bytes": len(content),
        "attempts": 1,
        "reason": "",
        "created_at": now,
        "updated_at": now,
        "metadata_json": json.dumps(metadata, ensure_ascii=False),
    }
    insert_cols = [c for c in values if c in attachment_cols]
    placeholders = ", ".join("?" for _ in insert_cols)
    connection.execute(
        f"insert into attachments ({', '.join(insert_cols)}) values ({placeholders})",
        [values[c] for c in insert_cols],
    )
    connection.commit()
    print(f"wrote {relative} ({len(content)} bytes) and registered attachment {attachment_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
