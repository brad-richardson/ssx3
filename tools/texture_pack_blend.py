#!/usr/bin/env python3
"""Blend over-inventing pack textures back toward a faithful upscale.

A detail model given a small block-compressed source does not see a smooth
gradient: it sees the 4x4 quantization the codec left behind, reads those block
edges as structure worth sharpening, and returns a hard speckled grid with
invented colour inside each block. On terrain that art is tiled, so the
invented motif repeats and reads as grid lines and patchy colour - which is
what SSX 3's snow came back looking like after `pack-v6`.

Re-running a different model is expensive and needs the GPU box. This does the
cheap half: keep the model's gain where it is real and pull it back toward a
plain Lanczos upscale where it is invention, choosing the blend weight *per
texture* from the same `local-shift` measure the audit gates on. A texture that
was already faithful keeps its full detail (weight 1.0); one that invented a
grid gets pulled back only as far as it takes to pass.

Alpha is never blended. A cutout's mask is load-bearing - the guest
alpha-*tests* foliage - and `upscale_textures.py` already re-thresholds it, so
the pack's alpha channel is copied through untouched.

  python3 tools/texture_pack_blend.py SOURCE_DIR PACK_DIR --output OUT \
      [--only-class block-compressed] [--target 12] [--classified DIR]

SOURCE_DIR is the dump the pack was built from (a directory of `tex1_*.png`,
one level of family subdirectories is fine). Textures outside the selection are
copied through unchanged, so the output is a complete pack.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import texture_pack_audit as audit  # noqa: E402  (after sys.path)

# Below the audit's own LOCAL_SHIFT threshold, so a blended pack passes with
# room rather than sitting exactly on the line.
TARGET = 12.0
# Weight search depth. Ten halvings resolve the weight to about 0.001, far
# finer than the measure is meaningful to.
STEPS = 10


def faithful_reference(source_image, scale):
    """A Lanczos upscale corrected to reduce back to its own source exactly.

    Plain Lanczos is smooth but not mean-preserving: box-reduced it does not
    return the source, and on noisy art the gap is large enough that the
    reference would fail the very target the blend is searching against,
    collapsing every weight to zero. Adding back the per-texel residual makes
    `box_down(reference, scale) == source` by construction, so the search
    always has a passing floor and the floor is a real image rather than
    pixel replication.
    """
    from PIL import Image
    import numpy as np
    size = (source_image.width * scale, source_image.height * scale)
    reference = np.asarray(source_image.resize(size, Image.LANCZOS), dtype=float)
    source = np.asarray(source_image, dtype=float)
    residual = source - audit.box_down(reference, scale)
    reference += np.repeat(np.repeat(residual, scale, axis=0), scale, axis=1)
    return np.clip(reference, 0, 255)


def shift_of(source, candidate):
    """The audit's local-shift for a candidate already at source resolution."""
    import numpy as np
    visible = source[..., 3] > 0
    if not visible.any():
        visible = np.ones(source.shape[:2], dtype=bool)
    return audit.local_shift(candidate[..., :3] - source[..., :3], visible)


def blend_arrays(reference, packed, weight):
    """Colour from a weighted mix; alpha straight from the pack."""
    import numpy as np
    out = packed.copy()
    out[..., :3] = reference[..., :3] * (1.0 - weight) + packed[..., :3] * weight
    return np.clip(out, 0, 255)


def choose_weight(source, reference, packed, scale, target=TARGET, steps=STEPS):
    """The largest blend weight whose local shift is still within target.

    Monotone in practice - mixing in more of the model's output can only move
    colour further from the source - so a bisection is enough, and it keeps
    every texture that never offended at full strength.
    """
    def measure(weight):
        candidate = blend_arrays(reference, packed, weight)
        reduced = audit.box_down(candidate, scale) if scale > 1 else candidate
        return shift_of(source, reduced)

    if measure(1.0) <= target:
        return 1.0, measure(1.0)
    low, high = 0.0, 1.0           # low passes (or is the floor), high fails
    for _ in range(steps):
        middle = (low + high) / 2
        if measure(middle) <= target:
            low = middle
        else:
            high = middle
    return low, measure(low)


def classified_names(directory, wanted):
    """Names living in a class subdirectory of a classification run."""
    chosen = set()
    for child in sorted(Path(directory).iterdir()):
        if child.is_dir() and (not wanted or child.name in wanted):
            chosen.update(path.name for path in child.glob('tex1_*.png'))
    return chosen


def blend_pack(source_dir, pack_dir, output_dir, names=None, target=TARGET):
    """Write a full pack to output_dir, blending the selected names."""
    from PIL import Image
    import numpy as np
    sources = audit.collect(Path(source_dir))
    packed_paths = audit.collect(Path(pack_dir))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {'source': str(source_dir), 'pack': str(pack_dir),
              'output': str(output_dir), 'target': target,
              'selected': 0, 'blended': 0, 'untouched': 0, 'copied': 0,
              'entries': []}
    for name, path in packed_paths.items():
        destination = output_dir / name
        selected = (names is None or name in names) and name in sources
        if not selected:
            shutil.copy2(path, destination)
            report['copied'] += 1
            continue
        report['selected'] += 1
        with Image.open(sources[name]) as image:
            source = np.asarray(image.convert('RGBA'), dtype=float)
            source_image = image.convert('RGBA')
        with Image.open(path) as image:
            packed_image = image.convert('RGBA')
        packed = np.asarray(packed_image, dtype=float)
        scale = packed.shape[1] / source.shape[1] if source.shape[1] else 0
        if (scale != int(scale) or scale < 1
                or packed.shape[0] != source.shape[0] * int(scale)):
            shutil.copy2(path, destination)     # not an integer upscale: leave it
            report['copied'] += 1
            report['selected'] -= 1
            continue
        scale = int(scale)
        reference = faithful_reference(source_image, scale)
        before = shift_of(source, audit.box_down(packed, scale) if scale > 1 else packed)
        weight, after = choose_weight(source, reference, packed, scale, target)
        if weight >= 1.0:
            shutil.copy2(path, destination)
            report['untouched'] += 1
        else:
            blended = blend_arrays(reference, packed, weight)
            Image.fromarray(blended.round().astype('uint8'), 'RGBA').save(destination)
            report['blended'] += 1
        report['entries'].append({'name': name, 'weight': round(weight, 4),
                                  'local_shift_before': round(before, 3),
                                  'local_shift_after': round(after, 3)})
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', type=Path, help='The dump the pack was built from')
    ap.add_argument('pack', type=Path, help='The pack to temper (base level only)')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--classified', type=Path,
                    help='A classification run (one subdirectory per class) to select from')
    ap.add_argument('--only-class', nargs='*', default=['block-compressed'],
                    help='Classes to blend; the rest are copied through')
    ap.add_argument('--target', type=float, default=TARGET,
                    help=f'Local-shift each blended texture must reach (default {TARGET})')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    names = None
    if args.classified:
        names = classified_names(args.classified, set(args.only_class))
        print(f'{len(names)} textures selected from {args.classified} '
              f'({", ".join(args.only_class)})')
    report = blend_pack(args.source, args.pack, args.output, names, args.target)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    worst = sorted(report['entries'], key=lambda e: e['weight'])[:10]
    print(f"selected {report['selected']}, blended {report['blended']}, "
          f"already faithful {report['untouched']}, copied through {report['copied']}")
    if worst:
        print('most tempered:')
        for entry in worst:
            print(f"  weight {entry['weight']:.3f}  "
                  f"{entry['local_shift_before']:6.1f} -> {entry['local_shift_after']:5.1f}  "
                  f"{entry['name']}")


if __name__ == '__main__':
    main()
