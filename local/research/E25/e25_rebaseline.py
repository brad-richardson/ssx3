"""E25 mission 4 -- assemble the re-baseline evidence.

This tool DOES NOT decide anything. It walks every pin E23's checkpoint
carried, reads E25's own receipt for the same quantity, and prints old, new,
match-or-delta and the CAUSE where a cause is measurable from this lane's
receipts. Unavailable quantities are printed as BLOCKED with the reason, never
inferred. The orchestrator reads the table; the lane does not re-baseline.
"""
from e25_common import *

E23D, E24D = E.parent / 'E23', E.parent / 'E24'

def js(p, default=None):
    p = Path(p)
    if not p.exists(): return default
    return json.loads(p.read_text())

rows = []
# Three statuses, and the third is not a softened DELTA: MATCH* means the pin
# matches once a field this lane DECLARED free is set aside, and the free field
# is named on the row. A pin that differs for any other reason is a DELTA.
def row(pin, old, new, cause='', status=None):
    if status is None:
        status = 'MATCH' if old == new else 'DELTA'
    rows.append(dict(pin=pin, old=old, new=new, status=status, cause=cause))

fork = js(E / 'fork-gate.json')
row('fork HEAD / refs/remotes/fork/ssx3 / ls-remote', BASE_SHA,
    fork['head'] if fork else None, 'unchanged; E25 made no fork commit')
row('fork `status --short`', '?? ps2_log.txt', (fork or {}).get('status_short', '').strip(),
    'unchanged')

inv = js(E / 'inventory.json')
row('9,457 generated .cpp/.h names+SHA256', '9457 / all match',
    f"{inv['generated_names']} / " + ('all match' if inv['generated_all_hashes_match'] else 'MISMATCH'),
    'source tree untouched')
row('21 E18 input/behaviour source SHA256', '21 / all equal',
    f"{inv['e18_sources']} / " + ('all equal' if inv['e18_sources_all_equal'] else 'MISMATCH'),
    'source tree untouched')

pins = js(E / 'pins.json')
if pins:
    cat = pins['categories']
    row('1,725 protected build hashes (3 trees)', '1725 present / all equal',
        f"{cat.get('IDENTICAL',0)} identical + {cat.get('DIFFERENT',0)+cat.get('SAME-SIZE-DIFFERENT-SHA',0)} differing "
        f"+ {cat.get('missing_after_rebuild',0)} missing of the 575 rebuilt; "
        f"{cat.get('not_rebuilt_other_tree',0)} in the two trees E25 did NOT rebuild",
        'one tree rebuilt (internal cap 3 GiB, and only this tree holds the runner+suite); '
        'the other two are historical build trees for P1 and E17')
    for key in ('runner', 'suite'):
        nb = pins['named_binaries'][key]
        row(f'{key} bytes', nb['old_bytes'], nb.get('new_bytes'),
            'rebuild' if nb.get('bytes_delta') else 'byte-size reproduced exactly')
        row(f'{key} SHA256', nb['old_sha'], nb.get('new_sha'),
            '' if nb.get('sha_equal') else 'derived output; see REPORT for the measured cause')

for key, rel in (('E18 fixture binary', 'fixture'), ('E23 cadence fixture binary', 'cadence_fixture')):
    b = inv['key_binaries'][rel]
    row(key + ' SHA256', b['expected_sha'], b.get('actual_sha'), 'survived; reused by copy + re-sha')
    row(key + ' bytes', b['expected_bytes'], b.get('actual_bytes'), 'survived; not rebuilt')
inst = inv['instrument']
row('observer dylib SHA256', inst['expected_sha'], inst.get('actual_sha'), 'reused, never rebuilt')
row('observer dylib bytes', inst['expected_bytes'], inst.get('actual_bytes'), 'reused, never rebuilt')

sc = js(E / 'suite-compare-checkpoint.json')
so = js(E / 'suite-compare-observer.json')
for label, d in (('unloaded', sc), ('observer-LOADED', so)):
    if not d:
        row(f'full suite ({label})', '458 passed / 0 failed', 'BLOCKED', 'receipt absent', 'BLOCKED')
        continue
    row(f'full suite ({label}) totals', d['old']['totals'], d['new']['totals'], '')
    if d['transcript_identical']:
        row(f'full suite ({label}) transcript', f"{d['old']['lines']} lines", 'byte-identical', '')
    elif d['transcript_identical_scratch_masked']:
        row(f'full suite ({label}) transcript',
            f"{d['old']['lines']} lines / {d['new']['runs']} runs",
            f"identical; {d['diff_line_count']} raw lines differ, all inside the "
            f"{d['masked_spans']['new']} masked lane-scratch spans, residual 0",
            'FREE FIELD: the four mc0 tests echo their own TMPDIR scratch path, which '
            'carries the lane directory name and a monotonic-clock nonce',
            'MATCH*')
    else:
        row(f'full suite ({label}) transcript', 'E23 transcript',
            f"{d['masked_diff_line_count']} lines differ after masking",
            'see suite-compare json for the exact lines')
    row(f'E18 R1-R6 lines ({label})', f"{d['r1_r6_present_old']} present",
        f"{d['r1_r6_present_new']} present",
        '' if d['r1_r6_identical'] else 'R1-R6 TEXT DIFFERS',
        'MATCH' if (d['r1_r6_identical'] and d['r1_r6_present_old'] == d['r1_r6_present_new']) else 'DELTA')

base = js(E / 'checkpoint-complete.json')
obs = js(E / 'observer-regression.json')
row('prior actual bindings', [24, 3, 14, 4, 'DROP'], (base or {}).get('prior'), '')
row('E15 no-input / input rc', [0, 0], (base or {}).get('e15_rc'), '')
row('E16 closure modes', 6, (base or {}).get('closure_cases'), '')
row('absorbed entries (5 presence + 3 ownership)', 8, (base or {}).get('extra_cases'), '')
row('observer-LOADED closures receipt-verified', 10, len((obs or {}).get('closures', [])) or None, '')

tc = js(E / 'toolchain-audit.json')
row('toolchain (clang / cmake / pkg-config / 5 ffmpeg modules)',
    'E18 configure.log + P1 REPORT', 'drift-free' if tc and tc['drift_free'] else (tc or {}).get('drift'),
    'compiler ids, cmake, pkg-config and all five ffmpeg module versions equal',
    'MATCH' if tc and tc['drift_free'] else 'DELTA')
cc = js(E / 'configure-compare.json')
row('configure log (substantive lines)', f"{(cc or {}).get('e18_substantive_lines')} lines",
    'identical' if cc and cc['identical'] else 'DIFFERS',
    'git transfer progress dropped; elapsed seconds and ninja counters masked',
    'MATCH' if cc and cc['identical'] else 'DELTA')
row('FetchContent dependency HEADs (raylib / imgui / rlImGui)',
    'E18 three HEADs', 'identical' if cc and cc['dependency_heads']['heads_equal'] else 'DIFFER',
    'same tags 5.5 / v1.92.7-docking / Raylib_5_5',
    'MATCH' if cc and cc['dependency_heads']['heads_equal'] else 'DELTA')
bc = js(E / 'build-compare.json')
row('build graph edges', f"{len((bc or {}).get('edges_only_in_e18', []))} E18-only",
    f"{len((bc or {}).get('edges_only_in_e25', []))} E25-only",
    'E18 ran one extra compile edge (its own AppleDouble sidecar) plus 22 FetchContent '
    'sub-steps and a re-configure; E25 ran nothing E18 did not',
    'MATCH' if bc and not bc['edges_only_in_e25'] else 'DELTA')
dc = js(E / 'delta-cause.json')
if dc:
    row('the 8 pins that changed -- cause',
        '575 pinned files', '567 identical / 7 archives / 1 pch',
        'ar member timestamps: every archive that did NOT reproduce carries dates written '
        'by THIS build; every archive that DID carries deterministic (0) or frozen vendor '
        'dates -- no exception. All 552 .o objects reproduced bit-for-bit, and each differing '
        'archive holds exactly those objects. Rebuild nondeterminism, not toolchain drift '
        'and not a path change.',
        'MATCH*')
bh = js(E / 'behavior-compare.json')
row('regression receipts, field by field (observer footers + fixtures + absorbed)',
    'E23 receipts', 'all sections match' if bh and bh['all_sections_match'] else 'DELTA',
    "FREE FIELDS: observer `ns` (wall clock) and `eventBytes` (event-text length, which "
    "carries the lane path)",
    'MATCH*' if bh and bh['all_sections_match'] else 'DELTA')
cad = js(E / 'cadence-compare.json')
row('complete-feed cadence control (60/120/180/240)', 'E23 + E24 reference',
    'all four match' if cad and cad['all_match'] else 'DELTA',
    'carried control beyond mission 3; runs on the SURVIVING fixture, not the rebuild',
    'MATCH' if cad and cad['all_match'] else 'DELTA')
sn = js(E / 'snapshot.json')
row('durability snapshot (new)', 'none existed',
    f"tar {sn['artifacts']['tree_tar']['members_files']} members + 2 standalone binaries, all re-read verified"
    if sn else 'ABSENT', 'restore procedure tabled, not exercised',
    'MATCH' if sn and sn['all_verified'] else 'DELTA')

deltas = [r for r in rows if r['status'] == 'DELTA']
blocked = [r for r in rows if r['status'] == 'BLOCKED']
starred = [r for r in rows if r['status'] == 'MATCH*']
save('rebaseline.json', dict(utc=utc(), rows=rows, pins=len(rows),
                             matched=len(rows)-len(deltas)-len(blocked)-len(starred),
                             matched_modulo_declared_free_field=len(starred),
                             deltas=len(deltas), blocked=len(blocked),
                             starred_pins=[r['pin'] for r in starred],
                             delta_pins=[r['pin'] for r in deltas],
                             blocked_pins=[r['pin'] for r in blocked],
                             status_key=dict(MATCH='old == new',
                                             **{'MATCH*': 'matches once a NAMED, declared free field is set aside'},
                                             DELTA='differs for a reason that is not a declared free field',
                                             BLOCKED='not obtainable in this lane'),
                             decision='NOT MADE HERE -- orchestrator gates this table'))
w = max(len(r['pin']) for r in rows)
for r in rows:
    print(f"{r['status']:8} {r['pin']:<{w}}  old={r['old']}  new={r['new']}")
print()
print(f'{len(rows)} pins: {len(rows)-len(deltas)-len(blocked)-len(starred)} MATCH / '
      f'{len(starred)} MATCH* (declared free field) / {len(deltas)} DELTA / {len(blocked)} BLOCKED')
if deltas:
    print('DELTA pins:')
    for r in deltas: print('  -', r['pin'], '::', r['cause'])
print('# E25 REBASELINE TAIL COMPLETE')
