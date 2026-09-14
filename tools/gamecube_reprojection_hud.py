#!/usr/bin/env python3
"""Recover the HUD tail's alpha from two captures of one movie frame.

One composited image cannot separate foreground from background. Two captures
of the *same* guest frame over two known constant backgrounds can, because the
tail's net effect on the background is affine:

    C = F + k * B        k = 1 - alpha, F = premultiplied foreground

Solved per channel from the pair, then checked against the untouched run, whose
real background is the rendered world. A blend the model does not describe --
anything reading destination colour non-linearly -- shows up as check error, so
the check result decides whether this is an alpha layer or another diagnostic.

  python3 tools/gamecube_reprojection_hud.py DARK.jsonl LIGHT.jsonl \
      --natural NATURAL.jsonl --output DIR
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from gamecube_reprojection_warp import load_capture

MATCHED = ('projection', 'viewport', 'scissor_offset', 'pixel_center_correction',
           'view', 'vertex_depth_range', 'reversed_depth', 'efb_pixel_format')
# Backgrounds closer than this leave k poorly conditioned at 8 bits per channel.
MIN_SEPARATION = 64


def background(capture):
    value = capture['split'].get('hud_clear')
    if value is None:
        raise ValueError(f"Capture was not cleared to a known background: {capture['path']}")
    return np.array([(value >> 16) & 255, (value >> 8) & 255, value & 255], dtype=float)


def same_frame(a, b, region=None):
    """Two runs of one movie must have reached an identical guest frame.

    Compared over the presented XFB area only. The EFB rows outside it are never
    redrawn, so a clear in one run persists there for the rest of that run and
    would otherwise reject every frame after the first.
    """
    if a['frame']['frame_id'] != b['frame']['frame_id']:
        raise ValueError('Captures are different frames')
    if a['frame']['late_perspective'] or b['frame']['late_perspective']:
        raise ValueError('Perspective draws follow the split; the tail is not HUD-only')
    for key in ('draws', 'perspective', 'ortho'):
        if a['frame'][key] != b['frame'][key]:
            raise ValueError(f'Runs diverged before the split: {key}')
    for key in MATCHED:
        if not np.allclose(np.asarray(a['split'][key], dtype=float),
                           np.asarray(b['split'][key], dtype=float), rtol=1e-6, atol=1e-7):
            raise ValueError(f'Runs disagree on {key}')
    # The scene behind the HUD is the strongest identity evidence available.
    active = np.s_[:] if region is None else region
    if (not np.array_equal(a['world'][active], b['world'][active]) or
            not np.array_equal(a['depth'][active], b['depth'][active])):
        raise ValueError('Runs rendered different world colour or depth for that frame')


def solve(dark, light):
    """Per-channel transmission and premultiplied foreground from the pair."""
    b0, b1 = background(dark), background(light)
    separation = b1 - b0
    if np.abs(separation).min() < MIN_SEPARATION:
        raise ValueError('Backgrounds are too close in some channel to separate alpha')
    c0 = dark['final'][:, :, :3].astype(float)
    c1 = light['final'][:, :, :3].astype(float)
    transmission = (c1 - c0) / separation
    foreground = c0 - transmission * b0
    return transmission, foreground


def active_region(capture):
    """The XFB area actually presented, in capture pixels."""
    height, width = capture['depth'].shape
    left, top, right, bottom = [int(v*s) for v, s in
                                zip(capture['frame']['xfb_rect'], [width/640, height/528]*2)]
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError('Invalid XFB crop')
    return np.s_[top:bottom, left:right]


def analyze(dark_path, light_path, natural_path, output):
    output.mkdir(parents=True, exist_ok=False)
    dark, light = load_capture(dark_path), load_capture(light_path)
    region = active_region(dark)
    same_frame(dark, light, region)
    transmission, foreground = solve(dark, light)
    alpha = 1 - transmission.mean(axis=2)
    natural = check = None
    if natural_path is not None:
        natural = load_capture(natural_path)
        if natural['split'].get('hud_clear') is not None:
            raise ValueError('The check run must not clear its background')
        same_frame(dark, natural, region)
        predicted = foreground + transmission * natural['world'][:, :, :3].astype(float)
        error = np.abs(np.clip(predicted, 0, 255) - natural['final'][:, :, :3].astype(float))
        check = dict(mean_abs_error=float(error[region].mean()), max_abs_error=float(error[region].max()),
                     within_one_level=float((error[region] <= 1).mean()),
                     within_two_levels=float((error[region] <= 2).mean()))
        Image.fromarray(np.clip(predicted, 0, 255).astype(np.uint8)).save(output/'predicted-final.png')
    layer = np.dstack([np.clip(foreground, 0, 255).astype(np.uint8),
                       np.clip(alpha*255, 0, 255).astype(np.uint8)])
    Image.fromarray(layer).save(output/'hud-premultiplied.png')
    Image.fromarray(np.clip(alpha*255, 0, 255).astype(np.uint8)).save(output/'hud-alpha.png')
    active = alpha[region]
    covered = active > 1/255
    report = dict(schema=1, frame_id=dark['frame']['frame_id'],
                  dark=str(dark_path), light=str(light_path),
                  natural=str(natural_path) if natural_path else None,
                  backgrounds=[int(dark['split']['hud_clear']), int(light['split']['hud_clear'])],
                  efb_pixel_format=dark['split']['efb_pixel_format'],
                  active_rect=list(dark['frame']['xfb_rect']),
                  covered_fraction=float(covered.mean()),
                  alpha_mean_where_covered=float(active[covered].mean()) if covered.any() else 0.0,
                  reconstruction_check=check,
                  # An affine solve is only an alpha layer if the untouched run agrees.
                  hud_alpha_layer=bool(check and check['max_abs_error'] <= 2),
                  limitations=['Alpha is exact only for blends that are affine in the destination '
                               'colour. The check run is the evidence that this frame is.',
                               'Per-channel transmission is averaged into one alpha; channels that '
                               'disagree indicate a per-channel blend, not a single coverage value.',
                               'One frame of one movie. Other HUD states and effects are unmeasured.',
                               'Only the presented XFB area is solved or compared. EFB rows outside it '
                               'keep whichever clear that run applied.',
                               'Recovering the layer offline says nothing about compositing it live.'])
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dark', type=Path)
    p.add_argument('light', type=Path)
    p.add_argument('--natural', type=Path, help='Untouched run of the same frame, to check the solve')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    analyze(args.dark, args.light, args.natural, args.output)


if __name__ == '__main__':
    main()
