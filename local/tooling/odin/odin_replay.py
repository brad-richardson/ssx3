#!/usr/bin/env python3
"""One-command on-device GS replay (TL1 Part 2).

Pushes a stream (skipped when the device copy's SHA matches), writes
ps2x.env (replay env + user keys), optionally installs an APK, launches
once, waits for the tick-N receipt, pulls the on-device hashes file and
PPM (never logcat rows for the record), diffs the rows against a Mac rows
file, then force-stops, restores ps2x.env and releases the lease.

Device rules (AGENTS.md): Odin lease claimed/released, keyguard
showing=false before launch (else BLOCKER exit, no launch), battery
`AC powered: true` and level >= 20 % (status ignored), `am force-stop`
after every run.

Usage:
  odin_replay.py --stream LOCAL.gs --rows MAC_ROWS --tick 2050 --out DIR
      [--apk APP.apk] [--env KEY=VAL ...] [--label L] [--step 50]
      [--wall 300] [--serial S]

  odin_replay.py --self-test   # no device: env/diff/ppm/tick pure-function checks
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

PKG = "com.ps2x.runner"
LEASE = "/data/local/tmp/mg/LEASE"
WALL_DEFAULT = 300

# Replay must never boot the game: these keys are refused in --env and in
# the rendered file (P7 precedent).
FORBIDDEN_ENV_KEYS = (
    "PS2X_GS_CAPTURE=",
    "PS2X_GS_CAPTURE_STOP_TICK",
    "PS2X_PAD_SCRIPT",
    "PS2X_CD_IMAGE",
)

REPLAY_KEYS = (
    "PS2X_GS_REPLAY_ONDEVICE=1",
    "PS2X_GS_REPLAY_BACKEND=parallel",
    "PS2X_GS_TURNIP=1",
    "PS2X_GS_REPLAY_PKTSEQ=1",
)


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def default_serial():
    with open(os.path.join(repo_root(), "local", "odin-serial")) as f:
        return f.read().strip()


def file_sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_env(remote_stream, remote_hashes, remote_ppmdir, tick, step, user_keys):
    """Render ps2x.env lines; raise ValueError on a forbidden key."""
    lines = list(REPLAY_KEYS)
    lines.append("PS2X_GS_REPLAY_CAPTURE=" + remote_stream)
    lines.append(f"PS2X_GS_REPLAY_STEP={step}")
    lines.append(f"PS2X_GS_REPLAY_PPM_TICKS={tick}")
    lines.append("PS2X_GS_REPLAY_PPM_DIR=" + remote_ppmdir)
    lines.append("PS2X_GS_REPLAY_OUT=" + remote_hashes)
    for key in user_keys:
        if "=" not in key:
            raise ValueError(f"bad --env (want KEY=VAL): {key!r}")
        lines.append(key)
    for line in lines:
        for forbidden in FORBIDDEN_ENV_KEYS:
            if line.startswith(forbidden):
                raise ValueError(f"forbidden replay env key: {line!r}")
    return lines


def parse_battery(text):
    """Return (ac_powered_bool, level_int). Raise ValueError if unparseable."""
    ac = re.search(r"AC powered:\s*(\w+)", text)
    level = re.search(r"\blevel:\s*(\d+)", text)
    if not ac or not level:
        raise ValueError("cannot parse dumpsys battery")
    return ac.group(1) == "true", int(level.group(1))


def parse_keyguard(text):
    """Return the showing= value ('true'/'false'). Raise ValueError if absent."""
    m = re.search(r"KeyguardServiceDelegate\s+showing=(\w+)", text)
    if not m:
        m = re.search(r"KeyguardServiceDelegate.*?showing=(\w+)", text, re.S)
    if not m:
        raise ValueError("cannot parse keyguard showing=")
    return m.group(1)


def find_tick_row(lines, tick):
    """Return the GB4_REPLAY tick=N row, or None."""
    want = f"GB4_REPLAY tick={tick} "
    for line in lines:
        if want in line:
            return line.rstrip("\n")
    return None


def row_lines(lines):
    """Keep comparator rows (whole-line exact): PKTSEQ + REPLAY tick rows."""
    out = []
    for line in lines:
        if "GB4_PKTSEQ tick=" in line or "GB4_REPLAY tick=" in line:
            out.append(line.rstrip("\n"))
    return out


def row_key(line):
    """(kind, tick) key for a comparator row, e.g. ('REPLAY', 50)."""
    kind = "PKTSEQ" if "GB4_PKTSEQ" in line else "REPLAY"
    m = re.search(r"tick=(\d+)", line)
    return kind, int(m.group(1)) if m else -1


def diff_rows(mac_lines, odin_lines):
    """Keyed whole-line diff: align PKTSEQ/REPLAY rows by (kind, tick).

    The on-device OUT file holds REPLAY rows only while a Mac log excerpt
    also holds PKTSEQ rows, so a positional diff would misalign; aligning
    by key compares the ticks both sides have and reports coverage.
    """
    a = {row_key(l): l for l in row_lines(mac_lines)}
    b = {row_key(l): l for l in row_lines(odin_lines)}
    common = sorted(set(a) & set(b))
    first = None
    for key in common:
        if a[key] != b[key]:
            first = {"tick": key[1], "kind": key[0], "mac": a[key], "odin": b[key]}
            break
    equal_ticks = sum(1 for key in common if a[key] == b[key])
    return {"mac_rows": len(a), "odin_rows": len(b), "common_rows": len(common),
            "equal_ticks": equal_ticks,
            "mac_only": len(a) - len(common), "odin_only": len(b) - len(common),
            "equal": first is None and len(a) == len(b),
            "first_diff": first}


def read_ppm(path):
    """Parse a binary P6 PPM; return (width, height, raster bytes)."""
    with open(path, "rb") as f:
        magic = f.readline().strip()
        if magic != b"P6":
            raise ValueError(f"{path}: not a P6 PPM ({magic!r})")
        dims = b""
        while len(dims.split()) < 2:
            line = f.readline()
            if not line:
                raise ValueError(f"{path}: truncated PPM header")
            if line.startswith(b"#"):
                continue
            dims += b" " + line.strip()
        w, h = map(int, dims.split()[:2])
        maxval = b""
        while not maxval.strip():
            line = f.readline()
            if line.startswith(b"#"):
                continue
            maxval = line
        if int(maxval) != 255:
            raise ValueError(f"{path}: maxval {maxval!r} != 255")
        raster = f.read(w * h * 3)
        if len(raster) != w * h * 3:
            raise ValueError(f"{path}: truncated raster")
        return w, h, raster


def ppm_stat(path):
    """Return {sha256, w, h, pixels, nonblack, nonblack_frac}."""
    w, h, raster = read_ppm(path)
    pixels = w * h
    nonblack = sum(1 for i in range(0, len(raster), 3)
                   if raster[i] | raster[i + 1] | raster[i + 2])
    return {"sha256": file_sha(path), "w": w, "h": h, "pixels": pixels,
            "nonblack": nonblack, "nonblack_frac": nonblack / pixels}


def ppm_compare(a_path, b_path):
    """Return ppm_stat(a) + equal-pixel fraction vs b (same dims required)."""
    wa, ha, ra = read_ppm(a_path)
    wb, hb, rb = read_ppm(b_path)
    if (wa, ha) != (wb, hb):
        raise ValueError(f"dim mismatch: {wa}x{ha} vs {wb}x{hb}")
    stat = ppm_stat(a_path)
    stat["equal_px"] = sum(1 for i in range(0, len(ra), 3) if ra[i:i + 3] == rb[i:i + 3])
    stat["equal_frac"] = stat["equal_px"] / stat["pixels"]
    return stat


class Odin:
    def __init__(self, serial, outdir, label):
        self.serial = serial
        self.outdir = outdir
        self.tag = f"TL1 {label} replay"
        self.files = f"/storage/emulated/0/Android/data/{PKG}/files"
        self.result = {"label": label, "serial": serial, "events": [],
                       "hashes": {}, "verdict": "not found"}
        self.lease_claimed = False
        self.env_pushed = False
        self.logcat_proc = None
        os.makedirs(outdir, exist_ok=True)

    def record(self, message):
        print(message, flush=True)
        self.result["events"].append(message)
        with open(os.path.join(self.outdir, "driver.log"), "a") as handle:
            handle.write(message + "\n")
        with open(os.path.join(self.outdir, "result.json"), "w") as handle:
            json.dump(self.result, handle, indent=2)

    def adb(self, *args, timeout=90, check=True):
        completed = subprocess.run(["adb", "-s", self.serial, *args],
                                   capture_output=True, text=True, timeout=timeout)
        if check and completed.returncode:
            raise RuntimeError(f"adb {args} rc={completed.returncode}: "
                               f"{completed.stderr.strip()} {completed.stdout.strip()}")
        return completed.stdout

    def shell(self, command, timeout=90):
        return self.adb("shell", command, timeout=timeout).strip()

    def pidof(self):
        """PID of the runner, or '' when not running (rc=1 is normal)."""
        return self.adb("shell", f"pidof {PKG}", check=False).strip()

    def device_sha_twice(self, remote, timeout=300):
        reads = [self.shell(f"sha256sum {remote}", timeout=timeout).split()[0]
                 for _ in range(2)]
        return reads

    def preflight(self, min_battery):
        state = self.adb("get-state").strip()
        lease = self.shell(f"cat {LEASE}")
        keyguard = parse_keyguard(self.shell("dumpsys window policy"))
        ac, level = parse_battery(self.shell("dumpsys battery"))
        self.record(f"PREFLIGHT state={state} lease={lease!r} keyguard={keyguard} "
                    f"ac={ac} battery={level}%")
        if keyguard != "false":
            raise SystemExit("BLOCKER: keyguard showing=true, ask Brad to unlock (never worked around)")
        if not ac or level < min_battery:
            raise SystemExit(f"BLOCKER: battery ac={ac} level={level}% "
                             f"(need AC powered + >= {min_battery}%)")
        if state != "device":
            raise SystemExit(f"BLOCKER: adb state {state!r}")
        if not (lease.startswith("LEASE_FREE") or lease == self.tag):
            raise SystemExit(f"BLOCKER: lease held: {lease!r}")
        self.shell(f"echo '{self.tag}' > {LEASE}")
        self.lease_claimed = True
        self.record(f"LEASE claimed: {self.tag}")

    def ensure_stream(self, local_stream, remote_name):
        want = [file_sha(local_stream) for _ in range(2)]
        self.result["hashes"]["local_stream"] = want
        if want[0] != want[1]:
            raise RuntimeError("local stream two-read SHA mismatch")
        remote = f"{self.files}/{remote_name}"
        try:
            have = self.device_sha_twice(remote)
        except RuntimeError:
            have = None  # absent or unreadable: push below
        self.result["hashes"]["device_stream_before"] = have
        if have == [want[0], want[0]]:
            self.record(f"STREAM {remote} SHA matches ({want[0][:12]}…), push skipped")
            return remote
        self.record(f"STREAM pushing {local_stream} -> {remote}")
        self.adb("push", local_stream, remote, timeout=600)
        have = self.device_sha_twice(remote)
        self.result["hashes"]["device_stream_after"] = have
        if have != [want[0], want[0]]:
            raise RuntimeError("pushed stream SHA mismatch")
        self.record(f"STREAM pushed + verified ({want[0][:12]}…)")
        return remote

    def install_apk(self, apk):
        want = [file_sha(apk) for _ in range(2)]
        self.result["hashes"]["local_apk"] = want
        if want[0] != want[1]:
            raise RuntimeError("local APK two-read SHA mismatch")
        self.record(f"INSTALL {apk} ({want[0][:12]}…)")
        out = self.adb("install", "-r", apk, timeout=300)
        self.record(f"INSTALL result: {out.strip()[:120]}")
        if "Success" not in out:
            raise RuntimeError(f"adb install failed: {out.strip()[:200]}")

    def launch_and_wait(self, tick, wall):
        self.shell(f"am force-stop {PKG}")
        self.adb("logcat", "-c", timeout=30)
        log_path = os.path.join(self.outdir, "logcat.txt")
        log_stream = open(log_path, "w")
        self.logcat_proc = subprocess.Popen(
            ["adb", "-s", self.serial, "logcat", "-v", "epoch",
             "-s", "ps2x", "DEBUG", "libc", "AndroidRuntime"],
            stdout=log_stream, stderr=subprocess.STDOUT)
        self.record("AM " + self.shell(f"am start -n {PKG}/android.app.NativeActivity",
                                       timeout=60).replace("\n", " | "))
        time.sleep(6)
        self.shell("input keyevent 4")  # dismiss the mini-USB "Use USB for" dialog
        self.record("BACK sent")
        time.sleep(2)
        outcome, deadline = None, time.time() + wall
        last_progress = time.time()
        while time.time() < deadline:
            time.sleep(2)
            with open(log_path, errors="replace") as handle:
                text = handle.read()
            if "replay ok:" in text:
                outcome = "ok"
                break
            if "replay failed:" in text or "replay rejected:" in text:
                outcome = "failed"
                break
            alive = self.pidof()
            if not alive and len(text) > 1000:
                outcome = "process-gone"
                break
            if time.time() - last_progress >= 30:
                last_progress = time.time()
                rows = len(re.findall(r"GB4_REPLAY tick=\d+ ", text))
                self.record(f"WAIT t+{wall - (deadline - time.time()):.0f}s logcat-rows~{rows} "
                            f"pid={'gone' if not alive else alive}")
        if outcome is None:
            outcome = "wall-cap"
        self.record(f"REPLAY outcome={outcome}")
        self._stop_logcat()
        return outcome

    def _stop_logcat(self):
        if self.logcat_proc is not None:
            try:
                self.logcat_proc.terminate()
                self.logcat_proc.wait(timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    self.logcat_proc.kill()
                except OSError:
                    pass
            self.logcat_proc = None

    def pull_outputs(self, remote_hashes, remote_ppmdir):
        local_hashes = os.path.join(self.outdir, "parallel.hashes")
        try:
            self.adb("pull", remote_hashes, local_hashes, timeout=120)
        except RuntimeError:
            local_hashes = None
        frames_dir = os.path.join(self.outdir, "frames")
        try:
            self.adb("pull", remote_ppmdir, frames_dir, timeout=300)
        except RuntimeError:
            pass
        return local_hashes, frames_dir

    def cleanup(self, orig_env):
        self._stop_logcat()
        try:
            self.shell(f"am force-stop {PKG}", timeout=30)
            time.sleep(2)
            self.record(f"CLEANUP force-stop pid-after={self.pidof() or 'none'}")
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            self.record(f"CLEANUP force-stop FAILED: {exc}")
        try:
            if orig_env is not None:
                with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as handle:
                    handle.write(orig_env)
                    tmp = handle.name
                self.adb("push", tmp, f"{self.files}/ps2x.env", timeout=60)
                os.unlink(tmp)
                self.record("CLEANUP ps2x.env restored: " +
                            self.shell(f"sha256sum {self.files}/ps2x.env", timeout=30))
            elif self.env_pushed:
                self.shell(f"rm -f {self.files}/ps2x.env", timeout=30)
                self.record("CLEANUP ps2x.env removed (no orig, we pushed)")
            else:
                self.record("CLEANUP ps2x.env untouched (never pushed)")
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            self.record(f"CLEANUP env restore FAILED: {exc}")
        if self.lease_claimed:
            try:
                self.shell("echo 'LEASE_FREE TL1 done' > " + LEASE, timeout=30)
                self.record("CLEANUP lease released")
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                self.record(f"CLEANUP lease release FAILED: {exc}")
            self.lease_claimed = False

    def run(self, args):
        stamp = time.strftime("%Y%m%d-%H%M%S")
        remote_hashes = f"{self.files}/tl1-{args.label}-{stamp}.hashes"
        remote_ppmdir = f"{self.files}/tl1-{args.label}-frames-{stamp}"
        env_lines = render_env(f"{self.files}/{args.remote_name}", remote_hashes,
                               remote_ppmdir, args.tick, args.step, args.env)
        with open(os.path.join(self.outdir, "ps2x.env"), "w") as handle:
            handle.write("\n".join(env_lines) + "\n")
        self.preflight(args.min_battery)
        orig_env = None
        try:
            remote_stream = self.ensure_stream(args.stream, args.remote_name)
            assert remote_stream == f"{self.files}/{args.remote_name}"
            orig_path = os.path.join(self.outdir, "ps2x.env.orig")
            try:
                self.adb("pull", f"{self.files}/ps2x.env", orig_path, timeout=60)
                with open(orig_path, errors="replace") as handle:
                    orig_env = handle.read()
                self.record(f"ENV orig saved ({len(orig_env)} bytes)")
            except RuntimeError:
                self.record("ENV no orig ps2x.env on device (will remove at restore)")
            if args.apk:
                self.install_apk(args.apk)
            self.shell(f"mkdir -p {remote_ppmdir}", timeout=30)
            self.adb("push", os.path.join(self.outdir, "ps2x.env"),
                     f"{self.files}/ps2x.env", timeout=60)
            self.env_pushed = True
            self.record("ENV pushed: " +
                        self.shell(f"sha256sum {self.files}/ps2x.env", timeout=30))
            outcome = self.launch_and_wait(args.tick, args.wall)
            local_hashes, frames_dir = self.pull_outputs(remote_hashes, remote_ppmdir)
            with open(os.path.join(self.outdir, "logcat.txt"), errors="replace") as handle:
                log_text = handle.read()
            gs_path = [line for line in log_text.splitlines() if "[gs-path]" in line]
            self.record(f"GS-PATH lines={len(gs_path)}" +
                        (f": {gs_path[0][:300]}" if gs_path else ""))
            self.result["gs_path"] = gs_path[:5]
            if local_hashes is None or not os.path.exists(local_hashes):
                self.result["verdict"] = "no-hashes-file"
                return 1
            with open(local_hashes, errors="replace") as handle:
                odin_lines = handle.read().splitlines()
            receipt = find_tick_row(odin_lines, args.tick)
            self.record(f"RECEIPT tick={args.tick}: {receipt if receipt else 'MISSING'}")
            if receipt is None:
                self.result["verdict"] = "no-tick-receipt"
                return 1
            with open(args.rows, errors="replace") as handle:
                mac_lines = handle.read().splitlines()
            diff = diff_rows(mac_lines, odin_lines)
            self.result["diff"] = diff
            self.record(f"DIFF mac={diff['mac_rows']} odin={diff['odin_rows']} "
                        f"common={diff['common_rows']} equal_ticks={diff['equal_ticks']} "
                        f"mac_only={diff['mac_only']} odin_only={diff['odin_only']} "
                        f"equal={diff['equal']}")
            first = diff["first_diff"]
            if first is not None:
                self.record(f"DIFF first {first['kind']}@{first['tick']}: mac={first['mac'][:160]}")
                self.record(f"DIFF first {first['kind']}@{first['tick']}: odin={first['odin'][:160]}")
            ppm_name = f"vq-{args.tick:06d}.ppm"
            ppm_path = os.path.join(frames_dir, ppm_name)
            if os.path.exists(ppm_path):
                if args.mac_ppm:
                    stat = ppm_compare(ppm_path, args.mac_ppm)
                else:
                    stat = ppm_stat(ppm_path)
                self.result["ppm"] = stat
                self.record(f"PPM {ppm_name} {stat['w']}x{stat['h']} "
                            f"nonblack={stat['nonblack_frac']:.3f} sha={stat['sha256'][:12]}…" +
                            (f" equal_px={stat['equal_frac']:.3f}" if "equal_frac" in stat else ""))
            else:
                self.record(f"PPM {ppm_name} MISSING from {frames_dir}")
            if outcome != "ok":
                self.result["verdict"] = f"replay-{outcome}"
                return 1
            self.result["verdict"] = "rows-match" if diff["equal"] else "rows-differ"
            return 0 if diff["equal"] else 1
        finally:
            self.cleanup(orig_env)
            with open(os.path.join(self.outdir, "result.json"), "w") as handle:
                json.dump(self.result, handle, indent=2)


def self_test():
    """No-device check of the pure pieces: env, battery/keyguard parse, diff, PPM."""
    lines = render_env("/F/s.gs", "/F/h.hashes", "/F/frames", 2050, 50, ["PS2X_FOO=1"])
    assert "PS2X_GS_REPLAY_ONDEVICE=1" in lines and "PS2X_FOO=1" in lines
    assert any(l == "PS2X_GS_REPLAY_PPM_TICKS=2050" for l in lines)
    for bad in ("PS2X_GS_CAPTURE=/x", "PS2X_PAD_SCRIPT=a:b", "PS2X_CD_IMAGE=i",
                "PS2X_GS_CAPTURE_STOP_TICK=5"):
        try:
            render_env("/F/s.gs", "/F/h", "/F/f", 1, 1, [bad])
        except ValueError:
            pass
        else:
            raise AssertionError(f"forbidden key accepted: {bad}")
    ac, level = parse_battery("  AC powered: true\n  status: 3\n  level: 75\n")
    assert (ac, level) == (True, 75)
    assert parse_keyguard("KeyguardServiceDelegate showing=false") == "false"
    mac = ["GB4_PKTSEQ tick=50 seq=aa commands=1", "GB4_REPLAY tick=50 vram=bb priv=cc present=dd",
           "GB4_REPLAY_SUMMARY noise=1"]
    assert diff_rows(mac, list(mac))["equal"]
    assert find_tick_row(mac, 50) == mac[1]
    assert find_tick_row(mac, 100) is None
    odin = [mac[0], "GB4_REPLAY tick=50 vram=XX priv=cc present=dd"]
    diff = diff_rows(odin, mac)
    assert not diff["equal"] and diff["first_diff"]["tick"] == 50, diff
    assert diff["first_diff"]["kind"] == "REPLAY", diff
    # OUT-file shape vs log-excerpt shape: common REPLAY row identical,
    # PKTSEQ only on the Mac side -> not equal, no row difference.
    diff = diff_rows(mac, mac[1:2])
    assert (diff["common_rows"], diff["equal_ticks"], diff["mac_only"]) == (1, 1, 1), diff
    assert not diff["equal"] and diff["first_diff"] is None, diff
    tmp = tempfile.mkdtemp(prefix="odin-replay-selftest-")
    black = os.path.join(tmp, "black.ppm")
    with open(black, "wb") as f:
        f.write(b"P6\n2 2\n255\n" + bytes(12))
    stat = ppm_stat(black)
    assert (stat["w"], stat["h"], stat["nonblack"], stat["nonblack_frac"]) == (2, 2, 0, 0.0)
    half = os.path.join(tmp, "half.ppm")
    with open(half, "wb") as f:
        f.write(b"P6\n# comment\n2 2\n255\n" + bytes([255, 0, 0] * 2 + [0, 0, 0] * 2))
    stat = ppm_stat(half)
    assert stat["nonblack_frac"] == 0.5, stat
    cmp_stat = ppm_compare(half, half)
    assert cmp_stat["equal_frac"] == 1.0
    cmp_stat = ppm_compare(half, black)
    assert cmp_stat["equal_frac"] == 0.5, cmp_stat
    print(f"odin_replay self-test PASS ({tmp})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true", help="run the no-device self-test and exit")
    ap.add_argument("--stream", help="local .gs stream to push")
    ap.add_argument("--remote-name", default="tl1.gs", help="device-side stream filename")
    ap.add_argument("--rows", help="Mac rows file to diff against (PKTSEQ + REPLAY lines)")
    ap.add_argument("--mac-ppm", default=None, help="Mac tick-N PPM to compare equal-px against")
    ap.add_argument("--tick", type=int, default=2050, help="receipt tick (PPM + row)")
    ap.add_argument("--step", type=int, default=50)
    ap.add_argument("--apk", default=None, help="APK to install before launch")
    ap.add_argument("--env", action="append", default=[], help="extra KEY=VAL env line (repeatable)")
    ap.add_argument("--label", default="run")
    ap.add_argument("--out", help="output dir for driver.log/result.json/hashes/frames")
    ap.add_argument("--wall", type=float, default=WALL_DEFAULT)
    ap.add_argument("--min-battery", type=int, default=20)
    ap.add_argument("--serial", default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    for required in ("stream", "rows", "out"):
        if not getattr(args, required):
            ap.error(f"--{required.replace('_', '-')} is required (or --self-test)")
    serial = args.serial or default_serial()
    odin = Odin(serial, args.out, args.label)
    return odin.run(args)


if __name__ == "__main__":
    sys.exit(main())