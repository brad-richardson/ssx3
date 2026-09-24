#!/usr/bin/env python3
"""N8D7M12 Part 5M3 static checker — read-only, device-free, no replay.

Proves the corrected Mac OFF driver (`mac_off.py`) is the reviewed Part 5M1
driver with only these changes: the private output root, result/lease
labels, and the pre-run cwd fixture symlink (`cwd/ps2xRecomp` -> the pinned
Part 1 fork's `ps2xRecomp` tree) plus its guards. It re-checks the Part 1
binary/stream/ON pins, the exact ON-minus-three-flags OFF env (unchanged
from 5M1), the ambient-PS2X clearing, dynamic one-slot lease + release in
`finally`, own-PID-only stop, one-run refusal, 300 s wall, 16/64 MiB caps,
the exact 41 ordered ticks, PPM tick2050 and the parse/backend gate.

It grounds the fixture only by reading the pinned fork HEAD
(`read_worktree_head`, no git process) and header SHA twice, and
functionally exercises the cwd-relative candidate resolution
(`read_first_candidate`) in a temporary directory. It never runs the
binary, never claims a lease, and touches no device.

Usage: python3 local/research/N8D7M12P5M3/check.py [--self-check]
"""
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DRIVER = HERE / "mac_off.py"
REPORT = HERE / "REPORT.md"
P5M1 = HERE.parent / "N8D7M12P5M1" / "mac_off.py"

PINS = {
    "binary_sha": "2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5",
    "binary_size": "8369016",
    "stream_sha": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
    "stream_size": "1100696462",
    "on_hashes_sha": "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290",
    "on_hashes_size": "2686",
    "on_ppm_sha": "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e",
    "on_ppm_size": "688143",
    "fork_head": "24801bcfa42611e5e36c8990183b793d28b4e5e8",
    "header_sha": "b8de8745e16d6a814763f69b0e8d1d54d957bf427f94ec2bc57f63e509f970cd",
    "header_size": "31244",
    "driver_sha": "to-be-filled-by-run",
}

WORK = Path.home() / "dev/ssx3-work"
FILES = {
    "binary": WORK / "N8D7M12/build/ps2xTest/ps2x_tests",
    "stream": WORK / "N8D7M6/n8d7m6.gs",
    "on_hashes": WORK / "N8D7M12/mac-parallel/parallel.hashes",
    "on_ppm": WORK / "N8D7M12/mac-parallel/vq-002050.ppm",
}
HEADER = WORK / "N8D7M12/PS2Recomp/ps2xRecomp/include/ps2recomp/instructions.h"

REMOVED_FLAGS = (
    "PS2X_N8D7F_SELECTED_CAPTURE",
    "PS2X_N8D7L_ORACLE",
    "PS2X_N8D5_TILE_CAPTURE",
)
KEPT_ENV = (
    "PS2X_GS_REPLAY_CAPTURE",
    "PS2X_GS_REPLAY_BACKEND",
    "PS2X_GS_REPLAY_STEP",
    "PS2X_GS_REPLAY_PPM_TICKS",
    "PS2X_GS_REPLAY_PPM_DIR",
    "PS2X_GS_REPLAY_OUT",
    "GRANITE_VULKAN_LIBRARY",
)
CHANGED_OUTPUT_KEYS = ("PS2X_GS_REPLAY_PPM_DIR", "PS2X_GS_REPLAY_OUT")
FIXTURE_BEGIN = "# P5M3-FIXTURE-BEGIN"
FIXTURE_END = "# P5M3-FIXTURE-END"

CHECKS = []


def check(name, kind="extra"):
    def deco(fn):
        CHECKS.append((name, kind, fn))
        return fn
    return deco


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def driver_text():
    return DRIVER.read_text()


def report_text():
    return REPORT.read_text() if REPORT.exists() else ""


def p5m1_text():
    return P5M1.read_text() if P5M1.exists() else ""


def strip_fixture(text):
    out, skip = [], False
    for line in text.splitlines():
        token = line.strip()
        if token == FIXTURE_BEGIN:
            skip = True
            continue
        if token == FIXTURE_END:
            skip = False
            continue
        if not skip:
            out.append(line)
    return "\n".join(out)


def normalize(text):
    text = text.replace("N8D7M12P5M1", "@ROOT@").replace("N8D7M12P5M3", "@ROOT@")
    text = text.replace("n8d7m12p5m1", "@LAB@").replace("n8d7m12p5m3", "@LAB@")
    return text


def body_nonblank(text):
    start = text.index("import hashlib")
    return [ln for ln in normalize(text[start:]).splitlines() if ln.strip()]


# --- pins ---------------------------------------------------------------

@check("driver_binary_stream_on_pins", "pin")
def c_pins(text, _rep, _mod):
    return all(pin in text for pin in (
        PINS["binary_sha"], PINS["stream_sha"], PINS["on_hashes_sha"],
        PINS["on_ppm_sha"]))


@check("pin_files_present_and_match", "pin")
def c_pinfile(_text, _rep, _mod):
    try:
        if FILES["binary"].stat().st_size != int(PINS["binary_size"]):
            return False
        if sha256_file(FILES["binary"]) != PINS["binary_sha"]:
            return False
        if FILES["on_hashes"].stat().st_size != int(PINS["on_hashes_size"]):
            return False
        if sha256_file(FILES["on_hashes"]) != PINS["on_hashes_sha"]:
            return False
        if FILES["on_ppm"].stat().st_size != int(PINS["on_ppm_size"]):
            return False
        if sha256_file(FILES["on_ppm"]) != PINS["on_ppm_sha"]:
            return False
        if FILES["stream"].stat().st_size != int(PINS["stream_size"]):
            return False
        if sha256_file(FILES["stream"]) != PINS["stream_sha"]:
            return False
    except OSError:
        return False
    return True


@check("on_pins_verified_in_driver", "pin")
def c_onpins(text, _rep, _mod):
    return ("Part 1 ON parallel.hashes pin mismatch" in text
            and "Part 1 ON vq-002050.ppm pin mismatch" in text
            and "ON_PINS" in text)


# --- fork / fixture provenance -----------------------------------------

@check("fork_pins_declared", "pin")
def c_forkdecls(text, _rep, _mod):
    return (PINS["fork_head"] in text and PINS["header_sha"] in text
            and str(PINS["header_size"]) in text
            and "FORK_PS2XRECOMP" in text and "n8d7m12-replay-core" in text)


@check("fork_provenance_grounded", "pin")
def c_forkground(_text, _rep, mod):
    """Ground fork HEAD (read-only) and header SHA twice on disk."""
    try:
        if mod.FORK_HEAD != PINS["fork_head"]:
            return False
        if str(mod.FORK_PS2XRECOMP) != str(WORK / "N8D7M12/PS2Recomp/ps2xRecomp"):
            return False
        heads = [mod.read_worktree_head(mod.FORK) for _ in range(2)]
        if heads != [PINS["fork_head"], PINS["fork_head"]]:
            return False
        if HEADER.stat().st_size != int(PINS["header_size"]):
            return False
        if sha256_file(HEADER) != PINS["header_sha"]:
            return False
        if sha256_file(HEADER) != PINS["header_sha"]:
            return False
    except OSError:
        return False
    return True


@check("fixture_guards_in_driver", "guard")
def c_fixguards(text, _rep, _mod):
    return ("def make_cwd_fixture" in text
            and "CWD_FIXTURE.symlink_to(FORK_PS2XRECOMP" in text
            and "os.path.realpath" in text
            and "fixture resolves outside pinned tree" in text
            and "cwd fixture already exists" in text
            and "def check_fork_pins" in text
            and "fixture did not make candidate 1 readable" in text
            and "fixture header does not resolve to pinned header" in text
            and text.count("file_sha(header) for _ in range(2)") >= 1
            and "make_cwd_fixture()" in text)


@check("fixture_candidate_resolution_functional", "contract")
def c_fixfunc(_text, _rep, mod):
    """Exercise the cwd-relative candidate lookup in a temp dir (no run)."""
    if tuple(mod.INSTRUCTIONS_CANDIDATES) != (
            "ps2xRecomp/include/ps2recomp/instructions.h",
            "../ps2xRecomp/include/ps2recomp/instructions.h",
            "../../ps2xRecomp/include/ps2recomp/instructions.h"):
        return False
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # No fixture: the first candidate must not resolve.
        if mod.read_first_candidate(base) is not None:
            return False
        # Fixture makes candidate 1 (cwd/ps2xRecomp/...) resolve.
        header = base / "ps2xRecomp/include/ps2recomp/instructions.h"
        header.parent.mkdir(parents=True)
        header.write_text("enum VU0_S1_ { VU0_S1_FIRST = 0 };\n")
        if mod.read_first_candidate(base) != header:
            return False
        # Candidate 1 absent but candidate 2 (../ps2xRecomp/...) resolves.
        sub = base / "inner"
        sub.mkdir()
        got = mod.read_first_candidate(sub)
        if got is None or got.resolve() != header.resolve():
            return False
    # In an isolated empty tree no candidate resolves (empty file falls
    # through, directories are not files).
    with tempfile.TemporaryDirectory() as td2:
        empty = Path(td2)
        (empty / "ps2xRecomp/include/ps2recomp").mkdir(parents=True)
        (empty / "ps2xRecomp/include/ps2recomp/instructions.h").write_text("")
        if mod.read_first_candidate(empty) is not None:
            return False
    return True


@check("diff_limited_to_fixture_and_labels", "contract")
def c_diff(_text, _rep, _mod):
    """The 5M3 body equals 5M1 once fixture regions and root/labels drop."""
    old, new = p5m1_text(), driver_text()
    if not old or FIXTURE_BEGIN not in new or FIXTURE_END not in new:
        return False
    # The fixture must be the only 5M3 addition: more begin/end markers is fine,
    # but every marked region must be removable and leave the 5M1 body.
    if body_nonblank(old) != body_nonblank(strip_fixture(new)):
        return False
    # The fixture markers only wrap additions, so stripping removes lines.
    return len(strip_fixture(new)) < len(new)


# --- exact env diff and no replay-env change ---------------------------

@check("removed_flags_exactly_three", "contract")
def c_removed(text, _rep, _mod):
    m = re.search(r"REMOVED_FLAGS = \((.*?)\)", text, re.S)
    if not m:
        return False
    flags = re.findall(r'"(PS2X_[A-Z0-9_]+)"', m.group(1))
    return flags == list(REMOVED_FLAGS)


@check("on_env_declares_three_flags_kept_keys", "contract")
def c_onenv(_text, _rep, mod):
    env = mod.ON_ENV
    if any(env.get(f) != "1" for f in REMOVED_FLAGS):
        return False
    if env.get("PS2X_GS_REPLAY_BACKEND") != "parallel":
        return False
    if env.get("PS2X_GS_REPLAY_STEP") != "50":
        return False
    if env.get("PS2X_GS_REPLAY_PPM_TICKS") != "2050":
        return False
    if env.get("PS2X_GS_REPLAY_CAPTURE") != str(mod.STREAM):
        return False
    if env.get("GRANITE_VULKAN_LIBRARY") != "/opt/homebrew/lib/libvulkan.1.dylib":
        return False
    return all(k in env for k in KEPT_ENV)


@check("no_ps2x_replay_env_changes", "contract")
def c_noenvchange(_text, _rep, mod):
    """The OFF replay env must be identical to the reviewed Part 5M1 env.

    Only the two private output-path values may differ between the two
    drivers; every other replay key (capture/backend/step/ppm tick/flags
    and the three removed flags) must be byte-identical.
    """
    mod1 = load(P5M1, "p5m1_ref")
    if mod1.ON_ENV != mod.ON_ENV:
        return False
    if tuple(mod1.REMOVED_FLAGS) != tuple(mod.REMOVED_FLAGS):
        return False
    if tuple(mod1.CHANGED_OUTPUT_KEYS) != tuple(mod.CHANGED_OUTPUT_KEYS):
        return False
    off1 = mod1.off_env(mod1.PPM_DIR, mod1.HASHES_PATH)
    off3 = mod.off_env(mod.PPM_DIR, mod.HASHES_PATH)
    for key in CHANGED_OUTPUT_KEYS:
        if key not in off1 or key not in off3:
            return False
        del off1[key]
        del off3[key]
    return off1 == off3


@check("off_env_diff_exact", "contract")
def c_offdiff(_text, _rep, mod):
    off, removed, changed = mod.assert_env_diff()
    return (set(removed) == set(REMOVED_FLAGS)
            and set(changed) == set(CHANGED_OUTPUT_KEYS)
            and set(off) - set(mod.ON_ENV) == set()
            and set(mod.ON_ENV) - set(off) == set(REMOVED_FLAGS)
            and all(f not in off for f in REMOVED_FLAGS))


@check("no_live_keys", "contract")
def c_nolive(text, _rep, _mod):
    return ("FORBIDDEN_PREFIXES" in text and "forbidden live key in child env" in text
            and "PS2X_GS_CAPTURE" in text and "PS2X_PAD_SCRIPT" in text
            and "PS2X_CD_IMAGE" in text
            and 'startswith("PS2X_")' in text
            and "ambient PS2X_* cleared" in text)


@check("ambient_ps2x_cannot_leak", "contract")
def c_ambient(_text, _rep, mod):
    off, _removed, _changed = mod.assert_env_diff()
    ambient = {
        "PATH": "/usr/bin:/bin",
        "GRANITE_VULKAN_LIBRARY": "/opt/homebrew/lib/libvulkan.1.dylib",
        "PS2X_GS_REPLAY_CAPTURE": "/tmp/evil.gs",
        "PS2X_GS_REPLAY_BACKEND": "cpu",
        "PS2X_N8D7F_SELECTED_CAPTURE": "1",
        "PS2X_LIVE_JUNK": "1",
    }
    env, inherited = mod.child_env(off, ambient=ambient)
    if env.get("PATH") != "/usr/bin:/bin":
        return False
    if env.get("GRANITE_VULKAN_LIBRARY") != ambient["GRANITE_VULKAN_LIBRARY"]:
        return False
    if env.get("PS2X_GS_REPLAY_CAPTURE") != off["PS2X_GS_REPLAY_CAPTURE"]:
        return False
    if env.get("PS2X_GS_REPLAY_BACKEND") != "parallel":
        return False
    if "PS2X_N8D7F_SELECTED_CAPTURE" in env or "PS2X_LIVE_JUNK" in env:
        return False
    got = {k for k in env if k.startswith("PS2X_")}
    want = {k for k in off if k.startswith("PS2X_")}
    if got != want or "PS2X_GS_REPLAY_CAPTURE" not in inherited:
        return False
    bad = dict(off)
    bad["PS2X_GS_CAPTURE"] = "x"
    try:
        mod.child_env(bad, ambient={})
        return False
    except RuntimeError:
        pass
    return True


@check("granite_vulkan_library_pin", "pin")
def c_granite(text, _rep, _mod):
    return ('GRANITE_VULKAN_LIBRARY = "/opt/homebrew/lib/libvulkan.1.dylib"' in text
            and '"GRANITE_VULKAN_LIBRARY"' in text)


# --- lease ---------------------------------------------------------------

@check("lease_dynamic_api_no_hardcoded_slot", "guard")
def c_lease(text, _rep, _mod):
    return ("from p_lane_lease import claim, release" in text
            and "claim(LEASE_LABEL)" in text
            and "if slot is None" in text
            and "release(slot)" in text
            and re.search(r"p_lane_lease\.py (claim|release) [12]\b", text) is None
            and '"/tmp/ssx3-p-lane' not in text)


@check("lease_released_in_finally", "guard")
def c_finally(text, _rep, _mod):
    tail = text[text.rfind("finally:"):]
    return "release(slot)" in tail and "lease_claimed" in text


@check("own_pid_only_no_broad_kill", "guard")
def c_ownpid(text, _rep, _mod):
    if re.search(r"\bpkill\b|\bpgrep\b|\bkillall\b", text):
        return False
    return "def stop_child(proc)" in text \
        and "proc.terminate()" in text and "proc.kill()" in text \
        and "child.pid" in text


# --- guards/caps ---------------------------------------------------------

@check("one_run_guard_refuses_reuse", "guard")
def c_onerun(text, _rep, _mod):
    return ("mac-off output dir already exists" in text
            and "N8D7M12P5M3 receipt already exists" in text
            and "OUT_DIR.exists()" in text)


@check("wall_cap_300", "guard")
def c_wall(text, _rep, _mod):
    return "WALL_CAP = 300" in text and "s wall cap" in text \
        and "elapsed >= WALL_CAP" in text


@check("log_cap_16", "guard")
def c_log(text, _rep, _mod):
    return "LOG_CAP = 16 * 1024 * 1024" in text \
        and "16 MiB log cap exceeded" in text


@check("output_cap_64", "guard")
def c_output(text, _rep, _mod):
    return "OUTPUT_CAP = 64 * 1024 * 1024" in text \
        and "output cap" in text and "output_bytes_under" in text


# --- rows / ppm / errors -------------------------------------------------

@check("expected_ticks_step50", "contract")
def c_ticks(_text, _rep, mod):
    return tuple(mod.EXPECTED_TICKS) == tuple(range(50, 2051, 50)) \
        and len(mod.EXPECTED_TICKS) == 41


@check("exact_ticks_gate_functional", "contract")
def c_ticksfun(_text, _rep, mod):
    base = ["GB4_REPLAY_SUMMARY mode=queue backend=parallel drop_priv=0 "
            "packets=862958 priv=11499 transfers=25445 markers=2050 "
            "readbacks=0 clears=0 samples=41 rtz=off rounded_packets=0",
            "GB4_FRAME tick=2050 backend=parallel pmode=ff21 present=d19b96fe"]

    def rows(ticks):
        return [(t, "aa", "bb", "cc") for t in ticks]

    with tempfile.TemporaryDirectory() as td:
        ppm_dir = Path(td)
        (ppm_dir / "vq-002050.ppm").write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")
        old = mod.PPM_DIR
        mod.PPM_DIR = ppm_dir
        try:
            exact = rows(range(50, 2051, 50))
            if not mod.replay_complete(0, mod.replay_markers(base), exact):
                return False
            if mod.replay_complete(1, mod.replay_markers(base), exact):
                return False
            if mod.replay_complete(0, mod.replay_markers(
                    base + ["GB4_REPLAY_PARSE_ERROR boom"]), exact):
                return False
            if mod.replay_complete(0, mod.replay_markers(
                    base + ["Failed: 1"]), exact):
                return False
            dup = list(range(50, 2051, 50))
            dup[-1] = 100
            if mod.replay_complete(0, mod.replay_markers(base), rows(dup)):
                return False
            short = [t for t in range(50, 2051, 50) if t != 2050]
            if mod.replay_complete(0, mod.replay_markers(base), rows(short)):
                return False
        finally:
            mod.PPM_DIR = old
    return True


@check("ppm_tick2050", "contract")
def c_ppm(text, _rep, _mod):
    return '"vq-002050.ppm"' in text \
        and '"PS2X_GS_REPLAY_PPM_TICKS": "2050"' in text


@check("no_parse_backend_error", "contract")
def c_errors(_text, _rep, mod):
    lines = ["GB4_REPLAY_PARSE_ERROR boom"]
    return bool(mod.replay_markers(lines)["errors"]) \
        and not mod.replay_markers(["GB4_FRAME tick=2050 backend=parallel "
                                    "pmode=ff21 present=x"])["errors"]


@check("classify_outcomes_functional", "contract")
def c_classify(_text, _rep, mod):
    good = [(t, "a", "b", "c") for t in mod.EXPECTED_TICKS]
    pre = list(good)
    pre[5] = (pre[5][0], "z", "b", "c")
    t2050 = list(good)
    t2050[-1] = (t2050[-1][0], "z", "b", "c")
    return (mod.classify_off_vs_on(good, list(good), "x", "x")[0]
            == "flag-unperturbed"
            and mod.classify_off_vs_on(good, pre, "x", "x")[0]
            == "void-pre2050"
            and mod.classify_off_vs_on(good, t2050, "x", "x")[0]
            == "tick2050-only"
            and mod.classify_off_vs_on(good, list(good), "x", "y")[0]
            == "tick2050-only")


# --- self-check / no run -------------------------------------------------

@check("self_check_runs_no_replay", "guard")
def c_norun(text, _rep, _mod):
    if 'if __name__ == "__main__":' not in text:
        return False
    if 'sys.argv[1] != "--released-sha"' not in text:
        return False
    if "raise SystemExit" not in text:
        return False
    return 'run()' in text.split('if __name__ == "__main__":')[1]


@check("driver_import_creates_no_output", "guard")
def c_nooutput(_text, _rep, mod):
    return (not mod.OUT_DIR.exists()
            and mod.result.get("replay_count") == 0
            and mod.lease_claimed is False)


@check("no_mac_off_result_yet", "guard")
def c_noresult(_text, _rep, mod):
    return not (mod.SCRATCH / "result.json").exists() \
        and not mod.OUT_DIR.exists()


@check("no_adb_no_build_no_fork_edit", "guard")
def c_nobuild(text, _rep, _mod):
    low = text.lower()
    return (".Popen([str(BINARY)]" in text
            and "adb" not in low
            and "cmake" not in low
            and "ninja" not in low
            and not re.search(r"git\s+(commit|add|reset|clean|checkout|push|"
                              r"restore|rm|rmdir|mv|stash)\b", low))


@check("checker_device_free_and_leaseless", "guard")
def c_devicefree(_text, _rep, _mod):
    mine = (HERE / "check.py").read_text()
    banned = re.compile(
        r"^\s*(?:import\s+subprocess|from\s+subprocess)\b"
        r"|subprocess\s*\.\s*(?:run|Popen|call)"
        r"|os\s*\.\s*(?:system|symlink|symlinkat)"
        r"|(?:^|[^\w.])adb\s*\("
        r"|^\s*(?:import|from)\s+p_lane_lease\b"
        r"|mod\s*\.\s*(?:run|claim|release|make_cwd_fixture|check_fork_pins)\s*\(",
        re.M)
    return not banned.search(mine)


# --- REPORT ---------------------------------------------------------------

@check("report_prepared_unexecuted", "contract")
def c_prep(_text, rep, _mod):
    low = rep.lower()
    return ("PREPARED" in rep and "unexecuted" in low
            and "no replay" in low and "no run" in low)


@check("report_acceptance_stop_table", "contract")
def c_table(_text, rep, _mod):
    low = rep.lower()
    return ("acceptance" in low and "stop" in low and "tick2050" in low
            and "--released-sha" in rep and "585" in rep and "PROVISIONAL" in rep)


@check("report_exact_command", "contract")
def c_cmd(_text, rep, _mod):
    return ("local/research/N8D7M12P5M3/mac_off.py --released-sha" in rep
            and "local/research/N8D7M12P5M3/check.py --self-check" in rep)


@check("report_outcomes_predeclared", "contract")
def c_outcomes(_text, rep, _mod):
    return ("flag-unperturbed" in rep
            and "void-pre2050" in rep
            and "tick2050-only" in rep
            and "separately gated" in rep.lower())


@check("report_env_matrix", "contract")
def c_matrix(_text, rep, _mod):
    return all(f in rep for f in REMOVED_FLAGS) \
        and "parallel" in rep and "2050" in rep and "GRANITE_VULKAN_LIBRARY" in rep


@check("report_fixture_documented", "contract")
def c_fixdoc(_text, rep, _mod):
    return ("ps2xRecomp" in rep and "symlink" in rep.lower()
            and PINS["fork_head"] in rep and PINS["header_sha"] in rep)


@check("no_graphics_verdict", "contract")
def c_noverdict(_text, rep, _mod):
    low = rep.lower()
    return ("no graphics" in low and "no mac off result" in low)


def main():
    text = driver_text()
    rep = report_text()
    try:
        mod = load(DRIVER, "p5m3_mac_off")
    except Exception as exc:  # pragma: no cover
        print(f"driver import failed: {exc!r}")
        mod = None

    rows = []
    for name, kind, fn in CHECKS:
        try:
            ok = bool(fn(text, rep, mod)) if mod is not None else False
        except Exception as exc:
            rows.append({"check": name, "kind": kind, "pass": False,
                         "error": repr(exc)})
            continue
        rows.append({"check": name, "kind": kind, "pass": ok})

    passed = sum(1 for r in rows if r["pass"])
    contract_fail = any(not r["pass"] and r["kind"] in ("pin", "contract")
                        for r in rows)
    verdict = "A" if passed == len(rows) else ("B" if contract_fail else "OTHER")
    launch_sha = hashlib.sha256(DRIVER.read_bytes()).hexdigest()
    out = {"brief": "N8D7M12P5M3", "checks": rows,
           "passed": f"{passed}/{len(rows)}", "verdict": verdict,
           "mac_off_sha": launch_sha,
           "note": "Static/functional only. No replay, build, device, lease or "
                   "binary execution. Mac OFF result remains unproved."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{verdict} {passed}/{len(rows)} mac_off_sha={launch_sha}")
    for r in rows:
        print(("PASS " if r["pass"] else "FAIL ") + r["check"])
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    if "--self-check" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(main())
    raise SystemExit("usage: check.py [--self-check]")
