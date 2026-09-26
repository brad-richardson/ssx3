#!/usr/bin/env python3
"""Cached det baselines: store one control run per fork tip, boot only candidates.

Store: ~/dev/ssx3-work/baselines/<key>/ with manifest.json (pins + per-file
SHAs). Key = readable prefix + short hash of the canonical pins JSON, e.g.
a3efbfe-det-fr1r1-t2400-snd1-1x-9f2c41ab. Key derivation is deterministic from
the pins file, so `get --pins` finds what `put --pins` stored.

Usage:
  baseline.py put --runner R --run DIR --pins PINS [--extra-frames DIR]
  baseline.py get <key|--pins PINS>
  baseline.py list
  baseline.py compare --key K --cand RUNDIR [--min-tick N]
  baseline.py make --pins PINS --runner R [--run DIR]
  baseline.py put-state --state F --pins PINS --tick T [--note TEXT]
  baseline.py get-state <key|--pins PINS --tick T>
  baseline.py list-states
SS1 save states live in <store>/states/<key>/ (state.bin + manifest.json with
the state's header lines). The state key uses only the guest-relevant pins
(STATE_PINS) + the save tick, so any candidate build with matching guest code,
route and backend finds it; SSAA/hi-res are in the key but only warn on load.
Global: [--store DIR] (default $SSX3_BASELINES or ~/dev/ssx3-work/baselines/).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
BOOT_DRIVER = HERE.parent / 'ssx3_boot.py'
HASHDIFF = REPO / 'local' / 'research' / 'GB8' / 'gb8_hashdiff.py'
DEFAULT_STORE = Path(os.environ.get('SSX3_BASELINES',
                                    str(Path.home() / 'dev' / 'ssx3-work' / 'baselines')))

REQUIRED_PINS = ('fork', 'codegen_register', 'codegen_changed', 'vu1_images',
                 'parallel_gs', 'build', 'route', 'stop_tick', 'sound',
                 'backend', 'ssaa', 'hires', 'pipeline', 'iso_sha', 'elf_sha')
TEXT_RECEIPTS = ('boot.log', 'snd.log', 'result.json', 'trace.jsonl')
COVERAGE_LINE = re.compile(r'^\[coverage:[^\]]+\].*$', re.M)
SND_TICK = re.compile(r'^tick .*cid0=.*$', re.M)
# Host-side counters: wall-clock audio under/overruns vary run to run even for
# guest-identical boots, so they are stripped before the snd comparison.
SND_HOST_NOISE = re.compile(r' underruns=\d+ overflows=\d+')


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_pins(path):
    pins = json.loads(Path(path).read_text())
    missing = [k for k in REQUIRED_PINS if k not in pins]
    if missing:
        raise SystemExit('pins %s missing: %s' % (path, ','.join(missing)))
    return pins


def canonical(pins):
    return json.dumps(pins, sort_keys=True, separators=(',', ':')).encode()


def key_of(pins):
    h8 = hashlib.sha256(canonical(pins)).hexdigest()[:8]
    prefix = '%s-%s-%s-t%d-snd%d-%dx' % (
        pins['fork'][:7], pins['build'], pins['route'], pins['stop_tick'],
        1 if pins['sound'] == 'on' else 0, pins['ssaa'])
    if pins['hires']:
        prefix += '-hires'
    if pins['pipeline']:
        prefix += '-pp'
    return '%s-%s' % (prefix, h8)


def dir_bytes(path):
    total = 0
    for root, _ds, fs in os.walk(path):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def verify(dest):
    """Check every stored file against the manifest. Returns (ok, message)."""
    man = json.loads((dest / 'manifest.json').read_text())
    for rel, want in man['files'].items():
        p = dest / rel
        if not p.exists():
            return False, 'CORRUPT %s %s (missing)' % (man['key'], rel)
        reads = [sha_of(p)]
        if rel == 'runner':
            reads.append(sha_of(p))  # two reads for the runner binary
        if any(r != want for r in reads):
            return False, 'CORRUPT %s %s' % (man['key'], rel)
    return True, ''


def cmd_put(args):
    pins = load_pins(args.pins)
    key = key_of(pins)
    store = Path(args.store)
    dest = store / key
    if dest.exists():
        raise SystemExit('EXISTS %s %s' % (key, dest))
    run = Path(args.run)
    boot = run / 'boot.log'
    result = run / 'result.json'
    if not boot.exists() or not result.exists():
        raise SystemExit('run %s lacks boot.log and/or result.json' % run)
    runner = Path(args.runner)
    if not runner.exists():
        raise SystemExit('no such runner %s' % runner)

    dest.mkdir(parents=True)
    (dest / 'frames').mkdir()
    shutil.copy2(runner, dest / 'runner')
    if sha_of(dest / 'runner') != sha_of(runner):
        raise SystemExit('runner copy mismatch')
    for name in TEXT_RECEIPTS:
        src = run / name
        if src.exists():
            shutil.copyfile(src, dest / name)
    frames = run / 'frames'
    if frames.is_dir():
        for f in sorted(frames.iterdir()):
            if f.is_file() and f.suffix in ('.png', '.txt'):
                shutil.copyfile(f, dest / 'frames' / f.name)
    if args.extra_frames:
        extra = Path(args.extra_frames)
        tag = extra.parent.name.lower().replace(' ', '_') + '-'
        for f in sorted(extra.iterdir()):
            if f.is_file() and f.suffix in ('.png', '.txt'):
                shutil.copyfile(f, dest / 'frames' / (tag + f.name))

    files = {}
    for root, _ds, fs in os.walk(dest):
        for f in fs:
            if f == 'manifest.json':
                continue
            p = Path(root) / f
            files[str(p.relative_to(dest))] = sha_of(p)
    man = {'key': key, 'pins': pins,
           'pins_canonical_sha256': hashlib.sha256(canonical(pins)).hexdigest(),
           'files': files, 'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'source_runner': str(runner), 'source_run': str(run),
           'extra_frames': str(Path(args.extra_frames)) if args.extra_frames else None,
           'store_bytes': None}
    (dest / 'manifest.json').write_text(json.dumps(man, indent=2) + '\n')
    man['store_bytes'] = dir_bytes(dest)
    (dest / 'manifest.json').write_text(json.dumps(man, indent=2) + '\n')
    print('%s %s' % (key, dest))
    return 0


def resolve_key(args):
    if args.pins:
        return key_of(load_pins(args.pins))
    return args.key


def cmd_get(args):
    key = resolve_key(args)
    dest = Path(args.store) / key
    if not dest.is_dir() or not (dest / 'manifest.json').exists():
        print('MISSING %s' % key)
        return 2
    ok, msg = verify(dest)
    if not ok:
        print(msg)
        return 1
    print(dest)
    return 0


def cmd_list(args):
    store = Path(args.store)
    rows = []
    total = 0
    if store.is_dir():
        for d in sorted(store.iterdir()):
            man_p = d / 'manifest.json'
            if not man_p.exists():
                continue
            man = json.loads(man_p.read_text())
            pins = man['pins']
            n = dir_bytes(d)
            total += n
            rows.append((man['key'], man['created_utc'], n, pins['fork'][:7],
                         pins['build'], pins['route'], pins['stop_tick'], pins['sound'],
                         pins['backend'], pins['ssaa'], pins['hires'], pins['pipeline']))
    print('%-46s %-20s %9s %7s %-5s %-6s %5s %-3s %-8s %s'
          % ('KEY', 'CREATED', 'BYTES', 'FORK', 'BUILD', 'ROUTE', 'STOP', 'SND',
             'BACKEND', 'SSAA/HR/PP'))
    for r in rows:
        print('%-46s %-20s %9d %7s %-5s %-6s %5d %-3s %-8s %dx/%d/%d' % r)
    print('%d baseline(s), %d bytes in %s' % (len(rows), total, store))
    return 0


STATE_PINS = ('fork', 'codegen_register', 'codegen_changed', 'vu1_images', 'parallel_gs',
              'route', 'backend', 'ssaa', 'hires', 'iso_sha', 'elf_sha')


def state_key_of(pins, tick):
    sub = {k: pins[k] for k in STATE_PINS}
    sub['tick'] = int(tick)
    h8 = hashlib.sha256(canonical(sub)).hexdigest()[:8]
    prefix = '%s-%s-t%d-%s-%dx' % (pins['fork'][:7], pins['route'], int(tick), pins['backend'], pins['ssaa'])
    if pins['hires']:
        prefix += '-hires'
    return '%s-%s' % (prefix, h8), sub


def state_header(path):
    """Header key=value lines from an SS1 state file (format 1)."""
    import struct
    with open(path, 'rb') as f:
        head = f.read(1 << 16)
    if head[:8] != b'PS2XSAVE':
        raise SystemExit('%s is not a ps2x save state' % path)
    pos = 12
    (klen,) = struct.unpack_from('<I', head, pos)
    pos += 4
    if head[pos:pos + klen] != b'header':
        raise SystemExit('%s: first section is not the header' % path)
    pos += klen + 4 + 8
    (tlen,) = struct.unpack_from('<Q', head, pos)
    pos += 8
    text = head[pos:pos + tlen].decode()
    return dict(line.split('=', 1) for line in text.splitlines() if '=' in line)


def cmd_put_state(args):
    pins = json.loads(Path(args.pins).read_text())
    missing = [k for k in STATE_PINS if k not in pins]
    if missing:
        raise SystemExit('pins %s missing: %s' % (args.pins, ','.join(missing)))
    key, sub = state_key_of(pins, args.tick)
    header = state_header(args.state)
    if int(header.get('save_tick', -1)) != args.tick:
        raise SystemExit('state saved at tick %s, not %d' % (header.get('save_tick'), args.tick))
    dest = Path(args.store) / 'states' / key
    if dest.exists():
        raise SystemExit('EXISTS %s %s' % (key, dest))
    dest.mkdir(parents=True)
    shutil.copyfile(args.state, dest / 'state.bin')
    reads = [sha_of(args.state), sha_of(dest / 'state.bin')]
    if reads[0] != reads[1]:
        shutil.rmtree(dest)
        raise SystemExit('copy SHA mismatch')
    man = {'key': key, 'kind': 'ss1-state', 'pins': pins, 'key_pins': sub, 'tick': args.tick,
           'header': header, 'note': args.note, 'source': str(Path(args.state).resolve()),
           'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'files': {'state.bin': reads[0]}, 'bytes': (dest / 'state.bin').stat().st_size}
    (dest / 'manifest.json').write_text(json.dumps(man, indent=2, sort_keys=True) + '\n')
    print(dest)
    return 0


def cmd_get_state(args):
    if args.key:
        key = args.key
    else:
        if not args.pins or args.tick is None:
            raise SystemExit('get-state needs a key or --pins + --tick')
        key, _ = state_key_of(json.loads(Path(args.pins).read_text()), args.tick)
    dest = Path(args.store) / 'states' / key
    if not (dest / 'manifest.json').exists():
        print('MISSING %s' % key)
        return 2
    man = json.loads((dest / 'manifest.json').read_text())
    want = man['files']['state.bin']
    if any(sha_of(dest / 'state.bin') != want for _ in range(2)):
        print('CORRUPT %s state.bin' % key)
        return 3
    print(dest / 'state.bin')
    return 0


def cmd_list_states(args):
    root = Path(args.store) / 'states'
    rows = []
    if root.is_dir():
        for d in sorted(root.iterdir()):
            m = d / 'manifest.json'
            if m.exists():
                man = json.loads(m.read_text())
                rows.append((man['key'], man['created_utc'], man['bytes'], man['header'].get('runner_sha', '')[:12],
                             man['note']))
    print('%-52s %-20s %9s %-12s %s' % ('KEY', 'CREATED', 'BYTES', 'RUNNER', 'NOTE'))
    for r in rows:
        print('%-52s %-20s %9d %-12s %s' % r)
    print('%d state(s) in %s' % (len(rows), root))
    return 0


def snd_coverage_summary(run):
    boot = (Path(run) / 'boot.log').read_bytes().decode(errors='replace')
    cov = COVERAGE_LINE.findall(boot)
    snd_p = Path(run) / 'snd.log'
    if snd_p.exists():
        ticks = SND_TICK.findall(snd_p.read_text(errors='replace'))
        snd = [SND_HOST_NOISE.sub('', t) for t in ticks] or ['(no tick lines)']
    else:
        snd = ['(no snd.log)']
    return cov, snd


def snd_prefix_ok(snd_b, snd_c):
    """Compare the snd tick lines both runs printed (host noise stripped).
    Runs stop a few ticks apart (runner stop is host-timed), so the last line
    can differ in a guest-identical pair (HP1: 2405 vs 2410): compare the common
    prefix, and require it to cover all but the last two base lines."""
    n = min(len(snd_b), len(snd_c))
    return n >= max(1, len(snd_b) - 2) and snd_b[:n] == snd_c[:n], n


def cmd_compare(args):
    dest = Path(args.store) / args.key
    if not dest.is_dir() or not (dest / 'manifest.json').exists():
        print('MISSING %s' % args.key)
        return 2
    ok, msg = verify(dest)
    if not ok:
        print(msg)
        return 1
    man = json.loads((dest / 'manifest.json').read_text())
    min_tick = args.min_tick if args.min_tick else man['pins']['stop_tick']
    if not HASHDIFF.exists():
        raise SystemExit('missing %s' % HASHDIFF)
    r = subprocess.run([sys.executable, str(HASHDIFF), '--base', str(dest),
                        '--cand', args.cand, '--min-tick', str(min_tick)],
                       capture_output=True, text=True)
    print(r.stdout, end='')
    if r.stderr:
        print(r.stderr, end='', file=sys.stderr)
    hash_ok = r.returncode == 0
    cov_b, snd_b = snd_coverage_summary(dest)
    cov_c, snd_c = snd_coverage_summary(args.cand)
    # HS1: coverage per-entry lines print in std::unordered_map iteration
    # order, which differs across STL implementations (Mac libc++ vs Linux
    # libstdc++) while the content is guest-identical — so compare coverage
    # as a multiset. Sorting cannot mask a real difference (same multiset
    # <=> same sorted list) and is a no-op verdict-wise for same-host
    # compares, where the order is stable run to run (F5 B1-B5).
    snd_ok, n_common = snd_prefix_ok(snd_b, snd_c)
    snd_cov_ok = sorted(cov_b) == sorted(cov_c) and snd_ok
    print('snd/coverage: %s' % ('IDENTICAL' if snd_cov_ok else 'DIFFER'))
    if not snd_cov_ok:
        if sorted(cov_b) != sorted(cov_c):
            print('  coverage base: %s' % cov_b)
            print('  coverage cand: %s' % cov_c)
        if not snd_ok:
            first = next((i for i in range(n_common) if snd_b[i] != snd_c[i]), None)
            print('  snd lines base=%d cand=%d common=%d first_diff_line=%s'
                  % (len(snd_b), len(snd_c), n_common, first))
            if first is not None:
                print('  snd base: %s' % snd_b[first])
                print('  snd cand: %s' % snd_c[first])
    else:
        print('  coverage: %s' % (' | '.join(cov_b[:4]) if cov_b else '(none)'))
        print('  snd: %d common tick lines, last %s' % (n_common, snd_b[n_common - 1]))
    print('compare %s vs %s: %s' % (args.key, args.cand,
                                    'IDENTICAL' if hash_ok and snd_cov_ok else 'DIFFER'))
    return 0 if hash_ok and snd_cov_ok else 1


def cmd_make(args):
    pins = load_pins(args.pins)
    key = key_of(pins)
    store = Path(args.store)
    dest = store / key
    if dest.is_dir():
        ok, msg = verify(dest)
        if not ok:
            print(msg)
            return 1
        print('EXISTS %s %s' % (key, dest))
        return 0
    if pins['build'] != 'det':
        raise SystemExit('make supports det controls only (pins build=%s); '
                         'speed baselines need the exclusive lease' % pins['build'])
    if args.run:
        rundir = Path(args.run)
    else:
        rundir = store / '.tmp' / ('%s-%s' % (
            key, time.strftime('%Y%m%dT%H%M%S', time.gmtime())))
    label = key[:32]
    cmd = [sys.executable, str(BOOT_DRIVER), '--mode', 'det',
           '--backend', pins['backend'], '--runner', args.runner,
           '--label', label, '--out', str(rundir),
           '--stop-tick', str(pins['stop_tick']), '--sound', pins['sound'],
           '--route', pins['route'],
           '--coverage-tick', str(pins.get('coverage_tick', pins['stop_tick'])),
           '--hash-every', str(pins.get('hash_every', 1))]
    if pins.get('dump_ticks'):
        cmd += ['--dump-ticks', pins['dump_ticks']]
    if pins.get('vu1_stats'):
        cmd += ['--vu1-stats']
    if pins['ssaa'] != 1:
        cmd += ['--env', 'PS2X_PGS_SSAA=%d' % pins['ssaa']]
    if pins['hires']:
        cmd += ['--env', 'PS2X_PGS_HIRES_SCANOUT=1']
    if pins['pipeline']:
        cmd += ['--env', 'PS2X_PGS_PRESENT_PIPELINE=1']
    print('+ %s' % ' '.join(cmd), flush=True)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print('BOOT-FAILED %s rc=%d run=%s' % (key, r.returncode, rundir))
        return 1
    args.runner, args.run = args.runner, str(rundir)
    args.extra_frames = None
    return cmd_put(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=str(DEFAULT_STORE))
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('put')
    p.add_argument('--runner', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--pins', required=True)
    p.add_argument('--extra-frames', default='')
    g = sub.add_parser('get')
    g.add_argument('key', nargs='?')
    g.add_argument('--pins', default='')
    sub.add_parser('list')
    c = sub.add_parser('compare')
    c.add_argument('--key', required=True)
    c.add_argument('--cand', required=True)
    c.add_argument('--min-tick', type=int, default=0)
    m = sub.add_parser('make')
    m.add_argument('--pins', required=True)
    m.add_argument('--runner', required=True)
    m.add_argument('--run', default='')
    ps = sub.add_parser('put-state')
    ps.add_argument('--state', required=True)
    ps.add_argument('--pins', required=True)
    ps.add_argument('--tick', type=int, required=True)
    ps.add_argument('--note', default='')
    gs = sub.add_parser('get-state')
    gs.add_argument('key', nargs='?')
    gs.add_argument('--pins', default='')
    gs.add_argument('--tick', type=int, default=None)
    sub.add_parser('list-states')
    args = ap.parse_args()
    if args.cmd == 'get' and not args.key and not args.pins:
        raise SystemExit('get needs a key or --pins')
    return {'put': cmd_put, 'get': cmd_get, 'list': cmd_list,
            'compare': cmd_compare, 'make': cmd_make, 'put-state': cmd_put_state,
            'get-state': cmd_get_state, 'list-states': cmd_list_states}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
