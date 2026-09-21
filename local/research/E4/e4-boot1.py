#!/usr/bin/env python3
"""E4 steady-frame boundary capture boot (one boot, BOUND=span).

Arms the GS debug history at VBlank tick N=600, freezes + dumps at M=601
(history text, VRAM arm/freeze, ReadVram samples, Present inputs) via the
ps2_e4 taps. P0 frame dumps join the returned image at ticks N..M.

Terminates on the FIRST of: [e4:span-complete] marker (+10s grace),
600s wall cap, 1M trace-line progress cap, 800MB LOG byte cap, 12MB E4-dir
byte cap. Keeps partials on any bound. Lease must be held by the caller.
Lean env (PARK + FRAMES + TRACE + E4 vars; no WATCH/394ED0/sema spam).
"""
import os
import subprocess
import sys
import time

W = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = os.path.join(W, "P1/run")
LOG = os.path.join(RUN, "boot-e4-1.log")
TRACE = os.path.join(RUN, "syscalls-e4-on.txt")
LIVE = "/tmp/e4-liveness.log"
BIN = "/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner"
ELF = os.path.join(W, "P1/cd/SLUS_207.72")
FRAMES = os.path.join(RUN, "frames-e4-1")
PARK = os.path.join(RUN, "park-e4-1")
E4DIR = os.path.join(RUN, "e4-1")
SECS = 600
EVENT_CAP = 1000000
BYTE_CAP = 800 * 1024 * 1024
E4_BYTE_CAP = 12 * 1024 * 1024
POLL = 5
GRACE = 10
ARM = "600"
FREEZE = "601"

env = dict(os.environ)
env["PS2X_CD_IMAGE"] = os.path.join(W, "SSX 3 (USA).iso")
env["PS2X_DIAG_PERIOD_MS"] = "5000"
env.pop("PS2X_DROP_SILENCE", None)
env["PS2X_DIAG_PARK"] = "1"
env["PS2X_DIAG_PARK_DIR"] = PARK
env["PS2X_TRACE_SYSCALLS"] = TRACE
env["PS2X_TRACE_SYSCALLS_PC"] = "1"
env["PS2X_FRAME_DUMP_DIR"] = FRAMES
env["PS2X_E4_ARM_TICK"] = ARM
env["PS2X_E4_FREEZE_TICK"] = FREEZE
env["PS2X_E4_DIR"] = E4DIR
os.makedirs(PARK, exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(E4DIR, exist_ok=True)

print(f"BIN={BIN}", flush=True)
print(f"ELF={ELF}", flush=True)
print(f"CWD={RUN}", flush=True)
print(f"LOG={LOG}", flush=True)
print(f"SECS={SECS} (wall cap)", flush=True)
print(f"EVENT_CAP={EVENT_CAP} (progress cap, trace lines)", flush=True)
print(f"BYTE_CAP={BYTE_CAP} (LOG byte cap)", flush=True)
print(f"E4_BYTE_CAP={E4_BYTE_CAP} (E4 dir byte cap)", flush=True)
print(f"E4_ARM={ARM} E4_FREEZE={FREEZE} E4_DIR={E4DIR}", flush=True)
print(f"FRAME_DUMP_DIR={FRAMES}", flush=True)


def trace_lines():
    try:
        with open(TRACE, "rb") as f:
            return f.read().count(b"\n")
    except FileNotFoundError:
        return 0


def fsize(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def dirsize(path):
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for fn in files:
                try:
                    total += os.path.getsize(os.path.join(root, fn))
                except OSError:
                    pass
    except OSError:
        pass
    return total


def log_has(marker):
    try:
        with open(LOG, "rb") as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            f.seek(max(0, end - 2 * 1024 * 1024))
            return marker in f.read()
    except OSError:
        return False


live = open(LIVE, "w")
live.write(f"# E4 liveness: wall={SECS}s progress={EVENT_CAP}lines bytes={BYTE_CAP} e4={E4_BYTE_CAP} poll={POLL}s\n")
live.flush()

with open(LOG, "wb") as lf:
    p = subprocess.Popen(
        ["stdbuf", "-o0", "-e0", BIN, ELF],
        cwd=RUN, env=env, stdout=lf, stderr=subprocess.STDOUT,
    )
    t0 = time.monotonic()
    bound = None
    span_at = None
    while True:
        try:
            rc = p.wait(timeout=POLL)
            print(f"exited rc={rc} before timeout (BOUND=none)")
            live.write(f"t={time.monotonic()-t0:.0f}s exited rc={rc} BOUND=none\n")
            live.close()
            break
        except subprocess.TimeoutExpired:
            el = time.monotonic() - t0
            nl = trace_lines()
            lb = fsize(LOG)
            eb = dirsize(E4DIR)
            line = (f"t={el:.0f}s alive log={lb}B "
                    f"trace_lines={nl} trace={fsize(TRACE)}B e4dir={eb}B")
            print(line, flush=True)
            live.write(line + "\n")
            live.flush()
            if span_at is None and log_has(b"[e4:span-complete]"):
                span_at = el
                print(f"SPAN-COMPLETE at {el:.0f}s, grace {GRACE}s", flush=True)
                live.write(f"SPAN-COMPLETE el={el:.0f}s grace={GRACE}s\n")
                live.flush()
            if span_at is not None and el - span_at >= GRACE:
                bound = "span"
            elif nl >= EVENT_CAP:
                bound = "event"
            elif lb >= BYTE_CAP:
                bound = "bytes"
            elif eb >= E4_BYTE_CAP:
                bound = "e4bytes"
            elif el >= SECS:
                bound = "wall"
            if bound is not None:
                p.terminate()
                try:
                    rc = p.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    p.kill()
                    rc = p.wait()
                print(f"SIGTERM after {el:.0f}s, rc={rc} BOUND={bound}")
                live.write(f"SIGTERM el={el:.0f}s rc={rc} BOUND={bound}\n")
                live.close()
                sys.exit(-15)
