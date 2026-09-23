#!/usr/bin/env python3
"""T58 fix (b1 link repair): t58_store_watch/t58_dma_watch are defined once
at global scope in R5900OpcodeImpl.cpp, but the FPU (COP1-nested) and VU0
(OpcodeImpl-nested) call sites resolve the unqualified name to their own
namespace. Qualify those two calls with :: and drop the misleading
namespace-scope decls (SPR/SIF0/SIF2/IPU call from global scope already).
Validates before writing.
"""
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"

FPU_DECL = "void t58_store_watch(u32 vaddr, u32 size); // T58: defined in R5900OpcodeImpl.cpp.\n"
VU0_DECL = FPU_DECL
FPU_CALL = "\tt58_store_watch(addr, 4); // T58: EE staging-buffer writer watch (log-only)."
VU0_CALL = "\t\tt58_store_watch(addr, 16); // T58: EE staging-buffer writer watch (log-only)."


def main():
    fpu = open(FPU, encoding="utf-8").read()
    vu0 = open(VU0, encoding="utf-8").read()
    assert "::t58_store_watch" not in fpu, "FPU already fixed"
    assert "::t58_store_watch" not in vu0, "VU0 already fixed"
    assert fpu.count(FPU_DECL) == 1, "FPU decl anchor=%d" % fpu.count(FPU_DECL)
    assert vu0.count(VU0_DECL) == 1, "VU0 decl anchor=%d" % vu0.count(VU0_DECL)
    assert fpu.count(FPU_CALL) == 1, "FPU call anchor=%d" % fpu.count(FPU_CALL)
    assert vu0.count(VU0_CALL) == 1, "VU0 call anchor=%d" % vu0.count(VU0_CALL)
    fpu = fpu.replace(FPU_DECL, "", 1)
    vu0 = vu0.replace(VU0_DECL, "", 1)
    fpu = fpu.replace(FPU_CALL,
                      "\t::t58_store_watch(addr, 4); // T58: global def in R5900OpcodeImpl.cpp.", 1)
    vu0 = vu0.replace(VU0_CALL,
                      "\t\t::t58_store_watch(addr, 16); // T58: global def in R5900OpcodeImpl.cpp.", 1)
    open(FPU, "w", encoding="utf-8").write(fpu)
    open(VU0, "w", encoding="utf-8").write(vu0)
    print("T58 fix applied: FPU(2) + VU0(2) ok")


if __name__ == "__main__":
    main()
