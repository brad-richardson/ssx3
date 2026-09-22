"""Hex-safe e24->e25 mechanical rename + proof, per errata E23-E1.

E23-E1: a mechanical e22->e23 rename rewrote the substring `e22` INSIDE a hex
digest (ELF_SHA), and the normalized-diff proof was blind to it because it
mapped both tokens to the same placeholder. This tool masks long hex runs
BEFORE renaming, so a digest can never be rewritten, and audits every output
for surviving corruption. Carried from E24 unchanged except for the lane
tokens and one added protected pair (see PROTECTED).
"""
import json, re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
SRC = E.parent / 'E24'
# A run of >=16 hex chars is a digest/FNV/address blob, never a lane token.
HEX = re.compile(r'\b[0-9a-fA-F]{16,}\b')
# Protected tokens: the REUSED instrument owns its interface (E21-spelled by
# necessity; carried verbatim through E22, E23 and E24). Never renamed.
PROTECTED = ['PS2X_E21_PARSER_DIR', 'PS2X_E21_PROOF', '# E21 PARSER CLOSURE',
             'e21-parser-observer.dylib', 'e21_parser_observer.h',
             # The E23 cadence fixture BINARY survived BOTH the host restart and
             # E24 at its E23 path and owns its own footer string. Renaming
             # either would point the lane at a file that does not exist or
             # assert on a footer the binary never prints. Held out, as in E24.
             'e23-fixtures/complete', '# E23 COMPLETE FEED FIXTURE TAIL COMPLETE',
             # E25 ADDS: the E18 fixture binary path and the E18 build tree that
             # E25 rebuilds IN PLACE. Both are E18-spelled by necessity -- the
             # tree path is the one every downstream driver, boot argv and pin
             # names, and the brief requires the EXACT E18 paths. (Neither
             # contains `e24`, so they are protected belt-and-braces, not by
             # need; the assertion below proves the rename is a no-op on them.)
             'e18-fixtures/after', '/tmp/e18-mpeg-link/runtime']


def rename_text(text):
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f'\x00HEX{len(holes)-1}\x00'

    for i, tok in enumerate(PROTECTED):
        text = text.replace(tok, f'\x00PROT{i}\x00')
    text = HEX.sub(stash, text)
    out = text.replace('e24', 'e25').replace('E24', 'E25')
    for i, blob in enumerate(holes):
        out = out.replace(f'\x00HEX{i}\x00', blob)
    for i, tok in enumerate(PROTECTED):
        out = out.replace(f'\x00PROT{i}\x00', tok)
    return out, len(holes)


def normalize(text):
    """Map BOTH lane tokens to one placeholder, with hex runs masked first."""
    text = HEX.sub('\x00HEX\x00', text)
    return text.replace('e24', 'EXX').replace('e25', 'EXX') \
               .replace('E24', 'EXX').replace('E25', 'EXX')


def main():
    names = sys.argv[1:]
    rows = []
    for name in names:
        src = SRC / f'e24_{name}.py'
        dst = E / f'e25_{name}.py'
        text = src.read_text()
        out, masked = rename_text(text)
        dst.write_text(out)
        identical = normalize(text) == normalize(out)
        # Hex audit: every digest-length run in the source must survive byte
        # for byte in the output. This is the check E23-E1 lacked.
        src_hex = HEX.findall(text)
        dst_hex = HEX.findall(out)
        # Protected-token audit: each protected token must appear the SAME
        # number of times before and after. E24 asserted this only implicitly.
        prot = {t: (text.count(t), out.count(t)) for t in PROTECTED if t in text}
        rows.append(dict(name=name, src=str(src), dst=str(dst),
                         src_bytes=len(text.encode()), dst_bytes=len(out.encode()),
                         hex_runs_masked=masked, hex_runs_src=len(src_hex),
                         hex_runs_dst=len(dst_hex),
                         hex_runs_equal=src_hex == dst_hex,
                         protected_counts={k: dict(src=v[0], dst=v[1]) for k, v in prot.items()},
                         protected_preserved=all(a == b for a, b in prot.values()),
                         normalized_diff_empty=identical))
        assert identical, f'normalized diff not empty for {name}'
        assert src_hex == dst_hex, f'HEX CORRUPTION in {name}'
        assert all(a == b for a, b in prot.values()), f'PROTECTED TOKEN LOST in {name}'
    (E / 'rename-proof-hexsafe.json').write_text(json.dumps(dict(
        tool='e25_rename.py', source_lane='E24', protected_tokens=PROTECTED,
        hex_rule='runs of >=16 hex chars masked before rename',
        files=rows, all_normalized_diffs_empty=all(r['normalized_diff_empty'] for r in rows),
        all_hex_runs_equal=all(r['hex_runs_equal'] for r in rows),
        all_protected_preserved=all(r['protected_preserved'] for r in rows)), indent=2) + '\n')
    print(json.dumps(rows, indent=2))
    print('# E25 RENAME TAIL COMPLETE')


if __name__ == '__main__':
    main()
