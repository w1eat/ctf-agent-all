#!/usr/bin/env python3
"""Decode MSKLC keyboard-layout (.klc) DEADKEY chain that composes the sun U+2600.
The chain of dead-key compositions spells out the flag the user types."""
data = open('/challenge/distfiles/boardwriter.klc','rb').read().decode('utf-16')
dead, cur = {}, None
for ln in data.splitlines():
    s = ln.strip()
    if s.startswith('DEADKEY'):
        cur = int(s.split()[1],16); dead[cur] = {}
    elif cur is not None and s and s != 'ENDKBD':
        p = s.split()
        if len(p) == 2:
            dead[cur][int(p[0],16)] = int(p[1].rstrip('@'),16)

cur, typed = 0x0060, '`'
while cur in dead:
    base, res = next(iter(dead[cur].items()))
    typed += chr(base); cur = res
print("typed to produce U+%04X: %r" % (cur, typed))
print("readable flag: %s" % typed.replace('`',''))
