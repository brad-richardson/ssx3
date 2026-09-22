# E24 tooling provenance

## Pure rename (hex-safe), normalized diff byte-empty

The `e23`→`e24` rename masks every run of ≥16 hex characters BEFORE
renaming, so a digest cannot be rewritten — errata E23-E1, where an
`e22`→`e23` rename corrupted `ELF_SHA` and the normalized-diff proof was
blind to it by construction. The proof additionally asserts that every
hex run in the source survives byte-for-byte in the output.

| Tool | src B | dst B | hex runs masked | normalized diff | hex runs equal |
|---|---:|---:|---:|---|---|
| `e24_io.py` | 672 | 672 | 0 | byte-empty | yes |
| `e24_closed_events.py` | 2,145 | 2,145 | 0 | byte-empty | yes |
| `e24_parser_receipt.py` | 2,818 | 2,818 | 1 | byte-empty | yes |
| `e24_bounded.py` | 3,508 | 3,508 | 0 | byte-empty | yes |
| `e24_validate.py` | 6,920 | 6,920 | 0 | byte-empty | yes |
| `e24_observer_regression.py` | 2,279 | 2,279 | 0 | byte-empty | yes |
| `e24_baseline.py` | 1,431 | 1,431 | 0 | byte-empty | yes |
| `e24_mine.py` | 4,509 | 4,509 | 0 | byte-empty | yes |
| `e24_cadence.py` | 2,965 | 2,965 | 0 | byte-empty | yes |
| `e24_capture.py` | 16,105 | 16,105 | 1 | byte-empty | yes |
| `e24_prepare_probe.py` | 3,565 | 3,565 | 0 | byte-empty | yes |
| `e24_boot_mine.py` | 3,396 | 3,396 | 0 | byte-empty | yes |

All 12 normalized diffs byte-empty: **True**. 
All hex runs equal: **True**.

`ELF_SHA` is byte-identical to E23's: `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`.

### Protected tokens (held out of the rename)

- `PS2X_E21_PARSER_DIR`
- `PS2X_E21_PROOF`
- `# E21 PARSER CLOSURE`
- `e21-parser-observer.dylib`
- `e21_parser_observer.h`
- `e23-fixtures/complete`
- `# E23 COMPLETE FEED FIXTURE TAIL COMPLETE`

The first five are the REUSED E21 dylib's interface, E21-spelled by
necessity since E21. The last two are new in E24: the E23 cadence fixture
**binary** survived the host restart at its E23 path and owns its own
footer string, so renaming either would point the lane at a file that does
not exist or assert on a footer the binary never prints.

## Intentional changes — lane tools (6)

Each exists because a PROTECTED build tree was wiped and a gate E23
asserted can no longer run. None weakens an assertion that is still
measurable; each records BLOCKED with its receipt.

**`e24_validate.py`**
```diff
-def suite(label):
-    scratch=E/('.suite-'+label);scratch.mkdir(exist_ok=False)
+def suite(label):
+    # E24 CHANGE 1: the suite binary lives in a PROTECTED build tree that the
+    # host restart wiped (`env-audit.json`). A missing suite is a BLOCKED gate
+    # with its receipt, never a silent skip and never a re-point at another
+    # build -- the 458 counts and the E18 R1-R6 text are properties of THAT
+    # binary. Callers record the returned row and stop.
+    binary=B/'ps2xTest/ps2x_tests'
+    if not binary.exists():
+        row=dict(label=label,status='BLOCKED',binary=str(binary),present=False,
+                 reason='protected build tree absent after host restart')
+        save(label+'-suite.json',row)
+        print('SUITE',label,'BLOCKED (binary absent)')
+        return None,'',row
+    scratch=E/('.suite-'+label);scratch.mkdir(exist_ok=False)
```

**`e24_baseline.py`**
```diff
-suite('checkpoint')
+suite_rc,suite_txt,suite_row=suite('checkpoint')
+# E24 CHANGE 2: the 458-test suite is BLOCKED (binary wiped with the protected
+# build tree). The fixture half below still runs on the SSD-resident, sha-equal
+# `binding-test`, so the behavior checkpoint is reported as what it IS:
+# fixture gates VERIFIED, suite gate BLOCKED.
```

**`e24_baseline.py`**
```diff
-save('checkpoint-complete.json',dict(utc=utc(),suite=458,closure_cases=6
+save('checkpoint-complete.json',dict(utc=utc(),suite=None,suite_status=suite_row.get('status','BLOCKED'),suite_receipt=suite_row,closure_cases=6
```

**`e24_observer_regression.py`**
```diff
-rows=[]
-for directory in [E/'.suite-observer/parser-observer',
+rows=[]
+# E24 CHANGE 3: the suite's own observer dir is BLOCKED with the suite binary.
+# In E23 the suite was the ONLY loaded run that reached the parser, so the
+# parser-reach receipt moves to the surviving E23 cadence fixture, which drives
+# the R3 payload through the actual title wrappers (`e24_cadence.py`). The
+# fixture closures below still carry real `# E21 PARSER CLOSURE` footers.
+for directory in [
```

**`e24_observer_regression.py`**
```diff
-assert rows[0]['footer']['parseCalls']>0
+assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'
```

**`e24_observer_regression.py`**
```diff
-save('observer-regression.json',dict(utc=utc(),suite=458,
+save('observer-regression.json',dict(utc=utc(),suite=None,suite_status='BLOCKED',parser_reach_moved_to='e24_cadence.py',
```

## Intentional changes — boot driver (4)

**`e24_capture.py`**
```diff
-PRODUCER = [0x548800, 0x548804, 0x548808,   # source descriptor head / data / bytes
-            0x5487c0,                        # source object passed to 0x3b06b0 / 0x3b06f8
-            0x587b28, 0x587b78, 0x587b7c,    # producer block +0x28 sourceObject, +0x78/+0x7c buffers
-            0xdc8340]                        # staging buffer AddBs read its 5,040 B from
+# E24 CHANGE 2: the TIERED extended watch set (BOOT-DESIGN.md, watch-set.json).
+# E23 watched 8 producer/source words and NAMED the gap: the descriptor head
+# advanced 0x548800 = 0x548880 and that successor node was unwatched, so its
+# post-park silence was vacuous. This covers the whole descriptor node array,
+# both buffers, and the bytes just past the delivered region -- 230 entries
+# against e23a's 37, sized by the cost model because diagWatchEmit scans the
+# whole vector on EVERY guest store.
+_WATCH_SET = json.loads((Path(__file__).resolve().parent / 'watch-set.json').read_text())
+PRODUCER = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c]   # carried singles, not in any tier
+for _tier in _WATCH_SET['tiers']:
+    PRODUCER.extend(_tier['addrs'])
+assert len(PRODUCER) == _WATCH_SET['new_entries'] + _WATCH_SET['carried_producer_singles'], len(PRODUCER)
```

**`e24_capture.py`**
```diff
-    record['files'] = []
-    for path, size, expected in [
+    # E24 CHANGE 1: PRESENCE first. e23a's driver went straight to .stat() and
+    # would raise FileNotFoundError deep inside the loop; E24 opened to exactly
+    # that situation (all three protected build trees wiped by a host restart)
+    # and a boot driver must refuse it as a named gate, before the lease.
+    record['presence'] = {}
+    for path in (BIN, TEST, ELF, W / 'P1/SLUS_207.72', W / 'SSX 3 (USA).iso',
+                 EVIDENCE / 'parser/e21-parser-observer.dylib'):
+        record['presence'][str(path)] = path.exists()
+    absent = sorted(k for k, v in record['presence'].items() if not v)
+    if absent:
+        raise RuntimeError('required binaries absent; E24 tables and stops '
+                           'without claiming the lease: ' + '; '.join(absent))
+    record['files'] = []
+    for path, size, expected in [
```

**`e24_capture.py`**
```diff
-    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
-               PS2X_DIAG_SEMA_CREATE='1',
+    # E24 CHANGE 3: PS2X_DIAG_SEMA / _S0 are already compiled into the proven
+    # runner (EeScheduler.cpp:156,168) and print nothing when unset, so this
+    # needs no rebuild and no fork edit. They are the ONLY source of the waker
+    # `ra` per signal -- the always-on park tally records the syscall stub pc
+    # (0x423dc8 / 0x423dd8), which cannot name a caller. Objective 2.
+    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
+               PS2X_DIAG_SEMA='1',PS2X_DIAG_SEMA_S0='1',
+               PS2X_DIAG_SEMA_CREATE='1',
```

**`e24_capture.py`**
```diff
-            result['rc']=p.returncode
-            result['process_end_utc']=utc()
+            result['rc']=p.returncode
+            # E24 CHANGE 4: record span-complete on EVERY path, not only when a
+            # bound fires, so the next lane can refit the watch-count cost model
+            # in BOOT-DESIGN.md against a third data point.
+            result.setdefault('span_complete_s',span_at)
+            result['watch_entries']=len(config['watch_addresses'])
+            result['process_end_utc']=utc()
```

## New in E24

- `e24_rename.py` — the hex-safe rename + proof tool itself (errata E23-E1 discipline)
- `e24_patch.py / e24_patch_capture.py` — the intentional changes, applied idempotently and recorded as data
- `e24_env_audit.py` — the environment-loss audit against E23's own 1,725-file manifest
- `e24_checkpoint.py` — every checkpoint gate recorded VERIFIED or BLOCKED with its receipt
- `e24_dims.py` — objective 3: the I-lane V3 dims, parsed from the retained 5,040 B
- `e24_sema_mine.py` — objectives 1b and 2 from the retained e23a park snapshot + boot log
- `e24_signaller_closure.py` — the closed signaller enumeration for semaphore 36
- `e24_close.py` — the E24 final audit

## `stdbuf` in E24

Present only as the forbidding assertion and the receipt field, carried
from E22/E23. The boot argv would exec the runner directly
(`argv0_is_runner`, `stdbuf_free`). No boot was spent.

