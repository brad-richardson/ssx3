# N8D7M12 Part 6M6 — one pinned Android package from staged sources (worker receipt — STOPPED at SSH gate)

Worker receipt. Brief: `local/muse/prompts/N8D7M12P6M6.md`. Owns only
`local/research/N8D7M12P6M6/` text receipts. No source/fork/renderer/
collector edit, no Odin/emulator action, no game bytes or binaries in git,
no upstream contact, no subagents. Time box 45 min (used ~10 min; stopped
on first failure per brief). No push.

Goal (not achieved — blocked): build the next arm64 APK from exact P6M5
staged bytes with a reviewable source→native→APK link.

## 1. Stop reason: SSH to bytesize denied by tool policy

First WSL-touching command was attempted once and denied:

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -lc "echo SSH_OK; ..."'
```

Denial text (verbatim, truncated to the rule): "The user has specified a
rule which prevents you from using this specific tool call" with
`{"permission":"bash","pattern":"ssh *","action":"deny"}`. This pane was
briefed as having a scoped SSH exception for `bytesize`, but the enforced
tool policy contains no such exception. Per the brief ("If SSH permission
or transfer check fails, stop and report; do not work around policy") and
the worker rules (no retrying a denied action another way), no transfer,
WSL verify, build, or APK step was attempted. No workaround was tried.

Full denial receipt: `ssh-denial.txt` (this dir, exact command + rule).

## 2. Mac-side preflight completed before the stop

| Item | Value | Status |
| --- | --- | --- |
| P6M5 checker re-run (`check.py`) | 24 rows, 0 failing, verdict A | pass (output in `preflight-p6m5-check.txt`) |
| P6M5 manifest aggregate | `6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a` | match (checker row `manifest_verify_match`) |
| P6M5 counts | 26,211 files / 612,576,408 B (fork 323, parallel 16,429, codegen 9,457, jni 2) | within 30,000 / 2,000,000,000 caps |
| Mini project disk (`disk_budget.sh`) | 157.5 GB of 200 GB cap, RC=0, 87 Gi free | pass |
| Stage size | 645 MiB (`stage/`, ignored/private) | ≤1 GiB |
| WSL root `/home/brad/n8d7m12p6m6` fresh/absent | not found (SSH blocked before check) | open |
| WSL free disk ≥20 GiB, no active N/T build | not found (SSH blocked before check) | open |
| Transfer commands/byte count | not found (no transfer attempted) | open |
| WSL collector `verify` pre/post build | not found | open |
| `assembleRelease` (one only) + argv/versions/CMakeCache/`PS2X_GAME_SOURCE_COUNT` | not found (no build attempted) | open |
| Compiled-input file list (compile_commands.json / Ninja graph) | not found | open |
| APK SHA, native member SHAs, runner Build ID, strings, flags, JNI equality | not found | open |
| Mac APK double-read vs WSL | not found | open |

## 3. Gaps (hand-back)

1. All WSL-side facts are open: the staged roots were never transferred,
   so there is no WSL verify, no build, and no package gate.
2. The scoped-SSH exception named in the brief is not present in the
   enforced tool policy; the orchestrator must either grant it (per-worker
   `OPENCODE_CONFIG_CONTENT` permission exception per
   `local/AGENTS.local.md:103-104`) or re-route this brief to a worker
   kind with SSH allowed.
3. Mac-side inputs remain as P6M5 left them (checker 24/24 A re-verified
   here); nothing was modified by this part.

## 4. Recommended next action

Re-issue 6M6 on a pane whose tool policy permits `ssh bytesize` (or add
the scoped exception), reusing the P6M5 stage + manifest aggregate above
as the transfer source. No other retry or repair is needed on the Mac side.

## 5. Receipts

- `REPORT.md`, `check-result.json` (this dir, committed with `git add -f`,
  `[N8D7M12] Part 6M6` / `Orchestrated-By: opencode`; no push).
- `ssh-denial.txt`, `preflight-p6m5-check.txt` (exact command outputs).
- Base commit `51d60aab` (`[orch] Queue pinned Android package build`).
- No APK, no binary, no game bytes in git; WSL root untouched (never
  reached); no device, lease, or upstream action.
