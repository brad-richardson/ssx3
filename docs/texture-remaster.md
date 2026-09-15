# Texture remaster: a runbook

How to replace any texture in GameCube SSX 3 on the native runtime, end to end,
with the exact commands. Written to be followed step by step; the reasoning
behind each step is in the notes under it, and everything that has actually been
measured is marked as such.

The worked example is SSX 3's own **R&B** course (`ASS1`, Peak 1 slopestyle),
September 15 2026.

## 0. What this rests on

The replacement mechanism is **Dolphin's own custom-texture feature**, not
anything in this repository. That is the single most important finding here,
because the earlier plan aimed at the wrong code:

- `GXRuntime/graphics/aurora/lib/gfx/texture_replacement.cpp` is a complete
  replacement system (pack loader, DDS/PNG readers, LRU cache) and the
  September 14 notes estimated 2-4 days to wire it into `gxcore_draw.cpp`. **It
  is not in this build.** The runtime's `compile_commands.json` has no entry for
  any file under `GXRuntime/graphics/aurora`; it compiles 110 `VideoCommon`
  translation units including `HiresTextures.cpp` and `TextureCacheBase.cpp`,
  plus 12 in `VideoBackends/Metal`.
- So the live path is Dolphin's, and Dolphin already dumps and replaces
  textures. No C++ change is needed, and the "reconcile the gxcore XXH3 content
  hash with the XXH64 dump-filename key" decision is moot: only Dolphin's hash
  exists on this path.

Both halves share one key, which is why a dump is directly usable as the
replacement's file name. From
`VideoCommon/TextureInfo.cpp CalculateTextureName`:

```
tex1_<width>x<height>[_m]_<texture hash>[_<palette hash>]_<gx format>[_arb][_mipN].png
```

- `<gx format>`: 0 I4, 1 I8, 2 IA4, 3 IA8, 4 RGB565, 5 RGB5A3, 6 RGBA8, 8 C4,
  9 C8, 10 C14X2, 14 CMPR.
- Both hashes are XXH64 with seed 0, 16 hex digits. The texture hash covers the
  base level's guest bytes; the palette hash covers **only the palette range the
  texels actually index** (Dolphin walks the indices for min and max first), so
  it is not a hash of the whole TLUT.
- **`_m` means the guest texture has mipmaps**, and it is part of the name — a
  replacement for a mipmapped texture must carry it. This is the easiest thing
  in the whole pipeline to get wrong: a dump also writes one `_mipN` sidecar per
  level, and a file-name pattern that does not expect `_m` silently drops every
  mipmapped texture. On R&B that was **92 of 198** course textures, including
  all the trees and rocks — the first pack here looked complete and left them
  untouched.
- `_arb` marks arbitrary (non-generated) mipmaps. `$` in place of either hash is
  a wildcard.

This loader replaces a mipmapped texture from its base image alone, so a pack
needs the `_m` base files and not the `_mipN` sidecars.

**Where the settings must live.** Not in `GFX.ini`: `UICommon::Init` runs
`Config::SetBaseOrCurrent(Config::GFX_DUMP_TEXTURES, false)` and then
`Config::Save()`, so a base-layer value is overwritten before the video backend
reads it — the first attempt here dumped nothing and the file came back reading
`False`. They go in the per-game layer, `<profile>/GameSettings/GXBE69.ini`,
whose `[Video_Settings]` section maps to the GFX `Settings` section
(`Core/ConfigLoaders/GameConfigLoader.cpp`). `tools/native_gamecube.py` writes
that file for you; you should not have to touch it.

## 1. Get to the course you want to remaster

A fresh profile's Select Event list offers only Snow Jam, Metro-City and
Happiness, so most courses cannot be reached by controller. Point event 0 at the
one you want with a [course-redirect manifest](course-selection.md):

```
# local/research/remaster/rnb-stock.txt
event = 0
code = ASS1        # the SDB location code of the course
name = R and B
short = R and B
location = 5       # its row in the location table
mode = 3           # 2 race, 3 slopestyle, 4 big air, 5 halfpipe, 6 backcountry
```

`code`, `location` and `mode` for every course are in
[peaks and locations](peaks-and-locations.md). Leave `archive` out to keep the
stock world archive.

## 2. Dump what that course loads

```sh
python3 tools/gamecube_course_check.py --game local/game/gxbe69-stock \
  --profile tex-rnb-2 --output local/research/remaster/dump-rnb-002 \
  --course-manifest local/research/remaster/rnb-stock.txt \
  --texture-dump --seconds 200
```

Dumps land in `local/native/profiles/<profile>/Dump/Textures/GXBE69/`. Use a
fresh profile name each time. 200 seconds is enough to boot, load and ride; the
course's own textures are uploaded during the *load screen*, so you do not need
a long ride to collect them.

## 3. Inventory the dump and choose a working set

```sh
python3 tools/texture_dump_inventory.py \
  local/native/profiles/tex-rnb-2/Dump/Textures/GXBE69 \
  --run local/research/remaster/dump-rnb-002 \
  --select 30 --copy-selection local/research/remaster/source-rnb-30 \
  --sheet local/research/remaster/source-rnb-30/contact-sheet.png \
  --output local/research/remaster/inventory-rnb-002.json
```

A run dumps far more than its course. The inventory separates them three ways,
using the run's own rider trace: the observer's first sample is the briefing (so
the course is loading from then on) and its first movement is the race start.

Measured on R&B: **1,437** files dumped, of which **1,036 are the frontend and
the attract movie**, **1,012 are Dolphin's EFB/XFB copies** (paletted and
screen-shaped — the inventory flags these, and they are not art) and **203 are
`_mipN` sidecars**, leaving **198 course textures**: 126 CMPR, 38 C8,
27 RGB5A3, 3 RGBA8, 2 RGB565, 1 C4, 1 I8. **92 of the 198 are mipmapped.**
Mostly 128x128 and 256x256.

`--select N` takes the N largest distinct course textures, which on R&B is a
usable cross-section: snow and ice terrain tiles, rider clothing, a face, crowd
sprites, mountain backdrops, wood, a font sheet, and the HUD sheets (GO!,
CHECKPOINT, TIME BONUS, the numerals). Look at the contact sheet before
spending GPU time.

## 4. Upscale

On the GPU box — `ssh bytesize` over Tailscale reaches the RTX 4070. WSL2 Ubuntu
does the work. **The venv `/home/brad/upscale` has no `bin/activate`**; call
`/home/brad/upscale/bin/python` directly. It has torch 2.6.0+cu124 and spandrel
0.4.2, and CUDA sees the 4070.

Quoting through `ssh → cmd.exe → wsl → bash` is fragile: copy scripts in over
stdin and run them, rather than inlining shell or Python.

```sh
# Copy the tool and the working set over (scp to the Windows side, untar in WSL)
tar czf /tmp/set.tgz -C local/research/remaster/source-rnb-30 .
scp /tmp/set.tgz bytesize:set.tgz
ssh bytesize 'cmd.exe /c wsl -d Ubuntu -e bash -lc "cat > /home/brad/ssx3-remaster/upscale_textures.py"' < tools/upscale_textures.py
ssh bytesize 'cmd.exe /c wsl -d Ubuntu -e bash -lc "mkdir -p /home/brad/ssx3-remaster/source && tar xzf /mnt/c/Users/bradr/set.tgz -C /home/brad/ssx3-remaster/source"'

# One pass per model, plus the no-model baseline
ssh bytesize 'cmd.exe /c wsl -d Ubuntu -e bash -lc "cd /home/brad/ssx3-remaster && /home/brad/upscale/bin/python upscale_textures.py source out-esrgan --model /home/brad/upscale-models/RealESRGAN_x4plus.pth --receipt out-esrgan.json"'
```

Models fetched to `/home/brad/upscale-models`:

| model | source | size | 30 textures took |
| --- | --- | ---: | ---: |
| `RealESRGAN_x4plus.pth` | Real-ESRGAN v0.1.0 release | 67 MB | 12.0 s |
| `4x-PBRify-UpscalerV4.safetensors` | PBRify_Remix 1.7.2 | 140 MB | 23.9 s |
| `4x-PBRify_UpscalerSPAN_Neutral.pth` | PBRify_Remix 1.7.2 extras | 9 MB | 7.1 s |
| Lanczos (`--mode lanczos`) | CPU baseline | — | 4.0 s |

At roughly a third of a second per texture, the whole 106-texture course is
about a minute per model. Cost is not the constraint; judgement about which
model suits which asset is.

**`tools/upscale_textures.py` keeps the dump file names byte for byte**, so its
output directory *is* a pack. It also keeps alpha out of the model: these models
are trained on opaque RGB and game textures are hard cutouts, so RGB goes
through the model, alpha through Lanczos, and fully transparent pixels take
their colour from the nearest visible pixel first — without that last step the
model spreads hidden background colour into the visible edge.

## 5. Compare before committing to a model

```sh
python3 tools/texture_compare_sheet.py local/research/remaster/source-rnb-30 \
  local/research/remaster/passes/out-lanczos local/research/remaster/passes/out-esrgan \
  local/research/remaster/passes/out-span local/research/remaster/passes/out-pbrify4 \
  --names lanczos real-esrgan pbrify-span pbrify-v4 \
  --output local/research/remaster/compare-first6.png --limit 6 --cell 200 --zoom 2
```

Rows are textures, columns are source then each pass, same crop in every cell,
the source enlarged nearest-neighbour so you see the texels it really has.

**What the R&B sheet shows, and it is the main result of this spike: the right
model depends on the asset family.**

- *Wood, clothing, faces, crowd sprites, fonts* — Real-ESRGAN is clearly best:
  it reconstructs plausible grain and keeps edges crisp where Lanczos only
  blurs.
- *Snow and ice terrain (CMPR)* — Real-ESRGAN is the **worst** choice. CMPR is
  4x4 block compression, and a sharpening model treats the block edges as
  structure and amplifies them into visible quilting. PBRify SPAN and V4 smooth
  the blocks instead and read as cleaner snow.
- *HUD sheets and fonts* — all four are close; anything beats the source, and
  the flat colour means there is little for a model to invent.

So a single model over a whole course is the wrong shape for this job, which is
what the [remaster plan](todo.md) assumed: classify by asset family first, then
pick a model per family. The classification signal is already in the dump —
format (CMPR vs RGB5A3 vs C8) plus size plus whether it carries alpha — and it
lines up with the families above.

## 6. Put it back in the game

```sh
python3 tools/gamecube_course_check.py --game local/game/gxbe69-stock \
  --profile tex-rnb-3 --output local/research/remaster/ride-esrgan-001 \
  --course-manifest local/research/remaster/rnb-stock.txt \
  --texture-pack local/research/remaster/passes/out-esrgan --seconds 200
```

`--texture-pack` links the directory as `<profile>/Load/Textures/GXBE69` and
turns on `HiresTextures` and `CacheHiresTextures` in the per-game layer. A pack
may cover any subset of the course; unreplaced textures render normally, so a
screenshot of a partial pack shows a mix.

For a comparison where the two screenshots are the *same moment*, record a
movie once and replay it against each pack, because two free rides diverge
within a fifth of a second
([why](aloha-conversion.md#93-static-collision-observed-under-movie-playback)):

```sh
python3 tools/native_determinism_check.py record --game ... --profile ... --output ... --course-manifest ...
python3 tools/native_determinism_check.py play --game ... --movie ....dtm --output ... --course-manifest ...
```

### Prove the pack is loading before you judge it

Nothing logs a successful custom-texture load, and an upscaled pack looks
plausible whether or not it is in use — so confirm the mechanism with a pack
you cannot mistake, then switch to the real one. Tint every texture and ride:

```python
from PIL import Image
for path in sorted(source.glob('tex1_*.png')):
    im = Image.open(path).convert('RGBA')
    big = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
    px = big.load()
    for y in range(big.height):
        for x in range(big.width):
            r, g, b, a = px[x, y]
            px[x, y] = ((r + 255) // 2, g // 2, (b + 255) // 2, a)   # 50% magenta
    big.save(pack / path.name)
```

If the course comes up pink, the key, the directory and the config layer are all
right, and any later "no visible change" is about the model rather than the
plumbing. Keep the tinted pack around; it is the fastest way to re-check after
changing profiles, game builds or platforms.

## 7. What the R&B spike produced

Files under `local/research/remaster/`:

| what | where |
| --- | --- |
| the course-redirect manifest | `rnb-stock.txt` |
| the dump run and its inventory | `dump-rnb-002/`, `inventory-rnb-002.json` |
| 198 course textures, grouped by family | `groups-rnb/{block-compressed,direct-colour,paletted}/` |
| a 30-texture working set and its contact sheet | `source-rnb-30/` |
| four upscaler passes over that set | `passes/out-{lanczos,esrgan,span,pbrify4}/` |
| the four-way comparison sheet | `compare-first6.png` |
| the complete per-family pack, 198 textures, 64 MB | `pack-mixed/` |
| the tinted proof pack | `pack-proof-magenta/` |
| rides | `ride-esrgan-001/` (30-texture pack), `ride-proof-001/` (tint) |

GPU time for the whole course is about 40 seconds: 126 block-compressed
textures through PBRify V4 in 30 s, 32 direct-colour and 40 paletted through
Real-ESRGAN in 7 s.

### It reaches the screen, and it looks better

Two things were verified at runtime rather than asserted.

**The mechanism.** `pack-proof-magenta/` is the same 106 textures the first
(incomplete) pack held, each tinted 50% magenta at 4x. Riding with it turned the
course pink — snow, sky panorama, HUD numerals, boost meter
(`ride-proof-001`, profile `tex-rnb-4`). That is what proved the key, the
directory and the config layer at once. It is also what exposed the `_m`
mipmapped names: the trees and the rock faces stayed their normal colour,
because 92 of the course's textures were never in that pack.

**The result.** One movie was recorded on stock R&B
(`det-record-rnb.dtm`, `bd121e8d`) and replayed twice, once bare and once with
the complete 198-texture pack (`det-play-stock`, `det-play-pack`). Both arms
reach the same instant — the HUD reads `00:00:40` and `4810` points in both
frames — so the pair is a real before/after rather than two different moments:
`before-after-full.png` and, cropped to the rock face and snow,
`before-after-rock-snow.png`.

The rock face is the clearest gain: flat, mushy blur becomes visible striation
and grain. Snow keeps fine streaks where the stock texture smears, and the
`dnL` and SSX 3 banners become legible. Rider and opponent clothing sharpens.

Honest about the rest: the two screenshots are the same guest second but not the
same frame (the harness captures on wall-clock, so the camera has moved a
fraction of a second), so this is a visual comparison and not a pixel diff. And
the upscaled snow has the classic invented-grain look in places — a model
putting detail where the original had none. Nothing here measures that; see the
quality-gate gap below.

## 8. The whole game at once

A replacement is keyed by content, not by course, so **one pack covers every
course** — and it has to, because courses share most of their art (rider, HUD,
trees, rocks). Three steps:

**Manifests.** `tools/course_manifests.py` reads SSX 3's own event, topology and
mode tables out of `main.dol` and writes one redirect manifest per event, so no
code, location id or discipline is ever guessed:

```sh
python3 tools/course_manifests.py --output local/research/remaster/manifests
```

It cross-checks all three tables against each row index and refuses to emit
anything if they disagree. The 17 courses are events 0-16; `--stations` adds the
five hubs and the debug track.

**Dumps, in parallel.** One run per course, and they do run concurrently:
three, then four at a time all rode cleanly here, each dumping normally. The
harness enforces 180-900 seconds, so a course costs about 3.5 minutes of wall
clock and four at a time puts the whole game inside half an hour.

```sh
for c in ARA1 CRA3 DRA4 ERA5; do
  python3 tools/gamecube_course_check.py --game local/game/gxbe69-stock \
    --profile td-$c --output local/research/remaster/dumps/$c \
    --course-manifest local/research/remaster/manifests/$c.txt \
    --texture-dump --seconds 180 &
done
wait
```

Watch the disk: each course dumps 1,300-1,700 files, roughly 60 MB.

**Union, then upscale once.** `tools/texture_pack_union.py` keeps each distinct
texture once and groups the result by family:

```sh
python3 tools/texture_pack_union.py --output local/research/remaster/union \
  --report local/research/remaster/union.json \
  --course ARA1=local/native/profiles/td-ARA1/Dump/Textures/GXBE69:local/research/remaster/dumps/ARA1 \
  --course ...
```

Then one upscale pass per family directory, as in step 4, and the merged output
is the pack.

### Measured over all 17 courses

| | |
| --- | ---: |
| dumped files across the 17 runs | 23,011 |
| distinct course textures | **907** |
| source art | 13.9 MB |
| block-compressed / paletted / direct-colour | 698 / 159 / 50 |
| mipmapped | 509 |
| pack at 4x | **288 MB**, 907 files |
| GPU time for the whole pack | 3 min 40 s (699 s block, 3 s direct, 17 s paletted) |

Sharing is why the union matters: Snow Jam alone contributes 221 textures, but
by the seventeenth course a new one adds only 15-35. Roughly half the pack is
used by a single course and 28 textures appear in all of them (the rider and
HUD set).

So the cost of the whole game, from nothing to an installed pack, is about
**40 minutes of wall clock**: half an hour of dumps four at a time, four
minutes of GPU, and a few minutes of copying.

### Verified across courses

Three courses were ridden with the whole 907-texture pack — Snow Jam (`ARA1`,
race), Crow's Nest (`ABA1`, big air) and The Throne (`EBC3`, backcountry) —
under `local/research/remaster/verify/`. All three: exit 0, riding observed
(817 / 862 / 815 samples), and zero invalid memory accesses, GPU command
errors, unknown instructions or JIT fallback runs. A pack covering the game
does not destabilise a course it was not built for, because the key is the
texture rather than the course.

## 9. The quality gate

`tools/texture_pack_audit.py` compares a finished pack with the dump it was
built from and ranks the textures worth a human's attention. An upscaler is
*meant* to invent detail, so the gate cannot ask "did anything change" — it
asks whether the change is one of four kinds that are wrong by construction:

| flag | what it measures | what it looks like |
| --- | --- | --- |
| `colour-shift` | mean per-channel delta over the pixels the source shows | the art changes hue or brightness before any detail lands |
| `structure-drift` | RMS luma delta once the pack is box-reduced to source size | the model moved edges instead of sharpening them |
| `alpha-drift` | RMS alpha delta, same reduction | a fringe or a chewed edge on a cutout |
| `flat-invention` | high-frequency energy the pack holds under a flat source | grain where there was nothing to reconstruct |

Every measure compares the pack with its own source *at the source's
resolution* — the pack is box-averaged down by its scale factor, which is the
closest thing to "what the guest would have authored". Colour statistics only
count pixels whose source alpha is non-zero, so a transparent border cannot
drag them around.

```sh
python3 tools/texture_pack_audit.py local/research/remaster/union-all \
  local/research/remaster/pack-all \
  --output local/research/remaster/audit-pack-all.json \
  --copy-flagged local/research/remaster/flagged
```

`--copy-flagged` writes `source/` and `pack/` directories holding just the
flagged pairs, which is what you actually open.

### What it said about the 17-course pack

**109 of 907 textures flagged**: 64 `alpha-drift`, 47 `colour-shift`, 20
`structure-drift`. Medians across the pack are `max_bias` 1.6, `rms` 3.5,
`alpha_rms` 0.0 — so the flags really are a tail and not a verdict on the pack.
Paletted art carries nearly all of it: 69 of 157 C8 textures flag, and 15 of 45
RGB5A3, against 27 of 698 CMPR. Those are the families with alpha, and alpha is
where these models are weakest.

**A flag means "large change", not "bad change" — the triage is visual and
cannot be skipped.** Opening all 109 (the sheet recipe is below), most flagged
textures are *improvements*: a dithered chain-link fence becomes a clean
lattice, a nose ring becomes round, an exclamation mark gets straight edges,
bare winter branches thicken slightly but read better. Two classes were real
defects:

- **Flat fills gaining grain.** 15 textures whose source has no colour *and* no
  alpha structure came back speckled — a flat black 16x16 became grey noise.
  There was nothing to reconstruct, so the model's output is pure invention.
  These are now Lanczos in `pack-all/` (on a flat source, Lanczos is exact), and
  `flat-invention` reads 0 for the pack.
- **Soft particle sprites gaining hard outlines.** The clearest is
  `tex1_32x32_84d2dbfb7e0bebb8_5.png`, a snow puff: a soft white blob with a
  radial alpha falloff came back as a cartoon shape with dark edges
  (`max_bias` 16.1). Real-ESRGAN treats a smooth gradient as a blurred edge and
  restores an edge that was never there. Unfixed — see below.

### The trap: "flat" has to mean flat in alpha too

The first cut of this gate called a font sheet flat. A glyph sheet is white
everywhere it is visible, so its colour variance is exactly zero while all of
its shape sits in the alpha channel; the same is true of glow and lens-flare
sprites. Those upscale *well*, and routing them to Lanczos threw away the best
results in the pack. `flat-invention` therefore requires low variance in colour
**and** in alpha. The 18 candidates split 15 genuinely flat, 3 mask-carried.

### The review sheet

The numbers pick the textures; the eye decides. For each flagged texture, put
the source at nearest-neighbour 4x beside the pack over a checkerboard, and
print its measures next to it:

```python
from PIL import Image
a = Image.open(source).convert('RGBA').resize((180, 180), Image.NEAREST)
b = Image.open(packed).convert('RGBA').resize((180, 180), Image.LANCZOS)
# composite each over a checkerboard so the alpha channel is visible
```

Nearest-neighbour on the source matters: Lanczos there hides the texels the
guest really had and makes every pack look like a smaller improvement than it
is. A checkerboard matters because two thirds of the flags are alpha.

### Still not measured

- **The particle family.** There is no automatic test that separates "soft
  gradient sprite" from "blurred photo texture", which is exactly the
  distinction the model gets wrong. Smoke, spray, glow and lens flare should
  go through Lanczos or SPAN rather than Real-ESRGAN; until they are
  classified, the pack keeps a handful of hard-edged puffs.
- **On-screen scale.** The gate compares textures, not frames. A defect in a
  32x32 particle matters less than the same number on a 256x256 rock face, and
  nothing here weights by how much screen the texture covers.

## 10. Three defects the numbers missed, and the v2 recipe

The gate in section 9 compares each texture with its own source, which cannot
see anything about *how the texture is used*. Riding the pack and looking at the
snow found three defects that are invisible to a per-texture metric, and all
three were reported by a person looking at a screenshot before any tool caught
them. They are worth knowing before remastering anything else, because every
one of them is a property of the pipeline rather than of a model.

### 10.1 A single-level PNG destroys the mip chain

**This is the biggest one.** Dolphin sets a custom texture's mip count from the
files the *pack* supplies:

```cpp
// TextureCacheBase.cpp, CreateTextureEntry
const u32 texLevels = no_mips ? 1 : (u32)custom_texture_data->m_slices[0].m_levels.size();
```

A stock mipmapped texture gets `texture_info.GetLevelCount()` levels; replacing
it with one PNG leaves it with **one**. The base level is then sampled at every
distance, and a 4x base has four times as much detail to alias with, so distant
snow and groomed piste shimmer and show moire banding that the stock game does
not have. 509 of the 907 textures in this game's pack are mipmapped (`_m` in
the name), including all the terrain — so most of what the pack replaces lost
its chain.

`tools/pack_mipmaps.py` fixes it by shipping the levels. Dolphin looks for
`<name>_mip1`, `_mip2`, … beside the base, loads until one is missing, and
requires each to be exactly half the previous (`TextureAssetUtils.cpp`), which
is what a box filter of the level above gives:

```sh
python3 tools/pack_mipmaps.py local/research/remaster/pack-v2-mips \
  --output local/research/remaster/pack-v2-mips.json
```

Levels come from the pack's own base, not from the guest's dumped `_mipN`
sidecars, so the chain is consistent with the art that ships. Cost for 907
textures: **7,789 extra files and about 117 MB** (289 MB → 425 MB). Build the
mip pack as hard links to the base pack so the two can be A/B'd without storing
the bases twice.

### 10.2 An upscaler invents a seam in every tile

A terrain tile repeats across a surface, so its left edge has to keep matching
its right edge, and no super-resolution model knows that. Run one over a tile
and its border pixels get invented context, which shows in game as a line along
every tile boundary — the seam people notice first on a wide snow slope.

Measured over SSX 3's 200 tiling textures (a tile is detectable: its wrap
discontinuity is no worse than its own interior detail), the first pack broke
**66** of them. The fix is `--wrap` in `tools/upscale_textures.py`: pad the
source circularly, upscale the padded image, crop the padding off.
`--wrap auto`, the default, pads only textures whose source already wraps —
padding a sprite or a face would pull the opposite edge of the image into view.

Two details matter:

- **The padding has to be wider than the texture for small tiles.** A 16x16
  tile padded by 16 still came out with a seam: a convolutional model's border
  handling reaches further than 16 pixels. The padding is now at least 32 px
  *and* at least the texture's own size, built by indexing the source modulo
  its size rather than pasting a 3x3 grid.
- **Lanczos breaks seams too**, less severely, so the classes that skip the
  model still pass `--wrap auto`.

With wrapping, broken seams fell from 66 to **13** of 200.

### 10.3 A sharpening model puts a hard rim on a soft sprite

Snow spray, smoke, glow and lens flare are smooth alpha falloffs. Real-ESRGAN
reads a smooth gradient as a blurred edge and restores an edge that was never
there: the snow-spray puff (`tex1_32x32_84d2dbfb7e0bebb8_5.png`) came back with
a hard navy outline, so every puff of spray on the slope had a black rim. The
cure is not a better model — there is nothing in a gradient to reconstruct — it
is to leave those textures to Lanczos.

### 10.4 Do the models differ? Yes, per class, and not by much otherwise

Seven models were compared over 33 textures, and six of them over the snow
tiles specifically (`4x-UltraSharp`, `4x_foolhardy_Remacri`,
`RealESRGAN_x4plus_anime_6B` and `4xNomos8kDAT` in addition to the three the
spike used). On the snow tiles, with wrapping on:

| pass | seam ratio | invented detail | delta from source |
| --- | ---: | ---: | ---: |
| stock | 1.16 | — | — |
| span (wrapped) | **1.11** | 7.3 | 3.1 |
| lanczos | 1.26 | 5.1 | **1.3** |
| ultrasharp (wrapped) | 1.29 | 9.1 | 2.9 |
| nomos8kDAT (wrapped) | 1.46 | 7.9 | 3.7 |
| remacri (wrapped) | 1.48 | 9.7 | 2.9 |
| pbrify v4 (wrapped) | 1.55 | 8.5 | 2.2 |
| esrgan (wrapped) | 2.12 | 9.2 | 5.9 |
| esrgan (no wrap) | 6.06 | 9.4 | 6.1 |

The ranking is stable and unsurprising once the classes are right: the gentle
models (SPAN, PBRify V4) suit terrain, the sharp ones (Real-ESRGAN, UltraSharp,
Remacri) suit art and text, and **no model is better than the correct class
assignment**. Chasing a better checkpoint is worth much less than wrapping the
tiles and shipping the mips.

### 10.5 A scaled cutout leaks, and what leaks through is black

The defect a person spots first in a screenshot: distant bushes, branches and
mesh fences appear as **hard black blobs** on the snow. Two pipeline properties
combine to produce it.

- The guest draws those cutouts with an **alpha test**, not alpha blending.
  A test has no soft edge - a pixel either passes or it does not - so scaling
  the alpha channel with Lanczos grows the shape by a pixel or two of whatever
  is *behind* the art.
- In a dump, what is behind the art is usually **black**: a paletted texture's
  hidden pixels are palette entry 0. `opaque_fill` bled the visible colour
  outward, but only four pixels' worth, so anything further out stayed black.
  Measured across the 176 textures with alpha, 44-75% of the hidden pixels in
  the worst offenders were black.

Both halves are fixed in `tools/upscale_textures.py`:

- `binary_alpha()` detects a hard cutout - 95% or more of its alpha is 0 or
  255 - and re-thresholds the scaled alpha at the halfway point, so the outline
  stays exactly where the guest drew it. (Trees and fences turn out to be
  strictly two-level, which is why the `soft-sprite` class never caught them.)
- `opaque_fill()` now floods the whole transparent area instead of four pixels,
  so a pixel that does leak past an alpha test shows the art's own colour.

Measured over the pack: the area the pack reveals where the source hid it fell
from **0.99% to 0.06%** of hidden pixels, and the share of that leak which is
black from 4.9% to 1.4%. `alpha-drift` flags fell from 64 to 21.

**The general lesson, worth carrying to every asset in both games: alpha is not
a colour channel.** A model must never see it, a scaler must not soften it when
the guest tests it, and whatever sits behind a cutout must be filled with
something plausible before anything touches the image.

### 10.6 The v2 recipe

`tools/texture_pack_plan.py` writes the class decision down once, so running
the pipeline is a loop rather than a judgement call:

```sh
python3 tools/texture_pack_plan.py local/research/remaster/union-all \
  local/research/remaster/plan-all --report local/research/remaster/plan-all.json
```

| class | test | model | wrap | SSX 3 count |
| --- | --- | --- | --- | ---: |
| `flat` | no colour and no alpha structure | Lanczos | auto | 16 |
| `soft-sprite` | >40% of pixels partially transparent | Lanczos | auto | 69 |
| `tile` | the source already wraps | PBRify SPAN | always | 169 |
| `block-compressed` | CMPR, not a tile | PBRify V4 | never | 571 |
| `paletted` | C4/C8/C14X2, not a tile or sprite | Real-ESRGAN | never | 61 |
| `direct-colour` | everything else | Real-ESRGAN | never | 21 |

Then one upscale pass per class directory with the model the report names, and
`pack_mipmaps.py` over the result. Against the first pack: 90 flagged textures
instead of 109 — alpha drift 64 → 21 and colour shift 47 → 32 — 13 broken seams
instead of 66, mip chains on all 931 (the 24 frontend textures included), and
the cutout leak down by a factor of sixteen.

The whole rebuild, once the dumps exist, is about **six minutes**: 40 seconds of
GPU for the four model classes, a couple of seconds of CPU for the two Lanczos
classes, and four minutes to write 8,019 mip levels.

```sh
# 1. classes
python3 tools/texture_pack_plan.py UNION PLAN --report PLAN.json
# 2. one pass per class, with the model and wrap mode PLAN.json names
python3 tools/upscale_textures.py PLAN/tile PACK --model .../SPAN --wrap always --wrap-pad 32
python3 tools/upscale_textures.py PLAN/block-compressed PACK --model .../PBRifyV4 --wrap never
python3 tools/upscale_textures.py PLAN/paletted PACK --model .../RealESRGAN --wrap never
python3 tools/upscale_textures.py PLAN/direct-colour PACK --model .../RealESRGAN --wrap never
python3 tools/upscale_textures.py PLAN/soft-sprite PACK --mode lanczos --wrap auto
python3 tools/upscale_textures.py PLAN/flat PACK --mode lanczos --wrap auto
# 3. the mip chain (hard-link PACK into PACK-mips first to keep both)
python3 tools/pack_mipmaps.py PACK-mips --output PACK-mips.json
# 4. the gate, then ride it
python3 tools/texture_pack_audit.py UNION PACK --output audit.json --copy-flagged flagged/
```

## 11. Putting a pack on the iPhone

The app has a **Remastered textures** switch in its pause menu, beside
Dual-core, and a **Course** row next to it that picks any installed course
([course selection](course-selection.md)) — a pack covers the whole game, so
the two together are what make an A/B on the phone worth doing. It writes `SSXRemasterTextures` and takes effect on the next Full
Reset or relaunch, like the other runtime switches. The switch is disabled and
labelled "No texture pack installed" when the pack directory is empty, so it is
never a dead control.

```sh
python3 tools/mobile_gamecube.py textures --device <identifier> --pack local/research/remaster/pack-all
```

`local/research/remaster/install-tonight.sh` does the whole sequence — build,
sign, install, copy the pack, launch — for the paired phone.

That copies the directory to `Documents/User/Load/Textures/GXBE69`. The app
writes `Documents/User/GameSettings/GXBE69.ini` at every launch with
`HiresTextures` set from the preference and **`CacheHiresTextures = False`** —
caching would preload the entire pack into memory, which is fine on the Mac and
not on a phone. Both states are recorded in the session log
(`texture_pack_state`, `texture_pack_preference_changed`), so a report says
which textures a session actually ran with.

## 12. Doing this for another course, or another asset class

Steps 1-6 are course-agnostic: change the manifest in step 1 and the profile
names. Nothing in the tools knows about R&B.

Not yet established, in order of how much they matter:

- **Whether a pack survives the archive.** Everything here replaces textures at
  *runtime*. Repacking upscaled art into `bam.big` needs CMPR/RGB5A3 encoders, a
  GX tiler, a mip writer and a palette quantiser that do not exist in this
  repository, and ARA1 already sits near the 24 MiB budget.
- **Mipmaps.** The dumps here are base levels. Dolphin can dump mips
  (`DumpMipTextures`) and load `_mip1`-style sidecars; a pack without them lets
  the runtime generate its own, which has not been examined at distance.
- **The iPhone.** The same profile layout exists on device, but no pack has been
  installed there and the 4 GB texture budget has not been measured.
- **The PS2 games.** This whole runbook is the GameCube native path. PCSX2 has
  its own replacement mechanism with a different key, so treat the PS2 side as
  unsolved rather than as a port of this.
- **Automated quality gates.** [Section 9](#9-the-quality-gate) is the first
  cut: four per-texture defect measures against the source, which found and
  fixed one defect class in the shipped pack. It ranks candidates rather than
  passing or failing a pack, and it does not look at frames — see that
  section's own gaps.
