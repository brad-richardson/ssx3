| E26 | Receipt |
|---|---|
| Stop point | **All three missions executed; nothing blocked.** The instrument was verified in place (path **(a)**, no rebuild, no restore), the five-pin capture preflight gate passed **5/5 with zero re-pinning**, and E24's designed boot was spent **once**: rc 0, bound `wall` at 75.568 s, lease claimed and released cleanly, 230 watch entries armed. Both X questions are answered with byte receipts. Fix gate: **STOP**, honored as written. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed at open **and** close; `status --short` exactly `?? ps2_log.txt`. Runner `e462e448…67e22` / suite `2152e5ad…f04c0` re-hashed **five times** across the lane (two restore passes × two reads, plus the close) — all equal. Observer dylib `e4d88fdc…b38e6be` reused by copy + re-sha, never rebuilt. The 458-test suite ran **fresh inside the boot driver's own preflight**, green, before the atomic claim. |
| Questions reached | **Objective 1a CLOSED** — the successor descriptor node does **not** move post-park; E23's named residual is closed, not inherited. **X (a) ANSWERED in bytes.** **X (b) ANSWERED and CONFIRMED dynamically**, with the waker `ra` E24 could not obtain. All four of E24's pre-registered branches are **decided**, one of them against its own expectation. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero pushes, zero regeneration, zero builds, zero relinks, zero observer rebuilds, zero deletions. **One title boot (1/1), one lease claim, one lease release.** |
| Next dependency | None blocking. E26 hands over a decided branch set, a refitted cost model that says the residual E24 traded away is **affordable**, and a sharpened X. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-22T13:08:58Z`; deadline `2026-09-22T21:08:58Z`; eight hours. Final audit `2026-09-22T13:27:48Z`. **Actual time used: 18 min 50 s**, well inside the box. |
| Required reads | E26 prompt; E24 REPORT 166 lines + NEXT-BRIEF 38 lines + BOOT-DESIGN 109 lines; E25 REPORT 150 lines; E15 REPORT §no-input; E16 REPORT §closure — all read in full, before the first copy, rename or run. |
| Hypotheses | E24's, carried unchanged and pre-registered in `CONTRACT.md`. **H0** nothing moves post-park · **H1** something does · **H2** signallers for 26/30/31/32 fire post-park · **H3** sema 36's signaller still never runs. E26 pre-registered **nothing new**. |
| Result | **H0 realised. H1 refuted. H2 refuted as stated. H3 confirmed.** |
| Alternatives | (a) silent post-park; (b) moves post-park; (c) the wait resolves upstream and MPEG is symptom; (d) observation fails. **(a) realised** on a watch set 6.2× larger than e23a's. (b) excluded by measurement. (c) neither proven nor excluded — and E26 found the first *structural* thing that speaks to it (below). (d) did not arise. |
| Observable | 6,725 watch emissions across 230 armed addresses; 20,574 parsed `[diag:sema]` lines of 20,597 present; a 3,607,246-line function log; the parser's own closure receipt; the park snapshot; the ISO chunk the CD read delivered. |
| Strict order | Contract → **fork gate (first)** → instrument reuse → hex-safe rename + proof → recorded tooling changes → open/admission → Mission 0 restore + preflight → boot fidelity proof → probe gate → **ONE boot** → Mission 2 mine → cost refit → fix gate → final audit → close. Opened in order; no gate tripped. |
| Fix gate | **STOP.** `fix-gate.json`. |
| Preserved constraints (E18 ABI, BINDING) | Caller-owned synchronous dispatch; word0-only cbData; `v0` discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. **Preserved by construction** — E26 edited no source and built nothing — and by identity: the binary it booted is byte-for-byte the one every E15–E23 receipt was taken on. |
| Contract source | `CONTRACT.md`, written before the first copy, rename or run. **No amendment declared.** Internal reservation 3 GiB (the brief's value), floor 2 GiB + 0.5 GiB guard unchanged; never approached, because E26 runs no build step. |

| **Mission 0 — restore + preflight** | Receipt |
|---|---|
| Machine | The brief anticipated a Mac-mini migration. **It did not happen** — this ran on `brads.macbook.air.lan`, the same host, and `/tmp/e18-mpeg-link` survived intact. Recorded because the brief made it a branch. |
| **Restore path taken** | **(a) VERIFIED IN PLACE.** No rebuild, no share-tier restore. The pins E24 declared lost and E25 reproduced are standing at their exact paths. |
| Two matching reads, separated in time | Pass 1 `13:12:40Z`, pass 2 `13:15:02Z`, **152.1 s apart**; each pass reads every pin **twice back to back**. Four reads per pin, **1 distinct value each**, all equal to the pin. `restore-pass-1.json`, `restore-pass-2.json`, `restore-gate.json`. |
| Independent corroboration | Every pin's SHA also equals the one **E25** measured hours earlier on its own run. The standing SSD rule is satisfied on both halves — repetition in time *and* independent corroboration. |
| Runner / suite | `163,529,696 B` / `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22` · `5,695,128 B` / `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0`. |
| **The five-pin gate, as written** | **5/5 PASS, 0 re-pinned**: runner, suite, ELF (cd) and ELF (P1) both `1b49d05c…7af7bc` at 3,890,784 B, observer dylib `e4d88fdc…b38e6be` at 52,472 B. Run **twice**, at `13:12:40Z` and `13:15:02Z`; the two passes' gate rows are **identical**. `readiness-pass-1.json`, `readiness-pass-2.json`. |
| ISO | Size only — 3,005,415,424 B — **exactly as E24's designed preflight checks it**. Hashing 3 GB over the flaky USB link is not a gate this boot needs, and inventing one would not have been fidelity. |
| `PS2X_DIAG_SEMA` | Present in `EeScheduler.cpp` at `3adc0478` (4 occurrences, `_S0` 2) **and compiled into the runner that was booted** (strings: `PS2X_DIAG_SEMA` ×3, `_S0` ×1, `PS2X_DIAG_PERIOD_MS` ×2). |
| Boot argv paths | Both exist: `/tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner` and `…/P1/cd/SLUS_207.72`. |
| SSD link | Mounted and stable throughout; re-checked at open, at both restore passes and at close. It never disappeared, so the brief's table-and-stop rule was never triggered. |
| Posture at open | Lease absent, `pgrep -x ps2EntryRunner` rc 1, no `boot-attempt.json`. |

| **Boot fidelity — proved, not asserted** | Receipt |
|---|---|
| Why a proof exists | The brief requires E24's boot "**EXACTLY as designed** (argv, environment, 230-entry watch-set + tiers, capture window, teardown)". E26 measures each of those five rather than claiming them. `boot-fidelity.json`, **14/14 green**. |
| Driver identity | E24's `e24_capture.py`, put through the **same** hex-safe rename, equals E26's driver **byte for byte** (18,158 B → 18,158 B). Nothing in the boot path was edited. |
| Watch set | `watch-set.json` **SHA-equal** to E24's (`a37a5eb0…945204`), copied verbatim, never regenerated. Tiers 64 / 32 / 37 / 16 / 16 / 32 = 197, each declaring the entry count it carries. |
| Full vector | **230 addresses, no duplicates** = 197 tiered + 4 carried producer singles + 29 carried non-producer — E24's 230 against e23a's 37. Compared **element for element, in order**, against E24's own module. Equal. |
| Capture window | `CAPS` and `ALLOCATED_CAPS` **identical** dicts: wall 90 s, SIGTERM reserve 15 s, boot log 256 MiB, trace 96 MiB, function log 1024 MiB, aggregate 1536 MiB. So exactly one variable changes against e23a. |
| argv / lease / teardown | argv identical; lease path identical (`/tmp/ssx3-p-lane-lease`, the one P-lane lease every prior lane shares); teardown unchanged. |
| **The one declared difference — the label** | E24 designed the boot as `e24a` and did not spend it. E26 spends it as **`e26a`**, by the same mechanical rename that carried E23's driver into E24 and E24's tooling into E25. **Declared in `CONTRACT.md` before the run, not discovered in the report.** Six environment values are label-derived output *destinations* (`PS2X_DIAG_PARK_DIR`, `PS2X_TRACE_SYSCALLS`, `PS2X_E4_DIR`, `PS2X_E21_PARSER_DIR`, `PS2X_E7_DIR`, `PS2X_FRAME_DUMP_DIR`); every other key and value is identical. e22a and e23a already differed in exactly this way, and the rename is what keeps the driver's refuse-to-overwrite asserts meaningful and this lane's SSD byte accounting honest. |

| **Mission 1 — the boot, spent once** | Receipt |
|---|---|
| Authorization | `e26_prepare_probe.py` green; `entry-preflight.json` + `e26a-build.json` written. The driver's own preflight then ran for real: presence gate on six paths, hex-safe five-pin hash gate, `pgrep` before **and** after, fresh T13 pre-claims, the aligner selftest (`ALL PASS`), and the **full 458-test suite fresh, rc 0, Failed: 0**. |
| Lease | Atomic claim `13:16:16.336019Z` (`LEASE.open('x')`); boot **5.615 ms** later. Released `13:17:31.911657Z`, **8.042 ms** after process end. Post-release `pgrep` rc 1, lease absent. `e26-waits.log` carries the CLAIM and RELEASE lines. |
| Execution | PID 46217. **rc 0**, bound **`wall`** at 75.194 s, total elapsed **75.568 s**, **no SIGKILL**. `watch_entries=230`. |
| **span-complete** | **9.5236 s** — recorded on every path by E24's CHANGE 4, which is why the cost model can be refit below. |
| Fate | The title reached the same terminal state as e23a: MPEG `GetPicture` fed one chunk and parked; the run then continued for **65.0 s** and **24,463 further boot-log lines** without the feed advancing. |
| Byte caps | boot log 13,315,314 B (cap 256 MiB) · trace 3,441,894 (96 MiB) · function log 127,058,902 (1024 MiB) · **aggregate 153,585,570 logical / 219,152,384 allocated** against 1536 MiB. Every per-path and aggregate bound satisfied; the only bound that fired was `wall`, by design. |
| Capture pins | `boot-e26a-1.log` `c9ddf91a…78e33e5` · `ps2_log-e26a-1.txt` `d849775b…cf1024ec` · `syscalls-e26a-on.txt` `28b26b19…0922b1b4` · `parser-input.bin` `cde8a830…2a1c875a`. `observed/e26a-capture-sha256.txt`. |
| **The feed reproduces exactly** | The parser received **5,040 B, SHA256 `cde8a830…2a1c875a`, FNV64 `0xd2a9588f0e0fd358`, first4 `000001b3`** — byte-identical to E22's, E23's and E24's retained copies. `parseCalls=1 offered=5040 consumed=5040 packets=0 frames=0 errors=0 pending=0`. A **third** independent reproduction, on a fresh boot. |

| **The watch-set ledger — every one of the 230 entries** | Entries | Hit | Emissions | Pre-park | **Post-park** |
|---|---:|---:|---:|---:|---:|
| descriptor node array `0x548800`-`0x5489ff` | 64 | 11 | 27 | 27 | **0** |
| data region head `0xd48748`-`0xd48847` | 32 | 0 | 0 | 0 | **0** |
| data region body sample `0xd48848`-`0xd49a73` | 37 | 7 | 7 | 7 | **0** |
| data region tail `0xd49a74`-`0xd49af3` | 16 | 1 | 1 | 1 | **0** |
| past-end extension `0xd49af4`-`0xd49b73` | 16 | 1 | 1 | 1 | **0** |
| staging buffer `0xdc8340`-`0xdc843f` | 32 | 32 | 68 | 68 | **0** |
| carried producer singles | 4 | 4 | 18 | 18 | **0** |
| carried non-producer | 29 | 27 | 7,233 | 7,233 | **0** |
| **total** | **230** | **83** | **7,355** | **7,355** | **0** |

| Ledger qualifications, stated not buried | Receipt |
|---|---|
| Hits vs emissions | 6,725 emissions produce 7,355 per-entry hits because a **16-byte store can overlap two adjacent 8-byte windows**. Both numbers are real; neither is inflated. |
| **Last emission** | Boot-log line **22,786** — *four lines before the park at 22,790*. The run then produced **24,463 more lines over 65 s with not one watch emission.** |
| Torn lines | **10** of 6,735 `[diag:watch]` lines were interleaved with a concurrent `[frame:*]` / `INFO: FILEIO` write on the same fd and could not be parsed strictly. **All 10 are pre-park and all 10 land in the carried non-producer tier** — none in the descriptor array, data region, past-end extension or staging buffer. Counted and located, not dropped silently. `watch-ledger.json` → `torn_lines`. |

| **Objective 1a — E23's named residual. CLOSED.** | Receipt |
|---|---|
| The question | Does the **successor** descriptor node at `0x548880` move post-park? E23 saw the head advance `0x548800 = 0x548880` and had **not watched** the successor, so its silence was vacuous. |
| The measurement | `0x548880` has **exactly one write in the entire run**: boot-log line **96**, value `0x5488c0`, `pc=0x3201a8 thread=1`. That is the boot-time free-list initialisation. **Post-park hits: 0.** |
| The head advance, reproduced | Line **22,786**: `addr=0x548800 value=0x548880 pc=0x3204c4 ra=0x319ffc thread=1` — E23's exact observation, on a fresh boot. |
| **Bonus: the tier is bigger than E24 sized it for** | Lines 93–101 show the array initialised as a **linked free list at `0x40` stride** (`0x5487c0 → 0x548800 → 0x548840 → 0x548880 → … → 0x548a00`), not the `0x80` E24 assumed. The 64-entry tier therefore covers **eight** nodes, not four. The coverage is **better** than designed. |
| **Verdict** | **H0.** The successor node does not move. E23's KILLED verdict **survives a watch set 6.2× larger** that now covers the whole node array, both buffers and the bytes past the delivered region. The residual E23 named is **closed by measurement**, not inherited. |

| **Mission 2 (a) — the final start code, in bytes and in time** | Receipt |
|---|---|
| The question | Where does the guest's final start-code write land relative to the feed the parser consumed? |
| **The answer** | **The guest never writes a terminating start code at all — and it does not have to. The start code was already sitting in guest RAM, 48 bytes past the end of the data the guest fed, delivered by the *same* CD read.** |
| Start-code-valued writes | **0** of 6,725 watch emissions carry a `000001` prefix. Not one. |
| How the feed actually arrives | Boot-log line **22,336**: `sceCdRead lbn=0x13ba33 sectors=16 buf=0xd48740` — **32,768 B of host-side CD DMA straight into guest RAM**. Line 22,338 gives the first eight bytes: `4d504368 ac130000` = magic **`MPCh`**, length **5,036**. |
| The chunk format, derived | Length field = **total chunk bytes including the 8-byte header**, confirmed on five consecutive chunks (`MPCh` 5036 → `SCHl` 40 → `MPCh` 14364 → `SCCl` 12 → `MPCh` 5732). ISO read **twice**, both reads equal, per the standing SSD rule. `chunk-map.json`. |
| What the guest fed, to the byte | ES payload = 5,036 − 8 = **5,028 B**, padded with **12 zero bytes** to **5,040** — the next 16-byte multiple. `fed[:5028] == ES payload` **true**; `fed[5028:]` all zero **true**; last non-zero byte at offset **5,024**. **That is E24's measurement exactly** — E24 read 15 zero bytes to offset 5,039, which is the ES payload's own three trailing zeros plus these twelve. Two lanes, two methods, same bytes. |
| **Where the terminating start code is** | The **next** `MPCh` chunk begins at blob offset 5,076 → guest **`0xd49b14`**; its ES payload begins at guest **`0xd49b1c`** and its first four bytes are **`00 00 01 00`** — a picture start code. It is **48 bytes past the end of the fed data**, **inside the same 32,768 B already in RAM**, and it sits **inside E24's past-end extension tier** (`0xd49af4`-`0xd49b73`, 16 entries at stride 8, complete byte cover). **E24 chose that tier for exactly this and aimed it correctly.** |
| **The guest had already walked to it** | Lines **22,351** and **22,354** — *before* the feed — thread 1 stores `0x02000028` at `0xd49af0` and `0x0100381c` at `0xd49b18`. Those two addresses are the **length fields** of the `SCHl` chunk (total 40 = `0x28`) and of the **next `MPCh`** chunk (total 14,364 = `0x381c`). The low 24 bits are the lengths the ISO already holds; only the top byte changes (`0x02`, `0x01`). The guest had parsed the chunk list past the picture it was about to feed. |
| Timing | Last guest write to any watched address: line 22,786. Feed: 22,788 (`feedES #0 size=5040 first4=000001b3`), parsed 22,789 (`inSize=5040 parsed=5040 packets=0 newFrames=0`). Park: 22,790. **Then 65.0 s and 24,463 lines of nothing.** `parse-enter` at 9.485 s, parser `_Exit` at 74.466 s, one parse call between them. |
| **Named limit** | `diagWatchEmit` fires on **guest stores only**. The picture payload arrives by host CD DMA (only 7 of the 37 body stride samples ever emit, all from one 128-bit guest copy loop), so "no start-code-valued write" is a statement about guest stores, not about every byte reaching the buffer. **It does not weaken the post-park result**: the descriptor writes *are* guest stores and are fully visible, and the past-end tier covers the start code's own address byte for byte. |
| **The reading, tabled not acted on** | E23 measured — and E24 and E25 re-confirmed — that the producer fires **exactly once per `GetPicture`** on every path. One `GetPicture` therefore feeds exactly one chunk, and `GetPicture` does not return until a frame appears. The host parser cannot emit a frame until it sees the next start code, and that start code is in the chunk the *next* feed would carry. **That is a mutual wait.** It is consistent with every measurement in this capture; it is a reading, and the fix gate is STOP. |
| What this capture cannot settle | Whether the title would ever re-ask given more wall time. This boot **bounds** it at 65 s of total silence after the park. A bound is not a proof of never. |

| **Mission 2 (b) — semaphore 36's sole signaller** | Receipt |
|---|---|
| The question | Does semaphore 36's only signaller appear anywhere in the capture? |
| **The answer** | **No — and this is now a dynamic result, not a static one.** |
| Sema 36 in the whole run | **Exactly one `[diag:sema]` line** of the 20,574 parsed (20,597 present): the **wait**, at boot-log line 5,917, `waker=6 parked=1 waiters=0->1 result=park`. **Signals: 0.** Raw `grep` agrees with the parser, and **no torn line mentions id 36**, so the count does not depend on the regex. |
| **The `ra` E24 could not get** | The observed waiter `ra` is **`0x3c19f0`** — **exactly** the return address E24's static 4-instruction closure predicted from `0x3c19ec lw $a0` → `WaitSema`. The always-on park tally could only record the syscall **stub** pc (`0x423de8`); `PS2X_DIAG_SEMA` names the caller. **Objective 2's missing half, delivered.** |
| The signaller | `sub_003C1298` (owns `0x3c15c0 lw $a0` → `iSignalSema`, the **unique** signaller across all 9,457 generated sources) has **0 entries** in the **3,607,246-line** function log. The delete path `sub_003C2268` and the create-store owner `sub_003C1E00` likewise **0**. |
| **Verdict** | E24's static enumeration is **confirmed dynamically on a second, independent boot**. The only code that can ever wake thread 6 never executed. |
| **New — the first structural link between the two chains** | The WaitSema(36) owner `sub_003C1980` runs **4,379 times**, and the `[diag:dormant]` trace taken **at the MPEG park** (line 22,792) ends: `… 0x402a10 GetPicture → 0x3b0b10 guest callback → 0x3b0b40 helper → 0x3b06b0 source → … → 0x4029d0 AddBs → 0x3e4db8 → 0x3825c0 → 0x3825f8 → 0x3c1980`. E24 recorded that **nothing** in the retained evidence linked the MPEG chain and the semaphore-36 chain in either direction. This capture puts the function that **owns** the WaitSema(36) site on the MPEG delivery path, entered immediately after `AddBs`. |
| **What that does NOT show** | That the sema-36 **branch** is on that path. Thread 6 was scheduled once and waited once; thread 1 entered the owner without ever reaching `0x3c19ec`. The two chains share a **function**, which is weaker than sharing a **dependency**. E26 does not upgrade it, and the next lane should not either without its own measurement. |

| **E24's four pre-registered branches, all decided** | Outcome |
|---|---|
| "Successor node, data region, past-end and staging buffer **all silent** after the park" | **REALISED.** 0 post-park emissions across all 230 entries. The demand edge stays closed; X stays upstream; E23's named residual is closed rather than inherited. |
| "**Any** of them moves after the park" | **REFUTED** by measurement. |
| "`[diag:sema]` shows a signaller for 26/30/31/32 firing post-park → those four are live idle workers" | **REFUTED AS STATED, and it is the more interesting outcome.** Post-park, the **only** semaphore with any activity at all is **31**: **4,192** waits (all `waker=4`) and **4,188** signals (all `waker=-1`, interrupt context, every one of the id's 4,396 signals from `ra=0x31abf8`). Semaphores **26, 30, 32 and 36 do nothing post-park**, and **thread 1 performs zero semaphore operations post-park**. The guest does not idle-tick; it goes **silent except for one interrupt-driven timer loop** — which is E24's objective 1b, now confirmed dynamically with the caller `ra`. |
| "`[diag:sema]` shows `sub_003C1298`/`0x3c15c0` still never reached" | **CONFIRMED**, over a longer window and with the `ra`. The second stuck chain is independent of MPEG and is its own X. |

| **The cost model, refit with its third point** | Receipt |
|---|---|
| Why this is not a new question | E24's CHANGE 4 exists precisely so the driver records span-complete on **every** path "so the next lane can refit". This is a designed deliverable, not new pre-registration. |
| The three points | e22a 29 watches → 7.61 s · e23a 37 → 8.30 s · **e26a 230 → 9.524 s**. |
| The old two-point fit | `k = 0.0863 s/entry`, `base = 5.11 s`, predicting **24.9 s** at 230 entries. |
| **Measured** | **9.524 s. The model over-predicted by 15.4 s — a factor of 2.6.** |
| The real slope | 193 extra entries cost **1.22 s** → **0.0063 s/entry**, **14× shallower** than the e22a→e23a pair implied. That pair differed by only **8** entries, so its slope was dominated by run-to-run variation, not by watch count. Three-point least squares: `k = 0.00806`, `base = 7.683 s`. |
| **Consequence for the residual E24 declared** | E24 traded away "an isolated write shorter than 121 B inside the sampled body span" to buy scan budget **that was not actually being spent**. On this measurement a **full 630-entry 8-byte cover** of the body costs about **12.8 s** of span-complete, not the ~64 s the old model predicted, and would leave roughly **65 s** of post-park window. **A later lane that wants that residual closed can afford it.** E26 does not re-spend a boot to prove that; it tables the number. |
| Caveat | Three points is still a small fit, and the driver keeps recording span-complete on every path. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | **3 GiB** declared in `CONTRACT.md` before the first action; floor 2 GiB + 0.5 GiB guard unchanged. |
| SSD reservation | 16 GiB in NEW `e26-*` paths; same floor + guard. |
| Initial admission | `13:09Z`: internal 4,767,924,224 B free (4,138,246,144 required) / SSD 139,890,524,160 B free (19,864,223,744 required). Both fit. |
| Final audit | Internal owned **1,767,751,680 B** of 3,221,225,472 reserved, free **4,580,569,088**; SSD owned **227,540,992 B** of 17,179,869,184 reserved, free **139,149,180,928**; **fork growth 0**, measured against a 1,549-path baseline taken at open. Every cap within bounds, both floors clear, no bound tripped. |
| Note on `internal_allocated` | It is dominated by the 1.77 GB E18 build tree E25 rebuilt bit-identically. **E26 runs no build step**, so the 3 GiB reservation is declared and not consumed. |
| Accounting | `st_blocks × 512`, incl. ExFAT directory/AppleDouble allocation; `COPYFILE_DISABLE=1` on every SSD step. **No reclaim, no deletion.** |
| Boot cap utilisation | **1/1 title boots, 1/1 lease claims.** Aggregate 153,585,570 B logical / 219,152,384 B allocated against a 1536 MiB cap. |

| Tooling provenance | Receipt |
|---|---|
| Hex-safe rename (11 files, **two source lanes**) | From **E25**: `io · closed_events · parser_receipt · mine · validate · bounded · instrument · tail · fork_gate · e26_readiness`. From **E24**: `capture · prepare_probe`. Normalized diff **byte-empty for all eleven**; every hex run byte-equal; every protected token count preserved. `rename-proof-hexsafe.json`. |
| Why two lanes | E25 is the most recent carrier and is the lane that **reverted** E24's three suite-presence CHANGE blocks once the suite binary existed again. But E25 created **no capture driver at all**, so the boot driver and its probe gate must come from E24. Each file names its own source lane and the proof normalizes against that lane's token. |
| Errata E23-E1 honoured | Runs of ≥16 hex characters are masked **before** renaming, so a digest cannot be rewritten; hex-run equality is asserted afterwards. `ELF_SHA` came through byte-identical. |
| Protected tokens | The five E21 instrument tokens; `e23-fixtures/complete` and its footer; `e18-fixtures/after` and `/tmp/e18-mpeg-link/runtime`. **E26 adds** `P1/e25-snapshot` and `e18-mpeg-link.tar` — E25-spelled by necessity, being real paths on the SSD rather than lane tokens. |
| `e26_common.py` | Written fresh, not renamed: internal reservation 3 GiB; `NEWB = B0` with a comment saying E26 **builds nothing**; `sample()` globs `e26-*` and `*e26*` so the boot's own artifacts are charged to this lane. |
| Intentional changes (2, both recorded, both idempotent) | Both in `e26_prepare_probe.py`. **CHANGE 1** points the regression gate at **E25's** receipts instead of E24's: E24's are red *by construction* — taken when the runner did not exist, so E24 never wrote a `checkpoint-complete.json`, `cadence.json` or `observer-regression.json` at all. E25 re-ran that identical chain green on byte-identical binaries and the orchestrator gated it. **Not one assertion is removed, softened or skipped** — only the directory they read from moves, and every one was verified to hold before the change was written. **CHANGE 2** records that provenance inside the manifests so a later reader cannot mistake an inherited receipt for one E26 took itself. The driver's own preflight still runs the **full 458-test suite fresh** before the atomic claim. `tooling-changes.json`, `tooling-diff.md`. |
| Carried `CHANGE` comments | The `E26 CHANGE 1..4` comments inside `e26_capture.py` are **E24's**, renamed mechanically. They describe E24's design decisions, not E26's. Named here so the rename cannot be misread as authorship. |
| New files | `e26_common.py`, `e26_rename.py`, `e26_patch.py`, `e26_open.py`, `e26_restore.py`, `e26_restore_gate.py`, `e26_boot_fidelity.py`, `e26_xlight.py`, `e26_fixgate.py`, `e26_close.py`. |
| `stdbuf` in E26 | Present only as the forbidding assertion inside the driver and as the `stdbuf_free: true` receipt field in `e26a-config.json`. Absent from the boot argv. |

| Fix gate | Receipt |
|---|---|
| Demonstrated edges | **Four.** (1) The terminating start code is already in guest RAM 48 B past the fed data, at `0xd49b1c`, from the same CD read. (2) Nothing in the 230-entry watch set moves after the park — 0 of 6,725 emissions. (3) Semaphore 36's sole signaller never runs, now confirmed dynamically with the waker `ra`. (4) E23's named residual — the successor descriptor node — is closed. |
| Isolated to ONE edge? | **No.** Four edges, and they are not the same edge: two concern the MPEG feed, one concerns a semaphore chain with no proven dependency on it, and one closes a prior lane's residual. A fix needs exactly one edge plus its own fail-before and full regression; E26 has none of those and was not asked to build them. |
| Gate decision | **STOP.** Diagnose and table, never patch. `fix-gate.json`. |
| Candidates still KILLED | C2a and C4 (E23); C1, C3, C5–C9 (E22). E26 re-confirms the reference they were killed against **by identity** — the runner it booted *is* the binary E23 booted — and re-proposes none of them. |
| **X, sharpened again** | E22 called the deficit "not computable from this run". E24 computed it from retained bytes: **one missing start code, not thousands of bytes**. E26 locates that start code: **it is already in RAM, 48 bytes away, in a chunk whose header the guest had already walked to and tagged.** X becomes: *why does the guest stop one **chunk** short of feeding, when the chunk it needs is already resident and already parsed?* — and, still separately, why semaphore 36's only signaller never runs. |
| Mutations | Zero fork source edits, zero fork commits, zero pushes. Diagnosis-only. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=…/E26`. |
| Gate 1 (**first**) | `python3 -B local/research/E26/e26_fork_gate.py` → `fork-gate.json`, **green**. |
| Rename / instrument / patch | `python3 local/research/E26/e26_rename.py E25:…:… E24:…:…` (11 files) → `rename-proof-hexsafe.json`; `… e26_instrument.py` → `instrument-reuse.json`; `… e26_patch.py` (run twice, second run a no-op) → `tooling-changes.json`, `tooling-diff.md`. |
| Open | `… e26_open.py` → `fork-allocation-before.json`, `admission-open.json`. |
| Mission 0 | `… e26_restore.py 1`; `… e26_readiness.py` (→ `readiness-pass-1.json`); `… e26_restore.py 2`; `… e26_readiness.py` (→ `readiness-pass-2.json`); `… e26_restore_gate.py` → `restore-gate.json`, **green**. |
| Fidelity | `… e26_boot_fidelity.py` → `boot-fidelity.json`, **14/14**. |
| Boot gate | `… e26_prepare_probe.py` → `entry-preflight.json`, `e26a-build.json`. |
| **The boot** | `python3 -B local/research/E26/e26_capture.py a --report-all` → `e26a-config.json`, `e26a-preflight.json`, `e26a-preclaim-suite.json/.txt`, `boot-attempt.json`, `e26a-liveness.txt`, `e26a-result.json`. |
| Mission 2 | `… e26_xlight.py` → `watch-ledger.json`, `objective-1a.json`, `x-a-startcode.json`, `x-b-sema36.json`, `sema-ledger.json`, `chunk-map.json`. |
| Fix gate / close | `… e26_fixgate.py` → `fix-gate.json`; `… e26_close.py` → `cost-model-refit.json`, `final-audit.json`, **14/14 green**. |
| Never executed | Any fork edit, commit or push; any regeneration or CSV work; any build, configure, relink or observer rebuild; **any second title boot or second lease claim**; `stdbuf` in any argv; any deletion or reclaim. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Contract; fork gate; instrument reuse; rename/hex/protected-token proof; tooling changes with full diffs; open admission and fork-allocation baseline; two restore passes and the restore gate; two readiness passes; the 14-check boot-fidelity proof; the probe gate manifests; the boot config, preflight, preclaim suite, liveness and result; the 230-entry watch ledger; objective 1a; both X receipts; the semaphore ledger; the chunk map; the cost-model refit; fix gate; final audit. |
| Retained text (`observed/`) | `e26a-parser-events.txt` (with its real `# E21 PARSER CLOSURE` footer), `e26a-park-snapshot.txt`, `e26-waits.log`, three boot-log excerpts (free-list init, the CD read + chunk walk, the feed and park), `e26a-sema36.txt`, and `e26a-capture-sha256.txt` pinning all four capture artifacts. |
| **Evidence is text-only** | The one binary in the tree is the **reused** E21 observer dylib (52,472 B), carried by `cp -p` + re-sha exactly as E22–E25 carried it, because the driver loads it by path. The 5,040 B vector is **not duplicated**: it is byte-identical to E24's retained `observed/parser-input.bin` (`cde8a830…2a1c875a`) and is referenced by SHA instead. |
| `.suite-*` scratch | `.suite-e26a-preclaim` created by the driver's preflight and retained on disk, **left unstaged**, matching E23's and E25's convention. |
| Tail qualification | Every bounded tool, receipt and mine ends with its real `TAIL COMPLETE` footer; counts re-verified, never appended. |
| Errata carried | **E21-E1, E23-E1, E23-E2, E24-E1, E24-E2, E24-E3 carried forward unchanged and not re-fixed.** E24-E2 is honoured operationally: the tail receipt below is recomputed **after** the last edit and its row lies outside the hashed prefix. **E26 adds no errata.** |
| Publication | `[E26]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Scope: E26 evidence only; no fork files, no generated sources. **Not pushed** — the orchestrator pushes at poll. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–180; 32414 B; SHA256 `f0fcda07d8d09f622a0c663b8c32ec6dd6aaf4b21beac2453671b9672220e3d7` (the prefix is every line ABOVE the `| Tail receipt | Value |` header, so this row lives after the boundary and cannot invalidate itself — errata E24-E2) |
| Source-tail gap | **None, and two named limits.** Every E26 capture carries its real footer. The limits are stated where they bite, not in a footnote: (1) `diagWatchEmit` sees **guest stores only**, so "no start-code-valued write" bounds guest stores, not host CD DMA — which is why the payload's arrival is evidenced from the CD read and the ISO rather than from the watch set; (2) the sema and watch tallies carry 23 and 10 torn lines respectively from concurrent writes on the same fd, all located, none post-park in the watch case and none touching id 36 in the sema case. Neither limit touches the post-park result, which is a count of **zero**. |
| E26 REPORT TAIL COMPLETE | The instrument was verified in place, the five-pin gate passed 5/5 with zero re-pinning, and E24's designed boot was spent **once** — rc 0, `wall` at 75.568 s, 230 watch entries, lease released 8 ms after exit, **1/1**. The driver was proved byte-identical to E24's under the mechanical rename before it ever claimed the lease. **Post-park, all 230 watched addresses are silent: 0 of 6,725 emissions, the last one four lines before the park, with 65 s and 24,463 log lines still to run.** E23's named residual is **closed** — the successor node's only write in the whole run is the boot-time free-list init. The feed reproduces byte-for-byte a third time (`cde8a830…2a1c875a`, `packets=0`). X (a) is answered in bytes: the guest writes **no** terminating start code because it does not need to — the code `00 00 01 00` is already in guest RAM at **`0xd49b1c`**, **48 B** past the fed data, inside the same 32,768 B CD read, in an `MPCh` chunk whose header the guest had **already walked to and tagged**; the guest stops one **chunk** short of feeding, not one start code short of writing. X (b) is confirmed dynamically: semaphore 36 has **one** event in the whole run — the wait, at the `ra` E24's static closure predicted — and its unique signaller has **zero** entries in 3.6 M function-log lines. E24's cost model over-predicted by 2.6×, so the residual it traded away is **affordable** for a later lane. 1 boot, 1 lease claim, 0 fork edits/commits/pushes, 0 deletions, 0 amendments, 0 new errata. |
