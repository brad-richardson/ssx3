"""E26's intentional tooling changes, applied idempotently and recorded as data.

Every change is a literal before/after pair. Running this tool twice is a no-op
on the second run (each pair asserts either the BEFORE or the AFTER is present,
never neither). Full diffs land in `tooling-diff.md`, the data in
`tooling-changes.json`.
"""
import difflib
from e26_common import *

CHANGES = [
    dict(
        file='e26_prepare_probe.py',
        name='CHANGE 1 -- gate against E25\'s fresh receipts, not E24\'s red ones',
        why=("E24's probe gate reads its regression receipts out of its OWN lane directory. "
             "Those receipts are RED: they were taken when the host restart had wiped the "
             "runner and the suite, so E24's `checkpoint.json` carries red=true and E24 never "
             "wrote a `checkpoint-complete.json`, a `cadence.json` or an `observer-regression.json` "
             "at all. E25 then re-ran that IDENTICAL chain green -- 458/458 unloaded, 458/458 "
             "observer-loaded, 10/10 closures, the four-point cadence reference, the prior "
             "bindings and the absorbed controls -- on binaries that are BYTE-IDENTICAL to the "
             "pins, and the orchestrator gated it. E26 therefore evaluates E24's assertions, "
             "UNCHANGED IN CONTENT, against E25's receipts. Not one assertion is removed, "
             "softened or skipped; only the directory they read from moves. The driver's own "
             "preflight still runs the full 458-test suite FRESH before the atomic claim."),
        pairs=[
            (   # the red gate: E26's red flag is its OWN Mission 0 restore receipt
                "ckpt=json.loads((E/'checkpoint.json').read_text())\n"
                "if ckpt['red']:\n"
                "    save('probe-authorization.json',dict(utc=utc(),authorized=False,\n"
                "        reason='checkpoint RED: '+', '.join(ckpt['red_gates']),\n"
                "        red_gates=ckpt['red_gates'],\n"
                "        protected_build_files_present=ckpt['protected_build_files'],\n"
                "        protected_build_files_expected=ckpt['protected_build_files_expected'],\n"
                "        runner=ckpt['runner'],suite=ckpt['suite'],\n"
                "        boot_spent=False,lease_claimed=False))\n"
                "    print('BOOT NOT AUTHORIZED -- checkpoint RED:',', '.join(ckpt['red_gates']))\n"
                "    print('# E26 PREPARE PROBE TAIL COMPLETE')\n"
                "    raise SystemExit(0)\n",
                "# E26 CHANGE 1: the regression receipts come from E25, which re-ran E24's\n"
                "# IDENTICAL chain green on byte-identical binaries hours ago. E24's own\n"
                "# receipts are red by construction -- taken when the runner did not exist.\n"
                "GATES=E.parent/'E25'\n"
                "# E26's red flag is its OWN Mission 0 restore receipt: the instrument is\n"
                "# verified in place, by two matching re-shas, or this lane does not boot.\n"
                "rst=json.loads((E/'restore-pass-1.json').read_text())\n"
                "if not rst['all_ok']:\n"
                "    save('probe-authorization.json',dict(utc=utc(),authorized=False,\n"
                "        reason='instrument RED: '+rst['path_taken'],\n"
                "        restore=rst,boot_spent=False,lease_claimed=False))\n"
                "    print('BOOT NOT AUTHORIZED -- instrument RED:',rst['path_taken'])\n"
                "    print('# E26 PREPARE PROBE TAIL COMPLETE')\n"
                "    raise SystemExit(0)\n"),
            ("chk=json.loads((E/'checkpoint-complete.json').read_text())\n",
             "chk=json.loads((GATES/'checkpoint-complete.json').read_text())\n"),
            ("txt=(E/'checkpoint-suite.txt').read_text();",
             "txt=(GATES/'checkpoint-suite.txt').read_text();"),
            ("v=json.loads((E/'checkpoint-bindings-validation.json').read_text());",
             "v=json.loads((GATES/'checkpoint-bindings-validation.json').read_text());"),
            ("obs=json.loads((E/'observer-regression.json').read_text())\n",
             "obs=json.loads((GATES/'observer-regression.json').read_text())\n"),
            ("cad=json.loads((E/'cadence.json').read_text())\n",
             "cad=json.loads((GATES/'cadence.json').read_text())\n"),
            ("    ctl=json.loads((E/f'{lab}-validation.json').read_text())\n",
             "    ctl=json.loads((GATES/f'{lab}-validation.json').read_text())\n"),
            (   # the binaries are pinned against E26's own verified restore receipt
                "ckpt=json.loads((E/'checkpoint.json').read_text())\n"
                "assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']\n"
                "assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']\n",
                "# The binaries are re-hashed HERE, a third time, against the pins E26's own\n"
                "# Mission 0 verified -- not against any inherited checkpoint file.\n"
                "PIN={r['item']:r for r in rst['rows']}\n"
                "ckpt=dict(runner=dict(bytes=PIN['runner']['bytes'],sha256=PIN['runner']['expected_sha']),\n"
                "          suite=dict(bytes=PIN['suite']['bytes'],sha256=PIN['suite']['expected_sha']))\n"
                "assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']\n"
                "assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']\n"),
        ]),
    dict(
        file='e26_prepare_probe.py',
        name='CHANGE 2 -- record the gate provenance in the manifests',
        why=("The two manifests the capture driver reads are the boot's authorization record. "
             "They now SAY which lane each gate was measured in, so a later reader cannot "
             "mistake an inherited receipt for one E26 took itself."),
        pairs=[
            ("    instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21'))\n",
             "    instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21',\n"
             "    regression_receipts_from='E25',regression_receipts_note=(\n"
             "        'E24 assertions unchanged in content, evaluated against E25 receipts taken '\n"
             "        'on byte-identical binaries; the capture driver still runs the 458-test '\n"
             "        'suite FRESH before the atomic claim'),\n"
             "    binaries_rehashed_by_E26=True,restore_path=rst['path_taken']))\n"),
        ]),
]


def main():
    rows = []
    diffs = []
    for change in CHANGES:
        path = E / change['file']
        text = path.read_text()
        before_text = text
        applied, already = 0, 0
        for before, after in change['pairs']:
            if after in text:
                already += 1
                continue
            assert before in text, f"neither BEFORE nor AFTER present in {change['file']}: {before[:60]!r}"
            assert text.count(before) == 1, f'ambiguous anchor in {change["file"]}'
            text = text.replace(before, after)
            applied += 1
        if text != before_text:
            path.write_text(text)
        rows.append(dict(file=change['file'], change=change['name'], why=change['why'],
                         pairs=len(change['pairs']), applied=applied, already_applied=already,
                         idempotent=True))
        if applied:
            diffs.append((change['name'], change['file'],
                          ''.join(difflib.unified_diff(
                              before_text.splitlines(keepends=True), text.splitlines(keepends=True),
                              fromfile=change['file'] + ' (renamed)', tofile=change['file'] + ' (E26)'))))
    save('tooling-changes.json', dict(utc=utc(), changes=rows,
         total_changes=len(rows), total_pairs=sum(r['pairs'] for r in rows),
         note='Each pair asserts BEFORE or AFTER is present; a second run is a no-op.'))
    if diffs:
        md = ['# E26 tooling changes — full diffs\n']
        for name, fname, d in diffs:
            md += [f'\n## {name}\n', f'\n`{fname}`\n', '\n```diff\n', d, '```\n']
        md.append('\n# E26 TOOLING DIFF TAIL COMPLETE\n')
        (E / 'tooling-diff.md').write_text(''.join(md))
    for r in rows:
        print(f"{r['file']}: {r['change']} -> applied {r['applied']}/{r['pairs']}, already {r['already_applied']}")
    print('# E26 PATCH TAIL COMPLETE')


if __name__ == '__main__':
    main()
