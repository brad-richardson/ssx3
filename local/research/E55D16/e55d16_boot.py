#!/usr/bin/env python3
"""E55D16 Part 2: ONE bounded seeded-card Load-game boot (released by brief).

Route (PS2X_PAD_SCRIPT_CLOCK=vsync; guest ms = tick * 100000 / 5994):
  - E55D12's 9-input Load-game spine unchanged: START tick 636 (hold 250 ms),
    Square tick 820, Downs 1000/1070/1140/1210, Cross C1 tick 1360 (Save/Load
    row), Down D5 tick 1540 (Save game -> Load game), Cross C2 tick 1700
    (select Load game; E55D14 observed the post-choice GetDir
    /BASLUS-20772-GAM* at tick 1740 on an empty card).
  - ONE added Cross C3 at tick 1950 (hold 150 ms): select the highlighted
    MEMORY CARD row (row 1 lists Brad's save on the seeded card).
  - Frame targets: F_LOAD=1620 (Load-game highlight), F_POST=1800 (seeded
    MEMORY CARD screen), F_SELECT=2050 (post-C3 result). Stop tick = 2100.

Cards: lane mc0 is SEEDED from the Part 1 extraction
(~/dev/ssx3-work/E55D16/mc0: BASLUS-20772-GAM0001 + BASLUS-20772-SET0001,
3 files each, seed SHAs pinned below, host mtimes set from the card's
modified timestamps interpreted in host-local wall time). mc1 fresh empty.
Refuses to start if lane/mc0 already exists (no reuse, no reseed).

Card-API observation: this fork rev has no PS2X_PAD_CARD_PROBE tap (that
lived in the retired E55D3 checkout); card lines come from the RUNTIME_LOG
[MC] GetDir/Open/Read/Sync lines in boot.log (this runner was built with
PS2X_ENABLE_RUNTIME_LOGS=ON). det-hash ticks (PS2X_ENABLE_DET_HASH_TAP=ON)
tag snapshot frames as in E55D12.

Stop only after tick >= 2100 AND a persisted snap PNG tagged >= 2100
(frame_unproven/OTHER if the 120 s grace expires without the proof).

Method (adapted from E55D12's e55d12_boot.py): per-run cwd
(~/dev/ssx3-work/E55D16/run/<label>), one mini P-lane slot held only during
the boot (waits for a free slot), wall cap 500 s, no-tick-progress cap
120 s, boot log cap 16 MiB (closed log). Kill only the recorded PID;
release the lease even on failure. Pre-boot checks: fork at exact fb11e18,
clean worktree, runner-dir guard vs upstream 14b1e5cb, and two matching
SHA reads of runner/ISO/ELF/codegen/seed against the pins below.

Usage: e55d16_boot.py --label S1          (ONE boot only)
       e55d16_boot.py --self-check        (pure helper tests, no boot/lease)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release

WORK = Path('/Users/brad/dev/ssx3-work/E55D16')
FORK = Path('/Users/brad/dev/PS2Recomp')
RUNNER = Path('/Users/brad/dev/ssx3-work/E55D16/build/ps2xRuntime/ps2EntryRunner')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
SEED_SRC = Path('/Users/brad/dev/ssx3-work/E55D16/mc0')

FORK_PIN_FULL = 'fb11e182310555c65201635f8d6c7fe8e170de74'
FORK_PIN_SHORT = 'fb11e18'
UPSTREAM_RUNNER_BASE = '14b1e5cb'
RUNNER_SHA = 'f4d7632ca371ed7b429a74ab535db6209968f7fcb4c69a2b2bf560c028b71711'
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'

# Part 1 extraction pins (seed file SHAs; sizes in REPORT.md).
SEED_SHA = {
    'BASLUS-20772-GAM0001/icon.sys': 'eab225745ef6695109743410261609e0569c14edb1555bc8941a965b3890a49c',
    'BASLUS-20772-GAM0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-GAM0001/BASLUS-20772-GAM0001': '4bdaee79a3bdaceef898bb44b6bcf62058e882a24237f8c81e46953a5067b78e',
    'BASLUS-20772-SET0001/icon.sys': 'dddf2d9c81a1c8bac2fe2036e1771dfa63635e3ae676760551defec2da67ee13',
    'BASLUS-20772-SET0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-SET0001/BASLUS-20772-SET0001': '4a31a2d7e095e277edceae2243002055aa830019b3a1be64f126aee9129002f1',
}

# Card modified timestamps (wall clock as stored on the card; applied to the
# lane copy with time.mktime, i.e. interpreted in host-local wall time).
SEED_MTIME = {
    'BASLUS-20772-GAM0001': '2026-05-08 06:44:15',
    'BASLUS-20772-GAM0001/icon.sys': '2026-05-08 06:44:13',
    'BASLUS-20772-GAM0001/ssx1.ico': '2026-05-08 06:44:14',
    'BASLUS-20772-GAM0001/BASLUS-20772-GAM0001': '2026-05-08 06:44:15',
    'BASLUS-20772-SET0001': '2026-05-08 06:14:32',
    'BASLUS-20772-SET0001/icon.sys': '2026-05-08 06:14:31',
    'BASLUS-20772-SET0001/ssx1.ico': '2026-05-08 06:14:31',
    'BASLUS-20772-SET0001/BASLUS-20772-SET0001': '2026-05-08 06:14:32',
}

START_TICK = 636
SQUARE_TICK = 820
DOWN_TICKS = (1000, 1070, 1140, 1210)
CROSS1_TICK = 1360
DOWN5_TICK = 1540
LOAD_FRAME_TICK = 1620
CROSS2_TICK = 1700
POST_FRAME_TICK = 1800
CROSS3_TICK = 1950
SELECT_FRAME_TICK = 2050
MIN_INPUT_GAP = 60


def tick_to_ms(tick):
    return int(round(tick * 100000 / 5994))


ROUTE = ','.join(
    ['%d:start:250' % tick_to_ms(START_TICK)] +
    ['%d:square:150' % tick_to_ms(SQUARE_TICK)] +
    ['%d:down:150' % tick_to_ms(t) for t in DOWN_TICKS] +
    ['%d:cross:150' % tick_to_ms(CROSS1_TICK)] +
    ['%d:down:150' % tick_to_ms(DOWN5_TICK)] +
    ['%d:cross:150' % tick_to_ms(CROSS2_TICK)] +
    ['%d:cross:150' % tick_to_ms(CROSS3_TICK)]
)

STOP_TICK = 2100
WALL_CAP_S = 500
PROGRESS_CAP_S = 120
FRAME_PROOF_GRACE_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 2 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 1.0

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')
SNAP_TICK = re.compile(r'snap-(\d+)t-.*\.png')


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(argv):
    return subprocess.run(argv, capture_output=True, text=True)


def existing_outputs(lane):
    return [lane / name for name in ('result.json', 'boot.log', 'frames', 'mc0', 'mc1')
            if (lane / name).exists()]


def prepare_lane(lane):
    lane = Path(lane)
    taken = existing_outputs(lane)
    if taken:
        raise SystemExit('refusing to reuse %s; exists: %s (at most one boot: S1)'
                         % (lane, ', '.join(p.name for p in taken)))
    lane.mkdir(parents=True, exist_ok=True)
    snap_dir = lane / 'frames' / 'snap'
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir


def latest_frame_proof(snap_dir):
    best = None
    try:
        names = os.listdir(snap_dir)
    except OSError:
        return None
    for name in names:
        m = SNAP_TICK.fullmatch(name)
        if m:
            tick = int(m.group(1))
            if best is None or tick > best[0]:
                best = (tick, name)
    return best


def dir_bytes(path):
    total = 0
    for root, _ds, fs in os.walk(path):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def parse_route_entries(route):
    entries = []
    for part in route.split(','):
        ms, button, hold = part.split(':')
        entries.append((int(ms), button, int(hold)))
    return entries


def precheck():
    errors = []
    head = run_cmd(['git', '-C', str(FORK), 'rev-parse', 'HEAD'])
    if head.stdout.strip() != FORK_PIN_FULL:
        errors.append('fork HEAD is %r, expected %s' % (head.stdout.strip(), FORK_PIN_FULL))
    status = run_cmd(['git', '-C', str(FORK), 'status', '--porcelain'])
    if status.returncode != 0 or status.stdout.strip():
        errors.append('fork worktree not clean: rc=%d out=%r' % (status.returncode, status.stdout.strip()[:200]))
    diff = run_cmd(['git', '-C', str(FORK), 'diff', '--exit-code',
                    UPSTREAM_RUNNER_BASE, FORK_PIN_SHORT, '--', 'ps2xRuntime/src/runner'])
    if diff.returncode != 0:
        errors.append('runner-dir guard failed: rc=%d' % diff.returncode)
    big = [RUNNER, ISO, ELF, CODEGEN]
    seed_paths = [SEED_SRC / rel for rel in sorted(SEED_SHA)]
    reads = []
    for _ in range(2):
        block = {str(p): sha_of(p) for p in big + seed_paths}
        reads.append(block)
    if reads[0] != reads[1]:
        errors.append('two SHA reads differ')
    pins = {str(RUNNER): RUNNER_SHA, str(ISO): ISO_SHA,
            str(ELF): ELF_SHA, str(CODEGEN): CODEGEN_SHA}
    for rel, want in SEED_SHA.items():
        pins[str(SEED_SRC / rel)] = want
    for path, want in pins.items():
        if reads[0].get(path) != want:
            errors.append('SHA mismatch for %s: got %s' % (path, reads[0].get(path)))
    return reads, errors


def seed_cards(lane):
    mc0 = lane / 'mc0'
    mc1 = lane / 'mc1'
    if mc0.exists() or mc1.exists():
        raise SystemExit('card roots already exist; refusing reseed')
    shutil.copytree(SEED_SRC, mc0, symlinks=False)
    for rel, wall in SEED_MTIME.items():
        epoch = time.mktime(time.strptime(wall, '%Y-%m-%d %H:%M:%S'))
        os.utime(mc0 / rel, (epoch, epoch))
    mc1.mkdir(parents=True, exist_ok=True)
    return card_manifest(lane)


def card_manifest(lane):
    manifest = {}
    for name in ('mc0', 'mc1'):
        root = lane / name
        files = []
        for p in sorted(root.rglob('*')):
            if p.is_file():
                st = p.stat()
                files.append({'path': str(p.relative_to(root)), 'size': st.st_size,
                              'sha256': sha_of(p), 'mtime_ns': st.st_mtime_ns})
        manifest[name] = files
    encoded = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
    return manifest, hashlib.sha256(encoded).hexdigest()


def route_self_check():
    cases = []

    def record(name, ok, detail=''):
        cases.append((name, ok))
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    entries = parse_route_entries(ROUTE)
    record('route_first_is_start_636',
           entries[0][1] == 'start' and entries[0][0] == tick_to_ms(START_TICK),
           str(entries[0]))
    record('route_entry_count_10', len(entries) == 10, str(entries))
    squares = [e for e in entries if e[1] == 'square']
    record('route_exactly_one_square', len(squares) == 1, str(squares))
    record('route_square_tick_820',
           squares and squares[0][0] == tick_to_ms(SQUARE_TICK),
           str(squares[0] if squares else None))
    downs = [e for e in entries if e[1] == 'down']
    record('route_exactly_five_downs', len(downs) == 5, str(downs))
    record('route_down_ticks_1000_1070_1140_1210_1540',
           [e[0] for e in downs] == [tick_to_ms(t) for t in list(DOWN_TICKS) + [DOWN5_TICK]],
           str([e[0] for e in downs]))
    crosses = [e for e in entries if e[1] == 'cross']
    record('route_exactly_three_crosses', len(crosses) == 3, str(crosses))
    record('route_cross1_tick_1360',
           crosses and crosses[0][0] == tick_to_ms(CROSS1_TICK),
           str(crosses[0] if crosses else None))
    record('route_cross2_tick_1700',
           len(crosses) >= 2 and crosses[1][0] == tick_to_ms(CROSS2_TICK),
           str(crosses[1] if len(crosses) >= 2 else None))
    record('route_cross3_tick_1950',
           len(crosses) == 3 and crosses[2][0] == tick_to_ms(CROSS3_TICK),
           str(crosses[2] if len(crosses) == 3 else None))
    record('route_cross_holds_150', all(e[2] == 150 for e in crosses),
           str([e[2] for e in crosses]))
    record('route_input_order_spine_plus_d5_c2_c3',
           [e[1] for e in entries] == ['start', 'square', 'down', 'down',
                                       'down', 'down', 'cross', 'down', 'cross', 'cross'],
           str([e[1] for e in entries]))
    input_ticks = ([START_TICK, SQUARE_TICK] + list(DOWN_TICKS)
                   + [CROSS1_TICK, DOWN5_TICK, CROSS2_TICK, CROSS3_TICK])
    gaps = [b - a for a, b in zip(input_ticks, input_ticks[1:])]
    record('route_all_input_gaps_ge_60', all(g >= MIN_INPUT_GAP for g in gaps),
           'gaps=%s' % gaps)
    record('route_load_frame_between_d5_and_c2',
           DOWN5_TICK < LOAD_FRAME_TICK < CROSS2_TICK,
           'D5=%d Fload=%d C2=%d' % (DOWN5_TICK, LOAD_FRAME_TICK, CROSS2_TICK))
    record('route_post_frame_between_c2_and_c3',
           CROSS2_TICK < POST_FRAME_TICK < CROSS3_TICK,
           'C2=%d Fpost=%d C3=%d' % (CROSS2_TICK, POST_FRAME_TICK, CROSS3_TICK))
    record('route_select_frame_between_c3_and_stop',
           CROSS3_TICK < SELECT_FRAME_TICK < STOP_TICK,
           'C3=%d Fsel=%d stop=%d' % (CROSS3_TICK, SELECT_FRAME_TICK, STOP_TICK))
    record('route_stop_tick_2100', STOP_TICK == 2100, str(STOP_TICK))
    record('caps_wall_500', WALL_CAP_S == 500, str(WALL_CAP_S))
    record('caps_progress_120', PROGRESS_CAP_S == 120, str(PROGRESS_CAP_S))
    record('caps_log_16mib', LOG_CAP_BYTES == 16 * 1024 * 1024, str(LOG_CAP_BYTES))
    record('caps_frames_le_2gib', FRAMES_CAP_BYTES <= 2 * 1024 * 1024 * 1024,
           str(FRAMES_CAP_BYTES))
    record('caps_frame_proof_grace_120', FRAME_PROOF_GRACE_S == 120,
           str(FRAME_PROOF_GRACE_S))
    record('seed_six_files', len(SEED_SHA) == 6, str(sorted(SEED_SHA)))
    record('seed_mtime_covers_seed', set(SEED_MTIME) >= set(SEED_SHA) |
           {'BASLUS-20772-GAM0001', 'BASLUS-20772-SET0001'},
           str(sorted(SEED_MTIME)))

    with tempfile.TemporaryDirectory(prefix='e55d16-lane-self-') as tmp:
        lane = Path(tmp) / 'S1'
        snap = prepare_lane(lane)
        record('lane_setup_fresh_ok', snap.is_dir() and snap == lane / 'frames' / 'snap',
               str(snap))
        try:
            prepare_lane(lane)
            record('lane_setup_second_refuses', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_second_refuses', 'frames' in str(exc), str(exc)[:120])
        (lane / 'mc0').mkdir()
        try:
            prepare_lane(Path(tmp) / 'S1')
            record('lane_setup_mc0_blocks', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_mc0_blocks', 'mc0' in str(exc), str(exc)[:120])

    with tempfile.TemporaryDirectory(prefix='e55d16-proof-self-') as tmp:
        snap = Path(tmp) / 'snap'
        record('frame_proof_missing_dir', latest_frame_proof(snap) is None)
        snap.mkdir()
        record('frame_proof_empty', latest_frame_proof(snap) is None)
        (snap / 'snap-002099t-00010.00s.png').write_bytes(b'f1')
        (snap / 'snap-002101t-00012.00s.png').write_bytes(b'f2')
        got = latest_frame_proof(snap)
        record('frame_proof_max_tick', got == (2101, 'snap-002101t-00012.00s.png'),
               str(got))
        record('frame_proof_meets_stop', got is not None and got[0] >= STOP_TICK,
               str(got))
    return 0 if all(ok for _, ok in cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--label', choices=('S1',))
    ap.add_argument('--self-check', action='store_true')
    args = ap.parse_args()
    if args.self_check:
        return route_self_check()
    if not args.label:
        ap.error('need --label S1 (or --self-check)')
    lane = WORK / 'run' / args.label
    snap_dir = prepare_lane(lane)
    log = lane / 'boot.log'
    frames_dir = lane / 'frames'
    result_path = lane / 'result.json'

    reads, errors = precheck()
    if errors:
        raise SystemExit('precheck failed (no boot): ' + '; '.join(errors))
    if route_self_check() != 0:
        raise SystemExit('route self-check failed (no boot)')

    card_files, card_sha = seed_cards(lane)
    if len(card_files['mc0']) != 6 or card_files['mc1']:
        raise SystemExit('seeded card layout wrong: %s' % card_sha)

    slot = claim('E55D16-' + args.label)
    while slot is None:
        print('both mini lease slots busy; retrying in 60 s', flush=True)
        time.sleep(60)
        slot = claim('E55D16-' + args.label)
    proc = None
    stop_snap = threading.Event()
    result = {'label': args.label, 'stop_tick': STOP_TICK,
              'wall_cap_s': WALL_CAP_S, 'progress_cap_s': PROGRESS_CAP_S,
              'frame_proof_grace_s': FRAME_PROOF_GRACE_S,
              'log_cap_bytes': LOG_CAP_BYTES, 'frames_cap_bytes': FRAMES_CAP_BYTES,
              'fork_pin': FORK_PIN_SHORT, 'fork_pin_full': FORK_PIN_FULL,
              'runner': str(RUNNER), 'elf': str(ELF), 'iso': str(ISO),
              'codegen': str(CODEGEN), 'seed_src': str(SEED_SRC), 'cwd': str(lane),
              'frames_dir': str(frames_dir),
              'route': ROUTE, 'start_tick': START_TICK,
              'square_tick': SQUARE_TICK, 'down_ticks': list(DOWN_TICKS),
              'cross1_tick': CROSS1_TICK, 'down5_tick': DOWN5_TICK,
              'load_frame_tick': LOAD_FRAME_TICK, 'cross2_tick': CROSS2_TICK,
              'post_frame_tick': POST_FRAME_TICK, 'cross3_tick': CROSS3_TICK,
              'select_frame_tick': SELECT_FRAME_TICK,
              'card_initial_files': card_files,
              'card_initial_sha256': card_sha, 'sha_reads': reads}
    env = dict(os.environ)
    for key in tuple(env):
        if key.startswith('PS2X_'):
            env.pop(key)
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1',
               PS2X_DETERMINISTIC='1', PS2X_DET_HASH_EVERY='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'),
               PS2X_FRAME_DUMP_DIR=str(frames_dir),
               PS2X_MISSING_FUNCTION_POLICY='stop', COPYFILE_DISABLE='1')
    result['env'] = {key: value for key, value in env.items() if key.startswith('PS2X_')}
    result['load_start'] = os.getloadavg()

    def snapshotter(t0):
        latest = frames_dir / 'upload-latest.png'
        latest_txt = frames_dir / 'upload-latest.txt'
        while not stop_snap.wait(SNAP_PERIOD_S):
            el = time.monotonic() - t0
            try:
                tail = log.read_bytes()[-32768:] if log.exists() else b''
                ticks = HASH_TICK.findall(tail)
                tick = int(ticks[-1]) if ticks else -1
            except OSError:
                tick = -1
            try:
                if latest.exists():
                    shutil.copyfile(latest, snap_dir / ('snap-%dt-%07.2fs.png' % (tick, el)))
                if latest_txt.exists():
                    shutil.copyfile(latest_txt, snap_dir / ('snap-%dt-%07.2fs.txt' % (tick, el)))
            except OSError:
                pass

    try:
        t0 = time.monotonic()
        with log.open('wb') as output:
            proc = subprocess.Popen([str(RUNNER), str(ELF)], cwd=lane, env=env,
                                    stdout=output, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label,
                              'slot': slot, 'runner_pid': proc.pid,
                              'card_initial_sha256': card_sha}), flush=True)
            th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
            th.start()
            last_tick = 0
            last_progress = t0
            phase2_start = None
            frame_proof = None
            bound = None
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
                    tail = log.read_bytes()[-32768:]
                    if any(marker in tail for marker in HASH_ERROR_MARKERS):
                        bound = 'hash_error'
                        break
                    matches = HASH_TICK.findall(tail)
                    if matches:
                        tick = int(matches[-1])
                        if tick > last_tick:
                            last_tick = tick
                            last_progress = now
                    if now - last_progress >= PROGRESS_CAP_S:
                        bound = 'progress_cap'
                        break
                    if phase2_start is None:
                        if last_tick >= STOP_TICK:
                            phase2_start = now
                    else:
                        frame_proof = latest_frame_proof(snap_dir)
                        if frame_proof is not None and frame_proof[0] >= STOP_TICK:
                            bound = 'target'
                            break
                        if now - phase2_start >= FRAME_PROOF_GRACE_S:
                            bound = 'frame_unproven'
                            break
                    time.sleep(0.5)
            finally:
                stop_snap.set()
                th.join(timeout=5)
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
            result['bound'] = bound
            result['elapsed_s'] = round(time.monotonic() - t0, 3)
            result['last_hash_tick'] = last_tick
            result['phase2_extra_s'] = (round(time.monotonic() - phase2_start, 3)
                                        if phase2_start is not None else 0.0)
            result['frame_proof'] = ({'tick': frame_proof[0], 'file': frame_proof[1]}
                                     if frame_proof is not None else None)
            result['log_bytes'] = log.stat().st_size
            result['frames_bytes'] = dir_bytes(frames_dir)
            result['load_end'] = os.getloadavg()
        final_files, final_sha = card_manifest(lane)
        result['card_final_files'] = final_files
        result['card_final_sha256'] = final_sha
        result_path.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({key: value for key, value in result.items() if key != 'env'}), flush=True)
        return 0 if bound == 'target' else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        release(slot)


if __name__ == '__main__':
    sys.exit(main())
