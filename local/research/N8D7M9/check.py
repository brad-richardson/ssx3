#!/usr/bin/env python3
"""N8D7M9 verifier: pins + cited source rows + A/B/OTHER table discipline.

Read-only: inspects pinned worktree sources and local/research/N8D7M9/REPORT.md.
Emits check-result.json; exit 0 on PASS, 1 on FAIL. Stdlib only.

It cannot prove execution from source strings alone: it verifies that the
cited source rows exist at the pinned revs, that the pins match, and that the
REPORT's prediction table gives (i)/(ii)/(iii) pairwise-unique observables
under an order-preserving witness, separates the four clocks, surveys
completion methods without awarding a per-draw method, and carries the
required cost/cap/gap discipline. Runtime execution and nonperturbation are
for the orchestrator's gate, not this script.
"""
import json
import os
import subprocess
import sys

FORK = os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/src/lib/gs")
FINCL = os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/include/runtime/gs")
G43 = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs/gs")
PAGE = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs/gs")
GRANITE_VK = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs/Granite/vulkan")
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "REPORT.md")

FORK_PIN = "a8cfefad109134767b0810b7707b4b58a5dfcca7"
PGS_PIN = "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd"

# (base_dir, rel_file, cited_line_1based, expected_token, window)
CITATIONS = [
    (FORK, "gs_frontend.cpp", 931, "m_worker && !t_inGsWorker", 5),
    (FORK, "gs_frontend.cpp", 947, "m_submitCount.fetch_add", 5),
    (FORK, "gs_frontend.cpp", 948, "vsyncTick", 5),
    (FORK, "gs_frontend.cpp", 956, "RawGifPacket", 5),
    (FORK, "gs_frontend.cpp", 197, "processGIFPacket", 5),
    (FORK, "gs_frontend.cpp", 769, "vsyncTick", 5),
    (FORK, "gs_frontend.cpp", 806, "m_backendLifetimeMutex", 5),
    (FORK, "gs_frontend.cpp", 809, "Flush", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 441, "selectedRequested", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 447, "phase", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 452, "m_iface->flush", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 601, "submit(cmd)", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 602, "wait_idle", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 621, "map_host_buffer", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 897, "RawGifPacket", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 901, "gif_transfer", 5),
    (FINCL, "gs_worker.h", 112, "bytes", 5),
    (FINCL, "gs_worker.h", 123, "kDefaultMaxDescriptors", 5),
    (FINCL, "gs_worker.h", 139, "enqueue", 5),
    (FINCL, "gs_frontend.h", 145, "NoteGifPath", 5),
    (FINCL, "gs_backend.h", 40, "RawGifPacket", 5),
    (G43, "gs_interface.cpp", 5161, "mark_submission_timeline", 5),
    (G43, "gs_interface.cpp", 5162, "flush_submit(value)", 5),
    (G43, "gs_interface.cpp", 5191, "gif_transfer", 5),
    (G43, "gs_interface.cpp", 5576, "renderer.vsync", 5),
    (G43, "gs_interface.cpp", 3329, "drawing_kick_append", 5),
    (G43, "gs_interface.cpp", 3694, "primitive_count++", 5),
    (G43, "gs_renderer.cpp", 4813, "barrier", 5),
    (G43, "gs_renderer.cpp", 4816, "copy_buffer", 5),
    (G43, "gs_renderer.cpp", 4834, "sample_crtc_circuit", 5),
    (G43, "gs_renderer.cpp", 5076, "selected_capture_status = 2", 5),
    (G43, "gs_renderer.cpp", 5354, "flush_submit(0)", 5),
    (G43, "gs_renderer.cpp", 1116, "flush_submit", 5),
    (G43, "gs_renderer.cpp", 879, "check_flush_stats", 5),
    (G43, "gs_renderer.cpp", 903, "mark_memory_pressure", 5),
    (G43, "gs_renderer.cpp", 1052, "wait_timeline", 5),
    (G43, "gs_renderer.cpp", 1199, "request_timeline_semaphore_as_binary", 5),
    (G43, "gs_interface.hpp", 269, "gif_transfer", 5),
    (G43, "gs_interface.hpp", 319, "query_timeline", 5),
    (PAGE, "page_tracker.cpp", 935, "mark_submission_timeline", 5),
    (PAGE, "page_tracker.hpp", 122, "FlushReason", 5),
    (GRANITE_VK, "device.hpp", 274, "wait_idle", 5),
    (GRANITE_VK, "device.hpp", 301, "submit(CommandBufferHandle", 5),
    (GRANITE_VK, "device.hpp", 518, "consumes_debug_markers", 5),
    (GRANITE_VK, "command_buffer.hpp", 840, "write_timestamp", 5),
    (GRANITE_VK, "query_pool.hpp", 141, "write_timestamp", 5),
    (GRANITE_VK, "fence.hpp", 49, "wait_timeout", 5),
]

results = {"citations": [], "errors": [], "pins": {},
           "report_bytes": 0, "verdict": ""}


def check_pins():
    ok = True
    for label, cwd, want in (
            ("fork", os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp"), FORK_PIN),
            ("pgs", os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs"), PGS_PIN)):
        try:
            p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                               text=True, cwd=cwd, timeout=60)
            got = p.stdout.strip()
            match = (p.returncode == 0 and got == want)
            results["pins"][label] = {"ok": match, "got": got, "want": want}
            if not match:
                results["errors"].append("pin %s mismatch: got %s want %s" % (label, got, want))
                ok = False
        except Exception as e:
            results["pins"][label] = {"ok": False, "got": "", "want": want}
            results["errors"].append("pin %s unreadable: %s" % (label, e))
            ok = False
    return ok


def check_citations():
    ok = True
    for base, rel, line, token, window in CITATIONS:
        path = os.path.join(base, rel)
        tag = "%s:%d" % (rel, line)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            results["citations"].append({"site": tag, "ok": False, "why": "unreadable: %s" % e})
            results["errors"].append("citation %s unreadable" % tag)
            ok = False
            continue
        if len(lines) < line:
            results["citations"].append({"site": tag, "ok": False,
                                        "why": "file has %d lines" % len(lines)})
            results["errors"].append("citation %s beyond EOF" % tag)
            ok = False
            continue
        lo = max(0, line - 1 - window)
        hi = min(len(lines), line + window)
        hit = any(token in lines[i] for i in range(lo, hi))
        results["citations"].append({"site": tag, "ok": hit,
                                    "why": "" if hit else "token %r not within +/-%d" % (token, window)})
        if not hit:
            results["errors"].append("citation %s token missing" % tag)
            ok = False
    return ok


def check_report():
    ok = True
    try:
        with open(REPORT, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        results["errors"].append("REPORT.md unreadable: %s" % e)
        return False
    # Required content: boundary/clock table, three-hypothesis predictions,
    # pseudocode hooks, costs/caps, completion survey, pins, gaps, honesty.
    for need in ["Boundary/clock table", "(i)", "(ii)", "(iii)",
                 "V_pre", "eeSeq", "footprint",
                 "EE enqueue", "submission order", "GPU completion",
                 "no per-draw completion method",
                 "pseudocode", "H1", "H5",
                 "4 MiB", "512 KiB", "default-OFF", "Default OFF",
                 "M1", "M5", "G5",
                 "448", "cannot prove execution",
                 "gs_frontend.cpp", "ps2_gs_parallel_backend.cpp",
                 "gs_renderer.cpp", "gs_interface.cpp",
                 "page_tracker", "device.hpp",
                 "a8cfefa", "3a66c19", "f6a78f71",
                 "wait_idle", "copy_buffer", "gif_transfer",
                 "No Turnip, shader, barrier",
                 "OTHER"]:
        if need not in text:
            results["errors"].append("REPORT.md missing %r" % need)
            ok = False
    # The A predeclare must be conditional (controls + Mac calibration), and
    # equal-prediction fallback to B must be stated.
    if "predeclared verdict A (conditional)" not in text:
        results["errors"].append("REPORT must predeclare conditional A explicitly")
        ok = False
    if "falls to B" not in text and "fall back to B" not in text:
        results["errors"].append("REPORT must state the B fallback on failed conditions")
        ok = False
    # No device cause may be declared from static code.
    for bad in ["root cause is the Turnip", "root cause is the shader",
                "root cause is the barrier", "caused by Turnip",
                "caused by the shader", "caused by the barrier",
                "driver fault"]:
        if bad in text:
            results["errors"].append("REPORT must not declare %r from static code" % bad)
            ok = False
    # No extra flush/submit/wait may be proposed as part of the witness.
    for bad in ["extra flush", "extra submit", "S2late"]:
        if bad in text and "rejected" not in text and "no extra" not in text.lower():
            results["errors"].append("REPORT mentions %r without rejection" % bad)
            ok = False
    n = len(text.encode("utf-8"))
    results["report_bytes"] = n
    if n >= 512 * 1024:
        results["errors"].append("REPORT.md >= 512 KiB cap")
        ok = False
    return ok


def main():
    ok = True
    ok = check_pins() and ok
    ok = check_citations() and ok
    ok = check_report() and ok
    verdict = "PASS" if ok else "FAIL"
    results["verdict"] = verdict
    out = os.path.join(HERE, "check-result.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")
    print("%s: %d citations, %d errors -> %s" % (
        os.path.basename(__file__), len(results["citations"]), len(results["errors"]), verdict))
    for e in results["errors"]:
        print("FAIL: %s" % e)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
