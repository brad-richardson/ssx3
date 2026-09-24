#!/usr/bin/env python3
"""N8D7M12 Part 5M3: one Mac OFF replay driver (PREPARED, unexecuted).

Reviewed-SHA-held driver for EXACTLY ONE diagnostic Mac replay that is the
OFF control of the Part 1 Mac ON replay. Same binary, same stream, same
parallel backend, step 50, PPM tick 2050; the only differences from ON are
the three measurement flags removed (absent, not =0):
    PS2X_N8D7F_SELECTED_CAPTURE
    PS2X_N8D7L_ORACLE
    PS2X_N8D5_TILE_CAPTURE
plus the private OFF output paths.

This is the Part 5M1 driver with one harness correction. The full
``ps2x_tests`` binary runs one CodeGenerator suite test that reads
``instructions.h`` from cwd-relative candidates; from the driver's private
cwd it was not found, so Part 5M2 exited 1 (suite 584/585) even though the
replay itself passed. Before the run this driver creates a private cwd
fixture symlink ``cwd/ps2xRecomp`` at the pinned Part 1 fork's
``ps2xRecomp`` tree, so the first candidate resolves. The fixture is a
test-suite fixture only: it is not on the replay path and changes no
replay env.

Inputs (N8D7M12 Part 1 REPORT sections 1/3/4):
- binary  ~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests      (SHA 2a0446e8..ae5)
- stream  ~/dev/ssx3-work/N8D7M6/n8d7m6.gs                        (SHA f6a78f71..a593)
- Mac ON  ~/dev/ssx3-work/N8D7M12/mac-parallel/{parallel.hashes,vq-002050.ppm}
- fork    ~/dev/ssx3-work/N8D7M12/PS2Recomp @ 24801bc (branch
          n8d7m12-replay-core), ps2xRecomp tree only for the fixture

No replay, boot, build, device or lease action may run before the
orchestrator releases the reviewed SHA in a separate run gate (require
--released-sha <mac_off.py SHA-256>). One mini P-lane slot is claimed
dynamically through local/tooling/p_lane_lease.py claim()/release() and is
always freed in `finally`. The child is stopped by its own PID only; no
broad kill is ever issued. Wall, log and output caps are enforced. A
diagnostic wall time is never a speed number. No Mac OFF result and no
graphics cause are produced by this preparation part.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "local" / "tooling"))
from p_lane_lease import claim, release  # noqa: E402

SCRATCH = Path.home() / "dev/ssx3-work" / "N8D7M12P5M3"
OUT_DIR = SCRATCH / "mac-off"
CWD = OUT_DIR / "cwd"
PPM_DIR = OUT_DIR / "frames"
HASHES_PATH = OUT_DIR / "parallel.hashes"
LOG_PATH = OUT_DIR / "run.log"

BINARY = Path.home() / "dev/ssx3-work" / "N8D7M12" / "build" / "ps2xTest" / "ps2x_tests"
STREAM = Path.home() / "dev/ssx3-work" / "N8D7M6" / "n8d7m6.gs"
ON_HASHES = Path.home() / "dev/ssx3-work" / "N8D7M12" / "mac-parallel" / "parallel.hashes"
ON_PPM = Path.home() / "dev/ssx3-work" / "N8D7M12" / "mac-parallel" / "vq-002050.ppm"

BINARY_SHA = "2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5"
BINARY_SIZE = 8369016
STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
STREAM_SIZE = 1100696462
ON_HASHES_SHA = "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290"
ON_HASHES_SIZE = 2686
ON_PPM_SHA = "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e"
ON_PPM_SIZE = 688143

# P5M3-FIXTURE-BEGIN
# Pinned Part 1 fork (REPORT section 1) — read-only fixture provenance.
FORK = Path.home() / "dev/ssx3-work" / "N8D7M12" / "PS2Recomp"
FORK_HEAD = "24801bcfa42611e5e36c8990183b793d28b4e5e8"
FORK_PS2XRECOMP = FORK / "ps2xRecomp"
HEADER_REL = "include/ps2recomp/instructions.h"
HEADER_SHA = "b8de8745e16d6a814763f69b0e8d1d54d957bf427f94ec2bc57f63e509f970cd"
HEADER_SIZE = 31244
CWD_FIXTURE = CWD / "ps2xRecomp"
# The same cwd-relative candidates code_generator_tests.cpp tries in order.
INSTRUCTIONS_CANDIDATES = (
    "ps2xRecomp/include/ps2recomp/instructions.h",
    "../ps2xRecomp/include/ps2recomp/instructions.h",
    "../../ps2xRecomp/include/ps2recomp/instructions.h",
)
# P5M3-FIXTURE-END

GRANITE_VULKAN_LIBRARY = "/opt/homebrew/lib/libvulkan.1.dylib"

# Exact Mac ON env (Part 1 REPORT section 4). The three measurement flags
# are present here as "1" so the OFF diff is explicit and checkable.
ON_ENV = {
    "PS2X_GS_REPLAY_CAPTURE": str(STREAM),
    "PS2X_GS_REPLAY_BACKEND": "parallel",
    "PS2X_N8D7F_SELECTED_CAPTURE": "1",
    "PS2X_N8D7L_ORACLE": "1",
    "PS2X_N8D5_TILE_CAPTURE": "1",
    "PS2X_GS_REPLAY_STEP": "50",
    "PS2X_GS_REPLAY_PPM_TICKS": "2050",
    "PS2X_GS_REPLAY_PPM_DIR": str(ON_HASHES.parent),
    "PS2X_GS_REPLAY_OUT": str(ON_HASHES),
    "GRANITE_VULKAN_LIBRARY": GRANITE_VULKAN_LIBRARY,
}
REMOVED_FLAGS = (
    "PS2X_N8D7F_SELECTED_CAPTURE",
    "PS2X_N8D7L_ORACLE",
    "PS2X_N8D5_TILE_CAPTURE",
)
CHANGED_OUTPUT_KEYS = ("PS2X_GS_REPLAY_PPM_DIR", "PS2X_GS_REPLAY_OUT")
FORBIDDEN_PREFIXES = ("PS2X_GS_CAPTURE", "PS2X_PAD_SCRIPT", "PS2X_CD_IMAGE")
FORBIDDEN_ENV_KEYS = ("PS2X_GS_CAPTURE=", "PS2X_GS_CAPTURE_STOP_TICK",
                      "PS2X_PAD_SCRIPT", "PS2X_CD_IMAGE")

# Exact step-50 tick sequence through tick2050: 50,100,...,2050 (41 rows).
EXPECTED_TICKS = tuple(range(50, 2051, 50))
WALL_CAP = 300
LOG_CAP = 16 * 1024 * 1024
OUTPUT_CAP = 64 * 1024 * 1024
LEASE_LABEL = "n8d7m12p5m3-mac-off"
COMPLETE = "first complete tick2050 summary/frame/41-row receipt (PROVISIONAL OFF)"

ROW_RE = re.compile(r"GB4_REPLAY tick=(\d+) vram=([0-9a-f]+) "
                    r"priv=([0-9a-f]+) present=([0-9a-f]+)")

result = {"brief": "N8D7M12P5M3", "replay_count": 0, "hashes": {},
          "events": [], "verdict": "not found", "provisional": True,
          "first_failure": "not found"}

child = None
slot = None
lease_claimed = False
log_stream = None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(message):
    print(message, flush=True)
    result["events"].append(message)
    if SCRATCH.exists():
        with (SCRATCH / "driver.log").open("a") as handle:
            handle.write(message + "\n")
        (SCRATCH / "result.json").write_text(json.dumps(result, indent=2) + "\n")


def off_env(ppm_dir, hashes_path):
    """Build the OFF env from the exact ON env (three flags removed)."""
    env = dict(ON_ENV)
    for flag in REMOVED_FLAGS:
        env.pop(flag, None)
    env["PS2X_GS_REPLAY_PPM_DIR"] = str(ppm_dir)
    env["PS2X_GS_REPLAY_OUT"] = str(hashes_path)
    return env


def assert_env_diff():
    """Prove OFF == ON minus exactly the three flags plus output paths."""
    off = off_env(PPM_DIR, HASHES_PATH)
    removed = set(ON_ENV) - set(off)
    added = set(off) - set(ON_ENV)
    changed = {k for k in set(ON_ENV) & set(off) if ON_ENV[k] != off[k]}
    if removed != set(REMOVED_FLAGS):
        raise RuntimeError(f"env diff removed set mismatch: {sorted(removed)}")
    if added:
        raise RuntimeError(f"env diff added keys: {sorted(added)}")
    if changed != set(CHANGED_OUTPUT_KEYS):
        raise RuntimeError(f"env diff changed keys mismatch: {sorted(changed)}")
    return off, sorted(removed), sorted(changed)


def child_env(off, ambient=None):
    """Build the child env as an exact OFF control.

    Keep the OS environment (PATH, Vulkan loader, ...) but clear every
    inherited ``PS2X_*`` key before adding the declared OFF env, so no
    ambient ``PS2X_*`` setting (live capture keys, a stray
    selected/oracle/tile flag, or a different replay capture/backend) can
    leak into the run. The result's ``PS2X_*`` key set must equal exactly
    the OFF env's. ``ambient`` is injectable so the static checker can
    prove the clearing without spawning a process.
    """
    env = dict(os.environ if ambient is None else ambient)
    inherited = sorted(k for k in env if k.startswith("PS2X_"))
    for key in list(env):
        if key.startswith("PS2X_"):
            del env[key]
    env.update(off)
    for key in list(env):
        if any(key.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            raise RuntimeError(f"forbidden live key in child env: {key}")
    off_keys = {k for k in off if k.startswith("PS2X_")}
    got = {k for k in env if k.startswith("PS2X_")}
    if got != off_keys:
        raise RuntimeError(
            "PS2X_* env is not exactly the OFF set: "
            f"extra={sorted(got - off_keys)} missing={sorted(off_keys - got)}")
    return env, inherited


def check_pins():
    """Double-hash binary and stream and verify the Part 1 ON pins."""
    if BINARY.stat().st_size != BINARY_SIZE:
        raise RuntimeError("binary size mismatch")
    b_reads = [file_sha(BINARY) for _ in range(2)]
    result["hashes"]["binary"] = b_reads
    record(f"HASH binary {b_reads[0]} {b_reads[1]} ({BINARY_SIZE} B)")
    if b_reads != [BINARY_SHA, BINARY_SHA]:
        raise RuntimeError("binary SHA mismatch")

    if STREAM.stat().st_size != STREAM_SIZE:
        raise RuntimeError("stream size mismatch")
    s_reads = [file_sha(STREAM) for _ in range(2)]
    result["hashes"]["stream"] = s_reads
    record(f"HASH stream {s_reads[0]} {s_reads[1]} ({STREAM_SIZE} B)")
    if s_reads != [STREAM_SHA, STREAM_SHA]:
        raise RuntimeError("stream SHA mismatch")

    if ON_HASHES.stat().st_size != ON_HASHES_SIZE or file_sha(ON_HASHES) != ON_HASHES_SHA:
        raise RuntimeError("Part 1 ON parallel.hashes pin mismatch")
    if ON_PPM.stat().st_size != ON_PPM_SIZE or file_sha(ON_PPM) != ON_PPM_SHA:
        raise RuntimeError("Part 1 ON vq-002050.ppm pin mismatch")
    record("ON_PINS on hashes + ppm verified (Part 1)")


# P5M3-FIXTURE-BEGIN
def read_worktree_head(fork):
    """Resolve a checkout's HEAD to a commit SHA read-only (no git process).

    Handles both a plain ``.git`` directory and a linked-worktree ``.git``
    file (``gitdir: ...``; the ref lives in the common dir via
    ``commondir``). Used to verify the pinned Part 1 fork revision before
    the cwd fixture is created.
    """
    dotgit = Path(fork) / ".git"
    if dotgit.is_dir():
        gitdir = dotgit
    elif dotgit.is_file():
        line = dotgit.read_text().strip()
        if not line.startswith("gitdir:"):
            raise RuntimeError(f"unrecognized .git file: {line!r}")
        gitdir = Path(line.split("gitdir:", 1)[1].strip())
    else:
        raise RuntimeError(f"no .git at {fork}")
    head = (gitdir / "HEAD").read_text().strip()
    if not head.startswith("ref:"):
        return head
    ref = head.split("ref:", 1)[1].strip()
    common = gitdir
    commondir = gitdir / "commondir"
    if commondir.is_file():
        common = (gitdir / commondir.read_text().strip()).resolve()
    ref_file = common / ref
    if ref_file.is_file():
        return ref_file.read_text().strip()
    packed = common / "packed-refs"
    if packed.is_file():
        for line in packed.read_text().splitlines():
            if line.endswith(" " + ref):
                return line.split(" ", 1)[0]
    raise RuntimeError(f"cannot resolve ref {ref}")


def read_first_candidate(cwd, candidates=INSTRUCTIONS_CANDIDATES):
    """Mirror code_generator_tests.cpp readFileFromCandidates from ``cwd``."""
    base = Path(cwd)
    for rel in candidates:
        path = base / rel
        try:
            if path.is_file() and path.stat().st_size > 0:
                return path
        except OSError:
            continue
    return None


def check_fork_pins():
    """Verify fork HEAD and header SHA twice before creating the fixture."""
    if not FORK.is_dir() or not FORK_PS2XRECOMP.is_dir():
        raise RuntimeError("pinned Part 1 fork ps2xRecomp tree missing")
    heads = [read_worktree_head(FORK) for _ in range(2)]
    result["hashes"]["fork_head"] = heads
    record(f"HASH fork_head {heads[0]} {heads[1]}")
    if heads != [FORK_HEAD, FORK_HEAD]:
        raise RuntimeError("Part 1 fork HEAD mismatch")
    header = FORK_PS2XRECOMP / HEADER_REL
    if not header.is_file() or header.stat().st_size != HEADER_SIZE:
        raise RuntimeError("Part 1 fork instructions.h size mismatch")
    reads = [file_sha(header) for _ in range(2)]
    result["hashes"]["fork_header"] = reads
    record(f"HASH fork_header {reads[0]} {reads[1]} ({HEADER_SIZE} B)")
    if reads != [HEADER_SHA, HEADER_SHA]:
        raise RuntimeError("Part 1 fork instructions.h SHA mismatch")


def make_cwd_fixture():
    """Create the private cwd symlink fixture and verify it resolves twice.

    The CodeGenerator suite test reads ``instructions.h`` from cwd-relative
    candidates. The driver runs the binary from its private cwd, so symlink
    ``cwd/ps2xRecomp`` at the pinned Part 1 fork's ``ps2xRecomp`` tree.
    Refuses unless the fork HEAD and header hash match the pins twice, the
    fixture does not already exist, and the symlink resolves to exactly
    the pinned tree (nothing outside it). This is a test-suite fixture
    only: not on the replay path, no replay env change.
    """
    if CWD_FIXTURE.is_symlink() or CWD_FIXTURE.exists():
        raise RuntimeError("one-run guard: cwd fixture already exists")
    check_fork_pins()
    CWD_FIXTURE.symlink_to(FORK_PS2XRECOMP, target_is_directory=True)
    target = os.path.realpath(CWD_FIXTURE)
    pinned = os.path.realpath(FORK_PS2XRECOMP)
    if target != pinned or os.path.commonpath([target, os.path.realpath(FORK)]) \
            != os.path.realpath(FORK):
        raise RuntimeError(f"fixture resolves outside pinned tree: {target}")
    resolved = read_first_candidate(CWD)
    if resolved is None:
        raise RuntimeError("fixture did not make candidate 1 readable")
    header = CWD_FIXTURE / HEADER_REL
    if os.path.realpath(header) != os.path.realpath(FORK_PS2XRECOMP / HEADER_REL):
        raise RuntimeError("fixture header does not resolve to pinned header")
    reads = [file_sha(header) for _ in range(2)]
    result["hashes"]["fixture_header"] = reads
    result["fixture"] = {"link": str(CWD_FIXTURE), "target": str(FORK_PS2XRECOMP),
                         "candidate": str(resolved)}
    record(f"FIXTURE cwd/ps2xRecomp -> {FORK_PS2XRECOMP} "
           f"header {reads[0]} {reads[1]}")
    if reads != [HEADER_SHA, HEADER_SHA]:
        raise RuntimeError("fixture instructions.h SHA mismatch")
# P5M3-FIXTURE-END


def parse_rows(path):
    rows = []
    for line in Path(path).read_text(errors="replace").splitlines():
        m = ROW_RE.search(line)
        if m:
            rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    return rows


def replay_markers(lines):
    """Parse the shared-core GB4 markers and failure lines (Mac form)."""
    text = "\n".join(lines)
    out = {"summary": None, "frame": None, "errors": []}
    for match in re.finditer(
            r"GB4_REPLAY_SUMMARY mode=(\S+) backend=(\S+).*?packets=(\d+) "
            r"priv=(\d+) transfers=(\d+) markers=(\d+)", text):
        out["summary"] = match.groups()
    for match in re.finditer(
            r"GB4_FRAME tick=(\d+) backend=(\S+) pmode=([0-9a-fA-F]+) "
            r".*?present=([0-9a-fA-F]+)", text):
        if match.group(1) == "2050":
            out["frame"] = match.groups()
    for pattern in (
            r"GB4_REPLAY_PARSE_ERROR.*",
            r"\[gs:parallel\] FATAL:.*",
            r"Turnip .*failed.*",
            r"Fatal signal.*",
            r"FATAL EXCEPTION.*",
            r"Failed: [1-9]\d*",
    ):
        out["errors"] += re.findall(pattern, text)
    out["replay_ticks"] = [int(m.group(1)) for m in
                           re.finditer(r"GB4_REPLAY tick=(\d+) ", text)]
    return out


def replay_complete(rc, markers, rows):
    """Complete OFF receipt: exit 0, markers, exact 41-row sequence, PPM.

    Requires exit code 0, GB4_REPLAY_SUMMARY (parallel, markers=2050),
    GB4_FRAME tick=2050, the exact ordered 41-tick list 50..2050 in the
    OUT file, the PPM file present, and no parse/backend error line.
    """
    if rc != 0 or markers["errors"]:
        return False
    if not markers["summary"] or not markers["frame"]:
        return False
    _mode, backend, _pk, _pr, _tr, nmarkers = markers["summary"]
    tick, _b2, _pmode, _present = markers["frame"]
    return (backend == "parallel" and nmarkers == "2050" and tick == "2050"
            and [r[0] for r in rows] == list(EXPECTED_TICKS)
            and len(rows) == 41 and (PPM_DIR / "vq-002050.ppm").exists())


def classify_off_vs_on(on_rows, off_rows, on_ppm_sha, off_ppm_sha):
    """Predeclared Mac OFF vs Mac ON reading (Part 5M1 brief).

    Returns (kind, detail) where kind is one of:
      "invalid"          row shapes are not the exact 41-tick sequence
      "void-pre2050"     any difference at tick <=2000 (flags unread there)
      "flag-unperturbed" 41/41 rows equal AND PPM byte-equal
      "tick2050-only"    rows <=2000 equal, tick2050 row and/or PPM differ
    """
    if ([r[0] for r in off_rows] != list(EXPECTED_TICKS)
            or len(on_rows) != 41):
        return "invalid", "row shapes differ from the exact 50..2050 sequence"
    pre = [(a[0], a, b) for a, b in zip(on_rows, off_rows)
           if a != b and a[0] <= 2000]
    if pre:
        return "void-pre2050", \
            f"differs at ticks<=2000: {[t for t, _, _ in pre]}"
    if on_rows == off_rows and on_ppm_sha == off_ppm_sha:
        return "flag-unperturbed", "41/41 rows and PPM byte-equal"
    return "tick2050-only", "rows<=2000 equal; tick2050 row and/or PPM differ"


def output_bytes_under(dirpath, caps):
    total = 0
    for p in sorted(Path(dirpath).rglob("*")):
        if p.is_file() and p.name != "run.log":
            total += p.stat().st_size
    if total > caps:
        raise RuntimeError(f"output cap {caps} exceeded ({total} B)")
    return total


def stop_child(proc):
    """Stop only this child by its own PID (terminate, then kill)."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)


def run():
    global child, slot, lease_claimed, log_stream
    if len(sys.argv) != 3 or sys.argv[1] != "--released-sha":
        raise SystemExit("review hold: require --released-sha "
                         "<reviewed mac_off.py SHA-256>")
    script_sha = file_sha(Path(__file__))
    if sys.argv[2] != script_sha:
        raise SystemExit("review hold: mac_off.py SHA differs from reviewed pin")
    if OUT_DIR.exists():
        raise SystemExit("one-run guard: mac-off output dir already exists")
    if (SCRATCH / "result.json").exists() or (SCRATCH / "driver.log").exists():
        raise SystemExit("one-run guard: N8D7M12P5M3 receipt already exists")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    result["script_sha"] = script_sha
    record(f"SCRIPT_SHA {script_sha}")

    check_pins()
    off, removed, changed = assert_env_diff()
    env, inherited = child_env(off)
    result["env_diff"] = {"removed": removed, "changed": changed,
                          "ambient_ps2x_cleared": inherited}
    record(f"ENV DIFF on-minus-off removed={removed} changed={changed}")
    if inherited:
        record(f"ENV ambient PS2X_* cleared={inherited}")

    CWD.mkdir(parents=True)
    PPM_DIR.mkdir(parents=True)
    if any(PPM_DIR.iterdir()) or any(CWD.iterdir()):
        raise RuntimeError("private OFF cwd/frames not empty")

    # P5M3-FIXTURE-BEGIN
    make_cwd_fixture()
    # P5M3-FIXTURE-END

    slot = claim(LEASE_LABEL)
    if slot is None:
        raise RuntimeError("P-lane busy: no free mini slot")
    lease_claimed = True
    record(f"LEASE claimed slot {slot}")

    log_stream = LOG_PATH.open("wb")
    start = time.monotonic()
    result["replay_count"] = 1
    record(f"RUN binary={BINARY.name} cwd={CWD} "
           f"backend=parallel step=50 ppm_tick=2050")
    child = subprocess.Popen([str(BINARY)], cwd=str(CWD), env=env,
                             stdout=log_stream, stderr=subprocess.STDOUT)
    result["pid"] = child.pid
    record(f"PID {child.pid}")

    stop_reason = ""
    rc = None
    while True:
        elapsed = time.monotonic() - start
        if LOG_PATH.stat().st_size > LOG_CAP:
            stop_reason = "16 MiB log cap exceeded"
            break
        rc = child.poll()
        if rc is not None:
            break
        if elapsed >= WALL_CAP:
            stop_reason = f"{WALL_CAP} s wall cap"
            break
        time.sleep(0.5)
    result["elapsed_s"] = round(time.monotonic() - start, 3)
    if child.poll() is None and not stop_reason:
        stop_reason = f"{WALL_CAP} s wall cap"
    if child.poll() is None:
        stop_child(child)
    rc = child.poll()
    result["exit_code"] = rc
    record(f"CHILD exit_code={rc} elapsed={result['elapsed_s']:.1f}s "
           f"(control only, not speed)")

    log_stream.close()
    log_stream = None
    lines = LOG_PATH.read_text(errors="replace").splitlines()
    markers = replay_markers(lines)
    rows = parse_rows(HASHES_PATH) if HASHES_PATH.exists() else []
    result["markers"] = markers
    result["row_count"] = len(rows)
    result["rows"] = [list(r) for r in rows]
    if HASHES_PATH.exists():
        result["hashes"]["off_hashes"] = file_sha(HASHES_PATH)
    ppm = PPM_DIR / "vq-002050.ppm"
    if ppm.exists():
        result["hashes"]["off_ppm"] = file_sha(ppm)
        result["off_ppm_path"] = str(ppm)
    output_bytes_under(OUT_DIR, OUTPUT_CAP)

    if replay_complete(rc, markers, rows):
        stop_reason = COMPLETE
        result["verdict"] = "PROVISIONAL PASS"
    else:
        if not stop_reason:
            stop_reason = "no complete 41-row tick2050 receipt"
        result["verdict"] = "FAIL"
    result["stop_reason"] = stop_reason
    result["provisional_note"] = (
        "provisional until the orchestrator views vq-002050.ppm and runs the "
        "predeclared OFF-vs-ON 41-row and PPM comparison in a separate gate; "
        "this control alone does not establish a graphics root cause or speed")
    record("STOP " + stop_reason)
    record("VERDICT " + result["verdict"] + " (provisional)")
    if result["verdict"] != "PROVISIONAL PASS":
        raise RuntimeError(stop_reason)


if __name__ == "__main__":
    try:
        run()
    except (Exception, SystemExit) as exc:
        if SCRATCH.exists() and (SCRATCH / "driver.log").exists():
            result["first_failure"] = str(exc)
            record("ERROR " + repr(exc))
        raise
    finally:
        if log_stream is not None:
            log_stream.close()
        stop_child(child)
        if lease_claimed:
            release(slot)
            record("CLEANUP lease released")
        if SCRATCH.exists() and (SCRATCH / "driver.log").exists():
            (SCRATCH / "result.json").write_text(
                json.dumps(result, indent=2) + "\n")
