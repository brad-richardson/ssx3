#!/usr/bin/env python3
"""T58 fix2 (b2 compile repair): FPU/VU0 call sites sit inside nested
namespaces where ::t58_store_watch has no visible declaration (fix1 removed
the decls). Use T50's block-scope extern idiom: declare extern locally at
the call site, which always names the global (RI TU) definition.
Validates before writing.
"""
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"

FPU_OLD = "\t::t58_store_watch(addr, 4); // T58: global def in R5900OpcodeImpl.cpp."
VU0_OLD = "\t\t::t58_store_watch(addr, 16); // T58: global def in R5900OpcodeImpl.cpp."
FPU_NEW = "\t{ extern void t58_store_watch(u32 vaddr, u32 size); t58_store_watch(addr, 4); } // T58: global def in R5900OpcodeImpl.cpp (T50 block-extern idiom)."
VU0_NEW = "\t\t{ extern void t58_store_watch(u32 vaddr, u32 size); t58_store_watch(addr, 16); } // T58: global def in R5900OpcodeImpl.cpp (T50 block-extern idiom)."


def main():
    fpu = open(FPU, encoding="utf-8").read()
    vu0 = open(VU0, encoding="utf-8").read()
    assert fpu.count(FPU_OLD) == 1, "FPU anchor=%d" % fpu.count(FPU_OLD)
    assert vu0.count(VU0_OLD) == 1, "VU0 anchor=%d" % vu0.count(VU0_OLD)
    assert "extern void t58_store_watch" not in fpu, "FPU already fixed"
    assert "extern void t58_store_watch" not in vu0, "VU0 already fixed"
    fpu = fpu.replace(FPU_OLD, FPU_NEW, 1)
    vu0 = vu0.replace(VU0_OLD, VU0_NEW, 1)
    open(FPU, "w", encoding="utf-8").write(fpu)
    open(VU0, "w", encoding="utf-8").write(vu0)
    print("T58 fix2 applied: FPU(1) + VU0(1) ok")


if __name__ == "__main__":
    main()
