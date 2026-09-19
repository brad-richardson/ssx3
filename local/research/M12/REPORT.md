# M12 — Same-frame partition: alternating NOP streams + dual ref2 references: REPORT

Same-frame slot-0 partition via alternating NOP streams with dual
(per-window) ref2 references, plus slot-36 indexed-path decode. Desktop
only. Runbook `local/muse/prompts/M12.md`. No `adb`, no device.
Tables, no verdicts.

Header read first: `local/research/M11/REPORT.md` (all of it: the
cross-frame partition rows, "What I could not do" item 2 — same-frame
partition via alternating NOP streams with dual ref2 references — which
IS this brief — plus items 1 and 3) and the base header
`local/research/M11/m11_replay_context.h`.

Time box 6 hours; used about 1.5. Zero lease waits (four claim/release
pairs plus one annotation; the P1t agent never observed holding the
lease; never forced).

## Baseline note (read before the tables)

The M11 header on disk (`local/research/M11/m11_replay_context.h`, clean
tree) hashes to
`f3383745b6edd023609857afcc30274caee4ea0cff424079865fea0b2a7d6e54`
via `shasum -a 256` (trust `shasum`, not memory; matches the M11 report's
pinned prefix).
Step 1 copied the on-disk file verbatim to
`local/research/M12/m12_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8/M9/M10/M11 mechanism is kept in
all steps: PE mask, verbatim execute stream, restore, stall, pipe snapshot,
watched-window re-hash, `done`, XFB hash + scratch redirect, side-effect
counters, continuation capture, scoped bus, `m6frame`, presenter tracing,
record guard, trig_imx probe, M7 full/delta transforms, per-replay xdiff
stats, M8 census/slot/proj modes with stream-epoch census, M9 VAT walk +
slot/survival, M10 order/matrix/epoch/occ walks + NOP/RAM/ref2 arms, M11
slot chain + idx decode + NOPSHR/NOPIDX/NOPTEXT arms. All M12 additions are
env-gated with defaults that preserve M11 behavior (`SSX_M12_SLOT`
unset); the committed header is the step-2 header (step 3 needs no new
header; §Header diffs, step 3), from which every step's run is
reproducible via env.

M12 modes (`SSX_M12_SLOT=N`, 0-63, forces M11+M10 mode 2 on the same slot,
so each M12 run carries its own M11 decode, M10 order/matrix/epoch/occ
receipts plus its M9 VAT census, M9 survival and M8 census as
cross-checks; M12 takes precedence over `SSX_M11_SLOT`; M11/M10 env alone
= M11/M10 behavior):
`SSX_M12_RAMREF=1` (same split as `SSX_M11_RAMREF`: implies RAMCOPY,
pristine replays 0–99, delta 100–199, rendered-reference diff; needs
`NOPCONS=0`),
`SSX_M12_ALT=1` (M12 mode only: alternating-NOP same-frame partition;
implies RAMCOPY and the same 100-split, but with per-window pristine
references; the single `m10_ref2` stays off). There are no M12 NOP
selectors; ALT runs set none of the M11 selectors (guard echoed in
`m12_win`).

Window design (recorded here; receipt in `m12_win`): window =
`replays % 4` — 0 verbatim total, 1 NOPSHR set (shared-path consumers
removed, indexed-only surviving), 2 NOPIDX set (indexed-position draws
exposed to the slot removed, shared-only surviving), 3 NOPTEXT set
(texture-epoch draws removed, non-texture-mediated surviving). 50
replays per window (25 pristine + 25 delta); one pristine reference per
window shape at replays 96, 97, 98, 99 (each window's last pristine
replay). The three NOP stream pairs use the exact M11 hit sets and are
fail-closed per shape (`ok=0` leaves that shape verbatim).

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M11. `m12-det*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M12\n'`, removed after each run);
the log is `local/research/M12/waits.log` (zero waits, four
claim/release pairs, one annotation, never forced). Builds ran any time;
no build ran during a run.
`complete_hazard_resets` (harness field, as observed): all arms 0;
every sequence is 200/200 with `done` and clean counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `f3383745…` (= M11 on disk) | `players/m12-baseline` | `m12-det-run` (`m12-det`, `SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M9_SURV=1`) | `m12-det-probe.jsonl` |
| 2 alt | `14f7c7f7…` | `players/m12-alt` | `m12-det2-run` (`m12-det2`, `SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1`) | `m12-det2-probe.jsonl` |
| 3 slot36 | `14f7c7f7…` (= step 2) | `players/m12-slot36` | `m12-det3-run-failed` (`m12-det3`, `SSX_M12_SLOT=36 SSX_M12_RAMREF=1 SSX_M9_SURV=1`) | `m12-det3-probe.jsonl-failed` |
| 3 slot36 re-run | `14f7c7f7…` | `players/m12-slot36` | `m12-det4-run` (`m12-det4`, same env) | `m12-det4-probe.jsonl` |

The committed header is `14f7c7f7…`. Step 3 needs no new header code (the
M12 slot chain + RAMREF alias + forced M11 decode already cover
`SSX_M12_SLOT=36`; step3-vs-step2 `diff -u` is empty), so every arm above
is reproducible from the committed header via env. The `m12-det3` attempt
exited -5 post-sequence on live resume with a complete 200/200 `done`
sequence (missing `resume_xfb` only), kept as `-failed` (see `waits.log`);
its decode + ref2 rows are tabulated as a second slot-36 frame sample,
marked `-failed`. The `m12-slot36` player hashes identically to `m12-alt`
(same header compiles to the same binary).

Player dirs live under `local/research/M12/players/` (the build driver
requires outputs under `local/`; they are gitignored build outputs, never
committed). Run dirs and every probe jsonl live under
`/Volumes/Extreme SSD/m12/` (symlink-free; `realpath` is the path as
written). Probes, runs and players are not committed.

## Step 1 — baseline (M11 end state reproduces)

Unmodified copy, M11 slot-0 true-delta env. `analyze.py` prints 200 rows +
`done` + `xfb_equal_scratch=0/200` (forced-RAM signature, as M11 det) +
`live_xfb_untouched=1` + `dafter_live`/`dframe`/`dpres`/`dimx` all 0/0 +
`pediff`/`vidiff` 0/0. Control for steps 2–3.

Seam-application receipt (`xform_stats`, slot mode):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 298000 |
| `hits` | 11700 (= 100 × 117 covering loads; first half counting-only) |
| `regcalls` | 0 |

Own-frame M9 census, m12-det (draws=2266, verts=38217; VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 2193 | 73 | n/a | n/a |
| Tex0 | 2266 | 0 | 2225 | 2225 |
| Tex1 | 2212 | 54 | 480 | 426 |
| Tex2 | 2266 | 0 | 61 | 61 |
| Tex3 | 2266 | 0 | 34 | 34 |
| Tex4-7 | 2266 | 0 | 0 | 0 |

Shared reach: Pos 0:793, Tex2 36:61. Order row: covering=117
(`arr12=117`), cons_pos=793, cons_tex=0, cons_any=793; seam 11700 =
100×117. Matrix: +0.1 on word 3 only, `mm_live=100 mm_snap=100`.
Survival trichotomy: live 100/100, per-vertex 100/100, shared-pos 100/100
(resident 100/100), shared-tex 0 (resident 0/100); `dirty_post=0`,
`zfreeze=0`; `vb_mm=10500 va_mm=10500`,
`hdirty 7800/2000/1900/11700`.
True-delta row: `ref=1 kref=100 refok=1 refhash=11b93d4261c567bb`,
`n2=100 gt0=100 uniform2=97 xd2min/xd2max=64616/64619 xdmax2max=114
xdmean2=2.416`.
Decode rides along (the step-1 header already contains the M11 decode):
`idx_pos_draws=73 idx_pos_verts=9873 exp_draws=71 exp_verts=3413`,
`tex_draws=0,54,0,0,0,0,0,0`, `tex_exp_draws` all zero; cross-checks 73 =
`pos_indexed` 73, 54 = `tex_indexed[1]` 54.

Recorded without verdict: M11's end-state mechanism reproduces (100/100
differing true delta against a rendered reference, guest/event clean);
97/100 delta replays hash-identical with a 3-byte max spread
(64616/64619); the byte count is frame-dependent (64616 here on a 392536
B frame vs M11's 29960/44021).

## Per-step wall table (final arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m12-det | 200 | 6.032 / 10.805 / 5.844 / 12.355 | 2.450 / 2.819 | 392536 / 3397 | YES | seq_wall_ms=1906.673 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m12-det2 | 200 | 24.175 / 54.445 / 17.735 / 132.618 | 11.479 / 13.306 | 531035 / 4559 | YES | seq_wall_ms=6240.736 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m12-det4 | 200 | 30.176 / 78.692 / 24.279 / 108.719 | 16.285 / 19.244 | 770340 / 6333 | YES | seq_wall_ms=7827.377 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
```

Failed-arm wall row (sequence-complete, missing `resume_xfb` only; rc=1):
`m12-det3-failed`: 200 replays, wall 29.900 / 59.983 / 22.288 / 110.380,
Thread-CPU 14.583 / 16.874, frame 513762 / 4279, `done`, `seq_wall_ms=
7464.407 completed=200 xfb_equal=200/200 ... xfb_equal_scratch=0/200
live_xfb_untouched=1 live_same=200/200`.

Frames differ per run (392536 … 770340 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table). All
rows: 200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2
dls=0 walk=100% unknown=0 benign=1` in all runs.
`xfb_equal_scratch=0/200` on all rows is the forced-RAM signature
(rendered scratch vs fuchsia live ref), not a failure.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m12-det | 0.110 | 0.001 | 0.037 | 5.883 | 0.000 | 10.663 |
| m12-det2 | 0.756 | 0.004 | 0.211 | 23.008 | 0.002 | 53.182 |
| m12-det4 | 1.419 | 0.005 | 0.255 | 28.438 | 0.002 | 73.324 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m12-det | 1490 | 71520 | 29.3 |
| m12-det2 | 5957 | 285936 | 7.3 |
| m12-det4 | 6054 | 290592 | 7.2 |

(`m12-det3-failed`: 2814 / 135072 / 15.5.)

## Step 2 — alternating NOP streams: same-frame partition (M11 gap 2)

One run (`SSX_M12_SLOT=0 SSX_M12_ALT=1`), one recorded frame (531035 B /
4559 updates, draws=1863, verts=60326, covering=375, cons=609), four
interleaved windows with one pristine reference each. Guard receipt
(`m12_win`): `alt=1 slot=0 scheme=mod4
map=0:verbatim,1:nopshr,2:nopidx,3:notext kref=96,97,98,99 sel_shr=0
sel_idx=0 sel_text=0 m10nop_ok=0` — no M11 selector armed, so window 0 is
the verbatim total. NOP-span receipts (`m12_nop`): `shr_ok=1 shr_draws=609
shr_bytes=55272 idx_ok=1 idx_draws=343 idx_bytes=326481 text_ok=1
text_draws=121 text_bytes=38111`. The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Per-window ref2 rows (SAME recorded frame; per-window pristine refs):

| win | name | kref | refhash | n2 | gt0 | uniform2 | xd2min/xd2max | xdmax2max | xdmean2 |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | verbatim (total) | 96 | `952b8486340604cc` | 25 | 25 | 25 | 70584 / 70584 | 167 | 5.735 |
| 1 | nopshr (indexed-only) | 97 | `12cf63d3a6d17a30` | 25 | 25 | 25 | 2572 / 2572 | 108 | 4.376 |
| 2 | nopidx (shared-only) | 98 | `95973c7cdf3376e6` | 25 | 25 | 25 | 33377 / 33377 | 107 | 2.104 |
| 3 | notext (non-texture-mediated) | 99 | `3395d2ce28b42626` | 25 | 25 | 25 | 34105 / 34105 | 167 | 2.366 |

Samples: w0 `r100:70584/167/5.735,r104:70584/167/5.735,r108:70584/167/5.735`;
w1 `r101:2572/108/4.376,r105:2572/108/4.376,r109:2572/108/4.376`;
w2 `r102:33377/107/2.104,r106:33377/107/2.104,r110:33377/107/2.104`;
w3 `r103:34105/167/2.366,r107:34105/167/2.366,r111:34105/167/2.366`.

Subtracted shares (total win0 70584 minus surviving window, same frame):

| removed set | surviving win | surviving xd2 | removed share (total − surviving) |
| --- | ---: | ---: | ---: |
| shared-path (nopshr) | 1 | 2572 | 68012 |
| indexed-path (nopidx) | 2 | 33377 | 37207 |
| texture-epoch (notext) | 3 | 34105 | 36479 |

Observed arithmetic (tabulated, no verdict): 68012 + 37207 = 105219 vs
total 70584.

Partition cross-checks (table):

| Check | Value |
| --- | --- |
| `shr_draws` vs `cons_any` | 609 = 609 |
| `idx_draws` vs `exp_draws` | 343 = 343 |
| `text_draws` vs draws 1..121 (12 texture epochs) | 121 = 121 |
| `idx_pos_draws` vs M9 `pos_indexed` | 345 = 345 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 284 = 284 |
| seam hits vs 100 × covering loads | 37500 = 100×375 |

Shared and indexed draw sets are disjoint by construction (the VAT path
bit decides per draw), so windows 1–2 remove exactly one path's slot-0
consumers; the surviving ref2 bytes are that window's other-path
contribution on the shared frame.

EFB-copy table, m12-det2 (compared xfb=`0x004dc660`/573440; `n=13` — the
`m10_copy` detail renders 12 of 13, the XFB drain past the 1024 B buffer
cap; `epoch_cons` carries all 14 epochs):

| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |
| ---: | --- | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |
| 0 | 9 | 0x00701560 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 1 | 18 | 0x00702580 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 2 | 27 | 0x007035a0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 3 | 36 | 0x007045c0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 4 | 45 | 0x007055e0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 5 | 54 | 0x00706600 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 6 | 64 | 0x0110b8a0 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 7 | 77 | 0x013fc9a0 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 8 | 88 | 0x01474860 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 9 | 99 | 0x014d4720 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 10 | 109 | 0x0153e800 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 11 | 121 | 0x015ae800 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 12 | 1863 | 0x004dc660 | 573440 | 1 | 1 | 0x000000 | 640 | 448 | 1 |

Epoch table, m12-det2 (draws=1863; epoch_cons=`9,9,9,9,9,9,1,1,1,1,1,1,549,0`):

| epoch | draw range | cons draws | closing copy |
| ---: | --- | ---: | --- |
| 0–5 | 1..54 | 9 each | copies 0–5 (texture) |
| 6 | 55..64 | 1 | copy 6 (texture) |
| 7 | 65..77 | 1 | copy 7 (texture) |
| 8 | 78..88 | 1 | copy 8 (texture) |
| 9 | 89..99 | 1 | copy 9 (texture) |
| 10 | 100..109 | 1 | copy 10 (texture) |
| 11 | 110..121 | 1 | copy 11 (texture) |
| 12 | 122..1863 | 549 | copy 12 (XFB drain) |
| 13 | 1864..1863 | 0 | tail (none) |

Per-class context: cons=609, culled=0, out-of-range=60 (the 60
texture-epoch consuming draws behind clear barriers), in-range=549;
`all_cull=all_scis=all_znever=0`.

Own-frame M9 census, m12-det2 (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1518 | 345 | n/a | n/a |
| Tex0 | 1863 | 0 | 1661 | 1661 |
| Tex1 | 1579 | 284 | 609 | 325 |
| Tex2 | 1863 | 0 | 34 | 34 |
| Tex3-5 | 1863 | 0 | 25 | 25 |
| Tex6-7 | 1863 | 0 | 7 | 7 |

Shared-pos reach total 1518 (`0:609 3:92 6:84 9:84 12:126 15:135 18:126
21:83 24:101 27:78`); tex2 shared+enabled reach `36:34`. Decode row
(slot 0): `idx_pos_draws=345 idx_pos_verts=44695 exp_draws=343
exp_verts=17089`, `tex_draws=0,284,0,0,0,0,0,0`, `tex_exp_draws` all zero.

m12-det2 survival note (as observed): the post-replay trichotomy reads
`xf_after=100 pv_after=75 pv_other=25 pos_res=100 pos_after=75
pos_other=25 dirty_post=25` — the 25s are the delta-half window-1
replays (M11 det4 pattern: shared-NOP'd replays sample `other` +
dirty); live xfmem still `xf_after=100`. Matrix: +0.1 on word 3 only,
`mm_live=100 mm_snap=125` (100 delta-half + 25 pristine window-1
mismatches vs the replay-0 verbatim sample, tabulated as observed).

Alternation receipt: the per-replay `xdiff` rows repeat with period 4
(`xdmean` 113.942 / 108.752 / 115.762 / 111.220 for windows 0/1/2/3),
and each window's three `samp` replays are 4 apart (100/104/108,
101/105/109, …).

Recorded without verdict: all four windows read 25/25 differing and
25/25 uniform against their own shape's pristine reference on the one
shared frame, so the shares above subtract against that frame's total
(70584) — the partition M11's cross-frame arms could not subtract.

## Step 3 — slot-36 indexed decode (M11 gap 3)

The M12 slot chain carries the M11 decode to slot 36 (`m11_mode` forced;
`m11_idx` fires with `slot=36`). Two frames: m12-det4 (final, 770340 B /
6333 updates, draws=3520, verts=86477, covering=326, cons=36) and
m12-det3-failed (sequence-clean, 513762 B / 4279 updates, draws=2759,
verts=51513, covering=162, cons=42; missing `resume_xfb` only).

Decode table (`m11_idx`; slot 36; `tex_draws`/`tex_exp_draws` per texgen
0..7):

| Arm | idx_pos_draws | idx_pos_verts | exp_draws | exp_verts | tex_draws | tex_exp_draws |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| m12-det4 | 337 | 51403 | 0 | 0 | 0,281,0,0,0,0,0,0 | 0,254,0,0,0,0,0,0 |
| m12-det3-failed | 178 | 24226 | 0 | 0 | 0,123,0,0,0,0,0,0 | 0,92,0,0,0,0,0,0 |

Indexed-Tex2 exposure of slot 36: 0 draws on both frames (no indexed
Tex2 vertices exist on either frame). Indexed-Tex1 exposure: 254
(m12-det4) / 92 (m12-det3-failed) draws reference slot 36.
Indexed-position exposure: 0 draws / 0 verts on both frames.

Decode cross-checks vs the M9 VAT census (table):

| Check | det4 | det3-failed |
| --- | ---: | ---: |
| `idx_pos_draws` vs M9 `pos_indexed` | 337 = 337 | 178 = 178 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 281 = 281 | 123 = 123 |
| `tex_draws[2]` vs M9 `tex_indexed[2]` | 0 = 0 | 0 = 0 |
| seam hits vs 100 × covering loads | 32600 = 100×326 | 16200 = 100×162 |
| shared Tex2 reach 36 vs `cons_tex` | 36 = 36 | 42 = 42 |

Slot-36 VAT context, m12-det4 (draws=3520): Pos 3183/337; Tex1
3239/281/806/525; Tex2 3520/0/36/36. Shared-pos reach total 3183
(`0:803 3:315 6:279 9:300 12:252 15:265 18:324 21:242 24:187 27:216`).
Slot-36 VAT context, m12-det3-failed (draws=2759): Pos 2581/178; Tex1
2636/123/624/501. Order rows: det4 `cons_pos=0 cons_tex=36`,
`first_cons=379 last_cons=414`, all 36 in-range, unculled; det3-failed
`cons_pos=0 cons_tex=42`. Matrix rows (both): +0.1 on word 147 only,
`mm_live=100 mm_snap=100`, `snap_which=2 snap_ti=2`.

Slot-36 true-delta rows carried by the same runs (M12 RAMREF split):

| field | det4 | det3-failed |
| --- | --- | --- |
| ref / kref / refok / refhash | 1 / 100 / 1 / `e200c29d93e8ccf8` | 1 / 100 / 1 / `ada673097833c486` |
| n2 (delta replays) | 100 | 100 |
| gt0 (differing) | 100 | 100 |
| uniform2 (identical to replay 100) | 99 | 100 |
| xd2min / xd2max (bytes, of 573440) | 1372 / 1373 | 1827 / 1827 |
| xdmax2max | 83 | 15 |
| xdmean2min / xdmean2max | 14.510 / 14.520 | 2.219 / 2.219 |
| samples | r100–r102: 1372/83/14.520 | r100–r102: 1827/15/2.219 |

Survival (as observed): det4 `pos_res=0 tex_res=100`, live/per-vertex/
shared-tex all 0/0/100 (`other`), `dirty_post=0`; first-hit values
87.4732 → 87.5732 (+0.1). det3-failed: same `other`-pattern; first-hit
146.277 → 146.377 (+0.1). (M11 det2's slot-36 frame sampled
`after`-pattern with first-hit 0 → 0.1; covering-load upload values are
frame-dependent.)

Per-draw depth (M11 gap 1): not attempted; restated as open — no
header-only per-draw depth instrument exists (`Flush`/`SetConstants` are
vendor-called with no header hook; the header drives the execute pass
through `RunFifo` with the live decoder's internal callbacks, so there is
no header-overridable per-draw callback in that path), and M12's
window-granular NOP arms bound each path's collective contribution only,
with the new M12 sentence that re-verification confirms the execute path
still offers no header hook (`Run`/`RunPre` call `OpcodeDecoder::RunFifo`
directly with the live decoder's callbacks while `OnPrimitiveCommand`
overrides exist only in the header's own setup-time walks), so per-draw
attribution remains collective per window rather than per draw.

## Mechanism table (M11 gaps this brief works through)

| M11 gap | Standing | Receipt |
| --- | --- | --- |
| 2 (same-frame partition) | measured | §Step 2: four 25/25 uniform windows on one frame; removed shares 68012/37207/36479 |
| 3 (slot-36 indexed exposure) | measured | §Step 3: pos exposure 0/0 both frames; `tex_exp_draws` 0,254/92,0…; Tex2-indexed 0 |
| 1 (per-draw depth) | open | no header-only per-draw instrument (see above) |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m12-det | `fc=6663` | `replay_disabled=0 fc=6666 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m12-det2 | `fc=5102` | `replay_disabled=0 fc=5105 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m12-det4 | `fc=5645` | `replay_disabled=0 fc=5648 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m12-det3-failed | `fc=5935` | (missing: native exit -5 post-sequence; sequence itself 200/200 `done`) |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the triple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M11/M10/M9/M8/M7 sequence hashes
and all M6 sequence and M5 sequence/disabled hashes) is tabulated as
observed. `resume fc − fc0 = 3` in each final run (the live record window;
per-replay `dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m12-det | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m12-det2 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m12-det4 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m12-det3-failed | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | (missing; see above) |

Scratch `0/200` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M11/build_replay_player.py`; `m12-slot36` was built from
the step-2 header — the driver compiles
`local/research/M12/m12_replay_context.h`):

```
python3 local/research/M12/build_replay_player.py local/research/M12/players/m12-baseline
python3 local/research/M12/build_replay_player.py local/research/M12/players/m12-alt
python3 local/research/M12/build_replay_player.py local/research/M12/players/m12-slot36
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M12\n'`,
remove after each run; profiles fresh per run):

```
SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m12/m12-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M12/players/m12-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m12-det --cpu-thread --output "/Volumes/Extreme SSD/m12/m12-det-run" --seconds 240
SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m12/m12-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M12/players/m12-alt --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m12-det2 --cpu-thread --output "/Volumes/Extreme SSD/m12/m12-det2-run" --seconds 240
SSX_M12_SLOT=36 SSX_M12_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m12/m12-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M12/players/m12-slot36 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m12-det3 --cpu-thread --output "/Volumes/Extreme SSD/m12/m12-det3-run" --seconds 240
SSX_M12_SLOT=36 SSX_M12_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m12/m12-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M12/players/m12-slot36 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m12-det4 --cpu-thread --output "/Volumes/Extreme SSD/m12/m12-det4-run" --seconds 240
```

Analysis:

```
python3 local/research/M12/analyze.py "m12-det=/Volumes/Extreme SSD/m12/m12-det-probe.jsonl" "m12-det2=/Volumes/Extreme SSD/m12/m12-det2-probe.jsonl" "m12-det4=/Volumes/Extreme SSD/m12/m12-det4-probe.jsonl"
python3 local/research/M12/analyze.py "m12-det3f=/Volumes/Extreme SSD/m12/m12-det3-probe.jsonl-failed"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M12/` — `m12_replay_context.h`
(`14f7c7f7…`), `build_replay_player.py`, `analyze.py`, `REPORT.md` (this
file), `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m12/` —
`m12-det-probe.jsonl` (20865267 B), `m12-det2-probe.jsonl` (6729442 B),
`m12-det4-probe.jsonl` (5246362 B) and the matching `-run` dirs and
`-run.log` harness receipts; `analyze-all.txt` (the three-arm analyzer
output) and `analyze-det.txt`, `analyze-det2.txt`, `analyze-det4.txt`
(per-arm outputs); per-step header snapshots
`m12_replay_context.step1.h` (= M11 header),
`m12_replay_context.step2.h` (= committed header),
`m12_replay_context.step3.h` (= step 2, byte-identical); the
post-sequence-crash det3 attempt (`m12-det3-probe.jsonl-failed`
(2566498 B), `m12-det3-run-failed`, `m12-det3-run.log-failed`,
`analyze-det3-failed.txt`; complete 200/200 `done` sequence, missing
`resume_xfb`). Players (gitignored):
`local/research/M12/players/{m12-baseline,m12-alt,m12-slot36}/`
(each with `player`, `build.json`, launchers). All paths above are
symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m12-baseline` `f3383745b6ed` /
`fe222dbd18e7` (player hash identical to M11's `m11-text`: same header
compiles to the same binary), `m12-alt` `14f7c7f7f58a` /
`45d923c93a6a`, `m12-slot36` `14f7c7f7f58a` / `45d923c93a6a`
(identical to `m12-alt`: same header, same binary).

## What I could not do

1. No per-draw depth-occlusion query exists header-only: `Flush` /
`SetConstants` are vendor-called with no header hook (M11 gap 1
persists), so per-draw occlusion is bounded collectively per window
(win0−win1/win2/win3 shares) but not attributed per draw. The header
drives the execute pass through `RunFifo` with the live decoder's
internal callbacks, so there is no header-overridable per-draw callback
in that path; a per-draw receipt needs a vendor execute-pass hook or
per-draw EFB readback (ordered follow-up, not this runbook). New in M12:
re-verification confirms the execute path still offers no header hook
(`Run`/`RunPre` call `OpcodeDecoder::RunFifo` directly with the live
decoder's callbacks while `OnPrimitiveCommand` overrides exist only in
the header's own setup-time walks).
2. The `m10_copy` detail renders 12 of 13 copies on the det2/det4/det3f
frames (1024 B buffer cap; the XFB drain is the unrendered 13th).
`epoch_cons` carries all epochs, and the report's epoch tables are built
from it; the analyzer's clock-derived epoch table mislabels the XFB
epoch's closing copy on those arms (inherited cosmetic, not a receipt
gap).
3. The alternating-NOP partition ran on slot 0 only; other slots
(including 36) carry the single-reference arm only (ordered follow-up,
not this runbook).
4. Player dirs are under `local/research/M12/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs and all
probes are on the SSD as ordered.
5. Desktop only; no device work.

## Files

Committed under `local/research/M12/`: `m12_replay_context.h` (research
header, `14f7c7f7…`), `build_replay_player.py` (M11 driver, header path
only), `analyze.py` (M11 tables unchanged + M12 `m12_win`/`m12_nop`/
`m12_ref2` parsing, per-window ref2 tables, subtracted-shares table;
missing keys print as n/a / sections skipped), `REPORT.md` (this file),
`waits.log` (zero waits, four claim/release pairs, one annotation).

## Header diffs per step (`diff -u` against the M11 header)

Step 1: empty (verbatim copy). Step 2 follows, generated from the
committed `local/research/M12/m12_replay_context.h` (= step 2; the
step-2 header adds env-gated branches only, so every arm is reproducible
from it via env). Step 3: no new header (step3-vs-step2 `diff -u` is
empty; the step-3 diff against the M11 header == the step-2 diff).

### Step 2

```diff
--- local/research/M11/m11_replay_context.h
+++ local/research/M12/m12_replay_context.h
@@ -1582,7 +1582,23 @@
     }
     return n;
   }();
-  const int m11_mode = m11_slot_self >= 0 ? 2 : 0;
+  // M12 step 2: SSX_M12_SLOT=N (0-63) runs the M11 instruments unchanged on
+  // the same slot (M12 mode forces M11+M10 mode 2, so the M11 decode event
+  // fills for this slot and every M11/M10/M9/M8 receipt rides along).
+  // Precedence: M12 > M11 > M10. M12 env unset = M11 behavior.
+  const int m12_slot_self = [] {
+    const char* v = std::getenv("SSX_M12_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m12_mode = m12_slot_self >= 0 ? 2 : 0;
+  const int m11_mode = (m11_slot_self >= 0 || m12_mode != 0) ? 2 : 0;
   const int m10_slot_self = [] {
     const char* v = std::getenv("SSX_M10_SLOT");
     if (!v || !*v) return -1;
@@ -1594,7 +1610,8 @@
     }
     return n;
   }();
-  const int m10_slot = m11_mode != 0 ? m11_slot_self : m10_slot_self;
+  const int m10_slot = m12_mode != 0 ? m12_slot_self
+                               : (m11_slot_self >= 0 ? m11_slot_self : m10_slot_self);
   const int m10_mode = m10_slot >= 0 ? 2 : 0;
   // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
   // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
@@ -1616,14 +1633,21 @@
   // and splits the sequence at kTransformFrom — replays 0..99 pristine
   // (counting on, delta off), 100..199 delta — storing replay 99's
   // rendered scratch frame as ref2 and diffing replays 100+ against it.
-  const int m10_ramcopy = m10_mode == 2 ? ([] {
+  const int m10_ramcopy = m10_mode == 2 ? ([&] {
                             const char* v = std::getenv("SSX_M10_RAMCOPY");
                             const char* r = std::getenv("SSX_M10_RAMREF");
                             // M11 step 2: SSX_M11_RAMREF=1 implies RAMCOPY too.
                             const char* r11 = std::getenv("SSX_M11_RAMREF");
+                            // M12 step 2: SSX_M12_RAMREF=1 and (in M12 mode)
+                            // SSX_M12_ALT=1 imply RAMCOPY too.
+                            const char* r12 = std::getenv("SSX_M12_RAMREF");
+                            const char* alt = std::getenv("SSX_M12_ALT");
                             const int ref =
                                 (r && std::strcmp(r, "1") == 0) ||
-                                        (r11 && std::strcmp(r11, "1") == 0)
+                                        (r11 && std::strcmp(r11, "1") == 0) ||
+                                        (r12 && std::strcmp(r12, "1") == 0) ||
+                                        (m12_mode != 0 && alt &&
+                                         std::strcmp(alt, "1") == 0)
                                     ? 1
                                     : 0;
                             return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
@@ -1634,8 +1658,11 @@
         const char* r = std::getenv("SSX_M10_RAMREF");
         // M11 step 2: SSX_M11_RAMREF=1 arms the same split (needs nop=0).
         const char* r11 = std::getenv("SSX_M11_RAMREF");
+        // M12 step 2: SSX_M12_RAMREF=1 arms the same split (M12 slot chain).
+        const char* r12 = std::getenv("SSX_M12_RAMREF");
         return (r && std::strcmp(r, "1") == 0) ||
-                       (r11 && std::strcmp(r11, "1") == 0)
+                       (r11 && std::strcmp(r11, "1") == 0) ||
+                       (r12 && std::strcmp(r12, "1") == 0)
                    ? 1
                    : 0;
       })()
@@ -1841,6 +1868,64 @@
       m10_nop_bytes = nb;
     }
   }
+  // M12 step 2: alternating-NOP arm (SSX_M12_ALT=1, M12 mode only). Builds
+  // three NOP stream pairs from the verbatim+scratch streams with the exact
+  // M11 hit sets — [0] shared-path consumers (M11 NOPSHR set), [1]
+  // indexed-position draws exposed to the slot (M11 NOPIDX set), [2]
+  // texture-epoch draws (M11 NOPTEXT set) — and alternates them per replay
+  // (replays % 4: 0 verbatim total, 1..3 the NOP shapes), so every window
+  // shares the SAME recorded frame. Fail-closed per shape: a bad span
+  // leaves that shape verbatim (ok=0 in m12_nop). ALT runs set no M11 NOP
+  // selector, so shape 0 is the verbatim total; m12_win echoes the M11
+  // selectors + m10_nop_ok as a guard receipt.
+  const int m12_alt = m12_mode == 2 ? ([] {
+                        const char* v = std::getenv("SSX_M12_ALT");
+                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                      })()
+                                    : 0;
+  std::vector<u8> m12_nop_exec[3], m12_nop_pre[3];
+  u32 m12_nop_draws[3] = {}, m12_nop_bytes[3] = {};
+  bool m12_nop_ok[3] = {};
+  if (m12_alt && m10_mode != 0) {
+    for (int s = 0; s < 3; ++s) {
+      m12_nop_exec[s] = frame_exec;
+      m12_nop_pre[s] = frame_pre_exec;
+    }
+    bool m12_patch_ok[3] = {!m10stream.drawrec.empty(),
+                            !m10stream.drawrec.empty(),
+                            !m10stream.drawrec.empty()};
+    u32 m12_nd[3] = {}, m12_nb[3] = {};
+    for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
+      const M10DrawRec& dr = m10stream.drawrec[d];
+      const bool cons = dr.cons_pos != 0 || dr.cons_texmask != 0;
+      bool in_tex_epoch = false;
+      for (size_t e = 0; e < m10stream.copies.size(); ++e) {
+        if (m10stream.copies[e].draw < u32(d) + 1) continue;
+        in_tex_epoch = m10stream.copies[e].is_xfb == 0;
+        break;
+      }
+      const bool hit[3] = {cons, dr.idx_pos_any != 0, in_tex_epoch};
+      for (int s = 0; s < 3; ++s) {
+        if (!hit[s] || !m12_patch_ok[s]) continue;
+        if (dr.size == 0 || dr.off + dr.size > m12_nop_exec[s].size() ||
+            dr.off + dr.size > m12_nop_pre[s].size()) {
+          m12_patch_ok[s] = false;
+          continue;
+        }
+        std::memset(m12_nop_exec[s].data() + dr.off, 0x00, dr.size);
+        std::memset(m12_nop_pre[s].data() + dr.off, 0x00, dr.size);
+        ++m12_nd[s];
+        m12_nb[s] += dr.size;
+      }
+    }
+    for (int s = 0; s < 3; ++s) {
+      if (m12_patch_ok[s] && m12_nd[s] > 0) {
+        m12_nop_ok[s] = true;
+        m12_nop_draws[s] = m12_nd[s];
+        m12_nop_bytes[s] = m12_nb[s];
+      }
+    }
+  }
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
   const std::vector<u8>& pre_stream =
@@ -1872,7 +1957,7 @@
     return 0;
   }();
   {
-    char detail[640];
+    char detail[768];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
@@ -1881,7 +1966,8 @@
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
                   "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
-                  "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d",
+                  "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d "
+                  "m12mode=%d m12slot=%d m12alt=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1892,7 +1978,7 @@
                   m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
                   m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
                   m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
-                  m11_notext);
+                  m11_notext, m12_mode, m12_slot_self, m12_alt);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1991,7 +2077,7 @@
     s_m8_regcalls = 0;
     for (auto& w : s_m8_writes) w = 0;
     for (auto& r : s_m8_reads) r = 0;
-    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref) ? m9_slot : -1;
+    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref && !m12_alt) ? m9_slot : -1;
     s_m8_proj = 0;
     s_m9_surv = m9_surv;
     s_m9_first_hit = 0;
@@ -1999,7 +2085,7 @@
     s_m9_vb_mm = s_m9_va_mm = 0;
     s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
     s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
-    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref) ? 1 : 0;
+    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref && !m12_alt) ? 1 : 0;
     s_m10_mat_done = 0;
     s_m10_post_done = 0;
     s_m10_snap_which = 0;
@@ -2033,6 +2119,21 @@
   int m10_samp_xm[3] = {};
   double m10_samp_xn[3] = {};
   unsigned m10_samp_n = 0;
+  // M12 step 2: per-window ref2 storage + tallies (one pristine reference
+  // per window shape; window = replays % 4).
+  std::vector<u8> m12_ref[4];
+  bool m12_ref_ok[4] = {};
+  u64 m12_ref_hash[4] = {}, m12_hk_hash[4] = {};
+  unsigned m12_n2[4] = {}, m12_gt0[4] = {}, m12_uniform2[4] = {};
+  unsigned m12_xd2_min[4] = {}, m12_xd2_max[4] = {};
+  int m12_xdmax2_max[4] = {};
+  double m12_xdmean2_min[4] = {}, m12_xdmean2_max[4] = {};
+  bool m12_xd2_first[4] = {true, true, true, true};
+  u32 m12_samp_r[4][3] = {};
+  unsigned m12_samp_xd[4][3] = {};
+  int m12_samp_xm[4][3] = {};
+  double m12_samp_xn[4][3] = {};
+  unsigned m12_samp_n[4] = {};
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -2054,7 +2155,8 @@
     // bases, strides and VATs.
     if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
-    if (replays == kTransformFrom && m10_ramref) {  // M10 step 3: arm delta half
+    // M10 step 3: arm delta half (M12 step 2: the alt arm splits identically).
+    if (replays == kTransformFrom && (m10_ramref || m12_alt)) {
       s_m8_slot = m10_slot;
       s_m10_cap = 1;
     }
@@ -2069,9 +2171,21 @@
     CopyPreprocessCPStateFromMain();
     VertexLoaderManager::MarkAllDirty();
     const double t_cp = Now();
-    if (deterministic) RunPre(pre_stream);
+    // M12 step 2: per-replay window select (alt mode only; otherwise the
+    // M11 streams above run unchanged).
+    const std::vector<u8>* m12_pre = &pre_stream;
+    const std::vector<u8>* m12_exec = &exec_stream;
+    int m12_win = 0;
+    if (m12_alt) {
+      m12_win = int(replays % 4);
+      if (m12_win > 0 && m12_nop_ok[m12_win - 1]) {
+        m12_pre = &m12_nop_pre[m12_win - 1];
+        m12_exec = &m12_nop_exec[m12_win - 1];
+      }
+    }
+    if (deterministic) RunPre(*m12_pre);
     const double t_pre = Now();
-    Run(exec_stream);
+    Run(*m12_exec);
     if (g_gfx) {
       g_gfx->Flush();
       g_gfx->WaitForGPUIdle();
@@ -2302,6 +2416,61 @@
             if (xm2 > m10_xdmax2_max) m10_xdmax2_max = xm2;
             if (xn2 < m10_xdmean2_min) m10_xdmean2_min = xn2;
             if (xn2 > m10_xdmean2_max) m10_xdmean2_max = xn2;
+          }
+        }
+      }
+    }
+    // M12 step 2: per-window ref2 capture + diff (alternating-NOP arm).
+    // Each window's last pristine replay (96+w) is its reference; that
+    // window's delta replays (25 each) diff against their own shape's
+    // bytes. After wall_end, out of wall_ms.
+    if (m12_alt && xfb_scratch_ok) {
+      u8* rwp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
+      if (rwp) {
+        const int w = int(replays % 4);
+        if (replays < kTransformFrom) {
+          m12_ref[w].assign(rwp, rwp + mask.xfb.bytes);
+          m12_ref_hash[w] = RamHash(rwp, mask.xfb.bytes);
+          m12_ref_ok[w] = true;
+        } else if (m12_ref_ok[w]) {
+          const u64 hh = RamHash(rwp, mask.xfb.bytes);
+          if (m12_n2[w] == 0) m12_hk_hash[w] = hh;
+          if (hh == m12_hk_hash[w]) ++m12_uniform2[w];
+          ++m12_n2[w];
+          unsigned x2 = 0;
+          int xm2 = 0;
+          unsigned long long xa2 = 0;
+          for (u32 i = 0; i < mask.xfb.bytes; ++i) {
+            const int dd = rwp[i] > m12_ref[w][i] ? rwp[i] - m12_ref[w][i]
+                                                 : m12_ref[w][i] - rwp[i];
+            if (dd > 0) {
+              ++x2;
+              xa2 += (unsigned)dd;
+              if (dd > xm2) xm2 = dd;
+            }
+          }
+          const double xn2 = x2 ? double(xa2) / double(x2) : 0.0;
+          if (x2 > 0) {
+            ++m12_gt0[w];
+            if (m12_samp_n[w] < 3) {
+              const unsigned sn = m12_samp_n[w]++;
+              m12_samp_r[w][sn] = replays;
+              m12_samp_xd[w][sn] = x2;
+              m12_samp_xm[w][sn] = xm2;
+              m12_samp_xn[w][sn] = xn2;
+            }
+          }
+          if (m12_xd2_first[w]) {
+            m12_xd2_min[w] = m12_xd2_max[w] = x2;
+            m12_xdmax2_max[w] = xm2;
+            m12_xdmean2_min[w] = m12_xdmean2_max[w] = xn2;
+            m12_xd2_first[w] = false;
+          } else {
+            if (x2 < m12_xd2_min[w]) m12_xd2_min[w] = x2;
+            if (x2 > m12_xd2_max[w]) m12_xd2_max[w] = x2;
+            if (xm2 > m12_xdmax2_max[w]) m12_xdmax2_max[w] = xm2;
+            if (xn2 < m12_xdmean2_min[w]) m12_xdmean2_min[w] = xn2;
+            if (xn2 > m12_xdmean2_max[w]) m12_xdmean2_max[w] = xn2;
           }
         }
       }
@@ -2942,6 +3111,50 @@
                     m11_nopidx, m11_notext, int(m10_nop_ok), m10_nop_draws,
                     m10_nop_bytes);
       Event("m11_nop", m11n);
+    }
+    // M12 step 2: alternating-NOP receipts (alt mode only; the M11/M10
+    // receipts above are unchanged). m12_win carries the window design +
+    // guard echo; m12_nop the per-shape spans; one m12_ref2 per window.
+    if (m12_alt) {
+      char m12w[256];
+      std::snprintf(m12w, sizeof(m12w),
+                    "alt=%d slot=%d scheme=mod4 map=0:verbatim,1:nopshr,2:nopidx,3:notext "
+                    "kref=%u,%u,%u,%u sel_shr=%d sel_idx=%d sel_text=%d m10nop_ok=%d",
+                    m12_alt, m10_slot, kTransformFrom - 4, kTransformFrom - 3,
+                    kTransformFrom - 2, kTransformFrom - 1, m11_nopshr,
+                    m11_nopidx, m11_notext, int(m10_nop_ok));
+      Event("m12_win", m12w);
+      char m12n[256];
+      std::snprintf(m12n, sizeof(m12n),
+                    "shr_ok=%d shr_draws=%u shr_bytes=%u idx_ok=%d idx_draws=%u "
+                    "idx_bytes=%u text_ok=%d text_draws=%u text_bytes=%u",
+                    int(m12_nop_ok[0]), m12_nop_draws[0], m12_nop_bytes[0],
+                    int(m12_nop_ok[1]), m12_nop_draws[1], m12_nop_bytes[1],
+                    int(m12_nop_ok[2]), m12_nop_draws[2], m12_nop_bytes[2]);
+      Event("m12_nop", m12n);
+      static const char* const m12_names[4] = {"verbatim", "nopshr", "nopidx",
+                                               "notext"};
+      for (int w = 0; w < 4; ++w) {
+        char m12f[512];
+        int m12foff = std::snprintf(
+            m12f, sizeof(m12f),
+            "win=%d name=%s ref=%d kref=%u refok=%d n2=%u gt0=%u uniform2=%u "
+            "xd2min=%u xd2max=%u xdmax2max=%d xdmean2min=%.3f xdmean2max=%.3f "
+            "refhash=%016llx samp=",
+            w, m12_names[w], m12_alt, kTransformFrom - 4 + (unsigned)w,
+            int(m12_ref_ok[w]), m12_n2[w], m12_gt0[w], m12_uniform2[w],
+            m12_xd2_min[w], m12_xd2_max[w], m12_xdmax2_max[w],
+            m12_xdmean2_min[w], m12_xdmean2_max[w],
+            static_cast<unsigned long long>(m12_ref_hash[w]));
+        for (unsigned s = 0; s < m12_samp_n[w]; ++s) {
+          if (m12foff < 0 || size_t(m12foff) >= sizeof(m12f) - 48) break;
+          m12foff += std::snprintf(
+              m12f + m12foff, sizeof(m12f) - size_t(m12foff), "%sr%u:%u/%d/%.3f",
+              s ? "," : "", m12_samp_r[w][s], m12_samp_xd[w][s],
+              m12_samp_xm[w][s], m12_samp_xn[w][s]);
+        }
+        Event("m12_ref2", m12f);
+      }
     }
   }
   XFReplay::g_transform = saved_transform;
```
