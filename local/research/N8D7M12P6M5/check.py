#!/usr/bin/env python3
"""N8D7M12 Part 6M5 checker: staged source-root invariants + manifest verify.

Reads only. Re-runs `source_manifest.py verify` against the four staged
roots and asserts required path/SHA/count invariants, stage-copy parity on
pinned files, and manifest-verify match. Writes check-result.json.
Source manifest itself is NOT proof of compilation or historical provenance.
"""
import hashlib
import json
import os
import subprocess
import sys
import zipfile

REPO = "/Users/brad/dev/ssx3"
DIR = os.path.join(REPO, "local/research/N8D7M12P6M5")
STAGE = os.path.join(DIR, "stage")
MANIFEST = os.path.join(DIR, "source-manifest.json")
FORK_SRC = "/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp"
PARALLEL_SRC = "/Users/brad/dev/ssx3-work/N8D7F/parallel-gs"
CODEGEN_SRC = "/Users/brad/dev/ssx3-work/codegen-ssx3"
TURNIP_SRC = "/Users/brad/dev/ssx3-work/G43/inputs/libvulkan_freedreno.so"
APK = "/Users/brad/dev/ssx3-work/N8D7M12P3/app-release.apk"

PINS = {
    "fork_head_prefix": "4fa0df1",
    "fork_head_full": "4fa0df1811df4381aa3ba95aa3fcd1310afd1d25",
    "runner_blob": "85cc2e348d60cfae0a4f220fc2a0535f7a756fa2",
    "runner_stub_sha": "cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068",
    "renderer_cpp_sha": "85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e",
    "interface_hpp_sha": "3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d",
    "shader_header_sha": "19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9",
    "codegen_register_sha": "8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3",
    "turnip_sha": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal_member_sha": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "hal_member_size": 7112,
    "aggregate": "6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a",
}
REQUIRED = [
    ("fork", "ps2xRuntime/src/lib/gs/gs_frontend.cpp"),
    ("fork", "ps2xRuntime/src/lib/gs/gs_worker.cpp"),
    ("fork", "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"),
    ("fork", "ps2xRuntime/src/main.cpp"),
    ("fork", "ps2xRuntime/src/runner/register_functions.cpp"),
    ("parallel", "gs/gs_interface.cpp"),
    ("parallel", "gs/gs_interface.hpp"),
    ("parallel", "gs/page_tracker.cpp"),
    ("parallel", "gs/page_tracker.hpp"),
    ("parallel", "gs/gs_renderer.cpp"),
    ("parallel", "gs/n8d5_tile_spirv.hpp"),
    ("parallel", "gs/shaders/n8d5_tile.comp"),
    ("parallel", "Granite/vulkan/memory_allocator.cpp"),
    ("codegen", "register_functions.cpp"),
    ("jni", "arm64-v8a/libvulkan_freedreno.so"),
    ("jni", "arm64-v8a/libhardware.so"),
]

rows = []


def row(name, ok, detail=""):
    rows.append({"name": name, "result": "pass" if ok else "fail",
                 "detail": detail})
    return ok


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def git(args, cwd):
    p = subprocess.run(["git", "-C", cwd] + args, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=60)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def main():
    ok_all = True

    # 1. Fork pins (independent re-read of source).
    rc, head = git(["rev-parse", "HEAD"], FORK_SRC)
    head = head.strip()
    ok_all &= row("fork_head_pin", rc == 0 and head == PINS["fork_head_full"], head[:12])
    rc, st = git(["status", "--short"], FORK_SRC)
    ok_all &= row("fork_no_tracked_mods", rc == 0 and st.strip() == "?? local/",
                  st.strip().replace("\n", ",")[:64])
    rc, diff = git(["diff", "--stat", "14b1e5cb", "HEAD", "--",
                    "ps2xRuntime/src/runner"], FORK_SRC)
    ok_all &= row("fork_runner_diff_empty", rc == 0 and diff.strip() == "",
                  repr(diff.strip()[:64]))
    rc, tree = git(["ls-tree", "-r", "HEAD", "--", "ps2xRuntime/src/runner"],
                   FORK_SRC)
    ok_all &= row("fork_runner_single_stub_blob",
                  rc == 0 and PINS["runner_blob"] in tree
                  and tree.strip().count("\n") == 0,
                  tree.strip()[:96])

    # 2. Staged fork export: no .git, no local/receipts, stub exact.
    froot = os.path.join(STAGE, "PS2Recomp")
    ok_all &= row("stage_fork_no_git",
                  not os.path.exists(os.path.join(froot, ".git")), "")
    ok_all &= row("stage_fork_no_receipts",
                  not os.path.exists(os.path.join(froot, "local")), "")
    stub = os.path.join(froot, "ps2xRuntime/src/runner/register_functions.cpp")
    ok_all &= row("stage_fork_stub_exact",
                  os.path.isfile(stub) and os.path.getsize(stub) == 438
                  and sha(stub) == PINS["runner_stub_sha"],
                  sha(stub)[:12] if os.path.isfile(stub) else "missing")
    ok_all &= row("stage_fork_runner_dir_single",
                  sorted(os.listdir(os.path.join(froot, "ps2xRuntime/src/runner")))
                  == ["register_functions.cpp"],
                  "")

    # 3. Stage-copy parity on pinned files (source vs stage bytes).
    pairs = [
        (os.path.join(PARALLEL_SRC, "gs/gs_renderer.cpp"),
         os.path.join(STAGE, "parallel-gs/gs/gs_renderer.cpp"),
         PINS["renderer_cpp_sha"]),
        (os.path.join(PARALLEL_SRC, "gs/gs_interface.hpp"),
         os.path.join(STAGE, "parallel-gs/gs/gs_interface.hpp"),
         PINS["interface_hpp_sha"]),
        (os.path.join(PARALLEL_SRC, "gs/n8d5_tile_spirv.hpp"),
         os.path.join(STAGE, "parallel-gs/gs/n8d5_tile_spirv.hpp"),
         PINS["shader_header_sha"]),
        (os.path.join(CODEGEN_SRC, "register_functions.cpp"),
         os.path.join(STAGE, "codegen-ssx3/register_functions.cpp"),
         PINS["codegen_register_sha"]),
        (TURNIP_SRC,
         os.path.join(STAGE, "jniLibs/arm64-v8a/libvulkan_freedreno.so"),
         PINS["turnip_sha"]),
    ]
    for src, dst, pin in pairs:
        match = (os.path.isfile(src) and os.path.isfile(dst)
                 and sha(src) == pin and sha(dst) == pin)
        ok_all &= row("parity_" + os.path.basename(dst) + "_matches_pin", match,
                      sha(dst)[:12] if os.path.isfile(dst) else "missing")

    # 4. HAL member: APK double-read vs staged bytes.
    with zipfile.ZipFile(APK) as z:
        m1 = z.read("lib/arm64-v8a/libhardware.so")
        m2 = z.read("lib/arm64-v8a/libhardware.so")
    hstaged = sha(os.path.join(STAGE, "jniLibs/arm64-v8a/libhardware.so"))
    ok_all &= row("hal_member_double_read_pin",
                  hashlib.sha256(m1).hexdigest() == PINS["hal_member_sha"]
                  and hashlib.sha256(m2).hexdigest() == PINS["hal_member_sha"]
                  and len(m1) == PINS["hal_member_size"], hstaged[:12])
    ok_all &= row("hal_staged_matches_member",
                  hstaged == PINS["hal_member_sha"]
                  and os.path.getsize(
                      os.path.join(STAGE, "jniLibs/arm64-v8a/libhardware.so"))
                  == PINS["hal_member_size"], hstaged[:12])
    ok_all &= row("jni_scope_exactly_two_members",
                  sorted(os.listdir(os.path.join(STAGE, "jniLibs/arm64-v8a")))
                  == ["libhardware.so", "libvulkan_freedreno.so"], "")

    # 5. Manifest: aggregate, counts, verify match, required entries.
    m = json.load(open(MANIFEST, encoding="utf-8"))
    ok_all &= row("manifest_aggregate_pin",
                  m.get("aggregate_sha256") == PINS["aggregate"],
                  m.get("aggregate_sha256", "")[:12])
    counts = m.get("counts", {})
    total_files = sum(counts.get(s, {}).get("files", 0) for s in counts)
    total_bytes = sum(counts.get(s, {}).get("bytes", 0) for s in counts)
    ok_all &= row("manifest_counts_caps",
                  total_files <= 30000 and total_bytes <= 2000000000,
                  f"files={total_files} bytes={total_bytes}")
    ok_all &= row("manifest_expected_counts",
                  counts.get("fork", {}).get("files") == 323
                  and counts.get("parallel", {}).get("files") == 16429
                  and counts.get("codegen", {}).get("files") == 9457
                  and counts.get("jni", {}).get("files") == 2,
                  json.dumps({s: counts.get(s, {}).get("files") for s in counts}))
    bykey = {(e["scope"], e["path"]): e for e in m["entries"]}
    missing = [f"{s}:{p}" for s, p in REQUIRED if (s, p) not in bykey]
    ok_all &= row("manifest_required_paths_present", not missing,
                  ";".join(missing[:6]))
    runner = [k for k in bykey
              if k[0] == "fork" and (k[1] == "ps2xRuntime/src/runner"
                                     or k[1].startswith("ps2xRuntime/src/runner/"))]
    ok_all &= row("manifest_runner_stub_only",
                  runner == [("fork", "ps2xRuntime/src/runner/register_functions.cpp")]
                  and bykey[runner[0]]["sha256"] == PINS["runner_stub_sha"],
                  str(len(runner)))
    receipts = [k for k in bykey if "local/receipts" in k[1]]
    ok_all &= row("manifest_no_receipts", not receipts, str(len(receipts)))
    pinned_pairs = {
        ("parallel", "gs/gs_renderer.cpp"): PINS["renderer_cpp_sha"],
        ("parallel", "gs/gs_interface.hpp"): PINS["interface_hpp_sha"],
        ("parallel", "gs/n8d5_tile_spirv.hpp"): PINS["shader_header_sha"],
        ("codegen", "register_functions.cpp"): PINS["codegen_register_sha"],
        ("jni", "arm64-v8a/libvulkan_freedreno.so"): PINS["turnip_sha"],
        ("jni", "arm64-v8a/libhardware.so"): PINS["hal_member_sha"],
    }
    bad = [f"{s}:{p}" for (s, p), want in pinned_pairs.items()
           if bykey.get((s, p), {}).get("sha256") != want]
    ok_all &= row("manifest_pinned_shas", not bad, ";".join(bad[:6]))

    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "local/tooling/orch/source_manifest.py"),
         "verify", "--manifest", MANIFEST,
         "--fork", os.path.join(STAGE, "PS2Recomp"),
         "--parallel", os.path.join(STAGE, "parallel-gs"),
         "--codegen", os.path.join(STAGE, "codegen-ssx3"),
         "--jni", os.path.join(STAGE, "jniLibs"),
         "--max-files", "30000", "--max-bytes", "2000000000"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=720)
    try:
        v = json.loads(p.stdout.decode("utf-8", "replace"))
    except ValueError:
        v = {}
    ok_all &= row("manifest_verify_match",
                  p.returncode == 0 and v.get("status") == "match"
                  and v.get("aggregate_actual") == PINS["aggregate"],
                  v.get("status", f"rc={p.returncode}"))

    verdict = "A" if ok_all else "C"
    result = {"part": "N8D7M12P6M5", "verdict": verdict,
              "rows": rows,
              "failing": [r["name"] for r in rows if r["result"] != "pass"],
              "aggregate_sha256": PINS["aggregate"],
              "note": "source staging only; not proof of compilation or "
                      "historical APK provenance"}
    with open(os.path.join(DIR, "check-result.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{len(rows)} rows, {len(result['failing'])} failing, "
          f"verdict {verdict}")
    for r in rows:
        print(("PASS " if r["result"] == "pass" else "FAIL ") + r["name"]
              + (" : " + r["detail"] if r["detail"] else ""))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
