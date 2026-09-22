"""Hex-safe e23->e24 mechanical rename + proof, per errata E23-E1.

E23-E1: a mechanical e22->e23 rename rewrote the substring `e22` INSIDE a hex
digest (ELF_SHA), and the normalized-diff proof was blind to it because it
mapped both tokens to the same placeholder. This tool masks long hex runs
BEFORE renaming, so a digest can never be rewritten, and audits every output
for surviving corruption.
"""
import json, re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
SRC = E.parent / 'E23'
# A run of >=16 hex chars is a digest/FNV/address blob, never a lane token.
HEX = re.compile(r'\b[0-9a-fA-F]{16,}\b')
# Protected tokens: the REUSED instrument owns its interface (E21-spelled by
# necessity; carried verbatim through E22 and E23). Never renamed.
PROTECTED = ['PS2X_E21_PARSER_DIR', 'PS2X_E21_PROOF', '# E21 PARSER CLOSURE',
             'e21-parser-observer.dylib', 'e21_parser_observer.h',
             # The E23 cadence fixture BINARY survived the host restart at its
             # E23 path and owns its own footer string. Renaming either would
             # point the lane at a file that does not exist or assert on a
             # footer the binary never prints -- the same class of hazard as
             # the E21 dylib's interface. Held out of the rename.
             'e23-fixtures/complete', '# E23 COMPLETE FEED FIXTURE TAIL COMPLETE']


def rename_text(text):
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f'\x00HEX{len(holes)-1}\x00'

    for i, tok in enumerate(PROTECTED):
        text = text.replace(tok, f'\x00PROT{i}\x00')
    text = HEX.sub(stash, text)
    out = text.replace('e23', 'e24').replace('E23', 'E24')
    for i, blob in enumerate(holes):
        out = out.replace(f'\x00HEX{i}\x00', blob)
    for i, tok in enumerate(PROTECTED):
        out = out.replace(f'\x00PROT{i}\x00', tok)
    return out, len(holes)


def normalize(text):
    """Map BOTH lane tokens to one placeholder, with hex runs masked first."""
    text = HEX.sub('\x00HEX\x00', text)
    return text.replace('e23', 'EXX').replace('e24', 'EXX') \
               .replace('E23', 'EXX').replace('E24', 'EXX')


def main():
    names = sys.argv[1:]
    rows = []
    for name in names:
        src = SRC / f'e23_{name}.py'
        dst = E / f'e24_{name}.py'
        text = src.read_text()
        out, masked = rename_text(text)
        dst.write_text(out)
        identical = normalize(text) == normalize(out)
        # Hex audit: every digest-length run in the source must survive byte
        # for byte in the output. This is the check E23-E1 lacked.
        src_hex = HEX.findall(text)
        dst_hex = HEX.findall(out)
        rows.append(dict(name=name, src=str(src), dst=str(dst),
                         src_bytes=len(text.encode()), dst_bytes=len(out.encode()),
                         hex_runs_masked=masked, hex_runs_src=len(src_hex),
                         hex_runs_dst=len(dst_hex),
                         hex_runs_equal=src_hex == dst_hex,
                         normalized_diff_empty=identical))
        assert identical, f'normalized diff not empty for {name}'
        assert src_hex == dst_hex, f'HEX CORRUPTION in {name}'
    (E / 'rename-proof-hexsafe.json').write_text(json.dumps(dict(
        tool='e24_rename.py', protected_tokens=PROTECTED,
        hex_rule='runs of >=16 hex chars masked before rename',
        files=rows, all_normalized_diffs_empty=all(r['normalized_diff_empty'] for r in rows),
        all_hex_runs_equal=all(r['hex_runs_equal'] for r in rows)), indent=2) + '\n')
    print(json.dumps(rows, indent=2))
    print('# E24 RENAME TAIL COMPLETE')


if __name__ == '__main__':
    main()
