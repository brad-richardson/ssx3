#!/usr/bin/env python3
"""E55D9 Part 1: ONE bounded observed Main Menu navigation boot (prepared, NOT run).

DO NOT RUN until the orchestrator reviews the exact script SHA and explicitly
releases Part 2 in the worker pane. Single Mac mini boot only after release.

Route (PS2X_PAD_SCRIPT_CLOCK=vsync; guest ms = tick * 100000 / 5994):
  - I26 title START at guest tick 636 (10611 ms), hold 250 ms.
  - NO Cross at tick 766 (the I26-FAST Main Menu press is deliberately omitted).
  - Settled full Main Menu frame dump before the first navigation input
    (planned frame tick F0 = 760, ~52 ticks after the I26-measured settle 708).
  - At most four one-step Down pulses (hold 150 ms each), planned press ticks
    D1..D4 = 820, 920, 1020, 1120 (gaps of 100 guest ticks, >= 45 required).
  - One full frame capture after each settle, planned frame ticks
    F1..F4 = 870, 970, 1070, 1170 (50 ticks after each Down).
  - No Cross, no card write, no seeded-card change in this part.
  - Stop early if an Options/Save/profile item is visibly selected, after the
    fourth pulse frame, or on any unexpected screen (title/menu not reached,
    ambiguous/unreadable frame, script/input mismatch -> OTHER).

Method (adapted from E55D4 e55d4_boot.py, read-only source: no fork edit):
  per-run cwd (~/dev/ssx3-work/E55D9/run/<label>, reserved for the released
  run only), fresh empty card roots, one mini P-lane slot held only during
  the boot, wall cap 500 s, no-tick-progress cap 120 s, boot log cap 16 MiB
  (closed log), probe NOT used in this part. Kill only the recorded PID;
  release the lease even on failure. Pre-boot checks: fork at exact bab6eb3,
  clean worktree, runner-dir guard vs upstream 14b1e5cb, and two matching SHA
  reads of runner/ISO/ELF/codegen against the pins below. Refuses to start if
  result.json, boot.log, or the frames dir already exists.

Frames: PS2X_FRAME_DUMP_DIR=<lane>/frames; a snapshotter thread copies
  upload-latest.png/.txt into <lane>/frames/snap/ every 1.0 s wall, tagging
  each copy with the latest [det-hash:v1] tick seen in boot.log at copy time
  (snap-<tick>t-<elapsed>s.{png,txt}). Full-frame PNGs are orchestrator
  evidence; this script makes no readability claim (check.py cannot either).

Usage: e55d9_boot.py --label M1          (ONE boot only, after release)
       e55d9_boot.py --self-check        (pure helper tests, no boot/lease)
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

WORK = Path('/Users/brad/dev/ssx3-work/E55D9')
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

# Planned guest ticks (I26-FAST spine: title settles ~570, menu settles ~708).
START_TICK = 636
MENU_FRAME_TICK = 760
DOWN_TICKS = (820, 920, 1020, 1120)
POST_FRAME_TICKS = (870, 970, 1070, 1170)
MIN_DOWN_GAP = 45
MAX_DOWN_PULSES = 4


def tick_to_ms(tick):
    return int(round(tick * 100000 / 5994))


ROUTE = ','.join(
    ['%d:start:250' % tick_to_ms(START_TICK)] +
    ['%d:down:150' % tick_to_ms(t) for t in DOWN_TICKS]
)

STOP_TICK = POST_FRAME_TICKS[-1]
WALL_CAP_S = 500
PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024
FRAMES_CAP_BYTES = 2 * 1024 * 1024 * 1024
SNAP_PERIOD_S = 1.0

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')


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
    return [lane / name for name in ('result.json', 'boot.log', 'frames')
            if (lane / name).exists()]


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
    """Pure route/limit checks: START tick, <=4 Downs, gaps, no Cross."""
    cases = []

    def record(name, ok, detail=''):
        cases.append((name, ok))
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    entries = parse_route_entries(ROUTE)
    record('route_first_is_start_636',
           entries[0][1] == 'start' and entries[0][0] == tick_to_ms(START_TICK),
           str(entries[0]))
    downs = [e for e in entries if e[1] == 'down']
    crosses = [e for e in entries if e[1] == 'cross']
    record('route_down_count_bounded', 1 <= len(downs) <= MAX_DOWN_PULSES, str(len(downs)))
    record('route_no_cross', crosses == [], str(crosses))
    down_ticks = list(DOWN_TICKS[:len(downs)])
    gaps = [b - a for a, b in zip(down_ticks, down_ticks[1:])]
    record('route_down_gaps_ge_45', all(g >= MIN_DOWN_GAP for g in gaps), str(gaps))
    record('route_menu_frame_before_first_down', MENU_FRAME_TICK < down_ticks[0],
           'F0=%d D1=%d' % (MENU_FRAME_TICK, down_ticks[0]))
    record('route_post_frames_after_downs',
           all(f > d for f, d in zip(POST_FRAME_TICKS, DOWN_TICKS)),
           str(list(zip(DOWN_TICKS, POST_FRAME_TICKS))))
    record('route_stop_tick_is_last_frame', STOP_TICK == POST_FRAME_TICKS[-1], str(STOP_TICK))
    record('route_no_button_but_start_down',
           all(b in ('start', 'down') for _, b, _ in entries),
           str(sorted(set(b for _, b, _ in entries))))
    record('caps_wall_500', WALL_CAP_S == 500, str(WALL_CAP_S))
    record('caps_progress_120', PROGRESS_CAP_S == 120, str(PROGRESS_CAP_S))
    record('caps_log_16mib', LOG_CAP_BYTES == 16 * 1024 * 1024, str(LOG_CAP_BYTES))
    return 0 if all(ok for _, ok in cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--label', choices=('M1',))
    ap.add_argument('--self-check', action='store_true')
    args = ap.parse_args()
    if args.self_check:
        return route_self_check()
    if not args.label:
        ap.error('need --label M1 (or --self-check)')
    lane = WORK / 'run' / args.label
    lane.mkdir(parents=True, exist_ok=True)
    log = lane / 'boot.log'
    frames_dir = lane / 'frames'
    snap_dir = frames_dir / 'snap'
    snap_dir.mkdir(parents=True, exist_ok=True)
    result_path = lane / 'result.json'
    taken = existing_outputs(lane)
    if taken:
        raise SystemExit('refusing to reuse %s; exists: %s (at most one boot: M1)'
                         % (lane, ', '.join(p.name for p in taken)))

    reads, errors = precheck()
    if errors:
        raise SystemExit('precheck failed (no boot): ' + '; '.join(errors))

    card_files, card_sha = card_manifest(lane)
    if any(card_files.values()):
        raise SystemExit('card roots are not empty at start')
    if route_self_check() != 0:
        raise SystemExit('route self-check failed (no boot)')

    slot = claim('E55D9-' + args.label)
    while slot is None:
        print('both mini lease slots busy; retrying in 60 s', flush=True)
        time.sleep(60)
        slot = claim('E55D9-' + args.label)
    proc = None
    stop_snap = threading.Event()
    result = {'label': args.label, 'stop_tick': STOP_TICK,
              'wall_cap_s': WALL_CAP_S, 'progress_cap_s': PROGRESS_CAP_S,
              'log_cap_bytes': LOG_CAP_BYTES, 'frames_cap_bytes': FRAMES_CAP_BYTES,
              'fork_pin': FORK_PIN_SHORT, 'fork_pin_full': FORK_PIN_FULL,
              'runner': str(RUNNER), 'elf': str(ELF), 'iso': str(ISO),
              'codegen': str(CODEGEN), 'cwd': str(lane),
              'frames_dir': str(frames_dir),
              'route': ROUTE, 'start_tick': START_TICK,
              'menu_frame_tick': MENU_FRAME_TICK,
              'down_ticks': list(DOWN_TICKS), 'post_frame_ticks': list(POST_FRAME_TICKS),
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
                    if last_tick >= STOP_TICK:
                        bound = 'target'
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
