# E23 tooling — intentional changes beyond the mechanical rename

Nine carried tools plus `e23_capture.py` / `e23_prepare_probe.py` have a
byte-empty normalized diff against their E22 originals (`rename-proof.json`,
`rename-proof-probe.json`). The changes below are the only intentional ones.
New files with no E22 original: `e23_complete_test.cpp`, `e23_payload.inc`,
`e23_link_test.py`, `e23_cadence.py`, `e23_mine.py`, plus the amendment A1 diff
to `e23_common.py` (`amendment-a1.diff`, cause in `AMENDMENT-A1.md`).

## e23_capture.py — producer/source watch set

```diff
--- e23_capture.py (rename only)
+++ e23_capture.py (E23)
@@ -29,6 +29,15 @@
 DISPLAY = [0x12000000, 0x12000020, 0x12000070, 0x12000080,
            0x12000090, 0x120000a0, 0x120000e0]
 OFFSETS = [0x5a78, 0x5a7c, 0x5a84, 0x5a88, 0x5a74, 0xf44, 0x59e8]
+# E23 step 4: the guest producer/source structures the E7 tap named on this exact
+# run shape in E18/E21/E22. Watching them measures whether the guest refills the
+# MPEG source while the caller is parked -- the one fact that decides whether a
+# re-ask at C2a's site could ever be satisfied. Addresses and their receipts are
+# tabled in BOOT-DESIGN.md; each watch covers an 8-byte window.
+PRODUCER = [0x548800, 0x548804, 0x548808,   # source descriptor head / data / bytes
+            0x5487c0,                        # source object passed to 0x3b06b0 / 0x3b06f8
+            0x587b28, 0x587b78, 0x587b7c,    # producer block +0x28 sourceObject, +0x78/+0x7c buffers
+            0xdc8340]                        # staging buffer AddBs read its 5,040 B from
 MIB = 1024 * 1024
 ALLOCATED_CAPS=dict(boot_log=256*MIB,trace=96*MIB,function_log=1024*MIB,e4_dir=64*MIB,park_dir=128*MIB,frames_dir=64*MIB,e7_dir=64*MIB,parser_dir=64*MIB,aggregate=1536*MIB)
 CAPS = dict(wall_s=90, terminate_reserve_s=15, progress_lines=1000000,
@@ -153,6 +162,7 @@
         watches += [args.s+off for off in OFFSETS]
         watches += [0x10005000,0x1000a000,0x1000a010,0x1000a020]
     watches += [0xb851a0,0xb851a4,0xb851ac,0xb851e0,0xb84e84,0xb84d88,0x4a3938,0x4a393c,0x4a3940,0x4a3944]
+    watches += PRODUCER
     try:
         preflight(label)
     except Exception as error:
```

## e23_prepare_probe.py — boot gated on the E23 cadence reference

```diff
--- e23_prepare_probe.py (rename only)
+++ e23_prepare_probe.py (E23)
@@ -21,13 +21,22 @@
 proven=json.loads((PRIOR/'parser-build.json').read_text())['observer']
 assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
 assert obs['observer']['sha256']==proven['sha256']
+# E23 gate: the boot may not be spent before the complete-feed reference lands.
+cad=json.loads((E/'cadence.json').read_text())
+assert len(cad['rows'])==4 and {r['feedBytes'] for r in cad['rows']}=={60,120,180,240}
+assert all(r['rc']==0 and r['cadence']['producerFirings']==1 and r['cadence']['addBs']==1 for r in cad['rows'])
+assert {r['outcome'] for r in cad['rows']}=={'SERVED','STALLED'},'reference needs both branches'
+assert all(r['parser']['footer']['pending']==0 and r['parser']['footer']['errors']==0 for r in cad['rows'])
+for lab in ('newbin-bindings','newbin-closure'):
+    ctl=json.loads((E/f'{lab}-validation.json').read_text())
+    assert all(c['rc']==0 for c in ctl['cases']),lab
 def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
 head=git('rev-parse','HEAD').strip();assert head==BASE_SHA and git('diff','--cached','--name-only')==''
 assert git('status','--short')=='?? ps2_log.txt\n'
 ckpt=json.loads((E/'checkpoint.json').read_text())
 assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']
 assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']
-save('entry-preflight.json',dict(utc=utc(),suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
+save('entry-preflight.json',dict(utc=utc(),cadence_cases=len(cad['rows']),cadence_branches=2,suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
     predicate_cases=14,query_cases=4,leaf_present=True,mpeg_delivery_cases=2,run_exit_cases=6,
     new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True,
     instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21'))
```
