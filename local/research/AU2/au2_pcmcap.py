#!/usr/bin/env python3
"""AU2: turn the lldb tag-buffer capture (0x620-byte records from EE
0x512E40: tag-1 header {1, 0x600, 0, 0}, 384 stereo s16 frames, tag-5
{5, serial, ...}) into a WAV. Records are de-duplicated on the serial;
serial gaps are reported and left out.
Usage: au2_pcmcap.py <pcm.bin> <out.wav> [rate=36000]"""
import struct, sys, wave
src, out = sys.argv[1], sys.argv[2]
rate = int(sys.argv[3]) if len(sys.argv) > 3 else 36000
b = open(src, "rb").read(); R = 0x620
recs = []; bad = 0
for o in range(0, len(b) - R + 1, R):
    tag1, ln = struct.unpack_from("<II", b, o)
    tag5, serial = struct.unpack_from("<II", b, o + 0x610)
    if tag1 != 1 or ln != 0x600 or tag5 != 5:
        bad += 1; continue
    recs.append((serial, b[o + 0x10:o + 0x610]))
seen = {}; order = []
for s, pcm in recs:
    if s not in seen: seen[s] = pcm; order.append(s)
order.sort()
gaps = [(a, b_) for a, b_ in zip(order, order[1:]) if b_ - a != (order[1] - order[0] if len(order) > 1 else 1)]
step = (order[1] - order[0]) if len(order) > 1 else 0
w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
w.writeframes(b"".join(seen[s] for s in order)); w.close()
nz = sum(1 for s in order if any(seen[s]))
print(f"records {len(recs)} (bad layout {bad}), unique serials {len(order)} ({order[0] if order else '-'}..{order[-1] if order else '-'}, step {step}), "
      f"gaps {len(gaps)}, non-silent {nz}, seconds {len(order) * 384 / rate:.1f} -> {out}")
