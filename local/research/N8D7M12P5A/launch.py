#!/usr/bin/env python3
"""N8D7M12 Part 5A: one leased Odin diagnostic replay of the staged stream.

Reviewed-SHA-held launcher for EXACTLY ONE diagnostic replay of the
already-staged 1,100,696,462-byte N8D7M6 stream on the Odin, using gated APK
caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512 with runner
329e44db..a218a3d, Turnip 717812c3..1ac29d, HAL 1b49d27c..fc387.

Device patterns based on N8D7M6 launch.py. Replay enters before EE boot via
PS2X_GS_REPLAY_ONDEVICE=1; no live GS capture key, no pad script, no game
thread. No device action may run before the orchestrator releases the
reviewed SHA in a separate run gate (require --released-sha <launch.py SHA>).

Source-grounded log syntax (shared core, fork n8d7m12-app @ a608ed1):
- frame file: ps2_vq::dumpPpm(dir, tick) writes "<dir>/vq-%06llu.ppm",
  so tick 2050 -> "vq-002050.ppm" (ps2xRuntime/include/ps2_vq.h:115-125).
- markers: "GB4_REPLAY_SUMMARY mode=.. backend=.. packets=.. markers=..",
  "GB4_REPLAY tick=.. vram=.. priv=.. present=..",
  "GB4_FRAME tick=2050 backend=parallel pmode=.. present=..",
  "GB4_PARALLEL_STATS packets=.. init_ok=..",
  "[n8d7f]/[n8d7l] selected/oracle census lines,
  "[n8d7m12] replay ok: packets=.. markers=.." (_Exit 0) or
  "[n8d7m12] replay failed: .." / "replay rejected: .." (_Exit 1).
"""

import gzip
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import subprocess
import sys
import time
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[3]
SERIAL_FILE = REPO / "local" / "odin-serial"
PKG = "com.ps2x.runner"
SCRATCH = Path("/Users/brad/dev/ssx3-work/N8D7M12P5A")
APK = Path("/Users/brad/dev/ssx3-work/N8D7M12P3/app-release.apk")
APK_SIZE = 153753116
STREAM_LOCAL = Path("/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs")
STREAM_SIZE = 1100696462
FILES = f"/storage/emulated/0/Android/data/{PKG}/files"
REMOTE_STREAM = f"{FILES}/n8d7m6.gs"
REMOTE_ENV = f"{FILES}/ps2x.env"
LEASE = "/data/local/tmp/mg/LEASE"
LEASE_TAG = "N8D7M12P5A replay"
LOG_CAP = 16 * 1024 * 1024
OUTPUT_CAP = 64 * 1024 * 1024
WALL_CAP = 600
PROGRESS_CAP = 180
DRAIN_SECS = 15
COMPLETE = "first complete tick2050 summary/census/frame (PROVISIONAL)"
# Literal (byte-address) control set from N8D7L REPORT, in kOracleControls
# order (ps2_gs_parallel_backend.cpp). Same as N8D7M6 launch.py.
CONTROL_ADDRS = (0x0E0000, 0x0E0534, 0x0E0040, 0x1BFFF4,
                 0x0E2000, 0x0F0000, 0x0E1FFC, 0x0F2000)
PINS = {
    "apk": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "runner": "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "stream": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
}
# Replay env: enters before EE boot (main.cpp:215+). No PS2X_GS_CAPTURE*,
# no PS2X_PAD_SCRIPT*, no PS2X_CD_IMAGE: replay never boots the game.
REPLAY_ENV_KEYS = (
    "PS2X_GS_REPLAY_ONDEVICE=1",
    "PS2X_GS_REPLAY_CAPTURE=" + REMOTE_STREAM,
    "PS2X_GS_REPLAY_BACKEND=parallel",
    "PS2X_GS_TURNIP=1",
    "PS2X_N8D7F_SELECTED_CAPTURE=1",
    "PS2X_N8D7L_ORACLE=1",
    "PS2X_N8D5_TILE_CAPTURE=1",
    "PS2X_GS_REPLAY_STEP=50",
    "PS2X_GS_REPLAY_PPM_TICKS=2050",
)
FORBIDDEN_ENV_KEYS = (
    "PS2X_GS_CAPTURE=",
    "PS2X_GS_CAPTURE_STOP_TICK",
    "PS2X_PAD_SCRIPT",
    "PS2X_CD_IMAGE",
)

result = {"brief": "N8D7M12P5A", "install_count": 0, "launch_count": 0,
          "hashes": {}, "events": [], "verdict": "not found",
          "provisional": True,
          "first_failure": "not found"}
lease_claimed = False
launched = False
force_stopped = False
env_existed = None
logger = None
log_stream = None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(message):
    print(message, flush=True)
    result["events"].append(message)
    with (SCRATCH / "driver.log").open("a") as handle:
        handle.write(message + "\n")
    (SCRATCH / "result.json").write_text(json.dumps(result, indent=2) + "\n")


def read_serial():
    return SERIAL_FILE.read_text().strip()


def adb(*args, timeout=90, check=True):
    serial = read_serial()
    completed = subprocess.run(["adb", "-s", serial, *args],
                               capture_output=True, text=True,
                               timeout=timeout)
    if check and completed.returncode:
        raise RuntimeError(f"adb {args} rc={completed.returncode}: "
                           f"{completed.stderr.strip()} {completed.stdout.strip()}")
    return completed.stdout


def shell(command, timeout=90):
    return adb("shell", command, timeout=timeout).strip()


def pidof():
    return adb("shell", f"pidof {PKG}", check=False).strip()


def preflight(ours=False):
    state = adb("get-state").strip()
    lease = shell(f"cat {LEASE}")
    policy = shell("dumpsys window policy")
    battery = shell("dumpsys battery")
    showing = re.search(r"KeyguardServiceDelegate\s+showing=(\w+)", policy)
    if not showing:
        showing = re.search(r"KeyguardServiceDelegate.*?showing=(\w+)",
                            policy, re.S)
    level_match = re.search(r"\blevel:\s*(\d+)", battery)
    status_match = re.search(r"\bstatus:\s*(\d+)", battery)
    level = int(level_match.group(1)) if level_match else -1
    status = int(status_match.group(1)) if status_match else -1
    free = int(shell("df -k /storage/emulated/0").splitlines()[-1].split()[3]) * 1024
    keyguard = showing.group(1) if showing else "unknown"
    record(f"PREFLIGHT state={state} lease={lease!r} keyguard={keyguard} "
           f"battery={level}% status={status} free_bytes={free}")
    free_lease = lease.startswith("LEASE_FREE") or (ours and lease == LEASE_TAG)
    if state != "device" or not free_lease or keyguard != "false" \
            or level < 20 or status not in (2, 5) \
            or free < 10 * 1024**3:
        if keyguard != "false":
            raise RuntimeError("BLOCKER: keyguard showing, unlock required "
                               "(never worked around)")
        raise RuntimeError("preflight failed (device, lease, unlock, "
                           "charging>=20%, or >=10GiB storage)")


def check_device_sha(label, remote, pin):
    reads = [shell(f"sha256sum {shlex.quote(remote)}",
                   timeout=300).split()[0] for _ in range(2)]
    result["hashes"][label] = reads
    record(f"HASH {label} {reads[0]} {reads[1]}")
    if reads != [pin, pin]:
        raise RuntimeError(f"{label} SHA mismatch")


def check_apk():
    if APK.stat().st_size != APK_SIZE:
        raise RuntimeError("local APK size mismatch")
    reads = [file_sha(APK) for _ in range(2)]
    result["hashes"]["local_apk"] = reads
    if reads != [PINS["apk"]] * 2:
        raise RuntimeError("local APK SHA mismatch")
    with ZipFile(APK) as archive:
        names = set(archive.namelist())
        for label, member in (
            ("runner", "lib/arm64-v8a/libps2EntryRunner.so"),
            ("turnip", "lib/arm64-v8a/libvulkan_freedreno.so"),
            ("hal", "lib/arm64-v8a/libhardware.so"),
        ):
            if member not in names:
                raise RuntimeError(f"APK member absent: {member}")
            pair = [sha256(archive.read(member)) for _ in range(2)]
            result["hashes"]["packaged_" + label] = pair
            if pair != [PINS[label]] * 2:
                raise RuntimeError(f"packaged {label} SHA mismatch")
        runner = archive.read("lib/arm64-v8a/libps2EntryRunner.so")
        for marker in (b"PS2X_GS_REPLAY_ONDEVICE", b"PS2X_GS_REPLAY_CAPTURE",
                       b"PS2XGSC1", b"GB4_REPLAY_SUMMARY",
                       b"PS2X_N8D7F_SELECTED_CAPTURE", b"PS2X_N8D7L_ORACLE"):
            if marker not in runner:
                raise RuntimeError(f"APK runner lacks {marker!r}")
    record("APK size, packaged runner/Turnip/HAL SHA pairs, replay strings match pins")


def check_stream_local():
    if STREAM_LOCAL.stat().st_size != STREAM_SIZE:
        raise RuntimeError("local stream size mismatch")
    reads = [file_sha(STREAM_LOCAL) for _ in range(2)]
    result["hashes"]["local_stream"] = reads
    record(f"HASH local_stream {reads[0]} {reads[1]}")
    if reads != [PINS["stream"]] * 2:
        raise RuntimeError("local stream SHA mismatch")


def same_pid_lines(pid):
    path = SCRATCH / "logcat-all.txt"
    if path.stat().st_size > LOG_CAP:
        raise RuntimeError("16 MiB log cap exceeded")
    lines = path.read_text(errors="replace").splitlines()
    pattern = re.compile(rf"^\s*\d+\.\d+\s+{re.escape(pid)}\s+")
    return [line for line in lines if pattern.search(line)]


def tile_vector(lines, name, words, pack):
    """Parse one wrapped ``<name>_tile_counts=`` logcat vector.

    Verbatim bounded rules from N8D7M6 launch.py: a logcat segment boundary
    can swallow the separator comma, so a wrapped continuation starts with
    exactly one leading comma; any incompleteness, wrong length, malformed
    field or inconsistent continuation returns ``None``.
    """
    marker = f"{name}_tile_counts="
    prefix = re.compile(r"^.*?\bI ps2x\s+: (.*)$")
    values = []
    collecting = False
    pending = 0
    for line in lines:
        if marker in line:
            values = []
            collecting = True
            pending = 0
            payload = line.split(marker, 1)[1]
        elif collecting:
            match = prefix.match(line)
            if not match or match.group(1).startswith("["):
                break
            payload = match.group(1)
            leading = len(payload) - len(payload.lstrip(","))
            if pending + leading != 1:
                return None
            payload = payload.lstrip(",")
        else:
            continue
        trailing = len(payload) - len(payload.rstrip(","))
        if trailing > 1:
            return None
        pending = trailing
        fields = payload.rstrip(",").split(",")
        if any(not field.isdecimal() for field in fields):
            return None
        values.extend(map(int, fields))
        if len(values) > words:
            return None
        if len(values) == words:
            packed = struct.pack(pack, *values)
            return {"words": words, "occupied": sum(values),
                    "active": sum(value >= 32 for value in values),
                    "sha256": sha256(packed), "values": values}
    return None


def parse_controls(payload):
    """Parse ``[n8d7l] oracle_controls=0xADDR=0xVALUE,...`` into 8 pairs."""
    if payload is None:
        return None
    parts = payload.split(",")
    if len(parts) != 8:
        return None
    out = []
    for part in parts:
        pair = part.split("=")
        if len(pair) != 2:
            return None
        try:
            out.append((int(pair[0], 16), int(pair[1], 16)))
        except ValueError:
            return None
    return out


def probe(lines):
    """Split census lines by tag and parse summaries (from N8D7M6)."""
    relevant = [line.split("[n8d5b] ", 1)[1] for line in lines if "[n8d5b] " in line]
    stage_lines = [line.split("[n8d6a] ", 1)[1] for line in lines if "[n8d6a] " in line]
    selected_lines = [line.split("[n8d7f] ", 1)[1] for line in lines if "[n8d7f] " in line]
    oracle_lines = [line.split("[n8d7l] ", 1)[1] for line in lines if "[n8d7l] " in line]
    out = {}
    patterns = {
        "alignment": r"alignment tick=(\d+) fbp=(\d+) pmode=([0-9a-fA-F]+) width=(\d+) height=(\d+)",
        "control": r"control=(\d+) expected=(\d+) (PASS|FAIL)",
        "sampled": r"sampled_summary tiles=(\d+) occupied=(\d+) active=(\d+)",
        "raw": r"raw_summary tiles=(\d+) occupied=(\d+) active=(\d+)",
    }
    for key, pattern in patterns.items():
        matches = [re.search(pattern, line) for line in relevant]
        out[key] = next((m.groups() for m in matches if m), None)
    out["stages"] = {}
    stage_pattern = re.compile(
        r"^stage=(circuit1|pre_deinterlace_merged|final) width=(\d+) height=(\d+) "
        r"tiles=(\d+) occupied=(\d+) active=(\d+) control=(\d+)$")
    for line in stage_lines:
        match = stage_pattern.fullmatch(line)
        if match:
            name, *values = match.groups()
            out["stages"][name] = tuple(map(int, values))
    out["selected"] = {}
    selected_patterns = {
        "metadata": (r"tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) "
                     r"phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+) "
                     r"extent=(\d+)x(\d+) valid=(\d+)x(\d+) status=(\d+)"),
        "bytes": r"bytes=(\d+) vram_sha256=(\S+) input_sha256=(\S+) circuit_sha256=(\S+)",
        "input": r"input tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)",
        "circuit": r"circuit tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)",
        "stage": r"stage tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)",
        "oracle": r"oracle tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)",
        "equal": r"input_circuit_equal=(\d+)/448 circuit_stage_equal=(\d+)/448",
    }
    for key, pattern in selected_patterns.items():
        matches = [re.search(pattern, line) for line in selected_lines]
        out["selected"][key] = next((m.groups() for m in matches if m), None)
    out["oracle"] = {}
    oracle_patterns = {
        "metadata": (r"tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) "
                     r"phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+)"),
        "controls": r"oracle_controls=(\S+)",
        "equal": r"oracle_input_equal=(\d+)/448",
    }
    for key, pattern in oracle_patterns.items():
        matches = [re.search(pattern, line) for line in oracle_lines]
        out["oracle"][key] = next((m.groups() for m in matches if m), None)
    out["vectors"] = {
        "sampled": tile_vector(lines, "sampled", 896, "<896I"),
        "raw": tile_vector(lines, "raw", 896, "<896I"),
        "input": tile_vector(lines, "input", 448, "<448H"),
        "circuit": tile_vector(lines, "circuit", 448, "<448H"),
        "stage": tile_vector(lines, "stage", 448, "<448H"),
        "oracle": tile_vector(lines, "oracle", 448, "<448H"),
    }
    out["errors"] = [line for line in relevant + stage_lines + selected_lines + oracle_lines
                     if "ERROR" in line or "alignment=OTHER" in line or "OTHER" in line]
    return out


def replay_markers(lines):
    """Parse shared-core replay markers (GB4_* + [n8d7m12] exit lines)."""
    text = "\n".join(lines)
    out = {"summary": None, "frame": None, "replay_ok": None,
           "errors": []}
    for match in re.finditer(
            r"GB4_REPLAY_SUMMARY mode=(\S+) backend=(\S+).*?packets=(\d+) "
            r"priv=(\d+) transfers=(\d+) markers=(\d+)", text):
        out["summary"] = match.groups()
    for match in re.finditer(
            r"GB4_FRAME tick=(\d+) backend=(\S+) pmode=([0-9a-fA-F]+) "
            r".*?present=([0-9a-fA-F]+)", text):
        if match.group(1) == "2050":
            out["frame"] = match.groups()
    ok = re.search(r"\[n8d7m12\] replay ok: packets=(\d+) markers=(\d+)",
                   text)
    if ok:
        out["replay_ok"] = ok.groups()
    for pattern in (
            r"GB4_REPLAY_PARSE_ERROR.*",
            r"\[n8d7m12\] replay (failed|rejected):.*",
            r"\[gs:parallel\] FATAL:.*",
            r"Turnip .*failed.*",
            r"Fatal signal.*",
            r"FATAL EXCEPTION.*",
    ):
        out["errors"] += re.findall(pattern, text)
    out["replay_rows"] = len(re.findall(r"GB4_REPLAY tick=\d+ ", text))
    return out


def census_gate(p):
    """Numeric census gate (adapted from N8D7M6 device_gate, replay form).

    Requires parsed control=128/128 PASS, tick-2050 alignment, selected
    11-shared-field metadata, 448-tile summaries consistent with the
    independently parsed vectors, 8 literal control addresses, and
    recomputed oracle equality. Mere line presence never passes.
    """
    selected = p.get("selected", {})
    oracle = p.get("oracle", {})
    vectors = p.get("vectors", {})
    stages = p.get("stages", {})
    if not all(p.get(key) for key in ("alignment", "control", "sampled", "raw")) \
            or not all(selected.values()) \
            or not all(oracle.values()) \
            or not all(vectors.get(kind) for kind in
                       ("sampled", "raw", "input", "circuit", "stage", "oracle")) \
            or set(stages) != {"circuit1", "pre_deinterlace_merged", "final"}:
        return False
    tick, fbp, pmode, width, height = p["alignment"]
    control, expected, status = p["control"]
    circuit1 = stages["circuit1"]
    merged = stages["pre_deinterlace_merged"]
    final = stages["final"]
    (s_tick, s_fbp, s_fbw, s_psm, s_dbx, s_dby, s_phase, s_stride, s_mask,
     s_samples, s_promoted, s_ew, s_eh, s_vw, s_vh, s_status) = selected["metadata"]
    in_tiles, ci_tiles, st_tiles, o_tiles = (selected["input"][0], selected["circuit"][0],
                                             selected["stage"][0], selected["oracle"][0])
    (r_tick, r_fbp, r_fbw, r_psm, r_dbx, r_dby, r_phase, r_stride, r_mask,
     r_samples, r_promoted) = oracle["metadata"]
    controls = parse_controls(oracle["controls"][0])
    selected_shared = (s_tick, s_fbp, s_fbw, s_psm, s_dbx, s_dby, s_phase, s_stride,
                       s_mask, s_samples, s_promoted)
    oracle_shared = (r_tick, r_fbp, r_fbw, r_psm, r_dbx, r_dby, r_phase, r_stride,
                     r_mask, r_samples, r_promoted)
    if p["errors"] \
            or (int(tick), int(fbp), pmode.lower(), int(width), int(height)) \
            != (2050, 112, "ff21", 512, 448) \
            or (control, expected, status) != ("128", "128", "PASS") \
            or (p["sampled"][0], p["raw"][0]) != ("896", "896") \
            or circuit1[:3] != (512, 224, 448) or merged[:3] != (512, 224, 448) \
            or final[:3] != (512, 448, 896) \
            or any(stage[5] != 128 for stage in stages.values()) \
            or (int(s_tick), int(s_fbp), int(s_samples), int(s_promoted), int(s_status)) \
            != (2050, 112, 1, 0, 2) \
            or (int(s_vw), int(s_vh)) != (512, 224) \
            or (in_tiles, ci_tiles, st_tiles, o_tiles) != ("448", "448", "448", "448") \
            or (int(r_tick), int(r_fbp), int(r_fbw), int(r_psm), int(r_samples),
                int(r_promoted), int(r_mask)) != (2050, 112, 8, 1, 1, 0, 4194303) \
            or selected_shared != oracle_shared \
            or controls is None or [a for a, _ in controls] != list(CONTROL_ADDRS):
        return False
    for kind, summary in (("sampled", p["sampled"]), ("raw", p["raw"])):
        vector = vectors[kind]
        if (vector["occupied"], vector["active"]) != (int(summary[1]), int(summary[2])):
            return False
    for kind, summary in (("input", selected["input"]), ("circuit", selected["circuit"]),
                          ("stage", selected["stage"]), ("oracle", selected["oracle"])):
        vector = vectors[kind]
        if (vector["occupied"], vector["active"]) != (int(summary[1]), int(summary[2])):
            return False
        if summary[3] != "unavailable" and summary[3] != vector["sha256"]:
            return False
    if vectors["sampled"]["values"] != vectors["raw"]["values"]:
        return False
    in_values = vectors["input"]["values"]
    ci_values = vectors["circuit"]["values"]
    st_values = vectors["stage"]["values"]
    or_values = vectors["oracle"]["values"]
    ic_equal, cs_equal = selected["equal"]
    if (int(ic_equal), int(cs_equal)) != (sum(a == b for a, b in zip(in_values, ci_values)),
                                          sum(a == b for a, b in zip(ci_values, st_values))):
        return False
    logged_equal = int(oracle["equal"][0])
    if logged_equal != sum(a == b for a, b in zip(or_values, in_values)):
        return False
    return True


def replay_complete(markers, p):
    """Complete receipt: markers + full numeric census, no errors."""
    if markers["errors"] or p["errors"]:
        return False
    if not markers["summary"] or not markers["frame"] or not markers["replay_ok"]:
        return False
    _mode, backend, _pk, _pr, _tr, nmarkers = markers["summary"]
    tick, _b2, _pmode, _present = markers["frame"]
    _opk, omarkers = markers["replay_ok"]
    return (backend == "parallel" and nmarkers == "2050" and tick == "2050"
            and omarkers == "2050" and census_gate(p))


def drain_after_exit(pid, prior_count):
    """Bounded final log drain after the replay process _Exits.

    The Part 2 branch drains the logcat pipe then _Exits, but trailing
    lines may still be in flight. Poll the log file for DRAIN_SECS,
    returning the final same-PID lines (never longer than the wall cap
    budget already accounted by the caller).
    """
    deadline = time.monotonic() + DRAIN_SECS
    lines = same_pid_lines(pid)
    while time.monotonic() < deadline:
        time.sleep(1)
        fresh = same_pid_lines(pid)
        if len(fresh) > len(lines):
            lines = fresh
            deadline = time.monotonic() + DRAIN_SECS
    record(f"DRAIN lines={len(lines)} (was {prior_count})")
    return lines


def pull_outputs(ppm_remote, hashes_remote):
    total = 0
    for remote, local in ((ppm_remote, SCRATCH / "vq-002050.ppm"),
                          (hashes_remote, SCRATCH / "parallel.hashes")):
        size = int(shell(f"stat -c %s {shlex.quote(remote)}",
                         timeout=120))
        total += size
        if total > OUTPUT_CAP:
            raise RuntimeError("64 MiB PPM/output cap exceeded")
        device = [shell(f"sha256sum {shlex.quote(remote)}",
                        timeout=120).split()[0] for _ in range(2)]
        adb("pull", remote, str(local), timeout=300)
        local_pair = [file_sha(local) for _ in range(2)]
        if local.stat().st_size != size or device != local_pair:
            raise RuntimeError(f"{local.name} SHA/size mismatch after pull")
        result["hashes"][local.name] = {"device": device,
                                        "local": local_pair,
                                        "bytes": size}
        record(f"PULLED {local.name} bytes={size} sha={device[0]}")


def close_logger():
    global logger, log_stream
    if logger is not None:
        logger.terminate()
        try:
            logger.wait(timeout=3)
        except subprocess.TimeoutExpired:
            logger.kill()
            logger.wait(timeout=3)
        logger = None
    if log_stream is not None:
        log_stream.close()
        log_stream = None
    path = SCRATCH / "logcat-all.txt"
    if path.exists():
        if path.stat().st_size > LOG_CAP:
            result["first_failure"] = "16 MiB log cap exceeded"
        with path.open("rb") as source, gzip.open(
                SCRATCH / "logcat-all.txt.gz", "wb") as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        path.unlink()
        record(f"LOG_CLOSED gzip_bytes={(SCRATCH / 'logcat-all.txt.gz').stat().st_size}")


def run():
    global lease_claimed, launched, force_stopped, env_existed, logger, log_stream
    if len(sys.argv) != 3 or sys.argv[1] != "--released-sha":
        raise SystemExit("review hold: require --released-sha <reviewed launch.py SHA-256>")
    script_sha = file_sha(Path(__file__))
    if sys.argv[2] != script_sha:
        raise SystemExit("review hold: launch.py SHA differs from reviewed pin")
    if read_serial() != "622c49b1":
        raise SystemExit("serial pin mismatch: local/odin-serial must read 622c49b1")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if (SCRATCH / "result.json").exists() or (SCRATCH / "driver.log").exists():
        raise SystemExit("one-run guard: N8D7M12P5A receipt already exists")
    result["script_sha"] = script_sha
    record(f"SCRIPT_SHA {script_sha}")
    check_apk()
    check_stream_local()
    preflight()
    shell(f"echo '{LEASE_TAG}' > {LEASE}")
    lease_claimed = True
    if shell(f"cat {LEASE}") != LEASE_TAG:
        raise RuntimeError("lease claim did not persist")
    record(f"LEASE claimed {LEASE_TAG}")
    installed_result = adb("install", "-r", str(APK), timeout=180).strip()
    result["install_count"] = 1
    record("INSTALL " + installed_result.replace("\n", " | "))
    installed = shell(f"pm path {PKG}").removeprefix("package:")
    if not installed.endswith("/base.apk"):
        raise RuntimeError("installed base.apk path absent")
    result["installed_path"] = installed
    check_device_sha("installed_apk", installed, PINS["apk"])
    # Pinned stream: verify only, never push/alter/delete.
    size = int(shell(f"stat -c %s {REMOTE_STREAM}", timeout=120))
    if size != STREAM_SIZE:
        raise RuntimeError(f"device stream size mismatch ({size})")
    check_device_sha("device_stream", REMOTE_STREAM, PINS["stream"])
    # Preserve existing device ps2x.env bytes before replacing: two
    # matching device SHA reads, pull, then two matching local reads; all
    # four must agree or the run stops before any device write.
    existed = shell(f"if test -f {shlex.quote(REMOTE_ENV)}; then echo present; "
                    f"else echo absent; fi")
    env_existed = (existed == "present")
    if env_existed:
        before_device = [shell(f"sha256sum {REMOTE_ENV}",
                               timeout=60).split()[0] for _ in range(2)]
        if before_device[0] != before_device[1]:
            raise RuntimeError("pre-existing ps2x.env device SHA pair mismatch")
        adb("pull", REMOTE_ENV, str(SCRATCH / "ps2x.env.before"),
            timeout=60)
        before_local = [file_sha(SCRATCH / "ps2x.env.before")
                        for _ in range(2)]
        if before_device != before_local:
            raise RuntimeError("preserved ps2x.env device/local SHA mismatch")
        result["env_before_sha"] = before_device
        record(f"ENV preserved sha={before_device[0]} (2 device + 2 local reads match)")
    else:
        record("ENV no pre-existing ps2x.env")
    stamp = int(time.time())
    ppm_dir = f"{FILES}/n8d7m12p5a-frames-{stamp}"
    hashes_path = f"{FILES}/n8d7m12p5a-{stamp}.hashes"
    for path in (ppm_dir, hashes_path):
        if shell(f"if test -e {shlex.quote(path)}; then echo present; "
                 f"else echo absent; fi") != "absent":
            raise RuntimeError(f"output path already exists: {path}")
    shell(f"mkdir -p {shlex.quote(ppm_dir)}")
    if shell(f"ls -A {shlex.quote(ppm_dir)}"):
        raise RuntimeError("PPM dir is not empty")
    result["ppm_dir"] = ppm_dir
    result["hashes_path"] = hashes_path
    env_lines = list(REPLAY_ENV_KEYS) + [
        f"PS2X_GS_REPLAY_PPM_DIR={ppm_dir}",
        f"PS2X_GS_REPLAY_OUT={hashes_path}",
    ]
    env_text = "".join(line + "\n" for line in env_lines)
    for forbidden in FORBIDDEN_ENV_KEYS:
        if forbidden in env_text:
            raise RuntimeError(f"forbidden live key in replay env: {forbidden}")
    (SCRATCH / "ps2x.env").write_text(env_text)
    adb("push", str(SCRATCH / "ps2x.env"), REMOTE_ENV)
    pushed = shell(f"sha256sum {REMOTE_ENV}").split()[0]
    if pushed != file_sha(SCRATCH / "ps2x.env"):
        raise RuntimeError("environment push SHA mismatch")
    record(f"ENV replay sha={pushed} ppm_dir={ppm_dir}")
    adb("shell", f"am force-stop {PKG}")
    adb("logcat", "-c")
    log_stream = (SCRATCH / "logcat-all.txt").open("wb")
    serial = read_serial()
    logger = subprocess.Popen(["adb", "-s", serial, "logcat", "-v", "epoch",
                               "-b", "main", "-b", "crash", "-s", "ps2x",
                               "ps2x-hwcompat", "raylib", "DEBUG", "libc",
                               "AndroidRuntime"], stdout=log_stream,
                              stderr=subprocess.STDOUT)
    preflight(ours=True)
    if pidof():
        raise RuntimeError("app running immediately before am start")
    start = time.monotonic()
    last_progress = start
    launched = True
    result["launch_count"] = 1
    am = shell(f"am start -n {PKG}/android.app.NativeActivity")
    record("LAUNCH " + am.replace("\n", " | "))
    pid = ""
    for _ in range(20):
        pid = pidof()
        if pid:
            break
        time.sleep(0.5)
    if not pid:
        raise RuntimeError("launch PID absent")
    result["pid"] = pid
    record(f"PID {pid}")
    stop_reason = ""
    markers = {}
    census = {}
    last_rows = 0
    back_sent = False
    while True:
        elapsed = time.monotonic() - start
        lines = same_pid_lines(pid)
        markers = replay_markers(lines)
        census = probe(lines)
        if markers["replay_rows"] != last_rows:
            last_rows = markers["replay_rows"]
            last_progress = time.monotonic()
            record(f"PROGRESS elapsed={elapsed:.1f}s replay_rows={last_rows}")
        combined_errors = markers["errors"] + census["errors"]
        if combined_errors:
            stop_reason = "first parse/backend/control error: " + str(combined_errors[0])
            break
        # Complete receipt is evaluated BEFORE process liveness: the replay
        # branch _Exits immediately after logging success, so pidof may
        # already be empty when the receipt is present.
        if replay_complete(markers, census):
            stop_reason = COMPLETE
            break
        if elapsed >= 6 and not back_sent:
            shell("input keyevent 4")
            back_sent = True
            record("BACK sent once for USB dialog")
        if not pidof():
            drained = drain_after_exit(pid, len(lines))
            markers = replay_markers(drained)
            census = probe(drained)
            lines = drained
            if replay_complete(markers, census):
                stop_reason = COMPLETE
            else:
                stop_reason = "process exited without complete receipt"
            break
        if elapsed - last_progress >= PROGRESS_CAP:
            stop_reason = f"{PROGRESS_CAP} s without new replay rows"
            break
        if elapsed >= WALL_CAP:
            stop_reason = f"{WALL_CAP} s wall cap"
            break
        time.sleep(1)
    result["elapsed_s"] = round(time.monotonic() - start, 3)
    result["stop_reason"] = stop_reason
    result["markers"] = {k: v for k, v in markers.items()}
    result["probe"] = {k: v for k, v in census.items()}
    for vector in result["probe"].get("vectors", {}).values():
        if vector:
            vector.pop("values", None)
    record("STOP " + stop_reason)
    lines = same_pid_lines(pid)
    (SCRATCH / "logcat-pid.txt").write_text("\n".join(lines) + "\n")
    adb("shell", f"am force-stop {PKG}", timeout=30)
    force_stopped = True
    time.sleep(1)
    if pidof():
        raise RuntimeError("force-stop left app PID present")
    record("POSTRUN pid absent")
    if stop_reason == COMPLETE:
        pull_outputs(f"{ppm_dir}/vq-002050.ppm", hashes_path)
    result["verdict"] = ("PROVISIONAL PASS" if stop_reason == COMPLETE
                         else "FAIL")
    result["provisional_note"] = (
        "provisional until the orchestrator views vq-002050.ppm and checks "
        "same-binary controls; one replay does not establish default-off "
        "behavior (no same-binary OFF control is run or claimed here), "
        "a root cause, or speed")
    record("VERDICT " + result["verdict"] + " (provisional)")
    if stop_reason != COMPLETE:
        raise RuntimeError(stop_reason)


def note_cleanup_error(message):
    result.setdefault("cleanup_errors", []).append(message)
    try:
        record("CLEANUP ERROR " + message)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        run()
    except (Exception, SystemExit) as exc:
        if SCRATCH.exists() and (SCRATCH / "driver.log").exists():
            result["first_failure"] = str(exc)
            record("ERROR " + repr(exc))
        raise
    finally:
        if lease_claimed:
            try:
                if launched and not force_stopped:
                    adb("shell", f"am force-stop {PKG}", timeout=30)
                    force_stopped = True
                    time.sleep(1)
                pid_after = pidof() or "none"
                record("CLEANUP pid-after=" + pid_after)
                if pid_after != "none":
                    note_cleanup_error("app PID present after force-stop")
            except Exception as exc:
                note_cleanup_error(f"force-stop: {exc!r}")
            try:
                if env_existed:
                    adb("push", str(SCRATCH / "ps2x.env.before"),
                        REMOTE_ENV, timeout=60)
                    restored_device = [
                        shell(f"sha256sum {REMOTE_ENV}",
                              timeout=60).split()[0] for _ in range(2)]
                    restored_local = [
                        file_sha(SCRATCH / "ps2x.env.before")
                        for _ in range(2)]
                    if restored_device != restored_local:
                        note_cleanup_error(
                            "restored ps2x.env device/local SHA mismatch")
                    else:
                        record("CLEANUP env restored, "
                               f"sha={restored_device[0]} (2+2 reads match)")
                elif env_existed is False:
                    adb("shell", f"rm -f {shlex.quote(REMOTE_ENV)}",
                        timeout=60)
                    record("CLEANUP pushed ps2x.env removed (none pre-existed)")
            except Exception as exc:
                note_cleanup_error(f"env restore: {exc!r}")
            try:
                current = shell(f"cat {LEASE}", timeout=30)
                if current == LEASE_TAG:
                    shell(f"echo 'LEASE_FREE N8D7M12P5A done' > {LEASE}",
                          timeout=30)
                    record("CLEANUP lease=" + shell(f"cat {LEASE}",
                                                    timeout=30))
                else:
                    note_cleanup_error(
                        f"lease not ours at release ({current!r})")
            except Exception as exc:
                note_cleanup_error(f"lease release: {exc!r}")
            # Any cleanup failure fails the outcome, even on a complete
            # receipt: the device may be left dirty.
            if result.get("cleanup_errors") and \
                    result.get("verdict") == "PROVISIONAL PASS":
                result["verdict"] = "FAIL"
                result["first_failure"] = (
                    "cleanup: " + "; ".join(result["cleanup_errors"]))
                try:
                    record("VERDICT FAIL (cleanup failure overrides receipt)")
                except Exception:
                    pass
        close_logger()
        if SCRATCH.exists() and (SCRATCH / "driver.log").exists():
            (SCRATCH / "result.json").write_text(
                json.dumps(result, indent=2) + "\n")
