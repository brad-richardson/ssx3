# E28 CONTRACT — written before the instrument copy, the open admission and the boot

E28 is a **guest-half confirmation** lane. E27 closed the static case; E28
spends **one** boot (`e28a`) on the **EXISTING byte-identical binary** to
confirm or refute E27's guest-side predictions. **Zero fork source edits, zero
builds, zero relinks.** Host-side `MPEG.cpp` instrumentation (`getMpegPicture`
entry logging, `pending.lock()` results, `completeExternalWait` callers) is
**E29's lane and is explicitly out of scope here.**

## Pre-registered hypotheses — E27's, carried verbatim, NOT authored by E28

E27's Mission 3 named the falsifiable set; the E28 brief pre-registered it.
E28 registers **nothing new**.

| # | Prediction (E27's words, as the brief carries them) |
|---|---|
| **P1** | the kind-1 queue head reads `0xd49b14` with a byte count ≥ **14,364** from the feed onward and **NEVER** changes to end of run |
| **P2** | `0xd49b18` still reads `0x0100381c` at the park |
| **P3** | **ZERO** guest stores to `0xd49b14` / `0xd49b18` after the feed |
| **P4** | `[MPEG:GetPicture]` ×1 and `[MPEG:feedES]` ×1 in the new boot log (re-confirmation; the counters cap at 32, so 1 is a true count) |

## The named limit E28 inherits and designs around

E26's limit still binds: **`diagWatchEmit` fires on GUEST STORES ONLY.** A
prediction whose at-park **value** has no store behind it is **unobservable
with the existing instruments** — no store, no emission, no value. Such a row
is tabled as `unobservable-as-designed` **with its reason**, and the observable
halves stand on their own. E28 invents no instrumentation and edits no fork
source.

## Gates

| Gate | Rule |
|---|---|
| Fork | `3adc0478` triple-agree **FIRST**; `status --short` exactly `?? ps2_log.txt` or table + stop. Zero fork edits / commits / pushes. |
| P-lane lease | **ONE** title boot (`e28a`), claimed per the standing protocol, released at end. **No second boot for any reason.** |
| Capture driver | E26's, carried by **mechanical hex-safe rename ONLY** (`e24a→e26a` rule, now `e26a→e28a`). The **ONLY** intentional change permitted is the **watch set** (new addresses + tiers), recorded with before/after receipts. |
| Preflight | As written: all pins, **zero re-pinning**, fresh 458-test suite. |
| Fix gate | **STOP** — diagnose and table, never patch. |
| E18 ABI / BINDING | Preserved by construction: no source touched at all. |

## Byte caps and reservations

| Bound | Value |
|---|---|
| Internal reservation | **3 GiB**; floor 2 GiB + guard 0.5 GiB, unchanged. E28 runs no build step, so the reservation is **declared, not consumed**. |
| SSD | NEW `e28-*` paths ≤ **16 GiB**; same floor + guard. |
| Evidence | `local/research/E28/` — **text only** (the one binary is the reused E21 observer dylib, carried by `cp -p` + re-sha, never rebuilt). |
| Hygiene | `COPYFILE_DISABLE=1` on every SSD step; **zero deletions**. |
| Time box | 8 h. |

## Standing SSD rule (the link is PROVEN pattern-dependent corrupt)

Every lane-critical SSD byte needs **2+ matching reads separated in time** AND
**corroboration against pinned committed bytes**. The two e26a captures are
**re-sha'd against E26's committed pins before they are mined**. If
`/Volumes/Extreme SSD` disappears mid-run: **table + stop immediately**, do not
improvise paths.

## Strict order

Fork gate (**first**) → hex-safe tooling carry + proof → CONTRACT → instrument
reuse → open admission → **Mission 0** (verify-or-restore, two passes separated
in time, restore gate, capture preflight, e26a capture re-sha) → **Mission 1**
(static slot-address derivation; **derived → arm; underivable → table + STOP
the boot, no blind watches**) → boot fidelity proof → probe gate → **ONE boot**
→ **Mission 2** mine + P1–P4 verdict table → fix gate → close.

## Actions taken before this CONTRACT was written, declared

Two, both text-only and neither lane-critical: (1) the **fork gate**, which the
brief orders **FIRST** and which is read-only on the fork; (2) the **hex-safe
mechanical carry** of E26's 18 tools into `local/research/E28/`, which is a
pure text operation inside the evidence directory and touches no build, no
lease and no SSD capture. No copy of the instrument, no admission, no boot and
no lease claim preceded this file.

## Amendment

**None declared.**

# E28 CONTRACT TAIL COMPLETE
