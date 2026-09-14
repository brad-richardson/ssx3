// Bounded countdown visibility handler. The only guest state it changes is one
// flag bit in the course script's own staged countdown definition, which is
// used by the three staged instances and nothing else. No timing, geometry,
// material or input is touched, and the write is exactly reversible.
//
// Both countdown events re-dispatch on a restart, and re-entering the course
// after a finish raises StartgateOpen with no lights before it, so show and
// hide are idempotent and independent rather than a paired state machine.
#pragma once
#include <stdio.h>
#include <stdlib.h>

#define SSX_GATE_VISIBLE 0x00010000u
#define SSX_GATE_UNBOUND 0xffffffffu

// This header is included by every hooked translation unit, and the binding
// hook lives in a different one from the two event hooks. `static` would give
// each its own copy, so the events would never see the bound address; weak
// definitions collapse to one shared object at link time.
__attribute__((weak)) unsigned ssx_gate_definition = 0;  // guest address; zero until bound
__attribute__((weak)) unsigned ssx_gate_instances[3] = {0, 0, 0};
__attribute__((weak)) unsigned ssx_gate_bound = 0;
__attribute__((weak)) unsigned ssx_gate_writes = 0;

static int ssx_gate_on(void) {
  static int initialized = 0, enabled = 0;
  if (!initialized) {
    const char* value = getenv("SSX_STARTGATE_HANDLER");
    enabled = value && value[0] == '1';
    initialized = 1;
  }
  return enabled;
}

static unsigned ssx_gate_staged_first(void) {
  static int initialized = 0;
  static unsigned first = 0;
  if (!initialized) {
    const char* value = getenv("SSX_STARTGATE_FIRST");
    if (value) first = (unsigned)strtoul(value, NULL, 0);
    initialized = 1;
  }
  return first;
}

static int ssx_gate_in_ram(const CPUState* c, unsigned a) {
  return a >= 0x80000000u && (unsigned long long)a + 4 <= 0x80000000ull + c->ram_size;
}

static unsigned ssx_gate_load(const CPUState* c, unsigned a) {
  const unsigned char* p = c->ram + (a - 0x80000000u);
  return ((unsigned)p[0] << 24) | ((unsigned)p[1] << 16) | ((unsigned)p[2] << 8) | p[3];
}

static void ssx_gate_store(CPUState* c, unsigned a, unsigned value) {
  unsigned char* p = c->ram + (a - 0x80000000u);
  p[0] = (unsigned char)(value >> 24);
  p[1] = (unsigned char)(value >> 16);
  p[2] = (unsigned char)(value >> 8);
  p[3] = (unsigned char)value;
}

// Learn the staged definition's address from a staged instance's own binding.
// Requiring every staged instance to name the same record, and that record to
// carry no callback or collision model, keeps a layout change from letting
// this write somewhere else.
static void ssx_gate_bind(const CPUState* c) {
  if (!ssx_gate_on()) return;
  const unsigned first = ssx_gate_staged_first();
  const unsigned instance = c->gpr[9];
  if (!first || !ssx_gate_in_ram(c, instance + 136)) return;
  const unsigned oid = ssx_gate_load(c, instance + 112);
  if (oid < first || oid - first >= 3) return;
  const unsigned definition = ssx_gate_load(c, instance + 136);
  if (!ssx_gate_in_ram(c, definition + 12) ||
      ssx_gate_load(c, definition + 8) != SSX_GATE_UNBOUND ||
      ssx_gate_load(c, definition + 12) != SSX_GATE_UNBOUND) {
    fprintf(stderr, "[ssx-startgate-handler] {\"event\":\"reject\",\"instance\":%u,"
                    "\"definition\":%u}\n", oid, definition);
    return;
  }
  if (ssx_gate_definition && ssx_gate_definition != definition) {
    fprintf(stderr, "[ssx-startgate-handler] {\"event\":\"conflict\",\"instance\":%u,"
                    "\"definition\":%u,\"bound\":%u}\n", oid, definition, ssx_gate_definition);
    ssx_gate_definition = 0;
    return;
  }
  ssx_gate_definition = definition;
  // The engine copies the definition's visibility into each instance's own
  // runtime flags when it binds, so a later write to the definition alone does
  // not reach an instance that is already live. Keep the addresses and drive
  // both: the instances for the objects that exist, the definition for any
  // that bind afterwards.
  if (ssx_gate_bound < 3) ssx_gate_instances[ssx_gate_bound++] = instance;
  fprintf(stderr, "[ssx-startgate-handler] {\"event\":\"bind\",\"instance\":%u,"
                  "\"address\":%u,\"definition\":%u,\"flags\":%u,\"instance_flags\":%u}\n",
          oid, instance, definition, ssx_gate_load(c, definition + 4),
          ssx_gate_load(c, instance + 128));
}

static void ssx_gate_set(CPUState* c, int show, const char* stage) {
  if (!ssx_gate_on()) return;
  if (!ssx_gate_definition || !ssx_gate_in_ram(c, ssx_gate_definition + 4)) {
    fprintf(stderr, "[ssx-startgate-handler] {\"event\":\"unbound\",\"stage\":\"%s\"}\n", stage);
    return;
  }
  const unsigned before = ssx_gate_load(c, ssx_gate_definition + 4);
  const unsigned after = show ? (before | SSX_GATE_VISIBLE) : (before & ~SSX_GATE_VISIBLE);
  if (after != before) {
    ssx_gate_store(c, ssx_gate_definition + 4, after);
    ++ssx_gate_writes;
  }
  unsigned instance_before = 0, instance_after = 0, touched = 0;
  for (unsigned i = 0; i < ssx_gate_bound; ++i) {
    const unsigned address = ssx_gate_instances[i] + 128;
    if (!ssx_gate_in_ram(c, address)) continue;
    const unsigned was = ssx_gate_load(c, address);
    const unsigned now = show ? (was | SSX_GATE_VISIBLE) : (was & ~SSX_GATE_VISIBLE);
    if (!i) { instance_before = was; instance_after = now; }
    if (now != was) { ssx_gate_store(c, address, now); ++ssx_gate_writes; ++touched; }
  }
  fprintf(stderr, "[ssx-startgate-handler] {\"event\":\"set\",\"stage\":\"%s\",\"show\":%s,"
                  "\"ticks\":%llu,\"before\":%u,\"after\":%u,"
                  "\"instance_before\":%u,\"instance_after\":%u,\"instances_changed\":%u,"
                  "\"writes\":%u}\n",
          stage, show ? "true" : "false", (unsigned long long)c->timebase,
          before, after, instance_before, instance_after, touched, ssx_gate_writes);
}
