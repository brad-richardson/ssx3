"""E29 bootstrap: carry E28's hex-safe rename tool into this lane, hex-safely.

`e28_rename.py` hardcodes `e28`/`E28` as its DESTINATION token, so it cannot
rename itself into E29. This one-off bootstrap applies E28's OWN algorithm --
its `HEX` regex, its `PROTECTED` list, its masking order -- with the
destination parameterised, to produce `e29_rename.py`. Every other file in the
lane is then carried by that renamed tool, exactly as E28 carried E26's and
E26 carried E25's.

Proven two ways, both asserted:
  (1) normalized diff empty + hex runs byte-equal + protected tokens preserved
      (the three audits E28's tool runs; errata E23-E1);
  (2) FIXPOINT: the file it just produced, loaded and asked to rename
      `e28_rename.py`, returns its own bytes.

Read-only on the fork. Touches no build, claims no lease, boots nothing.
"""
import importlib.util, json, sys
from pathlib import Path

E = Path(__file__).resolve().parent
SRC = E.parent / 'E28' / 'e28_rename.py'
DST = E / 'e29_rename.py'

spec = importlib.util.spec_from_file_location('e28_rename', SRC)
e28_rename = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e28_rename)
HEX, PROTECTED = e28_rename.HEX, e28_rename.PROTECTED


def rename_text(text, src_lane, dst_lane):
    """E28's rename_text with the destination token parameterised."""
    lo, up = src_lane.lower(), src_lane.upper()
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f'\x00HEX{len(holes)-1}\x00'

    for i, tok in enumerate(PROTECTED):
        text = text.replace(tok, f'\x00PROT{i}\x00')
    text = HEX.sub(stash, text)
    out = text.replace(lo, dst_lane.lower()).replace(up, dst_lane.upper())
    for i, blob in enumerate(holes):
        out = out.replace(f'\x00HEX{i}\x00', blob)
    for i, tok in enumerate(PROTECTED):
        out = out.replace(f'\x00PROT{i}\x00', tok)
    return out, len(holes)


def normalize(text, src_lane, dst_lane):
    lo, up = src_lane.lower(), src_lane.upper()
    text = HEX.sub('\x00HEX\x00', text)
    return text.replace(lo, 'EXX').replace(dst_lane.lower(), 'EXX') \
               .replace(up, 'EXX').replace(dst_lane.upper(), 'EXX')


src_text = SRC.read_text()
out_text, masked = rename_text(src_text, 'E28', 'E29')
DST.write_text(out_text)

src_hex, dst_hex = HEX.findall(src_text), HEX.findall(out_text)
prot = {t: (src_text.count(t), out_text.count(t)) for t in PROTECTED if t in src_text}
normalized_diff_empty = normalize(src_text, 'E28', 'E29') == normalize(out_text, 'E28', 'E29')

# (2) FIXPOINT -- the produced tool reproduces its own bytes from the source.
spec2 = importlib.util.spec_from_file_location('e29_rename', DST)
e29_rename = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(e29_rename)
fixpoint_text, _ = e29_rename.rename_text(src_text, 'E28')
fixpoint = fixpoint_text == out_text
dst_token_is_e29 = ("'e29'" in out_text and "'E29'" in out_text
                    and "'e28'" not in out_text and "'E28'" not in out_text)

row = dict(source_lane='E28', src=str(SRC), dst=str(DST),
           src_bytes=len(src_text.encode()), dst_bytes=len(out_text.encode()),
           hex_runs_masked=masked, hex_runs_src=len(src_hex), hex_runs_dst=len(dst_hex),
           hex_runs_equal=src_hex == dst_hex,
           protected_counts={k: dict(src=v[0], dst=v[1]) for k, v in prot.items()},
           protected_preserved=all(a == b for a, b in prot.values()),
           normalized_diff_empty=normalized_diff_empty,
           fixpoint=fixpoint, destination_token_is_e29=dst_token_is_e29)
green = all([row['hex_runs_equal'], row['protected_preserved'],
             normalized_diff_empty, fixpoint, dst_token_is_e29])
row['green'] = green
(E / 'rename-bootstrap.json').write_text(json.dumps(row, indent=2) + '\n')
print(json.dumps({k: v for k, v in row.items() if k != 'protected_counts'}, indent=2))
print('# E29 RENAME BOOTSTRAP TAIL COMPLETE green=' + ('1' if green else '0'))
if not green:
    raise SystemExit('BOOTSTRAP RED')
