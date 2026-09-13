"""Source-label observation stays read-only and fails closed on changed seams."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from gamecube_collision_trace import HEADER, instrument


class CollisionTraceTest(unittest.TestCase):
    def test_missing_or_duplicate_label_is_rejected(self):
        hooks={'801DDBC8':('narrow','ctx->gpr[4]','ctx->gpr[3]','-1')}
        prefix='#include "../generated.h"\n'
        for source in (prefix, prefix+'label_801DDBC8:\n'*2):
            with self.assertRaisesRegex(ValueError,'label changed'):
                instrument(source,hooks,HEADER)

    def test_observation_preserves_cpu_and_memory(self):
        source=r'''
#include <stdint.h>
#include <assert.h>
typedef struct { unsigned char* ram; uint32_t ram_size; uint64_t timebase; uint32_t gpr[32]; } CPUState;
#include "HEADER"
static void word(unsigned char* ram, unsigned offset, unsigned value) {
  for (unsigned i=0;i<4;++i) ram[offset+i]=(unsigned char)(value>>(24-8*i));
}
int main(void) {
  unsigned char ram[2048]={0}, before[2048];
  CPUState state={.ram=ram,.ram_size=sizeof(ram),.timebase=12345}, saved=state;
  word(ram,256+112,0x08000258); word(ram,256+128,0x00210021);
  word(ram,256+136,0x80000400); word(ram,1024,1);
  word(ram,1028,0x00210000); word(ram,1032,0xffffffff); word(ram,1036,0x80000600);
  word(ram,1536,0x00010001);
  memcpy(before,ram,sizeof(ram));
  ssx_collision_trace(&state,"narrow_enter",0x80000100,0,-1);
  ssx_collision_trace(&state,"ignored",0xfffffffc,0,-1);
  assert(memcmp(ram,before,sizeof(ram))==0);
  assert(memcmp(&state,&saved,sizeof(state))==0);
}
'''.replace('HEADER',str(HEADER))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder); (path/'probe.c').write_text(source)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(path/'probe.c'),'-o',str(path/'probe')],
                           check=True,capture_output=True)
            result=subprocess.run([str(path/'probe')],check=True,capture_output=True,text=True,
                                  env={**os.environ,'SSX_COLLISION_INSTANCE':'0x08000258'})
        lines=result.stderr.splitlines()
        self.assertEqual(len(lines),1)
        row=json.loads(lines[0].removeprefix('[ssx-collision] '))
        self.assertEqual(row['flags'],0x00210021)
        self.assertEqual(row['kind'],1)
        self.assertEqual(row['collision_header'],0x00010001)
        self.assertEqual(row['contacts'],-1)
