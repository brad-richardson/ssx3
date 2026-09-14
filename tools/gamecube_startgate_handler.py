#!/usr/bin/env python3
"""Build a bounded countdown visibility handler in an isolated native module.

It hooks the two observed countdown dispatches and the staged instances'
binding, and drives the visibility bit: set on StartlightBegin, cleared on
StartgateOpen. It writes the bit in the course script's own staged definition
-- the record those three instances use and nothing else -- and in each live
instance's `+128` word, because the engine copies the bit across when the
instance binds.

**Both writes land and the gate is not drawn.** That bit is the course's
load-time visibility, not a runtime switch; see docs/gamecube-scenery.md. This
tool is retained as the harness that established it, and to drive whatever
operation replaces the flag write -- most likely the engine's own node
lifecycle, builtin 2 (8019193c) DeadNode/RestoreNode.

Use it with a --countdown-ready candidate, whose definition differs from
ordinary scenery only in that bit, so the writes are minimal and reversible.

Set SSX_STARTGATE_HANDLER=1 and SSX_STARTGATE_FIRST to the staged first packed
instance ID, then pass the built dylib to gamecube_course_check.py --module.
Pass --summarize a runtime log to turn the handler's own lines into a report.

This is a host-side hook on generated guest code, not a course binding. The
shipping path is still a real callback through the named-event lookup, which
these observations now describe: the lookup returns value type 0, the events
re-dispatch, they are not always paired, and the instances bind once.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess

from gamecube_draw_trace import ROOT, compile_copy, sha
from gamecube_native_trace import DOL_SHA256

MODULE = ROOT/'local/native/ssx3-module'
HEADER = ROOT/'native/diagnostics/startgate_handler.h'
VISIBLE_FLAG = 0x00010000
# Show on the lights, hide on the gate: hiding is the donor's own authored
# post-countdown state, so the gate "opens" by leaving, needing no animation.
HOOKS = {
    'chunk_0063_text1_800FD7A0.c': {'801015C8': 'ssx_gate_set(ctx, 0, "startgate_open");'},
    'chunk_0064_text1_801017A0.c': {'80101804': 'ssx_gate_set(ctx, 1, "startlight_begin");'},
    'chunk_0145_text1_802457A0.c': {'8024620C': 'ssx_gate_bind(ctx);'},
}
MARKER = '[ssx-startgate-handler] '


def read_actions(log):
    """Collect the handler's own retained lines from a native runtime log."""
    rows = []
    for line in log.read_text(errors='replace').splitlines():
        if line.startswith(MARKER):
            rows.append(json.loads(line[len(MARKER):]))
    if not rows:
        raise ValueError('No handler actions in that log')
    return rows


def summarize(rows):
    """Report what the handler actually changed, and every refusal."""
    binds = [r for r in rows if r['event'] == 'bind']
    sets = [r for r in rows if r['event'] == 'set']
    refused = [r for r in rows if r['event'] in ('reject', 'conflict', 'unbound')]
    definitions = sorted({r['definition'] for r in binds})
    changed = [r for r in sets if r['before'] != r['after'] or r.get('instances_changed')]
    shows = [r for r in changed if r['show']]
    hides = [r for r in changed if not r['show']]
    for row in sets:
        if (row['before'] & ~VISIBLE_FLAG != row['after'] & ~VISIBLE_FLAG or
                row.get('instance_before', 0) & ~VISIBLE_FLAG !=
                row.get('instance_after', 0) & ~VISIBLE_FLAG):
            raise ValueError('Handler changed a bit outside the visibility flag')
    return dict(
        bindings=binds, definitions=definitions,
        bound_definition=definitions[0] if len(definitions) == 1 else None,
        dispatches=len(sets), effective_writes=len(changed),
        shown=len(shows), hidden=len(hides),
        redundant=len(sets)-len(changed),
        ended_visible=bool(changed and changed[-1]['show']),
        refusals=refused,
        limits='Reports the handler\'s own writes. Whether the gate was drawn is a rendering '
               'question that only screenshots answer, and no flipbook or timing runs.')


def build(args):
    if sha(args.game/'sys/main.dol') != DOL_SHA256:
        raise ValueError('Countdown handler requires pinned GXBE69 executable')
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
        include = '#include "../generated.h"'
        if data.count(include) != 1:
            raise ValueError('Generated chunk include changed')
        data = data.replace(include, f'#include "{MODULE / "codegen/generated/generated.h"}"\n#include "{header}"')
        for address, call in hooks.items():
            marker = f'label_{address}:\n'
            if data.count(marker) != 1:
                raise ValueError(f'Countdown handler label changed: {address}')
            data = data.replace(marker, marker+f'    {call}\n')
        copy, obj = output/name, output/(name+'.o')
        copy.write_text(data)
        command = next(c for c in commands if c.endswith('/'+name))
        argv = shlex.split(command)
        replacements[argv[argv.index('-o')+1]] = str(obj)
        command = compile_copy(command, copy, obj)
        receipt['sources'][name] = dict(original_sha256=sha(source), handled_sha256=sha(copy))
        receipt['commands'].append(command)
        subprocess.run(command, cwd=MODULE/'build', check=True)
    link = shlex.split(next(c for c in commands if ' -o gGXBE69_recomp.dylib ' in c))
    link = [replacements.get(a, a) for a in link[2:link.index('&&', 2)]]
    link[link.index('-o')+1] = str(output/'handler.dylib')
    receipt['commands'].append(link)
    subprocess.run(link, cwd=MODULE/'build', check=True)
    if sha(original) != receipt['original_module_sha256']:
        raise RuntimeError('Original module changed during handler build')
    receipt['module_sha256'] = sha(output/'handler.dylib')
    (output/'build.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(output/'handler.dylib')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--summarize', type=Path,
                        help='Report on a runtime log instead of building the handler')
    args = parser.parse_args()
    if args.summarize:
        report = summarize(read_actions(args.summarize))
        report['source_log_sha256'] = sha(args.summarize)
        print(json.dumps(report, indent=2))
        return
    if args.game is None or args.output is None:
        parser.error('Building the handler needs --game and --output')
    build(args)


if __name__ == '__main__':
    main()
