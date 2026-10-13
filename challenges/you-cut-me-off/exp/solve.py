#!/usr/bin/env python3
# Recover hidden rows of a PNG whose IHDR height was truncated ("you cut me off").
import zlib, struct
import numpy as np
from PIL import Image

SRC = '/challenge/distfiles/hereyougo.png'
W = 492                     # width from IHDR
DECLARED_H = 382            # height from IHDR (lie)
STRIDE = W * 4 + 1          # RGBA + 1 filter byte

# 1) collect all IDAT data
d = open(SRC, 'rb').read()
pos = 8
idat = b''
while pos < len(d):
    ln = struct.unpack('>I', d[pos:pos+4])[0]
    typ = d[pos+4:pos+8]
    if typ == b'IDAT':
        idat += d[pos+8:pos+8+ln]
    pos += 12 + ln

raw = zlib.decompress(idat)
H = len(raw) // STRIDE           # true height = 418
print('declared height:', DECLARED_H, ' true height:', H)

# 2) unfilter
out = np.zeros((H, W*4), dtype=np.uint8)
prev = np.zeros(W*4, dtype=np.uint8)
p = 0
for y in range(H):
    f = raw[p]; p += 1
    line = np.frombuffer(raw[p:p+W*4], dtype=np.uint8).copy(); p += W*4
    if f == 0:
        cur = line
    elif f == 1:
        cur = line.copy()
        for i in range(4, len(cur)):
            cur[i] = (cur[i] + cur[i-4]) & 255
    elif f == 2:
        cur = ((line.astype(int) + prev.astype(int)) & 255).astype(np.uint8)
    elif f == 3:
        cur = line.copy().astype(int)
        for i in range(len(cur)):
            a = cur[i-4] if i >= 4 else 0
            cur[i] = (line[i] + ((a + prev[i]) // 2)) & 255
        cur = cur.astype(np.uint8)
    elif f == 4:
        cur = line.copy().astype(int)
        for i in range(len(cur)):
            a = cur[i-4] if i >= 4 else 0
            b = prev[i]
            c = prev[i-4] if i >= 4 else 0
            pp = a + b - c
            pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
            pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            cur[i] = (line[i] + pr) & 255
        cur = cur.astype(np.uint8)
    out[y] = cur
    prev = cur

img = Image.fromarray(out.reshape(H, W, 4), 'RGBA')
img.save('/challenge/workspace/full.png')
img.crop((0, DECLARED_H, W, H)).resize((W*2, (H-DECLARED_H)*2), Image.LANCZOS)\
   .save('/challenge/workspace/hidden_rows.png')
print('hidden rows rendered -> hidden_rows.png ; flag shown in bottom chat box')
