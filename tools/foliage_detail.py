#!/usr/bin/env python3
"""Rework an upscaled foliage cutout so it reads as needles rather than a blob.

A super-resolution model treats SSX 3's trees as photographs of trees, which
they are not: they are alpha-tested cards a few dozen pixels tall on screen,
and what sells them is the *silhouette*. Upscaling smooths that silhouette and
fattens it (the model's soft alpha, thresholded, covers more area than the
guest's), so the card reads as a green blob with a smooth outline - which is
exactly why the trees look the most dated part of the scene.

Three passes, each addressing something a model cannot know:

1. **Coverage-preserving alpha.** The threshold is chosen so the fraction of
   pixels that pass the game's alpha test matches the source's, which undoes
   the fattening instead of guessing at it.
2. **A silhouette cut from the card's own shading.** Along the outline, the
   darkest pixels are the gaps *between* needle sprays - the model drew them,
   it just kept them opaque. Cutting there opens those gaps, which is what
   makes an outline read as needles. Random noise was tried first and looks
   like bite marks; shading-driven cuts follow the tree the artist drew. Thin
   structures are protected by local thickness, so a bare branch keeps its
   twigs, and the cut only ever *removes* area - a cutout can never grow past
   the outline the guest drew.
3. **Canopy depth.** Tips are lifted and the interior near the trunk is
   dropped, by local thickness, then the mean is restored. A flat card gains
   the shading a round canopy would have, which is most of what separates
   2003 foliage from modern foliage at this size.

Everything is derived from the source card, so a course's own palette and snow
load carry over; nothing here invents a species.
"""
import argparse
import json
from pathlib import Path

NAME_PREFIX = 'tex1_'


def luma(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def coverage_threshold(alpha, want, lo=8.0, hi=250.0):
    """The cut that makes `alpha` cover the same fraction as the source did."""
    import numpy as np
    for _ in range(24):
        mid = (lo + hi) / 2
        if float((alpha >= mid).mean()) > want:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def distance_inside(mask):
    """Rough distance to the silhouette edge, in output pixels.

    A few dilation steps of the inverse mask are enough: the fringe only cares
    about the first handful of pixels, and this avoids a scipy dependency.
    """
    import numpy as np
    inside = mask.astype(np.float32)
    distance = np.zeros(mask.shape, dtype=np.float32)
    current = inside.copy()
    for step in range(1, 12):
        shrunk = current.copy()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            shrunk = np.minimum(shrunk, np.roll(current, (dy, dx), (0, 1)))
        distance[(current > 0) & (shrunk == 0)] = step
        current = shrunk
        if not current.any():
            break
    distance[(distance == 0) & mask] = 12
    return distance


def noise_field(shape, seed, scale_y, scale_x):
    """Value noise stretched along one axis, so notches are wider than tall."""
    import numpy as np
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, shape[0] // scale_y), max(2, shape[1] // scale_x)))
    ys = np.linspace(0, small.shape[0] - 1, shape[0])
    xs = np.linspace(0, small.shape[1] - 1, shape[1])
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    y1 = np.minimum(y0 + 1, small.shape[0] - 1); x1 = np.minimum(x0 + 1, small.shape[1] - 1)
    fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    top = small[y0][:, x0] * (1 - fx) + small[y0][:, x1] * fx
    bottom = small[y1][:, x0] * (1 - fx) + small[y1][:, x1] * fx
    return top * (1 - fy) + bottom * fy


def structure_direction(grey, blur=2):
    """Local orientation from the structure tensor, as unit (dy, dx)."""
    import numpy as np
    gy, gx = np.gradient(grey)
    def smooth(field):
        out = field.copy()
        for _ in range(blur):
            out = (out + np.roll(out, 1, 0) + np.roll(out, -1, 0)
                   + np.roll(out, 1, 1) + np.roll(out, -1, 1)) / 5.0
        return out
    jxx, jyy, jxy = smooth(gx * gx), smooth(gy * gy), smooth(gx * gy)
    # Principal direction of the tensor; detail runs along it.
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
    return np.sin(theta), np.cos(theta)


def thickness(mask, reach=6):
    """How solid the card is around each pixel: a blurred coverage fraction.

    A bare branch is thin everywhere, a canopy is not, and the difference is
    what decides whether opening the outline is safe.
    """
    import numpy as np
    field = mask.astype(np.float32)
    for _ in range(reach):
        field = (field + np.roll(field, 1, 0) + np.roll(field, -1, 0)
                 + np.roll(field, 1, 1) + np.roll(field, -1, 1)) / 5.0
    return field


def rework(upscaled, source, *, fringe=0.45, depth=0.10, seed=7):
    """Return a new cutout from the upscaled card and its own source."""
    from PIL import Image
    import numpy as np
    up = np.asarray(upscaled.convert('RGBA'), dtype=np.float32).copy()
    src = np.asarray(source.convert('RGBA'), dtype=np.float32)
    scale = max(1, up.shape[1] // src.shape[1])
    want = float((src[..., 3] >= 128).mean())

    # 1. coverage-preserving alpha
    cut = coverage_threshold(up[..., 3], want)
    mask = up[..., 3] >= cut
    if not mask.any():
        return upscaled
    grey = luma(up[..., :3])

    # 2. open the gaps the shading already shows, along the outline only
    if fringe > 0:
        distance = distance_inside(mask)
        band = (distance > 0) & (distance <= max(1, scale // 2))
        solid = thickness(mask, reach=3 * scale) > 0.55
        edge_values = grey[band & mask]
        if edge_values.size:
            # Cut the darkest `fringe` of the outline band - the gaps between
            # sprays - and only where the card is solid enough to spare them.
            level = float(np.quantile(edge_values, min(0.9, fringe)))
            cutaway = band & solid & (grey < level)
            mask = mask & ~cutaway

    # 3. canopy depth: lift the tips, drop the interior, keep the mean.
    # Only where there is a canopy: on a bare-branch card every pixel is a
    # "tip", so shading by thickness would just wash the whole tree pale.
    if depth > 0:
        solidity = thickness(mask, reach=4 * scale)
        dense = thickness(mask, reach=3 * scale) > 0.55
        shade = np.where(dense, 1.0 + depth * (0.45 - solidity) * 2.0, 1.0)
        before = grey[mask].mean() if mask.any() else 0.0
        for channel in range(3):
            up[..., channel] = np.clip(up[..., channel] * shade, 0, 255)
        after = luma(up[..., :3])[mask].mean() if mask.any() else 0.0
        if after > 1.0 and before > 1.0:
            up[..., :3] = np.clip(up[..., :3] * (before / after), 0, 255)

    out = up.copy()
    out[..., 3] = np.where(mask, 255.0, 0.0)
    # Hidden pixels keep the colour they had, so a leaked pixel is still foliage.
    return Image.fromarray(out.astype('uint8'), 'RGBA')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path, help='directory of source cards (the dump)')
    parser.add_argument('pack', type=Path, help='directory of upscaled cards')
    parser.add_argument('output', type=Path, help='directory for the reworked cards')
    parser.add_argument('--names', type=Path, help='JSON list of file names to rework')
    parser.add_argument('--limit', type=int, help='Only the first N names')
    parser.add_argument('--fringe', type=float, default=0.45,
                        help='Fraction of the outline band to open up (0 disables)')
    parser.add_argument('--depth', type=float, default=0.10,
                        help='Canopy shading strength (0 disables)')
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()

    from PIL import Image
    names = (json.loads(args.names.read_text()) if args.names
             else sorted(p.name for p in args.pack.glob(f'{NAME_PREFIX}*.png')))
    if args.limit:
        names = names[:args.limit]
    sources = {p.name: p for p in args.source.rglob(f'{NAME_PREFIX}*.png')}
    args.output.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in names:
        if name not in sources or not (args.pack / name).is_file():
            continue
        with Image.open(sources[name]) as source, Image.open(args.pack / name) as packed:
            result = rework(packed, source, fringe=args.fringe, depth=args.depth, seed=args.seed)
        result.save(args.output / name)
        import numpy as np
        want = float((np.asarray(source.convert('RGBA'))[..., 3] >= 128).mean())
        got = float((np.asarray(result)[..., 3] >= 128).mean())
        entries.append({'name': name, 'source_coverage': round(want, 4),
                        'result_coverage': round(got, 4)})
    report = {'source': str(args.source), 'pack': str(args.pack), 'output': str(args.output),
              'fringe': args.fringe, 'depth': args.depth, 'cards': len(entries),
              'entries': entries}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('cards', 'fringe', 'depth', 'output')}, indent=2))


if __name__ == '__main__':
    main()
