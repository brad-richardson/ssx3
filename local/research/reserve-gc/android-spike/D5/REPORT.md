# D5 — Odin native exception attribution: REPORT

Question: which guest exception vectors are D1b's 35,646 in-race
`native_exc`/s, which guest instructions raise them, and what do they cost
the emulation thread. Tables only, no verdicts.

## Gate and method

Waited for M4: `M4/REPORT.md` was missing 02:50–04:33 UTC (13 polls, all
`M4/REPORT-missing`, lease M4 then absent; full log in `D5/waits.log`);
gate cleared 05:18 UTC (`M4/REPORT.md` present, LEASE absent, no process).
Device lease `D5` claimed before the first arm (removed at the end).
Same device rules as D1b: <50 °C wait per arm (elapsed below), kill only
on ≥110 °C or cpu7 <2.0 GHz >5 consecutive ticks (never triggered),
per-arm `performance_mode`/`fan_mode`/caps recorded, settings unchanged.

Instrument (temporary, never committed): at the `++m_native_exceptions`
site (`m_guest.pc` = vector, `m_guest.srr0` = faulting PC): (1) fixed
`u64` array indexed by `vector>>8` (classic vectors at 0x3–0xF,
0x8000xxxx aliases keep identity; none observed); (2) top-32 faulting-PC
table for 0x800; (3) `CLOCK_MONOTONIC` stamp at raise, closed on the first
later dispatch with `pc == srr0` (rfi return), per-vector `ns_total` +
timed count; a raise before return closes the open one as `nested`.
Prints at shutdown next to the `shutdown:` line as
`exc vector=.. count=.. ns_total=.. ns_mean=.. nested=..` and
`exc_pc vector=0x800 pc=.. count=..`. `ns_mean` = `ns_total`/`timed`.
Diff saved as `D5/instrument.patch`, NOT applied anywhere at the end.

Build: fresh dir `core-egl-d5-build`, M4's recipe (`M4/build-lse.sh`
flags verbatim), m4-src read-mostly + the instrument only.
`ninja -j8` (no dolrecomp procs; host lease M2 noted, load ~3.8).
Build exit 0. Binary `D5/moderngekko-run-d5-exc`:
`134a18773b56f58a62b81bd47e56ed1f3026b67f234f885d1f145d854e7a15ff`
(exc format strings verified in binary). Module on device:
`gGXBE69_recomp.so`
`1c6c89cf79c2cb35864d78dd071edb7457b67537f769de57c700ab6ac1286d31`.

m4-src restore: pre-edit shas recorded (`D5/preshas.txt`); the 3 edited
files restored from `.d5orig` backups (`cmp` identical each);
post-restore shas match pre-edit exactly (`D5/postshas.txt`); `.orig`
copies kept in `D5/`; no stray files left in m4-src.

## Runs (D1 `d1-base-a` launch shape, stock clocks throughout)

| arm | template | timeout | pre-launch settings | wait | thermals (full run) | counters |
|---|---|---|---|---|---|---|
| d5-exc-uncapped | aff-tpl | 300 | mode=1 fan=4 cpu7=4320000 cpu0=3532800 | 0s | tmax 104.3, cpu7 min/mean 3.283/4.214, 0 sub-2G ticks | native_exc=452719 hook_fb=441348 |
| d5-exc-capped | m6h | 300 | same | 1s | tmax 94.2, cpu7 min/mean 3.283/3.522, 0 sub-2G ticks | native_exc=185786 hook_fb=395810 |
| d5-exc-menu-pre | aff-tpl | 40 | same | 1s | tmax 103.5, cpu7 min/mean 3.283/3.564, 0 sub-2G ticks | native_exc=55384 hook_fb=373428 |

Affinity emu=80/video=40 verified at sample=10 in all three run.json.
Emu thread PSR=cpu7 throughout. uncapped race busy 0.92, capped 0.59
(sampler method, same as D1/analyze.py).

## Race verification without screenshots

Zero emulator screenshots on all three arms (0 files): m4-src gates
capture on `!headless` (`dolphin_runtime.cpp:488`), and these runs pass
`--headless` — that is the dead shot path, one line as scoped.
Per orchestrator steer, verification is by metric-speed pattern against
D1b stock arms: uncapped shows the race dip at samples 45–55
(1.207/1.145/1.562) and pause tail 2.22 at ≥120, matching D1b
base-stock-a/b sample-for-sample (menu-pre 0–40 series also matches to
±0.1); race window samples 43–57, HUD-timed 11 s wall. Capped runs locked
1.000 throughout; race window per D1b's screenshot-anchored capped1x
mapping (gate ~sample 125, pause ~150, 15 s wall). menu-pre ends at
sample 40 with menu speeds (2.13), before the 45–55 dip: valid baseline.
Note: menu-pre `hook_fb`=373428 here vs 11495 in D1b's pace-binary
menu-pre — different runner tree/patch stack; D5 subtractions below are
same-binary so self-consistent.

## Vector tables

Full-run `exc` lines sum to `native_exc` exactly on all three arms
(uncapped 452718+1, capped 185785+1, menu-pre 55383+1). Every counted
exception is vector 0x800 (FP-unavailable) except one 0xC00 syscall each.
No 0x300/0x400/0x600/0x700/0x900/0xF00, no 0x8000xxxx aliases, no
OVERFLOW line. nested: 13 / 4 / 1.

Race-window rates (run − menu-pre over the HUD-timed window):

| run | vector | race count/s | ns_mean (full-run) | ns_total race | % of race emu CPU-s |
|---|---|---|---|---|---|
| uncapped | 0x800 | 36121 | 1408 | 0.5745 s | 5.68 |
| uncapped | 0xc00 | 0 | 313 | ~0 | ~0 |
| capped | 0x800 | 8693 | 2140 | 0.3345 s | 3.78 |
| capped | 0xc00 | 0 | 312 | ~0 | ~0 |
| menu-pre | 0x800 | 1385 (wall rate, menus) | 1142 | — | — |

Emu CPU-s: uncapped 0.92×11 = 10.16 s; capped 0.59×15 = 8.81 s.
Capped caveat: baseline menu-pre used the uncapped template, and the
capped race window is D1b-mapped (no shots); arithmetic is as briefed.
Observed side fact for the owner: capped full-run 0x800 (185785) is far
below uncapped race alone (~397k) for the same movie+module, so the
per-guest-second fault count is host-timing dependent (lazy-FP
re-faults), not a fixed property of the guest stream.

## Top-32 faulting PCs for 0x800 (raw words from main.dol)

No PowerPC disassembler exists under `tools/` (only a LUN-chunk
round-tripper), so raw words per the brief. Nearly all faulting words are
FP loads/stores (0xC=lfs, 0xD=stfs, 0xE=psq_l, 0xCB=lfsx). The same two
PCs top all three runs (uncapped 133243×2 = 59% of its 0x800; capped
57280/57279 = 62%; menu-pre 19942/19941 = 72%).

uncapped (counts sum within the 0x800 total; only top 32 printed):

| pc | count | word | prev | next |
|---|---|---|---|---|
| 0x8026e1a0 | 133243 | c822cc38 | 38000014 | 3c804330 |
| 0x80264b48 | 133243 | dbe100c0 | 900100d4 | f3e100c8 |
| 0x801cd250 | 40079 | c822bc40 | 7c0802a6 | 90010034 |
| 0x801a8d18 | 33100 | c002b134 | 41820048 | 7ec3b378 |
| 0x8019ce5c | 28417 | c0230000 | 80010014 | 7c0803a6 |
| 0x8021a754 | 8910 | e3e10048 | 4e800421 | 80010054 |
| 0x8013ece8 | 5617 | e3e10018 | 4bffefbd | 80010024 |
| 0x801d6c04 | 5321 | c0040000 | 40810114 | d0050004 |
| 0x8013b344 | 5311 | c862a410 | 6c008000 | 9061000c |
| 0x8013ec94 | 5231 | c002a3ec | 40820058 | fc1f0040 |
| 0x8022db04 | 4387 | c0260004 | 408200f8 | c0040004 |
| 0x8022faa4 | 3821 | dbe10030 | 90010044 | f3e10038 |
| 0x8021d7b0 | 3621 | ecba702a | 60000020 | c1a10168 |
| 0x8021cd84 | 2232 | dbe10300 | 9421fcf0 | f3e10308 |
| 0x8022ddf0 | 2150 | dbe100c0 | 900100d4 | f3e100c8 |
| 0x8022c094 | 1727 | c01e0000 | 38630001 | 38e70001 |
| 0x8021a178 | 1671 | c842c448 | 7c0802a6 | 90010094 |
| 0x8021d7a0 | 1586 | c002c370 | 60000010 | fc0d0040 |
| 0x8022d950 | 1524 | c1040000 | 3be00000 | d1010008 |
| 0x8021c6a0 | 1327 | d3f9001c | 90990010 | 808f0e88 |
| 0x8022e584 | 1318 | c022c370 | 40820018 | 38600000 |
| 0x8013f86c | 1121 | c842a410 | 7c630774 | 6c638000 |
| 0x8015c714 | 1099 | e3e10018 | 4bffc0ad | 80010024 |
| 0x80233afc | 1050 | c8010018 | 819f000c | 39240006 |
| 0x801cd04c | 1034 | c862bc40 | 7c0802a6 | 90010024 |
| 0x8014b9b4 | 923 | c0430008 | 38600000 | c0230004 |
| 0x8014ce10 | 889 | c0230030 | 4e800421 | c0030034 |
| 0x80222870 | 866 | c0270028 | 55000e3c | c0470024 |
| 0x8021bdfc | 862 | c3d10000 | 81d60008 | 540007ff |
| 0x8013eabc | 859 | cbe10018 | 80010024 | 83e10014 |
| 0x8002d00c | 812 | e3e10338 | 4bffed45 | cbe10330 |
| 0x80155c64 | 745 | e3e10048 | 48009791 | cbe10040 |

capped top 32 (same top-2 PCs; order of the top pair swaps):

| pc | count | word |
|---|---|---|
| 0x80264b48 | 57280 | dbe100c0 |
| 0x8026e1a0 | 57279 | c822cc38 |
| 0x801cd250 | 17328 | c822bc40 |
| 0x801a8d18 | 10354 | c002b134 |
| 0x8019ce5c | 8533 | c0230000 |
| 0x801d6c04 | 5321 | c0040000 |
| 0x8021a754 | 3201 | e3e10048 |
| 0x8013b344 | 2364 | c862a410 |
| 0x8013ece8 | 1649 | e3e10018 |
| 0x8013ec94 | 1589 | c002a3ec |
| 0x8022db04 | 1489 | c0260004 |
| 0x8022faa4 | 1275 | dbe10030 |
| 0x8021d7b0 | 1224 | ecba702a |
| 0x801cd04c | 1034 | c862bc40 |
| 0x8002d00c | 812 | e3e10338 |
| 0x8022ddf0 | 723 | dbe100c0 |
| 0x8021cd84 | 708 | dbe10300 |
| 0x8021a178 | 591 | c842c448 |
| 0x8021d7a0 | 535 | c002c370 |
| 0x8022c094 | 517 | c01e0000 |
| 0x8022d950 | 501 | c1040000 |
| 0x8021c6a0 | 442 | d3f9001c |
| 0x80098180 | 425 | dbe10160 |
| 0x8022e584 | 424 | c022c370 |
| 0x8002c018 | 389 | dbe10330 |
| 0x8013f86c | 339 | c842a410 |
| 0x80233afc | 339 | c8010018 |
| 0x8015c714 | 325 | e3e10018 |
| 0x8021bdfc | 309 | c3d10000 |
| 0x8014b9b4 | 285 | c002b134 |
| 0x801a8db0 | 282 | c002b134 |
| 0x80222870 | 271 | c0270028 |

menu-pre top 32 (same top-2 PCs again; menu-only faulters include
0x8024xxxx/0x801d2144/0x801046fc not prominent in-race):

| pc | count | word |
|---|---|---|
| 0x80264b48 | 19942 | dbe100c0 |
| 0x8026e1a0 | 19941 | c822cc38 |
| 0x801cd250 | 6146 | c822bc40 |
| 0x801d6c04 | 4097 | c0040000 |
| 0x801cd04c | 1034 | c862bc40 |
| 0x8013b344 | 917 | c862a410 |
| 0x8002d00c | 812 | e3e10338 |
| 0x80098180 | 425 | dbe10160 |
| 0x8002c018 | 389 | dbe10330 |
| 0x8022db04 | 142 | c0260004 |
| 0x8024a1a4 | 111 | e3e10028 |
| 0x8021f4b0 | 106 | c822c448 |
| 0x8021a178 | 101 | c842c448 |
| 0x8022e544 | 100 | c022c454 |
| 0x80249ff8 | 85 | dbe10020 |
| 0x8024babc | 84 | c842c830 |
| 0x8024372c | 67 | e3e102d8 |
| 0x801d2144 | 62 | dbe10030 |
| 0x80243580 | 50 | d0230028 |
| 0x80222b00 | 45 | c0270028 |
| 0x80210764 | 39 | c8a2c368 |
| 0x8022d950 | 36 | c1040000 |
| 0x8022c094 | 35 | c01e0000 |
| 0x8022ddf0 | 33 | dbe100c0 |
| 0x8021a754 | 28 | e3e10048 |
| 0x801046fc | 21 | c0029a50 |
| 0x80222870 | 20 | c0270028 |
| 0x80244e1c | 20 | dbe10028 |
| 0x8022c1ac | 19 | e3e10148 |
| 0x802475e4 | 18 | dbe10150 |
| 0x8024a090 | 15 | c01c03d8 |
| 0x8021f954 | 15 | e3e10298 |

## Exact commands

- Configure/build (M4 recipe verbatim, BUILD swapped; log
  `D5/build-d5.log`): cmake per `M4/build-lse.sh` with
  `-B core-egl-d5-build`, then
  `ninja -C core-egl-d5-build -j8 moderngekko moderngekko-module-info
  moderngekko-run` (no dolrecomp procs; brief rule).
- Instrument apply/restore: `/tmp/d5_apply.py <m4-src root>` (scratch,
  not committed); backups `*.d5orig` beside sources, moved to `D5/` as
  `*.orig` after a byte-identical restore.
- Arms (`run` = `python3 tools/android_trial.py run`, serial 622c49b1,
  lease D5, <50 °C gate + settings snapshot before each):
  `run --binary D5/moderngekko-run-d5-exc --tag d5-exc-uncapped --output
  D5/d5-exc-uncapped-receipts --template aff-tpl ... --timeout 300`;
  `d5-exc-capped`: `--template m6h ... --timeout 300`;
  `d5-exc-menu-pre`: `--template aff-tpl ... --timeout 40`
  (all: `--movie m3-menu.dtm --module gGXBE69_recomp.so --graphics OGL
  --idle on --affinity emu=80,video=40 --sampler --screenshot-seconds 2`).
- DOL words: `/tmp/d5_dol.py <pcs...>` (scratch) against
  `local/source/gamecube/ssx3/sys/main.dol`.

## File list

`D5/`: `REPORT.md` (this file), `instrument.patch`, `waits.log`,
`run-notes.log`, `build-d5.log`, `preshas.txt`, `postshas.txt`,
`binary-sha.txt`, `module-sha.txt`, `moderngekko-run-d5-exc` (134a1877…),
`StaticRecompCore_{Run.cpp,.cpp,.h}.orig` (pre-instrument copies),
`d5-exc-uncapped-receipts/`, `d5-exc-capped-receipts/`,
`d5-exc-menu-pre-receipts/` (each: err/out, GFX+Dolphin-post, run.json,
sampler.log, empty shots dir). Fresh dir `core-egl-d5-build` (build tree,
kept). Repo: no changes, no commits.

## What I could not do

- HUD screenshots: dead by construction in m4-src (`!headless` gate);
  race verified by metric pattern + tail parity instead, per steer.
- Disassembly: no PowerPC disassembler under `tools/`; raw words only.
- Capped race-window isolation and baseline share the uncapped-template
  caveats stated above; per-sample exc timelines don't exist (shutdown
  totals only).
- No verdicts: tables above are the deliverable.
