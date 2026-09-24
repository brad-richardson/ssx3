# W1 — Widescreen default

Status: **STOP at first failed test gate.** The candidate runner built, but the
test suite returned 1 (544/545). No boot was attempted. Unverified cells are
marked **not found**.

The PS2 executable has a native option: its ELF string table includes
`kT_19Widescreen`, `kT_19Widescreen169`, and
`kT_19WidescreenAnimorphic` at file offsets `0x35ee50`, `0x35ef50`,
`0x35ef68` (EE VAs `0x45de50`, `0x45df50`, `0x45df68`). The .bss section
begins at `0x4a5c00` (ELF `llvm-readelf -S`); the options struct at
`0x535610` is in .bss.

| Item | Finding | Code or receipt |
|---|---|---|
| Widescreen flag address and offset | `0x535610` word bits 20–21 (mask `0x00300000`), offset 0 of the `0x288`-byte options block. Values: 0 = off, 1 = 16:9, 2 = anamorphic (menu labels). | `ee-at 0x189d14`, `0x189d28`, `0x189d30` (menu writer); `ee-at 0x228ce8`–`0x228d2c` (mode passed to display callback); `ee-at 0x189454`–`0x189488` (labels). |
| Default and initialization | `0x14f4f8` reads a video mode property and writes 0/1/2 to bits 20–21; stock default observed value **not found** (no boot). | `ee-at 0x14f4f8 0 135`; startup call chain `0x14f250 → 0x14f418 → 0x14f4f8` from `ee-xref 0x14f4f8`. |
| Options menu writer | Menu choice index from widget byte `+0x319` is masked to 2 bits, shifted by 20, and stored at `0x535610`; then `0x228c08` applies it. | `ee-at 0x189d10`–`0x189d38`; `0x18945c` and `0x189478` add the 16:9/anamorphic labels. |
| Projection/FOV reader | `0x228c08` extracts bits 20–21 and calls the active object's method at vtable `0x493260+0x140`, which points to `0x377950`. That method stores mode at object offset `+0x6b94` and sets scale/offset floats at `+0x6b98..+0x6ba4`; mode 2 sets horizontal scale `0.75`, vertical scale `1`, no offset. `0x376de4` and `0x376fd0` consume those floats in coordinate/projection calculations. The exact camera FOV formula remains **not found**. | `ee-at 0x228ce8`–`0x228d4c`, ELF data words at `0x4933a0/0x4933a4`, `ee-at 0x377950 0 120`, `ee-at 0x376de4`, `ee-at 0x376fd0`. |
| HUD layout reader | Exact HUD layout consumer: **not found**. The same mode/scale is read at `0x376ab4` to clamp display coordinates, but a HUD-specific call site was not established. | `ee-at 0x376ab4 15 36`; `ee-label` calls the relevant methods unknown. |
| Memory-card save/load behavior | `0x152bb0` copies a `0x288`-byte profile block and later calls `0x228c08` at `0x152dbc` after the load. The W1 hook enforces the host choice immediately before that apply call. | `ee-at 0x152bb0 0 75`, `ee-at 0x152d60 20 45`, `ee-xref 0x228c08`. |

## Build and validation

| Check | Result | Receipt |
|---|---|---|
| Fork worktree and pinned revisions | `w1-wide` at `~/dev/ssx3-work/W1/PS2Recomp`, from `b9647f54934f9f7c448d7cf41fb42f81c74c8ed8`; I26 commit `8a357acad8258a85aba10aa009855d715945890f` cherry-picked as `0c32269` (three iOS modify/delete conflicts resolved by keeping I26 versions). | `git show -s`, `git status`. |
| Host build | **PASS**, 1/3 builds. Release runner and `ps2x_tests` built (556/556 edges) using `~/dev/ssx3-work/W1/build.sh`. | `~/dev/ssx3-work/W1/cmake.log`, `build.log`. |
| Host test gate | **FAIL**: 544 passed, 1 failed. `VU0 macro mappings cover all S1/S2 enums` could not read `instructions.h` from the test working directory (`~/dev/ssx3-work/W1`). The header exists at `PS2Recomp/ps2xRecomp/include/ps2recomp/instructions.h`. This invocation used the wrong cwd; no retest was run under the first failed gate stop rule. | `~/dev/ssx3-work/W1/tests.log`, lines 28–31 and 688–691. |
| Runner SHA read 1 | `a924953e3f277d0acfd4a687c0be40af4dd8a1ade9a5a7c4de16b1241fdefaba` | `shasum -a 256 ~/dev/ssx3-work/W1/build/ps2xRuntime/ps2EntryRunner`. |
| Runner SHA read 2 | `a924953e3f277d0acfd4a687c0be40af4dd8a1ade9a5a7c4de16b1241fdefaba` | independent second `shasum -a 256`. |
| Title, main menu, Select Character, race | **not run**, 0/3 boots, 0 lease claims. Aspect and HUD visual result not found. | `p_lane_lease.py status`: slots 1 and 2 free at stop. |

## Commands and gaps

Host implementation: `PS2X_WIDESCREEN=1` default selects guest anamorphic
mode 2 before the game's `0x228c08` display update; `0` selects guest mode 0.
The hook is keyed to `SLUS_207.72` entry `0x100008` using the existing
`PS2_REGISTER_GAME_OVERRIDE` mechanism. It preserves every other options bit.
The shared `ps2_present_geometry.h` fits the frame to 16:9 for mode 2; it
accepts `PS2X_ASPECT=native|4:3|16:9` as an override. The shared runtime
presenter is used on desktop, iOS and Android; iOS touch glue remains in
`ps2_ios_runtime.mm`.

Commands so far: `git worktree add -b w1-wide ... b9647f5`; `git cherry-pick
8a357ac` (conflict resolved with `git add` and `git cherry-pick --continue`);
`strings -a -t x` and `llvm-readelf -S` on the stock ELF; `local/tooling/ee/ee-at`,
`ee-xref`, `ee-func`, `ee-label` on the addresses cited in the table;
`zsh ~/dev/ssx3-work/W1/build.sh` (exit 0);
`~/dev/ssx3-work/W1/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/W1/tests.log 2>&1`
from `~/dev/ssx3-work/W1` (exit 1).

Candidate edits are uncommitted in the W1 fork worktree (three files, 71
insertions/6 deletions); the I26 cherry-pick is committed only on local
`w1-wide`. The exact candidate diff is [w1-fork.patch](w1-fork.patch), and the
failing test lines are [test-gate-failure.txt](test-gate-failure.txt).
`git diff --check` is clean. W1 work directory at stop: 571 MB
against 4 GB cap. `w1_boot.py` was prepared but never invoked.

**Recommendation to orchestrator:** rerun the suite from the fork root so
`instructions.h` is found, then use the prepared bounded W1 capture to inspect
title, main menu, Select Character and race in mode 2 versus mode 0. Keep the
candidate local until the HUD and profile behavior are verified visually.
