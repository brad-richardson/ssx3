#!/usr/bin/env python3
"""Emit EF's static receipt bundle to stdout; reads only, no runtime capture.

Run from the ssx3 root with COPYFILE_DISABLE=1 and python3 -B. Redirect only
into local/research/EF/ if a persisted bundle is wanted. Dynamic observations
come exclusively from git-show of committed research artifacts.
"""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from ef_static import Elf, ROOT

REPO = Path(__file__).resolve().parents[3]
FORK = ROOT.parent / 'PS2Recomp'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def committed(path):
    return git('show', f'HEAD:{path}')


def section(name):
    print(f'\n## {name}')


def main():
    e = Elf(ROOT)
    print('# EF standalone static receipts; no boots, builds, emulator writes, or fresh traces')
    print('ssx3_HEAD', git('rev-parse', 'HEAD').decode().strip())
    print('fork_HEAD', subprocess.check_output(['git','-C',str(FORK),'rev-parse','HEAD']).decode().strip())
    print('ELF', e.path, 'bytes', len(e.data), 'sha256', sha(e.data))
    print('All disassembly annotations below have ELF-matching OUT words; ranges end exclusive.')

    section('R1 committed E4/E5 census and kept tails')
    for lane in ['E4', 'E5']:
        for name in ['REPORT.md', f'{lane.lower()}-history.txt', f'{lane.lower()}-present.txt']:
            path = f'local/research/{lane}/{name}'
            b = committed(path)
            print('SOURCE', path, 'bytes', len(b), 'sha256', sha(b))
            lines = b.decode().splitlines()
            if name=='REPORT.md':
                print('\n'.join(lines[-9:]))
            elif name.endswith('present.txt'):
                print('\n'.join(lines))
            else:
                ev = [x for x in lines if x.startswith('[e4:ev]')]
                print('\n'.join(lines[:3]))
                print('kinds', dict(Counter(re.search(r'kind=(\w+)',x)[1] for x in ev)))
                regs = Counter(re.search(r'reg=(0x[0-9a-f]+):',x)[1] for x in ev if 'kind=reg ' in x)
                print('register_counts',dict(regs))
                print('draw_fbps',dict(Counter(re.search(r'fbp=(\d+)',x)[1] for x in ev if 'kind=draw ' in x)))
                tags = Counter(re.search(r'gif=([^ ]+)',x)[1] for x in ev if 'kind=gif ' in x)
                print('gif_tags(size,nloop,flg,nreg)',dict(tags))
                print('TAIL',lines[-1])
    path='local/research/E5/e5-watch-series.txt'
    b=committed(path)
    rows=[l.split() for l in b.decode().splitlines() if not l.startswith('#')]
    print('SOURCE',path,'rows',len(rows),'sha256',sha(b))
    for reg in sorted({r[2] for r in rows}):
        rr=[r for r in rows if r[2]==reg]
        print(reg,'count',len(rr),'values',dict(Counter(r[4] for r in rr)),
              'pc/thread/ra',dict(Counter('/'.join(r[5:8]) for r in rr)))
    print('HEAD',rows[:5]); print('TAIL',rows[-5:])

    section('R2 committed runtime joins; older boots, not a same-boot E5 S watch')
    for path in ['local/research/T1/park-snapshot.json','local/research/T5/park-snapshot-base.json',
                 'local/research/T12/park-snapshot-dev.json','local/research/T12/park-snapshot-rel.json']:
        b=committed(path); j=json.loads(b)
        print('SOURCE',path,'sha256',sha(b))
        for t in j['threads']:
            if t['id']==5:
                print('thread5',t)
                if t['sp']=='0x622480':
                    print('S = sp + 0x10 + 0xb0 - 0x1000 - 0x5ae0 =',hex(0x622480+0xc0-0x1000-0x5ae0))
        for r in j['hot_pc']:
            if r['pc'] in ['0x375a08','0x375a40','0x395288','0x3691f8','0x37bd98',
                            '0x382af0','0x371940','0x382688','0x3825f8','0x382760']:
                print('hot_pc',r)
    b=committed('local/research/P1/REPORT.md')
    print('SOURCE local/research/P1/REPORT.md sha256',sha(b))
    for n,line in enumerate(b.decode().splitlines(),1):
        if '0x61ba60' in line: print(f'line {n}: {line}')

    section('R3 immediate/displacement census over the ELF executable sections')
    offsets={0x5a88,0x5a84,0x5a78,0x5a7c,0x59e8,0xf44,0x5a74}
    widths={0x1f:16,0x28:1,0x29:2,0x2b:4,0x39:4,0x3e:16,0x3f:8,
            0x2a:4,0x2c:8,0x2d:8,0x2e:4}
    overlap=[]
    for sec in e.sections.values():
        if sec[2]&4 and sec[1]==1 and sec[3]>=0x100000 and sec[3]<0x42e590:
            for pc in range(sec[3],sec[3]+sec[5],4):
                w=e.word(pc); op=w>>26; d=w&65535
                if d in offsets and op not in (0,2,3,0x10,0x11,0x12,0x1c):
                    print(e.decode(pc))
                if op in widths and d<0x5a8c and d+widths[op]>0x5a88:
                    overlap.append(e.decode(pc))
    print('stores with immediate spans overlapping +5a88..+5a8b:',overlap)
    print('Scope: same-base immediate forms; generic pointer writes, bulk zero/copy, and rebased aliases remain separate obligations.')

    ranges=[
        ('R4 S allocation, constructors, publications, thread binding',
         [(0x22696c,0x226990),(0x375a08,0x375a4c),(0x395288,0x3952b0),
          (0x3691f8,0x369218),(0x369368,0x36937c),(0x375c1c,0x375c20),
          (0x375d2c,0x375e48),(0x375fb0,0x375fd8),(0x382740,0x38277c)]),
        ('R5 configuration allocations and field writers',
         [(0x37bd98,0x37be50),(0x37bfec,0x37c040),(0x37c150,0x37c164),
          (0x382af0,0x382b74),(0x382cb0,0x382cf4),(0x395510,0x395580),
          (0x3946d8,0x3946e8),(0x37d040,0x37d060)]),
        ('R6 worker and IRQ state-machine joins',
         [(0x377b1c,0x377b70),(0x3825c0,0x3826e0),(0x3827d8,0x382858),
          (0x3828fc,0x382938),(0x382974,0x382a18),(0x382a18,0x382a54),
          (0x382abc,0x382af0)]),
        ('R7 copy packet, unconditional FRAME_2 signature, submission and VIF unmask',
         [(0x382e64,0x382f60),(0x383250,0x3832d4),(0x3833a8,0x383458),
          (0x383578,0x383588),(0x383674,0x383694),(0x383724,0x383770),
          (0x371940,0x371a54)]),
        ('R8 unrelated literal matches and alternate caller',
         [(0x216978,0x216988),(0x216f4c,0x216f5c),(0x294860,0x29489c),
          (0x3960e8,0x396100)])
    ]
    for name,rs in ranges:
        section(name)
        for lo,hi in rs:
            print(f'RANGE {lo:#x}..{hi:#x}')
            for pc in range(lo,hi,4): print(e.decode(pc))
    section('R9 ELF data: VIF mask/unmask command blocks, vtable, publication slots')
    for lo,hi in [(0x44b430,0x44b440),(0x44b9c0,0x44b9d0),
                  (0x44b3d0,0x44b3e0),(0x493260,0x493278),
                  (0x4a289c,0x4a28a0),(0x4a5b80,0x4a5b84)]:
        for pc in range(lo,hi,4):
            w=e.word(pc)
            print(f'{pc:08x} {w:#010x}' if w is not None else f'{pc:08x} BSS/unmapped')

    section('R10 emulator source slices; static fix-design inputs, no execution')
    sources={
        'ps2xRuntime/src/lib/ps2_runtime.cpp':[(2896,2913)],
        'ps2xRuntime/src/lib/ps2_memory.cpp':[(588,610),(1083,1130),(1216,1255),
            (1294,1337),(1561,1568),(1836,1898),(1913,1959)],
        'ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp':[(250,273),(351,362)],
        'ps2xRuntime/src/lib/gs/gs_frontend.cpp':[(375,407),(679,749),(1532,1538)],
        'ps2xRuntime/src/lib/Kernel/EeScheduler.cpp':[(964,986)],
        'ps2xTest/src/ps2_memory_tests.cpp':[(850,900)],
    }
    for path,rs in sources.items():
        b=(FORK/path).read_bytes(); lines=b.decode().splitlines()
        print('SOURCE',path,'sha256',sha(b))
        for lo,hi in rs:
            for n in range(lo,hi+1): print(f'{n}: {lines[n-1]}')
    section('R11 verified OUT vs runner identities')
    for name in ['sub_00382AF0_0x382af0.cpp','sub_00382760_0x382760.cpp',
                 'sub_00371940_0x371940.cpp','sub_00375A08_0x375a08.cpp']:
        a=(ROOT/'output'/name).read_bytes()
        b=(FORK/'ps2xRuntime/src/runner'/name).read_bytes()
        print(name,'OUT_sha256',sha(a),'runner_sha256',sha(b),'identical',a==b)
    print('\n# EF RECEIPTS TAIL COMPLETE: R1-R11; no new dynamic observations')


if __name__=='__main__':
    main()
