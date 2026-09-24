# E55D14 Part 2B — one empty-card Load game path run (2026-09-24)

Worker: opencode (Muse Spark). Brief: `local/muse/prompts/E55D14P2B.md`.
Exactly one boot with the released script SHA
`fa9444a9f80c89dfa2b1e8911d8870ddca87397db083e318f678ea4dc9285694`
(verified before launch; script unedited). Own only
`local/research/E55D14P2B/` plus private `~/dev/ssx3-work/E55D14P2/run/S1`.
No fork/source edit, build, seed/card copy, second boot, push, board/global
edit, or upstream contact. No speed claim (diagnostic build).

## 1. Evidence table (run)

| Item | Value |
| --- | --- |
| Result | `bound=target`, `elapsed_s=72.608`, `last_hash_tick=1826`, `phase2_extra_s=1.025`, `runner_pid=72826` (gone; SIGTERM rc=-15 expected), mini slot 1 claimed + released (both slots free) |
| Frame proof | tick 1824 `snap-1824t-0072.53s.png` ≥ stop 1800 |
| Caps | `log_bytes=874717` ≤ 16 MiB; `frames_bytes=14315698` ≤ 2 GiB; `probe_bytes=512206` ≤ 16 MiB; wall 500 / progress 120 / grace 100 (run-control metrics, not speed) |
| Cards | `mc0`/`mc1` empty at start AND end; manifest SHA `f9401596…ccb9ce` unchanged |
| Padscript (boot.log, 19 rows) | `armed n=9 clock=vsync`; presses Start `0x0008` ×1, Square `0x8000` ×1, Down `0x0040` ×5 (i=2..5 plus i=7), Cross `0x4000` ×2 (i=6 C1, i=8 C2), in plan order; 9 releases; no other input. D4 fired `now=20203ms at=20187ms` (16 ms late); C2 fired `now=28378ms at=28362ms` (16 ms late; gaps still ≥ 60) |
| Probe getdir (5 rows) | 4 pre-C2 at vsync 118/122/126/223 (addr `0x00b85660`, all `ok=0 reason=empty`, port=0 slot=0 max=6) + 1 post-C2 at vsync 1740 (addr `0x00ba5b20`, `ok=0 reason=empty`) |
| Probe getdirpath (5 siblings) | pord 1..5 paired by per-family ordinal/tick/port/slot/max with the getdir rows above (shared global `seq` NOT compared: 123/124, 133/134, 143/144, 339/340, 3375/3376). Early: `BASLUS-20772-SET*`, `BASLUS-20772-GAM*`, `BASLUS-20772-REP*`, `BASLUS-20772-REP*`. Post-choice (vsync 1740): `raw="BASLUS-20772-GAM*" query="/BASLUS-20772-GAM*" parent="" pattern="BASLUS-20772-GAM*" host="<lane>/mc0"` |
| mcread | 0 rows anywhere; probe total 3536 lines (5 + 5 + 3526 pad) |
| Checker | `local/research/E55D14P2B/check.py` 68/68 PASS (pins incl. double SHA reads, route, caps, cards, pad rows/order, probe counts/pairing/ticks, path fields, frame proof) |
| Private lane | `~/dev/ssx3-work/E55D14P2/run/S1/` (boot.log + .gz, probe.log + .gz, result.json, frames/, empty mc0/mc1). Raw log/probe kept; `.gz` copies made only after the runner exited |
| Committed text | `REPORT.md`, `check.py`, `s1-receipts.txt` (hashes + sizes, no game data) |
| Outcome vs A/B/OTHER | **A**: same Load game scene as E55D12 (Load-highlight pre, MEMORY CARD post) and all five post-choice path fields observed on the empty card, with zero copied table bytes and zero mcread stated separately |

## 2. Frames (worker-viewed; visual verdict rests with the orchestrator gate)

| File (absolute path) | SHA-256 (prefix) | Reading |
| --- | --- | --- |
| `/Users/brad/dev/ssx3-work/E55D14P2/run/S1/frames/snap/snap-1627t-0064.46s.png` | `16eae26d…573b` | Pre-C2 (tick 1627, \|1627−1620\|=7, nearest pre-C2 full frame): Title **Save/Load**; rows Save game, **Load game (highlighted orange bar)**, Save options, Load options, Load replay, New game; footer "Load previous game." + X Select / Triangle Previous |
| `/Users/brad/dev/ssx3-work/E55D14P2/run/S1/frames/snap/snap-1824t-0072.53s.png` | `70fc79f6…54b3` | Post-C2 (tick 1824, frame proof): Title **Load game**; header "MEMORY CARD slot1"; rows 1–6 all **\<EMPTY\>** with row 1 highlighted; footer "Load game to continue a previously saved game." + Triangle Previous |
| Adjacent (viewed, private only) | `b3e59c8c…9627c` (1652), `12e464b8…549a` (1799) | 1652: same Save/Load submenu with Load game highlighted as 1627. 1799: same Load game MEMORY CARD slot1 with 6 EMPTY rows as 1824. No unexpected screen |

Snapshot filename ticks are approximate (1 s wall grid tagged with the
latest det-hash tick); `.txt` sidecars carry the metadata ticks.

## 3. Commands run (one boot only)

- Pre-run: script SHA check (`fa9444a9…9285694` match), `e55d14_boot.py
  --self-check` 38/38, fork HEAD `80777cb…` + `.work/`-only status,
  runner-dir guard `git diff --exit-code 14b1e5cb 80777cb --
  ps2xRuntime/src/runner` exit 0 (run in fork), runner single SHA
  `d8fa114d…ef04`, `disk_budget.sh` exit 0 (150.4 GB of 200 GB),
  `p_lane_lease.py status` (both slots free), `ps` heavy-job check (no
  clang/ninja builds), lane absent (fresh)
- `python3 local/research/E55D14P2A/e55d14_boot.py --label S1` →
  `bound=target` (sole boot/build/run this part)
- Post-run: PID-gone + lease-free checks, frame viewing (1627, 1824, 1652,
  1799), padscript/probe parsing, `gzip -k` of closed boot.log/probe.log,
  wrote `s1-receipts.txt` + `check.py`, `python3
  local/research/E55D14P2B/check.py` → 68/68 PASS
- `git log -1`, `git status`, stage explicit paths only, commit `[E55D14]
  Part 2B` with `Orchestrated-By: opencode`, no push

## 4. Gaps (stated plainly)

- Tick tags remain snapshotter-approximate; the curated pre frame is +7
  ticks from target 1620 and the post frame is +24 (meta tick 1824 vs stop
  1800), with metadata ticks recorded.
- Why the post-choice GetDir returned `ok=0 reason=empty` on empty cards
  is unobserved; only the call's presence, tick, addr, path fields and
  empty result are evidenced. No copied table bytes and no mcRead were
  observed.
- The five Down pulses' row-by-row travel is inferred from endpoints
  (E55D11 submenu → Load game highlighted), not from per-press frames.
- No `s1-stdout.txt` is committed: stdout was observed live
  (`bound=target` line matches `result.json`); only byte-verifiable
  copies are recorded in `s1-receipts.txt`.
- No valid save, deterministic card behavior, or speed is inferred from
  this diagnostic boot.
