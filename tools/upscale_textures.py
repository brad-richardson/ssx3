#!/usr/bin/env python3
"""Upscale a directory of dumped game textures with a spandrel model, alpha kept separate.

Written for the RTX 4070 box (`ssh bytesize`), where torch and spandrel live in
a venv; it runs anywhere those import. Input names are Dolphin's texture-dump
convention (`tex1_<w>x<h>_<hash>[_<tlut hash>]_<format>.png`) and are preserved
exactly, because that name is the key the hi-res loader matches.

Alpha is not fed to the model. Super-resolution models are trained on opaque
RGB, and a game texture's alpha is usually a hard cutout, so the two are scaled
separately — RGB by the model, alpha by Lanczos — and recombined. `--mode
lanczos` skips the model entirely and is the baseline to compare against.

Fully transparent pixels carry no usable colour, so their RGB is filled from
the nearest opaque pixel before scaling (otherwise the model spreads the
background colour into the visible edge).
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

NAME_PREFIX = 'tex1_'


def opaque_fill(image):
    """Bleed edge colour into fully transparent pixels so scaling cannot halo."""
    from PIL import Image
    import numpy as np
    rgba = np.array(image)
    alpha = rgba[:, :, 3]
    if alpha.min() > 0 or alpha.max() == 0:
        return image
    # A few dilation passes are enough for the 1-2 pixel bleed that matters.
    rgb = rgba[:, :, :3].astype(np.float32)
    mask = (alpha > 0).astype(np.float32)[:, :, None]
    filled = rgb * mask
    weight = mask.copy()
    for _ in range(4):
        shifted_sum = np.zeros_like(filled)
        shifted_weight = np.zeros_like(weight)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            shifted_sum += np.roll(filled, (dy, dx), (0, 1))
            shifted_weight += np.roll(weight, (dy, dx), (0, 1))
        grow = (weight == 0) & (shifted_weight > 0)
        filled = np.where(grow, shifted_sum / np.maximum(shifted_weight, 1e-6), filled)
        weight = np.where(grow, 1.0, weight)
    out = rgba.copy()
    out[:, :, :3] = np.clip(filled, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def load_model(path, device):
    import torch
    from spandrel import ModelLoader
    model = ModelLoader().load_from_file(str(path))
    # fp32 throughout: these textures are tiny and half precision changes
    # results between the SPAN and DAT architectures.
    model.eval().to(device)
    return model


def run_model(model, image, device):
    """RGB through the model, one tile, no overlap logic: game textures are small."""
    import numpy as np
    import torch
    from PIL import Image
    rgb = np.array(image.convert('RGB'), dtype=np.float32) / 255.0
    tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        out = model(tensor)
    out = out.squeeze(0).permute(1, 2, 0).clamp(0, 1).cpu().numpy()
    return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8), 'RGB')


def upscale(image, model, scale, device):
    from PIL import Image
    source = opaque_fill(image) if image.mode == 'RGBA' else image
    if model is None:
        rgb = source.convert('RGB').resize(
            (source.width * scale, source.height * scale), Image.LANCZOS)
    else:
        rgb = run_model(model, source, device)
        if rgb.size != (source.width * scale, source.height * scale):
            rgb = rgb.resize((source.width * scale, source.height * scale), Image.LANCZOS)
    if image.mode != 'RGBA':
        return rgb
    alpha = image.getchannel('A').resize(rgb.size, Image.LANCZOS)
    out = rgb.convert('RGBA')
    out.putalpha(alpha)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', type=Path, help='Directory of dumped tex1_*.png files')
    ap.add_argument('output', type=Path, help='Directory for the upscaled copies')
    ap.add_argument('--model', type=Path, help='spandrel model file; omit for --mode lanczos')
    ap.add_argument('--mode', default='model', choices=('model', 'lanczos'))
    ap.add_argument('--scale', type=int, default=4, help='Expected scale factor (default 4)')
    ap.add_argument('--device', default='cuda', help='cuda, mps or cpu')
    ap.add_argument('--limit', type=int, help='Stop after this many images')
    ap.add_argument('--receipt', type=Path, help='Write a JSON receipt here')
    args = ap.parse_args()
    if args.mode == 'model' and not args.model:
        ap.error('--mode model needs --model')
    sources = sorted(p for p in args.source.iterdir()
                     if p.suffix.lower() == '.png' and p.name.startswith(NAME_PREFIX))
    if not sources:
        raise SystemExit(f'No {NAME_PREFIX}*.png files in {args.source}')
    if args.limit:
        sources = sources[:args.limit]
    args.output.mkdir(parents=True, exist_ok=True)
    device = args.device
    model = None
    if args.mode == 'model':
        import torch
        if device == 'cuda' and not torch.cuda.is_available():
            raise SystemExit('CUDA is not available on this host')
        model = load_model(args.model, device)
    from PIL import Image
    entries, started = [], time.monotonic()
    for path in sources:
        image = Image.open(path)
        image = image.convert('RGBA') if image.mode in ('RGBA', 'LA', 'P') else image.convert('RGB')
        result = upscale(image, model, args.scale, device)
        target = args.output / path.name
        result.save(target)
        entries.append({'name': path.name, 'source_size': list(image.size),
                        'output_size': list(result.size),
                        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        print(f'{path.name}: {image.size[0]}x{image.size[1]} -> {result.size[0]}x{result.size[1]}')
    receipt = {'mode': args.mode, 'model': str(args.model) if args.model else None,
               'model_sha256': hashlib.sha256(args.model.read_bytes()).hexdigest() if args.model else None,
               'device': device, 'scale': args.scale, 'images': len(entries),
               'seconds': round(time.monotonic() - started, 2), 'entries': entries}
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('mode', 'model', 'device', 'images', 'seconds')}, indent=2))


if __name__ == '__main__':
    main()
