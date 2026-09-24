#!/usr/bin/env python3
"""AU5 opcode census from the EE helper's generated-code index."""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "/Users/brad/dev/ssx3/local/tooling/ee")
import ee

OUT = Path("/Users/brad/dev/ssx3/local/research/AU5/instruction-census.csv")
FUNCTIONS = {
    0x3C1638: "sound thread; tag-1 record and DMA",
    0x3C1298: "sound thread direct callee",
    0x3C07A8: "sound thread VU0 state helper",
    0x3C0858: "sound thread VU0 save",
    0x3C08F8: "sound thread VU0 restore",
    0x3C8968: "sound thread direct mix dispatcher",
    0x3C85D0: "mix dispatcher callee; indirect callbacks",
    0x3C9E50: "decoder upstream caller",
    0x3CCF90: "XA decoder direct caller",
    0x3CCA08: "XA decoder",
    0x3CB538: "voice path candidate; PINTEH",
    0x3CBB28: "VU0 mix callback container; entry 0x3CBB78",
    0x3C03E0: "MMI pack/level candidate; tag-1 link unproven",
}
FPU_TESTS = {
    "add.s", "sub.s", "mul.s", "div.s", "sqrt.s", "rsqrt.s",
    "madd.s", "madda.s", "max.s", "min.s", "cvt.s.w", "cvt.w.s",
    "abs.s", "neg.s", "c.eq.s", "c.le.s", "c.lt.s",
}
VU_TESTS = {"vadd", "vmul", "vmadd", "vmadda", "vmax", "vmini",
            "vftoi0", "vitof0", "vsqrt", "vrsqrt", "vsqi", "vlqi"}


def classify(op):
    if op in ("lq", "sq"):
        return "EE 128-bit memory", "untested", "No EE LQ/SQ alignment edge test found"
    if op.startswith("p") and op not in ("pref", "pause"):
        return "MMI", "untested", "No PCSX2 edge-input semantics test found; codegen/decoder tests do not qualify"
    if op in ("lqc2", "sqc2", "qmtc2.ni", "qmfc2.ni", "ctc2.ni", "cfc2.i") or op.startswith("v"):
        base = op.split(".")[0]
        if base in VU_TESTS:
            return "COP2/VU0", "tested", "ps2_fpu_cop2_audit_tests.cpp"
        return "COP2/VU0", "untested", "No matching PCSX2 edge-input semantics test found"
    if op in ("lwc1", "swc1", "mtc1", "mfc1", "cfc1", "ctc1") or ".s" in op:
        if op in FPU_TESTS:
            return "COP1", "tested", "ps2_fpu_cop2_audit_tests.cpp"
        return "COP1", "untested", "No matching PCSX2 edge-input semantics test found"
    return None


def main():
    ins = ee.build_index()["ins"]
    owners = {start: next((end for s, end, _ in ee.load_csv() if s == start), None)
              for start in FUNCTIONS}
    assert all(owners.values())
    rows = []
    for start, role in FUNCTIONS.items():
        for addr in range(start, owners[start], 4):
            if addr not in ins:
                continue
            word, text, delay = ins[addr]
            op = text.split()[0].lower()
            info = classify(op)
            if info is None:
                continue
            family, status, evidence = info
            rows.append((f"0x{start:08X}", f"0x{owners[start]:08X}", role,
                         f"0x{addr:08X}", f"0x{word:08X}", op, text,
                         family, status, evidence))
    with OUT.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(("function_start", "function_end", "role", "instruction_addr",
                         "word", "opcode", "disassembly", "family", "edge_test_status", "test_evidence"))
        writer.writerows(rows)
    counts = Counter((r[0], r[7], r[8]) for r in rows)
    for (func, family, status), count in sorted(counts.items()):
        print(func, family, status, count)
    print("instructions", len(rows), "functions", len(FUNCTIONS), "out", OUT)


if __name__ == "__main__":
    main()
