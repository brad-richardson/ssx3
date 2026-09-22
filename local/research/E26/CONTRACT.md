# E26 CONTRACT — written before the first copy, rename or run

**Opened `2026-09-22T13:08:58Z`. Deadline `2026-09-22T21:08:58Z` (8 h).**

## What this lane is

E24 designed a boot and could not spend it (its checkpoint went red when a host
restart wiped all three protected build trees). E25 rebuilt the instrument and
proved the rebuild **bit-identical** to the lost pins. E26 **spends that one
designed boot** and takes first light on X.

E26 does not redesign the boot. E24 pre-registered the argv, the environment,
the 230-entry tiered watch set, the caps and the branches; this lane's job is
**fidelity**, and then read-only analysis of what comes back.

## Missions

| # | Mission | Bar |
|---|---|---|
| 0 | Verify-or-restore the instrument; capture preflight gate on all five pins; `PS2X_DIAG_SEMA` + argv paths | 5/5 pins pass with **zero re-pinning**, or table + stop |
| 1 | Spend E24's designed boot — **exactly one** | wall / rc / fate + every line of the 230-entry watch set; lease claim + release receipts |
| 2 | X first light, read-only, against this capture only | (a) where the guest's final start-code write lands vs the consumed feed; (b) does semaphore 36's sole signaller appear |

## Hypotheses (E24's, carried unchanged — nothing new is pre-registered)

- **H0** the successor descriptor node, the data region, the past-end extension
  and the staging buffer are **all silent** after the park → E23's KILLED
  verdict survives a watch set six times larger; the demand edge stays closed.
- **H1** **any** of them moves after the park → E23's verdict was
  watch-set-limited; the demand edge reopens with a measured bound.
- **H2** `[diag:sema]` shows signallers for 26/30/31/32 firing post-park →
  those four are live idle workers and MPEG is the only genuinely stuck chain.
- **H3** `[diag:sema]` shows `sub_003C1298` / `0x3c15c0` still never reached →
  semaphore 36's unique signaller never runs, confirmed dynamically with its
  `ra`; the second stuck chain is independent of MPEG and is its own X.

## Gates

| Gate | Rule |
|---|---|
| Fork | `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed (`HEAD`, `refs/remotes/fork/ssx3`, `ls-remote`) **FIRST**; `status --short` exactly `?? ps2_log.txt`. Any disagreement → table + stop. |
| Fork mutations | **ZERO** fork source edits, **ZERO** fork commits, **ZERO** pushes from this lane. |
| P-lane lease | Atomic claim, **exactly one** boot this brief, clean release. Lease occupied → table + stop, never wait. **No second boot for any reason** — no retry shape, no "quick check". |
| Fix gate | **STOP**, as E24 set it and designed the boot around it. Diagnose and table; never patch. |
| Preflight | E24's capture preflight gate **as written** on all five pins (runner, suite, both ELF copies, observer dylib). Zero re-pinning. |
| SSD link | The SanDisk USB link is flaky. Lane-critical SSD bytes need **2+ matching reads separated in time** before entering a gate. If `/Volumes/Extreme SSD` disappears mid-run → table + stop immediately; **do not improvise paths**. |
| E18 ABI / BINDING | Caller-owned synchronous dispatch; word0-only cbData; `v0` discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. Preserved by construction — E26 edits no source. |

## Byte caps

| Cap | Value |
|---|---|
| Internal reservation | **3 GiB** (E25's declared value). Floor **2 GiB** + **0.5 GiB** guard, unchanged. |
| SSD reservation | **16 GiB** in NEW `e26-*` paths; same floor + guard. |
| Evidence | `local/research/E26/` **text-only**, with the single established exception of the REUSED E21 observer dylib (52,472 B), carried by `cp -p` + re-sha exactly as E22/E23/E24/E25 carried it, because the capture driver loads it by path. |
| Boot caps | **Identical** to e22a/e23a/E24's design: wall 90 s, SIGTERM at 75 s (15 s terminate reserve), boot log 256 MiB, trace 96 MiB, function log 1024 MiB, aggregate 1536 MiB. Exactly one variable changes against e23a: the watch count. |
| Hygiene | `COPYFILE_DISABLE=1` on every SSD step. **Zero deletions.** No reclaim. |

## Declared up front: the boot label

E24 designed this boot under the label `e24a` and did not spend it. E26 spends
it under the label **`e26a`**, by the same hex-safe mechanical rename that
carried E23's driver into E24 and E24's tooling into E25.

Every element the brief enumerates as "exactly as designed" is preserved
byte-for-byte and is **proved**, not asserted, in `boot-fidelity.json`:

- **argv** — `[runner, ELF]`, identical strings;
- **environment** — identical `PS2X_*` key set and identical values, except the
  six values that are *output destinations* and are label-derived by
  construction (`PS2X_DIAG_PARK_DIR`, `PS2X_TRACE_SYSCALLS`, `PS2X_E4_DIR`,
  `PS2X_E21_PARSER_DIR`, `PS2X_E7_DIR`, `PS2X_FRAME_DUMP_DIR`);
- **watch set** — all 230 entries, same tiers, same addresses, same order;
- **capture window** — the `CAPS` and `ALLOCATED_CAPS` dicts, unchanged;
- **teardown** — atomic lease, function-log rename, release, post-release
  `pgrep`, unchanged.

Label-derived output names are not scientific content: e22a and e23a already
differed in exactly this way, and it is the mechanism that keeps the driver's
"refuse to overwrite" asserts meaningful and keeps this lane's SSD byte
accounting (`e26-*`, `*e26*`) honest. This is declared here, before the run,
rather than discovered in the report.

## Declared up front: how the boot-gate manifests are pinned

E24's `e24_prepare_probe.py` gates the boot against E24's own checkpoint chain.
That chain is **red** — it was taken when the runner and suite did not exist.
E26 does not re-run a 458-test chain that E25 already ran **today, green, on
byte-identical binaries**, and it does not gate against E24's red receipts.

`e26_prepare_probe.py` carries **one recorded intentional change**: it evaluates
E24's gate assertions, unchanged in content, against **E25's** fresh receipts
(`checkpoint-complete.json`, `checkpoint-suite.txt`,
`checkpoint-bindings-validation.json`, `observer-regression.json`,
`cadence.json`, `newbin-*-validation.json`), and re-verifies both binaries by
SHA itself. The change is recorded as data in `tooling-changes.json` with a
full diff in `tooling-diff.md`. The driver's own preflight still runs the
**full 458-test suite fresh** before the atomic claim — that gate is not
weakened, inherited or skipped.

## Strict order

Contract → fork gate (**first**) → instrument reuse → hex-safe rename + proof →
recorded tooling changes → Mission 0 restore + preflight → boot gate →
**ONE boot** → Mission 2 mine → fix gate → final audit → close.

## Amendments

**None declared at open.** Any amendment must be written here, with its reason,
before the step it authorizes.

# E26 CONTRACT TAIL COMPLETE
