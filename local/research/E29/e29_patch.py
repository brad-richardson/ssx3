"""E29's intentional tooling changes, applied idempotently and recorded as data.

Every change is a literal before/after pair. Running this tool twice is a no-op
on the second run (each pair asserts either the BEFORE or the AFTER is present,
never neither). Full diffs land in `tooling-diff.md`, the data in
`tooling-changes.json`.

E29 has TWO changes and no others. The CAPTURE DRIVER ITSELF IS NOT ONE OF
THEM: `e29_capture.py` is byte-identical to E26's under the hex-safe rename,
because the watch set lives in `watch-set.json`, which the driver loads.
"""
import difflib
from e29_common import *

CHANGES = [
    dict(
        file='e29_rename.py',
        name="CHANGE 1 -- protect E25's readiness receipt from the lane rename",
        why=("E25 named its readiness receipt `e26-readiness.json` -- it wrote the readiness for "
             "the lane that followed it. That is a REAL PATH on disk, not a lane token, and the "
             "mechanical e26->e29 carry rewrote `e29_restore_gate.py`'s reference to "
             "`E25/e29-readiness.json`, which does not exist: the Mission 0 restore gate would "
             "have died on FileNotFoundError. This is exactly the errata E23-E1 class of bug one "
             "directory over -- the rename proof is blind to it, because the normalized diff maps "
             "both lane tokens to one placeholder and the file is SUPPOSED to change there. The "
             "token is added to PROTECTED, and `e29_carry_audit.py` now resolves EVERY cross-lane "
             "path literal in every carried tool so the class is caught, not just this instance."),
        pairs=[("             'P1/e25-snapshot', 'e18-mpeg-link.tar']\n",
                "             'P1/e25-snapshot', 'e18-mpeg-link.tar',\n"
                "             # E29 ADDS (intentional change 1, recorded in tooling-changes.json):\n"
                "             # E25's readiness RECEIPT is literally named `e26-readiness.json`\n"
                "             # -- E25 wrote the readiness for the lane that followed it. It is a\n"
                "             # REAL PATH on disk, not a lane token, and the e26->e29 rename\n"
                "             # silently rewrote it to `E25/e29-readiness.json`, which does not\n"
                "             # exist: `e29_restore_gate.py` would have died on FileNotFoundError\n"
                "             # at the gate. Exactly the E23-E1 class of bug, one directory over.\n"
                "             # Protected so the carry points at the file that is actually there.\n"
                "             'E25/e26-readiness.json']\n")],
    ),
    dict(
        file='e29_boot_fidelity.py',
        name='CHANGE 2 -- the watch set is the ONE declared difference, so prove it instead of SHA-ing it',
        why=("E24's fidelity proof asserts the watch set is SHA-equal to E24's, which is right for "
             "a lane that changes nothing. E29's brief permits exactly one intentional change -- the "
             "watch set -- and requires before/after receipts, so a SHA equality is the one check "
             "that CANNOT be carried unchanged. It is replaced by a STRONGER statement, not a "
             "weaker one: E24's 230-entry vector must be carried verbatim, unreordered, and appear "
             "as an EXACT PREFIX of E29's, with the 13 new entries appended last and disjoint from "
             "everything carried. Not one other assertion in the tool is removed, softened or "
             "skipped, and the driver itself is still required to be byte-identical under the "
             "rename."),
        pairs=[
            ("  2. watch set         -- watch-set.json SHA-equal, 230 entries, tiers equal;\n",
             "  2. watch set         -- E24's 230-entry vector carried VERBATIM as an exact\n"
             "                          prefix, plus the one declared Mission-1 tier (13\n"
             "                          entries) appended last; every tier's count honest;\n"),
            ("check('watch-set.json SHA-equal to E24\\'s', a == b, e24_sha=a, e29_sha=b)\n",
             "wsc = json.loads((E / 'watch-set-change.json').read_text())\n"
             "# E29 CHANGE 2: the watch set is the ONE intentional change the brief permits, so it\n"
             "# cannot be asserted SHA-equal to E24's. It is PROVED instead to be E24's/E26's\n"
             "# 230-entry vector carried verbatim with exactly one tier appended -- a stronger\n"
             "# statement than a SHA, because it names what moved and what did not.\n"
             "check('watch set differs from E24\\'s ONLY by the declared appended tier',\n"
             "      wsc['green'] and a != b and a == wsc['before']['sha256'],\n"
             "      e24_sha=a, e29_sha=b, carried_baseline_sha=wsc['before']['sha256'],\n"
             "      change_checks=wsc['checks'], appended_tier=wsc['appended_tier']['name'],\n"
             "      appended_entries=len(wsc['appended_addrs']))\n"),
            ("check('total is E24\\'s 230 new entries against e23a\\'s 37',\n"
             "      ws['total_entries'] == 230 and ws['e23a_total_entries'] == 37,\n"
             "      total_entries=ws['total_entries'], e23a=ws['e23a_total_entries'],\n",
             "check('total is E24\\'s 230 carried plus the 13 declared new entries, against e23a\\'s 37',\n"
             "      ws['total_entries'] == 243 and ws['e23a_total_entries'] == 37\n"
             "      and ws['total_entries'] - len(wsc['appended_addrs']) == 230,\n"
             "      total_entries=ws['total_entries'], carried_total=230,\n"
             "      appended=len(wsc['appended_addrs']), e23a=ws['e23a_total_entries'],\n"),
            ("check('watch address list identical, entry for entry, in order',\n"
             "      e24['producer'] == e29['producer'], entries=len(e29['producer']))\n",
             "check('E24\\'s watch address list is an EXACT PREFIX of E29\\'s, entry for entry, in order',\n"
             "      e29['producer'][:len(e24['producer'])] == e24['producer']\n"
             "      and e29['producer'][len(e24['producer']):] == [int(x, 16) for x in wsc['appended_addrs']],\n"
             "      e24_entries=len(e24['producer']), e29_entries=len(e29['producer']),\n"
             "      appended=len(wsc['appended_addrs']))\n"),
            ("check('full watch vector = 197 tiered + 4 singles + 29 carried = E24\\'s 230, no duplicates',\n"
             "      len(watches) == ws['total_entries'] == 230 and len(set(watches)) == len(watches)\n"
             "      and ws['new_entries'] + ws['carried_producer_singles'] + ws['carried_non_producer'] == 230,\n",
             "check('full watch vector = 210 tiered + 4 singles + 29 carried = 243 (E24\\'s 230 + 13), no duplicates',\n"
             "      len(watches) == ws['total_entries'] == 243 and len(set(watches)) == len(watches)\n"
             "      and ws['new_entries'] + ws['carried_producer_singles'] + ws['carried_non_producer'] == 243,\n"),
            ("     verdict=('the boot E29 spends is E24\\'s designed boot: the driver is byte-identical under '\n"
             "              'the mechanical rename, the watch set is SHA-identical, and the caps, argv and '\n"
             "              'watch vector compare equal element for element')))\n",
             "     watch_set_change=json.loads((E / 'watch-set-change.json').read_text()),\n"
             "     verdict=('the boot E29 spends is E24\\'s designed boot with EXACTLY ONE declared '\n"
             "              'difference, the watch set: the driver is byte-identical under the mechanical '\n"
             "              'rename, the caps and argv compare equal, and E24\\'s 230-entry watch vector is '\n"
             "              'an exact prefix of E29\\'s 243 with the 13 Mission-1 entries appended last')))\n"),
        ],
    ),
    dict(
        file='e29_close.py',
        name='CHANGE 4 -- refit on every measured point, not just the stale two in watch-set.json',
        why=("E24's cost-model block inside `watch-set.json` carries only the e22a and e23a "
             "calibration points, because it was written before either of the big-vector boots "
             "existed. E26 then MEASURED a third point (230 entries, 9.524 s) and committed it in "
             "`E26/cost-model-refit.json`. Refitting from the stale two-point list would silently "
             "throw E26's measurement away and report a three-point fit that is really "
             "two-plus-one. The calibration list is taken from the prior lane's committed refit "
             "receipt instead, so E29's fit is four-point. Nothing else in the refit moves, and "
             "the receipt records both fits."),
        pairs=[("pts = [dict(boot=c['boot'], watches=c['watches'], span_complete_s=c['span_complete_s'])\n"
                "       for c in WS['cost_model']['calibration']]\n",
                "# E29 CHANGE 4: take the calibration points from E26's COMMITTED refit receipt,\n"
                "# which already carries E24's two plus E26's own measured third, instead of from\n"
                "# the two-point list frozen inside watch-set.json before either big boot existed.\n"
                "PRIOR = json.loads((E.parent / 'E26/cost-model-refit.json').read_text())['points']\n"
                "pts = [dict(boot=c['boot'], watches=c['watches'], span_complete_s=c['span_complete_s'])\n"
                "       for c in PRIOR]\n")],
    ),
    dict(
        file='e29_close.py',
        name='CHANGE 3 -- measure this lane\'s release latency instead of carrying E26\'s number',
        why=("E26's close tool writes `release_latency_ms=8` and `needed_sigkill=False` as LITERALS "
             "into its own final audit. Those were E26's measurements, and carried unchanged into "
             "E29 they would report E26's boot in E29's audit. Both are computed from this lane's "
             "own `e29a-result.json` instead. Nothing else in the tool moves."),
        pairs=[("               release_latency_ms=8, needed_sigkill=False),\n",
                "               release_latency_ms=round((datetime.datetime.fromisoformat(result['release_utc'])\n"
                "                                         - datetime.datetime.fromisoformat(result['process_end_utc'])\n"
                "                                        ).total_seconds()*1000, 3),\n"
                "               needed_sigkill=bool(result.get('needed_sigkill'))),\n")],
    ),
]

rows, diffs = [], []
for ch in CHANGES:
    p = E / ch['file']
    text = orig = p.read_text()
    applied = []
    for before, after in ch['pairs']:
        if after in text:
            applied.append(dict(state='already applied', before_len=len(before), after_len=len(after)))
            continue
        assert before in text, f"{ch['file']}: neither BEFORE nor AFTER present:\n{before[:200]}"
        text = text.replace(before, after, 1)
        applied.append(dict(state='applied now', before_len=len(before), after_len=len(after)))
    changed = text != orig
    if changed:
        p.write_text(text)
    rows.append(dict(file=ch['file'], name=ch['name'], why=ch['why'],
                     pairs=len(ch['pairs']), pair_states=applied,
                     wrote=changed, bytes_before=len(orig.encode()), bytes_after=len(text.encode()),
                     sha_after=sha(p)))
    diffs.append('## ' + ch['name'] + '\n\n**File:** `' + ch['file'] + '`\n\n' + ch['why'] + '\n\n```diff\n' +
                 ''.join(difflib.unified_diff(orig.splitlines(True), text.splitlines(True),
                                              fromfile=ch['file'] + ' (carried)',
                                              tofile=ch['file'] + ' (E29)')) + '```\n')

save('tooling-changes.json', dict(utc=utc(), changes=rows,
     written_fresh=[dict(
         file='e29_fixgate.py',
         why=("E26's fix gate reads E26's OWN mission receipts (x-a-startcode.json, "
              "x-b-sema36.json, objective-1a.json, watch-ledger.json) -- E26's questions, not "
              "E29's. Carried mechanically it would read files this lane never produces. Written "
              "fresh against E29's own receipts and NOT claimed as a carry; it is therefore absent "
              "from rename-proof-hexsafe.json by design. E27 set the precedent with e27_common.py."),
         gate_decision_unchanged='STOP'),
         dict(file='e29_common.py', why='the lane common, written fresh exactly as E26 wrote its own'),
         dict(file='e29_bootstrap_rename.py', why='one-off: e26_rename.py hardcodes its own destination token and cannot rename itself'),
         dict(file='e29_carry_audit.py', why='new check for the rename-induced dangling-path class that CHANGE 1 instantiates'),
         dict(file='e29_slot.py', why='Mission 1 has no prior-lane equivalent'),
         dict(file='e29_watchset.py', why='the one permitted driver-behaviour change, with before/after receipts'),
         dict(file='e29_prereg.py', why='pre-registration of the armed set and the P1-P4 pass/fail bytes'),
         dict(file='e29_verdict.py', why='Mission 2 grading, against the pre-registered rows only')],
     capture_driver_unchanged=dict(
         file='e29_capture.py',
         statement='byte-identical to E26\'s under the hex-safe rename; proved in boot-fidelity.json',
         why='the watch set lives in watch-set.json, which the driver loads, so changing it needs no driver edit'),
     fork_source_edits=0, fork_commits=0, pushes=0))
(E / 'tooling-diff.md').write_text('# E29 intentional tooling changes\n\n' + '\n'.join(diffs) +
                                   '\n# E29 TOOLING DIFF TAIL COMPLETE\n')
for r in rows:
    print(f"{r['file']}: {r['name'][:60]}  wrote={r['wrote']}  {r['bytes_before']}->{r['bytes_after']} B")
    for s in r['pair_states']:
        print('   ', s['state'])
print('# E29 PATCH TAIL COMPLETE')
