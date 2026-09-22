#!/usr/bin/env python3
# G38: first-difference scorer (Mac vs fresh Odin vs committed G31).
import re, hashlib, struct

SSD = "/Volumes/Extreme SSD"
MAC = f"{SSD}/ps2x-g38/g38-mac-stderr.txt"
ODIN = f"{SSD}/ps2x-g38/g38-odin-logcat.txt"
G31 = f"{SSD}/ps2x-g31/g31-logcat.txt"

def strip(lines):
    out = []
    for ln in lines:
        ln = re.sub(r"^\[INFO\]: ", "", ln)
        ln = re.sub(r"^\d\d-\d\d \d\d:\d\d:\d\d\.\d+ +\d+ +\d+ +[IVEW] Granite *: ?", "", ln)
        out.append(ln)
    return out

mac = strip(open(MAC).read().splitlines())
odin = strip(open(ODIN).read().splitlines())
g31 = strip(open(G31).read().splitlines())
print(f"lines mac={len(mac)} odin={len(odin)} g31={len(g31)}")

def sel(lines, *pats):
    return [ln for ln in lines if any(p in ln for p in pats)]

# 1. CPU alignment: fresh Odin vs committed G31 (excision non-perturbation)
for name, pats in [
    ("FRAME", ["G11: FRAME"]), ("RECORD", ["G11: record", "G11:   inst", "G11:   tex"]),
    ("FLUSH", ["G11: flush"]), ("G10", ["G10: pass"]), ("STATE", ["G31: state"]),
    ("BYTES", ["G31: bytes"]), ("VPAGE", ["G30: vpage"]), ("LADDER", ["G29: ladder"]),
    ("VRAM", ["G29: vram"]), ("WROTE", ["G8: wrote"]), ("RUN", ["Running frame"])]:
    a, b = sel(odin, *pats), sel(g31, *pats)
    print(f"odin-vs-g31 {name}: {len(a)}/{len(b)} eq={a == b}")
    if a != b:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print(f"  FIRST-DIFF idx{i}:\n   odin {x}\n   g31  {y}")
                break

# 2. Mac vs Odin CPU alignment (drop scratch/img + timings)
def norm_g10(ln):
    return re.sub(r"scratch=\d+ img=\d+", "scratch=X img=X", ln)
for name, pats, norm in [
    ("FRAME", ["G11: FRAME"], None), ("RECORD", ["G11: record", "G11:   inst"], None),
    ("TEX", ["G11:   tex"], None), ("FLUSH", ["G11: flush"], None),
    ("G10", ["G10: pass"], norm_g10), ("STATE", ["G31: state"], None),
    ("RUN", ["Running frame"], None)]:
    a, b = sel(mac, *pats), sel(odin, *pats)
    if norm:
        a, b = [norm(x) for x in a], [norm(x) for x in b]
    print(f"mac-vs-odin {name}: {len(a)}/{len(b)} eq={a == b}")
    if a != b:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print(f"  FIRST-DIFF idx{i}:\n   mac  {x}\n   odin {y}")
                break
# scratch/img informational
am, ao = sel(mac, "G10: pass"), sel(odin, "G10: pass")
dif = sum(1 for x, y in zip(am, ao) if x != y)
print(f"G10 full-line diffs (incl scratch/img): {dif}/{len(am)}")

# 3. A/B per-seq table
def bytes_map(lines):
    m = {}
    for ln in sel(lines, "G31: bytes"):
        s = int(re.search(r"seq=(\d+)", ln).group(1))
        a = re.search(r"A fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+)", ln)
        b = re.search(r"B fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+)", ln)
        m[s] = (a.groups(), b.groups())
    return m
mm, mo = bytes_map(mac), bytes_map(odin)
LOAD_B = ("eea04488c453e75b", "149721", "0000000000000000")
print("seq | A mac==odin | B mac==load | B odin==load | B mac==odin")
first = None
for s in range(16):
    am_eq = mm[s][0] == mo[s][0]
    bm_load = mm[s][1] == LOAD_B
    bo_load = mo[s][1] == LOAD_B
    bb_eq = mm[s][1] == mo[s][1]
    print(f"{s:3d} | {am_eq!s:11s} | {bm_load!s:11s} | {bo_load!s:12s} | {bb_eq}")
    if not bb_eq and first is None:
        first = s
print(f"FIRST B-DIFFERENCE at seq={first}")
if first is not None:
    print(f"  mac  B fnv={mm[first][1][0]} nz={mm[first][1][1]} head={mm[first][1][2]}")
    print(f"  odin B fnv={mo[first][1][0]} nz={mo[first][1][1]} head={mo[first][1][2]}")
# pass-repeat
for tag, m in (("mac", mm), ("odin", mo)):
    ra = sum(1 for i in range(8) if m[i][0] == m[i + 8][0])
    rb = sum(1 for i in range(8) if m[i][1] == m[i + 8][1])
    print(f"pass-repeat {tag}: A {ra}/8 B {rb}/8")

# 4. ladders + vpage counts
for name, pats in [("LADDER", ["G29: ladder"]), ("VRAM", ["G29: vram"])]:
    print(f"--- {name} mac ---")
    for ln in sel(mac, *pats)[:11]:
        print("  " + ln[:120])
print("--- LADDER odin(first3) ---")
for ln in sel(odin, "G29: ladder")[:3]:
    print("  " + ln[:120])
mv, ov = sel(mac, "G30: vpage"), sel(odin, "G30: vpage")
print(f"vpage counts mac={len(mv)} odin={len(ov)}")
neq = [(i, a, b) for i, (a, b) in enumerate(zip(mv, ov)) if a != b]
print(f"vpage differing lines: {len(neq)}")
pages = sorted(set(int(re.search(r"page=(\d+)", a).group(1)) for _, a, _ in neq))
print(f"differing pages: {pages[:20]}{'...' if len(pages) > 20 else ''} (n={len(pages)})")
