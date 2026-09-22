import sys, glob
ts = set()
for f in sorted(glob.glob(sys.argv[1])):
    for line in open(f):
        line = line.strip()
        if not line or line.startswith('LAYER') or '\t' not in line:
            continue
        a = line.split('\t')[0]
        try:
            v = int(a)
            if v > 0:
                ts.add(v)
        except ValueError:
            pass
s = sorted(ts)
print(f"files={sys.argv[1]} unique_frames={len(s)}")
if len(s) > 1:
    span = (s[-1]-s[0])/1e9
    print(f"span_s={span:.2f} presents_per_s={len(s)/span:.2f}")
    # thirds
    n = len(s)
    for i, (a, b) in enumerate([(0, n//3), (n//3, 2*n//3), (2*n//3, n-1)]):
        sp = (s[b]-s[a])/1e9
        print(f"third{i}: n={b-a} span={sp:.2f}s rate={(b-a)/sp:.2f}/s")
