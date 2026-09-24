#!/usr/bin/env python3
"""AU2: classify SND spike dumps (setdma-*/dmq-*.bin).

Per dump: size, zero fraction, (a) verbatim match of 64-byte windows inside
the named disc archives (compressed stream / bank bytes forwarded as-is),
(b) PS-ADPCM frame shape (16-byte frames: shift/filter byte + flag byte),
(c) s16le PCM smoothness (mean |d| / rms: ~1.4 for noise, <0.5 for audio),
(d) optional exact match of s16 PCM runs against a reference WAV.
Usage: au2_classify.py <dump-dir> <archive>[,<archive>...] [ref.wav]"""
import glob, math, os, struct, sys, wave

dumps = sorted(glob.glob(os.path.join(sys.argv[1], "*.bin")))
arch = {os.path.basename(p): open(p, "rb").read() for p in sys.argv[2].split(",")}
ref = None
if len(sys.argv) > 3:
    w = wave.open(sys.argv[3]); n = w.getnframes(); ch = w.getnchannels()
    ref = w.readframes(n); refch = ch


def archive_hits(b):
    hits = {}
    if len(b) < 64: return hits
    step = max(64, len(b) // 16)
    tried = 0
    for off in range(0, len(b) - 64, step):
        win = b[off:off + 64]
        if win.count(0) > 48: continue
        tried += 1
        for name, data in arch.items():
            i = data.find(win)
            if i >= 0:
                hits.setdefault(name, []).append((off, i))
    return hits, tried


def psadpcm(b):
    fr = [b[i:i + 16] for i in range(0, len(b) - 15, 16)]
    if not fr: return 0.0
    ok = sum(1 for x in fr if (x[0] >> 4) <= 4 and (x[0] & 15) <= 12 and x[1] in (0, 1, 2, 3, 4, 6, 7))
    return ok / len(fr)


def pcm_smooth(b):
    n = len(b) // 2
    if n < 64: return None
    s = struct.unpack(f"<{n}h", b[:2 * n])
    rms = math.sqrt(sum(x * x for x in s) / n) or 1.0
    d = sum(abs(s[i] - s[i - 1]) for i in range(1, n)) / (n - 1)
    return d / rms, rms


print("| Dump | Bytes | Zero % | Archive hits (dump off -> archive off) | PS-ADPCM-shaped | PCM |d|/rms, rms | Ref PCM match |")
print("| --- | ---: | ---: | --- | ---: | --- | --- |")
for p in dumps:
    b = open(p, "rb").read()
    if not b: continue
    z = b.count(0) / len(b)
    ah = archive_hits(b)
    hits, tried = ah if isinstance(ah, tuple) else ({}, 0)
    hs = "; ".join(f"{k}: {len(v)}/{tried} e.g. {v[0][0]:#x}->{v[0][1]:#x}" for k, v in hits.items()) or f"none/{tried}"
    ps = psadpcm(b)
    sm = pcm_smooth(b)
    smt = f"{sm[0]:.2f}, {sm[1]:.0f}" if sm else "-"
    rm = "-"
    if ref is not None and len(b) >= 64:
        probe = b[len(b) // 2: len(b) // 2 + 32]
        rm = "yes @%#x" % ref.find(probe) if probe.count(0) < 24 and ref.find(probe) >= 0 else "no"
    print(f"| `{os.path.basename(p)}` | {len(b)} | {100 * z:.0f} | {hs} | {ps:.2f} | {smt} | {rm} |")
