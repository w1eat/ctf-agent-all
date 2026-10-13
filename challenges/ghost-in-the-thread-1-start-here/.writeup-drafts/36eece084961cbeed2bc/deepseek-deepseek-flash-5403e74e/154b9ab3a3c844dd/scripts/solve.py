#!/usr/bin/env python3
"""
ghost in the thread - 1 - start here
Recovered from the SunshineCTF forensic appliance (GhostInTheThread.ova).

Chain:
  1. sunchan.html shows thread /po/ with suspicious upload referenced by post
     No.184726 ("folding-guide.pdf"): unlike other attachments it is
     "stored on the server" and its preview is blank.
  2. The disk image /srv/sunchan/uploads/po/184726.pdf is actually a
     PostScript file (GS-disguised). Its %% comments carry stage-2 metadata:
        %%Document-ID: po-184726
        %%Stage2-URL-Base64: aHR0cDovL2Fzc2V0cy5zdW5jaGFuLmludmFsaWQvcmVzb3VyY2VzL2dzLXJlc291cmNlLmJpbg==
             -> http://assets.sunchan.invalid/resources/gs-resource.bin
        %%Stage2-Destination: /var/tmp/sunchan-downloads/gs-resource.bin
        %%Stage2-SHA256: 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500
  3. The dropped /var/tmp/sunchan-downloads/gs-resource.bin is a tiny
     statically-linked ELF ("SunHash proof-of-work benchmark simulator").
     It reads a 9-char "Document-ID", checks its FNV-1a hash and then
     emits 30 bytes = input[i%9] ^ key[i] ^ 0x5a.
     key = 59 40 19 10 16 08 1a 37 04 4b 56 1c 0e 06 31 0f
           11 33 45 53 11 09 0d 0f 1f 0c 09 58 46 0a
     The only input satisfying eax==0xdac3d58d is "po-184726".
"""
key = bytes([0x59,0x40,0x19,0x10,0x16,0x08,0x1a,0x37,0x04,0x4b,0x56,0x1c,
             0x0e,0x06,0x31,0x0f,0x11,0x33,0x45,0x53,0x11,0x09,0x0d,0x0f,
             0x1f,0x0c,0x09,0x58,0x46,0x0a])
inp = b'po-184726'

def fnv_check(s: bytes) -> bool:
    ecx = 0x811c9dc5
    eax = 0
    for i in range(9):
        eax = (s[i] ^ ecx) & 0xffffffff
        ecx = (eax * 0x1000193) & 0xffffffff
    return eax == 0xdac3d58d

assert fnv_check(inp)
flag = bytes((inp[i % 9] ^ key[i] ^ 0x5a) for i in range(30))
print(flag.decode())
