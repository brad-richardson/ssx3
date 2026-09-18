#!/usr/bin/env python3
"""S2 Android trial TU relink (research only, runs on the SSD).

Mirrors `tools/android_trial.py build` (pristine TU from the pinned revision
+ INNER_ANDROID_STACK, TU copy, compile_commands retarget, relink ahead of
archives, receipt) with S2 substitutions: the instrumented headers are the
trial set plus replay_plan.h and local/research/S2/s2_replay_capacity.h, and
the dispatch step calls the trial driver (headless lifecycle) then the D2
replay instrument. The device cannot pass SSX_NATIVE_REPLAY (fixed launch
env), so the TU compiles with -DSSX_D2_REPLAY_ALWAYS=1 (receipt-recorded);
the desktop player stays env-gated. Reads reference trees read-only; writes
only the fresh SSD output dir.
"""
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import android_trial as trial

S2_HEADER = ROOT / "local/research/S2/s2_replay_capacity.h"
DOL_SHA256 = trial.DOL_SHA256
HEADERS = ("trial_control.h", "native_callback_trace.h", "callback_timing.h",
           "render_deadline.h", "native_render_schedule.h", "pose_history.h",
           "native_pose_interpolation.h", "replay_plan.h", "android_trial_driver.h")
INCLUDE_ORDER = ("native_callback_trace.h", "native_render_schedule.h",
                 "native_pose_interpolation.h", "s2_replay_capacity.h",
                 "android_trial_driver.h")
INCLUDE_ORDER_PLAIN = ("native_callback_trace.h", "native_render_schedule.h",
                       "native_pose_interpolation.h", "android_trial_driver.h")
STEP_CALL = ("          NativeTrialAndroid::Step(m_guest);\n"
             "          NativeReplay::Step(m_guest);\n")
STEP_CALL_PLAIN = "          NativeTrialAndroid::Step(m_guest);\n"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


D5_PATCH = Path("/Volumes/Extreme SSD/android-spike/D5/instrument.patch")


def apply_d5exc(out, source):
    """Apply D5's Run.cpp section verbatim (patch(1), fails loudly).

    D5's exception attribution lives in d5-build's archives (other TUs call
    DumpExcAttribution); a shadowing TU must provide the same definitions or
    the shadowed member gets pulled and collides. The source must equal D5's
    .orig base; the result is D5's exact compiled TU (their binary is the
    ground truth). Verbatim, attributed, TEMPORARY (see D5 REPORT).
    """
    text = D5_PATCH.read_text()
    section = text.split("=== StaticRecompCore_Run.cpp ===")[1].split("=== StaticRecompCore.cpp ===")[0]
    lines = ["--- a/StaticRecompCore_Run.cpp", "+++ b/StaticRecompCore_Run.cpp"]
    for line in section.splitlines()[1:]:
        if line.startswith("--- ") or line.startswith("+++ "):
            continue
        lines.append(line)
    base = out / "pristine_Run.cpp"
    base.write_text(source)
    (out / "d5-run.patch").write_text("\n".join(lines) + "\n")
    patched = out / "d5patched_Run.cpp"
    patched.write_text(source)
    subprocess.run(["patch", "-p1", str(patched)], input="\n".join(lines) + "\n",
                   cwd=out, check=True, capture_output=True, text=True)
    result = patched.read_text()
    assert "namespace D5Exc" in result and "DumpExcAttribution" in result
    # D5's .h hunk declares the static member (functions only: class layout
    # unchanged, so shadowing this one header for trial.o alone is safe).
    # Copy m4-src's header, apply the hunk, shadow it via a prepended -I.
    hsection = text.split("=== StaticRecompCore.h ===")[1]
    hlines = ["--- a/StaticRecompCore.h", "+++ b/StaticRecompCore.h"]
    for line in hsection.splitlines()[1:]:
        if line.startswith("--- ") or line.startswith("+++ ") or line.startswith("==="):
            continue
        hlines.append(line)
    incdir = out / "d5include" / "Core" / "PowerPC" / "StaticRecomp"
    incdir.mkdir(parents=True, exist_ok=True)
    header_src = Path("/Volumes/Extreme SSD/android-spike/m4-src/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore.h")
    assert header_src.exists(), "m4-src StaticRecompCore.h not found"
    (incdir / "StaticRecompCore.h").write_text(header_src.read_text())
    (out / "d5-h.patch").write_text("\n".join(hlines) + "\n")
    subprocess.run(["patch", "-p1", str(incdir / "StaticRecompCore.h")],
                   input="\n".join(hlines) + "\n", cwd=out,
                   check=True, capture_output=True, text=True)
    shadowed = (incdir / "StaticRecompCore.h").read_text()
    assert "DumpExcAttribution" in shadowed
    return result, f"-I{out / 'd5include'}"


def pristine_tu_from_reference(reference_tu):
    """Read the pristine TU from the reference build's own source tree.

    Used when the reference runner was built from a frozen tree (e.g. m4-src)
    whose TU source differs from reconstruct_tu() output (live-stack drift
    such as uncommitted hunks). The TU is then literally the exact source
    the reference runner compiled, plus the S2 injections below.
    """
    text = Path(reference_tu).read_text()
    return text


def build(args):
    game = args.game.resolve()
    if ((game / "sys/boot.bin").read_bytes()[:6] != b"GXBE69" or
            sha(game / "sys/main.dol") != DOL_SHA256):
        raise ValueError("Trial callback addresses require the pinned GXBE69 executable")
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        raise ValueError("Android trial builds must live outside the repo (Extreme SSD)")
    out.mkdir(parents=True, exist_ok=False)
    build_dir = args.build_dir.resolve()
    production = build_dir / "moderngekko-run"
    receipt = dict(schema=1, brief="S2", dol_sha256=DOL_SHA256, game=str(game),
                   build_dir=str(build_dir), stack=list(trial.INNER_ANDROID_STACK),
                   s2_header_sha256=sha(S2_HEADER),
                   production_runner_sha256=sha(production), commands=[])
    for name in HEADERS:
        (out / name).write_bytes((trial.DIAG / name).read_bytes())
        receipt[f"{name}_sha256"] = sha(out / name)
    (out / "s2_replay_capacity.h").write_bytes(S2_HEADER.read_bytes())
    plain = args.plain_trial
    if plain:
        receipt["s2_header"] = "omitted plain-trial control"
    if args.reference_tu:
        source = pristine_tu_from_reference(args.reference_tu)
        receipt["tu_origin"] = f"reference-tree:{args.reference_tu}"
    else:
        source = trial.reconstruct_tu()
        receipt["tu_origin"] = "reconstruct_tu(pinned+INNER_ANDROID_STACK)"
    receipt["original_tu_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    # Verify injection points on the pre-D5 source: D5's own
    # 'namespace D5Exc\n{' would trip the includes-marker count.
    for marker in (trial.INCLUDES_MARKER, trial.DISPATCH_MARKER):
        if source.count(marker) != 1:
            raise ValueError(f"S2 trial injection point changed: {marker!r}")
    extra_include = None
    if args.reference_tu and args.with_d5exc:
        source, extra_include = apply_d5exc(out, source)
        receipt["d5exc"] = "verbatim D5/instrument.patch Run.cpp+.h sections via patch(1) (TEMPORARY)"
    order = INCLUDE_ORDER_PLAIN if plain else INCLUDE_ORDER
    step = STEP_CALL_PLAIN if plain else STEP_CALL
    includes = "".join(f'#include "{out / name}"\n' for name in order)
    source = trial.TRIAL_DEFINE + source
    source = source.replace(trial.INCLUDES_MARKER, includes + trial.INCLUDES_MARKER)
    source = source.replace(trial.DISPATCH_MARKER, step + trial.DISPATCH_MARKER)
    trial_source = out / "Core_Run.cpp"
    trial_source.write_text(source)
    entries = [e for e in json.loads((build_dir / "compile_commands.json").read_text())
               if e["file"].endswith("StaticRecompCore_Run.cpp")]
    if len(entries) != 1:
        raise ValueError("Expected exactly one StaticRecompCore_Run.cpp compile entry")
    trial_obj = out / "trial.o"

    def run(command, **kw):
        receipt["commands"].append(command if isinstance(command, str) else " ".join(command))
        subprocess.run(command, cwd=build_dir, check=True, **kw)

    compile_cmd = trial.adapt_compile_command(entries[0]["command"], trial_source, trial_obj)
    compile_cmd.append("-DSSX_D2_REPLAY_ALWAYS=1")
    if extra_include:
        compile_cmd.insert(1, extra_include)  # first -I wins for "Core/..."
    receipt["s2_force_define"] = "SSX_D2_REPLAY_ALWAYS=1"
    run(compile_cmd)
    ninja = args.ninja or shutil.which("ninja")
    if not ninja:
        raise ValueError("ninja is required to read the runner link command")
    commands = subprocess.run([ninja, "-C", str(build_dir), "-t", "commands",
                               "moderngekko-run"], check=True, capture_output=True, text=True)
    trial_binary = out / trial.TRIAL_BINARY
    run(trial.adapt_link_command(trial.parse_link_command(commands.stdout), trial_obj, trial_binary))
    if sha(production) != receipt["production_runner_sha256"]:
        raise RuntimeError("Production runner changed during trial build")
    receipt["trial_object_sha256"] = sha(trial_obj)
    receipt["trial_binary_sha256"] = sha(trial_binary)
    if shutil.which("file"):
        kind = subprocess.run(["file", str(trial_binary)],
                              capture_output=True, text=True).stdout.strip()
        receipt["trial_binary_file"] = kind
        if "aarch64" not in kind:
            raise RuntimeError(f"Trial binary is not aarch64: {kind}")
    (out / "build.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(trial_binary)
    return receipt


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-tu", type=Path, default=None)
    parser.add_argument("--plain-trial", action="store_true")
    parser.add_argument("--with-d5exc", action="store_true")
    parser.add_argument("--ninja")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
