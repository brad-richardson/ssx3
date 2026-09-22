# V1 Mission 2 — smoke restore receipt (ONE small restore, end-to-end)

Source: `/Volumes/share/ssx3/e25-restore/ps2x_tests` (share tier, read-only).
Dest (NEW, retained): `/tmp/v1-smoke/ps2x_tests` (internal, 5.7 MB « 1 GB cap).
Expected (Tier-1, E25 RESTORE.md blob `518af4a3…`): 5,695,128 B,
`2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0`.

## Steps

1. `mkdir -p /tmp/v1-smoke` (new path; no lane output touched).
2. `cp -p <share>/ps2x_tests /tmp/v1-smoke/ps2x_tests`
   → bytes=5695128 mtime=1790081822 (copy wall: seconds).
3. SHA read 1 (post-copy, T1 15:45:06Z):
   `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0` — FULL-match.
4. SHA read 2 (T2 16:13:00Z, gap 1674 s = 27.9 min):
   `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0` — FULL-match.
5. `cmp` vs live `/tmp/e18-mpeg-link/runtime/ps2xTest/ps2x_tests`: CLEAN.
   `cmp` vs share source: CLEAN. Machine receipt: `smoke.json`.

## Verdict

SMOKE PASS: pin FULL-match ×2 (27.9 min apart) + cmp clean vs live and
share. `/tmp/v1-smoke/ps2x_tests` RETAINED (no deletions).

## Untested remainder (stated, not papered over)

- Full-tree tar extract (forbidden: needs deleting the live tree).
- Two-binary restore into the LIVE paths (would overwrite lane outputs —
  V1 restores to `v1-*` scratch only; the live-path argv is E26-proven).
- G/I/T restores (mirrors re-verified in place; no copy exercised).

# V1 SMOKE TAIL COMPLETE
