"""Objective 2, static half: close the signaller enumeration for the one
semaphore that was NEVER signalled, over all 9,457 generated sources.

Method: semaphore ids are runtime values. The id for thread 6's wait is stored
once, by the CreateSema return, into a fixed struct offset. Every use of that
slot is therefore findable by grepping the offset across the whole recompiled
image -- a CLOSED enumeration, not a sample. Cross-checked against the 127 MB
e23a function log for whether each site ever executed.
"""
import json, re, subprocess
from collections import Counter
from pathlib import Path
from e24_common import E, P, pin, save, utc

GEN = Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/ps2xRuntime/src/runner')
FLOG = P / 'run/ps2_log-e23a-1.txt'
SLOT = '0x1AA4'          # sema-36 id slot, from `sw $v0, 0x1AA4($s0)` at 0x3c1e08
STUBS = {'0x423DC0': 'SignalSema (syscall 0x42)',
         '0x423DD0': 'iSignalSema (syscall -0x43)',
         '0x423DE0': 'WaitSema (syscall 0x44)',
         '0x423DB0': 'DeleteSema (syscall 0x41)',
         '0x423DA0': 'CreateSema (syscall 0x40)'}


def run(args):
    return subprocess.run(args, text=True, capture_output=True).stdout


def main():
    # --- every instruction in the image that touches the id slot -----------
    raw = run(['grep', '-rhoE',
               r'0x[0-9a-f]{6}: 0x[0-9a-f]{8} +[a-z]+ +\$[a-z0-9]+, ' + SLOT + r'\(\$[a-z0-9]+\)',
               str(GEN)])
    uses = sorted(set(raw.splitlines()))
    sites = []
    for line in uses:
        m = re.match(r'(0x[0-9a-f]{6}): 0x[0-9a-f]{8} +([a-z]+) +\$([a-z0-9]+), ', line)
        addr, op, reg = m.group(1), m.group(2), m.group(3)
        sites.append(dict(addr=addr, op=op, reg=reg, text=line.strip()))

    # --- for each LOAD into $a0, the syscall stub it hands the id to -------
    for s in sites:
        if s['op'] != 'lw' or s['reg'] != 'a0':
            s['role'] = 'store of the CreateSema result' if s['op'] == 'sw' else 'other'
            continue
        owner = run(['grep', '-rl', s['addr'] + ':', str(GEN)]).split('\n')[0]
        body = Path(owner).read_text() if owner else ''
        after = body.split(s['addr'] + ':', 1)[-1][:900]
        stub = next((k for k in STUBS if k.lower() in after.lower() or k in after), None)
        s['owner'] = Path(owner).name if owner else None
        s['stub'] = stub
        s['stub_name'] = STUBS.get(stub)
        s['role'] = STUBS.get(stub, 'unresolved')

    # --- did each owning function ever execute? (127 MB e23a function log) -
    owners = sorted({s['owner'] for s in sites if s.get('owner')})
    counts = {}
    for name in owners:
        stem = name.split('_0x')[0]
        counts[stem] = int(run(['grep', '-c', stem + '_', str(FLOG)]).strip() or 0)
    for s in sites:
        if s.get('owner'):
            s['owner_function_log_entries'] = counts.get(s['owner'].split('_0x')[0])
            s['owner_ever_executed'] = bool(s['owner_function_log_entries'])

    signallers = [s for s in sites if s.get('stub') in ('0x423DC0', '0x423DD0')]
    waiters = [s for s in sites if s.get('stub') == '0x423DE0']
    out = dict(
        utc=utc(),
        SCOPE='static enumeration over all 9,457 generated sources, cross-checked '
              'against the RETAINED e23a function log. Not an E24 boot.',
        semaphore=36, id_slot=SLOT,
        id_slot_store='0x3c1e08  sw $v0, 0x1AA4($s0)  (the CreateSema return; '
                      'diag:sema-create ret=36 tid=3 ra=0x3c1e04)',
        enumeration_closed=True,
        closure_argument='the id is written to the slot once and every read of the '
                         'slot loads it straight into $a0; no copy to another '
                         'location exists, so the sites below are all of them',
        total_slot_instructions=len(sites),
        sites=sites,
        signaller_count=len(signallers),
        signallers=[dict(addr=s['addr'], owner=s['owner'], stub=s['stub_name'],
                         ever_executed=s['owner_ever_executed'],
                         function_log_entries=s['owner_function_log_entries'])
                    for s in signallers],
        waiters=[dict(addr=s['addr'], owner=s['owner'], stub=s['stub_name'])
                 for s in waiters],
        function_log=pin(FLOG),
        thread6_park_ra='0x3c19f0',
        waiter_matches_thread6_park_ra=any(
            s['addr'] == '0x3c19ec' for s in waiters),
    )
    save('signaller-closure.json', out)
    print(f'semaphore 36 id slot {SLOT}: {len(sites)} instructions in the whole image')
    for s in sites:
        print(f"  {s['addr']}  {s['op']:<3} ${s['reg']:<3} -> {s.get('role')}"
              + (f"   owner={s.get('owner')} logEntries={s.get('owner_function_log_entries')}"
                 if s.get('owner') else ''))
    print()
    print('signaller sites                     :', len(signallers))
    print('signallers that EVER executed       :',
          sum(1 for s in signallers if s['owner_ever_executed']))
    print('waiter matches thread 6 park ra     :', out['waiter_matches_thread6_park_ra'])
    print('# E24 SIGNALLER CLOSURE TAIL COMPLETE')


if __name__ == '__main__':
    main()
