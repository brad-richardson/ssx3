#!/usr/bin/env python3
"""N8D7M12P6M6R acceptance checker: staged-build stop at missing gradlew.

Reads the receipts in this dir. Verdict C = stopped on first failure per
brief (staged fork has no android/gradlew; no assembleRelease attempted).
Writes check-result.json. No device action.
"""
import json
import os

REPO = "/Users/brad/dev/ssx3"
DIR = os.path.join(REPO, "local/research/N8D7M12P6M6R")
EXPECTED_AGG = "6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a"

rows = []


def row(name, ok, detail=""):
    rows.append({"name": name, "result": "pass" if ok else "fail",
                 "detail": detail})
    return ok


def read(name):
    p = os.path.join(DIR, name)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    # 1. Mac P6M5 checker re-run still 24/24 A.
    pre = read("preflight-p6m5-check.txt") or ""
    row("mac_p6m5_checker_rerun",
        "24 rows, 0 failing, verdict A" in pre,
        "24 rows, 0 failing, verdict A" if "24 rows" in pre else "missing")
    # 2. Mac disk budget before step.
    disk = read("disk-budget-before.txt") or ""
    row("mac_disk_budget_before",
        "ssx3 internal usage: 157.5 GB of 200 GB cap" in disk,
        disk.strip().splitlines()[-1] if disk.strip() else "missing")
    # 3. WSL preflight: fresh root absent, toolchain, disk, no heavy job.
    pf = read("preflight.txt") or ""
    row("wsl_preflight_fresh_root_toolchain_disk_idle",
        all(s in pf for s in ("n8d7m12p6m6 absent OK", "jdk-17 present OK",
                              "ndk present OK", "governor present OK",
                              "HEAVY_JOBS []"))
        and "749G" in pf,
        "absent+toolchain+749G free+idle" if pf else "missing")
    # 4. Transfer delivered exactly the six top-level entries.
    tx = read("transfer.txt") or ""
    row("wsl_transfer_six_entries",
        all(s in tx for s in ("PS2Recomp", "parallel-gs", "codegen-ssx3",
                              "jniLibs", "source-manifest.json",
                              "source_manifest.py")),
        tx.replace("\n", ",")[:160] if tx else "missing")
    txb = read("transfer-bytes.txt") or ""
    row("transfer_byte_count_recorded", "STREAM_BYTES=669184000" in txb,
        "STREAM_BYTES=669184000" if "STREAM_BYTES" in txb else "missing")
    # 5. WSL pre-build collector verify: match + expected aggregate + stub.
    sv = read("source-verify-pre.json") or ""
    try:
        v = json.loads(sv.split("== runner dir ==")[0])
    except ValueError:
        v = {}
    row("wsl_source_verify_pre_match",
        v.get("status") == "match"
        and v.get("aggregate_actual") == EXPECTED_AGG
        and v.get("aggregate_expected") == EXPECTED_AGG
        and v.get("added") == [] and v.get("missing") == []
        and v.get("changed") == [],
        v.get("status", "missing"))
    row("wsl_runner_stub_only",
        "cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068"
        in sv and "register_functions.cpp" in sv,
        "438B pinned stub" if "cf62c485" in sv else "missing")
    # 6. Build step: stopped, zero assembleRelease attempts.
    build = read("build.txt") or ""
    row("build_blocked_missing_gradlew_stop",
        "./gradlew: No such file or directory" in build
        and "BUILD SUCCESSFUL" not in build
        and "assembleRelease.log" not in build,
        "gradlew absent; no build attempted")
    failing = [r["name"] for r in rows if r["result"] != "pass"]
    # The stop row passing means the stop was correctly taken; verdict is
    # still C because no package was produced.
    result = {"part": "N8D7M12P6M6R", "verdict": "C",
              "rows": rows, "failing": failing,
              "stop": "staged fork lacks android/gradlew wrapper; "
                      "zero assembleRelease attempts; no repair loop",
              "note": "transfer + pre-build source verify pass; no APK, "
                      "no binary, no game bytes in git; WSL root left with "
                      "verified pre-build bytes only"}
    with open(os.path.join(DIR, "check-result.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{len(rows)} rows, {len(failing)} failing, verdict C (stop)")
    for r in rows:
        print(("PASS " if r["result"] == "pass" else "FAIL ") + r["name"]
              + (" : " + r["detail"] if r["detail"] else ""))


if __name__ == "__main__":
    main()
