#!/usr/bin/env python3
"""Carrier program for THE FIRST LIGHT POST (news-image-20261123, akun4).

The artwork is a single PNG front page — light-grey paper, black ink,
burnt-orange accent — that compresses the whole of Monday 23 November
2026 into one image: a dozen numbered cards headed by the Hormuz
tankers, six day-defining numbers, a dotted map, a red date-check box
and thirty-one briefs. 43 stories, 7 regions, one day.

Drawing happened earlier, in the recorded build session (compose.py).
This file's only job at scoring time is delivery: copy entry.png from
beside this script into the output folder, byte for byte, after
checking the copy against the size and SHA-256 recorded below. It
imports nothing outside the standard library and never touches the
image's pixels, so two runs always produce the same file.
"""

import hashlib
import os
import sys

ARTWORK_BYTES = 117026
ARTWORK_SHA256 = "2b97bcaed6cb4173a2a8e9e2e55393ac89257b62f80a6ecf672c7fa164568908"
CEILING = 1048576  # 1 MiB, the gate's hard limit for this bounty
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_artwork(folder):
    path = os.path.join(folder, "entry.png")
    with open(path, "rb") as stream:
        return stream.read()


def check_artwork(blob):
    if len(blob) == 0:
        sys.exit("artwork missing: entry.png read as zero bytes")
    if blob[:8] != SIGNATURE:
        sys.exit("artwork is not a PNG: bad opening signature")
    if len(blob) > CEILING:
        sys.exit("artwork too large: %d bytes over the 1 MiB gate" % len(blob))
    if len(blob) != ARTWORK_BYTES:
        sys.exit(
            "artwork size mismatch: got %d, recorded %d"
            % (len(blob), ARTWORK_BYTES)
        )
    if hashlib.sha256(blob).hexdigest() != ARTWORK_SHA256:
        sys.exit("artwork fingerprint mismatch: sha256 differs from record")


def deliver(blob, folder):
    # The output folder may not exist yet on a fresh scoring machine.
    os.makedirs(folder, exist_ok=True)
    destination = os.path.join(folder, "entry.png")
    with open(destination, "wb") as stream:
        stream.write(blob)


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    blob = read_artwork(folder)
    check_artwork(blob)
    deliver(blob, os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    sys.stderr.write(
        "delivered entry.png — %d bytes, sha256 %s\n"
        % (len(blob), hashlib.sha256(blob).hexdigest())
    )


if __name__ == "__main__":
    main()
