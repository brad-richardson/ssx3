#!/usr/bin/env python3
"""P13 ELF sweep v2: restrict to CSV function ranges (code-only).
Usage: p13_elf_sweep2.py <elf> <sweep_csv> <outdir>
"""
import struct, sys, os, csv
from collections import Counter

elf_path, csv_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
with open(elf_path, 'rb') as f:
    data = f.read()
end = '<'
e_phoff = struct.unpack(end+'I', data[0x1C:0x20])[0]
e_phentsize, e_phnum = struct.unpack(end+'HH', data[0x2A:0x2E])
segs = []
for i in range(e_phnum):
    o = e_phoff + i*e_phentsize
    p_type, p_off, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack(end+'IIIIIIII', data[o:o+32])
    segs.append(dict(type=p_type, flags=p_flags, off=p_off, vaddr=p_vaddr, filesz=p_filesz, memsz=p_memsz))

def read_word(va):
    for s in segs:
        if s['type'] == 1 and s['vaddr'] <= va < s['vaddr'] + s['filesz']:
            o = s['off'] + (va - s['vaddr'])
            return struct.unpack(end+'I', data[o:o+4])[0]
    return None

funcs = []
with open(csv_path) as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            nm = row['name']; st = int(row['start'], 0); en = int(row['end'], 0)
        except Exception:
            continue
        funcs.append((nm, st, en))

OP = lambda w: (w >> 26) & 0x3F
RS = lambda w: (w >> 21) & 0x1F
RT = lambda w: (w >> 16) & 0x1F
RD = lambda w: (w >> 11) & 0x1F
SA = lambda w: (w >> 6) & 0x1F
FN = lambda w: w & 0x3F

code_words = 0
cop0_rs = Counter(); cop0_mf_rd = Counter(); cop0_mt_rd = Counter(); cop0_co_fn = Counter()
cop1_fmt = Counter(); cop1_cf_fs = Counter(); cop1_ct_fs = Counter()
cop2_fmt = Counter(); cop2_cfc_rd = Counter(); cop2_ctc_rd = Counter()
regimm_rt = Counter(); mmi_pairs = Counter(); special_fn = Counter()
bc0 = []; cache = pref = sync = 0; blez = 0
unlisted = Counter(); cop2_total = 0
mfc0_detail = []; mtc0_detail = []
for nm, st, en in funcs:
    a = st
    while a < en:
        w = read_word(a)
        if w is None: break
        code_words += 1
        op = OP(w)
        if op == 0x10:
            rs = RS(w); cop0_rs[rs] += 1
            if rs == 0: cop0_mf_rd[RD(w)] += 1; mfc0_detail.append((a, RD(w)))
            elif rs == 4: cop0_mt_rd[RD(w)] += 1; mtc0_detail.append((a, RD(w)))
            elif rs == 16: cop0_co_fn[FN(w)] += 1
            elif rs == 8: bc0.append((nm, a, w))
        elif op == 0x11:
            rs = RS(w); cop1_fmt[rs] += 1
            if rs == 2: cop1_cf_fs[RD(w)] += 1
            elif rs == 6: cop1_ct_fs[RD(w)] += 1
        elif op == 0x12:
            rs = RS(w); cop2_fmt[rs] += 1; cop2_total += 1
            if rs == 2: cop2_cfc_rd[RD(w)] += 1
            elif rs == 6: cop2_ctc_rd[RD(w)] += 1
        elif op == 0x01: regimm_rt[RT(w)] += 1
        elif op == 0x1C: mmi_pairs[(FN(w), SA(w))] += 1
        elif op == 0x00: special_fn[FN(w)] += 1
        elif op == 0x2F: cache += 1
        elif op == 0x33: pref += 1
        if op in (0x06,0x07,0x16,0x17): blez += 1
        if op in (0x22,0x26,0x1A,0x1B,0x35,0x32,0x2A,0x2E,0x2C,0x2D,0x3D,0x3A,0x30,0x38):
            unlisted[op] += 1
        a += 4
sync = special_fn.get(0x0F, 0)

with open(os.path.join(outdir, 'code_fields.txt'), 'w') as f:
    f.write(f"code_words={code_words} funcs={len(funcs)}\n")
    f.write(f"cop0_rs={dict(sorted(cop0_rs.items()))}\n")
    f.write(f"cop0_mf_rd={dict(sorted(cop0_mf_rd.items()))}\n")
    f.write(f"cop0_mt_rd={dict(sorted(cop0_mt_rd.items()))}\n")
    f.write(f"cop0_co_fn={dict(sorted(cop0_co_fn.items()))}\n")
    f.write(f"bc0_count={len(bc0)}\n")
    for nm, a, w in bc0[:40]:
        f.write(f"  bc0 {nm} 0x{a:x} raw=0x{w:08x} rt={RT(w)}\n")
    f.write(f"cop1_fmt={dict(sorted(cop1_fmt.items()))}\n")
    f.write(f"cop1_cf_fs={dict(sorted(cop1_cf_fs.items()))}\n")
    f.write(f"cop1_ct_fs={dict(sorted(cop1_ct_fs.items()))}\n")
    f.write(f"cop2_total={cop2_total} cop2_fmt={dict(sorted(cop2_fmt.items()))}\n")
    f.write(f"cop2_cfc_rd={dict(sorted(cop2_cfc_rd.items()))}\n")
    f.write(f"cop2_ctc_rd={dict(sorted(cop2_ctc_rd.items()))}\n")
    f.write(f"regimm_rt={dict(sorted(regimm_rt.items()))}\n")
    f.write(f"special_fn={dict(sorted(special_fn.items()))}\n")
    f.write(f"cache={cache} pref={pref} sync={sync} blez_bgtz={blez}\n")
    f.write(f"unlisted_memops={{{', '.join(f'0x{k:02x}:{v}' for k,v in sorted(unlisted.items()))}}} total={sum(unlisted.values())}\n")

with open(os.path.join(outdir, 'code_mmi_pairs.txt'), 'w') as f:
    for (fn, sa), c in sorted(mmi_pairs.items()):
        f.write(f"mmi_fn=0x{fn:02x} sa=0x{sa:02x} count={c}\n")

# The 8 JR-at-end functions: what is the real next word?
def has_delay(op, rs, rt, fn):
    if op in (0x02, 0x03): return True
    if op == 0x00 and fn in (0x08, 0x09): return True
    if op in (0x04,0x05,0x06,0x07,0x14,0x15,0x16,0x17): return True
    if op == 0x01 and rt in (0x00,0x01,0x02,0x03,0x10,0x11,0x12,0x13): return True
    if op in (0x10,0x11,0x12) and rs == 0x08: return True
    return False
with open(os.path.join(outdir, 'func_end_detail.txt'), 'w') as f:
    n = 0
    for nm, st, en in funcs:
        if en <= st: continue
        w = read_word(en-4)
        if w is None: continue
        if has_delay(OP(w), RS(w), RT(w), FN(w)):
            nxt = read_word(en)
            nxt2 = read_word(en+4)
            f.write(f"{nm} last=0x{en-4:x} raw=0x{w:08x} next=0x{en:x} raw={('0x%08x'%nxt) if nxt is not None else None} next2={('0x%08x'%nxt2) if nxt2 is not None else None}\n")
            n += 1
    f.write(f"total_end_in_branch={n}\n")
print("done", outdir, "code_words=", code_words)
