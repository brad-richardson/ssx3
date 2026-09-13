#!/usr/bin/env python3
"""Run a pinned isolated scheduling player through the normal course checker.

The remaining arguments are gamecube_course_check.py arguments. Profiles and
outputs must be fresh. No production config or player is changed.
"""
import argparse
import json
from pathlib import Path
import sys
import gamecube_course_check as course
from gamecube_draw_trace import ROOT, sha


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


if __name__ == '__main__':
    main()
