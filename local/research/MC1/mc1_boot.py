#!/usr/bin/env python3
"""MC1 bounded boots: memory-card write path on a scratch copy of Brad's save.

Mac, paraLLEl + PGS_HIER_BINNING=force, PS2X_SOUND=1, PS2X_SKIP_MOVIE=1
(dev-only), vsync pad clock, one mini slot each. Runner has RUNTIME_LOGS=ON
so the [MC] HLE log (GetDir/Chdir detail + Sync cmd/result) is visible;
sceMc* are HLE stubs, not numeric syscalls, so PS2X_TRACE_SYSCALLS would
not show them.

Routes (guest ms, PS2X_PAD_SCRIPT_CLOCK=vsync):
  r1seed   FR1-R1 (Happiness, no race inputs) shifted +4438 ms (+266 ticks)
           for the seeded-card title delay, plus 12 post-results crosses
           (every ~150 ticks from ~18300t) to answer save prompts.
  r1empty  FR1-R1 verbatim plus 12 post-results crosses from ~18030t.
  menu     Seeded title->Select Character prefix (start@902t + 2 crosses)
           plus 2 settle crosses; short reload check, no race.

mc0 modes (--mcmode): seed (copy of ~/dev/ssx3-work/MC1/mc0-seed),
empty (fresh dir), readonly (seed copy chmodded a-w after copy).
Before/after SHA+sizes+mtimes of the run mc0 are recorded.

Usage: mc1_boot.py --route r1seed|r1empty|menu --mcmode seed|empty|readonly
       --runner PATH --label NAME --wall SEC --coverage-tick N
       [--stop-tick N]
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

WORK = Path('/Users/brad/dev/ssx3-work/MC1')
SEED = WORK / 'mc0-seed'
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
VULKAN_LIB = '/opt/homebrew/lib/libvulkan.1.dylib'

# FR1-R1 verbatim (local/research/FR1/ROUTES-FR1.md), 30 entries.
FR1_R1 = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
          '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
          '22306:cross:250,24025:cross:250,'
          '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,'
          '30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,'
          '32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,'
          '34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,'
          '36520:cross:200,36771:down:700,37521:cross:200,37772:down:700')

SEED_SHIFT_MS = 4438  # +266 ticks: seeded title prompt ~836t vs ~570t empty


def shift(route, ms):
    parts = []
    for entry in route.split(','):
        at, btn, hold = entry.split(':')
        parts.append('%d:%s:%s' % (int(at) + ms, btn, hold))
    return ','.join(parts)


def post_crosses(first_ms, gap_ms, n):
    return ','.join('%d:cross:250' % (first_ms + k * gap_ms) for k in range(n))


# Seeded: FR1 results ~17798t -> ~18064t; first cross ~18300t (=305306 ms).
ROUTE_R1SEED = (shift(FR1_R1, SEED_SHIFT_MS) + ',' +
                post_crosses(305306, 2503, 12))


def T(tick):
    return int(tick * 100000 / 5994)


# Seeded save-flow: B1 showed results ~18686t with Restart highlighted and
# rows Next event/Restart/Replay/Records/Quit. Probe Replay (save replay?),
# back out, normalize to the top row with ups, then enter Records.
SAVE_NAV = [(19200, 'down', 150), (19350, 'cross', 250),
            (19600, 'cross', 250), (19900, 'cross', 250),
            (20200, 'cross', 250), (20500, 'circle', 250),
            (20650, 'circle', 250), (20800, 'up', 150), (20950, 'up', 150),
            (21100, 'down', 150), (21250, 'down', 150), (21400, 'down', 150),
            (21550, 'cross', 250), (21800, 'cross', 250),
            (22050, 'cross', 250), (22300, 'cross', 250),
            (22550, 'cross', 250)]
ROUTE_R1SAVE = (shift(FR1_R1, SEED_SHIFT_MS) + ',' +
                ','.join('%d:%s:%d' % (T(t), b, h) for t, b, h in SAVE_NAV))

# Seeded records+quit: results ~18665t (B1/B5), Restart highlighted, rows
# Next/Restart/Replay/Records/Quit. Enter Records (down,down,cross), answer
# with crosses; circle back; up,up,down x4 lands Quit from any highlight
# in {Next,Restart,Replay,Records} given clamp; cross + answer crosses.
QUIT_NAV = [(19100, 'down', 150), (19250, 'down', 150),
            (19400, 'cross', 250), (19700, 'cross', 250),
            (20000, 'cross', 250), (20300, 'cross', 250),
            (20600, 'cross', 250), (20900, 'cross', 250),
            (21200, 'circle', 250), (21350, 'circle', 250),
            (21500, 'up', 150), (21650, 'up', 150),
            (21800, 'down', 150), (21950, 'down', 150),
            (22100, 'down', 150), (22250, 'down', 150),
            (22400, 'cross', 250), (22700, 'cross', 250),
            (23000, 'cross', 250), (23300, 'cross', 250),
            (23600, 'cross', 250)]
ROUTE_R1QUIT = (shift(FR1_R1, SEED_SHIFT_MS) + ',' +
                ','.join('%d:%s:%d' % (T(t), b, h) for t, b, h in QUIT_NAV))

# Part 2: results ~18665t (Restart highlighted). Enter Records
# (down,down,cross — proven in B6), down to Save Records, cross, then
# answer crosses every ~300t.
SAVEREC_NAV = [(19100, 'down', 150), (19250, 'down', 150),
               (19400, 'cross', 250), (19750, 'down', 150),
               (19900, 'cross', 250), (20200, 'cross', 250),
               (20500, 'cross', 250), (20800, 'cross', 250),
               (21100, 'cross', 250), (21400, 'cross', 250),
               (21700, 'cross', 250), (22000, 'cross', 250),
               (22300, 'cross', 250)]
ROUTE_R1SAVEREC = (shift(FR1_R1, SEED_SHIFT_MS) + ',' +
                   ','.join('%d:%s:%d' % (T(t), b, h)
                             for t, b, h in SAVEREC_NAV))

# Part 2 corrected: P1 showed the overwrite prompt defaults to No, so the
# slot-select cross must be followed by up (No->Yes) then cross to confirm.
SAVEYES_NAV = [(19100, 'down', 150), (19250, 'down', 150),
               (19400, 'cross', 250), (19750, 'down', 150),
               (19900, 'cross', 250), (20200, 'cross', 250),
               (20500, 'up', 150), (20650, 'cross', 250),
               (20950, 'cross', 250), (21250, 'cross', 250),
               (21550, 'cross', 250), (21850, 'cross', 250),
               (22150, 'cross', 250), (22450, 'cross', 250)]
ROUTE_R1SAVEYES = (shift(FR1_R1, SEED_SHIFT_MS) + ',' +
                   ','.join('%d:%s:%d' % (T(t), b, h)
                             for t, b, h in SAVEYES_NAV))
# Empty: results ~17798t; first cross ~18030t (=300801 ms).
ROUTE_R1EMPTY = FR1_R1 + ',' + post_crosses(300801, 2503, 12)
# Seeded menu check: start@902t, crosses at 1032t/1150t/1330t/1510t.
ROUTE_MENU = '15049:start:250,17218:cross:250,19187:cross:250,22189:cross:250,25192:cross:250'

PROGRESS_CAP_S = 180
LOG_CAP_BYTES = 64 * 1024 * 1024
FRAMES_CAP_BYTES = 1 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 15
POLL_S = 1.0

RATE_TICK = re.compile(rb'\[vsync-rate\] tick=(\d+)\b')
GS_PATH = re.compile(r'^\[gs-path\].*$', re.M)
GS_FATAL = re.compile(r'^\[gs:parallel\] FATAL.*$', re.M)
COVERAGE = re.compile(r'^\[coverage:[^\]]*\].*$', re.M)
SND_OUT = re.compile(r'^\[snd-output\].*$', re.M)
PAD_ARMED = re.compile(r'^\[padscript\] armed.*$', re.M)
MC_LINE = re.compile(r'^\[MC\].*$', re.M)


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


def mc_snapshot(root):
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            p = Path(dirpath) / name
            st = p.stat()
            rows.append({'rel': str(p.relative_to(root)), 'size': st.st_size,
                         'mtime': st.st_mtime, 'sha': sha_of(p)})
        for name in sorted(dirnames):
            p = Path(dirpath) / name
            rows.append({'rel': str(p.relative_to(root)) + '/', 'size': None,
                         'mtime': p.stat().st_mtime, 'sha': None})
    rows.sort(key=lambda r: r['rel'])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--route', choices=('r1seed', 'r1empty', 'menu',
                                       'r1save', 'r1quit', 'r1saverec',
                                       'r1saveyes'),
                    required=True)
    ap.add_argument('--mcmode', choices=('seed', 'empty', 'readonly'),
                    required=True)
    ap.add_argument('--runner', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--wall', type=int, required=True)
    ap.add_argument('--coverage-tick', type=int, required=True)
    ap.add_argument('--stop-tick', type=int, default=10 ** 9)
    ap.add_argument('--mcsrc', default=None,
                    help='mc0 source dir for seed/readonly (default: pristine seed)')
    ap.add_argument('--snap-period', type=int, default=SNAP_PERIOD_S)
    args = ap.parse_args()

    route = {'r1seed': ROUTE_R1SEED, 'r1empty': ROUTE_R1EMPTY,
             'menu': ROUTE_MENU, 'r1save': ROUTE_R1SAVE,
             'r1quit': ROUTE_R1QUIT,
             'r1saverec': ROUTE_R1SAVEREC,
             'r1saveyes': ROUTE_R1SAVEYES}[args.route]
    runner = Path(args.runner).resolve()
    lane = WORK / 'run' / args.label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    mc0 = lane / 'mc0'
    if args.mcmode == 'empty':
        mc0.mkdir()
    else:
        src = Path(args.mcsrc) if args.mcsrc else SEED
        shutil.copytree(src, mc0, copy_function=shutil.copy2)
        if args.mcmode == 'readonly':
            for dirpath, dirnames, filenames in os.walk(mc0):
                for name in filenames:
                    os.chmod(os.path.join(dirpath, name), 0o444)
                for name in dirnames:
                    os.chmod(os.path.join(dirpath, name), 0o555)
            os.chmod(mc0, 0o555)
    (lane / 'mc1').mkdir()
    before = mc_snapshot(mc0)
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
               PS2X_MC_ROOT=str(mc0), PS2X_MISSING_FUNCTION_POLICY='stop',
               PS2X_GS_BACKEND='parallel', GRANITE_VULKAN_LIBRARY=VULKAN_LIB,
               PGS_HIER_BINNING='force', PS2X_VSYNC_RATE_LOG='1',
               PS2X_FRAME_DUMP_DIR=str(frames_dir),
               PS2X_COVERAGE_TICK=str(args.coverage_tick), PS2X_SOUND='1',
               COPYFILE_DISABLE='1')

    slot = claim('MC1-' + args.label, exclusive=False)
    while slot is None:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('MC1-' + args.label, exclusive=False)

    result = {'label': args.label, 'route': args.route, 'mcmode': args.mcmode,
              'mcsrc': str(Path(args.mcsrc).resolve()) if args.mcsrc else None,
              'snap_period': args.snap_period,
              'runner': str(runner), 'sha_reads': reads,
              'stop_tick': args.stop_tick, 'wall_cap': args.wall,
              'coverage_tick': args.coverage_tick,
              'slot': slot, 'exclusive': False,
              'mc_before': before,
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
        while not stop_snap.wait(args.snap_period):
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
                        time.sleep(3)
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
        if args.mcmode == 'readonly':
            for dirpath, dirnames, filenames in os.walk(mc0):
                for name in filenames:
                    os.chmod(os.path.join(dirpath, name), 0o644)
                for name in dirnames:
                    os.chmod(os.path.join(dirpath, name), 0o755)
            os.chmod(mc0, 0o755)
        text = log.read_text(errors='replace')
        gs_path = GS_PATH.findall(text)
        gs_fatal = GS_FATAL.findall(text)
        cov = COVERAGE.findall(text)
        snd = SND_OUT.findall(text)
        armed = PAD_ARMED.findall(text)
        mc = MC_LINE.findall(text)
        result.update(bound=bound, elapsed_s=round(time.monotonic() - t0, 3),
                      last_tick=last_tick, log_bytes=log.stat().st_size,
                      gs_path_line=gs_path[0] if gs_path else None,
                      gs_fatal=gs_fatal[0] if gs_fatal else None,
                      coverage_lines=cov if cov else None,
                      snd_output=snd if snd else None,
                      pad_armed=armed[0] if armed else None,
                      mc_lines=len(mc),
                      mc_after=mc_snapshot(mc0),
                      load_end=os.getloadavg())
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ('env', 'sha_reads', 'mc_before',
                                       'mc_after')}), flush=True)
        return 0 if bound in ('target', 'stop_file') else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        release(slot)


if __name__ == '__main__':
    sys.exit(main())
