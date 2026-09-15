#!/usr/bin/env python3
"""Sort a union of dumped textures into classes, each with the model that suits it.

Grouping by GX format alone (the first cut of this pipeline) puts a tiling snow
tile, a mountain backdrop and a rock face in one bucket because all three are
CMPR, and they do not want the same treatment. Three properties decide what a
texture needs, and all three are measurable from the dump:

* **does it tile** - its left edge already matches its right edge, so a model
  must be given circular padding or it will invent a seam that shows as a line
  along every tile boundary in game;
* **where its structure lives** - in colour, in alpha, or nowhere;
* **how soft its alpha is** - a hard cutout (a tree, a sign) is edges a model
  can sharpen, while a smooth radial falloff (smoke, spray, glow) is a gradient
  it will mistake for a blurred edge and give a hard rim.

The classes below are the outcome of the September 15 comparison over SSX 3's
907 course textures, recorded in `docs/texture-remaster.md`:

| class | test | model | wrap |
| --- | --- | --- | --- |
| `flat` | no colour and no alpha structure | Lanczos (exact on a flat fill) | auto |
| `soft-sprite` | most pixels partially transparent | Lanczos (nothing to reconstruct) | auto |
| `tile` | the source already wraps | PBRify SPAN (invents least, holds the seam) | yes |
| `block-compressed` | CMPR, not a tile | PBRify V4 (smooths CMPR blocks) | no |
| `paletted`, `direct-colour` | everything else | Real-ESRGAN (best on art and text) | no |
| `skip` | 8 pixels or less on a side | not replaced at all | - |

The output is one directory per class plus a JSON receipt naming the model each
one wants, so the upscale step is a loop over the plan rather than a judgement
call - which is the point: the decision is recorded here once, not re-made per
course by whoever runs the pipeline next.
"""
import argparse
import json
import shutil
from pathlib import Path

NAME_PREFIX = 'tex1_'

# Model per class. Paths are resolved by the caller on whichever box has them.
MODELS = {
    'flat': {'mode': 'lanczos', 'model': None, 'wrap': 'auto'},
    'soft-sprite': {'mode': 'lanczos', 'model': None, 'wrap': 'auto'},
    'tile': {'mode': 'model', 'model': '4x-PBRify_UpscalerSPAN_Neutral.pth', 'wrap': 'always'},
    'block-compressed': {'mode': 'model', 'model': '4x-PBRify-UpscalerV4.safetensors', 'wrap': 'never'},
    'paletted': {'mode': 'model', 'model': 'RealESRGAN_x4plus.pth', 'wrap': 'never'},
    'direct-colour': {'mode': 'model', 'model': 'RealESRGAN_x4plus.pth', 'wrap': 'never'},
}

BLOCK_FORMATS = {14}
PALETTED_FORMATS = {0, 1, 8, 9, 10}

FLAT_STD = 4.0
SOFT_ALPHA_FRACTION = 0.4
# A texture only a few pixels tall is not art: SSX 3's boot sequence draws its
# logos through 640x4 and 320x4 IA8 strips, and a model's guess at those tore
# the EA BIG and THX logos into horizontal bands. Nothing that thin has detail
# to reconstruct, so it is left alone rather than replaced.
THIN_SIDE = 8


def texture_format(name):
    """The GX format number, the last field of a dump name."""
    try:
        return int(name.rsplit('_', 1)[1].split('.')[0])
    except (IndexError, ValueError):
        return -1


def classify(path):
    """Which class this texture belongs to, and the measurements behind it."""
    from PIL import Image
    import numpy as np
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from upscale_textures import tileable
    with Image.open(path) as opened:
        image = opened.convert('RGBA')
    array = np.asarray(image, dtype=float)
    alpha = array[..., 3]
    visible = alpha > 0
    grey = array[..., 0] * 0.2126 + array[..., 1] * 0.7152 + array[..., 2] * 0.0722
    colour_std = float(grey[visible].std()) if visible.any() else 0.0
    alpha_std = float(alpha.std())
    partial = float(((alpha > 8) & (alpha < 247)).mean())
    tiles = bool(tileable(image))
    fmt = texture_format(path.name)

    if min(image.width, image.height) <= THIN_SIDE:
        name = 'skip'
    elif colour_std < FLAT_STD and alpha_std < FLAT_STD:
        name = 'flat'
    elif partial > SOFT_ALPHA_FRACTION:
        name = 'soft-sprite'
    elif tiles:
        name = 'tile'
    elif fmt in BLOCK_FORMATS:
        name = 'block-compressed'
    elif fmt in PALETTED_FORMATS:
        name = 'paletted'
    else:
        name = 'direct-colour'
    return name, {'colour_std': round(colour_std, 2), 'alpha_std': round(alpha_std, 2),
                  'partial_alpha': round(partial, 3), 'tiles': tiles, 'format': fmt}


def plan(union, output, copy=True):
    sources = sorted({p.name: p for p in union.rglob(f'{NAME_PREFIX}*.png')
                      if '_mip' not in p.name}.items())
    entries, counts = [], {}
    for name, path in sources:
        klass, measures = classify(path)
        counts[klass] = counts.get(klass, 0) + 1
        entries.append({'name': name, 'class': klass, **measures})
        if copy and klass != 'skip':
            directory = output / klass
            directory.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, directory / name)
    return {'union': str(union), 'output': str(output), 'textures': len(entries),
            'classes': dict(sorted(counts.items(), key=lambda kv: -kv[1])),
            'models': {k: v for k, v in MODELS.items() if k in counts},
            'entries': entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('union', type=Path, help='directory of distinct dumped textures')
    parser.add_argument('output', type=Path, help='directory to write <class>/ subdirectories in')
    parser.add_argument('--report', type=Path, help='JSON receipt')
    parser.add_argument('--dry-run', action='store_true', help='classify without copying')
    args = parser.parse_args()
    report = plan(args.union, args.output, copy=not args.dry_run)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    summary = {k: report[k] for k in ('textures', 'classes', 'models')}
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
