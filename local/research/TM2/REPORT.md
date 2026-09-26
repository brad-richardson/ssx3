# TM2 — who writes the rider position and the race clock?

Worker: Muse Code, brief `local/muse/prompts/TM2.md`, 2026-09-26 ~00:00–00:45 EDT.
Observation only; no behaviour change, no fix. No push. No `docs/` edits.

## Outcome

The rider triple at `0x5409c0` is written by **one EE `sq` at guest PC
`0x120e40`** (in `sub_00120E30`), called every VBlank from `sub_00121818`
(ra `0x1218bc`) on EE **thread 1** — the same thread that runs the drain /
app update / render dispatch. It is a **snapshot copy**: `[a0+0x110]` (live
position + w=1.0) → `[[a0+0x78c]]` (= `0x5409c0`), once per VBlank, after the
app update returns and outside the render call's stack frame. No DMA writes
(the new SPR_FROM rows are silent over 101 VBlanks). The true integrator is
whatever writes `[obj+0x110]` — one level deeper, named as the next probe.

The HUD clock's ultimate input is attributed one level: `A+0x1c` (update
counter) is incremented by the drain at `0x3171a4` on thread 1 immediately
before the app-update dispatch, exactly once per VBlank (TM1's exact slope
`HUD=(updcnt−1690)/60` stands). The render-time `/60` formatter itself was
**not found**: no integer div/mult, no `/60` or `/3600` (int or float)
constant, and no float→int convert in the render body, its 10 direct callee
targets, or the consumer/producer/update functions; the ELF has no
printf-style time
format string. The formatter sits deeper (likely behind the render's indirect
`jalr` calls).

## Watch coverage audit (brief Facts check)

| Path | Covered before TM2? | After |
| --- | --- | --- |
| (a) EE stores through FAST RAM path | YES — `WRITE*` macros report pre-store, before `FAST_WRITE*` (`ps2_runtime_macros.h`) | unchanged |
| (b) DMA writes into RDRAM | NO — `SPR_FROM` memcpy had no watch call | YES — `ps2DiagWatchReportRange` post-copy rows with `pc=0/thread=-1` (commit `86388ec`); IPU/SIF0 DMA into RDRAM are not implemented in this runtime, so there is nothing else to cover |
| (c) 128-bit stores (`SQ`, `SQC2`) | YES — `WRITE128` + `Store128` report width=16 | unchanged (the rider writer is one `sq`, observed as width=16) |

Also added in the same commit: `PS2X_DIAG_WATCH_TICKS="from-to"` (inclusive,
det-hash numbering) gating macro/Store/DMA rows; unset = log all ticks
(historical behaviour). Legacy `[diag:watch]` line format unchanged.
Not covered (stated gap): HLE syscall stubs that write RDRAM via raw `rdram`
pointers (Font/GS/FileIO/CD); nothing suggests they touch these addrs.

Tick-window alignment (read carefully): the window is evaluated on the
store-time vsync tick, which reads N during interval (VBlankStart N,
VBlankStart N+1], while TM1's `tm1-vblank` line N+1 summarises that interval.
So `PS2X_DIAG_WATCH_TICKS=1799-1899` aligns with TM1 lines 1800–1900 (101
VBlanks, 101 stores of each watched word — exact).

Each watched address names an 8-byte window, so one width-16 store at
`0x5409c0` matches all three watch windows → 3 identical lines per store
(303 lines = 101 stores). Likewise one width-4 store at `0x4c9444` matches
two windows (202 lines = 101 stores). Counts below are de-duplicated stores.

## Writer table (0x5409c0/4/8, TM1 lines 1800–1900)

101/101 VBlanks identical in writer, path, caller and thread (boots 2 AND 3
agree — a two-run repeat with different watch sets):

| What | Value |
| --- | --- |
| Guest PC | `0x120e40`: `sq $v0, 0x0($v1)` with `$v1` = `0x5409c0` (width=16: xyz + w=1.0) |
| Owning function | `sub_00120E30` `[0x120e30,0x120e50)`: `v1=[a0+0x78c]; if (v1) [v1]=[a0+0x110]` (128-bit snapshot copy) |
| Write path | EE store (`SQ`); DMA ruled out (zero `pc=0/thread=-1` rows; IPU/SIF0 DMA unimplemented) |
| Value | smooth: `(2871.045,-45500.219,95574.406)` → `(3621.608,-45229.020,94968.234)`, w=1.0 always; mean step 10.09, max 11.15, path 1008.5 over 100 steps (see `tm2-motion.txt`); first store bit-matches TM1's tick-1800 sample |
| Tick cadence | exactly 1 store per VBlank, 101/101 |
| Chain position | after the app update returns (`tm1-update` line precedes the store triple every interval); outside the render call (see Timing) |

## Call chain (one level up)

- Writer caller: `sub_00121818`, return address `0x1218bc` (call at
  `0x1218b4: jal func_120E30(a0=s0)`, unconditional tail of the function).
- Thread: EE thread **1**, sp `0x1fffe60` — same thread and stack region as
  the drain (`updcnt++` at sp `0x1ffff40`, thread 1). Not a separate physics
  thread, VU op, or DMA.
- Not taken on this route: the writer's second call site `0x128bc0` (in
  `sub_00128AF0`) — all 303 lines show ra `0x1218bc`.
- Two levels up (context, beyond the brief's one): `sub_00121818` is called
  from `0x128ea4` (in `sub_00128AF0`, size 0x670), which is itself reached by
  **indirect** call (its address sits in the `.rodata` table at `0x4584a4`;
  no static caller). Resolving that indirect edge needs a dispatch-target tap.

## Timing within the VBlank

Observed order every interval (store-tick N), thread in brackets:

1. `A+0x18`++ at `0x317380` [thread 4] — producer-wrapper count
2. `A+0x1c`++ at `0x3171a4` [thread 1] — drain, immediately before the
   app-update dispatch at `0x3171b4` (ra `0x317188` is stale, set by the
   catch-up-loop `jal` at `0x317180`)
3. app update `0x2306b8` returns (`tm1-update` line; pos unchanged — TM1
   reproduced)
4. **rider snapshot store at `0x120e40** [thread 1]
5. next `tm1-vblank` line (samples the new pos)

Render-relative placement: the render entry `0x22b008` opens with a
`0x83e0`-byte stack frame, but the writer's sp (`0x1fffe60`) sits only
`0xe0` below the drain's sp (`0x1ffff40`) — so the store runs **outside the
render call's frame**. Whether it runs before or after the render *dispatch*
(sites `0x317208`/`0x31723c`) is unresolved: both orders fit, and TM1's tap
has no render entry/exit stamps (its noted gap). Falsifiable next step: add
render entry/exit lines (1 build + 1 boot).

Thread map (by role; numeric→name mapping is not logged): thread 1 = drain /
update / render-dispatch / snapshot worker (stack near top of RAM); thread 4
= producer-wrapper thread (own stack at `0x608850`).

## HUD-clock source

- Input (attributed): `A+0x1c` at `0x4c9444`, incremented by the drain at
  `0x3171a4` on thread 1, once per VBlank, immediately before the update
  dispatch (`tm2-updcnt-lines.txt`: 101 stores, values `0x6d6`–`0x73a` =
  updcnt 1750–1850). The race-start offset (−1690) storage was not located.
- Formatter (not found): no `div`/`divu`/`mult`/`multu`/`mflo`/`mfhi` in the
  render body after `0x22b008`, in the consumer (`0x227e98`), or in the
  update (`0x2306b8`); no `60`/`3600`/`0xe10`/`0x42700000` constant and no
  `cvt.w.s` in the render body, its 10 direct callee targets (`0x22e8b8`,
  `0x22e920`, `0x231d60`, `0x22c830`, `0x36a1e8`, `0x31b6c8`, `0x230640`,
  `0x229ba8`, `0x344138`, `0x357c50` — the one div found, in `0x31b6c8`, is a
  float matrix normalize), or the consumer/producer/update files; ELF string
  search for printf-style time formats returns only binary noise (custom
  glyph path). The `/60` site is deeper, probably behind the render's
  indirect `jalr` calls (`0x22b060`, `0x22b088`, `0x22b0dc`, …).
- Consequence for the 120 Hz program: the clock reads a drain-side counter,
  so doubling the update rate without touching the formatter would run the
  clock at 2× — the formatter (once found) and the −1690 base both need the
  rate change.

## Non-perturbation

All three boots `IDENTICAL` to
`a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` (ticks 1–2400 + snd/coverage):
the unset control (required step 4) AND both armed runs (bonus). Zero
`tm1-capped` / `tm1-badptr`; 601/601 `tm1-update` + `tm1-vblank` lines in
both tap boots. Bonus: the true tip `fb28d99` is det-identical to TM1's base
build — the intervening VK1 (present-path) work does not affect guest
determinism. (Diagnostic boots, not speed numbers.)

## Exact commands, pins, SHAs

- Worktree `~/dev/ssx3-work/TM2/PS2Recomp`, branch `tm2` (never pushed):
  fork `ssx3` tip `fb28d99` (`[VK1] aspect-exact child rect…`, 2026-09-25;
  fetched from GitHub — the local `~/dev/PS2Recomp` checkout was stale at
  `f949ff0`/09-24, which lacks `ps2_guest_unwind` and cannot compile the TM1
  hunk) + `449026e` (cherry-pick of TM1 `cdaa331`, clean) + `86388ec`
  (`[TM2] Watch coverage: SPR_FROM DMA rows + PS2X_DIAG_WATCH_TICKS window`,
  3 files, +118/−2). Runner-dir check
  `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty.
- `local/tooling/build/mac_build.sh`: added `--diag` (4-line diff, per brief).
- Build 1/2: `mac_build.sh …/TM2/PS2Recomp …/TM2/build-det-diag --det --diag`
  → runner `58bd2e48d8b6ae81be829dcfc7e1f840f9fa95ae8ab1d8cdfa2a1c9fecdcbb37`
  (2 reads match), 416,375,376 B. Syntax pre-check of both edited TUs passed
  (`-fsyntax-only` with HR1 compile commands; caught the stale-base unwind
  issue before building).
- Boot 1/4 `tm2-unset` (control): `ssx3_boot.py --host mini --mode det
  --backend parallel --runner …/build-det-diag/…/ps2EntryRunner --label
  tm2-unset --out …/TM2/tm2-unset --route fr1r1 --stop-tick 2400 --sound on
  --wall 600` → target, t2410, 67.0 s, slot 1, log 1,164,059 B.
- Boot 2/4 `tm2-watch` (target): same + `--dump-ticks 1800,1900 --env
  PS2X_DIAG_WATCH=0x5409c0,0x5409c4,0x5409c8 --env
  PS2X_DIAG_WATCH_TICKS=1799-1899 --env PS2X_TIMING_TAP=1` → target, t2411,
  64.9 s, slot 1, log 1,740,704 B, 303 watch lines = 101 stores.
  Frame-fnv records: tick 1800 `22136e8c`, tick 1900 `5efc3a24` (per-tick
  PNGs are not kept by the boot script — only the log records).
- Boot 3/4 `tm2-updcnt` (counter+repeat): watch
  `0x5409c0,0x5409c4,0x5409c8,0x4c9440,0x4c9444`, same window+taps → target,
  t2403, 67.0 s, slot 1, log 1,760,717 B, 606 lines (303 rider + 202 updcnt
  + 101 wrapper; 1 line cosmetically mangled by a concurrent FILEIO stderr
  write — value/pc intact, counted by sequence).
- Compares: `baseline.py compare --key
  a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand …/TM2/tm2-{unset,watch,updcnt}`
  → all three IDENTICAL.
- Receipts: `tm2-watch-lines.txt` (303 canonical watch lines),
  `tm2-updcnt-lines.txt` (606), `tm2-motion.txt` (101 decoded xyzw).
  Full logs: `~/dev/ssx3-work/TM2/tm2-{unset,watch,updcnt}/` (outside git).

## Gaps and next

- The live position `[obj+0x110]` (the snapshot SOURCE) has no attributed
  writer yet — that is the true integrator the 120 Hz work needs. Next
  probe: log `$a0` at the `0x1218b4` call (or extend the watch to a
  dynamic base), then watch `[obj+0x110]` for one window. It may be
  integrated inside the app update (the triple's stability across the update
  does not rule that out — the triple is downstream of it).
- Render-dispatch-relative order of the snapshot (before vs after sites
  `0x317208`/`0x31723c`) needs render entry/exit stamps.
- The indirect caller of `sub_00128AF0` (vtable at `0x4584a4`) is
  unresolved; a dispatch-target tap would close it.
- HUD `/60` formatter not found (negatives listed above); same
  dispatch-target tap on the render's `jalr` sites, or a watch on a located
  digit/seconds buffer, is the way in. The −1690 race-start base is also
  unlocated.
- HLE-stub direct-RDRAM writes are unwatched (judged unlikely for these
  addrs; re-audit if a future window shows an unattributed change).
