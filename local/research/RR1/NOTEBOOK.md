# RR1 notebook (append-only)

Clock start: 2026-09-24 21:54:49 EDT (first command). Time box ends 00:54:49 EDT; write-up by 01:10.
Worker: Claude Code (Opus 5.5), exploratory.

## 22:10 setup
- Read brief + E51/E53/E59/E60. Worktree `~/dev/ssx3-work/RR1/PS2Recomp` branch `rr1-sky` @ f949ff0; build started 22:02 (nice 10, -j6; diag taps OFF, `PS2X_DIAG_WATCH` still compiled in).
- Lease: slot 1 held by `au8-race` (claim 01:30Z, no AU8 runner alive), slot 2 by AU9 (alive). bytesize busy: AU9 PCSX2 (pid 436).
- E59 lead check: full group-a revert showed the sun once, but its VCALLMSR-old, VSQI-old and both subsets didn't, and the only remaining sites (VLQI 0x3feb8c, CMSAR1) never execute (E60). Reading: the group-a sun is likely run-to-run scene variance (pre-deterministic boots). Hypothesis, not tested.
- PCSX2 T65 dump (`ref/pcsx2-race.gs`, zst sha aa56234a…) census, vsync 0 (`rr1_census.py`, E51 decoder + ALPHA/FBA/TEXA):
  - TBP0 11017 PSMT8 256² CBP 14473: 81 prims, **ALPHA 0x2a** (A=0,B=0,C=FIX,D=Cs → out = Cs, opaque), TEST 0x51143, TEX1 0x61.
  - E59 saw ours: same TBP/PSM/size, **ALPHA 0x1** (A=Cd,B=Cs,C=As,D=Cs → out = Cs + (Cd−Cs)·As/128). With As≈0x80 that's ≈Cd: the sky is drawn but leaves the destination untouched. **H1: sky is present in the stream but blended away by a wrong ALPHA register value built upstream (EE/VU1).**
  - PCSX2 uses ALPHA 0x1 only once in v0 (TBP 0 PSM 27 16 prims, TEST 0x70000).

## 22:12 Brad observation (I30 iOS, d711506)
- HUD/menu elements flash in and out every few seconds; many 3D assets pop in/out. Plan: on the Mac deterministic capture, count per-vsync prims by (program/TBP/ALPHA) and look for vsyncs where whole classes vanish (capped VU1 programs, frustum test via VU0 0x37de88, packet loss, or field/double-buffer alternation). Check if it shares H1's producer.

## 22:03 tools + boot A queued
- Build `~/dev/ssx3-work/RR1/build` done 22:00 (BUILD_RC=0). Added default-off dev tap `PS2X_RR1_ALPHA_SRC=<val>` (+`PS2X_RR1_FROM/TO`): scans VIF1/GIF DMA deliveries (chain + normal) for A+D qwords `lo=val, hi=0x42|0x43`, prints EE address via the E40 source spans (spans now also recorded when the tap is on) and the 3 preceding qwords. Files: new `ps2xRuntime/include/ps2_rr1_alpha_tap.h`, hooks in `ps2_memory.cpp`.
- `rr1_boot.py` (one slot, waits; target vsync from `[diag:frame]`; wall ≤ 600) and `rr1_cap.py` (census/flash over PS2XGSC1 captures).
- Boot A: deterministic I26-FAST to 2160, GS capture (stop 2160), frames 1800/1950/2100, ALPHA tap 1790–1800, gfx stats 1700–2160. Waiting on a slot (AU9 on slot 2; slot 1 stale au8-race lease left alone).
- 22:04 slot 1 lease `au8-race pid=66267 utc=01:30Z` judged stale (pid dead; the only live runner, pid 5533, is AU9's lldb boot on slot 2 with cwd under AU9). Moved to `/tmp/ssx3-p-lane-lease.stale-au8-rr1` so boot A can claim slot 1. Reported to the orchestrator in chat.

## 22:30 mechanism named: PATH3 released whole on the first MSKPATH3 unmask
- Boot A (deterministic, pre-fix, slot 1, 135 s, target 2173): tap hits for ALPHA=0x1 are a normal depth-pass draw (ZBUF/TEST 0x70000/ALPHA 0x1, PCSX2 has it too), not the sky.
- Timeline at tick 1795 (`rr1_timeline.py`): #2/#3 PATH2 set TEST1=0x51143 ALPHA1=0x2a (PCSX2's sky state) → **#5 PATH3 337,216 B** (all texture uploads + the depth pass: 7168 psm 0x32 TEST 0x30000, then TBP 0 psm 0x1b TEST 0x70000 ALPHA 0x1) → sky PSMT8 256² TBP 12905 draws inherit **ALPHA 0x1/TEST 0x70000** (76 prims).
- PCSX2 T65 timeline (`rr1_timeline_pcsx2.py`): #3/#4 same setup → #6–#9 one 64 KiB upload → TEX0 11017 → sky draws with 0x2a/0x51143. Depth pass at #1422 of 1537 (near frame end; inherits ALPHA 0x49 from the 3712 draws).
- Boot B (events, 1794–1795): VIF1 masks PATH3, the EE kicks one 178-tag GIF chain (337,216 B, queued whole), then VIF1 opens **17 one-command unmask windows** (`MSKPATH3 0` immediately followed by `MSKPATH3 1`), one before each object. Our `flushMaskedPath3Packets` released the whole FIFO on the first window. FLUSHA is a no-op in our VIF1.
- The queued data is 20 EOP packets (`rr1_eop.py`): eop#0 = 65,664 B = PCSX2's first-window upload; eop#18 = depth pass.
- **Fix candidate** (branch `rr1-sky`): split masked PATH3 data at EOP boundaries; each unmask releases one EOP packet; the rest drains when VIF1 delivery (DMA batch or VIF1 FIFO write) ends with PATH3 unmasked. `PS2X_PATH3_EOP_GATE=0` restores the old behaviour (dev A/B).
- Boot C (fixed, slot 3, 172 s): 17 releases in frame 1795, depth pass drains at the frame-end unmask. Sky draw now **ALPHA 0x2a/TEST 0x51143** with its upload right before, same as PCSX2. Frame 1800: dark lower region gone, snow lit and textured. Backdrop still dark navy (PCSX2: mountain panorama) → second issue, open.
- Capture path labels are only set when gfx stats is on (A had it, C didn't): C's all-p1 labels are an artifact.

## 22:24 menus before/after (orchestrator's G46 request) + backdrop lead
- Replay of boot A's capture (`ps2x_tests` with PS2X_GS_REPLAY_*) reproduces the live frames (tick 1800 present 762bd855 = live dump fnv). ps2x_tests exited 139 after the replay run (suite with replay env); clean suite run still to do.
- Route ticks (I26 ROUTES.md): Select Peak ~1099, Select Mode ~1185 → frames at 1090 / 1180.
  - Pre-fix 1090: photo panel = PEAK ACCESS/LEVEL icon atlas, logo slot = PEAK 1/VAL cells, big "3" missing, button glyphs = bars. Fixed (boot C): Peak 1 mountain photo, SSX logo, "3", ✕/△ glyphs.
  - Pre-fix 1180: course-map panel shows the "3" graphic; fixed: Peak 1 course map.
- Backdrop: race backdrop TBP 12905 (PSMT8 256², uploaded 64 KiB as CT32 128×128 right before use), CBP 12897 CLD=1. Its CLUT is uploaded once at tick 1608 (16×16 CT32) and no later upload covers it. Backdrop still dark navy after the fix. Open.

## 22:52 second mechanism: VIF UNPACK V4-5 not expanded; PCSX2 replay; fork commits
- PCSX2 gsrunner replay of our (PATH3-fixed, boot D) stream (`rr1_cap2gs.py` → bytesize `~/rr1`, `rr1_gsrunner.sh`, 32 s): Select Peak 1090 identical to ours (Peak 1 photo). **Race start 1607: PCSX2 also draws the dark backdrop from our stream** → backdrop fault is in the stream, not our GS. From 1608 on PCSX2's replay shows blank frames (also with forced NTSC SMODE1); replay gap, cause unknown.
- Backdrop CLUT (CBP 12897, uploaded tick 1608) has the same channel averages as PCSX2's sky CLUT at CBP 14473 (43.8/84.7/189.5/127.5 over 256 entries).
- **Vertex colours:** backdrop prims RGBA 0x01101010 vs PCSX2 0x80808080; terrain 0x01080504 vs 0x80402820. Exactly RGB>>3, A>>7 = VIF UNPACK V4-5 without the 5→8-bit expansion. `ps2_vif1_interpreter.cpp:986-989` stored raw fields; PCSX2 UNPACK_V4_5 shifts RGB<<3, A<<7. Fixed + test.
- Fork `rr1-sky` (local, not pushed): `3bc0449` PATH3 EOP gating (+ default-off dev taps), `f3dff5b` V4-5 expansion. Suite 598/598 (rc 0) from the worktree root on the combined tree; runner-dir check empty.
- Flash check (`rr1_flash.py`, drawing ticks 1800–1960): pre-fix A has no class dropping out and FST (HUD-style) prims 66–83 per tick, so there's no intermittent draw loss in the Mac stream at this moment. Brad's iOS flashing is probably the wrong-texture-at-draw-time effect (PATH3) or present tearing. Hypothesis, not tested on iOS.
- After the PATH3 fix, frames have 17 unmask windows for 20 queued EOP packets (PCSX2 frame: ~27 windows, one EOP packet per window, depth pass in its own window #1418). Our 3 extra packets (incl. depth + post pass) drain at the next frame's first unmask, i.e. one frame late. Fewer windows = fewer textured objects submitted → likely the missing-object/foliage lead (upstream, open).
- Boot E (both fixes) queued: all 4 mini slots held by E57/E61 exclusive speed runs since ~22:37.

## 23:25 third mechanism: 4096-tag DMA chain cap truncates the frame's VIF1 list; A/B
- After the PATH3 fix, frames had 15–27 windows with 5–7 leftover PATH3 packets (boot E, `rr1_windows.py`); PCSX2 v0 has none.
- Boot F (chain-end event, 1800–1830): **25 of 50 VIF1 chain kicks ended at exactly 4096 tags** (`kMaxChainTags`, `ps2_memory.cpp:1601`, upstream sanity cap from #80 era). The walker then completes the transfer, dropping the rest of the list.
- Raised to 1<<20 with a one-time `[dma] chain tag guard hit` warning. Boot G: VIF1 chains reach **5,126 tags**; guard never hit. Windows 20–31 per frame, ≤1 leftover besides the frame-start post packet; depth pass at packet ~1925/2064 (PCSX2 #1418/1537). Race frames 1800/2100: snow-spray particles, pink checkpoint beam (was black lines), extra trees. Prims per drawing tick 21–24k → 34–36k (PCSX2 T65 at 00:00:18: ~21.9k; different moment, not comparable).
- Menu chains (ticks 1000–1100, boot H) ≤ 320 tags: the cap never mattered in menus.
- Fork commit `4f69c98` + test (5,001-tag chain runs to END). Suite 599/599 rc 0. Cherry-picks of all three onto fork ssx3 `71c952e` apply cleanly (local `rr1-rebase-check`: 607d8ec, 58f5120, e20844a).
- **A/B boot H** (final runner, `PS2X_PATH3_EOP_GATE=0`): Select Peak atlas artifacts back; race dark lower region back, wrong tree textures; backdrop stays bright; beam/trees present. Attribution: PATH3 → menu atlas family + dark lower region + wrong textures + sky state leak; V4-5 → dark backdrop / dim vertex colours; chain cap → missing objects (trees, particles, beam) and late depth pass.
- Flash (boot G, 1800–1960): HUD-style prims 66–83 on every drawing tick; the only classes that come and go are PSMT8H particle textures. The cap cut varied with list length per frame, which is a direct pop-in/out mechanism for late-listed objects (hypothesis for Brad's iOS pop-in; iOS not tested). HUD flashing not reproduced on Mac in this window.
