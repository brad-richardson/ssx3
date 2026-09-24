#!/usr/bin/env python3
"""N9 Part 2 checker (run from repo root): asserts the APK + live-run receipts.

Checks the package gate/facts, Mac APK double-read, collector pre/post match,
wrapper pins, the single BUILD SUCCESSFUL, run result, PNG decodes + drawn
fractions, hash pins, env restore, no-PS2X_PGS_* env, and the tick-2050 host
hash cross-check vs N8X1's fixed run (fnv1a=4483c15c). Writes
local/research/N9/check-result.json. Verdict A iff every row passes.
"""
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

repo = Path('/Users/brad/dev/ssx3')
lane = repo / 'local/research/N9'
run = Path('/Users/brad/dev/ssx3-work/N9/run')
apk = Path('/Users/brad/dev/ssx3-work/N9/app-release.apk')
rows = []


def row(name, ok, detail=''):
    rows.append({'name': name, 'pass': bool(ok), 'detail': str(detail)[:220]})
    print(('PASS ' if ok else 'FAIL ') + name + (f' :: {detail}' if detail else ''))


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1024 * 1024), b''):
            h.update(c)
    return h.hexdigest()


def png_stats(p):
    d = Path(p).read_bytes()
    w, h = struct.unpack('>II', d[16:24])
    bitd, ctype = d[24], d[25]
    assert bitd == 8 and ctype in (2, 6), f'{p} bitd={bitd} ctype={ctype}'
    ch = 3 if ctype == 2 else 4
    # gather IDAT
    pos, idat = 8, b''
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        if typ == b'IDAT':
            idat += d[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    px = zlib.decompress(idat)
    stride = w * ch
    out = bytearray(len(px) - h)
    for y in range(h):
        f = px[y * (stride + 1)]
        line = bytearray(px[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        prev = out[(y - 1) * stride:y * stride] if y else bytes(stride)
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                p_ = a + b - c
                pa, pb, pc = abs(p_ - a), abs(p_ - b), abs(p_ - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
    n = w * h
    nz = sum(1 for i in range(n) if out[i * ch:i * ch + 3] != b'\0\0\0') / n
    return (w, h), nz


gate = json.loads((lane / 'apk-gate.json').read_text())
row('gate status pass', gate['status'] == 'pass', gate['apk'][0][:12])
facts = json.loads((lane / 'apk-facts.json').read_text())
row('facts status pass + 11 checks', facts['status'] == 'pass' and all(facts['checks'].values()))
r1, r2 = sha_file(apk), sha_file(apk)
row('mac apk double-read == gate sha', [r1, r2] == gate['apk'], r1[:12])
pre = json.loads((lane / 'source-verify-pre.json').read_text().split('== runner')[0])
post = json.loads((lane / 'source-verify-post.json').read_text().split('== runner')[0])
man = json.loads((lane / 'source-manifest.json').read_text())
row('collector pre/post match manifest', pre['status'] == post['status'] == 'match'
    and pre['aggregate_actual'] == man['aggregate_sha256'] == post['aggregate_actual'],
    man['aggregate_sha256'][:12])
wp = (lane / 'wrapper-pins.txt').read_text()
pins = ['a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3',
        '498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17',
        '3d91f0932da99885c41e9dc4e85c9f9a2d3bfef4f0ad87473014dc0827a94884']
row('wrapper pins x2 + props equal', all(wp.count(p) == 2 for p in pins) and 'WRAPPER_PROPS_EQUAL' in wp)
bt = (lane / 'build.txt').read_text()
row('one BUILD SUCCESSFUL, 48 tasks', bt.count('BUILD SUCCESSFUL') == 1 and '48 actionable tasks: 48 executed' in bt)
cg = (lane / 'codegen-graph.txt').read_text()
row('296 unity batches, 9455 codegen cpp', '296' in cg and '9455' in cg and 'no FAILED lines' in cg)
res = json.loads((run / 'result.json').read_text())
row('run result menu+race', res['result'] == 'menu and race captured', res['result'])
row('installed apk == pin', res['hashes']['installed_apk'] == [gate['apk'][0]] * 2)
row('elf+iso pins', res['hashes']['elf'] == ['1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'] * 2
    and res['hashes']['iso'] == ['3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'] * 2)
for name in ('menu', 'race'):
    (w, h), nz = png_stats(run / f'{name}.png')
    row(f'{name}.png 1920x1080 drawn', (w, h) == (1920, 1080) and nz > 0.3, f'{w}x{h} nonblack={nz:.3f}')
row('env restored to orig', res.get('env_restored_sha') == '176eff84eaf8e4f55800362f4827744b5f777ca0e3cbd623d271d4cd97cef32d')
row('no PS2X_PGS_* in run env', 'PGS_' not in (run / 'ps2x.env').read_text())
pid = (run / 'logcat-pid.txt').read_text(errors='replace')
m = re.findall(r'\[frame:dump\] seq=(\d+) tick=(\d+).*?fnv1a=([0-9a-f]+)', pid)
row('3 host dumps, tick2050 fnv=4483c15c (N8X1 x-check)',
    len(m) == 3 and m[2][1] == '2050' and m[2][2] == '4483c15c', str(m))
fatal = [l for l in pid.splitlines() if any(s in l for s in (
    'Turnip dlopen failed', 'Turnip HMI dlsym failed', 'Turnip dladdr(HMI) failed',
    'Turnip HMI layout/open invalid', 'Turnip HAL open failed',
    'Turnip HAL get-proc is null', '[gs:parallel] FATAL:', 'Fatal signal',
    'FATAL EXCEPTION'))]
row('no fatal loader lines (launcher set)', not fatal, fatal[0][-160:] if fatal else '')
verdict = 'A' if all(r['pass'] for r in rows) else 'MISMATCH'
(lane / 'check-result.json').write_text(json.dumps({'verdict': verdict, 'rows': rows}, indent=2) + '\n')
print('VERDICT', verdict)
sys.exit(0 if verdict == 'A' else 1)
