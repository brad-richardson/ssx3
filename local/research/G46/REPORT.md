# G46 report: menu fonts, sprite-sheet and snowflake artifacts, GS backend or game draws?

Brief: `local/muse/prompts/G46.md`. Tables and receipts. The orchestrator decides.
Worker: Claude Code (Opus). Tree: fork `ssx3` @ `eac6cba` + canonical `codegen-ssx3`.

## 0. Outcome first

- **Three renderers were fed the same recorded stream:** our CPU backend,
  paraLLEl-GS (the in-process G44 shadow) and **PCSX2 gsrunner** (a `.gs`
  converter was feasible in about 30 min). All three draw **every sprite-sheet and
  snowflake artifact Brad reported**, and PCSX2's own run (T47) shows none
  of them. So those are **(b)**: the texture contents or uploads the game's
  draws sample are wrong upstream of the GS.
- **One (a) artifact was found and fixed:** a thin bright dotted diagonal line
  (plus short horizontal and vertical seams) across the menu background. The
  cause is our CPU backend's triangle coverage: an inclusive epsilon test with no
  fill rule, so a shared edge gets drawn twice under alpha blending. A failing
  unit test proves it. The fix is fork commit `104dd7f` on `g46-gs` (no push). It
  was validated by offline replay (the seam pixels are the only change) and by
  one live boot on the 3 frames.
- **Fonts, "kerning":** the glyph advances are identical in ours, paraLLEl
  and PCSX2 at guest resolution, so this is **not a GS issue**. The likely
  cause is host presentation: the 512×448 frame is drawn with raylib's
  default POINT filter at a non-integer scale (×2.946 on the iPhone 16 Pro
  Max) and at 8:7 aspect instead of 4:3. That is a simulation, not proven on the device (§4).

## 1. Classification table

| # | Artifact (Brad's words / where) | Ours (CPU) | paraLLEl, same stream | PCSX2 gsrunner, same stream | PCSX2 own run (T47) | Class |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Font spacing ("kerning") on Select Mode/Peak | same advances | same advances (~2 px scanout shift) | same advances | same advances (640×480 resized to 512×448) | **not GS**: host presentation (§4) |
| 2 | Snowflakes "sometimes perfect" (❄ top right, Select Peak t1620) | clean ❄ | clean ❄ | n/a | ❄ present | fine |
| 3 | Snowflakes "weird square texture" (beige striped rectangles, Select Mode t1900–2260; striped "shards" on Main Menu) | striped quad | same quad, same texture | same quad (frame 2186) | ❄ snowflakes, no stripes | **(b)** |
| 4 | Select Peak photo panel shows the "PEAK ACCESS / LEVEL" icon atlas | atlas | atlas | atlas (frame 1627) | mountain photo | **(b)** |
| 5 | Ghost "LEVEL" + icon row behind the header, and the orange "3" missing (Select Peak) | ghost atlas | same | same | orange "3" | **(b)** |
| 6 | SSX logo slot shows "PEAK 1 / VAL" atlas cells (Select Peak only; correct on Select Mode) | atlas cells | same | same | SSX logo | **(b)** |
| 7 | Select Mode photo panel shows a striped "3" graphic | striped 3 | same | same (frame 2026) | mountain photo with routes | **(b)** |
| 8 | Button glyphs (✕/△) drawn as teal/pink bars (Select Peak/Mode) | bars | bars | bars | ✕ △ glyphs | **(b)** |
| 9 | Main Menu ghost controller diagram, L1/R1/L2/R2 boxes, D-pad, bottom-left icon cluster | present | present | present (frame 830) | absent | **(b)** (as G44) |
| 10 | Thin dotted diagonal line across the menu background plus a vertical line at the right edge (all menus) | **present** | absent | absent | absent | **(a), fixed** (§3) |

Side-by-side PNGs (ours / paraLLEl / PCSX2 on our stream / PCSX2 own run):
`png/g46-menu-900.png`, `png/g46-selectpeak-1700.png`,
`png/g46-selectmode-2260.png`. Zooms: `png/g46-snow-striped-2260.png`,
`png/g46-snow-clean-1620.png`, `png/g46-font-2100.png`,
`png/g46-seam-cpu-par-pcsx2-fixed-900.png` (old CPU | paraLLEl | PCSX2 |
fixed CPU), `png/g46-validation-live-g46b.png`,
`png/g46-font-presentation-sim.png`.

Reading of the (b) set: it is one family. The same draws sample texture
pages whose contents are wrong for that screen. The SSX-logo slot is right on
Select Mode but shows "PEAK 1/VAL" cells on Select Peak. The snowflake
particle is a clean ❄ at t1620 but shows beige stripes that look like the
Select Mode panel's striped "3" at t1900+. That points at texture uploads
that are missing, late or misplaced (E51: ~1 upload/vsync vs PCSX2 ~73) or at
wrong TEX0 TBP values, both upstream of the GS. The GS lane can't separate
those two.

## 2. Method and receipts

### 2.1 Fork branch `g46-gs` (worktree `~/dev/ssx3-work/G46/PS2Recomp`, no push)

| Commit | What |
| --- | --- |
| `6ba4a74`, `015a7c7`, `bf32437` | G44 shadow (`460e438`, `8c45d1f`, `6cfede4`) cherry-picked onto `eac6cba`. Conflicts with E33's packet listener in `ps2_gif_arbiter.{h,cpp}` and `ps2_runtime.cpp` were resolved by keeping both hooks (listener first, then shadow). |
| `a4dc71e` | Diagnostics, default off: `PS2X_GS_SHADOW_STRIDE` (one pair per N ticks); `PS2X_GS_SHADOW_REC` (records every fed GIF packet, HLE reg write, and the 15 priv regs per present; stops at `_TO`); `G46Replay` test (`PS2X_G46_REC` replays a recording through the CPU backend and writes PPMs at `PS2X_G46_TICKS`). |
| `104dd7f` | **The fix** (§3) + unit test. |

- `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` is empty (checked
  at `a4dc71e` and `104dd7f`).
- Build `~/dev/ssx3-work/G46/build`: Release, ninja, logs OFF, `PS2X_GS_SHADOW_PARALLEL=ON`,
  paraLLEl from `~/dev/ssx3-work/G43/parallel-gs` (G44 recipe), codegen
  `~/dev/ssx3-work/codegen-ssx3`. 1 configure; 3 incremental builds.
- Suite from the worktree root: **606/606** at `a4dc71e`. At the new test
  before the fix: **606/607** (only the new test fails: "no pixel … blended
  by both triangles", "… drawn exactly once"). After the fix: **607/607**.
- Runner SHAs: pre-fix `0331fd41…9151f30` (1 read, boot g46a); fixed
  `e2a0e881…cdd30` (2 matching reads, before and after boot g46b).

### 2.2 Boots (2 of 3 used, slot 1 each via `p_lane_lease.py`, released)

| Boot | Runner | Settings | Result |
| --- | --- | --- | --- |
| g46a | pre-fix | E51/I25 vsync route, `PS2X_SKIP_MOVIE=1`, shadow pairs 700–2300 stride 8, recorder on, `FORCE_SMODE1=ntsc` (G44 diagnostic, shadow copy only) | rc 0, wall 560 s. 200/200 pairs (Main Menu t700–1236, Select Character ~1244–1396, Select Peak ~1500–1852, Select Mode ~1860–2292). Recorder closed at tick 2300: 681,394,469 B (sha `a8438a5e…`; kept as `run/rec-g46a.bin.zst` `1cf9645d…`). Shadow stats: 3,277,542 packets fed, 0 reg writes, 11,100 presents. |
| g46b | fixed | same route, pairs 880–2200 stride 8, no recorder | rc 0, wall 400 s. 165 pairs. Validation at t904 / t1704 / t2104: the seam is gone, everything else unchanged (`png/g46-validation-live-g46b.png`). |

Shadow caveats (as G44): paraLLEl's scanout is field-combed and shifted about 1–2 px
(PSNR ~17 dB for that reason alone), so content is judged by eye per element.
While the shadow is active the native P6/P7 fast paths route through the
arbiter. That changes nothing visible: E51's shadow-free frames of the same
screens (`E51/run/frames-e51a-1/snap`, same `eac6cba` code) show the same (b) set.

### 2.3 Offline replay (no boot)

`PS2X_G46_REC=../run/rec-g46a.bin PS2X_G46_TICKS=724,900,1196,1700,2100 PS2X_G46_OUT=../rep0 ../build/ps2xTest/ps2x_tests`
from the worktree root. The replay reproduces the live CPU frames: t900/1196/1700/2100 are
within 4 LSB; t724 differs on one moving element (latch timing).
305,829 packets and 2,027 presents were replayed up to t2100.

### 2.4 PCSX2 gsrunner on our stream (bytesize, 1 job, 44 s)

- `g46_rec2gs.py` turns the recording into a PCSX2 `.gs`:
  - state v9, all zero: the recorder ran from boot, so every upload is in the stream;
  - header CRC and serial from `t48b-dump.gs`;
  - each present becomes a Registers packet plus a VSync packet;
  - path mapping 1→Path1New, 2→Path2, 3→Path3;
  - SMODE1 forced to the PCSX2 NTSC value `0x40814504` (G29) while the game's is 0, mirroring G44's diagnostic.
- Output: 334,310 packets, 2,225 vsyncs (ticks ≤ 2299).
- Files: `.gs` sha `6234f2f5…` (703 MB, deleted); `g46a.gs.zst` sha `8fec8aab…` (8.9 MB, two matching reads Mac and bytesize).
- Replayed with the T48-pinned gsrunner (`9056c083`), Vulkan renderer, `g10-uncorrected.ini`: 2,224 frames, rc 0, DISPFB 112 as ours (`local/research/G46/g46_gsrunner.sh`).
- Frame k is vsync k (`g46a.gs.ticks`); frames 830/1627/2026/2186 correspond to t900/1700/2100/2260.
- 14 frames kept locally (`~/dev/ssx3-work/G46/pcsx2/`); the other 2,210 were deleted on bytesize.

PCSX2 own-run references: T47 F8 shots `t47-shot-{menu,sp,sm}.png` (640×480,
read-only copy from the SSD; different moment of the same screens).

## 3. The (a) mechanism and the fix

`GSCpuBackend::DrawTriangle` (`gs_cpu_backend.cpp`, pre-fix ~L1270–1290):

- It covered a pixel when all three float barycentrics were ≥ −1e-4.
- It had no fill rule, so a pixel centre on (or within epsilon of) an edge shared by two triangles was drawn by both.
- The menu background is an alpha-blended gradient quad, and double blending made those edge pixels brighter.
- Result: a dotted bright diagonal from bottom-centre to top-right, plus a horizontal and a vertical seam at strip joins.
- paraLLEl and PCSX2 fed the same stream don't draw it.

Fix (`104dd7f`):

- Coverage uses exact edge functions in 1/16-pixel units (vertex XY is 12.4 fixed point, so this is exact in int64).
- It applies a top-left rule: an edge is included when it runs upward, or when it is horizontal and runs rightward, with interior on the positive side.
- Sample points (+0.5) and all attribute interpolation are unchanged.

Proof:

- New test "GS triangles sharing an edge cover each pixel once (G46 fill rule)": two additive triangles split a 24×24 quad along its diagonal.
  - Before the fix, the diagonal pixels read 2× and the test fails.
  - After the fix, all 576 pixels read 1×, there are no holes, and the corner pixel stays outside.
- The existing triangle and fan tests still pass (607/607).
- Replay diff, old vs fixed, on the same stream: only about 440–490 px per frame change, all on 1-px seam lines (`~/dev/ssx3-work/G46/mask-1700.png`).
- Live g46b confirms on the 3 frames.

## 4. Fonts: not the GS

- At guest resolution the glyph advances match across ours, paraLLEl and
  PCSX2 (`png/g46-font-2100.png`; T47 SP crop resized to 512×448).
- Host presenter (`ps2_runtime.cpp` ~L3348–3367):
  - it draws the 512×448 frame with uniform scale `min(sw/512, sh/448)`, so the aspect is 8:7 (4:3 on a TV);
  - it uses raylib's default POINT filter (no `SetTextureFilter` call).
- On the iPhone 16 Pro Max in landscape (2868×1320 px) that gives ×2.946 nearest sampling: stems and gaps alternate between 2 and 3 px, and the text is about 15% narrower than the game intends.
- `png/g46-font-presentation-sim.png` shows this. It is a **simulation**: Brad's iPhone wasn't used, per the install-only rule.
- Candidate fix, **not applied** (one-fix budget used, and it isn't the GS): present at 4:3 (dst width = height × 4/3) with `TEXTURE_FILTER_BILINEAR` on `frameTex`. It fits I26 or the N/I presentation owners.

## 5. Other things read (not implicated here, for the record)

- The CPU backend has no CLUT buffer (`// TODO: clut cache`): it reads CLUTs from VRAM at draw time and ignores TEX0.CLD. It isn't the cause of any artifact here, since all renderers agree, but it is a latent (a)-class difference.
- FST sprite UVs are truncated to whole texels (`v0.u >> 4`), and sprite XY is truncated rather than following the GS rule. Neither is implicated here.
- paraLLEl frames look paler only because of field combing (alternate lines from the other field), not content.

## 6. Gaps

- The (b) root cause is not identified. The GS lane can't tell missing or misplaced texture uploads from wrong TEX0/TBP values.
- PCSX2 own-run references are T47 stills of the same screens, not the same instant.
- The gsrunner run used the forced SMODE1 value and a zeroed initial state. Harmless for content, since the stream starts at boot, but stated here.
- Fonts: iPhone presentation cause is by simulation only.
- Budget: 2 of 3 boots, 1 bytesize job, about 2 h wall; G46 dir 3.3 GB of the 5 GB cap (build dominates); all-ssx3 74.2/200 GB.

## 7. Recommended next (orchestrator decides)

1. Fold `104dd7f` (fill rule + test) into `ssx3`. It stands alone and doesn't need
   the G44/G46 diagnostic commits.
2. E-lane brief for the (b) family:
   - Use the recorder (or `PS2X_GIF_DUMP`) to list the PATH2/3 IMAGE uploads (BITBLTBUF DBP/DBW/DPSM, TRXREG) and each draw's TEX0 TBP0/CBP between the Main Menu and Select Peak.
   - Diff against a PCSX2 `.gs` of the same screens (T-lane dump, `-dump tr`).
   - The target is the photo-panel texture: its upload is expected to be missing, or to land in the atlas/snowflake page.
3. I26/N: 4:3 + bilinear presentation for the font complaint.

## 8. Exact commands

```
git -C ~/dev/PS2Recomp worktree add -b g46-gs ~/dev/ssx3-work/G46/PS2Recomp eac6cba
git cherry-pick 460e438 8c45d1f 6cfede4   # conflicts resolved: keep both hooks
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_BUILD_TEST=ON -DPS2X_GAME_CODEGEN_DIR=$HOME/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=$HOME/dev/ssx3-work/G43/parallel-gs -DPARALLEL_GS_STANDALONE=ON
nice -n 10 ninja -j8 ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)
python3 local/research/G46/g46_boot.py --label g46a --wall 560 --snap 5 --sfrom 700 --sto 2300 --stride 8 --rec
python3 local/research/G46/g46_rec2gs.py run/rec-g46a.bin g46a.gs --force-smode1-ntsc && zstd -10 g46a.gs
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/G46/g46_gsrunner.sh
PS2X_G46_REC=../run/rec-g46a.bin PS2X_G46_TICKS=724,900,1196,1700,2100 PS2X_G46_OUT=../rep1 ../build/ps2xTest/ps2x_tests
python3 local/research/G46/g46_boot.py --label g46b --wall 400 --snap 5 --sfrom 880 --sto 2200 --stride 8
```

Image helpers: `local/research/G46/tools/*.py` (Pillow venv at
`~/dev/ssx3-work/G46/venv`).
