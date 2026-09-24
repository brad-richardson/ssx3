# E55D5 — one-change pad comparison (B1 booted once, committed, no push)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D5.md`
plus Part-1 review (paired-record acceptance gap) and the release naming the
exact script SHAs below. One B1 boot run with the released script; no second
boot. No build, no source/device/iOS/upstream/push. No determinism verdict —
the orchestrator decides.

## 1. Pre-run evidence table

| Item | Value |
| --- | --- |
| Private fork (read-only) | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703` (`bab6eb3 [E55D3]`, read 09-24, not edited) |
| ON runner (read-only) | `~/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner`, SHA `e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f` (one read 09-24 matched; script enforces two matching reads + `14b1e5cb` runner-dir guard at boot) |
| ISO (pin, not re-read in Part 1) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, pin `3c2f8eb1…9761ebf5` (E55D4 result-A1) |
| ELF (pin) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, pin `1b49d05c…67af7bc` |
| Codegen (pin) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, pin `8ea8ed43…2ae662d` |
| Baseline A (read-only) | `~/dev/ssx3-work/E55D4/run/A1` (`boot.log.gz`, `probe.log.gz`, `result.json`); E55D4 A1/A2: 2058 hash rows, 4000 probe lines, proof vsync 2055, cards empty `f9401596…ccb9ce` |
| B1 cwd/cards (one fresh boot, released script) | `~/dev/ssx3-work/E55D5/run/B1` with `boot.log.gz` (92189 B; pre-gzip sha `3cb0c64b…bdfbd83`, 374395 B), `probe.log.gz` (29767 B; pre-gzip sha `b472dcb5…84f13b`, 579670 B), `result.json`, fresh empty `mc0/mc1`, runner `imgui.ini` artifact; script refused-reuse guard held (run dir was empty before the single boot) |
| Route diff (exactly one entry) | E55D4 index 20 `33517:cross:200` → E55D5 `33517:square:200`; other 30 entries byte-identical, order preserved; self-check `route_single_change diff_idx=[20]` ok |
| Full B route | `10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:square:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000` |
| Pulse window (predeclared) | `33517 ms` → tick `33517*5994/100000 ≈ 2009`; hold 200 ms ≈ 12 ticks (2009..2021); comparator `PULSE_VSYNC_LO=2008`, `PULSE_VSYNC_HI=2025` (−1 boundary, +4 scheduling tolerance) |
| Env (as E55D4, route swapped) | `PS2X_CD_IMAGE`, `PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, `PS2X_DET_HASH_EVERY=1`, `PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_PAD_SCRIPT` (B route), `PS2X_MC_ROOT=<B1>/mc0`, `PS2X_PAD_CARD_PROBE=<B1>/probe.log`, `PS2X_MISSING_FUNCTION_POLICY=stop`; all `PS2X_*` cleared first |
| Stop rule | hash tick 2053 observed **and** persisted complete probe line vsync > 2053 (flush proof); bounded extra-wait 180 s / 60 ticks → else `flush_unproven` |
| Caps | 500 s wall, 120 s no-progress, 4 MiB boot log, 16 MiB probe; kill only recorded PID; lease released in `finally`; at most one boot (B1), slot lease only during boot |
| Comparator inputs | runA = E55D4 A1 dir (accepts `boot.log.gz`/`probe.log.gz`, bounded 16/32 MiB, read-only, never writes into inputs); runB = E55D5 B1 dir; optional `--hidutil-list` full-text row adjudication |
| Comparator classifier | PASS `pad_b_discriminated` (paired first pad records with identical metadata — seq, vsync, ord, port, slot, addr, len, ok — and exactly the `bytes` payload differing; vsync in [2008,2025]; identical ordered prefix; cards match; HID clean; hash None or ≥ probe vsync; both first diffs preserved). FAIL: `probe_wrong_family`, `probe_earlier_difference`, `probe_late_difference`, `probe_metadata_difference` (any non-`bytes` drift incl. seq/vsync), `probe_length_difference` (extra windowed line), `hash_without_probe`, `hash_earlier_than_probe`, `card_manifest_difference`. OTHER: `probe_missing_X`, `probe_truncated_X`, `probe_framing_X`, `hash_error_X`, `probe_cap_X`, `incomplete_trace`, `probe_unproven_X`, `live_pad_present`, `no_probe_difference` (pulse no-event). No hash-only attribution without the ordered write chain |
| Boot script | `local/research/E55D5/e55d5_boot.py`, 17557 B, SHA `cb9ba39b770270692baeccad6523a838165041c17df6d631acb4fe45ffcb293e` |
| Compare script | `local/research/E55D5/e55d5_compare.py`, 36608 B, SHA `e16d01819b03b8b8c40209886dd5df9e047e2285bd3cdbec26cb0a7ea4c51307` (rev 2: paired-record gate + metadata/length FAIL + 2 new synthetic cases) |
| Boot self-check | 11/11 (`self-check-boot.txt`): reuse ×3, split ×4, proof ×3, route_single_change ×1 |
| Compare self-check | 21/21 (`self-check-compare.txt`): 14 trace (identical_prefix, unchanged_no_event, expected_pad_change, both_first_differences, earlier/wrong_family/late, metadata_only, length_only, hash_without_probe, hash_earlier_than_probe, truncated/cap/unproven) + 7 HID (internal-clean, game-name, game-usage, ambiguous, internal end-to-end OTHER, gamepad end-to-end OTHER, legacy-flag OTHER) |
| Gz-path validation (read-only, no boot) | B-comparator on E55D4 A1 vs A2 → `OTHER no_probe_difference`, 2058 rows, 4000/3996 lines, proof 2055, HID 227 rows clean (temp json in `/tmp`, not committed) |
| Boots run | 1 (B1 only): slot 1, PID 63200, bound **target**, 123.838 s, last_hash_tick 2057, phase2 0.523 s, proof_vsync 2055, 2057 hash rows, 4000 probe lines, log 374395 B, probe 579670 B, rc −15, cards empty `f9401596…ccb9ce` initial and final; pre-boot and post-boot full HID lists show no gamepad (sole Controller = known-internal ANS3). No second boot |
| B1 vs A1 result | `comparison.json` verdict **PASS** `pad_b_discriminated` (comparator output; not a verdict): windowed probe 3996/3996 with first diff seq 3909 vsync 2010 pad port 0 ord 3905, metadata identical, bytes `…ffbf…` → `…ff7f…` (in [2008,2025]); first hash tick 2011 (fields eeCycle/rdram/combined), one tick after the write; HID 227 rows clean. Full first differences in `excerpts.txt` |
| Disk / text | new scratch ≈ 0.12 MiB gzipped logs + result in `~/dev/ssx3-work/E55D5/run/B1/`; committed text ~75 KiB (< 512 KiB); no global-budget pressure (single small boot) |

## 2. Exact commands run

- `mkdir -p ~/dev/ssx3-work/E55D5/run local/research/E55D5` (owned paths only)
- reads: E55D4 `REPORT.md`, `ORCH-GATE.md`, `e55d4_boot.py`, `e55d4_compare.py`, `comparison.json`, `excerpts.txt`, `result-A1.json`, `I26/ROUTES.md`; `git -C ~/dev/ssx3-work/E55D3/PS2Recomp log -1`; `sha256sum` runner; `ls` inputs
- `python3 local/research/E55D5/e55d5_boot.py --self-check` → 11/11
- `python3 local/research/E55D5/e55d5_compare.py --self-check` → 21/21 (rev 2)
- `python3 local/research/E55D5/e55d5_compare.py ~/dev/ssx3-work/E55D4/run/A1 ~/dev/ssx3-work/E55D4/run/A2 --hidutil-list local/research/E55D4/hidutil-list.txt --json-out /tmp/e55d5-a1a2-tmp.json` → OTHER no_probe_difference (gz read-only check)
- `sha256sum local/research/E55D5/e55d5_boot.py local/research/E55D5/e55d5_compare.py`
- Release (one boot only): `python3 local/research/E55D5/e55d5_boot.py --label B1` → bound target, 123.838 s
- `hidutil list > local/research/E55D5/hidutil-list.txt` (233 lines, post-boot receipt; pre-boot check identical: 0 gamepad/joystick, 1 known-internal Controller)
- `cp ~/dev/ssx3-work/E55D5/run/B1/result.json local/research/E55D5/result-B1.json`
- `python3 local/research/E55D5/e55d5_compare.py ~/dev/ssx3-work/E55D4/run/A1 ~/dev/ssx3-work/E55D5/run/B1 --hidutil-list local/research/E55D5/hidutil-list.txt --json-out local/research/E55D5/comparison.json` → PASS pad_b_discriminated
- `gzip ~/dev/ssx3-work/E55D5/run/B1/boot.log ~/dev/ssx3-work/E55D5/run/B1/probe.log` (pre-gzip SHAs in `excerpts.txt`)
- `git log -1`; `git add -f` named brief/scripts/receipts; commit `[E55D5]`, no push

## 3. Gaps / holds

- Single B1 sample: one changed-entry boot against one A1 baseline; no repeat, no reversed (square→cross) control, no card-path coverage (probe holds pad only; getdir/mcread unexercised, same as E55D4).
- Hash divergence (tick 2011, eeCycle/rdram/combined) follows the first differing guest write by one tick; per the predeclared rule it is preserved, not attributed to the pad alone.
- B1 stopped at tick 2057 vs A1's 2058 (both complete through the 2053 window with flush proof at 2055); post-window tick counts differ by phase-2 timing, not guest content.
- Elapsed 123.838 s is a diagnostic wall time, not a speed number.
- `p_lane_lease` LSP import warning is the same `sys.path` pattern as E55D4 (runtime import, not a defect).
- Committed `[E55D5]` (`Orchestrated-By: opencode`), no push. No determinism verdict — the orchestrator decides.
