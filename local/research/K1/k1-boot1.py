#!/usr/bin/env python3
"""K1 validation boot: T26 env verbatim EXCEPT WATCH retargeted to the
copied-payload contract + PS2X_FRAME_DUMP_DIR armed (P0).

CWD $W/P1/run, stdbuf -o0 -e0, log direct to boot-k1-1.log, foreground.
Caps: wall SECS=240 s AND guest-progress EVENT_CAP=1000000 trace lines
(event-count, T24/T26 precedent), polled every POLL=15 s with liveness
lines to stdout + /tmp/k1-liveness.log. Whichever binds first: SIGTERM,
print BOUND=wall|event, sys.exit(-15) (241, prior-script convention).
Liveness monitor only: no exit trigger (capture boot, not exit boot).
Env = /tmp/t26-boot1.py (T16 diag set + PARK + TRACE_SYSCALLS channel ON
+ PS2X_TRACE_SYSCALLS_PC=1, PS2X_DROP_SILENCE popped) with:
WATCH = 5 windows: 0x80075000 (copy head) + 0x80075300 (payload table
head) + 0x80075328 (payload table tail / entry-03 slot) + 0x80075330 /
0x80075338 (_kExecArg data: expect zero writes; host memcpy/DMA/SIF
blits bypass per P26-1h). NOTE: the [0x456538] epilogue store is
FAST_WRITE32 (recompiled, watch-invisible); its value is proven by the
[k1] lookup#6 line + the static no-v0-clobber read, not by watch.
FRAMES = PS2X_FRAME_DUMP_DIR frames-k1-1 (first two uploads kept +
upload-latest/fallback-latest overwritten every upload).
"""

import os
import subprocess
import sys
import time

W = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = os.path.join(W, "P1/run")
LOG = os.path.join(RUN, "boot-k1-1.log")
TRACE = os.path.join(RUN, "syscalls-k1-on.txt")
LIVE = "/tmp/k1-liveness.log"
BIN = "/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner"
ELF = os.path.join(W, "P1/cd/SLUS_207.72")
FRAMES = os.path.join(RUN, "frames-k1-1")
SECS = 240
EVENT_CAP = 1000000
POLL = 15

env = dict(os.environ)
env["PS2X_CD_IMAGE"] = os.path.join(W, "SSX 3 (USA).iso")
env["PS2X_DIAG_PERIOD_MS"] = "5000"
env["PS2X_DIAG_DRIVER_PROBE"] = "1"
env["PS2X_DIAG_SEMA"] = "1"
env["PS2X_DIAG_SEMA_CREATE"] = "1"
env["PS2X_DIAG_SEMA_S0"] = "1"
env["PS2X_DIAG_WATCH"] = ",".join(
    ["0x80075000", "0x80075300", "0x80075328", "0x80075330", "0x80075338"]
)
env.pop("PS2X_DROP_SILENCE", None)
env["PS2X_DIAG_394ED0"] = "1"
env["PS2X_DIAG_PARK"] = "1"
env["PS2X_DIAG_PARK_DIR"] = os.path.join(RUN, "park-k1-1")
env["PS2X_TRACE_SYSCALLS"] = TRACE
env["PS2X_TRACE_SYSCALLS_PC"] = "1"
env["PS2X_FRAME_DUMP_DIR"] = FRAMES
os.makedirs(env["PS2X_DIAG_PARK_DIR"], exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)


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


print(f"BIN={BIN}", flush=True)
print(f"ELF={ELF}", flush=True)
print(f"CWD={RUN}", flush=True)
print(f"LOG={LOG}", flush=True)
print(f"SECS={SECS} (wall cap)", flush=True)
print(f"EVENT_CAP={EVENT_CAP} (progress cap, trace lines)", flush=True)
print(f"PS2X_DIAG_WATCH={env['PS2X_DIAG_WATCH']}", flush=True)
print(f"PS2X_DROP_SILENCE={'<unset>' if 'PS2X_DROP_SILENCE' not in env else env['PS2X_DROP_SILENCE']}", flush=True)
print(f"PS2X_TRACE_SYSCALLS={env['PS2X_TRACE_SYSCALLS']}", flush=True)
print(f"PS2X_TRACE_SYSCALLS_PC={env['PS2X_TRACE_SYSCALLS_PC']}", flush=True)
print(f"PS2X_FRAME_DUMP_DIR={env['PS2X_FRAME_DUMP_DIR']}", flush=True)

live = open(LIVE, "w")
live.write(f"# K1 liveness: wall={SECS}s progress={EVENT_CAP}lines poll={POLL}s\n")
live.flush()

with open(LOG, "wb") as lf:
    p = subprocess.Popen(
        ["stdbuf", "-o0", "-e0", BIN, ELF],
        cwd=RUN, env=env, stdout=lf, stderr=subprocess.STDOUT,
    )
    t0 = time.monotonic()
    bound = None
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
            line = (f"t={el:.0f}s alive log={fsize(LOG)}B "
                    f"trace_lines={nl} trace={fsize(TRACE)}B")
            print(line, flush=True)
            live.write(line + "\n")
            live.flush()
            if nl >= EVENT_CAP:
                bound = "event"
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
