# E55D4 Part 1 — pinned pad/card A/A runs (both boots done, committed)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D4.md`
plus orchestrator reviews (flush-proof stop, framing rejection, both-side
FAIL reporting, full reuse refusal, hash-prefix validation, HID row
adjudication). A/A null comparison through guest vsync tick 2053.
**Two boots run with the released scripts. No source changes, no builds,
no fork push, no ssx3 push. No determinism verdict — the orchestrator decides.**

## 1. Evidence table (runs)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703`, clean, runner-dir guard exit 0 (checked in-script before each boot) |
| ON runner | `build-taps/ps2EntryRunner`, SHA `e282c8a7…0643f` ×2 reads per run (4 total, all match) |
| ISO / ELF / codegen | `3c2f8eb1…` / `1b49d05c…` / `8ea8ed43…` ×2 reads per run (all match E55C2 pins) |
| Boot script (released, unchanged) | `e55d4_boot.py` SHA `cbd08f96990480e2ce058f4e0fc34a24060e3b664cfaa1fee425b5938fa904f8` |
| Comparator (HID fix) | `e55d4_compare.py` SHA `7d27ef354c4c5eafe0849b6465a026db40ab3088f70cd88af7d6c4f3f379af3e` ×2 reads, 26586 B |
| Boot self-check | 10/10 (unchanged script) |
| Comparator self-check | 21/21 (14 trace + 7 HID: internal-clean, game-name, game-usage, ambiguous, internal end-to-end PASS, gamepad end-to-end OTHER, legacy-flag OTHER) |
| A1 | slot 1, PID 39728, bound **target**, 128.443 s, last_hash_tick 2058, phase2 0.523 s, proof_vsync 2055, 2058 hash rows, 4000 probe lines, log 374576 B, probe 579670 B, rc −15, cards empty `f9401596…ccb9ce` |
| A2 | slot 1, PID 40565, bound **target**, 123.982 s, last_hash_tick 2058, phase2 0.521 s, proof_vsync 2055, 2058 hash rows, 4000 probe lines, log 374576 B, probe 579670 B, rc −15, cards empty `f9401596…ccb9ce` |
| Probe content | 4000/4000 `pad ok=1` lines both runs (ports alternate, first vsync 58); **no getdir/mcread records** through tick 2055; whole-file probe SHA identical: `618e8a49…38136c8` |
| Hash prefix 1..2053 | identical `(tick,eeCycle,rdram,scratch,vu1Data,vu1Code,combined,count)` every row; windowed probe (3996 lines ≤2053) identical incl. payload bytes |
| First differences | none (null/null) |
| comparison.json | verdict **PASS** `identical_to_tick_2053`, hash_rows 2053, probe_lines 3996 (comparator output; not a verdict) |
| HID state | A1/A2 `hidutil` blocks byte-identical (stable); sole `Controller` match is `AppleANS3CGv2Controller` / `NAND CH0 temp` (UsagePage 65280, Usage 5) — internal NAND temp sensor, not input; full 227-row list saved as `hidutil-list.txt` (32206 B); classifier: 0 flagged, 1 known-internal |
| Closed logs | `run/A1| A2/boot.log.gz` (92241 B each), `probe.log.gz` (29757 B each); pre-gzip SHAs in `excerpts.txt`; run dirs also hold `result.json`, empty `mc0/mc1`, runner `imgui.ini` artifact |
| Times | diagnostic runs; elapsed times are not speed numbers |
| Commits | this `[E55D4]` commit (`Orchestrated-By: opencode`), no push |
| Disk | 143.4 GB of 200 GB cap; new scratch < 0.01 GiB; committed text ~104 KiB (< 512 KiB) |

## 2. HID adjudication (post-run review note; comparator/report only)

The boot script's blob-substring regex set `gamepad_like=true` on both runs
from `AppleANS3CGv2Controller`. The full host list (saved post-run, 227
rows, 1 match) shows that row is the internal Apple NAND temperature sensor
(UsagePage 65280 vendor, Usage 5, no game usage, no game product). No
gamepad/joystick row exists. A1/A2 in-run `hidutil` blocks are byte-identical,
so host HID state was stable across the runs.

The comparator now classifies a full `hidutil list` by row: UsagePage/Usage
from their columns, name matching on the Class/Product/UserClass tail; the
specific internal device is allowlisted (recorded, not flagged); an actual
gamepad/joystick product, a Generic-Desktop game usage (page 1, usage 4/5/8),
or any other `controller` row is flagged → OTHER `live_pad_present`. Without
`--hidutil-list` the legacy result.json flag still maps to OTHER. A1/A2 were
compared with the saved list: 0 flagged → gate clean. Boot script and both
boots unchanged.

## 3. Predeclared acceptance (as run)

- PASS criteria (prefix 1..2053 identical; windowed probe identical incl.
  payload bytes/statuses; flush proof each side; framing well-formed; no cap;
  identical card manifests incl. mtimes; no live pad input) — all met per
  `comparison.json`. FAIL differences: none. OTHER conditions: none.
- No diagnostic wall time is quoted as speed.

## 4. Future one-change plan (NOT run; orchestrator decides from A/A)

- **Pad-B:** one I26-FAST entry changed; stop at first differing ordered write.
- **Card-B:** one preseeded card file; stop at first differing ordered write.

## 5. Exact commands

- Pre-release pins/self-checks: see REPORT rev 3 (superseded SHAs in git history).
- `python3 local/research/E55D4/e55d4_boot.py --label A1` → bound target, 128.443 s
- `python3 local/research/E55D4/e55d4_boot.py --label A2` → bound target, 123.982 s
- `hidutil list > ~/dev/ssx3-work/E55D4/hidutil-list-full.txt` (32206 B, 1 match)
- `python3 local/research/E55D4/e55d4_compare.py …/run/A1 …/run/A2 --hidutil-list local/research/E55D4/hidutil-list.txt --json-out local/research/E55D4/comparison.json` → PASS
- `gzip …/run/A1| A2/{boot,probe}.log`; `cp …/result.json` receipts; `excerpts.txt`
- `git log -1`; `git add` named receipts + `git add -f` brief; commit `[E55D4]`, no push

## 6. Gaps

- Probe window holds pad reads only; getdir/mcread paths (incl. R5/G1–G3/R6–R7)
  unexercised by these runs — an A/A over executed paths only.
- Final card mtime strictness untested (no card files created).
- `hidutil` classification trusts the host list text; absence of a game row is
  recorded, not a proof of no physical input. The in-run flag
  (`gamepad_like=true`) remains in `result-A1/A2.json` as recorded; the
  adjudication lives in `comparison.json` + classifier.
- Untracked `local/research/E55D4/__pycache__/` from `py_compile` remains
  (rm denied, not retried) — excluded from the commit.
