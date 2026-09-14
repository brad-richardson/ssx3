// Read-only countdown event and hidden-instance observations. Generated label
// hooks cover same-chunk jumps; no guest data, inputs or timing are changed.
#pragma once
#include <stdio.h>
#include <stdlib.h>

static unsigned ssx_gate_word(const CPUState* c, unsigned a) {
  if (a < 0x80000000u || (unsigned long long)a + 4 > 0x80000000ull + c->ram_size) return 0;
  const unsigned char* p = c->ram + (a - 0x80000000u);
  return ((unsigned)p[0]<<24)|((unsigned)p[1]<<16)|((unsigned)p[2]<<8)|p[3];
}
static void ssx_gate_trace(const CPUState* c, const char* stage, int binding) {
  static int initialized=0, enabled=0;
  static unsigned first=0, events=0;
  if (!initialized) {
    const char* value=getenv("SSX_STARTGATE_TRACE");
    enabled=value && value[0]=='1';
    value=getenv("SSX_STARTGATE_FIRST");
    if (value) first=(unsigned)strtoul(value,NULL,0);
    initialized=1;
  }
  if (!enabled || events>=1000) return;
  unsigned instance=binding ? c->gpr[9] : 0;
  unsigned oid=binding ? ssx_gate_word(c,instance+112) : 0;
  if (binding && (!first || oid<first || oid-first>=3)) return;
  ++events;
  unsigned property=binding ? ssx_gate_word(c,instance+136) : 0;
  fprintf(stderr,"[ssx-startgate] {\"stage\":\"%s\",\"ticks\":%llu,"
    "\"r3\":%u,\"r4\":%u,\"r5\":%u,\"r6\":%u,\"lr\":%u,"
    "\"value_type\":%u,\"instance_id\":%u,\"flags\":%u,\"property\":%u,\"property_flags\":%u}\n",
    stage,(unsigned long long)c->timebase,c->gpr[3],c->gpr[4],c->gpr[5],c->gpr[6],c->lr,
    binding ? 0 : ssx_gate_word(c,c->gpr[3]+8),oid,
    binding ? ssx_gate_word(c,instance+128) : 0,property,
    binding ? ssx_gate_word(c,property+4) : 0);
}
