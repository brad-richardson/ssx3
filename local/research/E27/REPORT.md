| E27 | Receipt |
|---|---|
| Stop point | **All three missions executed; nothing blocked.** A STATIC autopsy, as briefed: no boot, no lease, no capture driver, no `stdbuf`, no title execution of any kind. The walker is named down to the instruction; the feed-once mechanism is named on **both** sides; the thread-1 path from the tag to the end of the run is tabled leg by leg against the log; and the re-ask question is answered — **not excluded**. Fix gate: **STOP**, honored as written. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed at open **and** close; `status --short` exactly `?? ps2_log.txt`. Read-only on the fork throughout: sources and `git show` only. |
| Questions reached | **Mission 1 CLOSED** — walker, classifier, tag semantics, post-tag path and the whole route from the tag to `sceMpegAddBs`. **Mission 2 CLOSED** — one call site, one loop, two independent once-mechanisms, and an eight-leg static-vs-log table with no disagreement. **Mission 3 ANSWERED, and it inverts E26's tabled reading**: the guest re-ask is **not** one-shot and the chunk it needs is **already the head of its own queue**; the one-shot is host-side and is held alive by the wait it blocks. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero pushes, zero regeneration, zero builds, zero relinks, zero boots, zero lease claims (not even a probe-claim), zero deletions. |
| Next dependency | None blocking. E27 hands over a closed static case and names, in one paragraph, the single host-side observable an E28 boot would settle. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | 8 h. Opened `2026-09-22T14:01:36Z` (fork gate), closed the same session. **Actual time used: well inside the box.** |
| Required reads | E26 `REPORT.md` (180 lines), `x-a-startcode.json`, `chunk-map.json`, E24 `REPORT.md` §picture and `NEXT-BRIEF.md` — all read in full before the first grep. E26 `NEXT-BRIEF.md` §X read for the question as posed. |
| Hypotheses | **None pre-registered.** This lane is an autopsy of already-captured bytes plus the sources; it measures, it does not test. Stated so the absence cannot be read as a lost registration. |
| Inputs | The e26a capture (function log, boot log — both re-hashed against E26's committed pins) and the fork at `3adc0478`: 9,454 generated guest sources plus the git-tracked `MPEG.cpp` and `EeScheduler.cpp`. Nothing else. |
| Strict order | Brief read in full → **fork gate (first)** → Mission 1 static → Mission 2(a) static → Mission 2(b) log mine → Mission 3 synthesis → fix gate → SSD pin pass 2 → close. No gate tripped. |
| Fix gate | **STOP.** `fix-gate.json`. |
| Preserved constraints (E18 ABI, BINDING) | **Preserved by construction** — E27 edited no source, built nothing and ran nothing. |
| Byte caps | Internal ≤ 512 MiB: E27 wrote **text only**, 9 JSON receipts + 2 Markdown + 6 Python tools. No `e27-*` SSD scratch was needed and none was created. `COPYFILE_DISABLE=1` on every step. Zero deletions. |

## Mission 1 — the walker, named

| Mission 1 | Receipt |
|---|---|
| **The walker** | **`sub_003DFED0`**, `ps2xRuntime/src/runner/sub_003DFED0_0x3dfed0.cpp`, guest `0x3dfed0 - 0x3e00d4`. |
| **The tagging instruction** | File **line 257**: `// 0x3dff8c: 0xae420004  sw $v0, 0x4($s2) (Delay Slot)` → `WRITE32(ADD32(GPR_U32(ctx, 18), 4), GPR_U32(ctx, 2))`. |
| **Why `ra` = `pc` + 4** | The store is the **delay slot** of `jal func_3E5700` at `0x3dff88`. `$ra = 0x3dff90` is that `jal`'s own return address, not a caller frame — and the file's line 26 carries `case 0x3dff90u: goto label_3dff90;`, the same address. E26's `pc=0x3dff8c ra=0x3dff90` pair is explained exactly, with no second function involved. |
| **What the tag is** | `$v0 = $s1 \| ($s5 << 24)` — `0x3dff84 or $v0, $s1, $v0`, with `$v0 = $s5 << 24` computed in the delay slot at `0x3dff3c`. `$s1` is the chunk's **total length** (`0x3e006c lw $s1, 0x4($s2)`); `$s5` is the **kind**. |
| **The arithmetic reproduces both captured words** | `(2 << 24) \| 0x28 = 0x02000028` at `0xd49af0` (SCHl, total 40) and `(1 << 24) \| 0x381c = 0x0100381c` at `0xd49b18` (MPCh, total 14,364). E26's two anchor lines, derived rather than matched. |
| **`$s2` is the walk cursor** | `0x3e0058 lw $s2, 0x54($s0)` — the cursor lives at **`ctx0 + 0x54`**, and `0x3dffe8 sw $v0, 0x54($s0)` advances it by the chunk length. The data end is `ctx0 + 0x58`. |
| **The classifier** | **`sub_003DFE88`**, `0x3dfe88 - 0x3dfecc`. It is a **table lookup**, not a state machine: `n = state->[0x20]`, `tbl = state->[0x1C]` of 12-byte `{mask, match, kind}` rows; `if ((magic & mask) == match) return kind` (`0x3dfeb8 lw $v0, 0x8($a0)`), else **`-2`** (`0x3dfecc`). |
| **So what does the top byte MEAN** | An **occupancy bit that carries the kind**. It is written when the walker *publishes* a chunk and **stripped when the consumer dequeues it** — `sub_003E12E0` at `0x3e132c and $s1, $v1, 0x00FFFFFF` then `0x3e1330 sw $s1, 0x4($s2)`. The walker reads it back at `0x3e0074 and $v0, $s1, 0xFF000000`: a chunk that is **still tagged** is still queued, so the walker overwrites it with an 8-byte sentinel stub (`0x3e0084` len = 8, `0x3e008c` magic = `$s6->[0x11c]`) and then terminates (`0x3e0044`: magic == sentinel → return 1). **The producer/consumer handshake of this ring is stored in the chunk headers themselves.** |

**The walk, in pseudocode from the source:**

```
walk(ctx0):                                  // $s0 = $a0
    $s7 = -0x40                              // 64-byte align mask
    $s6 = ctx0->[0x60]                       // the stream object
    goto LOOP_TOP                            // 0x3dff00 b .+0x54
LOOP_TOP:                                    // 0x3e0054
    end  = ctx0->[0x58]
    cur  = ctx0->[0x54]                      // $s2
    if (end - cur) < 8:            return 0  // 0x3e0064
    len = cur->[4]                           // $s1
    if (len & 0xFF000000):                   // 0x3e0078 -- STILL QUEUED
        cur->[4] = 8;  cur->[0] = $s6->[0x11c]   // write the sentinel stub
        len = 8
    if (end < cur + len):          return 0  // 0x3e00a0 -- body not resident
    if (cur->[0] == $s6->[0x11c]):           // 0x3dff08 -- the sentinel
        len = align64(len)                   // 0x3dff14-0x3dff24
    kind = sub_003DFE88(ctx0, cur)           // 0x3dff2c  -- $s5
    if (kind < 0):                           // 0x3dff38
        lock(ctx0+4)
        if ($s6->[4] != 4):
            cur->[0] = -2                    // 0x3dff60 mark DEAD
            ctx0->[0x54] += len              // 0x3dff6c skip it
        unlock(ctx0+4)
    else:
        cur->[4] = len | (kind << 24)        // *** 0x3dff8c  THE TAG ***
        lock(ctx0+4)                         // 0x3dff88 (the tag is its delay slot)
        if ($s6->[4] != 4):
            slot = ctx0->[0x24] + kind*16 - 16      // 0x3dffa4 the PER-KIND queue
            slot->[8] += len                        // 0x3dffb4-0x3dffc0
            if (slot->[8] == len): slot->[0xC] = cur  // 0x3dffc4 first entry -> head
            ctx0->[0x4C] += len                     // 0x3dffdc outstanding bytes
            ctx0->[0x54] += len                     // 0x3dffe8 ADVANCE THE CURSOR
            if (crossed ctx0->[0x44]): ctx0->[0x48] = 0
        unlock(ctx0+4)                       // 0x3dfff8
    if ($s6->[4] == 4):                      // 0x3e0000
        cur->[4] = align64(len) | (kind<<24);  return 0
    if (cur->[0] == $s6->[0x11c]): return 1   // 0x3e0044 sentinel reached
    goto LOOP_TOP                             // 0x3e00a0 beql -> 0x3dff08
```

| **The load-bearing question: what does it do AFTER tagging** | Receipt |
|---|---|
| Immediately | `0x3dff88 jal func_3E5700($s0+4)` — the tag store **is that call's delay slot**, so the very next thing is taking the stream lock. |
| Then | It **publishes**: `slot = ctx0->[0x24] + (kind-1)*16`; `slot->[8] += len`; and if the slot was empty, `slot->[0xC] = cur` — the queue **head**. |
| Then | It **advances the cursor** past the chunk (`ctx0->[0x54] += len`), releases the lock, and **loops**. |
| **It never feeds** | There is no `sceMpegAddBs`, no callback and no signal on this path. The walker is the **producer**; feeding is a different function on a different trigger. |
| **Who calls the walker** | **`sub_003E0170`** at `0x3e01ec jal func_3DFED0` — the **read-completion** path. It adds the delivered byte count to `ctx0->[0x170]` (`0x3e01e8`) and to the data end `ctx0->[0x58]` (`0x3e01f0`) **and only then** runs the walker. **The walker is driven by data arrival, never by consumption.** Nothing on the consume path re-enters it. |

| **Where a tagged chunk actually goes** | Step |
|---|---|
| 1 | `sub_003DFED0` publishes it into the per-kind slot at `ctx0->[0x24] + (kind-1)*16`, fields `{+0 owner, +4 kind, +8 bytes, +0xC head}`. |
| 2 | `sub_003E12E0` dequeues the head, **strips the kind byte**, decrements `slot->[8]`, and walks forward to the next chunk whose tag matches `slot->[4] << 24`. |
| 3 | `sub_003AEAD0` wraps it in a 3-word descriptor `{+0 header, +4 header+8, +8 total}` and stages it in the source object's one-slot pushback. |
| 4 | `sub_003B06B0` pops that slot (`0x3b06c4 sw $zero, 0x0($v0)`). |
| 5 | `sub_003B0B40` copies `total - 8` bytes, zero-pads to `(total + 7) & ~0xF`, and calls `sceMpegAddBs`. |
| **Every step has a watch receipt in e26a** | `0x548800 = 0xd48740` at `pc=0x3aebb0` (descriptor `+0` = chunk header) · `0x548804 = 0xd48748` at `pc=0x3aec08` (`+4` = header + 8) · `0x548808 = 0x13ac` at `pc=0x3aec1c` (`+8` = 5,036) · `0x5487c0 = 0x548800` at `pc=0x3b0510` (staged into the movie object by `sub_003B04F8`) · `0x5487c0 = 0x0` at `pc=0x3b06c4 ra=0x3b0b70` (the pop consuming it) · `0x548800 = 0x548880` at `pc=0x3204c4` (the descriptor node returned to the free list — E23's "head advance", now named as a **free**). |
| **The 5,040, derived from source before it is matched to bytes** | `0x3b0b84 lw $s0, 0x8($s3)` = 5,036 · `0x3b0b94 addiu $s0, $s0, -0x8` → **5,028 ES bytes** · `0x3b0b90`/`0x3b0b98` with `$v1 = -0x10` → `$s2 = (5036 + 7) & ~0xF =` **5,040** · the loop `0x3b0bb8-0x3b0bd0` zero-fills from offset 5,028, and the first **12** of those zeros land inside the 5,040 that is fed. **E24 and E26 measured 5,028 + 12 = 5,040 from the bytes; the source produces exactly that arithmetic.** |
| **Why the staged length reads `0x13ac` and not `0x010013ac`** | Because `sub_003E12E0` **strips the tag at `0x3e1330` before returning the chunk**, and `sub_003AEAD0` reads `chunk+4` only afterwards (`0x3aec1c`). The descriptor's untagged 5,036 is therefore evidence *for* the handshake, not against it. Stated as derived: `0xd48744` is **outside** E24's watch tiers (the head tier starts at `0xd48748`), so chunk 0's own tag store was never observable. |

## Mission 2 — the feed-once path

| Mission 2 (a) — static | Receipt |
|---|---|
| **`sceMpegGetPicture` call sites in the whole image** | **ONE.** `grep -rl 0x402A10u` over all 9,454 generated sources returns exactly `sub_003B0FB8_0x3b0fb8.cpp`. The thunk `sub_00402A10` is a one-line `ps2_stubs::sceMpegGetPicture(rdram, ctx, runtime);`. |
| **How closed that enumeration is, exactly** | It closes **direct** calls, and E27 also checked for **immediate materialisation**: the only three `addiu …, 0x2A10 / 0x29D0` sites in the image build `0x482A10` (`0x28ce7c lui $v0, 0x48`), `0x4A29D0` (`0x228490 lui $v0, 0x4A`) and `0x2C29D0` (`0x2c2c20 lui $s7, 0x2C`) — **none** of them `0x402a10` or `0x4029d0`. What it does **not** close is an address sitting in an ELF `.data` jump table, which is not in these sources. That residual is bounded dynamically instead: `[MPEG:GetPicture]` and `[MPEG:feedES]` each appear **once** in the boot log, both far below their 32-entry trace cap, so however many static sites exist, **one** call of each ran. |
| The call | `0x3b1020 jal func_402A10`, return address **`0x3b1028`**. The park snapshot records thread 1 at **`pc=0x3b1028 ra=0x3b1028 wait=Mpeg:0`** — byte-exactly this `jal`'s return address. |
| The caller itself | `sub_003B0FB8` (guest `0x3b0fb8 - 0x3b104c`) is **straight-line**: `func_3B10D0`, a size computation, the `jal`, then `self->[0x10] += 1` (`0x3b1034`/`0x3b103c`) and return. No loop **inside** it. |
| **But the loop is one level up** | **`sub_003B1050`** — the *second* guest function generated into the **same** file `sub_003B0FB8_0x3b0fb8.cpp` (header `// Address: 0x3b0fb8 - 0x3b10d0`; there is no separate `_0x3b1050.cpp`). |
| **The re-ask loop, as emitted** | `0x3b1070` release the previous picture through `$v0->[0x34]` if `$a1 != 0` · `0x3b108c jal func_402B38` — the guard, `v1 = (self+0x30)->[0x40]; return v1->[0]` · `0x3b1094` if the guard is non-zero, break with `v0 = 0` · **`0x3b109c jal func_3B0FB8`** — the GetPicture call · `0x3b10a4 lw $v1, 0x10($s0)` — the counter the callee just bumped · `0x3b10a8 sltu $v1, $v1, $s1` · **`0x3b10ac bnez $v1 → 0x3b1070`**. |
| **Verdict on the call site** | **COUNTER-BOUNDED and RE-ASKABLE.** Not one-shot, not by construction and not by latch. The bound is `self->[0x10] < $s1` (pictures served < pictures requested); the loop's only other exit is the `func_402B38` guard. |
| **A generated-code fact that matters for reading the log** | `jal func_3B0FB8` at `0x3b109c` is compiled as an **intra-file `goto label_3b0fb8`** (file lines 485–494), not as a `dispatchGuestBranch`. So the re-ask loop and the GetPicture caller share **one** `PS_LOG_ENTRY`. Any count of `sub_003B0FB8` in the function log is a count of *entries into the pair*, not of GetPicture calls. Named here because it is exactly the trap that would make the log read "one call" when it means "one frame". |
| **What enforces "one producer firing per GetPicture" — the guest half** | `sub_003B0B40` (guest `0x3b0b40`) is **straight-line**: exactly one `jal func_3B06B0` (`0x3b0b68`, the pop) and exactly one `jal func_4029D0` (`0x3b0c2c`, `sceMpegAddBs`) per invocation. No loop, no counter. `sceMpegAddBs` likewise has **exactly one call site** in the image. |
| **What enforces it — the host half (this is the load-bearing one)** | `g_mpeg_stub_state.nonStreamDeliveries`, an `unordered_map<uint64_t, weak_ptr<MpegNonStreamDelivery>>` keyed `(mpegAddr << 32) \| 1`. `MPEG.cpp:2464-2481`: `delivery = pending.lock(); if (requestInput && !delivery && decodedFrames.empty() && !eofSeen && !streamEnded && !decoderFailed) { …make_shared…; dispatchInput = true; }`. **A live delivery suppresses the dispatch.** |
| The second guard | `MPEG.cpp:1760` — the invocation's `onComplete` re-enters `getMpegPicture(rdram, &parent, runtime, **false**)`, with the author's comment *"continue this request without re-triggering it."* |
| The author's own words for the latch | `MPEG.cpp:531` — *"One caller-owned request, retained by its invocation/wait continuations."* |
| **Why it is self-sustaining** | `MPEG.cpp:2514` passes `waitExternal` a resume lambda that captures `delivery` **by value**; `EeScheduler.cpp:2120` moves that `std::function` into the blocked thread's `EeWaitState`. **The `shared_ptr` that suppresses the producer is owned by the very wait that is waiting for the producer's result.** Even the resume path cannot escape it: the lambda is alive while its own body calls `sceMpegGetPicture`, so `pending.lock()` is non-null there too. |
| **A guest path nobody has named yet** | `0x3b0b7c beqz $s2 → 0x3b0bdc`: if the pop yields nothing, the guest builds 16 bytes of word `0xB7010000` (`0x3b0be4 lui $a0, 0xB701`, loop `0x3b0be8-0x3b0c00`) and feeds **that**. In little-endian memory `0xB7010000` is `00 00 01 B7` — the MPEG-2 **`sequence_end_code`**. **The guest owns a path that terminates the stream by itself.** It is unreachable here for the same single reason the next chunk is. |

| Mission 2 (b) — the log, leg by leg | Receipt |
|---|---|
| The log | `P1/run/ps2_log-e26a-1.txt`, **3,607,246 lines, 0 unparsed**, SHA256 `d849775b…cf1024ec` — **equal to E26's committed pin**, read twice, separated in time. |
| **The feed, in the log** | **3456124** `>> sub_003B0FB8 enter` (depth 5) — the **only** entry in the whole run · **3456125** `>> sub_00402B38` — `sub_003B1050`'s loop guard, so this entry is guest fn `0x3b1050` · **3456127** `>> sub_003B10D0` — called at `0x3b0fc8`, i.e. guest fn `0x3b0fb8`, reached by the `goto` at `0x3b109c` · **3456129** `<< sub_003B0FB8 exit` — **the C++ frame returning because `dispatchGuestBranch(0x402A10)` returned false: the park** · **3456130–3456134** the whole guest stack unwinds to depth 0 · **3456135** `>> sub_003B0B10 enter **at depth 0**` — the producer callback, entered by the scheduler as a fresh `GuestInvocation` with RA forced to 0, exactly as `dispatchGuestNonStreamCallback` builds it · **3456136–3456225** the one feed: pop → memcpy → release → AddBs. |
| Named limit on the log | `ps2_log.h`'s `depth()` is `thread_local` and the EE runs all guest threads on one host thread, so the indentation is **one interleaved stack** and does not separate guest threads. And `<< exit` is a **C++ return**, which a park also produces. Counts are exact; nesting is not a per-guest-thread stack. |

| Leg | Static prediction | Log | Verdict |
|---|---|---|---|
| Walker `sub_003DFED0` runs again after the feed | NO — its only caller is `sub_003E0170`, the read-completion path | **16** enters, **all** in lines 3452090–3454855; the last is 1,269 lines before the GetPicture frame. **0 after.** | **AGREE** |
| Classifier `sub_003DFE88` runs again | NO — called only by the walker and by `sub_003DFE18` | **56** enters, all 3452091–3454735. **0 after.** (`sub_003DFE18`: **0** enters all run.) | **AGREE** |
| Walker caller `sub_003E0170` runs again | NO — it is the read completion; no read completes | **29** enters, last 3454849. **0 after.** | **AGREE** |
| Feeder `sub_003B0B40` runs again | NO — reached only from the producer callback or the movie open | **2** enters: 3455221 (the movie-open entry at guest `0x3b0c58`, which never calls the pop) and 3456136 (the one real feed). **0 after.** | **AGREE** |
| Pop `sub_003B06B0` runs again | NO — one call site, inside the feeder | **Exactly 1** enter in the entire run, at 3456137. | **AGREE** |
| GetPicture site `sub_003B0FB8` runs again | the loop at `0x3b10ac` **would** re-ask — but only once the `jal` at `0x3b1020` returns | **Exactly 1** enter, 3456124, and the frame never resumes. The guest never reaches `0x3b10ac`. | **AGREE on the precondition; no re-ask** |
| Refill kick `sub_003DCFC0` fires | only if `ctx0->[0x4C]` crosses **below** `ctx0->[0x44]` in `sub_003DFC48` **and** `ctx0->[0x38] == 1` | **ZERO** enters in the entire 3.6 M-line log. The threshold was never crossed downward, not once. | **AGREE, and stronger** |
| The `sceMpegAddBs` / `sceMpegGetPicture` thunks appear | NO — those thunk files guard `PS_LOG_ENTRY` with `#ifdef _DEBUG`, not `PS2_FUNCTION_LOG_TRACKER` | **LOG-SILENT**, 0 each, as predicted. | **AGREE (log-silent by construction)** |

| **What runs after the feed** | Receipt |
|---|---|
| Boundary | Line **3456226**, the line on which the one producer callback `sub_003B0B10` exits. **151,020 lines** follow. |
| Distinct symbols in all of them | **16.** `sub_003E4DB8 · sub_003825C0 · sub_003825F8 · sub_003C1980 · sub_0031A490 · sub_0031ABD0 · sub_00317520 · sub_00423DD0 · sub_00423DE0 · sub_0031AC08 · sub_00317500 · sub_00317348 · sub_00227F58 · sub_00326B88 · sub_00326EB0 · sub_0031A6B8`. |
| Shape | **4,195 identical iterations of one interrupt-driven cycle** (two of the sixteen run 8,390 = 2×). Not one MPEG, stream, chunk-walk, descriptor or CD symbol appears. |
| **Verdict** | **Thread 1 executes nothing after the feed.** The post-park tail is a single timer loop — E26's sema-31 result, seen from the other instrument and agreeing with it. |
| Boot-log corroboration | `[MPEG:feedES]` ×1, `[MPEG:feed]` ×1, `[MPEG:GetPicture]` ×1, `[MPEG:GetPicture:FRAME]` ×0, `IsEnd`/`CdStreamStart`/`CdStreamEof`/`demux` ×0. **Every one of those counters is capped at 32 in `MPEG.cpp`, so a count of 1 is a true count and not a cap.** |
| **One line E26 tabled that E27 can now downgrade** | E26 noted that `sub_003C1980` — the `WaitSema(36)` owner — appears on the MPEG delivery path "entered immediately after `AddBs`", and correctly declined to upgrade it. The post-feed histogram settles it: `sub_003C1980` is entered **4,195 times after the feed**, once per timer iteration. Its appearance next to `AddBs` in the park trace is the **first** iteration of that same loop, not a link to the MPEG chain. **The shared-function observation is weaker than E26 left it, not stronger.** |

## Mission 3 — the re-ask question, answered

| Mission 3 | Receipt |
|---|---|
| **Headline** | **The guest re-ask is not one-shot — it is one backward branch away, and the chunk it would get is already the head of its own queue.** What is structural is the **host-side** suppression, and it is held alive by the wait it blocks. |
| **The re-ask path, named** | `sub_003B1050`, branch **`0x3b10ac bnez $v1 → 0x3b1070`**, condition `(unsigned)self->[0x10] < $s1`. |
| **Its trigger, exactly** | **The `jal func_402A10` at `0x3b1020` returning.** That is all. No register, no callback, no semaphore, no event flag, no second thread. |
| **What it would get** | **`0xd49b14`, the second `MPCh`** — because `sub_003E12E0` **already advanced the kind-1 head to it** when it dequeued chunk 0: `0x3e1360 $a2 = 0xd48740 + 5036 = 0xd49aec` (SCHl, tag `0x02` ≠ kind 1), then the `0x3e1384` walk adds `0x28` to reach `0xd49b14`, whose tag `0x0100381c & 0xFF000000` matches `slot->[4] << 24 = 0x01000000`, so `0x3e13c8 sw $a2, 0xC($t1)` parks the head **there**. |
| **Which makes E26's byte finding sharper** | The terminating start code `00 00 01 00` E26 located at `0xd49b1c` is the **payload of the chunk the queue head is already pointing at**. The guest is **one `func_3E12E0` call** from it — not one chunk short of *finding* it, one call short of *asking for* it. |
| **And if the queue were empty instead** | `sub_003B0B40` would take `0x3b0b7c → 0x3b0bdc` and feed 16 bytes of `00 00 01 B7`, the `sequence_end_code`, on its own. **Both of the guest's exits from this state are live code; neither can run.** |
| **The structural one-shot, named** | `g_mpeg_stub_state.nonStreamDeliveries[(mpegAddr << 32) \| 1]`, a `weak_ptr<MpegNonStreamDelivery>`. (1) GetPicture with `requestInput=true` finds the key empty, creates the delivery, dispatches the producer **once** (`MPEG.cpp:2464-2493`). (2) `onComplete` re-enters `getMpegPicture` with `requestInput=**false**` (`MPEG.cpp:1760`). (3) `decodedFrames` is empty → `waitExternal` with a lambda **capturing the `shared_ptr` by value** (`MPEG.cpp:2514-2526`). (4) `EeScheduler::waitExternal` **moves that `std::function` into the blocked thread's `EeWaitState`** (`EeScheduler.cpp:2120`). (5) `pending.lock()` therefore stays non-null for the whole park, so every further GetPicture takes the `!delivery == false` branch and dispatches no producer. |
| **Every wake site, enumerated and disposed of** | `sceMpegAddBs` → `completeExternalWait` (`2058`) — needs new frames / end / failure, and needs a second AddBs, which needs a second producer dispatch: **circular** (and in this run `wakePictureWaiter` was **false**: 0 new frames). `notifyMpegCdStreamEof` (`1999`) — driven by thread 1's CD stream: **excluded**, 0 `CdStreamEof` lines. `sceMpegFlush` (`2023`), `sceMpegDelete` (`2239`), `sceMpegCreate` (`2165`), `sceMpegReset` (`2718`) — all guest calls on thread 1: **excluded**. `sceMpegDemuxPss`/`PssRing` (`2285`/`2291`/`2378`/`2384`) — the PSS path; this title uses the ES path, 0 demux lines: **excluded**. A **timeout**: `waitExternal` takes no timeout argument — **excluded by construction**. |
| **Could another thread do it?** | No. `sceMpegGetPicture` has one call site and `sceMpegAddBs` has one, both reached only from thread 1's suspended stack. Enumerated over all 9,454 generated sources. |
| **Which leg of E26's mutual-wait reading breaks** | Leg 1 ("one `GetPicture` feeds exactly one chunk") **holds**, and E27 names both halves. Leg 2 ("`GetPicture` does not return until a frame appears") **holds**: `getMpegPicture` calls `waitExternal` whenever `decodedFrames` is empty with no EOF/end/failure. Leg 3 (the parser needs the next start code) is E24/E26's bytes and E27 did not re-test it. **The leg that breaks is the unstated fourth one — "and so each side is waiting for the other."** The guest is not waiting for anything it could not do: it holds the next chunk at the head of its own queue and a live loop branch to ask for it. It is **blocked inside the host call**, and that host call is holding the token that stops the guest from being asked. **The symmetry E26 tabled is not there. It is a single party holding the key to its own door.** |
| **What an E28 capture would observe** | A dynamic capture can add little on the guest side — that case is closed statically — so the one thing worth a boot is the host side, and it needs no new guest instrumentation. Arm a watch on the kind-1 queue slot (`ctx0->[0x24]+0`: the byte count at `+8` and the head at `+0xC`) and on `0xd49b14`/`0xd49b18`, and log from inside `MPEG.cpp` every entry to `getMpegPicture` with its `requestInput` flag and the result of `pending.lock()`, plus every `completeExternalWait(kMpegPictureWaitType, …)` with its caller. **E27's falsifiable prediction, settled in one boot:** the slot head reads `0xd49b14` with a byte count of at least 14,364 from the feed onward and never changes; `0xd49b18` still reads `0x0100381c` at the park; `getMpegPicture` is entered exactly twice (`true` then `false`) with `pending.lock()` non-null on the second; and `completeExternalWait` for the picture wait is called **zero** times after the feed. That is E28's brief to write, not E27's — named in one paragraph and designed nowhere. |

## Gates, hygiene, budget

| Fork gate | Receipt |
|---|---|
| Open | `2026-09-22T14:01:36Z`. `HEAD` = `refs/remotes/fork/ssx3` = `ls-remote fork refs/heads/ssx3` = **`3adc0478b6d2260acdd28a249466f2eef9a20176`**, 7/7 checks green, `status --short` exactly `?? ps2_log.txt`. `fork-gate.json`. |
| Close | Re-run at close, same seven checks, same sha. `fork-gate-close.json`. |
| Pre-existing stderr | The four `non-monotonic index …._pack-….idx` lines are the AppleDouble artefact E23–E26 all recorded; carried verbatim, stderr only, `rc 0`. |
| Fork mutations | **Zero.** Read-only throughout: `cat`, `grep`, `git ls-files`, `git check-ignore`, `git show`. No edit, no commit, no push, no `git add` inside the fork. |

| SSD corroboration — the link is PROVEN pattern-dependent corrupt | Receipt |
|---|---|
| Rule applied | Every file this lane quotes was hashed **twice, in separate invocations separated in time**; anything git **tracks** was additionally compared against the git object, which is content-addressed and does not go through the same read path; the two e26a captures were compared against the SHA **E26 committed**. |
| Pass 1 / pass 2 | `pins-pass-1.json` at `14:19:13Z`, `pins-pass-2.json` at close. **19 files, all equal across both passes.** |
| Independent corroboration where it exists | `MPEG.cpp` (110,191 B, `f83ed02e…`) — **git object EQUAL**. `ps2_log-e26a-1.txt` (127,074,085 B, `d849775b…cf1024ec`) and `boot-e26a-1.log` (13,355,448 B, `c9ddf91a…78e33e5`) — **both equal to E26's committed pins**, so every byte quoted from them is corroborated against text already in this repo's history. |
| **Where corroboration is NOT available, stated** | The 16 generated guest sources are **`.gitignore`d** (`.gitignore:21  ps2xRuntime/src/runner`), so for them **repetition in time is the only check available**. `git ls-files ps2xRuntime/src/runner` returns 7 tracked paths, none of them a `sub_*.cpp`. This is named, not hidden: every disassembly quoted in Mission 1 and Mission 2(a) rests on two matching SSD reads and on nothing else. |
| SSD link | Mounted and stable throughout; re-checked at the fork gate, at both pin passes and at close. It never disappeared, so the brief's table-and-stop rule was never triggered. |
| **One receipt discrepancy, reported not chased** | E26's byte-cap table gives the boot log as 13,315,314 B and the function log as 127,058,902 B; the pinned files measure **13,355,448** and **127,074,085**. The **SHAs match E26's pins exactly**, so these are the right files; E26's cap accounting evidently sampled sizes at a different moment from the pinning. It changes nothing in E26's result or E27's and is recorded so a later reader does not mistake it for corruption. |

| Budget | Receipt |
|---|---|
| Internal | **Text only.** 6 Python tools, 9 JSON receipts, 2 Markdown — the whole lane is far inside the 512 MiB cap. |
| SSD | **No `e27-*` scratch was needed and none was created.** Zero writes to the SSD. `COPYFILE_DISABLE=1` exported on every step. |
| Deletions / reclaim | **Zero**, as required. |
| Boots / leases | **0 boots, 0 lease claims, 0 probe-claims.** The lease file was never opened, read or tested. No capture driver, no `stdbuf`, no suite execution. |

| Fix gate | Receipt |
|---|---|
| Decision | **STOP**, as the brief set it before the lane began. `fix-gate.json`. |
| Demonstrated edges | **Four**, and they are not one edge: the walker + tag semantics; the single GetPicture call site inside a counter-bounded re-ask loop; the host delivery latch owned by its own wait; and the empty post-feed tail. |
| Why no fix | The load-bearing edge is a **host lifetime question** — who owns the delivery `shared_ptr` while a picture wait is outstanding — which is adjacent to the preserved E18 ABI. E27 ran no boot, so it has **no fail-before, no regression and no suite run**. A fix needs all three plus exactly one edge. |
| Candidates still KILLED | C2a and C4 (E23); C1, C3, C5–C9 (E22). E27 re-proposes none and re-opens none. |

| Evidence hygiene | Receipt |
|---|---|
| Standalone data | `fork-gate.json`, `fork-gate-close.json`, `logmine.json`, `logmine2.json`, `tail-after-feed.json`, `mission-1-walker.json`, `mission-2-feedonce.json`, `mission-3-reask.json`, `pins-pass-1.json`, `pins-pass-2.json`, `fix-gate.json`, plus the six tools that produced them. |
| Evidence is text-only | **No binaries, no copied captures.** The e26a logs are referenced by SHA and read in place; not one byte was duplicated into the repo. |
| Tools | `e27_common.py` (written fresh — E27 builds nothing and boots nothing, so E26's build/admission/boot machinery is deliberately **not** carried), `e27_fork_gate.py` (E26's, renamed mechanically), `e27_logmine.py`, `e27_tail.py`, `e27_logmine2.py`, `e27_pins.py`, `e27_missions.py`, `e27_fixgate.py`, `e27_close.py`. |
| Errata carried | **E21-E1, E23-E1, E23-E2, E24-E1, E24-E2, E24-E3 carried forward unchanged and not re-fixed.** E24-E2 is honoured operationally: the tail receipt below is recomputed **after** the last edit and its row lies outside the hashed prefix. **E27 adds no errata.** |
| Publication | `[E27]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Scope: E27 evidence only; no fork files, no generated sources. **Not pushed** — the orchestrator pushes at poll. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–194; 31543 B; SHA256 `33c432bac61a56bf153accb1091dedf9ba23a216ad78cddad65c8c79a9cbd75d` (the prefix is every line ABOVE the `\| Tail receipt \| Value \|` header, so this row lives after the boundary and cannot invalidate itself — errata E24-E2) |
| Source-tail gap | **None, and three named limits, stated where they bite rather than in a footnote.** (1) The function log's `depth()` is `thread_local` and the EE runs all guest threads on one host thread, so indentation is one interleaved stack and does not separate guest threads; counts are exact, nesting is not a per-thread stack. (2) `<< exit` is a **C++ return**, and a park produces one — which is exactly why line 3456129 is the park and not a guest return. (3) The 16 generated guest sources are `.gitignore`d, so they have **no content-addressed copy anywhere**; two matching SSD reads 455 s apart is the only corroboration available for them, and every disassembly in Missions 1 and 2(a) rests on that alone. A fourth, smaller one: `jal func_3B0FB8` at `0x3b109c` compiles to an intra-file `goto`, so the re-ask loop and the GetPicture caller share one `PS_LOG_ENTRY` — named because it is the trap that would make the log read "one call" when it means "one frame". |
| E27 REPORT TAIL COMPLETE | A static autopsy, no boot, no lease, no fork mutation. **The walker is `sub_003DFED0`**, and the tag E26 saw is the **delay-slot store at `0x3dff8c`** in `jal func_3E5700` — which is the whole explanation of `ra = pc + 4`. The top byte is an **occupancy bit carrying the chunk kind** from `sub_003DFE88`'s `{mask, match, kind}` table: set when the walker publishes, **stripped when `sub_003E12E0` dequeues**. After tagging, the walker publishes into a per-kind queue at `ctx0->[0x24]` and advances its cursor; **it never feeds**, and its only caller is the **read-completion** path, so consumption can never re-enter it. `sceMpegGetPicture` has **exactly one call site** in all 9,454 generated sources, and that site sits inside **`sub_003B1050`, a counter-bounded re-ask loop** whose branch `0x3b10ac` needs nothing but the `jal` at `0x3b1020` to return. The chunk the guest needs is **already the head of the kind-1 queue at `0xd49b14`** — `sub_003E12E0` put it there while dequeuing chunk 0 — and its payload at `0xd49b1c` is the start code E26 located. After the single feed, thread 1 executes **nothing**: 151,020 further log lines, **16** distinct symbols, 4,195 identical timer iterations, and `sub_003DCFC0` — the refill kick — has **zero** entries in the whole 3.6 M-line log. So the one-shot is **host-side**: `nonStreamDeliveries[(mpegAddr << 32) \| 1]`, a `weak_ptr` whose `shared_ptr` is captured by the `waitExternal` resume lambda and moved into the parked thread's own `EeWaitState`. **The token that suppresses the producer is owned by the wait that is waiting for the producer.** E26's mutual-wait reading loses its fourth, unstated leg: this is not two parties waiting on each other, it is one party holding the key to its own door. Eight static-vs-log legs tabled, **zero disagreements**. 19/19 files equal across two pin passes 455 s apart, `MPEG.cpp` equal to its git object, both e26a logs equal to E26's committed pins. 0 boots, 0 lease claims, 0 fork edits/commits/pushes, 0 deletions, 0 amendments, 0 new errata, fix gate **STOP**. |
