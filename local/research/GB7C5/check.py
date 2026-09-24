#!/usr/bin/env python3
"""GB7C5 scripted acceptance checker.

Verifies the writer-watch trace structurally and the ON/OFF control
equivalence. Prints ACCEPT with evidence or OTHER with the first failing
reason (missing path coverage also yields OTHER). Exit 0 on ACCEPT,
exit 1 on OTHER.

Usage:
  check.py --trace <watch.tsv> --on-log <replay-1.log> --off-log <replay-off.log>
           --on-ppm <ppm dir> --off-ppm <ppm-off dir>
"""
import argparse
import hashlib
import re
import sys

WATCH_ADDR = "0019ae38"
KNOWN_OPS = {"-", "draw", "upload", "ll", "clear", "direct"}
BASELINE_PRESENT = {"600": "a6948f2", "601": "582dd887"}  # GB7C2/GB7C4 pins


def fail(reason):
    print("OTHER: %s" % reason)
    return 1


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True)
    ap.add_argument("--on-log", required=True)
    ap.add_argument("--off-log", required=True)
    ap.add_argument("--on-ppm", required=True)
    ap.add_argument("--off-ppm", required=True)
    args = ap.parse_args()

    try:
        with open(args.trace, "r") as f:
            lines = f.read().splitlines()
    except OSError as e:
        return fail("trace unreadable: %s" % e)
    if not lines:
        return fail("trace empty")
    header = lines[0].split("\t")
    expected = ["seq", "tick", "packet", "path", "batch", "op", "addr",
                "x", "y", "psm", "base", "bw", "old", "new", "kind", "detail"]
    if header != expected:
        return fail("header mismatch: %s" % ("|".join(header),))
    rows = [l.split("\t") for l in lines[1:] if l.strip()]
    if not rows:
        return fail("no data rows")
    for r in rows:
        if len(r) != len(expected):
            return fail("ragged row seq=%s" % (r[0] if r else "?",))

    # Sequence/order: seq strictly increasing from 0, packet non-decreasing.
    seqs = [int(r[0]) for r in rows]
    if seqs != list(range(len(rows))):
        return fail("seq not 0..N-1 in order")
    packets = [int(r[2]) for r in rows]
    if any(b < a for a, b in zip(packets, packets[1:])):
        return fail("packet index regresses")
    if max(packets) > 47240:
        return fail("row beyond packet 47240 (max %d)" % max(packets))

    # Unique watched address.
    addrs = set(r[6] for r in rows)
    if addrs != {WATCH_ADDR}:
        return fail("watched addr set = %s, want only %s" % (sorted(addrs), WATCH_ADDR))

    # Known op tags only (unknown mutation path -> OTHER).
    ops = set(r[5] for r in rows)
    unknown = ops - KNOWN_OPS
    if unknown:
        return fail("unknown op tags %s (missing path coverage)" % sorted(unknown))

    # Snapshots: start at packet 0, pre at 47240, post at/after 47240.
    kinds = {}
    for r in rows:
        kinds.setdefault(r[14], []).append(r)
    for need, pkt in (("snapshot-start", 0), ("pre-47240", 47240), ("post-47240", None)):
        if need not in kinds:
            return fail("missing %s row" % need)
    if int(kinds["snapshot-start"][0][2]) != 0:
        return fail("snapshot-start not at packet 0")
    if int(kinds["pre-47240"][0][2]) != 47240:
        return fail("pre-47240 not at packet 47240")
    if int(kinds["post-47240"][0][2]) < 47240:
        return fail("post-47240 before packet 47240")
    for k in ("snapshot-start", "pre-47240", "post-47240"):
        for r in kinds[k]:
            if r[12] != r[13]:
                return fail("%s row has old!=new" % k)

    # Transition rows: kind==change must carry old->new with packet IDs.
    changes = kinds.get("change", [])
    for r in changes:
        if r[12] == r[13]:
            return fail("change row seq=%s has old==new" % r[0])
        if not re.fullmatch(r"[0-9a-f]{8}", r[12]) or not re.fullmatch(r"[0-9a-f]{8}", r[13]):
            return fail("change row seq=%s has malformed words" % r[0])

    # Cap status from the ON log: capped trace = missing coverage -> OTHER.
    try:
        with open(args.on_log) as f:
            on_log = f.read()
    except OSError as e:
        return fail("on-log unreadable: %s" % e)
    m = re.search(r"GB7C5_SUMMARY rows=(\d+) bytes=(\d+) capped=(\d)", on_log)
    if not m:
        return fail("no GB7C5_SUMMARY in on-log")
    if m.group(3) != "0":
        return fail("trace capped (rows=%s bytes=%s): coverage incomplete" % (m.group(1), m.group(2)))
    if int(m.group(1)) != len(rows):
        return fail("summary rows=%s != trace rows=%d" % (m.group(1), len(rows)))

    # ON/OFF frame-hash equality + baseline pins.
    try:
        with open(args.off_log) as f:
            off_log = f.read()
    except OSError as e:
        return fail("off-log unreadable: %s" % e)

    def presents(log):
        out = {}
        for mm in re.finditer(r"GB4_FRAME tick=(\d+) .* present=([0-9a-f]+)", log):
            out[mm.group(1)] = mm.group(2)
        return out

    on_p, off_p = presents(on_log), presents(off_log)
    for tick, want in BASELINE_PRESENT.items():
        if on_p.get(tick) != want:
            return fail("ON tick%s present=%s, want baseline %s" % (tick, on_p.get(tick), want))
        if off_p.get(tick) != want:
            return fail("OFF tick%s present=%s, want baseline %s" % (tick, off_p.get(tick), want))
        if on_p.get(tick) != off_p.get(tick):
            return fail("ON/OFF present mismatch at tick%s" % tick)

    # PPM byte equality at ticks 600/601.
    for tick in ("000600", "000601"):
        a = "%s/vq-%s.ppm" % (args.on_ppm, tick)
        b = "%s/vq-%s.ppm" % (args.off_ppm, tick)
        try:
            ha, hb = sha256_file(a), sha256_file(b)
        except OSError as e:
            return fail("ppm unreadable: %s" % e)
        if ha != hb:
            return fail("ON/OFF ppm mismatch at tick %s" % tick)

    start_word = kinds["snapshot-start"][0][12]
    pre_word = kinds["pre-47240"][0][12]
    post_word = kinds["post-47240"][0][12]
    first_change = changes[0][2] if changes else "-"
    print("ACCEPT: rows=%d changes=%d ops=%s start=%s pre=%s post=%s first_change_packet=%s "
          "on/off presents 600/601 match baseline; ppms match; uncapped"
          % (len(rows), len(changes), ",".join(sorted(ops)),
             start_word, pre_word, post_word, first_change))
    return 0


if __name__ == "__main__":
    sys.exit(main())
