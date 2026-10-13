from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sandbox" / "tool-manifest.json"
CHECKER = ROOT / "sandbox" / "ctf-tools-check.py"


def _checker():
    spec = importlib.util.spec_from_file_location("ctf_tools_check", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_has_all_supported_categories_and_exact_targets():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["target_architecture"] == "x86_64"
    assert set(manifest["categories"]) == {
        "web", "pwn", "reverse", "crypto", "forensics", "stego",
        "misc", "mobile", "osint", "blockchain",
    }
    for category, tools in manifest["categories"].items():
        assert tools, category
        for tool in tools:
            assert tool["name"] and tool["use"]
            assert bool(tool.get("command")) != bool(tool.get("module"))
    assert "podman" not in MANIFEST.read_text(encoding="utf-8").lower()


def test_missing_tool_fails_json_check_and_cannot_write_reference(tmp_path, monkeypatch, capsys):
    checker = _checker()
    manifest_path = tmp_path / "tools.json"
    manifest_path.write_text(json.dumps({
        "target_architecture": "x86_64",
        "categories": {"web": [{"name": "absent", "command": "ctf-never-installed", "use": "test"}]},
    }), encoding="utf-8")
    monkeypatch.setattr(checker.platform, "machine", lambda: "x86_64")
    output = tmp_path / "tools.txt"
    code = checker.main(["--json", "--manifest", str(manifest_path), "--write-reference", str(output)])
    assert code == 1
    assert not output.exists()
    status = json.loads(capsys.readouterr().out)
    assert status["categories"]["web"][0]["available"] is False


def test_reference_comes_from_same_manifest(tmp_path, monkeypatch):
    checker = _checker()
    manifest_path = tmp_path / "tools.json"
    manifest_path.write_text(json.dumps({
        "target_architecture": "x86_64",
        "categories": {"web": [{"name": "Python", "command": "python", "use": "scripts"}]},
    }), encoding="utf-8")
    monkeypatch.setattr(checker.platform, "machine", lambda: "x86_64")
    output = tmp_path / "tools.txt"
    assert checker.main(["--manifest", str(manifest_path), "--write-reference", str(output)]) == 0
    assert "Python: python — scripts" in output.read_text(encoding="utf-8")


def test_wrong_architecture_fails_check(tmp_path, monkeypatch, capsys):
    checker = _checker()
    manifest_path = tmp_path / "tools.json"
    manifest_path.write_text(json.dumps({
        "target_architecture": "x86_64",
        "categories": {"web": [{"name": "Python", "command": "python", "use": "scripts"}]},
    }), encoding="utf-8")
    monkeypatch.setattr(checker.platform, "machine", lambda: "aarch64")
    assert checker.main(["--json", "--manifest", str(manifest_path)]) == 1
    assert json.loads(capsys.readouterr().out)["architecture"] == "aarch64"
