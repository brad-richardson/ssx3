# N8D7G — pinned Mac OFF/ON capture replay (DeepSeek Flash Go)

You are an OpenCode Go worker on one bounded replay. Read `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, `local/research/N8D7F/{REPORT.md,ORCH-GATE.md}` and these two scripts: `local/tooling/orch/{run_n8d7g.py,check_n8d7g.py}`. The orchestrator owns the verdict. Do not use web, LSP, Odin, iOS, Android, upstream contact or push. Do not edit source, build, scripts, docs/status/todo/ledger, or another lane's files.

Goal: calibrate the default-OFF selected-input probe on the **same pinned N8D4 GS stream** before any Odin package. Correct Mac behavior predicts OFF and ON final Present hash `7bf5c012`, circuit1/input/stage each 448 tile counts equal, input and circuit active ≥224, final active ≥500, control 128, nonpromoted one-sample source, and zero errors. A mismatch is an OTHER/stop, not a device-cause conclusion. N8D6A's prior Mac stage values were circuit1/merged 300/448, final 567/896. The N8D7D2 synthetic host fixture passed separately; it does not prove live capture.

Inputs are pinned in `run_n8d7g.py`: private fork `~/dev/ssx3-work/N8D7F/PS2Recomp` at backend `0678dd9`, binary `.../N8D7F/build/ps2xTest/ps2x_tests` SHA `66457eb4…70a804`, N8D4 stream SHA `38ace1a3…3f97d`, codegen SHA `8ea8ed43…2ae662`. The script double-hashes each input, claims one mini P-lane lease, runs OFF then ON from the private fork cwd, captures a tick-2050 frame in each, caps each at 600 s / 180 s no progress / 64 MiB log, and releases its lease. Do not re-run after any failed replay; hand back the failure and artifacts. If both slots are busy, wait/poll until one is free. No build and no device action.

Allowed writes: `~/dev/ssx3-work/N8D7F/{off.log,on.log,off.hashes,on.hashes,off-ppm/,on-ppm/,run-receipt.json}` via the script; `local/research/N8D7G/{REPORT.md,result.json,replay-excerpt.txt}` plus named small text receipts, ≤1 MiB total. The frame PPMs and full logs stay private and are never committed. Global internal ssx3 cap 200 GiB. The lease files under `/tmp` are explicitly authorized by this brief. If the OpenCode tool blocks the scripted lease/run, report that exact block; do not change global config or run unleased.

Commands, from ssx3 root:

```sh
git -C ~/dev/ssx3-work/N8D7F/PS2Recomp rev-parse HEAD
python3 local/tooling/p_lane_lease.py status
python3 local/tooling/orch/run_n8d7g.py
python3 local/tooling/orch/check_n8d7g.py ~/dev/ssx3-work/N8D7F > local/research/N8D7G/result.json
```

Stop if fork HEAD differs, input SHA mismatches, OFF fails, lease is lost, cap fires, or `check_n8d7g.py` returns OTHER. Do not run a second candidate or repair source. Copy only bounded relevant alignment/stage/selected/vector summary/error/hash rows to `replay-excerpt.txt`; state exact full-log paths and SHA from the receipt. REPORT.md must include commands, source pins, lease/status, result table, frame paths/SHAs (for orchestrator visual inspection), gaps and next-action recommendation. Check `git log -1` before the ssx3 commit; commit explicit named receipts `[N8D7G]` with `Orchestrated-By: opencode`, no push. **Hand back the table; do not conclude an Odin or GS cause.**
