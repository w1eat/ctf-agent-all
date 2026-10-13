"""Inspect what the runtime endpoint at 40537 actually speaks."""
import socket
import time

HOST, PORT = "noctf.fa1lsnow.com", 40537


def probe(label, send=None, wait=4.0):
    try:
        s = socket.create_connection((HOST, PORT), timeout=6)
    except Exception as exc:  # noqa: BLE001
        print(f"[{label}] connect failed: {exc}")
        return
    s.settimeout(0.5)
    if send:
        try:
            s.sendall(send)
        except Exception as exc:  # noqa: BLE001
            print(f"[{label}] send failed: {exc}")
    end = time.time() + wait
    out = b""
    while time.time() < end:
        try:
            d = s.recv(65536)
            if not d:
                out += b"<EOF>"
                break
            out += d
        except socket.timeout:
            continue
        except Exception as exc:  # noqa: BLE001
            out += f"<ERR {exc}>".encode()
            break
    print(f"[{label}] {out[:600]!r}")
    s.close()


if __name__ == "__main__":
    probe("silent-wait", None, 5.0)
    probe("http-get", b"GET / HTTP/1.0\r\nHost: x\r\n\r\n", 4.0)
    probe("newline", b"\n", 4.0)
    probe("hello", b"hello\n", 4.0)
