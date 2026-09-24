#!/usr/bin/env python3
"""N8D7M12 Part 7A gate: static diff gate + no-device self-tests.

No device, build, install, launch, or lease use. Every launcher
subprocess below exits at argument validation, SHA hold, serial-file
read, or the per-run one-run guard -- all of which precede the first
adb/preflight call in run() (proven structurally by
selftest_paths_precede_device). `--self-check` (or no-arg default)
runs all checks and writes check-result.json here.
"""
import ast
import difflib
import hashlib
import importlib.util
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LAUNCH = HERE / "launch.py"
REPORT = HERE / "REPORT.md"
P5A = REPO / "local" / "research" / "N8D7M12P5A" / "launch.py"
P5A_SHA = "287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e"
MAC_EXCERPT = (REPO / "local" / "research" / "N8D7M12P5F4P2"
               / "replay-excerpt.txt")
SCRATCH_BASE = Path("/Users/brad/dev/ssx3-work/N8D7M12P7")

PINS = {
    "apk": "da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262",
    "runner": "e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "stream": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
}
OLD_PINS = {
    "apk": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "runner": "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d",
}

CHECKS = []
NOTES = {}


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_launcher(*args, timeout=60):
    proc = subprocess.run([sys.executable, str(LAUNCH), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout + proc.stderr


def env_assign_source(text):
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and getattr(node.targets[0], "id", "") == "REPLAY_ENV_KEYS":
            return ast.get_source_segment(text, node)
    return None


def env_key_names(assign_source):
    return set(re.findall(r'"(PS2X_[A-Z0-9_]+)=', assign_source))


@check("p5a_anchor_unchanged")
def c_anchor(_text, _rep):
    return file_sha(P5A) == P5A_SHA


@check("pins_new_apk_runner")
def c_newpins(text, _rep):
    return PINS["apk"] in text and PINS["runner"] in text \
        and OLD_PINS["apk"] not in text and OLD_PINS["runner"] not in text


@check("pins_unchanged_turnip_hal_stream")
def c_oldpins(text, _rep):
    return PINS["turnip"] in text and PINS["hal"] in text \
        and PINS["stream"] in text


@check("apk_path_and_sizes")
def c_sizes(text, _rep):
    return "N8D7M12P6M6/app-release.apk" in text \
        and "N8D7M12P3/app-release.apk" not in text \
        and "153753116" in text and "1100696462" in text


@check("env_keys_p5a_plus_one")
def c_envproof(text, _rep):
    seg5 = env_assign_source(P5A.read_text())
    seg7 = env_assign_source(text)
    if not seg5 or not seg7:
        return False
    lines5 = seg5.splitlines()
    lines7 = seg7.splitlines()
    exact_append = (
        len(lines7) == len(lines5) + 1
        and lines7[:-2] == lines5[:-1]
        and lines7[-2] == '    "PS2X_GS_REPLAY_PKTSEQ=1",'
        and lines7[-1] == lines5[-1])
    keyed = (env_key_names(seg7)
             == env_key_names(seg5) | {"PS2X_GS_REPLAY_PKTSEQ"})
    return exact_append and keyed


@check("marker_check_plus_two")
def c_markers2(text, _rep):
    old = ("b\"PS2X_GS_REPLAY_ONDEVICE\"", "b\"PS2X_GS_REPLAY_CAPTURE\"",
           "b\"PS2XGSC1\"", "b\"GB4_REPLAY_SUMMARY\"",
           "b\"PS2X_N8D7F_SELECTED_CAPTURE\"", "b\"PS2X_N8D7L_ORACLE\"")
    new = ("b\"PS2X_GS_REPLAY_PKTSEQ\"", "b\"GB4_PKTSEQ tick=\"")
    return all(k in text for k in old + new)


@check("run_arg_plumbing")
def c_runarg(text, _rep):
    keys = ('sys.argv[1] != "--run"', 'not in ("run1", "run2")',
            'sys.argv[3] != "--released-sha"', "sys.argv[4] != script_sha",
            "SCRATCH_BASE / RUN", 'f"N8D7M12P7 {RUN} replay"',
            "n8d7m12p7-{RUN}-frames-", "n8d7m12p7-{RUN}-",
            "one-run guard: N8D7M12P7 {RUN}",
            "LEASE_FREE N8D7M12P7 {RUN} done",
            "global LEASE_TAG, SCRATCH, RUN")
    return all(k in text for k in keys)


@check("pktseq_extraction_gate")
def c_pktseq(text, _rep):
    keys = ("def pktseq_rows(lines)", "PKTSEQ_PATTERN",
            "GB4_PKTSEQ tick=(\\d+) seq=([0-9a-fA-F]{16}) commands=(\\d+)",
            "list(range(50, 2051, 50))",
            "(SCRATCH / \"pktseq.txt\")",
            "GB4_PKTSEQ rows not exactly 41 ticks 50..2050 in order",
            "result[\"pktseq_rows\"]",
            "PKTSEQ rows=41 ticks=50..2050")
    return all(k in text for k in keys)


# Diff allowlist: every added/removed line vs P5A is either an exact
# pktseq line (brief change 5, pure addition) or matches one pattern
# class. Class -> brief change: pins/docstring=1, env=2, markers=3,
# runid=4. pktseq uses exact lines (not patterns) so generic body lines
# (`for line in lines:`, `return None`) cannot mask a foreign edit.
DIFF_CLASSES = {
    "pins": (r"caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512"
             r"|da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262"
             r"|329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d"
             r"|e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1"
             r"|329e44db\.\.a218a3d|e5a3302c\.\.11af1"
             r"|N8D7M12P3/app-release\.apk|N8D7M12P6M6/app-release\.apk"
             r"|already-staged|gated APK|with runner|a608ed1|4fa0df1"),
    "env": r'"PS2X_GS_REPLAY_PKTSEQ=1",',
    "markers": (r'b"PS2X_GS_REPLAY_PKTSEQ"|b"GB4_PKTSEQ tick="'
                r'|b"PS2X_N8D7L_ORACLE"'),
    "runid": (r"N8D7M12 Part (5A|7)|EXACTLY ONE|per --run|one launch each"
              r"|Device patterns based on|--run|--released-sha|run1|run2"
              r"|sys\.argv|review hold|SCRATCH_BASE|SCRATCH = SCRATCH_BASE|RUN ="
              r"|/ RUN|{RUN}|LEASE_TAG|N8D7M12P5A|N8D7M12P7"
              r"|result\[\"run\"\]|run=\{RUN\}|n8d7m12p5a-|n8d7m12p7-"
              r"|one-run guard|LEASE_FREE|global LEASE_TAG|SCRIPT_SHA"),
}
PKTSEQ_ADDED = (
    '  "GB4_PKTSEQ tick=.. seq=.. commands=..",',
    'PKTSEQ_PATTERN = re.compile(',
    r'    r"GB4_PKTSEQ tick=(\d+) seq=([0-9a-fA-F]{16}) commands=(\d+)")',
    'def pktseq_rows(lines):',
    '    """Extract ordered worker-consumption rows; None unless exact 41.',
    '    Returns a list of (tick, seq, commands) for every GB4_PKTSEQ line,',
    '    or None unless the ticks are exactly 50..2050 in order (41 rows),',
    '    the same tick set as the GB4_REPLAY rows. Pure function: no device,',
    '    no filesystem, no globals.',
    '    """',
    '    rows = []',
    '    for line in lines:',
    '        match = PKTSEQ_PATTERN.search(line)',
    '        if match:',
    '            rows.append((int(match.group(1)), match.group(2).lower(),',
    '                         int(match.group(3))))',
    '    if [tick for tick, _, _ in rows] != list(range(50, 2051, 50)):',
    '        return None',
    '    return rows',
    '    (SCRATCH / "pktseq.txt").write_text(',
    r'        "".join(line + "\n" for line in lines if "GB4_PKTSEQ tick=" in line))',
    '    pktseq = pktseq_rows(lines)',
    '    if pktseq is None:',
    '        raise RuntimeError("GB4_PKTSEQ rows not exactly 41 ticks 50..2050 in order")',
    '    result["pktseq_rows"] = len(pktseq)',
    '    record(f"PKTSEQ rows=41 ticks=50..2050 commands_last={pktseq[-1][2]}")',
)


@check("diff_only_listed_changes")
def c_diff(text, _rep):
    old = P5A.read_text().splitlines()
    new = text.splitlines()
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    changed = [ln[1:] for ln in diff
               if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    compiled = {k: re.compile(v) for k, v in DIFF_CLASSES.items()}
    hunks, cur = [], []
    for ln in diff:
        if ln.startswith("@@"):
            if cur:
                hunks.append(cur)
                cur = []
            continue
        if ln.startswith("+++") or ln.startswith("---"):
            continue
        if ln[:1] in "+-":
            cur.append((ln[0], ln[1:]))
    if cur:
        hunks.append(cur)
    pending = list(PKTSEQ_ADDED)
    bad = []
    for hunk in hunks:
        # Blank separator lines are allowed only as reflow structure
        # inside a hunk whose every non-blank line is classified; a
        # blank-only hunk (or anything unclassified) fails.
        nonblank = [(sign, ln) for sign, ln in hunk if ln.strip()]
        if not nonblank:
            bad.append("<blank-only hunk>")
            continue
        for sign, ln in nonblank:
            if sign == "+" and ln in pending:
                pending.remove(ln)
            elif not any(rx.search(ln) for rx in compiled.values()):
                bad.append(ln)
    fired = {k for k, rx in compiled.items()
             if any(rx.search(ln) for ln in changed)}
    if not pending:
        fired.add("pktseq")
    NOTES["diff_changed_lines"] = len(changed)
    NOTES["diff_hunks"] = len(hunks)
    NOTES["diff_pktseq_consumed"] = f"{len(PKTSEQ_ADDED) - len(pending)}/{len(PKTSEQ_ADDED)}"
    NOTES["diff_classes_fired"] = sorted(fired)
    NOTES["diff_unmatched"] = bad[:10]
    return not bad and fired == set(compiled) | {"pktseq"}


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
            "PS2X_GS_REPLAY_PPM_TICKS=2050", "PS2X_GS_REPLAY_PKTSEQ=1",
            "PS2X_GS_REPLAY_PPM_DIR", "PS2X_GS_REPLAY_OUT")
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
    return ("--released-sha" in text and "--run" in text
            and "one-run guard" in text and 'result.json").exists()' in text)


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
            "GB4_REPLAY tick=", "GB4_PKTSEQ tick=",
            "[n8d7m12] replay ok",
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
    return ("n8d7m12p7-{RUN}-frames-" in text and "already exists" in text
            and "is not empty" in text)


@check("finally_force_stop_lease")
def c_finally(text, _rep):
    return ("am force-stop" in text and "lease not ours" in text
            and "LEASE_FREE N8D7M12P7 {RUN} done" in text
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


@check("drain_bounded_by_wall")
def c_drainwall(text, _rep):
    return ("def drain_after_exit(pid, prior_count, wall_deadline)" in text
            and "min(time.monotonic() + DRAIN_SECS, wall_deadline)" in text
            and "wall_deadline = start + WALL_CAP" in text)


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
    return ("--released-sha" in rep and "--run run1" in rep
            and "--run run2" in rep and "acceptance" in rep.lower()
            and "stop" in rep.lower() and "tick2050" in rep.lower()
            and "PROVISIONAL" in rep)


@check("selftest_paths_precede_device")
def c_precede(text, _rep):
    run_src = text[text.find("def run():"):]
    guard_at = run_src.find("one-run guard")
    device_at = min(run_src.find("preflight()"),
                    run_src.find("check_apk()\n    check_stream_local()\n"
                                 "    preflight()"))
    first_adb = run_src.find('adb("')
    first_shell = run_src.find("shell(")
    return 0 < guard_at < device_at \
        and (first_adb < 0 or device_at < first_adb) \
        and (first_shell < 0 or device_at < first_shell)


@check("selftest_arg_shape_exits")
def c_t1(_text, _rep):
    rc0, out0 = run_launcher()
    rc1, out1 = run_launcher("--released-sha", "x")
    rc2, out2 = run_launcher("--run", "run3", "--released-sha", "x")
    ok = (rc0 != 0 and "require --run run1|run2" in out0
          and rc1 != 0 and "require --run run1|run2" in out1
          and rc2 != 0 and "require --run run1|run2" in out2)
    untouched = (not (SCRATCH_BASE / "run1").exists()
                 and not (SCRATCH_BASE / "run2").exists())
    NOTES["selftest_arg_shape"] = f"rc={rc0},{rc1},{rc2}"
    return ok and untouched


@check("selftest_wrong_sha_exits")
def c_t4(_text, _rep):
    rc, out = run_launcher("--run", "run1", "--released-sha", "0" * 64)
    untouched = (not (SCRATCH_BASE / "run1").exists()
                 and not (SCRATCH_BASE / "run2").exists())
    NOTES["selftest_wrong_sha"] = f"rc={rc}"
    return rc != 0 and "SHA differs from reviewed pin" in out and untouched


@check("selftest_one_run_guard")
def c_t5(_text, _rep):
    run1 = SCRATCH_BASE / "run1"
    plant = run1 / "result.json"
    if plant.exists():
        NOTES["selftest_guard"] = "refused: real receipt present"
        return False
    try:
        run1.mkdir(parents=True, exist_ok=True)
        plant.write_text("{}\n")
        rc, out = run_launcher("--run", "run1", "--released-sha",
                               file_sha(LAUNCH))
    finally:
        plant.unlink(missing_ok=True)
        try:
            run1.rmdir()
        except OSError:
            pass
    NOTES["selftest_guard"] = f"rc={rc}"
    return rc != 0 and "one-run guard" in out


@check("selftest_pktseq_parser")
def c_t6(_text, _rep):
    spec = importlib.util.spec_from_file_location("p7_launch", LAUNCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mac_rows = MAC_EXCERPT.read_text().splitlines()[:41]
    if len(mac_rows) != 41 or not all(
            r.startswith("GB4_PKTSEQ tick=") for r in mac_rows):
        NOTES["selftest_pktseq"] = "mac excerpt shape changed"
        return False
    wrapped = [f"09-24 12:00:00.000 12345 12345 I ps2x : {r}"
               for r in mac_rows]
    good = mod.pktseq_rows(wrapped)
    ok_good = (good is not None and len(good) == 41
               and good[0][0] == 50 and good[-1] == (2050,
                   "79ee00a3024bfb44", 1737496))
    drop = mod.pktseq_rows(wrapped[:20] + wrapped[21:])
    swap = mod.pktseq_rows(wrapped[:10] + [wrapped[11], wrapped[10]]
                           + wrapped[12:])
    dup = mod.pktseq_rows(wrapped + wrapped[-1:])
    badhex = list(wrapped)
    badhex[5] = badhex[5].replace("seq=fc074a752258e1d2",
                                  "seq=fc074a752258e1d")
    malformed = mod.pktseq_rows(badhex)
    empty = mod.pktseq_rows([])
    NOTES["selftest_pktseq"] = (
        f"good={ok_good} drop={drop is None} swap={swap is None} "
        f"dup={dup is None} malformed={malformed is None} "
        f"empty={empty is None}")
    return ok_good and drop is None and swap is None and dup is None \
        and malformed is None and empty is None


@check("py_compile_both")
def c_pycompile(_text, _rep):
    py_compile.compile(str(LAUNCH), doraise=True)
    py_compile.compile(str(HERE / "check.py"), doraise=True)
    return True


@check("no_device_calls_in_checker")
def c_noself(_text, _rep):
    mine = (HERE / "check.py").read_text()
    # Exactly one subprocess site, and it execs only this Python + launch.py.
    runs = [m.start() for m in re.finditer(r"subprocess\.run\(", mine)]
    if len(runs) != 1:
        return False
    site = mine[runs[0]:runs[0] + 200]
    launcher_only = "[sys.executable, str(LAUNCH)" in site
    banned = re.findall(r"subprocess\.\s*(?:Popen|call|check_output)\b"
                        r"|os\s*\.\s*system\b|^\s*adb\s*\(", mine, re.M)
    # No quoted adb argv anywhere (regex form avoids self-matching).
    return launcher_only and not banned \
        and not re.search(r"""(['"])adb\1""", mine)


def main():
    text = LAUNCH.read_text()
    rep = REPORT.read_text() if REPORT.exists() else ""
    rows = []
    for name, fn in CHECKS:
        try:
            rows.append({"check": name, "pass": bool(fn(text, rep))})
        except Exception as exc:
            rows.append({"check": name, "pass": False,
                         "error": repr(exc)[:300]})
    passed = sum(1 for r in rows if r["pass"])
    mismatch = ("pins_new_apk_runner", "frame_filename_grounded",
                "marker_census_syntax", "no_live_capture_or_pad",
                "control128_numeric_census", "env_keys_p5a_plus_one",
                "diff_only_listed_changes")
    verdict = "A" if passed == len(rows) else (
        "B" if any(r["check"] in mismatch and not r["pass"] for r in rows)
        else "OTHER")
    launch_sha = file_sha(LAUNCH)
    out = {"brief": "N8D7M12P7-7A", "checks": rows,
           "passed": f"{passed}/{len(rows)}", "verdict": verdict,
           "launch_sha": launch_sha, "notes": NOTES,
           "note": "Static gate + no-device self-tests only. No adb, "
                   "install, launch, or lease executed."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{verdict} {passed}/{len(rows)} launch_sha={launch_sha}")
    for row in rows:
        extra = f" {row['error']}" if "error" in row else ""
        print(("PASS " if row["pass"] else "FAIL ") + row["check"] + extra)
    for key, value in NOTES.items():
        print(f"NOTE {key}={value}")
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    if "--self-check" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(main())
    raise SystemExit("usage: check.py [--self-check]")
