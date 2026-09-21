# E22 experiment contract — written before any copy, build, or boot

| Contract | Bound / observable |
|---|---|
| Opened | `2026-09-21T23:05:22Z`. Time box 8 h; deadline `2026-09-22T07:05:22Z`. |
| Mission | (1) checkpoint re-verify; (2) ONE `stdbuf`-free observed title boot closing e21a's per-call parser-observation gap; (3) X-signal hunt (candidate second-demand edges, static + the one boot); (4) strict fix gate. |
| Hypothesis | The e21a parser-observation gap is caused solely by `stdbuf` in the boot argv (E21's controlled proof). Executing the runner directly with `DYLD_INSERT_LIBRARIES` preserved will produce a closed per-call parser receipt inside the title window. |
| Alternatives | (a) argv was the only cause → closed parser receipt with 1:1 backend counts; (b) a second cause exists (runner re-exec, posix_spawn, SIP/hardened-runtime rejection, DYLD stripping) → observer files still absent or receipt refuses; (c) observation lands but the title window shows the same one-callback park. (a)/(c) and (b) are separable by the receipt itself. |
| Observable | Per-call parser timing inside the title window joined to the guest feed: parse/send/receive call sequence, offered/consumed bytes, packet emission (or its absence) against the single 5,040 B AddBs, with a real `# E21 PARSER CLOSURE` footer. |
| Strict order | Checkpoint (unloaded 458/458 + observer-loaded 458/458 with the REUSED dylib) → probe gates → ONE boot → mine/join → X-signal hunt → fix gate. Any red before the boot → table and stop, no boot on red. |
| Instrument | E21's proven `e21-parser-observer.dylib` (SHA256 `e4d88fdc…b38e6be`) REUSED by copy + re-sha; no rebuild unless the re-sha misses. Its env names (`PS2X_E21_PARSER_DIR`, `PS2X_E21_PROOF`) and footer prefix (`# E21 PARSER CLOSURE`) are properties of that binary and are carried verbatim. E19/E20 dylibs are never loaded. |
| Receipt verifier | E21's `e21_parser_receipt.py` copied to `e22_parser_receipt.py` under a functional-identity proof (normalized diff byte-empty); applied to every observer run. |
| Fix gate | Implement ONLY if the diagnosis isolates ONE edge with a minimal ABI-preserving change + its own fail-before + full regression. Policy invention (demand shapes the firmware's true behavior is unknown for) is excluded. "Guest never sends more without X" → NAME X and STOP. |
| Probe budget | ONE title boot; ONE lease claim (atomic `/tmp/ssx3-p-lane-lease`, never waited, clean release, post-release `pgrep`). Lease occupied at any check → table and stop. |
| Mutations | No CSV/regen (regen need = stop). No fork behavior commits except through the fix gate. No probe code changes to chase X (static + the one boot's trace only). |
| Preserved ABI | Caller-owned synchronous dispatch; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation; stream behavior unchanged. No CSV, main, scheduler or stream-callback edits. |

| Byte caps declared up front | Value |
|---|---|
| SSD lane | ≤16 GiB total in NEW `e22-*` paths under `/Volumes/Extreme SSD/ps2recomp-spike/P1` (tooltmp 8 GiB, fixtures 2 GiB, probe 1.5 GiB, reserve 4.5 GiB); floor 2 GiB + 0.5 GiB guard. |
| Internal | ≤3 GiB delta (evidence 0.5, observer/scratch 0.25, reserve 2.25); floor 2 GiB + 0.5 GiB guard. Internal free at open is the scarce resource — large artifacts stay on the SSD. |
| Elsewhere | 0 growth. No reclaim, no deletion. `COPYFILE_DISABLE=1` on every SSD step. |
| Accounting | `st_blocks × 512` including ExFAT directory/AppleDouble allocation, E22-owned paths and positive fork source/Git growth. |
| Process caps | Bounded wrapper: wall per step, stdout 16 MiB (1 MiB reserve), tooltmp 8 GiB (512 MiB reserve), fixtures 2 GiB (64 MiB reserve), poll 0.25 s. Suite wall 60 s, stdout 4 MiB, scratch 32 MiB. |
| Probe caps | One launch; wall 90 s / TERM 75 s; 1,000,000 syscall lines; aggregate 1.5 GiB; boot 256 MiB, trace 96 MiB, function 1 GiB; E4 12/64 MiB, park 32/128, frames 32/64, E7 8/64, parser 16/64; 8 MiB reserve. `REPORT_ALL=1`. |
| Protected | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link`, DerivedData; 1,725 protected build hashes. Never reclaimed, never rebuilt. |

| E22 CONTRACT TAIL COMPLETE | Written before the first copy, build, or boot; caps and the one-boot/one-lease rule fixed in advance. |
|---|---|
