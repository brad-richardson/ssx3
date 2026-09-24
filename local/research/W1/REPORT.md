# W1 — Widescreen default

Worker result: the native SSX 3 anamorphic option is found and enforced by the
local `w1-wide` candidate. The corrected host test gate passes, and three
bounded boots reached the race. The 3D rider keeps natural proportions at
Select Character, while title, menu and HUD graphics visibly widen in 16:9.
The race's existing GS composite occlusion prevents a full scenery judgment.
These are observations for the orchestrator's gate, not a product verdict.

The PS2 executable has a native option: its ELF string table includes
`kT_19Widescreen`, `kT_19Widescreen169`, and
`kT_19WidescreenAnimorphic` at file offsets `0x35ee50`, `0x35ef50`,
`0x35ef68` (EE VAs `0x45de50`, `0x45df50`, `0x45df68`). The .bss section
begins at `0x4a5c00` (ELF `llvm-readelf -S`); the options struct at
`0x535610` is in .bss.

| Item | Finding | Code or receipt |
|---|---|---|
| Widescreen flag address and offset | `0x535610` word bits 20–21 (mask `0x00300000`), offset 0 of the `0x288`-byte options block. Values: 0 = off, 1 = 16:9, 2 = anamorphic (menu labels). | `ee-at 0x189d14`, `0x189d28`, `0x189d30` (menu writer); `ee-at 0x228ce8`–`0x228d2c` (mode passed to display callback); `ee-at 0x189454`–`0x189488` (labels). |
| Default and initialization | **Stock boot value 0** immediately before the first display apply. The mode-on log records `guest_mode=0` at source `0x2285a0` before W1 writes 2. `0x14f4f8` reads a video mode property and writes 0/1/2 to bits 20–21. | [boot receipt](boot-receipt.txt); `ee-at 0x14f4f8 0 135`; startup call chain `0x14f250 → 0x14f418 → 0x14f4f8` from `ee-xref 0x14f4f8`. |
| Options menu writer | Menu choice index from widget byte `+0x319` is masked to 2 bits, shifted by 20, and stored at `0x535610`; then `0x228c08` applies it. | `ee-at 0x189d10`–`0x189d38`; `0x18945c` and `0x189478` add the 16:9/anamorphic labels. |
| Projection/FOV reader | `0x228c08` extracts bits 20–21 and calls the active object's method at vtable `0x493260+0x140`, which points to `0x377950`. That method stores mode at object offset `+0x6b94` and sets scale/offset floats at `+0x6b98..+0x6ba4`; mode 2 sets horizontal scale `0.75`, vertical scale `1`, no offset. `0x376de4` and `0x376fd0` consume those floats in coordinate/projection calculations. The exact camera FOV formula remains **not found**. | `ee-at 0x228ce8`–`0x228d4c`, ELF data words at `0x4933a0/0x4933a4`, `ee-at 0x377950 0 120`, `ee-at 0x376de4`, `ee-at 0x376fd0`. |
| HUD layout reader | Exact HUD layout consumer: **not found**. The same mode/scale is read at `0x376ab4` to clamp display coordinates, but a HUD-specific call site was not established. | `ee-at 0x376ab4 15 36`; `ee-label` calls the relevant methods unknown. |
| Memory-card save/load behavior | `0x152bb0` copies a `0x288`-byte profile block and later calls `0x228c08` at `0x152dbc` after the load. The W1 hook enforces the host choice immediately before that apply call. | `ee-at 0x152bb0 0 75`, `ee-at 0x152d60 20 45`, `ee-xref 0x228c08`. |

## Build, tests, boots and inputs

Fork worktree: /Users/brad/dev/ssx3-work/W1/PS2Recomp, local branch w1-wide from b9647f54934f9f7c448d7cf41fb42f81c74c8ed8. I26 commit 8a357acad8258a85aba10aa009855d715945890f was cherry-picked as 0c32269 (three iOS modify/delete conflicts resolved by keeping I26 files). The W1 candidate is committed locally as 7a0e46a06da59887a55395234e53fd657bc7dd3a. Fork worktree clean; no push.

The runtime override is keyed to SLUS_207.72 entry 0x100008. PS2X_WIDESCREEN=1 (also unset/default) selects guest mode 2; 0 selects mode 0. At the game's display apply call, it replaces only bits 20–21, preserving all other option bits. No ELF was edited. The shared presenter fits mode 2 to 16:9; PS2X_ASPECT=native|4:3|16:9 explicitly overrides it. The shared geometry serves desktop, iOS and Android. The hook also runs on the display apply after a profile load, though a saved profile with an opposing choice was not boot-tested.

| Check | Result | Receipt |
|---|---|---|
| Host build | **PASS**, 1/3 builds. zsh /Users/brad/dev/ssx3-work/W1/build.sh built the Release runner and tests. | /Users/brad/dev/ssx3-work/W1/cmake.log and build.log. |
| Initial test invocation | 544/545 from the wrong cwd (/Users/brad/dev/ssx3-work/W1): a test's relative instructions.h lookup failed. The orchestrator identified this as an invocation error and requested a rerun. | [initial failure excerpt](test-gate-failure.txt), /Users/brad/dev/ssx3-work/W1/tests.log. |
| Corrected test gate | **PASS, 545/545**. Command: cd /Users/brad/dev/ssx3-work/W1/PS2Recomp && ../build/ps2xTest/ps2x_tests > ../tests-root.log 2>&1. | [pass excerpt](test-gate-pass.txt), full /Users/brad/dev/ssx3-work/W1/tests-root.log. |
| Mode on boot | PS2X_WIDESCREEN=1, one mini slot, PID 18210, target 2050 reached at tick 2088 in 116.964 s; all four captures saved. rc=-15 is harness termination after target. | [boot receipt](boot-receipt.txt), /Users/brad/dev/ssx3-work/W1/run/on/boot.log and result.json. |
| Mode off boot | PS2X_WIDESCREEN=0, one mini slot, PID 18569, target reached at tick 2061 in 105.897 s; all four captures saved. rc=-15 is harness termination. | [boot receipt](boot-receipt.txt), /Users/brad/dev/ssx3-work/W1/run/off/. |
| Second mode on boot | PS2X_WIDESCREEN=1, one mini slot, PID 19592, target reached at tick 2053 in 121.000 s; Select Character recaptured after its transition. rc=-15 is harness termination. | [boot receipt](boot-receipt.txt), /Users/brad/dev/ssx3-work/W1/run/on2/. |

All three boots used the I26-FAST scripted route, PS2X_SKIP_MOVIE=1, PS2X_PAD_SCRIPT_CLOCK=vsync, frame capture, a 500 s wall cap, 120 s progress cap, 64 MiB log cap and 256 MiB frame cap. Each claimed and released one mini lease slot. Boot command: python3 /Users/brad/dev/ssx3-work/W1/w1_boot.py --label <on|off|on2> --capture --mode <1|0|1> --target 2050 --wall 500, run escalated as required for graphics initialization. The exact pad script and environment are in each result.json. All boots used the same runner and inputs, with [two matching SHA-256 reads for each](sha-receipt.txt):

| File | SHA-256 |
|---|---|
| Release ps2EntryRunner | a924953e3f277d0acfd4a687c0be40af4dd8a1ade9a5a7c4de16b1241fdefaba |
| Stock SLUS_207.72 | 1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc |
| Stock SSX 3 USA ISO | 3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5 |

## Visual comparison

I viewed every captured stage. The JPEGs below rescale the raw 512×448 frame as the shared presenter would: mode 0 to 960×720 (4:3), mode 2 to 1280×720 (16:9). They are presenter-equivalent reconstructions from frame dumps, not OS window screenshots. Every JPEG is under 8 MB. The mode-on Select Character image is from the third boot at tick 842; mode-off is tick 815. Other mode-on images are from the first boot.

| Stage | Mode 0 (4:3) | Mode 2 (16:9) | Viewed result |
|---|---|---|---|
| Title | [frame](off-title.jpg) | [frame](on-title.jpg) | Scene fills 16:9. The SSX 3 logo and Press START lettering are about one-third wider than at 4:3, with no compensating guest squeeze; visible 2D stretch. |
| Main menu | [frame](off-menu.jpg) | [frame](on-menu.jpg) | Main menu labels and button legends widen horizontally. Existing lower-left GS sprite/texture fragments occur in both modes. |
| Select Character | [frame](off-character.jpg) | [frame](on-character.jpg) | Zoe's displayed body proportions look comparable across modes: guest anamorphic squeeze and presenter stretch cancel for this 3D model. Stats, labels, silhouette icons and button legends widen; the 2D layout is distorted relative to 4:3. Both captures show existing sprite fragments. |
| Race | [frame](off-race.jpg) | [frame](on-race.jpg) | The race starts and advances. HUD rank, timer, radio box and text widen in mode 2. Both frames have a large black GS composite occlusion; the remaining snow/scene cannot establish whether full 3D scenery is correctly framed at 16:9. |

The title/menu raw captures have essentially the same 2D layout in both guest modes, so the 16:9 presenter widens those elements by 4/3. The 3D rider is the clearest positive evidence for the native anamorphic path. No PCSX2 comparison was needed to identify 2D widening. PS2X_ASPECT override and a profile save with an opposing setting were not separately boot-tested.

## Scope, limits and recommendation

Used 1/3 builds, 3/3 boots, and 577 MB in /Users/brad/dev/ssx3-work/W1 against the 4 GB cap. The local fork branch is committed and unpushed. W1 text receipts and eight JPEGs are in this report directory; full bounded logs and raw frames remain in the W1 work directory. The earlier candidate patch is [w1-fork.patch](w1-fork.patch); the commit is authoritative.

**Recommendation to orchestrator:** retain the native mode 2 mechanism for the 3D path, but treat 2D correctness as an open follow-up: the stock title, menus and HUD visibly widen under a full-frame 16:9 present. The race scenery needs another judgment after the GS composite occlusion is fixed. A saved profile override and PS2X_ASPECT override remain unexercised runtime cases; their code paths were inspected above.
