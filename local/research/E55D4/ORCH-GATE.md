# E55D4 orchestrator gate — PASS, bounded A/A repeatability

Worker commit `df99252f` (`Orchestrated-By: opencode`). The released
boot script SHA was `cbd08f96990480e2ce058f4e0fc34a24060e3b664cfaa1fee425b5938fa904f8`.
No source change or build occurred in this part. Two sequential Mac mini
boots used the same pinned runner, game inputs, I26-FAST vsync pad route,
deterministic flag, fresh empty card directories and slot-1 lease.

| Check | Orchestrator result |
| --- | --- |
| Bound / flush proof | Both `target`; 2058 consecutive hash rows; 4000 complete probe lines each, through vsync 2055; no cap or truncation |
| Common window | Hash rows 1..2053 equal field for field, 2053/2053. Ordered pad guest-write lines at vsync ≤2053 equal including payload, 3996/3996; no first difference |
| Card state | Both initial/final manifest SHAs `f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce`; no card files or card read/directory writes occurred |
| Host HID | Full saved 227-row `hidutil` list has one `Controller` match, `AppleANS3CGv2Controller NAND CH0 temp`, vendor usage page 65280/usage 5; no gamepad row. In-run HID blocks were identical. The comparator's row classifier flags no input device |
| Independent rerun | Orchestrator decompressed all four gzip logs; bytes and SHA-256 match `excerpts.txt`. In a temporary copy with result probe paths remapped, reran comparator: `PASS identical_to_tick_2053`, 2053 hashes and 3996 pad lines. Boot self-check 10/10 and comparator self-check 21/21 |
| Scope | Worker commit has named brief, scripts and text receipts only, correct trailer. `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` on the private fork is empty. Mini slot 1 subsequently passed to N8D7L; slot 2 free at gate read |

Verdict: **PASS** for repeatability of this executed A/A path through
guest tick 2053. This does not prove full determinism: getdir/mcread did
not execute, no card-file mtimes were exercised, and absence of transient
physical input is not proved by a postrun HID list. The boot script's
original broad HID substring flag remains in the run JSON; the saved
full-list row check adjudicates that false positive. Diagnostic wall times
are not speed measurements.

`git show --check` reports trailing spaces in the raw `hidutil list`
receipt. They are command output, not source-format defects; preserving
its original columns lets the classifier reparse the evidence. Next E
step: predeclare a single changed vsync-pad entry against this A/A
baseline and stop at the first changed ordered guest write. Card-path
coverage needs a separate one-change run.
