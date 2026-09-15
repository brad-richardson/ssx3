#!/usr/bin/env python3
"""Audit an upscaled texture pack against the dump it was built from.

An upscaler is free to invent detail, and that is what it is for, but four
kinds of invention are defects rather than gains:

* **colour shift** — the pack's average colour differs from the source's, so
  the art changes hue or brightness on screen even before any detail lands.
* **local shift** — the average matches but a *region* does not, so the art
  changes colour in patches. This needs its own check because the upscaler's
  own colour matching restores the mean, which is what the whole-texture
  measure looks at: a model that invents warmth in one corner and cools
  another passes "colour shift" with a perfect score. Small block-compressed
  sources are the ones this catches, because their 4x4 codec quantization
  reads to a detail model as structure worth sharpening.
* **structure drift** — reduced back to the source's own resolution, the pack
  no longer matches it, so the model has moved edges rather than sharpened
  them.
* **alpha drift** — the cutout mask has moved, which shows up as a fringe or a
  chewed edge on sprites and foliage.
* **flat invention** — the source is a flat or near-flat fill and the pack has
  grain in it; there was nothing there to reconstruct. "Flat" has to mean flat
  in *alpha as well as colour*: a font sheet or a glow sprite is white
  everywhere it is visible, so its colour variance is zero while all of its
  shape sits in the alpha channel, and those upscale well. Only a texture with
  neither colour nor alpha structure has nothing for a model to work from.

Each texture is compared with its own source at the source's resolution: the
pack is box-averaged back down by its scale factor, which is the closest thing
to "what the guest would have authored". Colour statistics only count pixels
the source shows (alpha > 0), so a transparent border cannot dominate them.

The result is a JSON receipt plus a ranked list of the textures worth looking
at. It does not decide whether a pack is good - it decides which few of several
hundred textures a human (or a later model) should open first.
"""
import argparse
import json
from pathlib import Path

# Defect thresholds, in 0-255 units. Chosen against the SSX 3 pack: every
# measure sits near zero for the bulk of a good pack, so these flag the tail
# rather than a fraction of everything.
COLOUR_SHIFT = 6.0
STRUCTURE_DRIFT = 12.0
ALPHA_DRIFT = 8.0
FLAT_SOURCE_STD = 4.0
FLAT_INVENTION = 3.0
LOCAL_SHIFT = 16.0
LOCAL_TILES = 8

LUMA = (0.2126, 0.7152, 0.0722)


def load_rgba(path):
    from PIL import Image
    import numpy as np
    with Image.open(path) as image:
        return np.asarray(image.convert('RGBA'), dtype=float)


def box_down(array, factor):
    """Average factor x factor blocks - the inverse of an integer upscale."""
    h, w = array.shape[0] // factor, array.shape[1] // factor
    trimmed = array[:h * factor, :w * factor]
    return trimmed.reshape(h, factor, w, factor, array.shape[2]).mean(axis=(1, 3))


def luma(rgb):
    return rgb[..., 0] * LUMA[0] + rgb[..., 1] * LUMA[1] + rgb[..., 2] * LUMA[2]


def local_shift(delta, visible):
    """Worst tile-average of the per-texel colour error.

    Pooling matters: a mean over the whole texture cancels a warm region
    against a cool one, and the upscaler's colour matching guarantees that
    cancellation by construction.
    """
    import numpy as np
    height, width = visible.shape
    tile = max(1, min(height, width) // LOCAL_TILES)
    magnitude = np.where(visible, np.abs(delta).max(axis=2), 0.0)
    rows, columns = height // tile, width // tile
    if not (rows and columns):
        return float(magnitude.max())
    tiles = magnitude[:rows * tile, :columns * tile]
    return float(tiles.reshape(rows, tile, columns, tile).mean(axis=(1, 3)).max())


def measure(source_path, pack_path):
    """Compare one pack texture with its source. Returns None if unusable."""
    import numpy as np
    source = load_rgba(source_path)
    pack = load_rgba(pack_path)
    if source.shape[0] == 0 or source.shape[1] == 0:
        return None
    scale = pack.shape[1] / source.shape[1]
    if scale != int(scale) or scale < 1 or pack.shape[0] != source.shape[0] * int(scale):
        return {'name': pack_path.name, 'scale': pack.shape[1] / source.shape[1],
                'flags': ['scale-mismatch'],
                'source_size': [source.shape[1], source.shape[0]],
                'pack_size': [pack.shape[1], pack.shape[0]]}
    scale = int(scale)
    reduced = box_down(pack, scale) if scale > 1 else pack

    visible = source[..., 3] > 0
    if not visible.any():
        visible = np.ones(source.shape[:2], dtype=bool)
    delta = reduced[..., :3] - source[..., :3]
    bias = [float(delta[..., c][visible].mean()) for c in range(3)]
    source_luma = luma(source[..., :3])
    rms = float(np.sqrt((luma(delta)[visible] ** 2).mean()))
    alpha_rms = float(np.sqrt(((reduced[..., 3] - source[..., 3]) ** 2).mean()))

    # High-frequency energy the pack holds below the source's texel grid: what
    # the model invented, as opposed to what it carried over.
    if scale > 1:
        carried = np.repeat(np.repeat(reduced, scale, axis=0), scale, axis=1)
        invented = float(luma(pack[..., :3] - carried[..., :3]).std())
    else:
        invented = 0.0
    # Local colour shift. `bias` is a mean over the whole texture, so a model
    # that invents warmth in one region and cools another scores a perfect
    # colour match - and match_colour() in the upscaler restores exactly that
    # mean, which makes the whole-texture number blind by construction. Pool
    # the per-texel error into a grid of tiles and keep the worst tile.
    shift = local_shift(delta, visible)

    source_std = float(source_luma[visible].std())
    alpha_std = float(source[..., 3].std())

    flags = []
    if max(abs(b) for b in bias) > COLOUR_SHIFT:
        flags.append('colour-shift')
    if rms > STRUCTURE_DRIFT:
        flags.append('structure-drift')
    if shift > LOCAL_SHIFT:
        flags.append('local-shift')
    if alpha_rms > ALPHA_DRIFT:
        flags.append('alpha-drift')
    if (source_std < FLAT_SOURCE_STD and alpha_std < FLAT_SOURCE_STD
            and invented > FLAT_INVENTION):
        flags.append('flat-invention')
    return {'name': pack_path.name, 'scale': scale,
            'source_size': [source.shape[1], source.shape[0]],
            'bias': [round(b, 3) for b in bias],
            'max_bias': round(max(abs(b) for b in bias), 3),
            'rms': round(rms, 3), 'alpha_rms': round(alpha_rms, 3),
            'local_shift': round(shift, 3),
            'invented': round(invented, 3), 'source_std': round(source_std, 3),
            'alpha_std': round(alpha_std, 3),
            'flags': flags}


def collect(directory):
    """Every dumped texture under a directory, including one level of families."""
    found = {}
    for path in sorted(directory.rglob('tex1_*.png')):
        found.setdefault(path.name, path)
    return found


def audit(source_dir, pack_dir):
    sources = collect(source_dir)
    packed = collect(pack_dir)
    results = []
    for name in sorted(packed):
        if name not in sources:
            results.append({'name': name, 'flags': ['no-source']})
            continue
        entry = measure(sources[name], packed[name])
        if entry is not None:
            results.append(entry)
    missing = sorted(set(sources) - set(packed))
    flagged = [r for r in results if r['flags']]
    counts = {}
    for entry in flagged:
        for flag in entry['flags']:
            counts[flag] = counts.get(flag, 0) + 1
    scored = [r for r in results if 'rms' in r]
    return {
        'source': str(source_dir), 'pack': str(pack_dir),
        'textures': len(results), 'unreplaced': len(missing),
        'flagged': len(flagged), 'flag_counts': counts,
        'thresholds': {'colour_shift': COLOUR_SHIFT, 'structure_drift': STRUCTURE_DRIFT,
                       'alpha_drift': ALPHA_DRIFT, 'flat_source_std': FLAT_SOURCE_STD,
                       'flat_invention': FLAT_INVENTION, 'local_shift': LOCAL_SHIFT},
        'medians': {key: round(sorted(r[key] for r in scored)[len(scored) // 2], 3)
                    for key in ('max_bias', 'local_shift', 'rms', 'alpha_rms',
                               'invented')} if scored else {},
        'worst': sorted(scored, key=lambda r: -r['rms'])[:20],
        'entries': results,
        'missing': missing[:50],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path, help='dump the pack was built from')
    parser.add_argument('pack', type=Path, help='upscaled pack')
    parser.add_argument('--output', type=Path, help='JSON receipt')
    parser.add_argument('--copy-flagged', type=Path,
                        help='copy each flagged texture, source and pack, here for review')
    parser.add_argument('--limit-flagged', type=int, default=24)
    args = parser.parse_args()

    report = audit(args.source, args.pack)
    if args.copy_flagged:
        import shutil
        sources = collect(args.source)
        packed = collect(args.pack)
        source_out = args.copy_flagged / 'source'
        pack_out = args.copy_flagged / 'pack'
        source_out.mkdir(parents=True, exist_ok=True)
        pack_out.mkdir(parents=True, exist_ok=True)
        flagged = [r for r in report['entries'] if r['flags'] and r['name'] in sources]
        flagged.sort(key=lambda r: -r.get('rms', 0))
        for entry in flagged[:args.limit_flagged]:
            shutil.copy2(sources[entry['name']], source_out / entry['name'])
            shutil.copy2(packed[entry['name']], pack_out / entry['name'])
        report['copied_flagged'] = min(len(flagged), args.limit_flagged)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    summary = dict(report)
    summary.pop('entries')
    summary['worst'] = [{k: w[k] for k in ('name', 'rms', 'max_bias', 'flags')}
                        for w in summary['worst'][:10]]
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
