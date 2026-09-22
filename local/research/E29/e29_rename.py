"""Hex-safe mechanical rename into E29 + proof, per errata E23-E1.

E23-E1: a mechanical e22->e23 rename rewrote the substring `e22` INSIDE a hex
digest (ELF_SHA), and the normalized-diff proof was blind to it because it
mapped both tokens to the same placeholder. This tool masks long hex runs
BEFORE renaming, so a digest can never be rewritten, and audits every output
for surviving corruption. Carried from E25 unchanged in content.

E29 DIFFERENCE, declared: E29 draws from TWO source lanes, not one. The carried
lane tooling comes from **E25** (the most recent, and the lane that reverted
E24's three suite-presence CHANGE blocks once the suite binary existed again);
the boot driver and its probe gate come from **E24**, because E25 created no
capture driver at all. Each file therefore names its own source lane, and the
normalized-diff proof maps THAT lane's token and `e29` to one placeholder.

Usage: e29_rename.py E25:e25_io.py:e29_io.py E24:e24_capture.py:e29_capture.py ...
"""
import json, re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
# A run of >=16 hex chars is a digest/FNV/address blob, never a lane token.
HEX = re.compile(r'\b[0-9a-fA-F]{16,}\b')
# Protected tokens: the REUSED instrument owns its interface (E21-spelled by
# necessity; carried verbatim through E22, E23, E24 and E25). Never renamed.
PROTECTED = ['PS2X_E21_PARSER_DIR', 'PS2X_E21_PROOF', '# E21 PARSER CLOSURE',
             'e21-parser-observer.dylib', 'e21_parser_observer.h',
             # The E23 cadence fixture BINARY survived the host restart, E24 and
             # E25 at its E23 path and owns its own footer string. Renaming
             # either would point the lane at a file that does not exist or
             # assert on a footer the binary never prints.
             'e23-fixtures/complete', '# E23 COMPLETE FEED FIXTURE TAIL COMPLETE',
             # The E18 fixture binary path and the E18 build tree. Both are
             # E18-spelled by necessity -- the tree path is the one every
             # downstream driver, boot argv and pin names, and it is where E25
             # rebuilt the instrument bit-identically.
             'e18-fixtures/after', '/tmp/e18-mpeg-link/runtime',
             # E29 ADDS: E25's snapshot path, the durable restore E29's
             # Mission 0 falls back to. E25-spelled by necessity -- it is a
             # real path on the SSD, not a lane token.
             'P1/e25-snapshot', 'e18-mpeg-link.tar',
             # E29 ADDS (intentional change 1, recorded in tooling-changes.json):
             # E25's readiness RECEIPT is literally named `e26-readiness.json`
             # -- E25 wrote the readiness for the lane that followed it. It is a
             # REAL PATH on disk, not a lane token, and the e26->e29 rename
             # silently rewrote it to `E25/e29-readiness.json`, which does not
             # exist: `e29_restore_gate.py` would have died on FileNotFoundError
             # at the gate. Exactly the E23-E1 class of bug, one directory over.
             # Protected so the carry points at the file that is actually there.
             'E25/e26-readiness.json']


def rename_text(text, src_lane):
    lo, up = src_lane.lower(), src_lane.upper()
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f'\x00HEX{len(holes)-1}\x00'

    for i, tok in enumerate(PROTECTED):
        text = text.replace(tok, f'\x00PROT{i}\x00')
    text = HEX.sub(stash, text)
    out = text.replace(lo, 'e29').replace(up, 'E29')
    for i, blob in enumerate(holes):
        out = out.replace(f'\x00HEX{i}\x00', blob)
    for i, tok in enumerate(PROTECTED):
        out = out.replace(f'\x00PROT{i}\x00', tok)
    return out, len(holes)


def normalize(text, src_lane):
    """Map BOTH lane tokens to one placeholder, with hex runs masked first."""
    lo, up = src_lane.lower(), src_lane.upper()
    text = HEX.sub('\x00HEX\x00', text)
    return text.replace(lo, 'EXX').replace('e29', 'EXX') \
               .replace(up, 'EXX').replace('E29', 'EXX')


def main():
    rows = []
    for spec in sys.argv[1:]:
        lane, src_name, dst_name = spec.split(':')
        src = E.parent / lane / src_name
        dst = E / dst_name
        text = src.read_text()
        out, masked = rename_text(text, lane)
        dst.write_text(out)
        identical = normalize(text, lane) == normalize(out, lane)
        # Hex audit: every digest-length run in the source must survive byte
        # for byte in the output. This is the check E23-E1 lacked.
        src_hex = HEX.findall(text)
        dst_hex = HEX.findall(out)
        # Protected-token audit: each protected token must appear the SAME
        # number of times before and after.
        prot = {t: (text.count(t), out.count(t)) for t in PROTECTED if t in text}
        rows.append(dict(source_lane=lane, src=str(src), dst=str(dst),
                         src_bytes=len(text.encode()), dst_bytes=len(out.encode()),
                         hex_runs_masked=masked, hex_runs_src=len(src_hex),
                         hex_runs_dst=len(dst_hex),
                         hex_runs_equal=src_hex == dst_hex,
                         protected_counts={k: dict(src=v[0], dst=v[1]) for k, v in prot.items()},
                         protected_preserved=all(a == b for a, b in prot.values()),
                         normalized_diff_empty=identical))
        assert identical, f'normalized diff not empty for {spec}'
        assert src_hex == dst_hex, f'HEX CORRUPTION in {spec}'
        assert all(a == b for a, b in prot.values()), f'PROTECTED TOKEN LOST in {spec}'
    (E / 'rename-proof-hexsafe.json').write_text(json.dumps(dict(
        tool='e29_rename.py', source_lanes=sorted({r['source_lane'] for r in rows}),
        protected_tokens=PROTECTED,
        hex_rule='runs of >=16 hex chars masked before rename',
        files=rows, all_normalized_diffs_empty=all(r['normalized_diff_empty'] for r in rows),
        all_hex_runs_equal=all(r['hex_runs_equal'] for r in rows),
        all_protected_preserved=all(r['protected_preserved'] for r in rows)), indent=2) + '\n')
    print(json.dumps([{k: v for k, v in r.items() if k != 'protected_counts'} for r in rows], indent=2))
    print('# E29 RENAME TAIL COMPLETE')


if __name__ == '__main__':
    main()
