"""Regression tests for the NoCTF Bearer attachment path."""

import asyncio
import base64
import hashlib
import json
import re

import pytest

from backend.config import Settings
from backend.platforms.browser_mcp import BrowserAutoPlatformAdapter

PAGE = ("https://platform.test/competitions/competition/challenges/challenge")
ATTACHMENT = ("https://platform.test/api/v1/competitions/competition/challenges/"
              "challenge/attachments/attachment-id")
PAYLOAD = b"verified binary"
SHA = hashlib.sha256(PAYLOAD).hexdigest()


def adapter(tmp_path):
    settings = Settings(
        _env_file=None, platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"), browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        attachment_max_retries=1, attachment_download_timeout_seconds=1,
    )
    result = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    result.browser._tool_specs = {"browser_run_code_unsafe": {}}
    return result


def register(subject, *, attachments=None):
    return subject.register_challenge({
        "native_id": "challenge", "name": "challenge", "challenge_url": PAGE,
        "attachments": attachments if attachments is not None else [
            {"name": "binary", "sha256": SHA}],
    })


@pytest.mark.asyncio
async def test_list_restores_id_and_ignores_inconsistent_challenge_id(tmp_path):
    subject = adapter(tmp_path)
    bundle = register(subject)
    async def browser_call(name, args=None):
        assert name == "browser_run_code_unsafe"
        assert "Authorization:auth" in args["code"]
        return '### Result\n' + json.dumps({"ok": True, "items": [{
            "id": "attachment-id", "fileName": "binary", "byteLength": len(PAYLOAD),
            "sha256": SHA, "challengeId": "unrelated-id",
        }]}) + '\n### Ran Playwright code'
    subject.browser.call = browser_call
    discovered = await subject._discover_authoritative_attachments(bundle)
    candidate = subject._build_attachment_candidates(discovered)[0]
    assert candidate.attachment_id == "attachment-id"
    assert candidate.source_url == ATTACHMENT
    assert subject._expected_attachment(candidate) == (len(PAYLOAD), SHA)
    await subject.close()


@pytest.mark.asyncio
async def test_duplicate_names_are_not_assigned_old_hash_by_position(tmp_path):
    subject = adapter(tmp_path)
    bundle = register(subject, attachments=[
        {"name": "same", "sha256": "a" * 64}, {"name": "same", "sha256": "b" * 64},
    ])
    async def browser_call(name, args=None):
        return '### Result\n' + json.dumps({"ok": True, "items": [
            {"id": "id1", "fileName": "same", "byteLength": 1, "sha256": "c" * 64},
            {"id": "id2", "fileName": "same", "byteLength": 2, "sha256": "d" * 64},
        ]})
    subject.browser.call = browser_call
    result = await subject._discover_authoritative_attachments(bundle)
    assert [item["sha256"] for item in result.source_data["attachments"]] == ["c" * 64, "d" * 64]
    await subject.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("error", ["download_http_401", "download_http_404", "bearer_not_observed"])
async def test_auth_failure_does_not_fallback_to_unverified_ui(tmp_path, error):
    subject = adapter(tmp_path)
    register(subject, attachments=[{
        "id": "attachment-id", "fileName": "binary", "byteLength": len(PAYLOAD),
        "sha256": SHA, "source_url": ATTACHMENT, "target": "button",
    }])
    calls = []
    async def browser_call(name, args=None):
        calls.append(name)
        if name == "browser_run_code_unsafe":
            code = args["code"]
            assert "let attempt=0; attempt<2" in code
            assert "credentials: 'include'" not in code
            return '### Result\n' + json.dumps({"ok": False, "reason": error})
        return "ok"
    subject.browser.call = browser_call
    with pytest.raises(RuntimeError, match=error):
        await subject.download_attachment("challenge", "attachment-id")
    assert "browser_click" not in calls
    assert not list((tmp_path / "challenges" / "challenge").glob("distfiles/*"))
    await subject.close()


@pytest.mark.asyncio
async def test_mismatched_hash_never_marks_ready(tmp_path):
    subject = adapter(tmp_path)
    register(subject, attachments=[{
        "id": "attachment-id", "fileName": "binary", "byteLength": len(PAYLOAD),
        "sha256": SHA, "source_url": ATTACHMENT,
    }])
    subject.browser.download_dir.mkdir(parents=True)
    async def browser_call(name, args=None):
        payload = b"unrelated bytes"
        return '### Result\n' + json.dumps({"ok": True, "bytes": len(payload),
                                            "payload": base64.b64encode(payload).decode()})
    subject.browser.call = browser_call
    with pytest.raises(RuntimeError, match="download_hash_mismatch"):
        await subject.download_attachment("challenge", "attachment-id")
    state = await subject.get_challenge_state("challenge")
    assert state["attachments"][0]["state"] != "ready"
    assert not list((tmp_path / "challenges" / "challenge").glob("distfiles/*"))
    await subject.close()


@pytest.mark.asyncio
async def test_parallel_downloads_use_separate_staging_names(tmp_path):
    subject = adapter(tmp_path)
    register(subject, attachments=[
        {"id": "a", "name": "a.bin", "byteLength": len(PAYLOAD), "sha256": SHA,
         "source_url": ATTACHMENT.replace("attachment-id", "a")},
        {"id": "b", "name": "b.bin", "byteLength": len(PAYLOAD), "sha256": SHA,
         "source_url": ATTACHMENT.replace("attachment-id", "b")},
    ])
    subject.browser.download_dir.mkdir(parents=True)
    urls = []
    async def browser_call(name, args=None):
        code = args["code"]
        urls.append(json.loads(re.search(r'const fileUrl = (".*?");', code).group(1)))
        return '### Result\n' + json.dumps({"ok": True, "bytes": len(PAYLOAD),
                                            "payload": base64.b64encode(PAYLOAD).decode()})
    subject.browser.call = browser_call
    results = await asyncio.gather(subject.download_attachment("challenge", "a"),
                                   subject.download_attachment("challenge", "b"))
    assert len(set(urls)) == 2
    assert {r.name for r in results} == {"a.bin", "b.bin"}
    await subject.close()


@pytest.mark.asyncio
async def test_bad_size_and_token_not_returned(tmp_path):
    subject = adapter(tmp_path)
    register(subject, attachments=[{
        "id": "attachment-id", "name": "binary", "byteLength": len(PAYLOAD) + 1,
        "sha256": SHA, "source_url": ATTACHMENT,
    }])
    subject.browser.download_dir.mkdir(parents=True)
    secret = "sensitive-access-token-marker"
    outputs = []

    async def browser_call(name, args=None):
        code = args["code"]
        assert secret not in code
        result = '### Result\n' + json.dumps({"ok": True, "bytes": len(PAYLOAD),
                                              "payload": base64.b64encode(PAYLOAD).decode()})
        outputs.append(result)
        return result

    subject.browser.call = browser_call
    with pytest.raises(RuntimeError, match="download_hash_mismatch") as exc:
        await subject.download_attachment("challenge", "attachment-id")
    assert secret not in str(exc.value) + repr(outputs)
    assert not list((tmp_path / "challenges" / "challenge").glob("distfiles/*"))
    await subject.close()


@pytest.mark.asyncio
async def test_incomplete_list_metadata_is_not_promoted_to_authoritative(tmp_path):
    subject = adapter(tmp_path)
    bundle = register(subject)

    async def browser_call(name, args=None):
        return '### Result\n' + json.dumps({"ok": True, "items": [
            {"id": "attachment-id", "fileName": "binary", "byteLength": len(PAYLOAD)},
        ]})

    subject.browser.call = browser_call
    result = await subject._discover_authoritative_attachments(bundle)
    assert result.source_data["attachments"] == bundle.source_data["attachments"]
    await subject.close()
