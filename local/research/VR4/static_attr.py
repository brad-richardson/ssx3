import json, re, subprocess, sys, collections
sys.path.insert(0, '/Users/brad/dev/ssx3/local/research/VR4')
import regions as R
L = '/opt/homebrew/opt/llvm/bin'
obj, sym = sys.argv[1], sys.argv[2]
dis = subprocess.run([L + '/llvm-objdump', '-d', '--no-show-raw-insn', '--disassemble-symbols=' + sym, obj], capture_output=True, text=True).stdout
addrs = [m.group(1) for m in re.finditer(r'^\s*([0-9a-f]+):\s+\S', dis, re.M)]
out = subprocess.run([L + '/llvm-symbolizer', '--obj=' + obj, '--inlining', '--functions=short', '--output-style=JSON'], input='\n'.join('0x' + a for a in addrs), capture_output=True, text=True).stdout
c = collections.Counter()
for rec in map(json.loads, out.splitlines()):
    ch = rec['Symbol']; names = [f['FunctionName'] for f in ch]
    if any(n.startswith('execUpper') for n in names): k = 'FMAC/upper core'
    elif any(n.startswith('execLower') for n in names): k = 'lower exec'
    else:
        r = R.region(ch); k = r.split(' > ')[0]
        if k.startswith('glue') or k.startswith('issuePair:'): k = 'glue/other'
    c[k] += 1
n = len(addrs)
print(f'{sym[-50:]}: {n} insns ' + ', '.join(f'{k} {v} ({100*v/n:.0f}%)' for k, v in c.most_common()))
