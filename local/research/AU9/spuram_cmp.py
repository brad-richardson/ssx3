# AU9: rebuild our SPU RAM from the SND HLE's dmq-*-spuXXXXXX-N.bin upload dumps (in order) and compare with a PCSX2 SPU RAM dump.
import glob, re, sys
ours = bytearray(2 << 20); spans = []
files = sorted(glob.glob(sys.argv[1] + '/dmq-*.bin'), key=lambda f: int(re.search(r'dmq-(\d+)', f)[1]))
for f in files:
    m = re.search(r'spu([0-9a-f]+)-(\d+)\.bin', f); a = int(m[1], 16); b = open(f, 'rb').read()
    ours[a:a + len(b)] = b; spans.append((a, len(b)))
ref = open(sys.argv[2], 'rb').read()
lo = min(a for a, n in spans); hi = max(a + n for a, n in spans)
print('uploads', len(files), 'span', hex(lo), hex(hi))
# compare only bytes covered by the LAST writer in our dumps (later banks overwrite earlier ones)
cov = bytearray(2 << 20)
for a, n in spans: cov[a:a + n] = b'\1' * n
same = diff = 0; first = None
for i in range(lo, hi):
    if not cov[i]: continue
    if ours[i] == ref[i]: same += 1
    else:
        diff += 1
        if first is None: first = i
print('covered bytes', same + diff, 'equal', same, 'differ', diff, 'first diff', hex(first) if first is not None else None)
