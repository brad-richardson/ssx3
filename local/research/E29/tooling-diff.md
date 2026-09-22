# E29 tooling changes — full diffs against the carried files

## CHANGE 1+2+3 — e29_common.py
```diff
--- e29_common.py.carried	2026-09-22 12:12:09
+++ e29_common.py	2026-09-22 12:12:10
@@ -4,26 +4,37 @@
 E = Path(__file__).resolve().parent
 W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
 R = W / 'PS2Recomp'
-# The protected build tree E15-E23 ran on, wiped by the host restart that opened
-# E24 red and REBUILT BIT-IDENTICALLY by E25 (runner e462e448..., suite
-# 2152e5ad..., both byte-equal to the lost pins). E29 BUILDS NOTHING and EDITS
-# NOTHING: it spends its one boot on the binary already standing at this exact
-# path, which is the very binary E23 and E26 booted. Host-side MPEG.cpp logging
-# is E29's lane, not this one; E29 is a GUEST-half confirmation on the EXISTING
-# byte-identical binary. The other two trees stay absent and are NOT rebuilt.
+# E29 CHANGE 1 -- the DEV-ONLY bypass build lives in a NEW dir ON THE SSD. The
+# internal volume cannot hold two trees (floor rule), and the brief forbids a
+# /tmp build outright. The mainline tree below is NOT touched, NOT rebuilt and
+# NOT deleted; E29 only pins it.
+NEWSSD = W / 'e29-movie-bypass-build'
+# The MAINLINE protected build tree (E18's recipe, rebuilt bit-identically by
+# E25). E29 BUILDS NOTHING HERE and EDITS NOTHING HERE: it pins this tree as the
+# reference the 458 suite and the e28a receipts were taken on, and builds its
+# own DEV-ONLY bypass binary into NEWSSD instead.
 B0 = Path('/tmp/e18-mpeg-link/runtime')
+MAINLINE_RUNNER = B0 / 'ps2xRuntime/ps2EntryRunner'
+MAINLINE_SUITE = B0 / 'ps2xTest/ps2x_tests'
 PROTECTED_BUILDS = [Path('/tmp/p1-link/runtime'), Path('/tmp/e17-map-link/runtime'), B0]
-NEWB = B0
-B = Path(os.environ.get('E29_BUILD_DIR', str(B0)))
+# E29 CHANGE 1 (cont.) -- NEWB is the bypass build, on the SSD.
+NEWB = NEWSSD
+B = Path(os.environ.get('E29_BUILD_DIR', str(NEWSSD)))
+BYPASS_RUNNER = NEWSSD / 'ps2xRuntime/ps2EntryRunner'
+BYPASS_SUITE = NEWSSD / 'ps2xTest/ps2x_tests'
 OUT = Path('/tmp/e29-no-codegen')
 P = W / 'P1'
 M = 1024**2
 G = 1024**3
 BASE_SHA = '3adc0478b6d2260acdd28a249466f2eef9a20176'
-# E29 CONTRACT: internal reservation 3 GiB, the brief's declared value. E29's
-# Mission 0 is verify-or-restore; on path (a) no build runs, so the reservation
-# is declared, not consumed. FLOOR and GUARD stay 2 GiB + 0.5 GiB, untouched.
-IRES = 3*G
+# E29 CHANGE 2 -- the brief caps the INTERNAL volume at a 512 MB DELTA, because
+# E29 runs no internal build at all (the bypass tree is on the SSD). E28's 3 GiB
+# reservation was sized for a tree this lane does not create. FLOOR and GUARD
+# stay 2 GiB + 0.5 GiB, untouched. SSD: NEW build dir <= 6 GB, all NEW e29-*
+# paths <= 16 GB.
+IRES = 512*M
+BUILD_CAP = 6*G
+SSD_CAP = 16*G
 
 def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
 def sha(p):
@@ -52,7 +63,11 @@
         return total
     except FileNotFoundError: return 0
 def sample():
+    # E29 CHANGE 3 -- the NEW SSD build dir and every NEW e29-* path are charged
+    # to the SSD caps; the internal figure now covers evidence only, because
+    # this lane creates no internal tree.
     paths = list(P.glob('e29-*')) + list(P.glob('._e29-*')) + list((P/'run').glob('*e29*'))
+    paths += list(W.glob('e29-*')) + list(W.glob('._e29-*'))
     # The shared function trace is charged even though its name lacks E29.
     paths += [P/'run/ps2_log.txt', P/'run/._ps2_log.txt']
     allocation_receipt=E/'fork-allocation-before.json'
@@ -66,17 +81,19 @@
                 except FileNotFoundError:pass
     owned=sum(size(p) for p in set(paths))
     return dict(utc=utc(), internal_free=shutil.disk_usage('/private/tmp').free,
-                internal_allocated=size(NEWB)+size(OUT)+size(E), build_allocated=size(NEWB), codegen_allocated=size(OUT), evidence_allocated=size(E),
+                internal_allocated=size(OUT)+size(E), codegen_allocated=size(OUT), evidence_allocated=size(E),
+                build_allocated=size(NEWB),
                 ssd_free=shutil.disk_usage(W).free, ssd_allocated=owned+fork_delta,
                 ssd_owned_paths_allocated=owned,fork_positive_growth=fork_delta,
                 ssd_paths=[str(p) for p in sorted(set(paths)) if p.exists()])
 def bound(s):
     if OUT.exists(): return 'unexpected_codegen'
+    if s['build_allocated'] >= BUILD_CAP - 256*M: return 'ssd_build_dir_cap'
     if s['internal_allocated'] >= IRES-128*M: return 'internal_allocation'
     if s['internal_free'] <= 2*G+512*M: return 'internal_floor'
-    if s['ssd_allocated'] >= 16*G-512*M: return 'ssd_allocation'
+    if s['ssd_allocated'] >= SSD_CAP-512*M: return 'ssd_allocation'
     if s['ssd_free'] <= 2*G+512*M: return 'ssd_floor'
 def admission(s):
     assert not bound(s), s
     assert s['internal_free'] >= 2*G+512*M+max(0,IRES-s['internal_allocated']), s
-    assert s['ssd_free'] >= 2*G+512*M+max(0,16*G-s['ssd_allocated']), s
+    assert s['ssd_free'] >= 2*G+512*M+max(0,SSD_CAP-s['ssd_allocated']), s
```

## CHANGE 4 — e29_open.py
```diff
--- e29_open.py.carried	2026-09-22 12:12:25
+++ e29_open.py	2026-09-22 12:12:25
@@ -1,8 +1,10 @@
 """E29 open: fork allocation baseline + initial admission against the contract.
 
-E29 builds nothing and edits nothing in the fork. The allocation baseline is
-taken anyway so the lane's "fork growth 0" claim at close is MEASURED rather
-than assumed -- the same discipline E25 used.
+E29 CHANGE 4, declared: unlike E22-E28, this lane DOES mutate the fork worktree
+-- exactly twice, as the brief permits (the `e29-movie-bypass` checkout and the
+Mission-1 bypass diff) -- and DOES build, into a NEW dir on the SSD. So the
+baseline is not here to prove "fork growth 0"; it is here to MEASURE the growth
+the two permitted mutations cause, and to prove at close that nothing else did.
 """
 from e29_common import *
 
@@ -18,15 +20,16 @@
 s = sample()
 admission(s)
 save('admission-open.json', dict(utc=utc(), reservation_internal=IRES,
-                                 reservation_ssd=16*G, floor=2*G, guard=512*M,
+                                 reservation_ssd=SSD_CAP, build_dir_cap=BUILD_CAP, floor=2*G, guard=512*M,
                                  sample=s, bound=bound(s),
                                  internal_free_required=2*G+512*M+max(0, IRES-s['internal_allocated']),
-                                 ssd_free_required=2*G+512*M+max(0, 16*G-s['ssd_allocated']),
-                                 note=('internal_allocated is dominated by the 1.77 GB E18 build tree E25 '
-                                       'rebuilt bit-identically; E29 runs no build step, so the 3 GiB '
-                                       'reservation is declared and not consumed.')))
+                                 ssd_free_required=2*G+512*M+max(0, SSD_CAP-s['ssd_allocated']),
+                                 note=('E29 CHANGE 2/3: internal_allocated now covers EVIDENCE ONLY -- the '
+                                       '1.6 GB mainline E18 tree at /tmp/e18-mpeg-link is pinned, not owned, '
+                                       'and is neither rebuilt nor deleted. The bypass build is charged to '
+                                       'the SSD caps (build dir <= 6 GB, all e29-* <= 16 GB).')))
 print('fork allocation paths', len(allocated))
 print('internal free', s['internal_free'], 'required', 2*G+512*M+max(0, IRES-s['internal_allocated']))
-print('ssd free', s['ssd_free'], 'required', 2*G+512*M+max(0, 16*G-s['ssd_allocated']))
+print('ssd free', s['ssd_free'], 'required', 2*G+512*M+max(0, SSD_CAP-s['ssd_allocated']))
 print('bound', bound(s))
 print('# E29 OPEN TAIL COMPLETE')
```
