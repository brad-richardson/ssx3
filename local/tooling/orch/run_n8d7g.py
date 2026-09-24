#!/usr/bin/env python3
"""Run the two pinned N8D7F Mac replays with one mini lease and hard caps."""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p_lane_lease import claim, release  # noqa: E402

ROOT = Path("/Users/brad/dev/ssx3-work/N8D7F")
FORK = ROOT / "PS2Recomp"
BIN = ROOT / "build/ps2xTest/ps2x_tests"
STREAM = Path("/Users/brad/dev/ssx3-work/N8D4/n8d4.gs")
CODEGEN = Path("/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp")
PINS = {
    str(BIN): "66457eb47ac6c29a8ffca38795d88122fb1c03e4e19e4f55e977f716eb70a804",
    str(STREAM): "38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d",
    str(CODEGEN): "8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stop(p):
    if p.poll() is None:
        os.killpg(p.pid, signal.SIGTERM)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()


def run(which):
    log = ROOT / f"{which}.log"
    hashes = ROOT / f"{which}.hashes"
    if log.exists() or hashes.exists():
        raise RuntimeError(f"{which}: output exists; no silent rerun")
    frames = ROOT / f"{which}-ppm"
    frames.mkdir(exist_ok=False)
    env = os.environ.copy()
    env.update({
        "PS2X_N8D7F_SELECTED_CAPTURE": "1" if which == "on" else "0",
        "PS2X_N8D5_TILE_CAPTURE": "1",
        "PS2X_GS_REPLAY_CAPTURE": str(STREAM),
        "PS2X_GS_REPLAY_STEP": "50",
        "PS2X_GS_REPLAY_OUT": str(hashes),
        "PS2X_GS_REPLAY_BACKEND": "parallel",
        "PS2X_GS_REPLAY_PPM_TICKS": "2050",
        "PS2X_GS_REPLAY_PPM_DIR": str(frames),
        "GRANITE_VULKAN_LIBRARY": "/opt/homebrew/lib/libvulkan.1.dylib",
    })
    started = time.monotonic()
    last_progress = started
    seen = 0
    with log.open("wb") as out:
        p = subprocess.Popen([str(BIN)], cwd=FORK, env=env, stdout=out,
                             stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while p.poll() is None:
                time.sleep(2)
                elapsed = time.monotonic() - started
                size = log.stat().st_size
                if size > 64 * 1024 * 1024:
                    raise RuntimeError(f"{which}: log cap 64 MiB")
                with log.open("rb") as f:
                    f.seek(seen)
                    added = f.read()
                seen = size
                if re.search(rb"GB4_REPLAY tick=\d+", added):
                    last_progress = time.monotonic()
                if elapsed > 600:
                    raise RuntimeError(f"{which}: 600 s wall cap")
                if time.monotonic() - last_progress > 180:
                    raise RuntimeError(f"{which}: 180 s without replay progress")
            return {"kind": which, "pid": p.pid, "exit": p.returncode,
                    "seconds": round(time.monotonic() - started, 2),
                    "log_bytes": log.stat().st_size, "log_sha256": sha(log),
                    "hashes_sha256": sha(hashes) if hashes.exists() else None,
                    "frames": [{"path": str(f), "bytes": f.stat().st_size, "sha256": sha(f)}
                               for f in sorted(frames.glob("*.ppm"))]}
        finally:
            stop(p)


def main():
    receipts = {"pins": {}, "runs": []}
    for path, expected in PINS.items():
        first, second = sha(path), sha(path)
        receipts["pins"][path] = {"first": first, "second": second, "expected": expected}
        if first != second or first != expected:
            raise RuntimeError(f"pin mismatch: {path}")
    slot = claim("n8d7g")
    if slot is None:
        raise RuntimeError("mini lease busy; wait and retry before any run")
    receipts["lease_slot"] = slot
    try:
        for which in ("off", "on"):
            result = run(which)
            receipts["runs"].append(result)
            (ROOT / "run-receipt.json").write_text(json.dumps(receipts, indent=2) + "\n")
            if result["exit"] != 0:
                raise RuntimeError(f"{which}: exit {result['exit']}; stop before next run")
    finally:
        release(slot)
        receipts["lease_released"] = True
        (ROOT / "run-receipt.json").write_text(json.dumps(receipts, indent=2) + "\n")
    print(json.dumps(receipts, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"N8D7G STOP: {exc}", file=sys.stderr)
        sys.exit(1)
