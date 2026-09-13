// Read-only GXBE69 collision observation in isolated generated-source copies.
// Label hooks also cover same-chunk jumps that bypass the native dispatcher.
#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned ssx_collision_word(const CPUState* c, unsigned a) {
  if (a < 0x80000000u || (unsigned long long)a + 4 > 0x80000000ull + c->ram_size) return 0;
  const unsigned char* p=c->ram+(a-0x80000000u);
  return ((unsigned)p[0]<<24)|((unsigned)p[1]<<16)|((unsigned)p[2]<<8)|p[3];
}
static double ssx_collision_float(const CPUState* c, unsigned a) {
  unsigned bits=ssx_collision_word(c,a); float value; memcpy(&value,&bits,4); return value;
}
static void ssx_collision_trace(const CPUState* c, const char* stage, unsigned instance,
                                unsigned query, int contacts) {
  static int initialized=0;
  static unsigned selected=0, events=0;
  if (!initialized) {
    const char* value=getenv("SSX_COLLISION_INSTANCE");
    if (value) selected=(unsigned)strtoul(value, NULL, 0);
    initialized=1;
  }
  if (!selected || ssx_collision_word(c,instance+112)!=selected || events>10000) return;
  if (events++==10000) {
    fprintf(stderr,"[ssx-collision] {\"stage\":\"overflow\"}\n"); return;
  }
  const unsigned property=ssx_collision_word(c,instance+136);
  const unsigned collision=ssx_collision_word(c,property+12);
  const unsigned model=ssx_collision_word(c,instance+120);
  fprintf(stderr,"[ssx-collision] {\"stage\":\"%s\",\"ticks\":%llu,\"instance_id\":%u,"
    "\"instance\":%u,\"next\":%u,\"flags\":%u,\"property\":%u,\"kind\":%u,\"property_flags\":%u,"
    "\"effect\":%u,\"collision\":%u,\"collision_header\":%u,\"model\":%u,\"model_parts\":%u,"
    "\"contacts\":%d,\"bounds\":[%.9g,%.9g,%.9g,%.9g,%.9g,%.9g],"
    "\"query\":%u,\"query_bounds\":[%.9g,%.9g,%.9g,%.9g,%.9g,%.9g]}\n",
    stage,(unsigned long long)c->timebase,selected,instance,ssx_collision_word(c,instance),
    ssx_collision_word(c,instance+128),property,ssx_collision_word(c,property),
    ssx_collision_word(c,property+4),ssx_collision_word(c,property+8),collision,
    ssx_collision_word(c,collision),model,ssx_collision_word(c,model+4),contacts,
    ssx_collision_float(c,instance+88),ssx_collision_float(c,instance+92),ssx_collision_float(c,instance+96),
    ssx_collision_float(c,instance+100),ssx_collision_float(c,instance+104),ssx_collision_float(c,instance+108),
    query,ssx_collision_float(c,query+32),ssx_collision_float(c,query+36),ssx_collision_float(c,query+40),
    ssx_collision_float(c,query+48),ssx_collision_float(c,query+52),ssx_collision_float(c,query+56));
}
