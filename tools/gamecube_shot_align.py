"""Align two screenshot sequences from different runs of the same movie.

Same movie + same guest frames, but wall-clock screenshot cadence and
different emulation speeds mean run B's frame j is NOT run A's frame j:
sequences differ by a start offset AND a rate ratio (a 2x run produces
half the frames for the same guest span). Comparing pairs by index, as
cross-device scorers historically did, compares different frames.

Model: j = round((i - offset) * rate), fit by coarse-to-fine search over
thumbnail SAD (16x12 stride-sampled RGB). Offset is in A-coordinates:
offset=k means B starts at A[k]; rate is B-frames per A-frame.

Pure-python, standard library only; reuses the hermetic PNG reader from
gamecube_snow_check.

Usage:
  python3 tools/gamecube_shot_align.py shots-A/ shots-B/
Prints offset/rate/mean-residual/pairs/confidence. Exit code is 1 when
no confident alignment exists (different content or drifting rate).

Known limits: assumes a CONSTANT rate (no mid-run speed changes) -- the
per-pair residuals expose drift when that breaks. The confidence
threshold is calibrated on synthetic + self pairs only; cross-backend
(OGL-vs-VK) calibration is the snow hunt's job.
"""
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import gamecube_snow_check as snow

THUMB_W = 16
THUMB_H = 12
COARSE_W = 8
COARSE_H = 6
RATE_MIN = 0.5
RATE_MAX = 2.0
RATE_COARSE_STEP = 0.1
OFFSET_REFINE_SPAN = 4
# Coarse scores EVERY pair (no striding): at real 2 s screenshot cadence
# adjacent race frames differ hugely, so a strided sample can land the
# true mapping entirely on off-by-one pairs and lose to chance. The
# coarse stage stays cheap via tiny thumbnails + the coarse rate grid.
COARSE_PAIR_STRIDE = 1
MIN_OVERLAP = 5
CONFIDENT_PAIRS = 10
# Mean thumbnail SAD per byte below which an alignment is trusted.
# Self-pairs score ~0.0; unrelated content scores ~30+.
CONFIDENT_SAD = 12.0
MARGIN_MIN = 0.05


def thumbnail(width, height, rgb, tw=THUMB_W, th=THUMB_H):
    """Stride-sample RGB bytes down to a tw x th thumbnail (bytes)."""
    out = bytearray(tw * th * 3)
    for ty in range(th):
        y = min(ty * height // th, height - 1)
        for tx in range(tw):
            x = min(tx * width // tw, width - 1)
            src = (y * width + x) * 3
            dst = (ty * tw + tx) * 3
            out[dst:dst + 3] = rgb[src:src + 3]
    return bytes(out)


def sad(a, b):
    """Sum of absolute byte differences between equal-length buffers."""
    return sum(abs(x - y) for x, y in zip(a, b))


def frange(start, stop, step):
    vals = []
    v = start
    while v <= stop + 1e-9:
        vals.append(round(v, 6))
        v += step
    return vals


def evaluate(thumbs_a, thumbs_b, offset, rate, pair_stride=1,
             min_overlap=MIN_OVERLAP):
    """Mean thumbnail SAD per byte over overlapping pairs; None if thin."""
    total, count = 0, 0
    scale = len(thumbs_a[0])
    for i in range(0, len(thumbs_a), pair_stride):
        j = round((i - offset) * rate)
        if 0 <= j < len(thumbs_b):
            total += sad(thumbs_a[i], thumbs_b[j])
            count += 1
    if count < min_overlap:
        return None
    return total / count / scale


def search(thumbs_a, thumbs_b, offsets, rates, pair_stride=1,
           min_overlap=MIN_OVERLAP):
    """Return (best, second_best) as (cost, offset, rate) tuples."""
    ranked = []
    for rate in rates:
        for offset in offsets:
            cost = evaluate(thumbs_a, thumbs_b, offset, rate,
                            pair_stride=pair_stride,
                            min_overlap=min_overlap)
            if cost is not None:
                ranked.append((cost, offset, rate))
    # Ties (static content) break toward the identity mapping; the
    # margin check still reports them WEAK.
    ranked.sort(key=lambda r: (r[0], abs(r[1]), abs(r[2] - 1.0)))
    while len(ranked) < 2:
        ranked.append((float('inf'), 0, 1.0))
    return ranked[0], ranked[1]


def align(coarse_a, coarse_b, fine_a, fine_b, max_offset=60):
    """Fit (offset, rate); returns dict with residual/pairs/confidence.

    Coarse stage scans the FULL offset grid (exact-match basins are one
    wide; a stepped grid skips over them) on tiny thumbnails with
    strided pairs; the fine stage refines around the winner at full
    resolution. Both sizes come from load_sequence.
    """
    max_offset = max(1, min(max_offset, len(fine_a) // 2 or 1))
    coarse_offsets = list(range(-max_offset, max_offset + 1))
    coarse_rates = frange(RATE_MIN, RATE_MAX, RATE_COARSE_STEP)
    # Coarse tolerates thin overlap: striding plus edge invalidity can
    # drop the true mapping to a handful of sampled pairs, and
    # disqualifying it there strands the fine stage on garbage.
    (_, best_off, best_rate), _ = search(
        coarse_a, coarse_b, coarse_offsets, coarse_rates,
        pair_stride=COARSE_PAIR_STRIDE, min_overlap=3)
    fine_offsets = list(range(best_off - OFFSET_REFINE_SPAN,
                               best_off + OFFSET_REFINE_SPAN + 1))
    fine_rates = frange(max(RATE_MIN, best_rate - RATE_COARSE_STEP),
                        min(RATE_MAX, best_rate + RATE_COARSE_STEP), 0.02)
    (cost, offset, rate), (second, _, _) = search(
        fine_a, fine_b, fine_offsets, fine_rates)
    pairs = sum(1 for i in range(len(fine_a))
                if 0 <= round((i - offset) * rate) < len(fine_b))
    margin = (second - cost) / second if second else 0.0
    confident = (pairs >= CONFIDENT_PAIRS and cost <= CONFIDENT_SAD
                 and margin >= MARGIN_MIN)
    return {'offset': offset, 'rate': rate, 'residual': cost,
            'pairs': pairs, 'margin': margin, 'confident': confident}


def load_sequence(directory):
    """Load sorted PNGs as (coarse, fine) thumbnail pairs plus names."""
    coarse, fine, names = [], [], []
    for path in sorted(Path(directory).glob('*.png')):
        if path.name.startswith('._'):
            continue
        width, height, rgb = snow.read_png_rgb(path)
        coarse.append(thumbnail(width, height, rgb,
                                tw=COARSE_W, th=COARSE_H))
        fine.append(thumbnail(width, height, rgb))
        names.append(path.name)
    if not fine:
        raise ValueError(f'{directory}: no screenshots found')
    return coarse, fine, names


def main(argv):
    if len(argv) != 2:
        print('usage: gamecube_shot_align.py shots-A/ shots-B/',
              file=sys.stderr)
        return 2
    try:
        coarse_a, fine_a, _ = load_sequence(argv[0])
        coarse_b, fine_b, _ = load_sequence(argv[1])
    except (OSError, ValueError) as error:
        print(f'ERROR {error}', file=sys.stderr)
        return 2
    result = align(coarse_a, coarse_b, fine_a, fine_b)
    print(f"A={argv[0]} ({len(fine_a)} shots) "
          f"B={argv[1]} ({len(fine_b)} shots)")
    print(f"offset={result['offset']} rate={result['rate']:.2f} "
          f"residual={result['residual']:.2f} pairs={result['pairs']} "
          f"margin={result['margin']:.3f} "
          f"verdict={'confident' if result['confident'] else 'WEAK'}")
    return 0 if result['confident'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
