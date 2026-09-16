#!/usr/bin/env python3
"""Run a pinned isolated scheduling player through the normal course checker.

The remaining arguments are gamecube_course_check.py arguments. Profiles and
outputs must be fresh. No production config or player is changed.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import gamecube_course_check as course
from gamecube_draw_trace import ROOT, sha


def validate_trial_trace(rows):
    events = [r for r in rows if r.get('event') == 'trial_test']
    expected = ['request', 'cancel_during_repeat', 'quiescent', 'restart', 'quiescent', 'complete']
    if [r.get('action') for r in events] != expected:
        raise RuntimeError('Lifecycle trial did not demonstrate cancellation, drain, restart and completion')
    if any(b['wall'] < a['wall'] for a, b in zip(events, events[1:])):
        raise RuntimeError('Lifecycle events are out of order')
    walls = {r['action']: r['wall'] for r in events}
    first = [r for r in rows if walls['request'] < r.get('wall', 0) < walls['restart']]
    if not any(r.get('event') == 'f_trial' and r.get('action') == 'patched' for r in first):
        raise RuntimeError('Lifecycle F trial never patched its dt consts')
    if not any(r.get('event') == 'f_trial' and r.get('action') == 'restored' for r in first):
        raise RuntimeError('Lifecycle F trial never restored its dt consts')
    repeats = [r for r in first if r.get('event') == 'update' and r.get('repeat') == 1]
    if not any(r.get('same_rider') == 1 and r.get('state_before') == r.get('state_after') for r in repeats):
        raise RuntimeError('Lifecycle F trial never completed a clean doubled update')
    # Trial 2 must make real extras: with a stale schedule epoch it limits
    # instantly past trial 1's grace and this finds nothing.
    extras = [r for r in rows if r.get('event') == 'render' and r.get('repeat') and
              r.get('wall', 0) > walls['restart'] and
              r.get('result', 0) & 255 and r.get('view_matrix_calls') and r.get('frame_end_calls')]
    if not extras:
        raise RuntimeError('Lifecycle trial never completed an injected draw')
    for r in extras:
        if (r.get('same_rider') != 1 or r.get('same_view') != 1 or
                r.get('state_before') != r.get('state_after') or
                r.get('rng_changed') != 0 or r.get('position_changed') != 0 or
                any(r.get(k) != [] for k in ('body_offsets', 'app_offsets', 'view_offsets'))):
            raise RuntimeError('Lifecycle extra draw changed watched guest state')
    return dict(lifecycle_complete=True, complete_extras=len(extras), first_trial_repeats=len(repeats))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--player-dir', type=Path, required=True)
    parser.add_argument('--immediate-xfb', action='store_true')
    parser.add_argument('--resolution', choices=('640x528','1920x1080'), default='1920x1080')
    args, remaining = parser.parse_known_args()
    directory = args.player_dir.resolve()
    if not directory.is_relative_to(ROOT/'local'):
        parser.error('Use an isolated diagnostic player under local/')
    receipt = json.loads((directory/'build.json').read_text())
    if (not receipt.get('scheduler_headers') or
            sha(directory/'player') != receipt['player_sha256'] or
            sha(directory/'run_native.py') != receipt['launchers']['run_native.py']):
        parser.error('Scheduler player or launcher does not match its build receipt')
    original = course.subprocess.Popen

    def launch(command, *pos, **kw):
        command = list(command)
        target = str(ROOT/'tools/native_gamecube.py')
        if target in command:
            profile = ROOT/'local/native/profiles'/command[command.index('--profile')+1]
            config = profile/'Config'
            config.mkdir(exist_ok=True)
            gfx = config/'GFX.ini'
            frontend = profile/'config.ini'
            if gfx.exists() or frontend.exists():
                raise RuntimeError('Preserving existing profile settings')
            gfx.write_text('[Hacks]\nImmediateXFBEnable = '+str(args.immediate_xfb)+
                           '\nCapImmediateXFB = False\n')
            frontend.write_text('[Video]\nresolution='+args.resolution+
                                '\nbackend=Vulkan\nfullscreen=false\nshow_fps_in_title=true\n')
            command[command.index(target)] = str(directory/'run_native.py')
        return original(command, *pos, **kw)

    course.subprocess.Popen = launch
    sys.argv = [sys.argv[0]] + remaining
    try:
        course.main()
    finally:
        course.subprocess.Popen = original
    if receipt.get('trial_test_driver_sha256'):
        path = os.environ.get('SSX_NATIVE_PROBE')
        if not path:
            raise RuntimeError('Lifecycle acceptance requires SSX_NATIVE_PROBE')
        result = validate_trial_trace([json.loads(line) for line in Path(path).read_text().splitlines()])
        print(json.dumps(result))


if __name__ == '__main__':
    main()
