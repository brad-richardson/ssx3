#!/usr/bin/env python3
"""N8D7M12 Part 5M2 receipt checker — read-only, narrow, no replay.

Verifies the receipts of the ONE released Mac OFF replay driven by the
reviewed driver `local/research/N8D7M12P5M1/mac_off.py` at SHA-256
bec9a4c6... The replay used the Part 1 Mac ON binary/stream, parallel
backend, step 50, tick2050 PPM, with exactly the three capture flags
removed.

It asserts, from the on-disk receipts only:
  - driver SHA is the reviewed one and matches result.json `script_sha`
  - result.json records exactly one replay and the exact env diff
  - the shared-core markers are the parallel/markers=2050 form
  - OFF `parallel.hashes` is the exact ordered 41-tick sequence 50..2050
  - every OFF row and the OFF PPM are byte-equal to the pinned Mac ON
    artifacts (the predeclared `flag-unperturbed` reading)
  - the recorded first failure (suite exit 1) is the cwd-relative
    CodeGenerator test, not a replay/parse/backend error
  - cleanup: lease released (both slot files absent), child PID gone,
    outputs bounded

Run: python3 local/research/N8D7M12P5M2/check.py
Writes check-result.json next to this file. Never starts a process,
claims no lease, and touches no device.
"""
import hashlib
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path.home() / "dev" / "ssx3-work"
SCRATCH = WORK / "N8D7M12P5M1"
OFF_DIR = SCRATCH / "mac-off"
RESULT = SCRATCH / "result.json"
DRIVER = Path.home() / "dev" / "ssx3" / "local" / "research" / "N8D7M12P5M1" / "mac_off.py"

DRIVER_SHA = "bec9a4c626092b5a2e66a8f1597f90235c1335631aa2f2cba432851de6ecd9f1"
BINARY_SHA = "2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5"
STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
ON_HASHES = WORK / "N8D7M12" / "mac-parallel" / "parallel.hashes"
ON_PPM = WORK / "N8D7M12" / "mac-parallel" / "vq-002050.ppm"
ON_HASHES_SHA = "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290"
ON_PPM_SHA = "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e"
REMOVED_FLAGS = {
    "PS2X_N8D5_TILE_CAPTURE", "PS2X_N8D7F_SELECTED_CAPTURE", "PS2X_N8D7L_ORACLE"}
CHANGED_KEYS = {"PS2X_GS_REPLAY_OUT", "PS2X_GS_REPLAY_PPM_DIR"}
EXPECTED_TICKS = tuple(range(50, 2051, 50))
ROW_RE = re.compile(
    r"GB4_REPLAY tick=(\d+) vram=([0-9a-f]+) priv=([0-9a-f]+) present=([0-9a-f]+)")
LEASE_FILES = (Path("/tmp/ssx3-p-lane-lease"), Path("/tmp/ssx3-p-lane-lease-2"))
LOG_CAP = 16 * 1024 * 1024
OUTPUT_CAP = 64 * 1024 * 1024


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rows(path):
    rows = []
    for line in Path(path).read_text(errors="replace").splitlines():
        m = ROW_RE.search(line)
        if m:
            rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    return rows


def tree_bytes(root):
    return sum(p.stat().st_size for p in Path(root).rglob("*") if p.is_file())


CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


@check("driver_sha_reviewed_and_recorded")
def c_driver(rec):
    got = sha256_file(DRIVER)
    return (got == DRIVER_SHA
            and rec.get("script_sha") == DRIVER_SHA
            and rec.get("replay_count") == 1)


@check("result_verdict_fail_exit1")
def c_verdict(rec):
    return (rec.get("verdict") == "FAIL" and rec.get("exit_code") == 1
            and rec.get("first_failure") == "no complete 41-row tick2050 receipt")


@check("env_diff_exactly_minus_three_flags")
def c_env(rec):
    diff = rec.get("env_diff", {})
    return (set(diff.get("removed", [])) == REMOVED_FLAGS
            and set(diff.get("changed", [])) == CHANGED_KEYS
            and diff.get("ambient_ps2x_cleared") == [])


@check("markers_parallel_markers2050")
def c_markers(rec):
    m = rec.get("markers", {})
    summary = m.get("summary") or []
    return (len(summary) == 6 and summary[1] == "parallel"
            and summary[5] == "2050")


@check("marker_frame_tick2050")
def c_frame(rec):
    frame = rec.get("markers", {}).get("frame") or []
    return len(frame) == 4 and frame[0] == "2050" and frame[1] == "parallel"


@check("off_rows_exact_41_ordered_ticks")
def c_rows(rec):
    rows = parse_rows(OFF_DIR / "parallel.hashes")
    return [r[0] for r in rows] == list(EXPECTED_TICKS) and len(rows) == 41


@check("off_hashes_sha_equals_on_pin")
def c_offhashes(_rec):
    return sha256_file(OFF_DIR / "parallel.hashes") == ON_HASHES_SHA


@check("off_ppm_sha_equals_on_pin")
def c_offppm(_rec):
    return sha256_file(OFF_DIR / "frames" / "vq-002050.ppm") == ON_PPM_SHA


@check("all_41_rows_byte_equal_on")
def c_rowequal(_rec):
    return parse_rows(OFF_DIR / "parallel.hashes") == parse_rows(ON_HASHES)


@check("off_ppm_byte_equal_on")
def c_ppmequal(_rec):
    return (OFF_DIR / "frames" / "vq-002050.ppm").read_bytes() == ON_PPM.read_bytes()


@check("first_failure_is_cwd_codegen_not_replay")
def c_firstfail(rec):
    log = (OFF_DIR / "run.log").read_text(errors="replace")
    if "VU0 macro mappings cover all S1/S2 enums" not in log:
        return False
    if "instructions.h should be readable from the test working directory" not in log:
        return False
    if "Failed: 1" not in log or "Failed: 0" in log:
        return False
    if "GB4_REPLAY_PARSE_ERROR" in log:
        return False
    # the PS2GSReplay test itself passed (its [Passed] is the first after the
    # tick2050 row block)
    summary_idx = log.find("GB4_REPLAY_SUMMARY")
    if summary_idx < 0:
        return False
    tail = log[summary_idx:]
    return tail.find("GB4_REPLAY tick=2050") >= 0 and "[Passed]" in tail


@check("lease_released_both_slots_free")
def c_lease(rec):
    return not any(p.exists() for p in LEASE_FILES) \
        and "CLEANUP lease released" in json.dumps(rec.get("events", []))


@check("child_pid_gone")
def c_pid(rec):
    pid = rec.get("pid")
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


@check("outputs_bounded")
def c_bounded(_rec):
    log = (OFF_DIR / "run.log").stat().st_size
    return log <= LOG_CAP and tree_bytes(OFF_DIR) <= OUTPUT_CAP


@check("pins_unchanged")
def c_pins(_rec):
    return (sha256_file(WORK / "N8D7M12" / "build" / "ps2xTest" / "ps2x_tests")
            == BINARY_SHA
            and sha256_file(WORK / "N8D7M6" / "n8d7m6.gs") == STREAM_SHA
            and sha256_file(ON_HASHES) == ON_HASHES_SHA
            and sha256_file(ON_PPM) == ON_PPM_SHA)


def compare_reading(rec):
    """Predeclared reading of the produced artifacts (rows/PPM only)."""
    off = parse_rows(OFF_DIR / "parallel.hashes")
    on = parse_rows(ON_HASHES)
    if [r[0] for r in off] != list(EXPECTED_TICKS) or len(on) != 41:
        return "invalid"
    pre = [a for a, b in zip(on, off) if a != b and a[0] <= 2000]
    if pre:
        return "void-pre2050"
    same_ppm = (sha256_file(OFF_DIR / "frames" / "vq-002050.ppm")
                == sha256_file(ON_PPM))
    if on == off and same_ppm:
        return "flag-unperturbed"
    return "tick2050-only"


def main():
    rec = json.loads(RESULT.read_text()) if RESULT.exists() else {}
    rows = []
    for name, fn in CHECKS:
        try:
            ok = bool(fn(rec))
        except Exception as exc:
            rows.append({"check": name, "pass": False, "error": repr(exc)})
            continue
        rows.append({"check": name, "pass": ok})
    passed = sum(1 for r in rows if r["pass"])
    reading = compare_reading(rec)
    out = {
        "brief": "N8D7M12P5M2",
        "driver_sha": DRIVER_SHA,
        "checks": rows,
        "passed": f"{passed}/{len(rows)}",
        "receipt_verdict": "A" if passed == len(rows) else "B",
        "acceptance": "FAIL",
        "acceptance_reason": "suite exit 1 (cwd-relative CodeGenerator test); "
                             "replay artifacts themselves complete and byte-equal",
        "artifact_reading": reading,
        "off_ppm_path": str(OFF_DIR / "frames" / "vq-002050.ppm"),
        "off_ppm_sha": sha256_file(OFF_DIR / "frames" / "vq-002050.ppm"),
        "note": "Read-only receipt check. No replay, build, device or lease "
                "action. No graphics root cause; diagnostic wall is not speed.",
    }
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{out['receipt_verdict']} {passed}/{len(rows)} "
          f"acceptance=FAIL artifact_reading={reading}")
    for r in rows:
        print(("PASS " if r["pass"] else "FAIL ") + r["check"])
    return 0 if out["receipt_verdict"] == "A" else 1


if __name__ == "__main__":
    raise SystemExit(main())
