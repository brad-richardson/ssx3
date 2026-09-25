#!/usr/bin/env python3
"""GA1 bounded boot: I26-FAST to the race, paraLLEl GS backend, PK_ORDER tap.

One det boot (PS2X_DETERMINISTIC=1, PS2X_DET_HASH_EVERY=1 tick gate, empty
mc0/mc1, own cwd, own PID). Stops at --stop-tick (default 2400). One mini
slot (never exclusive). Wall 500 s / progress 120 s / log 16 MiB /
order-file 1 GiB caps. Only the recorded runner PID is signalled; the
lease is released on every path.

Usage: ga1_boot.py --runner PATH --label NAME [--stop-tick N]
Results: ~/dev/ssx3-work/GA1/run/<label>/{boot.log,pk-order.txt,result.json,trace.jsonl}
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release  # noqa: E402

WORK = Path('/Users/brad/dev/ssx3-work/GA1')
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
ORDER_CAP_BYTES = 1 * 1024 * 1024 * 1024
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


def main():
    ap = argparse.ArgumentParser()
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
    log = lane / 'boot.log'
    order_path = lane / 'pk-order.txt'

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
    # PS2X_SOUND=1 is required on the folded tip: B1 without it sat on the
    # title (9 small packets/tick, all presses ignored); F1's B1 with it
    # reaches the race. GB8's env predates the AU9 fold.
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               PS2X_GS_BACKEND='parallel', GRANITE_VULKAN_LIBRARY=VULKAN_LIB,
               PS2X_DET_HASH_EVERY='1', PS2X_PK_ORDER=str(order_path),
               PS2X_SOUND='1', COPYFILE_DISABLE='1')

    slot = claim('GA1-' + args.label, exclusive=False)
    while slot is None:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('GA1-' + args.label, exclusive=False)

    result = {'label': args.label, 'backend': 'parallel',
              'runner': str(runner), 'sha_reads': reads, 'stop_tick': args.stop_tick,
              'slot': slot, 'exclusive': False,
              'env': {k: v for k, v in env.items()
                      if k.startswith('PS2X_') or k.startswith('GRANITE_')},
              'load_start': os.getloadavg()}
    proc = None
    trace_path = lane / 'trace.jsonl'
    try:
        t0 = time.monotonic()
        trace = trace_path.open('w')
        with log.open('wb') as out:
            proc = subprocess.Popen([str(runner), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label, 'pid': proc.pid,
                              'slot': slot}), flush=True)
            last_tick, last_progress, bound = 0, t0, None
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
                if order_path.exists() and order_path.stat().st_size > ORDER_CAP_BYTES:
                    bound = 'order_cap'
                    break
                tail = log.read_bytes()[-65536:]
                if any(m in tail for m in HASH_ERROR_MARKERS):
                    bound = 'hash_error'
                    break
                m = HASH_TICK.findall(tail)
                if m and int(m[-1]) > last_tick:
                    last_tick = int(m[-1])
                    last_progress = now
                trace.write(json.dumps({'wall_s': round(now - t0, 3),
                                        'tick': last_tick}) + '\n')
                trace.flush()
                if now - last_progress >= PROGRESS_CAP_S:
                    bound = 'progress_cap'
                    break
                if last_tick >= args.stop_tick:
                    bound = 'target'
                    break
                time.sleep(POLL_S)
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
        result.update(bound=bound, elapsed_s=round(time.monotonic() - t0, 3),
                      last_tick=last_tick, log_bytes=log.stat().st_size,
                      order_bytes=order_path.stat().st_size if order_path.exists() else 0,
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
        release(slot)


if __name__ == '__main__':
    sys.exit(main())
