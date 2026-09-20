#!/usr/bin/env python3
"""P13 ELF sweep: opcode/field census over SLUS_207.72 executable words.
Read-only. Pure stdlib. Writes receipt files under scratch dir.
Usage: p13_elf_sweep.py <elf> <sweep_csv> <outdir>
"""
import struct, sys, os, csv
from collections import Counter

elf_path, csv_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)

with open(elf_path, 'rb') as f:
    data = f.read()

assert data[:4] == b'\x7fELF', "not ELF"
ei_class, ei_data = data[4], data[5]
le = (ei_data == 1)
end = '<' if le else '>'
is64 = (ei_class == 2)
print(f"class={'64' if is64 else '32'} endian={'LE' if le else 'BE'} size={len(data)}")

if is64:
    e_phoff, e_shoff = struct.unpack(end+'QQ', data[0x20:0x30])
    e_phentsize, e_phnum = struct.unpack(end+'HH', data[0x36:0x3A])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(end+'HHH', data[0x3A:0x40])
else:
    e_phoff = struct.unpack(end+'I', data[0x1C:0x20])[0]
    e_shoff = struct.unpack(end+'I', data[0x20:0x24])[0]
    e_phentsize, e_phnum = struct.unpack(end+'HH', data[0x2A:0x2E])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(end+'HHH', data[0x2E:0x34])

# Program headers: PT_LOAD=1, flags PF_X=1
segs = []
for i in range(e_phnum):
    o = e_phoff + i*e_phentsize
    if is64:
        p_type, p_flags, p_off, p_vaddr, p_filesz, p_memsz = struct.unpack(end+'IIQQQQ', data[o:o+56])
    else:
        # 32-bit order: type,off,vaddr,paddr,filesz,memsz,flags,align
        p_type, p_off, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack(end+'IIIIIIII', data[o:o+32])
    segs.append(dict(type=p_type, flags=p_flags, off=p_off, vaddr=p_vaddr, filesz=p_filesz, memsz=p_memsz))

# Section headers for symtab/reloc/symname census
PT_LOAD = 1
SHT_SYMTAB, SHT_DYNSYM, SHT_REL, SHT_RELA = 2, 11, 9, 4
shnames = []
if e_shnum and e_shoff:
    if is64:
        fmt = end+'IIQQQQIIQQ'
        sz = 64
    else:
        fmt = end+'IIIIIIIIII'
        sz = 40
    strs = None
    if e_shstrndx < e_shnum:
        o = e_shoff + e_shstrndx*sz
        f = struct.unpack(fmt, data[o:o+sz])
        strs = data[f[4 if is64 else 4]:f[4 if is64 else 4]+f[5 if is64 else 5]]
    for i in range(e_shnum):
        o = e_shoff + i*sz
        f = struct.unpack(fmt, data[o:o+sz])
        if is64:
            name, typ, flags, addr, off, size, link, info, align, esz = f
        else:
            name, typ, flags, addr, off, size, link, info, align, esz = f
        nm = ''
        if strs is not None:
            z = strs.find(b'\x00', name)
            nm = strs[name:z].decode('ascii', 'replace')
        shnames.append((nm, typ, flags, addr, off, size))

with open(os.path.join(outdir, 'elf_sections.txt'), 'w') as f:
    f.write(f"phnum={e_phnum} shnum={e_shnum}\n")
    for i, s in enumerate(segs):
        f.write(f"seg{i} type={s['type']} flags={s['flags']} off=0x{s['off']:x} vaddr=0x{s['vaddr']:x} filesz=0x{s['filesz']:x} memsz=0x{s['memsz']:x}\n")
    for nm, typ, flags, addr, off, size in shnames:
        f.write(f"sec name={nm!r} type={typ} flags=0x{flags:x} addr=0x{addr:x} off=0x{off:x} size=0x{size:x}\n")
    symtabs = [n for n in shnames if n[1] in (SHT_SYMTAB, SHT_DYNSYM)]
    relocs = [n for n in shnames if n[1] in (SHT_REL, SHT_RELA)]
    f.write(f"symtab_sections={len(symtabs)} reloc_sections={len(relocs)}\n")

# Executable words from PT_LOAD X segments
words = []  # (vaddr, raw)
for s in segs:
    if s['type'] == PT_LOAD and (s['flags'] & 1):
        for off in range(0, s['filesz'] - 3, 4):
            raw = struct.unpack(end+'I', data[s['off']+off:s['off']+off+4])[0]
            words.append((s['vaddr']+off, raw))

print(f"exec_words={len(words)}")

OP = lambda w: (w >> 26) & 0x3F
RS = lambda w: (w >> 21) & 0x1F
RT = lambda w: (w >> 16) & 0x1F
RD = lambda w: (w >> 11) & 0x1F
SA = lambda w: (w >> 6) & 0x1F
FN = lambda w: w & 0x3F

op_hist = Counter()
cop0_rs = Counter(); cop0_mf_rd = Counter(); cop0_mt_rd = Counter(); cop0_co_fn = Counter()
cop1_fmt = Counter(); cop1_cf_fs = Counter(); cop1_ct_fs = Counter()
cop2_fmt = Counter(); cop2_cfc_rd = Counter(); cop2_ctc_rd = Counter()
regimm_rt = Counter()
mmi_fn = Counter(); mmi0_sa = Counter(); mmi1_sa = Counter(); mmi2_sa = Counter(); mmi3_sa = Counter()
pmfhl_sa = Counter(); pmthl_sa = Counter()
special_fn = Counter()
bc0_count = 0; bc0_rs_detail = Counter()
cache_count = pref_count = sync_count = 0
blez_bgtz = 0
lwl_lwr_ldl_ldr = Counter(); ldc1_lwc2 = Counter(); swl_sdr_sdc1_swc2 = Counter(); ll_sc = Counter()
mfc0_unknown = Counter(); mtc0_unknown = Counter(); mtc0_readonly = Counter()

# Known sets mirror the translator switches
COP0_KNOWN = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31}
# actually translator lists: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19,21,22,23,25,26,27,28,30? check: INDEX0 RANDOM1 ENTRYLO0_2 ENTRYLO1_3 CONTEXT4 PAGEMASK5 WIRED6 ? 7(reserved!) BADVADDR8 COUNT9 ENTRYHI10 COMPARE11 STATUS12 CAUSE13 EPC14 PRID15 CONFIG16 ?17 ?18 ?19 ?20 BADPADDR21 DEBUG22 PERF23 ?24 TAGLO25? ...
# We census raw rd values; classification happens in analysis.
COP0_MF, COP0_MT, COP0_BC, COP0_CO = 0, 4, 8, 16
COP1_MF, COP1_CF, COP1_CT, COP1_MT, COP1_BC, COP1_S, COP1_W = 0, 2, 6, 4, 8, 16, 20
COP2_CFC2, COP2_CTC2 = 2, 6

for va, w in words:
    op = OP(w)
    op_hist[op] += 1
    if op == 0x10:  # COP0
        rs = RS(w); cop0_rs[rs] += 1
        if rs == COP0_MF: cop0_mf_rd[RD(w)] += 1
        elif rs == COP0_MT: cop0_mt_rd[RD(w)] += 1
        elif rs == COP0_CO: cop0_co_fn[FN(w)] += 1
        elif rs == COP0_BC: bc0_count += 1; bc0_rs_detail[RT(w)] += 1
    elif op == 0x11:  # COP1
        rs = RS(w); cop1_fmt[rs] += 1
        if rs == COP1_CF: cop1_cf_fs[RD(w)] += 1
        elif rs == COP1_CT: cop1_ct_fs[RD(w)] += 1
    elif op == 0x12:  # COP2
        rs = RS(w); cop2_fmt[rs] += 1
        # CFC2: rs==2 -> rd selects; CTC2: rs==6
        if rs == 2: cop2_cfc_rd[RD(w)] += 1
        elif rs == 6: cop2_ctc_rd[RD(w)] += 1
    elif op == 0x01:  # REGIMM
        regimm_rt[RT(w)] += 1
    elif op == 0x1C:  # MMI
        fn = FN(w); mmi_fn[fn] += 1
    elif op == 0x00:  # SPECIAL
        special_fn[FN(w)] += 1
    elif op == 0x2F: cache_count += 1   # CACHE
    elif op == 0x33: pref_count += 1    # PREF
    if op in (0x06, 0x07, 0x16, 0x17): blez_bgtz += 1  # BLEZ BGTZ BLEZL BGTZL
    if op in (0x22, 0x26, 0x1A, 0x1B): lwl_lwr_ldl_ldr[op] += 1  # LWL LWR LDL LDR
    if op in (0x35, 0x30): ldc1_lwc2[op] += 1  # LDC1 LWC2
    if op in (0x2A, 0x2E, 0x2B, 0x2C, 0x3D, 0x38, 0x30+0x8 if False else 0x3A): swl_sdr_sdc1_swc2[op] += 1  # SWL SWR SDL SDR SDC1 SWC2
    if op in (0x30, 0x38): pass
    if op in (0x20, 0x38-0x38+0x38): pass
    if op == 0x30: pass  # LL is 0x30? no: LL=0x30, SC=0x38
    if op == 0x38: ll_sc['SC'] += 1
# fix: LL opcode is 0x30, SC is 0x38 (but 0x38 also LWC2? no: LWC2=0x32? verify)
# MIPS: LL=0x30, LWC1=0x31, LWC2=0x32, PREF=0x33, LD=0x37, SC=0x38, SWC1=0x39, SWC2=0x3A, SD=0x3F? no SD=0x3F, SCD...
# Correct mapping: 0x22 LWL,0x26 LWR,0x1A LDL,0x1B LDR,0x35 LDC1,0x36 LDC2,0x32 LWC2,0x2A SWL,0x2E SWR,0x2C SDL,0x2D SDR,0x3D SDC1,0x3E SDC2,0x3A SWC2,0x30 LL,0x38 SC,0x31 LWC1,0x39 SWC1

# Recompute the unlisted-memory-op census with correct opcodes
unlisted = Counter()
for va, w in words:
    op = OP(w)
    if op in (0x22,0x26,0x1A,0x1B,0x35,0x32,0x2A,0x2E,0x2C,0x2D,0x3D,0x3A,0x30,0x38):
        unlisted[op] += 1
# SYNC is SPECIAL function 0x0F
sync_count = special_fn.get(0x0F, 0)

with open(os.path.join(outdir, 'elf_opcode_hist.txt'), 'w') as f:
    f.write(f"exec_words={len(words)}\n")
    for op, c in sorted(op_hist.items()):
        f.write(f"op=0x{op:02x} count={c}\n")

with open(os.path.join(outdir, 'elf_fields.txt'), 'w') as f:
    f.write(f"cop0_rs={dict(sorted(cop0_rs.items()))}\n")
    f.write(f"cop0_mf_rd={dict(sorted(cop0_mf_rd.items()))}\n")
    f.write(f"cop0_mt_rd={dict(sorted(cop0_mt_rd.items()))}\n")
    f.write(f"cop0_co_fn={dict(sorted(cop0_co_fn.items()))}\n")
    f.write(f"bc0_branches={bc0_count} rt_detail={dict(sorted(bc0_rs_detail.items()))}\n")
    f.write(f"cop1_fmt={dict(sorted(cop1_fmt.items()))}\n")
    f.write(f"cop1_cf_fs={dict(sorted(cop1_cf_fs.items()))}\n")
    f.write(f"cop1_ct_fs={dict(sorted(cop1_ct_fs.items()))}\n")
    f.write(f"cop2_fmt={dict(sorted(cop2_fmt.items()))} total_cop2={sum(cop2_fmt.values())}\n")
    f.write(f"cop2_cfc_rd={dict(sorted(cop2_cfc_rd.items()))}\n")
    f.write(f"cop2_ctc_rd={dict(sorted(cop2_ctc_rd.items()))}\n")
    f.write(f"regimm_rt={dict(sorted(regimm_rt.items()))}\n")
    f.write(f"mmi_fn={dict(sorted(mmi_fn.items()))}\n")
    f.write(f"special_fn={dict(sorted(special_fn.items()))}\n")
    f.write(f"cache={cache_count} pref={pref_count} sync={sync_count}\n")
    f.write(f"blez_bgtz_likely={blez_bgtz}\n")
    f.write(f"unlisted_memops_LWL0x22_LWR0x26_LDL0x1a_LDR0x1b_LDC1_0x35_LWC2_0x32_SWL0x2a_SWR0x2e_SDL0x2c_SDR0x2d_SDC1_0x3d_SWC2_0x3a_LL0x30_SC0x38={dict(sorted(unlisted.items()))} total={sum(unlisted.values())}\n")

# MMI subfunction detail: need sa field for MMI0-3 (function 0x08,0x09? MMI_MMI0..3 = ?)
# MMI group: op 0x1C, function field selects; MMI0=0x08? Actually per decoder: mmiFunction==MMI_MMI0 etc.
# Census raw (fn, sa) pairs for op 0x1C
mmi_pairs = Counter()
for va, w in words:
    if OP(w) == 0x1C:
        mmi_pairs[(FN(w), SA(w))] += 1
with open(os.path.join(outdir, 'elf_mmi_pairs.txt'), 'w') as f:
    for (fn, sa), c in sorted(mmi_pairs.items()):
        f.write(f"mmi_fn=0x{fn:02x} sa=0x{sa:02x} count={c}\n")

# Functions ending with a branch (synthetic-delay-slot reachability)
# Branch/jump opcodes with delay slots (approx, opcode-level + SPECIAL JR/JALR + REGIMM branches + COP branches)
def has_delay(op, rs, rt, fn):
    if op in (0x02, 0x03): return True  # J JAL
    if op == 0x00 and fn in (0x08, 0x09): return True  # JR JALR
    if op in (0x04,0x05,0x06,0x07,0x14,0x15,0x16,0x17): return True  # BEQ..BGTZL
    if op == 0x01 and rt in (0x00,0x01,0x02,0x03,0x10,0x11,0x12,0x13): return True  # REGIMM branches
    if op in (0x10,0x11,0x12) and rs == 0x08: return True  # BC0/BC1/BC2
    return False

# Build addr->raw index for exec segments
idx = {va: w for va, w in words}
funcs = []
with open(csv_path) as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            nm = row['Name'] if 'Name' in row else row['name']
            st = int(row['Start'] if 'Start' in row else row['start'], 0)
            en = int(row['End'] if 'End' in row else row['end'], 0)
        except Exception:
            continue
        funcs.append((nm, st, en))

end_branch = 0; end_branch_total = 0; examples = []
no_last_word = 0
for nm, st, en in funcs:
    if en <= st or en - st < 4: continue
    last = en - 4
    if last not in idx:
        no_last_word += 1
        continue
    end_branch_total += 1
    w = idx[last]
    if has_delay(OP(w), RS(w), RT(w), FN(w)):
        end_branch += 1
        if len(examples) < 15:
            examples.append((nm, hex(last), hex(w)))

with open(os.path.join(outdir, 'elf_func_end_branch.txt'), 'w') as f:
    f.write(f"funcs={len(funcs)} with_last_word={end_branch_total} end_in_branch={end_branch} no_last_word={no_last_word}\n")
    for nm, la, w in examples:
        f.write(f"{nm} {la} {w}\n")

# Duplicate real (reliable) names in CSV
def reliable(n):
    if not n: return False
    for p in ('sub_','FUN_','func_','entry_','function_','LAB_'):
        if n.startswith(p): return False
    return any(c.isalpha() for c in n)
from collections import defaultdict
byname = defaultdict(list)
for nm, st, en in funcs:
    if reliable(nm):
        byname[nm].append(st)
dups = {k: v for k, v in byname.items() if len(v) > 1}
with open(os.path.join(outdir, 'csv_dup_names.txt'), 'w') as f:
    f.write(f"reliable_names={len(byname)} dup_names={len(dups)}\n")
    for k in sorted(dups)[:50]:
        f.write(f"{k} addrs={[hex(a) for a in dups[k][:8]]} n={len(dups[k])}\n")

print("done", outdir)
