# N8D7M7 — selected-VRAM divergence boundary (PARTIAL source-grounded design)

**State: PARTIAL design (orchestrator gate correction 2026-09-24). The §2
command-order table is preserved. S2late is labeled an intervention, O is
unresolved, D is impossible under identical bytes/decoder. No source edit,
build, replay, boot, Odin/iOS action, lease, push, or status/todo/ledger
edit. No shader/Turnip/driver root cause is claimed; no device brief is cut
from this worker; the orchestrator decides the gate.**

Brief: `local/muse/prompts/N8D7M7.md`. Observation to explain: N8D7M6
captured one complete Odin tick2050 GS stream (SHA `f6a78f71…a593`) and
replayed those exact bytes on Mac paraLLEl. All 11 selected-image descriptor
fields match; Mac input/oracle 300 active of 448, Odin input/oracle 23;
viewed race frame broad on Mac, mostly black on Odin. The loss is at or
before the selected-VRAM staging snapshot on this same stream. N8D7M3/M4
draw counts, pending flags, isolated words and the later tick2052 frame do
not separate writes from copy timing and are not revived below except as
explicitly rejected OTHER rows.

LSP hover returned "No LSP server available for this file type"; every code
link below rests on direct source reads at the pinned revs (same basis as
N8D7M3 §7 / N8D7M4 §7).

## 1. Pins read in this part

| Item | Pin |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, HEAD `a8cfefad109134767b0810b7707b4b58a5dfcca7` (`[N8D7M5]`, base `d1ba1d4`) |
| Parallel-GS worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== N8D7F REPORT §12 pinned G43 copy HEAD) |
| Reference stream | N8D7M6 `n8d7m6.gs`, SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` (Mac 300 / Odin 23, descriptor equal) |
| Prior provenance | N8D7M5 CPU executed-word tap (fork `a8cfefa`; packet/write presence only, never Odin GPU word values — REPORT §6) |
| Repo HEAD (receipts only) | `c44d581b` |

## 2. Renderer command sequence, GIF acceptance → mapped staging

Order is top-to-bottom (record order == GPU execution order within and
across submits). Owner = which memory holder / thread; clock = whose tick
or fence witnesses execution.

| # | Stage | Code site (pinned rev) | Owner / clock |
| --- | --- | --- | --- |
| 1 | EE submits GIF packet | `GS::processGIFPacket`, fork `gs_frontend.cpp:929-956` | EE thread owns packet bytes; clock = EE `vsyncTick` (`m_privRegs->vsyncTick`, read at `:948`) |
| 2 | Queue-or-direct split | same file `:931-940` (enqueue `GifPacket` iff `m_worker && !t_inGsWorker`, else synchronous body `:942-1048`) | On the live device a GS worker exists, so packets queue; on Mac CPU-direct replay they execute synchronously (N8D7M5 REPORT §1) |
| 3 | Packet recorded as GPU draw state | `RawGifPacket`, backend `ps2_gs_parallel_backend.cpp:897-905` → `m_iface->gif_transfer(path,…:901)`; `GSInterface::gif_transfer`, G43 `gs_interface.cpp:5191+` decodes GIF tags into draw state | Presenting/GS-worker thread owns `m_iface` record state; **no GPU execution yet** — draws accumulate until flush |
| 4 | Present request built | `GS::buildPresentationRequestUnlocked`, fork `gs_frontend.cpp:757-769` (`vsyncTick` acquired at `:769`); consumed under `m_backendLifetimeMutex` with `Flush()+Sync()+Present` at `:804-812` | Tick owned by priv regs (EE vblank clock); request snapshot owned by presenting thread |
| 5 | Selected-request gate + phase | backend `:441-447` (`selectedRequested` iff `request.vsyncTick==2050` and `PS2X_N8D7F_SELECTED_CAPTURE=1`; `vsync.phase = tick&1` at `:447`) | Tick owned by priv regs; phase bit owned by backend Present |
| 6 | Prior draws flushed first | backend `:452` `m_iface->flush()` → `GSInterface::flush`, G43 `gs_interface.cpp:5153-5165` (`flush_pending_transfer` + `renderer.flush_submit(value)` with fresh timeline value) | GPU executes previously flushed draws first in submission (timeline) order |
| 7 | Scanout cmd built | `GSInterface::vsync`, G43 `gs_interface.cpp:5527-5578` → `renderer.vsync(…)` at `:5576-5578`, recorded into `direct_cmd` | Same presenting thread; record order below is GPU order |
| 8 | Selected descriptor latched | G43 `gs_renderer.cpp:4779-4792` (FBP/FBW/PSM/DBX/DBY from `priv.dispfb1`; phase/stride from `compute_circuit_rect` at `:4776`; mask/samples/promoted `:4786-4788`; extents `:4789-4792`) | DISPFB1 + DISPLAY1/SMODE own the fields (EE register clock) |
| 9 | **S1: early raw copy** (existing) | `gs_renderer.cpp:4806-4820`: 4 MiB `selected_vram_staging` alloc (`:4806-4810`); barrier COMPUTE\|TRANSFER → TRANSFER_READ (`:4813-4815`); `copy_buffer(staging←buffers.gpu, 4 MiB)` (`:4816-4817`); barrier TRANSFER_READ → FRAGMENT_READ (`:4818-4819`). Guarded by `:4793-4804` (supported PSM, 512×224, 4 MiB, coords < 2048) | GPU owns `buffers.gpu` (all prior flushed draws) and staging; executes at submit time, not record time |
| 10 | GPU-shader source read (existing) | `sample_crtc_circuit`, `gs_renderer.cpp:4262-4318`: binds `buffers.gpu` (`:4282`), pushes FBP/FBW/DBX/DBY/phase/stride (`:4307-4313`), draws (`:4316`); invoked for circuit1 at `:4834` (after S1) | GPU-side consumer of the same `buffers.gpu` bytes through the shader path, independent of the `copy_buffer` path |
| 11 | Circuit1 readback + status (existing) | `gs_renderer.cpp:5054-5077` (circuit1 → `circuit1_staging` 512×224×4; `selected_capture_status=2` at `:5076`); raw-circuit early return at `:4990-5031` leaves status 1 (OTHER) | GPU owns circuit image; status 2 = ordered completion of the whole scanout cmd up to this point |
| 12 | End of scanout submit | `flush_submit(0)` at `gs_renderer.cpp:5354`; `GSRenderer::flush_submit` at `:1116+` submits `direct_cmd` | GPU submission order: S1 copy → circuit sample → circuit copy → merged render |
| 13 | **Ordered completion point** (existing) | backend `:601-602` (`m_device->submit(cmd)`; `m_device->wait_idle()`) | Host observes only after GPU idle: every byte mapped later is post-completion by construction |
| 14 | Host map + decode (existing) | backend `:621-626` (map `selected_vram_staging`, `circuit1_staging`, stage counts); `selectedDecode` `:100-156` + `selectedTileCounts`; oracle `oracleDecodeCensus` `:190-222` on the same mapped bytes; SHAs + 448-vectors + `input_circuit_equal`/`circuit_stage_equal` at `:647-663`; oracle controls + `oracle_input_equal` at `:712-729` | Host owns mapped snapshot; clock = post-`wait_idle` |
| 15 | O-window (hypothesis, not fact) | `RawGifPacket` (`:897-905`) takes no `m_backendLifetimeMutex`, while Present's `Flush/Sync/Present` runs under it (`gs_frontend.cpp:804-812`): EE-recorded draws flushed **after** step 6 execute **after** the S1 cmd | If tick≤2050 draws are recorded after step 6, they land after S1 in GPU order — the exact O mechanism; named as hypothesis with line refs, not observed |

## 3. Candidate tap sites (bounded, default-OFF, same tick2050 Present)

`S1` = existing early copy (§2 row 9). `G` = existing circuit1 shader
sample + staging (§2 rows 10–11, decoded as the existing 448 `circuit`
vector). Two candidate additions were considered inside the same tick2050
Present call; only one survives as nonperturbing:

- **S2same**: second 4 MiB `copy_buffer(buffers.gpu → staging2)` recorded in
  the same `direct_cmd`, placed immediately before `flush_submit(0)`
  (`gs_renderer.cpp:5354` site), same barrier pair as S1, mapped after the
  existing `wait_idle` (`:601-602`). Same-submit, no extra submit/wait:
  observational.
- **S2late (INTERVENTION, rejected as discriminator)**: after the existing
  `wait_idle` returns it would call an extra `m_iface->flush()` plus a fresh
  `submit` + `wait_idle` + `map`. That extra flush submits draw work that
  the original Present never executed, so it changes what executes in this
  Present: a broad S2late is equally consistent with O (late-but-due
  tick≤2050 writes) and with delayed/missing work that only the extra
  submit flushed. `post_tick==2050` proves the EE clock had not advanced,
  not that the newly flushed writes were already due before the S1 copy.
  S2late therefore cannot uniquely establish O and is labeled an
  intervention; O stays unresolved (§4).

Bytes: +4 MiB staging (S2same) + ~3 KiB text (one extra 448-vector log +
SHA) on top of the existing 5,177,344 B probe budget (N8D7F REPORT §21);
S2late's further +4 MiB is not proposed for any gate. Sync required: none
beyond the existing `:601-602` for S2same. Default-OFF behind the existing
`PS2X_N8D7F_SELECTED_CAPTURE=1` gate; unset/empty = zero behavior change.
Every census below is the **full 448-tile census** (RGB max ≥ 32,
active = count ≥ 32) decoded with the identical `selectedDecode` +
`oracleDecodeCensus` from each staging; thresholds per N8D7M6:
sparse ≤ 100/448, broad ≥ 250/448, else OTHER.

| Tap | Command / fence order | Bytes | Sync | Observational or intervention? | Separates which W/O/C/D pairs? |
| --- | --- | --- | --- | --- | --- |
| T1 S1 early copy (existing, baseline) | §2 row 9 → `:601-602` → map `:621-626` | 4 MiB (exists) | existing wait | Observational | Anchors all rows; alone separates nothing new → OTHER by itself |
| T2 G circuit shader sample (existing) | §2 rows 10–11, same cmd after S1 | 512×224×4 (exists) | existing wait | Observational (independent read path of same source) | {W} (G sparse) vs {C} (G broad, copies sparse) |
| T3 S2same late-in-cmd copy (proposed) | same `direct_cmd`, pre-`:5354` → same `:601-602` → map | +4 MiB | none new | Observational (same-submit; no reorder) | hardens {C} (two sparse copies + broad G = copy path, not one bad copy); T3 broad/S1 sparse → informative OTHER (unpredicted in-cmd write) |
| T4 S2late post-wait copy (**intervention, rejected**) | extra flush → fresh cmd copy → extra submit/wait/map | +4 MiB (not proposed) | extra submit/wait | **Intervention**: the extra flush executes draw work the original Present never ran; broad S2late fits O and delayed/missing work equally; `post_tick` cannot restore attribution → OTHER | none (rejected; O unresolved) |
| T5 4 MiB SHA + oracle/input agreement (existing) | map `:621-626`, SHAs `:647-651`, `oracle_input_equal` `:725-729` | text only | none | Observational | consistency check only: identical bytes through the identical decoder must give identical census (§4 D-impossibility); no category separation → OTHER |
| X1 split-submit between S1 and S2 (rejected) | submit S1 early, wait, then submit rest | — | extra wait mid-order | **Intervention**: changes execution order; can prove nothing about the original order → OTHER | none (rejected) |
| X2 draw counts / pending flags / isolated words (rejected) | frontend ring / Present-entry flag / 8 words | — | none | Nondiscriminating per N8D7M3/M4 gates; no execution witness → OTHER | none (rejected, per brief) |
| X3 second-tick (2052) snapshot as ordering witness (rejected) | different vsync | — | — | Different tick: intervening packets can change content (N8D7M4 gate) → OTHER | none (rejected, per brief) |

## 4. W/O/C/D predictions on the full 448-tile census (same run)

Preconditions for every row (else OTHER): same exact stream SHA (two device
+ two Mac reads equal); 11/11 selected-descriptor equality Odin == Mac
replay; marker2050 + EOF; `selected_capture_status == 2`;
`control == 128 PASS`; no map/decode/probe error; every active below is the
full 448 census from the named staging with the identical decoders.
`S1a/S2a` = input+oracle actives from S1/S2same; `Gc` = circuit 448
actives; `Bs` = staging 4 MiB SHAs vs the same-stream Mac broad reference.
Only **W** and **C** have unique nonperturbing observables; O is
unresolved and D is impossible (see rows). No row may be awarded on a
subset of its clauses.

| Category | Mechanism | Predicted same-run observable (all must hold) |
| --- | --- | --- |
| **W** source GPU VRAM sparse after all submitted work complete | tick≤2050 draws absent or never wrote FBP112 region on the Odin GPU | S1 sparse (≤100) AND S2same sparse AND Gc sparse; input==oracle 448/448 on each staging; staging SHAs match each other (both sparse) and differ from Mac broad SHA |
| **O UNRESOLVED** (no awardable observable) | tick≤2050 draws recorded after step 6 flush execute after the S1 cmd (§2 row 15) | No nonperturbing checkpoint separates O from delayed/missing work: the only candidate (T4 S2late) is an intervention whose broad outcome fits both. An O-shaped pattern (in-submit sparse + any later broad read) is recorded as **OTHER/ordering-unresolved**, never as O. Awarding O requires a new execution witness (§5) |
| **C** source broad at copy boundary but staging sparse (copy/barrier/readback) | `buffers.gpu` holds the frame; `copy_buffer` path loses it | S1 sparse AND S2same sparse (copy path broken consistently) AND Gc broad (shader path reads the same source fine); staging SHAs sparse-like while circuit census broad |
| **D IMPOSSIBLE** under identical bytes/decoder | bytes present at fork-table addresses; census loses them | Contradictory as stated: staging bytes byte-equal to the broad reference, run through the identical `selectedDecode`/`oracleDecodeCensus` under the identical 11-field descriptor, must yield a broad census — a sparse decode from identical bytes+decoder is logically impossible. D is awardable **only** with a separately proved host decoder/architecture difference (none exists; N8D7M6 shows 448/448 decoder agreement on both devices). Until such proof, any broad-bytes/sparse-decode pattern is **OTHER/decode-contradiction**, never D |
| **OTHER** | gate miss, intervention, nondiscriminating, or contradiction | any precondition miss; any active 101–249; any O-shaped pattern (ordering-unresolved); any broad-bytes/sparse-decode pattern (decode-contradiction); S2same broad while S1 sparse (unpredicted in-cmd write → informative OTHER); X1/X2/X3/T4 rows; missing vector/SHA |

Separation that survives: W–C by Gc (sparse vs broad) with both copies
sparse. O and D have no awardable signature: O's candidate prediction
equals delayed/missing work under the T4 intervention (equal predictions
cannot discriminate), and D's stated prediction contradicts itself under
identical bytes and decoder. The checker (§6) enforces this by rejecting
any record that awards O or D, or that claims a tap separates a pair
involving them.

## 5. No sound one-run gate; smallest Mac-only experiment

No sound one-run W/O/C/D gate exists from the surviving taps: the only
awardable pair is W–C, and O (the ordering question the milestone actually
needs) has no nonperturbing execution witness while D is self-contradictory
without a separately proved decoder difference. Cutting a device brief now
would spend an Odin launch on a gate that cannot resolve O. No device brief
is cut from this worker.

Smallest next **Mac-only** experiment (no device, no Android build, two
replays, nonperturbing):

1. Implement T3 S2same only (default-OFF, same-submit, +4 MiB) in the
   private worktrees; rebuild `ps2x_tests` only; suite 585/585 with taps
   OFF; record fork + G43 pins, binary SHA, codegen SHA.
2. One OFF + one ON paraLLEl replay of the N8D7M6 stream (lease slot,
   ≤600 s each, ≤16 MiB logs). Require: S1/S2same each broad (≥250), Gc
   broad, input==oracle 448/448 per staging, S1/S2same staging SHAs equal,
   OFF/ON frame hashes equal. This proves the extra in-cmd copy does not
   perturb a broad stream and that S1==S2same when no in-vsync writer
   exists.
3. Stop rules: any OFF/ON frame-hash inequality, or S1≠S2same on the Mac
   broad stream, voids T3 before any device brief is considered.

Extra execution witness still required for O (open design question, not a
claim): a GPU-side witness tying a specific tick≤2050 draw's completion to
before/after the S1 submit — e.g. timeline-tagged per-flush attribution
recorded at `GSInterface::flush` (`gs_interface.cpp:5153-5165`) correlated
with the EE packet tick at `processGIFPacket` (`gs_frontend.cpp:948`).
Per the N8D7M3/M4 gates, bare submit counts or Present-entry pending flags
alone are not such a witness; the witness must show the draw's GPU
execution order relative to the S1 copy, not merely its queue presence.
No speed number is quoted (diagnostic builds only).

## 6. Verifier

`check.py` (this dir, stdlib only) checks the design record, not the
device: (a) every cited source row names a file that exists at its pinned
worktree with at least the cited line count and containing the expected
token (`copy_buffer`, `wait_idle`, `submitCount`/`m_submitCount`,
`selectedRequested`, `oracle_input_equal`, …); (b) exactly the awardable
categories {W, C} carry pairwise-unique full-census signatures (S1,
S2same, Gc, staging-SHA family, input/oracle agreement); (c) O is recorded
UNRESOLVED (no unique observable; any O-shaped pattern is OTHER) and D is
recorded IMPOSSIBLE under identical bytes/decoder (contradictory
prediction) — the checker fails any record that awards O or D or that
claims a tap separates a pair involving them; (d) every tap row that
separates no awardable pair is labeled OTHER or intervention-rejected
(T1, T4, X1/X2/X3). It emits `check-result.json` (`PASS`/`FAIL`) and exits
nonzero on failure. Reran here: see `check-result.json`.

## 7. Gaps / handback

- The O-window (§2 row 15) is a grounded hypothesis (line-cited), not an
  observed race: the implementer must confirm whether EE `gif_transfer`
  recording can interleave the Present thread's step 6→13 window on the
  Odin build (threading differs from Mac replay). Even confirmed, O needs
  the §5 execution witness before any award.
- S2late was the v1 design's O-witness attempt and is withdrawn as a
  discriminator: an extra flush+submit changes what executes in the
  Present, and `post_tick==2050` attests the EE clock, not write
  due-dates. Retained in §3 only as a labeled intervention so the next
  design does not re-propose it.
- D is closed unless a host decoder/architecture difference is separately
  proved (byte-identical staging through identical decoders cannot diverge
  in census). No such proof exists.
- No CPU replay is proposed for the new stream's word values (N8D7M5 §6:
  only 2/6 CPU finals match paraLLEl; value oracle = same-stream Mac
  paraLLEl snapshot, never CPU words).
- No Turnip/shader/barrier cause is claimed; barriers are named only as
  the recorded sites (`gs_renderer.cpp:4813-4819`, `:5063-5075`).

Recommended next action (orchestrator decision): gate this PARTIAL design;
if accepted, run the §5 Mac-only S2same nonperturbation experiment first.
Do not cut a device brief until the §5 O execution witness is designed:
the surviving nonperturbing taps resolve at most W vs C. No push from this
worker.

## 8. Receipts / commands read (all read-only, repo root unless noted)

Reads: this brief; `~/dev/AGENTS.md`; repo `AGENTS.md`;
`local/AGENTS.local.md`; N8D7M6 `REPORT.md` + `ORCH-GATE.md`;
N8D7M3/M4 `ORCH-GATE.md` (+ REPORTs for context); N8D7M5 `REPORT.md` +
`ORCH-GATE.md`; N8D7F `REPORT.md` + `ORCH-GATE.md`. Sources (direct reads):
fork `ps2_gs_parallel_backend.cpp:100-222,400-470,601-750,890-905`,
`gs_frontend.cpp:170-190,750-812,900-956`; G43 `gs_renderer.cpp:1116-1170,
4262-4331,4700-4790,4793-4820,4830-4836,4990-5080,5354`,
`gs_interface.cpp:5153-5165,5191+,5527-5646`, `gs_interface.hpp:150-309`;
plus targeted symbol greps and `git rev-parse/log` in both worktrees.
One LSP hover attempt (no server). No build, replay, boot, install,
launch, lease, or push. New text < 512 KiB.
