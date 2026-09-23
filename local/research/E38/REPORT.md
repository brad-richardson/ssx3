# E38 report — VIF DMA TTE fix: correct per unit tests, mechanism refuted by boots

Brief `local/muse/prompts/E38.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/E37/REPORT.md`,
`local/research/T49/REPORT.md` §T49-5.

## Outcome

- Fix implemented exactly as briefed (CHCR.TTE-gated tag transfer for **all**
  VIF0/VIF1 tag ids) + 3 new unit tests; 3 existing VIF chain tests moved to
  TTE=1. Suite **483/483** flags-unset. One fork commit, ff-pushed.
- Boot validation is **NEGATIVE for the named mechanism**: with the fix live,
  VU1 code at 0x10/0x40 is unchanged (`LQI`, not PCSX2's `B`), the stuck
  programs still stop at the 4th `0x418` arrival, and the settled stats band is
  identical to E33/E37 down to VU cycles. The REF-embedded-MPG drop does not
  explain the stuck programs.
- New positive finding (extra Boot A2, within budget): our `0x12B8` program
  receives **16 MPG uploads** in a 262-line packet (PCSX2's `0x257` tail packet:
  265 lines, 16 MPGs) and runs **80 pairs** (PCSX2: 80 to E-bit). So MPG
  microcode **does land** in our runtime through the walker — "MPG never lands"
  is false as a blanket statement. The 0x10/0x40 staleness is narrower: either
  the payload bytes covering slots 2/8 diverge upstream, or the traced 0x10
  runs precede the uploading packet within the vsync. Recommended redirect in
  §Recommendation.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `7f022ed` | [E38] VIF DMA chain: TTE-gated tag transfer for all tag ids (REF MPG lands) |

Base `11725b4` (E37 tip). Pushed `11725b4..7f022ed` (`git ls-remote fork ssx3`
= `7f022ed…`); runner-dir gate `git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner` empty. Suite 483/483 before commit and before push.

## Diff summary (`ps2xRuntime/src/lib/ps2_memory.cpp`, DMA chain walker)

- Deleted `appendCompactVif1TagData` (transferred tag upper half only for ids
  1/2/5/6/7, and sourced REF data from the wrong address `tagAddr+16`).
- New rule: on VIF0 (`0x10008000`) / VIF1 (`0x10009000`) chain transfers with
  CHCR bit 6 (TTE) set, append the tag's upper 8 bytes (`tp+8..tp+16`, already
  bounds-checked) ahead of the tag's data **for every tag id** (0/3/4
  included); with TTE clear, no tag bytes enter the stream. Payload always
  comes from `dataAddr` (for ids 1/2/5/6/7 `dataAddr == tagAddr+16`, so with
  TTE=1 their behavior is byte-identical to before). GIF channel untouched.
- Net: +11/−26 in the walker.

## Tests (`ps2xTest/src/ps2_memory_tests.cpp`)

- 3 existing VIF1 chain tests now start CHCR `0x144` (STR|CHAIN|TTE) instead of
  `0x104`: DIRECT-compact, qwc-zero ITOP, packet-builder live packet. (With
  TTE=0 their tag-embedded VIF codes correctly no longer transfer; the old
  CHCR values encoded the pre-fix always-transfer assumption.)
- 3 new: REF+NOP;MPG(num=2,slot=4)+16 B payload at ADDR with TTE=1 ⇒ VU1 code
  at slot 4 updated, STR clears; same layout with TTE=0 ⇒ code untouched, STR
  clears (dropped-MPG payload parses as 4 UNK words, verified safe in
  `ps2_vif1_interpreter.cpp` terminal `else`); CNT→NEXT→END chain with TTE=1,
  each tag carrying NOP;MPG to distinct slots ⇒ both slots updated, STR clears.
- Suite from fork root, flags unset: **483/483, rc 0** (480 E37 + 3 new). New
  tests confirmed present and passing by name in the run output.

## Boots (Mac mini, E32-build @ fork `7f022ed`, runner SHA `5fe18fc8…9389`
two matching reads, lease-claimed, all rc 0, lease released)

| Boot | Env | Result |
|---|---|---|
| e38a (A) | vsync route, wall 300, stats 1200–1500, entry `_PCS=0x40,0x10 _VSYNC=1300` | wall-bound 300.75 s, tick ~1373; 174 stats lines 1200–1373; both blocks @1300 |
| e38a2 (A2) | same + `_PCS=0x12B8,0x40,0x10` | wall-bound 302.6 s; 0x12B8 block (80 pairs, 16 MPG) + 0x10/0x40 as in A |
| e38b (B) | vsync route, wall 700, stats 7200–7800 | wall-bound 701.4 s, **tick 6483 only** (vs E33b 7288); presses i=0..8 fired, i=9+ never; stats window missed; ends at pre-race Rival Challenge dialog |
| e38eq | flags-unset, wall 120 (`e32_boot.py`) | EQUIVALENT to E32a: park pc=`0x3b1028`, final `fnv1a=fd889dc5` |

Boot B shortfall: 6483 vs 7288 ticks in the same wall (~11% fewer). Not
attributed to fix tax: the SC settled band below is cycle-identical pre/post
fix, so per-vsync work is unchanged where measured; remainder is scene/timing
drift (char-idle runs 0.4 tick/s; small press-time differences compound).
Stated as gap, not verdict.

## Per-startPC tables

### 0x10 / 0x40 (e38a and e38a2, vsync 1300) — UNCHANGED vs E37

| startPC | Setup pairs | Total | arrivals @0x418 | First pair |
|---|---|---|---|---|
| 0x10 | 129 | 250 | 4 | `LQI vf18,vf13` (`lo=81d26b7c`, vi13 `d549→d54a`) |
| 0x40 | 123 | 244 | 4 | as E37 (non-branch at 0x40) |

Expectation was `B` (`lo=40000048` / `400000f2`). Feeding spans contain
**zero MPG lines** (same UNPACK-only shape as E37: 52-line spans). Pair
streams are identical to E37's (verified: first pairs + arrival counts; full
`pair` diff not run — stated gap).

### 0x12B8 (e38a2 only, vsync 1300) — NEW, healthy, MPGs flow

| Field | Ours (0x12B8) | PCSX2 (0x257, T49-5) |
|---|---|---|
| pairs / end | 80, arrivals=0 (no 0x418 visit) | 80 to E-bit |
| feeding span | 262 lines: NOP 213 / **MPG 16** / UNPACK 9 / DIRECT 8 / FLUSHE 4 / STMOD 2 / OFFSET 2 / FLUSHA 2 / FLUSH 2 / BASE 2 / STCYCL 1 / MSCAL 1 | tail packet 265 lines, incl. 16 MPG + STMOD/BASE/OFFSET |
| MPG addrs (displayed) | 0,256,0,256,0,256,0,193@256 (×2 sets) | 0,256,512,768,0,256,512,193@768 (×2 sets) |
| first pairs | `XTOP vi7`; `IADDIU vi3,vi7,219` (vi3 `15c9→0101`) @0x12c0; `LQ vf17/vf16` | opens ESQRT; vi03 first-write @0x12c0, same instr `lo=100338db`, `02dd→0101` |
| entry vi03 | `0x15c9` | `0x02dd` |

Caveats (do not over-read the addr rows): our MPG log prints `imm & 0x1FF`
(9-bit display alias: true 512/768/1024… print as 0/256/0…), T49 wraps mod
1024 — so command-level imm equality is **unproven** from these traces; and
T49 logs no MPG payload bytes, so payload equality is untestable from traces.
What IS proven: same MPG count/shape/position in the packet, same pair count,
same vi03-writer PC+instruction+result, different vi03 entry, and slot 599
code differs (`XTOP` vs `ESQRT`) while slot 604 agrees.

## Before/after stats vs E33

- Settled SC band (1371–1373): `mscal=583 mscnt=0 vu_cycles=32645598
  vu_exhausted=498 vu_maxcyc=65536 xgkick=85` — **identical to E33/E37 down to
  cycles**. `diff gfx-stats-e33a.txt gfx-stats-e38a.txt`: 22 lines over 8
  transition vsyncs (1242–43, 1267–72: menu-animation floats, e.g. d1_box
  y0 2356.75 vs 2358.56) + 1 extra line (174 vs 173); settled band untouched.
- Decode-cache path re-checked read-only (`ps2_vu1_core.cpp` 1565–1595):
  per-fetch generation check against `getVU1CodeGeneration()`, rebuild on
  mismatch; MPG handler bumps the generation only on a guarded in-bounds copy
  (`ps2_vif1_interpreter.cpp` ~593–625). Stale-cache as the (sole) explanation
  is disfavored at this level — stated, not proven end-to-end.

## Frames (paths + SHAs, viewed by eye)

| Point | File (repo) | SHA256 | Shows |
|---|---|---|---|
| A Select Character settled | `local/research/E38/e38a-sc.png` (= snap-0299.21s) | `498a38ac…3e7c4d8` | Zoe name+bars+silhouettes (one orange), mountain backdrop, **no 3D rider model** — same as E33a |
| B pre-race (tick 6483) | `local/research/E38/e38b-prerace.png` (= upload-latest) | `0a5ce1a3…096c76b85` | 2D "Rival Challenge / Happiness - Race" dialog (Face off against Mac, X Continue), **no 3D world**; race unreached |

## Gaps / notes

- Full `pair`-stream diff E37 vs E38a (0x10/0x40) not run; verdict rests on
  first pairs, arrival counts, and identical settled stats.
- Boot B never entered the race: no race stats exist (window 7200–7800
  missed); "no 3D world" is read at the pre-race dialog, not in-race.
- MPG payload bytes (ours: first 8 words logged; T49: not logged) never
  compared; T49 executed-words at covered slots could supply the PCSX2 side
  (not done).
- In-vsync MSCAL order (does our 0x10 run before/after our 0x12B8 upload?)
  is unknown from these traces; blocks carry no timestamps.
- Bytes: E38-run 155 MB; internal total 26.9/200 GB cap. 4 launches used
  (brief: 3 boots + 1 retry).

## Exact commands

```
cmake --build ~/dev/ssx3-work/E32-build -j8   # fork ssx3 @ 7f022ed
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 483/483
python3 local/research/E38/e38_boot.py --label e38a --wall 300 --snap 2.0 --stats-from 1200 --stats-to 1500 --entry-pcs 0x40,0x10 --entry-vsync 1300 --script "<route>"
python3 local/research/E38/e38_boot.py --label e38a2 --wall 300 --snap 2.0 --stats-from 1200 --stats-to 1500 --entry-pcs 0x12B8,0x40,0x10 --entry-vsync 1300 --script "<route>"
python3 local/research/E38/e38_boot.py --label e38b --wall 700 --snap 2.0 --stats-from 7200 --stats-to 7800 --script "<route>"
python3 local/research/E32/e32_boot.py --label e38eq --wall 120
git push fork ssx3  # 11725b4..7f022ed (runner-dir gate empty)
```

(`<route>` = E33 vsync string
`10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000`;
no main push; fork ff-push + ssx3 commit pending orchestrator.)

## Recommendation (orchestrator decides)

The walker fix is correct and regression-free but is not the missing-3D
mechanism — do not revert it (unit-proven HW behavior, zero measured cost),
but stop this line. The next lane should discriminate, in order: (1) MPG
**payload** divergence — compare our 0x12B8 MPG payload bytes (logged, first 8
words × 16 in `vu1-entry-e38a2.txt`) against PCSX2-side ground truth for the
same slots (T49 traces lack payloads; needs a T-lane re-read or executed-word
comparison at slots 0–960); (2) in-vsync **order** — timestamp MSCALs to test
whether 0x10 runs precede the 0x12B8 upload; (3) if payloads match and order
is sane, the remaining suspect is the **REF ADDR translation/copy path**
(`appendData(dataAddr)` vs the game's address forms) or EE-side chain
construction (game builds different chains from diverged state). Entry-VI
inheritance (E37: `vi03=0xC224` never written; here 0x12B8 entry `15c9` vs
`02dd`) remains a live second fault for the loop-exit regardless of code.
