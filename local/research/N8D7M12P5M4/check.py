#!/usr/bin/env python3
"""N8D7M12 Part 5M4 receipt checker — read-only, narrow, no replay.

Independently verifies the ONE released Mac OFF replay driven by the
reviewed Part 5M3 driver `local/research/N8D7M12P5M3/mac_off.py` at SHA-256
1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738.

The replay used the pinned Part 1 Mac ON binary/stream, parallel backend,
step 50, tick2050 PPM, with exactly the three capture flags removed
(PS2X_N8D7F_SELECTED_CAPTURE, PS2X_N8D7L_ORACLE, PS2X_N8D5_TILE_CAPTURE)
and the private output paths changed.

Acceptance is recomputed here from the raw run.log / result.json /
parallel.hashes / PPM only, never from the driver's provisional verdict:
  - binary exit 0
  - suite Total Tests 585 / Passed 585 / Failed 0, no failed/error test
  - GB4_REPLAY_SUMMARY mode=queue backend=parallel markers=2050
  - GB4_FRAME tick=2050
  - exactly the ordered 41 ticks 50,100,...,2050
  - vq-002050.ppm present
  - no parse/backend error line
  - 16 MiB log cap, 64 MiB output cap
  - child PID gone and the mini P-lane lease released
  - binary/stream/ON-hashes/ON-PPM pins unchanged
  - the pre-run cwd fixture resolves only into the pinned Part 1 fork
Then it classifies OFF vs the pinned Mac ON:
  flag-unperturbed | void-pre2050 | tick2050-only | invalid
If acceptance fails, the run verdict is FAIL even when artifacts match ON.

Writes check-result.json next to this file. Never starts a process, claims
no lease, and touches no device.

Run: python3 local/research/N8D7M12P5M4/check.py
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WORK = Path.home() / "dev" / "ssx3-work"

DRIVER = REPO / "local" / "research" / "N8D7M12P5M3" / "mac_off.py"
RELEASED_SHA = "1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738"

SCRATCH = WORK / "N8D7M12P5M3"
OFF_DIR = SCRATCH / "mac-off"
CWD = OFF_DIR / "cwd"
PPM_PATH = OFF_DIR / "frames" / "vq-002050.ppm"
HASHES_PATH = OFF_DIR / "parallel.hashes"
RUN_LOG = OFF_DIR / "run.log"
RESULT = SCRATCH / "result.json"
DRIVER_LOG = SCRATCH / "driver.log"

BINARY = WORK / "N8D7M12" / "build" / "ps2xTest" / "ps2x_tests"
STREAM = WORK / "N8D7M6" / "n8d7m6.gs"
ON_HASHES = WORK / "N8D7M12" / "mac-parallel" / "parallel.hashes"
ON_PPM = WORK / "N8D7M12" / "mac-parallel" / "vq-002050.ppm"
FORK = WORK / "N8D7M12" / "PS2Recomp"
FORK_PS2XRECOMP = FORK / "ps2xRecomp"
HEADER = FORK_PS2XRECOMP / "include" / "ps2recomp" / "instructions.h"

BINARY_SHA = "2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5"
STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
ON_HASHES_SHA = "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290"
ON_PPM_SHA = "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e"
HEADER_SHA = "b8de8745e16d6a814763f69b0e8d1d54d957bf427f94ec2bc57f63e509f970cd"
HEADER_SIZE = 31244

REMOVED_FLAGS = {
    "PS2X_N8D5_TILE_CAPTURE",
    "PS2X_N8D7F_SELECTED_CAPTURE",
    "PS2X_N8D7L_ORACLE",
}
CHANGED_KEYS = {"PS2X_GS_REPLAY_OUT", "PS2X_GS_REPLAY_PPM_DIR"}
EXPECTED_TICKS = tuple(range(50, 2051, 50))
ROW_RE = re.compile(
    r"GB4_REPLAY tick=(\d+) vram=([0-9a-f]+) priv=([0-9a-f]+) present=([0-9a-f]+)")
LEASE_FILES = (Path("/tmp/ssx3-p-lane-lease"), Path("/tmp/ssx3-p-lane-lease-2"))
LOG_CAP = 16 * 1024 * 1024
OUTPUT_CAP = 64 * 1024 * 1024
ERROR_PATTERNS = (
    r"GB4_REPLAY_PARSE_ERROR.*",
    r"\[gs:parallel\] FATAL:.*",
    r"Turnip .*failed.*",
    r"Fatal signal.*",
    r"FATAL EXCEPTION.*",
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    p = Path(path)
    return p.read_text(errors="replace") if p.exists() else ""


def parse_rows(path):
    rows = []
    for line in read(path).splitlines():
        m = ROW_RE.search(line)
        if m:
            rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    return rows


def tree_bytes(root):
    return sum(p.stat().st_size for p in Path(root).rglob("*") if p.is_file())


def suite_totals(log):
    """Return (total, passed, failed) or (None, None, None)."""
    def last_num(pat):
        vals = re.findall(pat, log, re.M)
        return int(vals[-1]) if vals else None
    total = last_num(r"^Total Tests:\s*(\d+)")
    passed = last_num(r"^Passed:\s*(\d+)")
    failed = last_num(r"^Failed:\s*(\d+)")
    return total, passed, failed


def error_lines(log):
    out = []
    for pat in ERROR_PATTERNS:
        out += re.findall(pat, log)
    return out


def marker_summary(log):
    m = re.findall(
        r"GB4_REPLAY_SUMMARY mode=(\S+) backend=(\S+).*?packets=(\d+) "
        r"priv=(\d+) transfers=(\d+) markers=(\d+)", log)
    return m[-1] if m else None


def marker_frame_2050(log):
    m = re.findall(
        r"GB4_FRAME tick=2050 backend=(\S+) pmode=([0-9a-fA-F]+).*?"
        r"present=([0-9a-fA-F]+)", log)
    return m[-1] if m else None


def classify(on_rows, off_rows, on_ppm_sha, off_ppm_sha):
    if [r[0] for r in off_rows] != list(EXPECTED_TICKS) or len(on_rows) != 41:
        return "invalid"
    pre = [a for a, b in zip(on_rows, off_rows) if a != b and a[0] <= 2000]
    if pre:
        return "void-pre2050"
    if on_rows == off_rows and on_ppm_sha == off_ppm_sha:
        return "flag-unperturbed"
    return "tick2050-only"


def main():
    rec = json.loads(RESULT.read_text()) if RESULT.exists() else {}
    log = read(RUN_LOG)
    dlog = read(DRIVER_LOG)
    markers = rec.get("markers", {})

    rows_off = parse_rows(HASHES_PATH)
    rows_on = parse_rows(ON_HASHES) if ON_HASHES.exists() else []
    off_ppm_sha = sha256_file(PPM_PATH) if PPM_PATH.exists() else None
    on_ppm_sha = sha256_file(ON_PPM) if ON_PPM.exists() else None

    total, passed, failed = suite_totals(log)
    summary = marker_summary(log)
    frame = marker_frame_2050(log)
    errs = error_lines(log)

    checks = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    add("driver_sha_is_released_sha", sha256_file(DRIVER) == RELEASED_SHA,
        sha256_file(DRIVER))
    add("result_script_sha_matches_release",
        rec.get("script_sha") == RELEASED_SHA)
    add("exactly_one_replay", rec.get("replay_count") == 1)
    add("binary_exit_zero", rec.get("exit_code") == 0,
        f"exit_code={rec.get('exit_code')}")
    add("suite_585_585_0", total == 585 and passed == 585 and failed == 0,
        f"total={total} passed={passed} failed={failed}")
    add("no_failed_or_error_test",
        "[Failed]" not in log and "[Error]" not in log and not errs,
        f"errs={errs[:3]}")
    add("summary_parallel_markers2050",
        summary is not None and summary[1] == "parallel" and summary[5] == "2050",
        str(summary))
    add("frame_tick2050",
        frame is not None and frame[0] == "parallel", str(frame))
    add("off_rows_exact_41_ordered_ticks",
        [r[0] for r in rows_off] == list(EXPECTED_TICKS), str(len(rows_off)))
    add("off_ppm_present", PPM_PATH.exists(),
        f"{off_ppm_sha} {PPM_PATH.stat().st_size if PPM_PATH.exists() else '-'}")
    add("run_log_cap_16mib",
        RUN_LOG.exists() and RUN_LOG.stat().st_size <= LOG_CAP,
        str(RUN_LOG.stat().st_size if RUN_LOG.exists() else "-"))
    add("outputs_cap_64mib",
        OFF_DIR.exists() and tree_bytes(OFF_DIR) <= OUTPUT_CAP,
        str(tree_bytes(OFF_DIR) if OFF_DIR.exists() else "-"))

    # child PID gone
    pid = rec.get("pid")
    pid_gone = False
    if isinstance(pid, int):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pid_gone = True
        except PermissionError:
            pid_gone = False
    add("child_pid_gone", pid_gone, f"pid={pid}")

    add("lease_released_both_slots_free",
        not any(p.exists() for p in LEASE_FILES)
        and "CLEANUP lease released" in dlog)

    add("pins_unchanged",
        sha256_file(BINARY) == BINARY_SHA
        and sha256_file(STREAM) == STREAM_SHA
        and sha256_file(ON_HASHES) == ON_HASHES_SHA
        and sha256_file(ON_PPM) == ON_PPM_SHA)

    diff = rec.get("env_diff", {})
    add("env_diff_exactly_three_flags",
        set(diff.get("removed", [])) == REMOVED_FLAGS
        and set(diff.get("changed", [])) == CHANGED_KEYS
        and diff.get("ambient_ps2x_cleared") == [],
        json.dumps(diff))

    # fixture resolves only into the pinned Part 1 fork
    fixture = CWD / "ps2xRecomp"
    fixture_ok = False
    if fixture.is_symlink():
        target = os.path.realpath(fixture)
        fixture_ok = (target == os.path.realpath(FORK_PS2XRECOMP)
                      and os.path.realpath(HEADER).startswith(
                          os.path.realpath(FORK) + os.sep)
                      and HEADER.stat().st_size == HEADER_SIZE
                      and sha256_file(HEADER) == HEADER_SHA)
    add("cwd_fixture_only_pinned_fork", fixture_ok,
        os.path.realpath(fixture) if fixture.is_symlink() else "absent")

    acceptance = all(c["pass"] for c in checks)
    reading = classify(rows_on, rows_off, on_ppm_sha, off_ppm_sha)
    # An invalid/failed acceptance run is never an artifact verdict.
    if not acceptance and reading == "flag-unperturbed":
        artifact_reading = "unaccepted-equal"
    else:
        artifact_reading = reading

    out = {
        "brief": "N8D7M12P5M4",
        "driver_sha": RELEASED_SHA,
        "checks": checks,
        "passed": f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
        "acceptance": "PASS" if acceptance else "FAIL",
        "final_run_verdict": "PASS" if acceptance else "FAIL",
        "artifact_reading": artifact_reading,
        "raw_classification": reading,
        "off_hashes_sha": (sha256_file(HASHES_PATH) if HASHES_PATH.exists() else None),
        "off_ppm_sha": off_ppm_sha,
        "off_ppm_path": str(PPM_PATH),
        "on_hashes_sha": ON_HASHES_SHA,
        "on_ppm_sha": ON_PPM_SHA,
        "row_count": len(rows_off),
        "note": "Read-only receipt check. No replay, build, device or lease "
                "action. Matching artifacts never override a failed suite; "
                "diagnostic wall is not speed.",
    }
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"acceptance={out['acceptance']} final={out['final_run_verdict']} "
          f"reading={artifact_reading} checks={out['passed']}")
    for c in checks:
        print(("PASS " if c["pass"] else "FAIL ") + c["check"])
    return 0 if acceptance else 1


if __name__ == "__main__":
    raise SystemExit(main())
