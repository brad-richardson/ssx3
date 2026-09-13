#!/usr/bin/env python3
"""Build isolated GX draw-state diagnostic players, or compare their captures.

The production runner, vendor sources and libraries are never rewritten.
Build requires the existing native runtime build. Set SSX3_DRAW_TRACE to a
JSONL path when running; create PATH.enable to start collecting distinct
material/texture combinations (up to 4096). This is not a frame/visibility log.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'local/native/runtime-build'
VENDOR = ROOT / 'third_party/ModernGekko'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_copy(command, source, output):
    args = shlex.split(command)
    args[args.index('-c') + 1] = str(source)
    args[args.index('-o') + 1] = str(output)
    for flag in ('-MF', '-MT'):
        if flag in args:
            i = args.index(flag)
            del args[i:i + 2]
    return args


def build(args):
    game = args.game.resolve()
    dol, boot = game / 'sys/main.dol', game / 'sys/boot.bin'
    identity = dict(disc_id=boot.read_bytes()[:6].decode('ascii'), dol_sha256=sha(dol))
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'local'):
        raise ValueError('Diagnostic outputs must be under the workspace local/ directory')
    output.mkdir(parents=True, exist_ok=False)
    commands = subprocess.check_output([str(ROOT / 'local/tooling/ninja'), '-C', str(BUILD),
                                       '-t', 'commands', 'moderngekko-run'], text=True).splitlines()
    receipt = dict(game=str(game), cpu=args.cpu, **identity, commands=[],
                   production_runner_sha256=sha(BUILD / 'moderngekko-run'))

    def run(command):
        receipt['commands'].append(command)
        subprocess.run(command, cwd=BUILD, check=True)

    original = VENDOR / 'vendor/dolphin/Source/Core/VideoCommon/VertexManagerBase.cpp'
    source = original.read_text()
    marker = 'std::unique_ptr<VertexManagerBase> g_vertex_manager;'
    texture_marker = '  const auto used_textures = UsedTextures();'
    flush_marker = '  vertex_shader_manager.SetConstants(texture_names, xf_state_manager);'
    for marker_check in (marker, texture_marker, flush_marker):
        if source.count(marker_check) != 1:
            raise ValueError(f'Diagnostic injection point changed: {marker_check}')
    source = source.replace(marker, '#include "' + str(ROOT / 'native/diagnostics/draw_trace.h') + '"\n' + marker)
    source = source.replace(texture_marker, texture_marker + '\n  std::string draw_trace_textures;')
    load_marker = '\n        const float custom_tex_scale = cache_entry->GetWidth() / float(cache_entry->native_width);'
    if source.count(load_marker) != 1:
        raise ValueError('Texture-load injection point changed')
    source = source.replace(load_marker, '''        if (std::getenv("SSX3_DRAW_TRACE")) {
          if(!draw_trace_textures.empty()) draw_trace_textures+=",";
          draw_trace_textures+=fmt::format("{{\\\"unit\\\":{},\\\"hash\\\":\\\"{:016x}\\\",\\\"width\\\":{},\\\"height\\\":{}}}",i,cache_entry->hash,cache_entry->native_width,cache_entry->native_height);
        }
''' + load_marker)
    source = source.replace(flush_marker,
                            '  TraceDraw(draw_trace_textures,m_base_buffer_pointer,m_cur_buffer_pointer-m_base_buffer_pointer);\n' + flush_marker)
    local_source = output / 'VertexManagerBase.cpp'
    local_source.write_text(source)
    trace_object = output / 'VertexManagerBase.o'
    run(compile_copy(next(c for c in commands if c.endswith('/VertexManagerBase.cpp')), local_source, trace_object))

    cli = compile_copy(next(c for c in commands if c.endswith('/moderngekko_run.cpp')),
                       VENDOR / 'tools/moderngekko_run.cpp', output / 'runner.o')
    for i, arg in enumerate(cli):
        for macro, value in [('MODERNGEKKO_REQUIRED_DISC_ID', identity['disc_id']),
                             ('MODERNGEKKO_REQUIRED_DOL_SHA256', identity['dol_sha256'])]:
            if arg.startswith('-D' + macro + '='):
                cli[i] = f'-D{macro}="{value}"'
    run(cli)
    link = shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link = link[2:link.index('&&', 2)]
    link[link.index('-o') + 1] = str(output / 'player')
    link[link.index('CMakeFiles/moderngekko-run.dir/tools/moderngekko_run.cpp.o')] = str(output / 'runner.o')
    link.insert(link.index('libmoderngekko.a'), str(trace_object))
    if args.cpu == 'jit':
        runtime = VENDOR / 'src/runtime/dolphin_runtime.cpp'
        text = runtime.read_text()
        marker = 'PowerPC::CPUCore::StaticRecomp'
        if text.count(marker) != 1:
            raise ValueError('Runtime CPU selection changed')
        local_runtime = output / 'runtime.cpp'
        local_runtime.write_text(text.replace(marker, 'PowerPC::CPUCore::JITARM64'))
        command = compile_copy(next(c for c in commands if c.endswith('/dolphin_runtime.cpp')),
                               local_runtime, output / 'runtime.o')
        command.insert(1, '-I' + str(runtime.parent))
        run(command)
        link.insert(link.index('libmoderngekko.a'), str(output / 'runtime.o'))
    run(link)
    receipt.update(player_sha256=sha(output / 'player'),
                   trace_header_sha256=sha(ROOT / 'native/diagnostics/draw_trace.h'),
                   vertex_source_sha256=sha(original))
    if sha(BUILD / 'moderngekko-run') != receipt['production_runner_sha256']:
        raise RuntimeError('Production runner changed during diagnostic build')
    (output / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(output / 'player')


def terrain_pair(row):
    """Recognize the observed base/lightmap prefix, excluding menu/sprite draws."""
    bp = struct.unpack('<256I', bytes.fromhex(row['bp']))
    textures = {t['unit']: t for t in row['textures']}
    if ((bp[0] >> 10 & 15) < 1 or 0 not in textures or 1 not in textures or
            bp[0xc0] & 0xffffff != 0x08fff8 or
            bp[0xc2] & 0xcfffff != 0x08f80f or
            bp[0x28] & 0x7f != 0x40 or bp[0x28] >> 12 & 0x7f != 0x49):
        return None
    return tuple(textures[i]['hash'] for i in (0, 1))


def compare(args):
    records = {}
    for label, path in [('source', args.source), ('target', args.target)]:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        groups = {}
        for row in rows:
            pair = terrain_pair(row)
            if pair:
                groups.setdefault(pair, []).append(row)
        records[label] = groups
    common = sorted(records['source'].keys() & records['target'].keys())
    if not common:
        raise ValueError('No matching terrain base/lightmap image hashes; comparison is inconclusive')
    matches = []
    for pair in common:
        result = dict(texture_hash=pair[0], lightmap_hash=pair[1])
        for label in records:
            rows = records[label][pair]
            scales = sorted({(1, 2, 4, 0.5)[struct.unpack_from('<I', bytes.fromhex(r['bp']), 0xc2 * 4)[0] >> 20 & 3]
                             for r in rows})
            result[label] = dict(draw_ids=[r['id'] for r in rows], lightmap_scales=scales)
        matches.append(result)
    report = dict(schema=1, source_sha256=sha(args.source), target_sha256=sha(args.target),
                  matched_image_pairs=len(matches), matches=matches,
                  scope='First observed distinct material states; not matching cameras or a visibility test')
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'{len(matches)} matching terrain image pairs; {args.output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--cpu', choices=('aot', 'jit'), required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('compare')
    p.add_argument('source', type=Path)
    p.add_argument('target', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    {'build': build, 'compare': compare}[args.command](args)


if __name__ == '__main__':
    main()
