# E24 boot design — the extended-watch boot, designed, driven and GATED, not spent

**Status: NOT SPENT.** E24's checkpoint is RED — the three protected build
trees were wiped by the host restart, so `ps2EntryRunner` does not exist
(`env-audit.json`, `checkpoint.json`). The brief's mission 1 says *any red →
table + stop, no boot on red*. The design and the driver below are complete
and gated; the next lane spends the boot the moment a build is restored.

## What the boot must measure

| # | Question | Instrument |
|---|---|---|
| 1a | Does the SUCCESSOR descriptor node at `0x548880` move post-park? E23's NAMED residual: the head advanced `0x548800 = 0x548880` at boot-log line 10,168 and that node was **not** watched, so its silence was vacuous. | extended `PS2X_DIAG_WATCH` |
| 1a' | Does the `0xd48748+` data region or the staging buffer refill post-park? | extended `PS2X_DIAG_WATCH` |
| 1b | What do thread 4's ~300 wakes per 5 s touch? | watch set + `PS2X_DIAG_SEMA=1` |
| 2 | Who is meant to signal semaphores 26/30/**31**/32/36, and what are the signallers doing instead? | `PS2X_DIAG_SEMA=1` |

**E24 has already closed 1b and most of 2 from retained e23a artifacts** —
see `sema-mine.json` and `signaller-closure.json`. What the boot still owes is
**1a** (needs the new watch set) and the **waker `ra` per signal** (needs
`PS2X_DIAG_SEMA=1`, which the always-on park tally cannot supply because it
records the syscall stub pc, not the caller).

## The watch set — tiered, because the per-store scan is linear

`diagWatchEmit` (`ps2_runtime.cpp:1309`) is called from **every** guest store
(`WRITE8/16/32/64/128` in `ps2_runtime_macros.h`, and `PS2Runtime::Store*`) and
loops over the whole watch vector. Watch count is therefore a direct multiplier
on per-store cost, and a naive full cover of the 5,036 B body would be 630
entries. Full receipt in `watch-set.json`.

| Tier | Range | Stride | Entries | Guarantee |
|---|---|---:|---:|---|
| descriptor node array | `0x548800`-`0x5489ff` | 8 | 64 | **complete** — current node, the successor node (E23's residual), and two more at the observed `0x80` stride |
| data region head | `0xd48748`-`0xd48847` | 8 | 32 | complete for the first 256 B |
| data region body | `0xd48848`-`0xd49a73` | 128 | 37 | any **contiguous run ≥ 121 B** is caught (stride 128 − window 8 = 120 B max gap); an isolated shorter write inside the sampled span is **not** |
| data region tail | `0xd49a74`-`0xd49af3` | 8 | 16 | complete |
| past-end extension | `0xd49af4`-`0xd49b73` | 8 | 16 | complete — E24 measured the feed ends in 15 zero bytes with **no terminating start code**, so a continuation writes exactly here |
| staging buffer | `0xdc8340`-`0xdc843f` | 8 | 32 | complete for the first 256 B (E23 watched only the first 8 B) |
| carried from e23a | — | — | 33 | the non-producer set plus `0x5487c0`, `0x587b28`, `0x587b78`, `0x587b7c` |
| **total** | | | **230** | e23a ran 37 |

**Residual this design does NOT close, stated up front:** an isolated write
shorter than 121 B landing inside `0xd48848`-`0xd49a73` and touching none of
the sampled windows would still be invisible. A bulk refill cannot hide there;
a single stray word can. That is a strictly smaller residual than E23's
(an entire unwatched 128-byte descriptor node), and it is a deliberate trade
against the scan cost below — not an oversight.

## Cost model — why 230 and not 630

The only calibration available is e22a → e23a, which changed the watch count
and nothing else about the boot shape:

| Boot | Watch entries | span-complete |
|---|---:|---:|
| e22a | 29 | 7.61 s |
| e23a | 37 | 8.30 s |

Fitting `T = base + k·W` gives `k = 0.0863 s/entry`, `base = 5.11 s`.

| Watch entries | predicted span-complete | post-park window under the 75 s SIGTERM |
|---:|---:|---:|
| 37 (e23a, actual) | 8.30 s | 66 s (actual) |
| **230 (this design)** | **~24.9 s** | **~50 s** |
| 630 (full body cover) | ~64 s | ~11 s |

A two-point fit on two runs is indicative, not measured. It is used only to
**size** the list conservatively, and the driver records the actual
span-complete time so the next lane can refit. The caps are otherwise
**identical to e22a/e23a** (wall 90 s, SIGTERM at 75 s, same byte caps) so the
comparison against e23a stays clean with one variable changed.

## The second instrument — already compiled in, no rebuild

`PS2X_DIAG_SEMA=1` (`EeScheduler.cpp:156`) emits one line per semaphore signal
and wait with **id, count transition, waiters before/after, waker thread,
waker pc AND `ra`, inInt, iSafe, invocation kind/depth/cbFunc, target waiter,
result**. `PS2X_DIAG_SEMA_S0=1` adds the object pointer on unknown-id waits.
Both are cached static env checks — nothing is printed when unset, so the
proven binary needs no rebuild and no fork edit.

Expected volume from e23a's park tallies: ~10,200 waits + ~10,100 signals
≈ 20k lines, ~4 MB against a 256 MiB boot-log cap. Negligible.

## Gates (the gate this lane needed and E23's driver lacked)

`e24_capture.py` refuses to claim the lease unless, in order:

1. every protected binary named in the checkpoint is **present and sha-equal**
   — e23a's driver asserted sizes/hashes but assumed the files existed, and an
   absent tree is exactly what stopped E24;
2. the P-lane lease is absent (occupied → table and stop, never wait);
3. `pgrep -x ps2EntryRunner` rc 1, before and after preflight;
4. fresh T13 pre-claims + the full suite green at the pinned count;
5. `stdbuf` absent from argv and `argv0_is_runner` true (E22's finding);
6. hex-safe file-hash preflight (errata E23-E1) before the atomic claim.

One boot, one atomic claim, clean release, post-release `pgrep`.

## Pre-registered branches — both decisive

| Outcome | Reading | Consequence |
|---|---|---|
| Successor node, data region, past-end and staging buffer **all silent** after the park | E23's KILLED verdict survives a watch set six times larger, now covering the whole descriptor node array and both buffers | The demand edge stays closed and X stays upstream. E23's named residual is closed, not merely inherited. |
| **Any** of them moves after the park | E23's verdict was watch-set-limited | The demand edge reopens with a measured bound ("re-ask while the producer makes progress"), and the next lane gets a concrete fail-before. |
| `[diag:sema]` shows a signaller for 26/30/31/32 firing post-park | those four are live idle workers, as E24's static half already indicates | MPEG is the only genuinely stuck chain. |
| `[diag:sema]` shows `sub_003C1298`/`0x3c15c0` still never reached | semaphore 36's unique signaller never runs, confirmed dynamically with its `ra` | the second stuck chain is independent of MPEG and is its own X. |
