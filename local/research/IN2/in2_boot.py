#!/usr/bin/env python3
"""IN2 proof boots: injected short taps vs guest pad reads, latch off vs on.

One binary (in2-latch), two runs: PS2X_PAD_LATCH=0 (pre-IN2 direct sampling,
the lost-tap repro) and latch on (default; taps must be seen exactly once).
I26-FAST drives to the race; PS2X_VPAD_TEST_TAP injects wall-clocked R3 taps
(script never presses R3) + late cross taps; PS2X_PAD_READ_LOG=1 records host
edges and every guest read. CPU backend: slow guest, wide read gaps.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release  # noqa: E402

WORK = Path('/Users/brad/dev/ssx3-work/IN2')
RUNNER = WORK / 'build/ps2xRuntime/ps2EntryRunner'
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'

ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,'
         '19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,'
         '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,'
         '30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,'
         '35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,'
         '38522:down:30000')

# Wall ms since the render loop's first frame: R3 taps every 3 s (40 ms),
# plus three late 60 ms cross taps (script's last cross is ~tick 2249).
TAPS = ','.join(['%d:r3:40' % ms for ms in range(30000, 300000, 3000)] +
                ['282000:cross:60', '292000:cross:60', '302000:cross:60'])

WALL_RUN_S = int(os.environ.get('IN2_WALL_S', '340'))
PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024


def sha_of(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    label = sys.argv[1]  # latch-off | latch-on
    latch_off = label == 'latch-off'
    lane = WORK / 'run' / label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    (lane / 'mc0').mkdir()
    (lane / 'mc1').mkdir()
    log_path = lane / 'boot.log'

    reads = [{str(p): sha_of(p) for p in (RUNNER, ISO, ELF)} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    if reads[0][str(ISO)] != ISO_SHA or reads[0][str(ELF)] != ELF_SHA:
        raise SystemExit('input SHA mismatch')

    env = {k: v for k, v in os.environ.items() if not k.startswith('PS2X_')}
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               PS2X_VIRTUAL_PAD='1', PS2X_VPAD_TEST_TAP=TAPS, PS2X_PAD_READ_LOG='1',
               PS2X_VSYNC_RATE_LOG='1', COPYFILE_DISABLE='1')
    if latch_off:
        env['PS2X_PAD_LATCH'] = '0'

    slot = claim('IN2-' + label)
    while slot is None:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('IN2-' + label)

    result = {'label': label, 'slot': slot, 'runner_sha': reads[0][str(RUNNER)],
              'tap_count': TAPS.count(',') + 1, 'load_start': os.getloadavg()}
    proc = None
    try:
        t0 = time.monotonic()
        with log_path.open('wb') as out:
            proc = subprocess.Popen([str(RUNNER), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': label, 'pid': proc.pid,
                              'slot': slot}), flush=True)
            last_progress, bound = t0, None
            last_size = 0
            while True:
                now = time.monotonic()
                if proc.poll() is not None:
                    bound = 'exit rc=%s' % proc.returncode
                    break
                if now - t0 >= WALL_RUN_S:
                    bound = 'tap_window_done'
                    proc.terminate()
                    try:
                        proc.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    break
                try:
                    size = log_path.stat().st_size
                except OSError:
                    size = 0
                if size != last_size:
                    last_size, last_progress = size, now
                if size >= LOG_CAP_BYTES:
                    bound = 'log_cap'
                    proc.terminate()
                    break
                if now - last_progress >= PROGRESS_CAP_S:
                    bound = 'no_progress'
                    proc.terminate()
                    break
                time.sleep(1)
        result['bound'] = bound
        result['wall_s'] = round(time.monotonic() - t0, 1)
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
        release(slot)
    (lane / 'result.json').write_text(json.dumps(result, indent=1) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
