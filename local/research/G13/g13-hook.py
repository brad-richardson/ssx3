#!/usr/bin/env python3
"""G13 rich-scene trigger + draw/byte counters + G12-log gating (pcsx2-g7).

Applies 10 exact-match hunks (asserts count==1 each, aborts otherwise):
  GS.cpp:
    H1 decls for g_g13_transfer_bytes / g_g13_draw_batches (def, GS thread)
    H2 comment note that the fire condition is replaced (G8 text kept)
    H3 fire-block replace: G8 K=500 fire -> G13 rate trigger + fallback
         (FIRST_NONZERO kept as determinism receipt; G13_SCAN every 500)
  GSState.cpp:
    H4 extern decls for the two counters
    H5 Transfer: also count GIF bytes (same mem>start condition)
    H6 FlushPrim: count prim-flush batches (same site as IncDraw)
  GSRendererHW.cpp (G12-log gates; replay binary already built, untouched):
    H7 gate H1 G12_DRAW on m_dump (dump window only during capture)
    H8 gate H4 G12_RASTER on m_dump
    H9 gate H2 G12_SKIP/badframe on m_dump
    H10 gate H3 G12_SKIP/blackpoint on m_dump
  Deliberately unchanged: H5 G12_VSYNC (1 line/vsync cadence), H6 replayer.

Thresholds (declared): floor vsync>=1200 (past G8 1076+window+margin);
scene = >=25 batches AND >=16 KiB in one vsync, 2 consecutive (loading:
3 draws + ~2.4 KiB/vsync); fallback vsync>=5000 (~190 s at 26 vsync/s).
Log-only except the trigger/counters (no behavior change besides the
one-shot snapshot queue + gated logs).
Idempotent: aborts if G13_DUMP_QUEUED already present.
"""
import sys

GS = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GS.cpp"
ST = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"
HW = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/Renderers/HW/GSRendererHW.cpp"

H1_FIND = "std::atomic<int> g_g8_transfer_count{0}; // G8: Transfer-packet counter, incremented on the GS thread in GSState::Transfer.\n"
H1_ADD = (
    "std::atomic<unsigned long long> g_g13_transfer_bytes{0}; // G13: GIF-byte counter, incremented on the GS thread in GSState::Transfer.\n"
    "std::atomic<unsigned long long> g_g13_draw_batches{0}; // G13: prim-flush counter, incremented on the GS thread in GSState::FlushPrim.\n"
)

H2_FIND = "\t// the first non-zero-transfer vsync past game entry (ExecPS2 #5).\n"
H2_ADD = "\t// G13: fire condition replaced (rate-based scene trigger + fallback below); FIRST_NONZERO kept as determinism receipt.\n"

H3_FIND = (
    "\t\t\t\tif (g8_first_nonzero_vsync >= 0 && (total - g8_first_nonzero_total) >= 500)\n"
    "\t\t\t\t{\n"
    "\t\t\t\t\tg8_dump_queued = true;\n"
    '\t\t\t\t\tConsole.WriteLn("G8_DUMP_QUEUED vsync=%d transfers=%d K=500", g8_vsync_index, total);\n'
    "\t\t\t\t\tGSQueueSnapshot(std::string(), 5);\n"
    "\t\t\t\t}\n"
)
H3_REPL = (
    "\t\t\t\t// G13: rich-scene trigger (replaces the G8 K=500 fire above).\n"
    "\t\t\t\tstatic unsigned long long g13_prev_bytes = 0;\n"
    "\t\t\t\tstatic unsigned long long g13_prev_batches = 0;\n"
    "\t\t\t\tstatic int g13_hot_streak = 0;\n"
    "\t\t\t\tstatic bool g13_prev_init = false;\n"
    "\t\t\t\tconst unsigned long long total_bytes = g_g13_transfer_bytes.load(std::memory_order_relaxed);\n"
    "\t\t\t\tconst unsigned long long total_batches = g_g13_draw_batches.load(std::memory_order_relaxed);\n"
    "\t\t\t\tif (!g13_prev_init)\n"
    "\t\t\t\t{\n"
    "\t\t\t\t\tg13_prev_bytes = total_bytes;\n"
    "\t\t\t\t\tg13_prev_batches = total_batches;\n"
    "\t\t\t\t\tg13_prev_init = true;\n"
    "\t\t\t\t}\n"
    "\t\t\t\tconst unsigned long long this_bytes = total_bytes - g13_prev_bytes;\n"
    "\t\t\t\tconst unsigned long long this_batches = total_batches - g13_prev_batches;\n"
    "\t\t\t\tg13_prev_bytes = total_bytes;\n"
    "\t\t\t\tg13_prev_batches = total_batches;\n"
    "\t\t\t\tif ((g8_vsync_index % 500) == 0)\n"
    '\t\t\t\t\tConsole.WriteLn("G13_SCAN vsync=%d transfers=%d bytes=%llu batches=%llu", g8_vsync_index, total, total_bytes, total_batches);\n'
    "\t\t\t\tif (this_batches >= 25 && this_bytes >= 16384)\n"
    "\t\t\t\t\tg13_hot_streak++;\n"
    "\t\t\t\telse\n"
    "\t\t\t\t\tg13_hot_streak = 0;\n"
    "\t\t\t\tif (g8_vsync_index >= 1200 && g13_hot_streak >= 2)\n"
    "\t\t\t\t{\n"
    "\t\t\t\t\tg8_dump_queued = true;\n"
    '\t\t\t\t\tConsole.WriteLn("G13_DUMP_QUEUED vsync=%d transfers=%d bytes=%llu batches=%llu streak=%d", g8_vsync_index, total, total_bytes, total_batches, g13_hot_streak);\n'
    "\t\t\t\t\tGSQueueSnapshot(std::string(), 5);\n"
    "\t\t\t\t}\n"
    "\t\t\t\telse if (g8_vsync_index >= 5000)\n"
    "\t\t\t\t{\n"
    "\t\t\t\t\tg8_dump_queued = true;\n"
    '\t\t\t\t\tConsole.WriteLn("G13_DUMP_FALLBACK vsync=%d transfers=%d bytes=%llu batches=%llu", g8_vsync_index, total, total_bytes, total_batches);\n'
    "\t\t\t\t\tGSQueueSnapshot(std::string(), 5);\n"
    "\t\t\t\t}\n"
)

H4_FIND = "extern std::atomic<int> g_g8_transfer_count; // G8: defined in GS.cpp, incremented below on the GS thread.\n"
H4_ADD = (
    "extern std::atomic<unsigned long long> g_g13_transfer_bytes; // G13: defined in GS.cpp, incremented below on the GS thread.\n"
    "extern std::atomic<unsigned long long> g_g13_draw_batches; // G13: defined in GS.cpp, incremented in FlushPrim on the GS thread.\n"
)

H5_FIND = (
    "\t// G8: count Transfer packets on the GS thread (same mem>start condition as the dump writer below).\n"
    "\tif (mem > start)\n"
    "\t\tg_g8_transfer_count.fetch_add(1, std::memory_order_relaxed);\n"
)
H5_REPL = (
    "\t// G8: count Transfer packets on the GS thread (same mem>start condition as the dump writer below).\n"
    "\t// G13: also count GIF bytes (scene-vs-loading discriminator).\n"
    "\tif (mem > start)\n"
    "\t{\n"
    "\t\tg_g8_transfer_count.fetch_add(1, std::memory_order_relaxed);\n"
    "\t\tg_g13_transfer_bytes.fetch_add(static_cast<unsigned long long>(mem - start), std::memory_order_relaxed);\n"
    "\t}\n"
)

H6_FIND = "\t\tIncDraw();\n"
H6_ADD = "\t\tg_g13_draw_batches.fetch_add(1, std::memory_order_relaxed); // G13: draw-batch counter (same site as IncDraw).\n"

H7_FIND = "\t// G12: per-draw order trace (log-only).\n"
H7_ADD = "\tif (m_dump) // G13: capture runs log draws only inside the dump window (replay binary already built).\n"

H8_FIND = "\t// G12: actual-rasterization trace (log-only).\n"
H8_ADD = "\tif (m_dump) // G13: same gate as H7.\n"

H9_FIND = '\t\tConsole.WriteLn("G12_SKIP n=%llu reason=badframe", static_cast<unsigned long long>(s_n));\n'
H9_ADD = "\t\tif (m_dump)\n"

H10_FIND = '\t\t\tConsole.WriteLn("G12_SKIP n=%llu reason=blackpoint", static_cast<unsigned long long>(s_n));\n'
H10_ADD = "\t\t\tif (m_dump)\n"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, f"{name}: anchor count={n}, want 1"
    return text.replace(find, find + add, 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, f"{name}: anchor count={n}, want 1"
    return text.replace(find, repl, 1)


def main():
    gs = open(GS, encoding="utf-8").read()
    assert "G13_DUMP_QUEUED" not in gs, "G13 already applied to GS.cpp"
    gs = apply_after_once(gs, H1_FIND, H1_ADD, "H1")
    gs = apply_after_once(gs, H2_FIND, H2_ADD, "H2")
    gs = replace_once(gs, H3_FIND, H3_REPL, "H3")
    open(GS, "w", encoding="utf-8").write(gs)

    st = open(ST, encoding="utf-8").read()
    assert "g_g13_draw_batches" not in st, "G13 already applied to GSState.cpp"
    st = apply_after_once(st, H4_FIND, H4_ADD, "H4")
    st = replace_once(st, H5_FIND, H5_REPL, "H5")
    st = apply_after_once(st, H6_FIND, H6_ADD, "H6")
    open(ST, "w", encoding="utf-8").write(st)

    hw = open(HW, encoding="utf-8").read()
    assert "G13: capture runs log draws only" not in hw, "G13 already applied to GSRendererHW.cpp"
    hw = apply_after_once(hw, H7_FIND, H7_ADD, "H7")
    hw = apply_after_once(hw, H8_FIND, H8_ADD, "H8")
    n = hw.count(H9_FIND)
    assert n == 1, f"H9: anchor count={n}, want 1"
    hw = hw.replace(H9_FIND, H9_ADD + H9_FIND, 1)
    n = hw.count(H10_FIND)
    assert n == 1, f"H10: anchor count={n}, want 1"
    hw = hw.replace(H10_FIND, H10_ADD + H10_FIND, 1)
    open(HW, "w", encoding="utf-8").write(hw)

    print("G13 hook applied: H1-H10 ok")


if __name__ == "__main__":
    main()
