"""Re-run the three maintained writeup examples in fresh project Docker sandboxes.

This saves evidence without calling a model, submitting flags, or rewriting a WP.
Run with: python -B tools/verify_writeup_docker.py
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shlex
import sys
import textwrap
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.sandbox import DockerSandbox  # noqa: E402
from backend.writeup_evidence import (  # noqa: E402
    EvidenceRecorder,
    atomic_write,
    capture_artifact_files,
    load_command_evidence,
)

EXAMPLES = ("you-cut-me-off", "welcome-call!", "intmod")


def python_command(source: str) -> str:
    return "python3 -B - <<'WP_VERIFY_PY'\n" + textwrap.dedent(source).strip() + "\nWP_VERIFY_PY"


ENVIRONMENT = python_command("""
    import importlib.metadata
    import json
    import platform
    import zlib
    print(json.dumps({
        'system': platform.system(), 'machine': platform.machine(),
        'python': platform.python_version(), 'zlib': zlib.ZLIB_RUNTIME_VERSION,
        'scapy': importlib.metadata.version('scapy'),
        'pillow': importlib.metadata.version('pillow'),
    }, indent=2))
""")

PNG_CHECK = python_command("""
    import hashlib
    import json
    from pathlib import Path
    from PIL import Image
    root = Path('/challenge/workspace')
    original = Image.open('/challenge/distfiles/hereyougo.png').convert('RGBA')
    full = Image.open(root / 'full.png').convert('RGBA')
    visible = Image.open(root / 'original_view.png').convert('RGBA')
    hidden = Image.open(root / 'hidden_rows.png').convert('RGBA')
    enlarged = Image.open(root / 'hidden_rows_4x.png').convert('RGBA')
    assert original.size == visible.size == (492, 382)
    assert full.size == (492, 418) and hidden.size == (492, 36)
    assert enlarged.size == (1968, 144)
    assert original.tobytes() == visible.tobytes() == full.crop((0, 0, 492, 382)).tobytes()
    assert hidden.tobytes() == full.crop((0, 382, 492, 418)).tobytes()
    assert enlarged.tobytes() == hidden.resize((1968, 144), Image.Resampling.NEAREST).tobytes()
    for name in ('original_view.png', 'full.png', 'hidden_rows.png', 'hidden_rows_4x.png'):
        current = Image.open(root / name).convert('RGBA')
        previous = Image.open(root / 'reference' / name).convert('RGBA')
        assert current.size == previous.size and current.tobytes() == previous.tobytes(), name
    report = {
        'visible_pixels_match_original': True, 'hidden_pixels_match_full_crop': True,
        'enlargement_matches_nearest_neighbor': True,
        'all_four_images_match_previous_rgba_pixels': True,
        'full_rgba_sha256': hashlib.sha256(full.tobytes()).hexdigest(),
        'full_size': list(full.size), 'hidden_rows': 36,
        'flag_recognition': 'not performed; image still requires visual verification',
    }
    text = json.dumps(report, indent=2) + '\\n'
    (root / 'pixel-verification.json').write_text(text, encoding='utf-8')
    print(text, end='')
""")

AUDIO_CHECK = python_command("""
    import audioop
    import importlib.util
    import json
    import struct
    import wave
    from pathlib import Path
    root = Path('/challenge/workspace')
    spec = importlib.util.spec_from_file_location('recover_audio', root / 'exp/recover_audio.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for value in range(256):
        assert module.mulaw_sample(value) == struct.unpack('<h', audioop.ulaw2lin(bytes([value]), 2))[0]
    def samples(name):
        with wave.open(str(root / name), 'rb') as wav:
            assert wav.getnchannels() == 1 and wav.getsampwidth() == 2 and wav.getframerate() == 8000
            assert wav.getnframes() == 124480
            data = wav.readframes(wav.getnframes())
        values = struct.unpack('<124480h', data)
        return values
    recorded, reversed_samples = samples('recorded.wav'), samples('reversed.wav')
    assert reversed_samples == recorded[::-1]
    report = {
        'all_256_mulaw_values_match_audioop': True,
        'pcm_sample_reversal_matches': True, 'samples': len(recorded),
        'duration_seconds': len(recorded) / 8000,
        'speech_recognition': 'not performed; audio still requires listening verification',
    }
    text = json.dumps(report, indent=2) + '\\n'
    (root / 'audio-verification.json').write_text(text, encoding='utf-8')
    print(text, end='')
""")

ELF_CHECK = python_command("""
    import hashlib
    import json
    import shutil
    import subprocess
    from pathlib import Path
    root = Path('/challenge/workspace')
    binary = root / 'intmod'
    shutil.copyfile('/challenge/distfiles/intmod', binary)
    binary.chmod(0o755)
    solver = subprocess.run(['python3', '-B', str(root / 'exp/solve_intmod.py')], capture_output=True, check=True)
    candidate = solver.stdout.strip()
    assert len(candidate) == 33 and candidate.startswith(b'sun{') and candidate.endswith(b'}')
    wrong = bytearray(candidate)
    wrong[5] ^= 1
    def run(value):
        proc = subprocess.run([str(binary)], input=value + b'\\n', capture_output=True, timeout=30)
        return {'exit_code': proc.returncode, 'stdout': proc.stdout.decode('utf-8', errors='replace'),
                'stderr': proc.stderr.decode('utf-8', errors='replace')}
    accepted, rejected = run(candidate), run(bytes(wrong))
    assert accepted['exit_code'] == 0 and 'Correct' in accepted['stdout'], accepted
    assert 'Correct' not in rejected['stdout'] and rejected['stdout'].strip() == 'Nope', rejected
    report = {
        'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'input_source': 'stdout of freshly executed solve_intmod.py',
        'candidate': candidate.decode('ascii'), 'candidate_bytes': len(candidate),
        'positive_control': accepted, 'negative_control': rejected,
        'original_elf_accepts_candidate': True, 'mutated_same_length_input_rejected': True,
    }
    text = json.dumps(report, indent=2) + '\\n'
    (root / 'elf-verification.json').write_text(text, encoding='utf-8')
    print(text, end='')
""")

TRACE_CHECK = python_command("""
    import json
    import pickle
    from pathlib import Path
    sequences = pickle.loads(Path('/tmp/seqs.pkl').read_bytes())
    assert len(sequences) == 4 and all(sequences)
    report = {'input_vectors': 4, 'state_counts': [len(seq) for seq in sequences],
              'first_rips': [[hex(row[0]) for row in seq[:6]] for seq in sequences],
              'limitations': 'State capture only; MICRO inference and D matrix extraction are not reconstructed.'}
    root = Path('/challenge/workspace')
    (root / 'trace-states.json').write_text(json.dumps(sequences) + '\\n', encoding='utf-8')
    text = json.dumps(report, indent=2) + '\\n'
    (root / 'trace-verification.json').write_text(text, encoding='utf-8')
    print(text, end='')
""")


async def verify_example(name: str, image: str) -> dict:
    challenge = ROOT / "challenges" / name
    state = json.loads((challenge / "solution/manifest.json").read_text(encoding="utf-8"))
    record = next(row for row in state["records"] if row["key"] == state["current_key"])
    assert hashlib.sha256((challenge / "writeup.md").read_bytes()).hexdigest() == record["writeup_sha256"], "Preserve manual WP edits"
    identities = {**record["exp_sha256"], **{row["path"]: row["sha256"] for row in record["inputs"]}}
    for relative, digest in identities.items():
        assert hashlib.sha256((challenge / relative).read_bytes()).hexdigest() == digest, relative
    recorder = EvidenceRecorder(challenge, "docker-writeup-verification", record["run_id"], provenance="docker_replay")
    sandbox = DockerSandbox(image=image, challenge_dir=str(challenge), memory_limit="2g")
    report = {"challenge": name, "started_at": datetime.now(UTC).isoformat(), "image": image,
              "record_key": record["key"], "run_id": record["run_id"], "status": "running",
              "baseline_writeup_sha256": record["writeup_sha256"], "input_and_exp_sha256": identities,
              "evidence_logs": [recorder.relative_path], "executions": [], "artifacts": []}
    step = 0

    async def execute(label: str, command: str, timeout: int = 60):
        nonlocal step
        step += 1
        recorder.call("docker_bash", {"command": command, "cwd": "/challenge"}, step)
        result = await sandbox.exec(command, timeout_s=timeout)
        recorder.result("docker_bash", asdict(result), step)
        report["executions"].append({"label": label, "evidence_id": f"command-{recorder.token[:12]}-{step}",
                                     "command": command, **asdict(result)})
        print(f"{name}: {label}: exit {result.exit_code}", flush=True)
        if result.exit_code != 0:
            raise RuntimeError(f"{label}: {result.stderr or result.stdout}")
        return result

    try:
        await asyncio.wait_for(sandbox.start(), timeout=90)
        report["container_id"] = sandbox.container_id
        container = await sandbox._container.show()
        report["image_id"] = container["Image"]
        report["environment"] = json.loads((await execute("environment", ENVIRONMENT)).stdout)
        folders = {str(Path(relative).parent.as_posix()) for relative in record["exp_sha256"]}
        if name == "you-cut-me-off":
            folders.add("reference")
        await execute("prepare_workspace", "mkdir -p " + " ".join(shlex.quote("/challenge/workspace/" + folder) for folder in sorted(folders)))
        for relative in record["exp_sha256"]:
            await sandbox.write_file("/challenge/workspace/" + relative, (challenge / relative).read_bytes())
        if name == "you-cut-me-off":
            for artifact in record["saved_artifacts"]:
                if artifact["media_type"] == "image/png":
                    content = (challenge / artifact["path"]).read_bytes()
                    assert hashlib.sha256(content).hexdigest() == artifact["sha256"]
                    await sandbox.write_file("/challenge/workspace/reference/" + Path(artifact["path"]).name, content)
        paths = {("/challenge/" + relative if relative.startswith("distfiles/") else "/challenge/workspace/" + relative): digest
                 for relative, digest in identities.items()}
        identity_command = python_command("import hashlib, json\nfrom pathlib import Path\nexpected = " + repr(paths) + "\n"
                                          "actual = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in expected}\n"
                                          "assert actual == expected\nprint(json.dumps(actual, indent=2))")
        await execute("verify_input_and_exp_identity", identity_command)
        if name == "you-cut-me-off":
            await execute("inspect_png", "python3 -B /challenge/workspace/exp/solve.py --inspect-only")
            result = await execute("main_exp", "python3 -B /challenge/workspace/exp/solve.py --output-dir /challenge/workspace")
            generated = json.loads(result.stdout)
            assert generated["stored_height"] == 418 and generated["hidden_rows"] == 36
            report["independent_checks"] = json.loads((await execute("pixel_cross_check", PNG_CHECK)).stdout)
            artifact_names = ["original_view.png", "full.png", "hidden_rows.png", "hidden_rows_4x.png", "report.json", "pixel-verification.json"]
        elif name == "welcome-call!":
            result = await execute("main_exp", "python3 -B /challenge/workspace/exp/recover_audio.py --output-dir /challenge/workspace")
            generated = json.loads(result.stdout)
            assert generated["rtp_packets"] == 778 and generated["duration_seconds"] == 15.56
            report["independent_checks"] = json.loads((await execute("audio_cross_check", AUDIO_CHECK)).stdout)
            artifact_names = ["recorded.wav", "reversed.wav", "report.json", "audio-verification.json"]
        else:
            result = await execute("main_exp", "python3 -B /challenge/workspace/exp/solve_intmod.py")
            assert result.stdout.strip() == record["flag"]
            await execute("transform_cross_check", "python3 -B /challenge/workspace/exp/check_transform.py --output-dir /challenge/workspace")
            report["independent_checks"] = json.loads((await execute("original_elf_controls", ELF_CHECK)).stdout)
            trace_command = ("mkdir -p /challenge/workspace/trace-work && cp /challenge/distfiles/intmod /challenge/workspace/trace-work/intmod && "
                             "chmod 755 /challenge/workspace/trace-work/intmod && "
                             "gcc /challenge/workspace/exp/tracer.c -o /challenge/workspace/trace-work/tracer && "
                             "cd /challenge/workspace/trace-work && python3 -B ../exp/runseq.py")
            await execute("ptrace_state_capture", trace_command, timeout=120)
            report["trace_checks"] = json.loads((await execute("trace_summary", TRACE_CHECK)).stdout)
            artifact_names = ["transform-report.json", "elf-verification.json", "trace-verification.json", "trace-states.json"]
        await execute("verify_final_input_and_exp_identity", identity_command)
        artifacts, issues = capture_artifact_files(challenge, sandbox, artifact_names, source="docker-writeup-verification",
                                                    run_id=record["run_id"], stage="replay")
        report["artifacts"], report["artifact_issues"] = artifacts, issues
        if issues or len(artifacts) != len(artifact_names):
            raise RuntimeError(f"Artifact capture failed: {issues}")
        previous = {Path(row["path"]).name: row for row in record["saved_artifacts"]}
        comparisons = []
        for artifact in artifacts:
            filename = Path(artifact["path"]).name
            if filename not in previous:
                continue
            old = previous[filename]
            same = artifact["sha256"] == old["sha256"]
            row = {"name": filename, "previous_sha256": old["sha256"], "docker_sha256": artifact["sha256"], "byte_identical": same}
            if artifact["media_type"] == "application/json":
                old_data = json.loads((challenge / old["path"]).read_text(encoding="utf-8"))
                new_data = json.loads((challenge / artifact["path"]).read_text(encoding="utf-8"))
                row["json_identical"] = old_data == new_data
                if name == "you-cut-me-off":
                    row["json_equal_except_png_compression_hashes"] = (
                        old_data.keys() == new_data.keys()
                        and old_data["outputs"].keys() == new_data["outputs"].keys()
                        and {k: v for k, v in old_data.items() if k != "outputs"} == {k: v for k, v in new_data.items() if k != "outputs"}
                    )
                    assert row["json_equal_except_png_compression_hashes"], filename
                else:
                    assert row["json_identical"], filename
            elif artifact["media_type"].startswith("image/"):
                row["rgba_pixels_identical"] = report["independent_checks"]["all_four_images_match_previous_rgba_pixels"]
                assert row["rgba_pixels_identical"], filename
            elif artifact["media_type"].startswith("audio/"):
                assert same, f"Investigate media bytes before updating the writeup: {filename}"
            comparisons.append(row)
        report["artifact_comparison"] = comparisons
        rows = load_command_evidence(challenge, [recorder.relative_path], run_id=record["run_id"])
        assert len(rows) == len(report["executions"])
        report["status"] = "passed"
    except Exception as exc:
        report["status"], report["error"] = "failed", str(exc)
        print(f"{name}: FAILED: {exc}", flush=True)
    finally:
        await asyncio.wait_for(sandbox.stop(), timeout=60)
        report["finished_at"] = datetime.now(UTC).isoformat()
        path = challenge / "solution" / f"docker-reproduction-{datetime.now(UTC):%Y%m%d}.json"
        if path.is_file():
            previous = json.loads(path.read_text(encoding="utf-8"))
            history = previous.pop("verification_history", [])
            report["verification_history"] = [*history, previous]
        atomic_write(path, (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return report


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="ctf-sandbox:latest")
    parser.add_argument("--challenge", action="append", choices=EXAMPLES)
    args = parser.parse_args()
    results = await asyncio.gather(*(verify_example(name, args.image) for name in args.challenge or EXAMPLES))
    print(json.dumps({row["challenge"]: row["status"] for row in results}, indent=2))
    return int(any(row["status"] != "passed" for row in results))


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
