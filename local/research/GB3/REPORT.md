# GB3 report — in-order priv stores (VQ), SetGsCrt SMODE, paraLLEl live on the Mac

Brief `local/muse/prompts/GB3.md`. Worker: Claude Code (Opus). Tables +
receipts; the orchestrator decides. **Stopped at Part 1 per the stop rule:
the VQ gate still fails after the store routing.** Part 2 was not run: its
code is parked, unbuilt, on a side branch (§6).

## 0. Outcome first

| Item | Result |
|---|---|
| 1.1 Guest priv stores go through the GS worker in order (plus HLE IMR/DispEnv/SetGsCrt writes and the VBlank FIELD flip); load fence kept, now on by default when queued | Done. Unit test proves program order against a queued FINISH/SIGNAL packet (matches direct). With the routing bypassed, the test fails. Suite 606/606 |
| 1.2 VQ gate: queue off vs queue on + fence, two on-boots | **FAIL. 0/26 VRAM match in both on-boots, and the two on-boots also differ from each other (0/26 and 2/26).** Priv regs match at all 26 ticks |
| 1.3 SetGsCrt SMODE1/SMODE2 like the kernel, unit-tested; CPU presenter unchanged with the queue off | **PASS.** SMODE1 = `0x740814504` (NTSC) now reaches the regs through the game's real path. Queue-off present hash and VRAM are identical at all 26 gate ticks and at every sample through tick 4050 (80 ticks) |
| 2 paraLLEl live backend | Not run (Part 1 failed). WIP code parked, unbuilt |

**First differing packet (the stop-rule hand-back):** packet idx **0**. It
is the `sceGsResetGraph` stub's own 128-byte GIF packet (`fnv 3af1a56c`,
path 3). The content is the same in all boots, but the tick differs: off =
tick **40**, on #1 (gb3c) = **39**, on #2 (gb3d) = **41**. From there each
on-boot keeps a constant shift (−1 / +1 / c-vs-d +2) over the next
**49,670–49,793 content-identical packets**. Content first diverges at
tick ~620, a Path1 XGKICK (len 208) whose per-tick animation depends on
the phase. The first CSR read (pc `0x375d10`, `0x12001000`) follows the
same shift: off tick 40 `0x4000`, gb3c tick 39 `0x6000`, gb3d tick 41
`0x6000`.

What this means (read, not proven):

- **The store routing did not cause the divergence, and it can't fix
  it.** The shift is already there at packet 0. Before that packet the GS
  has no work, the guest makes no priv loads (the first CSR read comes
  after it), and the only guest priv stores are CSR writes. So the tick at
  which the game reaches `sceGsResetGraph` is decided before the GS path
  does anything.
- **It's a race, not a systematic offset, and the direct path has it
  too.** The two on-boots landed on opposite sides of off (−1 and +1).
  gb3d's +1 series is exactly GB2's queue-**off** baseline C (§3), so a
  direct boot has landed at +1 as well. GB2's VQ failures vs C (Parts 2,
  5 and 7) were mostly measured against an off boot that was itself
  phase-shifted.
- **Off/off matched here, both at phase 0 (GB2's C shows off can also land
  at +1).** gb3a vs gb3b (different binaries,
  SMODE1 0 vs NTSC) match packet for packet for 582,753 packets, with 0
  tick shift. That holds through tick 4056, where the race load starts,
  and E51 saw the same.
- The early phase is close to host-paced. The first 5 s run 270/275
  vsyncs, about 54–55/s against a 60/s ceiling. In `EeScheduler`, events
  are dual-clocked (cycle deadline + `hostDeadline`,
  `EeScheduler.cpp:2525-2566`). When no guest thread is runnable,
  `waitForEvent` (`:2820-2866`) sleeps until the next host deadline. It
  charges the skipped cycles only if nothing was queued first. The
  hypothesis is that the queue's extra host thread and its per-VBlank
  wake-ups move where an idle wait ends relative to vsync. That
  hypothesis is **not tested**.

## 1. Pins and receipts

- Fork worktree `~/dev/ssx3-work/GB3/PS2Recomp`, local branch `gb3-gs`:
  - fork `ssx3` `eac6cba`;
  - GB2 `c937929..c5fd6f3` cherry-picked clean (`f67e123 bdf58cf a0bde6e
    f1c7cab e630532`);
  - GB3 Part 1 `f9f9a6f`;
  - Part 1b `574354a`;
  - G44 `460e438 8c45d1f 6cfede4` cherry-picked as Part 2 prep (`851fc5a
    8dcb6af 94ea49a`). These are env-gated and don't change the CPU path.
    Merge conflicts were all keep-both, plus one brace fixed in
    `ps2_gif_arbiter.cpp`.
- Side branch `gb3-parallel-wip` `f907deb`: the Part 2 WIP (§6). Nothing
  pushed.
- `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` is empty.
- Build `~/dev/ssx3-work/GB3/build`:
  - Release, Ninja, canonical `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`
    (E50 regen), runtime/aggressive logs OFF;
  - built niced (host load average 19–22 from other lanes);
  - 1 configure + 5 builds: tests, full, incremental ×2, negative control.
- Runners:
  - gb3a ran `496a5ad0aead5498a172170920289b53c1f066b53ba7f9ffd156151c2f7d4a9a`
    (Part 1 `f9f9a6f` + legacy switch, 1 read).
  - gb3b/c/d ran `23e4f44bd3948dab3796e6b7dae939192f9da7f0e359c460cd520033f81c48ee`
    (`574354a`). 2 matching reads: after the build and after gb3d.
- Suite: **606/606** from the worktree root, including the 3 new GB3
  tests (`~/dev/ssx3-work/GB3/suite-p1c.log`).
  - Negative control (routing bypassed): 604/605, and only the
    ordering test fails (`suite-neg.log`).
- Boots: **4/6**, slot 2 (`p_lane_lease.py`), PIDs tracked, released
  cleanly, 540 s each (under 600), display kept awake with `caffeinate`.
- Disk: `GB3/` 3.0 GB + `GB3-run/` 0.9 GB, under the 8 GB cap.
  All-ssx3 76.5/200 GB (`disk_budget.sh`).
- Time: about 3 h of the 8 h box.

## 2. Changes (fork `gb3-gs`)

| File | Change |
|---|---|
| `gs_worker.h` | + `PrivWrite` command (`std::function<void()> apply`), + `DiagPresent` RPC |
| `gs_frontend.{h,cpp}` | `GS::privWrite(apply)` enqueues when queued (runs now when direct or on the worker) + `privWriteCount`. `GS::presentForDiagnostics()` runs the backend's Present into a returned frame with no host-latch side effects (an RPC when queued) |
| `ps2_memory.{h,cpp}` | `setGsFrontend`, `gsPrivStore(apply)`, `gsPrivSync()`. `write32`/`write64`/`writeIORegister` priv branches go through `gsPrivStore` (same RMW bodies as before, now in a lambda) |
| `EeScheduler.cpp` | VBlank CSR FIELD flip through `gsPrivStore` (in stream with guest CSR writes) |
| `Stubs/Helpers/Support.h` | `applyGsDispEnv` through `gsPrivStore` |
| `Syscalls/System.{h,cpp}` | `gsCrtSmode1ForMode`, `applyGsCrt` (SMODE1 per mode, SMODE2 = INT\|FFMD<<1, CRT1 kept on, in stream). `GsSetCrt` uses it. `GsGetIMR`/`GsPutIMR` fence, then read. IMR store in stream. `PS2X_GS_SETCRT_LEGACY=1` kill-switch. One-shot `[gs:setcrt] via=…` line |
| `Stubs/GS.cpp` | **`sceGsResetGraph(0,…)` calls `applyGsCrt`** (see §4) |
| `ps2_pk.h` | Priv-load fence **on by default** when queued. `PS2X_GS_CSR_DRAIN=0` is the kill-switch. Now that stores are async, a load has to fence to see the guest's own store |
| `ps2_vq.h` | Window `PS2X_VQ_FROM/TO/STEP` (default GB2's 26 ticks). Each line adds `priv=`, `pres=` (fnv of presented rows), `pw/ph`. `PS2X_VQ_DUMP_DIR` writes PPMs |
| `ps2_runtime.cpp` | `m_memory.setGsFrontend(&m_gs)` |
| tests | `GB3: SetGsCrt programs SMODE1/SMODE2 per mode like the kernel` (NTSC/PAL aliases, field/frame, VESA/DTV leave SMODE1, SMODE1 field decode). `GB3: sceGsResetGraph(0, ...) applies SetGsCrt's SMODE1`. `GB3: priv stores keep program order vs queued packets (matches direct)`: the worker is held behind a gate while a FINISH+SIGNAL packet is queued, then guest W1C CSR, SIGLBLID, DISPFB1, IMR stores and the FIELD flip. Queued final regs == direct |

Scripts (main repo): `local/research/GB3/gb3_boot.py` (GB2 wrapper + VQ
window/dump, legacy, backend, `--env`) and `gb3_vq.py` (VQ table + gate
+ pk/csr row compare).

## 3. VQ gate (Part 1.2)

Common to all four boots:
- the E51/E33 route string, `PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_SKIP_MOVIE=1`;
- `--vq --vq-from 100 --vq-to 8300 --vq-step 50 --vq-dump --pklog`;
- 540 s wall.

The gate is GB2's 26 ticks (100..1350); later samples are "extra".

| Boot | Binary | Queue | Fence | pklog (2M-line cap) | VQ samples | End |
|---|---|---|---|---|---|---|
| gb3a | `496a5ad0` (SMODE1 never written = legacy) | off | — | to tick 10593 | 165 (to 8300) | race, rc 0 |
| gb3b | `23e4f44b` | off | — | capped | 123 (to 6200) | rc 0 |
| gb3c | `23e4f44b` | on | on | capped | 165 | race, rc 0 |
| gb3d | `23e4f44b` | on | on | capped | 165 | rc 0 |

| Pair | Gate (vram+regs) | Present hash | Packets: content-identical prefix, tick shift | First content diff |
|---|---|---|---|---|
| b (off) vs c (on) | **0/26** (regs 26/26 equal) | 119/122 differ | 49,793, shift −1 from idx 0 | idx 49,793 @ b-tick 621, Path1 len 208 |
| b (off) vs d (on) | **0/26** (regs 26/26 equal) | 120/123 differ | 49,670, shift +1 from idx 0 | idx 49,670 @ b-tick 620 |
| c (on) vs d (on) | 2/26 | 157/164 differ | 49,670, shift +2 | idx 49,670 |
| a (off, legacy) vs b (off) | vram 26/26 (regs differ: SMODE1) | 26/26 gate, 80/80 through tick 4050 equal | 582,753, shift 0 | idx 582,753 @ tick 4056, Path2 len 80 vs 96 (race load) |

Gate rows at tick 100 (submits, priv stores):

| Boot | vram | regs | sub | priv |
|---|---|---|---|---|
| gb3b off | 3949391b | 3d2c63b8 | 547 | 392 |
| gb3c on | 24c509cb | 3d2c63b8 | 558 | 397 |
| gb3d on | dc2e1eaa | 3d2c63b8 | 536 | 387 |

The submit series match GB2's boots exactly, so the attractors reappear on
the new codegen, and one of them was GB2's own "off" baseline:

| Series at ticks 100/150/200/250/300 | GB3 boot | GB2 boot(s) with the identical series |
|---|---|---|
| 547 / 1284 / 2134 / 3514 / 10475 (phase 0) | gb3a, gb3b (off) | G (off), L/M (on + fence) |
| 558 / 1301 / 2151 / 3910 / 10597 (phase −1) | gb3c (on) | B/D (on, no fence) |
| 536 / 1267 / 2117 / 3505 / 10353 (phase +1) | gb3d (on + fence) | **C (off + vq, GB2's baseline)**; K's tick-100 VRAM `dc2e1eaa` = gb3d's |

**GB2's Parts 2–7 VQ baseline C was itself a +1-phase off boot.** L/M
(phase 0) failed VQ against C for that reason, not because of store
order. It also shows that queue-off boots can land in the +1 attractor
too. So the race predates the queue; the queue changes the odds. Full tables: `cmp-b-c.txt`, `cmp-b-d.txt`, `cmp-c-d.txt`,
`cmp-a-b.txt`, `pk-content-align.txt`.

### Presents/s and wall ticks/s (DIAGNOSTIC build: VQ + pklog + frame dumps; mini M5 Pro; host shared with other lanes)

| Boot | Queue | Elapsed s | frame:dump | Presents/s | Max tick | Ticks/s | Tick at 30/60/120/180/240/300 s (snaps) |
|---|---|---|---|---|---|---|---|
| gb3a | off | 540.2 | 13,891 | 25.71 | 14,341 | 26.55 | 1035/1930/3775/7014/8385/9632 |
| gb3b | off | 540.5 | 6,069 | 11.23 | 6,237 | 11.54 | 889/1374/2372/3552/4212/4467 |
| gb3c | on | 540.3 | 12,729 | 23.56 | 14,318 | 26.50 | 1170/2145/4500/7722/9042/10267 |
| gb3d | on | 540.2 | 10,046 | 18.60 | 10,525 | 19.48 | 916/1676/3205/4771/6340/7509 |

**Not comparable as speed.** gb3a and gb3b ran the same guest stream to
tick 4056, yet gb3b took twice the wall time to reach tick 1930. Host
contention on the mini (load average up to about 22 from other lanes'
builds and boots) dominates. After tick 4056 the boots take different
routes. With the fence on, presents per tick stay close to off
(c ≈ 0.89/tick vs a ≈ 0.97/tick). GB2's no-fence 3× drop doesn't recur.

## 4. SetGsCrt (Part 1.3)

- **Real values.**
  - NTSC SMODE1 = `0x0000000740814504`, SMODE2 = `0x1`. That's the priv
    block in the G13 PCSX2 GS dump of SSX 3 (real BIOS;
    `~/dev/ssx3-inputs/g13/g13-dump.gs`, block at offset 0x52c233).
  - The field list matches PCSX2 `pcsx2/GS/GSRegs.h` (rev `9056c0834`,
    fetched read-only to `~/dev/ssx3-work/GB3/pcsx2-ref/`): CLKSEL=1
    CMOD=2 LC=32 NVCK=1 PRST=1 RC=4 SLCK2=1 SPML=4 T1248=1 VCKSEL=1.
  - PAL = CMOD 3 (`0x740816504`), from the same comment. There is no PAL
    dump, so this value is taken from PCSX2's field list, not observed.
  - Mode numbers follow PCSX2's SetGsCrt hook (`R5900OpcodeImpl.cpp`):
    0/2 NTSC, 1/3 PAL. VESA/DTV/DVD modes aren't modelled; SMODE1 is left
    as it was.
- **Found on the first boot.** SSX 3 never makes syscall 0x02. Its
  display setup goes through the **HLE `sceGsResetGraph` stub**. The real
  library calls `SetGsCrt(interlace, omode, ffmode)` at that point; the
  stub didn't, which is why SMODE1 stayed 0 in G44 and gb3a. The stub now
  calls `applyGsCrt`. Receipt on gb3b/c/d:
  `[gs:setcrt] via=sceGsResetGraph interlaced=1 mode=0x2 field_frame=0
  smode1=0x740814504 smode2=0x1`.
- **CPU presenter unchanged.** gb3a (SMODE1 0) vs gb3b (SMODE1 NTSC),
  queue off:
  - present hash and VRAM identical at all 26 gate ticks and at every
    sample through tick 4050 (80 ticks);
  - by construction, `GSPresentationRequest` carries no SMODE1
    (`gs_frontend.cpp` `buildPresentationRequestUnlocked`).
- **Presenter check sources.** gb3a is on the Part-1 binary before the
  stub fix, so it is the legacy case. The `PS2X_GS_SETCRT_LEGACY=1`
  switch exists but wasn't needed.
- **Consequence for paraLLEl.** A real scanout backend now sees CMOD=NTSC
  and LC=32 from the game's own setup, so `PS2X_GS_SHADOW_FORCE_SMODE1`
  shouldn't be needed. That is **not validated with paraLLEl** (no Part 2
  boot).

## 5. Why GB2's store-ordering mechanism doesn't hold (code read)

GB2 §15.4 put the VRAM gap down to priv-store vs packet interleaving. On
this tree:
- the CPU raster path never reads priv regs;
- the only priv reads in the GS are `buildPresentationRequestUnlocked`
  (Present, read-only on VRAM) and the SIGNAL/FINISH/LABEL writers;
- `GSCpuBackend::Submit` draws immediately, and `Flush`/`Sync` are
  no-ops.

So VRAM is a pure function of the GS command stream, and store order
can't change it. The failing gates always come with a shifted or
different packet stream: GB2's C had sub 536 vs L's 547 at tick 100, and
here the ticks shift from packet 0.

## 6. Part 2: not run; WIP parked

Branch `gb3-parallel-wip` `f907deb` is on top of `gb3-gs`, **not compiled
and not booted**:
- `GSRasterBackend` gets raw-GIF hooks: `WantsRawGif`, `RawGifPacket`,
  `RawWriteRegister`.
- The frontend feeds each raw packet with its arbiter path, and feeds
  HLE register writes. It still decodes packets for CSR and transfer
  state.
- `ps2x_gs_parallel::GSParallelBackend`:
  - initializes on the GS worker using G44's recipe;
  - copies the priv regs at each Present;
  - does flush + vsync + one CachedHost readback into a 640-stride frame;
  - `SnapshotVram` goes through `map_vram_read`; local→host through
    `read_transfer_fifo`;
  - HLE clears and debug VRAM I/O are counted as unsupported.
- `PS2X_GS_BACKEND=parallel` forces the queue on and swaps the backend by
  RPC. The P6/P7 native fast paths go through the arbiter while it is
  active.
- A matched-tick CPU reference is ready: the gb3b PPMs
  (`~/dev/ssx3-work/GB3-run/vqdump-gb3b-1`, 123 ticks, 100..6200). The
  race frames are in `vqdump-gb3a-1`/`-c-1`.

## 7. Gaps

- The mechanism behind the attractor choice isn't identified. The
  host-paced idle-wait hypothesis (§0) is untested. Two on-boots were run
  (brief); a full N-run distribution isn't sized.
- Off/off determinism past tick ~4056 (race load) is unproven: a vs b
  were different binaries, and E51 saw the same divergence.
- Wall rates are contaminated by host load (§3).
- PAL SMODE1 is taken from the PCSX2 field list, not from a PAL dump.
- The gb3a runner `496a5ad0` has 1 SHA read (it was rebuilt before a
  second read). It's a non-device binary.

## 8. Recommended next action (the orchestrator decides)

1. **Stop gating the queue on free-running VQ.** Packet 0 already
   differs by ±1 tick, before any GS work. That's a timeline race outside
   the GS path, and no GS-side ordering fix can close it.
   - Option A: gate queue correctness on **stream-replay equality**.
     Capture off-boot packets, replay queued, byte-compare VRAM. GB2
     Part 1's captured-stream test is the template; extend it to the full
     2M-packet pklog capture.
   - Option B: pin the timeline so both modes see the same guest stream,
     then run the VQ.
   - At minimum, any free-running VQ pair must first check that packet 0
     lands on the same tick in both boots. That check would have caught
     GB2's C baseline.
2. To confirm the host-paced hypothesis cheaply, run one off boot with a
   dummy idle host thread that wakes per VBlank, or one on boot with
   `PS2X_GS_QUEUE=1` and the worker parked. Either should reproduce or
   remove the ±1 shift before packet 0.
3. Part 2 can proceed independently of this gate:
   - build `gb3-parallel-wip` with `PS2X_GS_SHADOW_PARALLEL=ON`;
   - boot `PS2X_GS_BACKEND=parallel` with the same VQ window and dumps;
   - compare against the gb3b/gb3a PPMs at ticks where the pklog shows
     the same stream. It has to be the same stream, not only the same
     tick number, because the phase shift applies here too.
4. Keep the SetGsCrt / `sceGsResetGraph` fix (Part 1b). It retires the G44
   SMODE1 override for real scanout backends, and the queue-off presenter
   is unchanged.

## 9. Exact commands

```
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GB3/PS2Recomp -b gb3-gs eac6cba
git cherry-pick c937929 a77b933 b975930 1234451 c5fd6f3        # in the worktree
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_GAME_CODEGEN_DIR=$HOME/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF   # in ~/dev/ssx3-work/GB3
nice -n 10 cmake --build build -j8
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)                     # 606/606
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
python3 local/research/GB3/gb3_boot.py --label gb3{a,b} --wall 540 --snap 10 --script "$ROUTE" \
  --vq --vq-from 100 --vq-to 8300 --vq-step 50 --vq-dump --pklog
python3 local/research/GB3/gb3_boot.py --label gb3{c,d} ... --gs-queue 1 --csr-drain
python3 local/research/GB3/gb3_vq.py boot-gb3b-1.log boot-gb3c-1.log --pk pklog-gb3b-1.txt pklog-gb3c-1.txt
```
