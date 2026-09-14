#!/usr/bin/env python3
"""Bounded native course check with rider observations and state-aware race start.

Uses an isolated profile, the pinned GXBE69 runtime checks, and controller input.
The MemoryWatcher observer never writes guest memory. Menu navigation is timed;
start requests wait for observed state 6 after menu input has finished. That
state also exists during loading, so requests repeat until riding is observed.
Screenshots and the runtime receipt remain essential to interpret the ride.

--restart-after rides for that many observed seconds, then takes the pause
menu's Restart and requires riding to be observed a second time. The pause
menu opens on Return with Restart one step below, and Restart confirms with
"Are you sure?" defaulting to No; the whole path is sent in one pass, because
a menu left open stops frame production. The second ride must follow a freshly
observed briefing state, since the rider observation can hold its last
pre-restart value.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def reset_events(rows):
    """Require ground contact and three hazard-free seconds after a reset."""
    def hazard(r):
        return r['surface'] == 18 or bool(r.get('terrain_flags',0)&2)
    events = []
    for i, row in enumerate(rows):
        if row['state'] != 9 or i and rows[i-1]['state'] == 9:
            continue
        before = [r for r in rows[:i] if row['t']-10 <= r['t'] <= row['t']]
        prior_hazard = next((r for r in reversed(before) if hazard(r)), None)
        if prior_hazard is None and hazard(row):
            prior_hazard = row
        after = None
        for j in range(i+1,len(rows)):
            r=rows[j]
            if r['t']>row['t']+15 or r['state']==9 and rows[j-1]['state']!=9:
                break
            if r['state']!=0 or hazard(r):continue
            stop=next((k for k in range(j,len(rows)) if rows[k]['t']>=r['t']+3),None)
            if stop is None:break
            window=rows[j:stop+1]
            if (all(q['state'] not in (8,9) and not hazard(q) for q in window) and
                    all(b['t']-a['t']<=1 for a,b in zip(window,window[1:]))):
                after=r;break
        events.append(dict(reset=row, hazard=prior_hazard, recovered=after))
    return events


def reset_loops(events):
    """Flag repeated failed recoveries in the same small area."""
    loops=[]
    for i in range(len(events)-2):
        group=events[i:i+3]
        a=group[0]['reset']
        if (all(e['recovered'] is None for e in group) and
                group[-1]['reset']['t']-a['t']<30 and
                all(sum((e['reset'].get(k,0)-a.get(k,0))**2 for k in ('x','y','z'))<1000**2 for e in group)):
            loops.append(dict(first_reset_t=a['t'],last_reset_t=group[-1]['reset']['t']))
    return loops


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--game', required=True, type=Path)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--seconds', type=int, default=300)
    ap.add_argument('--expect-reset', action='store_true')
    ap.add_argument('--metal-validation', choices=('on', 'off'), default='on',
                    help='Keep validation on for correctness; explicitly disable for performance comparisons')
    ap.add_argument('--cpu-thread', action='store_true',
                    help='Dual-core runtime (CPUThread = True) for this fresh profile')
    ap.add_argument('--module', type=Path, help='Module dylib to load instead of the default build')
    ap.add_argument('--restart-after', type=int,
                    help='Seconds of observed riding before choosing the pause menu Restart; '
                         'the check then requires riding again')
    args = ap.parse_args()
    if not 180 <= args.seconds <= 900:
        ap.error('Use a bounded 180–900 second check')
    if args.restart_after is not None and not 5 <= args.restart_after <= args.seconds-120:
        ap.error('Restart must follow at least 5 riding seconds and leave 120 seconds to ride again')
    if Path(args.profile).name != args.profile or args.profile in ('.', '..'):
        ap.error('Use a single isolated profile name')
    profile = ROOT/'local/native/profiles'/args.profile
    if profile.exists() or args.output.exists():
        ap.error('Preserving existing profile/evidence; choose fresh paths')
    args.output.mkdir(parents=True)
    sequence_path=args.output/'menu-sequence.json'
    sequence_path.write_bytes((ROOT/'native/diagnostics/course-start.json').read_bytes())
    rows_path = args.output/'rider.jsonl'
    children = []
    started = False
    with (args.output/'runtime.log').open('w') as runtime_log, (args.output/'input.log').open('w') as input_log, (args.output/'observer.log').open('w') as observer_log:
        try:
            watcher = subprocess.Popen([sys.executable, str(ROOT/'tools/gamecube_telemetry.py'),
                '--profile', args.profile, '--output', str(rows_path), '--seconds', str(args.seconds+60)],
                cwd=ROOT, stdout=observer_log, stderr=subprocess.STDOUT)
            children.append(watcher)
            deadline = time.monotonic()+10
            while not (profile/'MemoryWatcher/MemoryWatcher').exists():
                if watcher.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError('Observer did not bind; see observer.log')
                time.sleep(.1)
            run = subprocess.Popen([sys.executable, str(ROOT/'tools/native_gamecube.py'), 'run',
                '--game', str(args.game.resolve()), '--profile', args.profile, '--seconds', str(args.seconds),
                '--pipe-controller', *(['--cpu-thread'] if args.cpu_thread else []),
                *(['--module', str(args.module.resolve())] if args.module else [])], cwd=ROOT,
                env=dict(os.environ, MTL_DEBUG_LAYER='1' if args.metal_validation == 'on' else '0'),
                stdout=runtime_log, stderr=subprocess.STDOUT)
            children.append(run)
            deadline = time.monotonic()+45
            while True:
                if run.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError('Runtime did not accept controller input')
                try:
                    fd = os.open(profile/'Pipes/ssx3', os.O_WRONLY | os.O_NONBLOCK)
                    os.close(fd)
                    break
                except OSError:
                    time.sleep(.25)
            replay = subprocess.Popen([sys.executable, str(ROOT/'tools/native_replay.py'),
                '--profile', args.profile, '--sequence', str(sequence_path.resolve())],
                cwd=ROOT, stdout=input_log, stderr=subprocess.STDOUT)
            children.append(replay)
            briefing_since = None
            last_request = -float('inf')
            riding_since = None
            restart_wall = None
            observed_starts = 0
            briefing_after_restart = False
            with rows_path.open() as stream:
                latest = None
                while run.poll() is None:
                    if watcher.poll() is not None:
                        raise RuntimeError('Observer stopped during gameplay')
                    for line in stream:
                        latest = json.loads(line)
                    # A restart can leave the observed rider fixed at its last
                    # pre-restart value, so only a freshly written sample counts.
                    fresh = bool(latest) and time.time()-latest['wall_time'] < 2
                    ready = fresh and latest['state'] == 6
                    if ready and restart_wall is not None:
                        briefing_after_restart = True
                    if fresh and last_request > 0 and latest['state'] in range(10) and latest['state'] != 6:
                        # After a restart, riding only counts once the briefing
                        # state has been seen again; otherwise a stale wipeout
                        # sample would pass as a second ride.
                        if restart_wall is not None and not briefing_after_restart:
                            pass
                        else:
                            if not started:
                                observed_starts += 1
                                riding_since = time.monotonic()
                            started = True
                    # The pause menu opens on Return with Restart one below it,
                    # and Restart then asks "Are you sure?" with No selected, so
                    # the confirmation needs an explicit move up to Yes. Drive
                    # the whole path in one pass: a menu left open stops frame
                    # production and the run fails its own rendering evidence.
                    if (args.restart_after is not None and restart_wall is None and started
                            and riding_since is not None
                            and time.monotonic()-riding_since >= args.restart_after):
                        for button, settle in (('START', 2.0), ('D_DOWN', 1.0), ('A', 2.0),
                                               ('D_UP', 1.0), ('A', 0.0)):
                            subprocess.run([sys.executable, str(ROOT/'tools/gamecube_input.py'),
                                '--profile', args.profile, 'tap', button], cwd=ROOT, check=True,
                                stdout=input_log, stderr=subprocess.STDOUT)
                            time.sleep(settle)
                        restart_wall = time.time()
                        # Require riding to be observed again, and let the
                        # existing state-6 retry carry the post-restart briefing.
                        started = False
                        riding_since = None
                        last_request = time.monotonic()
                        input_log.write(f'Requested restart at {restart_wall}\n'); input_log.flush()
                        continue
                    if ready and replay.poll() == 0 and not started:
                        if briefing_since is None:
                            briefing_since = time.monotonic()
                        # State 6 also spans the countdown. A quick retry can
                        # arrive just after GO and become an unintended jump,
                        # invalidating a controlled collision comparison.
                        elif time.monotonic()-briefing_since > 2 and time.monotonic()-last_request > 15:
                            subprocess.run([sys.executable, str(ROOT/'tools/gamecube_input.py'),
                                '--profile', args.profile, 'tap', 'A'], cwd=ROOT, check=True,
                                stdout=input_log, stderr=subprocess.STDOUT)
                            last_request = time.monotonic()
                            input_log.write(f'Requested start in observed state 6 at {latest["wall_time"]}\n'); input_log.flush()
                    else:
                        briefing_since = None
                    time.sleep(.25)
            if run.returncode:
                raise RuntimeError('Native runtime failed; see runtime.log')
        finally:
            # Only children of this bounded check are stopped.
            for child in reversed(children):
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=30)
            # SIGTERM cannot execute the observer's finally block. It has exited,
            # so its own isolated socket is now stale and safe to remove.
            (profile/'MemoryWatcher/MemoryWatcher').unlink(missing_ok=True)
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    events = reset_events(rows)
    loops = reset_loops(events)
    summary = dict(game=str(args.game), profile=args.profile, samples=len(rows),
                   metal_validation=args.metal_validation, cpu_thread=args.cpu_thread,
                   module=str(args.module.resolve()) if args.module else None,
                   menu_sequence_sha256=hashlib.sha256(sequence_path.read_bytes()).hexdigest(),
                   riding_observed_after_start=observed_starts >= 1,
                   restart_requested_wall=restart_wall,
                   riding_observed_after_restart=(observed_starts >= 2
                                                  if args.restart_after is not None else None),
                   resets=events,
                   complete_hazard_resets=sum(bool(e['hazard'] and e['recovered']) for e in events),
                   reset_loops=loops, source='read-only GXBE69 MemoryWatcher; native Metal check')
    (args.output/'observations.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='resets'}, indent=2))
    if (not summary['riding_observed_after_start'] or not rows or loops or
            args.restart_after is not None and not summary['riding_observed_after_restart'] or
            args.expect_reset and not summary['complete_hazard_resets']):
        raise RuntimeError('Expected gameplay evidence was not observed')


if __name__ == '__main__':
    main()
