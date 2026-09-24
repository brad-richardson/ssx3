#!/usr/bin/env python3
"""E55D5 Part 1: one bounded pinned pad-B boot (label B1) on the Mac mini.

One predeclared vsync-pad change against the E55D4 A/A baseline: the same
I26-FAST route except exactly `33517:cross:200` -> `33517:square:200`
(after race start, around tick2010, before tick2053). All other route
entries, ISO/ELF/codegen, runner SHA, deterministic mode, movie bypass,
probe/hash flags and empty cards are as E55D4. No source or binary mutation.

DO NOT RUN until the orchestrator explicitly releases this exact script SHA
in the worker pane. At most one boot total (B1), slot lease only during boot.

Method (from E55D4 e55d4_boot.py): per-run cwd, distinct probe file, fresh
cards, one mini P-lane slot held only during the boot, wall cap 500 s,
no-tick-progress cap 120 s, boot log cap 4 MiB, probe cap 16 MiB. Kill only
the recorded PID; release the lease even on failure. Pre-boot checks: fork
at exact bab6eb3, clean worktree, runner dir matches upstream 14b1e5cb, and
two matching SHA reads of runner/ISO/ELF/codegen against the pins below.
Refuses to start if result.json, boot.log, or probe.log already exists.

Flush-proof stop (E55D3 tap flushes the probe file only every 16 lines, and
SIGTERM can lose the unflushed tail): after hash tick 2053 is observed, the
run continues until a *persisted complete* probe line with vsync > 2053 is
seen, proving every line at vsync <= 2053 was flushed (the tap writes
sequentially through one stream, so a persisted later line implies the
earlier prefix is durable). Bounded extra wait: 180 s wall and 60 ticks past
2053. Without that proof the run ends bound 'flush_unproven' (OTHER).
The comparator compares only probe lines with vsync <= 2053.

Usage: e55d5_boot.py --label B1
       e55d5_boot.py --self-check   (pure helper tests only, no boot/lease)
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release

WORK = Path('/Users/brad/dev/ssx3-work/E55D5')
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

# E55D4 I26-FAST route with exactly one entry changed:
#   33517:cross:200 -> 33517:square:200 (pulse start ~tick2010, hold 200 ms).
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
         '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
         '22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,'
         '29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,'
         '31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:square:200,33768:down:700,34518:cross:200,34769:down:700,'
         '35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,'
         '37521:cross:200,37772:down:700,38522:down:30000')

STOP_TICK = 2053
WALL_CAP_S = 500
PROGRESS_CAP_S = 120
EXTRA_WAIT_S = 180
EXTRA_TICKS = 60
LOG_CAP_BYTES = 4 * 1024 * 1024
PROBE_CAP_BYTES = 16 * 1024 * 1024

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
HASH_ERROR_MARKERS = (b'[det-hash] null', b'[det-hash] line cap', b'[det-hash] invalid')
PROBE_VSYNC = re.compile(rb'vsync=(\d+)')
PAD_WORDS = re.compile(r'gamepad|controller|joystick', re.IGNORECASE)


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
    return [lane / name for name in ('result.json', 'boot.log', 'probe.log')
            if (lane / name).exists()]


def split_persisted(data):
    """Split probe bytes into (complete_lines, truncated).

    Only newline-terminated lines count as persisted; a trailing chunk
    without '\\n' is a partial write (or torn tail) and is excluded.
    """
    if not data:
        return ([], False)
    if data.endswith(b'\n'):
        return (data[:-1].split(b'\n'), False)
    chunks = data.split(b'\n')
    return (chunks[:-1], True)


def probe_proof(probe_path):
    """Return (max_vsync, complete_lines, truncated) over persisted lines."""
    try:
        data = Path(probe_path).read_bytes()
    except OSError:
        return (None, 0, False)
    complete, truncated = split_persisted(data)
    vsyncs = [int(m.group(1)) for line in complete
              for m in [PROBE_VSYNC.search(line)] if m]
    return ((max(vsyncs) if vsyncs else None), len(complete), truncated)


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


def hidutil_check():
    """Record whether any HID gamepad/controller/joystick is present."""
    try:
        proc = run_cmd(['hidutil', 'list'])
        out = (proc.stdout or '') + (proc.stderr or '')
    except (OSError, FileNotFoundError) as exc:
        return {'available': False, 'gamepad_like': False, 'note': 'hidutil failed: %s' % exc}
    hits = sorted(set(PAD_WORDS.findall(out)))
    return {'available': True, 'gamepad_like': bool(hits),
            'matches': hits, 'output_head': out[:4096]}


def boot_self_check():
    """Pure helper tests: reuse refusal, persisted-split, and proof logic."""
    cases = []

    def record(name, ok, detail=''):
        cases.append((name, ok))
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    with tempfile.TemporaryDirectory(prefix='e55d5-boot-self-') as tmp:
        lane = Path(tmp) / 'lane'
        lane.mkdir()
        record('reuse_empty', existing_outputs(lane) == [])
        (lane / 'probe.log').write_bytes(b'pad seq=1 vsync=10 ord=1 bytes=\n')
        found = existing_outputs(lane)
        record('reuse_probe', [p.name for p in found] == ['probe.log'], str(found))
        (lane / 'boot.log').write_bytes(b'x')
        (lane / 'result.json').write_bytes(b'{}')
        record('reuse_all', sorted(p.name for p in existing_outputs(lane))
               == ['boot.log', 'probe.log', 'result.json'])

    record('split_empty', split_persisted(b'') == ([], False))
    record('split_complete', split_persisted(b'a\nb\n') == ([b'a', b'b'], False))
    record('split_truncated', split_persisted(b'a\nb') == ([b'a'], True))
    record('split_only_partial', split_persisted(b'partial') == ([], True))

    with tempfile.TemporaryDirectory(prefix='e55d5-proof-self-') as tmp:
        probe = Path(tmp) / 'probe.log'
        probe.write_bytes(b'pad seq=1 vsync=10 ord=1 port=0 slot=0 bytes=\n'
                          b'mcread seq=2 vsync=2054 ord=1 fd=1 bytes=\n')
        record('proof_found', probe_proof(probe)[0] == 2054)
        probe.write_bytes(b'pad seq=1 vsync=10 ord=1 port=0 slot=0 bytes=\n'
                          b'mcread seq=2 vsync=9999 ord=1 fd=1 bytes=abc')
        maxv, n, trunc = probe_proof(probe)
        record('proof_ignores_partial', (maxv, n, trunc) == (10, 1, True),
               'max=%r n=%r trunc=%r' % (maxv, n, trunc))
        record('proof_missing_file', probe_proof(Path(tmp) / 'nope.log') == (None, 0, False))

    # Route single-change guard: exactly one entry differs from E55D4.
    e55d4 = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
             '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
             '22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,'
             '29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,'
             '31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
             '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,'
             '35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,'
             '37521:cross:200,37772:down:700,38522:down:30000')
    a_parts, b_parts = e55d4.split(','), ROUTE.split(',')
    diff_idx = [i for i, (a, b) in enumerate(zip(a_parts, b_parts)) if a != b]
    record('route_single_change',
           len(a_parts) == len(b_parts) and diff_idx == [20]
           and b_parts[20] == '33517:square:200' and a_parts[20] == '33517:cross:200',
           'diff_idx=%r' % (diff_idx,))
    return 0 if all(ok for _, ok in cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--label', choices=('B1',))
    ap.add_argument('--self-check', action='store_true')
    args = ap.parse_args()
    if args.self_check:
        return boot_self_check()
    if not args.label:
        ap.error('need --label B1 (or --self-check)')
    lane = WORK / 'run' / args.label
    lane.mkdir(parents=True, exist_ok=True)
    log = lane / 'boot.log'
    probe = lane / 'probe.log'
    result_path = lane / 'result.json'
    taken = existing_outputs(lane)
    if taken:
        raise SystemExit('refusing to reuse %s; exists: %s (at most one boot: B1)'
                         % (lane, ', '.join(p.name for p in taken)))

    reads, errors = precheck()
    if errors:
        raise SystemExit('precheck failed (no boot): ' + '; '.join(errors))

    card_files, card_sha = card_manifest(lane)
    if any(card_files.values()):
        raise SystemExit('card roots are not empty at start')
    hid = hidutil_check()

    slot = claim('E55D5-' + args.label)
    while slot is None:
        print('both mini lease slots busy; retrying in 60 s', flush=True)
        time.sleep(60)
        slot = claim('E55D5-' + args.label)
    proc = None
    result = {'label': args.label, 'stop_tick': STOP_TICK,
              'wall_cap_s': WALL_CAP_S, 'progress_cap_s': PROGRESS_CAP_S,
              'extra_wait_s': EXTRA_WAIT_S, 'extra_ticks': EXTRA_TICKS,
              'log_cap_bytes': LOG_CAP_BYTES, 'probe_cap_bytes': PROBE_CAP_BYTES,
              'fork_pin': FORK_PIN_SHORT, 'fork_pin_full': FORK_PIN_FULL,
              'runner': str(RUNNER), 'elf': str(ELF), 'iso': str(ISO),
              'codegen': str(CODEGEN), 'cwd': str(lane),
              'probe_file': str(probe), 'card_initial_files': card_files,
              'card_initial_sha256': card_sha, 'sha_reads': reads,
              'hidutil': hid}
    env = dict(os.environ)
    for key in tuple(env):
        if key.startswith('PS2X_'):
            env.pop(key)
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1',
               PS2X_DETERMINISTIC='1', PS2X_DET_HASH_EVERY='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'),
               PS2X_PAD_CARD_PROBE=str(probe),
               PS2X_MISSING_FUNCTION_POLICY='stop', COPYFILE_DISABLE='1')
    result['env'] = {key: value for key, value in env.items() if key.startswith('PS2X_')}
    result['load_start'] = os.getloadavg()
    try:
        t0 = time.monotonic()
        with log.open('wb') as output:
            proc = subprocess.Popen([str(RUNNER), str(ELF)], cwd=lane, env=env,
                                    stdout=output, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label,
                              'slot': slot, 'runner_pid': proc.pid,
                              'card_initial_sha256': card_sha}), flush=True)
            last_tick = 0
            last_progress = t0
            phase2_start = None
            proof_vsync = None
            bound = None
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
                if probe.exists() and probe.stat().st_size > PROBE_CAP_BYTES:
                    bound = 'probe_cap'
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
                    proof_vsync, _, _ = probe_proof(probe)
                    if proof_vsync is not None and proof_vsync > STOP_TICK:
                        bound = 'target'
                        break
                    if now - phase2_start >= EXTRA_WAIT_S:
                        bound = 'flush_unproven'
                        break
                    if last_tick >= STOP_TICK + EXTRA_TICKS:
                        bound = 'flush_unproven'
                        break
                time.sleep(0.5)
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
            proof_vsync, proof_lines, proof_trunc = probe_proof(probe)
            result['bound'] = bound
            result['elapsed_s'] = round(time.monotonic() - t0, 3)
            result['last_hash_tick'] = last_tick
            result['phase2_extra_s'] = (round(time.monotonic() - phase2_start, 3)
                                        if phase2_start is not None else 0.0)
            result['probe_proof_vsync'] = proof_vsync
            result['probe_proof_lines'] = proof_lines
            result['probe_proof_truncated'] = proof_trunc
            result['log_bytes'] = log.stat().st_size
            result['probe_bytes'] = probe.stat().st_size if probe.exists() else 0
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
