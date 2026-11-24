#!/usr/bin/env python3
"""THE ATLAS LEDGER v2 -- one day, one front page.

Copies the finished 1024x1024 broadsheet (entry.png, rendered by
render.py in the build session from the 36 stories sourced in
SOURCES.md) to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png
on the grader, or ./out/entry.png when run by hand).

Pure Python 3 standard library, no network. The copy is
byte-identical every run: the same bytes come out twice, because
the file copied never changes.
"""
import hashlib
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # the copy must be exact: fail loudly if source and output differ
    src_hash = hashlib.sha256(open(src, "rb").read()).hexdigest()
    data = open(dst, "rb").read()
    dst_hash = hashlib.sha256(data).hexdigest()
    assert src_hash == dst_hash, "copy mismatch: %s != %s" % (src_hash, dst_hash)
    print("wrote %s %d bytes sha256=%s"
          % (dst, len(data), dst_hash))


if __name__ == "__main__":
    main()
