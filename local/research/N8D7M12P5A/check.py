#!/usr/bin/env python3
"""N8D7M12 Part 5A static gate: no device, build, or subprocess use.

Checks launch.py text for pins, replay-only env, one-run guard, serial
scope, caps, stop rules, and finally cleanup; verifies REPORT.md carries
the exact unexecuted command and acceptance/stop table. `--self-check`
(or no-arg default) runs the dry path and writes check-result.json here.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LAUNCH = HERE / "launch.py"
REPORT = HERE / "REPORT.md"

PINS = {
    "apk": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "runner": "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "stream": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
}

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


@check("pins_all_present")
def c_pins(text, _rep):
    return all(pin in text for pin in PINS.values())


@check("apk_stream_sizes")
def c_sizes(text, _rep):
    return "153753116" in text and "1100696462" in text


@check("serial_from_file_scoped")
def c_serial(text, _rep):
    return "odin-serial" in text and "622c49b1" in text \
        and '"-s", serial' in text


@check("replay_env_keys")
def c_env(text, _rep):
    keys = ("PS2X_GS_REPLAY_ONDEVICE=1", "PS2X_GS_REPLAY_CAPTURE",
            "PS2X_GS_REPLAY_BACKEND=parallel", "PS2X_GS_TURNIP=1",
            "PS2X_N8D7F_SELECTED_CAPTURE=1", "PS2X_N8D7L_ORACLE=1",
            "PS2X_N8D5_TILE_CAPTURE=1", "PS2X_GS_REPLAY_STEP=50",
            "PS2X_GS_REPLAY_PPM_TICKS=2050", "PS2X_GS_REPLAY_PPM_DIR",
            "PS2X_GS_REPLAY_OUT")
    return all(k in text for k in keys)


@check("no_live_capture_or_pad")
def c_nolive(text, _rep):
    m = re.search(r"env_text = .*?(?=\n    \(SCRATCH)", text, re.S)
    body = m.group(0) if m else text
    return ("PS2X_GS_CAPTURE=" not in body
            and "PS2X_GS_CAPTURE_STOP_TICK" not in body
            and "PS2X_PAD_SCRIPT" not in body
            and "PS2X_CD_IMAGE" not in body
            and "FORBIDDEN_ENV_KEYS" in text)


@check("one_run_guard")
def c_onerun(text, _rep):
    return ("--released-sha" in text and "one-run guard" in text
            and 'result.json").exists()' in text)


@check("single_install_single_launch")
def c_single(text, _rep):
    return ('"install", "-r"' in text and "install_count" in text
            and "launch_count" in text
            and text.count("am start -n") == 1)


@check("stream_never_pushed_or_deleted")
def c_stream(text, _rep):
    pushes = re.findall(r'adb\("push".*?\)', text)
    joined = "\n".join(pushes)
    return ("REMOTE_STREAM" not in joined and "n8d7m6.gs" not in joined
            and "never push/alter/delete" in text)


@check("env_preserve_restore_finally")
def c_envrestore(text, _rep):
    return ("ps2x.env.before" in text and "env_existed" in text
            and "CLEANUP env restored" in text and "finally:" in text)


@check("frame_filename_grounded")
def c_frame(text, _rep):
    return "vq-002050.ppm" in text and "vq-%06" in text


@check("marker_census_syntax")
def c_markers(text, _rep):
    keys = ("GB4_REPLAY_SUMMARY", "GB4_FRAME tick=2050",
            "GB4_REPLAY tick=", "[n8d7m12] replay ok",
            "[n8d7m12] replay failed", "replay rejected")
    return all(k in text for k in keys)


@check("keyguard_blocker_no_workaround")
def c_keyguard(text, _rep):
    return "BLOCKER: keyguard" in text and "never worked around" in text


@check("caps_wall_log_output_progress")
def c_caps(text, _rep):
    return ("WALL_CAP = 600" in text and "LOG_CAP = 16" in text
            and "OUTPUT_CAP = 64" in text and "PROGRESS_CAP = 180" in text)


@check("unique_empty_outputs")
def c_outputs(text, _rep):
    return ("n8d7m12p5a-frames-" in text and "already exists" in text
            and "is not empty" in text)


@check("finally_force_stop_lease")
def c_finally(text, _rep):
    return ("am force-stop" in text and "lease not ours" in text
            and "LEASE_FREE N8D7M12P5A done" in text
            and "close_logger" in text)


@check("provisional_marking")
def c_prov(text, _rep):
    return "PROVISIONAL" in text and "same-binary controls" in text


@check("complete_before_exit_drain")
def c_drain(text, _rep):
    complete_at = text.find("if replay_complete(markers, census):")
    exit_at = text.find("if not pidof():")
    return ("def drain_after_exit" in text and "DRAIN_SECS = 15" in text
            and "drain_after_exit(pid" in text
            and "process exited without complete receipt" in text
            and 0 < complete_at < exit_at)


@check("control128_numeric_census")
def c_census(text, _rep):
    return ("def tile_vector" in text and "def parse_controls" in text
            and "def census_gate" in text and "CONTROL_ADDRS" in text
            and '("128", "128", "PASS")' in text
            and 'summary[3] != vector["sha256"]' in text
            and "Mere line presence never passes" in text)


@check("env_double_sha")
def c_envsha(text, _rep):
    return ("pre-existing ps2x.env device SHA pair mismatch" in text
            and "preserved ps2x.env device/local SHA mismatch" in text
            and "restored ps2x.env device/local SHA mismatch" in text)


@check("cleanup_failure_fails")
def c_cleanup(text, _rep):
    return ("cleanup_errors" in text
            and "cleanup failure overrides" in text)


@check("no_off_control_claim")
def c_nooff(text, rep):
    return ("no same-binary OFF control" in text
            and "OFF control" in rep)


@check("report_unexecuted_command_table")
def c_report(text, rep):
    del text
    return ("--released-sha" in rep and "acceptance" in rep.lower()
            and "stop" in rep.lower() and "tick2050" in rep.lower()
            and "PROVISIONAL" in rep)


@check("no_device_calls_in_checker")
def c_noself(_text, _rep):
    mine = (HERE / "check.py").read_text()
    imports = re.findall(r"^\s*(?:import\s+subprocess|from\s+subprocess)\b",
                         mine, re.M)
    calls = re.findall(
        r"^\s*(?:subprocess\s*\.\s*(?:run|Popen|call)|os\s*\.\s*system"
        r"|adb\s*\()", mine, re.M)
    return not imports and not calls


def main():
    text = LAUNCH.read_text()
    rep = REPORT.read_text() if REPORT.exists() else ""
    rows = []
    for name, fn in CHECKS:
        try:
            rows.append({"check": name, "pass": bool(fn(text, rep))})
        except Exception as exc:
            rows.append({"check": name, "pass": False,
                         "error": repr(exc)})
    passed = sum(1 for r in rows if r["pass"])
    mismatch = ("pins_all_present", "frame_filename_grounded",
                "marker_census_syntax", "no_live_capture_or_pad",
                "control128_numeric_census")
    verdict = "A" if passed == len(rows) else (
        "B" if any(r["check"] in mismatch and not r["pass"] for r in rows)
        else "OTHER")
    launch_sha = hashlib.sha256(LAUNCH.read_bytes()).hexdigest()
    out = {"brief": "N8D7M12P5A", "checks": rows,
           "passed": f"{passed}/{len(rows)}", "verdict": verdict,
           "launch_sha": launch_sha,
           "note": "Static only. No device, build, install, or launch executed."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{verdict} {passed}/{len(rows)} launch_sha={launch_sha}")
    for row in rows:
        print(("PASS " if row["pass"] else "FAIL ") + row["check"])
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    if "--self-check" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(main())
    raise SystemExit("usage: check.py [--self-check]")
