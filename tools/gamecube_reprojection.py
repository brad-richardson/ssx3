#!/usr/bin/env python3
"""Build/run an isolated GPU capture player. Offline research; never presents extra frames.

Captures at most eight frames after SSX_REPROJECTION_AFTER (default 140 seconds).
The first perspective-to-orthographic boundary is a candidate HUD split, explicitly
invalidated if perspective draws follow it. Color subtraction is NOT a HUD alpha layer.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys
from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha


def replace_once(source, marker, replacement):
    if source.count(marker) != 1:
        raise ValueError(f'Capture injection point changed: {marker!r}')
    return source.replace(marker, replacement)


def build(args):
    out=args.output.resolve()
    if not out.is_relative_to(ROOT/'local'):
        raise ValueError('Research outputs must remain under local/')
    out.mkdir(parents=True,exist_ok=False)
    commands=subprocess.check_output([str(ROOT/'local/tooling/ninja'),'-C',str(BUILD),'-t','commands','moderngekko-run'],text=True).splitlines()
    header=ROOT/'native/diagnostics/reprojection_capture.h'
    copy=out/header.name;copy.write_bytes(header.read_bytes())
    receipt=dict(schema=1,production_runner_sha256=sha(BUILD/'moderngekko-run'),header_sha256=sha(header),commands=[],sources={})
    objects=[]
    def run(command):
        receipt['commands'].append(command)
        subprocess.run(command,cwd=BUILD,check=True)
    for name in ('VertexManagerBase','TextureCacheBase','OpcodeDecoding'):
        original=VENDOR/f'vendor/dolphin/Source/Core/VideoCommon/{name}.cpp'
        source=original.read_text()
        if name=='VertexManagerBase':
            source=replace_once(source,'std::unique_ptr<VertexManagerBase> g_vertex_manager;',f'#include "{copy}"\nstd::unique_ptr<VertexManagerBase> g_vertex_manager;')
            marker='  vertex_shader_manager.SetConstants(texture_names, xf_state_manager);'
            source=replace_once(source,marker,marker+'\n  ReprojectionCapture::Draw();')
        elif name=='TextureCacheBase':
            marker='  const bool is_xfb_copy = !is_depth_copy && !isIntensity && dstFormat == EFBCopyFormat::XFB;'
            source=replace_once(source,marker,marker+'\n  if (is_xfb_copy) ReprojectionCapture::Xfb(dstAddr, srcRect);')
            source=f'#include "{copy}"\n'+source
        else:
            marker='    else\n      LoadIndexedXF(array, index, address, size);'
            source=replace_once(source,marker,'    else {\n      LoadIndexedXF(array, index, address, size);\n      ReprojectionCapture::Indexed(array,index,address,size);\n    }')
            source=f'#include "{copy}"\n'+source
        target=out/f'{name}.cpp';target.write_text(source)
        obj=out/f'{name}.o';objects.append(str(obj))
        run(compile_copy(next(c for c in commands if c.endswith(f'/{name}.cpp')),target,obj))
        receipt['sources'][name]=dict(original_sha256=sha(original),instrumented_sha256=sha(target))
    link=shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link=link[2:link.index('&&',2)]
    link[link.index('-o')+1]=str(out/'player')
    link[link.index('libmoderngekko.a'):link.index('libmoderngekko.a')]=objects
    run(link)
    launcher=(f'import sys\nfrom pathlib import Path\nsys.path.insert(0,{str(ROOT/"tools")!r})\n'
              'import native_gamecube as native\noriginal=native.executable\n'
              f'player=Path({str(out/"player")!r})\n'
              'native.executable=lambda name: player if name=="moderngekko-run" else original(name)\n'
              'native.main()\n')
    (out/'run_native.py').write_text(launcher)
    receipt.update(player_sha256=sha(out/'player'),launcher_sha256=sha(out/'run_native.py'))
    if sha(BUILD/'moderngekko-run')!=receipt['production_runner_sha256']:
        raise ValueError('Production player changed during build')
    (out/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(out/'player')


def check(args,remaining):
    import gamecube_course_check as course
    directory=args.player_dir.resolve()
    receipt=json.loads((directory/'build.json').read_text())
    if sha(directory/'player')!=receipt['player_sha256'] or sha(directory/'run_native.py')!=receipt['launcher_sha256']:
        raise ValueError('Research player or launcher changed')
    original=course.subprocess.Popen
    def launch(command,*pos,**kw):
        command=list(command);target=str(ROOT/'tools/native_gamecube.py')
        if target in command: command[command.index(target)]=str(directory/'run_native.py')
        return original(command,*pos,**kw)
    course.subprocess.Popen=launch
    sys.argv=[str(ROOT/'tools/gamecube_course_check.py'),*remaining]
    course.main()


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    b=sub.add_parser('build');b.add_argument('--output',type=Path,required=True)
    c=sub.add_parser('check');c.add_argument('--player-dir',type=Path,required=True)
    args,remaining=p.parse_known_args()
    if args.command=='build':
        if remaining:p.error(f'Unknown arguments: {remaining}')
        build(args)
    else:check(args,remaining)

if __name__=='__main__':main()
