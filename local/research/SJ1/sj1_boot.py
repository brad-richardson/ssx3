#!/usr/bin/env python3
"""SJ1 bounded boot: full Happiness race (R1) and Snow Jam re-test (R2).

Mac, paraLLEl + PGS_HIER_BINNING=force, PS2X_SOUND=1, empty mc0,
PS2X_SKIP_MOVIE=1 (dev-only), vsync pad clock, one mini slot each.

Routes (guest ms, PS2X_PAD_SCRIPT_CLOCK=vsync):
  r1  I26-FAST to the Happiness race, then X-tap every 10 s guest with
      down-tuck held between taps (X is ignored while down is held, so
      each tap gets a 250 ms down-free window), out to ~358 s guest.
  r2  Same minus the two Select-Event downs (Snow Jam is the default),
      so cross@22306 confirms Snow Jam.

Env: PS2X_DETERMINISTIC=1, PS2X_VSYNC_RATE_LOG=1 (tick source),
PS2X_FRAME_DUMP_DIR (upload-latest pair) + 20 s snapshotter,
PS2X_COVERAGE_TICK, PS2X_MISSING_FUNCTION_POLICY=stop; R2 adds
PS2X_CD_READ_TRACE. A STOP file in the run dir ends the boot cleanly
(bound=stop_file) so the worker can stop on observed end states.

Usage: sj1_boot.py --route r1|r2 --runner PATH --label NAME --wall SEC
       --coverage-tick N [--cd-trace] [--stop-tick N]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release  # noqa: E402

WORK = Path('/Users/brad/dev/ssx3-work/SJ1')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
VULKAN_LIB = '/opt/homebrew/lib/libvulkan.1.dylib'

# I26-FAST menu prefix + Rival-card taps (local/research/I26/ROUTES.md).
MENU_PREFIX = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
               '18336:cross:250,19770:cross:250,')
MENU_DOWNS = '21205:down:150,21706:down:150,'  # Snow Jam -> Metro-City -> Happiness
MENU_SUFFIX = ('22306:cross:250,24025:cross:250,'
               '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,'
               '30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,'
               '32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,'
               '34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,'
               '36520:cross:200,36771:down:700,37521:cross:200,37772:down:700')


def race_tail():
    # X tap every 10 s guest (RECOVER/jump), down-tuck otherwise, to ~358 s.
    parts = []
    for k in range(32):
        t = 38522 + k * 10000
        parts.append('%d:cross:200' % t)
        parts.append('%d:down:9750' % (t + 250))
    return ',' + ','.join(parts)


ROUTE_R1 = MENU_PREFIX + MENU_DOWNS + MENU_SUFFIX + race_tail()
ROUTE_R2 = MENU_PREFIX + MENU_SUFFIX + race_tail()
# Spare-run control: I26-FAST verbatim (30 s tuck, then no input at all).
ROUTE_R1B = MENU_PREFIX + MENU_DOWNS + MENU_SUFFIX + ',38522:down:30000'

PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 1 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 20
POLL_S = 1.0

RATE_TICK = re.compile(rb'\[vsync-rate\] tick=(\d+)\b')
GS_PATH = re.compile(r'^\[gs-path\].*$', re.M)
GS_FATAL = re.compile(r'^\[gs:parallel\] FATAL.*$', re.M)
COVERAGE = re.compile(r'^\[coverage:[^\]]*\].*$', re.M)
SND_OUT = re.compile(r'^\[snd-output\].*$', re.M)
PAD_ARMED = re.compile(r'^\[padscript\] armed.*$', re.M)


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def dir_bytes(path):
    total = 0
    for root, _ds, fs in os.walk(path):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--route', choices=('r1', 'r2', 'r1b'), required=True)
    ap.add_argument('--runner', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--wall', type=int, required=True)
    ap.add_argument('--coverage-tick', type=int, required=True)
    ap.add_argument('--cd-trace', action='store_true')
    ap.add_argument('--stop-tick', type=int, default=10 ** 9)
    args = ap.parse_args()

    route = {'r1': ROUTE_R1, 'r2': ROUTE_R2, 'r1b': ROUTE_R1B}[args.route]
    runner = Path(args.runner).resolve()
    lane = WORK / 'run' / args.label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    (lane / 'mc0').mkdir()
    (lane / 'mc1').mkdir()
    frames_dir = lane / 'frames'
    snap_dir = frames_dir / 'snap'
    snap_dir.mkdir(parents=True)
    log = lane / 'boot.log'
    stop_file = lane / 'STOP'

    pins = {str(ISO): ISO_SHA, str(ELF): ELF_SHA, str(CODEGEN): CODEGEN_SHA}
    big = [runner, ISO, ELF, CODEGEN]
    reads = [{str(p): sha_of(p) for p in big} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    for path, want in pins.items():
        if reads[0][path] != want:
            raise SystemExit('SHA mismatch for %s' % path)
    if not os.path.exists(VULKAN_LIB):
        raise SystemExit('missing %s' % VULKAN_LIB)

    env = {k: v for k, v in os.environ.items() if not k.startswith('PS2X_')}
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=route,
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               PS2X_GS_BACKEND='parallel', GRANITE_VULKAN_LIBRARY=VULKAN_LIB,
               PGS_HIER_BINNING='force', PS2X_VSYNC_RATE_LOG='1',
               PS2X_FRAME_DUMP_DIR=str(frames_dir),
               PS2X_COVERAGE_TICK=str(args.coverage_tick), PS2X_SOUND='1',
               COPYFILE_DISABLE='1')
    if args.cd_trace:
        env['PS2X_CD_READ_TRACE'] = str(lane / 'cdread.log')

    slot = claim('SJ1-' + args.label, exclusive=False)
    while slot is None:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('SJ1-' + args.label, exclusive=False)

    result = {'label': args.label, 'route': args.route,
              'runner': str(runner), 'sha_reads': reads,
              'stop_tick': args.stop_tick, 'wall_cap': args.wall,
              'coverage_tick': args.coverage_tick, 'cd_trace': args.cd_trace,
              'slot': slot, 'exclusive': False,
              'env': {k: v for k, v in env.items()
                      if k.startswith('PS2X_') or k.startswith('GRANITE_')
                      or k.startswith('PGS_')},
              'load_start': os.getloadavg()}
    proc = None
    stop_snap = threading.Event()
    shared = {'tick': 0}
    trace_path = lane / 'trace.jsonl'

    def snapshotter(t0):
        latest = frames_dir / 'upload-latest.png'
        latest_txt = frames_dir / 'upload-latest.txt'
        while not stop_snap.wait(SNAP_PERIOD_S):
            el = time.monotonic() - t0
            try:
                if latest.exists():
                    shutil.copyfile(latest, snap_dir / ('snap-%06dt-%07.2fs.png'
                                                        % (shared['tick'], el)))
                if latest_txt.exists():
                    shutil.copyfile(latest_txt, snap_dir / ('snap-%06dt-%07.2fs.txt'
                                                            % (shared['tick'], el)))
            except OSError:
                pass

    try:
        t0 = time.monotonic()
        trace = trace_path.open('w')
        with log.open('wb') as out:
            proc = subprocess.Popen([str(runner), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label, 'pid': proc.pid,
                              'slot': slot}), flush=True)
            th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
            th.start()
            last_tick, last_progress, bound = 0, t0, None
            try:
                while True:
                    now = time.monotonic()
                    if proc.poll() is not None:
                        bound = 'exit'
                        break
                    if now - t0 >= args.wall:
                        bound = 'wall_cap'
                        break
                    if stop_file.exists():
                        bound = 'stop_file'
                        time.sleep(3)  # let the snapshotter grab final frames
                        break
                    if log.stat().st_size > LOG_CAP_BYTES:
                        bound = 'log_cap'
                        break
                    if dir_bytes(frames_dir) > FRAMES_CAP_BYTES:
                        bound = 'frames_cap'
                        break
                    tail = log.read_bytes()[-65536:]
                    m = RATE_TICK.findall(tail)
                    if m and int(m[-1]) > last_tick:
                        last_tick = int(m[-1])
                        last_progress = now
                        shared['tick'] = last_tick
                    trace.write(json.dumps({'wall_s': round(now - t0, 3),
                                            'tick': last_tick}) + '\n')
                    trace.flush()
                    if now - last_progress >= PROGRESS_CAP_S:
                        bound = 'progress_cap'
                        break
                    if last_tick >= args.stop_tick:
                        bound = 'target'
                        time.sleep(3)
                        break
                    time.sleep(POLL_S)
            finally:
                stop_snap.set()
                th.join(timeout=10)
            if proc.poll() is None:
                proc.terminate()
                try:
                    result['runner_rc'] = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    result['runner_rc'] = proc.wait(timeout=10)
                    bound += '+kill'
            else:
                result['runner_rc'] = proc.returncode
        trace.close()
        text = log.read_text(errors='replace')
        gs_path = GS_PATH.findall(text)
        gs_fatal = GS_FATAL.findall(text)
        cov = COVERAGE.findall(text)
        snd = SND_OUT.findall(text)
        armed = PAD_ARMED.findall(text)
        cd_lines = None
        if args.cd_trace and (lane / 'cdread.log').exists():
            with open(lane / 'cdread.log', errors='replace') as f:
                cd_lines = sum(1 for _ in f)
        result.update(bound=bound, elapsed_s=round(time.monotonic() - t0, 3),
                      last_tick=last_tick, log_bytes=log.stat().st_size,
                      gs_path_line=gs_path[0] if gs_path else None,
                      gs_fatal=gs_fatal[0] if gs_fatal else None,
                      coverage_lines=cov if cov else None,
                      snd_output=snd if snd else None,
                      pad_armed=armed[0] if armed else None,
                      cd_trace_lines=cd_lines,
                      load_end=os.getloadavg())
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ('env', 'sha_reads')}), flush=True)
        return 0 if bound in ('target', 'stop_file') else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        release(slot)


if __name__ == '__main__':
    sys.exit(main())
