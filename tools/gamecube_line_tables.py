#!/usr/bin/env python3
"""Guest-PC line tables for static-recomp chunks, plus signpost selection.

The Time Profiler leaf report attributes riding CPU to whole 16KB chunk
functions (func_802697A0, ...) with no intra-chunk resolution. The generated
chunk C files already carry one `// ADDR: disasm` comment per guest
instruction, so a line table mapping guest PC -> (chunk, C line, function,
disassembly) can be built without touching codegen or rebuilding the module.

Subcommands:
  build      parse chunk C files + a symbol map into line_tables.json
  symbolize  attribute guest-PC samples (pc_hist, dispatch CSV, pc list)
             to chunks/functions/lines
  signposts  select callback signposts for the hot chunks (JSON + C table)
  annotate   inject #line guest-PC markers into a chunk copy for an isolated
             instrumented rebuild (source-only change; module flags untouched)
  check      cross-check the hot-chunk role claims against the symbol map and
             chunk contents, calling out mismatches

Only stdlib. Game paths stay under local/; tests use fixtures.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The 9 hot chunks from the normal-frame leaf report (16KB static-recomp
# chunks, contiguous [base, base+0x4000) ranges), with the role claimed for
# each by size/loop evidence. Signposts + line tables must confirm or refute
# these at function level; see `check`.
HOT_CHUNKS = {
    0x8022D7A0: dict(role='render batch', note='fdiv-by-255 loop + FIFO emit'),
    0x802197A0: dict(role='cNGCGridMesh terrain', note=''),
    0x802697A0: dict(role='world-streaming decode', note='~70% (denominator unstated)'),
    0x801097A0: dict(role='scene-graph traversal', note=''),
    0x8021D7A0: dict(role='mesh-draw virtuals', note=''),
    0x802317A0: dict(role='batch handlers + state switch', note=''),
    0x8029D7A0: dict(role='GX FIFO writer lib', note='flush dispatcher 0x8029f4d4'),
    0x801C17A0: dict(role='anim pose eval', note=''),
    0x801A57A0: dict(role='rider physics', note=''),
}
CHUNK_SIZE = 0x4000

# Guest PCs with task-level meaning. Included as signposts when they fall
# inside a hot chunk; the callback entries also drive the signpost header's
# own update/render classification.
NAMED_PCS = {
    0x8029F4D4: 'flush dispatcher (GX FIFO writer lib)',
    0x8010550C: 'application update entry',
    0x8010A4C8: 'application render entry',
}

PC_COMMENT = re.compile(r'^\s*// ([0-9A-F]{8}): (.*)$')
PC_ASSIGN = re.compile(r'ctx->pc = 0x([0-9A-Fa-f]{8})u;')
LABEL_DEF = re.compile(r'^label_([0-9A-F]{8}):$')
SWITCH_CASE = re.compile(r'case 0x([0-9A-Fa-f]{8})u: goto label_')
LOOP_DEF = re.compile(r'^static void (loop_[0-9A-F]{8})\(CPUState\* ctx\) \{$')
FUNC_DEF = re.compile(r'^void (func_[0-9A-F]{8})\(CPUState\* ctx\) \{$')
SYMBOL = re.compile(r"^(\S+) = \.[^:]*:0x([0-9A-Fa-f]+); // type:(\S+)(?: size:(0x[0-9A-Fa-f]+))?")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_symbols(text):
    """Parse a dtc-style symbol map into sorted function records."""
    functions = []
    for line in text.splitlines():
        match = SYMBOL.match(line.strip())
        if not match or match.group(3) != 'function':
            continue
        name, start = match.group(1), int(match.group(2), 16)
        size = int(match.group(4), 16) if match.group(4) else 0
        functions.append(dict(name=name, start=start, size=size))
    functions.sort(key=lambda f: f['start'])
    return functions


def function_at(functions, pc):
    """Innermost function containing pc, or None (padding/gaps happen)."""
    best = None
    for func in functions:
        if func['start'] <= pc < func['start'] + func['size']:
            best = func
        elif func['start'] > pc:
            break
    return best


def parse_chunk(path):
    """Parse one generated chunk C file into per-PC line records."""
    text = Path(path).read_text()
    match = re.search(r'text\d_([0-9A-F]{8})\.c$', Path(path).name)
    if not match:
        raise ValueError(f'Chunk filename does not carry a base address: {path}')
    base = int(match.group(1), 16)
    declared = re.search(FUNC_DEF.pattern, text, re.M)
    if not declared or int(declared.group(1)[5:], 16) != base:
        raise ValueError(f'{path}: func_ declaration does not match filename base')
    assigns, labels, switch, loops = {}, {}, set(), {}
    pcs = {}
    for number, line in enumerate(text.splitlines(), 1):
        match = PC_COMMENT.match(line)
        if match:
            pcs[int(match.group(1), 16)] = dict(line=number, disasm=match.group(2).strip())
        for found in PC_ASSIGN.findall(line):
            assigns.setdefault(int(found, 16), number)
        match = LABEL_DEF.match(line)
        if match:
            labels[int(match.group(1), 16)] = number
        for found in SWITCH_CASE.findall(line):
            switch.add(int(found, 16))
        match = LOOP_DEF.match(line)
        if match:
            loops[int(match.group(1)[5:], 16)] = dict(name=match.group(1), line=number)
    if not pcs:
        raise ValueError(f'{path}: no per-instruction PC comments found')
    return dict(base=base, pcs=pcs, assigns=assigns, labels=labels, switch=switch, loops=loops)


def build_tables(chunk_paths, functions):
    """Join chunk parses with the symbol map into per-chunk line tables."""
    tables = dict(schema=1, chunk_size=CHUNK_SIZE, chunks={})
    for path in chunk_paths:
        parsed = parse_chunk(path)
        base = parsed['base']
        records = []
        for pc in sorted(parsed['pcs']):
            info = parsed['pcs'][pc]
            func = function_at(functions, pc)
            records.append(dict(pc=f'{pc:08X}', line=info['line'], disasm=info['disasm'],
                                func=func['name'] if func else None,
                                func_start=f"{func['start']:08X}" if func else None,
                                in_switch=pc in parsed['switch']))
        chunk_funcs = [f for f in functions if base <= f['start'] < base + CHUNK_SIZE]
        tables['chunks'][f'{base:08X}'] = dict(
            file=Path(path).name, records=records,
            functions=[dict(name=f['name'], start=f"{f['start']:08X}", size=f['size']) for f in chunk_funcs],
            loops=[dict(addr=f'{a:08X}', **parsed['loops'][a]) for a in sorted(parsed['loops'])],
            switch_cases=len(parsed['switch']), pc_count=len(records))
    return tables


def build(args):
    chunks = sorted(args.chunks.glob('chunk_*_text*.c'))
    if args.only:
        wanted = {int(c, 16) for c in args.only}
        chunks = [c for c in chunks if int(re.search(r'text\d_([0-9A-F]{8})', c.name).group(1), 16) in wanted]
    if not chunks:
        raise ValueError('No chunk C files selected')
    functions = parse_symbols(args.symbols.read_text())
    tables = build_tables(chunks, functions)
    tables['provenance'] = dict(symbols=str(args.symbols), symbols_sha256=sha(args.symbols),
                                chunk_sha256={c.name: sha(c) for c in chunks})
    args.output.write_text(json.dumps(tables, indent=2) + '\n')
    print(f'{len(tables["chunks"])} chunks, ' +
          f'{sum(c["pc_count"] for c in tables["chunks"].values())} PCs -> {args.output}')


def load_tables(path):
    tables = json.loads(Path(path).read_text())
    index = {}
    for base, chunk in tables['chunks'].items():
        for record in chunk['records']:
            index[int(record['pc'], 16)] = (int(base, 16), record)
    return tables, index


def load_pc_hist(path):
    """Guest-PC histogram rows: (pc, count, table). Buckets are 256-byte."""
    samples = []
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        if row.get('event') != 'pc_hist':
            continue
        for bucket, count in row['buckets']:
            samples.append((int(bucket, 16), count, row['table']))
    return samples


def load_dispatch_csv(path):
    """Sparse chassis dispatch trace: one row per 2^20 native dispatches."""
    import csv
    samples = []
    with open(path, newline='') as stream:
        for fields in csv.reader(stream):
            if len(fields) >= 6 and fields[0].isdigit():
                samples.append((int(fields[1], 16), 1, 'dispatch'))
    return samples


def symbolize_pcs(index, samples):
    """Attribute (pc, weight, source) samples to chunk/function/line."""
    hits = dict(samples=0, attributed=0, by_chunk={}, unattributed=0)
    for pc, weight, source in samples:
        hits['samples'] += weight
        found = index.get(pc)
        if found is None:
            # pc_hist buckets name 256-byte ranges; attribute the bucket head
            # when it lands inside a mapped instruction, else leave it out.
            hits['unattributed'] += weight
            continue
        hits['attributed'] += weight
        base, record = found
        chunk = hits['by_chunk'].setdefault(f'{base:08X}', dict(samples=0, by_func={}))
        chunk['samples'] += weight
        func = chunk['by_func'].setdefault(record['func'] or 'none',
                                           dict(samples=0, lines={}, start=record['func_start']))
        func['samples'] += weight
        line = func['lines'].setdefault(str(record['line']),
                                        dict(samples=0, pc=record['pc'], disasm=record['disasm']))
        line['samples'] += weight
    return hits


def symbolize(args):
    tables, index = load_tables(args.tables)
    samples = []
    for hist in args.pc_hist:
        samples.extend(load_pc_hist(hist))
    for trace in args.dispatch_csv:
        samples.extend(load_dispatch_csv(trace))
    for pc in args.pc:
        samples.append((int(pc, 16), 1, 'cli'))
    hits = symbolize_pcs(index, samples)
    for base in sorted(tables['chunks']):
        role = HOT_CHUNKS.get(int(base, 16), {}).get('role', 'not a hot chunk')
        chunk = hits['by_chunk'].get(base, dict(samples=0, by_func={}))
        top = sorted(chunk['by_func'].items(), key=lambda kv: -kv[1]['samples'])[:5]
        print(f'--- {base} ({role}): {chunk["samples"]} samples ---')
        for name, func in top:
            top_lines = sorted(func['lines'].items(), key=lambda kv: -kv[1]['samples'])[:3]
            detail = ', '.join(f"line {ln} pc={info['pc']} x{info['samples']} [{info['disasm']}]"
                               for ln, info in top_lines)
            print(f'  {name} +{func["start"]}: {func["samples"]} :: {detail}')
    coverage = sorted(hits['by_chunk'])
    print(f'attributed {hits["attributed"]}/{hits["samples"]} samples; '
          f'chunks hit: {len(coverage)}; unattributed: {hits["unattributed"]}')
    if args.output:
        args.output.write_text(json.dumps(hits, indent=2) + '\n')


def select_signposts(tables, per_chunk=3):
    """Deterministic signpost selection: named PCs + top-N functions by size
    + every outlined loop, one entry per hot chunk member."""
    posts = {}
    for base_text, chunk in tables['chunks'].items():
        base = int(base_text, 16)
        if base not in HOT_CHUNKS:
            continue
        switch = {int(r['pc'], 16) for r in chunk['records'] if r['in_switch']}
        by_size = sorted(chunk['functions'], key=lambda f: -f['size'])[:per_chunk]
        for func in by_size:
            posts[int(func['start'], 16)] = dict(
                chunk=base_text, name=func['name'], kind='func',
                role=HOT_CHUNKS[base]['role'], size=func['size'],
                in_switch=int(func['start'], 16) in switch)
        for loop in chunk['loops']:
            posts[int(loop['addr'], 16)] = dict(
                chunk=base_text, name='loop_' + loop['addr'], kind='loop',
                role=HOT_CHUNKS[base]['role'], size=None,
                in_switch=int(loop['addr'], 16) in switch)
    for pc, why in NAMED_PCS.items():
        base = next((b for b in HOT_CHUNKS if b <= pc < b + CHUNK_SIZE), None)
        if base is None:
            continue
        symbol = next((f['name'] for f in tables['chunks'][f'{base:08X}']['functions']
                       if int(f['start'], 16) == pc), f'sub_{pc:08X}')
        posts[pc] = dict(chunk=f'{base:08X}', name=symbol, kind='named',
                         role=why, size=None,
                         in_switch=any(int(r['pc'], 16) == pc and r['in_switch']
                                       for r in tables['chunks'][f'{base:08X}']['records']))
    return [dict(pc=f'{pc:08X}', **posts[pc]) for pc in sorted(posts)]


def signposts(args):
    tables, _ = load_tables(args.tables)
    posts = select_signposts(tables, args.per_chunk)
    payload = dict(schema=1, tables=str(args.tables), signposts=posts,
                   invisible=[p for p in posts if not p['in_switch']],
                   note=('Dispatcher signposts fire only on cross-chunk entries: a '
                         'same-chunk-called function shows zero hits even when hot. '
                         'Zero hits beside a hot pc_hist bucket means same-chunk-only callers.'))
    args.json.write_text(json.dumps(payload, indent=2) + '\n')
    rows = [f'  {{{p["pc"]}u /* {p["name"]} [{p["chunk"]}] {p["role"]}, {p["kind"]}'
            + ('' if p['in_switch'] else ', NOT dispatcher-visible') + ' */},' for p in posts]
    args.c.write_text('// Generated by gamecube_line_tables.py signposts -- do not edit.\n'
                      f'static const u32 kSignpostPcs[{len(posts)}] = {{\n' + '\n'.join(rows) + '\n};\n')
    if args.h:
        args.h.write_text(render_signpost_header(posts, args.tables))
    print(f'{len(posts)} signposts ({len(payload["invisible"])} invisible) -> '
          f'{args.json} + {args.c}' + (f' + {args.h}' if args.h else ''))


SIGNPOST_HEADER_PROLOGUE = '''// Authored diagnostic signposts for the 9 hot GXBE69 chunks. Not game source.
// Isolated research players only: counts cross-chunk entries at named guest
// PCs (top-by-size functions, outlined loops, task-named addresses) while an
// application update/render callback is pending. A same-chunk-called function
// compiles to direct gotos and NEVER fires its signpost: zero hits beside a
// hot pc_hist bucket means same-chunk-only callers, not a cold function.
// Counts are cumulative; SSX_NATIVE_SIGNPOSTS=path snapshots them as JSON
// every 256 callback exits (last snapshot wins; the runtime is SIGTERMed, so
// there is no shutdown flush). No guest instructions are patched.
#pragma once
#include "Core/Core.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>

namespace ChunkSignposts {
using Clock=std::chrono::steady_clock;
static auto start=Clock::now();
static double Now(){return std::chrono::duration<double>(Clock::now()-start).count();}
static constexpr u32 kUpdateEntry=0x8010550c;
static constexpr u32 kRenderEntry=0x8010a4c8;
struct Post{u32 pc;const char* name;const char* chunk;const char* role;const char* kind;};
'''

SIGNPOST_HEADER_EPILOGUE = '''
static const unsigned kCount=sizeof(kPosts)/sizeof(kPosts[0]);
enum{kMax=128};
static_assert(kCount<=kMax,"signpost table overflow");
static u64 s_update[kMax]={},s_render[kMax]={},s_other[kMax]={};
static u64 s_first_tb[kMax]={},s_last_tb[kMax]={};
static double s_first_wall[kMax]={},s_last_wall[kMax]={};
static u32 s_update_ret=0,s_render_ret=0;
static u64 s_exits=0;
static bool Active(){static bool on=[](){const char* p=std::getenv("SSX_NATIVE_SIGNPOSTS");return p&&*p;}();return on;}
static const char* Path(){static const char* p=std::getenv("SSX_NATIVE_SIGNPOSTS");return (p&&*p)?p:nullptr;}
static int Find(u32 pc){
 unsigned lo=0,hi=kCount;
 while(lo<hi){unsigned mid=lo+(hi-lo)/2;
  if(kPosts[mid].pc<pc)lo=mid+1;else hi=mid;}
 return (lo<kCount&&kPosts[lo].pc==pc)?(int)lo:-1;
}
static void Dump(){
 const char* p=Path();if(!p)return;
 FILE* f=std::fopen(p,"w");if(!f)return;
 std::fprintf(f,"{\\"schema\\":1,\\"exits\\":%llu,\\"posts\\":[",
              (unsigned long long)s_exits);
 for(unsigned i=0;i<kCount;++i){
  if(i)std::fprintf(f,",");
  std::fprintf(f,"{\\"pc\\":\\"%08x\\",\\"name\\":\\"%s\\",\\"chunk\\":\\"%s\\","
               "\\"role\\":\\"%s\\",\\"kind\\":\\"%s\\",\\"update\\":%llu,\\"render\\":%llu,"
               "\\"other\\":%llu,\\"first_tb\\":%llu,\\"last_tb\\":%llu,"
               "\\"first_wall\\":%.6f,\\"last_wall\\":%.6f}",
               kPosts[i].pc,kPosts[i].name,kPosts[i].chunk,kPosts[i].role,kPosts[i].kind,
               (unsigned long long)s_update[i],(unsigned long long)s_render[i],
               (unsigned long long)s_other[i],
               (unsigned long long)s_first_tb[i],(unsigned long long)s_last_tb[i],
               s_first_wall[i],s_last_wall[i]);
 }
 std::fprintf(f,"]}\\n");
 std::fclose(f);
}
static inline void Step(CPUState& c){
 if(!Active())return;
 if(c.pc==kUpdateEntry&&!s_update_ret)s_update_ret=c.lr;
 else if(c.pc==kRenderEntry&&!s_render_ret)s_render_ret=c.lr;
 const bool in_render=s_render_ret!=0,in_update=s_update_ret!=0;
 const int hit=Find(c.pc);
 if(hit>=0){
  const unsigned i=(unsigned)hit;
  if(in_render)++s_render[i];else if(in_update)++s_update[i];else ++s_other[i];
  if(!s_first_tb[i]){s_first_tb[i]=c.timebase;s_first_wall[i]=Now();}
  s_last_tb[i]=c.timebase;s_last_wall[i]=Now();
 }
 bool exited=false;
 if(s_render_ret&&c.pc==s_render_ret){s_render_ret=0;exited=true;}
 if(s_update_ret&&c.pc==s_update_ret){s_update_ret=0;exited=true;}
 if(exited&&++s_exits%256==0)Dump();
}
}
'''


def render_signpost_header(posts, tables_path):
    rows = [f'  {{0x{p["pc"]}u,"{p["name"]}","{p["chunk"]}","{p["role"]}","{p["kind"]}"}},'
            for p in posts]
    return (SIGNPOST_HEADER_PROLOGUE +
            f'// Table generated by gamecube_line_tables.py signposts from {tables_path}.\n'
            '// Selection: task-named PCs + top-3 functions by size per chunk +\n'
            '// every outlined loop_* in the 9 hot chunks. Regenerate, do not edit.\n'
            'static const Post kPosts[] = {\n' + '\n'.join(rows) + '\n};\n' +
            SIGNPOST_HEADER_EPILOGUE)


def annotate(args):
    """Inject #line guest-PC markers into a chunk copy.

    Encoding: line = pc - 0x80000000 + 1, file gxbe69_<base>.s. Debug info
    only; generated code is unchanged and no build flag changes.
    """
    parsed = parse_chunk(args.chunk)
    base = parsed['base']
    out = []
    for number, line in enumerate(args.chunk.read_text().splitlines(keepends=True), 1):
        stripped = line.rstrip('\n')
        label = LABEL_DEF.match(stripped)
        loop = LOOP_DEF.match(stripped)
        addr = None
        if label:
            addr = int(label.group(1), 16)
        elif loop:
            addr = int(loop.group(1)[5:], 16)
        if addr is not None:
            if not base <= addr < base + CHUNK_SIZE:
                raise ValueError(f'{args.chunk}:{number}: label pc {addr:08X} outside chunk')
            out.append(f'#line {addr - 0x80000000 + 1} "gxbe69_{base:08X}.s"\n')
        out.append(line)
    args.output.write_text(''.join(out))
    print(f'{args.chunk.name}: {sum(1 for l in out if l.startswith("#line"))} markers -> {args.output}')


def check(args):
    """Cross-check hot-chunk role claims against symbols + chunk contents."""
    functions = parse_symbols(args.symbols.read_text())
    chunks = {c: args.chunks / f'chunk_*_text*_{c:08X}.c' for c in HOT_CHUNKS}
    findings = []
    for base, claim in HOT_CHUNKS.items():
        paths = sorted(args.chunks.glob(f'chunk_*_text*_{base:08X}.c'))
        if not paths:
            findings.append(dict(chunk=f'{base:08X}', status='MISSING', detail='no chunk file'))
            continue
        parsed = parse_chunk(paths[0])
        in_chunk = [f for f in functions if base <= f['start'] < base + CHUNK_SIZE]
        named = [f for f in in_chunk if not f['name'].startswith('fn_')]
        text = paths[0].read_text()
        detail = dict(role=claim['role'], functions=len(in_chunk),
                      named_symbols=[f['name'] for f in named][:10],
                      named_fraction=round(len(named) / max(1, len(in_chunk)), 3),
                      loops=[f'{a:08X}' for a in sorted(parsed['loops'])])
        status, notes = 'OK', []
        if base == 0x8029D7A0:
            if 0x8029F4D4 < base or 0x8029F4D4 >= base + CHUNK_SIZE:
                status, notes = 'MISMATCH', ['0x8029f4d4 outside chunk range']
            else:
                func = function_at(functions, 0x8029F4D4)
                prologue = re.search(r'// 8029F4D4: mflr    r0', text) is not None
                notes.append(f'0x8029f4d4 in {func["name"] if func else "no-symbol"}'
                             f' (start {func["start"]:08X})' if func else 'no symbol covers F4D4')
                if not func or func['start'] != 0x8029F4D4 or not prologue:
                    status = 'MISMATCH'
                    notes.append('F4D4 is not a function entry (expected mflr prologue at symbol start)')
        if base == 0x8022D7A0:
            fdivs = len(re.findall(r': fdivs? ', text))
            stores = len(re.findall(r'mem_write32', text))
            notes.append(f'fdiv(s) sites: {fdivs}; computed-EA stores: {stores}; '
                         f'no literal 255.0/FIFO base in chunk text (both operands are '
                         f'indirect: divisors via fpr loads, stores via computed EA)')
            if fdivs:
                holders = sorted({function_at(functions, int(m.group(1), 16))['name']
                                  for m in re.finditer(r'// ([0-9A-F]{8}): fdivs? ', text)})
                notes.append('fdiv sites live in: ' + ', '.join(holders))
            status = 'UNCORROBORATED'
            notes.append('"by-255" and "FIFO emit" need dynamic confirmation; signposts + '
                         'external-write tracing must confirm, chunk text cannot')
        if base == 0x802697A0:
            notes.append('~70% has no stated denominator; treat as uncorroborated until signposts size it')
            status = 'UNCORROBORATED'
        if not named and base != 0x8029D7A0:
            notes.append('symbol map is fully anonymous here; role rests on dynamics, not names')
        findings.append(dict(chunk=f'{base:08X}', status=status, notes=notes, **detail))
    print(json.dumps(findings, indent=2))
    if args.output:
        args.output.write_text(json.dumps(findings, indent=2) + '\n')
    return 0 if all(f['status'] == 'OK' for f in findings) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--chunks', type=Path, required=True)
    p.add_argument('--symbols', type=Path, required=True)
    p.add_argument('--only', nargs='*', help='Chunk bases in hex (default: all)')
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('symbolize')
    p.add_argument('--tables', type=Path, required=True)
    p.add_argument('--pc-hist', type=Path, nargs='*', default=[])
    p.add_argument('--dispatch-csv', type=Path, nargs='*', default=[])
    p.add_argument('--pc', nargs='*', default=[])
    p.add_argument('--output', type=Path)
    p = sub.add_parser('signposts')
    p.add_argument('--tables', type=Path, required=True)
    p.add_argument('--per-chunk', type=int, default=3)
    p.add_argument('--json', type=Path, required=True)
    p.add_argument('--c', type=Path, required=True)
    p.add_argument('--h', type=Path, help='Also emit the full player header')
    p = sub.add_parser('annotate')
    p.add_argument('--chunk', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('check')
    p.add_argument('--chunks', type=Path, required=True)
    p.add_argument('--symbols', type=Path, required=True)
    p.add_argument('--output', type=Path)
    args = parser.parse_args()
    raise SystemExit({'build': build, 'symbolize': symbolize, 'signposts': signposts,
                      'annotate': annotate, 'check': check}[args.command](args))


if __name__ == '__main__':
    main()
