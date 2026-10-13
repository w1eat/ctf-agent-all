#!/usr/bin/env python3
import sys, socket, struct, time

DATA = open('/challenge/distfiles/code-breaker','rb').read()
T = DATA[0x2040:0x2140]
assert len(T) == 256

def rol8(b, n):
    b &= 0xff
    return ((b << n) | (b >> (8-n))) & 0xff

def key_schedule(R, B):
    buf = bytes(R) + bytes(B)
    S = bytearray(16)
    for o in range(4):
        for k in range(16):
            ia = (8*o + k) & 0x1f
            ib = (3*o + k)
            S[k] = rol8(T[(buf[ia] ^ S[k]) & 0xff] ^ buf[ib], 3)
    return bytes(S)

def vbytes(S):
    v = bytearray(16)
    for j in range(16):
        v[j] = T[S[j]] ^ S[(j+5) & 0xf]
    return bytes(v)

def keystream(S, counter, n):
    ks = bytearray(n)
    for i in range(n):
        ks[i] = T[(counter + i + S[i % 16]) & 0xff]
    return bytes(ks)

class Conn:
    def __init__(self, sock):
        self.s = sock
        self.cin = 0
        self.cout = 0
    def recvn(self, n):
        buf = b''
        while len(buf) < n:
            try:
                d = self.s.recv(n - len(buf))
            except AttributeError:
                d = self.s.recv(n - len(buf))
            if not d:
                raise EOFError('eof')
            buf += d
        return buf
    def send_raw(self, data):
        if hasattr(self.s, 'sendall'):
            self.s.sendall(data)
        else:
            self.s.send(data)
    def read_pkt(self):
        l = struct.unpack('>H', self.recvn(2))[0]
        return self.recvn(l)
    def send_pkt(self, data):
        self.send_raw(struct.pack('>H', len(data)) + data)
    # encrypted protocol helpers once S is known and counters set
    def send_enc(self, S, data):
        ks = keystream(S, self.cin, len(data))
        enc = bytes(data[i] ^ ks[i] for i in range(len(data)))
        self.cin += len(data)
        self.send_pkt(enc)
    def read_enc(self, S):
        resp = self.read_pkt()
        ks = keystream(S, self.cout, len(resp))
        self.cout += len(resp)
        return bytes(resp[i] ^ ks[i] for i in range(len(resp)))

def build_handshake(R, B=None):
    if B is None:
        B = bytes(range(16))
    S = key_schedule(R, B)
    p2 = b'\x02' + bytes(B)
    ks = keystream(S, 0, 17)
    plain3 = b'\x03' + vbytes(S)
    p3 = bytes(plain3[i] ^ ks[i] for i in range(17))
    return S, p2, p3

def connect(host=None, port=None):
    if host:
        s = socket.create_connection((host, port))
    else:
        from pwn import process
        s = process(["/challenge/workspace/run/ld-linux-x86-64.so.2","/challenge/workspace/run/code-breaker"])
    c = Conn(s)
    init = c.read_pkt()
    R = init[1:17]
    S, p2, p3 = build_handshake(R)
    c.send_pkt(p2)
    c.send_pkt(p3)
    # outbound counter 0 for the 2-byte handshake response
    c.cout = 0
    resp = c.read_enc(S)
    c.cout = 2   # consumed by the handshake response
    c.cin = 17   # consumed by packet3 decryption
    return c, S, resp

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else None
    c, S, hr = connect(host, port)
    print('handshake resp', hr.hex())
    # info command
    c.send_enc(S, b'\x16')
    dec = c.read_enc(S)
    print('info resp len', len(dec), dec[:4].hex())
    print(dec.hex())
