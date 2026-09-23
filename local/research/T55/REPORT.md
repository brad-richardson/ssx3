# T55 REPORT — PCSX2: inputs and hash of `func_394ED0` calls from `0x362f68` (healthy side of E43)

Brief `local/muse/prompts/T55.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T54/REPORT.md`.

## T55-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Log-only hook at `jal func_394ED0` @`0x362f68` (call inputs, hash, ret, stores flag) on T54's clone, EE interp | DONE — Interpreter.cpp only: JAL call-site + execI func-entry/return/store-cluster hooks, all anchors first try (one placement fix, no new build round-trip beyond the rebuild) |
| 2 | Builds ≤1 | 2 invocations: b1 compile error (decl after use) + decl-move fix, b2 clean. Reported as overrun in §T55-7.5 |
| 3 | Preservation (G13 replay 7/7 + HWSTAT, zero T55 lines) | DONE |
| 4 | Capture: ~5 settled vsyncs of per-call lines | DONE — 1 capture, 8192 h394 over vsyncs 0–36 (cap), vsyncs 0–4 full (5×224) |
| 5 | Per-call table | DONE — §T55-4/5 + `t55-trace.txt` (all 8192 calls) |
| 6 | Receipts + `[T55]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **at SC settled, `sub_00362DE8` calls
`func_394ED0` (tgt always `0x394ed0`) exactly 224×/vsync = 2 passes over a
112-item table at `0x70000000–0x70003780` (stride `0x80`), `a0=0x8095f0`
constant. Pass 1 consumes each item in place (`w0/w2/w3` rewritten, record
written, `stores=1` on first-of-tuple); pass 2 re-walks the consumed items
(`stores=0` except one row). Even/odd vsyncs form 2 exact classes differing
in only 11 rows — the `w0=0x1b0` items whose `w3` ping-pongs
(`0x6efd00`/`0x623080` family) — and the returned record slot is identical
across parity for all 112 items while the hash follows `w3`.** The two
mode-6 records (`0x85aabc`, `0x85abac`) are returned for items
`0x70000000`/`0x70000500` every vsync with `stores=1`.

## T55-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T54-end working tree + T55 hook below |
| T55 binaries SHAs | qt `74344614…0509`, gsrunner `01a01509…f34cb` (full SHAs in build log §T55-8) |
| Patch | `t55-patch.diff` 4,312 B sha256 `e887d4c9…b2b38fa` (diff of `pcsx2/Interpreter.cpp` vs HEAD; carries T48–T55 hunks, 6 `T55` marker lines) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t50` (interp, `EnableEE=false`); state `t50-sc-state` (T50 SC-settled F1) |
| Capture | CWINDOW 524, TARGET 530 PATHS seen, `h394` 8192, `T55_CAP` 1 (@vsync 36), `ctag` 3606; LOADED 1.6037/46; F8 `t55a-shot-sc.png`; trace `t55-trace.txt` 1,106,959 B sha256 `06ce9b8a…7f201f64` |
| Poll log | `t55a-poll.log` |

Builds: b1 fail (compile) + b2 clean (1 TU + 2 links). Captures: 1/2, no
infra kills (foreground held-ssh recipe from T51 §T51-6 held). Bytesize new
bytes ≈ 50 MB of 2 GB (44 MB emulog dominates; `t55stage/` scripts).

## T55-2. The patch

`t55-hook.py` (validate-all-then-write, idempotent) + `t55-fix.py`
(decl-move, §T55-7.5), all in `pcsx2/Interpreter.cpp`:

| Hook | Anchor | What |
| --- | --- | --- |
| T55 decl | `static void execI()` (×1) | `t55_call/enter/mark/ret` + pending/incall state, snapshot regs, 8192-line cap (`T55_CAP`) |
| T55 call-site | T54 census line in `JAL()` (×1) | `if (cpuRegs.pc == 0x362f6c) t55_call(_JumpTarget_)` — jal @`0x362f68`, arms pending (snapshot deferred to func entry so delay-slot arg setup is included) |
| T55 entry/ret/stores | execI `CommitClearSkipFirst…pc` block (×1) | `pc == 0x394ed0 → t55_enter()` (snapshot a0/a1/a2, `memRead32(s1+0/4/8/12)`); `pc in 0x394fdc–0x394fe8 → t55_mark()`; `pc == 0x362f70 → t55_ret()` (log v0) |

Line format: `h394 vsync=<n> tgt=0x<> a0=0x<> s1=0x<> w0=… w1=… w2=…
w3=… hash=0x<a2 & 0xff> ret=0x<v0> stores=<0|1>` (`tgt`/`a0` are extra vs
the brief: they validate the call target and the s6 input).

## T55-3. Preservation

G13 rich-dump replay on the T55 gsrunner: **7/7 PNG md5s match the T48 pins
exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`), HWSTAT
exact (791/37/0/14/320/6), zero `h394`/`T55_CAP` lines (gsrunner runs no EE).

## T55-4. Per-call table (vsyncs 0–4, settled; full 8192 calls in trace)

224 calls every full vsync (36/36 vsyncs 0–35; vsync 36 partial 128 = cap).
`tgt=0x394ed0` on all 8192 calls; `a0=0x8095f0` constant. Two passes/vsync
over the same 112 `s1` (`0x70000000+i*0x80`, i=0..111), same order.

Mode-6 items (pass 1; the 11 rows that differ even-vs-odd — w3/hash only,
ret identical):

| s1 | w0 | w1 | w2 | w3 even (vsync 0) | hash even | w3 odd (vsync 1) | hash odd | ret (both) | stores |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0x70000000 | 0x1b0 | 0x814884 | 0x2a0 | 0x6efd00 | 0x56 | 0x623080 | 0x9d | 0x85aabc | 1 |
| 0x70000080 | 0x1b0 | 0xb5c616 | 0x6ea0 | 0x6efd00 | 0xa3 | 0x623080 | 0x1d | 0x85aad4 | 1 |
| 0x70000100 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f29f0 | 0x24 | 0x625d70 | 0xfe | 0x85aaec | 1 |
| 0x70000180 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f2b50 | 0x86 | 0x625ed0 | 0x50 | 0x85ab04 | 1 |
| 0x70000200 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f2d10 | 0xd9 | 0x626090 | 0xf7 | 0x85ab1c | 1 |
| 0x70000280 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f3a70 | 0xca | 0x626df0 | 0x8c | 0x85ab34 | 1 |
| 0x70000300 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f6200 | 0x14 | 0x629580 | 0x2e | 0x85ab4c | 1 |
| 0x70000380 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f63a0 | 0xb7 | 0x629720 | 0x8f | 0x85ab64 | 1 |
| 0x70000400 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f6d30 | 0x21 | 0x62a0b0 | 0x28 | 0x85ab7c | 1 |
| 0x70000480 | 0x1b0 | 0x814884 | 0x2a0 | 0x6f7680 | 0x7e | 0x62aa00 | 0xaa | 0x85ab94 | 1 |
| 0x70000500 | 0x1b0 | 0xb5c616 | 0x6ea0 | 0x6f7920 | 0x16 | 0x62aca0 | 0x57 | 0x85abac | 1 |

`ret=0x85aabc`/`0x85abac` are T54's mode-6 records; item w1/w2 equal the
records' w1/w2 (`0x814884`/`0x2a0`, `0xb5c616`/`0x6ea0`); item w3 alternates
are T54's record-w3 ping-pong values. Remaining 101 pass-1 rows/vsync are
parity-identical (w3=0 static items, §T55-5).

Per-vsync `stores=1` (21/vsync, every full vsync 0–35): the 11 mode-6 rows
above + 9 static first-of-tuple rows (vsync 0: `0x70000580` w0=0xc→`0x85abc4`;
`0x70000680` 0xcc/0x220→`0x85abdc`; `0x70001980` 0xcc/0x240→`0x85abf4`;
`0x70001a00` 0xcc/0x2a0→`0x85ac0c`; `0x70002800` 0xcc/0x120→`0x85ac24`;
`0x70002880` 0xcc/0x200→`0x85ac3c`; `0x70002900` 0xcc/0x140→`0x85ac54`;
`0x70003180` 0xcc/0x260→`0x85ac6c`; `0x70003200` 0xcc/0x280→`0x85ac84`) + 1
pass-2 row (`0x70002f80` 0xcc/`0x1414294`/0x1c0/0x0 hash=0xb3→`0x85ac9c`,
same both parities). Static rets land on T54's mode-3 records
(`0x85ac24/54/9c/3c` with matching w2 `0x120/0x140/0x1c0/0x200`).

## T55-5. Distributions and the consume model

- Calls: 224/vsync × 36 full vsyncs + 128 @36 (cap) = 8192; 0 grammar
  rejects. `tgt` 1 distinct, `a0` 1 distinct, `s1` 112 distinct (74 hits
  each = 2/vsync × 37), `hash` 30 distinct, `ret` 21 distinct (all
  `0x85aa..–0x85ac..`), 218 distinct (s1,w0..w3,hash) tuples.
- Parity: vsync-stripped full-row signatures form exactly 2 classes —
  evens 0..34, odds 1..35 (pass-1, pass-2, rets all class-equal).
- Pass 1→2 mutation (96/112 rows differ; 16 pre-consumed static rows
  identical, all hash=0xd0→`0x85ac0c`, stores=0): e.g. `0x70000000`
  pass 1 `(0x1b0,…,0x2a0,0x6efd00)` → pass 2 `(0xcc,…,0x280,0x0)`
  hash `0x56→0xf0` ret `0x85aabc→0x85ac84` stores `1→0`. Reading (no
  verdict): pass 1 rewrites the item in place and writes the record;
  pass 2 re-walks consumed items into other buckets without firing the
  `0x394fdc–0x394fe8` cluster (except `0x70002f80`).
- `ret` is parity-independent for all 112 pass-1 items (112/112 identical
  even-vs-odd) while `hash` follows `w3`: slot selection does not follow
  the 8-bit hash on these inputs.
- Dominant bucket: hash=0xd0, 3809/8192 calls (46%), all →`0x85ac0c`.

## T55-6. E43 join keys (for the orchestrator)

| Fact | T55 (PCSX2, healthy) |
| --- | --- |
| Call site | jal @`0x362f68` → tgt `0x394ed0` always; 224 calls/vsync, 2 passes × 112 items `0x70000000+i*0x80` |
| Inputs | `a0=s6=0x8095f0` const; `a1=s1` item ptr; `a2&0xff`=hash folded from the 4 words (w3-sensitive, §T55-4 table) |
| Returns | record-slot ptr (`0x85aa..–0x85ac..`); mode-6 slots `0x85aabc`/`0x85abac` for items `0x70000000`/`0x70000500`; parity-independent for all items |
| Stores | `0x394fdc–0x394fe8` fire on first-of-tuple (21/vsync: 20 pass-1 + `0x70002f80` pass-2); pass 1 mutates items in place (w0/w2/w3 rewritten) |
| Cadence | from vsync 0 of the statefile boot, even/odd classes stable over 36 vsyncs |

## T55-7. Gaps, overruns

1. Cap @8192 (vsync 36) cuts the window: cadence past ~36 vsyncs is
   extrapolated, not observed (cap, not silence). Vsyncs 0–4 (the brief's
   ~5) are complete: 5×224.
2. `stores` marks execution of the pcs `0x394fdc–0x394fe8`, not store
   completion; which of the 4 pcs fires per call is not logged.
3. Snapshot is at func entry (post-delay-slot); JAL-time regs are not
   recorded — if the delay slot sets args, the entry read is the correct
   ABI input (by design, §T55-2), but a delay slot that touches memory at
   `s1` would be invisible.
4. Single call-scope flag: a non-returning call (exception) would drop one
   row and misattribute `stores`; no such gap observed (224/vsync exact,
   every vsync pairs).
5. Budgets: 2 build invocations (b1 1-TU compile error from decl-after-use,
   fixed by `t55-fix.py`; b2 clean) vs brief's ≤1 — authoring miss, no
   extra full build. 1 capture of ≤2. ~25 min wall; bytesize ≈50 MB new of
   2 GB.
6. LOADED p99 46 vs T54's 37–40 (mean 1.60, same <2.0 SC band; F8 PNG +
   CWINDOW + ctag-3606 confirm the route). Same watch-logging jitter
   class; speed gate already passed on gsrunner (§T55-3).

## T55-8. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (no `>|<|` in the
ssh string; multi-step logic in staged files; transfers via
`C:/Users/bradr/t55stage/`): `t55-hook.py` (validate-all-then-write) →
`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2` (b1 fail;
`t55-fix.py` decl-move; b2 clean; SHAs §T55-1:
qt `7434461414bc43fb65eeb3db88efa83f80ee1e5c851dd014b16845d030501059`,
gsrunner `01a01509fd6f2eb667b5f0057ac6b27cd0a5e28f8eaa505a950e72e0fabf34cb`)
→ `t55-replay.sh` (G13 dump, 7/7 + HWSTAT) → `t55-cap.sh` (`TAG=t55a`,
statefile, free-gate, CWINDOW→PATHS V+6, F8) → extract (`t55-extract.sh`
grammar, 0 rejects) + analyze (`t55-analyze{,2,3,4,5}.py`) →
`git diff -- pcsx2/Interpreter.cpp --output=…/t55-patch.diff`.
`git log -1` checked before commit (main @ `0a5b45d` + prior lane commits).

## T55-9. Receipts

Repo (this commit): `local/research/T55/` — REPORT.md, `t55-patch.diff`
(4,312 B), appliers (`t55-hook.py`, `t55-fix.py`), build/cap/extract/
analyze×5/replay scripts, `t55-trace.txt` (sha `06ce9b8a…7f201f64`),
`t55a-poll.log`, F8 `t55a-shot-sc.png`. Bytesize residue under cap:
`t55stage/` (scripts, trace, poll log, PNG, `t55-patch.diff`), rotated
emulogs, `t55-frames/`, both binaries (§T55-1).
