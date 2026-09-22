"""V1 pin extraction: every Tier-1 pin is a literal verified present in a HEAD blob.

Reads working-tree files (tree is clean at HEAD, verified) and records the
HEAD blob id per source. Fails loudly if any literal is absent.
"""
import json, re, subprocess
from pathlib import Path
from v1_common import E, REPO, run, git_blob_id, utc

HEAD = run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'])['stdout'].strip()
st = run(['git', '-C', str(REPO), 'status', '--short'])['stdout'].strip()
# V1 evidence is new/untracked-ignored; require no MODIFIED tracked files.
modified = [l for l in st.splitlines() if l and l[0] != '?' and not l.startswith('!!')]
assert not modified, modified

def blob_text(relpath):
    r = run(['git', '-C', str(REPO), 'show', f'HEAD:{relpath}'])
    assert r['rc'] == 0, relpath
    return r['stdout']

def check(relpath, *literals):
    text = blob_text(relpath)
    for lit in literals:
        assert lit in text, (relpath, lit[:48])
    return {'path': relpath, 'blob': git_blob_id(REPO, relpath)}

def check_sameline(relpath, *lits):
    """All literals on ONE committed line; returns source with line number."""
    for i, line in enumerate(blob_text(relpath).splitlines(), 1):
        if all(lit in line for lit in lits):
            return {'path': relpath, 'blob': git_blob_id(REPO, relpath), 'line': i}
    raise AssertionError((relpath, lits))

pins = {}
def add(key, sources, **kw):
    pins[key] = dict(sources=sources, **kw)

# --- E25: tar + runner + suite (RESTORE.md + REPORT.md) ---
s_rest = check('local/research/E25/RESTORE.md',
               '9ded806562f1cc150b81040afd24588089fd4bc1f1cbffb7190bc2badb161d10',
               'e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22',
               '2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0',
               '1,762,803,200', '163,529,696', '5,695,128')
add('tar_ssd', [s_rest], bytes=1762803200,
    sha256='9ded806562f1cc150b81040afd24588089fd4bc1f1cbffb7190bc2badb161d10')
RE25 = 'e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22'
SE25 = '2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0'
for k in ('runner_ssd', 'runner_share', 'runner_live'):
    add(k, [s_rest], bytes=163529696, sha256=RE25)
for k in ('suite_ssd', 'suite_share', 'suite_live'):
    add(k, [s_rest], bytes=5695128, sha256=SE25)

# --- Live tree: all 7342 manifest entries ---
man_blob = git_blob_id(REPO, 'local/research/E25/snapshot-manifest.json')
man = json.loads(blob_text('local/research/E25/snapshot-manifest.json'))
assert man['files'] == 7342 and len(man['entries']) == 7342
for row in man['entries']:
    add(f"live/{row['path']}", [{'path': 'local/research/E25/snapshot-manifest.json', 'blob': man_blob}],
        bytes=row['bytes'], sha256=row['sha256'])

# --- G binaries + BuildIDs + dump + scanouts ---
G = {
    33: ('7e0ea8031c6a581fb20b3107b968bcb9a77d3f1c22192621a94aec1b7ee87b00', 265853048,
         '8a89ed2c80eb9fc230404e556203e533930de98e'),
    34: ('2b101ddec1cb27838c57192cf46960ac221eebd4ca8ca7d7e544c691e8dc2586', 265853192,
         'c696a76ab6fa162124da9794d82d2aef0232a7ef'),
    35: ('f3a33f7c51c76c4979ed1cd0f977bd74491be314e9d020d6afd44876c69a41c0', 265853184,
         '132df20bb2c1321cfb9f5e48e0a313b4a03d164b'),
    36: ('4e68911da7b85b6e086cea15987524b3a9ae5aba6e25a63075b8b978b43c49ff', 265853160,
         '384d6429df446fc7d8c245f6b45fa14e8a5bb73f'),
    37: ('97c339552a193ee9c718e8aee34dcf860c6ccf8913f0dc99584bfba73078d1c0', 265853016, None),
}
DUMP = ('154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32', 11537377)
SCAN = {33: '99418f1b1a94ed9ffcfadd6fc0b6573eca5275d6834a3d4cffb64da330233b34',
        34: 'd19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f',
        35: 'd19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f',
        36: 'd19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f',
        37: '34697c14ddac68db3529595d26eb9cf3e51584ae266848379aac22d1d219a276'}
for g, (sha, size, bid) in G.items():
    rp = f'local/research/G{g}/REPORT.md'
    src = check(rp, sha)
    kw = dict(bytes=size, sha256=sha)
    if bid:
        check(rp, bid)
        kw['build_id'] = bid
    add(f'g{g}_bin', [src], **kw)
    # G37 build-id: extract if present
    if g == 37:
        m = re.search(r'build-id \| `([0-9a-f]{40})`', blob_text(rp))
        if m:
            pins[f'g{g}_bin']['build_id'] = m.group(1)
# dump (G35+ pin it; G33/G34 predate the full-sha convention but cite the prefix)
dump_src = [check('local/research/G35/REPORT.md', DUMP[0]),
            check('local/research/G36/REPORT.md', DUMP[0]),
            check('local/research/G37/REPORT.md', DUMP[0])]
add('g13/g13-dump.gs', dump_src, bytes=DUMP[1], sha256=DUMP[0])
# scanout PPMs: 10 per lane, each 688143 B, unanimous per-lane sha
ppms = [f'g13-dump.gs.g10-vsync{i}.ppm' for i in range(8)] + \
       ['g13-dump.gs.g8-first.ppm', 'g13-dump.gs.g8-last.ppm']
for g in (33, 34, 35, 36, 37):
    rp = f'local/research/G{g}/REPORT.md'
    src = check(rp, SCAN[g])  # size 688143 corroborated by G37:503 + unanimous-PPM lines, re-verified by measure
    for n in ppms:
        add(f'g{g}_ssd/{n}', [src], bytes=688143, sha256=SCAN[g])
        add(f'g{g}_share/{n}', [src], bytes=688143, sha256=SCAN[g])

# --- I24: console + RGBA + vector→m2v ---
s_sizes = check('local/research/I24/logs/launch-v3-console.sizes',
                '1806a480504f0063402c75162388a6dd9425288c343adddf0d05ab75d346d4a2')
CON = '1806a480504f0063402c75162388a6dd9425288c343adddf0d05ab75d346d4a2'
for k in ('i24_logs_ssd/launch-v3-console.log', 'i24_logs_share/launch-v3-console.log'):
    add(k, [s_sizes], bytes=17085609, sha256=CON)
s_rgba = check('local/research/I24/logs/v3-rgba-host-fnv.txt',
               '048b41af4c243b82971db805b7f4ef9877fcaf2d8236803479738187c2131a6e')
RGBA = '048b41af4c243b82971db805b7f4ef9877fcaf2d8236803479738187c2131a6e'
for k in ('i24_logs_ssd/v3-rgba-host-7.1.1.bin', 'i24_logs_share/v3-rgba-host-7.1.1.bin',
          'i24_logs_ssd/v3-rgba-device.bin', 'i24_logs_share/v3-rgba-device.bin'):
    add(k, [s_rgba], bytes=917504, sha256=RGBA)
# i24-v3.m2v is a copy of E24's committed vector blob
vec_blob = git_blob_id(REPO, 'local/research/E24/observed/parser-input.bin')
vr = run(['git', '-C', str(REPO), 'cat-file', '-s', f'HEAD:local/research/E24/observed/parser-input.bin'])
vec_size = int(vr['stdout'].strip())
s_vec = check('local/research/I24/REPORT.md', 'cde8a830')
# full vector sha: hash the blob bytes
import hashlib
cp = subprocess.run(['git', '-C', str(REPO), 'show', 'HEAD:local/research/E24/observed/parser-input.bin'],
                    capture_output=True)
vec_sha = hashlib.sha256(cp.stdout).hexdigest()
assert vec_sha.startswith('cde8a830'), vec_sha
add('i24_signed/i24-v3.m2v', [s_vec, {'path': 'local/research/E24/observed/parser-input.bin', 'blob': vec_blob}],
    bytes=vec_size, sha256=vec_sha)

# --- W binary/lib: prefix+tail+size only (never committed in full) ---
s_i24 = check('local/research/I24/REPORT.md', 'edb3eadce3ff9d03...0c60c1', '122,458,696',
              'f356aaa7ddfd9643...2addcd')
add('w_bin', [s_i24], bytes=122458696, sha_prefix='edb3eadce3ff9d03', sha_tail='0c60c1')
s_libsize = check_sameline('local/research/I17/REPORT.md', 'libps2_game_objects.a', '155327984')
add('w_lib', [s_i24, s_libsize], bytes=155327984,
    sha_prefix='f356aaa7ddfd9643', sha_tail='2addcd')

# --- ELF copies: TWO committed candidates (one is a typo; measurement decides) ---
ELF_A = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
ELF_B = '1b49d05ca2793922180851b9e1ce9ae2391d61a7863565ac4e71f12e967af7bc'
s_elf = check('local/research/E21/e21a-preflight.json', ELF_A)
check('local/research/E23/hex-audit.json', ELF_B)
for k in ('p1cd/SLUS_207.72', 'i24_signed/SLUS_207.72'):
    add(k, [s_elf], bytes=3890784, sha256=ELF_A, alt_candidate=ELF_B)

# --- spike ISO + staged ISO (full sha committed; source located below) ---
ISO = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
_iso_hits = [h[5:] if h.startswith('HEAD:') else h for h in
               run(['git', '-C', str(REPO), 'grep', '-l', ISO, 'HEAD', '--', 'local/research'])['stdout'].split()]
assert _iso_hits, 'iso pin source'
s_iso = check(_iso_hits[0], ISO)
for k in ('iso_spike', 'i24_signed/SSX3.iso'):
    add(k, [s_iso], bytes=3005415424, sha256=ISO)

# --- T4: hand-verified (filename -> bytes, sha, source) from committed REPORT lines ---
# Each line read by V1; bytes = the trace's byte count (NOT the line count,
# NOT sha-tail digits). Rotation pairs share bytes by design (pre-tN == t(N-1)).
T_PINS = [
    # (file, bytes, sha, report, line)
    ('emulog-pre-t33-20260921T054304Z.txt', 1706068225,
     '1915aaf93fe11b5db9c2b661665e991aef9304513b069af6fe23d4c7eb5fd6dc', 'T33', 357),
    ('emulog-pre-t34-20260921T062214Z.txt', 2403143826,
     '757497b860cd8100ec9452bb4371b0a67902b9770544ad3eee2867004743af3d', 'T34', 398),
    ('emulog-pre-t35-20260921T065839Z.txt', 2526769871,
     'e7b19750893380b1cbf802cb1011a293ebe4be5da8fbeeed3c370a4bee4d13a9', 'T35', 499),
    ('emulog-pre-t36-20260921T074342Z.txt', 2919779317,
     'e337f8e8304eba0ca963302e0234737e35938ace54a7775417b5bc2dafc60865', 'T36', 561),
    ('emulog-pre-t37-20260921T084313Z.txt', 2885188969,
     'a6f43f21064fe9b5a9ae6e18333af219fb4118fd8495afd046c4beab918142bf', 'T37', 636),
    ('emulog-pre-t38-20260921T094255Z.txt', 2907114770,
     '1ade45733595b77b7e597f87a277be69b7a051e682e648610f1d6418d7da7cc1', 'T38', 647),
    ('emulog-pre-t39-20260921T104301Z.txt', 2903385415,
     '1180c368852527a5ce33201470fb4a656ad320a6a9b3736dbce78283973609a3', 'T39', 701),
    ('emulog-pre-t40-20260921T114358Z.txt', 2898445035,
     '749b8c93dcb961ec047f5e0d506aedf11e92041c9f751a47ab6f3f3be1744249', 'T40', 793),
    ('emulog-pre-t40-20260921T123238Z.txt', 1103446016,
     'b77089b3c6438375c6ab08055cc02b1d76fb1dc9416ce475d115d6540cab22f5', 'T40', 792),
    ('emulog-pre-t41-20260921T135533Z.txt', 1914391860,
     '2452f1dafb512aa0fea486ad5dec7dd34425bb7e54d91a1bb17974a99f9f07e7', 'T41', 955),
    ('emulog-pre-t41-20260921T140920Z.txt', 1913796712,
     'e5f6ef2b7fdb0e864658c172ea42d70cb8ca098e7dc8fc50ba1bfc3e208765df', 'T41', 954),
    ('emulog-pre-t41-20260921T141832Z.txt', 1435642909,
     '98d17eb2caa6191a03366b248935344881eb1b0dbbe7b7abc42cd0e4f96e43ca', 'T41', 953),
    ('emulog-pre-t44-20260922T005924Z.txt', 2679800948,
     '27483c1eb6ba1f1584927d3dc49416e2417a5e611d7882908c9522b299e9445d', 'T45', 431),
    ('emulog-t33r2.txt', 2403143826,
     '757497b860cd8100ec9452bb4371b0a67902b9770544ad3eee2867004743af3d', 'T33', 584),
    ('emulog-t34r1.txt', 2526769871,
     'e7b19750893380b1cbf802cb1011a293ebe4be5da8fbeeed3c370a4bee4d13a9', 'T34', 397),
    ('emulog-t35r1.txt', 2919779317,
     'e337f8e8304eba0ca963302e0234737e35938ace54a7775417b5bc2dafc60865', 'T35', 498),
    ('emulog-t36r1.txt', 2885188969,
     'a6f43f21064fe9b5a9ae6e18333af219fb4118fd8495afd046c4beab918142bf', 'T36', 560),
    ('emulog-t37r1.txt', 2907114770,
     '1ade45733595b77b7e597f87a277be69b7a051e682e648610f1d6418d7da7cc1', 'T37', 635),
    ('emulog-t38r1.txt', 2903385415,
     '1180c368852527a5ce33201470fb4a656ad320a6a9b3736dbce78283973609a3', 'T38', 646),
    ('emulog-t39r1.txt', 2898445035,
     '749b8c93dcb961ec047f5e0d506aedf11e92041c9f751a47ab6f3f3be1744249', 'T39', 700),
    ('emulog-t40r2.txt', 2782052936,
     '6fb03830dfa816abb077cfbacaabd26c6b71444cfafde14ecfd2a9a39fea367c', 'T40', 791),
    ('emulog-t41r4.txt', 2745300674,
     '5b0a734900d41722718155925fecd1deffa879aeb7852cad69c7bcf198853d3f', 'T41', 952),
]
t_pin_files = set()
for f, b, sha, lane, line in T_PINS:
    rp = f'local/research/{lane}/REPORT.md'
    src = dict(check(rp, sha), line=line)
    t_pin_files.add(f)
    for side in ('ssd', 'share'):
        add(f't4_{side}/{f}', [src], bytes=b, sha256=sha)
# --- T4 PARTIAL pins: size + sha prefix/tail on one committed line ---
# (file, bytes, prefix, tail, lane, file-lit, size-lit)
T_PARTIAL = [
    ('emulog-t42r3.txt', 2751948037, '5b23c553', 'd092', 'T42', 'emulog-t42r3.txt', '2751948037'),
    ('emulog-t43r1.txt', 2789610604, 'b8a27b83', 'e82e03', 'T43', 'emulog-t43r1.txt', '2789610604'),
    ('emulog-t27r1.txt', 1194941663, 'dd788742', 'eda4de', 'T27', 'emulog-t27r1.txt', '1,194,941,663'),
    ('emulog-t27r2.txt', 1516867318, '13e41a85', '09dac', 'T27', 'emulog-t27r2.txt', '1,516,867,318'),
    ('emulog-t27r3.txt', 1213776079, '31d8209c', 'e501', 'T27', 'emulog-t27r3.txt', '1,213,776,079'),
    ('emulog-t28r1.txt', 1585843957, '650c0620', '23f57', 'T28', 'emulog-t28r1.txt', '1,585,843,957'),
    ('emulog-t29r1.txt', 1819248014, '77df239e', 'e2171ebd2', 'T29', 'emulog-t29r1.txt', '1,819,248,014'),
    ('emulog-t30r1.txt', 1966668019, '48713961', 'e609e360', 'T30', 'emulog-t30r1.txt', '1,966,668,019'),
    ('emulog-t31r1.txt', 2112217704, '8cbf2827', '896d081e', 'T31', 'emulog-t31r1.txt', '2,112,217,704'),
    ('emulog-t32r1.txt', 2259205200, '7f14d876', 'af9cc3c', 'T32', 'emulog-t32r1.txt', '2,259,205,200'),
    ('emulog-t17c.txt', 540313630, '4f61ea83', '38749', 'T17', 'emulog-t17c.txt', '540,313,630'),
    ('emulog-t19.txt', 555405357, '8882a6bb', 'd0ad6f70', 'T19', 'emulog-t19.txt', '555,405,357'),
    ('emulog-t21.txt', 567984708, 'f4e7e8e1', '200ec7', 'T21', 'emulog-t21.txt', '567,984,708'),
    ('emulog-t23.txt', 589666091, 'd94cef1a', '268f4', 'T23', 'emulog-t23.txt', '589,666,091'),
    ('emulog-t25nvm.txt', 949510490, '59496133', '53de8e', 'T25', 'emulog-t25nvm.txt', '949,510,490'),
    ('emulog-r1a.txt', 991575587, 'b9494f01', 'e21a95', 'R1', 'emulog-r1a.txt', '991,575,587'),
    ('emulog-boot3.txt', 528683584, '2433a33e', '59c6a5', 'T17', 'emulog-boot3.txt', '528,683,584'),
    ('emulog-pre-t17-20260920T151753Z.txt', 125924723, '01f18c93', '94e456', 'T17', 'T151753Z', '125,924,723'),
    ('emulog-pre-t17b-20260920T153248Z.txt', 535682684, 'b754c4db', '1c06f', 'T17', 'T153248Z', '535,682,684'),
    ('emulog-pre-t17c-20260920T153703Z.txt', 223035641, '7dda30fc', '9f0d4b', 'T17', 'T153703Z', '223,035,641'),
    ('emulog-pre-t27-20260920T223824Z.txt', 2482598052, '1ba568cc', 'e15e', 'T27',
     'emulog-pre-t27-20260920T223824Z.txt', '2,482,598,052'),
]
for f, b, pre, tail, lane, flit, slit in T_PARTIAL:
    rp = f'local/research/{lane}/REPORT.md'
    src = check_sameline(rp, flit, slit, pre, tail)
    t_pin_files.add(f)
    for side in ('ssd', 'share'):
        add(f't4_{side}/{f}', [src], bytes=b, sha_prefix=pre, sha_tail=tail)
# pre-t17auto: SIZE-ONLY pin (sha explicitly "not taken")
src_auto = check_sameline('local/research/T17/REPORT.md', 'T152548Z', '117,669,919', 'not taken')
t_pin_files.add('emulog-pre-t17auto-20260920T152548Z.txt')
for side in ('ssd', 'share'):
    add('t4_%s/emulog-pre-t17auto-20260920T152548Z.txt' % side, [src_auto],
        bytes=117669919, size_only=True)
# r1b FULL pin from R1 evidence (REPORT prose `b3ca14e…` drops the leading 3;
# r1b-game.txt + r1b-window.txt carry the full sha — authoritative)
R1B_FULL = '3b3ca14e009c2d6601037b067bea2221219664b57bfe6f4a2cd59b197142e412'
r1b_src = [check('local/research/R1/r1b-game.txt', R1B_FULL),
           check('local/research/R1/r1b-window.txt', R1B_FULL),
           check_sameline('local/research/R1/REPORT.md', 'emulog-r1b.txt', '528,190,303')]
for side in ('ssd', 'share'):
    add(f't4_{side}/emulog-r1b.txt', r1b_src, bytes=528190303, sha256=R1B_FULL)
t_pin_files.add('emulog-r1b.txt')

# share-only variant: size+sha MATCH the live trace per T45:433 (SSD ABSENT);
# the live trace full sha is T45:431, so the variant inherits a FULL pin.
SV_FULL = '27483c1eb6ba1f1584927d3dc49416e2417a5e611d7882908c9522b299e9445d'
sv_src = [check('local/research/T45/REPORT.md', SV_FULL),
          check_sameline('local/research/T45/REPORT.md', 'emulog-t45r2-variant.txt', '2679800948', 'MATCH')]
add('t4_share/emulog-t45r2-variant.txt', sv_src, bytes=2679800948, sha256=SV_FULL)
# T46 trace (streamed mid-V1-pass1, 15:35-15:43Z; FULL pin + committed slices)
T46_FULL = '19c1b583304500581f61db20605befff333d2d262c847a997606cde20364ae84'
t46_src = [check('local/research/T46/REPORT.md', T46_FULL),
           check_sameline('local/research/T46/REPORT.md', 'emulog-t46r3.txt', '2682545633', 'MATCH')]
for side in ('ssd', 'share'):
    add(f't4_{side}/emulog-t46r3.txt', t46_src, bytes=2682545633, sha256=T46_FULL)
t_pin_files.add('emulog-t46r3.txt')
t_pin_files.add('emulog-t45r2-variant.txt')

# --- observer dylib (in-git second copy) + fork/clone HEAD pins ---
obs_blob = git_blob_id(REPO, 'local/research/E25/parser/e21-parser-observer.dylib')
meta = {'head': HEAD,
        'fork_head': {'sha': '3adc0478b6d2260acdd28a249466f2eef9a20176',
                      'src': check('local/research/E25/REPORT.md', '3adc0478b6d2260acdd28a249466f2eef9a20176')},
        'clone_head': {'sha': '3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd',
                       'src': check('local/research/G37/REPORT.md', '3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd')},
        'observer_dylib': {'path': 'local/research/E25/parser/e21-parser-observer.dylib', 'blob': obs_blob},
        't_pin_files': sorted(t_pin_files)}

(E / 'v1_pins.json').write_text(json.dumps(
    {'utc': utc(), 'head': HEAD, 'pins': pins, 'meta': meta}, indent=1) + '\n')
print(f'pins={len(pins)} t_pin_files={len(t_pin_files)} head={HEAD[:12]}')
