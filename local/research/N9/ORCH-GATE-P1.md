# N9 Part 1 orchestrator gate — fork branches sorted and pushed (2026-09-24)

Read REPORT, the two classification diffs and commit `be2b3cb4`. The build clone's 34 superproject
hunks are diagnostics (each symbol grepped against PS2Recomp `959f4ea`'s backend call surface: zero
hits); the fork's `ssx3` already held the product fixes (G26, Turnip HAL loader, shims, G28). Granite
had one product hunk, G18 (update templates gated on `supports_descriptor_buffer`; the Adreno 830
legacy flush path needs it), and one logging hunk. Mac shadow build against the new tips: suite
593/593; runner-dir check empty.

Verified before pushing: paraLLEl-GS `3b1ca9e..ssx3-next` = the 10-line wave64 fix (`495cb69`) + the
Granite gitlink (`963cb57`); Granite `46db18a8..ssx3-next` = G18 only (`166ba21a`); all fast-forwards.

Pushed (fork URLs only; no upstream contact):
| Repo | Branch | SHA |
| --- | --- | --- |
| brad-richardson/Granite | `ssx3` | `166ba21a` |
| brad-richardson/Granite | `wip/ssx3-n9` (new; diagnostics) | `24fb882f` |
| brad-richardson/parallel-gs | `ssx3` | `963cb57` |
| brad-richardson/parallel-gs | `wip/ssx3-n9` (new; diagnostics, Granite → wip) | `26327117` |
| brad-richardson/PS2Recomp | `ssx3` (+ N8B1 `f5e6378`, `fb11e18`) | `fb11e18` |

The older `wip/ssx3-snapshot` branches stay untouched (no force-push). **Verdict A; Part 2 released**:
one APK from these tips, live Odin route with no `PS2X_PGS_*` env.
