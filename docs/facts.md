# Verified facts

Mechanisms and gotchas established by gated lanes, for writing briefs and reading code. Each
line names its source lane (`local/research/<ID>/`). Standing rules live in `AGENTS.md`;
orchestration lessons in `docs/orchestration.md`.

## Guest (SSX 3 on the EE)

- Music is EE-mixed PCM: EA-XA decoded and mixed on the EE at 36 kHz stereo, 384 frames per
  sound tick in tag 1; the sound tick is 93.75 Hz of guest time. **The tag-1 payload is planar:**
  384 s16 for one channel, then 384 for the other; the first block feeds the SPU2 **right** input.
  SNDDRV resamples 3→4 (linear, phase 0.5 from the saved last sample) to 48 kHz. At Select Character
  PCSX2's final output is exactly that, with no IOP-mixer, voice or reverb content. (AU8; AU2–AU7
  read it as interleaved, which is wrong.) The tag-1 record `0x512E40` sits inside DMA buffer
  `0x512B80`. (AU2, AU4)
- Movie end: the guest reads `[[mpeg+0x40]+0]` at `0x402b38`; the MPEG HLE writes the
  `sceMpegIsEnd` word. `0x548840` is the single startup-movie codec pool node. (E48, E49)
- Widescreen: options block `0x535610` bits 20–21 (0 off / 1 16:9 / 2 anamorphic), applied by
  `0x228c08` → vtable `0x377950`; profile loads re-apply via `0x152bb0`. (W1)
- Load game issues GetDir `/BASLUS-20772-GAM*` at tick 1740 on an empty card. (E55D14)
- Memory card: our `mc0` is a host directory (`PS2X_MC_ROOT`, else `<elf dir>/mc0`); GetDir synthesizes
  attributes and uses host mtime. SSX 3 autoloads `BASLUS-20772-SET*`/`GAM*` at boot (ticks ~118–373),
  which delays the title ~200 ticks. PS2 card images decode as 528-byte pages, 2-page clusters,
  physical = FAT cluster + alloc offset (41 on Brad's card). (E55D16)
- SSX 3 never calls `SetGsCrt` (syscall 0x02); the `sceGsResetGraph` stub applies NTSC SMODE1
  `0x740814504`. `SMODE2=0x1` field bob → `PS2X_DEINTERLACE=weave` default. (GB3, E32)
- SSX 3 uses UCAB (`0x30000000`) for DMA-bound data: a trace fold of `& 0x1FFFFFFF` misses those
  stores. (T58, T59)
- Missing indirect-call targets: `PS2X_MISSING_FUNCTION_POLICY` (dev `stop`, release
  `continue`) plus counters; add targets via `extra_function_starts` in `games/ssx3/ssx3.toml`.
  The Ghidra sweep CSV can merge getter clusters into one function (e.g. `0x396b40` inside
  `sub_00396958`; `0x3c9520`/`0x3c95f0` inside `sub_003C9420`). (E46, E56, AU3)

- `DATA/CONFIG/SLUSOVF.BIG` is a BIGF archive of `overlay.dat` (0x1903ac B, a relocatable MIPS
  ELF: EE code overlay) + `config.dat`. It was unreachable before AU9's `0x3E3968` fix (the
  file-table bsearch missed it); whether the route now loads/executes it is CT1's question.
- The game's file table is qsort-ed with comparator `0x3E3968` (`dsubu` + `bltz/bgtz`); with
  32-bit sign branches, bsearch misses `banks.inf` and 5 other files, so no SFX banks load. (AU9)

## Runtime semantics and builds

- FP model: `-ffp-contract=off` (clang fuses MADD otherwise); EE thread RTZ + FZ like PCSX2.
  Before E53's IEEE scope, PATH1 was rasterized under the VU core's RTZ rounding. (E52, E53, GB4)
- `long double` is quad soft-float on arm64 Android (plain double on Mac); VU1 uses
  `VuWide=double`. (E45)
- Speed builds need `PS2X_ENABLE_DIAG_TAPS=OFF`: with taps, guest `.text` is 3.2× and every
  store calls a tap. (N5)
- Determinism: free-running boots aren't frame-deterministic (the RNG was seeded from host time
  via `sceCdReadClock`); use `PS2X_DETERMINISTIC=1` (fixed RTC, guest-cycle event order) and the
  VBlank XXH64 tap for A/B. (E55A2, E55B2, E55C2)
- Live presents are torn at wall-clock-racy cut points; CPU-backend VRAM is a pure function of
  the GS stream, so gate GS changes by capture + replay. (GB2, GB3)
- `PS2X_FRAME_DUMP_ONCE_TICKS` accepts three entries; gfx-stats `top` is (FRAME.fbp,
  PRIM.type); E43/MPG logs flush every 128 lines, so SIGTERM drops the tail. (GB6, E47)
- Replay and `ps2x_tests` are desktop-only; Android sets `PS2X_BUILD_TEST=OFF`. (N8D7M12)

- Models the fixes rely on (RR1/RV3): PATH3 data queued while masked is released one EOP packet per
  `MSKPATH3 0` window; the GIF arbiter still stable-sorts a drain by path (GA1 measures
  inversions); DMA completes at the CHCR store; chain walker has a runaway guard, not a 4096 cap;
  VU1 runs with a 65,536-cycle budget per program (cap hits = a bug, PCSX2 max 23,540), VU0 4,096;
  INTC dispatched: VBlank 2/3, timers 9–12 only. The CPU GS backend lacks dither, mip/LOD,
  COLCLAMP, AA1, SCANMSK: it is **not a pixel reference**; PCSX2 gsrunner on our stream is. (RV3)
- Mac GS default is paraLLEl (`PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=
  /opt/homebrew/lib/libvulkan.1.dylib`, build `PS2X_GS_SHADOW_PARALLEL=ON`); det-hash is
  identical to the CPU backend. Speed boots are unpaced: ratios > 1 mean headroom. (GB8, F1)
- Mac boots also set `PGS_HIER_BINNING=force` (paraLLEl-GS fork `ssx3` `19d93b2`): the Odin's
  hier-if-large binning (t2=2, t4=4) runs correctly on M5/MoltenVK (bit-identical to flat). What
  stays Odin-only: subgroup width (Apple 32 vs Adreno wave64; can't be forced either way),
  descriptor buffers, Turnip driver CPU cost/thermals, Adreno bilinear rounding. (GB9)

## Odin / Android / GPU

- paraLLEl-GS's hierarchical binner mis-bins at wave128 on Adreno (Apple never uses it); the
  fork forces wave64. Mac vs Adreno hardware bilinear rounding differs by ±1–2 LSB. (N8X1)
- Ship Turnip: the proprietary Adreno driver loses composite draws, varying per run. Turnip HAL:
  `hw_device_t` has `reserved[12]`; `GetInstanceProcAddr` is at offset 136. The app namespace
  lacks `libhardware.so`, so Turnip needs an app-local shim whose `hw_get_module` returns
  `-ENOENT`. (G40–G43, N8B2–N8C2)
- Android input: raylib reads keyboard and gamepad together; inject with `sendevent` on event8
  (gamepad) / event5 (keyboard); `input keyevent BUTTON_*` never reaches the game. (N6)
- simpleperf on the Odin works with `--app`, not `-p`. raylib `fopen`/`ExportImage` fails in
  the app dir: use `ExportImageToMemory` + `std::ofstream`. (N4, N8D5E)
- Android stdout→logcat keeps at most 1,023 chars per record, and drops lines on big bulk
  flushes: pull on-device output files instead. (N8D5L, N8D7M13)
- The Android emulator (AVD) can't create a Turnip device on its virtual GPU: glue tests only.
  (NAVD1)
- On the mini the only `Controller` HID match is an internal NAND sensor, not a gamepad. (E55D4)

## iOS

- Pinned raylib SDL2 `GetWindowScaleDPI()` returns 1; I27B's DPI patch fixes the viewport.
  Without an iPad device family the app runs in an iPhone-compat portrait window. (I27, IPAD1)

## PCSX2 reference

- T48 VU1 startPCs are in 8-byte units: PCSX2 `0x0/0x2/0x8/0x73` = ours `0x0/0x10/0x40/0x398`.
  Healthy VU1 programs: ≤ 2,090 cycles at Select Character, race max 23,540. (E36, T48)
- PCSX2 runs zero VU0 micro-programs and zero VIF0 words at settled Select Character. (T57)
- Healthy Snow Jam load: ENTER → race in ~109 emu-s, one continuous 990-iteration `_sceCdSC`
  loop, 1.75 MB SPU voice upload. (T47)
- `local/research/G46/g46_rec2gs.py` converts our GS stream to `.gs` for PCSX2 gsrunner. (G46)

## Workers

- OpenCode's `../*` edit rule overrides a scoped allow when the pane starts in `ssx3`: launch
  fork-editing opencode workers from the private worktree cwd. OpenCode `ssh` is denied. (E55D14,
  GB7C7, N8D7M12P6M6)
- Local Qwen: bounded, scripted extraction with an immutable checker; semantic verdicts stay
  with the orchestrator; an empty LSP result is a tooling gap, not proof of no callers. (X9–X14)
