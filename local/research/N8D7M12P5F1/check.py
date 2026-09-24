#!/usr/bin/env python3
"""N8D7M12 Part 5F1 checker: verifies pinned citations/claims for the
read-only GPU hash/sync path audit.

Read-only (git rev-parse/status + file reads). No build/replay/device.
Verdicts: A = map grounded; B = provenance/edge unproved; OTHER = access.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
FORK = Path.home() / "dev/ssx3-work/N8D7M12P2/PS2Recomp"
PGS = Path.home() / "dev/ssx3-work/N8D7F/parallel-gs"
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})


def lines(path, lo, hi):
    try:
        with open(path, errors="replace") as f:
            all_lines = f.read().splitlines()
        return "\n".join(all_lines[lo - 1:hi])
    except OSError as e:
        return f"OTHER: {e}"


def has(path, lo, hi, *needles):
    text = lines(path, lo, hi)
    return all(n in text for n in needles), text[:120]


def git(args, cwd):
    try:
        r = subprocess.run(["git", "-C", str(cwd)] + args,
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"OTHER: {e}"


def main():
    report = EV / "REPORT.md"
    check("report_present", report.exists(), str(report))

    head = git(["rev-parse", "HEAD"], FORK)
    check("fork_pin_a608ed1", head.startswith("a608ed1"), head)
    st = git(["status", "--short"], FORK)
    check("fork_clean", st == "" and not st.startswith("OTHER"), st[:200])

    phead = git(["rev-parse", "HEAD"], PGS)
    check("pgs_pin_3a66c19", phead.startswith("3a66c19"), phead)
    pst = git(["status", "--short"], PGS)
    check("pgs_dirty_noted",
          "gs_renderer.cpp" in pst and "gs_interface.cpp" in pst,
          pst.replace("\n", "; ")[:300])

    core = FORK / "ps2xRuntime/src/lib/gs/gs_replay_core.cpp"
    fe = FORK / "ps2xRuntime/src/lib/gs/gs_frontend.cpp"
    be = FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"
    main_cpp = FORK / "ps2xRuntime/src/main.cpp"
    vq = FORK / "ps2xRuntime/include/ps2_vq.h"

    cites = [
        ("e01_entry", main_cpp, 215, 216, ["PS2X_GS_REPLAY_ONDEVICE"]),
        ("e01_call", main_cpp, 239, 239, ["ps2x_gs_replay_run()"]),
        ("e02_queued", core, 178, 178, ["queued"]),
        ("e03_fnv", core, 25, 34, ["2166136261u", "16777619u"]),
        ("e04_priv", core, 84, 92, ["privHash", "vsyncTick"]),
        ("e05_present", core, 94, 113, ["presentHash", "640u * 4u"]),
        ("e06_drain", core, 443, 443, ["drainQueue()"]),
        ("e07_vram", core, 450, 458, ["refreshDisplaySnapshot",
                                      "lockDisplaySnapshot",
                                      "unlockDisplaySnapshot"]),
        ("e08_frame", core, 459, 472, ["presentForDiagnostics",
                                       "GB4_FRAME"]),
        ("e09_out", core, 699, 705, ["PS2X_GS_REPLAY_OUT"]),
        ("e10_fence", fe, 178, 190, ["Fence", "rpc->wait()"]),
        ("e11_snap", fe, 377, 390, ["DebugReadback", "SnapshotVram"]),
        ("e12_diag", fe, 839, 864, ["Flush()", "Presentation",
                                    "Present(request)"]),
        ("e13_noop", be, 427, 429, ["Flush() override {}",
                                    "Sync(GSSyncReason) override {}"]),
        ("e14_present", be, 431, 453, ["flush()", "vsync(vsync)"]),
        ("e14_wait", be, 601, 602, ["submit(cmd)", "wait_idle()"]),
        ("e15_pack", be, 819, 829, ["640u", "displayFbp"]),
        ("e16_snapvram", be, 867, 886, ["map_vram_read", "memcpy"]),
        ("e17_init", be, 916, 936, ["initTurnipLoader",
                                    "init_loader(nullptr)"]),
        ("e21_ppm", vq, 115, 139, ["P6", "640u"]),
        ("flag_sel", be, 441, 442, ["vsyncTick == 2050u",
                                    'strcmp(selectedEnv, "1")']),
        ("flag_tile", be, 443, 444, ["vsyncTick == 2050u",
                                     "tileEnv"]),
        ("flag_oracle_in_selected", be, 603, 603, ["if (selectedRequested)"]),
        ("flag_oracle", be, 667, 668, ["PS2X_N8D7L_ORACLE",
                                       "oracleRequested"]),
    ]
    for name, path, lo, hi, needles in cites:
        ok, _ = has(path, lo, hi, *needles)
        check(name, ok, f"{path.name}:{lo}-{hi}")

    # flag-gating completeness: exactly 3 getenv sites in fork runtime
    hits = []
    scan_err = ""
    for p in (FORK / "ps2xRuntime").rglob("*.cpp"):
        try:
            text = p.read_text(errors="replace")
        except OSError as e:
            scan_err = f"OTHER: {e}"
            break
        for i, ln in enumerate(text.splitlines(), 1):
            if ("PS2X_N8D7F_SELECTED_CAPTURE" in ln
                    or "PS2X_N8D7L_ORACLE" in ln
                    or "PS2X_N8D5_TILE_CAPTURE" in ln):
                hits.append(f"{p.name}:{i}")
    if scan_err:
        check("flag_sites_3", False, scan_err)
    else:
        check("flag_sites_3", len(hits) == 3, "; ".join(hits))

    # ON/OFF receipt pins restated in REPORT
    try:
        text = report.read_text(errors="replace")
    except OSError as e:
        check("receipt_pins", False, f"OTHER: {e}")
    else:
        check("receipt_pins", all(s in text for s in
                                  ["0e89a493", "19738cc3", "39b70d67",
                                   "5e0caca3", "tick850", "41/41",
                                   "19/41", "25/41"]),
              "on/off hashes + comparison in REPORT")

    verdict = "A" if all(c["ok"] for c in CHECKS) else "B"
    if any(c["detail"].startswith("OTHER") for c in CHECKS):
        verdict = "OTHER"
    EV.joinpath("check-result.json").write_text(
        json.dumps({"verdict": verdict, "checks": CHECKS}, indent=2))
    print(json.dumps({"verdict": verdict,
                      "pass": sum(1 for c in CHECKS if c["ok"]),
                      "total": len(CHECKS)}, indent=2))
    for c in CHECKS:
        if not c["ok"]:
            print(f"FAIL {c['name']}: {c['detail']}")
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    sys.exit(main())
