#!/usr/bin/env python3
"""GB8 bounded boot: I26-FAST to the race, CPU vs paraLLEl GS backend.

Modes (runner built with PS2X_GS_SHADOW_PARALLEL=ON; backend chosen at runtime):
  speed  diagnostics-off runner: PS2X_VSYNC_RATE_LOG=1 ([vsync-rate] every 5 s);
         takes the EXCLUSIVE mini lease (all slots). Stops at --stop-tick.
         Samples `ps -M <pid>` in the race window (Q4 host cost).
  det    det-hash runner (PS2X_ENABLE_DET_HASH_TAP=ON): PS2X_DET_HASH_EVERY=1 and
         continuous presentation-frame capture (PS2X_FRAME_DUMP_DIR) with a
         0.5 s snapshotter tagging upload-latest pairs by det-hash tick (Q3).
         One mini slot. No GS stream capture. Stops at --stop-tick + 3 s settle.

--backend cpu|parallel: parallel sets PS2X_GS_BACKEND=parallel and
GRANITE_VULKAN_LIBRARY (Mac MoltenVK loader path, GB6/TL1 recipe).

Both modes: PS2X_DETERMINISTIC=1, PS2X_SKIP_MOVIE=1 (dev-only), vsync pad clock,
empty mc0/mc1 under the run dir. Wall cap 500 s, no-progress cap 120 s, log cap
16 MiB. Only the recorded runner PID is signalled; the lease is released on
every path. A (wall, tick) trace is written every poll for phase-rate analysis.

Usage: gb8_boot.py --mode speed|det --backend cpu|parallel --runner PATH --label NAME
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

WORK = Path('/Users/brad/dev/ssx3-work/GB9')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
VULKAN_LIB = '/opt/homebrew/lib/libvulkan.1.dylib'

# I26-FAST (local/research/I26/ROUTES.md), race HUD at tick ~1714.
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,'
         '19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,'
         '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,'
         '30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,'
         '35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,'
         '38522:down:30000')

WALL_CAP_S = 500
PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 1 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 0.5
POLL_S = 0.5
PS_EVERY_S = 10
PS_START_TICK = 1750
PS_MAX_SAMPLES = 12

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')
RATE_TICK = re.compile(rb'\[vsync-rate\] tick=(\d+)\b')
GS_PATH = re.compile(r'^\[gs-path\].*$', re.M)
GS_FATAL = re.compile(r'^\[gs:parallel\] FATAL.*$', re.M)


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
    ap.add_argument('--mode', choices=('speed', 'det'), required=True)
    ap.add_argument('--backend', choices=('cpu', 'parallel'), required=True)
    ap.add_argument('--runner', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--stop-tick', type=int, default=2400)
    args = ap.parse_args()

    runner = Path(args.runner).resolve()
    lane = WORK / 'run' / args.label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    (lane / 'mc0').mkdir()
    (lane / 'mc1').mkdir()
    frames_dir = lane / 'frames'
    snap_dir = frames_dir / 'snap'
    if args.mode == 'det':
        snap_dir.mkdir(parents=True)
    log = lane / 'boot.log'

    pins = {str(ISO): ISO_SHA, str(ELF): ELF_SHA, str(CODEGEN): CODEGEN_SHA}
    big = [runner, ISO, ELF, CODEGEN]
    reads = [{str(p): sha_of(p) for p in big} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    for path, want in pins.items():
        if reads[0][path] != want:
            raise SystemExit('SHA mismatch for %s' % path)
    if args.backend == 'parallel' and not os.path.exists(VULKAN_LIB):
        raise SystemExit('missing %s' % VULKAN_LIB)

    env = {k: v for k, v in os.environ.items() if not k.startswith('PS2X_')}
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               PS2X_SOUND='1', COPYFILE_DISABLE='1')
    if args.backend == 'parallel':
        env.update(PS2X_GS_BACKEND='parallel', GRANITE_VULKAN_LIBRARY=VULKAN_LIB,
               PGS_HIER_BINNING='force', PGS_HIER_PROBE='1')
    if args.mode == 'det':
        env.update(PS2X_DET_HASH_EVERY='1', PS2X_FRAME_DUMP_DIR=str(frames_dir),
                   PS2X_SND_LOG=str(lane / 'snd.log'))
        tick_re = HASH_TICK
    else:
        env.update(PS2X_VSYNC_RATE_LOG='1')
        tick_re = RATE_TICK

    exclusive = args.mode == 'speed'
    held = os.environ.get('GB9_HELD_SLOT')
    if held:
        slot = held  # pre-held by gb8_watch.py across back-to-back boots; no release here
        print(json.dumps({'event': 'using-held-slot', 'slot': slot}), flush=True)
    else:
        slot = claim('GB9-' + args.label, exclusive=exclusive)
        while slot is None:
            print('lease busy; retrying in 30 s', flush=True)
            time.sleep(30)
            slot = claim('GB9-' + args.label, exclusive=exclusive)

    result = {'label': args.label, 'mode': args.mode, 'backend': args.backend,
              'runner': str(runner), 'sha_reads': reads, 'stop_tick': args.stop_tick,
              'slot': slot, 'exclusive': exclusive,
              'env': {k: v for k, v in env.items()
                      if k.startswith('PS2X_') or k.startswith('GRANITE_') or k.startswith('PGS_')},
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
            th = None
            if args.mode == 'det':
                th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
                th.start()
            last_tick, last_progress, bound = 0, t0, None
            ps_samples, last_ps = 0, 0.0
            try:
                while True:
                    now = time.monotonic()
                    if proc.poll() is not None:
                        bound = 'exit'
                        break
                    if now - t0 >= WALL_CAP_S:
                        bound = 'wall_cap'
                        break
                    if log.stat().st_size > LOG_CAP_BYTES:
                        bound = 'log_cap'
                        break
                    if args.mode == 'det' and dir_bytes(frames_dir) > FRAMES_CAP_BYTES:
                        bound = 'frames_cap'
                        break
                    tail = log.read_bytes()[-65536:]
                    if args.mode == 'det' and any(m in tail for m in HASH_ERROR_MARKERS):
                        bound = 'hash_error'
                        break
                    m = tick_re.findall(tail)
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
                    if (args.mode == 'speed' and last_tick >= PS_START_TICK
                            and ps_samples < PS_MAX_SAMPLES and now - last_ps >= PS_EVERY_S):
                        last_ps = now
                        try:
                            ps = subprocess.run(['ps', '-M', str(proc.pid)],
                                                capture_output=True, timeout=15)
                            (lane / ('ps-race-%02d.txt' % ps_samples)).write_bytes(ps.stdout)
                            ps_samples += 1
                        except (OSError, subprocess.SubprocessError):
                            pass
                    if last_tick >= args.stop_tick:
                        bound = 'target'
                        if args.mode == 'det':
                            time.sleep(3)  # let the snapshotter grab final frames
                        break
                    time.sleep(POLL_S)
            finally:
                stop_snap.set()
                if th is not None:
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
        hud_wall = None
        prev = None
        for line in trace_path.read_text().splitlines():
            row = json.loads(line)
            if row['tick'] >= 1714:
                if prev is not None and row['tick'] != prev['tick']:
                    f = (1714 - prev['tick']) / (row['tick'] - prev['tick'])
                    hud_wall = round(prev['wall_s'] + f * (row['wall_s'] - prev['wall_s']), 2)
                else:
                    hud_wall = row['wall_s']
                break
            prev = row
        result.update(bound=bound, elapsed_s=round(time.monotonic() - t0, 3),
                      last_tick=last_tick, log_bytes=log.stat().st_size,
                      hud_wall_s=hud_wall, ps_samples=ps_samples,
                      gs_path_line=gs_path[0] if gs_path else None,
                      gs_fatal=gs_fatal[0] if gs_fatal else None,
                      load_end=os.getloadavg())
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ('env', 'sha_reads')}), flush=True)
        return 0 if bound == 'target' else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        if not held:
            release(slot)


if __name__ == '__main__':
    sys.exit(main())
