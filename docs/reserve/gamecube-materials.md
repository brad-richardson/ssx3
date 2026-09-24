# Terrain material conversion

Terrain geometry and image identity do not establish rendered fidelity. Each
engine also defines how those images combine. Keep that convention in an
engine-pair material profile, rather than adding color adjustments per track.

## Verified Tricky → SSX 3 lighting transfer

`tools/gamecube_materials.py` defines `tricky-gc-to-ssx3-gc-v1`, the default
when `gamecube_terrain.py` imports Tricky textures and lightmaps. September 12
draw captures contain **108 matching base-texture/lightmap hash pairs**. All
use these terrain stage operations:

| Operation | Tricky GameCube | SSX 3 GameCube |
| --- | --- | --- |
| Stage 0 | Load base texture | Load base texture |
| Stage 1 | Base × lightmap, scale **1**, clamp | Base × lightmap, scale **2**, clamp |

Copying a Tricky lightmap unchanged therefore doubles its contribution and
clips highlights before later shadow/fog operations. The profile converts
the lightmap to half its original channel values, compensating for the
target's scale. This is a conversion of GX channel values, with no gamma or
exposure correction. Base textures, alpha, geometry and UVs are preserved.

The source RGB565 image expands using GX bit replication. The converted
sheet uses RGBA8 (`0x16`), with opaque alpha, in 4×4 GX tiles: an A/R plane
followed by G/B. Re-encoding into RGB565 would discard additional shadow
precision after halving. Across all 65,536 RGB565 colors, doubling the
converted channels reconstructs each original channel within one 8-bit code
value. That bound excludes texture filtering, TEV arithmetic rounding, fog
and framebuffer quantization; it is not a screenshot fidelity score.

The original files are never modified. Every imported lightmap gets a receipt
under `experiment.json → textures.lightmap_transfer`, including source and
output pixel hashes, source/target scales, format, gain and reconstruction
error. The regular archive readback verifies the actual serialized images.
For Garibaldi, build 013 changes only its 16 donor lightmap payloads. The
archive grows by 229,376 compressed bytes; decoded sheets grow by 524,288 bytes.

The verified profile accepts RGB565 lightmaps and rejects other formats,
including already-converted RGBA8 sheets. Inspect a new source format before
extending the profile. `--material-profile raw` is available as an explicitly
uncorrected control. A different engine version or material equation needs
a separately verified profile; do not silently reuse this gain.

## Reusable draw-state comparison

`tools/gamecube_draw_trace.py` builds separate diagnostic executables from the
existing native build. It compiles a local copy of the vertex manager with
`native/diagnostics/draw_trace.h`, pins the CLI to the selected source disc and
DOL hash, and optionally selects JIT for the original game. Production players,
vendor sources and libraries remain unchanged. Each output has `build.json`
with compiler/link commands, input identity and binary/header hashes.

For example, choosing fresh output directories:

```sh
python3 tools/gamecube_draw_trace.py build \
  --game local/game/gste69-original --cpu jit \
  --output local/native/tricky-material-review
python3 tools/gamecube_draw_trace.py build \
  --game local/game/gc-gari-012 --cpu aot \
  --output local/native/import-material-review
```

Run those players with the normal `--game`, `--user-dir`, `--no-mods` and
`--graphics Metal` arguments. Use an isolated profile with the pipe controller
mapping, then navigate with `tools/gamecube_input.py`. For JIT, pass
`--allow-interpreter`, `STATICRECOMP_NO_JIT=0` and
`SSX3_NO_EXECUTABLE_MEMORY=0`. For AOT, pass the matching `--module` and set
both guards to `1`.

Set `SSX3_DRAW_TRACE` to a fresh absolute JSONL path. Create the adjacent
`PATH.enable` file when the desired course is loaded; remove it to stop
sampling. Existing JSONL files are preserved. Collection stops at 4096
distinct texture/combiner/order combinations. Stop the player after the
desired observations; the trace is diagnostic work, not a performance run.

Each record contains the sampled BP/XF state, color constants, texture cache
hashes, vertex declaration and initial vertex bytes. Raw words use the little
endian host layout of the pinned build. It records the **first observed draw**
of each combination; animated uniform/vertex changes are not continuous
samples. These traces do not count visible patches or prove absence of pop-in.

Compare an unconverted import with its original:

```sh
python3 tools/gamecube_draw_trace.py compare \
  local/evidence/source.jsonl local/evidence/import-raw.jsonl \
  --output local/evidence/material-pairs.json
```

The comparator recognizes the observed terrain combiner prefix and pairs
identical base/lightmap cache hashes. It reports every observed scale for
each pair, and rejects a comparison with no matching pairs as inconclusive.
Converted lightmaps intentionally have new hashes; verify those using the
transfer receipts and archive readback, then inspect actual gameplay.

For each new course, preserve source identity, transfer receipts, image and
geometry audits, a small original/import screenshot set, and device readback
identity. Keep lighting equivalence, environment fidelity, route visibility
and mobile performance as separate acceptance checks. The initial evidence
and remaining limitations are in the [Garibaldi comparison](garibaldi-visual-comparison.md).
