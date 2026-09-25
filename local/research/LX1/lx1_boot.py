#!/usr/bin/env python3
"""LX1 bounded det boot on bradflix (CPU GS backend, inside the ssx3-lx1 container).

Runs on the bradflix HOST; the runner executes in docker with the LX1 work dir
bind-mounted at /work. Mirrors local/research/F2/f2_boot.py det mode: I26-FAST
to the race, PS2X_DETERMINISTIC=1, PS2X_SKIP_MOVIE=1 (dev-only), vsync pad
clock, empty mc0/mc1, sound off (PS2X_SOUND unset; AU10: guest-identical),
continuous present-frame capture with a 0.5 s snapshotter tagging
upload-latest pairs by det-hash tick. Stops at --stop-tick + 3 s settle.

Requires the bradflix lease (~/dev/ssx3-work/BRADFLIX_LEASE, held by the
caller, e.g. local/tooling/remote/bradflix_boot.sh): refuses to run without it.
Wall cap 500 s, no-progress cap 120 s, log cap 16 MiB, frames cap 1 GiB.
Only the recorded docker PID / named container is stopped.

Usage: lx1_boot.py --runner PATH --label NAME [--stop-tick 2400] [--root DIR]
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

DEFAULT_ROOT = Path.home() / 'dev' / 'ssx3-work' / 'LX1'
LEASE_DIR = Path.home() / 'dev' / 'ssx3-work' / 'BRADFLIX_LEASE'
C_ROOT = '/work'  # bind-mount target inside the container
IMAGE = 'ssx3-lx1'

ISO_NAME = 'SSX 3 (USA).iso'
ELF_NAME = 'SLUS_207.72'
CODEGEN_NAME = 'register_functions.cpp'
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'

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

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')


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
    ap.add_argument('--runner', required=True, help='host path to ps2EntryRunner')
    ap.add_argument('--label', required=True)
    ap.add_argument('--stop-tick', type=int, default=2400)
    ap.add_argument('--root', default=str(DEFAULT_ROOT))
    ap.add_argument('--coverage-tick', type=int, default=2400)
    ap.add_argument('--extra-env', action='append', default=[],
                    help='extra guest env KEY=VAL, verbatim into the container (repeatable); a VAL under /work/ is mkdir -p-ed on the host')
    args = ap.parse_args()

    if not LEASE_DIR.is_dir():
        raise SystemExit('bradflix lease %s not held; refusing' % LEASE_DIR)
    holder = (LEASE_DIR / 'HOLDER').read_text().strip() if (LEASE_DIR / 'HOLDER').exists() else '?'

    root = Path(args.root).resolve()
    runner = Path(args.runner).resolve()
    iso = root / 'inputs' / ISO_NAME
    elf = root / 'inputs' / ELF_NAME
    codegen = root / 'codegen' / CODEGEN_NAME
    for p in (runner, iso, elf, codegen):
        if not p.is_file():
            raise SystemExit('missing %s' % p)

    lane = root / 'run' / args.label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    (lane / 'mc0').mkdir()
    (lane / 'mc1').mkdir()
    frames_dir = lane / 'frames'
    snap_dir = frames_dir / 'snap'
    snap_dir.mkdir(parents=True)
    log = lane / 'boot.log'

    pins = {str(iso): ISO_SHA, str(elf): ELF_SHA, str(codegen): CODEGEN_SHA}
    big = [runner, iso, elf, codegen]
    reads = [{str(p): sha_of(p) for p in big} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    for path, want in pins.items():
        if reads[0][path] != want:
            raise SystemExit('SHA mismatch for %s' % path)

    fork_sha = subprocess.run(['git', '-C', str(root / 'PS2Recomp'), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
    image_id = subprocess.run(['docker', 'images', IMAGE, '--format', '{{.ID}}'],
                              capture_output=True, text=True).stdout.strip()

    c_lane = '%s/run/%s' % (C_ROOT, args.label)
    c_runner = C_ROOT + '/' + str(runner.relative_to(root))
    guest_env = {
        'PS2X_CD_IMAGE': '%s/inputs/%s' % (C_ROOT, ISO_NAME),
        'PS2X_SKIP_MOVIE': '1',
        'PS2X_DETERMINISTIC': '1',
        'PS2X_PAD_SCRIPT_CLOCK': 'vsync',
        'PS2X_PAD_SCRIPT': ROUTE,
        'PS2X_MC_ROOT': c_lane + '/mc0',
        'PS2X_MISSING_FUNCTION_POLICY': 'stop',
        'PS2X_DET_HASH_EVERY': '1',
        'PS2X_FRAME_DUMP_DIR': c_lane + '/frames',
        'PS2X_SND_LOG': c_lane + '/snd.log',
        'PS2X_COVERAGE_TICK': str(args.coverage_tick),
        # PS2X_SOUND deliberately unset (sound-off; AU10 guest-identical).
        # PS2X_GS_BACKEND deliberately unset (CPU GS default).
    }
    for item in args.extra_env:
        if '=' not in item:
            raise SystemExit('bad --extra-env %r (need KEY=VAL)' % item)
        k, v = item.split('=', 1)
        guest_env[k] = v
        if k.endswith('_DIR') and v.startswith(C_ROOT + '/'):  # container dir -> host dir
            (root / v[len(C_ROOT) + 1:]).mkdir(parents=True, exist_ok=True)
    cname = 'lx1-%s-%d' % (re.sub(r'[^A-Za-z0-9_.-]', '_', args.label), os.getpid())
    uid = os.getuid()
    cmd = ['docker', 'run', '--rm', '--name', cname,
           '--user', '%d:%d' % (uid, os.getgid()),
           '-e', 'HOME=/work', '-w', c_lane, '-v', '%s:%s' % (root, C_ROOT)]
    for k, v in guest_env.items():
        cmd += ['-e', '%s=%s' % (k, v)]
    # NOTE: no xvfb-run: its Xvfb-ready handshake (SIGUSR1 + wait) hangs
    # in this container (worked once, then hung with the X server already
    # up — first as PID 1, then flakily under a wrapper too). Manage Xvfb
    # directly: poll for the socket, run with DISPLAY=:99, kill after.
    # stdbuf keeps early runner output visible (docker pipes = libc full
    # buffering otherwise; a killed runner's buffered output would be lost).
    inner = ('Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/tmp/xvfb.log 2>&1 & '
             'XPID=$!; READY=0; '
             'for i in $(seq 1 100); do if [ -S /tmp/.X11-unix/X99 ]; then READY=1; break; fi; '
             'sleep 0.2; done; '
             'if [ $READY -eq 0 ]; then echo Xvfb-failed-to-start; cat /tmp/xvfb.log; '
             'kill $XPID 2>/dev/null; exit 3; fi; '
             "trap 'kill $XPID $RPID 2>/dev/null' TERM INT; "
             'DISPLAY=:99 stdbuf -o0 -e0 %s %s & RPID=$!; wait $RPID; RC=$?; '
             'kill $XPID 2>/dev/null; exit $RC'
             % (shlex.quote(c_runner), shlex.quote('%s/inputs/%s' % (C_ROOT, ELF_NAME))))
    cmd += [IMAGE, 'bash', '-c', inner]

    result = {'label': args.label, 'mode': 'det', 'backend': 'cpu', 'host': 'bradflix',
              'fork_sha': fork_sha, 'image': IMAGE, 'image_id': image_id,
              'runner': str(runner), 'sha_reads': reads, 'stop_tick': args.stop_tick,
              'lease_holder': holder, 'sound': 'off', 'env': guest_env,
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

    def stop_container():
        try:
            subprocess.run(['docker', 'stop', '-t', '5', cname],
                           capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            pass

    try:
        t0 = time.monotonic()
        trace = trace_path.open('w')
        with log.open('wb') as out:
            proc = subprocess.Popen(cmd, cwd=lane, stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            result['container'] = cname
            print(json.dumps({'event': 'boot', 'label': args.label, 'pid': proc.pid,
                              'container': cname}), flush=True)
            th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
            th.start()
            last_tick, last_progress, bound = 0, t0, None
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
                    if dir_bytes(frames_dir) > FRAMES_CAP_BYTES:
                        bound = 'frames_cap'
                        break
                    tail = log.read_bytes()[-65536:]
                    if any(m in tail for m in HASH_ERROR_MARKERS):
                        bound = 'hash_error'
                        break
                    m = HASH_TICK.findall(tail)
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
                        time.sleep(3)  # let the snapshotter grab final frames
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
                stop_container()
            else:
                result['runner_rc'] = proc.returncode
        trace.close()
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
                      hud_wall_s=hud_wall, load_end=os.getloadavg())
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ('env', 'sha_reads')}), flush=True)
        return 0 if bound == 'target' else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        stop_container()


if __name__ == '__main__':
    sys.exit(main())
