"""Shared-browser and repeated-registration invariants."""

import asyncio
import hashlib
import json

import pytest

from backend.config import Settings
from backend.platforms.browser_mcp import BrowserAutoPlatformAdapter


def make_adapter(tmp_path):
    settings = Settings(
        _env_file=None, platform_url='https://platform.test',
        browser_profile_dir=str(tmp_path / 'profile'), browser_download_dir=str(tmp_path / 'downloads'),
        platform_recipe_dir=str(tmp_path / 'recipes'), challenge_state_db_path=str(tmp_path / 'state.db'),
        attachment_max_retries=1, attachment_download_timeout_seconds=1,
    )
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / 'challenges'))
    adapter.browser._tool_specs = {'browser_run_code_unsafe': {}}
    return adapter


def challenge(name, attachment=None):
    return {'native_id': name, 'name': name,
            'challenge_url': f'https://platform.test/competitions/c/challenges/{name}',
            'attachments': [attachment or {'name': 'binary'}]}


@pytest.mark.asyncio
async def test_authoritative_scans_serialize_shared_browser(tmp_path):
    adapter = make_adapter(tmp_path)
    names = ('one', 'two', 'three', 'four', 'five')
    bundles = [adapter.register_challenge(challenge(name)) for name in names]
    active = False
    visited = []

    async def browser_call(name, args=None):
        nonlocal active
        assert name == 'browser_run_code_unsafe'
        assert not active, 'shared page was navigated concurrently'
        active = True
        cid = next(name for name in names if f'/challenges/{name}' in args['code'])
        visited.append(cid)
        await asyncio.sleep(0.01)
        active = False
        return '### Result\n' + json.dumps({'ok': True, 'items': [{
            'id': cid + '-id', 'fileName': 'binary', 'byteLength': 4,
            'sha256': hashlib.sha256(cid.encode()).hexdigest(),
        }]})

    adapter.browser.call = browser_call
    results = await asyncio.gather(*(adapter._discover_authoritative_attachments(bundle)
                                     for bundle in bundles))
    assert set(visited) == set(names)
    assert [result.source_data['attachments'][0]['id'] for result in results] == [
        name + '-id' for name in names
    ]
    await adapter.close()


@pytest.mark.asyncio
async def test_authoritative_failure_is_explicit_and_never_guesses_ui(tmp_path):
    adapter = make_adapter(tmp_path)
    bundle = adapter.register_challenge(challenge('one'))
    calls = []

    async def browser_call(name, args=None):
        calls.append(name)
        return '### Result\n{"ok":false,"reason":"bearer_not_observed"}'

    adapter.browser.call = browser_call
    result = await adapter.prepare_challenge_package(bundle.name)
    assert result['state'] == 'needs_input'
    assert 'attachment_metadata_unavailable' in result['message']
    assert calls == ['browser_run_code_unsafe']
    await adapter.close()


@pytest.mark.asyncio
async def test_ui_scan_rejects_sidebar_only_name(tmp_path):
    adapter = make_adapter(tmp_path)
    adapter.browser._tool_specs = {}  # Generic UI-only platform.
    bundle = adapter.register_challenge({
        'native_id': 'one', 'name': 'one', 'attachments': [{'name': 'binary', 'sha256': 'a' * 64}],
    })
    snapshot = (
        '  - option "one" [ref=sidebar]\n'
        '  - heading "two" [level=2] [ref=active]\n'
        '  - region [ref=attachments]:\n'
        '      - heading "\u9644\u4ef6" [level=3] [ref=heading]\n'
        '      - button "other.zip" [ref=button]\n'
    )

    async def browser_call(name, args=None):
        return snapshot if name == 'browser_snapshot' else 'ok'

    adapter.browser.call = browser_call
    with pytest.raises(RuntimeError, match='attachment_page_mismatch'):
        await adapter._discover_visible_attachment_candidates(bundle)
    assert adapter._bundles[bundle.name].source_data['attachments'] == bundle.source_data['attachments']
    await adapter.close()


@pytest.mark.asyncio
async def test_reregistration_preserves_verified_file_then_invalidates_changed_hash(tmp_path):
    adapter = make_adapter(tmp_path)
    payload = b'correct binary'
    sha = hashlib.sha256(payload).hexdigest()
    url = 'https://platform.test/api/v1/competitions/c/challenges/one/attachments/a1'
    initial = {'id': 'a1', 'name': 'binary', 'byteLength': len(payload),
               'sha256': sha, 'source_url': url}
    original = adapter.register_challenge(challenge('one', initial))
    staging = adapter.browser.download_dir / 'verified.bin'
    staging.parent.mkdir(parents=True)
    staging.write_bytes(payload)
    candidate = (await adapter.list_attachment_candidates('one'))[0]
    await adapter._archive_downloaded_attachment(original, candidate, staging)
    repeated = adapter.register_challenge(challenge('one', {'name': 'binary'}))
    assert repeated.state.value == 'ready'
    assert repeated.files == ['distfiles/binary']
    assert repeated.source_data['attachments'][0]['id'] == 'a1'
    assert adapter.state.list_attachments('one')[0]['state'] == 'ready'
    changed = adapter.register_challenge(challenge('one', {
        **initial, 'sha256': hashlib.sha256(b'different').hexdigest(),
    }))
    assert changed.state.value == 'waiting_for_package'
    assert changed.files == []
    row = adapter.state.list_attachments('one')[0]
    assert row['state'] != 'ready' and row['relative_path'] == ''
    assert (tmp_path / 'challenges' / 'one' / 'distfiles' / 'binary').read_bytes() == payload
    await adapter.close()


@pytest.mark.asyncio
async def test_repeated_registration_recovers_ready_row_when_metadata_files_were_reset(tmp_path):
    adapter = make_adapter(tmp_path)
    payload = b'verified'
    sha = hashlib.sha256(payload).hexdigest()
    item = {'id': 'a1', 'name': 'binary', 'byteLength': len(payload), 'sha256': sha,
            'source_url': 'https://platform.test/api/v1/competitions/c/challenges/one/attachments/a1'}
    bundle = adapter.register_challenge(challenge('one', item))
    candidate = (await adapter.list_attachment_candidates('one'))[0]
    staging = adapter.browser.download_dir / 'binary'
    staging.parent.mkdir(parents=True)
    staging.write_bytes(payload)
    await adapter._archive_downloaded_attachment(bundle, candidate, staging)
    # Simulate a prior coordinator write that omitted the files list but left
    # the verified attachment row and artifact intact.
    current = adapter._bundles['one']
    adapter._write_bundle(current.model_copy(update={'files': [], 'state': 'waiting_for_decision'}))
    restored = adapter.register_challenge(challenge('one', {'name': 'binary'}))
    assert restored.state.value == 'ready'
    assert restored.files == ['distfiles/binary']
    assert adapter.state.list_attachments('one')[0]['state'] == 'ready'
    await adapter.close()


@pytest.mark.asyncio
async def test_changed_registration_during_download_does_not_archive_stale_candidate(tmp_path):
    adapter = make_adapter(tmp_path)
    payload = b'first'
    item = {'id': 'a1', 'name': 'binary', 'byteLength': len(payload),
            'sha256': hashlib.sha256(payload).hexdigest(),
            'source_url': 'https://platform.test/api/v1/competitions/c/challenges/one/attachments/a1'}
    bundle = adapter.register_challenge(challenge('one', item))
    candidate = (await adapter.list_attachment_candidates('one'))[0]
    staging = adapter.browser.download_dir / 'binary'
    staging.parent.mkdir(parents=True)
    staging.write_bytes(payload)
    adapter.register_challenge(challenge('one', {**item,
        'sha256': hashlib.sha256(b'second').hexdigest()}))
    with pytest.raises(RuntimeError, match='attachment_identity_changed'):
        await adapter._archive_downloaded_attachment(bundle, candidate, staging)
    assert not (tmp_path / 'challenges' / 'one' / 'distfiles' / 'binary').exists()
    await adapter.close()
