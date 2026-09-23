# N4 log receipts (transcribed from observed tool output, 2026-09-23)

## branch-log.txt
fetch: `git fetch origin` -> origin/ssx3 3d4feed..e57b5f8 (matches brief pin).
rebase: `git checkout n2-android; GIT_SEQUENCE_EDITOR="sed -i -e /8c04667/d -e /b003c8a/d" git rebase -i --onto origin/ssx3 3adc047`
  -> "Successfully rebased and updated refs/heads/n2-android." (3 picks, no conflicts;
     H1 CMakeLists hunk auto-emptied against upstream)
final `git log --oneline -8`:
  f9d78da [N4-local] Profileable + show-when-locked manifest; PNG dumps via memory-encode plus ofstream (n2-android only, never push)
  3da81ad [N3-local] Package arm64-v8a only for the Odin install build (n2-android only, never push)
  322e55b [N3-local] Android env-file shim plus parser unit test (n2-android only, never push)
  8e7d5ac [N2-local] H1 port: PS2X_GAME_CODEGEN_DIR game-objects lib + in-tree drop (n2-android only, never push)
  e57b5f8 Present full frames by default behind PS2X_DEINTERLACE (default weave)
  dcecf13 I18 tap: frame/GS line on the P1c periodic console sampler
  5461ad8 [E31] DEV-ONLY scripted pad input behind PS2X_PAD_SCRIPT (default OFF)
  6526329 [E29] DEV-ONLY startup-movie bypass behind PS2X_SKIP_MOVIE (default OFF)
`git rev-parse n2-android` = f9d78da0a3ae7a806149445fee6fc6d8a162d862
status clean except pre-existing untracked android/gradlew* wrapper files. No push.

## build4-bars.txt
BUILD4_START 2026-09-23T01:31:55Z branch=n2-android head=f9d78da
BUILD4_END 2026-09-23T01:32:20Z EXIT=0 (BUILD SUCCESSFUL, 25 s incremental)
SO=.../cxx/RelWithDebInfo/282v703p/obj/arm64-v8a/libps2EntryRunner.so
  ELF 64-bit LSB shared object, ARM aarch64, version 1 (SYSV), dynamically linked,
  BuildID[sha1]=8e31384489df797fae58e1ab7751eb4c453528f9, with debug_info, not stripped
  905605320 B, sha 9528e21aff8bcba6e0dc819654129cb33da37e408a56fecb397c32171c67915c
APK=.../outputs/apk/release/app-release.apk
  134164820 B, sha d93b81a72d101b4b61fa54fb66f560b7eb8f91255e579a66df79597e6ee76229
APK members: META-INF/*, classes.dex, lib/arm64-v8a/libps2EntryRunner.so (only ABI),
  AndroidManifest.xml, resources.arsc
T ANativeActivity_onCreate + T main present.
STR[PS2X_SKIP_MOVIE]=1 STR[PS2X_PAD_SCRIPT]=2 STR[ps2x.env]=4 STR[ps2x.env: set ]=1
STR[SLUS_207.72]=3 STR[DEINTERLACE]=1 WRITEPNGBYTES_SRC=3

## so-probe.txt (unstripped .so, llvm-nm)
SO_SIZE=905605320
DEFINED_MANGLED_SUB_STAR_T=9457
UNDEF_MANGLED_SUB_STAR_U=0
EXPORTIMAGETOMEMORY=1 MEMFREE=1 WRITEPNGBYTES_LOCAL=1
APK_SHA=d93b81a7... (full in table) SO_SHA=9528e21a... (full in table)

## apk-sha reads (mini, COPYFILE n/a — internal disk)
read1: d93b81a72d101b4b61fa54fb66f560b7eb8f91255e579a66df79597e6ee76229
read2: d93b81a72d101b4b61fa54fb66f560b7eb8f91255e579a66df79597e6ee76229
(build tree + Windows landing agree; see build4-bars)

## aapt-profileable.txt (aapt dump xmltree app-release.apk AndroidManifest.xml)
E: profileable (line=21) / A: android:shell=0xffffffff
activity: A: android:showWhenLocked=0xffffffff, A: android:turnScreenOn=0xffffffff

## simpleperf-pid-denied.txt
`adb shell simpleperf record -g -p 309 -o /data/local/tmp/n4/perf1.data --duration 30`
  -> "simpleperf E event_selection_set.cpp:739] failed to open perf event file
      for event_type cpu-cycles: Permission denied" (no perf1.data written)
`adb shell simpleperf record --app com.ps2x.runner -o /data/local/tmp/n4/perf-app.data --duration 10`
  -> kptr_restrict warning; "Recorded for 9.99316 seconds."; "Samples recorded: 66172. Samples lost: 0."
device simpleperf version: 1.build.eng.Odin3.20260204.171202
`dumpsys package com.ps2x.runner | grep -ci profileable` = 0 (display quirk; aapt proves flag in APK)

## title record / menu record
`simpleperf record -g --app com.ps2x.runner -o /data/local/tmp/n4/perf-title.data --duration 30`
  -> "Recorded for 29.9971 seconds."; "Samples recorded: 194954. Samples lost: 0." (36,154,471 B)
`simpleperf record -g --app com.ps2x.runner -o /data/local/tmp/n4/perf-menu.data --duration 30`
  -> "Recorded for 29.9971 seconds."; "Samples recorded: 128639. Samples lost: 0." (22,570,193 B)

## tickbins.txt (tick-gated [frame:dump], device clock)
launch1 n=767: bin0 +0-30s n=744 tick 0->812 rate=27.1/s; bin1 +30-60s n=23 tick 813->835 rate=23.5/s
  whole: tick 0->835 / 30.951 s = 27.0/s (45.0% of 59.94)
launch2 n=2215: bin0 25.1/s (0->752); bin1 24.7/s (753->1493); bin2 24.1/s (1494->2215);
  bin3 +90-120s 2.2/s (2216->2279); bin4 +120-150s 0.2/s (2280->2283); bin5 0.2/s (2284->2285)
  whole: tick 0->2285 / 158.799 s = 14.4/s
pad log launch2: `armed n=2`, `press i=0 now=25001ms at=25000ms hold=5000ms buttons=0x0008`,
  `press i=1 now=90035ms at=90000ms hold=5000ms buttons=0x4000`
late-run hashes: 58 distinct fnv1a in last 60 dumps (ticks 2280-2285:
  4b21fc56 c49358e e6a2fa35 ea2e6d3c 7922d81b 4b996609)
upload-latest.txt L1: seq=764 tick=833 512x448 fbp=112/112 fnv1a=6815bf97
upload-latest.txt L2: seq=2214 tick=2285 512x448 fbp=112/112 fnv1a=4b996609
upload-latest.png L1: 320,973 B, `file` = PNG image data, 512 x 448, 8-bit/color RGBA
crash census both logs: 0 unimplemented/fatal/exception/FATAL

## addr2line.txt (llvm-addr2line -f -C on unstripped .so; function | file:line)
0xdff210 __invoke std::function read-fn wrapper | invoke.h:150  -> gs bucket
0xdfbef4 SampleTexture::$_0::operator() | gs_cpu_backend.cpp:1051 -> gs
0xdfbf14 wrapTextureCoordinate | gs_cpu_backend.cpp:128 -> gs
0xdfbf68 clampInt | ps2_gs_common.h:49 -> gs
0xdfbf90 SampleTexture::$_0::operator() | gs_cpu_backend.cpp:1053 -> gs
0xde581c/0xde5824/0xde5818 fnv1a32 | ps2_runtime.cpp:404-407 -> diag
0xdfc04c ReadVramUnlocked | gs_cpu_backend.cpp:648 -> gs
0xdfbff4 SampleTexture::$_0::operator() | gs_cpu_backend.cpp:0 -> gs
0xdfc014 __function::__value_func::operator() | function.h:428 -> gs
0xdfc194 SampleTexture::$_0::operator() | gs_cpu_backend.cpp:1078 -> gs
0xdff228 __invoke wrapper | invoke.h:150 -> gs
0xdfc148 applyTexa | gs_cpu_backend.cpp:0 -> gs
0xe105d8 calculateFmacExactResult::$_1::operator() | ps2_vu1_core.cpp:236 -> vu1
0x79688bc/0x7968cc8 __addtf3 | addtf3.c -> vu1 (soft-float)
0x7968ef0/74/1c/5c/edc/f3c/ee0/f64/eec/f60/ee8 __extendsftf2 -> vu1
0x7968d08/0x7968d3c __eqtf2 | comparetf2.c -> vu1
0x7969398 __multf3 | multf3.c -> vu1
0xe46cc0/e46c98 insertion_sort publishSnapshot | sort.h -> sched
0xe459ec insertion_sort publishSnapshot | sort.h -> sched
0xe449c8/e43e24 introsort dispatchIrq | sort.h -> sched
0xe10610 fortify memcpy (inlined in VU1 TU) | string.h:53 -> vu1
0xe10648 normalizeOperand | ps2_vu1_core.cpp:114 -> vu1
0xe1068c calculateFmacExactResult::$_0::operator() | ps2_vu1_core.cpp:232 -> vu1
0xde65cc syncCoreSubsystems::$_1::operator() | ps2_runtime.cpp:785 (VIF dispatch)
0xde7f20 PS2Runtime::run::$_0::operator() | ps2_runtime.cpp:3204 (GameThread entry)
0xde5a04 dumpPresentationFrame | ps2_runtime.cpp:487
0xde6218 writePngBytes | ps2_runtime.cpp:421
range rules: 0xdf0000-0xe00000 gs; 0xde5800-0xde5900 diag; 0xe10500-0xe10800 vu1;
  0xe43e00-0xe47000 sched; 0x7968000-0x796a000 vu1

## buckets.txt (scripts/buckets.py over full self reports)
title rows=1946 total=98.49: gs 59.53 / diag 28.43 / sys 4.12 / vu1 2.15 /
  plt 1.64 / other_unresolved 1.40 / other 0.70 / guest 0.39 / sched 0.09 / stl 0.04
menu rows=1497 total=99.16: vu1 91.55 / plt 4.36 / sys 2.03 / gs 0.59 /
  other 0.34 / diag 0.29 / guest 0.00 / stl 0.00 / other_unresolved 0.00 /
  sched 0.00 / present 0.00
DSO census title: our lib 93.88 / libc 3.79 / kernel.kallsyms 0.38 / vdso 0.22 /
  Adreno GLES 0.10 / linker64 0.08
DSO census menu: our lib 96.86 / libc 1.15 / vdso 0.84 / kernel.kallsyms 0.21 /
  Adreno GLES 0.04
sub_ census: title 163 rows sum 0.39 (top sub_00376938 0.120, sub_00398A60 0.080);
  menu 19 rows sum 0.00

## launch table details
L1: install Success; lease N4 2026-09-23T01:40Z; keyguard showing=false;
  SLUS 1b49d05c... == N3 pin; ISO 3c2f8eb1... re-hashed on device; env d8321b85...
  am start pid 309 (same pid all run); BACK t+6; focus scap t+10 (title, no dialog);
  title scap t+28; frames upload-39/40.png + fallback-0/1.png + latest pairs on device.
L2: env + pad script (ps2x-launch2.env sha on device not re-read; pushed 262 B OK);
  am start pid 1454; BACK t+6; prescript scap t+100 = Select Character (Zoe);
  settled t+130 = Select Character; postrec = Select Character; all 4 scaps distinct SHAs.
closeout: force-stop (pidof exit 1), rm -rf /data/local/tmp/n4 (verified gone),
  lease `LEASE_FREE N4 done`; bytesize C:/n4-* + symfs removed; ~/n4work 63 MB.
