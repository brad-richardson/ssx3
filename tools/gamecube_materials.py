"""Translate baked terrain lighting between verified GameCube engine conventions.

Tricky's terrain TEV stage multiplies base color by the lightmap at scale 1;
SSX 3 uses scale 2 before clamping. Copying Tricky sheets unchanged therefore
clips highlights. These are GX channel values, not sRGB values to gamma-correct.
See docs/garibaldi-visual-comparison.md for the paired draw-state evidence.
"""
import hashlib

from gamecube_textures import decode

LIGHTMAP_PROFILE = 'tricky-gc-to-ssx3-gc-v1'
PROFILES = (LIGHTMAP_PROFILE, 'raw')


def convert_lightmap(image, profile=LIGHTMAP_PROFILE):
    """Return a new image and an auditable transfer receipt; never mutate sources.

    RGBA8 avoids re-quantizing the halved channels to RGB565's 5/6 bits. After
    the target's 2x scale, each channel differs by at most one 8-bit code value
    before filtering/TEV rounding. Alpha remains opaque. This bound concerns
    this conversion only, not the final rendered scene.
    """
    if profile not in PROFILES:
        raise ValueError(f'Unknown lightmap material profile: {profile}')
    source_hash = hashlib.sha256(image['pixels']).hexdigest()
    if profile == 'raw':
        return dict(image), dict(profile=profile, source_pixels_sha256=source_hash,
                                 output_pixels_sha256=source_hash, converted=False)
    if image['type'] != 0x14:
        raise ValueError('Verified Tricky lighting transfer requires RGB565 lightmaps; '
                         'inspect the source material before adding another format')
    width, height = image['width'], image['height']
    if width <= 0 or height <= 0 or width % 4 or height % 4:
        raise ValueError('RGB565 lightmap dimensions must be positive multiples of four')
    if len(image['pixels']) != width * height * 2:
        raise ValueError('Truncated RGB565 lightmap')
    rgba = decode(image)
    pixels = bytearray()
    error = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            tile = []
            for y in range(4):
                for x in range(4):
                    src = rgba[(by + y) * width + bx + x]
                    dst = tuple((c + 1) // 2 for c in src[:3])
                    error = max(error, *(abs(min(255, 2 * d) - s) for d, s in zip(dst, src)))
                    tile.append((*dst, 255))
            # GX RGBA8: 4x4 tiles, 32 bytes of A/R followed by 32 of G/B.
            pixels.extend(c for r, g, b, a in tile for c in (a, r))
            pixels.extend(c for r, g, b, a in tile for c in (g, b))
    converted = dict(image, type=0x16, pixels=bytes(pixels), palette=None)
    return converted, dict(profile=profile, converted=True, source_format='RGB565',
                           output_format='RGBA8', source_tev_scale=1, target_tev_scale=2,
                           lightmap_gain=0.5, channel_domain='GX encoded channel values',
                           max_reconstructed_channel_error=error,
                           source_pixels_sha256=source_hash,
                           output_pixels_sha256=hashlib.sha256(pixels).hexdigest())
