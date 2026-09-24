#!/usr/bin/env python3
"""E55D12 Part 1: ONE bounded Load-game-selection boot (prepared, NOT run).

DO NOT RUN until the orchestrator reviews the exact script SHA and explicitly
releases Part 2 in the worker pane. Single Mac mini boot only after release.

Route (PS2X_PAD_SCRIPT_CLOCK=vsync; guest ms = tick * 100000 / 5994):
  - Proven E55D11 spine, unchanged: I26 title START at guest tick 636
    (10611 ms), hold 250 ms; ONE Square at tick 820 (13680 ms), hold 150 ms
    (E55D10-proved Options opener); FOUR separate Down pulses at ticks 1000 /
    1070 / 1140 / 1210 (16683 / 17851 / 19019 / 20187 ms), hold 150 ms each;
    ONE Cross (C1) at tick 1360 (22689 ms), hold 150 ms, selecting the
    Save/Load row. E55D11 viewed the Save/Load submenu by tick 1454 with
    Save game highlighted and Load game one row below (ORCH-GATE-P2).
  - ONE separate Down (D5) at guest tick 1540 (25692 ms), hold 150 ms:
    Save game -> Load game (gap 180 from C1, ~86 after the observed 1454
    submenu settle; >= 60 by construction).
  - Load-highlight frame target F_LOAD = 1620 (27027 ms): settled full-frame
    capture proving the Load game highlight before C2 (80 ticks after D5).
  - ONE Cross (C2) at guest tick 1700 (28362 ms), hold 150 ms, selecting
    Load game (gap 160 from D5, 80 after F_LOAD target).
  - Post-choice settled full-frame target F_POST = 1800 (30030 ms), 100
    ticks after C2. Stop tick = 1800.
  - No other game input; no card seeding, no card write.

Card-API observation: the pinned E55D3 diagnostic runner carries the
ps2_e55d3_pad_card_probe.h taps (GetDir/Read/pad). This script sets
PS2X_PAD_CARD_PROBE=<lane>/probe.log so every sceMcGetDir / sceMcRead /
scePadRead call is recorded (getdir/mcread/pad lines + 16 MiB hard cap).
Fresh empty card roots only (refuses non-empty at start). Early title/menu
GetDir calls (E55D11 saw 4 at vsync 118/122/126/223, all ok=0 reason=empty)
are separated from choice-triggered calls at/after C2 tick 1700 by vsync.

Stop only after tick >= 1800 AND a persisted snap PNG tagged >= 1800
(frame_unproven/OTHER if the 120 s grace expires without the proof).
Stop early on any unexpected screen (title/menu/submenu not reached,
ambiguous/unreadable frame, script/input mismatch -> OTHER).

Method (adapted from E55D11's e55d11_boot.py, read-only source):
  per-run cwd (~/dev/ssx3-work/E55D12/run/<label>, reserved for the released
  run only), fresh empty card roots, one mini P-lane slot held only during
  the boot, wall cap 500 s, no-tick-progress cap 120 s, boot log cap 16 MiB
  (closed log). Kill only the recorded PID; release the lease even on
  failure. Pre-boot checks: fork at exact bab6eb3, clean worktree,
  runner-dir guard vs upstream 14b1e5cb, and two matching SHA reads of
  runner/ISO/ELF/codegen against the pins below. prepare_lane() refuses
  reuse BEFORE creating the frames dir (checking after creating would
  refuse every fresh invocation). Refuses to start if result.json,
  boot.log, probe.log, or the frames dir already exists.

Frames: PS2X_FRAME_DUMP_DIR=<lane>/frames; a snapshotter thread copies
  upload-latest.png/.txt into <lane>/frames/snap/ every 1.0 s wall, tagging
  each copy with the latest [det-hash:v1] tick seen in boot.log at copy time
  (snap-<tick>t-<elapsed>s.{png,txt}). Full-frame PNGs are orchestrator
  evidence; this script makes no readability claim (check.py cannot either).

Usage: e55d12_boot.py --label S1          (ONE boot only, after release)
       e55d12_boot.py --self-check        (pure helper tests, no boot/lease)
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

WORK = Path('/Users/brad/dev/ssx3-work/E55D12')
FORK = Path('/Users/brad/dev/ssx3-work/E55D3/PS2Recomp')
RUNNER = Path('/Users/brad/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')

FORK_PIN_FULL = 'bab6eb382673155ffd756fe8db265964eeff9703'
FORK_PIN_SHORT = 'bab6eb3'
UPSTREAM_RUNNER_BASE = '14b1e5cb'
RUNNER_SHA = 'e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f'
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'

# Planned guest ticks (E55D11 spine + E55D11 observation: Save/Load submenu
# settled by ~1454 with Save game highlighted, Load game one row below).
START_TICK = 636
SQUARE_TICK = 820
DOWN_TICKS = (1000, 1070, 1140, 1210)
CROSS1_TICK = 1360
CROSS_TICK = CROSS1_TICK  # alias: first Cross (E55D11-compatible name)
DOWN5_TICK = 1540
LOAD_FRAME_TICK = 1620
CROSS2_TICK = 1700
POST_FRAME_TICK = 1800
MIN_INPUT_GAP = 60


def tick_to_ms(tick):
    return int(round(tick * 100000 / 5994))


ROUTE = ','.join(
    ['%d:start:250' % tick_to_ms(START_TICK)] +
    ['%d:square:150' % tick_to_ms(SQUARE_TICK)] +
    ['%d:down:150' % tick_to_ms(t) for t in DOWN_TICKS] +
    ['%d:cross:150' % tick_to_ms(CROSS1_TICK)] +
    ['%d:down:150' % tick_to_ms(DOWN5_TICK)] +
    ['%d:cross:150' % tick_to_ms(CROSS2_TICK)]
)

STOP_TICK = POST_FRAME_TICK
WALL_CAP_S = 500
PROGRESS_CAP_S = 120
FRAME_PROOF_GRACE_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 2 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 1.0
PROBE_NAME = 'probe.log'

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
    """Output paths that already exist (any one blocks a fresh boot)."""
    return [lane / name for name in ('result.json', 'boot.log', PROBE_NAME, 'frames')
            if (lane / name).exists()]


def prepare_lane(lane):
    """Refuse reuse BEFORE creating anything, then create lane + snap dirs.

    Setup order matters: the reuse check must run before the frames dir
    exists, otherwise every invocation would refuse itself. Returns snap_dir.
    Raises SystemExit if any prior output exists.
    """
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
    """Return (tick, filename) of the highest-tick snap PNG, or None.

    The snapshotter tags each copy snap-<tick>t-<elapsed>s.png with the
    latest det-hash tick at copy time, so a tag >= STOP_TICK proves a
    full-frame copy persisted after the stop tick was reached.
    """
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
    """Parse 'ms:button:hold,...' into [(ms, button, hold)]."""
    entries = []
    for part in route.split(','):
        ms, button, hold = part.split(':')
        entries.append((int(ms), button, int(hold)))
    return entries


def precheck():
    """Verify fork pin, clean tree, runner-dir guard, and two SHA reads."""
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
    reads = []
    for _ in range(2):
        block = {str(p): sha_of(p) for p in (RUNNER, ISO, ELF, CODEGEN)}
        reads.append(block)
    if reads[0] != reads[1]:
        errors.append('two SHA reads differ: %r vs %r' % (reads[0], reads[1]))
    pins = {str(RUNNER): RUNNER_SHA, str(ISO): ISO_SHA,
            str(ELF): ELF_SHA, str(CODEGEN): CODEGEN_SHA}
    for path, want in pins.items():
        if reads[0].get(path) != want:
            errors.append('SHA mismatch for %s: got %s' % (path, reads[0].get(path)))
    return reads, errors


def card_manifest(lane):
    """Manifest of fresh card roots: per-file relpath, size, sha256, mtime_ns."""
    manifest = {}
    for name in ('mc0', 'mc1'):
        root = lane / name
        root.mkdir(parents=True, exist_ok=True)
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
    """Pure route/limit checks: E55D11 spine + D5/C2 Load-game choice."""
    cases = []

    def record(name, ok, detail=''):
        cases.append((name, ok))
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    entries = parse_route_entries(ROUTE)
    record('route_first_is_start_636',
           entries[0][1] == 'start' and entries[0][0] == tick_to_ms(START_TICK),
           str(entries[0]))
    record('route_entry_count_9', len(entries) == 9, str(entries))
    squares = [e for e in entries if e[1] == 'square']
    record('route_exactly_one_square', len(squares) == 1, str(squares))
    record('route_square_tick_820',
           squares and squares[0][0] == tick_to_ms(SQUARE_TICK),
           str(squares[0] if squares else None))
    record('route_square_hold_150',
           squares and squares[0][2] == 150,
           str(squares[0] if squares else None))
    downs = [e for e in entries if e[1] == 'down']
    record('route_exactly_five_downs', len(downs) == 5, str(downs))
    record('route_down_ticks_1000_1070_1140_1210_1540',
           [e[0] for e in downs] == [tick_to_ms(t) for t in list(DOWN_TICKS) + [DOWN5_TICK]],
           str([e[0] for e in downs]))
    record('route_down_holds_150', all(e[2] == 150 for e in downs),
           str([e[2] for e in downs]))
    crosses = [e for e in entries if e[1] == 'cross']
    record('route_exactly_two_crosses', len(crosses) == 2, str(crosses))
    record('route_cross1_tick_1360',
           crosses and crosses[0][0] == tick_to_ms(CROSS1_TICK),
           str(crosses[0] if crosses else None))
    record('route_cross2_tick_1700',
           len(crosses) == 2 and crosses[1][0] == tick_to_ms(CROSS2_TICK),
           str(crosses[1] if len(crosses) == 2 else None))
    record('route_cross_holds_150', all(e[2] == 150 for e in crosses),
           str([e[2] for e in crosses]))
    record('route_input_order_spine_plus_d5_c2',
           [e[1] for e in entries] == ['start', 'square', 'down', 'down',
                                       'down', 'down', 'cross', 'down', 'cross'],
           str([e[1] for e in entries]))
    record('route_no_button_but_start_square_down_cross',
           all(b in ('start', 'square', 'down', 'cross') for _, b, _ in entries),
           str(sorted(set(b for _, b, _ in entries))))
    input_ticks = ([START_TICK, SQUARE_TICK] + list(DOWN_TICKS)
                   + [CROSS1_TICK, DOWN5_TICK, CROSS2_TICK])
    gaps = [b - a for a, b in zip(input_ticks, input_ticks[1:])]
    record('route_all_input_gaps_ge_60', all(g >= MIN_INPUT_GAP for g in gaps),
           'gaps=%s' % gaps)
    record('route_d5_after_c1_settle',
           CROSS1_TICK < DOWN5_TICK and DOWN5_TICK - CROSS1_TICK >= MIN_INPUT_GAP,
           'C1=%d D5=%d gap=%d' % (CROSS1_TICK, DOWN5_TICK, DOWN5_TICK - CROSS1_TICK))
    record('route_load_frame_between_d5_and_c2',
           DOWN5_TICK < LOAD_FRAME_TICK < CROSS2_TICK,
           'D5=%d Fload=%d C2=%d' % (DOWN5_TICK, LOAD_FRAME_TICK, CROSS2_TICK))
    record('route_post_frame_after_c2', POST_FRAME_TICK > CROSS2_TICK,
           'C2=%d Fpost=%d' % (CROSS2_TICK, POST_FRAME_TICK))
    record('route_stop_tick_is_post_frame', STOP_TICK == POST_FRAME_TICK, str(STOP_TICK))
    record('caps_wall_500', WALL_CAP_S == 500, str(WALL_CAP_S))
    record('caps_progress_120', PROGRESS_CAP_S == 120, str(PROGRESS_CAP_S))
    record('caps_log_16mib', LOG_CAP_BYTES == 16 * 1024 * 1024, str(LOG_CAP_BYTES))
    record('caps_frames_le_2gib', FRAMES_CAP_BYTES <= 2 * 1024 * 1024 * 1024,
           str(FRAMES_CAP_BYTES))
    record('caps_frame_proof_grace_120', FRAME_PROOF_GRACE_S == 120,
           str(FRAME_PROOF_GRACE_S))

    with tempfile.TemporaryDirectory(prefix='e55d12-lane-self-') as tmp:
        lane = Path(tmp) / 'S1'
        snap = prepare_lane(lane)
        record('lane_setup_fresh_ok', snap.is_dir() and snap == lane / 'frames' / 'snap',
               str(snap))
        try:
            prepare_lane(lane)
            record('lane_setup_second_refuses', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_second_refuses', 'frames' in str(exc), str(exc)[:120])
        try:
            prepare_lane(Path(tmp) / 'S1')
            record('lane_setup_frames_blocks', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_frames_blocks', 'frames' in str(exc), str(exc)[:120])
        (lane / 'result.json').write_text('{}')
        try:
            prepare_lane(lane)
            record('lane_setup_result_blocks', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_result_blocks', 'result.json' in str(exc), str(exc)[:120])
        (lane / PROBE_NAME).write_text('x')
        try:
            prepare_lane(Path(tmp) / 'S1')
            record('lane_setup_probe_blocks', False, 'no refusal raised')
        except SystemExit as exc:
            record('lane_setup_probe_blocks', PROBE_NAME in str(exc), str(exc)[:120])

    with tempfile.TemporaryDirectory(prefix='e55d12-proof-self-') as tmp:
        snap = Path(tmp) / 'snap'
        record('frame_proof_missing_dir', latest_frame_proof(snap) is None)
        snap.mkdir()
        record('frame_proof_empty', latest_frame_proof(snap) is None)
        (snap / 'snap-001799t-00010.00s.png').write_bytes(b'f1')
        (snap / 'snap-001800t-00011.00s.txt').write_bytes(b't')
        (snap / 'snap-001801t-00012.00s.png').write_bytes(b'f2')
        got = latest_frame_proof(snap)
        record('frame_proof_max_tick', got == (1801, 'snap-001801t-00012.00s.png'),
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
    probe_path = lane / PROBE_NAME
    frames_dir = lane / 'frames'
    result_path = lane / 'result.json'

    reads, errors = precheck()
    if errors:
        raise SystemExit('precheck failed (no boot): ' + '; '.join(errors))

    card_files, card_sha = card_manifest(lane)
    if any(card_files.values()):
        raise SystemExit('card roots are not empty at start')
    if route_self_check() != 0:
        raise SystemExit('route self-check failed (no boot)')

    slot = claim('E55D12-' + args.label)
    while slot is None:
        print('both mini lease slots busy; retrying in 60 s', flush=True)
        time.sleep(60)
        slot = claim('E55D12-' + args.label)
    proc = None
    stop_snap = threading.Event()
    result = {'label': args.label, 'stop_tick': STOP_TICK,
              'wall_cap_s': WALL_CAP_S, 'progress_cap_s': PROGRESS_CAP_S,
              'frame_proof_grace_s': FRAME_PROOF_GRACE_S,
              'log_cap_bytes': LOG_CAP_BYTES, 'frames_cap_bytes': FRAMES_CAP_BYTES,
              'fork_pin': FORK_PIN_SHORT, 'fork_pin_full': FORK_PIN_FULL,
              'runner': str(RUNNER), 'elf': str(ELF), 'iso': str(ISO),
              'codegen': str(CODEGEN), 'cwd': str(lane),
              'frames_dir': str(frames_dir), 'probe_file': str(probe_path),
              'route': ROUTE, 'start_tick': START_TICK,
              'square_tick': SQUARE_TICK, 'down_ticks': list(DOWN_TICKS),
              'cross1_tick': CROSS1_TICK, 'cross_tick': CROSS1_TICK,
              'down5_tick': DOWN5_TICK, 'load_frame_tick': LOAD_FRAME_TICK,
              'cross2_tick': CROSS2_TICK, 'post_frame_tick': POST_FRAME_TICK,
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
               PS2X_PAD_CARD_PROBE=str(probe_path),
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
                        # Post-1800 full-frame proof: the 1 s snapshotter may
                        # not yet have copied F_POST when tick 1800 lands.
                        # Stop only once a snap PNG tagged >= STOP_TICK is
                        # persisted; without it the run is OTHER.
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
            try:
                result['probe_bytes'] = probe_path.stat().st_size
            except OSError:
                result['probe_bytes'] = 0
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
