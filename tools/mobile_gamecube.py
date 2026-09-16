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
import math
import os
from pathlib import Path
import plistlib
import re
import shutil
import tempfile
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
             f"-DRECOMPCORE_FAST_FP={'ON' if getattr(args, 'fast_fp', False) else 'OFF'}",
             f"-DCMAKE_OSX_SYSROOT={'iphonesimulator' if args.simulator else 'iphoneos'}"])


def write_receipt(kind, receipt):
    # Working receipts are replaced by later builds/signatures. Retain the
    # exact record under a content hash so delivery evidence survives that.
    payload = json.dumps(receipt, indent=2) + "\n"
    archive = WORK / "receipts" / (kind + "-" + hashlib.sha256(payload.encode()).hexdigest() + ".json")
    archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        with archive.open("x") as stream:
            stream.write(payload)
    except FileExistsError:
        if archive.read_text() != payload:
            raise RuntimeError("Archived mobile receipt does not match its content hash")
    (WORK / (kind + "-receipt.json")).write_text(payload)
    print(f"Archived {kind} receipt: {archive}")
    return archive


def build(args):
    configure(args)
    command(["cmake", "--build", WORK, "--target", "SSXNative", "-j", args.jobs])
    receipt = {"dependencies": native.PINS, "app_executable_sha256": native.sha256(APP / "SSXNative"),
               "build_info": json.loads((APP / 'build-info.json').read_text()),
               "game_module_archive_sha256": native.sha256(WORK / "game-module/gGXBE69_recomp.a"),
               "patch_sha256": {p.name: native.sha256(p) for p in
                                (ROOT / "native/patches").glob("*-platform.patch")},
               "fast_fp": bool(getattr(args, "fast_fp", False)),
               "mobile_execution_verified": False}
    write_receipt("build", receipt)


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
    write_receipt("signing", {
        "bundle_id": BUNDLE, "profile_uuid": profile["UUID"],
        "build_info": json.loads((APP / 'build-info.json').read_text()),
        "executable_sha256": native.sha256(APP / "SSXNative"),
        "device_model": details["hardwareProperties"]["marketingName"],
        "os": details["deviceProperties"]["osVersionNumber"]})


def app_is_running(args):
    """Whether SSXNative is live on the device right now."""
    report = device_call(["device", "info", "processes", "--device", args.device], timeout=120)
    processes = (report or {}).get("result", {}).get("runningProcesses", [])
    return any("SSXNative" in str(entry.get("executable", "")) for entry in processes)


def install(args):
    if args.simulator:
        command(["xcrun", "simctl", "install", args.device, APP])
        return
    command(["codesign", "--verify", "--strict", APP])
    # Installing over a running app ends that session *without* a checkpoint -
    # the process is replaced mid-ride and the runtime never gets to stop
    # cleanly, which reads in the telemetry as a session that simply stops after
    # its last lifecycle event. That is indistinguishable from a crash to whoever
    # was playing, so refuse rather than explain it afterwards.
    if not args.force_install and app_is_running(args):
        raise RuntimeError(
            "SSXNative is running on the device; installing would end that session "
            "without a checkpoint. Quit the app, or pass --force-install.")
    device_call(["device", "install", "app", "--device", args.device, str(APP)], timeout=300)


def copy_to(args, source, destination, timeout=300):
    return device_call(["device", "copy", "to", "--device", args.device,
                        "--source", str(source), "--destination", destination,
                        "--domain-type", "appDataContainer", "--domain-identifier", BUNDLE], timeout=timeout)


# The three UI sheets that carry the prompt icons; their `art_` images are
# identical, and the game picks whichever sheet the current screen uses.
GLYPH_SHEETS = ("fe_1", "ov_1", "gl_1")


def patched_ui(game, workspace):
    """The Xbox-position prompt glyphs, rebuilt from this game's own UI sheets.

    The game draws the GameCube input's icon for every prompt, so reading
    "B for recovery" while holding an Xbox-style overlay means hunting for the
    button. `patch_ui_glyphs.py` repaints each icon for the Xbox button at the
    same physical position, and provisioning applies it every time because it
    has to: provisioning copies `files/` from the pristine disc, so a patch
    that lives only in the device container is reverted by the next install and
    the prompts silently revert to GameCube letters.
    """
    try:
        from patch_ui_glyphs import patch_sheet
    except ImportError:
        from tools.patch_ui_glyphs import patch_sheet
    destination = workspace / "ui"
    destination.mkdir(parents=True, exist_ok=True)
    for name in GLYPH_SHEETS:
        patch_sheet(game / "files/data/ui" / f"{name}.gsh", destination / f"{name}.gsh")
    return destination


def provision(args):
    game = args.game.resolve()
    if native.sha256(game / "sys/main.dol") != native.PINS["dol_sha256"]:
        raise RuntimeError("Game DOL is not the verified GXBE69 revision 0")
    workspace = None
    glyphs = None
    if not args.stock_glyphs:
        workspace = Path(tempfile.mkdtemp(prefix="ssx-ui-"))
        glyphs = patched_ui(game, workspace)
    try:
        if args.simulator:
            destination = simulator_documents(args) / "Game"
            if destination.is_symlink():
                raise RuntimeError("Simulator Game is a symlink; refusing to write through it")
            for directory in ("sys", "files"):
                shutil.copytree(game / directory, destination / directory, dirs_exist_ok=True)
            if glyphs:
                shutil.copytree(glyphs, destination / "files/data/ui", dirs_exist_ok=True)
            print("Game data copied to the local simulator container")
            return
        # Explicit subdirectories avoid ambiguity about directory-copy roots.
        for directory in ("sys", "files"):
            copy_to(args, game / directory, "Documents/Game/" + directory, timeout=1800)
        if glyphs:
            # After files/, so it overwrites the pristine sheets rather than
            # being overwritten by them.
            copy_to(args, glyphs, "Documents/Game/files/data/ui", timeout=300)
            print(f"Xbox-position prompt glyphs applied to {', '.join(GLYPH_SHEETS)}")
    finally:
        if workspace:
            shutil.rmtree(workspace, ignore_errors=True)


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


def textures(args):
    """Copy a replacement texture pack into the app's Load/Textures/GXBE69."""
    pack = args.pack
    if not pack or not pack.is_dir():
        raise RuntimeError("--pack must name a directory of tex1_*.png replacements")
    images = sorted(p for p in pack.iterdir() if p.suffix.lower() in ('.png', '.dds')
                    and p.name.startswith('tex1_'))
    if not images:
        raise RuntimeError(f"No tex1_*.png / .dds replacements in {pack}")
    total = sum(p.stat().st_size for p in images)
    print(f"{len(images)} textures, {total / 1e6:.0f} MB")
    # Which format this pack is, recorded for the app to act on. Dolphin's
    # HiresTexture::Update searches one directory for both .png and .dds and
    # keys the result on the file *stem*, so a stem present in both formats is
    # resolved by whichever the file search happens to return first - and a
    # device container cannot be pruned from here, because devicectl copies but
    # never deletes. The app removes the other format at startup instead.
    formats = {p.suffix.lower() for p in images}
    if len(formats) > 1:
        raise RuntimeError(f"Pack mixes {', '.join(sorted(formats))}; Dolphin would "
                           f"resolve duplicate stems unpredictably")
    marker = WORK / "pack-format.txt"
    marker.write_text(formats.pop().lstrip('.') + '\n')
    if args.simulator:
        destination = simulator_documents(args) / "User/Load/Textures/GXBE69"
        destination.mkdir(parents=True, exist_ok=True)
        for image in images:
            shutil.copy2(image, destination / image.name)
        shutil.copy2(marker, destination.parent.parent.parent / "pack-format.txt")
        print(f"Texture pack copied to the simulator container: {destination}")
        return
    copy_to(args, pack, "Documents/User/Load/Textures/GXBE69", timeout=1800)
    copy_to(args, marker, "Documents/User/pack-format.txt", timeout=60)
    print("Texture pack copied to the device container: Documents/User/Load/Textures/GXBE69\n"
          "Turn it on in the app's pause menu (Remastered textures), then Full Reset.")


def courses(args):
    """Copy course-redirect manifests into the app's Documents/Courses."""
    source = args.courses_dir
    if not source or not source.is_dir():
        raise RuntimeError("--courses-dir must name a directory of manifest .txt files")
    manifests = sorted(p for p in source.iterdir() if p.suffix == '.txt')
    if not manifests:
        raise RuntimeError(f"No .txt manifests in {source}")
    for path in manifests:
        # The app applies these to the event table at boot; a malformed one
        # would fail the boot, so parse each before it leaves the Mac.
        try:
            from gamecube_course_check import parse_course_manifest
        except ImportError:
            from tools.gamecube_course_check import parse_course_manifest
        parse_course_manifest(path.read_text())
    print(f"{len(manifests)} manifests: " + ", ".join(p.stem for p in manifests))
    if args.simulator:
        destination = simulator_documents(args) / "Courses"
        destination.mkdir(parents=True, exist_ok=True)
        for path in manifests:
            shutil.copy2(path, destination / path.name)
        print(f"Courses copied to the simulator container: {destination}")
        return
    copy_to(args, source, "Documents/Courses", timeout=300)
    print("Courses copied to the device container: Documents/Courses\n"
          "Pick one in the app's pause menu (Course), then Full Reset.")


def launch(args):
    flags = []
    internal_scale = getattr(args, "internal_scale", None)
    if internal_scale is not None and (type(internal_scale) is not int or internal_scale not in (1, 2, 3, 4)):
        raise ValueError("--internal-scale must be 1, 2, 3 or 4")
    null_audio = getattr(args, "simulator_null_audio", False)
    if null_audio and not args.simulator:
        raise ValueError("--simulator-null-audio requires --simulator")
    sequence = validate_sequence(json.loads(args.sequence.read_text())) if args.sequence else None
    if sequence and sequence.get("start_when")=="main_menu" and not getattr(args,"debug_main_menu",False):
        raise ValueError("main_menu sequences require --debug-main-menu")
    if null_audio and sequence is None:
        raise ValueError("--simulator-null-audio requires a bounded --sequence")
    smoothing_at = getattr(args, "smoothing_at", None)
    if smoothing_at is not None:
        if sequence is None:
            raise ValueError("--smoothing-at requires a bounded --sequence")
        if not math.isfinite(smoothing_at) or not 0 <= smoothing_at <= sequence["duration"]-40:
            raise ValueError("--smoothing-at must be nonnegative and leave 40 seconds before test end")
    f_at = getattr(args, "f_at", None)
    if f_at is not None:
        if sequence is None:
            raise ValueError("--f-at requires a bounded --sequence")
        if not math.isfinite(f_at) or not 0 <= f_at <= sequence["duration"]-40:
            raise ValueError("--f-at must be nonnegative and leave 40 seconds before test end")
    if args.sequence:
        if args.simulator:
            shutil.copy2(args.sequence, simulator_documents(args) / "test-sequence.json")
        else:
            copy_to(args, args.sequence, "Documents/test-sequence.json")
        flags = ["-ssxAutoTest"]
    if getattr(args, "output_scale", None):
        flags.extend(["-ssxOutputScale", args.output_scale])
    if internal_scale is not None:
        flags.extend(["-ssxInternalScale", str(internal_scale)])
    if smoothing_at is not None:
        flags.extend(["-ssxSmoothingAt", str(smoothing_at)])
    if f_at is not None:
        flags.extend(["-ssxFAt", str(f_at)])
    if null_audio:
        flags.append("-ssxNullAudio")
    if getattr(args,"debug_main_menu",False):
        flags.append("-ssxDebugMainMenu")
    if getattr(args,"normal_boot",False):
        flags.append("-ssxNormalBoot")
    if getattr(args,"cpu_thread",False):
        flags.append("-ssxCPUThread")
    if getattr(args,"single_core",False):
        flags.append("-ssxSingleCore")
    if getattr(args,"fast_disc",False):
        flags.append("-ssxFastDisc")
    if getattr(args,"dispatch_samples",False):
        flags.append("-ssxDispatchSamples")
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
    parser.add_argument("command", choices=("configure", "build", "sign", "install", "provision", "world",
                                           "textures", "courses", "launch", "collect"))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--simulator", action="store_true", help="Use the iOS Simulator SDK and simctl")
    parser.add_argument("--device", help="Paired iPhone name/identifier, or simulator UUID with --simulator")
    parser.add_argument("--game", type=Path, default=native.DEFAULT_GAME)
    parser.add_argument("--force-install", action="store_true",
                        help="Install even though the app is running, ending that session")
    parser.add_argument("--stock-glyphs", action="store_true",
                        help="Provision the disc's own GameCube prompt icons instead of repainting them for Xbox positions")
    parser.add_argument("--sequence", type=Path, help="Optional bounded automated input sequence")
    parser.add_argument("--output-scale", choices=("full", "three-quarter", "match-internal", "half"),
                        help="Launch-only drawable scale; normal launches use the saved choice (initially half)")
    parser.add_argument("--internal-scale", type=int, choices=(1, 2, 3, 4),
                        help="Launch-only GameCube internal detail; normal launches use the saved choice (initially 2x)")
    parser.add_argument("--smoothing-at", type=float,
                        help="Request one guarded trial at active test seconds; requires --sequence and 40 seconds remaining; separate from --f-at by 40+ seconds or the later trial skips")
    parser.add_argument("--f-at", type=float,
                        help="Request one guarded route-F sim trial at active test seconds; requires --sequence and 40 seconds remaining; separate from --smoothing-at by 40+ seconds or the later trial skips")
    parser.add_argument("--simulator-null-audio", action="store_true",
                        help="Graphics-only Simulator diagnostic; requires launch, --simulator, and bounded --sequence")
    boot=parser.add_mutually_exclusive_group()
    boot.add_argument("--debug-main-menu",action="store_true",
                      help="Launch with faster cold starts; preserve checkpoint restore and saved preference")
    boot.add_argument("--normal-boot",action="store_true",
                      help="Launch with normal cold starts, overriding the saved faster-start preference")
    parser.add_argument("--world", type=Path, help="Built BAM.BIG for the world command")
    parser.add_argument("--pack", type=Path,
                        help="Directory of tex1_*.png replacements for the textures command")
    parser.add_argument("--courses-dir", type=Path,
                        help="Directory of course-redirect manifests for the courses command")
    core=parser.add_mutually_exclusive_group()
    core.add_argument("--cpu-thread", action="store_true",
                      help="Launch-only dual-core runtime for this process, ignoring the saved menu choice (default on)")
    core.add_argument("--single-core", action="store_true",
                      help="Launch-only single-core runtime for this process; the control for dual-core comparisons")
    parser.add_argument("--fast-disc", action="store_true",
                        help="Launch-only Dolphin FastDiscSpeed for a loading comparison")
    parser.add_argument("--fast-fp", action="store_true",
                        help="configure/build: compile the generated module with the inline JIT-fidelity floating-point paths")
    parser.add_argument("--dispatch-samples", action="store_true",
                        help="Launch-only native dispatch-site sampling (diagnostic overhead)")
    args = parser.parse_args()
    for flag in ("cpu_thread", "single_core", "fast_disc", "dispatch_samples"):
        if getattr(args, flag) and args.command != "launch":
            parser.error(f"--{flag.replace('_', '-')} applies only to launch")
    if (args.debug_main_menu or args.normal_boot) and args.command!="launch":
        parser.error("--debug-main-menu and --normal-boot apply only to launch")
    if args.output_scale and args.command != "launch":
        parser.error("--output-scale applies only to launch")
    if args.internal_scale is not None and args.command != "launch":
        parser.error("--internal-scale applies only to launch")
    if args.smoothing_at is not None and args.command != "launch":
        parser.error("--smoothing-at applies only to launch")
    if args.f_at is not None and args.command != "launch":
        parser.error("--f-at applies only to launch")
    if args.simulator_null_audio and (args.command != "launch" or not args.simulator or not args.sequence):
        parser.error("--simulator-null-audio requires launch, --simulator, and a bounded --sequence")
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
