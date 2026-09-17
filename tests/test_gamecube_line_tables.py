"""Line tables map guest PCs to chunk lines/functions; signpost selection stays deterministic."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gamecube_line_tables as lt

ROOT = Path(__file__).resolve().parents[1]

CHUNK = '''// DolRecomp output
#include "../generated.h"

static void loop_80005800(CPUState* ctx) {
label_80005800:
    ctx->pc = 0x80005800u;
    // 80005800: lwz     r5, 0(r3)
    {
        u32 ea = ctx->gpr[3] + (u32)(s32)(0);
        ctx->gpr[5] = mem_read32(ctx, ea);
    }
}

void func_800057A0(CPUState* ctx) {
    switch (ctx->pc) {
    case 0x800057A0u: goto label_800057A0;
    case 0x80005800u: goto label_80005800;
    default: return;
    }
label_800057A0:
    ctx->pc = 0x800057A0u;
    // 800057A0: mflr    r0
label_800057A4:
    // 800057A4: blr
}
'''

SYMBOLS = '''fn_800057A0 = .text:0x800057A0; // type:function size:0x10
fn_80005800 = .text:0x80005800; // type:function size:0x20
someobj = .text:0x80005820; // type:object size:0x4 data:4byte
'''


def write_chunk(directory, name='chunk_0001_text1_800057A0.c', text=CHUNK):
    path = Path(directory) / name
    path.write_text(text)
    return path


class LineTableTests(unittest.TestCase):
    def test_parse_chunk_extracts_lines_switch_and_loops(self):
        with tempfile.TemporaryDirectory() as directory:
            parsed = lt.parse_chunk(write_chunk(directory))
        self.assertEqual(parsed['base'], 0x800057A0)
        self.assertEqual(sorted(parsed['pcs']),
                         [0x800057A0, 0x800057A4, 0x80005800])
        self.assertEqual(parsed['pcs'][0x800057A0]['disasm'], 'mflr    r0')
        self.assertIn(0x800057A0, parsed['switch'])
        self.assertNotIn(0x800057A4, parsed['switch'])
        self.assertEqual(list(parsed['loops']), [0x80005800])
        self.assertIn(0x800057A0, parsed['labels'])

    def test_parse_chunk_rejects_base_mismatch_and_missing_name(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = write_chunk(directory, 'chunk_0001_text1_800097A0.c')
            with self.assertRaisesRegex(ValueError, 'does not match filename base'):
                lt.parse_chunk(bad)
            plain = Path(directory) / 'chunk.c'
            plain.write_text(CHUNK)
            with self.assertRaisesRegex(ValueError, 'does not carry a base address'):
                lt.parse_chunk(plain)

    def test_function_at_resolves_containment_and_gaps(self):
        functions = lt.parse_symbols(SYMBOLS)
        self.assertEqual(len(functions), 2)
        self.assertEqual(lt.function_at(functions, 0x800057A4)['name'], 'fn_800057A0')
        self.assertIsNone(lt.function_at(functions, 0x80005790))
        self.assertIsNone(lt.function_at(functions, 0x80005900))

    def test_build_tables_joins_pcs_with_functions(self):
        with tempfile.TemporaryDirectory() as directory:
            tables = lt.build_tables([write_chunk(directory)], lt.parse_symbols(SYMBOLS))
        chunk = tables['chunks']['800057A0']
        by_pc = {r['pc']: r for r in chunk['records']}
        self.assertEqual(by_pc['800057A0']['func'], 'fn_800057A0')
        self.assertTrue(by_pc['800057A0']['in_switch'])
        self.assertFalse(by_pc['800057A4']['in_switch'])
        self.assertEqual(by_pc['80005800']['func'], 'fn_80005800')
        self.assertEqual(chunk['loops'][0]['addr'], '80005800')

    def test_symbolize_attributes_samples_to_functions_and_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            tables = lt.build_tables([write_chunk(directory)], lt.parse_symbols(SYMBOLS))
        _, index = None, {}
        for base, chunk in tables['chunks'].items():
            for record in chunk['records']:
                index[int(record['pc'], 16)] = (int(base, 16), record)
        hits = lt.symbolize_pcs(index, [(0x800057A0, 10, 't'), (0x80005800, 5, 't'),
                                        (0x80100000, 3, 't')])
        self.assertEqual(hits['attributed'], 15)
        self.assertEqual(hits['unattributed'], 3)
        funcs = hits['by_chunk']['800057A0']['by_func']
        self.assertEqual(funcs['fn_800057A0']['samples'], 10)
        self.assertEqual(funcs['fn_80005800']['samples'], 5)
        line = next(iter(funcs['fn_800057A0']['lines'].values()))
        self.assertEqual(line['pc'], '800057A0')

    def test_select_signposts_picks_named_top3_and_loops(self):
        tables = dict(chunks={'800057A0': dict(
            records=[dict(pc='800057A0', in_switch=True), dict(pc='800057C0', in_switch=True),
                     dict(pc='80005800', in_switch=True)],
            functions=[dict(name=f'fn_{a:08X}', start=f'{a:08X}', size=s) for a, s in
                       ((0x800057A0, 100), (0x800057C0, 400), (0x80005800, 300), (0x80005900, 50))],
            loops=[dict(addr='80005800', name='loop_80005800', line=4)])})
        hot = {0x800057A0: dict(role='fixture', note='')}
        named = {0x800057C0: 'fixture entry'}
        with mock.patch.object(lt, 'HOT_CHUNKS', hot), mock.patch.object(lt, 'NAMED_PCS', named):
            posts = lt.select_signposts(tables, per_chunk=3)
        by_pc = {p['pc']: p for p in posts}
        # Top-3 by size plus the loop plus the named pc (deduped by address).
        self.assertEqual(sorted(by_pc), ['800057A0', '800057C0', '80005800'])
        self.assertEqual(by_pc['800057C0']['kind'], 'named')
        self.assertEqual(by_pc['80005800']['kind'], 'loop')
        self.assertTrue(all(p['in_switch'] for p in posts))
        self.assertEqual([p['pc'] for p in posts], sorted(by_pc))

    def test_annotate_marks_labels_with_decodable_guest_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk = write_chunk(directory)
            out = Path(directory) / 'annotated.c'
            lt.annotate(mock.Mock(chunk=chunk, output=out))
            text = out.read_text()
        markers = re.findall(r'#line (\d+) "gxbe69_([0-9A-F]+)\.s"', text)
        self.assertNotIn('#line -', text)
        self.assertEqual(len(markers), 4)  # every label + loop is marked
        for line, base in markers:
            pc = 0x80000000 + int(line) - 1
            self.assertIn(f'{pc:08X}', text)
            self.assertEqual(base, '800057A0')
        self.assertIn('label_800057A0:', text)

    def test_render_signpost_header_holds_sorted_table_and_step(self):
        posts = [dict(pc='80005800', chunk='800057A0', name='loop_80005800',
                      kind='loop', role='fixture', size=None, in_switch=True),
                 dict(pc='800057A0', chunk='800057A0', name='fn_800057A0',
                      kind='func', role='fixture', size=16, in_switch=True)]
        header = lt.render_signpost_header(sorted(posts, key=lambda p: p['pc']), 'tables.json')
        pcs = re.findall(r'\{0x([0-9A-F]+)u,', header)
        self.assertEqual(pcs, ['800057A0', '80005800'])
        self.assertIn('namespace ChunkSignposts', header)
        self.assertIn('void Step(CPUState& c)', header)
        self.assertIn('SSX_NATIVE_SIGNPOSTS', header)
        self.assertIn('static_assert', header)

    def test_check_flags_missing_chunks_and_confirms_flush_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            symbols = Path(directory) / 'symbols.txt'
            symbols.write_text('fn_8029F4D4 = .text:0x8029F4D4; // type:function size:0x10\n')
            chunks = Path(directory) / 'chunks'
            chunks.mkdir()
            out = Path(directory) / 'check.json'
            code = lt.check(mock.Mock(chunks=chunks, symbols=symbols, output=out))
            self.assertEqual(code, 1)
            findings = {f['chunk']: f for f in json.loads(out.read_text())}
            self.assertEqual(findings['8029D7A0']['status'], 'MISSING')
            # Now provide the flush-dispatcher chunk with its prologue.
            (chunks / 'chunk_0167_text1_8029D7A0.c').write_text(
                CHUNK.replace('800057A0', '8029D7A0').replace('80005800', '8029F4D4')
                .replace('mflr    r0', 'mflr    r0') +
                '\nlabel_8029F4D4:\n    // 8029F4D4: mflr    r0\n')
            code = lt.check(mock.Mock(chunks=chunks, symbols=symbols, output=out))
            findings = {f['chunk']: f for f in json.loads(out.read_text())}
            self.assertEqual(findings['8029D7A0']['status'], 'OK')
            self.assertEqual(code, 1)  # other chunks still missing

    def test_check_leaves_fdiv_claim_uncorroborated_without_dynamics(self):
        with tempfile.TemporaryDirectory() as directory:
            symbols = Path(directory) / 'symbols.txt'
            symbols.write_text('fn_8022E090 = .text:0x8022E090; // type:function size:0x17C\n')
            chunks = Path(directory) / 'chunks'
            chunks.mkdir()
            (chunks / 'chunk_0139_text1_8022D7A0.c').write_text(
                CHUNK.replace('800057A0', '8022D7A0').replace('80005800', '8022E110') +
                '\nlabel_8022E110:\n    // 8022E110: fdivs   f29, f31, f30\n')
            out = Path(directory) / 'check.json'
            lt.check(mock.Mock(chunks=chunks, symbols=symbols, output=out))
            findings = {f['chunk']: f for f in json.loads(out.read_text())}
            finding = findings['8022D7A0']
            self.assertEqual(finding['status'], 'UNCORROBORATED')
            self.assertTrue(any('fn_8022E090' in note for note in finding['notes']))

    def test_checked_in_header_matches_selection_contract(self):
        header = (ROOT / 'native/diagnostics/chunk_signposts.h').read_text()
        rows = re.findall(r'\{0x([0-9A-F]{8})u,"([^"]+)","([0-9A-F]{8})","([^"]+)","([^"]+)"\},', header)
        self.assertGreaterEqual(len(rows), 40)
        pcs = [int(r[0], 16) for r in rows]
        self.assertEqual(pcs, sorted(pcs))
        self.assertEqual(len(set(pcs)), len(pcs))
        for pc, name, chunk, role, kind in rows:
            base = int(chunk, 16)
            self.assertIn(base, lt.HOT_CHUNKS)
            self.assertTrue(base <= int(pc, 16) < base + lt.CHUNK_SIZE)
            self.assertIn(kind, ('func', 'loop', 'named'))
        self.assertIn(0x8010A4C8, pcs)  # render entry
        self.assertIn(0x8029F4D4, pcs)  # flush dispatcher


if __name__ == '__main__':
    unittest.main()
