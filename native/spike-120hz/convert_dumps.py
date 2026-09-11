#!/usr/bin/env python3
"""Convert SSX3_FRAMEGEN_DUMP raw BGRA triplets into PNGs and a side-by-side contact sheet.

Each dump is `frame-NNNNNN-{prev,cur,interp}.bgra`: two little-endian u32 (width, height)
followed by width*height*4 bytes of BGRA. This writes `frame-NNNNNN-{prev,cur,interp}.png`
plus `frame-NNNNNN-sheet.png` (prev | interp | cur, optionally cropped and scaled) and
prints a simple difference metric so a mismatch is visible in numbers as well as pixels.
"""
import argparse
from pathlib import Path
import struct

import numpy as np
from PIL import Image


def load(path):
    data = path.read_bytes()
    width, height = struct.unpack("<II", data[:8])
    pixels = np.frombuffer(data[8:8 + width * height * 4], dtype=np.uint8).reshape(height, width, 4)
    return Image.fromarray(pixels[:, :, [2, 1, 0]].copy(), "RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump_dir", type=Path)
    parser.add_argument("--out", type=Path, help="Output directory (default: the dump directory)")
    parser.add_argument("--crop", help="left,top,right,bottom crop applied to the contact sheet")
    parser.add_argument("--scale", type=float, default=1.0, help="Contact sheet scale factor")
    parser.add_argument("--keep-raw", action="store_true", help="Do not delete the .bgra files")
    args = parser.parse_args()
    out = args.out or args.dump_dir
    out.mkdir(parents=True, exist_ok=True)
    crop = tuple(int(v) for v in args.crop.split(",")) if args.crop else None
    frames = sorted({p.name.split("-")[1] for p in args.dump_dir.glob("frame-*-interp.bgra")})
    for frame in frames:
        images = {}
        for tag in ("prev", "cur", "interp"):
            raw = args.dump_dir / f"frame-{frame}-{tag}.bgra"
            if not raw.exists():
                break
            images[tag] = load(raw)
            images[tag].save(out / f"frame-{frame}-{tag}.png", optimize=True)
            if not args.keep_raw:
                raw.unlink()
        if len(images) != 3:
            continue
        prev = np.asarray(images["prev"], dtype=np.float32)
        cur = np.asarray(images["cur"], dtype=np.float32)
        interp = np.asarray(images["interp"], dtype=np.float32)
        blend = (prev + cur) / 2
        print(f"frame {frame}: mean|prev-cur|={np.abs(prev - cur).mean():.2f} "
              f"mean|interp-blend|={np.abs(interp - blend).mean():.2f} "
              f"mean|interp-cur|={np.abs(interp - cur).mean():.2f}")
        panels = []
        for tag in ("prev", "interp", "cur"):
            image = images[tag]
            if crop:
                image = image.crop(crop)
            if args.scale != 1.0:
                image = image.resize((round(image.width * args.scale), round(image.height * args.scale)),
                                     Image.LANCZOS)
            panels.append(image)
        sheet = Image.new("RGB", (sum(p.width for p in panels) + 2 * (len(panels) - 1), panels[0].height),
                          (255, 0, 255))
        x = 0
        for panel in panels:
            sheet.paste(panel, (x, 0))
            x += panel.width + 2
        sheet.save(out / f"frame-{frame}-sheet.png", optimize=True)


if __name__ == "__main__":
    main()
