#!/usr/bin/env python3
"""
NAS coal (Forensics) - gem-collection.pptm

The .pptm (PowerPoint with macros) contains a VBA macro 'MediaCache.RefreshCache'
that builds a PowerShell -EncodedCommand from a hard-coded Base64 blob.

Analyse with olevba (or manually) -> decode the Base64 (UTF-16LE PowerShell) -> campaign.
"""
import base64, re, zipfile, io

path = "/challenge/distfiles/gem-collection.pptm"
z = zipfile.ZipFile(path)
data = z.read("ppt/vbaProject.bin")

# The Base64 blob is a long printable run inside the OLE stream
blobs = re.findall(rb"[A-Za-z0-9+/=]{100,}", data)
for b in blobs:
    dec = base64.b64decode(b).decode("utf-16-le", "replace")
    print(dec)
    m = re.search(r"sun\{[^}]+\}", dec)
    if m:
        print("FLAG:", m.group(0))
