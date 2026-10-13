from __future__ import annotations

import asyncio
import hashlib
import warnings
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
import yaml

from backend.challenge_filter import normalize_challenge_types
from backend.config import Settings
from backend.ctfd import CTFdClient
from backend.platforms import browser_mcp
from backend.platforms.browser_mcp import (
    BrowserAutoPlatformAdapter,
    BrowserMCPClient,
    BrowserProfileInUseError,
    PlaywrightToolDiscoveryError,
)
from backend.platforms.environments import LocalEnvironmentManager
from backend.platforms.factory import create_platform
from backend.platforms.local import LocalPlatformAdapter
from backend.platforms.models import (
    AttachmentMetadata,
    ChallengeBundle,
    ChallengeMode,
    ChallengeState,
    EnvironmentInfo,
)
from backend.platforms.recipes import PlatformRecipe, RecipeStore, redact_sensitive_text
from backend.platforms.state import AttachmentCandidate, ChallengeStateStore
from backend.prompts import ChallengeMeta


def _staged_name(arguments):
    import re
    return re.search(r'const filename = "([^"]+)";', arguments["code"]).group(1)


def test_challenge_type_preference_normalization():
    assert normalize_challenge_types(["PWN", "reverse,web"]) == {"pwn", "reverse", "web"}


@pytest.mark.parametrize(
    ("files", "connection_info", "expected"),
    [
        ([], "", ChallengeMode.UNKNOWN),
        (["distfiles/a.zip"], "", ChallengeMode.ATTACHMENT),
        ([], "http://target/", ChallengeMode.REMOTE),
        (["distfiles/a.zip"], "http://target/", ChallengeMode.HYBRID),
    ],
)
def test_challenge_mode_inference(files, connection_info, expected):
    bundle = ChallengeBundle(
        native_id="1",
        name="demo",
        files=files,
        connection_info=connection_info,
    )
    assert bundle.normalized().mode == expected


def test_challenge_mode_inference_uses_environment_requirement_before_start():
    remote = ChallengeBundle(
        native_id="remote",
        name="remote",
        environment_required=True,
    )
    hybrid = ChallengeBundle(
        native_id="hybrid",
        name="hybrid",
        files=["distfiles/source.zip"],
        environment_required=True,
    )

    assert remote.normalized().mode == ChallengeMode.REMOTE
    assert hybrid.normalized().mode == ChallengeMode.HYBRID


def test_normalized_coerces_restored_state_without_pydantic_serializer_warning():
    bundle = ChallengeBundle(native_id="restored", name="restored").model_copy(
        update={"state": "needs_input"}
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        normalized = bundle.normalized()

    assert normalized.state is ChallengeState.NEEDS_INPUT
    assert not [warning for warning in caught if "Pydantic serializer warnings" in str(warning.message)]


def _browser_settings(tmp_path, **overrides):
    values = {
        "_env_file": None,
        "platform_url": "https://platform.test",
        "browser_profile_dir": str(tmp_path / "profile"),
        "browser_download_dir": str(tmp_path / "downloads"),
        "platform_recipe_dir": str(tmp_path / "recipes"),
        "challenge_state_db_path": str(tmp_path / "state.sqlite3"),
        "attachment_download_timeout_seconds": 1,
        "attachment_max_retries": 1,
    }
    values.update(overrides)
    return Settings(**values)


def test_browser_registration_separates_attachment_objects_from_downloaded_files(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    bundle = adapter.register_challenge(
        {
            "native_id": "42",
            "name": "hybrid",
            "connection_info": "nc target 31337",
            "files": [{"id": "a1", "fileName": "binary", "byteLength": 3}],
        }
    )

    assert bundle.files == []
    assert bundle.mode == ChallengeMode.HYBRID
    assert bundle.state.value == "waiting_for_decision"
    assert bundle.source_data["attachments"][0]["id"] == "a1"
    assert bundle.source_data["attachments_scanned"] is False


def test_browser_registration_preserves_solved_state(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    bundle = adapter.register_challenge(
        {
            "native_id": "42",
            "name": "solved",
            "solved": True,
            "attachments": [{"id": "a1", "fileName": "binary"}],
        }
    )
    assert bundle.state.value == "solved"


@pytest.mark.asyncio
async def test_attachment_scan_finds_button_on_remote_challenge(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test/competitions/",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "source",
            "name": "source",
            "attachments": [{
                "id": "known",
                "fileName": "known.bin",
                "source_url": "https://platform.test/api/v1/competitions/competition/challenges/source/attachments/known",
            }],
        }
    )
    remote = adapter.register_challenge(
        {
            "native_id": "remote-id",
            "name": "hardcar",
            "connection_info": "https://target.test",
            "attachments": [],
        }
    )
    snapshot = """
      - heading "hardcar" [level=2] [ref=title]
      - region [ref=attachments]:
          - heading "\u9644\u4ef6" [level=3] [ref=heading]
          - listitem [ref=item]:
              - button "\u9644\u4ef6.zip" [ref=download]
      - region [ref=hints]:
          - button "\u5237\u65b0\u63d0\u793a" [ref=refresh]
    """

    async def browser_call(name, arguments=None):
        return snapshot if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    with pytest.raises(RuntimeError, match="attachment_metadata_unavailable"):
        await adapter._discover_visible_attachment_candidates(remote)
    assert not remote.source_data["attachments"]
    assert remote.mode == ChallengeMode.REMOTE


@pytest.mark.asyncio
async def test_browser_download_uses_visible_attachment_button(tmp_path):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges")
    )
    adapter.register_challenge(
        {
            "native_id": "button-id",
            "name": "button-download",
            "attachments": [{"id": "a1", "fileName": "source.zip", "target": "download", "sha256": hashlib.sha256(b"archive").hexdigest()}],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)

    async def browser_call(name, arguments=None):
        if name == "browser_click":
            (adapter.browser.download_dir / "source.zip").write_bytes(b"archive")
        return "ok"

    adapter.browser.call = browser_call
    artifact = await adapter.download_attachment("button-download", "a1")

    assert artifact.relative_path == "distfiles/source.zip"
    assert (tmp_path / "challenges" / "button-download" / "distfiles" / "source.zip").exists()
    await adapter.close()


@pytest.mark.asyncio
async def test_browser_download_falls_back_to_authenticated_fetch(tmp_path):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges")
    )
    adapter.register_challenge(
        {
            "native_id": "fallback-id",
            "name": "button-fallback",
            "attachments": [{
                "id": "a1",
                "fileName": "source.zip",
                "target": "download",
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/fallback-id/attachments/a1",
            }],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}
    calls: list[str] = []

    async def browser_call(name, arguments=None):
        calls.append(name)
        if name == "browser_click":
            return "ERROR: attachment button not found"
        if name == "browser_run_code_unsafe":
            (adapter.browser.download_dir / _staged_name(arguments)).write_bytes(b"archive")
        return "ok"

    adapter.browser.call = browser_call
    artifact = await adapter.download_attachment("button-fallback", "a1")

    assert artifact.relative_path == "distfiles/source.zip"
    assert "browser_click" not in calls
    assert "browser_run_code_unsafe" in calls
    await adapter.close()


@pytest.mark.asyncio
async def test_hybrid_waits_for_environment_after_attachment_is_ready(tmp_path):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges")
    )
    adapter.register_challenge(
        {
            "native_id": "hybrid-id",
            "name": "hybrid-wait",
            "environment_required": True,
            "attachments": [{"id": "a1", "fileName": "source.zip", "target": "download", "sha256": hashlib.sha256(b"archive").hexdigest()}],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)

    async def browser_call(name, arguments=None):
        if name == "browser_click":
            (adapter.browser.download_dir / "source.zip").write_bytes(b"archive")
        return "ok"

    adapter.browser.call = browser_call
    outcome = await adapter.prepare_challenge_package("hybrid-wait")
    assert outcome["state"] == "waiting_for_environment"
    assert (await adapter.get_challenge_state("hybrid-wait"))["state"] == "waiting_for_environment"

    adapter.set_environment(
        "hybrid-wait",
        {"status": "ready", "source": "remote", "url": "https://target.test/"},
    )
    assert (await adapter.get_challenge_state("hybrid-wait"))["state"] == "ready"
    assert (await adapter.list_challenges())[0].mode == ChallengeMode.HYBRID
    await adapter.close()


@pytest.mark.asyncio
async def test_remote_waits_for_environment_registration(tmp_path):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges")
    )
    adapter.register_challenge(
        {
            "native_id": "remote-id",
            "name": "remote-wait",
            "environment_required": True,
        }
    )

    outcome = await adapter.prepare_challenge_package("remote-wait")
    assert outcome["state"] == "waiting_for_environment"
    adapter.set_environment(
        "remote-wait",
        {"status": "ready", "source": "remote", "host": "target.test", "port": 31337},
    )
    assert (await adapter.get_challenge_state("remote-wait"))["state"] == "ready"
    await adapter.close()


def test_legacy_stringified_attachment_is_migrated_from_files():
    bundle = ChallengeBundle.from_metadata(
        {
            "native_id": "42",
            "name": "legacy",
            "files": ["{'id': 'a1', 'fileName': 'binary', 'byteLength': 3}"],
            "attachments": [{"id": "a1", "fileName": "binary", "byteLength": 3}],
        }
    )

    assert bundle.files == []
    assert bundle.mode == ChallengeMode.ATTACHMENT
    assert len(bundle.source_data["attachments"]) == 1


def test_legacy_metadata_round_trip():
    bundle = ChallengeBundle.from_metadata(
        {"name": "old", "category": "web", "value": 100, "connection_info": "nc host 1"}
    )
    assert bundle.native_id == "old"
    assert bundle.mode == ChallengeMode.REMOTE
    assert bundle.metadata_dict()["challenge_mode"] == "remote"


def test_challenge_meta_reads_utf8_yaml(tmp_path):
    metadata = tmp_path / "metadata.yml"
    metadata.write_text("name: 中文题目\ncategory: pwn\ndescription: 中文描述\n", encoding="utf-8")
    meta = ChallengeMeta.from_yaml(metadata)
    assert meta.name == "中文题目"
    assert meta.description == "中文描述"


def test_challenge_state_store_persists_attachment_manifest(tmp_path):
    store = ChallengeStateStore(tmp_path / "state.sqlite3", run_id="run-1")
    store.upsert_challenge(
        native_id="42",
        name="demo",
        slug="demo",
        mode="attachment",
        package_dir=str(tmp_path / "demo"),
        state="waiting_for_decision",
    )
    candidate = AttachmentCandidate("a1", "source.zip", target="download")
    store.upsert_attachment("42", candidate)
    store.set_attachment_state(
        "42",
        "a1",
        "ready",
        relative_path="distfiles/source.zip",
        sha256="abc",
        byte_count=3,
    )
    assert store.get_challenge("42")["state"] == "waiting_for_decision"
    assert store.ready_artifacts("42")[0].relative_path == "distfiles/source.zip"


@pytest.mark.asyncio
async def test_browser_download_ignores_page_evidence_files(tmp_path):
    download_dir = tmp_path / "downloads"
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        ctfd_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(download_dir),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "platform": "browser-auto",
            "native_id": "42",
            "name": "download demo",
            "attachments": [{
                "id": "a1",
                "name": "source.zip",
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/42/attachments/a1",
            }],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}

    async def browser_call(name, arguments=None):
        if name == "browser_run_code_unsafe":
            (adapter.browser.download_dir / _staged_name(arguments)).write_bytes(b"archive")
            (adapter.browser.download_dir / "page-after.yml").write_text("snapshot", encoding="utf-8")
        return "ok"

    adapter.browser.call = browser_call
    artifact = await adapter.download_attachment("download demo", "a1")
    assert artifact.relative_path == "distfiles/source.zip"
    assert (tmp_path / "challenges" / "download-demo" / "distfiles" / "source.zip").exists()
    assert not (tmp_path / "challenges" / "download-demo" / "distfiles" / "page-after.yml").exists()
    await adapter.close()


@pytest.mark.asyncio
async def test_browser_download_uses_authenticated_page_fetch(tmp_path):
    payload = b"binary-data"
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        attachment_download_timeout_seconds=3,
        attachment_max_retries=1,
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "challenge-id",
            "name": "delayed",
            "attachments": [{
                "id": "a1",
                "fileName": "binary",
                "byteLength": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/challenge-id/attachments/a1",
            }],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}

    async def browser_call(name, arguments=None):
        if name == "browser_run_code_unsafe":
            (adapter.browser.download_dir / _staged_name(arguments)).write_bytes(payload)
        return "ok"

    adapter.browser.call = browser_call
    artifact = await adapter.download_attachment("delayed", "a1")
    assert artifact.bytes == len(payload)
    assert artifact.sha256 == hashlib.sha256(payload).hexdigest()
    await adapter.close()


@pytest.mark.asyncio
async def test_browser_download_uses_authenticated_same_origin_fetch(tmp_path):
    payload = b"fetched-data"
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        attachment_download_timeout_seconds=1,
        attachment_max_retries=1,
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "challenge-id",
            "name": "fetch-fallback",
            "attachments": [{
                "id": "a1",
                "fileName": "archive.zip",
                "byteLength": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/challenge-id/attachments/a1",
            }],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}
    evaluated: list[str] = []

    async def browser_call(name, arguments=None):
        if name == "browser_snapshot":
            return "attachment region is still empty"
        if name == "browser_find":
            return "not found"
        if name == "browser_run_code_unsafe":
            code = arguments["code"]
            evaluated.append(code)
            (adapter.browser.download_dir / _staged_name(arguments)).write_bytes(payload)
            return "ok"
        return "ok"

    adapter.browser.call = browser_call
    artifact = await adapter.download_attachment("fetch-fallback", "a1")
    assert artifact.bytes == len(payload)
    assert evaluated and "credentials: 'include'" in evaluated[0]
    assert "document.cookie" not in evaluated[0]
    assert "showSaveFilePicker" not in evaluated[0]
    await adapter.close()


def test_attachment_metadata_normalizes_aliases_and_collection_url():
    metadata = AttachmentMetadata.from_raw(
        {
            "id": "a1",
            "file_name": "attach.png",
            "byte_length": "12",
            "url": "https://platform.test/api/v1/competitions/c/challenges/ch/attachments",
            "sha256": "ABC123",
        }
    )
    assert metadata.attachment_id == "a1"
    assert metadata.name == "attach.png"
    assert metadata.size == 12
    assert metadata.source_url.endswith("/attachments/a1")
    assert metadata.has_exact_source_url is True
    assert metadata.sha256 == "abc123"


def test_attachment_metadata_rejects_collection_url_without_id():
    metadata = AttachmentMetadata.from_raw(
        {
            "file_name": "attach.png",
            "url": "https://platform.test/api/v1/competitions/c/challenges/ch/attachments",
        }
    )
    assert metadata.is_collection_url is True
    assert metadata.has_exact_source_url is False


@pytest.mark.asyncio
async def test_existing_verified_distfile_is_migrated_to_ready(tmp_path):
    payload = b"existing-attachment"
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "challenge-id",
            "name": "recovered",
            "attachments": [{
                "id": "a1",
                "file_name": "attach.png",
                "byte_length": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/ch/attachments/a1",
            }],
        }
    )
    distfiles = tmp_path / "challenges" / "recovered" / "distfiles"
    distfiles.mkdir(parents=True)
    (distfiles / "attach.png").write_bytes(payload)
    candidates = await adapter.list_attachment_candidates("recovered")
    assert candidates[0].name == "attach.png"
    state = await adapter.get_challenge_state("recovered")
    assert state["attachments"][0]["state"] == "ready"
    assert state["attachments"][0]["relative_path"] == "distfiles/attach.png"
    assert "distfiles/attach.png" in (await adapter.list_challenges())[0].files
    await adapter.close()


@pytest.mark.asyncio
async def test_collection_attachment_without_id_requires_input(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "challenge-id",
            "name": "collection-only",
            "attachments": [{
                "file_name": "attach.png",
                "url": "https://platform.test/api/v1/competitions/c/challenges/ch/attachments",
            }],
        }
    )
    with pytest.raises(RuntimeError, match="exact authenticated download URL"):
        await adapter.download_attachment("collection-only", "0")
    state = await adapter.get_challenge_state("collection-only")
    assert state["state"] == "needs_input"
    assert state["attachments"][0]["state"] == "failed"
    await adapter.close()


@pytest.mark.asyncio
async def test_attachment_download_retries_three_times_then_fails(tmp_path, monkeypatch):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        attachment_max_retries=3,
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "42",
            "name": "broken-download",
            "attachments": [{
                "id": "a1",
                "fileName": "binary",
                "source_url": "https://platform.test/api/v1/competitions/c/challenges/42/attachments/a1",
            }],
        }
    )
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}

    async def browser_call(name, arguments=None):
        return "ERROR: browser fetch failed" if name == "browser_run_code_unsafe" else "ok"

    async def no_delay(_seconds):
        return None

    adapter.browser.call = browser_call
    monkeypatch.setattr("backend.platforms.browser_mcp.asyncio.sleep", no_delay)
    with pytest.raises(RuntimeError, match="after 3 attempts"):
        await adapter.download_attachment("broken-download", "a1")

    state = await adapter.get_challenge_state("broken-download")
    assert state["attachments"][0]["attempts"] == 3
    assert state["attachments"][0]["state"] == "failed"
    await adapter.close()


@pytest.mark.asyncio
async def test_package_failure_marks_challenge_needs_input_with_evidence(tmp_path, monkeypatch):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge(
        {
            "native_id": "42",
            "name": "partial",
            "attachments": [
                {"id": "a1", "fileName": "one.bin", "target": "one"},
                {"id": "a2", "fileName": "two.bin", "target": "two"},
            ],
        }
    )
    calls: list[str] = []

    async def fake_download(challenge_name, attachment_id):
        calls.append(attachment_id)
        if attachment_id == "a2":
            raise RuntimeError("second attachment failed")
        adapter.state.set_attachment_state("42", "a1", "ready", relative_path="distfiles/one.bin")
        distfiles = tmp_path / "challenges" / "partial" / "distfiles"
        distfiles.mkdir(parents=True, exist_ok=True)
        (distfiles / "one.bin").write_bytes(b"one")
        return None

    monkeypatch.setattr(adapter, "download_attachment", fake_download)
    outcome = await adapter.prepare_challenge_package("partial")

    assert calls == ["a1", "a2"]
    assert outcome["state"] == "needs_input"
    state = await adapter.get_challenge_state("partial")
    assert state["state"] == "needs_input"
    assert "second attachment failed" in state["reason"]
    assert "one.bin" in state["reason"]
    await adapter.close()


@pytest.mark.asyncio
async def test_local_adapter_reads_downloaded_challenge(tmp_path):
    challenge_dir = tmp_path / "demo"
    distfiles = challenge_dir / "distfiles"
    distfiles.mkdir(parents=True)
    (distfiles / "flag.txt").write_text("not the flag", encoding="utf-8")
    (challenge_dir / "metadata.yml").write_text(
        yaml.safe_dump({"name": "demo", "category": "misc", "value": 10}),
        encoding="utf-8",
    )

    adapter = LocalPlatformAdapter(tmp_path)
    await adapter.start()
    challenges = await adapter.list_challenges()
    assert len(challenges) == 1
    assert challenges[0].mode == ChallengeMode.ATTACHMENT
    assert challenges[0].files == ["distfiles/flag.txt"]
    assert (await adapter.prepare_challenge("demo")).name == "demo"
    await adapter.close()


@pytest.mark.asyncio
async def test_local_duplicate_names_fail_before_indexing(tmp_path):
    for folder in ("first", "second"):
        directory = tmp_path / "challenges" / folder
        directory.mkdir(parents=True)
        (directory / "metadata.yml").write_text(
            "name: Same Name\nconnection_info: nc example.org 1\n", encoding="utf-8"
        )
    adapter = LocalPlatformAdapter(
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        with pytest.raises(ValueError, match="Duplicate challenge names"):
            await adapter.list_challenges()
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_local_duplicate_native_ids_fail_before_state_write(tmp_path):
    for folder in ("first", "second"):
        directory = tmp_path / "challenges" / folder
        directory.mkdir(parents=True)
        (directory / "metadata.yml").write_text(
            f"name: {folder}\nnative_id: shared\nconnection_info: nc example.org 1\n",
            encoding="utf-8",
        )
    adapter = LocalPlatformAdapter(
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        with pytest.raises(ValueError, match="Duplicate challenge native IDs"):
            await adapter.list_challenges()
        assert adapter.state.list_challenges() == []
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_local_invalid_solve_status_fails_instead_of_clearing_solves(tmp_path):
    (tmp_path / ".solve-status.json").write_text("{invalid", encoding="utf-8")
    adapter = LocalPlatformAdapter(
        str(tmp_path),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        with pytest.raises(RuntimeError, match="Could not read local solve status"):
            await adapter.get_solve_status()
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_local_manual_state_survives_poll_until_explicit_retry(tmp_path):
    directory = tmp_path / "challenges" / "challenge"
    (directory / "distfiles").mkdir(parents=True)
    (directory / "distfiles" / "input.txt").write_text("fixture", encoding="utf-8")
    (directory / "metadata.yml").write_text("name: Challenge\n", encoding="utf-8")
    adapter = LocalPlatformAdapter(
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        await adapter.list_challenges()
        await adapter.mark_needs_input("Challenge", "operator review")
        await adapter.list_challenges()
        state = await adapter.get_challenge_state("Challenge")
        assert state["state"] == "needs_input"
        assert state["reason"] == "operator review"
        await adapter.retry_challenge_preparation("Challenge")
        await adapter.list_challenges()
        assert (await adapter.get_challenge_state("Challenge"))["state"] == "ready"
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_local_nested_attachment_is_ready_and_visible_to_solver(tmp_path):
    from backend.prompts import list_distfiles

    directory = tmp_path / "challenges" / "nested"
    nested = directory / "distfiles" / "resources"
    nested.mkdir(parents=True)
    (nested / "input.bin").write_bytes(b"fixture")
    (directory / "metadata.yml").write_text("name: nested\n", encoding="utf-8")
    adapter = LocalPlatformAdapter(
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        bundles = await adapter.list_challenges()
        assert bundles[0].files == ["distfiles/resources/input.bin"]
        assert (await adapter.get_challenge_state("nested"))["state"] == "ready"
        assert list_distfiles(str(directory)) == ["resources/input.bin"]
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_local_compose_waits_until_started_and_exposes_runtime_endpoint(tmp_path, monkeypatch):
    directory = tmp_path / "challenges" / "service"
    directory.mkdir(parents=True)
    (directory / "metadata.yml").write_text(
        yaml.safe_dump({
            "name": "service",
            "environment": {"source": "compose", "compose_file": "compose.yml", "url": "http://localhost:8765/"},
        }), encoding="utf-8",
    )
    adapter = LocalPlatformAdapter(
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    calls = []

    async def fake_start(name, env):
        calls.append((name, env))
        return EnvironmentInfo(status="ready", source="compose", url="http://localhost:8765/", compose_project="demo")

    monkeypatch.setattr(adapter._environment_manager, "start", fake_start)
    try:
        await adapter.list_challenges()
        assert (await adapter.get_challenge_state("service"))["state"] == "waiting_for_environment"
        info = await adapter.start_environment("service")
        assert info.status == "ready"
        assert len(calls) == 1
        assert calls[0][1]["challenge_dir"] == "service"
        assert (await adapter.start_environment("service")) == info
        bundle = await adapter.prepare_challenge("service")
        assert bundle.connection_info == "http://localhost:8765/"
        assert bundle.environment["compose_project"] == "demo"
        state = await adapter.get_challenge_state("service")
        assert state["state"] == "ready"
        assert state["connection_info"] == bundle.connection_info
    finally:
        await adapter.close()


def test_browser_rejects_duplicate_name_and_slug_before_overwriting(tmp_path):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    first = adapter.register_challenge({"native_id": "1", "name": "A.B", "connection_info": "nc one 1"})
    metadata = (tmp_path / "challenges" / "ab" / "metadata.yml").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate challenge name"):
        adapter.register_challenge({"native_id": "2", "name": "A.B", "connection_info": "nc two 2"})
    with pytest.raises(ValueError, match="collide after directory normalization"):
        adapter.register_challenge({"native_id": "3", "name": "AB", "connection_info": "nc three 3"})
    assert adapter._bundles == {first.name: first}
    assert (tmp_path / "challenges" / "ab" / "metadata.yml").read_text(encoding="utf-8") == metadata


def test_browser_rejects_rename_of_registered_native_id(tmp_path):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.register_challenge({"native_id": "1", "name": "Original", "connection_info": "nc one 1"})
    with pytest.raises(ValueError, match="changed name"):
        adapter.register_challenge({"native_id": "1", "name": "Renamed", "connection_info": "nc one 1"})
    assert set(adapter._bundles) == {"Original"}
    assert not (tmp_path / "challenges" / "renamed").exists()


def test_compose_policy_rejects_host_access(tmp_path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text(
        yaml.safe_dump({"services": {"web": {"image": "nginx", "privileged": True}}}),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="privileged"):
        LocalEnvironmentManager(tmp_path).validate_compose(compose)


@pytest.mark.parametrize(
    "volume",
    [
        "./host:/container",
        "/host:/container",
        r"C:\host:/container",
        {"type": "bind", "source": "./host", "target": "/container"},
        {"type": "bind", "source": "/host", "target": "/container"},
    ],
)
def test_compose_policy_rejects_short_and_long_bind_mounts(tmp_path, volume):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text(
        yaml.safe_dump({"services": {"web": {"image": "nginx", "volumes": [volume]}}}),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="bind mount"):
        LocalEnvironmentManager(tmp_path).validate_compose(compose)


def test_compose_policy_allows_named_volumes(tmp_path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text(
        yaml.safe_dump(
            {
                "services": {"web": {"image": "nginx", "volumes": ["cache:/cache"]}},
                "volumes": {"cache": {}},
            }
        ),
        encoding="utf-8",
    )
    LocalEnvironmentManager(tmp_path).validate_compose(compose)


def test_recipe_store_and_redaction(tmp_path):
    store = RecipeStore(tmp_path)
    recipe = PlatformRecipe(
        platform_origin="https://example.test",
        confidence=0.9,
        steps=[{"action": "navigate", "value": "https://example.test/challenges"}],
    )
    saved = store.save(recipe)
    assert store.load("https://example.test") == recipe
    assert saved.exists()
    redacted = redact_sensitive_text("Authorization: Bearer abc.def")
    assert "abc.def" not in redacted
    assert "<redacted>" in redacted


@pytest.mark.parametrize(
    "steps",
    [
        [{"action": "snapshot"}],
        [{"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
         {"action": "click", "target": "submit"}],
        [{"action": "navigate", "value": "https://evil.test/challenges/{challenge_id}"},
         {"action": "type", "target": "input", "value": "{flag}"},
         {"action": "click", "target": "submit"}],
        [{"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
         {"action": "type", "target": "input", "value": "{flag}"},
         {"action": "snapshot"}],
    ],
)
def test_submission_setup_rejects_non_submitting_recipes(tmp_path, steps):
    settings = _browser_settings(tmp_path)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"), allow_submit=True)
    with pytest.raises(RuntimeError, match="recipe"):
        adapter.save_recipe({"platform_origin": "https://platform.test", "steps": steps})
    assert adapter.submission_recipe_issue() is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("steps", [
    [
        {"action": "navigate", "url": "https://platform.test/challenges/{challenge_id}"},
        {"action": "type", "target": 'textarea[aria-label="Flag"]', "value": "{flag}", "submit": True},
    ],
    [
        {"type": "navigate", "url": "https://platform.test/challenges/{challenge_id}"},
        {"type": "type", "target": 'textarea[aria-label="Flag"]', "text": "{flag}", "submit": True},
    ],
])
async def test_logged_recipe_aliases_save_and_execute(tmp_path, steps):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges"), allow_submit=True,
    )
    adapter.register_challenge({"native_id": "real-id", "name": "demo"})
    calls = []

    async def browser_call(name, args=None):
        calls.append((name, args))
        return "Flag form" if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    adapter.save_recipe({"platform_origin": "https://platform.test", "steps": steps})
    assert adapter.submission_recipe_issue() is None
    recipe = adapter.recipes.load("https://platform.test")
    assert [step.action for step in recipe.steps] == ["navigate", "type"]
    assert recipe.steps[1].data["submit"] is True
    result = await adapter.submit_flag("demo", "FLAG{ok}")
    assert result.status == "pending"
    assert ("browser_navigate", {"url": "https://platform.test/challenges/real-id"}) in calls
    assert ("browser_type", {
        "target": 'textarea[aria-label="Flag"]', "text": "FLAG{ok}", "submit": True,
    }) in calls
    await adapter.close()


def test_recipe_validation_error_names_expected_fields(tmp_path):
    adapter = BrowserAutoPlatformAdapter(
        _browser_settings(tmp_path), str(tmp_path / "challenges"), allow_submit=True,
    )
    with pytest.raises(ValueError, match=r"steps\.0\.action.*Use action='navigate'"):
        adapter.save_recipe({
            "platform_origin": "https://platform.test",
            "steps": [{"value": "https://platform.test/challenges/{challenge_id}"}],
        })


@pytest.mark.asyncio
async def test_failed_browser_click_never_creates_pending_submission(tmp_path):
    settings = _browser_settings(tmp_path)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"), allow_submit=True)
    adapter.register_challenge({"native_id": "42", "name": "demo"})
    adapter.save_recipe({
        "platform_origin": "https://platform.test",
        "steps": [
            {"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
            {"action": "type", "target": "flag-input", "value": "{flag}"},
            {"action": "click", "target": "stale-submit-button"},
        ],
    })

    async def browser_call(name, args=None):
        if name == "browser_click":
            return "ERROR\nElement not found"
        return "Flag form" if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    with pytest.raises(RuntimeError, match="Submission recipe browser_click failed"):
        await adapter.submit_flag("demo", "FLAG{ok}")
    assert adapter._pending_submissions == {}
    await adapter.close()


@pytest.mark.asyncio
async def test_submission_recipe_uses_native_id_for_challenge_url(tmp_path):
    settings = _browser_settings(tmp_path)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"), allow_submit=True)
    adapter.register_challenge({"native_id": "real-id", "name": "display name"})
    calls = []

    async def browser_call(name, args=None):
        calls.append((name, args))
        return "submission result" if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    adapter.save_recipe({
        "platform_origin": "https://platform.test",
        "steps": [
            {"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
            {"action": "type", "target": "flag-input", "value": "{flag}"},
            {"action": "click", "target": "submit-button"},
        ],
    })
    result = await adapter.submit_flag("display name", "FLAG{real}")
    assert result.status == "pending"
    assert ("browser_navigate", {"url": "https://platform.test/challenges/real-id"}) in calls
    assert ("browser_type", {"target": "flag-input", "text": "FLAG{real}"}) in calls
    await adapter.close()


def test_ctfd_token_prefix_is_normalized():
    client = CTFdClient(token="Bearer abc")
    assert client._base_headers()["Authorization"] == "Token abc"


def test_submission_requires_browser_platform(tmp_path):
    settings = Settings(_env_file=None, platform="local")
    with pytest.raises(ValueError, match="Playwright MCP"):
        create_platform(settings, str(tmp_path), allow_submit=True)


def test_browser_origin_allowlist():
    client = BrowserMCPClient("https://platform.test", ".runtime/profile", ".runtime/downloads")
    client.allow_origin("https://target.test")
    assert client._check_url("https://target.test/challenge") is None
    assert client._check_url("https://other.test/") is not None


@pytest.mark.asyncio
async def test_browser_client_enters_and_exits_mcp_contexts_in_one_task(tmp_path, monkeypatch):
    """Regression: anyio aborts the run when another task exits these contexts."""
    entered: list[asyncio.Task] = []
    exited: list[asyncio.Task] = []

    @asynccontextmanager
    async def fake_stdio(_params):
        entered.append(asyncio.current_task())
        try:
            yield SimpleNamespace(), SimpleNamespace()
        finally:
            exited.append(asyncio.current_task())

    class FakeSession:
        def __init__(self, read_stream, write_stream):
            self.read_stream, self.write_stream = read_stream, write_stream

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_exc_info):
            return False

        async def initialize(self) -> None:
            return None

        async def list_tools(self):
            names = ("browser_navigate", "browser_snapshot", "browser_click",
                     "browser_find", "browser_wait_for", "browser_tabs")
            return SimpleNamespace(tools=[
                SimpleNamespace(name=name, description=name, input_schema={"type": "object"})
                for name in names
            ])

    monkeypatch.setattr(browser_mcp, "stdio_client", fake_stdio)
    monkeypatch.setattr(browser_mcp, "ClientSession", FakeSession)

    client = BrowserMCPClient("https://platform.test", str(tmp_path / "profile"),
                              str(tmp_path / "downloads"))
    await client.start()
    await asyncio.create_task(client.restart())
    await asyncio.create_task(client.close())

    assert entered == exited
    assert len(entered) == 2
    assert len(set(entered)) == 1
    assert entered[0] is not asyncio.current_task()


@pytest.mark.asyncio
async def test_profile_in_use_error_blocks_further_browser_calls(tmp_path):
    client = BrowserMCPClient("https://platform.test", str(tmp_path / "profile"),
                              str(tmp_path / "downloads"))

    class ErrorResult:
        is_error = True
        content = [SimpleNamespace(type="text", text=(
            "Error: Browser is already in use for C:\\runtime\\profile, "
            "use --isolated to run multiple instances of the same browser"
        ))]

    calls: list[str] = []

    class Session:
        async def call_tool(self, name, arguments):
            calls.append(name)
            return ErrorResult()

    client._session = Session()
    client._tool_specs = {"browser_navigate": {}, "browser_snapshot": {}}

    first = await client.call("browser_snapshot", {})
    assert "already in use" in first
    assert "browser_restart" in first
    assert client.profile_blocked_reason() == first

    second = await client.call("browser_navigate", {"url": "https://platform.test"})
    assert second == first
    assert calls == ["browser_snapshot"]


@pytest.mark.asyncio
async def test_platform_login_start_raises_when_profile_is_held(tmp_path, monkeypatch):
    settings = _browser_settings(tmp_path, platform_login=True)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))

    async def fake_start() -> None:
        return None

    async def blocked_call(name, arguments=None):
        adapter.browser._block_on_profile_conflict()
        return adapter.browser.profile_blocked_reason()

    monkeypatch.setattr(adapter.browser, "start", fake_start)
    monkeypatch.setattr(adapter.browser, "call", blocked_call)

    with pytest.raises(BrowserProfileInUseError, match="profile"):
        await adapter.start()


def test_attachment_collection_url_is_treated_as_challenge_page_not_file_download(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    url = "https://platform.test/api/v1/competitions/c/challenges/ch/attachments"
    assert adapter._derive_challenge_page(url) == (
        "https://platform.test/competitions/c/challenges?challenge=ch"
    )
    assert adapter._has_usable_attachment_metadata({"fileName": "attach.png", "url": url}) is False
    assert adapter._has_usable_attachment_metadata(
        {"fileName": "attach.png", "url": url + "/file-id"}
    ) is True


def test_browser_mcp_loads_dynamic_tool_catalog_and_fails_closed(tmp_path):
    client = BrowserMCPClient("https://platform.test", str(tmp_path / "profile"), str(tmp_path / "downloads"))
    tools = [
        SimpleNamespace(name=name, description=name, input_schema={"type": "object"})
        for name in (
            "browser_navigate",
            "browser_snapshot",
            "browser_click",
            "browser_find",
            "browser_wait_for",
            "browser_tabs",
            "browser_run_code_unsafe",
        )
    ]
    client._load_tool_catalog(tools)
    assert {item["name"] for item in client.browser_tool_specs()} == {item.name for item in tools}
    assert "browser_run_code_unsafe" in client._tool_specs

    missing = BrowserMCPClient("https://platform.test", str(tmp_path / "p2"), str(tmp_path / "d2"))
    with pytest.raises(PlaywrightToolDiscoveryError):
        missing._load_tool_catalog(tools[:2])


def test_browser_mcp_result_helpers_do_not_read_deprecated_aliases():
    class V2Result:
        structured_content = None
        is_error = False
        content = []

        def __getattr__(self, name):
            if name in {"structuredContent", "isError"}:
                raise AssertionError(f"deprecated MCP field {name} was accessed")
            raise AttributeError(name)

    result = V2Result()
    assert BrowserMCPClient._result_is_error(result) is False
    assert BrowserMCPClient._format_result(result) == "(no output)"


@pytest.mark.asyncio
async def test_browser_adapter_registers_download_and_environment(tmp_path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        ctfd_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(download_dir),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge({
        "platform": "browser-auto",
        "native_id": "42",
        "name": "web demo",
        "attachments": [{
            "id": "source",
            "name": "source.zip",
            "sha256": hashlib.sha256(b"archive").hexdigest(),
            "source_url": "https://platform.test/api/v1/competitions/c/challenges/42/attachments/source",
        }],
    })
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    adapter.browser._tool_specs = {"browser_run_code_unsafe": {}}
    (adapter.browser.download_dir / "source.zip").write_bytes(b"archive")

    async def browser_call(name, arguments=None):
        return "ok"

    adapter.browser.call = browser_call
    imported = await adapter.import_latest_download("web demo", "source.zip")
    assert imported["path"] == "distfiles/source.zip"
    info = adapter.set_environment("web demo", {"status": "ready", "source": "remote", "url": "https://target.test/"})
    assert info.url == "https://target.test/"
    bundle = (await adapter.list_challenges())[0]
    assert bundle.mode == ChallengeMode.HYBRID
    assert adapter.browser._check_url("https://target.test/") is None
    await adapter.close()


@pytest.mark.asyncio
async def test_browser_submission_returns_evidence_for_agent_judgment(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        ctfd_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"), allow_submit=True)
    adapter.register_challenge({"platform": "browser-auto", "native_id": "42", "name": "web demo"})

    async def browser_call(name, arguments=None):
        if name == "browser_snapshot":
            return "Submission accepted"
        return "ok"

    adapter.browser.call = browser_call
    adapter.save_recipe(
        {
            "platform_origin": "https://platform.test",
            "steps": [
                {"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
                {"action": "type", "target": "flag-input", "value": "{flag}"},
                {"action": "click", "target": "submit-button"},
            ],
            "success_markers": ["Submission accepted"],
            "failure_markers": ["Incorrect"],
        }
    )

    result = await adapter.submit_flag("web demo", "FLAG{test}")
    assert result.status == "pending"
    assert "SUBMISSION_PENDING" in result.display
    confirmed = await adapter.confirm_submission(
        "web demo", "FLAG{test}", True, "The page states Submission accepted."
    )
    assert confirmed.status == "correct"
    assert await adapter.get_solve_status() == {"web demo"}
    assert adapter.get_confirmed_flag("web demo") == "FLAG{test}"
    assert adapter.get_confirmed_flag("42") == "FLAG{test}"
    with pytest.raises(RuntimeError, match="No pending submission"):
        await adapter.confirm_submission("web demo", "FLAG{test}", True, "duplicate")
    await adapter.close()


@pytest.mark.asyncio
async def test_browser_submission_confirmation_requires_matching_pending_flag(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"), allow_submit=True)
    adapter.register_challenge({"native_id": "42", "name": "web demo"})
    snapshots = iter(
        [
            "Flag form", "Flag form",
            "Incorrect flag",
            "Incorrect flag is historical; accepted now",
            "Incorrect flag is historical; accepted now",
        ]
    )

    async def browser_call(name, arguments=None):
        return next(snapshots) if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    adapter.save_recipe(
        {
            "platform_origin": "https://platform.test",
            "steps": [
                {"action": "navigate", "value": "https://platform.test/challenges/{challenge_id}"},
                {"action": "type", "target": "flag-input", "value": "{flag}"},
                {"action": "click", "target": "submit-button"},
            ],
            "failure_markers": ["Incorrect flag"],
        }
    )
    pending = await adapter.submit_flag("web demo", "FLAG{right}")
    assert pending.status == "pending"
    with pytest.raises(RuntimeError, match="does not match"):
        await adapter.confirm_submission("web demo", "FLAG{wrong}", True, "wrong flag")
    with pytest.raises(RuntimeError, match="explicitly mention"):
        await adapter.confirm_submission("web demo", "FLAG{right}", True, "The new result is accepted")

    confirmed = await adapter.confirm_submission(
        "web demo",
        "FLAG{right}",
        True,
        "The 'Incorrect flag' marker is historical; the current result says accepted now.",
    )
    assert confirmed.status == "correct"
    record = adapter._submission_confirmations[-1]
    assert "accepted now" in record.evidence
    assert record.failure_markers == ("Incorrect flag",)
    await adapter.close()


def test_browser_submission_recipe_requires_steps(tmp_path):
    settings = Settings(
        _env_file=None,
        platform_url="https://platform.test",
        ctfd_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    with pytest.raises(RuntimeError, match="browser steps"):
        adapter.save_recipe(
            {
                "platform_origin": "https://platform.test",
                "steps": [],
            }
        )


@pytest.mark.asyncio
async def test_ui_only_without_hash_rejects_unrelated_download(tmp_path):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.register_challenge({"native_id": "one", "name": "one", "attachments": [
        {"id": "a1", "fileName": "attachment", "target": "button"}]})
    adapter.browser.download_dir.mkdir(parents=True, exist_ok=True)
    (adapter.browser.download_dir / "attachment").write_bytes(b"other challenge")
    calls = []

    async def browser_call(name, arguments=None):
        calls.append(name)
        return "ok"

    adapter.browser.call = browser_call
    with pytest.raises(RuntimeError, match="attachment_unverifiable"):
        await adapter.download_attachment("one", "a1")
    assert "browser_click" not in calls
    assert not (tmp_path / "challenges" / "one" / "distfiles" / "attachment").exists()
    await adapter.close()


@pytest.mark.asyncio
async def test_exact_url_rejects_cross_challenge_id(tmp_path):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.register_challenge({"native_id": "one", "name": "one", "attachments": [{
        "id": "a1", "fileName": "attachment", "source_url":
        "https://platform.test/api/v1/competitions/c/challenges/two/attachments/a1"}]})
    with pytest.raises(RuntimeError, match="attachment_identity_mismatch"):
        await adapter.download_attachment("one", "a1")
    await adapter.close()


@pytest.mark.asyncio
async def test_stale_ready_record_is_invalidated_including_path(tmp_path):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.register_challenge({"native_id": "one", "name": "one", "attachments": [{
        "id": "a1", "fileName": "attachment", "sha256": hashlib.sha256(b"correct").hexdigest(),
        "target": "button"}]})
    distfiles = tmp_path / "challenges" / "one" / "distfiles"
    distfiles.mkdir()
    (distfiles / "attachment").write_bytes(b"incorrect")
    candidate = (await adapter.list_attachment_candidates("one"))[0]
    adapter.state.set_attachment_state("one", candidate.attachment_id, "ready",
                                       relative_path="distfiles/attachment",
                                       sha256=hashlib.sha256(b"incorrect").hexdigest(), byte_count=9)
    result = await adapter.get_challenge_state("one")
    assert result["attachments"][0]["state"] == "available"
    assert result["attachments"][0]["relative_path"] == ""
    assert result["attachments"][0]["sha256"] == ""
    assert result["state"] != "ready"
    await adapter.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("with_id", [False, True])
async def test_attachment_scan_keeps_hash_and_exact_url(tmp_path, with_id):
    adapter = BrowserAutoPlatformAdapter(_browser_settings(tmp_path), str(tmp_path / "challenges"))
    url = "https://platform.test/api/v1/competitions/c/challenges/source/attachments/a1"
    item = {"name": "binary", "sha256": "ab" * 32, "size": 123}
    if with_id:
        item.update({"id": "a1", "source_url": url})
    bundle = adapter.register_challenge({
        "native_id": "source", "name": "source",
        "challenge_url": "https://platform.test/competitions/c/challenges/source",
        "attachments": [item],
    })
    snapshot = (
        '  - heading "source" [level=2] [ref=title]\n'
        '  - region [ref=attachments]:\n'
        '      - heading "附件" [level=3] [ref=heading]\n'
        '      - button "binary" [ref=download]\n'
        '  - region [ref=hints]:\n'
        '      - button "hint" [ref=hint]\n'
    )

    async def browser_call(name, arguments=None):
        return snapshot if name == "browser_snapshot" else "ok"

    adapter.browser.call = browser_call
    bundle = bundle.model_copy(update={"source_data": {**bundle.source_data, "attachments_scanned": False}})
    scanned = await adapter._discover_visible_attachment_candidates(bundle)
    found = scanned.source_data["attachments"][0]
    assert found["sha256"] == "ab" * 32
    assert found["size"] == 123
    if with_id:
        assert found["id"] == "a1"
        assert found["source_url"] == url
    else:
        assert "id" not in found
    assert found["challenge_page_url"] == bundle.challenge_url
    await adapter.close()
