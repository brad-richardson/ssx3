#!/usr/bin/env python3
"""T49 unhook: exact inverse of t49-hook.py, for patch-diff generation ONLY.

NEVER run on the real tree. Operates solely on the baseline copies under
/home/brad/pcsx2-g7/t49base/pcsx2 (created by copying the 6 worktree files).
Each removal asserts count==1 or aborts. After this, t49base holds the
G+T48 baseline; diffing it against the worktree yields the pure T49 patch.
"""
import importlib.util

ROOT = "/home/brad/pcsx2-g7/t49base/pcsx2"
GS = ROOT + "/GS/GS.cpp"
V1 = ROOT + "/VU1micro.cpp"
VI = ROOT + "/VU1microInterp.cpp"
VO = ROOT + "/VUops.cpp"
VT = ROOT + "/Vif_Transfer.cpp"
VC = ROOT + "/Vif_Codes.cpp"

spec = importlib.util.spec_from_file_location("t49_hook", "/home/brad/pcsx2-g7/t49-hook.py")
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)


def remove_once(text, find, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, "", 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


SETSTART = "\tCpuVU1->SetStartPC(VU1.VI[REG_TPC].UL << 3);\n"
PTR2 = "\tptr = (u32*)&VU->Micro[VU->VI[REG_TPC].UL];\n\tVU->VI[REG_TPC].UL += 8;\n"
VO2A = "\tif (VU == &vuRegs[1])\n\t\treturn (u32*)(vuRegs[1].Mem + (addr & 0x3fff));\n"
MSCAL_A = "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);\n"
MSCALF_A = "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);\n"
MSCNT_A = "\t\tvuExecMicro(idx, -1, false);\n"


def main():
    assert GS.startswith("/home/brad/pcsx2-g7/t49base/"), "refusing non-baseline root"
    gs = open(GS, encoding="utf-8").read()
    gs = remove_once(gs, "std::atomic<int> g_t49_winstart{-1}; // T49: dump-window start mirror (GS writes / EE reads).\n", "U-GS1")
    gs = remove_once(gs, "\t\t\t\t\tg_t49_winstart.store(t48_winstart, std::memory_order_relaxed); // T49: mirror for the dump-vsync gate.\n", "U-GS2")
    open(GS, "w", encoding="utf-8").write(gs)

    v1 = open(V1, encoding="utf-8").read()
    v1 = remove_once(v1, H.T49_V1_DECLS, "U-V1a")
    v1 = replace_once(v1, H.T49_V1_DUMP + SETSTART, SETSTART, "U-V1b")
    open(V1, "w", encoding="utf-8").write(v1)

    vi = open(VI, encoding="utf-8").read()
    vi = remove_once(vi, H.T49_VI_EXTERNS, "U-VI0")
    vi = remove_once(vi, H.T49_VI_DISASM, "U-VI1")
    vi = replace_once(vi, PTR2 + H.T49_VI_PROLOGUE, PTR2, "U-VI2")
    vi = remove_once(vi, H.T49_VI_EPILOGUE, "U-VI3")
    vi = remove_once(vi, H.T49_VI_EBIT, "U-VI4")
    open(VI, "w", encoding="utf-8").write(vi)

    vo = open(VO, encoding="utf-8").read()
    vo = remove_once(vo, H.T49_VO_DECLS, "U-VO1")
    vo = replace_once(vo,
                      "\tif (VU == &vuRegs[1])\n\t{\n\t\tif (g_t49_pair_active) t49_touch((addr & 0x3fff) >> 4); // T49: tap VU1 interp mem rows (log-only).\n\t\treturn (u32*)(vuRegs[1].Mem + (addr & 0x3fff));\n\t}\n",
                      VO2A, "U-VO2")
    open(VO, "w", encoding="utf-8").write(vo)

    vt = open(VT, encoding="utf-8").read()
    vt = remove_once(vt, "extern void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops); // T49: defined in VU1micro.cpp.\n", "U-VT1")
    vt = remove_once(vt, "\t\t\tif (idx == 1) t49_vif_record(data[0], data, pSize, vifXRegs.cycle.cl, vifXRegs.cycle.wl, vifXRegs.mask, vifXRegs.tops, vifXRegs.itops); // T49: record every VIF1 command (log-only).\n", "U-VT2")
    open(VT, "w", encoding="utf-8").write(vt)

    vc = open(VC, encoding="utf-8").read()
    vc = remove_once(vc, "extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.\n", "U-VC1")
    vc = replace_once(vc, "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n" + MSCAL_A, MSCAL_A, "U-VC2")
    vc = replace_once(vc, "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n" + MSCALF_A, MSCALF_A, "U-VC3")
    vc = replace_once(vc, "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n" + MSCNT_A, MSCNT_A, "U-VC4")
    open(VC, "w", encoding="utf-8").write(vc)

    print("T49 unhook ok: baseline copies stripped")


if __name__ == "__main__":
    main()
