# E28 intentional tooling changes

## CHANGE 1 -- protect E25's readiness receipt from the lane rename

**File:** `e28_rename.py`

E25 named its readiness receipt `e26-readiness.json` -- it wrote the readiness for the lane that followed it. That is a REAL PATH on disk, not a lane token, and the mechanical e26->e28 carry rewrote `e28_restore_gate.py`'s reference to `E25/e28-readiness.json`, which does not exist: the Mission 0 restore gate would have died on FileNotFoundError. This is exactly the errata E23-E1 class of bug one directory over -- the rename proof is blind to it, because the normalized diff maps both lane tokens to one placeholder and the file is SUPPOSED to change there. The token is added to PROTECTED, and `e28_carry_audit.py` now resolves EVERY cross-lane path literal in every carried tool so the class is caught, not just this instance.

```diff
```

## CHANGE 2 -- the watch set is the ONE declared difference, so prove it instead of SHA-ing it

**File:** `e28_boot_fidelity.py`

E24's fidelity proof asserts the watch set is SHA-equal to E24's, which is right for a lane that changes nothing. E28's brief permits exactly one intentional change -- the watch set -- and requires before/after receipts, so a SHA equality is the one check that CANNOT be carried unchanged. It is replaced by a STRONGER statement, not a weaker one: E24's 230-entry vector must be carried verbatim, unreordered, and appear as an EXACT PREFIX of E28's, with the 13 new entries appended last and disjoint from everything carried. Not one other assertion in the tool is removed, softened or skipped, and the driver itself is still required to be byte-identical under the rename.

```diff
--- e28_boot_fidelity.py (carried)
+++ e28_boot_fidelity.py (E28)
@@ -6,7 +6,9 @@
 
   1. driver identity   -- E24's driver, put through the SAME hex-safe rename,
                           must equal E28's driver BYTE FOR BYTE;
-  2. watch set         -- watch-set.json SHA-equal, 230 entries, tiers equal;
+  2. watch set         -- E24's 230-entry vector carried VERBATIM as an exact
+                          prefix, plus the one declared Mission-1 tier (13
+                          entries) appended last; every tier's count honest;
   3. capture window    -- CAPS and ALLOCATED_CAPS dicts equal;
   4. argv              -- the two argv strings equal;
   5. environment       -- key set equal, and every value equal except the six
@@ -39,15 +41,26 @@
 # 2. the watch set -----------------------------------------------------------
 a, b = sha(E24D / 'watch-set.json'), sha(E / 'watch-set.json')
 ws = json.loads((E / 'watch-set.json').read_text())
-check('watch-set.json SHA-equal to E24\'s', a == b, e24_sha=a, e28_sha=b)
+wsc = json.loads((E / 'watch-set-change.json').read_text())
+# E28 CHANGE 2: the watch set is the ONE intentional change the brief permits, so it
+# cannot be asserted SHA-equal to E24's. It is PROVED instead to be E24's/E26's
+# 230-entry vector carried verbatim with exactly one tier appended -- a stronger
+# statement than a SHA, because it names what moved and what did not.
+check('watch set differs from E24\'s ONLY by the declared appended tier',
+      wsc['green'] and a != b and a == wsc['before']['sha256'],
+      e24_sha=a, e28_sha=b, carried_baseline_sha=wsc['before']['sha256'],
+      change_checks=wsc['checks'], appended_tier=wsc['appended_tier']['name'],
+      appended_entries=len(wsc['appended_addrs']))
 tier_rows = [dict(tier=t['name'], lo=t['lo'], hi=t['hi'], stride=t['stride'],
                   entries=t['entries'], addrs=len(t['addrs']),
                   entries_match=t['entries'] == len(t['addrs'])) for t in ws['tiers']]
 check('every tier declares the entry count it actually carries',
       all(r['entries_match'] for r in tier_rows), tiers=tier_rows)
-check('total is E24\'s 230 new entries against e23a\'s 37',
-      ws['total_entries'] == 230 and ws['e23a_total_entries'] == 37,
-      total_entries=ws['total_entries'], e23a=ws['e23a_total_entries'],
+check('total is E24\'s 230 carried plus the 13 declared new entries, against e23a\'s 37',
+      ws['total_entries'] == 243 and ws['e23a_total_entries'] == 37
+      and ws['total_entries'] - len(wsc['appended_addrs']) == 230,
+      total_entries=ws['total_entries'], carried_total=230,
+      appended=len(wsc['appended_addrs']), e23a=ws['e23a_total_entries'],
       new_entries=ws['new_entries'], carried_singles=ws['carried_producer_singles'],
       carried_non_producer=ws['carried_non_producer'])
 
@@ -76,8 +89,11 @@
 
 check('capture window (CAPS) identical', e24['caps'] == e28['caps'], caps=e28['caps'])
 check('allocated caps identical', e24['allocated_caps'] == e28['allocated_caps'])
-check('watch address list identical, entry for entry, in order',
-      e24['producer'] == e28['producer'], entries=len(e28['producer']))
+check('E24\'s watch address list is an EXACT PREFIX of E28\'s, entry for entry, in order',
+      e28['producer'][:len(e24['producer'])] == e24['producer']
+      and e28['producer'][len(e24['producer']):] == [int(x, 16) for x in wsc['appended_addrs']],
+      e24_entries=len(e24['producer']), e28_entries=len(e28['producer']),
+      appended=len(wsc['appended_addrs']))
 check('display/offset watch tiers identical',
       e24['display'] == e28['display'] and e24['offsets'] == e28['offsets'])
 check('ELF pin identical', e24['elf_sha'] == e28['elf_sha'], elf_sha=e28['elf_sha'])
@@ -99,9 +115,9 @@
 # E24's "230 entries" IS the full vector: 197 tiered + 4 carried producer
 # singles + 29 carried non-producer. e23a's 37 was the same 29 plus 8 producer
 # words. The driver's own assert covers only PRODUCER; this covers the vector.
-check('full watch vector = 197 tiered + 4 singles + 29 carried = E24\'s 230, no duplicates',
-      len(watches) == ws['total_entries'] == 230 and len(set(watches)) == len(watches)
-      and ws['new_entries'] + ws['carried_producer_singles'] + ws['carried_non_producer'] == 230,
+check('full watch vector = 210 tiered + 4 singles + 29 carried = 243 (E24\'s 230 + 13), no duplicates',
+      len(watches) == ws['total_entries'] == 243 and len(set(watches)) == len(watches)
+      and ws['new_entries'] + ws['carried_producer_singles'] + ws['carried_non_producer'] == 243,
       total=len(watches), unique=len(set(watches)), declared_total=ws['total_entries'],
       tiered=ws['new_entries'], carried_producer_singles=ws['carried_producer_singles'],
       carried_non_producer=ws['carried_non_producer'],
@@ -126,9 +142,11 @@
      watch_set=dict(sha256=b, tiers=tier_rows, total_entries=ws['total_entries'],
                     full_vector=len(watches), cost_model=ws['cost_model']),
      caps=e28['caps'], allocated_caps=e28['allocated_caps'], argv=argv26,
-     verdict=('the boot E28 spends is E24\'s designed boot: the driver is byte-identical under '
-              'the mechanical rename, the watch set is SHA-identical, and the caps, argv and '
-              'watch vector compare equal element for element')))
+     watch_set_change=json.loads((E / 'watch-set-change.json').read_text()),
+     verdict=('the boot E28 spends is E24\'s designed boot with EXACTLY ONE declared '
+              'difference, the watch set: the driver is byte-identical under the mechanical '
+              'rename, the caps and argv compare equal, and E24\'s 230-entry watch vector is '
+              'an exact prefix of E28\'s 243 with the 13 Mission-1 entries appended last')))
 print('ALL GREEN:', ok)
 print('# E28 BOOT FIDELITY TAIL COMPLETE')
 raise SystemExit(0 if ok else 3)
```

## CHANGE 4 -- refit on every measured point, not just the stale two in watch-set.json

**File:** `e28_close.py`

E24's cost-model block inside `watch-set.json` carries only the e22a and e23a calibration points, because it was written before either of the big-vector boots existed. E26 then MEASURED a third point (230 entries, 9.524 s) and committed it in `E26/cost-model-refit.json`. Refitting from the stale two-point list would silently throw E26's measurement away and report a three-point fit that is really two-plus-one. The calibration list is taken from the prior lane's committed refit receipt instead, so E28's fit is four-point. Nothing else in the refit moves, and the receipt records both fits.

```diff
--- e28_close.py (carried)
+++ e28_close.py (E28)
@@ -10,8 +10,12 @@
 # ------------------------------------------------- the refit E24 asked for
 # BOOT-DESIGN.md: "the driver records the actual span-complete time so the next
 # lane can refit" -- E24 CHANGE 4 exists for exactly this. Not a new question.
+# E28 CHANGE 4: take the calibration points from E26's COMMITTED refit receipt,
+# which already carries E24's two plus E26's own measured third, instead of from
+# the two-point list frozen inside watch-set.json before either big boot existed.
+PRIOR = json.loads((E.parent / 'E26/cost-model-refit.json').read_text())['points']
 pts = [dict(boot=c['boot'], watches=c['watches'], span_complete_s=c['span_complete_s'])
-       for c in WS['cost_model']['calibration']]
+       for c in PRIOR]
 pts.append(dict(boot='e28a', watches=result['watch_entries'],
                 span_complete_s=round(result['span_complete_s'], 3)))
 n = len(pts)
```

## CHANGE 3 -- measure this lane's release latency instead of carrying E26's number

**File:** `e28_close.py`

E26's close tool writes `release_latency_ms=8` and `needed_sigkill=False` as LITERALS into its own final audit. Those were E26's measurements, and carried unchanged into E28 they would report E26's boot in E28's audit. Both are computed from this lane's own `e28a-result.json` instead. Nothing else in the tool moves.

```diff
--- e28_close.py (carried)
+++ e28_close.py (E28)
@@ -101,7 +101,10 @@
                watch_entries=result['watch_entries'],
                signal_utc=result['signal_utc'], process_end_utc=result['process_end_utc'],
                release_utc=result['release_utc'],
-               release_latency_ms=8, needed_sigkill=False),
+               release_latency_ms=round((datetime.datetime.fromisoformat(result['release_utc'])
+                                         - datetime.datetime.fromisoformat(result['process_end_utc'])
+                                        ).total_seconds()*1000, 3),
+               needed_sigkill=bool(result.get('needed_sigkill'))),
      probes=dict(title_boots_spent=1, title_boots_allowed=1,
                  lease_claims=1, lease_releases=1),
      mutations=dict(fork_source_edits=0, fork_commits=0, pushes=0, regenerations=0,
```

# E28 TOOLING DIFF TAIL COMPLETE
