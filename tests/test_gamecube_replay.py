"""Keep ordered replay capture prerequisites separate from safe GPU replay."""
import copy
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from gamecube_replay_check import assess, capture_info, png_info


def fixture(directory):
    fifo = b'\x00\x00\x00\x00'
    data = bytearray(128 + 64)
    struct.pack_into('<III', data, 0, 0x0D01F1F0, 6, 1)
    for field, count in ((12, 256), (24, 256), (36, 4096), (48, 88)):
        struct.pack_into('<QI', data, field, len(data), count)
        data.extend(b'\0' * count * 4)
    struct.pack_into('<QI', data, 60, 128, 1)
    struct.pack_into('<QI', data, 76, len(data), 1024 * 1024)
    data.extend(b'\0' * 1024 * 1024)
    fifo_offset = len(data)
    data.extend(fifo)
    updates_offset = len(data)
    data.extend(struct.pack('<IIQIB3x', 0, 0, updates_offset + 24, 4, 2))
    data.extend(b'\x01\x02\x03\x04')
    struct.pack_into('<QIIIQI', data, 128, fifo_offset, len(fifo), 32, 64, updates_offset, 1)
    capture = directory/'events.jsonl.fifo'
    capture.write_bytes(data)
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind+payload))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(b'\0\xff\0\0')) + chunk(b'IEND', b'')
    reference = directory/'reference.png'
    reference.write_bytes(png)
    actions = ['record_start', 'reference_requested', 'recorded', 'capture_saved',
               'audit', 'audit', 'audit', 'audit_complete', 'blocked']
    rows = [dict(event='replay', schema=2, action=a, wall=i, render_execution=False)
            for i, a in enumerate(actions)]
    for row in rows[1:3]:
        row.update(frame_boundaries=2, reference_frame=123, reference_present=456)
    rows[2].update(bytes=len(fifo), memory_updates=1, fifo_start=32, fifo_end=64)
    for i, row in enumerate(rows[4:7]):
        row.update(ok=True, **{'pass': i}, private_memory=True, initial_state_reset=True,
                   commands=10, primitives=1, indexed_loads=2, indexed_bytes_hash='001122',
                   draw_done=1, tokens=1, efb_copies=2, xfb_copies=1, tmem_loads=0, bbox_writes=0)
    rows[-1]['reason'] = 'renderer_isolation_and_pixel_fidelity_unimplemented'
    return rows, capture, reference


class ReplayTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
    def test_compiled_ordered_resources_private_reset_and_rejection(self):
        code = r'''
#include "native/diagnostics/replay_plan.h"
#include <cassert>
#include <limits>
using namespace ReplayResearch;
int main() {
  ShadowMemory memory(16,15,8,7);
  std::vector<uint8_t> live(16, 99);
  assert(AllocatedBankSize(nullptr,64*1024*1024)==0); // configured GC MEM2 is unallocated
  assert(AllocatedBankSize(live.data(),live.size())==16);
  std::vector<MemoryUpdate> updates{{0,0,{1,2,3}}, {4,1,{4}}, {4,1,{5}}, {8,0,{7}}};
  for(unsigned pass=0;pass<3;++pass) {
    memory.Reset();
    assert(*memory.Resolve(0,1)==0);
    std::vector<unsigned> observed;
    std::string error;
    auto decode=[&](size_t start,size_t end) {
      assert(end-start==4);
      observed.push_back(*memory.Resolve(1,1));
      return true;
    };
    assert(DecodeOrdered(8,updates,memory,decode,error));
    assert((observed==std::vector<unsigned>{2,5})); // future writes cannot leak backwards
    assert(*memory.Resolve(0,1)==7);               // end-position write applies after FIFO
    assert(live==std::vector<uint8_t>(16,99));     // no borrowed/live memory
  }
  std::string error;
  unsigned calls=0;
  auto decode=[&](size_t,size_t){++calls;return true;};
  assert(!DecodeOrdered(8,{{4,0,{1}},{2,0,{2}}},memory,decode,error));
  assert(calls==0 && error=="invalid_update_position");
  assert(!DecodeOrdered(8,{{9,0,{1}}},memory,decode,error));
  assert(calls==0);
  assert(!DecodeOrdered(8,{{0,15,{1,2}}},memory,decode,error));
  assert(calls==0 && error=="invalid_update_range");
  assert(!memory.Resolve(0,std::numeric_limits<size_t>::max()));
  assert(memory.Apply({0,0x10000000,{42}}));
  assert(*memory.Resolve(0x10000000,1)==42 && *memory.Resolve(0,1)==7);
  assert(!memory.Resolve(0x10000007,2));
  ShadowMemory no_exram(16,15,0,0);
  assert(!no_exram.Resolve(0x10000000,1));
  auto complete_commands=[](size_t start,size_t end){return (end-start)%4==0;};
  assert(!DecodeOrdered(8,{{2,0,{1}}},memory,complete_commands,error));
  assert(error=="invalid_fifo_segment");          // resource boundary splits a command
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'order.cpp'
            source.write_text(code)
            binary = Path(directory)/'order'
            subprocess.run(['c++', '-std=c++17', '-I', str(ROOT), str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)

    def test_private_capture_pass_never_accepts_renderer_or_equal_pngs(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            rows, capture, reference = fixture(directory)
            candidate = directory/'candidate.png'
            candidate.write_bytes(reference.read_bytes())
            result = assess(rows, capture, reference, [candidate])
            self.assertTrue(result['capture_gate_passed'])
            self.assertTrue(result['candidate_comparisons'][0]['pixels_equal'])
            self.assertFalse(result['candidate_comparisons'][0]['same_frame_provenance_verified'])
            self.assertFalse(result['replay_accepted'])
            self.assertFalse(result['guest_render_isolation_verified'])
            self.assertFalse(result['original_frame_fidelity_verified'])
            events = directory/'events.jsonl'
            events.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            command = [sys.executable, str(ROOT/'tools/gamecube_replay_check.py'),
                       '--events', str(events), '--reference', str(reference)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
            self.assertEqual(subprocess.run(command+['--capture-only'], capture_output=True).returncode, 0)

    def test_missing_early_or_mismatched_reference_and_partial_audits_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, capture, reference = fixture(Path(directory))
            changes = [lambda r: r.pop(1), lambda r: r[1].update(frame_boundaries=1),
                       lambda r: r[1].update(reference_frame=122),
                       lambda r: r[5].update(indexed_bytes_hash='different'),
                       lambda r: r[5].update(initial_state_reset=False),
                       lambda r: r[5].update(render_execution=True),
                       lambda r: r[5].update(wall=float('nan')),
                       lambda r: r[2].update(bytes=100)]
            for change in changes:
                with self.subTest(change=change):
                    modified = copy.deepcopy(rows)
                    change(modified)
                    with self.assertRaises(ValueError):
                        assess(modified, capture, reference)
            with self.assertRaises(ValueError):
                assess(rows, capture, reference, [reference])

    def test_fifo_artifact_bounds_and_update_order_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, capture, reference = fixture(Path(directory))
            good = capture.read_bytes()
            capture.write_bytes(good[:-1])
            with self.assertRaises(ValueError):
                capture_info(capture)
            changed = bytearray(good)
            updates_offset = struct.unpack_from('<Q', changed, 128+20)[0]
            struct.pack_into('<I', changed, updates_offset, 5)
            capture.write_bytes(changed)
            with self.assertRaises(ValueError):
                capture_info(capture)

    def test_png_decode_compares_pixels_and_rejects_incomplete_captures(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            rows, capture, reference = fixture(directory)
            def chunk(kind, data):
                return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))
            # Different metadata/compression, identical red pixel.
            candidate = directory/'candidate.png'
            png = reference.read_bytes()
            candidate.write_bytes(png[:33] + chunk(b'tEXt', b'comment\0different encoding') + png[33:])
            result = assess(rows, capture, reference, [candidate])['candidate_comparisons'][0]
            self.assertFalse(result['png_bytes_identical'])
            self.assertTrue(result['pixels_equal'])
            self.assertEqual(png_info(candidate)['pixels_sha256'], png_info(reference)['pixels_sha256'])
            for broken in (png[:33], png[:-1], png[:40]+bytes([png[40]^1])+png[41:]):
                candidate.write_bytes(broken)
                with self.assertRaises(ValueError):
                    png_info(candidate)

    def test_png_filters_and_rgb_rgba_normalize_to_the_same_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory)/'filter.png'
            def chunk(kind, data):
                return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))
            # Two known RGB rows; these are the PNG-specified filter residuals.
            rows = {
                0: ([1,2,3,4,5,6], [7,8,9,10,11,12]),
                1: ([1,2,3,3,3,3], [7,8,9,3,3,3]),
                2: ([1,2,3,4,5,6], [6,6,6,6,6,6]),
                3: ([1,2,3,4,4,5], [7,7,8,5,5,5]),
                4: ([1,2,3,3,3,3], [6,6,6,3,3,3]),
            }
            def write(raw, color):
                image.write_bytes(b'\x89PNG\r\n\x1a\n' +
                    chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 2, 8, color, 0, 0, 0)) +
                    chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
                return png_info(image)['pixels_sha256']
            hashes = {write(bytes([f]+a+[f]+b), 2) for f, (a, b) in rows.items()}
            hashes.add(write(bytes([0,1,2,3,255,4,5,6,255,0,7,8,9,255,10,11,12,255]), 6))
            self.assertEqual(len(hashes), 1)


if __name__ == '__main__':
    unittest.main()
