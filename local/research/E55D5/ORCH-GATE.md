# E55D5 orchestrator gate — PASS, one changed pad entry

Worker commit `e80163eb` (`Orchestrated-By: opencode`) used the
released E55D5 boot SHA `cb9ba39b770270692baeccad6523a838165041c17df6d631acb4fe45ffcb293e`
and comparator SHA `e16d01819b03b8b8c40209886dd5df9e047e2285bd3cdbec26cb0a7ea4c51307`.
The brief changed exactly one I26-FAST route entry, `33517:cross:200`
to `33517:square:200`; all other entries and pinned runner/ISO/ELF/codegen
were held. One B1 Mac mini boot ran; no source/build/device action.

| Gate check | Orchestrator result |
| --- | --- |
| Run bounds | B1 `target`, 2057 consecutive hash rows; 4000 complete probe lines through vsync2055, proving flush past tick2053; no cap/truncation. A1 baseline has 2058/4000. Both complete through tick2053 |
| Ordered first difference | Independently parsed full A1/B1 logs: first 3908 pad records byte-identical; first difference is shared seq3909/ord3905 at vsync2010, port0. Metadata including slot/address/len/ok is identical; Cross `…ffbf…` versus Square `…ff7f…` in the 32-byte payload. Windowed record counts 3996/3996 |
| Hash first difference | Hash rows 1..2010 identical. First changed row at tick2011 (`eeCycle`, `rdram`, `combined`); both have all 2053 rows in the comparison window |
| Cards/HID | Initial/final card manifest SHA `f9401596…feccb9ce` on both runs; no card files or getdir/mcread writes. Full 227-row HID list has only the known internal Apple NAND temperature `Controller`, no gamepad. Pre/postrun lists agreed on that match |
| Independent replay | Orchestrator reran the revised comparator on retained gzipped A1/B1 logs: `PASS pad_b_discriminated`, seq3909/vsync2010 and hash tick2011. Independently decompressed B1 logs; sizes/SHA match `excerpts.txt`. Boot self-check 11/11 and comparator self-check 21/21 |
| Scope/cleanup | Worker commit contains named brief/scripts/text receipts, no binary/game data; private fork runner-dir diff vs `14b1e5cb` empty. B1 runner PID63200 absent and both mini leases free. `git show --check` flags trailing spaces in raw HID command output only |

Verdict: **PASS** for this bounded one-change pad discriminator. The
ordered guest write changes in the predeclared pulse window after an
identical prefix, and the VBlank hash changes on the next tick. This
supports that the pad script reaches the guest write hook and that the
hash tap observes downstream state. It does not prove all future runs
are deterministic, isolate every later state change, or exercise card
getdir/mcread paths. The 123.838 s diagnostic wall is not a speed
number. Next E work: identify a real reachable card read/directory
path and predeclare a separate one-change card comparison.
