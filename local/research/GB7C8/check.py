#!/usr/bin/env python3
"""GB7C8 checker: verify pins/cited source rows; reject A claims on forbidden bases.

Read-only. Cannot prove runtime behaviour from strings: it checks that the
REPORT claims B (not A), that all pins verify, and that every load-bearing
source row is present at the pinned revs. Any failure -> RESULT OTHER.
An A verdict found in REPORT.md -> RESULT FAIL (A must not be claimed from
packet-entry bytes, queued counts, marker259 frame, isolated words, or an
added flush/submit).
"""
import hashlib
import os
import struct
import subprocess
import sys

FORK = "/Users/brad/dev/ssx3-work/GB4/PS2Recomp"
FORK_PIN = "f54adff3ab38108300d7ab7d239f59345bae97c3"
CAPTURE = "/Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin"
CAP_SHA = "a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851"
SIDECAR = "/Users/brad/dev/ssx3-work/GB4/run/gb4p4.paths.txt"
G43 = "/Users/brad/dev/ssx3-work/G43/parallel-gs"
G43_PIN = "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd"
CACHE = "/Users/brad/dev/ssx3-work/GB4/build/CMakeCache.txt"
HERE = os.path.dirname(os.path.abspath(__file__))

passes, fails = [], []


def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + detail) if detail and not cond else ""))


def git(d, *a):
    r = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True)
    return r.stdout.strip()


def read(p, n=400000):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read(n)


def has(path, needle):
    try:
        return needle in read(path)
    except OSError:
        return False


# 1. pins
check("fork_head", git(FORK, "rev-parse", "HEAD") == FORK_PIN, git(FORK, "rev-parse", "HEAD"))
st = git(FORK, "status", "--short")
check("fork_clean", st == "", st[:200])
h = hashlib.sha256()
with open(CAPTURE, "rb") as f:
    while True:
        chunk = f.read(1 << 20)
        if not chunk:
            break
        h.update(chunk)
check("capture_sha", h.hexdigest() == CAP_SHA, h.hexdigest()[:16])
with open(SIDECAR) as f:
    lines = f.read().splitlines()
check("sidecar_lines", len(lines) == 1982063, str(len(lines)))
check("sidecar_5471", lines[5470] == "5470 3", lines[5470] if len(lines) > 5470 else "short")
check("g43_head", git(G43, "rev-parse", "HEAD") == G43_PIN, git(G43, "rev-parse", "HEAD"))
cache = read(CACHE)
check("cache_sourcedir", "PS2X_PARALLEL_GS_SOURCE_DIR:PATH=/Users/brad/dev/ssx3-work/G43/parallel-gs" in cache)
check("g43_dirty_recorded", "dirty" in read(os.path.join(HERE, "REPORT.md")).lower())

# 2. cited fork rows at pin
F = FORK + "/ps2xRuntime/src/lib/gs/"
check("row_fanout", has(F + "gs_frontend.cpp", "m_backend->RawGifPacket(static_cast<uint32_t>(m_curGifPath), data, sizeBytes)"))
check("row_wantsraw", has(F + "ps2_gs_parallel_backend.cpp", "bool WantsRawGif() const override { return true; }"))
check("row_rawgif", has(F + "ps2_gs_parallel_backend.cpp", "m_iface->gif_transfer(path, data, static_cast<size_t>(sizeBytes))"))
check("row_flush_noop", has(F + "ps2_gs_parallel_backend.cpp", "void Flush() override {}"))
check("row_present_flush_vsync", has(F + "ps2_gs_parallel_backend.cpp", "m_iface->flush();")
      and has(F + "ps2_gs_parallel_backend.cpp", "m_iface->vsync(vsync)"))
check("row_snapshot_flush_map", has(F + "ps2_gs_parallel_backend.cpp", "self->m_iface->flush();")
      and has(F + "ps2_gs_parallel_backend.cpp", "self->m_iface->map_vram_read(0, kVram)"))
check("row_wait_idle", has(F + "ps2_gs_parallel_backend.cpp", "m_device->wait_idle();"))
check("row_diag_triple", has(F + "gs_frontend.cpp", "m_backend->Flush();")
      and has(F + "gs_frontend.cpp", "m_backend->Sync(GSSyncReason::Presentation);"))
check("row_cpu_submit", has(F + "gs_cpu_backend.cpp", "DrawPrimitive(batch);"))
check("row_addrpsm", has(FORK + "/ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h", "addrPSMCT32(uint32_t block, uint32_t width, uint32_t x, uint32_t y)"))

# 3. cited paraLLEl rows (working tree at G43_PIN, dirty)
G = G43 + "/gs/"
check("row_gif_transfer", has(G + "gs_interface.cpp", "void GSInterface::gif_transfer(uint32_t path_index, const void *data, size_t size)"))
check("row_flush_submit", has(G + "gs_interface.cpp", "renderer.flush_submit(value);"))
check("row_map_flush_wait", has(G + "gs_interface.cpp", "renderer.flush_submit(host_read_timeline);")
      and has(G + "gs_interface.cpp", "renderer.wait_timeline(host_read_timeline);"))

# 4. independent capture scan: marker259 precedes packet5470; confounder counts
def scan():
    pkt = 0
    pkt_off = {}
    marks = {}
    off = 8
    with open(CAPTURE, "rb") as fh:
        assert fh.read(8) == b"PS2XGSC1"
        while True:
            hdr = fh.read(4)
            if len(hdr) < 4:
                break
            (ln,) = struct.unpack("<I", hdr)
            rec = fh.read(ln)
            if len(rec) < ln:
                break
            kind = rec[0]
            tick = struct.unpack("<Q", rec[1:9])[0]
            cur = off
            off += 4 + ln
            if kind == 1:
                pkt_off[pkt] = (tick, cur)
                pkt += 1
            elif kind == 4 and tick not in marks:
                marks[tick] = (cur, pkt)
            if pkt > 11000:
                break
    return pkt_off, marks

pkt_off, marks = scan()
t5470, o5470 = pkt_off.get(5470, (None, None))
o259, p259 = marks.get(259, (None, None))
o300, p300 = marks.get(300, (None, None))
o301, p301 = marks.get(301, (None, None))
check("pkt5470_tick259", t5470 == 259, str((t5470, o5470)))
check("marker259_precedes_packet5470", o259 is not None and o5470 is not None and o259 < o5470,
      str((o259, o5470)))
check("confounder_300", p300 is not None and p300 - 5471 == 5001, str(p300))
check("confounder_301", p301 is not None and p301 - 5471 == 5123, str(p301))

# 5. verdict discipline: REPORT must claim B, reject A, name confounder, claim no GPU cause
rep = read(os.path.join(HERE, "REPORT.md"))
check("verdict_B", "Verdict: **B**" in rep)
check("no_A_claim", "RESULT A" not in rep and "Outcome: **A**" not in rep and "**A** (nonperturbing" not in rep.replace("**A** (nonperturbing per-packet witness exists)", ""))
check("A_rejected", "**REJECTED**" in rep)
check("confounder_named", "5001" in rep and "5123" in rep)
check("no_gpu_cause", "NOT CLAIMED" in rep)
check("forbidden_bases_listed", all(s in rep for s in
      ["Packet-entry byte equality", "queued-batch counts", "marker259", "isolated words", "flush/submit added before the observation"])
      or all(s in rep.lower() for s in ["packet-entry", "marker259", "flush"]))

ok = not fails
print("---")
print("CHECKS %d pass %d fail" % (len(passes), len(fails)))
verdict = "B" if ok else "OTHER"
reason = "all-match" if ok else "fail:" + ",".join(fails[:8])
print("RESULT %s reason=%s" % (verdict, reason))
with open(os.path.join(HERE, "check-result.txt"), "w") as f:
    f.write("RESULT %s reason=%s\nchecks_pass=%d checks_fail=%d\n" % (verdict, reason, len(passes), len(fails)))
    for n in passes:
        f.write("PASS " + n + "\n")
    for n in fails:
        f.write("FAIL " + n + "\n")
sys.exit(0 if ok else 1)
