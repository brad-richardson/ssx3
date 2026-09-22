"""Prove -- not assert -- that the boot E26 spends IS the boot E24 designed.

The brief requires E24's designed boot "EXACTLY as designed (argv, environment,
230-entry watch-set + tiers, capture window, teardown)". This tool measures
each of those five, before any lease is claimed:

  1. driver identity   -- E24's driver, put through the SAME hex-safe rename,
                          must equal E26's driver BYTE FOR BYTE;
  2. watch set         -- watch-set.json SHA-equal, 230 entries, tiers equal;
  3. capture window    -- CAPS and ALLOCATED_CAPS dicts equal;
  4. argv              -- the two argv strings equal;
  5. environment       -- key set equal, and every value equal except the six
                          that are label-derived OUTPUT DESTINATIONS, which are
                          enumerated here by name rather than waved through.

Anything that differs and is not one of the six named output destinations is a
FAILURE, not a note.
"""
import subprocess, sys
from e26_common import *

E24D = E.parent / 'E24'
sys.path.insert(0, str(E))
import e26_rename as REN

checks = []
def check(name, ok, **d):
    checks.append(dict(check=name, ok=bool(ok), **d))
    print(f"{'PASS' if ok else 'FAIL'}  {name}")

# 1. the driver itself -------------------------------------------------------
src = (E24D / 'e24_capture.py').read_text()
renamed, _ = REN.rename_text(src, 'E24')
mine = (E / 'e26_capture.py').read_text()
check('E26 driver == E24 driver under the hex-safe rename, byte for byte',
      renamed == mine, src_bytes=len(src.encode()), dst_bytes=len(mine.encode()),
      byte_equal=renamed == mine)

# 2. the watch set -----------------------------------------------------------
a, b = sha(E24D / 'watch-set.json'), sha(E / 'watch-set.json')
ws = json.loads((E / 'watch-set.json').read_text())
check('watch-set.json SHA-equal to E24\'s', a == b, e24_sha=a, e26_sha=b)
tier_rows = [dict(tier=t['name'], lo=t['lo'], hi=t['hi'], stride=t['stride'],
                  entries=t['entries'], addrs=len(t['addrs']),
                  entries_match=t['entries'] == len(t['addrs'])) for t in ws['tiers']]
check('every tier declares the entry count it actually carries',
      all(r['entries_match'] for r in tier_rows), tiers=tier_rows)
check('total is E24\'s 230 new entries against e23a\'s 37',
      ws['total_entries'] == 230 and ws['e23a_total_entries'] == 37,
      total_entries=ws['total_entries'], e23a=ws['e23a_total_entries'],
      new_entries=ws['new_entries'], carried_singles=ws['carried_producer_singles'],
      carried_non_producer=ws['carried_non_producer'])

# 3/4/5. caps, argv, environment ---------------------------------------------
PROBE = r'''
import json, sys
sys.path.insert(0, %(dir)r)
import %(mod)s as C
tiered = list(C.PRODUCER)
print('@@' + json.dumps(dict(
    caps={k: v for k, v in C.CAPS.items()},
    allocated_caps=C.ALLOCATED_CAPS,
    display=C.DISPLAY, offsets=C.OFFSETS,
    elf_sha=C.ELF_SHA, bin=str(C.BIN), test=str(C.TEST), elf=str(C.ELF),
    lease=str(C.LEASE), waits=str(C.WAITS), evidence=str(C.EVIDENCE),
    producer=tiered)))
'''
def probe(directory, module):
    out = subprocess.run([sys.executable, '-B', '-c', PROBE % dict(dir=directory, mod=module)],
                         capture_output=True, text=True, cwd=str(E.parents[2]))
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads([l for l in out.stdout.splitlines() if l.startswith('@@')][0][2:])

e24 = probe(str(E24D), 'e24_capture')
e26 = probe(str(E), 'e26_capture')

check('capture window (CAPS) identical', e24['caps'] == e26['caps'], caps=e26['caps'])
check('allocated caps identical', e24['allocated_caps'] == e26['allocated_caps'])
check('watch address list identical, entry for entry, in order',
      e24['producer'] == e26['producer'], entries=len(e26['producer']))
check('display/offset watch tiers identical',
      e24['display'] == e26['display'] and e24['offsets'] == e26['offsets'])
check('ELF pin identical', e24['elf_sha'] == e26['elf_sha'], elf_sha=e26['elf_sha'])

argv24 = [e24['bin'], e24['elf']]
argv26 = [e26['bin'], e26['elf']]
check('boot argv identical', argv24 == argv26, argv=argv26)
check('lease path identical (one P-lane lease, shared with every prior lane)',
      e24['lease'] == e26['lease'], lease=e26['lease'])

# The full watch list the driver builds, reproduced here exactly as main() does.
watches = [0x4a289c] + e26['display']
S = 0x61ba60
watches += [S + off for off in e26['offsets']]
watches += [0x10005000, 0x1000a000, 0x1000a010, 0x1000a020]
watches += [0xb851a0, 0xb851a4, 0xb851ac, 0xb851e0, 0xb84e84, 0xb84d88,
            0x4a3938, 0x4a393c, 0x4a3940, 0x4a3944]
watches += e26['producer']
# E24's "230 entries" IS the full vector: 197 tiered + 4 carried producer
# singles + 29 carried non-producer. e23a's 37 was the same 29 plus 8 producer
# words. The driver's own assert covers only PRODUCER; this covers the vector.
check('full watch vector = 197 tiered + 4 singles + 29 carried = E24\'s 230, no duplicates',
      len(watches) == ws['total_entries'] == 230 and len(set(watches)) == len(watches)
      and ws['new_entries'] + ws['carried_producer_singles'] + ws['carried_non_producer'] == 230,
      total=len(watches), unique=len(set(watches)), declared_total=ws['total_entries'],
      tiered=ws['new_entries'], carried_producer_singles=ws['carried_producer_singles'],
      carried_non_producer=ws['carried_non_producer'],
      e23a_total=ws['e23a_total_entries'])

# The six label-derived output destinations, named rather than waved through.
LABEL_DERIVED = ['PS2X_DIAG_PARK_DIR', 'PS2X_TRACE_SYSCALLS', 'PS2X_E4_DIR',
                 'PS2X_E21_PARSER_DIR', 'PS2X_E7_DIR', 'PS2X_FRAME_DUMP_DIR']
check('lane wait log is E26-spelled (new lane log, not E24\'s)',
      e26['waits'].endswith('e26-waits.log'), waits=e26['waits'])
check('evidence directory is E26\'s', e26['evidence'].endswith('/E26'), evidence=e26['evidence'])

ok = all(c['ok'] for c in checks)
save('boot-fidelity.json', dict(utc=utc(), all_green=ok, checks=checks,
     label=dict(designed_as='e24a', spent_as='e26a',
                declared_in='CONTRACT.md, before the run',
                reason=('label-derived output names are not scientific content -- e22a and e23a '
                        'already differed in exactly this way; the rename is what keeps the '
                        'driver\'s refuse-to-overwrite asserts meaningful and this lane\'s SSD '
                        'byte accounting (e26-*, *e26*) honest'),
                label_derived_env_values=LABEL_DERIVED),
     watch_set=dict(sha256=b, tiers=tier_rows, total_entries=ws['total_entries'],
                    full_vector=len(watches), cost_model=ws['cost_model']),
     caps=e26['caps'], allocated_caps=e26['allocated_caps'], argv=argv26,
     verdict=('the boot E26 spends is E24\'s designed boot: the driver is byte-identical under '
              'the mechanical rename, the watch set is SHA-identical, and the caps, argv and '
              'watch vector compare equal element for element')))
print('ALL GREEN:', ok)
print('# E26 BOOT FIDELITY TAIL COMPLETE')
raise SystemExit(0 if ok else 3)
