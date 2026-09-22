"""The FOUR intentional changes to the renamed boot driver.

(1) a binary-presence gate -- the gate this lane needed and e23a's driver
    lacked: it asserted sizes and hashes but assumed the files existed, and an
    absent protected tree is exactly what stopped E24;
(2) the tiered extended watch set from `watch-set.json` (objective 1a);
(3) PS2X_DIAG_SEMA / _S0, already compiled into the proven runner (objective 2);
(4) span-complete always recorded, so the next lane can refit the cost model.
"""
import json
from pathlib import Path

CHANGES = [
    # (2) the watch set
    ("e24_capture.py",
     """PRODUCER = [0x548800, 0x548804, 0x548808,   # source descriptor head / data / bytes
            0x5487c0,                        # source object passed to 0x3b06b0 / 0x3b06f8
            0x587b28, 0x587b78, 0x587b7c,    # producer block +0x28 sourceObject, +0x78/+0x7c buffers
            0xdc8340]                        # staging buffer AddBs read its 5,040 B from""",
     """# E24 CHANGE 2: the TIERED extended watch set (BOOT-DESIGN.md, watch-set.json).
# E23 watched 8 producer/source words and NAMED the gap: the descriptor head
# advanced 0x548800 = 0x548880 and that successor node was unwatched, so its
# post-park silence was vacuous. This covers the whole descriptor node array,
# both buffers, and the bytes just past the delivered region -- 230 entries
# against e23a's 37, sized by the cost model because diagWatchEmit scans the
# whole vector on EVERY guest store.
_WATCH_SET = json.loads((Path(__file__).resolve().parent / 'watch-set.json').read_text())
PRODUCER = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c]   # carried singles, not in any tier
for _tier in _WATCH_SET['tiers']:
    PRODUCER.extend(_tier['addrs'])
assert len(PRODUCER) == _WATCH_SET['new_entries'] + _WATCH_SET['carried_producer_singles'], len(PRODUCER)"""),

    # (1) the presence gate
    ("e24_capture.py",
     """    record['files'] = []
    for path, size, expected in [""",
     """    # E24 CHANGE 1: PRESENCE first. e23a's driver went straight to .stat() and
    # would raise FileNotFoundError deep inside the loop; E24 opened to exactly
    # that situation (all three protected build trees wiped by a host restart)
    # and a boot driver must refuse it as a named gate, before the lease.
    record['presence'] = {}
    for path in (BIN, TEST, ELF, W / 'P1/SLUS_207.72', W / 'SSX 3 (USA).iso',
                 EVIDENCE / 'parser/e21-parser-observer.dylib'):
        record['presence'][str(path)] = path.exists()
    absent = sorted(k for k, v in record['presence'].items() if not v)
    if absent:
        raise RuntimeError('required binaries absent; E24 tables and stops '
                           'without claiming the lease: ' + '; '.join(absent))
    record['files'] = []
    for path, size, expected in ["""),

    # (3) the semaphore instrument
    ("e24_capture.py",
     """    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
               PS2X_DIAG_SEMA_CREATE='1',""",
     """    # E24 CHANGE 3: PS2X_DIAG_SEMA / _S0 are already compiled into the proven
    # runner (EeScheduler.cpp:156,168) and print nothing when unset, so this
    # needs no rebuild and no fork edit. They are the ONLY source of the waker
    # `ra` per signal -- the always-on park tally records the syscall stub pc
    # (0x423dc8 / 0x423dd8), which cannot name a caller. Objective 2.
    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
               PS2X_DIAG_SEMA='1',PS2X_DIAG_SEMA_S0='1',
               PS2X_DIAG_SEMA_CREATE='1',"""),

    # (4) span-complete always recorded
    ("e24_capture.py",
     """            result['rc']=p.returncode
            result['process_end_utc']=utc()""",
     """            result['rc']=p.returncode
            # E24 CHANGE 4: record span-complete on EVERY path, not only when a
            # bound fires, so the next lane can refit the watch-count cost model
            # in BOOT-DESIGN.md against a third data point.
            result.setdefault('span_complete_s',span_at)
            result['watch_entries']=len(config['watch_addresses'])
            result['process_end_utc']=utc()"""),
]


def main():
    applied = []
    for name, old, new in CHANGES:
        p = Path(name)
        t = p.read_text()
        assert t.count(old) == 1, (name, old[:70], t.count(old))
        p.write_text(t.replace(old, new))
        applied.append(dict(file=name, removed=old, added=new))
    Path('capture-changes.json').write_text(json.dumps(dict(
        note='intentional changes to the renamed boot driver',
        count=len(applied), changes=applied), indent=2) + '\n')
    print(f'applied {len(applied)} capture changes')
    print('# E24 CAPTURE PATCH TAIL COMPLETE')


if __name__ == '__main__':
    main()
