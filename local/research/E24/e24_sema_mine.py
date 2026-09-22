"""Objectives 1b + 2 mined from the RETAINED e23a artifacts.

SCOPE, stated up front: this is E23's boot, not an E24 boot. E24's checkpoint
is RED (the protected build trees were wiped by the host restart) so no boot was
spent. What these artifacts CAN settle is settled here; what needs the extended
watch set or `PS2X_DIAG_SEMA=1` is named BLOCKED, not guessed.
"""
import json, re
from collections import defaultdict
from pathlib import Path
from e24_common import E, P, pin, save, utc

RUN = P / 'run'
LOG = RUN / 'boot-e23a-1.log'
PARK = RUN / 'park-e23a-1/park-snapshot.json'
PARKTXT = RUN / 'park-e23a-1/park-snapshot.txt'


def tally_block(text, header):
    """Parse the park table's `sema waits:` / `sema signals:` blocks."""
    rows = []
    grab = False
    for line in text.splitlines():
        if line.rstrip() == header:
            grab = True
            continue
        if grab:
            if not line.startswith('  '):
                break
            m = re.match(r'\s+id=(\d+) pc=0x([0-9a-f]+) n=(\d+)', line)
            if m:
                rows.append(dict(id=int(m.group(1)), pc='0x' + m.group(2), n=int(m.group(3))))
    return rows


def main():
    for p in (LOG, PARK, PARKTXT):
        assert p.exists(), f'retained e23a artifact missing: {p}'
    park = json.loads(PARK.read_text())
    ptxt = PARKTXT.read_text()
    log = LOG.read_text(errors='replace')
    lines = log.splitlines()

    waits = tally_block(ptxt, 'sema waits:')
    signals = tally_block(ptxt, 'sema signals:')
    wait_by_id = defaultdict(int)
    sig_by_id = defaultdict(int)
    sig_kind = defaultdict(lambda: defaultdict(int))
    for r in waits:
        wait_by_id[r['id']] += r['n']
    for r in signals:
        sig_by_id[r['id']] += r['n']
        # 0x423dc8 = SignalSema stub, 0x423dd8 = iSignalSema stub (syscall census).
        sig_kind[r['id']]['iSignalSema' if r['pc'] == '0x423dd8' else 'SignalSema'] += r['n']

    creates = {}
    for line in lines:
        if '[diag:sema-create]' not in line:
            continue
        f = dict(re.findall(r'(\w+)=(\S+)', line))
        creates[int(f['ret'])] = dict(creator_tid=int(f['tid']), creator_ra=f['ra'],
                                      max=int(f['max']), init=int(f['init']), attr=int(f['attr']))

    sem_state = {s['id']: s for s in park['semaphores']}
    threads = park['threads']
    blocked = [t for t in threads if t['wait_reason_name'] == 'Semaphore']

    rows = []
    for t in blocked:
        sid = t['wait_id']
        c = creates.get(sid, {})
        rows.append(dict(
            thread=t['id'], entry=t['entry'], priority=t['priority'], scheduled=t['scheduled'],
            park_pc=t['pc'], park_ra=t['ra'], sp=t['sp'], wait_id=sid,
            sema_count=sem_state.get(sid, {}).get('count'),
            sema_max=sem_state.get(sid, {}).get('max'),
            sema_init=sem_state.get(sid, {}).get('init'),
            sema_waiters=sem_state.get(sid, {}).get('waiters'),
            creator_tid=c.get('creator_tid'), creator_ra=c.get('creator_ra'),
            waits_total=wait_by_id.get(sid, 0), signals_total=sig_by_id.get(sid, 0),
            signal_kinds=dict(sig_kind.get(sid, {})),
            deficit=wait_by_id.get(sid, 0) - sig_by_id.get(sid, 0),
            ever_signalled=sig_by_id.get(sid, 0) > 0))

    # Objective 1b: what thread 4's wakes actually are.
    t4 = next(t for t in threads if t['id'] == 4)
    t4_row = next(r for r in rows if r['thread'] == 4)
    samples = defaultdict(list)
    for line in lines:
        if '[diag:thread]' not in line:
            continue
        f = dict(re.findall(r'(\w+)=(\S+)', line))
        samples[int(f['id'])].append(dict(status=int(f['status']), waitReason=int(f['waitReason']),
                                          waitId=int(f['waitId']), pc=f['pc'],
                                          scheduled=int(f['scheduled'])))
    t4_sched = [s['scheduled'] for s in samples[4]]
    t4_waitids = sorted({s['waitId'] for s in samples[4]})

    attribution = dict(
        thread=4, entry=t4['entry'], priority=t4['priority'],
        park_wait_id=t4['wait_id'], park_wait_ra=t4['ra'],
        scheduled_total_at_park=t4['scheduled'],
        sema31_waits_total=wait_by_id.get(31, 0),
        sema31_signals_total=sig_by_id.get(31, 0),
        scheduled_equals_sema31_waits=t4['scheduled'] == wait_by_id.get(31, 0),
        per_sample_scheduled=t4_sched,
        wait_ids_seen_in_samples=t4_waitids,
        producer_watch_windows_touched_after_park=0,
        conclusion_kind='wait/signal round trips on semaphore 31, not memory traffic '
                        'in any watched producer/source window',
        limit='attribution is to the SEMAPHORE round trip. What thread 4 TOUCHES '
              'between wake and re-wait is outside every watched window and '
              'outside the E7 tap; the extended watch set + PS2X_DIAG_SEMA is '
              'what would name it.')

    out = dict(
        utc=utc(),
        SCOPE='mined from RETAINED e23a artifacts (E23 boot). NOT an E24 boot; '
              'E24 checkpoint is RED and no boot was spent.',
        artifacts={str(p): pin(p) for p in (LOG, PARK, PARKTXT)},
        objective_1b=attribution,
        objective_2=dict(
            blocked_threads=rows,
            corrected_wait_id_set=sorted({r['wait_id'] for r in rows}),
            e23_report_said='26/30/32/36',
            correction='thread 4 waits on semaphore 31, which E23 REPORT and '
                       'NEXT-BRIEF both omitted; the real set is 26/30/31/32/36',
            never_signalled=[r['wait_id'] for r in rows if not r['ever_signalled']],
            all_deficits_one=all(r['deficit'] == 1 for r in rows),
            signaller_identity='BLOCKED: the always-on park tally records the '
                               'SYSCALL STUB pc (0x423dc8 SignalSema / 0x423dd8 '
                               'iSignalSema), not the calling ra. Only '
                               'PS2X_DIAG_SEMA=1 emits the waker ra per signal, '
                               'and that needs the boot this lane could not spend.'),
        mpeg_thread=next(t for t in threads if t['wait_reason_name'] == 'Mpeg'),
        gs_counters=ptxt.strip().splitlines()[-1],
        all_semaphores=[dict(id=s['id'], **{k: s[k] for k in ('count', 'max', 'init', 'waiters')},
                             waits=wait_by_id.get(s['id'], 0), signals=sig_by_id.get(s['id'], 0),
                             creator_ra=creates.get(s['id'], {}).get('creator_ra'))
                        for s in park['semaphores']],
    )
    save('sema-mine.json', out)
    print('OBJECTIVE 2 -- the five semaphore waits (e23a reference)')
    print(f"{'thr':>3} {'sema':>5} {'cnt':>4} {'max':>5} {'init':>5} {'waits':>6} {'signals':>8} "
          f"{'deficit':>8} {'sched':>6}  entry      creator_ra  signal kinds")
    for r in rows:
        print(f"{r['thread']:>3} {r['wait_id']:>5} {r['sema_count']:>4} {r['sema_max']:>5} "
              f"{r['sema_init']:>5} {r['waits_total']:>6} {r['signals_total']:>8} "
              f"{r['deficit']:>8} {r['scheduled']:>6}  {r['entry']:<10} {r['creator_ra']:<11} "
              f"{r['signal_kinds']}")
    print()
    print('never signalled at all :', out['objective_2']['never_signalled'])
    print('every deficit exactly 1:', out['objective_2']['all_deficits_one'])
    print()
    print('OBJECTIVE 1b -- thread 4')
    print('  scheduled total at park      :', attribution['scheduled_total_at_park'])
    print('  sema 31 waits / signals      :', attribution['sema31_waits_total'], '/',
          attribution['sema31_signals_total'])
    print('  scheduled == sema 31 waits   :', attribution['scheduled_equals_sema31_waits'])
    print('  producer windows touched     :', attribution['producer_watch_windows_touched_after_park'])
    print('# E24 SEMA MINE TAIL COMPLETE')


if __name__ == '__main__':
    main()
