#!/usr/bin/env python3
"""T48 bounded log-only patch (pcsx2-g7 @ 9056c083, on top of G12+G13).

Adds (all Console.WriteLn via the G8 emulog channel, plus counters):
  (a) GIF path (PATH1/2/3 = Transfer<0/1/2>) + true vertex count on each
      G12_DRAW line (ring written in FlushPrim, match-checked at Draw).
  (b) T48_PATHS per vsync (packets + bytes per path), armed runs only.
  (c) T48_VU1 per VU1 program (MSCAL/MSCNT/MSCALF via vu1ExecMicro to the
      E-bit stop in _vu1Exec): start_pc (TPC instruction index), cycles
      (VU1.cycle delta, interp 1/instr + stalls), xgkicks, end=ebit/abort.
      Exact under VU1-interp + MTVU-off (capture config); graceful
      (abort-only records) otherwise.
  (d) Script-driven 8-vsync dump trigger (/tmp/t48-arm + /tmp/t48-dump-now),
      suppressing the G13 auto-trigger while armed.

Hunks assert count==1 each, abort otherwise. Idempotent: aborts if T48
already applied. Behavior: counters + gated logs only; no renderer, EE,
timing or content change.
"""
import sys

GS = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GS.cpp"
ST = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"
HW = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/Renderers/HW/GSRendererHW.cpp"
V1 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU1micro.cpp"
VI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU1microInterp.cpp"
VO = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VUops.cpp"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, find + add, 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


def main():
    # ---- GS.cpp: atomics + trigger/PATHS block ----
    gs = open(GS, encoding="utf-8").read()
    assert "T48_DUMP_QUEUED" not in gs, "T48 already applied to GS.cpp"

    g13h1 = "std::atomic<int> g_g8_transfer_count{0}; // G8: Transfer-packet counter, incremented on the GS thread in GSState::Transfer.\n"
    gs_add_atoms = (
        "std::atomic<int> g_t48_vsync{0}; // T48: vsync mirror, GS writes / EE reads (relaxed; skew <1 vsync).\n"
        "std::atomic<bool> g_t48_window{false}; // T48: widened dump-window flag for VU1 gating.\n"
        "extern unsigned long long g_t48_pkts[4]; // T48: defined in GSState.cpp, per-index packet counts.\n"
        "extern unsigned long long g_t48_bytes[4]; // T48: defined in GSState.cpp, per-index byte counts.\n"
    )
    gs = apply_after_once(gs, g13h1, gs_add_atoms, "T48-GS1")

    g8q = "\t\tstatic bool g8_dump_queued = false;\n"
    t48_trig = (
        "\t\tstatic bool t48_queued = false;\n"
        "\t\tstatic bool t48_seen = false;\n"
        "\t\tstatic int t48_winstart = -1;\n"
        "\t\t// T48: script-driven dump trigger + per-path lines (log-only).\n"
        "\t\tif (!t48_seen)\n"
        "\t\t{\n"
        '\t\t\tFILE* t48af = fopen("/tmp/t48-arm", "r");\n'
        "\t\t\tif (t48af) { fclose(t48af); t48_seen = true; }\n"
        "\t\t}\n"
        "\t\tg_t48_vsync.store(g8_vsync_index, std::memory_order_relaxed);\n"
        "\t\tif (t48_seen)\n"
        "\t\t{\n"
        "\t\t\tif (!t48_queued && !g8_dump_queued && g_g7_execps2_count.load(std::memory_order_relaxed) >= 5)\n"
        "\t\t\t{\n"
        '\t\t\t\tFILE* t48qf = fopen("/tmp/t48-dump-now", "r");\n'
        "\t\t\t\tif (t48qf)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\tfclose(t48qf);\n"
        "\t\t\t\t\tt48_queued = true;\n"
        "\t\t\t\t\tg8_dump_queued = true; // T48: suppress the G13 auto-trigger; this window is ours.\n"
        "\t\t\t\t\tt48_winstart = g8_vsync_index + 1;\n"
        '\t\t\t\t\tConsole.WriteLn("T48_DUMP_QUEUED vsync=%d", g8_vsync_index);\n'
        '\t\t\t\t\tGSQueueSnapshot(std::string(), 5);\n'
        "\t\t\t\t}\n"
        "\t\t\t}\n"
        "\t\t\tconst bool t48_win = t48_queued && (g8_vsync_index >= t48_winstart - 30) && (g8_vsync_index < t48_winstart + 8);\n"
        "\t\t\tg_t48_window.store(t48_win, std::memory_order_relaxed);\n"
        '\t\t\tConsole.WriteLn("T48_PATHS vsync=%d p1_pkts=%llu p1_bytes=%llu p2_pkts=%llu p2_bytes=%llu p3_pkts=%llu p3_bytes=%llu p0_pkts=%llu p0_bytes=%llu",\n'
        "\t\t\t\tg8_vsync_index, g_t48_pkts[3], g_t48_bytes[3], g_t48_pkts[1], g_t48_bytes[1], g_t48_pkts[2], g_t48_bytes[2], g_t48_pkts[0], g_t48_bytes[0]);\n"
        "\t\t\tg_t48_pkts[0] = g_t48_pkts[1] = g_t48_pkts[2] = g_t48_pkts[3] = 0;\n"
        "\t\t\tg_t48_bytes[0] = g_t48_bytes[1] = g_t48_bytes[2] = g_t48_bytes[3] = 0;\n"
        "\t\t}\n"
    )
    gs = apply_after_once(gs, g8q, t48_trig, "T48-GS3")

    # Guard the two G13 fires while a T48 run is armed.
    g13rate = "\t\t\t\tif (g8_vsync_index >= 1200 && g13_hot_streak >= 2)\n"
    gs = replace_once(gs, g13rate,
        "\t\t\t\tif (!t48_seen && g8_vsync_index >= 1200 && g13_hot_streak >= 2)\n", "T48-GS4a")
    g13fb = "\t\t\t\telse if (g8_vsync_index >= 5000)\n"
    gs = replace_once(gs, g13fb,
        "\t\t\t\telse if (!t48_seen && g8_vsync_index >= 5000)\n", "T48-GS4b")

    open(GS, "w", encoding="utf-8").write(gs)

    _apply_gs_state()
    return


def _apply_gs_state():
    ST_local = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"
    HW = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/Renderers/HW/GSRendererHW.cpp"
    # ---- GSState.cpp: counters + ring ----
    st = open(ST_local, encoding="utf-8").read()
    assert "g_t48_pkts" not in st, "T48 already applied to GSState.cpp"

    g13h4b = "extern std::atomic<unsigned long long> g_g13_draw_batches; // G13: defined in GS.cpp, incremented in FlushPrim on the GS thread.\n"
    st_defs = (
        "// T48: per-path census + per-draw ring (GS thread only; log-only).\n"
        "unsigned long long g_t48_pkts[4] = {0, 0, 0, 0};\n"
        "unsigned long long g_t48_bytes[4] = {0, 0, 0, 0};\n"
        "int g_t48_curpath = -1;\n"
        "unsigned long long g_t48_ring_n[4096] = {};\n"
        "unsigned g_t48_ring_v[4096] = {};\n"
        "int g_t48_ring_p[4096] = {};\n"
    )
    st = apply_after_once(st, g13h4b, st_defs, "T48-ST1")

    tr_anchor = "\tGIFPath& path = m_path[index];\n"
    tr_add = (
        "\t// T48: per-path census + current-path stash (log-only; idx3=P1 XGKICK/ring, idx1=P2 DIRECT, idx2=P3 DMA/FIFO, idx0=dead).\n"
        "\tif (index >= 0 && index < 4)\n"
        "\t{\n"
        "\t\tg_t48_pkts[index]++;\n"
        "\t\tg_t48_bytes[index] += static_cast<unsigned long long>(size) * 16u;\n"
        "\t\tg_t48_curpath = (index == 3) ? 1 : (index == 1) ? 2 : (index == 2) ? 3 : 0;\n"
        "\t}\n"
    )
    st = apply_after_once(st, tr_anchor, tr_add, "T48-ST2")

    fl_anchor = "\tconst u32 next = vtx_buff.next;\n"
    fl_add = (
        "\t// T48: per-draw vertex/path ring (log-only; match-checked on the G12_DRAW line).\n"
        "\tg_t48_ring_n[s_n & 4095] = s_n;\n"
        "\tg_t48_ring_v[s_n & 4095] = (tail > head) ? (tail - head) : 0;\n"
        "\tg_t48_ring_p[s_n & 4095] = g_t48_curpath;\n"
    )
    st = apply_after_once(st, fl_anchor, fl_add, "T48-ST3")
    open(ST, "w", encoding="utf-8").write(st)

    # ---- GSRendererHW.cpp: path + true verts on G12_DRAW ----
    hw = open(HW, encoding="utf-8").read()
    assert "g_t48_ring_n" not in hw, "T48 already applied to GSRendererHW.cpp"

    h7_anchor = "\t// G12: per-draw order trace (log-only).\n"
    hw = apply_after_once(hw, h7_anchor,
        "\textern unsigned long long g_t48_ring_n[4096]; // T48: defined in GSState.cpp.\n"
        "\textern unsigned g_t48_ring_v[4096];\n"
        "\textern int g_t48_ring_p[4096];\n",
        "T48-HW0")

    fmt_find = "TME=%u PRIM=%u verts=%u\",\n"
    hw = replace_once(hw, fmt_find, "TME=%u PRIM=%u verts=%u path=%d\",\n", "T48-HW1a")

    arg_find = "\t\tstatic_cast<unsigned>(m_draw_env->PRIM.PRIM), vtx_buff.tail - vtx_buff.head);\n"
    arg_repl = (
        "\t\tstatic_cast<unsigned>(m_draw_env->PRIM.PRIM), (g_t48_ring_n[s_n & 4095] == s_n) ? g_t48_ring_v[s_n & 4095] : 0,\n"
        "\t\t(g_t48_ring_n[s_n & 4095] == s_n) ? g_t48_ring_p[s_n & 4095] : -2);\n"
    )
    hw = replace_once(hw, arg_find, arg_repl, "T48-HW1b")
    open(HW, "w", encoding="utf-8").write(hw)

    # ---- VU1micro.cpp: program record begin ----
    v1 = open(V1, encoding="utf-8").read()
    assert "g_t48_vu_active" not in v1, "T48 already applied to VU1micro.cpp"

    v1_defs_anchor = '#include "MTVU.h"\n'
    v1_defs = (
        "// T48: per-program cycle/xgkick record (log-only; exact under sync VU1 interp, i.e. MTVU off + interpreter).\n"
        "u64 g_t48_vu_startcycle = 0;\n"
        "u32 g_t48_vu_startpc = 0;\n"
        "u64 g_t48_vu_startxg = 0;\n"
        "extern u64 g_t48_vu_xg; // T48: defined in VUops.cpp.\n"
        "bool g_t48_vu_active = false;\n"
        "bool g_t48_vu_win = false;\n"
        "static bool g_t48_mode_logged = false;\n"
        "extern std::atomic<int> g_t48_vsync;\n"
        "extern std::atomic<bool> g_t48_window;\n"
    )
    v1 = apply_after_once(v1, v1_defs_anchor, v1_defs, "T48-VU1a")

    v1_begin_anchor = "\tif ((s32)addr != -1) VU1.VI[REG_TPC].UL = addr & 0x7FF;\n"
    v1_begin = (
        "\t// T48: begin program record (a live one closes as aborted).\n"
        "\tif (!g_t48_mode_logged) { g_t48_mode_logged = true; Console.WriteLn(\"T48_MODE mtvu=%d\", THREAD_VU1 ? 1 : 0); }\n"
        "\tif (g_t48_vu_active)\n"
        "\t{\n"
        '\t\tif (g_t48_vu_win) Console.WriteLn("T48_VU1 vsync=%d start_pc=0x%x cycles=%llu xgkicks=%llu end=abort", g_t48_vsync.load(std::memory_order_relaxed), g_t48_vu_startpc, VU1.cycle - g_t48_vu_startcycle, g_t48_vu_xg - g_t48_vu_startxg);\n'
        "\t}\n"
        "\tg_t48_vu_startpc = VU1.VI[REG_TPC].UL;\n"
        "\tg_t48_vu_startcycle = VU1.cycle;\n"
        "\tg_t48_vu_startxg = g_t48_vu_xg;\n"
        "\tg_t48_vu_active = true;\n"
        "\tg_t48_vu_win = g_t48_window.load(std::memory_order_relaxed);\n"
    )
    v1 = apply_after_once(v1, v1_begin_anchor, v1_begin, "T48-VU1b")
    open(V1, "w", encoding="utf-8").write(v1)

    # ---- VU1microInterp.cpp: close at E-bit ----
    vi = open(VI, encoding="utf-8").read()
    assert "g_t48_vu_active" not in vi, "T48 already applied to VU1microInterp.cpp"

    vi_ext_anchor = "extern void _vuFlushAll(VURegs* VU);\nextern void _vuXGKICKFlush(VURegs* VU);\n"
    vi = apply_after_once(vi, vi_ext_anchor,
        "extern u64 g_t48_vu_startcycle; // T48: defined in VU1micro.cpp.\n"
        "extern u32 g_t48_vu_startpc;\n"
        "extern u64 g_t48_vu_startxg;\n"
        "extern u64 g_t48_vu_xg;\n"
        "extern bool g_t48_vu_active;\n"
        "extern bool g_t48_vu_win;\n"
        "extern std::atomic<int> g_t48_vsync;\n"
        "extern std::atomic<bool> g_t48_window;\n",
        "T48-VU2a")

    vi_ebit_anchor = "\t\tif (VU->ebit-- == 1)\n\t\t{\n"
    vi_ebit_add = (
        "\t\t\t// T48: close program record at the E-bit stop (log-only).\n"
        "\t\t\tif (g_t48_vu_active)\n"
        "\t\t\t{\n"
        '\t\t\t\tif (g_t48_vu_win) Console.WriteLn("T48_VU1 vsync=%d start_pc=0x%x cycles=%llu xgkicks=%llu end=ebit", g_t48_vsync.load(std::memory_order_relaxed), g_t48_vu_startpc, VU1.cycle - g_t48_vu_startcycle, g_t48_vu_xg - g_t48_vu_startxg);\n'
        "\t\t\t\tg_t48_vu_active = false;\n"
        "\t\t\t}\n"
    )
    vi = apply_after_once(vi, vi_ebit_anchor, vi_ebit_add, "T48-VU2b")
    open(VI, "w", encoding="utf-8").write(vi)

    # ---- VUops.cpp: XGKICK counter ----
    vo = open(VO, encoding="utf-8").read()
    assert "g_t48_vu_xg" not in vo, "T48 already applied to VUops.cpp"

    vo_ext_anchor = "u32 laststall = 0;\n"
    vo = apply_after_once(vo, vo_ext_anchor,
        "u64 g_t48_vu_xg = 0; // T48: XGKICK-instruction counter (log-only; def here, record in VU1micro.cpp).\n",
        "T48-VU3a")

    vo_xg_anchor = "static __ri void _vuXGKICK(VURegs* VU)\n{\n"
    vo = apply_after_once(vo, vo_xg_anchor,
        "\tg_t48_vu_xg++; // T48: one XGKICK instruction executed (log-only).\n",
        "T48-VU3b")
    open(VO, "w", encoding="utf-8").write(vo)

    print("T48 hook applied: GS(4) + ST(3) + HW(3) + V1(2) + VI(2) + VO(2) ok")


if __name__ == "__main__":
    main()
