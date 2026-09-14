"""Exercise actual NativeProbe capture/emission against bounded synthetic RAM."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VTABLE = 0x802E543C

HARNESS = r'''
#include <cstdint>
#include <vector>
using u32=uint32_t; using u64=uint64_t;
struct CPUState {u32 gpr[32]{},pc=0,lr=0;u64 timebase=0;unsigned char* ram=nullptr;u32 ram_size=0;};
#include "native/diagnostics/native_callback_trace.h"
using namespace NativeProbe;
int main(){
 std::vector<unsigned char> ram(8192);CPUState c;
 c.ram=ram.data();c.ram_size=ram.size();c.gpr[3]=1;
 constexpr u32 app=0x80001000;
 auto put=[&](size_t offset,u32 word){for(unsigned i=0;i<4;++i)ram[4096+offset+i]=word>>(24-i*8);};
 auto reset=[&](u32 table){std::fill(ram.begin(),ram.end(),0);c.ram_size=ram.size();put(0,table);};
 auto begin=[&](){Active a;a.app=app;a.before=Capture(c,app);a.wall=Now();return a;};
 auto emit=[&](Active& a,const Snapshot& b){Emit(c,"render",a,b);};
 output_file=stdout;render.pending=true;

 reset(GameModuleVtable);auto mixed=begin();
 put(536,0x11223344);put(540,0x55667788);put(632,0xfedcba98);put(640,0x80000000);
 put(644,7);put(924,8);put(928,9);put(1020,10);
 emit(mixed,Capture(c,app));

 reset(0x802e9999);auto unknown=begin();put(632,22);emit(unknown,Capture(c,app));

 reset(GameModuleVtable);auto changed=begin();put(0,0x802e9999);emit(changed,Capture(c,app));

 reset(GameModuleVtable);auto unchanged=begin();emit(unchanged,Capture(c,app));

 reset(GameModuleVtable);auto unreadable=begin();c.ram_size=4096+512;emit(unreadable,Capture(c,app));

 reset(GameModuleVtable);auto replaced=begin();auto other=Capture(c,app);other.app+=4;emit(replaced,other);
}
'''


@unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
class NativeAppOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            stub = output/'Core/Core.h'
            stub.parent.mkdir()
            stub.write_text('#pragma once\n#include <string>\n'
                            'namespace Core { inline void SaveScreenShot(const std::string&) {} }\n')
            source = output/'ownership.cpp'
            binary = output/'ownership'
            source.write_text(HARNESS)
            subprocess.run(['c++', '-std=c++17', '-I', str(output), '-I', str(ROOT),
                            str(source), '-o', str(binary)], check=True, capture_output=True, text=True)
            text = subprocess.check_output([str(binary)], text=True)
            cls.rows = [json.loads(line) for line in text.splitlines()]

    def test_raw_watch_and_big_endian_values_survive_owned_boundary(self):
        row = self.rows[0]
        offsets = [536, 540, 632, 640, 644, 924, 928, 1020]
        self.assertEqual(row['app_offsets'], offsets)
        self.assertEqual(row['app_owned_extent_bytes'], 540)
        self.assertEqual(row['app_owned_offsets'], [536])
        self.assertEqual(row['app_adjacent_offsets'], offsets[1:])
        self.assertEqual(row['app_vtable_before'], VTABLE)
        self.assertEqual(row['app_vtable_after'], VTABLE)
        self.assertTrue(row['app_snapshot_valid_before'])
        self.assertTrue(row['app_snapshot_valid_after'])
        changes = {item['offset']: item for item in row['app_word_changes']}
        self.assertEqual(sorted(changes), offsets)
        self.assertEqual(changes[632], dict(offset=632, before=0, after=0xFEDCBA98))
        self.assertEqual(changes[640]['after'], 0x80000000)
        self.assertEqual(changes[1020]['after'], 10)

    def test_unknown_vtable_retains_raw_evidence_without_classification(self):
        row = self.rows[1]
        for field in ('app_owned_extent_bytes', 'app_owned_offsets', 'app_adjacent_offsets'):
            self.assertIsNone(row[field])
        self.assertEqual(row['app_offsets'], [632])
        self.assertEqual(row['app_word_changes'], [dict(offset=632, before=0, after=22)])

    def test_vtable_change_cannot_keep_previous_known_extent(self):
        row = self.rows[2]
        self.assertEqual(row['app_vtable_before'], VTABLE)
        self.assertEqual(row['app_vtable_after'], 0x802E9999)
        self.assertIsNone(row['app_owned_extent_bytes'])
        self.assertIsNone(row['app_owned_offsets'])
        self.assertIsNone(row['app_adjacent_offsets'])
        self.assertEqual(row['app_word_changes'], [dict(offset=0, before=VTABLE, after=0x802E9999)])

    def test_known_unchanged_snapshot_has_empty_lists(self):
        row = self.rows[3]
        self.assertEqual(row['app_owned_extent_bytes'], 540)
        for field in ('app_offsets', 'app_owned_offsets', 'app_adjacent_offsets', 'app_word_changes'):
            self.assertEqual(row[field], [])

    def test_unreadable_snapshot_does_not_fabricate_word_values(self):
        row = self.rows[4]
        self.assertTrue(row['app_snapshot_valid_before'])
        self.assertFalse(row['app_snapshot_valid_after'])
        self.assertEqual(row['app_vtable_before'], VTABLE)
        self.assertIsNone(row['app_vtable_after'])
        self.assertIsNone(row['app_owned_extent_bytes'])
        self.assertIsNone(row['app_word_changes'])
        # The historical raw field remains intact, including its zero-filled fallback.
        self.assertEqual(row['app_offsets'], [0])

    def test_different_app_identity_cannot_share_classification(self):
        row = self.rows[5]
        self.assertEqual(row['app_vtable_before'], VTABLE)
        self.assertEqual(row['app_vtable_after'], VTABLE)
        self.assertIsNone(row['app_owned_extent_bytes'])


if __name__ == '__main__':
    unittest.main()
