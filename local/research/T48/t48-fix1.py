#!/usr/bin/env python3
"""T48 fix 1: move the GS-side T48 globals from FlushPrim body to file scope."""
ST = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"

st = open(ST, encoding="utf-8").read()

in_fn = (
    "\t\tg_g13_draw_batches.fetch_add(1, std::memory_order_relaxed); // G13: draw-batch counter (same site as IncDraw).\n"
    "// T48: per-path census + per-draw ring (GS thread only; log-only).\n"
    "unsigned long long g_t48_pkts[3] = {0, 0, 0};\n"
    "unsigned long long g_t48_bytes[3] = {0, 0, 0};\n"
    "static int g_t48_curpath = -1;\n"
    "static unsigned long long g_t48_ring_n[4096] = {};\n"
    "static unsigned g_t48_ring_v[4096] = {};\n"
    "static int g_t48_ring_p[4096] = {};\n"
)
assert st.count(in_fn) == 1, "in-function T48 block count=%d" % st.count(in_fn)
st = st.replace(in_fn,
    "\t\tg_g13_draw_batches.fetch_add(1, std::memory_order_relaxed); // G13: draw-batch counter (same site as IncDraw).\n", 1)

file_anchor = "extern std::atomic<unsigned long long> g_g13_draw_batches; // G13: defined in GS.cpp, incremented in FlushPrim on the GS thread.\n"
assert st.count(file_anchor) == 1, "file-scope anchor count=%d" % st.count(file_anchor)
st = st.replace(file_anchor, file_anchor +
    "// T48: per-path census + per-draw ring (GS thread only; log-only).\n"
    "unsigned long long g_t48_pkts[3] = {0, 0, 0};\n"
    "unsigned long long g_t48_bytes[3] = {0, 0, 0};\n"
    "static int g_t48_curpath = -1;\n"
    "static unsigned long long g_t48_ring_n[4096] = {};\n"
    "static unsigned g_t48_ring_v[4096] = {};\n"
    "static int g_t48_ring_p[4096] = {};\n", 1)

open(ST, "w", encoding="utf-8").write(st)
print("T48 fix1 ok: globals at file scope")

# Also mirror the fix into the canonical hook script's ST1 hunk text is done
# by hand on the mini (t48-hook.py), not here.
