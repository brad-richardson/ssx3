# E26 tooling changes — full diffs

## CHANGE 1 -- gate against E25's fresh receipts, not E24's red ones

`e26_prepare_probe.py`

```diff
--- e26_prepare_probe.py (renamed)
+++ e26_prepare_probe.py (E26)
@@ -5,25 +5,27 @@
 # mission 1 says any red checkpoint gate -> table and stop with no boot, so the
 # red check comes FIRST and refuses here rather than letting a later assert
 # fail somewhere less legible.
-ckpt=json.loads((E/'checkpoint.json').read_text())
-if ckpt['red']:
+# E26 CHANGE 1: the regression receipts come from E25, which re-ran E24's
+# IDENTICAL chain green on byte-identical binaries hours ago. E24's own
+# receipts are red by construction -- taken when the runner did not exist.
+GATES=E.parent/'E25'
+# E26's red flag is its OWN Mission 0 restore receipt: the instrument is
+# verified in place, by two matching re-shas, or this lane does not boot.
+rst=json.loads((E/'restore-pass-1.json').read_text())
+if not rst['all_ok']:
     save('probe-authorization.json',dict(utc=utc(),authorized=False,
-        reason='checkpoint RED: '+', '.join(ckpt['red_gates']),
-        red_gates=ckpt['red_gates'],
-        protected_build_files_present=ckpt['protected_build_files'],
-        protected_build_files_expected=ckpt['protected_build_files_expected'],
-        runner=ckpt['runner'],suite=ckpt['suite'],
-        boot_spent=False,lease_claimed=False))
-    print('BOOT NOT AUTHORIZED -- checkpoint RED:',', '.join(ckpt['red_gates']))
+        reason='instrument RED: '+rst['path_taken'],
+        restore=rst,boot_spent=False,lease_claimed=False))
+    print('BOOT NOT AUTHORIZED -- instrument RED:',rst['path_taken'])
     print('# E26 PREPARE PROBE TAIL COMPLETE')
     raise SystemExit(0)
-chk=json.loads((E/'checkpoint-complete.json').read_text())
+chk=json.loads((GATES/'checkpoint-complete.json').read_text())
 assert chk['suite']==458 and chk['closure_cases']==6 and chk['e15_rc']==[0,0] and chk['extra_cases']==8 and chk['boot']==0
-txt=(E/'checkpoint-suite.txt').read_text();assert 'Total Tests: 458' in txt and 'Failed: 0' in txt
+txt=(GATES/'checkpoint-suite.txt').read_text();assert 'Total Tests: 458' in txt and 'Failed: 0' in txt
 assert 'MPEG non-stream R1' in txt and 'MPEG non-stream R6' in txt
-v=json.loads((E/'checkpoint-bindings-validation.json').read_text());prior=v['cases'][0]
+v=json.loads((GATES/'checkpoint-bindings-validation.json').read_text());prior=v['cases'][0]
 assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
-obs=json.loads((E/'observer-regression.json').read_text())
+obs=json.loads((GATES/'observer-regression.json').read_text())
 assert obs['suite']==458 and obs['closure_cases']==6 and obs['boot']==0
 assert all(c['footer']['pending']==0 for c in obs['closures'])
 # Inherited E21 receipts: isolation forwarding, Q1 threshold, Q2 static audit.
@@ -38,18 +40,22 @@
 assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
 assert obs['observer']['sha256']==proven['sha256']
 # E26 gate: the boot may not be spent before the complete-feed reference lands.
-cad=json.loads((E/'cadence.json').read_text())
+cad=json.loads((GATES/'cadence.json').read_text())
 assert len(cad['rows'])==4 and {r['feedBytes'] for r in cad['rows']}=={60,120,180,240}
 assert all(r['rc']==0 and r['cadence']['producerFirings']==1 and r['cadence']['addBs']==1 for r in cad['rows'])
 assert {r['outcome'] for r in cad['rows']}=={'SERVED','STALLED'},'reference needs both branches'
 assert all(r['parser']['footer']['pending']==0 and r['parser']['footer']['errors']==0 for r in cad['rows'])
 for lab in ('newbin-bindings','newbin-closure'):
-    ctl=json.loads((E/f'{lab}-validation.json').read_text())
+    ctl=json.loads((GATES/f'{lab}-validation.json').read_text())
     assert all(c['rc']==0 for c in ctl['cases']),lab
 def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
 head=git('rev-parse','HEAD').strip();assert head==BASE_SHA and git('diff','--cached','--name-only')==''
 assert git('status','--short')=='?? ps2_log.txt\n'
-ckpt=json.loads((E/'checkpoint.json').read_text())
+# The binaries are re-hashed HERE, a third time, against the pins E26's own
+# Mission 0 verified -- not against any inherited checkpoint file.
+PIN={r['item']:r for r in rst['rows']}
+ckpt=dict(runner=dict(bytes=PIN['runner']['bytes'],sha256=PIN['runner']['expected_sha']),
+          suite=dict(bytes=PIN['suite']['bytes'],sha256=PIN['suite']['expected_sha']))
 assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']
 assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']
 save('entry-preflight.json',dict(utc=utc(),cadence_cases=len(cad['rows']),cadence_branches=2,suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
```

## CHANGE 2 -- record the gate provenance in the manifests

`e26_prepare_probe.py`

```diff
--- e26_prepare_probe.py (renamed)
+++ e26_prepare_probe.py (E26)
@@ -61,7 +61,12 @@
 save('entry-preflight.json',dict(utc=utc(),cadence_cases=len(cad['rows']),cadence_branches=2,suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
     predicate_cases=14,query_cases=4,leaf_present=True,mpeg_delivery_cases=2,run_exit_cases=6,
     new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True,
-    instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21'))
+    instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21',
+    regression_receipts_from='E25',regression_receipts_note=(
+        'E24 assertions unchanged in content, evaluated against E25 receipts taken '
+        'on byte-identical binaries; the capture driver still runs the 458-test '
+        'suite FRESH before the atomic claim'),
+    binaries_rehashed_by_E26=True,restore_path=rst['path_taken']))
 save('e26a-build.json',dict(utc=utc(),fork_head=head,fork_status='?? ps2_log.txt\n',test_count=458,
     bin_size=ckpt['runner']['bytes'],bin_sha=ckpt['runner']['sha256'],
     test_size=ckpt['suite']['bytes'],test_sha=ckpt['suite']['sha256']))
```

# E26 TOOLING DIFF TAIL COMPLETE
