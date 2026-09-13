#!/usr/bin/env python3
"""Build, locally sign, deploy, and collect the SSX 3 iOS development app.

All products, device identifiers, profiles, and game content stay in local/.
Only the dedicated SSX bundle/container is modified on the paired device.
"""
from __future__ import annotations
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import time

try:
    from . import native_gamecube as native
    from .native_replay import validate_sequence
except ImportError:
    import native_gamecube as native
    from native_replay import validate_sequence

ROOT = native.ROOT
WORK = ROOT / "local/native/ios-device"
BUNDLE = "com.brad-richardson.ssx-native"
APP = WORK / "SSXNative.app"
REPORTS = ROOT / "local/reports/mobile"


def command(args, **kwargs):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def device_call(args, *, timeout=60):
    REPORTS.mkdir(parents=True, exist_ok=True)
    receipt = REPORTS / (dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-device.json")
    command(["xcrun", "devicectl", *args, "--timeout", timeout, "--quiet", "--json-output", receipt])
    return json.loads(receipt.read_text())["result"]


def device_details(device):
    return device_call(["device", "info", "details", "--device", device])


def simulator_documents(args):
    container = subprocess.check_output([
        "xcrun", "simctl", "get_app_container", args.device, BUNDLE, "data"], text=True).strip()
    documents = Path(container) / "Documents"
    documents.mkdir(exist_ok=True)
    return documents


def configure(args):
    native.check_pins()
    native.check_patches()
    if native.sha256(native.MODULE / "codegen/generated/main.dol") != native.PINS["dol_sha256"]:
        raise RuntimeError("Generated module DOL does not match GXBE69 revision 0")
    command(["cmake", "-S", ROOT / "native/ios", "-B", WORK, "-G", "Ninja",
             f"-DCMAKE_MAKE_PROGRAM={native.ninja()}",
             f"-DCMAKE_TOOLCHAIN_FILE={ROOT / 'native/ios/toolchain.cmake'}",
             "-DCMAKE_C_COMPILER=/usr/bin/clang", "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
             "-DCMAKE_OBJCXX_COMPILER=/usr/bin/clang++", "-DCMAKE_AR=/usr/bin/ar",
             "-DCMAKE_RANLIB=/usr/bin/ranlib", "-DCMAKE_BUILD_TYPE=Release",
             f"-DCMAKE_OSX_SYSROOT={'iphonesimulator' if args.simulator else 'iphoneos'}"])


def build(args):
    configure(args)
    command(["cmake", "--build", WORK, "--target", "SSXNative", "-j", args.jobs])
    receipt = {"dependencies": native.PINS, "app_executable_sha256": native.sha256(APP / "SSXNative"),
               "build_info": json.loads((APP / 'build-info.json').read_text()),
               "game_module_archive_sha256": native.sha256(WORK / "game-module/gGXBE69_recomp.a"),
               "patch_sha256": {p.name: native.sha256(p) for p in
                                (ROOT / "native/patches").glob("*-platform.patch")},
               "mobile_execution_verified": False}
    (WORK / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


def sign(args):
    if not APP.is_dir():
        raise RuntimeError("Build the app before signing")
    details = device_details(args.device)
    udid = details["hardwareProperties"]["udid"]
    identities_text = subprocess.check_output(["security", "find-identity", "-v", "-p", "codesigning"], text=True)
    identities = {fingerprint.lower(): name for fingerprint, name in re.findall(
        r'\b([0-9A-Fa-f]{40}) "(Apple Development:[^"]+)"', identities_text)}
    roots = [Path.home() / "Library/Developer/Xcode/UserData/Provisioning Profiles",
             Path.home() / "Library/MobileDevice/Provisioning Profiles"]
    candidates = []
    for root in roots:
        for path in root.glob("*.mobileprovision"):
            decoded = subprocess.run(["security", "cms", "-D", "-i", str(path)], capture_output=True)
            if decoded.returncode:
                continue
            profile = plistlib.loads(decoded.stdout)
            entitlements = profile.get("Entitlements", {})
            if not entitlements.get("get-task-allow") or udid not in profile.get("ProvisionedDevices", []):
                continue
            if profile["ExpirationDate"] <= dt.datetime.now(dt.timezone.utc).replace(tzinfo=None):
                continue
            prefix = profile["ApplicationIdentifierPrefix"][0]
            app_id = prefix + "." + BUNDLE
            pattern = entitlements.get("application-identifier", "")
            if not fnmatch.fnmatchcase(app_id, pattern):
                continue
            for cert in profile.get("DeveloperCertificates", []):
                fingerprint = hashlib.sha1(cert).hexdigest()
                if fingerprint in identities:
                    candidates.append(("*" in pattern, path, profile, fingerprint, app_id))
    if not candidates:
        raise RuntimeError("No valid local development profile matches this app and device; Xcode provisioning is needed")
    _, profile_path, profile, fingerprint, app_id = sorted(candidates, key=lambda c: (c[0], str(c[1])))[0]
    # The development app needs only its own identity and debugger entitlement.
    # No runtime-code-generation or unrelated app capabilities are requested.
    entitlements = {"application-identifier": app_id,
                    "com.apple.developer.team-identifier": profile["TeamIdentifier"][0],
                    "get-task-allow": True}
    entitlements_file = WORK / "development-entitlements.plist"
    entitlements_file.write_bytes(plistlib.dumps(entitlements))
    shutil.copy2(profile_path, APP / "embedded.mobileprovision")
    command(["codesign", "--force", "--sign", fingerprint, "--timestamp=none",
             "--entitlements", entitlements_file, APP])
    command(["codesign", "--verify", "--strict", APP])
    (WORK / "signing-receipt.json").write_text(json.dumps({
        "bundle_id": BUNDLE, "profile_uuid": profile["UUID"],
        "executable_sha256": native.sha256(APP / "SSXNative"),
        "device_model": details["hardwareProperties"]["marketingName"],
        "os": details["deviceProperties"]["osVersionNumber"]}, indent=2) + "\n")


def install(args):
    if args.simulator:
        command(["xcrun", "simctl", "install", args.device, APP])
        return
    command(["codesign", "--verify", "--strict", APP])
    device_call(["device", "install", "app", "--device", args.device, str(APP)], timeout=300)


def copy_to(args, source, destination, timeout=300):
    return device_call(["device", "copy", "to", "--device", args.device,
                        "--source", str(source), "--destination", destination,
                        "--domain-type", "appDataContainer", "--domain-identifier", BUNDLE], timeout=timeout)


def provision(args):
    game = args.game.resolve()
    if native.sha256(game / "sys/main.dol") != native.PINS["dol_sha256"]:
        raise RuntimeError("Game DOL is not the verified GXBE69 revision 0")
    if args.simulator:
        destination = simulator_documents(args) / "Game"
        if destination.is_symlink():
            raise RuntimeError("Simulator Game is a symlink; refusing to write through it")
        for directory in ("sys", "files"):
            shutil.copytree(game / directory, destination / directory, dirs_exist_ok=True)
        print("Game data copied to the local simulator container")
        return
    # Explicit subdirectories avoid ambiguity about directory-copy roots.
    for directory in ("sys", "files"):
        copy_to(args, game / directory, "Documents/Game/" + directory, timeout=1800)


def world_build_metadata(world):
    if not world or not world.is_file():
        raise RuntimeError("--world must name a built BAM.BIG")
    with world.open('rb') as stream:
        magic = stream.read(4)
    if magic != b"BIGF":
        raise RuntimeError("Not a BIGF archive")
    archive_hash = native.sha256(world)
    recipe_path = world.parent / 'experiment.json'
    if recipe_path.exists() and json.loads(recipe_path.read_text()).get('output_sha256') != archive_hash:
        raise RuntimeError('World archive does not match its build recipe')
    return dict(build=world.parent.name, archive_sha256=archive_hash,
                built_at=dt.datetime.fromtimestamp(world.stat().st_mtime,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))


def world(args):
    """Copy one world archive (a built BAM.BIG) over the app's files/data/worlds/bam.big."""
    metadata = world_build_metadata(args.world)
    REPORTS.mkdir(parents=True,exist_ok=True)
    manifest = REPORTS / (dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-course-build.json')
    manifest.write_text(json.dumps(metadata,indent=2)+'\n')
    if args.simulator:
        documents = simulator_documents(args)
        destination = documents / "Game/files/data/worlds/bam.big"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.world, destination)
        shutil.copy2(manifest, documents / 'course-build.json')
        print(f"World copied to the simulator container: {destination}")
        return
    copy_to(args, args.world, "Documents/Game/files/data/worlds/bam.big", timeout=900)
    # Outside Game/: display metadata must not change the game's asset identity.
    copy_to(args, manifest, "Documents/course-build.json", timeout=60)
    print(f"World copied to the device container: {args.world} ({args.world.stat().st_size} bytes)")


def launch(args):
    flags = []
    if args.sequence:
        validate_sequence(json.loads(args.sequence.read_text()))
        if args.simulator:
            shutil.copy2(args.sequence, simulator_documents(args) / "test-sequence.json")
        else:
            copy_to(args, args.sequence, "Documents/test-sequence.json")
        flags = ["-ssxAutoTest"]
    if args.simulator:
        command(["xcrun", "simctl", "launch", "--terminate-running-process", args.device, BUNDLE, *flags])
        return
    # Arguments must follow devicectl's own options and the bundle identifier.
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = REPORTS / (dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-launch.json")
    # "--" stops devicectl from parsing the app's own flags (it read -ssxAutoTest as -t).
    command(["xcrun", "devicectl", "device", "process", "launch", "--device", args.device,
             "--terminate-existing", "--timeout", "60", "--json-output", output, BUNDLE, "--", *flags])


def collect(args):
    destination = REPORTS / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    destination.mkdir(parents=True)
    if args.simulator:
        documents = simulator_documents(args)
        for source, folder in (("Reports", "Reports"), ("User/ScreenShots", "ScreenShots")):
            shutil.copytree(documents / source, destination / folder)
        print(f"Collected simulator reports: {destination}")
        return
    for source, folder in (("Documents/Reports", "Reports"), ("Documents/User/ScreenShots", "ScreenShots")):
        device_call(["device", "copy", "from", "--device", args.device,
                     "--source", source, "--destination", str(destination / folder),
                     "--domain-type", "appDataContainer", "--domain-identifier", BUNDLE], timeout=300)
    print(f"Collected: {destination}")


def main():
    global WORK, APP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("configure", "build", "sign", "install", "provision", "world", "launch", "collect"))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--simulator", action="store_true", help="Use the iOS Simulator SDK and simctl")
    parser.add_argument("--device", help="Paired iPhone name/identifier, or simulator UUID with --simulator")
    parser.add_argument("--game", type=Path, default=native.DEFAULT_GAME)
    parser.add_argument("--sequence", type=Path, help="Optional bounded automated input sequence")
    parser.add_argument("--world", type=Path, help="Built BAM.BIG for the world command")
    args = parser.parse_args()
    if args.simulator:
        if args.command == "sign":
            parser.error("Simulator installation does not use the iPhone development identity")
        WORK = ROOT / "local/native/ios-simulator"
        APP = WORK / "SSXNative.app"
    if args.jobs < 1 or args.jobs > 16:
        parser.error("--jobs must be between 1 and 16")
    if args.command not in ("configure", "build") and not args.device:
        parser.error("--device is required for this operation")
    try:
        globals()[args.command](args)
    except (RuntimeError, ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
