#!/usr/bin/env python3
"""MF1 offline analysis: quality (OUT vs GT), baselines (A/B vs GT), PNGs, contact sheet.

Usage: python3 analyze.py <run-dir> [<run-dir> ...]
Each run dir holds A.rgba B.rgba GT.rgba UI.rgba OUT.rgba (BGRA8) + run.json.
Writes metrics.json, *.png, contact.png into the run dir.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def load_rgba(path, w, h):
    a = np.fromfile(path, dtype=np.uint8)
    assert a.size == w * h * 4, (path, a.size, w * h * 4)
    return a.reshape(h, w, 4)[:, :, [2, 1, 0]].astype(np.float32)  # -> RGB float


def regions(w, h):
    rect_w, rect_h = w // 4, h // 2
    rect_y = (h - rect_h) // 2
    rx_a = round(w / 2 - 16 - rect_w / 2)
    rx_b, rx_g = rx_a + 32, rx_a + 16
    hud_h = h * 8 // 100
    yy, xx = np.mgrid[0:h, 0:w]
    in_a = (xx >= rx_a) & (xx < rx_a + rect_w) & (yy >= rect_y) & (yy < rect_y + rect_h)
    in_b = (xx >= rx_b) & (xx < rx_b + rect_w) & (yy >= rect_y) & (yy < rect_y + rect_h)
    in_g = (xx >= rx_g) & (xx < rx_g + rect_w) & (yy >= rect_y) & (yy < rect_y + rect_h)
    hud = yy < hud_h
    # motion-boundary band: within 4px of GT rect edge, outside GT rect
    edge_dist = np.minimum(
        np.minimum(np.abs(xx - rx_g), np.abs(xx - (rx_g + rect_w))),
        np.minimum(np.abs(yy - rect_y), np.abs(yy - (rect_y + rect_h))),
    )
    band = (edge_dist <= 4) & ~in_g & ~hud
    interior = np.zeros_like(in_g)
    interior[rect_y + 4:rect_y + rect_h - 4, rx_g + 4:rx_g + rect_w - 4] = True
    interior &= ~hud
    static = ~(in_a | in_b | in_g) & ~hud
    return {"hud": hud, "interior": interior, "band": band, "static": static,
            "all": np.ones((h, w), bool)}


def mae(a, b, mask):
    d = np.abs(a.astype(np.float32) - b.astype(np.float32))[mask]
    return float(d.mean()), float(d.max()), float((d > 4).mean() * 100)


def analyze(run):
    run = Path(run)
    meta = json.loads((run / "run.json").read_text())
    w, h = meta["width"], meta["height"]
    a = load_rgba(run / "A.rgba", w, h)
    b = load_rgba(run / "B.rgba", w, h)
    gt = load_rgba(run / "GT.rgba", w, h)
    if meta.get("colorfmt") == "rgba16f":
        out = np.fromfile(run / "OUT.as16f", dtype=np.float16).reshape(h, w, 4)
        out = (np.clip(out[:, :, :3].astype(np.float32), 0, 1) * 255)
    else:
        out = load_rgba(run / "OUT.rgba", w, h)
    if meta.get("ui") == "separate":
        # Reference for the UI path: GT world + UI strip composited (alpha=1 strip).
        ui = np.fromfile(run / "UI.rgba", dtype=np.uint8).reshape(h, w, 4)
        has_ui = ui[:, :, 3] > 0
        gt[has_ui] = ui[has_ui][:, [2, 1, 0]].astype(np.float32)
    regs = regions(w, h)
    m = {"run": run.name, "width": w, "height": h,
         "motion": meta.get("motion"), "ui": meta.get("ui")}
    for label, ref in (("out_vs_gt", out), ("a_vs_gt", a), ("b_vs_gt", b)):
        m[label] = {}
        for rname, mask in regs.items():
            mean, mx, pct = mae(ref, gt, mask)
            m[label][rname] = {"mae": round(mean, 4), "max": round(mx, 1),
                               "pct_gt4": round(pct, 3), "npix": int(mask.sum())}
    (run / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    for name, arr in (("A", a), ("B", b), ("GT", gt), ("OUT", out)):
        Image.fromarray(arr.astype(np.uint8)).save(run / f"{name}.png")
    diff = np.abs(out - gt).mean(axis=2)
    Image.fromarray(np.clip(diff * 4, 0, 255).astype(np.uint8)).save(run / "diff4x.png")
    thumbs = [Image.open(run / f"{n}.png").resize((w // 3, h // 3)) for n in ("A", "GT", "OUT")]
    sheet = Image.new("RGB", (w // 3 * 3, h // 3))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i * w // 3, 0))
    sheet.save(run / "contact.png")
    print(f"{run.name}: OUTvsGT all={m['out_vs_gt']['all']['mae']} static={m['out_vs_gt']['static']['mae']} "
          f"interior={m['out_vs_gt']['interior']['mae']} band={m['out_vs_gt']['band']['mae']} hud={m['out_vs_gt']['hud']['mae']}")


if __name__ == "__main__":
    for r in sys.argv[1:]:
        analyze(r)
