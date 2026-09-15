#!/usr/bin/env python3
"""Pinned macOS SSX 3 AOT prototype. Game bytes and builds stay under local/.

bootstrap fetches sources; configure/build compile the runtime; module translates
the verified DOL; run launches with CPU JIT fallback disabled by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / "native/dependencies.json").read_text())
SOURCE = ROOT / "third_party/ModernGekko"
CORE = SOURCE / "vendor/dolphin"
BUILD = ROOT / "local/native/runtime-build"
MODULE = ROOT / "local/native/ssx3-module"
DEFAULT_GAME = Path("/Volumes/share/brad/games/ssx3-workbench/native/GXBE69")


def sha256(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def run(command, **kwargs):
    print("+", " ".join(map(str, command)), flush=True)
    return subprocess.run(list(map(str, command)), check=True, **kwargs)


def revision(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def check_pins():
    for path, expected in ((SOURCE, PINS["moderngekko"]["revision"]),
                           (CORE, PINS["recompcore_revision"]),
                           (CORE / "DolRecomp", PINS["dolrecomp_revision"])):
        actual = revision(path)
        if actual != expected:
            raise RuntimeError(f"{path}: expected {expected}, found {actual}")


def check_patches():
    for checkout, filename in ((CORE, "recompcore-platform.patch"), (SOURCE, "moderngekko-platform.patch")):
        run(["git", "-C", checkout, "apply", "--reverse", "--check", ROOT / "native/patches" / filename])


def bootstrap(args):
    if not SOURCE.exists():
        SOURCE.mkdir(parents=True)
        run(["git", "init", SOURCE])
        run(["git", "-C", SOURCE, "remote", "add", "origin", PINS["moderngekko"]["url"]])
        run(["git", "-C", SOURCE, "fetch", "--depth", "1", "origin", PINS["moderngekko"]["revision"]])
        run(["git", "-C", SOURCE, "checkout", "--detach", "FETCH_HEAD"])
    if revision(SOURCE) != PINS["moderngekko"]["revision"]:
        raise RuntimeError("Existing ModernGekko checkout has a different revision; refusing to replace it")
    run(["git", "-C", SOURCE, "submodule", "update", "--init", "--depth", "1", "vendor/dolphin"])
    run(["git", "-C", CORE, "submodule", "update", "--init", "--depth", "1", "--jobs", args.jobs,
         *PINS["core_submodules"]])
    run(["git", "-C", CORE / "Externals/cubeb/cubeb", "submodule", "update", "--init", "--recursive", "--depth", "1"])
    check_pins()
    for checkout, filename in ((CORE, "recompcore-platform.patch"), (SOURCE, "moderngekko-platform.patch")):
        patch = ROOT / "native/patches" / filename
        already = subprocess.run(["git", "-C", str(checkout), "apply", "--reverse", "--check", str(patch)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not already:
            run(["git", "-C", checkout, "apply", "--check", patch])
            run(["git", "-C", checkout, "apply", patch])


def ninja():
    path = ROOT / "local/tooling/ninja"
    if path.is_file():
        return path
    found = shutil.which("ninja")
    if not found:
        raise RuntimeError("Install Ninja or place the verified macOS binary at local/tooling/ninja (see native/dependencies.json)")
    return Path(found)


def configure(args):
    check_pins()
    check_patches()
    run(["cmake", "-S", SOURCE, "-B", BUILD, "-G", "Ninja",
         f"-DCMAKE_MAKE_PROGRAM={ninja()}", "-DCMAKE_C_COMPILER=/usr/bin/clang",
         "-DCMAKE_CXX_COMPILER=/usr/bin/clang++", "-DCMAKE_AR=/usr/bin/ar", "-DCMAKE_RANLIB=/usr/bin/ranlib",
         "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0", "-DBUILD_TESTING=OFF",
         "-DDOLRECOMP_ENABLE_LLVM=OFF", "-DENABLE_VULKAN=OFF", "-DUSE_BUNDLED_MOLTENVK=OFF",
         "-DMODERNGEKKO_GAMECUBE_CONTROLLERS=ON", f"-DMODERNGEKKO_REQUIRED_DISC_ID={PINS['disc_id']}",
         f"-DMODERNGEKKO_REQUIRED_DOL_SHA256={PINS['dol_sha256']}",
         "-DMODERNGEKKO_DEFAULT_WINDOW_TITLE=SSX 3 Native Prototype"])


def build(args):
    check_pins()
    check_patches()
    run(["cmake", "--build", BUILD, "--target", "moderngekko-run", "moderngekko-port",
         "moderngekko-module-info", "-j", args.jobs])


def executable(name):
    matches = [p for p in BUILD.rglob(name) if p.is_file() and os.access(p, os.X_OK)]
    if not matches:
        raise RuntimeError(f"Build the runtime first: missing {name}")
    return min(matches, key=lambda p: len(p.parts))


def module(args):
    check_pins()
    dol = args.dol.resolve()
    if sha256(dol) != PINS["dol_sha256"]:
        raise RuntimeError("DOL hash differs from verified GXBE69 revision 0")
    generator = executable("dolrecomp")
    generated = MODULE / "codegen/generated"
    receipt = MODULE / "generation.json"
    identity = {"dol_sha256": PINS["dol_sha256"], "dolrecomp_revision": PINS["dolrecomp_revision"],
                "generator_sha256": sha256(generator), "backend": "c"}
    if not receipt.exists() or json.loads(receipt.read_text()) != identity:
        if generated.exists():
            raise RuntimeError("Existing generated output has a different or incomplete identity; use a fresh module directory")
        MODULE.mkdir(parents=True, exist_ok=True)
        run([generator, f"-j{args.jobs}", "--backend=c", "--cpu", "gekko", "--gamecube", dol, MODULE / "codegen"])
        shutil.copy2(dol, generated / "main.dol")
        receipt.write_text(json.dumps(identity, indent=2) + "\n")
    run(["cmake", "-S", CORE / "module-template", "-B", MODULE / "build", "-G", "Ninja",
         f"-DCMAKE_MAKE_PROGRAM={ninja()}", "-DCMAKE_C_COMPILER=/usr/bin/clang",
         "-DCMAKE_AR=/usr/bin/ar", "-DCMAKE_RANLIB=/usr/bin/ranlib", "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0", f"-DGAME_ID={PINS['disc_id']}",
         f"-DGENERATED_DIR={generated}", f"-DGXRUNTIME_DIR={CORE / 'GXRuntime'}",
         f"-DCHASSIS_ABI_DIR={CORE / 'Source/Core/Core/PowerPC/StaticRecomp'}",
         f"-DRECOMPCORE_MODULE_OPT_LEVEL={args.opt_level}",
         f"-DRECOMPCORE_FAST_FP={'ON' if getattr(args, 'fast_fp', False) else 'OFF'}"])
    run(["cmake", "--build", MODULE / "build", "-j", args.jobs])
    library = MODULE / "build/gGXBE69_recomp.dylib"
    metadata = {**identity, "dependencies": PINS, "module_sha256": sha256(library),
                "opt_level": args.opt_level, "fast_fp": bool(getattr(args, "fast_fp", False)),
                "cpu_jit_required": "not established by compilation"}
    (MODULE / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    run([executable("moderngekko-module-info"), library])


def runtime_evidence(text):
    counters = re.search(r"\[staticrecomp\] shutdown: ([^\n]+)", text)
    jit = re.search(r"\[staticrecomp\] fallback_jit_runs=(\d+)", text)
    mode = re.search(r"\[staticrecomp\] fallback mode: (\w+)", text)
    return {
        "module_loaded": "[staticrecomp] module loaded:" in text,
        "cpu_fallback_mode": mode[1] if mode else None,
        "fallback_jit_runs": int(jit[1]) if jit else None,
        "invalid_memory_accesses": len(re.findall(
            r"\bInvalid (?:read from|write to)\b|\bUnknown Pointer 0x[0-9a-fA-F]+", text)),
        "gpu_command_errors": text.count('GFX FIFO: Unknown Opcode'),
        "unknown_guest_instructions": len(re.findall(
            r'unknown guest instruction|IntCPU: Unknown instruction', text)),
        "shutdown_counters": {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", counters[1])} if counters else None,
        "performance_samples": [dict(sample=int(sample), fps=float(fps), vps=float(vps), speed=float(speed))
                                for sample, fps, vps, speed in re.findall(
                                    r"\[ssx3-metrics\] sample=(\d+) fps=([\d.]+) vps=([\d.]+) speed=([\d.]+)", text)],
        "sites": [dict(kind=kind, pc="0x" + pc, samples=int(count)) for kind, pc, count in re.findall(
            r"\[staticrecomp\] (dispatch|fallback)-site pc=([0-9a-f]+) samples=(\d+)", text)],
    }


def runtime_fault(chunk):
    """Errors that invalidate a local diagnostic immediately, before log floods."""
    match = re.search(rb'Invalid (?:read from|write to)|Unknown Pointer 0x[0-9a-fA-F]+|GFX FIFO: Unknown Opcode|unknown guest instruction|IntCPU: Unknown instruction', chunk)
    return match[0].decode('ascii') if match else None


def wait_for_runtime(process, log_path, seconds):
    deadline = time.monotonic()+seconds if seconds is not None else float('inf')
    carry = b''
    with log_path.open('rb') as stream:
        while process.poll() is None:
            chunk = stream.read(1024*1024)
            fault = runtime_fault(carry+chunk)
            if log_path.stat().st_size > 32*1024*1024:
                fault = fault or 'Diagnostic log exceeded 32 MiB'
            if fault:
                # A corrupt runtime can remain inside a copy loop during a
                # graceful shutdown. Stop this owned diagnostic immediately.
                process.kill()
                return process.wait(), fault
            carry = (carry+chunk)[-128:]
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(process.args, seconds)
            time.sleep(.05)
    return process.returncode, None


def verify_runtime_execution(evidence):
    """Basic execution gate; gameplay still requires course-state/capture checks."""
    counters = evidence['shutdown_counters']
    if not evidence['module_loaded'] or not counters:
        raise RuntimeError('Run lacks module/shutdown evidence')
    if counters.get('native', 0) <= 0:
        raise RuntimeError('Run never executed the native game module')
    if counters.get('smc_failed', 0) or evidence.get('invalid_memory_accesses', 0):
        raise RuntimeError('Run contains code verification failures or invalid memory accesses')
    if evidence.get('gpu_command_errors', 0):
        raise RuntimeError('Run contains malformed GPU commands')
    if evidence.get('unknown_guest_instructions', 0):
        raise RuntimeError('Run contains unknown guest instructions')


def verify_rendered_frames(rendering, seconds):
    """Long visual runs must keep producing captures, not cached FPS values."""
    if seconds >= 60 and (rendering['last_screenshot_age_seconds'] is None or
                          rendering['last_screenshot_age_seconds'] > 60):
        raise RuntimeError('Visual run stopped producing screenshots; cached FPS is not gameplay evidence')


def launch(args):
    check_pins()
    check_patches()
    if args.seconds is not None and args.seconds <= 0:
        raise RuntimeError("--seconds must be positive")
    game = args.game.resolve()
    if sha256(game / "sys/main.dol") != PINS["dol_sha256"]:
        raise RuntimeError("Extracted game's DOL hash is incorrect")
    profile = ROOT / "local/native/profiles" / args.profile
    if profile.parent != ROOT / "local/native/profiles" or args.profile in (".", ".."):
        raise RuntimeError("--profile must be a single directory name")
    profile.mkdir(parents=True, exist_ok=True)
    config_dir = profile / "Config"
    config_dir.mkdir(exist_ok=True)
    config = config_dir / "Dolphin.ini"
    cpu_thread = "True" if getattr(args, "cpu_thread", False) else "False"
    if not config.exists():
        # SSX3_IDLE_PC=0x80288ED4 (the OS idle spin in SelectThread) enables the
        # runtime's idle-loop skipping for a fresh profile; research knob only.
        idle = os.environ.get("SSX3_IDLE_PC")
        extra = f"StaticRecompIdlePC = {idle}\n" if idle else ""
        if os.environ.get('SSX3_RUSH_PRESENT') == '1':
            extra += 'RushFramePresentation = True\n'
        config.write_text(f"[Core]\nCPUThread = {cpu_thread}\nDSPHLE = True\nSkipIPL = True\n{extra}[DSP]\nEnableJIT = False\n[Interface]\nConfirmStop = False\n")
    if f"CPUThread = {cpu_thread}\n" not in config.read_text():
        raise RuntimeError(f"Existing profile {args.profile} does not use CPUThread = {cpu_thread}; use a fresh --profile")
    texture_settings = {}
    if getattr(args, "texture_dump", False):
        # Dolphin's own dumper writes PROFILE/Dump/Textures/<game id>/ with the
        # standard tex1_<w>x<h>_<hash>[_<tlut hash>]_<format>.png name, which is
        # the same key the hi-res loader reads back.
        texture_settings["DumpTextures"] = "True"
        texture_settings["DumpBaseTextures"] = "True"
    if getattr(args, "texture_pack", None):
        pack = Path(args.texture_pack).resolve()
        if not pack.is_dir():
            raise RuntimeError(f"No texture pack directory at {pack}")
        # D_HIRESTEXTURES is PROFILE/Load/Textures; Dolphin searches the game-id
        # subdirectory recursively for tex1_*.png / .dds.
        load = profile / "Load/Textures"
        load.mkdir(parents=True, exist_ok=True)
        link = load / "GXBE69"
        if link.is_symlink() or link.exists():
            if not link.is_symlink() or link.resolve() != pack:
                raise RuntimeError(f"{link} already exists; use a fresh --profile")
        else:
            link.symlink_to(pack)
        texture_settings["HiresTextures"] = "True"
        texture_settings["CacheHiresTextures"] = "True"
    if texture_settings:
        # These belong in the per-game layer, not GFX.ini: UICommon::Init runs
        # SetBaseOrCurrent(GFX_DUMP_TEXTURES, false) and saves, so a base-layer
        # GFX.ini value is overwritten before the video backend reads it.
        # GameSettings/<id>.ini is the LocalGame layer, which sits above base,
        # and its [Video_Settings] maps to the GFX "Settings" section
        # (Core/ConfigLoaders/GameConfigLoader.cpp).
        settings_dir = profile / "GameSettings"
        settings_dir.mkdir(exist_ok=True)
        game_ini = settings_dir / "GXBE69.ini"
        body = "".join(f"{key} = {value}\n" for key, value in sorted(texture_settings.items()))
        game_ini.write_text(f"[Video_Settings]\n{body}")
    if args.pipe_controller:
        pipes = profile / "Pipes"
        pipes.mkdir(exist_ok=True)
        pipe = pipes / "ssx3"
        if not pipe.exists():
            os.mkfifo(pipe)
        import stat
        if not stat.S_ISFIFO(pipe.stat().st_mode):
            raise RuntimeError(f"{pipe} must be a named pipe")
        pad = config_dir / "GCPadNew.ini"
        mapping = "[GCPad1]\nDevice = Pipe/0/ssx3\nOptions/Always Connected = True\n"
        for label, button in (("A", "A"), ("B", "B"), ("X", "X"), ("Y", "Y"), ("Z", "Z"), ("Start", "START")):
            mapping += f"Buttons/{label} = `Button {button}`\n"
        for group, prefix in (("Main Stick", "MAIN"), ("C-Stick", "C")):
            for direction, axis in (("Up", "Y +"), ("Down", "Y -"), ("Left", "X -"), ("Right", "X +")):
                mapping += f"{group}/{direction} = `Axis {prefix} {axis}`\n"
        for direction in ("Up", "Down", "Left", "Right"):
            mapping += f"D-Pad/{direction} = `Button D_{direction.upper()}`\n"
        for trigger in ("L", "R"):
            mapping += f"Triggers/{trigger} = `Button {trigger}`\nTriggers/{trigger}-Analog = `Axis {trigger} +`\n"
        if pad.exists() and "Device = Pipe/0/ssx3" not in pad.read_text():
            raise RuntimeError("Use a fresh --profile for pipe input; preserving the existing controller mapping")
        if not pad.exists():
            pad.write_text(mapping)
    reports = ROOT / "local/reports/native-runs"
    reports.mkdir(parents=True, exist_ok=True)
    # The profile is part of the name because several runs can be in flight at
    # once (texture dumps across courses, for one) and a bare timestamp
    # collides at one-second resolution: two runs then interleave into one log
    # and each reads the other's evidence from it.
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_profile = "".join(c if c.isalnum() or c in "._-" else "_" for c in args.profile)
    log_path = reports / f"{stamp}-{safe_profile}.log"
    for attempt in range(2, 100):
        if not log_path.exists():
            break
        log_path = reports / f"{stamp}-{safe_profile}-{attempt}.log"
    if log_path.exists():
        raise RuntimeError("Could not find an unused run log name")
    env = os.environ.copy()
    env.update(SSX3_NO_EXECUTABLE_MEMORY="0" if args.jit_fallback else "1",
               STATICRECOMP_NO_JIT="0" if args.jit_fallback else "1",
               SSX3_RUNTIME_METRICS="1")
    dispatch_samples = os.environ.get('SSX3_DISPATCH_SAMPLES', '1') != '0'
    if dispatch_samples:
        env.update(STATICRECOMP_DISPATCH_SAMPLES='1',
                   # Beside its own log, so parallel runs keep separate traces and
                   # `<log stem>-dispatch.csv` still finds the right one.
                   STATICRECOMP_TRACE_FILE=str(log_path.with_name(log_path.stem + '-dispatch.csv')))
    else:
        env.pop('STATICRECOMP_DISPATCH_SAMPLES', None)
        env.pop('STATICRECOMP_TRACE_FILE', None)
    if not args.headless:
        env["SSX3_SCREENSHOTS"] = "1"
        if getattr(args, 'screenshot_seconds', None):
            env["SSX3_SCREENSHOT_SECONDS"] = str(args.screenshot_seconds)
    if args.pipe_controller:
        env["SSX3_BACKGROUND_INPUT"] = "1"
    module_path = (args.module.resolve() if getattr(args, "module", None) else MODULE / "build/gGXBE69_recomp.dylib")
    command = [str(executable("moderngekko-run")), "--game", str(game), "--module",
               str(module_path), "--user-dir", str(profile),
               "--no-mods", "--graphics", "Null" if args.headless else "Metal"]
    if args.headless:
        command += ["--headless", "--audio", "Null"]
    print(f"Log: {log_path}", flush=True)
    runner_sha256 = sha256(command[0])
    module_sha256 = sha256(module_path)
    world_archive = game / 'files/data/worlds/bam.big'
    world_sha256 = sha256(world_archive) if world_archive.is_file() else None
    # A course-redirect game directory can hold several world archives and boot
    # any of them (docs/course-selection.md), so bam.big alone no longer says
    # what was ridden. Record every installed archive.
    world_archives = {path.name: sha256(path)
                      for path in sorted((game / 'files/data/worlds').glob('*.big'))}
    started_wall = time.time()
    started = time.monotonic()
    with log_path.open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        stopped_on_fault = None
        try:
            code, stopped_on_fault = wait_for_runtime(process, log_path, args.seconds)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            process.terminate()
            try:
                code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait()
    result = {"command": command, "exit_code": code, "seconds": time.monotonic() - started,
              "dispatch_samples": dispatch_samples,
              "cpu_thread": cpu_thread == "True",
              "module_path": str(module_path),
              "metal_validation": env.get('MTL_DEBUG_LAYER'),
              "core_config_sha256": sha256(config),
              "stopped_on_fault": stopped_on_fault,
              "requested_cpu_jit_fallback": args.jit_fallback, "log": str(log_path),
              "profile": str(profile), "runner_sha256": runner_sha256,
              "module_sha256": module_sha256,
              "world_archive_sha256": world_sha256,
              "world_archives_sha256": world_archives,
              "texture_dump": bool(getattr(args, "texture_dump", False)),
              "texture_pack": str(Path(args.texture_pack).resolve()) if getattr(args, "texture_pack", None) else None,
              "evidence": runtime_evidence(log_path.read_text(errors="replace"))}
    if not args.headless:
        captures = [p.stat().st_mtime for p in (profile / 'ScreenShots').rglob('*.png')
                    if p.stat().st_mtime >= started_wall]
        result['rendering'] = dict(screenshot_count=len(captures),
                                   last_screenshot_age_seconds=time.time()-max(captures) if captures else None)
    # Beside its own log, so `<log>.json` is this run's receipt even when
    # several runs share a second.
    log_path.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if code:
        raise RuntimeError(f"Runtime exited {code}; inspect {log_path}")
    verify_runtime_execution(result['evidence'])
    if not args.headless:
        verify_rendered_frames(result['rendering'], result['seconds'])
    if not args.jit_fallback and (result["evidence"]["cpu_fallback_mode"] != "interpreter" or
                                  result["evidence"]["fallback_jit_runs"] != 0):
        raise RuntimeError("Runtime did not verify the requested CPU interpreter fallback mode")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("bootstrap", "configure", "build", "module", "run"))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--dol", type=Path, default=ROOT / "local/source/gamecube/ssx3/sys/main.dol")
    parser.add_argument("--opt-level", choices=("0", "1", "2", "3"), default="2")
    parser.add_argument("--game", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--profile", default="stock")
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--jit-fallback", action="store_true", help="Desktop diagnostic only; default is interpreter fallback")
    parser.add_argument("--pipe-controller", action="store_true", help="Map a test pad to PROFILE/Pipes/ssx3")
    parser.add_argument("--fast-fp", action="store_true",
                        help="module: build generated chunks with the inline JIT-fidelity floating-point paths")
    parser.add_argument("--module", type=Path, help="run: module dylib to load instead of the default build")
    parser.add_argument("--cpu-thread", action="store_true",
                        help="Dual-core runtime (CPUThread = True); applies to a fresh profile's Dolphin.ini")
    parser.add_argument("--screenshot-seconds", type=int,
                        help="Screenshot cadence for a visual run (default 15). A visual A/B "
                             "needs a fine cadence: two arms can only be matched to within "
                             "half an interval of each other (docs/texture-remaster.md)")
    parser.add_argument("--texture-dump", action="store_true",
                        help="run: dump every texture the game loads to PROFILE/Dump/Textures/GXBE69")
    parser.add_argument("--texture-pack", type=Path,
                        help="run: load replacement textures from this directory (linked as "
                             "PROFILE/Load/Textures/GXBE69)")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    try:
        {"bootstrap": bootstrap, "configure": configure, "build": build,
         "module": module, "run": launch}[args.command](args)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
