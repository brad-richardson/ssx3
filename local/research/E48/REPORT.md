# E48 report — the `0x3b1140` breaker, and the stray glyphs

Brief `local/muse/prompts/E48.md`. Tables + receipts; the orchestrator
decides. Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/E46/REPORT.md` (Part 2 §(1)). Worker: Claude Code
(Opus pane), 2026-09-23, Mac mini.

## Outcome

- **The hypothesis is refuted.** Node `0x548840` is not a UI element.
  It is the one **MPEG picture node** of the startup-movie codec object
  `0x587b00` (vtable `0x456850`, in section
  `.gnu.linkonce.d._vt$23PS2_SONY_CODEC_INTERNAL`, the class that calls
  `sceMpegGetPicture@0x402A10`). Each startup movie's Open builds it,
  its Close frees it, and malloc reuses the address for the next
  movie. With the breaker OFF, the node, its list and the codec are
  all gone by tick ~255. Their memory then belongs to unrelated heap
  users. No codec or holder code touches it at Select Character, and
  the stray glyphs are still there (B2 frame at tick 1363).
- **Why a correct release blacks the screen: two bugs cancel out.**
  The guest ends a movie on either of two signals:
  1. its own end check `0x402b38` (reads word `[[mpeg+0x40]+0]`;
     nonzero → `0x3b1050` returns "no picture"), or
  2. running out of pool nodes (the one-node pool's alloc
     `0x3b10d0` returns 0 → no picture).

  The runtime's MPEG HLE never sets that end word. Its only write is
  0 (`MPEG.cpp:2939`), and `0x402b38` isn't bound to any HLE in
  `ssx3.toml`, so the check never fires. When the release is skipped,
  the node never goes back to the free list. The 2nd picture request
  then finds the pool empty, and **that** is what ends each bypassed
  movie today. With the release working, the pool never runs dry.
  The first startup movie then "plays" blank pictures at 29.97 fps
  forever: **2,493 alloc→SetPicture→release cycles in 120 s** (one
  every 2 ticks from tick 248 to 5240). No 2nd movie starts (no
  further MPC CD reads), so the frontend never starts, and the
  display stays black (`fd889dc5`) from tick 246.
- **The unlink itself is clean.** It moves the node from the active
  list (`0x587b18`) to the free list (`0x587b20`) of a live codec.
  Every store is in bounds, and the watch on guest `0x8..0xf` saw no
  write after tick 52. Nothing is corrupted.
- **Correction to E46 (`3→2→1→0`):** each of the 3 calls hits a
  *fresh* node at the same address. Its refcount is 1 every time
  (set by alloc `0x3b1130`; the constructor zeroes it at `0x3b0838`).
  That makes 3 × `1→0`, one per movie, not one node counting down.
- **Stray glyphs:** they don't trace to this node or its list (see B2).
  Their cause is elsewhere and is still open.

## Code read (`ee-at` / `ee-xref` / `ee-func` / `ee-label`)

Labels: `ee-label` knows only `0x402a10 = sceMpegGetPicture` (from
the ssx3.toml stub list). Everything else is unknown and described by
address.

### Codec object (a0 = `0x587b00`, vtable `0x456850`)

| Slot (vt+) | Target | What it does (by reading) |
|---|---|---|
| +0x0c | `0x3b09a0` | Close/dtor: vtable ← `0x456850`; frees the buffers at +0x2c/+0x78; drains the **active list** (sentinel +0x18) and the **free list** (sentinel +0x20). Each node is unlinked, its links poisoned to `0xb`, then `0x3b08e0(node,3)` (node dtor + free) |
| +0x14 | `0x3b0c58` | Open: [+0x10]=[+0x14]=0 … loops `[[a1]+0x10]` times: allocate a node (`jalr [0x509430]`), construct it with `0x3b07f8(node,w,h)`, push it on the free list +0x20 (`0x3b0e7c..0x3b0e8c`); then calls `0x402708` (`sceMpegInit` per ee-label) |
| +0x1c | `0x3b1050` | Next picture: loop { if a1: release(a1) via vt+0x34; **if `0x402b38(this+0x30)` ≠ 0 → return 0**; a1 = `0x3b0fb8(this)` } while `[this+0x10] < s1` |
| +0x24 | `0x3b0fa0` | returns `[this+0x10]` (pictures fetched) |
| +0x34 | **`0x3b1140`** | Release(node): `rc=[node+0x10]-1`, store it; if >0 return rc; else unlink from the active list and append to the free list |
| (direct) | `0x3b0fb8` | alloc `0x3b10d0(this)` → node s1; image ← `[s1+4]` (+0x10 or +[img+0x10]); `sceMpegGetPicture(this+0x30, image, size)`; `[this+0x10]++` |
| (direct) | `0x3b10d0` | Alloc: pop the free-list head (+0x20); **if the list is empty return 0**; poison its links to `0xb`, append it to the active list (+0x18), `rc=1`, return the node |

Node layout (from `0x3b07f8`, `0x3b10d0`, `0x3b1140`): +0x0 = 2,
+0x4 image object (`0x3b2a68`), +0x8 next, +0xc prev (the link lives
at node+8), +0x10 refcount. Sentinels: active `0x587b18/1c`, free
`0x587b20/24`. Pool size = 1 (one constructor call per Open in both
boots).

### The unlink in `0x3b1140` (at rc 0)

| pc | Store | Meaning |
|---|---|---|
| `0x3b1150` | `[node+0x10] = rc` | refcount |
| `0x3b116c` | `[prev+0] = next` | unlink from the **active list** (head `codec+0x18`) |
| `0x3b1174` | `[next+4] = prev` | |
| `0x3b1178/7c` | `[node+8] = [node+0xc] = 0xb` | poison |
| `0x3b1184` | `[freeTail+0] = node+8` | append to the **free list** (head `codec+0x20`) |
| `0x3b1188` | `[codec+0x24] = node+8` | |
| `0x3b118c/90` | `[node+8] = codec+0x20`, `[node+0xc] = old tail` | |

### Who creates and points at `0x548840`, and the caller chain

| Role | Site |
|---|---|
| Heap block | allocator `sub_003204B8` (`0x3204c4` writes the heap link at node+0) |
| Constructed | `0x3b07f8` called from Open `0x3b0e68` (ra `0x3b0e70`) |
| Codec lists | free list `0x587b20` (Open) → active list `0x587b18` (alloc `0x3b111c`) |
| Holder `0x587b80` | `+0xc = node` at `0x254c7c` (in `0x254c48`, "set picture": also `+0x10 = node+4`; reached from `0x253920`) |
| Release caller | `0x254dc0` (vtable-called, `.rodata 0x4802a4`): wait loop on `[[a1+0x10d8]+0x94]`, then if `[s0+0xc]` is set: `0x3b0680([s0], pic)`, then `[s0+0xc]=0` (`0x254e08`) |
| `0x3b0680` | `a2=[a0+0x14]` (the codec) → `jalr vt+0x34` at `0x3b0698` → `0x3b1140`; caller ignores the return |
| Other `0x3b0680` callers | `0x253650` (`sub_002535F8`), `0x254878` (`sub_00254410`); park `first_ra`/`last_ra` of `0x3b0680` = `0x254e08` in both boots |
| Picture fetch | `0x3b0600` → `jalr vt+0x1c` = `0x3b1050` (ra `0x3b0664`) |

## Boot B1 — breaker ON (`codegen-ssx3-e463b1140`)

`python3 local/research/E48/e48_boot.py --build on --label e48b1
--wall 120 --snap 1 --script "<E33 route>"` (E33 route string from
`local/research/E33/REPORT.md` §Vsync-clock script; wrapper sets
`PS2X_SKIP_MOVIE=1`, `PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_DIAG_PARK=1`,
`PS2X_DIAG_WATCH=` 14 windows: node +0..+0x20, sibling-node links
`0x548788/7c8/808/888`, codec `0x587b10/18/20`, holder `0x587b80/88`,
guest `0x8`). Slot 1, no peers. rc 0, 120.2 s, tick 5240.

Ticks: `[diag:watch]` lines carry no tick, so each is stamped with
the last `[frame:dump] tick=` line before it ("tN" = between frames N
and N+1).

| Tick | Event (watch pc) |
|---|---|
| t246 | movie 1 MPC read (lbn `0x13ba33`); codec ctor (`0x3b0954..90`: sentinels self-linked); Open: node ctor (`0x3b0820..60`), push free (`0x3b0e7c..8c`) |
| t248 | alloc #1 (`0x3b10f8..0x3b1130`, rc=1), count=1 (`0x3b103c`); SetPicture `[0x587b8c]=0x548840` |
| t249 | **release #1 executes**: rc=0 (`0x3b1150`), unlink active, relink free (`0x3b1184..90`); holder `+0xc=0` (`0x254e08`); **alloc #2 returns the same node** (rc=1, count=2), SetPicture again |
| t253, t255, … | same cycle; count increments every 2 ticks |
| t5240 (end) | count `0x9bd` = 2493; still movie 1 |

| Counter (park hot_pc) | B1 |
|---|---|
| `0x3b1050` next-picture / `0x402b38` end check / `0x3b10d0` alloc / `0x402a10` GetPicture / `0x254c48` SetPicture | **2493 each** |
| `0x3b1140` release / `0x3b0680` / `0x254dc0` | 2492 each |
| `0x3b0c58` Open | 1 |
| `0x3b09a0` Close | **0** |
| MPC (`4d504368`) CD reads | 1 (movie 1 only); 14 CD reads in total after it, then none |
| missing-target lines | 0 |
| writes to `0x8..0xf` after t52 | 0 |

`0x402b38` and `0x3b10d0` counts are equal. `0x3b1050` returns
before alloc whenever `0x402b38` is nonzero, so it returned 0 on all
2,493 calls.

Park snapshot at SIGTERM (`park-e48b1.txt`): thread 1 (main) Ready
at `ra=0x377b6c`; thread 5 (entry `0x382740`, pri 5) Running at
`ra=0x382ae8`; threads 2/3/4/6 in sema waits (26/30/31/36). No thread
is parked or deadlocked. The main loop is alive and draws each blank
picture. **Why black:** the displayed image is the blank MPEG frame the
HLE writes when no frames were decoded (`writeBlankMpegFrame`, since
the bypass decodes none). Frames `fd889dc5` from t246 to t5240 (every
snap; `frames/e48b1-black-t1861.png`, the same 9448-byte black as
e46a/e46c).

## Boot B2 — breaker OFF (canonical `codegen-ssx3` = E46g)

Same wrapper, `--build off --label e48b2`. Slot 1 (E47's runner started
later in slot 2; own PID checked, gone). rc 0, 121.0 s, tick 3610.

The node's life over the boot:

| Tick | Event |
|---|---|
| t0 | heap: `[0x548840]` / `[0x587b80]` written by the allocator `0x3201a8/f0` (pre-movie use of the same heap) |
| t246 | movie 1: codec ctor, Open (1 node), alloc #1 (rc=1), SetPicture |
| t248 | `missing-target 0x3b1140` (skipped); holder `+0xc=0`; **alloc #2 returns 0** (count → 2 with no list or node writes, which is the empty-list branch at `0x3b10dc`) |
| t249 | holder vtable `0x480270→0x4802b0` (`0x254894`), holder block freed (allocator `0x3204dc` writes its heap link); **Close**: node unlinked from active, poisoned `0xb`, then `0x3b0908..1c` (`+4=0`, links=7), freed (`0x3204c4`); codec sentinels poisoned 7 (`0x3b0ac0..d0`); movie 2 MPC read (lbn `0x13b5b1`), fresh codec at the same address, fresh node at `0x548840` |
| t251–252 | movie 2: same pattern (skip, null, Close) |
| t253–255 | movie 3 (lbn `0x15107b`): same |
| t257+ | frontend frames (`34df101e` at t267, `frames/e48b2-t267.png`) |
| t257–1399 | the node words (and codec `0x587b10`) are written only by **`sub_003A3280`** (`0x3a3a70..aa8`, per-frame 12-byte vec3 copy + float scale) and the allocator: ordinary heap reuse |

| Counter (park hot_pc) | B2 |
|---|---|
| `0x3b1050` / `0x402b38` / `0x3b10d0` / `0x402a10` / `0x3b0600` | 6 each (2 per movie: one node, one null) |
| `0x254c48` SetPicture / `0x254dc0` / `0x3b0680` | 3 each |
| `0x3b0c58` Open / `0x3b09a0` Close | 3 / 3 |
| missing-target | `0x3b1140` × 3 only |

Park at SIGTERM: all 6 threads in sema waits (main on sema 29,
`ra=0x31aa8c`).

**Stray glyphs vs the node:** `frames/e48b2-sc-t1363.png` shows Select
Character with Zoe **and** the stray button glyphs, D-pad and L1/R1
boxes in the top-left and bottom-left corners. At that point
(t1247–1399) nothing from the codec, node, list or holder touches the
watched words. The codec was closed at t255, its sentinels poisoned
(7) and its memory reused. The glyphs therefore can't come from a
live node or list of this codec. I didn't run the E43 draw census:
there is no live list left to join against. **Not traced:** which
draw records the glyphs are.

## Hypothesis verdict

| Claim | Verdict | Evidence |
|---|---|---|
| `0x548840` is a UI element | **Refuted** | MPEG picture node of the `PS2_SONY_CODEC_INTERNAL` codec; ctor `0x3b07f8`, image via `sceMpegGetPicture` |
| Skipped release leaves it drawn → stray glyphs | **Refuted** | Close frees the node either way (B2 t249/252/255); glyphs present in B2 with no codec activity after t255 |
| Enabled release corrupts something built differently earlier | **Refuted** | the unlink is in bounds on a live codec; the effect is control flow (the movie never ends), not corruption |
| (New) the skipped release is what ends each bypassed movie; the guest's own end check never fires because the HLE never sets `[[mpeg+0x40]+0]` | **Supported** | B1 2493× `0x402b38` = 2493× alloc; B2 alloc #2 → 0 → player ends within one tick, 3× |

## Proposed candidate fix (not built)

One mechanism: **give the guest's own end check a true answer.** In
the MPEG HLE, once the playback state is ended (the bypass sets
`streamEnded`; the faithful path at producer EOF with the frame queue
empty), write 1 to `[[mpeg+0x40]+0]`, the word `0x402b38` returns.
The alternative is to bind `0x402b38` to an HLE that returns that
state. The existing `sceMpegIsEnd` handler (`MPEG.cpp:2859`) isn't
wired to any address, and its label for `0x402b38` is unverified.
Then add `0x3b1140` to `extra_function_starts`.

Predicted observables (breaker ON + fix, E33 route):
- per movie, `0x402b38` returns nonzero on the 2nd `0x3b1050` call;
- `0x3b10d0` alloc count 3, not 6 (no null-node alloc);
- `0x3b1140` runs 3× (rc `1→0` each time; zero missing-target);
- Close ×3; menus at ~t257.

Check before building: a T-lane PCSX2 read of `[[0x587b30+0x40]+0]`
across the end of the first movie. It should go nonzero there, which
would confirm the stock game ends movies through that word.

This also matters for **faithful movie playback** (flag off): with the
breaker entry added, a faithful movie would also never end unless the
HLE sets this word.

## Side lead (unverified, not in scope)

On today's OFF path, the null alloc still reaches
`sceMpegGetPicture`. `0x3b0fb8` loads the image from `[0+4]` (guest
address 4), then +0x10 or +`[img+0x10]`. With no decoded frames, the
HLE writes a blank frame there (`writeBlankMpegFrame`, ≥320×240×4
bytes). If `[0x4] == 0`, the destination is `0x10` and the write
covers low RAM up to about `0x4b010`, or up to `0xe0010` at 512×448.
That happens three times per boot, in the build everyone uses now.
Host-side HLE writes don't show on `PS2X_DIAG_WATCH`, and `[0x4]` was
never observed. The fix above removes this call entirely.

## Gaps and deviations

- The worktree was added **detached** at `ssx3` = `2e21cdc`. The brief's
  `worktree add … ssx3` fails because the branch is checked out in
  `~/dev/PS2Recomp`. The content is identical. The worktree was removed
  at close; nothing was committed on the fork.
- Two build dirs (on/off) configured with the E46-build flags and
  `FETCHCONTENT_SOURCE_DIR_*` pointed at a copy of E46-build's `_deps`.
  `PS2X_BUILD_STUDIO` defaulted ON (E46: OFF), which doesn't affect the
  `ps2EntryRunner` target. Both runners are **byte-identical to E46's**:
  ON = e46c `4591f446…`, OFF = e46g/h `a2521d92…`.
- **Byte cap overrun:** E48 peaked at **7.1 GB** (2 × 2.9 GB build dirs
  + 1.1 GB deps) against the 3 GB cap. I noticed it at close and
  trimmed to **770 MB** (two runners 720 MB + run dir 49 MB). A single
  build dir would have fit.
- **Host contention:** the two runner builds (`-j8` + `-j6`, ~15:32–15:50)
  overlapped E47's race boot. The orchestrator's `efeb995` records that boot
  as starved by E48 builds. Next time, one build at a time and check
  the other slot before starting.
- The ticks are frame-interleave stamps, accurate to ±1 tick.
- `0x402b38`'s semantic ("end flag") is inferred from the code shape
  and the counts; there's no verified label.
- The glyphs' draw records weren't identified (E43 census not run).

## Receipts

| Item | Value |
|---|---|
| Fork | `ssx3` @ `2e21cdc` (detached worktree, removed) |
| Runner ON | `4591f44682893b5656712b555544c650aba6b3d8402b26515450e79de71ca0a2` ×2 (`~/dev/ssx3-work/E48/runners/ps2EntryRunner-on`) |
| Runner OFF | `a2521d92f3f019f2208b2f6a66ef7a36357f639bd093ad4bfd90662d408bbd59` ×2 (`…/ps2EntryRunner-off`) |
| B1 log | `boot-e48b1-1.log` 16,118,518 B `7b6e213a1d8a146c925d5a74ad9e6ac89a78cf12b00f2a7fec96cbfada04f85d`; gz 245,760 B `72a93d06…42de` |
| B2 log | `boot-e48b2-1.log` 8,469,557 B `800d5bb99d94f32f5457ce3183dec48cdc03a5c2dfc16e25bb6fb2e147f2e42a`; gz 171,534 B `b638cc56…9270` |
| Frames | `frames/e48b1-black-t1861.png` `6120a759…`, `frames/e48b2-sc-t1363.png` `158f8f64…`, `frames/e48b2-t267.png` `cc9ca994…` |
| Extracts | `e48b1-watch-t0-300.txt` (656 lines), `e48b2-watch-t0-300.txt` (874), `park-e48b1.txt`, `park-e48b2.txt` |
| Build | `ninja -j8/-j6 ps2EntryRunner`, 15.4 / 17.5 min, rc 0 (logs in `~/dev/ssx3-work/E48/`) |
| Budgets | boots 2/2 (slot 1 each, lease claimed + released, own-PID checked); ~0.7 h of 4 h; disk see above; ssx3 total 44.8 GB of 200 |

## Recommendation (orchestrator decides)

1. Keep `0x3b1140` out of `extra_function_starts` until the HLE end
   signal exists. Then land both together (fix above), with one
   boot checking the predicted counters.
2. Brief the T lane to confirm `[[mpeg+0x40]+0]` goes nonzero at the
   end of the first movie in PCSX2.
3. Stray glyphs: drop the node hypothesis. The next step is the
   E35-style per-draw TEX0/UV walk at Select Character (todo H4).
