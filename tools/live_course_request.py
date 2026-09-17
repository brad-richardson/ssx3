#!/usr/bin/env python3
"""File a desktop live-course request (the SSX3_COURSE_REQUEST protocol).

The runtime watches the request file named by SSX3_COURSE_REQUEST and consumes
it within about a second: the first line names the manifest to apply, or the
word "stock" to drop a queued switch (the stock event itself restores on the
next reset; live apply cannot un-poke the table). See
docs/course-selection.md, "Live apply".

The write is atomic (temporary file plus rename) so the runtime never reads a
half-written path, and filing fails while an earlier request is still
unconsumed so one switch cannot silently clobber another.
"""
import argparse
import os
import tempfile
from pathlib import Path

STOCK = "stock"


def write_request(request_path, manifest):
    """File a request; return the request path.

    manifest is a path to an existing manifest file, or "stock". Raises
    FileNotFoundError for a missing manifest and FileExistsError while an
    earlier request is still queued.
    """
    request = Path(request_path)
    if request.exists():
        raise FileExistsError(f"Request {request} is still queued; wait for the runtime to consume it")
    if manifest == STOCK:
        body = STOCK + "\n"
    else:
        target = Path(manifest)
        if not target.is_file():
            raise FileNotFoundError(f"No manifest at {target}")
        body = str(target) + "\n"
    request.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=request.name + ".", dir=request.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(body)
        os.rename(tmp, request)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("request", type=Path, help="Request file named by SSX3_COURSE_REQUEST")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", type=Path, help="Manifest file to apply live")
    group.add_argument("--stock", action="store_true", help="Drop any queued switch")
    args = ap.parse_args()
    print(write_request(args.request, STOCK if args.stock else args.manifest))


if __name__ == "__main__":
    main()
