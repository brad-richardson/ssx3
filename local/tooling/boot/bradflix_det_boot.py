#!/usr/bin/env python3
"""HS1 bradflix det boot: one deterministic boot in Docker (GPU + Xvfb).

Runs ON BRADFLIX (synced + invoked by ssx3_boot.py --host bradflix, but also
runnable directly there). Mirrors ssx3_boot.py --mode det exactly: same
pins, same guest env incl. sound/coverage/dump-ticks/vu1-stats, same
caps/trace/result.json fields, so baseline.py compare works unchanged on
the pulled-back run dir.

Deltas vs the mini path (all host-necessary, guest-neutral):
- runner executes in the ssx3-hs1 container (HS1 root bind-mounted at
  /work); GPU (--device renderD128 + group 993) only for backend=parallel.
- GRANITE_VULKAN_LIBRARY is NOT set (system loader, LX1 Part 2 recipe).
- Xvfb is managed directly (lx1_boot.py lesson: xvfb-run hangs here).
- Requires a held bradflix lease slot (--slot N: ~/.ssx3-lease/N/HOLDER).

Usage (on bradflix): bradflix_det_boot.py --runner PATH --label NAME --slot N
  [--stop-tick 2400] [--sound on|off] [--coverage-tick 2400]
  [--backend cpu|parallel] [--route i26|fr1r1] [--pad-script STR]
  [--dump-ticks a,b,c] [--hash-every 1] [--wall 500] [--no-snap]
  [--unpaced] [--vu1-stats] [--vu1-dump DIR] [--stack-kb N]
  [--env K=V ...] [--root DIR] [--image NAME]
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

DEFAULT_ROOT = Path.home() / 'dev' / 'ssx3-work' / 'HS1'
LEASE_ROOT = Path.home() / '.ssx3-lease'
C_ROOT = '/work'
IMAGE = 'ssx3-hs1'

ISO_NAME = 'SSX 3 (USA).iso'
ELF_NAME = 'SLUS_207.72'
CODEGEN_NAME = 'register_functions.cpp'
CODEGEN_VF0_NAME = 'sub_003FE828_0x3fe828.cpp'
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
CODEGEN_VF0_SHA = '89953ba218efd63c2fdba28116765d524977f1233d0e370d22111a762e02383d'

# Duplicates of ssx3_boot.py ROUTE/ROUTE_FR1R1 (fallback for direct runs;
# the wrapper always passes --pad-script, which wins). I26-FAST, HUD ~1714.
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,'
         '19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,'
         '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,'
         '30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,'
         '35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,'
         '38522:down:30000')
ROUTE_FR1R1 = ROUTE.rsplit(',', 1)[0]

PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 1 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 0.5
POLL_S = 0.5

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')
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
    ap.add_argument('--runner', required=True, help='bradflix path to ps2EntryRunner')
    ap.add_argument('--label', required=True)
    ap.add_argument('--slot', required=True, help='held bradflix lease slot (1-4)')
    ap.add_argument('--stop-tick', type=int, default=2400)
    ap.add_argument('--sound', choices=('on', 'off'), default='on')
    ap.add_argument('--coverage-tick', type=int, default=2400)
    ap.add_argument('--backend', choices=('cpu', 'parallel'), default='parallel')
    ap.add_argument('--route', choices=('i26', 'fr1r1'), default='fr1r1')
    ap.add_argument('--pad-script', default='', help='override the route string (wrapper passes it)')
    ap.add_argument('--dump-ticks', default='')
    ap.add_argument('--hash-every', type=int, default=1)
    ap.add_argument('--wall', type=int, default=500)
    ap.add_argument('--no-snap', action='store_true')
    ap.add_argument('--unpaced', action='store_true')
    ap.add_argument('--vu1-stats', action='store_true')
    ap.add_argument('--vu1-dump', default='')
    ap.add_argument('--stack-kb', type=int, default=0)
    ap.add_argument('--env', action='append', default=[], help='extra K=V (verbatim)')
    ap.add_argument('--root', default=str(DEFAULT_ROOT))
    ap.add_argument('--image', default=IMAGE)
    args = ap.parse_args()
    wall_cap = min(args.wall, 1800)
    if args.slot not in ('1', '2', '3', '4'):
        raise SystemExit('bad --slot %s' % args.slot)
    holder_p = LEASE_ROOT / args.slot / 'HOLDER'
    if not holder_p.is_file():
        raise SystemExit('bradflix lease slot %s not held; refusing' % args.slot)
    holder = holder_p.read_text().strip()

    root = Path(args.root).resolve()
    runner = Path(os.path.expanduser(args.runner))
    if not runner.is_absolute():
        runner = (Path.home() / runner).resolve()
    else:
        runner = runner.resolve()
    iso = root / 'inputs' / ISO_NAME
    elf = root / 'inputs' / ELF_NAME
    codegen = root / 'codegen' / CODEGEN_NAME
    codegen_vf0 = root / 'codegen' / CODEGEN_VF0_NAME
    for p in (runner, iso, elf, codegen, codegen_vf0):
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

    pins = {str(iso): ISO_SHA, str(elf): ELF_SHA, str(codegen): CODEGEN_SHA,
            str(codegen_vf0): CODEGEN_VF0_SHA}
    big = [runner, iso, elf, codegen, codegen_vf0]
    reads = [{str(p): sha_of(p) for p in big} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    for path, want in pins.items():
        if reads[0][path] != want:
            raise SystemExit('SHA mismatch for %s' % path)

    fork_sha = subprocess.run(['git', '-C', str(root / 'PS2Recomp'), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
    image_id = subprocess.run(['docker', 'images', args.image, '--format', '{{.ID}}'],
                              capture_output=True, text=True).stdout.strip()

    pad = args.pad_script or (ROUTE_FR1R1 if args.route == 'fr1r1' else ROUTE)
    c_lane = '%s/run/%s' % (C_ROOT, args.label)
    try:
        c_runner = C_ROOT + '/' + str(runner.relative_to(root))
    except ValueError:
        raise SystemExit('runner %s is outside --root %s' % (runner, root))
    guest_env = {
        'PS2X_CD_IMAGE': '%s/inputs/%s' % (C_ROOT, ISO_NAME),
        'PS2X_SKIP_MOVIE': '1',
        'PS2X_DETERMINISTIC': '1',
        'PS2X_PAD_SCRIPT_CLOCK': 'vsync',
        'PS2X_PAD_SCRIPT': pad,
        'PS2X_MC_ROOT': c_lane + '/mc0',
        'PS2X_MISSING_FUNCTION_POLICY': 'stop',
        'COPYFILE_DISABLE': '1',
        'PS2X_DET_HASH_EVERY': str(args.hash_every),
        'PS2X_FRAME_DUMP_DIR': c_lane + '/frames',
        'PS2X_SND_LOG': c_lane + '/snd.log',
        'PS2X_COVERAGE_TICK': str(args.coverage_tick),
    }
    if args.backend == 'parallel':
        guest_env.update(PS2X_GS_BACKEND='parallel', PGS_HIER_BINNING='force')
    if args.sound == 'on':
        guest_env['PS2X_SOUND'] = '1'
    if args.unpaced:
        guest_env['PS2X_UNPACED'] = '1'
    if args.vu1_stats:
        guest_env['PS2X_VU1_RECOMP_STATS'] = '1'
    if args.vu1_dump:
        guest_env['PS2X_VU1_RECOMP_DUMP'] = args.vu1_dump
        guest_env['PS2X_VU1_RECOMP'] = '0'
    if args.stack_kb:
        guest_env['PS2X_GAME_THREAD_STACK_KB'] = str(args.stack_kb)
    if args.dump_ticks:
        guest_env['PS2X_FRAME_DUMP_ONCE_TICKS'] = args.dump_ticks
    for kv in args.env:
        if '=' not in kv:
            raise SystemExit('bad --env %r (need K=V)' % kv)
        k, v = kv.split('=', 1)
        guest_env[k] = v

    cname = 'hs1-%s-%d' % (re.sub(r'[^A-Za-z0-9_.-]', '_', args.label), os.getpid())
    cmd = ['docker', 'run', '--rm', '--name', cname,
           '--user', '%d:%d' % (os.getuid(), os.getgid())]
    if args.backend == 'parallel':
        cmd += ['--device', '/dev/dri/renderD128', '--group-add', '993']
    cmd += ['-e', 'HOME=/work', '-w', c_lane, '-v', '%s:%s' % (root, C_ROOT)]
    for k, v in guest_env.items():
        cmd += ['-e', '%s=%s' % (k, v)]
    # Direct-Xvfb management (xvfb-run's ready handshake hangs in this
    # container); stdbuf keeps early output visible (LX1 §5 lesson).
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
    cmd += [args.image, 'bash', '-c', inner]

    result = {'label': args.label, 'mode': 'det', 'backend': args.backend,
              'host': 'bradflix', 'fork_sha': fork_sha, 'image': args.image,
              'image_id': image_id, 'runner': str(runner), 'sha_reads': reads,
              'stop_tick': args.stop_tick, 'slot': args.slot,
              'lease_holder': holder, 'sound': args.sound,
              'gpu': args.backend == 'parallel',
              'env': {k: v for k, v in guest_env.items()
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
            th = None
            if not args.no_snap and not args.dump_ticks:
                th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
                th.start()
            last_tick, last_progress, bound = 0, t0, None
            try:
                while True:
                    now = time.monotonic()
                    if proc.poll() is not None:
                        bound = 'exit'
                        break
                    if now - t0 >= wall_cap:
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
                stop_container()
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
                      hud_wall_s=hud_wall,
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
        stop_container()


if __name__ == '__main__':
    sys.exit(main())
