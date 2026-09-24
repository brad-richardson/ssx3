#!/usr/bin/env python3
"""N8D7M11 checker: pins + cited source rows + table invariants.

Verifies citations, pins, and table consistency only. Source strings
cannot prove Android runtime behavior: no build, replay, boot, stream
copy, device action, or execution occurred in this part, so pass/fail
here says nothing about what the Odin, Turnip, or the Android loader
would actually do.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/brad/dev/ssx3")
FORK = Path("/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp")
RDIR = REPO / "local" / "research" / "N8D7M11"

FORK_PIN = "a8cfefad109134767b0810b7707b4b58a5dfcca7"
G43_PIN = "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd"
STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
APK_SHA = "e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1"

errors = []
rows = []


def check(name, cond, detail=""):
    rows.append([name, "PASS" if cond else "FAIL", detail])
    if not cond:
        errors.append(name)


def rev_parse(path):
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return f"ERR {e}"


def has(path, pattern):
    try:
        return re.search(pattern, Path(path).read_text()) is not None
    except Exception:
        return False


report = (RDIR / "REPORT.md").read_text()
check("report outcome A choice A",
      "outcome a" in report.lower() and "choice (a)" in report.lower())
check("report states source strings cannot prove runtime",
      "cannot prove" in report.lower() and "android runtime behavior" in report.lower())
check("fork pin", rev_parse(FORK) == FORK_PIN, rev_parse(FORK)[:12])
check("parallel pin",
      rev_parse(REPO.parent / "ssx3-work" / "N8D7F" / "parallel-gs") == G43_PIN
      if False else subprocess.run(
          ["git", "-C", "/Users/brad/dev/ssx3-work/N8D7F/parallel-gs",
           "rev-parse", "HEAD"],
          capture_output=True, text=True, timeout=30).stdout.strip() == G43_PIN,
      G43_PIN[:7])
check("stream sha cited", STREAM_SHA in report)
check("stream bytes cited", "1,100,696,462" in report)
check("apk sha cited", APK_SHA in report)
check("turnip pin cited", "717812c3" in report)
check("hal pin cited", "1b49d27c" in report)

cites = [
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2X_GS_REPLAY_CAPTURE"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2XGSC1"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2X_GS_REPLAY_BACKEND"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"MiniTest::Case"),
    (FORK / "ps2xTest/src/main.cpp", r"register_ps2_gs_replay_tests"),
    (FORK / "ps2xTest/CMakeLists.txt", r"add_executable\(ps2x_tests"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"PS2X_N8D7F_SELECTED_CAPTURE"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"vsyncTick == 2050"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"selectedDecode"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"oracleDecodeCensus"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"PS2X_HAS_PARALLEL_SHADOW"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"libvulkan_freedreno\.so"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"dlsym\(library, \"HMI\"\)"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"PS2X_GS_TURNIP"),
    (FORK / "ps2xRuntime/src/lib/gs/gs_stream_capture.cpp", r"PS2XGSC1"),
    (FORK / "ps2xRuntime/src/lib/gs/gs_stream_capture.cpp", r"PS2X_GS_CAPTURE_STOP_TICK"),
    (FORK / "ps2xRuntime/src/lib/ps2_android_runtime.cpp", r"ps2x\.env"),
    (FORK / "ps2xRuntime/include/ps2_android_env.h", r"envFilePathForBootElf"),
    (FORK / "ps2xRuntime/src/main.cpp", r"redirectStdioToLogcat"),
    (FORK / "ps2xRuntime/src/main.cpp", r"runtime\.initialize"),
    (FORK / "ps2xRuntime/CMakeLists.txt", r"add_library\(ps2EntryRunner SHARED"),
    (FORK / "ps2xRuntime/CMakeLists.txt", r"ANativeActivity_onCreate"),
    (FORK / "ps2xRuntime/CMakeLists.txt", r"PS2X_HAS_PARALLEL_SHADOW=1"),
    (FORK / "android/app/build.gradle", r"PS2X_BUILD_TEST.*OFF"),
    (FORK / "android/app/build.gradle", r"arm64-v8a"),
    (FORK / "android/app/build.gradle", r"targets 'ps2EntryRunner'"),
    (FORK / "android/app/src/main/AndroidManifest.xml", r"NativeActivity"),
    (FORK / "android/app/src/main/AndroidManifest.xml", r"ps2EntryRunner"),
]
for path, pat in cites:
    check(f"cite {path.name}:{pat[:30]}", has(path, pat), str(path))

check("manifest no uses-permission",
      not has(FORK / "android/app/src/main/AndroidManifest.xml", r"uses-permission"))

hits = subprocess.run(
    ["rg", "-l", "PS2X_GS_REPLAY", str(FORK / "ps2xRuntime")],
    capture_output=True, text=True, timeout=60).stdout.strip()
reader_hits = []
for h in [x for x in hits.splitlines() if x.strip()]:
    try:
        for line in Path(h).read_text().splitlines():
            if "PS2X_GS_REPLAY" in line and "getenv" in line:
                reader_hits.append(f"{h}:{line.strip()[:60]}")
    except Exception:
        pass
check("no PS2X_GS_REPLAY reader in ps2xRuntime (missing link stands)",
      reader_hits == [], ";".join(reader_hits) or "none")

# N8D7M6 receipts reused as design inputs
comp = json.loads((REPO / "local/research/N8D7M6/comparison.json").read_text())
check("stream bytes", comp["stream"]["bytes"] == 1100696462)
check("stream sha", comp["stream"]["sha"] == STREAM_SHA)
check("stream last marker", comp["stream"]["last"] == [4, 2050])
check("same descriptor", comp["same_descriptor"] is True)
check("mac broad", comp["mac"]["input"]["active"] == 300)
check("odin sparse", comp["odin"]["input"]["active"] == 23)

# Design completeness: option matrix, factoring, staging, controls
check("option matrix has A and B rows",
      "(A)" in report and "(B)" in report and "REJECTED" in report)
check("parser factoring without MiniTest",
      "MiniTest" in report and "gs_replay_core" in report)
check("backend + tick2050 invocation",
      "GSParallelBackend" in report and "vsyncTick == 2050" in report)
check("app-readable FILES path",
      "/storage/emulated/0/Android/data/com.ps2x.runner/files" in report)
check("two matching SHA reads", "two matching SHA" in report)
check("no invented adb push path",
      "No `adb push` path is invented" in report)
check("default off stated", "default off" in report.lower())
check("broad >=250", re.search(r"≥250", report) is not None)
check("sparse <=100", re.search(r"≤100", report) is not None)
check("101–249 OTHER", "101–249" in report and "OTHER" in report)
check("neither proves faulty packet/copy/120Hz",
      "Neither" in report and "copy timing" in report and "120 Hz" in report)
check("patch plan unexecuted",
      "not executed" in report.lower() or "unexecuted" in report.lower())

# Read-only: reject executed device commands or claimed runs
bad = []
for pat in (r"(?m)^PID \d+", r"am force-stop com\.ps2x\.runner'\s*$",
            r"BUILD SUCCESSFUL", r"INSTALLED.*Success",
            r"two device \+ two local reads match"):
    if re.search(pat, report):
        bad.append(pat)
check("no executed device/build receipts", bad == [], ";".join(bad) or "none")
check("no stream copy made",
      "no copy was made" in report.lower())

size = (RDIR / "REPORT.md").stat().st_size
check("text <512 KiB", size < 512 * 1024, f"{size} B")

out = {
    "status": "pass" if not errors else "FAIL",
    "errors": errors,
    "rows": rows,
    "note": "Source strings cannot prove Android runtime behavior; "
            "this checker verifies pins, cited rows, and table invariants only.",
}
Path(RDIR / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
for name, st, detail in rows:
    print(f"{st} {name} {detail}")
print("OVERALL", out["status"])
sys.exit(0 if not errors else 1)
