# N8D7M12 Part 7A orchestrator gate — launcher A with one amendment (2026-09-24)

Read REPORT and worker commit `cf7788d5`; diffed `N8D7M12P5A/launch.py` (`287140bf…1334e`)
against the new launcher myself. The diff holds exactly the five brief changes: APK/runner
pins (`da9a41a8…`, `e5a3302c…`), `PS2X_GS_REPLAY_PKTSEQ=1` appended to the P5A env, two
marker strings, `--run run1|run2` scratch/lease/basenames, and a 41-row ordered `GB4_PKTSEQ`
extraction from the runner PID's logcat lines. Worker SHA `27d242fa…b6d6b`; self-check 37/37.

**Orchestrator amendment:** the Odin reads `status: 3` (discharging) with `AC powered: true`
at 100% (charge limit), which the P5A gate (`status in (2,5)`) would refuse. The launcher now
also accepts status 3 only when AC-powered and level >= 90. Released SHA
**`5983f315982ea08eb41c8fe0593e57e7b59c272faad7ae516a4300ac78b934aa`** (double read,
`py_compile` OK). Checker now reads 36/37: its sole FAIL `diff_only_listed_changes` is this
amendment. **Verdict A; Part 7B released at that SHA.**
