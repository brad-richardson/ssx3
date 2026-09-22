# E25 intentional tooling changes

Nine tools are byte-pure renames from E24 (`rename-proof-hexsafe.json`).
`e25_common.py` is written fresh (internal reservation 3 GiB, declared in
`CONTRACT.md`; rebuild target `NEWB = B0`, the E18 path). The edits below
revert the three E24 CHANGE comments that exist only because E24 had no
suite binary.

## e25_baseline.py — restore the 458-test unloaded suite gate (APPLIED)

```diff
--- e25_baseline.py (E24 shape)
+++ e25_baseline.py (E25)
@@ -0,0 +1,4 @@
+# E25 CHANGE 1 (reverts E24 CHANGE 2): the suite binary was REBUILT by this
+# lane, so the 458-test gate runs again instead of reporting BLOCKED. The
+# presence short-circuit in e25_validate.suite() is kept -- it is the gate
+# that would catch a failed rebuild -- but it is no longer expected to fire.
@@ -2,4 +6 @@
-# E25 CHANGE 2: the 458-test suite is BLOCKED (binary wiped with the protected
-# build tree). The fixture half below still runs on the SSD-resident, sha-equal
-# `binding-test`, so the behavior checkpoint is reported as what it IS:
-# fixture gates VERIFIED, suite gate BLOCKED.
+assert suite_rc==0 and suite_row.get('status')!='BLOCKED',suite_row
```

## e25_baseline.py — record the restored suite count in the checkpoint receipt (APPLIED)

```diff
--- e25_baseline.py (E24 shape)
+++ e25_baseline.py (E25)
@@ -1 +1 @@
-save('checkpoint-complete.json',dict(utc=utc(),suite=None,suite_status=suite_row.get('status','BLOCKED'),suite_receipt=suite_row,
+save('checkpoint-complete.json',dict(utc=utc(),suite=458,suite_status='PASS',suite_receipt=suite_row,
```

## e25_observer_regression.py — assert the observer-LOADED suite ran rather than short-circuiting (APPLIED)

```diff
--- e25_observer_regression.py (E24 shape)
+++ e25_observer_regression.py (E25)
@@ -1 +1,2 @@
-suite('observer')
+suite_rc,suite_txt,suite_row=suite('observer')
+assert suite_rc==0 and suite_row.get('status')!='BLOCKED',suite_row
```

## e25_observer_regression.py — restore the suite's own observer directory as the parser-reach receipt (APPLIED)

```diff
--- e25_observer_regression.py (E24 shape)
+++ e25_observer_regression.py (E25)
@@ -1,6 +1,6 @@
-# E25 CHANGE 3: the suite's own observer dir is BLOCKED with the suite binary.
-# In E23 the suite was the ONLY loaded run that reached the parser, so the
-# parser-reach receipt moves to the surviving E23 cadence fixture, which drives
-# the R3 payload through the actual title wrappers (`e25_cadence.py`). The
-# fixture closures below still carry real `# E21 PARSER CLOSURE` footers.
-for directory in [*sorted((P/'e25-fixtures/observer-bindings').glob('*/parser-observer')),
+# E25 CHANGE 2 (reverts E24 CHANGE 3): with the suite rebuilt, the suite's own
+# observer directory is once more the loaded run that REACHES the parser, so it
+# leads the closure list exactly as it did in E23 and the parser-reach receipt
+# returns here from the cadence fixture.
+for directory in [E/'.suite-observer/parser-observer',
+                  *sorted((P/'e25-fixtures/observer-bindings').glob('*/parser-observer')),
```

## e25_observer_regression.py — restore E23 parser-reach assertion and the loaded suite count (APPLIED)

```diff
--- e25_observer_regression.py (E24 shape)
+++ e25_observer_regression.py (E25)
@@ -2 +2,2 @@
-save('observer-regression.json',dict(utc=utc(),suite=None,suite_status='BLOCKED',parser_reach_moved_to='e25_cadence.py',
+assert rows[0]['footer']['parseCalls']>0,'suite observer dir did not reach the parser'
+save('observer-regression.json',dict(utc=utc(),suite=458,suite_status='PASS',parser_reach='suite observer dir',
```

# E25 TOOLING DIFF TAIL COMPLETE
