#!/usr/bin/env python3
"""Offline, task-level checks for every advertised CTF category."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"


def run(*args: str, timeout: int = 120, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=timeout, cwd=cwd, check=False)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(args)} exited {proc.returncode}: {proc.stderr[-1600:]}")
    return proc.stdout + proc.stderr


def check_web_and_osint(root: Path) -> dict:
    from playwright.sync_api import sync_playwright

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            page = b"<html><body><div id='flag'></div><script>document.getElementById('flag').textContent='CTF{browser-js}'</script></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *_: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    screenshot = root / "browser.png"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}/")
            assert page.locator("#flag").inner_text() == "CTF{browser-js}"
            page.screenshot(path=str(screenshot))
            browser.close()
        assert screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    finally:
        server.shutdown()
        server.server_close()
    return {"web": "JavaScript DOM and PNG screenshot", "osint": "headless Chromium"}


def compile_elf(root: Path) -> Path:
    source = root / "fixture.c"
    source.write_text('#include <stdio.h>\nint main(void) { puts("CTF{elf}"); return 0; }\n')
    for bits in (32, 64):
        binary = root / f"fixture{bits}"
        run("gcc", f"-m{bits}", "-g", "-O0", str(source), "-o", str(binary))
        assert "CTF{elf}" in run(str(binary))
        debug = run("gdb", "-nx", "-batch", "-ex", f"file {binary}",
                    "-ex", "break main", "-ex", "run", "-ex", "disassemble main")
        assert "main" in debug and "Breakpoint" in debug
    for qemu in ("qemu-arm", "qemu-mips"):
        assert "usage" in run(qemu, "-h").lower()
    return root / "fixture64"


def check_reverse(binary: Path, root: Path) -> str:
    import pefile

    assert '21.' in run("java", "-version")
    assert '21.' in run("javac", "-version")
    pe_fixture = Path("/opt/ghidra/docs/GhidraClass/ExerciseFiles/WinhelloCPP/WinHelloCPP.exe")
    pe = pefile.PE(str(pe_fixture), fast_load=True)
    assert pe.DOS_HEADER.e_magic == 0x5A4D
    assert pe.FILE_HEADER.NumberOfSections > 0
    # analyzeHeadless exports decompiled C through Ghidra's bundled script.
    script_dir = root / "ghidra_scripts"
    script_dir.mkdir()
    (script_dir / "DecompileFixture.java").write_text(
        'import ghidra.app.script.GhidraScript;\n'
        'import ghidra.app.decompiler.DecompInterface;\n'
        'import ghidra.app.decompiler.DecompileResults;\n'
        'public class DecompileFixture extends GhidraScript {\n'
        '  public void run() throws Exception {\n'
        '    DecompInterface d = new DecompInterface();\n'
        '    d.openProgram(currentProgram);\n'
        '    var f = getGlobalFunctions("main").get(0);\n'
        '    DecompileResults r = d.decompileFunction(f, 60, monitor);\n'
        '    if (!r.decompileCompleted()) throw new Exception("decompilation failed");\n'
        '    println(r.getDecompiledFunction().getC());\n'
        '    d.dispose();\n'
        '  }\n'
        '}\n', encoding="utf-8")
    project_dir = root / "ghidra_project"
    project_dir.mkdir()
    output = run("ghidra-headless", str(project_dir), "smoke", "-import", str(binary),
                 "-scriptPath", str(script_dir), "-postScript", "DecompileFixture.java",
                 "-deleteProject", timeout=300)
    if "puts(" not in output and "CTF{elf}" not in output:
        raise RuntimeError("Ghidra did not output decompiled main(): " + output[-1000:])
    return "Ghidra headless decompiled an amd64 ELF; pefile parsed a Windows PE"


def check_crypto() -> str:
    output = run("sage", "-c", "M=matrix(ZZ,[[4,1],[1,3]]); print(M.LLL())", timeout=120)
    assert "[" in output and "]" in output
    from fpylll import IntegerMatrix, LLL

    matrix = IntegerMatrix.from_matrix([[4, 1], [1, 3]])
    LLL.reduction(matrix)
    assert matrix.nrows == 2
    assert "usage" in run("RsaCtfTool", "--help").lower()
    assert "usage" in run("cado-nfs", "--help", timeout=120).lower()
    assert "usage" in run("flatter", "-h").lower()
    return "SageMath/fpylll LLL; RSA, CADO-NFS and flatter entry points"


def check_forensics(root: Path) -> str:
    from scapy.all import IP, Raw, TCP, wrpcap

    pcap = root / "fixture.pcap"
    wrpcap(str(pcap), [IP(dst="198.51.100.1") / TCP(dport=80) / Raw(load=b"CTF{pcap}")])
    output = run("tshark", "-r", str(pcap), "-Y", "tcp", "-T", "fields", "-e", "tcp.payload")
    assert b"CTF{pcap}".hex() in output
    return "Scapy PCAP and tshark TCP payload filter"


def check_stego(root: Path) -> str:
    from PIL import Image

    payload = b"CTF{png-lsb}\x00"
    bits = [int(bit) for byte in payload for bit in f"{byte:08b}"]
    image = Image.new("RGB", (16, 16), (128, 128, 128))
    pixels = image.load()
    for index, bit in enumerate(bits):
        x, y = index % 16, index // 16
        pixels[x, y] = (128 | bit, 128, 128)
    png = root / "lsb.png"
    image.save(png)
    run("pngcheck", str(png))
    output = run("zsteg", "-E", "b1,r,lsb,xy", str(png))
    assert "CTF{png-lsb}" in output
    return "PNG validation and LSB extraction"


def check_misc(root: Path) -> str:
    from zipfile import ZipFile

    archive = root / "sample.zip"
    with ZipFile(archive, "w") as zipped:
        zipped.writestr("flag.txt", "CTF{archive}")
    output_dir = root / "archive"
    output_dir.mkdir()
    run("7z", "x", str(archive), f"-o{output_dir}")
    assert (output_dir / "flag.txt").read_text() == "CTF{archive}"
    assert "chi_sim" in run("tesseract", "--list-langs")
    assert "eng" in run("tesseract", "--list-langs")
    assert "cpu" in run("hashcat", "-I", timeout=120).lower()
    run("john", "--test=1", timeout=60)
    return "7z extraction, English/Chinese OCR and CPU password tools"


def check_mobile(root: Path) -> str:
    from androguard.core.apk import APK

    apk = FIXTURES / "TestActivity.apk"
    if not apk.is_file():
        raise RuntimeError("offline TestActivity.apk fixture missing")
    package = APK(str(apk)).get_package()
    assert package
    jadx_dir = root / "jadx"
    apktool_dir = root / "apktool"
    run("jadx", "-d", str(jadx_dir), str(apk), timeout=180)
    run("apktool", "d", "-f", "-o", str(apktool_dir), str(apk), timeout=180)
    assert (apktool_dir / "AndroidManifest.xml").is_file()
    assert any(jadx_dir.rglob("*.java"))
    assert "Android Debug Bridge" in run("adb", "version")
    assert run("frida", "--version").strip()
    return f"Androguard, JADX and Apktool parsed {package}"


def check_blockchain(root: Path) -> str:
    assert "forge" in run("forge", "--version").lower()
    assert "cast" in run("cast", "--version").lower()
    source = root / "Counter.sol"
    source.write_text("pragma solidity ^0.8.26; contract Counter { uint public n; function inc() public { n++; } }\n")
    output = run("solc", "--bin", str(source), timeout=90)
    assert "Binary:" in output
    analysis = run("slither", str(source), "--solc", "solc",
                   "--print", "contract-summary", timeout=150)
    assert "Counter" in analysis
    node = subprocess.Popen(["anvil", "--host", "127.0.0.1", "--port", "18545", "--silent"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        from web3 import Web3

        rpc = Web3(Web3.HTTPProvider("http://127.0.0.1:18545", request_kwargs={"timeout": 2}))
        for _ in range(50):
            if node.poll() is not None:
                raise RuntimeError(f"anvil exited early: {node.stderr.read()[-1000:]}")
            if rpc.is_connected():
                break
            time.sleep(0.2)
        assert rpc.is_connected()
        assert rpc.eth.chain_id > 0
    finally:
        node.terminate()
        try:
            node.wait(timeout=10)
        except subprocess.TimeoutExpired:
            node.kill()
            node.wait()
    return "solc compilation, Slither analysis and Anvil RPC"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results: dict[str, dict] = {}

    def check(name: str, func) -> None:
        try:
            detail = func()
            results[name] = {"ok": True, "detail": detail}
        except Exception as exc:
            results[name] = {"ok": False, "error": str(exc)}

    with tempfile.TemporaryDirectory(prefix="ctf-smoke-") as directory:
        root = Path(directory)
        try:
            browser_details = check_web_and_osint(root)
            for category, detail in browser_details.items():
                results[category] = {"ok": True, "detail": detail}
        except Exception as exc:
            for category in ("web", "osint"):
                results[category] = {"ok": False, "error": str(exc)}
        check("pwn", lambda: "amd64/i386 execution and GDB; ARM/MIPS QEMU entry points" if compile_elf(root) else "")
        if (root / "fixture64").exists():
            check("reverse", lambda: check_reverse(root / "fixture64", root))
        else:
            results["reverse"] = {"ok": False, "error": "ELF fixture unavailable"}
        check("crypto", check_crypto)
        check("forensics", lambda: check_forensics(root))
        check("stego", lambda: check_stego(root))
        check("misc", lambda: check_misc(root))
        check("mobile", lambda: check_mobile(root))
        check("blockchain", lambda: check_blockchain(root))
    report = {"ok": all(item["ok"] for item in results.values()), "categories": results}
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        for category, status in results.items():
            print(f"{category}: {status.get('detail') if status['ok'] else status['error']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
