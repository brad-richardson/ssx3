#!/usr/bin/env python3
"""Stock-track census for M3: per-course render cost on one pinned player.

Step 2 of docs/plan-120fps-2026-09-17.md (M3): for every stock course, ride
it through a redirect manifest and record draws per presented frame (median,
p95), update/render callback CPU medians, vertex counts per frame, and
whether the rider rode. Step 3 ranks by render CPU median and draws p95.

The repo has no committed per-frame draw instrumentation, and M3 may only
create new files, so this script builds one isolated census player the way
tools/gamecube_draw_trace.py and tools/gamecube_native_trace.py do: copies
of pinned sources are patched under local/ (never the vendor tree or the
production runner) and relinked. The player carries two observers:

* the pinned callback probe (native/diagnostics/native_callback_trace.h via
  the scheduler namespace, so gamecube_schedule_check.py accepts the build
  receipt) for per-callback thread-CPU seconds;
* a per-present draw/vertex hook injected into a copy of the Metal backend
  TU (Draw/DrawIndexed count, PresentBackbuffer emits one row per presented
  frame). A "draw" here is one Metal backend Draw/DrawIndexed call,
  including EFB-copy draws; "vertices" is the call's vertex/index count.

`build-player` compiles the player. `run` executes one bounded course leg
through gamecube_schedule_check.py (640x528, immediate XFB, single core,
callback probe on, screenshots every 10 s) with the draw hook enabled only
while the observer sees the rider past the briefing. `table` ranks legs.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import signal
import statistics
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha
from gamecube_native_trace import DOL_SHA256, HEADER
from paths import workbench_root

# Default for --game; resolved lazily in main() so importing this module
# never requires SSX3_WORKBENCH.
GAME_DEFAULT = None
HOST_LEASE = Path('/tmp/ssx3-host-lease')
LEASE_ID = 'M3'
# Orchestrator sequencing history: legs were once gated on M2's Part 2
# heading; the gate was later lifted (M2 stands down until the census is
# done) and the check retired.
M2_REPORT = ROOT / 'local/research/M2/REPORT.md'
QUIET_LOAD = 3.0
MAX_WAIT_SECONDS = 4 * 3600

# Brief asks for 150 s legs; gamecube_course_check.py enforces a 180-900 s
# bound and M3 may not edit tracked files, so legs run at the tool floor.
CENSUS_SECONDS = 180
SCREENSHOT_SECONDS = 10

# Embedded diagnostic header: written to the player directory at build time,
# compiled into the copied Metal TU only. No tracked file carries it.
M3_HEADER = r'''// M3 census hook: per-present draws/vertices for tools/course_census.py.
// Compiled into an isolated player only; never into the production runner.
#pragma once
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
struct M3CensusState {
  unsigned long draws = 0;
  unsigned long long vertices = 0;
  unsigned long emitted = 0;
  FILE* file = nullptr;
};
inline M3CensusState& M3Census() {
  static M3CensusState state;
  return state;
}
inline const char* M3CensusPath() {
  static const char* path = std::getenv("SSX3_CENSUS_FRAMES");
  return path;
}
inline bool M3CensusEnabled() {
  const char* path = M3CensusPath();
  if (!path || !*path)
    return false;
  std::error_code error;
  return std::filesystem::exists(std::string(path) + ".enable", error);
}
inline void M3CensusDraw(unsigned long vertices) {
  if (!M3CensusPath())
    return;
  M3CensusState& state = M3Census();
  state.draws += 1;
  state.vertices += vertices;
}
// One row per presented frame while enabled: seq,draws,vertices. While
// disabled the counters reset without emitting, so menu draws never leak
// into the first riding frame after the enable file appears.
inline void M3CensusPresent() {
  const char* path = M3CensusPath();
  if (!path || !*path)
    return;
  M3CensusState& state = M3Census();
  if (!M3CensusEnabled()) {
    state.draws = 0;
    state.vertices = 0;
    return;
  }
  if (!state.file) {
    state.file = std::fopen(path, "wx");
    if (!state.file)
      return;
  }
  std::fprintf(state.file, "%lu,%lu,%llu\n", state.emitted, state.draws,
               state.vertices);
  state.emitted += 1;
  if ((state.emitted & 63) == 0)
    std::fflush(state.file);
  state.draws = 0;
  state.vertices = 0;
}
'''


def parse_frame_file(text):
    """Parse emitted frame rows; returns (rows, skipped)."""
    rows, skipped = [], 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) != 3:
            skipped += 1
            continue
        try:
            rows.append((int(parts[0]), int(parts[1]), int(parts[2])))
        except ValueError:
            skipped += 1
    return rows, skipped


def frame_spans(rows):
    """Group rows into spans of contiguous seq numbers."""
    spans, current = [], []
    for row in rows:
        if current and row[0] != current[-1][0] + 1:
            spans.append(current)
            current = []
        current.append(row)
    if current:
        spans.append(current)
    return spans


def trim_span(span, margin=2):
    """Drop margin frames at each span edge (enable-toggle latency)."""
    if len(span) <= 2 * margin:
        return []
    return span[margin:-margin]


def median_p95(values):
    """Median and p95 (repo convention: sorted[int(.95*(n-1))])."""
    ordered = sorted(values)
    if not ordered:
        return None, None
    return (statistics.median(ordered),
            ordered[int(0.95 * (len(ordered) - 1))])


def complete_render(row):
    return (row.get('event') == 'render' and (row.get('result', 0) & 255) and
            row.get('view_matrix_calls', 0) > 0 and
            row.get('frame_end_calls', 0) > 0)


def probe_cpu(row):
    try:
        value = float(row.get('cpu_duration_ms'))
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


def probe_riding_stats(rows):
    """Update/render thread-CPU over riding callbacks (state_before == 0).

    Riding follows the movie A/B definition: non-repeat callbacks with the
    rider present and unchanged. Render rows must additionally be complete
    draws, so repeated or empty callbacks never enter the median.
    """
    groups = {'update': [], 'render': []}
    for row in rows:
        if row.get('event') not in groups or row.get('repeat'):
            continue
        if not row.get('rider') or not row.get('same_rider'):
            continue
        if row.get('state_before') != 0:
            continue
        if row['event'] == 'render' and not complete_render(row):
            continue
        cpu = probe_cpu(row)
        if cpu is not None:
            groups[row['event']].append(cpu)
    result = {}
    for name, values in groups.items():
        median, _ = median_p95(values)
        result[f'{name}_n'] = len(values)
        result[f'{name}_cpu_ms_median'] = median
    return result


def frame_stats(rows, margin=2):
    """Draw/vertex median+p95 over trimmed enabled spans."""
    kept = []
    for span in frame_spans(rows):
        kept.extend(trim_span(span, margin))
    draws = [r[1] for r in kept]
    verts = [r[2] for r in kept]
    draws_median, draws_p95 = median_p95(draws)
    verts_median, verts_p95 = median_p95(verts)
    return dict(frames_n=len(kept), spans_n=len(frame_spans(rows)),
                draws_median=draws_median, draws_p95=draws_p95,
                vertices_median=verts_median, vertices_p95=verts_p95)


def manifest_code(text):
    """Read the SDB location code out of a redirect manifest."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('code'):
            _, _, value = stripped.partition('=')
            return value.strip()
    return None


def rank_key(entry):
    """Heaviest first; courses without numbers sort last (never picked)."""
    render = entry.get('render_cpu_ms_median')
    draws = entry.get('draws_p95')
    return ((render is None, -(render or 0)),
            (draws is None, -(draws or 0)))


def rank_rows(entries):
    return sorted(entries, key=rank_key)


def check_game(game):
    game = Path(game)
    if (game / 'sys/boot.bin').read_bytes()[:6] != b'GXBE69':
        raise ValueError(f'Not a GXBE69 game directory: {game}')
    digest = sha(game / 'sys/main.dol')
    if digest != DOL_SHA256:
        raise ValueError(f'DOL sha mismatch: {digest}')
    return game


def patch_probe_source(out):
    """Copy the pinned run-loop TU with the scheduler-namespaced probe step."""
    original = (VENDOR / 'vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp' /
                'StaticRecompCore_Run.cpp')
    source = original.read_text()
    includes = 'namespace\n{'
    dispatch = '          const u32 runtime_dispatch_address = m_guest.pc;'
    for marker in (includes, dispatch):
        if source.count(marker) != 1:
            raise ValueError(f'Native diagnostic injection point changed: {marker!r}')
    for name in (HEADER.name, 'callback_timing.h', 'render_deadline.h',
                 'native_render_schedule.h'):
        (out / name).write_bytes((ROOT / 'native/diagnostics' / name).read_bytes())
    source = source.replace(
        includes,
        f'#include "{out / HEADER.name}"\n'
        f'#include "{out / "native_render_schedule.h"}"\n' + includes)
    source = source.replace(dispatch,
                            '          NativeSchedule::Step(m_guest);\n' + dispatch)
    copy = out / 'Core_Run.cpp'
    copy.write_text(source)
    return original


def patch_metal_source(out):
    """Copy the Metal backend TU with the census draw/present hook."""
    original = (VENDOR / 'vendor/dolphin/Source/Core/VideoBackends/Metal/MTLGfx.mm')
    source = original.read_text()
    header_copy = out / 'm3_census.h'
    header_copy.write_text(M3_HEADER)
    anchor = '#include "VideoCommon/Present.h"'
    if source.count(anchor) != 1:
        raise ValueError(f'Metal injection anchor changed: {anchor!r}')
    source = source.replace(anchor, anchor + f'\n#include "{header_copy}"')
    patches = [
        ('g_state_tracker->Draw(base_vertex, num_vertices);',
         'M3CensusDraw((unsigned long)num_vertices);\n    g_state_tracker->Draw(base_vertex, num_vertices);'),
        ('g_state_tracker->DrawIndexed(base_index, num_indices, base_vertex);',
         'M3CensusDraw((unsigned long)num_indices);\n    g_state_tracker->DrawIndexed(base_index, num_indices, base_vertex);'),
        ('g_state_tracker->EndRenderPass();',
         'M3CensusPresent();\n    g_state_tracker->EndRenderPass();'),
    ]
    for marker, replacement in patches:
        if source.count(marker) != 1:
            raise ValueError(f'Metal injection point changed: {marker!r}')
        source = source.replace(marker, replacement)
    copy = out / 'MTLGfx.mm'
    copy.write_text(source)
    return original


def build_player(args):
    game = check_game(args.game)
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'local'):
        raise ValueError('Diagnostic outputs must remain under local/')
    out.mkdir(parents=True, exist_ok=False)
    production = BUILD / 'moderngekko-run'
    receipt = dict(schema=1, census=1, game=str(game), dol_sha256=DOL_SHA256,
                   probe_source_sha256=None, metal_source_sha256=None,
                   probe_header_sha256=sha(HEADER),
                   callback_timing_sha256=sha(ROOT / 'native/diagnostics/callback_timing.h'),
                   scheduler_headers={},
                   production_runner_sha256=sha(production), commands=[])
    for name in ('render_deadline.h', 'native_render_schedule.h'):
        receipt['scheduler_headers'][name] = sha(ROOT / 'native/diagnostics' / name)
    run_original = patch_probe_source(out)
    receipt['probe_source_sha256'] = sha(run_original)
    metal_original = patch_metal_source(out)
    receipt['metal_source_sha256'] = sha(metal_original)
    receipt['census_header_sha256'] = sha(out / 'm3_census.h')
    commands = subprocess.check_output(
        [str(ROOT / 'local/tooling/ninja'), '-C', str(BUILD),
         '-t', 'commands', 'moderngekko-run'], text=True).splitlines()

    def run(command):
        receipt['commands'].append(command)
        subprocess.run(command, cwd=BUILD, check=True)

    run(compile_copy(next(c for c in commands
                          if c.endswith('/StaticRecompCore_Run.cpp')),
                     out / 'Core_Run.cpp', out / 'probe.o'))
    run(compile_copy(next(c for c in commands if c.endswith('/MTLGfx.mm')),
                     out / 'MTLGfx.mm', out / 'mtl.o'))
    link = shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link = link[2:link.index('&&', 2)]
    if any(part.endswith('MTLGfx.mm.o') for part in link):
        raise ValueError('Metal backend links by object, not archive; refusing to duplicate it')
    link[link.index('-o') + 1] = str(out / 'player')
    first_archive = next(i for i, part in enumerate(link) if part.endswith('.a'))
    link[first_archive:first_archive] = [str(out / 'probe.o'), str(out / 'mtl.o')]
    run(link)
    if sha(production) != receipt['production_runner_sha256']:
        raise RuntimeError('Production runner changed during diagnostic build')
    receipt['player_sha256'] = sha(out / 'player')
    native_launcher = out / 'run_native.py'
    native_launcher.write_text(
        'import sys\nfrom pathlib import Path\n'
        f'ROOT=Path({str(ROOT)!r})\n'
        "sys.path.insert(0,str(ROOT/'tools'))\n"
        'import native_gamecube as native\n'
        'original=native.executable\n'
        f'player=Path({str(out / "player")!r})\n'
        "native.executable=lambda name: player if name=='moderngekko-run' else original(name)\n"
        'native.main()\n')
    course_launcher = out / 'course_check.py'
    course_launcher.write_text(
        'import sys\nfrom pathlib import Path\n'
        f'ROOT=Path({str(ROOT)!r})\n'
        "sys.path.insert(0,str(ROOT/'tools'))\n"
        'import gamecube_course_check as course\n'
        'original=course.subprocess.Popen\n'
        'def launch(args,*pos,**kw):\n'
        ' args=list(args)\n'
        " target=str(ROOT/'tools/native_gamecube.py')\n"
        f' if target in args: args[args.index(target)]={str(native_launcher)!r}\n'
        ' return original(args,*pos,**kw)\n'
        'course.subprocess.Popen=launch\n'
        'course.main()\n')
    receipt['launchers'] = {p.name: sha(p) for p in (native_launcher, course_launcher)}
    (out / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(out / 'player')


def foreign_emulators():
    """Process lines suggesting a Mac emulator run outside this process.

    The orchestrator's monitor shells quote the same patterns in their own
    command lines; those scaffolding lines are not foreign runs. Device
    trials (android_trial.py, thermal-wait.sh) run the emulator on the Odin
    over adb; their Mac-side shells are orchestration, not host load, so
    only the load gate judges them. Isolated players are named `player`,
    which carries no `moderngekko` string, so both patterns are matched.
    """
    try:
        out = subprocess.run(['pgrep', '-fl', 'moderngekko|/player( |$)'],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ['pgrep failed']
    lines = []
    for line in out.stdout.splitlines():
        if any(tag in line for tag in ('muse_mon', 'snapshot-zsh', 'course_census',
                                       'sleep 1200', 'pgrep -fl', 'android_trial',
                                       'thermal-wait.sh', 'adb -s ')):
            continue
        lines.append(line)
    return lines


def quiet_blockers():
    blockers = []
    try:
        load = os.getloadavg()[0]
        if load >= QUIET_LOAD:
            blockers.append(f'1-minute load {load:.2f} >= {QUIET_LOAD}')
    except OSError as error:
        blockers.append(f'load unavailable: {error}')
    # Substring match on the process name (not -f: monitor shells quote the
    # same words in their command lines). This catches clang++ too.
    for name in ('ninja', 'cmake', 'clang'):
        try:
            found = subprocess.run(['pgrep', name],
                                   capture_output=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            blockers.append(f'{name} check failed')
            continue
        if found.returncode == 0:
            blockers.append(f'{name} running')
    blockers.extend(f'emulator: {line}' for line in foreign_emulators())
    if HOST_LEASE.exists():
        try:
            owner = HOST_LEASE.read_text().strip()
        except OSError:
            owner = 'unreadable'
        if LEASE_ID not in owner:
            blockers.append(f'host lease held by {owner!r}')
    return blockers


def light_blockers():
    """Back-to-back gate while the M3 lease is already held.

    Orchestrator steer: legs 2+ run back to back on the held lease while an
    M1d -j4 desktop build may run concurrently (accepted for census
    ranking). Only a foreign Mac emulator executable blocks; shells that
    merely quote a target name (cmake --build ... --target moderngekko-run)
    do not. Load and compilers are recorded, not gated.
    """
    try:
        out = subprocess.run(['pgrep', '-fl', 'moderngekko|/player( |$)'],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ['pgrep failed']
    blockers = []
    for line in out.stdout.splitlines():
        if any(tag in line for tag in ('muse_mon', 'snapshot-zsh', 'course_census',
                                       'sleep 1200', 'pgrep -fl', 'android_trial',
                                       'thermal-wait.sh', 'adb -s ')):
            continue
        pid = line.split(None, 1)[0]
        try:
            comm = subprocess.run(['ps', '-o', 'comm=', '-p', pid],
                                  capture_output=True, text=True,
                                  timeout=10).stdout.strip().split('/')[-1]
        except (OSError, subprocess.TimeoutExpired):
            comm = ''
        if comm in ('player', 'moderngekko-run'):
            blockers.append(f'emulator: {line}')
    return blockers


def wait_for_quiet(waits, purpose, strict=True):
    """Wait for a quiet host; every wait is recorded, never silent."""
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while True:
        blockers = quiet_blockers() if strict else light_blockers()
        if not blockers:
            return
        event = dict(t=time.time(), purpose=purpose, strict=strict,
                     waiting_on=blockers)
        waits.append(event)
        print(f'[m3] waiting ({purpose}): {"; ".join(blockers)}', flush=True)
        if time.monotonic() > deadline:
            raise RuntimeError(f'Host never quiet for {purpose}: {blockers[-1]}')
        time.sleep(30)


def check_player(directory):
    """Verify the census player against its build receipt."""
    directory = Path(directory).resolve()
    if not directory.is_relative_to(ROOT / 'local'):
        raise ValueError('Use an isolated diagnostic player under local/')
    receipt = json.loads((directory / 'build.json').read_text())
    if not receipt.get('census') or not receipt.get('scheduler_headers'):
        raise ValueError('Not a census player receipt')
    for name, expected in [('player', receipt.get('player_sha256')),
                           ('run_native.py', (receipt.get('launchers') or {}).get('run_native.py'))]:
        if not expected or sha(directory / name) != expected:
            raise ValueError(f'Player {name} does not match its build receipt')
    return receipt


def enable_watch(rows_path, enable_path, log_path, stop):
    """Toggle the draw hook while the rider is past the briefing.

    The observer writes rider.jsonl live at a few Hz. Menus (everything up
    to and including briefing state 6) stay disabled; stale samples fail
    closed. Toggles are logged; analysis additionally trims span edges.
    """
    seen_briefing, enabled, offset = False, False, 0
    with log_path.open('w') as log:
        while not stop.is_set():
            try:
                with open(rows_path) as stream:
                    stream.seek(offset)
                    lines = stream.readlines()
                    offset = stream.tell()
                latest = None
                for line in lines:
                    try:
                        latest = json.loads(line)
                    except ValueError:
                        continue
                    if latest.get('state') == 6:
                        seen_briefing = True
                want = (seen_briefing and latest is not None and
                        time.time() - latest.get('wall_time', 0) < 3 and
                        latest.get('state') in range(10) and
                        latest.get('state') != 6)
            except OSError:
                want = False
            if want != enabled:
                enabled = want
                try:
                    if enabled:
                        enable_path.touch()
                    else:
                        enable_path.unlink(missing_ok=True)
                    log.write(json.dumps(dict(t=time.time(), enabled=enabled)) + '\n')
                    log.flush()
                except OSError:
                    pass
            stop.wait(0.5)
        try:
            enable_path.unlink(missing_ok=True)
        except OSError:
            pass


def reap_player(player):
    """SIGTERM then SIGKILL any leftover process running this player binary.

    The checker stops its direct children, but the player is a grandchild
    (via run_native.py): if the middle process dies first, the player is
    orphaned and keeps emulating. Match the full player path so sibling
    agents' players are never signalled.
    """
    me = os.getpid()
    try:
        out = subprocess.run(['pgrep', '-f', str(Path(player) / 'player')],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return []
    reaped = []
    targets = []
    for line in out.stdout.splitlines():
        try:
            pid = int(line.strip())
        except ValueError:
            continue
        if pid != me:
            targets.append(pid)
    for pid in targets:
        try:
            os.kill(pid, signal.SIGTERM)
            reaped.append(pid)
        except OSError:
            continue
    deadline = time.monotonic() + 10
    while targets and time.monotonic() < deadline:
        time.sleep(1)
        alive = []
        for pid in targets:
            try:
                os.kill(pid, 0)
                alive.append(pid)
            except OSError:
                continue
        targets = alive
    for pid in targets:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            continue
    return reaped


def run_leg(args):
    import gamecube_schedule_check as schedule
    game = check_game(args.game)
    manifest = Path(args.manifest).resolve()
    manifest_text = manifest.read_text()
    player = Path(args.player_dir).resolve()
    receipt = check_player(player)
    output = Path(args.output)
    if output.exists():
        raise ValueError(f'Preserving existing output {output}; choose a fresh path')
    waits = []
    # Reap any residue of my own player first (a killed leg's orphan would
    # otherwise trip the emulator gate forever); only this player path is
    # ever signalled.
    try:
        stale = reap_player(player)
    except Exception:  # noqa: BLE001 - best effort before the waits
        stale = []
    # First leg of a sequence takes the lease under the full gate;
    # back-to-back legs on the held lease use the light gate and record
    # the host state instead (a concurrent M1d build is accepted). The
    # take is re-checked so a reclaim between the last poll and the write
    # waits again instead of overwriting a foreign lease.
    while True:
        try:
            held = LEASE_ID in HOST_LEASE.read_text()
        except OSError:
            held = False
        wait_for_quiet(waits, f'census {args.profile}', strict=not held)
        try:
            claimed = LEASE_ID in HOST_LEASE.read_text()
            foreign = HOST_LEASE.exists() and not claimed
        except OSError:
            claimed, foreign = False, False
        if foreign:
            continue
        try:
            HOST_LEASE.write_text(f'{LEASE_ID} pid={os.getpid()}\n')
        except OSError as error:
            raise RuntimeError(f'Cannot take host lease: {error}')
        break
    try:
        load_at_start = list(os.getloadavg())
    except OSError:
        load_at_start = None
    probe_path = output.resolve() / 'probe.jsonl'
    frames_path = output.resolve() / 'frames.csv'
    enable_path = Path(str(frames_path) + '.enable')
    result = dict(schema=1, census=1, profile=args.profile,
                  game=str(game), manifest=str(manifest),
                  manifest_sha256=sha(manifest),
                  manifest_code=manifest_code(manifest_text),
                  player=str(player), player_sha256=receipt['player_sha256'],
                  production_runner_sha256=receipt['production_runner_sha256'],
                  seconds=args.seconds, resolution='640x528', immediate_xfb=True,
                  cpu_thread=False, metal_validation='off',
                  load_at_start=load_at_start, stale_reaped=stale,
                  rerun=bool(args.rerun),
                  deviations=['legs run 180 s (tool floor) instead of the brief 150 s',
                              'Metal validation off for timing (orchestrator steer)'],
                  waits=waits)
    stop = threading.Event()
    code, error = 0, None
    started_wall = time.time()
    # The enable log must not live inside the course output: the checker
    # requires a fresh directory and owns everything under it.
    enable_log = output.resolve().parent / f'{output.name}.enable.log'
    watcher = threading.Thread(target=enable_watch,
                               args=(output.resolve() / 'rider.jsonl',
                                     enable_path, enable_log, stop),
                               daemon=True)
    old_argv, old_environ = sys.argv, dict(os.environ)
    env = dict(os.environ, SSX_NATIVE_PROBE=str(probe_path),
               SSX3_CENSUS_FRAMES=str(frames_path))
    env.pop('SSX_NATIVE_SCHEDULE', None)
    sys.argv = ['gamecube_schedule_check.py', '--player-dir', str(player),
                '--immediate-xfb', '--resolution', '640x528',
                '--game', str(game), '--profile', args.profile,
                '--output', str(output.resolve()), '--seconds', str(args.seconds),
                '--metal-validation', 'off',
                '--screenshot-seconds', str(SCREENSHOT_SECONDS),
                '--course-manifest', str(manifest)]
    watcher.start()
    try:
        os.environ.clear()
        os.environ.update(env)
        try:
            schedule.main()
        except SystemExit as done:
            code = done.code or 0
    except Exception as failed:  # noqa: BLE001 - legs report, never crash the loop
        error = f'{type(failed).__name__}: {failed}'
        code = 1
    finally:
        stop.set()
        watcher.join(timeout=10)
        sys.argv = old_argv
        os.environ.clear()
        os.environ.update(old_environ)
        try:
            result['reaped_players'] = reap_player(player)
        except Exception as reap_error:  # noqa: BLE001 - recorded, never fatal
            result['reap_error'] = str(reap_error)
        # Orchestrator steer: back-to-back legs keep the lease; only the
        # driver releases it when step 2 is complete.
        result['kept_lease'] = bool(args.keep_lease)
        if not args.keep_lease:
            try:
                HOST_LEASE.unlink(missing_ok=True)
            except OSError:
                pass
    result.update(wall_seconds=time.time() - started_wall, exit_code=code,
                  error=error)
    if output.exists():
        try:
            observations = json.loads((output / 'observations.json').read_text())
        except (OSError, ValueError):
            observations = None
        result['observations'] = observations
        result['riding_observed'] = bool(
            observations and observations.get('riding_observed_after_start'))
        shots_dir = ROOT / 'local/native/profiles' / args.profile / 'ScreenShots'
        profile_shots = sorted(shots_dir.rglob('*.png')) if shots_dir.exists() else []
        result['screenshots'] = [p.name for p in profile_shots]
        try:
            probe_rows = [json.loads(line) for line in
                          probe_path.read_text().splitlines() if line.strip()]
        except OSError:
            probe_rows = []
        result['probe_rows'] = len(probe_rows)
        result['probe_sha256'] = sha(probe_path) if probe_path.exists() else None
        result.update(probe_riding_stats(probe_rows))
        try:
            frame_text = frames_path.read_text() if frames_path.exists() else ''
        except OSError:
            frame_text = ''
        frame_rows, skipped = parse_frame_file(frame_text)
        result['frame_rows'] = len(frame_rows)
        result['frame_rows_skipped'] = skipped
        result['frames_sha256'] = sha(frames_path) if frames_path.exists() else None
        result.update(frame_stats(frame_rows))
        result['rode'] = bool(result['riding_observed'] and
                              (result.get('render_n') or 0) > 0 and
                              (result.get('frames_n') or 0) > 0)
        try:
            (output / 'census.json').write_text(json.dumps(result, indent=2) + '\n')
        except OSError as write_error:
            result['census_write_error'] = str(write_error)
    print(json.dumps({k: result.get(k) for k in
                      ('profile', 'manifest_code', 'exit_code', 'error', 'rode',
                       'riding_observed', 'update_cpu_ms_median',
                       'render_cpu_ms_median', 'draws_median', 'draws_p95',
                       'vertices_median', 'vertices_p95', 'frames_n')}, indent=2))
    return 1 if code or error else 0


def table(args):
    entries = []
    for path in args.census:
        data = json.loads((Path(path).resolve() / 'census.json').read_text())
        entries.append(data)
    ranked = rank_rows(entries)
    lines = ['| course | code | rode | render CPU med ms | draws p95 | verts p95 | '
             'update CPU med ms | frames |',
             '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for entry in ranked:
        def show(value):
            return 'n/a' if value is None else f'{value:.2f}'
        lines.append(
            f"| {entry.get('profile')} | {entry.get('manifest_code')} | "
            f"{'yes' if entry.get('rode') else 'NO'} | "
            f"{show(entry.get('render_cpu_ms_median'))} | "
            f"{show(entry.get('draws_p95'))} | {show(entry.get('vertices_p95'))} | "
            f"{show(entry.get('update_cpu_ms_median'))} | {entry.get('frames_n')} |")
    report = '\n'.join(lines) + '\n'
    print(report)
    riders = [e for e in ranked if e.get('rode')]
    pick = riders[0] if riders else None
    print(f"heaviest that rides: {pick['profile'] if pick else 'NONE'}")
    if args.output:
        out = Path(args.output)
        out.write_text(json.dumps(dict(ranked=[e['profile'] for e in ranked],
                                       pick=pick['profile'] if pick else None,
                                       entries=ranked), indent=2) + '\n')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build-player')
    p.add_argument('--game', type=Path, default=GAME_DEFAULT,
                   help='Extracted game dir (default: $SSX3_WORKBENCH/native/GXBE69)')
    p.add_argument('--output', type=Path, required=True)
    p.set_defaults(fn=build_player)
    p = sub.add_parser('run')
    p.add_argument('--game', type=Path, default=GAME_DEFAULT,
                   help='Extracted game dir (default: $SSX3_WORKBENCH/native/GXBE69)')
    p.add_argument('--player-dir', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--profile', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=CENSUS_SECONDS)
    p.add_argument('--keep-lease', action='store_true',
                   help='Keep the host lease after the leg for a back-to-back sequence')
    p.add_argument('--rerun', action='store_true',
                   help='Mark this leg as a rerun (post-restore repeat)')
    p.set_defaults(fn=run_leg)
    p = sub.add_parser('table')
    p.add_argument('census', nargs='+', type=Path)
    p.add_argument('--output', type=Path)
    p.set_defaults(fn=table)
    args = parser.parse_args()
    if args.command in ('build-player', 'run') and args.game is None:
        args.game = workbench_root() / 'native/GXBE69'
    if getattr(args, 'seconds', CENSUS_SECONDS) != CENSUS_SECONDS:
        parser.error(f'Legs run at the {CENSUS_SECONDS} s tool floor')
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
