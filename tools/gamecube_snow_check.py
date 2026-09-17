"""Ground/snow corruption scorer for SSX 3 GameCube screenshots.

Detects the in-race ground-corruption signature seen on the Odin3 OGL/EGL
backend: near-black ground and saturated green/red garbage replacing snow in
the lower frame band, while sky/trees/riders/HUD stay correct. The same
scorer also fires on the post-restart orange-streak ground seen on Metal,
which is corrupted snow by the same definition (see calibration below).

Pure-python, standard library only: PNG decoding is implemented here so the
regression test stays hermetic (Dolphin screenshots are 8-bit RGB,
non-interlaced).

Calibration (ground band x 0.25-0.75, y 0.55-0.90, every 2nd pixel):
  clean in-race (iPad Metal stock, 6 shots) .......... <= 0.05
  Odin menus ........................................ <= 0.08
  corrupt transition frames ......................... >= 0.17
  full black / psychedelic ground ................... >= 0.38
Threshold 0.12 separates clean from corrupt with margin on both sides.

Known gap: the early flat-blue stage (ground renders as untextured dark
blue before going black) scores ~0.0 -- it is missing detail, not garbage,
and mean/luminance statistics do not separate it from clean snow. It needs
visual review, not this scorer.

Usage:
  python3 tools/gamecube_snow_check.py SHOT.png [SHOT.png ...]
  python3 tools/gamecube_snow_check.py shots-dir/
Exit code is 1 when any scored frame is corrupt.
"""
import struct
import sys
import zlib
from pathlib import Path

REGION_X = (0.25, 0.75)
REGION_Y = (0.55, 0.90)
STRIDE = 2
BLACK_MAX = 20
PSYCH_SATURATION = 90
PSYCH_BRIGHTNESS = 90
CORRUPT_THRESHOLD = 0.12


def classify_pixel(r, g, b):
    """Classify one ground-band pixel: 'black', 'psychedelic', or 'ok'.

    Saturated blue-dominant pixels are excluded: the course-edge tape and
    blue shadows are legitimately saturated blue, while the garbage
    signature is green/red (or orange) dominant.
    """
    mx = max(r, g, b)
    if mx < BLACK_MAX:
        return 'black'
    if mx - min(r, g, b) > PSYCH_SATURATION and mx > PSYCH_BRIGHTNESS \
            and b <= max(r, g):
        return 'psychedelic'
    return 'ok'


def score_pixels(width, height, rows):
    """Score row-major RGB bytes; returns dict with fractions and verdict."""
    x0, x1 = int(width * REGION_X[0]), int(width * REGION_X[1])
    y0, y1 = int(height * REGION_Y[0]), int(height * REGION_Y[1])
    black = psych = total = 0
    for y in range(y0, y1, STRIDE):
        offset = y * width * 3
        for x in range(x0, x1, STRIDE):
            i = offset + x * 3
            verdict = classify_pixel(rows[i], rows[i + 1], rows[i + 2])
            total += 1
            black += verdict == 'black'
            psych += verdict == 'psychedelic'
    corrupt = (black + psych) / total if total else 0.0
    return {'black': black / total if total else 0.0,
            'psychedelic': psych / total if total else 0.0,
            'corrupt': corrupt,
            'verdict': 'corrupt' if corrupt > CORRUPT_THRESHOLD else 'clean'}


def read_png_rgb(path):
    """Read an 8-bit RGB/RGBA non-interlaced PNG; returns (w, h, rgb_bytes)."""
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: not a PNG')
    pos, raw = 8, bytearray()
    width = height = color = None
    while pos + 8 <= len(data):
        (length, kind) = struct.unpack('>I4s', data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b'IHDR':
            width, height, depth, color, comp, filt, inter = \
                struct.unpack('>IIBBBBB', chunk)
            if depth != 8 or color not in (2, 6) or inter != 0:
                raise ValueError(f'{path}: unsupported PNG kind '
                                 f'(depth={depth} color={color} '
                                 f'interlace={inter})')
        elif kind == b'IDAT':
            raw += chunk
        elif kind == b'IEND':
            break
    if width is None:
        raise ValueError(f'{path}: missing IHDR')
    channels = 3 if color == 2 else 4
    stride = width * channels
    pixels = zlib.decompress(bytes(raw))
    rows = bytearray(width * height * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        f = pixels[p]
        p += 1
        cur = bytearray(pixels[p:p + stride])
        p += stride
        if f == 1:
            for i in range(channels, stride):
                cur[i] = (cur[i] + cur[i - channels]) & 0xFF
        elif f == 2:
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                left = cur[i - channels] if i >= channels else 0
                cur[i] = (cur[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                left = cur[i - channels] if i >= channels else 0
                up = prev[i]
                up_left = prev[i - channels] if i >= channels else 0
                q = left + up - up_left
                pa, pb, pc = abs(q - left), abs(q - up), abs(q - up_left)
                pred = left if (pa <= pb and pa <= pc) else \
                    (up if pb <= pc else up_left)
                cur[i] = (cur[i] + pred) & 0xFF
        elif f != 0:
            raise ValueError(f'{path}: bad filter {f}')
        out = y * width * 3
        if channels == 3:
            rows[out:out + width * 3] = cur
        else:
            for x in range(width):
                rows[out + x * 3:out + x * 3 + 3] = cur[x * 4:x * 4 + 3]
        prev = cur
    return width, height, bytes(rows)


def score_file(path):
    width, height, rows = read_png_rgb(path)
    result = score_pixels(width, height, rows)
    result['path'] = str(path)
    return result


def main(argv):
    paths = []
    for arg in argv:
        entry = Path(arg)
        if entry.is_dir():
            paths.extend(sorted(entry.glob('*.png')))
        else:
            paths.append(entry)
    if not paths:
        print('no screenshots found', file=sys.stderr)
        return 2
    worst = 0.0
    any_corrupt = False
    for path in paths:
        try:
            result = score_file(path)
        except (OSError, ValueError) as error:
            print(f'{path}: ERROR {error}')
            return 2
        print(f"{result['path']}: {result['verdict']} "
              f"corrupt={result['corrupt']:.3f} "
              f"(black={result['black']:.3f} "
              f"psych={result['psychedelic']:.3f})")
        worst = max(worst, result['corrupt'])
        any_corrupt |= result['verdict'] == 'corrupt'
    print(f'{len(paths)} shots, worst={worst:.3f}')
    return 1 if any_corrupt else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
