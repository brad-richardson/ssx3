#!/usr/bin/env python3
"""Build an isolated startup observer; preserve production/vendor binaries."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import threading
import time

from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha
import native_gamecube as native


def build(args):
    if sha(args.game/'sys/main.dol')!=native.PINS['dol_sha256']:
        raise ValueError('Startup addresses require the pinned GXBE69 executable')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'local'):
        raise ValueError('Startup research outputs must be under local/')
    output.mkdir(parents=True,exist_ok=False)
    original=VENDOR/'vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
    header=ROOT/'native/diagnostics/startup_skip.h'
    (output/header.name).write_bytes(header.read_bytes())
    text=original.read_text()
    marker='          const u32 runtime_dispatch_address = m_guest.pc;'
    if text.count(marker)!=1:
        raise ValueError('Startup dispatch seam changed')
    text='#include "'+str(output/header.name)+'"\n'+text.replace(marker,'          StartupBoot::Step(m_guest);\n'+marker)
    source=output/'Startup_Run.cpp'; source.write_text(text)
    commands=subprocess.check_output([str(ROOT/'local/tooling/ninja'),'-C',str(BUILD),'-t','commands','moderngekko-run'],text=True).splitlines()
    receipt=dict(schema=1,source_sha256=sha(original),header_sha256=sha(header),
                 dol_sha256=native.PINS['dol_sha256'],game=str(args.game.resolve()),
                 production_sha256=sha(BUILD/'moderngekko-run'),commands=[])
    compile=compile_copy(next(c for c in commands if c.endswith('/StaticRecompCore_Run.cpp')),source,output/'startup.o')
    receipt['commands'].append(compile); subprocess.run(compile,cwd=BUILD,check=True)
    link=shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link=link[2:link.index('&&',2)]
    link[link.index('-o')+1]=str(output/'player')
    link.insert(link.index('libmoderngekko.a'),str(output/'startup.o'))
    receipt['commands'].append(link); subprocess.run(link,cwd=BUILD,check=True)
    if sha(BUILD/'moderngekko-run')!=receipt['production_sha256']:
        raise RuntimeError('Production player changed during diagnostic build')
    receipt['player_sha256']=sha(output/'player')
    (output/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(output/'player')


def read_events(path):
    rows=[]
    if path.exists():
        for line in path.read_text().splitlines():
            try:rows.append(json.loads(line))
            except ValueError:pass # concurrently written final row
    return rows


def run(args):
    player=args.player.resolve()
    if not player.is_relative_to(ROOT/'local'):
        raise ValueError('Use an isolated player under local/')
    receipt=json.loads((player.parent/'build.json').read_text())
    if sha(player)!=receipt['player_sha256']:
        raise ValueError('Startup player does not match its build receipt')
    if not 0<args.seconds<=180:
        raise ValueError('Startup checks must last at most 180 seconds')
    if Path(args.profile).name!=args.profile or args.profile in ('.','..'):
        raise ValueError('Profile must be a single directory name')
    profile=ROOT/'local/native/profiles'/args.profile
    if profile.exists():
        raise ValueError('Use a fresh isolated startup profile')
    trace=player.parent/(args.profile+'.jsonl')
    if trace.exists():
        raise ValueError('Startup trace already exists')
    os.environ.update(SSX_STARTUP_TRACE=str(trace),SSX_DEBUG_MAIN_MENU='1' if args.skip else '0',
                      MTL_DEBUG_LAYER='1',SSX3_DISPATCH_SAMPLES='0')
    stop=threading.Event(); errors=[]; inputs=[]
    def drive():
        fd=None
        try:
            deadline=time.monotonic()+args.seconds
            while not stop.wait(.05) and time.monotonic()<deadline:
                rows=read_events(trace)
                if any(r.get('event')=='title_ready' for r in rows):
                    fd=os.open(profile/'Pipes/ssx3',os.O_WRONLY|os.O_NONBLOCK)
                    os.write(fd,b'PRESS START\n');inputs.append(dict(action='press_start',wall=time.time()))
                    release=time.monotonic()+2
                    while not stop.wait(.02) and time.monotonic()<release:
                        if any(r.get('event') in ('main_menu_loading','main_menu_ready') for r in read_events(trace)):break
                    os.write(fd,b'RELEASE START\n');inputs.append(dict(action='release_start',wall=time.time()))
                    break # One attempt, never timed button mashing.
        except Exception as error:errors.append(str(error))
        finally:
            if fd is not None:
                try:os.write(fd,b'RELEASE START\n')
                finally:os.close(fd)
    worker=threading.Thread(target=drive);worker.start()
    original_executable=native.executable
    native.executable=lambda name:player
    try:
        native.launch(argparse.Namespace(game=args.game,profile=args.profile,seconds=args.seconds,
            headless=False,jit_fallback=False,pipe_controller=True))
    finally:
        stop.set();worker.join();native.executable=original_executable
    rows=read_events(trace)
    result=dict(player_sha256=sha(player),skip_requested=args.skip,events=rows,inputs=inputs,input_errors=errors,
                menu_reached=any(r.get('event')=='main_menu_ready' for r in rows))
    (player.parent/(args.profile+'-check.json')).write_text(json.dumps(result,indent=2)+'\n')
    if errors or (args.skip and (not result['menu_reached'] or not any(r.get('event')=='startup_movies_skipped' for r in rows))):
        raise RuntimeError('Startup shortcut did not establish the main-menu state; inspect its trace')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    compile=commands.add_parser('build')
    compile.add_argument('--output',type=Path,required=True)
    compile.add_argument('--game',type=Path,default=native.DEFAULT_GAME)
    check=commands.add_parser('run')
    check.add_argument('--player',type=Path,required=True)
    check.add_argument('--game',type=Path,default=native.DEFAULT_GAME)
    check.add_argument('--profile',required=True)
    check.add_argument('--skip',action='store_true')
    check.add_argument('--seconds',type=float,default=60)
    args=parser.parse_args()
    {'build':build,'run':run}[args.command](args)
