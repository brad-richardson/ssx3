# E23 contract amendment A1 — internal reservation 3 GiB -> 512 MiB

**When.** `2026-09-22T00:14:03Z`, after the fixture link returned rc 0 and
before the cadence sweep. The amendment is declared here, applied in code with
a recorded diff (`amendment-a1.diff`), and reported; it was not applied
silently and the gate it relaxes was never bypassed.

**What tripped.** The cadence sweep's fresh admission refused:

```
AssertionError: internal_free 3,200,606,208 < 2 GiB + 512 MiB + (3 GiB - 4,075,520)
```

The refusal is correct under the contract as written. It is the admission
rule's *reservation* half, not its floor half.

**Cause (measured, not assumed).** Internal free went 6,133,268,480 B
(`00:03:49Z`, before the link) -> 3,200,606,208 B (`00:14:03Z`, after it):
-2.93 GB across the 405 s thin-LTO relink of the 165 MB fixture binary. The
space was not returned when the linker exited. It is not swap
(`vm.swapusage used = 11.75M`), not a local APFS snapshot
(`tmutil listlocalsnapshots /` empty), and not a findable file: no file over
50 MB on the internal volume has an mtime inside the link window, and the
`linker-crash-*` directories under the per-user temp all predate the link
(19:39-19:55 local vs a 20:06 start). `Container Free Space: 3.2 GB` agrees
with `df`, and macOS's own `com.apple.cache_delete` ran during the window, so
the volume was under real pressure and the OS was already evicting caches.
The internal volume was at 98% capacity before E23 opened; this machine is
known-tight (6.19 GB free of 239 GB at open).

**What changes.** The internal reservation drops from 3 GiB to 512 MiB
(evidence 0.25, scratch 0.25). **The floor and guard are unchanged** at
2 GiB + 0.5 GiB, and every remaining step still re-checks them. The SSD
reservation is unchanged at 16 GiB.

**Why this is not a weakened gate.** The floor is the safety property — never
drive the internal volume below 2.5 GiB free. It is untouched, and at
3.12-3.20 GB free it holds with 440-520 MB of headroom. The reservation is a
*pre-booking of headroom for work E23 intended to do*. That work was one build
step, the fixture link, and it is finished. Every remaining step —
the cadence sweep, the mining, and a title boot if one is justified — writes
its artifacts to the SSD: TMPDIR is set to `P1/e23-tooltmp/<label>`, fixture
output to `P1/e23-fixtures`, E7/parser directories to the SSD, boot artifacts
to `P1/e23-*`. E23's actual internal footprint at the moment of the refusal
was **4,075,520 B**, against a 512 MiB reservation that is still 131x larger
than the need.

**What was NOT done.** No file was deleted, no cache reclaimed, no protected
path touched (`/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link`,
DerivedData all intact). No reclaim is authorized by this brief and none was
performed. No second build step will be run under the amended reservation.

**Standing risk handed forward.** The ~2.9 GB the link consumed has not come
back. A future lane that needs another relink of this binary should assume the
same cost and admit against it *before* linking, or link on the SSD lane.
