#!/usr/bin/env python3
"""N4 bucket rollup from simpleperf self-report text files."""
import re
import sys

# addr2line-resolved attributions for otherwise-bare offsets
BARE = {
    # title cluster: GS read-path std::function wrappers + texture sampling
    "0xdff210": "gs", "0xdff214": "gs", "0xdff21c": "gs", "0xdff224": "gs",
    "0xdff22c": "gs", "0xdff228": "gs", "0xdfc014": "gs",
    "0xdfbef4": "gs", "0xdfbf14": "gs", "0xdfbf68": "gs", "0xdfbf90": "gs",
    "0xdfbff4": "gs", "0xdfc194": "gs", "0xdfc04c": "gs", "0xdfc148": "gs",
    "0xdfbf6c": "gs",
    # fnv1a32 frame-dump hash (diagnostics)
    "0xde581c": "diag", "0xde5824": "diag", "0xde5818": "diag",
    # VU1 exact-result lambda
    "0xe105d8": "vu1",
    # EeScheduler snapshot sort
    "0xe46cc0": "sched",
    # menu cluster: compiler-rt quad-precision soft-float (VU1 FMAC emulation)
    "0x79688bc": "vu1", "0x7968cc8": "vu1", "0x7968ef0": "vu1",
    "0x7968f74": "vu1", "0x7968f1c": "vu1", "0x7968f5c": "vu1",
    "0x7968edc": "vu1", "0x7968f3c": "vu1", "0x7968ee0": "vu1",
    "0x7968d08": "vu1", "0x7968d3c": "vu1", "0x7968f64": "vu1",
    "0x7969398": "vu1", "0x7968eec": "vu1", "0x7968f60": "vu1",
    "0x7968ee8": "vu1",
}


RANGES = [
    (0xdf0000, 0xe00000, "gs"),
    (0xde5800, 0xde5900, "diag"),
    (0xe10500, 0xe10800, "vu1"),
    (0xe43e00, 0xe47000, "sched"),
    (0x7968000, 0x796a000, "vu1"),
]


def classify(sym, dso):
    s = sym.strip()
    m = re.search(r"\[\+([0-9a-f]+)\]$", s)
    if m and "libps2EntryRunner" in dso:
        key = "0x" + m.group(1)
        if key in BARE:
            return BARE[key]
        addr = int(m.group(1), 16)
        for lo, hi, b in RANGES:
            if lo <= addr < hi:
                return b
        return "other_unresolved"
    if "VU1Interpreter::" in s:
        return "vu1"
    if "__addtf3" in s or "__extendsftf2" in s or "__eqtf2" in s or \
       "__multf3" in s or "__subtf3" in s or "__letf2" in s or "__gttf2" in s:
        return "vu1"
    if "GSCpuBackend::" in s or "GSMem::" in s or "GSInternal::" in s or \
       "wrapTextureCoordinate" in s or "applyTexa" in s or \
       "SampleTexture" in s or "ReadVram" in s or "clampInt" in s:
        return "gs"
    if "sub_" in s and ("_Z" in s or " T " in s or "sub_0x" in s or re.search(r"sub_[0-9a-f]", s)):
        return "guest"
    if re.search(r"\b(Gif|Vif|Dma)::", s):
        return "gifvifdma"
    if "stbi_" in s or "fnv1a32" in s or "writePngBytes" in s or \
       "ExportImage" in s or "dumpPresentationFrame" in s:
        return "diag"
    if "EeScheduler::" in s or "publishSnapshot" in s or "ps2_e7" in s or \
       "ps2_e15" in s or "diag" in s.lower():
        return "sched"
    if "libc.so" in dso or "libm.so" in dso or "[vdso]" in dso or \
       "bionic" in dso or "libEGL" in dso or "libGLES" in dso or \
       "libhar" in dso or "agl" in dso.lower():
        return "sys"
    if "raylib" in s or "rlgl" in s or "RL_" in s or "LoadImageColors" in s or \
       "CopyFrameToHostRgba" in s or "UploadFrame" in s or "MemFree" in s or \
       "BeginDrawing" in s or "EndDrawing" in s:
        return "present"
    if "@plt" in s:
        return "plt"
    if "std::__" in s or "operator" in s:
        return "stl"
    return "other"


def main(path):
    buckets = {}
    total = 0.0
    tops = []
    for line in open(path):
        m = re.match(r"\s*([\d.]+)%\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(.*\S)\s*$", line)
        if not m:
            continue
        pct, comm, pid, tid, dso, sym = float(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)
        total += pct
        b = classify(sym, dso)
        buckets[b] = buckets.get(b, 0.0) + pct
        tops.append((pct, comm, tid, sym[:100]))
    print("FILE " + path + " rows=%d total=%.2f" % (len(tops), total))
    for b, v in sorted(buckets.items(), key=lambda x: -x[1]):
        print("  BUCKET %-16s %6.2f%%" % (b, v))
    return tops


if __name__ == "__main__":
    main(sys.argv[1])
