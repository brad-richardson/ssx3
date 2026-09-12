#!/usr/bin/env python3
"""Push a built GameCube disc image to the Odin (Dolphin for Android) over adb.

The Odin plays patched discs in Dolphin with its JIT, so a build reaches it as
a plain ISO: no Android native build is involved. One-time setup on the Odin
(Android 13): Settings -> System -> Developer options -> Wireless debugging ->
Pair device with pairing code, then on this Mac

  adb pair <odin-ip>:<pairing-port>     # enter the code shown on the Odin
  adb connect <odin-ip>:<debug-port>    # the port on the Wireless debugging page

or plug in USB and accept the debugging prompt. Then

  python3 tools/deploy_odin.py local/builds/gc-gari-009/SSX3-gc-gari-009.iso

pushes the image to the Dolphin game folder (default /sdcard/Games/GameCube,
override with --destination; add that folder once in Dolphin's game list)
and verifies the size and MD5 on the device. adb comes from Homebrew's
android-platform-tools cask.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import time

DEFAULT_DESTINATION = "/sdcard/Games/GameCube"


def adb(args, serial=None, check=True, capture=True, timeout=None):
    cmd = ["adb"] + (["-s", serial] if serial else []) + args
    return subprocess.run(cmd, check=check, capture_output=capture, text=True, timeout=timeout)


def devices():
    out = adb(["devices"]).stdout.splitlines()[1:]
    return [line.split()[0] for line in out if line.strip() and line.split()[1] == "device"]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", type=Path)
    ap.add_argument("--destination", default=DEFAULT_DESTINATION, help="Folder on the Odin that Dolphin scans")
    ap.add_argument("--serial", help="adb device serial or ip:port when more than one device is attached")
    ap.add_argument("--connect", help="ip:port to `adb connect` first (wireless debugging)")
    ap.add_argument("--skip-verify", action="store_true", help="Do not hash the pushed file on the device")
    args = ap.parse_args()
    if not args.iso.is_file():
        ap.error(f"{args.iso} is not a file")
    if args.connect:
        print(adb(["connect", args.connect]).stdout.strip())
    attached = devices()
    if not attached:
        sys.exit("No adb device is attached; pair or connect the Odin first (see --help)")
    serial = args.serial or (attached[0] if len(attached) == 1 else None)
    if serial is None:
        sys.exit(f"Several devices attached, pass --serial: {attached}")
    adb(["shell", "mkdir", "-p", args.destination], serial)
    target = f"{args.destination.rstrip('/')}/{args.iso.name}"
    size = args.iso.stat().st_size
    print(f"pushing {args.iso} ({size} bytes) to {serial}:{target}")
    started = time.time()
    subprocess.run(["adb", "-s", serial, "push", str(args.iso), target], check=True)
    print(f"pushed in {time.time() - started:.0f} s")
    remote_size = int(adb(["shell", "stat", "-c", "%s", target], serial).stdout.strip())
    if remote_size != size:
        sys.exit(f"Size mismatch on device: {remote_size} != {size}")
    if not args.skip_verify:
        local = md5(args.iso)
        remote = adb(["shell", "md5sum", target], serial, timeout=1800).stdout.split()[0]
        if remote != local:
            sys.exit(f"MD5 mismatch on device: {remote} != {local}")
        print(f"verified md5 {local}")
    print("done; rescan the game list in Dolphin if the disc does not appear")


if __name__ == "__main__":
    main()
