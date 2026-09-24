#!/usr/bin/env python3
"""N8D7M8 verifier: pins + cited source rows + A/B/OTHER table discipline.

Read-only: inspects pinned worktree sources and local/research/N8D7M8/REPORT.md.
Emits check-result.json; exit 0 on PASS, 1 on FAIL. Stdlib only.

It cannot prove execution from source strings alone: it verifies that the
cited source rows exist at the pinned revs, that the pins match, and that the
REPORT's A/B/OTHER table does not award A on host-only counts, 8 words, a
later tick, or an extra flush. Runtime execution and nonperturbation are for
the orchestrator's gate, not this script.
"""
import json
import os
import subprocess
import sys

FORK = os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/src/lib/gs")
G43 = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs/gs")
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
    (FORK, "gs_frontend.cpp", 769, "vsyncTick", 5),
    (FORK, "gs_frontend.cpp", 809, "m_backend->Flush", 5),
    (FORK, "gs_frontend.cpp", 178, "drainQueue", 5),
    (FORK, "gs_frontend.cpp", 197, "processGIFPacket", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 441, "selectedRequested", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 452, "m_iface->flush", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 601, "submit(cmd)", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 602, "wait_idle", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 621, "map_host_buffer", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 728, "oracle_input_equal", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 897, "RawGifPacket", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 901, "gif_transfer", 5),
    (G43, "gs_renderer.cpp", 4816, "copy_buffer", 5),
    (G43, "gs_renderer.cpp", 4813, "barrier", 5),
    (G43, "gs_renderer.cpp", 4282, "buffers.gpu", 5),
    (G43, "gs_renderer.cpp", 4316, "cmd.draw(3)", 5),
    (G43, "gs_renderer.cpp", 4834, "sample_crtc_circuit", 5),
    (G43, "gs_renderer.cpp", 5076, "selected_capture_status = 2", 5),
    (G43, "gs_renderer.cpp", 5354, "flush_submit(0)", 5),
    (G43, "gs_renderer.cpp", 1116, "flush_submit", 5),
    (G43, "gs_renderer.cpp", 45, "insert_label", 5),
    (G43, "gs_renderer.cpp", 1052, "wait_timeline", 5),
    (G43, "gs_interface.cpp", 5161, "mark_submission_timeline", 5),
    (G43, "gs_interface.cpp", 5191, "gif_transfer", 5),
    (G43, "gs_interface.cpp", 5576, "renderer.vsync", 5),
    (G43, "gs_interface.hpp", 142, "deterministic_timeline_query", 5),
    (G43, "gs_interface.hpp", 160, "capture_selected_input", 5),
    (G43, "gs_interface.hpp", 269, "gif_transfer", 5),
    (GRANITE_VK, "device.hpp", 274, "wait_idle", 5),
    (GRANITE_VK, "command_buffer.hpp", 840, "write_timestamp", 5),
    (GRANITE_VK, "command_buffer.hpp", 364, "copy_buffer", 5),
]

results = {"citations": [], "errors": [], "pins": {}, "report_bytes": 0,
           "verdict": ""}


def check_pins():
    ok = True
    for label, cwd, want in (("fork", os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp"), FORK_PIN),
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
            results["citations"].append({"site": tag, "ok": False, "why": "file has %d lines" % len(lines)})
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
    # Required content: A/B/OTHER discipline, three cases, full census,
    # verdict B, Mac-only experiment, honesty about static analysis.
    for need in ["**A**", "**B**", "**OTHER**", "(i)", "(ii)", "(iii)",
                 "448", "Verdict: B", "EXP1", "Mac-only",
                 "cannot prove execution from source strings alone",
                 "gs_frontend.cpp", "ps2_gs_parallel_backend.cpp",
                 "gs_renderer.cpp", "gs_interface.cpp",
                 "a8cfefa", "3a66c19", "f6a78f71",
                 "positive/negative controls", "wait_idle",
                 "copy_buffer", "gif_transfer", "L1", "L7"]:
        if need not in text:
            results["errors"].append("REPORT.md missing %r" % need)
            ok = False
    # The A table must not be awarded on host-only evidence: reject any A
    # verdict, and require each insufficient class to be labeled as such.
    if "Verdict: A" in text:
        results["errors"].append("REPORT must not award A (equal predictions -> B)")
        ok = False
    for need in ["host submits", "8-word", "later-tick", "extra flush",
                 "Insufficient", "Intervention", "OTHER"]:
        if need not in text:
            results["errors"].append("REPORT.md missing A-rejection marker %r" % need)
            ok = False
    # No device cause may be declared from static code: the denial sentence
    # must be present, and no affirmative causal award may appear.
    if "No Turnip, shader, or barrier cause" not in text:
        results["errors"].append("REPORT must deny a device cause from static code")
        ok = False
    for bad in ["root cause is the Turnip", "root cause is the shader",
                "root cause is the barrier", "caused by Turnip",
                "caused by the shader", "caused by the barrier"]:
        if bad in text:
            results["errors"].append("REPORT must not declare a %r from static code" % bad)
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
