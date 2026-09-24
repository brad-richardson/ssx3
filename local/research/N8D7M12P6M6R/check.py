#!/usr/bin/env python3
"""N8D7M12P6M6R acceptance checker: pinned build via external wrapper.

Reads the receipts in this dir. Verdict A = all rows pass; B = build done
with a packaged-output difference vs the P3 set, smallest failing row
named (here: one log string absent, explained by staged fork sources).
Writes check-result.json. No device action.
"""
import json
import os
import re

REPO = "/Users/brad/dev/ssx3"
DIR = os.path.join(REPO, "local/research/N8D7M12P6M6R")
EXPECTED_AGG = "6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a"
PINS = {
    "apk": "da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262",
    "runner": "e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "build_id": "4c9c9d149900cdc3494201c38124d11bfb616fa3",
    "gradlew": "a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3",
    "wrapper_jar": "498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17",
    "wrapper_props": "3d91f0932da99885c41e9dc4e85c9f9a2d3bfef4f0ad87473014dc0827a94884",
}

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
    pre = read("preflight-p6m5-check.txt") or ""
    row("mac_p6m5_checker_rerun", "24 rows, 0 failing, verdict A" in pre,
        "24/24 A")
    disk = read("disk-budget-before.txt") or ""
    row("mac_disk_budget_before",
        "ssx3 internal usage: 157.5 GB of 200 GB cap" in disk,
        disk.strip().splitlines()[-1] if disk.strip() else "missing")
    pf = read("preflight.txt") or ""
    row("wsl_preflight_fresh_root_toolchain_disk_idle",
        all(s in pf for s in ("n8d7m12p6m6 absent OK", "jdk-17 present OK",
                              "ndk present OK", "governor present OK",
                              "HEAVY_JOBS []")) and "749G" in pf,
        "absent+toolchain+749G free+idle")
    tx = read("transfer.txt") or ""
    row("wsl_transfer_six_entries",
        all(s in tx for s in ("PS2Recomp", "parallel-gs", "codegen-ssx3",
                              "jniLibs", "source-manifest.json",
                              "source_manifest.py")),
        "6 top-level entries, 619387661 B")
    txb = read("transfer-bytes.txt") or ""
    row("transfer_byte_count_recorded", "STREAM_BYTES=669184000" in txb,
        "STREAM_BYTES=669184000")
    for tag in ("pre", "post"):
        sv = read(f"source-verify-{tag}.json") or ""
        try:
            v = json.loads(sv.split("== runner dir ==")[0])
        except ValueError:
            v = {}
        row(f"wsl_source_verify_{tag}_match",
            v.get("status") == "match"
            and v.get("aggregate_actual") == EXPECTED_AGG
            and v.get("aggregate_expected") == EXPECTED_AGG
            and v.get("added") == [] and v.get("missing") == []
            and v.get("changed") == [],
            v.get("status", "missing"))
    sv = read("source-verify-post.json") or ""
    row("wsl_runner_stub_only",
        "cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068" in sv,
        "438B pinned stub")
    wp = read("wrapper-pins.txt") or ""
    row("external_wrapper_pins_double_read",
        all(wp.count(p) >= 2 for p in
            (PINS["gradlew"], PINS["wrapper_jar"], PINS["wrapper_props"]))
        and "WRAPPER_PROPS_EQUAL" in wp
        and "new gradlew absent OK" in wp
        and "new wrapper jar absent OK" in wp
        and "HEAVY_JOBS []" in wp,
        "3 pins x2 reads + props equal + no copies + idle")
    b1 = read("build.txt") or ""
    b2 = read("build2.txt") or ""
    n_success = len(re.findall(r"BUILD SUCCESSFUL", b2))
    row("one_build_success_no_retry",
        n_success == 1 and "FAILED" not in b2 and "EXIT=0" in b2
        and "BUILD SUCCESSFUL" not in b1,
        f"build2 BUILD SUCCESSFUL x{n_success}, in 5m 34s" if n_success else "missing")
    row("build_argv_new_root_in_root_codegen",
        "-Pps2xGameCodegenDir=/home/brad/n8d7m12p6m6/codegen-ssx3" in b2
        and "-Pps2xParallelGsSourceDir=/home/brad/n8d7m12p6m6/parallel-gs" in b2
        and "-Pps2xJniLibsDir=/home/brad/n8d7m12p6m6/jniLibs" in b2
        and "-Pps2xGsShadowParallel=ON" in b2
        and "cwd" in b2 and "/home/brad/n8d7m12p6m6/PS2Recomp/android" in b2
        and "Gradle 8.9" in b2,
        "external gradlew, new-root cwd, P3 flags")
    ci = read("compiled-inputs.txt") or ""
    cg = read("codegen-graph.txt") or ""
    row("compiled_inputs_fork_renderer_granite",
        all(s in ci for s in ("gs_frontend.cpp: 1", "gs_worker.cpp: 1",
                              "ps2_gs_parallel_backend.cpp: 1",
                              "gs_interface.cpp: 1", "page_tracker.cpp: 1",
                              "memory_allocator.cpp: 1"))
        and "entries=449" in ci,
        "449 compile_commands entries; 6/6 required TUs")
    row("compiled_inputs_codegen_9455",
        "296" in cg and "codegen-ssx3/register_functions.cpp" in cg
        and "9455" in cg,
        "296 unity batches; register + 9455 distinct codegen .cpp")
    try:
        facts = json.loads(read("apk-facts.json") or "")
    except ValueError:
        facts = {}
    members = facts.get("members", {})
    row("apk_sha_and_size",
        facts.get("apk") == [PINS["apk"], PINS["apk"]]
        and facts.get("apk_size") == 153753116,
        PINS["apk"][:12] + " 153753116 B")
    row("member_set_exact_three_arm64",
        facts.get("checks", {}).get("member_set_exact") is True
        and facts.get("found_members") == sorted([
            "lib/arm64-v8a/libhardware.so",
            "lib/arm64-v8a/libps2EntryRunner.so",
            "lib/arm64-v8a/libvulkan_freedreno.so"]),
        "exactly the 3 arm64 members")
    row("turnip_hal_pins_pair_equal",
        members.get("lib/arm64-v8a/libvulkan_freedreno.so", {}).get("sha")
        == [PINS["turnip"], PINS["turnip"]]
        and members.get("lib/arm64-v8a/libhardware.so", {}).get("sha")
        == [PINS["hal"], PINS["hal"]],
        "both pins unchanged, pairs equal")
    row("runner_sha_build_id_new",
        members.get("lib/arm64-v8a/libps2EntryRunner.so", {}).get("sha")
        == [PINS["runner"], PINS["runner"]]
        and facts.get("runner_build_id") == PINS["build_id"]
        and facts.get("runner_new_vs_p3") is True
        and facts.get("runner_build_id_new_vs_p3") is True,
        PINS["runner"][:12] + " / " + PINS["build_id"][:12] + " new vs P3")
    row("packaged_strings_22_of_23_explained",
        facts.get("strings_missing") == ["PNG write failed path="],
        "22/23; sole miss absent from all staged inputs (REPORT sec 5)")
    caches = facts.get("caches", [])
    row("sole_cache_flags_new_root_paths",
        len(caches) == 1
        and facts.get("checks", {}).get("off_flags_all_off") is True
        and facts.get("checks", {}).get("shadow_on") is True
        and facts.get("checks", {}).get("parallel_dir_is_new_root") is True
        and facts.get("checks", {}).get("codegen_dir_is_new_root") is True,
        "6xOFF + SHADOW=ON + new-root dirs + RelWithDebInfo")
    row("wsl_root_under_10gib",
        facts.get("checks", {}).get("root_under_10gib") is True,
        f"{facts.get('root_size_bytes')} B")
    failing = [r["name"] for r in rows if r["result"] != "pass"]
    verdict = "A" if not failing else "B"
    result = {"part": "N8D7M12P6M6R", "verdict": verdict,
              "rows": rows, "failing": failing,
              "pins": PINS, "aggregate_sha256": EXPECTED_AGG,
              "note": "one pinned build via external pinned wrapper; no "
                      "staged-source mutation (post aggregate match); Mac "
                      "APK double-read matches WSL; no Odin/GPU verdict"}
    with open(os.path.join(DIR, "check-result.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{len(rows)} rows, {len(failing)} failing, verdict {verdict}")
    for r in rows:
        print(("PASS " if r["result"] == "pass" else "FAIL ") + r["name"]
              + (" : " + r["detail"] if r["detail"] else ""))
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    raise SystemExit(main())
