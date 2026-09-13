#!/usr/bin/env python3
"""Build an isolated read-only static-collision diagnostic module.

Only three copied generated chunks change; original module and sources remain
intact. Set SSX_COLLISION_INSTANCE to the packed track/instance ID (for example
0x08000258) before using the generated course_check.py. Logs include every
observed binder, broad-phase and narrow-phase visit for that instance, including
same-chunk AOT jumps. Native correctness gates still apply; this is not a
performance measurement and no geometry/guest state is changed by the hooks.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess

from gamecube_draw_trace import ROOT, sha, compile_copy
from gamecube_native_trace import DOL_SHA256

MODULE = ROOT / 'local/native/ssx3-module'
HEADER = ROOT / 'native/diagnostics/collision_trace.h'
HOOKS = {
    'chunk_0118_text1_801D97A0.c': {
        '801DB554': ('broad_sweep', 'ctx->gpr[4]', 'ssx_collision_word(ctx,ctx->gpr[3])', '-1'),
        '801DC718': ('broad_contact', 'ctx->gpr[4]', 'ssx_collision_word(ctx,ctx->gpr[3])', '-1'),
    },
    'chunk_0119_text1_801DD7A0.c': {
        '801DDBC8': ('narrow_enter', 'ctx->gpr[4]', 'ctx->gpr[3]', '-1'),
        '801DE444': ('narrow_exit', 'ctx->gpr[31]', 'ctx->gpr[21]', '(int)ctx->gpr[3]'),
    },
    'chunk_0145_text1_802457A0.c': {
        '8024620C': ('bound', 'ctx->gpr[9]', '0', '-1'),
    },
}


def instrument(source, hooks, header):
    marker = '#include "../generated.h"'
    if source.count(marker) != 1:
        raise ValueError('Generated chunk header changed')
    source = source.replace(marker, f'#include "{MODULE / "codegen/generated/generated.h"}"\n#include "{header}"')
    for address, (stage, instance, query, contacts) in hooks.items():
        marker = f'label_{address}:\n'
        if source.count(marker) != 1:
            raise ValueError(f'Collision observation label changed: {address}')
        source = source.replace(marker, marker +
            f'    ssx_collision_trace(ctx, "{stage}", {instance}, {query}, {contacts});\n')
    return source


def build(args):
    if sha(args.game / 'sys/main.dol') != DOL_SHA256:
        raise ValueError('Collision labels require the pinned GXBE69 executable')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'local'):
        raise ValueError('Diagnostic outputs must remain under local/')
    output.mkdir(parents=True,exist_ok=False)
    (output/'build').mkdir()
    original=MODULE/'build/gGXBE69_recomp.dylib'
    receipt=dict(schema=1,dol_sha256=DOL_SHA256,original_module_sha256=sha(original),
                 header_sha256=sha(HEADER),sources={},commands=[])
    header=output/HEADER.name;header.write_bytes(HEADER.read_bytes())
    commands=subprocess.check_output([str(ROOT/'local/tooling/ninja'),'-t','commands','gGXBE69_recomp.dylib'],
                                    cwd=MODULE/'build',text=True).splitlines()
    replacements={}
    for name,hooks in HOOKS.items():
        source=MODULE/'codegen/generated/chunks'/name
        copy=output/name;copy.write_text(instrument(source.read_text(),hooks,header))
        command=next(c for c in commands if c.endswith('/'+name))
        obj=output/(name+'.o')
        replacements[shlex.split(command)[shlex.split(command).index('-o')+1]]=str(obj)
        compile_command=compile_copy(command,copy,obj)
        receipt['sources'][name]=dict(original_sha256=sha(source),instrumented_sha256=sha(copy),hooks=hooks)
        receipt['commands'].append(compile_command)
        subprocess.run(compile_command,cwd=MODULE/'build',check=True)
    link=shlex.split(next(c for c in commands if ' -o gGXBE69_recomp.dylib ' in c))
    link=link[2:link.index('&&',2)]
    link=[replacements.get(arg,arg) for arg in link]
    link[link.index('-o')+1]=str(output/'build/gGXBE69_recomp.dylib')
    receipt['commands'].append(link)
    subprocess.run(link,cwd=MODULE/'build',check=True)
    if sha(original)!=receipt['original_module_sha256']:
        raise RuntimeError('Original module changed during diagnostic build')
    receipt['module_sha256']=sha(output/'build/gGXBE69_recomp.dylib')
    launcher=output/'run_native.py'
    launcher.write_text('import sys\nfrom pathlib import Path\n'+f'ROOT=Path({str(ROOT)!r})\n'+
        "sys.path.insert(0,str(ROOT/'tools'))\nimport native_gamecube as native\n"+
        f'native.MODULE=Path({str(output)!r})\nnative.main()\n')
    course=output/'course_check.py'
    course.write_text('import sys\nfrom pathlib import Path\n'+f'ROOT=Path({str(ROOT)!r})\n'+
        "sys.path.insert(0,str(ROOT/'tools'))\nimport gamecube_course_check as course\n"+
        'original=course.subprocess.Popen\ndef launch(args,*pos,**kw):\n args=list(args)\n'+
        " target=str(ROOT/'tools/native_gamecube.py')\n"+
        f' if target in args: args[args.index(target)]={str(launcher)!r}\n'+
        ' return original(args,*pos,**kw)\ncourse.subprocess.Popen=launch\ncourse.main()\n')
    receipt['launchers']={p.name:sha(p) for p in (launcher,course)}
    (output/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(course)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args())
