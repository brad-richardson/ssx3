#!/usr/bin/env python3
"""mine_snapshot.py: rebuild a ps2x-park-snapshot/1 JSON from a raw boot log.

This is the manual P1ab/P1ac/P1ad rebuild, automated: per-thread state,
sema waiter/signaller pc histograms, hot-pc sums, [drop] census, SIF/RPC
rows, GS counters. Miner-blind fields (loads, binds, claimed calls,
sema table, stub-truncated hot-pc tails) are omitted; ladder_diff.py
reports them as BLIND/TRUNC/SATURATED rather than DELTA.

Usage:
  mine_snapshot.py BOOT.log [-o SNAP.json]
"""

import argparse
import collections
import json
import re
import sys

THREAD_RE = re.compile(
    r"\[diag:thread\] id=(\d+) status=(\d+) waitReason=(\d+) waitId=(-?\d+) "
    r"pc=(0x[0-9a-fA-F]+) entry=(0x[0-9a-fA-F]+) priority=(\d+) scheduled=(\d+)")
CREATE_RE = re.compile(
    r"\[diag:sema-create\] tid=(\d+) pc=(0x[0-9a-fA-F]+) ra=(0x[0-9a-fA-F]+) "
    r"param=0x[0-9a-fA-F]+ (?:noparam|count=\S+ max=(-?\d+) init=(-?\d+) "
    r"wait=\S+ attr=\S+ option=\S+) ret=(-?\d+)")
SEMA_RE = re.compile(r"\[diag:sema\] op=(wait|signal) id=(-?\d+) .*? pc=(0x[0-9a-fA-F]+)")
STUB_RE = re.compile(
    r"\[diag:stub\] target=(0x[0-9a-fA-F]+) count=(\d+) "
    r"firstRa=(0x[0-9a-fA-F]+) lastRa=(0x[0-9a-fA-F]+)")
DROP_RE = re.compile(r"\[drop\] (\S+) (\S+)")
RPC_RE = re.compile(
    r"\[IOP/RPC trace:unhandled\] sid=(0x[0-9a-fA-F]+) rpc=(0x[0-9a-fA-F]+) "
    r"pc=0x[0-9a-fA-F]+ ra=0x[0-9a-fA-F]+ send=0x[0-9a-fA-F]*/(\d+) "
    r"recv=0x[0-9a-fA-F]*/(\d+)")
SENDCMD_RE = re.compile(
    r"\[sceSifSendCmd\] cid=(0x[0-9a-fA-F]+) packet=0x[0-9a-fA-F]+ "
    r"psize=(0x[0-9a-fA-F]+) extra=0x[0-9a-fA-F]+")
KICK_RE = re.compile(r"\[gs:kick\] idx=\d+ drawing=(\d+)")
GIF_RE = re.compile(r"\[gs:gif\] idx=")
COPY_RE = re.compile(r"\[gs:copy-reg\] reg=")
TICK_RE = re.compile(r"\[run:tick\].*? dma=(\d+) gif=(\d+) gsw=(\d+) vif=(\d+)")
HANDSHAKE_RE = re.compile(r"\[sif-handshake\]")

STATUS_NAMES = ["Running", "Ready", "Waiting", "WaitingSuspended", "Suspended", "Dormant"]
WAIT_NAMES = ["None", "Sleep", "Semaphore", "EventFlag", "VSync", "External", "Mpeg"]


def norm_hex(h):
    return "0x%x" % int(h, 16)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mine a park snapshot from a boot log.")
    ap.add_argument("log")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args(argv)

    last_threads = {}
    sched = collections.Counter()
    creates = []
    wait_hist = collections.defaultdict(collections.Counter)
    signal_hist = collections.defaultdict(collections.Counter)
    hot = {}
    drops = collections.Counter()
    calls = []
    sendcmds = []
    handshake = False
    kicks = kicks_drawing = gifs = copies = 0
    tick_tail = None

    with open(args.log, errors="replace") as f:
        for line in f:
            s = line.strip()
            m = THREAD_RE.search(s)
            if m:
                tid = int(m.group(1))
                last_threads[tid] = {
                    "id": tid,
                    "status": int(m.group(2)),
                    "status_name": STATUS_NAMES[int(m.group(2))] if int(m.group(2)) < 6 else "Unknown",
                    "wait_reason": int(m.group(3)),
                    "wait_reason_name": WAIT_NAMES[int(m.group(3))] if int(m.group(3)) < 7 else "Unknown",
                    "wait_id": int(m.group(4)),
                    "pc": norm_hex(m.group(5)),
                    "ra": "0x0",
                    "sp": "0x0",
                    "entry": norm_hex(m.group(6)),
                    "priority": int(m.group(7)),
                    "scheduled": 0,
                    "chain": [],
                }
                sched[tid] += int(m.group(8))
                continue
            m = CREATE_RE.search(s)
            if m and int(m.group(6)) > 0:
                creates.append({
                    "id": int(m.group(6)),
                    "tid": int(m.group(1)),
                    "pc": norm_hex(m.group(2)),
                    "init": int(m.group(5)) if m.group(5) is not None else 0,
                    "max": int(m.group(4)) if m.group(4) is not None else 0,
                })
                continue
            m = SEMA_RE.search(s)
            if m:
                (wait_hist if m.group(1) == "wait" else signal_hist)[m.group(2)][norm_hex(m.group(3))] += 1
                continue
            m = STUB_RE.search(s)
            if m:
                pc = norm_hex(m.group(1))
                if pc not in hot:
                    hot[pc] = {"pc": pc, "count": 0,
                               "first_ra": norm_hex(m.group(3)), "last_ra": norm_hex(m.group(4))}
                hot[pc]["count"] += int(m.group(2))
                hot[pc]["last_ra"] = norm_hex(m.group(4))
                continue
            m = DROP_RE.search(s)
            if m:
                drops[(m.group(1), m.group(2))] += 1
                continue
            m = RPC_RE.search(s)
            if m:
                calls.append({"op": "call", "sid": norm_hex(m.group(1)), "fno": norm_hex(m.group(2)),
                              "send_size": int(m.group(3)), "recv_size": int(m.group(4)),
                              "tid": 0, "claimed": False, "path": ""})
                continue
            m = SENDCMD_RE.search(s)
            if m:
                sendcmds.append({"op": "sendcmd", "sid": norm_hex(m.group(1)), "fno": "0x0",
                                 "send_size": int(m.group(2), 16), "recv_size": 0,
                                 "tid": 0, "claimed": False, "path": ""})
                continue
            if HANDSHAKE_RE.search(s):
                handshake = True
                continue
            m = KICK_RE.search(s)
            if m:
                kicks += 1
                kicks_drawing += int(m.group(1))
                continue
            if GIF_RE.search(s):
                gifs += 1
                continue
            if COPY_RE.search(s):
                copies += 1
                continue
            m = TICK_RE.search(s)
            if m:
                tick_tail = [int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))]

    for tid, row in last_threads.items():
        row["scheduled"] = sched[tid]
    if handshake:
        for e in sendcmds:
            if e["sid"] == "0x80000001":
                e["claimed"] = True

    doc = {
        "schema": "ps2x-park-snapshot/1",
        "source": "miner",
        "threads": [last_threads[k] for k in sorted(last_threads)],
        "semaphores": [],
        "sema_creates": sorted(creates, key=lambda c: c["id"]),
        "sema_wait_hist": {k: dict(sorted(v.items())) for k, v in sorted(wait_hist.items(), key=lambda kv: int(kv[0]))},
        "sema_signal_hist": {k: dict(sorted(v.items())) for k, v in sorted(signal_hist.items(), key=lambda kv: int(kv[0]))},
        "hot_pc": sorted(hot.values(), key=lambda h: -h["count"]),
        "drops": [{"site": k[0], "reason": k[1], "count": v} for k, v in sorted(drops.items())],
        "sif_rpc": calls + sendcmds,
        "sif_rpc_overflow": 0,
        "gs": {"kicks": kicks, "kicks_drawing": kicks_drawing, "gif_packets": gifs,
               "copy_regs": copies,
               "dma_starts": tick_tail[0] if tick_tail else 0,
               "gif_copies": tick_tail[1] if tick_tail else 0,
               "gs_writes": tick_tail[2] if tick_tail else 0,
               "vif_writes": tick_tail[3] if tick_tail else 0},
        "sched_counts": {str(k): v for k, v in sorted(sched.items())},
    }
    text = json.dumps(doc, indent=2) + "\n"
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
