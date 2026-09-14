#!/usr/bin/env python3
"""Build a bounded, read-only countdown observer in an isolated native module.

Set SSX_STARTGATE_TRACE=1 and SSX_STARTGATE_FIRST to the staged first packed
instance ID, then use gamecube_course_check.py --module OUTPUT/probe.dylib.
This observes dispatch and binding; it does not execute replacement scripts.

The observer writes its lines to the runtime's own log, not to the check's
observer.log, which carries the MemoryWatcher instead. Pass --summarize with
that runtime log to turn the retained lines into a report.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess

from gamecube_draw_trace import ROOT, compile_copy, sha
from gamecube_native_trace import DOL_SHA256

MODULE = ROOT/'local/native/ssx3-module'
HEADER = ROOT/'native/diagnostics/startgate_trace.h'
HOOKS = {
    'chunk_0063_text1_800FD7A0.c': {'801015C8': ('startgate_open', 0)},
    'chunk_0064_text1_801017A0.c': {'80101804': ('startlight_begin', 0)},
    'chunk_0096_text1_801817A0.c': {
        '801823F8': ('event_lookup', 0),
        '80182430': ('event_value', 0),
        '80182364': ('event_invoke', 0),
    },
    'chunk_0145_text1_802457A0.c': {'8024620C': ('instance_bound', 1)},
}


TIMEBASE_HZ = 40500000
EVENT_HASHES = {'startlight_begin': 0x0ebf88fe, 'startgate_open': 0x0dfb527e}


def countdown_windows(dispatches):
    """Seconds from each lights dispatch to the gate dispatch that follows it.

    A restart raises both events again, and re-entering the course after a
    finish raises StartgateOpen on its own, so the events must be paired in
    order rather than assumed to occur once or always together. Gate
    dispatches with no preceding lights are reported separately, not dropped.
    """
    windows, unpaired, lights = [], 0, None
    for dispatch in dispatches:
        if dispatch['hash'] != EVENT_HASHES[dispatch['event']]:
            raise ValueError(f'Unexpected {dispatch["event"]} event hash')
        if dispatch['event'] == 'startlight_begin':
            # Two lights in a row would mean a missed gate, not a window.
            unpaired += lights is not None
            lights = dispatch['ticks']
        elif lights is None:
            unpaired += 1
        else:
            windows.append((dispatch['ticks'] - lights) / TIMEBASE_HZ)
            lights = None
    return windows, unpaired + (lights is not None)


def countdown_window(dispatches):
    """The first complete lights-to-gate window, or None."""
    windows, _ = countdown_windows(dispatches)
    return windows[0] if windows else None


def read_observations(log):
    """Collect the observer's retained lines from a native runtime log."""
    rows = []
    for line in log.read_text(errors='replace').splitlines():
        marker = '[ssx-startgate] '
        if line.startswith(marker):
            rows.append(json.loads(line[len(marker):]))
    if not rows:
        raise ValueError('No countdown observations in that log')
    return rows


def summarize(rows):
    """Respect the observer's independent 1000-event cap in each copied TU."""
    stages = {stage: name for name, hooks in HOOKS.items() for stage, _ in hooks.values()}
    counts = {name: 0 for name in HOOKS}
    dispatches, lookups, bindings = [], [], []
    pending = None
    for row in rows:
        stage = row['stage']
        if stage not in stages:
            raise ValueError('Unknown countdown observation stage')
        counts[stages[stage]] += 1
        if stage in ('startgate_open', 'startlight_begin'):
            dispatches.append(dict(event=stage, ticks=row['ticks'], hash=row['r4']))
        elif stage == 'event_lookup':
            pending = row
        elif stage == 'event_value' and pending is not None:
            lookups.append(dict(hash=pending['r5'], course=pending['r4'], ticks=pending['ticks'],
                                value_type=row['value_type'], callback=row['value_type'] == 5))
            pending = None
        elif stage == 'instance_bound':
            bindings.append(dict(instance_id=row['instance_id'], flags=row['flags'],
                                 property_flags=row['property_flags']))
    windows, unpaired = countdown_windows(dispatches)
    return dict(dispatches=dispatches, named_lookups=lookups, bindings=bindings,
                countdown_window_seconds=windows[0] if windows else None,
                countdown_windows_seconds=windows,
                unpaired_dispatches=unpaired,
                events_per_translation_unit=counts,
                truncated_translation_units=[name for name, count in counts.items() if count >= 1000],
                limits='Observed dispatch and binding only. Missing events in a capped translation unit '
                       'are unknown; no countdown animation or restart restoration is established.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--summarize', type=Path,
                        help='Report on a runtime log instead of building the observer')
    args = parser.parse_args()
    if args.summarize:
        report = summarize(read_observations(args.summarize))
        report['source_log_sha256'] = sha(args.summarize)
        print(json.dumps(report, indent=2))
        return
    if args.game is None or args.output is None:
        parser.error('Building the observer needs --game and --output')
    if sha(args.game/'sys/main.dol') != DOL_SHA256:
        raise ValueError('Countdown observer requires pinned GXBE69 executable')
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/'local'):
        raise ValueError('Diagnostic outputs must stay under local/')
    output.mkdir(parents=True, exist_ok=False)
    header = output/HEADER.name
    header.write_bytes(HEADER.read_bytes())
    original = MODULE/'build/gGXBE69_recomp.dylib'
    receipt = dict(dol_sha256=DOL_SHA256, original_module_sha256=sha(original),
                   header_sha256=sha(header), hooks=HOOKS, sources={}, commands=[])
    commands = subprocess.check_output([str(ROOT/'local/tooling/ninja'), '-t', 'commands',
                                        'gGXBE69_recomp.dylib'], cwd=MODULE/'build', text=True).splitlines()
    replacements = {}
    for name, hooks in HOOKS.items():
        source = MODULE/'codegen/generated/chunks'/name
        data = source.read_text()
        marker = '#include "../generated.h"'
        if data.count(marker) != 1:
            raise ValueError('Generated chunk include changed')
        data = data.replace(marker, f'#include "{MODULE / "codegen/generated/generated.h"}"\n#include "{header}"')
        for address, (stage, binding) in hooks.items():
            marker = f'label_{address}:\n'
            if data.count(marker) != 1:
                raise ValueError(f'Countdown observation label changed: {address}')
            data = data.replace(marker, marker+f'    ssx_gate_trace(ctx, "{stage}", {binding});\n')
        copy, obj = output/name, output/(name+'.o')
        copy.write_text(data)
        command = next(c for c in commands if c.endswith('/'+name))
        argv = shlex.split(command)
        replacements[argv[argv.index('-o')+1]] = str(obj)
        command = compile_copy(command, copy, obj)
        receipt['sources'][name] = dict(original_sha256=sha(source), observed_sha256=sha(copy))
        receipt['commands'].append(command)
        subprocess.run(command, cwd=MODULE/'build', check=True)
    link = shlex.split(next(c for c in commands if ' -o gGXBE69_recomp.dylib ' in c))
    link = [replacements.get(a,a) for a in link[2:link.index('&&',2)]]
    link[link.index('-o')+1] = str(output/'probe.dylib')
    receipt['commands'].append(link)
    subprocess.run(link, cwd=MODULE/'build', check=True)
    if sha(original) != receipt['original_module_sha256']:
        raise RuntimeError('Original module changed during observer build')
    receipt['module_sha256'] = sha(output/'probe.dylib')
    (output/'build.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(output/'probe.dylib')


if __name__ == '__main__':
    main()
