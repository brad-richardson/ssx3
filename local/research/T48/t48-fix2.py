#!/usr/bin/env python3
"""T48 fix 2: external linkage (drop static on shared globals), 4 index
slots, index->PATH mapping (idx3=P1 XGKICK/ring, idx1=P2 DIRECT,
idx2=P3 DMA/FIFO, idx0=dead GSgifTransfer1)."""
GS = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GS.cpp"
ST = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"
V1 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU1micro.cpp"


def rep_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


def main():
    st = open(ST, encoding="utf-8").read()
    st = rep_once(st,
        "unsigned long long g_t48_pkts[3] = {0, 0, 0};\n"
        "unsigned long long g_t48_bytes[3] = {0, 0, 0};\n"
        "static int g_t48_curpath = -1;\n"
        "static unsigned long long g_t48_ring_n[4096] = {};\n"
        "static unsigned g_t48_ring_v[4096] = {};\n"
        "static int g_t48_ring_p[4096] = {};\n",
        "unsigned long long g_t48_pkts[4] = {0, 0, 0, 0};\n"
        "unsigned long long g_t48_bytes[4] = {0, 0, 0, 0};\n"
        "int g_t48_curpath = -1;\n"
        "unsigned long long g_t48_ring_n[4096] = {};\n"
        "unsigned g_t48_ring_v[4096] = {};\n"
        "int g_t48_ring_p[4096] = {};\n",
        "T48-F2a")
    st = rep_once(st,
        "\tif (index >= 0 && index < 3)\n"
        "\t{\n"
        "\t\tg_t48_pkts[index]++;\n"
        "\t\tg_t48_bytes[index] += static_cast<unsigned long long>(size) * 16u;\n"
        "\t\tg_t48_curpath = index;\n"
        "\t}\n",
        "\tif (index >= 0 && index < 4)\n"
        "\t{\n"
        "\t\tg_t48_pkts[index]++;\n"
        "\t\tg_t48_bytes[index] += static_cast<unsigned long long>(size) * 16u;\n"
        "\t\tg_t48_curpath = (index == 3) ? 1 : (index == 1) ? 2 : (index == 2) ? 3 : 0;\n"
        "\t}\n",
        "T48-F2b")
    open(ST, "w", encoding="utf-8").write(st)

    gs = open(GS, encoding="utf-8").read()
    gs = rep_once(gs,
        "extern unsigned long long g_t48_pkts[3]; // T48: defined in GSState.cpp, per-path packet counts.\n"
        "extern unsigned long long g_t48_bytes[3]; // T48: defined in GSState.cpp, per-path byte counts.\n",
        "extern unsigned long long g_t48_pkts[4]; // T48: defined in GSState.cpp, per-index packet counts.\n"
        "extern unsigned long long g_t48_bytes[4]; // T48: defined in GSState.cpp, per-index byte counts.\n",
        "T48-F2c")
    gs = rep_once(gs,
        '\t\t\tConsole.WriteLn("T48_PATHS vsync=%d p1_pkts=%llu p1_bytes=%llu p2_pkts=%llu p2_bytes=%llu p3_pkts=%llu p3_bytes=%llu",\n'
        "\t\t\t\tg8_vsync_index, g_t48_pkts[0], g_t48_bytes[0], g_t48_pkts[1], g_t48_bytes[1], g_t48_pkts[2], g_t48_bytes[2]);\n"
        "\t\t\tg_t48_pkts[0] = g_t48_pkts[1] = g_t48_pkts[2] = 0;\n"
        "\t\t\tg_t48_bytes[0] = g_t48_bytes[1] = g_t48_bytes[2] = 0;\n",
        '\t\t\tConsole.WriteLn("T48_PATHS vsync=%d p1_pkts=%llu p1_bytes=%llu p2_pkts=%llu p2_bytes=%llu p3_pkts=%llu p3_bytes=%llu p0_pkts=%llu p0_bytes=%llu",\n'
        "\t\t\t\tg8_vsync_index, g_t48_pkts[3], g_t48_bytes[3], g_t48_pkts[1], g_t48_bytes[1], g_t48_pkts[2], g_t48_bytes[2], g_t48_pkts[0], g_t48_bytes[0]);\n"
        "\t\t\tg_t48_pkts[0] = g_t48_pkts[1] = g_t48_pkts[2] = g_t48_pkts[3] = 0;\n"
        "\t\t\tg_t48_bytes[0] = g_t48_bytes[1] = g_t48_bytes[2] = g_t48_bytes[3] = 0;\n",
        "T48-F2d")
    open(GS, "w", encoding="utf-8").write(gs)

    v1 = open(V1, encoding="utf-8").read()
    v1 = rep_once(v1,
        "static u64 g_t48_vu_startcycle = 0;\n"
        "static u32 g_t48_vu_startpc = 0;\n"
        "static u64 g_t48_vu_startxg = 0;\n"
        "extern u64 g_t48_vu_xg; // T48: defined in VUops.cpp.\n"
        "static bool g_t48_vu_active = false;\n"
        "static bool g_t48_vu_win = false;\n"
        "static bool g_t48_mode_logged = false;\n",
        "u64 g_t48_vu_startcycle = 0;\n"
        "u32 g_t48_vu_startpc = 0;\n"
        "u64 g_t48_vu_startxg = 0;\n"
        "extern u64 g_t48_vu_xg; // T48: defined in VUops.cpp.\n"
        "bool g_t48_vu_active = false;\n"
        "bool g_t48_vu_win = false;\n"
        "static bool g_t48_mode_logged = false;\n",
        "T48-F2e")
    open(V1, "w", encoding="utf-8").write(v1)

    print("T48 fix2 ok")


if __name__ == "__main__":
    main()
