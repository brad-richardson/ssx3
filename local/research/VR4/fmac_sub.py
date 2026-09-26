import json, re, subprocess, sys, collections
L = '/opt/homebrew/opt/llvm/bin'
obj, sym = sys.argv[1], sys.argv[2]
dis = subprocess.run([L + '/llvm-objdump', '-d', '--no-show-raw-insn', '--disassemble-symbols=' + sym, obj], capture_output=True, text=True).stdout
rows = [(m.group(1), m.group(2)) for m in re.finditer(r'^\s*([0-9a-f]+):\s+(\S+)', dis, re.M)]
out = subprocess.run([L + '/llvm-symbolizer', '--obj=' + obj, '--inlining', '--functions=short', '--output-style=JSON'], input='\n'.join('0x' + a for a, _ in rows), capture_output=True, text=True).stdout
c = collections.Counter(); ln = collections.Counter()
for rec, (a, op) in zip(map(json.loads, out.splitlines()), rows):
    ch = rec['Symbol']; names = [f['FunctionName'] for f in ch]
    if not any(n.startswith('execUpper') for n in names): continue
    i = max(k for k, n in enumerate(names) if n.startswith('execUpper'))
    sub = [n for n in names[:i]][::-1]
    key = sub[0] if sub else 'execUpperImpl'
    if key.startswith('fmacSimd') and len(sub) > 1: key = 'fmacSimd > ' + sub[1]
    c[key] += 1
    if key.startswith('fmacSimd') and len(sub) == 1:
        ln[ch[0]['Line']] += 1
tot = sum(c.values())
for k, v in c.most_common(14): print(f'  {v:5d} {100*v/tot:4.1f}%  {k}')
print('  fmacSimd own lines (ps2_vu1_fmac_simd.h):', ', '.join(f'{l}:{v}' for l, v in sorted(ln.items(), key=lambda x: -x[1])[:14]))
