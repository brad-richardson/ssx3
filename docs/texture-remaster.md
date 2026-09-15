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

## 8. Doing this for another course, or another asset class

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
- **Automated quality gates.** Everything above is eyeballed. The plan's "QA"
  stage does not exist yet; a first cut would be a per-texture metric against
  the source (structure kept, palette kept, no new saturation) run over a pass
  directory.
