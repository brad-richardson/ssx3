#!/usr/bin/env python3
"""N8D7M12 Part 2 static source checker (no build, no device).

Asserts the pinned branch, the single Android-only default-off replay branch
in ps2xRuntime/src/main.cpp before all game-boot calls, strict key/backend/
Turnip/capture checks, the Part 1 core call, the result gate, default-off
fallthrough, and an empty runner-dir diff. Source strings cannot prove
Android compile, loader or runtime behavior.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

FORK = Path.home() / "dev" / "ssx3-work" / "N8D7M12P2" / "PS2Recomp"
BASE = "24801bc"
UPSTREAM_RUNNER_BASE = "14b1e5cb"
MAIN = "ps2xRuntime/src/main.cpp"

results = []


def check(name, ok, detail=""):
    results.append({"name": name, "pass": bool(ok), "detail": detail})


def git(*args):
    p = subprocess.run(["git", "-C", str(FORK), *args],
                       capture_output=True, text=True)
    return p


def main():
    text = (FORK / MAIN).read_text()

    head = git("rev-parse", "HEAD").stdout.strip()
    check("fork_head_present", len(head) == 40, head)
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    check("fork_branch", branch == "n8d7m12-app", branch)
    base_ok = git("merge-base", "--is-ancestor", BASE, "HEAD")
    check("fork_base_ancestor", base_ok.returncode == 0, BASE)
    check("fork_head_advances_base",
          head != git("rev-parse", BASE).stdout.strip(), head[:12])

    files = git("diff", "--name-only", BASE, "--", ".").stdout.split()
    check("diff_single_file", files == [MAIN], json.dumps(files))

    diff_stat = git("diff", "--stat", BASE, "--", ".").stdout
    added = 0
    m = re.search(r"(\d+) insertions?", diff_stat)
    if m:
        added = int(m.group(1))
    check("diff_bounded", 0 < added <= 80, diff_stat.strip().splitlines()[-1] if diff_stat.strip() else "")

    # Single Android-only branch keyed strictly on "1".
    check("key_single_occurrence",
          text.count('getenv("PS2X_GS_REPLAY_ONDEVICE")') == 1,
          "single getenv entry to the branch")
    check("key_strict_eq_1",
          'std::strcmp(replayOnDevice, "1") == 0' in text,
          "strcmp ==1")
    check("key_null_guarded",
          "replayOnDevice &&" in text,
          "null guard before strcmp")

    # Strict capture/backend/Turnip gates, explicit reject (no silent fallback).
    check("capture_nonempty",
          "capture[0] == '\\0'" in text or 'capture[0] !=' in text,
          "nonempty CAPTURE")
    check("backend_strict_parallel",
          'std::strcmp(backend, "parallel") != 0' in text,
          "BACKEND=parallel")
    check("turnip_strict_1",
          'std::strcmp(turnip, "1") != 0' in text,
          "TURNIP=1")
    check("reject_line",
          "replay rejected" in text and "PS2X_GS_REPLAY_BACKEND=parallel" in text,
          "explicit reject")

    # Core call + full result gate + one success/failure line + exit code.
    check("core_call", "ps2x_gs_replay_run()" in text, "core call")
    for field in ["openOk", "headerOk", "rtzOk", "pathFileOk", "wordsOk",
                  "backendOk", "parseOk", "packetTraceOk", "outOk",
                  "expectOk", "hasStream", "hasSamples", "skipped"]:
        check(f"gate_{field}", f"replayResult.{field}" in text, field)
    check("success_line", "[n8d7m12] replay ok" in text, "ok line")
    check("failure_line", "[n8d7m12] replay failed" in text, "fail line")
    check("exit_codes", "std::_Exit(replayOk ? 0 : 1)" in text, "_Exit(ok?0:1)")
    check("reject_exit", text.count("std::_Exit(1)") >= 1, "reject _Exit(1)")

    # Android-only + exit/flush pattern preserved.
    check("android_guard", "#if defined(__ANDROID__)" in text, "guard")
    check("core_include_android_guarded",
          '#include "runtime/gs/gs_replay_core.h"' in text, "core include")
    check("flush_before_exit",
          text.count("std::cout.flush();") >= 2 and
          text.count("std::cerr.flush();") >= 2, "flush preserved")

    # Ordering: branch before every game-boot call.
    lines = text.splitlines()
    def lineno(pat):
        for i, l in enumerate(lines, 1):
            if re.search(pat, l):
                return i
        return -1
    branch_line = lineno(r"PS2X_GS_REPLAY_ONDEVICE")
    setup_line = lineno(r"setupTerminateLogger\(\);")
    boot_calls = {
        "getExecutablePath": lineno(r"getExecutablePath\(argc, argv\)"),
        "PS2Runtime_construction": lineno(r"PS2Runtime runtime;"),
        "initialize": lineno(r"runtime\.initialize\("),
        "loadELF": lineno(r"runtime\.loadELF\("),
        "run": lineno(r"runtime\.run\(\)"),
    }
    check("branch_after_setup",
          0 < setup_line < branch_line,
          f"setup={setup_line} branch={branch_line}")
    for name, ln in boot_calls.items():
        check(f"branch_before_{name}",
              0 < branch_line < ln, f"branch={branch_line} {name}={ln}")
    # Logcat drain: both replay _Exit sites must drain/join via the existing
    # stopLogcatRedirect() after flushing (the tick2050 census receipt may
    # still sit in the pipe; _Exit bypasses atexit). Game-boot path keeps
    # its original flush + _Exit with no added drain call.
    check("replay_drain_calls",
          text.count("stopLogcatRedirect();") == 2, "reject + result drains")
    branch_region = "\n".join(lines[branch_line - 1:branch_line + 80])
    check("drain_before_replay_exits",
          len(re.findall(r"stopLogcatRedirect\(\);\s*\n\s*std::_Exit",
                         branch_region)) == 2,
          "drain immediately precedes both replay _Exits")
    tail = "\n".join(lines[branch_line + 80:])
    check("default_off_no_drain",
          "stopLogcatRedirect();" not in tail, "game-boot path unchanged")

    # Default-off fallthrough: game boot calls still present exactly once,
    # no #else around them, manifest/Gradle/CMake untouched in diff.
    check("game_boot_intact",
          all(v > 0 for v in boot_calls.values()), json.dumps(boot_calls))
    check("no_else_boot",
          "#else" not in "\n".join(lines[max(0, branch_line - 3):branch_line + 70]),
          "no else-gated boot")
    check("no_manifest_change",
          "AndroidManifest.xml" not in git("diff", "--name-only", BASE).stdout,
          "manifest untouched")
    check("no_gradle_change",
          "build.gradle" not in git("diff", "--name-only", BASE).stdout,
          "gradle untouched")
    check("no_cmake_change",
          "CMakeLists.txt" not in git("diff", "--name-only", BASE).stdout,
          "cmake untouched")
    check("no_new_binary",
          "add_executable" not in git("diff", BASE).stdout,
          "no new target")

    runner = git("diff", "--stat", UPSTREAM_RUNNER_BASE, "HEAD",
                 "--", "ps2xRuntime/src/runner").stdout.strip()
    check("runner_dir_empty", runner == "", runner[:200])

    fails = [r for r in results if not r["pass"]]
    missing = [r["name"] for r in fails]
    if any(n in ("fork_branch", "fork_base_ancestor", "no_manifest_change",
                 "no_gradle_change", "no_cmake_change", "runner_dir_empty")
           for n in missing):
        verdict = "OTHER"
    elif not fails:
        verdict = "A"
    else:
        verdict = "B"

    out = {"verdict": verdict,
           "fork_head": head,
           "checks": results,
           "note": "Source strings cannot prove Android compile, loader or runtime behavior. No build/device verdict."}
    Path("check-result.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"verdict": verdict,
                      "pass": f"{len(results) - len(fails)}/{len(results)}",
                      "fails": missing}, indent=2))
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    sys.exit(main())
