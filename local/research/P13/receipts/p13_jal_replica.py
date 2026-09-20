#!/usr/bin/env python3
"""P13: replicate ScanJalTargetsFallback + CSV merge to explain 316 extensions."""
import struct, csv
elf_path = "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"
csv_path = "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv"
ranges_path = "/Volumes/Extreme SSD/ps2x-p13/output_ranges.txt"
with open(elf_path, 'rb') as f:
    data = f.read()
end = '<'
e_entry = struct.unpack(end+'I', data[0x18:0x1C])[0]
e_shoff = struct.unpack(end+'I', data[0x20:0x24])[0]
e_shentsize, e_shnum, e_shstrndx = struct.unpack(end+'HHH', data[0x2E:0x34])
SHF_EXECINSTR = 0x4
secs = []
for i in range(e_shnum):
    o = e_shoff + i*e_shentsize
    name, typ, flags, addr, off, size, link, info, align, esz = struct.unpack(end+'IIIIIIIIII', data[o:o+40])
    secs.append(dict(flags=flags, addr=addr, off=off, size=size))
def in_code(va):
    for s in secs:
        if (s['flags'] & SHF_EXECINSTR) and s['addr'] <= va < s['addr'] + s['size']:
            return s
    return None
starts = set()
if in_code(e_entry): starts.add(e_entry)
njal_words = 0
for s in secs:
    if not (s['flags'] & SHF_EXECINSTR) or s['size'] < 4: continue
    for off in range(0, s['size'] - 3, 4):
        raw = struct.unpack(end+'I', data[s['off']+off:s['off']+off+4])[0]
        if (raw >> 26) & 0x3F != 0x03: continue
        njal_words += 1
        pc = s['addr'] + off
        tgt = ((pc + 4) & 0xF0000000) | ((raw & 0x03FFFFFF) << 2)
        if in_code(tgt): starts.add(tgt)
print(f"entry=0x{e_entry:x} jal_words={njal_words} jal_starts={len(starts)}")
srt = sorted(starts)
jal_end = {}
for i, st in enumerate(srt):
    sec = in_code(st)
    sec_end = (sec['addr'] + sec['size']) & 0xFFFFFFFF
    e = sec_end
    if i + 1 < len(srt):
        nxt = srt[i+1]
        if nxt > st and nxt < sec_end: e = nxt
    jal_end[st] = e if e > st else st + 4
csv_rows = []
with open(csv_path) as f:
    for row in csv.DictReader(f):
        csv_rows.append((row['name'], int(row['start'], 0), int(row['end'], 0)))
csv_starts = set(s for _, s, _ in csv_rows)
inter = starts & csv_starts
print(f"csv_rows={len(csv_rows)} jal_csv_overlap={len(inter)} pruned_jal={len(starts)-len(inter)}")
# merge rule: same start -> max end (both auto names)
csv_by_start = {}
for nm, s, e in csv_rows:
    if s in csv_by_start:
        print(f"DUP-START {nm} vs {csv_by_start[s]}")
        csv_by_start[s] = (nm, max(e, csv_by_start[s][1]))
    else:
        csv_by_start[s] = (nm, e)
pred_ext = {}
for st in inter:
    je = jal_end[st]
    if je > csv_by_start[st][1]:
        pred_ext[st] = (csv_by_start[st][1], je)
print(f"predicted_extended={len(pred_ext)}")
# observed
import re
obs = {}
pat = re.compile(r'// Address: 0x([0-9a-fA-F]+) - 0x([0-9a-fA-F]+)')
with open(ranges_path) as f:
    for line in f:
        m = pat.search(line)
        if m: obs[int(m.group(1),16)] = int(m.group(2),16)
obs_ext = {s: e for s, e in obs.items() if s in csv_by_start and e > csv_by_start[s][1]}
print(f"observed_extended={len(obs_ext)}")
exact = sum(1 for s in obs_ext if s in pred_ext and pred_ext[s][1] == obs_ext[s])
print(f"exact_match={exact} obs_not_pred={len([s for s in obs_ext if s not in pred_ext])} pred_not_obs={len([s for s in pred_ext if s not in obs_ext])}")
for s in sorted(set(obs_ext) - set(pred_ext))[:10]:
    print(f"  OBS-NOT-PRED {hex(s)} csv_end={hex(csv_by_start[s][1])} obs_end={hex(obs_ext[s])} jal_end={hex(jal_end.get(s,0))}")
for s in sorted(set(pred_ext) - set(obs_ext))[:10]:
    print(f"  PRED-NOT-OBS {hex(s)} csv_end={hex(csv_by_start[s][1])} pred={hex(pred_ext[s][1])} obs={hex(obs.get(s,0))}")
