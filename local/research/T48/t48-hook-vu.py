#!/usr/bin/env python3
"""T48 VU-only applier: exact subset of t48-hook.py (V1/VI/VO sections).

Repair tool: the first t48-hook.py run had anchor re-add bugs in the VU
sections only; the 3 VU files were reverted to HEAD (they carry no prior
G12/G13 hunks) while GS.cpp/GSState.cpp/GSRendererHW.cpp keep their T48
hunks. This applies the fixed VU hunks. Same asserts, same hunks as the
full script would have produced.
"""
import sys

V1 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU1micro.cpp"
VI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU1microInterp.cpp"
VO = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VUops.cpp"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, find + add, 1)


def main():
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

    print("T48 VU hook applied: V1(2) + VI(2) + VO(2) ok")


if __name__ == "__main__":
    main()
