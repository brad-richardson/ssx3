# T49 REPORT — PCSX2 entry trace of the same VU1 programs (healthy side of the E37 diff)

Brief: `local/muse/prompts/T49.md` + orchestrator addendum (vi-entry lines;
trace start_pc 0x257 if it runs in the same vsync before 0x8/0x2). Tables +
receipts; the orchestrator decides. Read first: `AGENTS.md`,
`local/research/T48/REPORT.md`, `local/research/E36/REPORT.md`,
`local/muse/prompts/E37.md`.

## T49-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | One bounded log-only patch on T48's clone, gated like T48 (interp only) | DONE — 6 files, 16 hunks, `t49-patch.diff` proven exact (§T49-3) |
| 2 | First MSCAL at PCSX2 start_pc 0x8 + 0x2 at/after dump vsync: vumem + vif + pairs to 4th arrival @0x418, E37 formats, byte PCs | DONE — both traced, neither ever reaches 0x418 (§T49-5) |
| 3 | Addendum: `vi-entry` (vi00–vi15) at each traced MSCAL | DONE — 3/3 lines |
| 4 | Addendum: trace 0x257 (byte 0x12B8) + `vi-exit` at its E-bit | DONE — 80 pairs to E-bit, vi-exit present; same-vsync-before-0x8 holds in vsync 18714 (§T49-5) |
| 5 | Preservation as T48 did (replay leg + live-frames leg) | DONE — replay 7/7 exact; live mean 0.92 < 2.0 (§T49-4) |
| 6 | Trace text to `~/dev/ssx3-work/T49/` + share mirror + repo if < 5 MB | DONE — 924 KB + 344 KB in all three places |

Headline for the E-brief: healthy entry VIs are small and stable
(vi13=0x03e4 in all three traces; vi03=0x00ca/0x03a2/0x02dd) vs the recomp's
wild inherited values (E37: vi13=0xd549, vi03=0xC224, never written by setup).
The healthy 0x40 program opens with an unconditional `B` to 0x7d8 (2 pairs);
the healthy 0x10 program opens with `B` to 0x258. Neither visits 0x418.

## T49-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T48-end (G-series + T48) + T49 below |
| Pre-T49 file SHAs (T48-end, from `t49-apply.sh`) | VU1micro `426572ef…064`, VU1microInterp `c6887611…190`, VUops `66231594…f82`, Vif_Transfer `d34a0f29…afb`, Vif_Codes `659e9572…83c` |
| Post-T49 qt | `c3ad0af05bff6d4048f4aaf4c1181c4a59e3471f8f5520aaf0cf9fae002f8713`, 131,004,800 B |
| Post-T49 gsrunner | `cf08aab3bea6428f7f1f100ed04f13919ba4800fefaa74335a5061b509a5cb9c`, 90,510,120 B |
| Game inputs / dat | T48's verbatim (`dat-t48`, vuThread=false, EnableVU1=false); ISO `SSX 3 (USA).iso` |
| Capture | run 2 (deliverable): `T48_DUMP_QUEUED vsync=18712`, winstart=18713, dump over 18713–18720; F8 `t49-shot-t49a-sc.png` (settled SC, Zoe rendered, viewed §T49-6) |
| Trace | `t49-trace.txt` sha256 `1bfdbd05…863af7` (923,811 B); `t49-trace-vu1.txt` sha256 `f609807a…43d6ee` (343,854 B; 5,499 T48_VU1 records, same population as T48-A) |
| Patch | `t49-patch.diff` sha256 `8e3b799b…45c92a24` (526 lines, 6 files); applier `t49-hook.py` sha256 `79a869e3…4d3b8` |

Superseded (do not use): first-build binaries (qt `01e1a89f…`, gsrunner
`3ea4de79…`) whose VIF ring had an off-by-one (write index `(seq-1)&4095`
vs read index `seq&4095`); every entry failed its seq check, so run 1
printed zero `vif` lines. Fixed, rebuilt, recaptured as run 2.

## T49-2. The patch (16 hunks, 6 files; `t49-patch.diff` as text)

Hook sites (T49 hunks only; T48 hunks untouched):

| Hunk | File:anchor | What |
| --- | --- | --- |
| T49-GS1/GS2 | `GS/GS.cpp`: T48 atomics + `t48_winstart = … + 1` | `g_t49_winstart` atomic mirror of the dump-window start; BEGIN gate needs it on the EE side (trace only at/after the dump vsync, inside the T48 window) |
| T49-V1a | `VU1micro.cpp`: T48 externs | T49 globals: arm/once flags (0x8/0x2/0x257), pair state, VI/VF/mem snapshots, 16-deep GET_VU_MEM touch buffer, 4096-entry VIF ring (code/cl/wl/mask/tops/itops + ≤8 payload words + seq) |
| T49-V1b | `VU1micro.cpp`: before `SetStartPC` | BEGIN gate (arm file + T48 window + vsync ≥ winstart + once-flag); prints `T49_BEGIN`, `vi-entry`, 1024 `vumem` lines, ring `vif` lines since last dump, arms pair tracing (0x257 runs to E-bit, 0x8/0x2 to 4th arrival @0x418); preempt-close + exit-disarm on any newer MSCAL |
| T49-VI0/VI1 | `VU1microInterp.cpp`: T48 externs + `VUmicro.h` | externs + compact pair disassembler (lower + upper-direct names mirror the VUops tables; upper FD groups/unknowns fall back to `UFDt.fd`/`Uxx`/`LOxx` — best-effort context, up/lo hex authoritative) |
| T49-VI2 | `VU1microInterp.cpp`: `_vu1Exec` top | prologue: fetch PC (byte addr), arrival counting @0x418 (skipped for 0x257), 20k-pair cap, VI/VF/16KB-mem snapshots |
| T49-VI3 | `VU1microInterp.cpp`: function tail | epilogue: `pair` line (vi/vf deltas, deduped touch rows as `rd` pre-state / `wr` post-state by opcode kind, capped 8+8), plus deferred `T49_END reason=ebit` |
| T49-VI4 | `VU1microInterp.cpp`: T48 E-bit close | `vi-exit` (all 16 VI) when the traced 0x257 program reaches its E-bit; arms the deferred END so the E-bit pair line prints first |
| T49-VO1/VO2 | `VUops.cpp`: T48 counter + `GET_VU_MEM` | row tap `((addr & 0x3fff) >> 4)` into the touch buffer when pair tracing (XGKICK's direct-mem reads don't pass through here — stated gap) |
| T49-VT1/VT2 | `Vif_Transfer.cpp`: includes + new-VifCode | record every VIF1 command (code + ≤8 payload words + cl/wl/mask/tops/itops + seq) |
| T49-VC2/3/4 | `Vif_Codes.cpp`: MSCAL/MSCALF/MSCNT pass1 | packet-boundary marks (ring position at each VIF1 MSCAL-family command) |

Gating (all must hold for a BEGIN): `/tmp/t49-arm` seen + `g_t48_window`
+ `g_t48_vsync ≥ g_t49_winstart (≥ 0)` + first qualifying MSCAL per
startPC. Default-off cost: one file-probe per MSCAL until armed, a few
branches + unconditional VIF-ring stores otherwise (proven neutral §T49-4).

Line-format notes (all E37 field orders kept; T49-only tail after `wl=` on
`vif` lines is `code=<hex> flg=<0/1> tops=<n>`):
- `fmt` prints `VVN_VL` (double V, e.g. `VV4_32`) — script typo, normalize
  one leading V when diffing against E37.
- `addr` on `STCYCL` lines is the raw immediate field (CL/WL live in
  `cl=`/`wl=`); the STCYCL's own line shows pre-update cl/wl.
- `addr` on FLG UNPACKs is the effective row `(raw + tops) & 0x3ff`
  (verified: 553→553/560/561/562 and 553+180=733 in the 0x8 packet).
- `vi 26` deltas are taken-branch receipts (VI26 = TPC).
- `rd` = pre-state row contents, `wr` = post-state; store/load classified
  by opcode kind (LQ/ILW/LQI/LQD/ILWR vs SQ/ISW/SQI/SQD/ISWR).
- `vif` spans print everything since the last *traced* MSCAL (a superset
  when several VIF packets intervene); the feeding packet is the tail after
  the last `^vif MSCAL/MSCALF/MSCNT` line (sliced §T49-5; 0x8's 39-line span
  needs no slicing).

## T49-3. Patch proof (exactness, not just review)

`t49-patch.diff` was generated as worktree-minus-baseline where the baseline
is worktree copies stripped by `t49-unhook.py` (exact inverse of the applier,
16/16 removals count==1 — itself proof the tree holds exactly the scripted
hunks). Applying the diff to the baseline reproduces all 6 worktree files
byte-identically (`cmp`, 6/6). Two reconstruction notes: (1) the tree also
carries G-series hunks outside T48's patch file (found via a GSState/R5900
mismatch during reconstruction — the T49 diff is vs the G+T48 tree, which is
what the report pins); (2) `t48-hook-vu.py` reproduces the pre-fix2 broken
linkage (`static` cross-TU globals) — T48 restoration used the committed
`t48-patch.diff` instead. `/tmp` on bytesize does not persist across ssh
sessions (per-connection); all multi-step state lives under `~/pcsx2-g7/`.

## T49-4. Behavior preservation (two legs, as T48)

Leg 1 — deterministic replay (patched gsrunner `cf08aab3…` on the G13 rich
dump, T48's `t48-replay.sh` verbatim): **7/7 PNG md5s match the T48 §T48-1
pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`)
**and HWSTAT matches exactly** (791 draws / 37 passes / 0 barriers /
14 copies / 320 uploads / 6 readbacks).

Leg 2 — live frames (patched run-2 F8 `t49-shot-t49a-sc.png` sha256
`50ab10dc…5f9efab` vs stashed unpatched proof F8 sha256 `6d3fa8bd…32023`,
same settled SC, native 640×480, whole-frame cropdiff): **mean = 0.92,
p99 = 28** — identical up to animation phase (T48's gate is mean < 2.0).
Patched vs T47 SC ref: mean = 0.44, p99 = 16.

## T49-5. The trace (run 2; run 1 superseded — zero `vif` lines, §T49-1)

Per-program summary (`t49-analyze.py`; `end=` = T49_END reason/pairs):

| startPC (byte) | vsync | vumem | vif span / feeding pkt | pairs | arrivals @0x418 | end |
| --- | --- | --- | --- | --- | --- | --- |
| 0x257 (0x12B8) | 18713 (= winstart) | 1024 | 4095 (truncated, dropped=121888878) / 265 | 80 | 0 | ebit |
| 0x2 (0x10) | 18714 | 1024 | 3783 / 39 | 62 | 0 | preempted (next MSCAL; T48_VU1 shows these programs end=ebit, 36–100 cycles, 0 aborts) |
| 0x8 (0x40) | 18714 | 1024 | 39 / 39 (complete packet) | 6 | 0 | preempted (T48_VU1: end=ebit, 6 cycles, 1 xgkick) |

Feeding-packet shapes: 0x8 = NOP 22 / STCYCL 5 / UNPACK 5 (V4_32 num=7 @553,
V4_16 num=57 @560, V3_16 num=57 @561, V3_32 num=57 @562, V2_32 num=1 @733) /
STROW+STMASK 3 / FLUSH 1, tops=553. 0x2's tail packet is the same shape
(39 lines, tops=192; head UNPACK V4_32 `00008004 302e4000 00000412`).
0x257's tail packet is larger (265 lines, incl. 16 MPG + STMOD/BASE/OFFSET,
tops 192/38). The 0x8 header qwords (`00008039 302e4000 00000412 …`)
match E36's TOP-header reading for startPC 0x40 exactly.

vi-entry (all three; full lines in trace):

| reg | 0x8 | 0x2 | 0x257 |
| --- | --- | --- | --- |
| vi00–vi02 | 0000 / 017c / 017c | 0000 / 0021 / 0081 | 0000 / 7fff / 0350 |
| vi03 | 00ca | 03a2 | 02dd |
| vi11 / vi13 / vi14 / vi15 | 8004 / 03e4 / 02c1 / 0004 | same | same |

vi13/vi11/vi14 are byte-identical across all three traces (two vsyncs).
vi-exit (0x257 only, pairs=79): vi01 7fff→0000, vi03 02dd→0101, rest
unchanged (vi13 stays 03e4).

First vi03/vi13 writes (operands + values; up/lo hex authoritative, names
best-effort — lower 0x08 and upper UFD3.0b are unnamed in PCSX2's tables):

| startPC | vi03 first-write | vi13 first-write |
| --- | --- | --- |
| 0x257 | pc=0x12c0, up=000002ff, lo=100338db (lower op 0x08, Fd 0x03), 02dd→0101 | never in 80 pairs (03e4 throughout) |
| 0x2 | pc=0x270, up=000002ff, lo=09030fff = ILW IT=3 IS=1 imm=-1, 03a2→0006 from integer row 373 (`00000006 00000000 00000000 00000000`); check: vi01 was 0176 by then, 0176−1 = 373 ✓ | never in 62 pairs |
| 0x8 | never in 6 pairs | never in 6 pairs |

First pairs (code-upload check for E37): 0x40: `up=000002ff lo=400000f2`
(B→0x7d8; delay slot 0x48 writes vi26 0050→07d8 = branch landing); then
0x7d8/0x7e0/0x7e8/0x7f0 epilogue. 0x10: `up=000002ff lo=40000048`
(B→0x258; vi26 0020→0258), then setup (ESQRT, ILW vi05←row 193, ILW
vi03←row 373, LQ vf01←row 372, IADDs…). 0x12b8 opens with ESQRT (no
branch): LQ vf17←row 42, vf16←row 45, real VF arithmetic (SUB.xyzw), …
80 pairs to E-bit.

Ordering receipt (addendum condition): in vsync 18714 (the 0x8/0x2 vsync),
T48_VU1 order is […, 0x257 @ pos 84, …, first 0x8 @ pos 158, …] of 613
programs — a 0x257 runs in the same vsync before 0x8. The traced 0x257 is
the first-qualifying one at winstart (18713); vi13=03e4 is identical in all
three traces across both vsyncs.

## T49-6. Frames

`t49-shot-t49a-sc.png` (201,238 B, sha256 `50ab10dc…5f9efab`, 640×480
native): settled Select Character, Zoe 3D model rendered, stat bars, rider
silhouettes — viewed by eye, same settle point as T48-A.

## T49-7. Gaps, overruns, and harness lessons

1. **Build budget overrun (3 invocations vs ≤2, 1 clean).** (a) My first
   applier duplicated anchor lines (`apply_after` adds repeating the
   anchor; worst case an extra `}` closed `_vu1Exec` early) — caught by
   compiler, fixed, audit-harnessed (11/11 anchor≠add checks in-repo).
   (b) T48 restoration via `t48-hook-vu.py` reproduces the pre-fix2
   `static` linkage failure — restored from the committed `t48-patch.diff`
   instead. (c) VIF ring off-by-one (all entries seq-skipped) — found via
   zero `vif` lines + `nm`, fixed; cost one rebuild + recapture.
2. **Capture budget met (2/2):** run 1 (VIF-broken binary) superseded by
   run 2; no proof boot needed (Leg 2 via cross-run F8 compare, §T49-4).
3. **Time box overrun (~5 h vs 3 h):** two resets + rebuilds + recapture.
4. Bytesize bytes: new T49 residue ≈ 3 MB (scripts, traces, verify dirs) +
   run-2 emulog 1.1 GB + dump `.gs` (~11 MB, snaps dir) — under the 5 GB
   cap. No mini boots (no P-lane lease); bytesize idle at each heavy step.
5. `disasm` names are best-effort (upper-FD/lower-0x08 fallbacks); up/lo
   hex + register/memory deltas are authoritative. `fmt` has the `VV`
   typo; STCYCL `addr` is the raw immediate; STCYCL's own line shows
   pre-update cl/wl. XGKICK rows aren't tapped (direct-mem path).
6. 0x257's span is ring-truncated (head lost; feeding-packet tail kept);
   0x2's span is a multi-packet superset (feeding packet = 39-line tail).
7. `t49-capA.sh` kept T48's route verbatim (only TAG/poll/arm-file names
   + dual `/tmp/t48-arm /tmp/t49-arm` arming changed).

## T49-8. Exact commands

On bytesize (each line one ssh call, single-quote pattern; `$`-bearing
one-liners do not survive the quoting layers — ship scripts by stdin
redirect instead; `/tmp` is per-connection, keep state under `~/pcsx2-g7/`):
`python3 ~/pcsx2-g7/t49-hook.py` (asserts count==1) → `bash
~/pcsx2-g7/t49-build.sh` (`cmake --build …/build --target pcsx2-qt
pcsx2-gsrunner -j2`) → `bash ~/pcsx2-g7/t48-replay.sh` (Leg 1) → `bash
~/pcsx2-g7/t49-capA.sh` (capture; `UNPATCHED=1` reserved for proof, unused)
→ `bash ~/pcsx2-g7/t49-extract.sh <emulog> <trace>` → `python3
~/pcsx2-g7/t49-analyze.py <trace> <vu1>`. Retrieval: WSL→`/mnt/c/Users/
bradr/pcsx2-t4/` → `scp bytesize:pcsx2-t4/<f>` (plain `scp bytesize:…`
lands on Windows, not WSL). Analysis/verify locally as in §T49-5/3.

## T49-9. Receipt paths + recommendation

- Repo (this commit): `local/research/T49/` — REPORT.md, `t49-patch.diff`
  (proven exact), `t49-hook.py`, `t49-unhook.py`, `t49-{apply,build,capA,
  extract,analyze}.sh|py`, `t49-trace.txt` + `t49-trace-vu1.txt` +
  `t49-shot-t49a-sc.png` + `t49a-poll.log`.
- Workdir `~/dev/ssx3-work/T49/` holds the same four receipts (SHAs match
  across workdir/repo/share/bytesize).
- Share mirror `/Volumes/share/ssx3/ps2x-t49/`: trace + vu1 + shot +
  REPORT.md (copied after writing, before commit).
- Bytesize residue (all under cap): `t49-hook.py`, `t49-unhook.py`,
  `t49-{apply,build,capA,extract,analyze}`, `t49-trace{,-vu1}.txt`,
  `t49-patch.diff`, `t49-patch2.diff`, `t48end/`, `t49base/`,
  `t49verify{,2}/`, `dat-t48` emulogs (`emulog.txt` run 2 + `emulog-pre-*`
  run 1), run-2 dump `.gs` in snaps, `t49-frames` absent (no replay frames
  kept; md5s/HWSTAT in §T49-4 from the log).

Recommended next action (orchestrator): diff these three traces
pair-by-pair against E37's recomp traces at the same byte PCs — start with
the first-pair code words (upload check) and the vi-entry table. No
follow-up T-lane work is queued by this brief.

