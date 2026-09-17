#!/usr/bin/env python3
"""Build an isolated native callback observer or summarize its JSONL events.

Research only. SSX_NATIVE_PROBE must name a new JSONL output file. Explicitly
setting SSX_NATIVE_DOUBLE_RENDER=1 attempts at most 120 extra renderer calls
after 140 host seconds while riding. Readiness gates remain intact; an attempted
call is not evidence of drawing or displaying another frame.

Experimental flags (unset to disable): SSX_NATIVE_DOUBLE_UPDATE=1 re-enters the
application update once per ordinary update in the window (same dt, same render
rate: a 2x-update workload probe, not a timestep change); SSX_NATIVE_HALF_CADENCE=1
skips every other application update in the window (same dt, same render rate:
a half-cadence wrong-control probe; with DOUBLE_UPDATE also set this is the
time-normalized 30 Hz mode, 60 executions per guest second in pairs);
SSX_NATIVE_HALF_DT=1 one-shot rewrites dt constants in guest RAM on window
entry (1/60 to 1/120, render divisor 60.0 to 120.0; with DOUBLE_UPDATE this
is the 120 Hz candidate v0); SSX_NATIVE_WAIT_REPEAT retries rejected
extra calls with bounded guest polling; SSX_NATIVE_SKIP_BOOKKEEPING omits two
timing helpers on extras; SSX_NATIVE_CAMERA_OFFSET offsets a copied graphics
matrix; SSX_NATIVE_FROZEN_VIEW_SWEEP holds one state for normal/offset/restored
phases; SSX_NATIVE_CAPTURE requests screenshots. SSX_NATIVE_GUEST_WINDOW=1
replaces the host-clock window with guest-timed edges (arms on the first
stable update that moves the rider, engages SSX_NATIVE_WINDOW_SKIP ticks
later, repeats start the next tick, consts restore after
SSX_NATIVE_WINDOW_TICKS doubled ticks; SSX_NATIVE_SPEED_GATE re-arms the
v2 0x8002DE04 skip; SSX_NATIVE_WATCH_OFFS logs in-window rider-word
changers; SSX_NATIVE_COUNTER_RESTORE saves/restores the race tick counter
across repeats; SSX_NATIVE_INTERLEAVE_RENDER draws once between the two
update halves of each doubled tick, cap 600; SSX_NATIVE_PC_HIST=path
histograms guest pcs per callback class to a separate file;
SSX_NATIVE_QUIET=1 skips per-row Diff/Hash compute for ship-prize
sizing). SSX_NATIVE_SIGNPOSTS=path (with a --signposts player build)
snapshots cumulative per-callback-class entry counts at the 9 hot-chunk
signposts (native/diagnostics/chunk_signposts.h). These are research
controls, not a high-refresh implementation. See docs/research/120hz-render-seam.md.

With build --scheduler, SSX_NATIVE_SCHEDULE enables the independent deadline
experiment during host seconds 140–175. It requires SKIP_BOOKKEEPING and no
DOUBLE/WAIT/SWEEP flags. SSX_NATIVE_COMPLETION_RELEASE uses the
original single guest XFB with uncapped host immediate copies before enabling
the game's graphics-completion mode. Use
gamecube_schedule_check.py and gamecube_schedule_trace.py for this experiment;
see docs/research/120hz-independent-schedule.md for ownership limits.
"""
import argparse
import collections
import json
from pathlib import Path
import shlex
import subprocess

from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha

DOL_SHA256 = 'b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce'
HEADER = ROOT / 'native/diagnostics/native_callback_trace.h'


def build(args):
    game = args.game.resolve()
    if ((game / 'sys/boot.bin').read_bytes()[:6] != b'GXBE69' or
            sha(game / 'sys/main.dol') != DOL_SHA256):
        raise ValueError('Callback addresses require the pinned GXBE69 executable')
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'local'):
        raise ValueError('Diagnostic outputs must remain under local/')
    out.mkdir(parents=True, exist_ok=False)
    original = VENDOR / 'vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
    production = BUILD / 'moderngekko-run'
    receipt = dict(schema=1, dol_sha256=DOL_SHA256, game=str(game),
                   original_source_sha256=sha(original), probe_header_sha256=sha(HEADER),
                   production_runner_sha256=sha(production), commands=[])
    source = original.read_text()
    includes = 'namespace\n{'
    dispatch = '          const u32 runtime_dispatch_address = m_guest.pc;'
    for marker in (includes, dispatch):
        if source.count(marker) != 1:
            raise ValueError(f'Native diagnostic injection point changed: {marker!r}')
    # Snapshot the authored header too, so later edits cannot change a receipt.
    header_copy = out / HEADER.name
    header_copy.write_bytes(HEADER.read_bytes())
    timing = ROOT / 'native/diagnostics/callback_timing.h'
    (out / timing.name).write_bytes(timing.read_bytes())
    receipt['callback_timing_sha256'] = sha(timing)
    if getattr(args, 'signposts', False):
        signposts = ROOT / 'native/diagnostics/chunk_signposts.h'
        (out / signposts.name).write_bytes(signposts.read_bytes())
        receipt['signposts_header_sha256'] = sha(signposts)
    extra_includes = ''
    if getattr(args, 'app_trial_check', False):
        source = '#define SSX_NATIVE_TRIAL_APP 1\n' + source
        control = ROOT/'native/diagnostics/trial_control.h'
        (out/control.name).write_bytes(control.read_bytes())
        receipt['trial_control_sha256'] = sha(control)
    probe_namespace = 'NativeProbe'
    if getattr(args, 'scheduler', False):
        receipt['scheduler_headers'] = {}
        for name in ('render_deadline.h', 'native_render_schedule.h'):
            path = ROOT / 'native/diagnostics' / name
            (out / name).write_bytes(path.read_bytes())
            receipt['scheduler_headers'][name] = sha(path)
        extra_includes = f'#include "{out / "native_render_schedule.h"}"\n'
        probe_namespace = 'NativeSchedule'
        if getattr(args, 'interpolation', False):
            for name in ('pose_history.h', 'native_pose_interpolation.h'):
                path = ROOT / 'native/diagnostics' / name
                (out / name).write_bytes(path.read_bytes())
                receipt['scheduler_headers'][name] = sha(path)
            extra_includes += f'#include "{out / "native_pose_interpolation.h"}"\n'
            probe_namespace = 'NativeInterpolation'
            if getattr(args, 'app_trial_check', False):
                source = '#define SSX_NATIVE_TRIAL_TEST 1\n' + source
                driver = ROOT/'native/diagnostics/trial_test_driver.h'
                (out/driver.name).write_bytes(driver.read_bytes())
                receipt['trial_test_driver_sha256'] = sha(driver)
                extra_includes += f'#include "{out / driver.name}"\n'
                probe_namespace = 'NativeTrialTest'
        if getattr(args, 'replay', False):
            helper = ROOT / 'native/diagnostics/replay_plan.h'
            (out / helper.name).write_bytes(helper.read_bytes())
            receipt['scheduler_headers'][helper.name] = sha(helper)
            receipt['replay_mode'] = 'capture-private-audit-only'
            path = ROOT / 'native/diagnostics/native_frame_replay.h'
            (out / path.name).write_bytes(path.read_bytes())
            receipt['scheduler_headers'][path.name] = sha(path)
            extra_includes += f'#include "{out / path.name}"\n'
            probe_namespace = 'NativeReplay'
    if getattr(args, 'signposts', False):
        extra_includes += f'#include "{out / "chunk_signposts.h"}"\n'
    source = source.replace(includes, f'#include "{header_copy}"\n' + extra_includes + includes)
    step = f'          {probe_namespace}::Step(m_guest);\n'
    if getattr(args, 'signposts', False):
        # After the probe step so signposts observe the final dispatch pc
        # (repeat/skip redirects included), never a pre-redirect one.
        step += '          ChunkSignposts::Step(m_guest);\n'
    source = source.replace(dispatch, step + dispatch)
    copy = out / 'Core_Run.cpp'
    copy.write_text(source)
    commands = subprocess.check_output(
        [str(ROOT / 'local/tooling/ninja'), '-C', str(BUILD), '-t', 'commands', 'moderngekko-run'],
        text=True).splitlines()

    def run(command):
        receipt['commands'].append(command)
        subprocess.run(command, cwd=BUILD, check=True)

    run(compile_copy(next(c for c in commands if c.endswith('/StaticRecompCore_Run.cpp')),
                     copy, out / 'probe.o'))
    link = shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link = link[2:link.index('&&', 2)]
    link[link.index('-o') + 1] = str(out / 'player')
    link.insert(link.index('libmoderngekko.a'), str(out / 'probe.o'))
    if getattr(args, 'presentation_object', None):
        obj = args.presentation_object.resolve()
        if not obj.is_relative_to(ROOT / 'local') or not obj.is_file():
            raise ValueError('Use a locally built presentation observer object under local/')
        receipt['presentation_object_sha256'] = sha(obj)
        link.insert(link.index('libmoderngekko.a'), str(obj))
    run(link)
    if sha(production) != receipt['production_runner_sha256']:
        raise RuntimeError('Production runner changed during diagnostic build')
    receipt['player_sha256'] = sha(out / 'player')
    # Keep the normal course runner's pin checks, fault checks and scratch-profile
    # protection. Only substitute the isolated player in its child launcher.
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


def summarize(rows, after=140, frozen_sequence=False):
    """Keep attempted repeats separate from observed scene-path coverage."""
    result = dict(schema=1, after_host_seconds=after,
                  frozen_sequence=frozen_sequence, groups={})
    for label in ('update', 'render', 'repeat', 'interleave'):
        group = [r for r in rows if r['wall'] > after and r['rider'] and r['same_rider']
                 and (r['repeat'] and not r.get('interleaved') if label == 'repeat' else
                      r['event'] == 'render' and bool(r.get('interleaved')) if label == 'interleave' else
                      r['event'] == label and not r['repeat'])]
        counts = dict(calls=len(group))
        for field in ('position_changed', 'rng_changed', 'view_offsets', 'body_offsets', 'app_offsets'):
            counts[field] = sum(bool(r[field]) for r in group)
        counts['state_changed'] = sum(r['state_before'] != r['state_after'] for r in group)
        counts['view_pointer_changed'] = sum(not r['same_view'] for r in group)
        coverage = bool(group) and all('gate_calls' in r for r in group)
        counts['render_gate_instrumented'] = coverage
        if coverage and label != 'update':
            for field in ('view_matrix_calls', 'frame_end_calls', 'elapsed_calls', 'queue_calls',
                          'gate_calls', 'gate_ready'):
                if all(field in r for r in group):
                    counts[field] = sum(r[field] for r in group)
            counts['results'] = dict(collections.Counter(str(r['result']) for r in group))
        result['groups'][label] = counts
    repeats = [(i, r) for i, r in enumerate(rows) if r['repeat'] and r['event'] == 'render'
               and not r.get('interleaved')]
    interleaves = [r for r in rows if r['event'] == 'render' and r.get('interleaved')]
    result['interleave_renders'] = len(interleaves)
    result['verified_complete_interleave_renders'] = sum(
        1 for r in interleaves if r.get('result', 0) & 255 and
        r.get('view_matrix_calls', 0) > 0 and r.get('frame_end_calls', 0) > 0)
    def paired(i, complete=False):
        current = rows[i]
        if i == 0:
            return False
        first = i - 1
        if frozen_sequence:
            while first > 0 and rows[first]['event'] == 'render' and rows[first]['repeat']:
                first -= 1
        if rows[first]['repeat']:
            return False
        for row in rows[first:i+1]:
            if (row['event'] != 'render' or row['app'] != current['app'] or
                    row['rider'] != current['rider']):
                return False
            if complete and not (row.get('result', 0) & 255 and
                                 row.get('view_matrix_calls', 0) > 0 and
                                 row.get('frame_end_calls', 0) > 0):
                return False
        return True

    result['repeat_pairing_failures'] = sum(not paired(i) for i, _ in repeats)
    result['verified_complete_render_pairs'] = sum(paired(i, complete=True) for i, _ in repeats)
    result['unverified_or_incomplete_render_pairs'] = (
        len(repeats) - result['verified_complete_render_pairs'])
    update_repeats = [(i, r) for i, r in enumerate(rows)
                      if r['repeat'] and r['event'] == 'update']
    def update_paired(i):
        if i == 0:
            return False
        prev, current = rows[i - 1], rows[i]
        return (prev['event'] == 'update' and not prev['repeat'] and
                prev['app'] == current['app'] and prev['rider'] == current['rider'])
    result['update_repeats'] = len(update_repeats)
    result['verified_update_repeats'] = sum(update_paired(i) for i, _ in update_repeats)
    result['skipped_updates'] = sum(1 for r in rows if r['event'] == 'update'
                                    and r.get('skipped_update', 0))
    for label in ('render', 'repeat'):
        group = [r for r in rows if r['wall'] > after and r['rider'] and r['same_rider']
                 and r['event'] == 'render' and bool(r['repeat']) == (label == 'repeat')]
        for field in ('retries', 'skipped_elapsed', 'skipped_queue', 'camera_offsets',
                      'camera_restores'):
            if group and all(field in r for r in group):
                result['groups'][label][field] = sum(r[field] for r in group)
    result['limits'] = ('Scoped entry/return comparisons, not whole-game determinism or a '
                        'presentation count. Dispatch counters must observe ordinary draws '
                        'before absent repeat calls are evidence of a skipped path. Guest '
                        'time and interrupts continue during repeated rendering.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--scheduler', action='store_true',
                   help='Include the opt-in, bounded independent render-schedule experiment')
    p.add_argument('--replay', action='store_true',
                   help='Capture and privately audit a FIFO frame; rendering is blocked (requires --scheduler)')
    p.add_argument('--interpolation', action='store_true',
                   help='Include the bounded native transform interpolation prototype (requires --scheduler)')
    p.add_argument('--app-trial-check', action='store_true',
                   help='Exercise iOS trial cancellation and restart controls in an isolated desktop player')
    p.add_argument('--signposts', action='store_true',
                   help='Count cross-chunk entries at the 9 hot-chunk signposts '
                        '(SSX_NATIVE_SIGNPOSTS=path snapshots the JSON counters)')
    p.add_argument('--presentation-object', type=Path,
                   help='Link an isolated MTLGfx.o built by gamecube_present_trace.py')
    p = sub.add_parser('summarize')
    p.add_argument('trace', type=Path)
    p.add_argument('--after', type=float, default=140)
    p.add_argument('--frozen-sequence', action='store_true',
                   help='Validate a continuous repeat sequence anchored to one completed original render')
    p.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        if args.interpolation and not args.scheduler:
            parser.error('--interpolation requires --scheduler')
        if args.replay and (not args.scheduler or args.interpolation):
            parser.error('--replay requires --scheduler and excludes --interpolation')
        if args.app_trial_check and not args.interpolation:
            parser.error('--app-trial-check requires --interpolation')
        build(args)
    else:
        rows = [json.loads(line) for line in args.trace.read_text().splitlines()]
        result = summarize(rows, args.after, args.frozen_sequence)
        result['trace_sha256'] = sha(args.trace)
        encoded = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.write_text(encoded)
        else:
            print(encoded, end='')


if __name__ == '__main__':
    main()
