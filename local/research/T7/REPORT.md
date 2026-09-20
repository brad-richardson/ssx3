# T7 report — driver-loop (i, N) site examination at 0x36356c: examined-and-absent, emitter work STOPPED per Task 1.1

Brief `local/muse/prompts/T7.md`. Tables, no verdicts. Stale-reading
guard: P1 REPORT Part 31 §P31-6b (the deciding receipt this brief
builds) + `local/research/T1/REPORT.md` (the snapshot emitter style
conventions — extended by zero lines: STOP clause triggered).

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`.
`$R`-relative paths below unless noted. All guest reads read-only
(recompiled-source comments + ELF word reads + existing-trace greps).

Headline readings: `0x36356c` is `lw $s3,0x2A90($gp)` (ELF word
`0x8f932a90`), not a call to `0x362DE8`; the sole JAL to `0x362DE8`
in `sub_00363490` is at `0x3634cc` in straight-line prologue
(once per fresh entry); 12 back-edges in the function, minimum
target `0x3635C0`, none containing a `0x362DE8` call; existing P1ag
trace counts `362DE8:13108` / `363490:39324` / `376938:392030`.
No emitter change, no boots (STOP clause: do not burn boots on it).

## T7-0. Fork / lease / time record

| Item | Value |
|---|---|
| Fork HEAD at T7 start | `a611702ca2135aa02a4acf0d7baf05b352d035df` (= brief base; T5 not yet landed) |
| Fork HEAD at T7 end | `1a76df4614c241b3f22a0baabe79a84671408639` (`Analyzer: treat materialized .text pointers as function entries (T5)`, 2 files, +289/−0, `fork/ssx3` already points at it) |
| T5 landing | Mid-session; recorded, not fought; zero T7 fork changes, nothing to rebase |
| Fork working tree (start) | `M ps2xRecomp/src/lib/elf_parser.cpp`, `M ps2xRuntime/src/runner/register_functions.cpp`, `M ps2xTest/src/ps2_recompiler_tests.cpp` (foreign, untouched) |
| Fork working tree (end) | `M ps2xRuntime/src/runner/register_functions.cpp` only (foreign, untouched) |
| Fork commits by T7 | 0 (STOP before emitter work); fork `git pull/push`: never run |
| Lease `/tmp/ssx3-p-lane-lease` | Absent at every check (start, mid, end); never claimed; no contention with T5 |
| Waits log | `$W/P1/run/t7-waits.log` (2 lines: `start … lease=absent pgrep=1`, `end … no-hold no-boots no-waits`) |
| Boots | 0 of max 2 (STOP clause); `adb`: not used |
| Wall | 2026-09-20 ~05:45–06:10Z (≈25 min active), inside the 4 h box |
| ssx3 HEAD | `daaaa57` (`T7+M22 briefs written`); evidence commit below, no push |

## T7-1. Site disassembly: `sub_00363490` around `0x36356c` (straight-line, no loop)

Source: `ps2xRuntime/src/runner/sub_00363490_0x363490.cpp`
(`// Function: sub_00363490`, `// Address: 0x363490 - 0x363c20`);
ELF cross-check column from `$W/P1/SLUS_207.72`
(file offset = vaddr − `0xFF000`).

| Addr | Word (comment) | Instr | ELF word | Note |
|---|---|---|---|---|
| `0x363550` | `0x8f831384` | `lw $v1,0x1384($gp)` | — | straight-line |
| `0x363554` | `0x24050005` | `addiu $a1,$zero,0x5` | — | |
| `0x363558` | `0xafa30034` | `sw $v1,0x34($sp)` | — | |
| `0x36355c` | `0x8c640000` | `lw $a0,0x0($v1)` | — | |
| `0x363560` | `0xafa40038` | `sw $a0,0x38($sp)` | — | |
| `0x363564` | `0x0c0e3cc0` | `jal func_38F300` | `0x0c0e3cc0` | target `0x38F300`, not `0x362DE8` |
| `0x363568` | `0x0060202d` | `daddu $a0,$v1,$zero` (delay) | `0x0060202d` | |
| `0x36356c` | `0x8f932a90` | `lw $s3,0x2A90($gp)` | `0x8f932a90` | THE SITE: a load, not a call |
| `0x363570` | `0x8e6518f4` | `lw $a1,0x18F4($s3)` | `0x8e6518f4` | |
| `0x363574` | `0x00a0202d` | `daddu $a0,$a1,$zero` | — | |
| `0x363578` | `0x0c0e584a` | `jal func_396128` | — | next call after the site |
| `0x36357c` | `0xafa5003c` | `sw $a1,0x3C($sp)` (delay) | — | |

Branches in `0x363490–0x36356c`: none except the JALs
(`0x3634cc`, `0x363538`, `0x363540`, `0x363548`); first branch
instr is `0x363598 beqz` (forward, → `0x363B08`). No back-edge
in the function targets below `0x3635C0` (§T7-3), so the site
executes exactly once per fresh entry in straight-line flow.

Origin-of-label check (why the brief names `0x36356c`):

| Row | Value |
|---|---|
| P29 reading (`REPORT.md:9805-9806`) | Tick pc `0x36356c` glossed "`sub_00363490+0xdc` — the direct caller of `0x362DE8`" (a wall-clock sample, not a JAL site) |
| P31-2 reading (`REPORT.md:10339`) | Caller row carries "call site `0x36356c` = +0xdc, per P1af ticks" |
| P1ad-era reading (`REPORT.md:9319`) | Caller chain cites `sub_00363490:0x3634cc (a0 passthrough)` — the actual JAL |
| T7 reading | ELF + source agree: no JAL to `0x362DE8` at `0x36356c` (§T7-2) |

## T7-2. JAL inventory in `sub_00363490` (16 JALs; one to `0x362DE8`)

No `jalr`/indirect in the function (comment grep for `jr`/`jalr`:
only `0x363c14 jr $ra`, the return; `dispatchGuestBranch` ×17 =
16 JALs + 1 return). No self-JAL (not recursive).

| # | JAL addr | Target | In a loop? (§T7-3) |
|---|---|---|---|
| 1 | `0x3634cc` | `func_362DE8` | No (straight-line prologue; §T7-3 min target `0x3635C0`) |
| 2 | `0x363538` | `func_364360` | No |
| 3 | `0x363540` | `func_364050` | No |
| 4 | `0x363548` | `func_3666F8` | No |
| 5 | `0x363564` | `func_38F300` | No |
| 6 | `0x363578` | `func_396128` | No |
| 7 | `0x363584` | `func_365F68` | No |
| 8 | `0x3637f0` | `func_363C20` | Yes (loops 5, 6, 12) |
| 9 | `0x363828` | `func_368660` | Yes (loops 5, 6, 12) |
| 10 | `0x3638e0` | `func_36AC00` | Yes (loops 7, 12) |
| 11 | `0x363948` | `func_364360` | Yes (loop 12) |
| 12 | `0x363a18` | `func_36C790` | Yes (loops 9, 12) |
| 13 | `0x363a50` | `func_3904A0` | Yes (loops 10, 12) |
| 14 | `0x363ab8` | `func_364360` | Yes (loop 12) |
| 15 | `0x363bd8` | `func_365FA8` | No |
| 16 | `0x363be4` | `func_38F300` | No |

Prologue JAL detail (`0x3634cc`, ELF-verified):

| Item | Value |
|---|---|
| Word | `0x0c0d8b7a` → JAL target `0x362DE8` |
| Delay slot `0x3634d0` | `0x00e0a82d` `daddu $s5,$a3,$zero` |
| Return addr | `0x3634d4` |
| Branches/returns above it (`0x363490–0x3634cc`) | None (16 straight-line instrs) |
| Back-edge reaching it | None (min back-edge target `0x3635C0`) |
| Executions per fresh entry | Exactly 1 |

## T7-3. Back-edge (loop) inventory in `sub_00363490` (12 loops; none issues `0x362DE8`)

Targets computed as `addr + 4 + (signed_offset << 2)`.

| # | Back-edge | Target | Loop range | Index / step / exit | Bound readable? | JAL to `362DE8` inside? |
|---|---|---|---|---|---|---|
| 1 | `0x363624 bnez $a1` | `0x3635D8` | `0x3635D8–0x363624` | list-walk `$a1=*($a1+0x18)`; `$s2` counts (+1 @`0x363628`); exit `$a1==NULL` | No bound N (pointer-chased) | No (no JAL in range) |
| 2 | `0x363638 bnez $v0` | `0x3635C0` | `0x3635C0–0x363638` | `$v1` from 0 (`0x3635a0`), +1 (`0x3635cc/30`); exit `slt` (`0x363634`) | `lw $v0,0x7CA4($t1)` @`0x36362c`, `$t1=$fp+0x60000` → mem[`$fp+0x67CA4`] (struct/heap field) | No (no JAL in range) |
| 3 | `0x363700 beqz $v0` | `0x3636C0` | `0x3636C0–0x363700` | bisection `($a3+$t0)>>1` (`0x3636c0`); exit `subu/slti 2` | Converging pair, no count N | No |
| 4 | `0x363714 bnez $v0` | `0x363670` | `0x363670–0x363714` | `$a0`=0,1 (`0x363660/6c`); exit `slti 2` | Imm `2` (2 iterations) | No |
| 5 | `0x363880 bnel $s1` | `0x3637E0` | `0x3637E0–0x363880` | — (not enumerated: no `362DE8` call inside) | — | No (JALs `363C20`, `368660`) |
| 6 | `0x363890 bnez $v0` | `0x3637C0` | `0x3637C0–0x363890` | — | — | No (JALs `363C20`, `368660`) |
| 7 | `0x3638f4 bnez $v0` | `0x3638D8` | `0x3638D8–0x3638F4` | — | — | No (JAL `36AC00`) |
| 8 | `0x363974 bgez $v1` | `0x363960` | `0x363960–0x363974` | — | — | No (no JAL in range) |
| 9 | `0x363a2c bnez $v0` | `0x363A10` | `0x363A10–0x363A2C` | — | — | No (JAL `36C790`) |
| 10 | `0x363a64 bnel $v0` | `0x363A48` | `0x363A48–0x363A64` | — | — | No (JAL `3904A0`) |
| 11 | `0x363ae4 bgez $v1` | `0x363AD0` | `0x363AD0–0x363AE4` | — | — | No (no JAL in range) |
| 12 | `0x363b00 bnez $v0` | `0x363768` | `0x363768–0x363B00` | — | — | No (JALs `363C20`/`368660`/`36AC00`/`364360`/`36C790`/`3904A0`) |

Minimum back-edge target `0x3635C0` > `0x36356c` > `0x3634cc`:
no loop contains the site or the prologue JAL.

## T7-4. Examined-and-absent table (STOP trigger: one row per brief requirement)

| # | Brief requirement | Where looked | Reading |
|---|---|---|---|
| 1 | Loop at `0x36356c` issuing `0x362DE8` invocations | §T7-1 disassembly + §T7-3 back-edges | Absent: site is `lw` in straight-line code; no back-edge targets `0x363490–0x3635BF` |
| 2 | Call site `0x36356c` → `0x362DE8` | §T7-2 JAL inventory + ELF words | Absent: sole `362DE8` JAL is `0x3634cc`; label origin is a P29 tick pc (§T7-1) |
| 3 | Index reg/slot at the site | `0x363550–0x36359c` flow | Absent: no induction variable at the site (single-execution load) |
| 4 | Bound reg/slot/imm at the site | Same | Absent: no compare/exit belonging to a loop at the site |
| 5 | Step + exit condition | Same | Absent: no loop to step/exit |
| 6 | Nearest indexed loop (loop 2, `0x3635C0`) as substitute | `0x3635a0–0x363638` | Exists but issues no `0x362DE8` call; bound is mem[`$fp+0x67CA4`] (struct/heap field, not site-constant) |
| 7 | Nearest counting loop (loop 1, list-walk) as substitute | `0x3635D8–0x363624` | Exists but pointer-chased (`exit NULL`), no bound N; no `0x362DE8` call |
| 8 | Indirect/recursive `0x362DE8` issue inside `363490` | `jalr`/`jr`/self-JAL grep | Absent: no `jalr`, no self-JAL; only `jr $ra` return |

STOP action taken: no emitter extension, no unit tests, no fork
changes of any kind, no boots (brief: "do not burn boots on it").
Emitter schema delta: none. BEFORE/AFTER suite: not run (no code
change exists to test). Proof-boot `(i, N)` series: not taken
(no site to sample).

## T7-5. Dynamic cross-check (existing P1ag receipts only; no boot)

Trace `ps2_log-p1ag-1.txt` (1.2 GB, 35,916,072 lines), `grep -c`:

| Function event | Count | Relation |
|---|---|---|
| `sub_00362DE8 enter` | 13,108 | = P31 trace enters exactly |
| `sub_00363490 enter` / `exit` | 39,324 / 39,324 | = 3 × 13,108; balanced |
| `sub_00376938 enter` / `exit` | 392,030 / 392,029 | deficit 1 = live frame at SIGTERM |

Combination table (structure + P31-2 census + counts above):

| Row | Value |
|---|---|
| Every `0x362DE8` enter's parent | `sub_00363490` (P31-2 full-trace indent census: 13,108/13,108, 0 other) |
| `0x362DE8` calls per `363490` frame | ≤1 (sole JAL `0x3634cc` in prologue; no back-edge reaches it) |
| Fresh `363490` frames | 13,108 (= `362DE8` enters 1:1: fresh frames always execute the prologue JAL) |
| Resume `363490` frames | 26,216 (= 2 × fresh; resume re-enters skip the prologue via the `ctx->pc` switch, emitting `enter` without a `362DE8` call) |
| Repetition driver location | Strictly above `sub_00363490` (each logical call issues exactly one `0x362DE8` call) |

## T7-6. P31 baselines carried (not re-proven: STOP = no boot; values cited)

| Baseline (brief) | P31 value | T7 status |
|---|---|---|
| Single caller `sub_00363490` for all `0x362DE8` enters | 13,108/13,108, 0 other (§P31-2) | Carried (no new trace; §T7-5 counts consistent) |
| 20/19/1/2534 per-invocation constancy | Exact inv 75–13106 (§P31-1d) | Carried (no new trace) |
| Stubs 222 | ×54 blocks 5–58 (§P30-3c) | Carried (no new boot) |
| Sema-30 4w/3s parked | §P30-2b | Carried (no new boot) |
| Deviation tabled | — | None observed (nothing re-measured) |

## T7-7. Next-cheapest receipt spec (complete-result remainder)

Cheapest-first; each row names inputs already on disk where they exist.

| Step | Action (read-only unless noted) | Input | Output | Boot/lease cost |
|---|---|---|---|---|
| 1 | Indent-aware attribution: for each of the 13,108 `0x362DE8` enters, record the issuing `376938` frame (depth + ancestry) | Existing `ps2_log-p1ag-1.txt` | Whether the 13,108 repetitions come from `376938` recursion (self-JALs `0x376b5c`/`0x377208`/`0x3778e4`), a loop (14 back-edges, none spanning `0x377b14` in-window), or re-entry from above | 0 boots |
| 2 | Disassemble the issuing edge found in step 1 (same method as §T7-1–3: JAL inventory + back-edge targets + ELF words) | `$W/P1/SLUS_207.72` + `$R/…/runner/sub_*.cpp` | Index/bound operands if a loop; recursion counter/arg if recursion; examined-and-absent if neither | 0 boots |
| 3a | If step 2 yields a loop with a site-readable bound: extend T1 emitter with a `driver_loop[]` section sampling `(i, N)` per `363490` enter (first, not per `362DE8`: 1:1 fresh mapping, §T7-5), gated by `PS2X_DIAG_PARK` write path | T1 emitter files | `(i, N)` series → `N−i` + §P31-1b rate = projection inputs | 1 boot ≤90 s (lease-gated) |
| 3b | If step 2 yields recursion with a depth/arg counter: sample the counter per `363490` enter instead of `(i, N)` | Same | Monotone progress proxy (no total `N`; completion fraction unavailable) | 1 boot ≤90 s (lease-gated) |
| 3c | If steps 1–2 yield no readable bound (likely if driver is the game's outer frame loop): run to phase exit (4th sema-30 signal per §P31-6c) and count total `0x362DE8` enters = empirical `N` | P31-6d 600 s boot shape | `N` empirically; no per-sample `i` | ~10 min lease (P-lane) |
| Alt (inner, different question) | Index/bound hunt in `362DE8`'s own loops (`0x362EB0–0x363188`: back-edges `0x363160`→`0x362F00`, `0x363188`→`0x362EB0`, containing the `394ED0`/`395000` JALs @`0x362f68`/`0x363008`) | Same as step 2 | Per-invocation `(i, N)` (the 20×/19× repetition) — phase progress NOT answered | 0 boots to spec; 1 boot to sample |

## T7-8. Exact commands used

From `/Users/bradrichardson/dev/ssx3` unless noted; `R`, `W` as above.
Guest reads only (`grep`/`sed`/`python3` reads of sources, ELF bytes,
existing trace); no builds, no boots, no fork writes:

```
git rev-parse HEAD; git log --oneline -5; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -8; git -C "$R" status --porcelain=v1
git -C "$R" branch --show-current; git -C "$R" remote -v
cat /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (exit 1)
grep -o "// 0x363..." sub_00363490 file (disassembly comments, JAL + back-edge inventory)
grep -rl "func_363490" $R/ps2xRuntime/src/runner/ (caller census: 376938 only + registry/header)
python3 ELF word reads at 0x3634cc/0x363564/0x363568/0x36356c/0x363570/0x377b14/0x377b18/0x377b1c
grep -c sub_00362DE8/00363490/00376938 enter/exit ps2_log-p1ag-1.txt (13108/39324/39324/392030/392029)
grep JAL/back-edge inventories in sub_00362DE8 + sub_00376938 files
git -C "$R" log --oneline -4 (T5 1a76df4 landed mid-session); show --stat HEAD
printf ... > $W/P1/run/t7-waits.log (2 lines)
(mkdir + write local/research/T7/REPORT.md; this file)
git add -f local/research/T7/REPORT.md
git commit -m "[T7] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T7-9. What I could not do (gap rows)

- Extend the emitter / add unit tests / run BEFORE/AFTER suite:
  STOP clause (§T7-4) — no site exists to sample.
- Take a proof boot / reproduce P31 baselines in a new window:
  STOP clause — boots forbidden when the bound is absent (§T7-6
  carries the baselines instead).
- Attribute the 13,108 repetitions to a specific `376938`
  recursion edge or outer loop: needs the indent-aware trace pass
  (§T7-7 step 1) — specified, not run (outside T7's site-examination
  scope; zero-lease work for the follow-up).
- Identify the inner 20×/19× loop bounds inside `362DE8`:
  scoped as the alternate (§T7-7 alt) — not pursued (answers a
  different question than the phase-level `N`).
- Session wall ≈25 min active, inside the 4 h box.
