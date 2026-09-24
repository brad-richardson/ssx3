#!/usr/bin/env python3
"""N8D7M12 Part 5E1 static gate: no device, build, or subprocess use.

Checks the OFF-repeat launch.py text for same-APK pins, OFF env
semantically identical to OFF1 (P5D1) except unique output paths,
normalized byte-identity proof (only listed path/label changes),
one-run guard, serial scope, caps, stop rules, OFF census
non-requirement with 41-row exact-tick receipt, and finally cleanup;
verifies REPORT.md carries the exact unexecuted command,
acceptance/stop table, and predeclared OFF2-vs-OFF1 comparison.
`--self-check` (or no-arg default) runs the dry path and writes
check-result.json here.
"""
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LAUNCH = HERE / "launch.py"
REPORT = HERE / "REPORT.md"
OFF1_LAUNCH = REPO / "local" / "research" / "N8D7M12P5D1" / "launch.py"
OFF1_SHA = "223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170"

PINS = {
    "apk": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "runner": "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "stream": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
}

REMOVED_FLAGS = (
    "PS2X_N8D7F_SELECTED_CAPTURE=1",
    "PS2X_N8D7L_ORACLE=1",
    "PS2X_N8D5_TILE_CAPTURE=1",
)

KEPT_ENV_KEYS = (
    "PS2X_GS_REPLAY_ONDEVICE=1",
    "PS2X_GS_REPLAY_CAPTURE",
    "PS2X_GS_REPLAY_BACKEND=parallel",
    "PS2X_GS_TURNIP=1",
    "PS2X_GS_REPLAY_STEP=50",
    "PS2X_GS_REPLAY_PPM_TICKS=2050",
    "PS2X_GS_REPLAY_PPM_DIR",
    "PS2X_GS_REPLAY_OUT",
)

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def env_block(text):
    m = re.search(r"REPLAY_ENV_KEYS = \((.*?)\)", text, re.S)
    return m.group(1) if m else ""


def normalized(text):
    """Map OFF2 labels back to OFF1 labels for the byte-identity proof."""
    return (text.replace("N8D7M12P5E1", "N8D7M12P5D1")
                .replace("n8d7m12p5e1-", "n8d7m12p5d1-")
                .replace("Part 5E1", "Part 5D1")
                .replace("OFF-repeat", "OFF-control"))


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


@check("off1_launcher_sha_pinned")
def c_off1sha(text, _rep):
    del text
    if not OFF1_LAUNCH.exists():
        return False
    return hashlib.sha256(OFF1_LAUNCH.read_bytes()).hexdigest() == OFF1_SHA


@check("off_env_exact_minus_three")
def c_offenv(text, _rep):
    block = env_block(text)
    if not block:
        return False
    if any(flag in block for flag in REMOVED_FLAGS):
        return False
    tuple_keys = KEPT_ENV_KEYS[:6]
    if not all(k in block for k in tuple_keys):
        return False
    # PPM_DIR/OUT are appended in run(), not in the tuple (same as OFF1).
    return ("PS2X_GS_REPLAY_PPM_DIR={ppm_dir}" in text
            and "PS2X_GS_REPLAY_OUT={hashes_path}" in text)


@check("off2_env_semantically_identical_to_off1")
def c_envsame(text, _rep):
    if not OFF1_LAUNCH.exists():
        return False
    old = OFF1_LAUNCH.read_text()
    if env_block(old) != env_block(text):
        return False
    # PPM_DIR/OUT construction lines must differ only in the basename
    # prefix (p5d1 -> p5e1); everything else (stamp, guards) identical.
    old_ppm = [l for l in old.splitlines() if "PS2X_GS_REPLAY_PPM_DIR={ppm_dir}" in l
               or "PS2X_GS_REPLAY_OUT={hashes_path}" in l
               or "ppm_dir = " in l or "hashes_path = " in l]
    new_ppm = [l for l in text.splitlines() if "PS2X_GS_REPLAY_PPM_DIR={ppm_dir}" in l
               or "PS2X_GS_REPLAY_OUT={hashes_path}" in l
               or "ppm_dir = " in l or "hashes_path = " in l]
    if len(old_ppm) != len(new_ppm):
        return False
    for a, b in zip(old_ppm, new_ppm):
        if a.replace("n8d7m12p5d1-", "X") != b.replace("n8d7m12p5e1-", "X"):
            return False
    for flag in REMOVED_FLAGS:
        if flag in env_block(old) or flag in env_block(text):
            return False
    return True


@check("off2_normalized_identical_to_off1")
def c_norm(text, _rep):
    if not OFF1_LAUNCH.exists():
        return False
    old = OFF1_LAUNCH.read_text()
    if normalized(text) != old:
        return False
    # Every unified-diff line must carry only an allowed token change.
    diff = list(difflib.unified_diff(old.splitlines(), text.splitlines(),
                                     lineterm=""))
    allowed = ("5D1", "5E1", "p5d1-", "p5e1-", "OFF-control", "OFF-repeat",
               "Part 5D1", "Part 5E1")
    for line in diff:
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith(("+", "-")) and not any(t in line for t in allowed):
            return False
    return True


@check("no_live_capture_or_pad")
def c_nolive(text, _rep):
    m = re.search(r"env_text = .*?(?=\n    \(SCRATCH)", text, re.S)
    body = m.group(0) if m else text
    return ("PS2X_GS_CAPTURE=" not in body
            and "PS2X_GS_CAPTURE_STOP_TICK" not in body
            and "PS2X_PAD_SCRIPT" not in body
            and "PS2X_CD_IMAGE" not in body
            and "FORBIDDEN_ENV_KEYS" in text)


@check("scratch_is_p5e1")
def c_scratch(text, _rep):
    return "N8D7M12P5E1" in text and "/Users/brad/dev/ssx3-work/N8D7M12P5E1" in text \
        and "N8D7M12P5D1" not in text and "n8d7m12p5d1-" not in text \
        and "N8D7M12P5A/" not in text and '"N8D7M12P5A ' not in text


@check("lease_tag_p5e1")
def c_lease(text, _rep):
    return 'LEASE_TAG = "N8D7M12P5E1 replay"' in text \
        and "LEASE_FREE N8D7M12P5E1 done" in text \
        and "N8D7M12P5D1 replay" not in text


@check("one_run_guard")
def c_onerun(text, _rep):
    return ("--released-sha" in text and "one-run guard" in text
            and 'result.json").exists()' in text
            and "N8D7M12P5E1 receipt already exists" in text)


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


@check("marker_success_syntax")
def c_markers(text, _rep):
    keys = ("GB4_REPLAY_SUMMARY", "GB4_FRAME tick=2050",
            "GB4_REPLAY tick=", "[n8d7m12] replay ok",
            "[n8d7m12] replay failed", "replay rejected")
    return all(k in text for k in keys)


@check("off_census_never_fails")
def c_offcensus(text, _rep):
    m = re.search(r"def census_gate\(p\):(.*?)(?=\ndef )", text, re.S)
    if not m:
        return False
    body = m.group(1)
    if "return True" not in body:
        return False
    if '("128", "128"' in body or "CONTROL_ADDRS" in body:
        return False
    if "selected" in body.lower().replace("selected/oracle/tile census is not required", ""):
        # allow only the docstring mention, no gating logic
        logic = body.split('"""')[-1] if '"""' in body else body
        if "selected" in logic.lower() or "oracle" in logic.lower():
            return False
    m2 = re.search(r"def replay_complete\(.*?\):(.*?)(?=\ndef )", text, re.S)
    if not m2:
        return False
    rc = m2.group(1)
    if "census_gate(p)" not in rc:
        return False
    # Banned markers must not gate the code path (docstring mentions
    # of what OFF does NOT require are allowed).
    code = rc.split('"""')[-1] if '"""' in rc else rc
    for banned in ("[n8d7f]", "[n8d7l]", "[n8d5b]", "[n8d6a]",
                   "control=128", "CONTROL_ADDRS"):
        if banned in code:
            return False
    # error gate must be markers-only, never census absence
    if 'combined_errors = markers["errors"] + census' in text:
        return False
    return 'combined_errors = markers["errors"]' in text


@check("off_requires_41_rows")
def c_rows(text, _rep):
    m = re.search(r"def replay_complete\(.*?\):(.*?)(?=\ndef )", text, re.S)
    if not m:
        return False
    rc = m.group(1)
    count_kept = 'replay_rows") == 41' in rc or "replay_rows') == 41" in rc
    progress_kept = 'if markers["replay_rows"] != last_rows:' in text
    return count_kept and progress_kept


@check("off_exact_tick_sequence")
def c_ticks(text, _rep):
    # Static part: EXPECTED_TICKS is exactly 50..2050 step 50,
    # replay_markers parses the ordered replay_ticks list, and
    # replay_complete gates on replay_ticks == list(EXPECTED_TICKS).
    if "EXPECTED_TICKS = tuple(range(50, 2051, 50))" not in text:
        return False
    if '"replay_ticks"' not in text and "['replay_ticks']" not in text \
            and 'out["replay_ticks"]' not in text:
        return False
    m = re.search(r"def replay_complete\(.*?\):(.*?)(?=\ndef )", text, re.S)
    if not m or "replay_ticks\") == list(EXPECTED_TICKS)" not in m.group(1):
        return False
    # Functional part: run the real parser/gate on synthetic logs.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p5e1_launch_under_check", str(LAUNCH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if tuple(mod.EXPECTED_TICKS) != tuple(range(50, 2051, 50)):
        return False
    base = ["GB4_REPLAY_SUMMARY mode=queue backend=parallel packets=862958 "
            "priv=11499 transfers=25445 markers=2050",
            "GB4_FRAME tick=2050 backend=parallel pmode=ff21 present=b167a719",
            "[n8d7m12] replay ok: packets=862958 markers=2050"]

    def rows(ticks):
        return [f"GB4_REPLAY tick={t} vram=aa priv=bb present=cc"
                for t in ticks]
    exact = base + rows(range(50, 2051, 50))
    if not mod.replay_complete(mod.replay_markers(exact), {}):
        return False
    # 41 rows but tick 100 duplicated and tick 2050 missing: the count
    # gate alone would pass, the exact-sequence gate must fail it.
    dup_ticks = list(range(50, 2051, 50))
    dup_ticks[-1] = 100
    dup = base + rows(dup_ticks)
    dup_markers = mod.replay_markers(dup)
    if dup_markers.get("replay_rows") != 41:
        return False
    if mod.replay_complete(dup_markers, {}):
        return False
    # A missing tick (40 rows) must also fail.
    short = base + rows([t for t in range(50, 2051, 50) if t != 2050])
    if mod.replay_complete(mod.replay_markers(short), {}):
        return False
    return True


@check("ppm_hashes_pull_stays")
def c_pull(text, _rep):
    return ("def pull_outputs" in text and "vq-002050.ppm" in text
            and "parallel.hashes" in text
            and "SHA/size mismatch after pull" in text)


@check("keyguard_blocker_no_workaround")
def c_keyguard(text, _rep):
    return "BLOCKER: keyguard" in text and "never worked around" in text


@check("caps_wall_log_output_progress")
def c_caps(text, _rep):
    return ("WALL_CAP = 600" in text and "LOG_CAP = 16" in text
            and "OUTPUT_CAP = 64" in text and "PROGRESS_CAP = 180" in text)


@check("unique_empty_off2_outputs")
def c_outputs(text, _rep):
    return ("n8d7m12p5e1-frames-" in text and "n8d7m12p5e1-" in text
            and "already exists" in text and "is not empty" in text
            and "n8d7m12p5d1-frames-" not in text
            and "n8d7m12p5a-frames-" not in text)


@check("finally_force_stop_lease")
def c_finally(text, _rep):
    return ("am force-stop" in text and "lease not ours" in text
            and "LEASE_FREE N8D7M12P5E1 done" in text
            and "close_logger" in text)


@check("provisional_marking")
def c_prov(text, _rep):
    return "PROVISIONAL" in text and "provisional" in text.lower()


@check("complete_before_exit_drain")
def c_drain(text, _rep):
    complete_at = text.find("if replay_complete(markers, census):")
    exit_at = text.find("if not pidof():")
    return ("def drain_after_exit" in text and "DRAIN_SECS = 15" in text
            and "drain_after_exit(pid" in text
            and "process exited without complete receipt" in text
            and 0 < complete_at < exit_at)


@check("drain_bounded_by_wall")
def c_drainwall(text, _rep):
    return ("def drain_after_exit(pid, prior_count, wall_deadline)" in text
            and "min(time.monotonic() + DRAIN_SECS, wall_deadline)" in text
            and "wall_deadline = start + WALL_CAP" in text)


@check("env_double_sha")
def c_envsha(text, _rep):
    return ("pre-existing ps2x.env device SHA pair mismatch" in text
            and "preserved ps2x.env device/local SHA mismatch" in text
            and "restored ps2x.env device/local SHA mismatch" in text)


@check("cleanup_failure_fails")
def c_cleanup(text, _rep):
    return ("cleanup_errors" in text
            and "cleanup failure overrides" in text)


@check("no_graphics_verdict")
def c_noverdict(text, rep):
    return ("no graphics verdict" in text.lower()
            and "no graphics verdict" in rep.lower()
            and "No ON or OFF graphics verdict" in rep)


@check("report_unexecuted_command_table")
def c_report(text, rep):
    del text
    return ("--released-sha" in rep and "acceptance" in rep.lower()
            and "stop" in rep.lower() and "tick2050" in rep.lower()
            and "PROVISIONAL" in rep
            and "N8D7M12P5E1/launch.py --released-sha" in rep)


@check("report_predeclares_off2_vs_off1")
def c_predecl(text, rep):
    del text
    keys = ("N8D7M12P5D1/parallel.hashes" in rep,
            "priv" in rep and "present" in rep and "first differ" in rep,
            "PPM SHA" in rep,
            "voids" in rep,
            "is speed" in rep,
            "ON repeat" in rep)
    return all(keys)


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
                "marker_success_syntax", "no_live_capture_or_pad",
                "off_env_exact_minus_three",
                "off2_env_semantically_identical_to_off1",
                "off2_normalized_identical_to_off1",
                "off1_launcher_sha_pinned")
    verdict = "A" if passed == len(rows) else (
        "B" if any(r["check"] in mismatch and not r["pass"] for r in rows)
        else "OTHER")
    launch_sha = hashlib.sha256(LAUNCH.read_bytes()).hexdigest()
    out = {"brief": "N8D7M12P5E1", "checks": rows,
           "passed": f"{passed}/{len(rows)}", "verdict": verdict,
           "launch_sha": launch_sha,
           "off1_sha": OFF1_SHA,
           "note": "Static only. No device, build, install, or launch executed. "
                   "OFF1 and ON receipts preserved untouched."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{verdict} {passed}/{len(rows)} launch_sha={launch_sha}")
    for row in rows:
        print(("PASS " if row["pass"] else "FAIL ") + row["check"])
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    if "--self-check" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(main())
    raise SystemExit("usage: check.py [--self-check]")
