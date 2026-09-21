#!/usr/bin/env python3
"""Emit raw-word-verified E8 wall and active dispatch-binding receipts."""
import hashlib
from pathlib import Path
import re
from e8_static import Elf, ROOT

HERE=Path(__file__).resolve().parent
FORK=ROOT.parent/'PS2Recomp'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    e=Elf(ROOT)
    out=[]
    def emit(x=''):out.append(str(x))
    emit(f'# E8 static wall; ELF {e.path}; bytes={len(e.data)} sha256={hashlib.sha256(e.data).hexdigest()}')
    for name,lo,hi in [
        ('card object factory',0x2c22c8,0x2c22fc),
        ('constructor and initial state/outstanding fields',0x2c3fa8,0x2c40a0),
        ('UI launch request',0x241380,0x2413fc),
        ('UI selection to virtual port selector',0x23fae0,0x23fb54),
        ('port selector to missing busy query',0x2c4480,0x2c44dc),
        ('intended busy query',0x2c5140,0x2c5168),
        ('UI update and busy gate',0x23d660,0x23d6f4),
        ('state setter and fallback GetInfo',0x2c48c0,0x2c490c),
        ('state3 request entry',0x2c4980,0x2c4990),
        ('state setter default',0x2c50ac,0x2c513c),
        ('update state0 dispatch',0x2c58ec,0x2c5914),
        ('update idle tail',0x2c6070,0x2c6128),
        ('separately observed sibling query',0x2c5358,0x2c5390),
        ('sibling virtual caller',0x2d3810,0x2d383c),
    ]:
        emit(f'\n## {name}: [{lo:#x},{hi:#x})')
        for pc in range(lo,hi,4):emit(e.decode(pc))
    emit('\n## Pointer and jump-table words')
    for pc in [0x486f94,0x486fa4,0x486fd4,0x48711c,0x486350,0x4860c8]:
        emit(f'{pc:08x} -> {e.word(pc):08x}')
    emit('\n## Active generated binding inventory (read only)')
    p=FORK/'ps2xRuntime/src/runner/register_functions.cpp'
    emit(f'{p} sha256={sha(p)} bytes={p.stat().st_size}')
    lines=p.read_text().splitlines();targets=[0x2c50e0,0x2c5118,0x2c5140,0x2c5358,0x2c55d8,0x426230]
    bound={pc:[] for pc in targets}
    for n,line in enumerate(lines,1):
        m=re.search(r'// 0x([0-9a-f]+)$',line)
        if m and int(m[1],16) in bound:bound[int(m[1],16)].append((n,line.strip()))
    for pc,rows in bound.items():
        emit(f'{pc:#x} bindings={len(rows)}')
        for n,line in rows:emit(f'  {n}: {line}')
    for pc in [0x2c5140,0x2c5358]:
        owner=e.owner(pc);p=ROOT/'output'/f'{owner[2]}_0x{owner[0]:x}.cpp'
        emit(f'\nOUT target {pc:#x}; owner={owner}; {p.name} sha256={sha(p)}')
        content=p.read_text()
        emit(f'entry_case={bool(re.search(rf"case 0x{pc:x}u:",content))} entry_label={bool(re.search(rf"^label_{pc:x}:",content,re.M))} instruction_present={bool(re.search(rf"// 0x{pc:x}:",content))}')
        for n,line in enumerate(content.splitlines(),1):
            if re.search(rf'case 0x{pc:x}u:|^label_{pc:x}:',line):emit(f'{n}: {line.strip()}')
    emit('\n# E8 STATIC WALL TAIL COMPLETE; all ranges end-exclusive; no source mutated')
    (HERE/'e8-wall-dis.txt').write_text('\n'.join(out)+'\n')
    sections=[
        ('ps2xRuntime/include/ps2_runtime.h',333,346),
        ('ps2xRuntime/src/lib/ps2_runtime.cpp',1421,1426),
        ('ps2xRuntime/src/lib/ps2_runtime.cpp',1674,1684),
        ('ps2xRuntime/src/lib/ps2_runtime.cpp',1808,1829),
        ('ps2xRuntime/src/lib/ps2_runtime.cpp',2017,2080),
    ]
    source=[]
    for name,start,end in sections:
        p=FORK/name;lines=p.read_text().splitlines()
        source.append(f'\n# {p} SHA256={sha(p)} lines={start}..{end}')
        source.extend(f'{n}: {lines[n-1]}' for n in range(start,end+1))
    p=ROOT/'output/sub_002C4410_0x2c4410.cpp';lines=p.read_text().splitlines()
    source.append(f'\n# Generated caller (read only) {p} SHA256={sha(p)}')
    source.extend(f'{n}: {lines[n-1]}' for n in range(479,542))
    p=ROOT/'output/sub_002C50E0_0x2c50e0.cpp';lines=p.read_text().splitlines()
    source.append(f'\n# Generated query owner (read only) {p} SHA256={sha(p)}')
    source.extend(f'{n}: {lines[n-1]}' for lo,hi in [(15,29),(103,150)] for n in range(lo,hi))
    source.append('\n# E8 RUNTIME POLICY TAIL COMPLETE')
    (HERE/'e8-runtime-policy.txt').write_text('\n'.join(source)+'\n')
    print('e8-wall-dis.txt',len(out),'lines; e8-runtime-policy.txt',len(source),'lines')
    print('# E8 WALL MINER TAIL COMPLETE')


if __name__=='__main__':main()
