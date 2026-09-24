#!/usr/bin/env python3
"""N8D7M7 verifier (PARTIAL gate): source-citation rows + awardable-category
uniqueness + rejection of equal-prediction/contradictory categories.

Read-only: inspects pinned worktree sources and local/research/N8D7M7/REPORT.md.
Emits check-result.json; exit 0 on PASS, 1 on FAIL. Stdlib only.
"""
import json
import os
import sys

FORK = os.path.expanduser("~/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/src/lib/gs")
G43 = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs/gs")
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "REPORT.md")

# (base_dir, rel_file, cited_line_1based, expected_token, window)
CITATIONS = [
    (FORK, "gs_frontend.cpp", 929, "processGIFPacket", 5),
    (FORK, "gs_frontend.cpp", 947, "m_submitCount.fetch_add", 5),
    (FORK, "gs_frontend.cpp", 178, "drainQueue", 5),
    (FORK, "gs_frontend.cpp", 769, "vsyncTick.load", 5),
    (FORK, "gs_frontend.cpp", 809, "m_backend->Flush", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 441, "selectedRequested", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 452, "m_iface->flush", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 601, "submit(cmd)", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 602, "wait_idle", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 621, "map_host_buffer", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 728, "oracle_input_equal", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 897, "RawGifPacket", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 105, "PGS_BLOCKS_PER_PAGE", 5),
    (FORK, "ps2_gs_parallel_backend.cpp", 199, "fbp << 5u", 5),
    (G43, "gs_renderer.cpp", 4816, "copy_buffer", 5),
    (G43, "gs_renderer.cpp", 4813, "barrier", 5),
    (G43, "gs_renderer.cpp", 4282, "buffers.gpu", 5),
    (G43, "gs_renderer.cpp", 4834, "sample_crtc_circuit", 5),
    (G43, "gs_renderer.cpp", 5076, "selected_capture_status = 2", 5),
    (G43, "gs_renderer.cpp", 5354, "flush_submit(0)", 5),
    (G43, "gs_renderer.cpp", 1116, "flush_submit", 5),
    (G43, "gs_interface.cpp", 5162, "flush_submit(value)", 5),
    (G43, "gs_interface.cpp", 5576, "renderer.vsync", 5),
]

# Awardable full-448-census signatures: (S1, S2same, Gc, SHAfam, decode).
# sparse = active<=100/448, broad = active>=250/448. Only W and C are
# awardable. O is UNRESOLVED (its T4-broad candidate prediction equals
# delayed/missing work under an intervention) and D is IMPOSSIBLE
# (broad-bytes + identical decoder + sparse census is self-contradictory).
AWARDABLE = {
    "W": ("sparse", "sparse", "sparse", "sparse", "agree"),
    "C": ("sparse", "sparse", "broad", "sparse", "agree"),
}
UNRESOLVED = {"O"}
IMPOSSIBLE = {"D"}

# Tap rows mirrored from REPORT §3: name -> (label, pairs_claimed).
# Pairs may only name awardable categories. T4 is an intervention and must
# claim nothing; T1/T5/X* are OTHER/consistency-only.
TAPS = {
    "T1": ("OTHER", set()),
    "T2": ("OBS", {"W-C"}),
    "T3": ("OBS", {"W-C"}),
    "T4": ("INTERVENTION", set()),
    "T5": ("OTHER", set()),
    "X1": ("OTHER", set()),
    "X2": ("OTHER", set()),
    "X3": ("OTHER", set()),
}

results = {"citations": [], "errors": [], "signature_pairs": [],
           "report_bytes": 0, "verdict": ""}


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


def check_signatures():
    ok = True
    # Awardable categories must be pairwise unique ...
    seen = {}
    for cat, sig in AWARDABLE.items():
        if sig in seen:
            results["errors"].append("awardable %s and %s share signature %r" % (seen[sig], cat, sig))
            ok = False
        else:
            seen[sig] = cat
    cats = sorted(AWARDABLE)
    for i in range(len(cats)):
        for j in range(i + 1, len(cats)):
            a, b = AWARDABLE[cats[i]], AWARDABLE[cats[j]]
            if not any(x != y for x, y in zip(a, b)):
                results["errors"].append("awardable pair %s-%s not separated" % (cats[i], cats[j]))
                ok = False
    results["signature_pairs"] = ["%s-%s:separated" % (cats[i], cats[j])
                                  for i in range(len(cats)) for j in range(i + 1, len(cats))]
    # ... and neither O (equal-prediction) nor D (contradictory) may be
    # awardable alongside them.
    for cat in UNRESOLVED | IMPOSSIBLE:
        if cat in AWARDABLE:
            results["errors"].append("category %s must not be awardable" % cat)
            ok = False
    return ok


def check_taps():
    ok = True
    awardable = set(AWARDABLE)
    for name, (label, seps) in TAPS.items():
        for pair in seps:
            letters = set(pair.split("-"))
            if not letters <= awardable:
                results["errors"].append(
                    "tap %s claims separation %s involving unresolvable/impossible category" % (name, pair))
                ok = False
        if not seps and label not in ("OTHER", "INTERVENTION"):
            results["errors"].append("tap %s separates nothing but is labeled %s" % (name, label))
            ok = False
        if seps and label in ("OTHER", "INTERVENTION"):
            results["errors"].append("tap %s labeled %s but claims separations" % (name, label))
            ok = False
    if TAPS.get("T4", ("", set()))[0] != "INTERVENTION":
        results["errors"].append("T4 S2late must be labeled INTERVENTION")
        ok = False
    if not any("W-C" in seps for _, seps in TAPS.values()):
        results["errors"].append("no tap separates the surviving W-C pair")
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
    for need in ["**W**", "**C**", "**O UNRESOLVED**", "**D IMPOSSIBLE**",
                 "**OTHER**", "ordering-unresolved", "decode-contradiction",
                 "equally consistent", "logically impossible", "INTERVENTION",
                 "No device brief", "448",
                 "gs_frontend.cpp", "ps2_gs_parallel_backend.cpp",
                 "gs_renderer.cpp", "gs_interface.cpp", "post_tick",
                 "a8cfefa", "3a66c19"]:
        if need not in text:
            results["errors"].append("REPORT.md missing %r" % need)
            ok = False
    if len(text.encode("utf-8")) >= 512 * 1024:
        results["errors"].append("REPORT.md >= 512 KiB cap")
        ok = False
    results["report_bytes"] = len(text.encode("utf-8"))
    return ok


def main():
    ok = True
    ok = check_citations() and ok
    ok = check_signatures() and ok
    ok = check_taps() and ok
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
