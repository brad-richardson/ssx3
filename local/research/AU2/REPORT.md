# AU2 REPORT: SND protocol table + IOP tick spike (EE-mixed PCM vs IOP-side XA)

Brief: `local/muse/prompts/AU2.md`. Worker: Claude Code (Opus pane, same
context as AU1). Tables and receipts; the recommendation is in AU2-5.

## AU2-1. Part A: the SND protocol (static)

Sources: SNDDRV.IRX disassembled with its own symbols
(`/opt/homebrew/opt/llvm/bin/llvm-objdump -d -r --triple=mipsel`, full
listing `snddrv-disasm.txt`); EE code via `local/tooling/ee/ee-at|ee-xref|ee-label`.
IOP addresses are SNDDRV-relative (module loaded at its link address 0 for
this reading).

### Transport

| Direction | Mechanism | EE side | IOP side (SNDDRV) |
| --- | --- | --- | --- |
| EE→IOP, once | SIF RPC SID `0x534E44`, fno 0 (init), 1 (restore), 2 (reverb init / restore) | `sub_003C0B10` → `sceSifCallRpc(0x50B980, fno, mode=(fno==2), send 0x50AD00, size)` | `SNDIOP_dispatchrpc` (0x8BF0) via `threadmain`'s GetNextRequest/ExecRequest loop |
| IOP→EE, every IOP cycle | `sceSifSendCmd` cid 1, 0x20-byte packet (+ optional extra-data DMA) | handler `0x3C1578` registered by `sceSifAddCmdHandler(1, 0x3C1578, 0x50C900)` (`0x3c20b8–0x3c20cc`; handler table `0x50C880`, 16 entries) | `threadmain` 0x911C / 0x9188, `SNDIOP_dmcallback` 0x4A14 (`isceSifSendCmd`) |
| EE→IOP, per tick | EE `sceSifSetDma` (syscall 0x77 wrapper `0x424160`) of the **tag buffer** to the IOP address carried in the tick | sound thread `0x3C1B48`: descriptor at `0x50C800` = {src, **dst = `0x50C804`** (written by the tick handler), size, attr} | `SNDIOP_copytagbuf` (0x6F50) + `SNDIOP_processtagbuf` (0x6FD8) in `threadmain` |
| EE→IOP, on demand | EE `sceSifSetDma` of payload to an IOP staging buffer, then `sceSifSendCmd` cid 0 | `sub_003C43C0` (SetDma, `0x3c4400`/`0x3c4430`), `sub_003C4450` builds the cid-0 packet and sends it (`0x3c4588–0x3c45c0`) | `SNDIOP_cmdhandler` (0x8BA0, registered by `sceSifAddCmdHandler(0, 0x8BA0, …)` at 0x8FF8) → `SNDIOP_dmqueue` → `SNDIOP_dmtransfer` → **`sceSdVoiceTrans`** (IOP RAM → SPU RAM) |

### RPC fno 0 (init) payload, 20 bytes (`SNDIOP_dispatchrpc` 0x8C4C–0x8D60)

| Offset | Census value (AU1) | Meaning (IOP store) |
| --- | --- | --- |
| +0x00 | `0x00080303` | SND version 8.03.03; any other value prints the "APPLICATION LINKED WITH SND VERSION … BUT LOADED SNDDRV.IRX VER …" message and `break` |
| +0x04 | `0x0050B740` | EE address that receives the 0x240-byte IOP status block on every tick (stored at IOP `0x1172C` = `state+0x5C`) |
| +0x08 | `0x00000000` | EE address for type-3 data (IOP→EE `n×1 KiB`, `state+0x60`); 0 in SSX 3 |
| +0x0C u16 | `0x8CA0` = 36,000 | EE mixer rate |
| +0x0E u16 | `0x5DC0` = 24,000 | IOP mixer rate. (36,000 / 24,000) selects `SNDIOP_ee36_iop24[_spu48]` in `SNDIOP_mix` (0x6C2C–0x6C74) |
| +0x10..0x13 | `02 00 08 00` (AU2 spike log) | four config bytes stored to IOP state (0x8CD4–0x8D18) |

### IOP→EE cid-1 packet (0x20 bytes)

| Field | Tick (`threadmain` 0x9140–0x9188) | Data (0x90D0–0x911C) | Upload done (`SNDIOP_dmcallback` 0x49E4–0x4A14) |
| --- | --- | --- | --- |
| +0x0C (header `opt`) | IOP address of SNDDRV's tag-buffer receive area (`state+0xE0`) | – | the EE's callback id (from cid-0 `+0x14`) |
| +0x10 type | **0** | **3** | **2** |
| extra DMA | 0x240 bytes IOP status (serial at +0 and +0x23C) → EE `+0x04` address from init | `(a+b) << 10` bytes from IOP `0x13470` → EE `+0x08` address | none |
| EE handler action (`0x3C1578`) | store opt to `0x50C804`, `iSignalSema(36)` → sound thread runs | ignored (type ≥ 3) | `func_3C4918(opt)` |

### EE→IOP cid-0 packet (0x30 bytes, built at `0x3c4540–0x3c4584`)

| Field | Source on the EE | `SNDIOP_cmdhandler` use |
| --- | --- | --- |
| +0x10 | 1 | type (only 1 is handled) |
| +0x14 | request word 0 (`lw 0x0($s0)`) | callback id, echoed back in the type-2 packet |
| +0x18 | `*(0x50AD00+0xE8C)` | IOP source (staging buffer filled by the preceding `sceSifSetDma`) |
| +0x1C | request word 2 (`lw 0x8($s0)`) | SPU RAM destination |
| +0x20 u16 | request `+0xC` | size (rounded up to 64 by `dmqueue`) |
| +0x22 | request `+0xE` (byte) | priority (s16 in `dmqueue`) |

`SNDIOP_dmqueue` keeps 32 slots of 0x18 bytes; `SNDIOP_dmtransfer` runs the
highest-priority one as `sceSdVoiceTrans(1, dir, iop, spu, size)`, and
`SNDIOP_dmcallback` sends the type-2 packet when it completes.

### Tag buffer (EE→IOP each tick)

`SNDIOP_processtagbuf` walks tagged records; jump table at IOP `0xA410`:

| Tag | Handler | Meaning (from symbol) |
| --- | --- | --- |
| 0, 5 | 0x7048 | skip a 12-byte record |
| 1 | 0x705C → `SNDIOP_mix` | combine the IOP mixer slice (`MIX_audioslice`, 24 kHz) with the EE-mixed slice via `SNDIOP_ee36_iop24_spu48` → 48 kHz output |
| 2 | 0x7070 → `SNDIOP_maincpufx` | EE-side effects |
| 3 | 0x7084 → `SNDIOP_updatevoices` | IOP/SPU voice parameter updates |
| 4 | 0x70B8 → `SNDIOP_parsedts` | (DTS/timestamp record) |
| 6 | – | end of buffer |

### Output

`SNDIOP_dmathread` (0x8EA8) polls `sceSdBlockTransStatus`, refills with
`SNDIOP_loadautodma1/2` (AutoDMA PCM into the SPU2 core input), and calls
`SNDIOP_transfersputoiop` (0x8D8C) → `SNDIOP_dmqueue`. That suggests SPU
RAM also serves as sample storage that the IOP mixer reads back; this is an
inference from the names.

### Codec (disc bytes + EE decoder)

`SCHl` codec byte `0x0A` = EA-XA as decoded by the EE routine
`sub_003CCA08` (coefficient table at `0x44E890`: {0, .9375, 1.796875,
1.53125} / {0, 0, −.8125, −.859375}; 0xEE raw-frame marker; sample =
nibble << (12 − shift), high nibble first; 15-byte frames of 28 samples).
SCDl blocks: u32 samples, u32 per-channel offsets, then per channel 2 BE16
history samples + frames (6,096/6,096 frame headers valid at that
alignment over 40 `charsel.mus` blocks, ~50% at any other). `au2_eaxa.py`
decodes it; the first 8 s of `charsel.mus` give a spectrogram with a clear
beat and harmonics (`ref/charsel-ref-spec.png`). SNDDRV holds the same table
as int16 pairs (file offset `0xAD70`, vaddr `0xACC0`) for its own `SFILTER_unpackxa*`, so **both**
processors can decode XA.

## AU2-2. Part B: the spike and boot au2a

Fork worktree `~/dev/ssx3-work/AU2/PS2Recomp`, local branch `au2-snd` =
`ssx3` `eac6cba` + `7c2a02e` (not pushed). New header
`ps2xRuntime/include/ps2_snd_spike.h` plus hooks in `EeScheduler.cpp`
(vblank), `Stubs/SIF.cpp` (AddCmdHandler, SetDma), and `Syscalls/RPC.cpp`
(SendCmd, CallRpc); +38 lines outside the header. All of it is inert unless
`PS2X_SND_TICK` is set.

| Piece | What it does |
| --- | --- |
| Tick | Each vblank, `n = PS2X_SND_TICK` Interrupt-kind `GuestInvocation`s of the cid-1 handler recorded at `sceSifAddCmdHandler(1, …)` (a0 = packet at EE `0x01F31000`, a1 = handler data, gp = registration gp). Packet: type 0, opt = `0xB3C4` (SNDDRV's own tag-buffer address). Stamps the serial at status +0/+0x23C |
| cid 0 | Logs every packet. Type 1: dumps the staged payload and answers with a type-2 completion if `+0x14 ≠ 0` |
| SetDma | Descriptors whose caller `ra` is in the SND range `0x3B0000–0x3D0000` are logged and captured host-side (dumped, keyed by IOP address) instead of being copied into low EE RDRAM |
| `_sceSifSendCmd` | `0x426078` is bound to `ps2_syscalls::sceSifSendCmd` but takes `(cid, mode, pkt, size, src, dst, esize)` in a0..t2. While the spike is on, calls returning to `0x426220` (`isceSifSendCmd`) are reparsed. **This mis-binding is a real runtime bug**, latent today because nothing calls `isceSifSendCmd` without the spike |
| Env | `PS2X_SND_TICK`, `PS2X_SND_LOG` (≤60,000 lines), `PS2X_SND_DUMP_DIR` (≤256 MiB; tag buffers: first 40, then every 300th) |

Build: `~/dev/ssx3-work/AU2/build`, Release, codegen
`~/dev/ssx3-work/codegen-ssx3`, dependency sources reused read-only from
E50's `_deps` (`FETCHCONTENT_SOURCE_DIR_*`); runner sha256
`122e882da8c1f10ac9b57ac848c07c6b50339edbd297d3224baab1a4e73faa97`; suite
**597/597** from the worktree root. Game `.o` files deleted after linking
to stay under the 2 GB cap (a relink would recompile them).

Boot au2a: `local/research/AU2/au2_boot.sh au2a 540 1` (E51 route, 540 s,
slot 1, rc 0, own runner exited; `PS2X_CD_READ_TRACE` on).

| Observable (brief) | AU1 (no tick) | au2a (tick 1/vblank) | Receipt |
| --- | --- | --- | --- |
| Sema 36 signals | 0 (1 wait) | **9,228 signals / 9,229 waits**; sound thread `sched=9232` | `receipts/park-au2a.txt` |
| Counter `0x50A8E8+0x180` | not advancing | **0 → 0x2620** over 9,175 ticks | `receipts/snd-au2a-head.txt`, `…-ticks.txt` |
| `charsel.mus` reads | 13 reads / 97 sectors, all at vsync 335 | **301 reads / 2,373 sectors (4.6 MiB), vsync 334–3969** (whole menu stretch) | `big-reads-au2a.txt` |
| Race music | `fspoon.mus` + `fsloops0.mus`, stalls | `gdanse.mus` 139 reads / 965 sectors to vsync 9133, + `gdloops0.mus` (track differs per boot) | same |
| Tag buffers EE→IOP | none | **9,174**, 2,288 bytes each, one per tick | log |
| cid-0 packets (SPU uploads) | 0 | **0** | log |
| Other SND SetDma | 0 | **0** | log |
| Race reached | yes | yes (same route; the tick doesn't disturb it) | frames |

Every tag buffer has the same four records (`au2_tagbuf.py`): tag 0
{running byte count, 0x8F0, 0}; tag 3 `updatevoices`, 0x2A8 bytes (7
non-zero bytes: no SPU voices in use); **tag 1 `mix`: `{1, 0x600, 0, 0}` +
0x600 bytes = 384 interleaved stereo s16 frames**; tag 5 {tick serial}; tag
6 end. The mix payload is all zero before the music starts (v66–v105) and
non-zero, smooth s16 audio from v365 onward: consecutive samples change by
tens of units (e.g. −2755, −2788, −2713, −2696, …).

**Case: EE-mixed PCM.** The EE decodes the XA stream itself (the XA
routine's caller `0x3CCF90` appears in the boot log's call chains), mixes at
36 kHz, and hands the IOP 384 stereo frames of finished PCM per tick in the
tag buffer. The IOP's role in SSX 3 is only rate conversion (`ee36 → spu48`)
and AutoDMA output. No SPU-RAM uploads were requested in 540 s (menus +
race start), and the voice-update record stays essentially empty.

Tick rate: 384 frames at 36 kHz = 10.67 ms, so real hardware ticks at
36,000 / 384 = **93.75 Hz** (one 512-frame AutoDMA half-buffer at 48 kHz).
The spike ticks at 59.94 Hz, so the EE's sound clock ran at 0.64× real time.
The PCM content is unaffected; only the pace is.

Track identity from the sampled dumps (`ncc-au2a.txt`, `au2_ncc.c`): a
10.7 ms slice's best NCC against 400 s of the decoded `charsel` reference
reaches 0.93, but the same slices reach ~0.90 against `gdanse`, and their
best positions don't advance with time. A 384-frame window does not
discriminate, so these numbers are **not** evidence of which track plays.

## AU2-3. Boot au2b: a continuous capture of the EE mix (WAV)

The sampled dumps can't be played, so boot 2 used the same runner and env
with **lldb attached** (no rebuild): each `ps2_stubs::sceSifSetDma` entry
appended 0x620 bytes of EE RAM from `0x512E40` (tag-1 header, 384 frames,
tag-5 serial) to a file (`au2_lldb_capture.sh`). `au2_pcmcap.py` checks
the record layout and de-duplicates on the serial.

| Item | Value |
| --- | --- |
| Records | 13,963, all with the expected layout; serials 1..13,963, **no gaps** |
| Non-silent ticks | 13,663 |
| WAV | `~/dev/ssx3-work/AU2/run/au2b-ee-mix-36k.wav`, 36 kHz stereo s16, **148.9 s**, sha256 `2cd31f2c…f406` (not committed, 26 MB) |
| Music read during it | `charsel.mus` vsync 335–3970 (menus ≈ capture 3–42 s), then race `poorleno.mus` + `plloops0.mus` (MUSIC.BIG) vsync 4037–13751 (`big-reads-au2b.txt`) |
| Spectrogram | `receipts/au2b-spec-full.png`: silence, then a rhythmic section; a clean break at ~43 s where the reads switch to the race track; then tonal/sustained sections. `receipts/au2b-spec-20s.png`: a regular beat grid |

**Is it music?** Yes by structure: a regular beat, sections that change
exactly where the game switches tracks, and continuous non-silent 36 kHz
stereo audio. **Which track:** the beat-period fingerprint (`au2_tempo.py`,
`tempo-au2b.txt`) of the race section matches the `poorleno` reference
decode exactly and at the assumed 36 kHz rate:

| Signal | Top 4 onset-autocorrelation lags |
| --- | --- |
| Capture 45–75 s (race) | 1.94, 0.47, 0.48, 1.46 s |
| `poorleno.mus` reference 0–30 s | 1.94, 0.47, 1.46, 0.48 s |
| `charsel.mus` reference 0–30 s (control) | 0.47, 1.26, 1.27, 0.79 s |
| Capture 5–35 s (menu) | 1.92, 0.96, 0.64, 0.48 s (a ~0.48 s beat; `charsel` ref's top lag is 0.47 s, but this is not distinctive) |

Waveform correlation does **not** match (`ncc2-au2b.txt`: 0.5 s and 2 s
windows reach only 0.1–0.33 against the full `charsel`/`poorleno`
decodes, no better than chance, at 24/32/36/40.5/48 kHz alike). Likely
reasons, not verified: the EE mixes several MPF stems at once (the race
also streamed `plloops0.mus`) plus SFX/crowd and its own filters, so no
single stem lines up. A second possibility is a remaining error in my
reference decoder that keeps the envelope but not the waveform.
**Listening to the WAV is the quick check** (orchestrator or Brad).

## AU2-4. Incident: boot au2b ran outside the lease for ~10.5 min

With lldb attached, the E46/E31 harness's child check reported the
runner as exited after 1.012 s (`receipts/wrap-au2b.log`: `"bound":
"exit"`). It then **released slot 2 and stopped enforcing the 300 s wall**,
while the runner kept running under lldb. I found it at 20:09 EDT and killed
it by PID (21281; SIGTERM ignored, SIGKILL). It ran from 23:59:38Z to about
00:10:10Z, **~10.5 min without a lease and over the 600 s boot cap**, next to
other lanes' leased boots (slot 2 was then claimed by `e53b`). No files
outside `~/dev/ssx3-work/AU2` were touched. Any other lane's speed numbers
from that window are suspect. Fix for next time: launch the runner *under*
lldb from the harness, or have the harness watch the PID instead of
`waitpid` status, and don't attach a debugger to a harness child again.

## AU2-5. Answer and next-brief shape (recommendation; orchestrator decides)

**Case: EE-mixed PCM.** SSX 3's EA SND library decodes and mixes all audio
on the EE (36 kHz stereo) and gives the IOP 384 finished frames per tick in
tag-1 of the tag buffer. It made no SPU uploads (cid 0) and no voice work
(tag 3 empty) through menus and race start. The IOP only resamples
36→48 kHz and feeds the SPU2 AutoDMA. **So route (a)-lite is enough for
audible music, with no XA decoder, SPU2 or IOP emulation on our side.**

Proposed **AU3** (one worker, 1 build, ≤2 boots, Mac only):

1. Make the spike a real HLE, still env-gated at first. Tick from the
   **host audio clock**: one cid-1 type-0 tick per 384 frames consumed at
   36 kHz (93.75 Hz), not per vblank. Take tag-1 PCM straight into a raylib
   `AudioStream` ring (36 kHz stereo s16, or resample to 48k host-side). Keep
   the status stamp and type-2 answers. The tick must be queued on the EE
   executor thread, so the audio callback only counts demand and the
   scheduler delivers ticks at its next checkpoint.
2. Fix the `_sceSifSendCmd` (0x426078) argument binding for real. It is
   independent of audio and latent today.
3. Validation: a WAV tap of what reaches the host stream + Brad listens on
   the Mac at Select Character (M-A1). Underrun count per minute; guest
   speed with and without sound (the sound thread now runs ~94×/s).
4. Then Odin/iPhone: same path. Where the guest runs below real time, the
   audio underruns rather than slowing down; report underruns as a speed
   symptom, not a sound bug.

Not needed for M-A1: SNDDRV emulation, SPU2, XA decoding. Watch later for
tag-3 voice updates or cid-0 uploads (SFX banks may use them in other
modes); the spike logs both.

## AU2-6. Budget, pins, receipts, gaps

| Item | Value |
| --- | --- |
| Builds | 1 (`~/dev/ssx3-work/AU2/build`; a reconfigure + test link to add the analyzer lib for the suite) |
| Boots | 2: au2a 540 s (slot 1, leased); au2b 300 s requested, **~630 s actual, ~10.5 min unleased** (AU2-4) |
| Time | ~2 h 45 min |
| Disk | `~/dev/ssx3-work/AU2` 1.2 GB (build 0.8 GB, run, worktree); references deleted; internal 82.5 of 200 GB |
| Fork | local `au2-snd` `7c2a02e` on `ssx3` `eac6cba`, not pushed; runner-dir diff vs `14b1e5cb` empty |
| Runner | sha256 `122e882d…faa97`; suite 597/597 |
| Commands | `au2_boot.sh au2a 540 1`; `au2_lldb_capture.sh au2b 300`; `au2_tagbuf.py`, `au2_pcmcap.py`, `au2_eaxa.py decode …`, `au2_ncc.c`, `au2_ncc2.c`, `au2_tempo.py`, `au2_classify.py` (unused: no non-tag payloads were captured) |
| Receipts | `receipts/` (park, SND log head + tick lines, CD reads, two tag-buffer dumps, spectrograms, wrap logs, lldb log tail, sha256 of raw files); `ncc-au2a.txt`, `ncc2-au2b.txt`, `tempo-au2b.txt`, `big-reads-au2a.txt`, `big-reads-au2b.txt`, `snddrv-disasm.txt` |

Gaps:
- G1. The capture has not been listened to. Track identity rests on
  tempo, not waveform (AU2-3).
- G2. Spike tick = per vblank (59.94 Hz) vs the real ~93.75 Hz. Whether the
  EE's buffering behaves at the right rate is untested.
- G3. The status block content beyond the serial is unknown (all else left
  as the EE initialized it); the EE didn't seem to need it.
- G4. SFX: no uploads or voice records appeared, but the route never
  pressed buttons in the race much. Whether SFX are also EE-mixed is
  likely (same tag-1 path) but untested.
- G5. The race track differs per boot (`fspoon` in AU1, `gdanse` in au2a,
  `poorleno` in au2b): an EA Radio shuffle.
- G6. The upstream `_sceSifSendCmd` mis-binding is only fixed under the
  spike flag.
