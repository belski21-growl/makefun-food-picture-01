# food-picture-01 entry (Python 3.13, standard library only).
#
# The picture is the entry.png beside this file: a photorealistic hero shot
# of a gourmet smash burger - glossy brioche bun, molten cheddar dripping
# over a charred patty, fresh lettuce and tomato, a wisp of steam, warm
# golden light on a dark slate. The program copies its exact bytes to
# /output/entry.png. It is deterministic: every run writes the same bytes.
#
# The gate takes a whole PNG or JPEG of at most 1 MiB and 1024 by 1024
# pixels; this image is a JPEG (told apart by its first bytes) of 234,273
# bytes at 1024x1024, and the judge sees exactly the bytes copied.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DESTINATION = os.path.join(OUTPUT_DIR, "entry.png")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def check_jpeg(path, label):
    """Check the file at path is a whole JPEG: starts with the SOI marker
    (ffd8), ends with the EOI marker (ffd9) and is within the gate's size
    limit of 1 MiB. Returns its size in bytes."""
    size = os.path.getsize(path)
    if size > 1048576:
        fail(label + " is " + str(size) + " bytes, over the 1 MiB gate limit")
    with open(path, "rb") as handle:
        head = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        tail = handle.read(2)
    if head != b"\xff\xd8":
        fail(label + " does not start with the JPEG SOI marker (ffd8)")
    if tail != b"\xff\xd9":
        fail(label + " does not end with the JPEG EOI marker (ffd9)")
    return size


def fail(message):
    print("food-picture-01: " + message, file=sys.stderr)
    raise SystemExit(1)


# The source must be the image we ship: a whole JPEG, within the gate's
# size limit. Refuse to run on a missing, empty or truncated file rather
# than writing a broken entry.
if not os.path.isfile(SOURCE):
    fail("source image missing: " + SOURCE)
if os.path.getsize(SOURCE) == 0:
    fail("source image is empty: " + SOURCE)
source_size = check_jpeg(SOURCE, "source image")

# The output directory must exist and be writable; create it if needed.
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except OSError as exc:
    fail("cannot create output directory " + OUTPUT_DIR + ": " + str(exc))
if not os.path.isdir(OUTPUT_DIR) or not os.access(OUTPUT_DIR, os.W_OK):
    fail("output directory is not writable: " + OUTPUT_DIR)

# Copy the image byte for byte, in chunks, so the run never depends on
# how much memory the container gives it.
with open(SOURCE, "rb") as src, open(DESTINATION, "wb") as dst:
    while True:
        chunk = src.read(65536)
        if not chunk:
            break
        dst.write(chunk)

# Fail loudly rather than hand the grader a truncated copy: the two runs
# the grader makes must write the same bytes, so the copy is verified
# against the source before the program exits - same size, same SHA-256,
# and still a whole JPEG (SOI through EOI) after the copy.
if sha256_of(SOURCE) != sha256_of(DESTINATION):
    fail("entry.png copy failed integrity check (sha256 mismatch)")
if check_jpeg(DESTINATION, "output image") != source_size:
    fail("entry.png copy failed integrity check (size mismatch)")
