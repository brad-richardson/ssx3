#!/usr/bin/env python3
"""G16: ONE bounded mac-host ASan(+UBSan) replay of the rich dump copy.

macOS ships no `timeout(1)` binary, so this wrapper enforces the wall cap
(280 s, same as the G14/G15 device runs) via subprocess.run(timeout=...).
Full stdout+stderr are captured to files; exit code + wall time printed.

Env mirrors the G13 mac run receipts (MoltenVK ICD + DYLD_LIBRARY_PATH)
plus sanitizer options (macOS has no LeakSanitizer: detect_leaks=0).
The dump under test is a sha-verified COPY in ps2x-g16: the G8+G10 PPM
hook writes scanouts next to the dump path, and ps2x-g13 is read-only.
"""
import os
import subprocess
import sys
import time

SSD = "/Volumes/Extreme SSD"
BUILD = os.path.join(SSD, "parallel-gs-g16-asan-build")
REPLAYER = os.path.join(BUILD, "tools", "parallel-gs-replayer")
DUMP = os.path.join(SSD, "ps2x-g16", "g16-dump.gs")
WALL_CAP = 280

env = dict(os.environ)
env["VK_ICD_FILENAMES"] = "/opt/homebrew/etc/vulkan/icd.d/MoltenVK_icd.json"
env["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
env["ASAN_OPTIONS"] = "detect_leaks=0:symbolize=1"
env["UBSAN_OPTIONS"] = "print_stacktrace=1:halt_on_error=1"

t0 = time.time()
try:
    p = subprocess.run(
        [REPLAYER, DUMP, "--iterations", "2"],
        cwd=os.path.join(BUILD, "tools"),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=WALL_CAP,
    )
    wall = time.time() - t0
    print(f"G16_EXIT={p.returncode} WALL={wall:.1f}s")
    timed_out = False
except subprocess.TimeoutExpired as e:
    wall = time.time() - t0
    print(f"G16_EXIT=TIMEOUT WALL={wall:.1f}s (cap {WALL_CAP}s)")
    p = e
    timed_out = True

out_path = "/tmp/g16-run-stdout.txt"
err_path = "/tmp/g16-run-stderr.txt"
with open(out_path, "wb") as f:
    f.write(p.stdout or b"")
with open(err_path, "wb") as f:
    f.write(p.stderr or b"")
print(f"STDOUT_BYTES={os.path.getsize(out_path)} -> {out_path}")
print(f"STDERR_BYTES={os.path.getsize(err_path)} -> {err_path}")
sys.exit(0 if timed_out else 0)
