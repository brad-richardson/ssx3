#!/usr/bin/env python3
"""S2 replay-capacity player build (research only, not committed as a tool).

Mirrors `tools/gamecube_native_trace.py build --scheduler --replay` semantics
(same header set, include order, probe namespace, compile_copy + relink
technique, same launcher/receipt shape) with one substitution: the replay
header compiled into the player is local/research/S2/s2_replay_capacity.h
(the S2 fixed loop), never native/diagnostics/native_frame_replay.h.
Reads the shared tree read-only; writes only the fresh output dir. Refuses
to run while the production runner or the live vendor tree changes under it.
"""
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from gamecube_draw_trace import BUILD, VENDOR, compile_copy, sha

DOL_SHA256 = "b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce"
S2_HEADER = ROOT / "local/research/S2/s2_replay_capacity.h"
GAME = ROOT / "local/game/gxbe69-stock"


def main(output):
    out = Path(output).resolve()
    if not out.is_relative_to(ROOT / "local"):
        raise ValueError("Diagnostic outputs must remain under local/")
    if (GAME / "sys/boot.bin").read_bytes()[:6] != b"GXBE69" or \
            sha(GAME / "sys/main.dol") != DOL_SHA256:
        raise ValueError("Callback addresses require the pinned GXBE69 executable")
    out.mkdir(parents=True, exist_ok=False)
    original = VENDOR / "vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp"
    production = BUILD / "moderngekko-run"
    receipt = dict(schema=1, brief="S2", dol_sha256=DOL_SHA256, game=str(GAME),
                   original_source_sha256=sha(original),
                   s2_header_sha256=sha(S2_HEADER),
                   production_runner_sha256=sha(production), commands=[])
    source = original.read_text()
    includes, dispatch = "namespace\n{", "          const u32 runtime_dispatch_address = m_guest.pc;"
    for marker in (includes, dispatch):
        if source.count(marker) != 1:
            raise ValueError(f"Native diagnostic injection point changed: {marker!r}")
    # Same header set and include order as --scheduler --replay.
    header_copy = out / "native_callback_trace.h"
    header_copy.write_bytes((ROOT / "native/diagnostics/native_callback_trace.h").read_bytes())
    timing = ROOT / "native/diagnostics/callback_timing.h"
    (out / timing.name).write_bytes(timing.read_bytes())
    receipt["callback_timing_sha256"] = sha(timing)
    receipt["scheduler_headers"] = {}
    extra_includes = ""
    for name in ("render_deadline.h", "native_render_schedule.h", "replay_plan.h"):
        path = ROOT / "native/diagnostics" / name
        (out / name).write_bytes(path.read_bytes())
        receipt["scheduler_headers"][name] = sha(path)
        extra_includes += f'#include "{out / name}"\n'
    replay_copy = out / "native_frame_replay.h"
    replay_copy.write_bytes(S2_HEADER.read_bytes())
    extra_includes += f'#include "{replay_copy}"\n'
    source = source.replace(includes, f'#include "{header_copy}"\n' + extra_includes + includes)
    source = source.replace(dispatch, "          NativeReplay::Step(m_guest);\n" + dispatch)
    copy = out / "Core_Run.cpp"
    copy.write_text(source)
    commands = subprocess.check_output(
        [str(ROOT / "local/tooling/ninja"), "-C", str(BUILD), "-t", "commands", "moderngekko-run"],
        text=True).splitlines()

    def run(command):
        receipt["commands"].append(command)
        subprocess.run(command, cwd=BUILD, check=True)

    run(compile_copy(next(c for c in commands if c.endswith("/StaticRecompCore_Run.cpp")),
                     copy, out / "probe.o"))
    link = shlex.split(next(c for c in commands if " -o moderngekko-run " in c))
    link = link[2:link.index("&&", 2)]
    link[link.index("-o") + 1] = str(out / "player")
    link.insert(link.index("libmoderngekko.a"), str(out / "probe.o"))
    run(link)
    if sha(production) != receipt["production_runner_sha256"]:
        raise RuntimeError("Production runner changed during diagnostic build")
    receipt["player_sha256"] = sha(out / "player")
    native_launcher = out / "run_native.py"
    native_launcher.write_text(
        "import sys\nfrom pathlib import Path\n"
        f"ROOT=Path({str(ROOT)!r})\n"
        "sys.path.insert(0,str(ROOT/'tools'))\n"
        "import native_gamecube as native\n"
        "original=native.executable\n"
        f'player=Path({str(out / "player")!r})\n'
        "native.executable=lambda name: player if name=='moderngekko-run' else original(name)\n"
        "native.main()\n")
    course_launcher = out / "course_check.py"
    course_launcher.write_text(
        "import sys\nfrom pathlib import Path\n"
        f"ROOT=Path({str(ROOT)!r})\n"
        "sys.path.insert(0,str(ROOT/'tools'))\n"
        "import gamecube_course_check as course\n"
        "original=course.subprocess.Popen\n"
        "def launch(args,*pos,**kw):\n"
        " args=list(args)\n"
        " target=str(ROOT/'tools/native_gamecube.py')\n"
        f" if target in args: args[args.index(target)]={str(native_launcher)!r}\n"
        " return original(args,*pos,**kw)\n"
        "course.subprocess.Popen=launch\n"
        "course.main()\n")
    receipt["launchers"] = {p.name: sha(p) for p in (native_launcher, course_launcher)}
    (out / "build.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(out / "player")


if __name__ == "__main__":
    main(sys.argv[1])
