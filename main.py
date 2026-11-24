#!/usr/bin/env python3
"""THE FIRST LIGHT POST — entry program for news-image-20261123 (akun4).

Concept: a light-grey broadsheet front page with black ink and a
burnt-orange accent, summing up Monday 23 November 2026 in one image:
12 numbered main cards led by the burning tankers in the Strait of
Hormuz, a day-in-numbers box, a dotted world map, a red date-check box
and 31 further briefs — 43 stories, 7 regions, all from the one day.

This program is deliberately boring: it is a stdlib-only, copy-only
carrier. It reads the finished entry.png sitting next to it, verifies
the byte count and the SHA-256 fingerprint, and writes the identical
bytes to the output directory. No image work happens here — the
picture was drawn beforehand by compose.py in the recorded session.
"""

import hashlib
import os
import sys

# Fingerprint of the shipped artwork (filled in once entry.png was final).
EXPECTED_BYTES = 117026
EXPECTED_SHA256 = "2b97bcaed6cb4173a2a8e9e2e55393ac89257b62f80a6ecf672c7fa164568908"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
HARD_LIMIT = 1048576  # the competition's 1 MiB ceiling


def load_artwork(path):
    # Read in one pass: the artwork is small (about 117 KB) and the run
    # must be deterministic, so no chunking or streaming tricks here.
    with open(path, "rb") as handle:
        return handle.read()


def verify(data):
    """Refuse to ship anything that is not exactly the final artwork."""
    if not data:
        raise SystemExit("entry.png is empty")
    if data[:8] != PNG_SIGNATURE:
        raise SystemExit("entry.png does not start with the PNG signature")
    if len(data) > HARD_LIMIT:
        raise SystemExit("entry.png exceeds 1 MiB: %d bytes" % len(data))
    if len(data) != EXPECTED_BYTES:
        raise SystemExit(
            "entry.png size drifted: %d bytes, expected %d"
            % (len(data), EXPECTED_BYTES)
        )
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("entry.png sha256 drifted: %s" % digest)
    return digest


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(out_dir, "entry.png")

    data = load_artwork(source)
    digest = verify(data)

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(data)

    sys.stderr.write("entry.png: %d bytes sha256=%s\n" % (len(data), digest))


if __name__ == "__main__":
    main()
