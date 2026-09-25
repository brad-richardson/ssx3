#!/usr/bin/env python3
"""VB1: top-of-stack PCs from an xctrace time-profile export (GameThread only), bucketed
inside the generated VU1 pair functions by instruction (diagnostic)."""
import re, sys, subprocess, collections
xml = open(sys.argv[1]).read()
binary = sys.argv[2]
frames = {}
for m in re.finditer(r'<frame id="(\d+)" name="([^"]*)" addr="(0x[0-9a-f]+)"', xml):
    frames[m.group(1)] = (m.group(2), int(m.group(3), 16))
bts = {}
rows = re.findall(r'<row>(.*?)</row>', xml, re.S)
top = collections.Counter(); names = collections.Counter(); total = 0
load = int(re.search(r'load-addr="(0x[0-9a-f]+)" path="[^"]*runner', xml).group(1), 16)
slide = load - 0x100000000
threads = {}
for r in rows:
    t = re.search(r'<thread (?:id="(\d+)" fmt="([^"]*)"|ref="(\d+)")', r)
    if t.group(1): threads[t.group(1)] = t.group(2); tname = t.group(2)
    else: tname = threads.get(t.group(3), '')
    if 'GameThread' not in tname and 'Main' not in tname and 'main' not in tname:
        continue
    b = re.search(r'<tagged-backtrace (?:id="(\d+)">(.*?)</tagged-backtrace>|ref="(\d+)"/>)', r, re.S)
    if b.group(1):
        f = re.search(r'<frame (?:id="(\d+)"|ref="(\d+)")', b.group(2))
        fid = f.group(1) or f.group(2); bts[b.group(1)] = fid
    else:
        fid = bts.get(b.group(3))
    if fid is None or fid not in frames: continue
    name, addr = frames[fid]
    total += 1
    names[name.split('(')[0][:60]] += 1
    if 'VU1RecompImage' in name:
        top[(addr - slide) & ~3] += 1
print('GameThread samples', total, 'threads seen', len(threads))
gen = sum(top.values()); print('in pair functions', gen, '%.1f%%' % (100.0 * gen / max(total, 1)))
for n, c in names.most_common(12): print('  %5d %5.1f%%  %s' % (c, 100.0 * c / total, n))
# disassemble the hot PCs
hot = top.most_common(60)
cls = collections.Counter()
lines = []
for pc, c in hot:
    out = subprocess.run(['/opt/homebrew/opt/llvm/bin/llvm-objdump', '-d', '--no-show-raw-insn', '--start-address=0x%x' % pc,
                          '--stop-address=0x%x' % (pc + 4), binary], capture_output=True, text=True).stdout
    ins = [l for l in out.splitlines() if re.match(r'\s+[0-9a-f]+:', l)]
    text = ins[0].split(':', 1)[1].strip() if ins else '?'
    lines.append('%5d  0x%x  %s' % (c, pc, text))
print('top PCs in pair functions (sample lands on the instruction after a slow one):')
print('\n'.join(lines[:40]))
