#!/usr/bin/env python3
"""E3b one-or-two-frame order capture boot (no separate baseline boot).

Terminates on the FIRST of: [e3:span-complete] marker (+10s grace),
600s wall cap, 1M trace-line progress cap, 800MB LOG byte cap.
Keeps partials on any bound. Lease must be held by the caller.
"""
import os
import subprocess
import sys
import time

W = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = os.path.join(W, "P1/run")
LOG = os.path.join(RUN, "boot-e3b-1.log")
TRACE = os.path.join(RUN, "syscalls-e3b-1.txt")
PLOG = os.path.join(RUN, "ps2_log.txt")
PLOG_FINAL = os.path.join(RUN, "ps2_log-e3b-1.txt")
LIVE = "/tmp/e3b-liveness.log"
BIN = "/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner"
ELF = os.path.join(W, "P1/cd/SLUS_207.72")
FRAMES = os.path.join(RUN, "frames-e3b-1")
PARK = os.path.join(RUN, "park-e3b-1")
WATCHENV = "/Users/bradrichardson/dev/ssx3/local/research/T26/watch-env.txt"
SECS = 600
EVENT_CAP = 1000000
BYTE_CAP = 800 * 1024 * 1024
POLL = 5
GRACE = 10

with open(WATCHENV, "r") as f:
    watch = f.read().strip()
assert len(watch.split(",")) == 83, f"want 83 T26 windows, got {len(watch.split(','))}"

env = dict(os.environ)
env["PS2X_CD_IMAGE"] = os.path.join(W, "SSX 3 (USA).iso")
env["PS2X_DIAG_PERIOD_MS"] = "5000"
env["PS2X_DIAG_DRIVER_PROBE"] = "1"
env["PS2X_DIAG_SEMA"] = "1"
env["PS2X_DIAG_SEMA_CREATE"] = "1"
env["PS2X_DIAG_SEMA_S0"] = "1"
env["PS2X_DIAG_WATCH"] = watch
env.pop("PS2X_DROP_SILENCE", None)
env["PS2X_DIAG_394ED0"] = "1"
env["PS2X_DIAG_PARK"] = "1"
env["PS2X_DIAG_PARK_DIR"] = PARK
env["PS2X_TRACE_SYSCALLS"] = TRACE
env["PS2X_TRACE_SYSCALLS_PC"] = "1"
env["PS2X_FRAME_DUMP_DIR"] = FRAMES
env["PS2X_E3_INV"] = "1000"
env["PS2X_E3_S1BASE"] = "0x70001C00"
env["PS2X_E3_BYTES"] = str(8 * 1024 * 1024)
os.makedirs(PARK, exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)

print(f"BIN={BIN}", flush=True)
print(f"ELF={ELF}", flush=True)
print(f"CWD={RUN}", flush=True)
print(f"LOG={LOG}", flush=True)
print(f"SECS={SECS} (wall cap)", flush=True)
print(f"EVENT_CAP={EVENT_CAP} (progress cap, trace lines)", flush=True)
print(f"BYTE_CAP={BYTE_CAP} (LOG byte cap)", flush=True)
print(f"E3_INV={env['PS2X_E3_INV']} E3_S1BASE={env['PS2X_E3_S1BASE']} E3_BYTES={env['PS2X_E3_BYTES']}", flush=True)
print(f"WATCH_windows=83 (T26 verbatim)", flush=True)
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


def log_has(marker):
    try:
        with open(LOG, "rb") as f:
            # Span markers are rare; scan the tail (last 2MB) each poll.
            f.seek(0, os.SEEK_END)
            end = f.tell()
            f.seek(max(0, end - 2 * 1024 * 1024))
            return marker in f.read()
    except OSError:
        return False


live = open(LIVE, "w")
live.write(f"# E3b liveness: wall={SECS}s progress={EVENT_CAP}lines bytes={BYTE_CAP} poll={POLL}s\n")
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
            line = (f"t={el:.0f}s alive log={lb}B "
                    f"trace_lines={nl} trace={fsize(TRACE)}B")
            print(line, flush=True)
            live.write(line + "\n")
            live.flush()
            if span_at is None and log_has(b"[e3:span-complete]"):
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
