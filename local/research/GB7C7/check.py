#!/usr/bin/env python3
"""GB7C7 scripted acceptance (stop-short version).

Verifies input SHA/path pins, then requires the ON-probe trace the brief
names. The probe was never implemented (fork edit denied), so the expected
result is OTHER with the first mismatch named. Exit 0 when the verdict line
is emitted; exit 1 on checker internal error only.
"""
import hashlib
import os
import sys

GB4 = os.path.expanduser("~/dev/ssx3-work/GB4")
CAPTURE = os.path.join(GB4, "run", "gb4p4.capture.bin")
PATHS = os.path.join(GB4, "run", "gb4p4.paths.txt")
TRACE = os.path.join(GB4, "run", "gb7c7", "tap.tsv")
PIN_SHA = "a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851"

rows = []


def check(name, ok, detail=""):
    rows.append((name, bool(ok), detail))
    return bool(ok)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ok = True
try:
    ok &= check("capture_sha", sha256(CAPTURE) == PIN_SHA, PIN_SHA[:12])
except OSError as e:
    ok &= check("capture_sha", False, f"unreadable: {e}")

try:
    with open(PATHS) as f:
        n = sum(1 for _ in f)
    ok &= check("paths_lines", n == 1982063, str(n))
except OSError as e:
    ok &= check("paths_lines", False, f"unreadable: {e}")

try:
    with open(PATHS) as f:
        line5471 = None
        for i, line in enumerate(f, 1):
            if i == 5471:
                line5471 = line.strip()
                break
    ok &= check("paths_5470", line5471 == "5470 3", repr(line5471))
except OSError as e:
    ok &= check("paths_5470", False, f"unreadable: {e}")

trace_exists = os.path.exists(TRACE)
ok &= check("trace_present", trace_exists, TRACE if not trace_exists else "present")

verdict = "OTHER"
reason = "probe-not-implemented"
for name, passed, detail in rows:
    if not passed:
        reason = name
        break
else:
    reason = "missing-trace-rows" if not trace_exists else "not-evaluated"

print("check\tpass\tdetail")
for name, passed, detail in rows:
    print(f"{name}\t{'PASS' if passed else 'FAIL'}\t{detail}")
print(f"RESULT {verdict} reason={reason}")
