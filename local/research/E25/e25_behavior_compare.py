"""Field-by-field behaviour compare of E25's regression receipts against E23's.

Same inputs must give same outputs. Two declared free fields are excluded and
NAMED, never silently masked:
  * `ns`   -- the observer's own elapsed-nanosecond counter (wall clock);
  * `eventBytes` -- the byte length of the event text, which embeds the LANE
    directory path, so it moves by the length of `E23` vs `E25` plus scratch.
Everything else -- every counter, every rc, every tap field -- must match, and
any field that does not is listed by name with both values.
"""
from e25_common import *

E23D = E.parent / 'E23'
FREE = {'ns', 'eventBytes'}

def js(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None

sections = []

# --- observer closure footers, all ten ------------------------------------
o23, o25 = js(E23D / 'observer-regression.json'), js(E / 'observer-regression.json')
rows = []
by23 = {Path(c['directory']).parent.name: c['footer'] for c in o23['closures']}
by25 = {Path(c['directory']).parent.name: c['footer'] for c in o25['closures']}
for name in sorted(set(by23) | set(by25)):
    a, b = by23.get(name), by25.get(name)
    if a is None or b is None:
        rows.append(dict(case=name, status='ONE-SIDED', in_e23=a is not None, in_e25=b is not None)); continue
    diff = {k: dict(e23=a.get(k), e25=b.get(k)) for k in sorted(set(a) | set(b))
            if a.get(k) != b.get(k)}
    material = {k: v for k, v in diff.items() if k not in FREE}
    rows.append(dict(case=name, fields=len(set(a) | set(b)),
                     differing=sorted(diff), material_differing=sorted(material),
                     material=material, status='MATCH' if not material else 'DELTA'))
sections.append(dict(section='observer closure footers (10)', rows=rows,
                     free_fields=sorted(FREE),
                     all_match=all(r['status'] == 'MATCH' for r in rows)))

# --- fixture validation receipts: prior / E15 / E16 / absorbed ------------
def fixture_rows(label):
    a, b = js(E23D / f'{label}-validation.json'), js(E / f'{label}-validation.json')
    if not a or not b: return dict(label=label, status='ABSENT', in_e23=bool(a), in_e25=bool(b))
    out = []
    A = {c['mode']: c for c in a['cases']}
    B = {c['mode']: c for c in b['cases']}
    for mode in sorted(set(A) | set(B)):
        x, y = A.get(mode), B.get(mode)
        if not x or not y:
            out.append(dict(mode=mode, status='ONE-SIDED')); continue
        keys = ['rc', 'tap_bytes', 'tap_tail', 'leaf', 'consumer', 'predicate', 'query',
                'drop', 'closure', 'shutdown', 'source_count_match']
        d = {k: dict(e23=x.get(k), e25=y.get(k)) for k in keys if k in x or k in y
             if x.get(k) != y.get(k)}
        out.append(dict(mode=mode, status='MATCH' if not d else 'DELTA', differing=d))
    return dict(label=label, binary_e23=a['binary']['sha256'], binary_e25=b['binary']['sha256'],
                binary_same=a['binary']['sha256'] == b['binary']['sha256'],
                cases=out, all_match=all(r['status'] == 'MATCH' for r in out))

for label in ('checkpoint-bindings', 'checkpoint-closure',
              'observer-bindings', 'observer-closure'):
    sections.append(dict(section=label, **fixture_rows(label)))

# --- absorbed entries (5 presence + 3 ownership) --------------------------
a, b = js(E23D / 'checkpoint-extra-validation.json'), js(E / 'checkpoint-extra-validation.json')
extra = []
if a and b:
    A = {c['mode']: c for c in a['cases']}; B = {c['mode']: c for c in b['cases']}
    for mode in sorted(set(A) | set(B)):
        x, y = A.get(mode), B.get(mode)
        extra.append(dict(mode=mode, status=('MATCH' if x and y and x['rc'] == y['rc'] else 'DELTA'),
                          e23_rc=(x or {}).get('rc'), e25_rc=(y or {}).get('rc')))
sections.append(dict(section='absorbed entries (5 presence + 3 ownership)', rows=extra,
                     all_match=all(r['status'] == 'MATCH' for r in extra)))

ok = all(s.get('all_match') for s in sections)
save('behavior-compare.json', dict(utc=utc(), free_fields=sorted(FREE),
                                   sections=sections, all_sections_match=ok))
for s in sections:
    print(f"{'MATCH' if s.get('all_match') else 'DELTA':<6} {s['section']}")
    for r in s.get('rows', []) + s.get('cases', []):
        key = r.get('case') or r.get('mode')
        if r['status'] != 'MATCH':
            print(f"       {key}: {r.get('material') or r.get('differing') or r['status']}")
        else:
            free = [k for k in r.get('differing', []) if k in FREE]
            print(f"       {key}: MATCH" + (f" (free fields differ: {free})" if free else ''))
print('ALL SECTIONS MATCH:', ok)
print('# E25 BEHAVIOR COMPARE TAIL COMPLETE')
