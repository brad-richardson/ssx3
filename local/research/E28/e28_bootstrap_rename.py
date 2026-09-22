"""E28 bootstrap: carry E26's hex-safe rename tool into this lane, hex-safely.

`e26_rename.py` hardcodes `e26`/`E26` as its DESTINATION token, so it cannot
rename itself into E28. This one-off bootstrap applies E26's OWN algorithm --
its `HEX` regex, its `PROTECTED` list, its masking order -- with the
destination parameterised, to produce `e28_rename.py`. Every other file in the
lane is then carried by that renamed tool, exactly as E26 carried E25's and
E24's.

The bootstrap proves itself two ways and asserts both:
  (1) normalized diff empty + hex runs byte-equal + protected tokens preserved,
      the same three audits E26's tool runs (errata E23-E1);
  (2) FIXPOINT: the file it just produced, loaded and asked to rename
      `e26_rename.py`, returns its own bytes. If the bootstrap had deviated
      from E26's algorithm in any way, this check would fail.
Read-only on the fork. Touches no build, claims no lease, boots nothing.
"""
import importlib.util, json, sys
from pathlib import Path

E = Path(__file__).resolve().parent
SRC = E.parent / 'E26' / 'e26_rename.py'
DST = E / 'e28_rename.py'

spec = importlib.util.spec_from_file_location('e26_rename', SRC)
e26_rename = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e26_rename)
HEX, PROTECTED = e26_rename.HEX, e26_rename.PROTECTED


def rename_text(text, src_lane, dst_lane):
    """E26's rename_text with the destination token parameterised."""
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
out_text, masked = rename_text(src_text, 'E26', 'E28')
DST.write_text(out_text)

src_hex, dst_hex = HEX.findall(src_text), HEX.findall(out_text)
prot = {t: (src_text.count(t), out_text.count(t)) for t in PROTECTED if t in src_text}
normalized_diff_empty = normalize(src_text, 'E26', 'E28') == normalize(out_text, 'E26', 'E28')

# (2) FIXPOINT -- the produced tool reproduces its own bytes from the source.
spec2 = importlib.util.spec_from_file_location('e28_rename', DST)
e28_rename = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(e28_rename)
fixpoint_text, _ = e28_rename.rename_text(src_text, 'E26')
fixpoint = fixpoint_text == out_text
# and the carried destination token really is e28 now
dst_token_is_e28 = ("'e28'" in out_text and "'E28'" in out_text
                    and "'e26'" not in out_text and "'E26'" not in out_text)

row = dict(source_lane='E26', src=str(SRC), dst=str(DST),
           src_bytes=len(src_text.encode()), dst_bytes=len(out_text.encode()),
           hex_runs_masked=masked, hex_runs_src=len(src_hex), hex_runs_dst=len(dst_hex),
           hex_runs_equal=src_hex == dst_hex,
           protected_counts={k: dict(src=v[0], dst=v[1]) for k, v in prot.items()},
           protected_preserved=all(a == b for a, b in prot.values()),
           normalized_diff_empty=normalized_diff_empty,
           fixpoint_reproduces_itself=fixpoint,
           destination_token_carried=dst_token_is_e28)
(E / 'rename-bootstrap.json').write_text(json.dumps(dict(
    tool='e28_bootstrap_rename.py',
    why='e26_rename.py hardcodes its own destination token and cannot rename itself',
    algorithm='E26 rename_text/normalize, imported from e26_rename.py, destination parameterised',
    hex_rule='runs of >=16 hex chars masked before rename',
    protected_tokens=PROTECTED, file=row), indent=2) + '\n')
print(json.dumps({k: v for k, v in row.items() if k != 'protected_counts'}, indent=2))
assert normalized_diff_empty, 'normalized diff not empty'
assert src_hex == dst_hex, 'HEX CORRUPTION'
assert all(a == b for a, b in prot.values()), 'PROTECTED TOKEN LOST'
assert fixpoint, 'FIXPOINT FAILED - bootstrap deviates from E26 algorithm'
assert dst_token_is_e28, 'destination token not carried'
print('# E28 RENAME BOOTSTRAP TAIL COMPLETE')
