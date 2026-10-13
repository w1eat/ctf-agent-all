"""Audit and safely repair challenge distfiles using a platform attachment manifest.

Default is read-only. --apply backs up metadata/SQLite, quarantines misplaced
files, and copies uniquely identified content to the correct challenge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

import yaml


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest().lower()


def audit(root: Path, manifest: dict) -> tuple[list[dict], dict, dict]:
    expected = {}
    owners = defaultdict(list)
    for challenge_id, attachments in manifest.items():
        for item in attachments:
            key = (challenge_id, str(item["id"]))
            expected[key] = item
            owners[str(item["sha256"]).lower()].append(key)
    dirs = defaultdict(list)
    metadata = {}
    for directory in root.iterdir():
        path = directory / "metadata.yml"
        if directory.is_dir() and path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            dirs[str(data.get("native_id", ""))].append(directory)
            metadata[directory] = data
    rows = []
    for directory, data in metadata.items():
        for path in sorted((directory / "distfiles").glob("*")):
            if not path.is_file():
                continue
            # Ignore solver/IDA sidecars and unknown user files. Only an attachment
            # named in metadata or one whose hash is in the manifest is in scope.
            if path.suffix.lower() in {".id0", ".id1", ".id2", ".nam", ".til", ".i64", ".idb"}:
                continue
            try:
                sha = digest(path)
            except (OSError, PermissionError):
                rows.append({"path": str(path), "status": "unreadable", "owners": []})
                continue
            matches = owners.get(sha, [])
            listed = {Path(name).name for name in data.get("files", []) or []}
            listed.update(str(item.get("name")) for item in data.get("attachments", []) or [] if isinstance(item, dict))
            if not matches and path.name not in listed:
                rows.append({"path": str(path), "sha256": sha, "status": "unmanaged", "owners": []})
                continue
            valid = [(cid, aid) for cid, aid in matches if cid == str(data.get("native_id"))
                     and path.name == str(expected[cid, aid]["name"])
                     and path.stat().st_size == int(expected[cid, aid]["size"])]
            rows.append({"path": str(path), "sha256": sha, "status": "valid" if valid else "misplaced",
                         "owners": [{"challenge_id": cid, "attachment_id": aid} for cid, aid in matches]})
    return rows, metadata, {"expected": expected, "owners": owners, "dirs": dirs}


def sync_state(db: Path, metadata: dict, expected: dict) -> None:
    if not db.is_file():
        return
    with sqlite3.connect(db, timeout=10) as conn:
        conn.execute("BEGIN IMMEDIATE")
        now = time.time()
        for directory, data in metadata.items():
            cid = str(data.get("native_id"))
            valid = {}
            for (owner, aid), item in expected.items():
                if owner != cid:
                    continue
                path = directory / "distfiles" / str(item["name"])
                if path.is_file() and digest(path) == str(item["sha256"]).lower() and path.stat().st_size == int(item["size"]):
                    valid[aid] = (f"distfiles/{path.name}", str(item["sha256"]).lower(), int(item["size"]))
            # The state store may have several runs referencing the same directory.
            records = conn.execute("""SELECT a.run_id, a.native_id, a.attachment_id FROM attachments a
                                   JOIN challenges c ON c.run_id=a.run_id AND c.native_id=a.native_id
                                   WHERE a.native_id=? AND lower(c.package_dir)=lower(?)""",
                                   (cid, str(directory))).fetchall()
            for run_id, native_id, aid in records:
                if aid in valid:
                    relative, sha, size = valid[aid]
                    conn.execute("""UPDATE attachments SET state='ready', relative_path=?, sha256=?, bytes=?,
                                 reason='verified against platform manifest', updated_at=?
                                 WHERE run_id=? AND native_id=? AND attachment_id=?""",
                                 (relative, sha, size, now, run_id, native_id, aid))
                else:
                    conn.execute("""UPDATE attachments SET state='available', relative_path='', sha256='', bytes=NULL,
                                 reason='attachment missing or unverified after repair', updated_at=?
                                 WHERE run_id=? AND native_id=? AND attachment_id=?""",
                                 (now, run_id, native_id, aid))
            conn.execute("""UPDATE challenges SET state=?, reason=?, updated_at=?
                         WHERE native_id=? AND lower(replace(package_dir, '/', '\\'))=lower(?) AND state != 'solved'""",
                         (data["state"], data.get("reason", ""), now, cid, str(directory)))


def repair(root: Path, manifest: dict, db: Path, *, apply: bool = False,
           backup_root: Path | None = None) -> dict:
    rows, metadata, index = audit(root, manifest)
    expected, dirs = index["expected"], index["dirs"]
    report = {"files": rows, "actions": [], "applied": apply}
    wrong = [row for row in rows if row["status"] == "misplaced"]
    for row in wrong:
        matches = row["owners"]
        destination = None
        if len(matches) == 1 and len(dirs[matches[0]["challenge_id"]]) == 1:
            key = (matches[0]["challenge_id"], matches[0]["attachment_id"])
            candidate = dirs[key[0]][0] / "distfiles" / str(expected[key]["name"])
            if candidate.resolve() != Path(row["path"]).resolve():
                destination = candidate
        report["actions"].append({"source": row["path"], "destination": str(destination) if destination else None,
                                  "action": "quarantine-and-copy" if destination else "quarantine"})
    if not apply:
        return report
    if backup_root is None:
        backup_root = db.parent / "attachment-repair" / time.strftime("%Y%m%d-%H%M%S")
    if backup_root.exists():
        raise FileExistsError(f"Backup directory already exists: {backup_root}")
    backup_root.mkdir(parents=True)
    if db.is_file():
        with sqlite3.connect(db, timeout=10) as source, sqlite3.connect(backup_root / "challenge_state.sqlite3") as target:
            source.backup(target)
    for directory in metadata:
        saved = backup_root / "metadata" / directory.name / "metadata.yml"
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(directory / "metadata.yml", saved)
    for action in report["actions"]:
        source = Path(action["source"])
        saved = backup_root / "quarantine" / source.parent.parent.name / "distfiles" / source.name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, saved)
        dest = Path(action["destination"]) if action["destination"] else None
        if dest is not None:
            if dest.is_file() and digest(dest) != digest(saved):
                action["conflict"] = str(dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(saved, dest)
    for directory, data in metadata.items():
        cid = str(data.get("native_id"))
        attachments = [(key, item) for key, item in expected.items() if key[0] == cid]
        valid = []
        for _, item in attachments:
            path = directory / "distfiles" / str(item["name"])
            if path.is_file() and digest(path) == str(item["sha256"]).lower() and path.stat().st_size == int(item["size"]):
                valid.append(f"distfiles/{path.name}")
        data["files"] = sorted(set(valid))
        for item in data.get("attachments", []) or []:
            if not isinstance(item, dict):
                continue
            authoritative = expected.get((cid, str(item.get("id") or item.get("attachment_id") or "")))
            if authoritative:
                item["sha256"] = str(authoritative["sha256"]).lower()
                item["size"] = int(authoritative["size"])
                item["name"] = str(authoritative["name"])
        if data.get("state") != "solved":
            if len(valid) != len(attachments):
                data["state"] = "waiting_for_package"
                data["reason"] = "Attachment missing or unverified after manifest repair"
            elif data.get("environment_required") and not (data.get("connection_info") or data.get("environment")):
                data["state"] = "waiting_for_environment"
                data["reason"] = "Environment still required"
            elif attachments:
                data["state"] = "ready"
                data["reason"] = ""
        temporary = directory / "metadata.yml.repair-tmp"
        temporary.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        temporary.replace(directory / "metadata.yml")
    sync_state(db, metadata, expected)
    report["backup"] = str(backup_root)
    (backup_root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("challenges"))
    parser.add_argument("--manifest", type=Path, default=Path("all_attachments.json"))
    parser.add_argument("--db", type=Path, default=Path(".runtime/challenge_state.sqlite3"))
    parser.add_argument("--apply", action="store_true", help="Back up and apply audited changes")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"Missing challenge directory: {args.root}")
    result = repair(args.root.resolve(), json.loads(args.manifest.read_text(encoding="utf-8")),
                    args.db.resolve(), apply=args.apply)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
