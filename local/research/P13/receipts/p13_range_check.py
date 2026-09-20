#!/usr/bin/env python3
"""P13 output-vs-CSV range conformance + overlap + end-in-branch census."""
import struct, sys, csv, re
elf_path, csv_path, ranges_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(elf_path, 'rb') as f:
    data = f.read()
end = '<'
e_phoff = struct.unpack(end+'I', data[0x1C:0x20])[0]
e_phentsize, e_phnum = struct.unpack(end+'HH', data[0x2A:0x2E])
segs = []
for i in range(e_phnum):
    o = e_phoff + i*e_phentsize
    p_type, p_off, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack(end+'IIIIIIII', data[o:o+32])
    segs.append((p_type, p_off, p_vaddr, p_filesz))
def rw(va):
    for t, off, va0, fz in segs:
        if t == 1 and va0 <= va < va0 + fz:
            return struct.unpack(end+'I', data[off+(va-va0):off+(va-va0)+4])[0]
    return None
OP = lambda w: (w >> 26) & 0x3F
RS = lambda w: (w >> 21) & 0x1F
RT = lambda w: (w >> 16) & 0x1F
FN = lambda w: w & 0x3F
def has_delay(w):
    op, rs, rt, fn = OP(w), RS(w), RT(w), FN(w)
    if op in (0x02, 0x03): return True
    if op == 0x00 and fn in (0x08, 0x09): return True
    if op in (0x04,0x05,0x06,0x07,0x14,0x15,0x16,0x17): return True
    if op == 0x01 and rt in (0x00,0x01,0x02,0x03,0x10,0x11,0x12,0x13): return True
    if op in (0x10,0x11,0x12) and rs == 0x08: return True
    return False

csv_by_start = {}
with open(csv_path) as f:
    for row in csv.DictReader(f):
        try:
            csv_by_start[int(row['start'], 0)] = (row['name'], int(row['end'], 0))
        except Exception:
            pass
out = []
pat = re.compile(r'// Address: 0x([0-9a-fA-F]+) - 0x([0-9a-fA-F]+)')
with open(ranges_path) as f:
    for line in f:
        m = pat.search(line)
        if m:
            out.append((int(m.group(1), 16), int(m.group(2), 16)))
out.sort()
print(f"output_funcs={len(out)} csv_rows={len(csv_by_start)}")
# conformance
match = ext = shrink = nocsv = 0
ext_ex = []
for s, e in out:
    if s not in csv_by_start:
        nocsv += 1
        continue
    nm, ce = csv_by_start[s]
    if e == ce: match += 1
    elif e > ce:
        ext += 1
        if len(ext_ex) < 12: ext_ex.append((nm, hex(s), hex(ce), hex(e)))
    else:
        shrink += 1
print(f"match={match} extended={ext} shrunk={shrink} no_csv_row={nocsv}")
for x in ext_ex: print("  EXT", x)
# overlaps among output ranges
ov = 0; ov_ex = []
for i in range(len(out)-1):
    if out[i][1] > out[i+1][0]:
        ov += 1
        if len(ov_ex) < 12: ov_ex.append((hex(out[i][0]), hex(out[i][1]), hex(out[i+1][0]), hex(out[i+1][1])))
print(f"overlapping_adjacent_pairs={ov}")
for x in ov_ex: print("  OV", x)
# end-in-branch over OUTPUT ranges (= synthetic delay slot used)
eb = 0; eb_ex = []
for s, e in out:
    if e <= s: continue
    w = rw(e-4)
    if w is not None and has_delay(w):
        eb += 1
        if len(eb_ex) < 20: eb_ex.append((hex(s), hex(e-4), hex(w)))
print(f"output_end_in_branch={eb}")
for x in eb_ex: print("  EB", x)
# end-in-branch over CSV ranges (fork csv)
ceb = 0
for s, (nm, ce) in csv_by_start.items():
    if ce <= s: continue
    w = rw(ce-4)
    if w is not None and has_delay(w):
        ceb += 1
print(f"csv_end_in_branch={ceb}")
