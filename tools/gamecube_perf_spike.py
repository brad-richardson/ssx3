#!/usr/bin/env python3
"""Sequential, isolated comparisons of native probe and diagnostic overhead.

Players must be built with gamecube_native_trace.py --scheduler --interpolation.
Each case retains the executable/fault/course checks. No game clocks, CPU JIT,
cache accuracy, resolution or guest assets change between cases. Host-timed
navigation means these are diagnostic comparisons, not deterministic speedups.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from gamecube_draw_trace import ROOT, sha
from gamecube_schedule_trace import summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before-player', type=Path, required=True)
    parser.add_argument('--after-player', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT/'local'):
        parser.error('Keep experiments under local/')
    out.mkdir(parents=True, exist_ok=False)
    cases = [('before', args.before_player, 'on', '1'),
             ('filtered', args.after_player, 'on', '1'),
             ('validation-off', args.after_player, 'off', '1'),
             ('sampling-off', args.after_player, 'off', '0'),
             ('rush-presentation', args.after_player, 'off', '0')]
    report = dict(schema=1, game=str(args.game.resolve()),
                  window=[145, 170], cases=[],
                  limits='Sequential host-timed rides, not state-matched benchmarks. '
                         'Render completion is not actual presentation or mobile headroom.')
    prefix = 'p'+time.strftime('%H%M%S')
    for i, (name, player, validation, sampling) in enumerate(cases):
        trace = out/(name+'.jsonl')
        env = {k:v for k,v in os.environ.items() if not k.startswith('SSX_NATIVE_')}
        env.update(SSX_NATIVE_PROBE=str(trace), SSX_NATIVE_SCHEDULE='1',
                   SSX_NATIVE_COMPLETION_RELEASE='1', SSX_NATIVE_SKIP_BOOKKEEPING='1',
                   SSX_NATIVE_START_SPACING='1', SSX_NATIVE_SPEED_FLOOR='1',
                   SSX3_DISPATCH_SAMPLES=sampling)
        env.pop('SSX3_IDLE_PC', None)
        env['SSX3_RUSH_PRESENT'] = '1' if name == 'rush-presentation' else '0'
        command = [sys.executable, str(ROOT/'tools/gamecube_schedule_check.py'),
                   '--player-dir', str(player.resolve()), '--game', str(args.game.resolve()),
                   '--profile', prefix+str(i), '--output', str(out/name), '--seconds', '180',
                   '--immediate-xfb', '--resolution', '640x528', '--metal-validation', validation]
        print('Starting '+name, flush=True)
        with (out/(name+'.log')).open('w') as log:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        case = dict(name=name, player_sha256=sha(player/'player'), command=command,
                    metal_validation=validation, dispatch_sampling=sampling=='1',
                    rush_presentation=name=='rush-presentation',
                    exit_code=result.returncode, accepted=False)
        if trace.exists():
            try:
                rows = [json.loads(line) for line in trace.read_text().splitlines()]
                case['measurements'] = summarize(rows)
                measured = case['measurements']
                case['accepted'] = (result.returncode == 0 and measured['complete_renders'] > 0 and
                                    not any(measured['extra_state_changes'].values()))
                case['trace_sha256'] = sha(trace)
            except (ValueError, KeyError) as error:
                case['trace_error'] = str(error)
        report['cases'].append(case)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(case), flush=True)
    print(out/'report.json', flush=True)


if __name__ == '__main__':
    main()
