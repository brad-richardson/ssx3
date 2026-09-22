# Adreno filing draft — Vulkan sampler returns cleared pattern for stale-but-valid VRAM source (SM8750, Android 15)

Target: Qualcomm Developer Network forums (Adreno GPU SDK), per the
Vulkan-Errata driver-id directory. To be posted by the owner from
their account. All claims below are receipted in
`local/research/G28/`–`G32/` (gate-verified by an independent second
read); binaries/dump/logs available on request.

---

**Title:** `sample_circuit`-equivalent VRAM sampling path returns uniform
cleared pattern while addressed source holds stale bytes (Adreno 830,
Android 15, Granite)

**Environment**

- Device: AYN Odin 3 (`Odin3`), SoC SM8750 (Snapdragon 8 Elite),
  Adreno 830, Android 15 (`Odin3_V1.0.0.151_20260204` user build).
- App: Granite-based PS2 GS dump replayer (native shell binary,
  Vulkan, `PGS_SKIP_COMPILATION_TASKS=1`, 2-iteration bounded run,
  non-sanitizer). No validation errors; run exits 0.
- Driver: stock proprietary (`VK_DRIVER_ID_QUALCOMM_PROPRIETARY` path).

**Observed behavior**

A compute/circuit sampling stage reads a display framebuffer region
(FBP=112, FBW=8, PSM=1, 512×448 output) and emits a UNIFORM cleared
pattern (`00 00 00 80` per pixel) on all 10 output images, while the
addressed VRAM source provably holds stale (non-cleared, non-uniform)
bytes at every sample time — BUT emits its source byte-exactly when
the sampled pages are host-committed (map-write + flush + barrier)
before each sample. The sampler's full input state is pinned and
logged (`DISPFB=112/8/1/0/0`, `DISP=2560/447/4/0/641/50`,
`super_samples=1`, `vram_size-1` spec); backbuffer promotion is
provably OFF both structurally (flag default `false`, setter uncalled
anywhere, register/lookup dead) and on-device (16/16 null promotion
queries across 8 vsyncs × 2 passes).

**Controlled experiments (each: one diagnostic hunk, one build, one
bounded run, verify-then-push, zero new tombstones)**

1. Readback ladder (3 independent paths: file-writeback, post-display
   frame, pre-display VRAM): all agree bit-exactly
   (FNV `aa2fa32572450383`, 229,376/229,376 nonzero) — readback is
   exonerated; the zeros originate upstream in the render path.
2. Pre-restart VRAM page dump (512 pages × 8 KiB, FNV + nonzero +
   head per page): 174/174 upload-target pages land BYTE-EXACT vs a
   host-computed prediction (last-write-wins map over 593 traced
   transfers, 38 buffer pages, swizzle port differentially tested
   96,632 vectors / 0 mismatches); 112/112 scene pages + 112/112
   Z pages show landed raster; 2/2 never-touched control pages
   unchanged; 0 stray pages. Uploads land; raster executes.
3. In-`vsync()` state dump at all 16 sample times: promotion null
   ×16, sampled region == stale load-state bytes ×16 (FNV match to
   host-computed region hash), while circuit output is uniform
   cleared. No cleared 512×448 region exists anywhere in the 4 MiB
   VRAM image, so the emitted pattern matches no readable source.

4. Host-committed pattern probe: with a two-zone controlled pattern
   (address-echo words + constant, zero zero-RGB words) written +
   committed before every sample, the circuit emits the pattern
   EXACTLY — 10/10 outputs byte-identical to a host swizzle-model
   render (sha-unanimous), 229,376/229,376 pixels in-set, 0 zero-RGB.
   Same sampler path, same regs/knobs as experiment 3. Addressing,
   decode, and descriptor fault are all refuted; the remaining split
   is ordering/coherency (the commit/barrier fixed it) vs
   content-dependent fault (the pattern content fixed it) — our next
   experiment is a write-back control (same sync, stale bytes
   re-written) to close it.

**Question**

Is the stale-without-commit → cleared behavior a known
ordering/coherency expectation on the Adreno sampling path (i.e. is a
host commit/barrier required for content written this way to be
visible to the sampler), or does it look like a driver bug? We can
provide the replayer binary, the GS dump, per-page checksums, and the
exact sampler/push-constant state. Happy to run any additional
diagnostics you suggest (we have not yet tested the freedreno/Turnip
path — currently queued as our contrast experiment).

---

*Orchestrator note: synced with G32 (ordering/coherency reframe) on
09-21. G33 (write-back control) may upgrade the question again — check
before posting if G33 has landed. Do not post without owner review.*
