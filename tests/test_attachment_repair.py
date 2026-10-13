import hashlib
import sqlite3

import yaml

from tools.repair_attachments import repair


def test_repair_quarantines_and_places_unique_hash_and_resets_state(tmp_path):
    root = tmp_path / "challenges"
    first, second = root / "first", root / "second"
    for directory, cid, name in ((first, "one", "one.bin"), (second, "two", "two.bin")):
        (directory / "distfiles").mkdir(parents=True)
        (directory / "metadata.yml").write_text(yaml.safe_dump({
            "native_id": cid, "name": directory.name, "state": "ready", "files": ["distfiles/one.bin"],
            "attachments": [{"id": cid, "name": name}],
        }), encoding="utf-8")
    (first / "distfiles" / "one.bin").write_bytes(b"wrong")
    db = tmp_path / "state.db"
    with sqlite3.connect(db) as conn:
        conn.executescript("""CREATE TABLE challenges(run_id TEXT, native_id TEXT, package_dir TEXT, state TEXT, reason TEXT, updated_at REAL);
            CREATE TABLE attachments(run_id TEXT, native_id TEXT, attachment_id TEXT, state TEXT,
            relative_path TEXT, sha256 TEXT, bytes INTEGER, reason TEXT, updated_at REAL);""")
        for cid, directory in (("one", first), ("two", second)):
            conn.execute("INSERT INTO challenges VALUES (?,?,?,?,?,?)", ("run", cid, str(directory), "ready", "", 0))
            conn.execute("INSERT INTO attachments VALUES (?,?,?,?,?,?,?,?,?)", (
                "run", cid, cid, "ready", "distfiles/one.bin", "bad", 5, "", 0))
    manifest = {
        "one": [{"id": "one", "name": "one.bin", "size": 5, "sha256": hashlib.sha256(b"right").hexdigest()}],
        "two": [{"id": "two", "name": "two.bin", "size": 5, "sha256": hashlib.sha256(b"wrong").hexdigest()}],
    }
    preview = repair(root, manifest, db)
    assert len(preview["actions"]) == 1
    assert (first / "distfiles" / "one.bin").read_bytes() == b"wrong"
    backup = tmp_path / "backup"
    result = repair(root, manifest, db, apply=True, backup_root=backup)
    assert result["backup"] == str(backup)
    assert not (first / "distfiles" / "one.bin").exists()
    assert (second / "distfiles" / "two.bin").read_bytes() == b"wrong"
    assert (backup / "quarantine" / "first" / "distfiles" / "one.bin").read_bytes() == b"wrong"
    assert (backup / "metadata" / "first" / "metadata.yml").is_file()
    assert yaml.safe_load((first / "metadata.yml").read_text())["state"] == "waiting_for_package"
    assert yaml.safe_load((second / "metadata.yml").read_text())["attachments"][0]["sha256"] == manifest["two"][0]["sha256"]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT state,relative_path,sha256 FROM attachments WHERE native_id='one'").fetchone() == (
            "available", "", "")
        assert conn.execute("SELECT state,relative_path FROM attachments WHERE native_id='two'").fetchone() == (
            "ready", "distfiles/two.bin")
    assert not repair(root, manifest, db)["actions"]


def test_unknown_sidecar_is_not_quarantined(tmp_path):
    directory = tmp_path / "challenges" / "one" / "distfiles"
    directory.mkdir(parents=True)
    (directory.parent / "metadata.yml").write_text("native_id: one\nfiles: []\n", encoding="utf-8")
    (directory / "solver.i64").write_bytes(b"user work")
    (directory / "notes.txt").write_bytes(b"user work")
    result = repair(directory.parent.parent, {}, tmp_path / "missing.db")
    assert not result["actions"]
    assert (directory / "solver.i64").exists()
