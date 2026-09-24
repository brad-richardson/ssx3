#!/usr/bin/env python3
"""N8D7M10 checker: pins + cited source rows + table invariants.

Verifies citations, pins, and table consistency only. Source strings
cannot prove Android runtime behavior: no build, replay, device action,
or execution occurred in this part, so pass/fail here says nothing
about what the Odin, Turnip, or the Android loader would actually do.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/brad/dev/ssx3")
FORK = Path("/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp")
G43 = Path("/Users/brad/dev/ssx3-work/N8D7F/parallel-gs")
RDIR = REPO / "local" / "research" / "N8D7M10"

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
check("report verdict B", "verdict: b" in report.lower())
check("report states source strings cannot prove runtime",
      "cannot prove" in report.lower() and "android runtime behavior" in report.lower())
check("fork pin", rev_parse(FORK) == FORK_PIN, rev_parse(FORK)[:12])
check("parallel pin", rev_parse(G43) == G43_PIN, rev_parse(G43)[:12])
check("stream sha cited", STREAM_SHA in report)
check("apk sha cited", APK_SHA in report)

# Cited source rows exist at pinned revs
cites = [
    (FORK / "ps2xTest/CMakeLists.txt", r"add_executable\(ps2x_tests"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2X_GS_REPLAY_CAPTURE"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2XGSC1"),
    (FORK / "ps2xTest/src/ps2_gs_replay_tests.cpp", r"PS2X_GS_REPLAY_BACKEND"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"PS2X_N8D7F_SELECTED_CAPTURE"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"vsyncTick == 2050"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"selectedDecode"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"oracleDecodeCensus"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"PS2X_HAS_PARALLEL_SHADOW"),
    (FORK / "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", r"libvulkan_freedreno\.so"),
    (FORK / "ps2xRuntime/src/lib/gs/gs_stream_capture.cpp", r"PS2XGSC1"),
    (FORK / "ps2xRuntime/src/lib/gs/gs_stream_capture.cpp", r"PS2X_GS_CAPTURE_STOP_TICK"),
    (FORK / "ps2xRuntime/src/lib/ps2_android_runtime.cpp", r"ps2x\.env"),
    (FORK / "android/app/build.gradle", r"PS2X_BUILD_TEST.*OFF"),
    (FORK / "android/app/build.gradle", r"arm64-v8a"),
    (FORK / "android/app/src/main/AndroidManifest.xml", r"NativeActivity"),
    (FORK / "android/app/src/main/AndroidManifest.xml", r"ps2EntryRunner"),
]
for path, pat in cites:
    check(f"cite {path.name}:{pat[:28]}", has(path, pat), str(path))

# No PS2X_GS_REPLAY reader under ps2xRuntime (the missing-link claim)
hits = subprocess.run(
    ["rg", "-l", "PS2X_GS_REPLAY", str(FORK / "ps2xRuntime")],
    capture_output=True, text=True, timeout=60).stdout.strip()
# gs_cpu_backend.h carries only a comment mention; no getenv/reader
code_hits = [h for h in hits.splitlines() if h.strip()]
reader_hits = []
for h in code_hits:
    try:
        t = Path(h).read_text()
        if "getenv" in t and "PS2X_GS_REPLAY" in t:
            # must be a file that actually reads the env, not a comment
            for line in t.splitlines():
                if "PS2X_GS_REPLAY" in line and "getenv" in line:
                    reader_hits.append(f"{h}:{line.strip()[:60]}")
    except Exception:
        pass
check("no PS2X_GS_REPLAY reader in ps2xRuntime", reader_hits == [], ";".join(reader_hits) or "none")

# Manifest has no uses-permission
check("manifest no uses-permission",
      not has(FORK / "android/app/src/main/AndroidManifest.xml", r"uses-permission"))

# N8D7M6 receipts: closed stream + descriptor + no PATH_FILE override
comp = json.loads((REPO / "local/research/N8D7M6/comparison.json").read_text())
check("stream bytes", comp["stream"]["bytes"] == 1100696462)
check("stream sha", comp["stream"]["sha"] == STREAM_SHA)
check("stream last marker", comp["stream"]["last"] == [4, 2050])
check("same descriptor", comp["same_descriptor"] is True)
check("mac broad", comp["mac"]["input"]["active"] == 300)
check("odin sparse", comp["odin"]["input"]["active"] == 23)
accept = (REPO / "local/research/N8D7M6/accept.py").read_text()
check("no PATH_FILE override in gated mac replay", "PATH_FILE" not in accept)

# Future-branch thresholds stated
check("branch (i) broad >=250", re.search(r"\(i\).*≥250", report) is not None)
check("branch (ii) sparse <=100", re.search(r"\(ii\).*≤100", report) is not None)
check("branch (iii) OTHER", re.search(r"\(iii\).*OTHER", report) is not None)

# Size cap
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
