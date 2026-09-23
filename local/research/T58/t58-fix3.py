#!/usr/bin/env python3
"""T58 fix3: declare t58_store_watch at GLOBAL scope (before the namespace
opens) in FPU.cpp/VU0.cpp, and use plain unqualified calls (which then find
the global via enclosing-scope lookup). Removes the fix2 block-extern lines.
Validates before writing.
"""
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"

NS = "namespace R5900 {"
FPU_OLD = "\t{ extern void t58_store_watch(u32 vaddr, u32 size); t58_store_watch(addr, 4); } // T58: global def in R5900OpcodeImpl.cpp (T50 block-extern idiom)."
VU0_OLD = "\t\t{ extern void t58_store_watch(u32 vaddr, u32 size); t58_store_watch(addr, 16); } // T58: global def in R5900OpcodeImpl.cpp (T50 block-extern idiom)."
DECL = "void t58_store_watch(u32 vaddr, u32 size); // T58: global def in R5900OpcodeImpl.cpp.\n"


def main():
    for path, old, newcall in (
            (FPU, FPU_OLD, "\tt58_store_watch(addr, 4); // T58: EE staging-buffer writer watch (log-only)."),
            (VU0, VU0_OLD, "\tt58_store_watch(addr, 16); // T58: EE staging-buffer writer watch (log-only).")):
        body = open(path, encoding="utf-8").read()
        assert body.count(NS) == 1, "%s: ns anchor=%d" % (path, body.count(NS))
        assert body.count(old) == 1, "%s: call anchor=%d" % (path, body.count(old))
        assert "defined in R5900OpcodeImpl.cpp.\n" not in body, "%s: stale decl present" % path
        body = body.replace(NS, DECL + NS, 1)
        body = body.replace(old, newcall, 1)
        open(path, "w", encoding="utf-8").write(body)
    print("T58 fix3 applied: FPU(2) + VU0(2) ok")


if __name__ == "__main__":
    main()
