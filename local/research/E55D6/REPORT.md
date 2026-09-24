# E55D6 — reachable memory-card guest-write path (read-only design)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D6.md`.
Read-only: no build, boot, device action, source edit, fork commit, push, or
change to any card image. Write scope is this REPORT plus the brief only.
No determinism verdict — the orchestrator decides.
Prior context: `local/research/E55D3/{REPORT.md,ORCH-GATE.md}`,
`local/research/E55D4/{REPORT.md,ORCH-GATE.md}`,
`local/research/E55D5/{REPORT.md,ORCH-GATE.md}`, `docs/todo.md` E55D6 entry.

## 1. Source/trace evidence table

| # | Claim | Evidence (file:line or named receipt) |
| --- | --- | --- |
| 1 | E55D4 A/A + E55D5 pad-B reached race tick 2053/2055 with empty mc0 and **zero** `getdir`/`mcread` probe records | `local/research/E55D4/REPORT.md:23` (4000/4000 `pad ok=1`, no getdir/mcread through tick 2055); `local/research/E55D5/REPORT.md:34` + `local/research/E55D5/excerpts.txt:13` (all pad, no getdir/mcread through tick 2055); gates `E55D4/ORCH-GATE.md:13`, `E55D5/ORCH-GATE.md:15` |
| 2 | The tap records **all** GetDir/Read exits incl. failures, so zero lines means zero calls, not zero successes | `local/research/E55D3/REPORT.md:91-112` (G1–G6, R1–R7 coverage table); on an empty-but-existing mc0 root any real `sceMcGetDir` call would emit at least `ok=1` with the `.`/`..` entries (see #7) |
| 3 | Game-side card API surface is mapped: `sceMcRead@0x40a090` ← {0x2c4d1c, 0x2c4ee4, 0x2c6b90}; `sceMcGetDir@0x40a688` ← {0x2c424c, 0x2c431c, 0x2c4f84, 0x2c5020, 0x2c6884} | `local/research/P8/census-pad-sound.tsv:40,44` (counts 3 reads / 5 getdirs with call-site list); independently confirmed live: `ee-xref 0x40a090` → `0x2c4d1c/0x2c4ee4 (sub_002C48C0), 0x2c6b90 (sub_002C6B78)`; `ee-xref 0x40a688` → `0x2c424c (sub_002C4210), 0x2c431c (sub_002C42B0), 0x2c4f84/0x2c5020 (sub_002C48C0), 0x2c6884 (sub_002C6848)`; codegen stubs `codegen-ssx3/sub_0040A090_0x40a090.cpp:13` (`sceMcRead`), `codegen-ssx3/sub_0040A688_0x40a688.cpp:13` (`sceMcGetDir`); cluster list `local/research/P7/elf-cluster.txt:220,227` |
| 4 | All card call sites sit in one game-side save-manager cluster (0x2C3FA8–0x2C6xxx): GetDir wrappers (0x2C4210, 0x2C42B0, 0x2C6848) and Read users (0x2C48C0, 0x2C6B78) are all driven under the `sub_002C5570` state machine | `ee-xref 0x2c4210/0x2c42b0` → both called only from `sub_002C5570` (0x2c5988, 0x2c59b4); `ee-xref 0x2c6b78/0x2c6848` → `0x2c5f7c/0x2c5e64 (sub_002C5570)`; `ee-xref 0x2c48c0` → ~20 callers incl. `sub_002C4210/0x2C42B0` and `sub_002C5570`-adjacent wrappers; `ee-at 0x2c424c` shows the GetDir call prologue (`a2=s1+0x139` path-ish arg); `ee-at 0x2c4d1c` shows the Read call (`jal func_40A090`) |
| 5 | Full card-op inventory exists game-side: Open ×6, Mkdir ×2, Close ×8, Seek ×1, Read ×3, Write ×4, Sync ×4, GetInfo ×1 (0x2c5110), GetDir ×5, Format ×1, Delete ×2, Flush ×1; Chdir/SetFileInfo/Rename ×0 direct | `local/research/P8/census-pad-sound.tsv:35-50` (same rows; read verbatim, not re-derived) |
| 6 | Game's save identity strings exist in the ELF: folder `BASLUS-20772`, `mc0:`; `SAVEDATA` does **not** occur in the ELF (it occurs only in the runtime unit test's query `/SAVEDATA/*`) | `strings SLUS_207.72 \| grep -E "SAVEDATA\|BASLUS\|mc0"` → `BASLUS-20772`, `mc0:` only (read-only run, this part); unit-test query `local/research/E26/e26a-preclaim-suite.txt:752` (`GetDir port=0 '/SAVEDATA/*' maxent=8 -> result=3`) — a stub self-test, **not** game behavior |
| 7 | Runtime host-card semantics: mc0 is a plain host dir (`PS2X_MC_ROOT`); GetDir always synthesizes `.`/`..` entries, sorts case-insensitively, copies `entryCount*64` B; Read freads host bytes straight into RDRAM; every op completes synchronously (`sceMcSync` → 1/−1) | `~/dev/PS2Recomp` @ `eac6cba`: `MemoryCard.cpp:118-155` (root resolution), `:706-865` (`sceMcGetDir`, `.`/`..` at `:777-789`, sort at `:802-808`, table `memcpy` at `:839-843`), `:1069-1115` (`sceMcRead`, `fread` at `:1095`), `:1226-1273` (`sceMcSync`); same anchors at `ddaee78` in `local/research/E55D1/REPORT.md:115-123` |
| 8 | Host-clock injection: `.`/`..`/mtime-fallback entries stamped with `std::time(nullptr)`; real entries carry host `last_write_time`/`file_size` | `MemoryCard.cpp:296-312` (`writeMcDateTime`), `:314-331` (`fillMcDirTableEntry`), `:823-830` (per-entry times); `local/research/E55D1/REPORT.md:124-132` |
| 9 | I26-FAST assumes an **empty** card with **no profile prompt** — i.e. a nonempty card is expected to prompt at/before the title | `local/research/I26/ROUTES.md:4-5`; game strings `Title_SaveProfile`, `cFEStateLogin MemoryCard`, `122bAutosave` exist in the ELF string set (same `strings` run as #6; names quoted, relationships not traced) |
| 10 | Save-menu surface exists game-side: `title_Save Replay`, `title_Save Records`, `kT_TITLESaveOptions`, `option_savereplay`, `Save Profile` strings in the ELF | Same `strings` run as #6 (names only; no call-edge traced — gap §4a) |
| 11 | `sceMcGetInfo` (type/free/format) and `sceMcWrite` guest writes are **outside** the E55D3 probe families | `local/research/E55D3/REPORT.md:114-116` (out of scope by brief) |
| 12 | LSP code-connection confirmation unavailable in this environment | `documentSymbol` on `MemoryCard.cpp:706` returned no results (no usable server); caller/callee links rest on `ee-xref`/`ee-at` + exact citations, as in E55D2 (`local/research/E55D2/REPORT.md:16-17`) |

## 2. Candidate user flows (at most two; reachability NOT established)

No existing trace, menu log, or route shows the game calling GetDir/Read on any
boot: the only bounded whole-boot card observations (E55D4 A/A, E55D5 pad-B)
record zero card calls (#1). The flows below have a mapped callee (#3–#5) and a
plausible UI trigger (#9–#10) but **no menu→caller edge and no tick**; the
route/tick cells are explicit `unknown`.

### Flow A — seeded-card title/login check (cheapest; no route detour)

1. **Exact GetDir/Read evidence:** callee mapping only — `sceMcGetDir@0x40a688`
   has 5 game call sites and `sceMcRead@0x40a090` has 3 (#3), all inside the
   save-manager cluster (#4). There is **no** evidence any of them fires on
   I26-FAST (zero records, #1–#2). The trigger hint is `ROUTES.md` "empty
   memory card (no profile prompt)" (#9): a card containing `BASLUS-20772`
   (#6) is expected to produce a profile/autosave prompt at or before the
   title, which is the natural reader of a directory listing and, on accept,
   of save payloads.
2. **Required layout + safe creation:** host dir `mc0/BASLUS-20772/` with save
   payload file(s) (#6–#7). Exact expected filenames/payload shape are
   **unknown** (gap §4b). Creation rule: never mutate a canonical input —
   copy the pinned empty-card dir to a fresh run dir, add files only to the
   copy, point `PS2X_MC_ROOT` at the copy. No existing save exists today
   (manifests empty, #1), so nothing can be destroyed yet; the rule still
   binds for any future real save.
3. **Route/tick:** `unknown` — no trace of the prompt or of any card call on
   any route. Plausible window (hypothesis only): title ticks ~570–636
   (`ROUTES.md:23`, "Press START" settles ~570).
4. **Predicted probe line (E55D3 schema, `REPORT.md:56-61`):** presence — not a
   field diff. Baseline has **zero** `getdir` lines, so the prediction is the
   first-ever record, e.g. `getdir seq=<s> vsync=<t> ord=1 port=0 slot=0
   addr=0x<…> entries=<n≥3> max=<m> len=<64n> ok=1 bytes=<hex>` with the
   `BASLUS-20772` 64 B entry appended after `.`/`..` (name bytes at entry
   offset +32), and on prompt-accept a first `mcread seq=<s'> vsync=<t'>
   ord=1 fd=<f> addr=0x<…> req=<q> len=<a> ok=1 err=- bytes=<hex>` carrying
   save payload. Seq-family/address/length values are unpredictable before
   the run (depend on guest heap placement); the discriminating fact is the
   family's first appearance with `ok=1` and the new entry/payload bytes.
5. **Competing explanation + distinguisher:** the game may probe the card with
   `sceMcGetInfo@0x40a498` only (one game site, 0x2c5110, #5) or gate on the
   always-true `mcCheck*Start*File` HLE stubs (`MemoryCard.cpp:1352+`) —
   neither emits pad-probe-family lines (#11). Distinguisher: run the same
   seeded-card boot with `RUNTIME_LOG` `[MC]` lines enabled (or an extended
   tap): GetInfo-only predicts `[MC] GetInfo …` lines with still-zero
   `getdir`/`mcread` probe lines; HLE-gate predicts no `[MC]` stub lines at
   all; Flow A predicts `getdir`/`mcread` probe lines.

### Flow B — in-game save-menu detour (Options Save / pause Save Replay-Records)

1. **Exact GetDir/Read evidence:** same callee mapping as Flow A (#3–#5).
   Trigger hint is the save-menu string surface (#10). No menu→cluster call
   edge is traced (gap §4a), and I26-FAST never visits these menus.
2. **Required layout + safe creation:** same as Flow A, item 2; additionally
   the detour needs no card change at all for the reachability pre-trace
   (§3) — empty card suffices to test whether the menu *calls*.
3. **Route/tick:** `unknown` — requires a new route detour off I26-FAST
   (Main Menu → Options/Save, or pause-menu save) that no brief has driven;
   tick depends on the detour taken.
4. **Predicted probe line:** same presence-shape as Flow A, item 4, but at
   detour-menu ticks instead of title ticks; a save-*write* flow would
   additionally exercise `sceMcWrite`/`sceMcMkdir` (#5), which are outside the
   probe families — so a write-only flow predicts continued probe silence
   with changed final card manifest (state this in the run's stop rule).
5. **Competing explanation + distinguisher:** the menus may be display-only on
   this build (no card calls wired), or the detour route may miss the screen.
   Distinguisher: the §3 pre-trace with unchanged empty card — first
   `getdir`/`mcread` record at detour ticks confirms wiring; continued zero
   records through the detour refutes menu wiring and points back to Flow A
   (or to the GetInfo/HLE-gate alternative).

## 3. Predeclared one-change comparison (NOT run; orchestrator decides)

- **Baseline invalidation rule:** any card-layout change invalidates the
  E55D4 A/A starting manifest (`f9401596…ccb9ce`, #1). A seeded-card program
  must first re-run its own A/A: two boots on a **copy** of the seeded layout
  (same pinned binary/ISO/route/clock/tap as E55D4: runner `e282c8a7…f211643f`,
  ISO `3c2f8eb1…`, ELF `1b49d05c…`, codegen `8ea8ed43…`, I26-FAST,
  `PS2X_DETERMINISTIC=1`, slot-lease discipline), requiring identical hash
  prefix 1..2053 and identical windowed probe incl. payloads (E55D4 bar,
  `REPORT.md:24`), same-prefix SHA comparison, and flush proof per side
  (persisted complete probe line with vsync > stop tick, E55D4 pattern
  `proof_vsync 2055`).
- **One-change B:** from the re-baselined A', exactly one card-file byte or
  one directory-entry difference in a fresh copy (e.g. one payload byte flip;
  never touch the A' dirs). Same pins; stop at the **first differing `getdir`
  or `mcread` ordered guest-write record**; record family, seq, vsync, ord,
  port/slot or fd, guest address, and differing bytes; do not run past it for
  attribution. Hash rows are compared only up to the probe-difference tick;
  any `.`/`..`/mtime bytes (#8) must match between A' repeats or the A' is
  void (host-clock contamination, not game signal).
- **Cheapest reachability pre-trace before ANY card-change boot** (recommended
  next action, §5): one bounded boot with the existing E55D3 probe, an
  **unchanged empty card**, and a route that detours into Flow B menus
  (Flow A needs no detour — the title prompt, if it exists, fires on I26-FAST
  with a seeded card, but seeding is itself the card change, so probe the
  detour first): stop at the first `getdir`/`mcread` record or a tick cap
  (suggest 2053-parity window + menu ticks), standard 500 s / 4 MiB log /
  16 MiB probe caps, PID-scoped kill, lease discipline. If it fires, the
  one-change program targets the proven flow; if silent, do Flow A's seeded
  title boot next. No static codegen build is needed (codegen index already
  exists at `~/dev/ssx3-work/codegen-ssx3`; no gap there).

## 4. Gaps (stated plainly)

a. No menu→save-cluster call edge: the five GetDir / three Read sites (#3)
   are mapped, but nothing links them to title/login/autosave or to a save
   menu (function names at 0x2Cxxxx are `unknown` per `ee-label`; brief
   forbids inventing relationships from name similarity — none invented).
b. Expected card content unknown: `BASLUS-20772` folder name is confirmed
   (#6) but payload filenames, sizes, and the guest query paths (`a2=s1+0x139`
   at `0x2c424c` not resolved to a string) are not.
c. `sceMcGetInfo`/HLE-gate alternative (§2A.5) is untested: the current probe
   cannot see it (#11); needs `[MC]` log lines or a tap extension.
d. Host-clock coupling (#8) means even a perfect game-side A/A can differ on
   `.`/`..`/mtime bytes; the predeclared program voids on A'-internal mtime
   drift rather than attributing it.
e. LSP unavailable (#12); links rest on `ee-xref`/`ee-at` as E55D2 allowed.
f. Pins of the read-only inputs: fork reads at `~/dev/PS2Recomp` @ `eac6cba`
   (MemoryCard.cpp line numbers verified against this checkout; E55D-audit
   anchors were at `ddaee78`); ssx3 checkout `c0c9837c` at read time;
   codegen `~/dev/ssx3-work/codegen-ssx3` (9441 files indexed by ee-tools).
   No pinned SHAs were re-read in this part (read-only; snapshot SHAs in §5).

## 5. Exact read-only commands run

- `git -C /Users/brad/dev/ssx3 log -1` → `c0c9837c`; `status --short` clean
  before writing (re-checked before commit per standing rules).
- `ls ~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/` (MemoryCard.cpp
  present in both `~/dev/PS2Recomp` and the E55D3 worktree).
- Full read `~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp`
  (anchors §1 #7–#8 verified at `eac6cba`).
- `rg -n "40a090|40a688" codegen-ssx3/sceMcUdCheckNewCard_0x40a618_0x40a618.cpp`;
  `rg -n "McGetDir|McRead|sceMc" codegen-ssx3/sub_0040A090_0x40a090.cpp` →
  `sceMcRead` (:13); same on `sub_0040A688_0x40a688.cpp` → `sceMcGetDir` (:13).
- `rg -ln "0x40a090|0x40a688|…" codegen-ssx3/` (5 files: the two stubs,
  headers, register table, CheckNewCard fallthrough).
- `bash local/tooling/ee/ee-xref {0x40a090,0x40a688,0x2c4210,0x2c42b0,0x2c48c0,0x2c6b78,0x2c6848,0x2c4050,0x2c4410,0x2c5570}` (all outputs cited in §1 #3–#4).
- `bash local/tooling/ee/ee-at {0x2c4d1c,0x2c424c,0x2c5988,0x2c5e64,0x2c5f7c}`;
  `ee-func 0x2c4d1c/0x2c5570`; `ee-label 0x2c4d1c/0x2c6b90` → unknown.
- `strings E32-inputs/cd/SLUS_207.72 | grep -E "mc0:|…|BASLUS|…|SAVEDATA|…|sceMc"` (§1 #6, #9–#10).
- `python3 -c gzip.read E55D4/run/A1/boot.log.gz` → zero `[MC]` lines
  (RUNTIME_LOG compiled out of the diagnostic runner; weak corroboration of
  #1, not independent evidence).
- `sed -n` reads of `P8/census-pad-sound.tsv:35-50`,
  `P7/elf-cluster.txt:210-235`, `I26/ROUTES.md` (full), `docs/todo.md:1565-1614`.
- LSP `documentSymbol MemoryCard.cpp:706` → no results (#12).
- Receipt sizes: this REPORT only (~9 KiB, < 512 KiB budget); <20 min review.

## 6. Recommended next action (no verdict)

Run the §3 reachability pre-trace: one bounded empty-card menu-detour probe
boot (Flow B wiring test, zero card mutation). If it emits a first
`getdir`/`mcread` record, predeclare the one-change card program against that
flow; if silent, the next step is a seeded-card title boot (Flow A) with a
re-run A/A baseline per the §3 invalidation rule. ExternalWake policy stays
parked (no production poster per E55D1; untouched by this part).
