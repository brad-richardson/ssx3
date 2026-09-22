# E23 — the complete-feed demand cadence, and what it does and does not transfer

**Tables, no verdicts.** Every number below is from a runtime-closed receipt in
this lane: `cadence.json`, `suite-parse-episodes.json`, `checkpoint-suite.txt`,
`observer-suite.txt`, `cadence-*-events.txt`, `e23a-boot.json`.

## 1. The reference measurement — does the complete path loop?

Hypothesis H0 was that the path where bytes SUFFICE runs a multi-round demand
cadence whose round count and stop condition are the missing rule. The sweep
feeds prefixes of the R3 authored payload through the **actual title wrappers**
(`0x4027b8` Create, `0x402c08` AddCallback, `0x402a10` GetPicture, `0x4029d0`
AddBs) with the E7/E15 tap and the reused observer loaded:

| Feed | Outcome | Producer firings | AddBs | `mpeg-complete` | **matched waiters** | Parks | Parse calls | Packets | Frames |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 60 B | STALLED | **1** | 1 | 0 | 0 | 1 | 1 | 0 | 0 |
| 120 B | STALLED | **1** | 1 | 0 | 0 | 1 | 2 | 1 | 0 |
| 180 B | SERVED | **1** | 1 | 1 | **0** | 0 | 3 | 2 | 1 |
| 240 B | SERVED | **1** | 1 | 1 | **0** | 0 | 4 | 3 | 2 |

**H0 is falsified; H1 holds.** The type-1 producer fires **exactly once per
`GetPicture`** on every branch. The complete-feed path supplies no multi-round
cadence, because the implemented path has no rounds to count. Serving and
stalling differ only in whether that single round delivered enough bytes.

Served runs reached `resumes=1 resumeV0=0 width=16 height=16 pixel=0x800000fe`
with `saved128=1` and `manualCallbackCalls=0`; stalled runs reached
`parked=1 waitReason=6 resumes=0`. All four rc 0, all four parser receipts
`pending=0 errors=0`, backend forwarding exactly 1:1, `bindingChecks=4` valid.

## 2. The ordered cadence — where the two branches actually diverge

The tap sequences for 60 B (STALLED) and 240 B (SERVED) are **identical event
for event through seq 12**, on thread 1, at tick 0:

| seq | Event | Both branches |
|---:|---|---|
| 1-2 | `mpeg-call`/`return` `0x4027b8` | Create, `v0=0x160118` |
| 3-4 | `mpeg-call`/`return` `0x402c08` | AddCallback type 1, `v0=0x1` (handle 1) |
| 5 | `mpeg-call` `0x402a10` | GetPicture enters |
| 6 | `mpeg-request-registration` | one registration |
| 7 | `mpeg-selected` `0x100070` | the one type-1 producer selected |
| 8 | `mpeg-unwind` `0x402a10` | GetPicture unwinds into the typed wait path |
| 9 | `mpeg-call` `0x100070` **`callback=1`** | **the producer fires — once** |
| 10 | `mpeg-producer` | producer block read |
| 11 | `mpeg-call` `0x4029d0` | AddBs enters |
| 12 | `mpeg-input` | bytes offered |

Then, and only then:

| STALLED (60 B) | SERVED (240 B) |
|---|---|
| seq 13 `mpeg-return 0x4029d0 v0=0x3c` (60 accepted) | seq 13 **`mpeg-complete matched=0`** |
| seq 14 `mpeg-return 0x100070 callback=1` | seq 14 `mpeg-return 0x4029d0 v0=0xf0` (240 accepted) |
| seq 15 **`mpeg-wait` thread 1 reason 6** — park | seq 15 `mpeg-return 0x100070 callback=1` |
| *(nothing further)* | *(no park; the picture is served from `onComplete`)* |

## 3. What ends the loop — three bounds, none of them a demand rule

| Loop | Where | Bound | Kind |
|---|---|---|---|
| Callback dispatch | `dispatchGuestNonStreamCallback`, `MPEG.cpp:1714` | `nextCallback < delivery->callbacks.size()` — registration-list exhaustion. **Constant 1** on the fixture, the suite and the title (all have one type-1 registration). | structural |
| Host parser feed | `feed()`, `MPEG.cpp:102-145` | `while (remaining > 0)`, breaking early on `used == 0 && packetSize == 0` — offered-buffer exhaustion. | byte-driven, inside ONE AddBs |
| Picture wait | `getMpegPicture`, `MPEG.cpp:2469` / `:2496` | `decodedFrames.empty()` — serve if a frame exists, else `waitExternal`. | data-driven |

**No round counter exists anywhere.** The 240 B feed's 4 parse calls are the
host loop draining one `sceMpegAddBs`, not four demands:

| Parse call | Offered | Used | Packet | Receives | Frames after |
|---:|---:|---:|---:|---|---:|
| 1 | 240 | 60 | 60 | `rc=-35` | 0 |
| 2 | 180 | 60 | 60 | `rc=0` 16x16, then `rc=-35` | 1 |
| 3 | 120 | 60 | 60 | `rc=0` 16x16, then `rc=-35` | 2 |
| 4 | 60 | 60 | **0** | — | 2 |

This reproduces the suite's committed R3 line exactly
(`[MPEG:feed] inSize=240 parsed=240 packets=3 newFrames=2 totalFrames=2`) and
E18's committed R3 evidence (`parsed240, packets3, newFrames2`), both unloaded
and observer-loaded, from an independently linked fixture. The last parse call
always yields `packetSize=0`: the parser holds the final picture pending a next
start code. **That terminal state — bytes consumed, no packet — is the title's
entire observed state.**

## 4. The C1 control the elimination lacked

On the SERVED branch `sceMpegAddBs` does change the frame count, so
`completeExternalWait(kMpegPictureWaitType, mpegAddr, KE_OK)` **is** raised
(seq 13). It matched **zero** waiters, because the caller is still inside its
own callback (seq 9-15) and is not `Waiting`. The picture is served afterwards
by the `onComplete` continuation, never by the wake.

E22 eliminated C1 on the stalling path, where the wake is never even raised
(`wakePictureWaiter` is false with `packets=0`). E23 shows the wake **raised
and still inert on the path that works**. The retry at `MPEG.cpp:2484` is the
only mechanism that has ever delivered a picture in this runtime.

## 5. Transfer to the incomplete title feed

| Half of the rule | Complete-path reference | Transfers? |
|---|---|---|
| **Trigger point** | The sole post-dispatch re-entry is `onComplete` -> `getMpegPicture(..., false)`, `MPEG.cpp:2484` — **C2a's site**. Measured live on both branches: the served branch serves from it, the stalled branch parks from it. | **Yes.** No invention: the site already runs on the title. |
| **Discrimination C2a vs C4** | C4's site (`:2496-2513`, before the park) is reached **only** on branches that stall. No run that served a picture ever visited it. | **C2a has precedent; C4 has none.** |
| **Loop bound** | The complete path stops because `decodedFrames.empty()` becomes false at `:2469`, closing the gate against a second delivery. | **No.** On the title that gate never closes, so the same bound leaves a re-ask unbounded. |

So a C2a-shaped release-then-re-request **self-terminates for free on the
complete path** and is **unbounded on the title path**. The only additional
stop condition that is not invention is "the producer supplied no new bytes" —
and whether that can ever be satisfied is a fact about the guest, not the host.
That fact is what the one boot measured; see section 7.

## 7. The title observation (e23a) — the transfer is killed, with one named residual

ONE guarded boot, `bound=wall`, rc 0, 75.75 s, atomic claim `E23A` at
`00:19:09Z`, clean release at `00:20:25Z`, post-release `pgrep` rc 1, lease
absent. It reproduces E22 exactly — 6,401 E7 events, park at `seq=6401
tick=249`, parser called **once** (5,040 offered / 5,040 consumed /
`packets=0` / `frames=0` / `errors=0`), backend 1:1, `bindingChecks=4`, real
`# E21 PARSER CLOSURE … reason=_Exit rc=0` — and adds the producer/source
watch set designed in `BOOT-DESIGN.md`.

| Measurement | Value |
|---|---|
| `[diag:watch]` lines total | 6,676 — the **most frequent tag in the pre-park log** (6,639 of 10,171 lines; 1,291 in the final 2,000 before the park) |
| Writes to the 8 producer/source windows | **29, every one before the park.** Last at boot-log line 10,168; the park marker is line 10,171 |
| Writes to those windows after the park | **0**, across 12,113 further boot-log lines (~66 s) |
| Guest still executing after the park? | **Yes.** Thread 4 is scheduled ~300x per 5 s interval in the last sample, and the dormant path's counter runs 333 -> 638 |
| All six guest threads | `status=2` (waiting): thread 1 `waitReason=6` (Mpeg) at `pc=0x3b1028`; threads 2-6 `waitReason=2` (semaphore) at `pc=0x423de8` |
| DMA / GIF | frozen at `dma=4542 gif=210 gsw=0 vif=2` across all six post-park `[run:tick]` samples |

The pre-park writes read as the producer's one-shot setup and match E18's
committed values exactly: `0x548804 = 0xd48748` (data pointer),
`0x548808 = 0x13ac` (= 5,036 bytes), `0x587b78 = 0xdc8340` and
`0x587b7c = 0x30dc8340` (staging buffer). The staging buffer itself was
written once, at line 9,447, by **thread 3** at `pc=0x3e65d0` — the CD/stream
reader — and never again.

**Decision, per the pre-registered table: the transfer is KILLED.** A second
dispatch of the type-1 producer would re-read a source that nothing has
touched for 66 s while a guest thread was running, and would deliver no new
bytes. C2a and C4 cannot produce a frame however they are bounded.

### Residual, named rather than papered over

The watch covers 22 eight-byte windows, not the address space. At line 10,168
the descriptor head was advanced `0x548800 = 0x548880` — and the successor
node at `0x548880` was **not** in the watched set, so its silence is vacuous,
not measured. A follow-up closes this cheaply by adding `0x548880`-`0x5488ff`
and the `0xd48748+` data region to the watch list. Thread 4's ~300 wakes per
5 s are likewise unattributed: they touch nothing watched. The verdict above is
therefore **strong but not exhaustive** — it is the pre-registered branch on
the evidence obtained, not a proof that no byte exists anywhere in guest RAM.

## 6. ASSUMPTIONS — tabled, not adopted

| # | Assumption a fix would need | Why it is not adopted |
|---|---|---|
| A1 | The firmware re-asks its input producer more than once per picture request. | Nothing in this lane's evidence shows more than one firing on ANY path, including the four that decode. Multi-round demand is unobserved everywhere. |
| A2 | A no-progress round (producer returns 0 new bytes) is a legitimate stop. | Plausible and cheap, but the runtime has no such counter today, and whether a second ask could ever return bytes was the open fact step 4 measures. |
| A3 | The title's 5,040 B is a partial first delivery rather than the whole of what the guest had. | E22 retained the complete payload and showed it is accepted cleanly (`errors=0`, `decoderFailed=0`); it does not show more exists. |
| A4 | Q1's `GOP offset + 5,461` is the real-stream deficit. | Barred by E22's scope limit — measured on `authored-black.m2v`, not the real stream. Not imported. |
