#!/usr/bin/env python3
# Solver for SunshineCTF 2026 "IntMod" (RE, 483).
#
# The binary is a signal/ucontext-based VM.  Its "hash" is
#   h = sum_{k} Dbyte[k] * (seed & 0xffff)^k  (mod 65521)
# where Dbyte are the 40 little-endian bytes of the 5 VM registers r0..r4.
# The 126 VM instructions transform the 33-byte input into r0..r4 (= digest D),
# then 26 groups of (op5 seed / op6 target) verify  (h(seed) - seed_hi) % 65521 == target.
# Because the hash is a *linear* function of D mod 65521 we can solve for D,
# and because each VM instruction is invertible we can invert the digest back to input.
#
# This script embeds:
#   - the exact 90 micro-ops (exec op + dispatch "extra" op) recovered via ptrace
#   - the target digest D (solution of the linear system over GF(65521))
import struct
M = (1 << 64) - 1

def rol(v, c):
    c %= 64
    return ((v << c) | (v >> (64 - c))) & M if c else v & M

def ror(v, c):
    c %= 64
    return ((v >> c) | (v << (64 - c))) & M if c else v & M

# --- micro-op sequence (type, args...) as recovered with the ptrace tracer ---
MICRO = [
('addrol', 0, 1, 7),
('xorrol', 2, 0, 0),
('mul', 3, 11400714785074694791),
('rol', 4, 19),
('swap', 1, 3),
('addrol', 3, 0, 13),
('xorrol', 4, 3, 0),
('mul', 1, 14029467366897019727),
('rol', 2, 31),
('swap', 0, 1),
('addrol', 1, 4, 29),
('xorrol', 3, 1, 0),
('mul', 2, 1609587929392839161),
('rol', 0, 11),
('swap', 2, 4),
('addrol', 4, 2, 43),
('xorrol', 0, 4, 0),
('mul', 3, 9650029242287828579),
('rol', 1, 23),
('swap', 2, 3),
('addrol', 2, 3, 17),
('xorrol', 1, 2, 0),
('mul', 0, 2870177450012600261),
('rol', 4, 37),
('swap', 0, 3),
('addrol', 0, 2, 5),
('xorrol', 4, 0, 0),
('mul', 1, 10723151780598845931),
('rol', 3, 47),
('swap', 1, 2),
('addrol', 4, 1, 41),
('xorrol', 3, 4, 0),
('mul', 0, 13787848793156543929),
('rol', 2, 9),
('swap', 0, 1),
('addrol', 2, 0, 23),
('xorrol', 1, 2, 0),
('mul', 4, 15485907386658061715),
('rol', 3, 53),
('swap', 0, 4),
('addrol', 1, 3, 31),
('xorrol', 0, 1, 0),
('mul', 4, 11562461410679940143),
('rol', 2, 7),
('swap', 3, 4),
('addrol', 3, 4, 11),
('xorrol', 2, 3, 0),
('mul', 1, 16646288086500911323),
('rol', 0, 39),
('swap', 1, 4),
('addrol', 0, 4, 37),
('xorrol', 3, 0, 0),
('mul', 2, 10285213230658275043),
('rol', 1, 17),
('swap', 2, 4),
('addrol', 2, 1, 19),
('xorrol', 4, 2, 0),
('mul', 3, 6384245875588680899),
('rol', 0, 43),
('swap', 1, 3),
('addrol', 4, 3, 47),
('xorrol', 1, 4, 0),
('mul', 0, 2129725606500045391),
('rol', 2, 13),
('swap', 0, 3),
('addrol', 1, 0, 3),
('xorrol', 2, 1, 0),
('mul', 4, 16952864883938283877),
('rol', 3, 29),
('swap', 0, 4),
('addrol', 3, 2, 53),
('xorrol', 0, 3, 0),
('mul', 1, 11376068507788127593),
('rol', 4, 21),
('swap', 1, 2),
('addrol', 0, 3, 27),
('xorrol', 2, 0, 0),
('mul', 4, 14320364442791297827),
('rol', 1, 49),
('swap', 3, 4),
('addrol', 4, 0, 9),
('xorrol', 3, 4, 0),
('mul', 1, 15802862336838869349),
('rol', 2, 35),
('swap', 0, 1),
('addrol', 2, 4, 45),
('xorrol', 1, 2, 0),
('mul', 3, 13537915256980136287),
('rol', 0, 15),
('swap', 3, 4)
]

# --- target digest D = r0..r4 after the 90 transform micro-ops ---
# Obtained by solving  sum_k Dbyte[k]*base^k == target + seed_hi  (mod 65521)
D = [0x7647653d32c8af6c, 0x8b335299eb07dda8, 0x82dd9502a3be9591,
     0xd66e926f06c4a36f, 0x77a194bf7b25dff2]

def inverse_transform(D):
    r = list(D)
    for op in reversed(MICRO):
        t = op[0]
        if t == 'addrol':
            a, b, c = op[1], op[2], op[3]
            r[a] = (r[a] - rol(r[b], c)) & M
        elif t == 'xorrol':
            a, b, c = op[1], op[2], op[3]
            r[a] ^= rol(r[b], c)
        elif t == 'rol':
            a, c = op[1], op[2]
            r[a] = ror(r[a], c)
        elif t == 'swap':
            a, b = op[1], op[2]
            r[a], r[b] = r[b], r[a]
        elif t == 'mul':
            a, K = op[1], op[2]
            r[a] = (r[a] * pow(K, -1, 1 << 64)) & M
    return r

if __name__ == '__main__':
    regs = inverse_transform(D)
    raw = b''.join(struct.pack('<Q', x) for x in regs)
    flag = raw[:33].decode()
    assert raw[33:40] == b'\x07' * 7, "padding check failed"
    print(flag)
