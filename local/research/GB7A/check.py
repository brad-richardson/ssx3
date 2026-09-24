#!/usr/bin/env python3
"""GB7A checker: validates source-map.tsv headers/row count and source paths.

Semantic correctness is NOT certified by this script (orchestrator decides).
Read-only; exits 0 on pass, 1 on fail.
"""
import os
import sys

RECEIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(RECEIPT_DIR, "source-map.tsv")
PIN_DIR = "/Users/brad/dev/ssx3-work/GB4/PS2Recomp"
EXPECTED_HEADER = ["step", "source_file", "line_range",
                   "caller_or_data_source", "observed_fact",
                   "unknown", "proposed_probe"]

failures = []

if not os.path.isfile(TSV):
    print("FAIL: source-map.tsv missing");
    sys.exit(1)

with open(TSV, "r", encoding="utf-8") as f:
    lines = [ln.rstrip("\n") for ln in f if ln.strip() != ""]

header = lines[0].split("\t")
if header != EXPECTED_HEADER:
    failures.append("header mismatch: %r" % (header,))
rows = lines[1:]

if not (6 <= len(rows) <= 10):
    failures.append("row count %d not in 6-10" % len(rows))

for i, row in enumerate(rows, start=2):
    cols = row.split("\t")
    if len(cols) != 7:
        failures.append("line %d: %d cols, want 7" % (i, len(cols)))
        continue
    src, lr = cols[1].strip(), cols[2].strip()
    if not src or not lr:
        failures.append("line %d: empty source_file/line_range" % i)
        continue
    if "-" not in lr:
        failures.append("line %d: line_range %r lacks '-'" % (i, lr))
        continue
    full = os.path.join(PIN_DIR, src)
    if not os.path.isfile(full):
        failures.append("line %d: path missing under pin: %s" % (i, src))

size_total = sum(os.path.getsize(os.path.join(RECEIPT_DIR, n))
                 for n in ("REPORT.md", "source-map.tsv", "check.py")
                 if os.path.isfile(os.path.join(RECEIPT_DIR, n)))
print("rows=%d total_bytes=%d" % (len(rows), size_total))
if size_total >= 64 * 1024:
    failures.append("receipt set >= 64 KiB")

if failures:
    for m in failures:
        print("FAIL: " + m)
    sys.exit(1)
print("PASS")
