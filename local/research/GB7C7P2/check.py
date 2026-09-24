#!/usr/bin/env python3
"""GB7C7P2 scripted acceptance: tick259 packet5470 texture-word tap.

Verifies capture/path pins, exactly one uncapped executed pixel row at
tick259/packet5470/path3/batch10/(342,377) with actual per-tap read
words/addresses (tap0 addr 0x000bae74, tap0 word RGB 353341), actual
storage destination words old_raw=dc302f3b new_raw=dc353341, accepted
write classification, replay completion, and ON/OFF common-frame plus
PPM equality. Emits A/B/OTHER with the first mismatch. Exit 0 when the
verdict line is emitted; exit 1 on checker internal error only.
"""
import hashlib
import os
import re
import sys

GB4 = os.path.expanduser("~/dev/ssx3-work/GB4")
SCRATCH = os.path.expanduser("~/dev/ssx3-work/GB7C7/run")
CAPTURE = os.path.join(GB4, "run", "gb4p4.capture.bin")
PATHS = os.path.join(GB4, "run", "gb4p4.paths.txt")
TAP = os.path.join(SCRATCH, "tap3.tsv")
ON_LOG = os.path.join(SCRATCH, "replay-on3.log")
HASH_ON = os.path.join(SCRATCH, "hashes-on3.txt")
HASH_OFF = os.path.join(SCRATCH, "hashes-off.txt")
HASH_ON1 = os.path.join(SCRATCH, "hashes-on.txt")
PPM_ON = os.path.join(SCRATCH, "ppm-on3")
PPM_OFF = os.path.join(SCRATCH, "ppm-off")
PIN_SHA = "a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851"

rows = []


def check(name, ok, detail=""):
    rows.append((name, bool(ok), detail))
    return bool(ok)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- pins ----
try:
    check("capture_sha", sha256(CAPTURE) == PIN_SHA, PIN_SHA[:12])
except OSError as e:
    check("capture_sha", False, f"unreadable: {e}")

try:
    with open(PATHS) as f:
        n = sum(1 for _ in f)
    check("paths_lines", n == 1982063, str(n))
except OSError as e:
    check("paths_lines", False, f"unreadable: {e}")

try:
    with open(PATHS) as f:
        line5471 = None
        for i, line in enumerate(f, 1):
            if i == 5471:
                line5471 = line.strip()
                break
    check("paths_5470", line5471 == "5470 3", repr(line5471))
except OSError as e:
    check("paths_5470", False, f"unreadable: {e}")

# ---- trace parse ----
pixrows = []
batchrows = []
header_ok = False
try:
    with open(TAP) as f:
        header = f.readline().rstrip("\n").split("\t")
    header_ok = header == ["tick", "packet", "path", "batch", "kind",
                           "dst_xy", "dst_addr", "old", "new",
                           "old_raw", "new_raw",
                           "src_uv", "taps", "tap_state", "blend",
                           "state", "test", "classification"]
    check("tap_header", header_ok, f"{len(header)}cols")
    with open(TAP) as f:
        next(f)
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) != 18:
                continue
            d = dict(zip(header, c))
            if d["kind"] == "pixel":
                pixrows.append(d)
            elif d["kind"] == "batch":
                batchrows.append(d)
    check("tap_parse", True, f"{len(batchrows)}batch+{len(pixrows)}pixel")
except OSError as e:
    check("tap_header", False, f"unreadable: {e}")
    check("tap_parse", False, "")

check("one_pixel_row", len(pixrows) == 1, f"n={len(pixrows)}")
p = pixrows[0] if len(pixrows) == 1 else {}

# ---- pixel identity ----
check("pix_tick", p.get("tick") == "259", p.get("tick", "-"))
check("pix_packet", p.get("packet") == "5470", p.get("packet", "-"))
check("pix_path", p.get("path") == "3", p.get("path", "-"))
check("pix_batch", p.get("batch") == "10", p.get("batch", "-"))
check("pix_xy", p.get("dst_xy") == "(342,377)", p.get("dst_xy", "-"))
check("pix_dstaddr", p.get("dst_addr") == "0019ae38", p.get("dst_addr", "-"))

# ---- batch10 row ----
b10 = [b for b in batchrows if b.get("tick") == "259" and
       b.get("packet") == "5470" and b.get("path") == "3" and
       b.get("batch") == "10"]
check("batch10_row", len(b10) == 1, f"n={len(b10)}")
if b10:
    st = b10[0].get("state", "")
    check("batch10_state",
          all(k in st for k in ("fst=1", "tme=1", "frame=fbp112",
                                "tex=tbp0-0,tbw8,psm0", "clamp=0x5")),
          st[:60])

# ---- tap recompute fields ----
if p:
    check("taps_quad",
          p.get("taps") == "pre=(343,378);(344,378);(343,379);(344,379) "
          "post=(343,378);(344,378);(343,379);(344,379)",
          (p.get("taps", "-"))[:40])
    ts = p.get("tap_state", "")
    m = re.search(r"addrs=\(([0-9a-f,]+)\) words=\(([0-9a-f,]+)\)", ts)
    addrs = m.group(1).split(",") if m else []
    words = m.group(2).split(",") if m else []
    check("tap0_addr", addrs[:1] == ["000bae74"], ",".join(addrs[:1]) or "-")
    check("tap0_word_rgb",
          len(words) > 0 and words[0][2:] == "353341", words[0] if words else "-")
    check("taps13_words",
          words[1:] == ["66302e3d", "8004051d", "8004051d"], ",".join(words[1:]) or "-")
    bl = p.get("blend", "")
    check("texel_rgb", "texel=63353341" in bl and "fx=0.0000" in bl
          and "fy=0.0000" in bl, bl)
    check("interp_uv", "interpF=(343.500,378.500)" in p.get("src_uv", ""),
          p.get("src_uv", "-")[:32])
    check("dst_old_raw", p.get("old_raw") == "dc302f3b", p.get("old_raw", "-"))
    check("dst_new_raw", p.get("new_raw") == "dc353341", p.get("new_raw", "-"))
    check("dst_logical_masked",
          p.get("old") == "00302f3b" and p.get("new") == "00353341",
          f"{p.get('old', '-')}>{p.get('new', '-')}")
    check("write_class", p.get("classification") == "accepted-write-changed",
          p.get("classification", "-"))
    st = p.get("state", "")
    check("pix_state",
          all(k in st for k in ("tex0=(tbp0=0,tbw=8,psm=0,tw=10,th=9,tcc=0,tfx=0",
                                "frame=(fbp=112,fbw=8,psm=1",
                                "vrt=(128,128,128,128)")),
          "state-ok" if True else "-")

# ---- uncapped + completion ----
cap_ok = summ_ok = False
markers = -1
passed = failed = None
try:
    log = open(ON_LOG).read()
    m = re.search(r"GB7C7_SUMMARY rows=(\d+) bytes=(\d+) capped=(\d)", log)
    cap_ok = bool(m) and m.group(3) == "0"
    check("uncapped", cap_ok, m.group(0) if m else "no-summary")
    m2 = re.search(r"markers=(\d+)", log)
    markers = int(m2.group(1)) if m2 else -1
    mp = re.search(r"Passed:\s*(\d+)", log)
    mf = re.search(r"Failed:\s*(\d+)", log)
    passed = int(mp.group(1)) if mp else None
    failed = int(mf.group(1)) if mf else None
    check("replay_complete",
          passed == 556 and failed == 0 and markers >= 301,
          f"pass={passed} fail={failed} markers={markers}")
except OSError as e:
    check("uncapped", False, f"unreadable: {e}")
    check("replay_complete", False, "")

# ---- ON/OFF equality ----
try:
    on = [l.strip() for l in open(HASH_ON) if l.strip()]
    off = [l.strip() for l in open(HASH_OFF) if l.strip()]
    common = min(len(on), len(off))
    mm = [i for i in range(common) if on[i] != off[i]]
    check("frame_hash_equal", common > 0 and not mm,
          f"on={len(on)} off={len(off)} common={common} mm={len(mm)}")
except OSError as e:
    check("frame_hash_equal", False, f"unreadable: {e}")

ppm_ok = True
ppm_detail = []
for t in (259, 300, 301):
    a = os.path.join(PPM_ON, f"vq-000{t}.ppm")
    b = os.path.join(PPM_OFF, f"vq-000{t}.ppm")
    try:
        ha, hb = sha256(a), sha256(b)
        same = ha == hb
    except OSError:
        same = False
        ha = hb = "unreadable"
    ppm_ok &= same
    ppm_detail.append(f"{t}:{'eq' if same else 'DIFF'}")
check("ppm_equal", ppm_ok, " ".join(ppm_detail))

# bridge note: ppm-on came from the build-2 binary while the final ON
# (hashes-on3) ran build-5 and OFF ran build-4 (adjacent binaries, no
# same-binary ON/OFF pair). Row equality across hashes-on/hashes-on3
# plus identical ON/OFF hashes/PPMs is the control; same-binary
# nonperturbation is unverified (see REPORT).
try:
    on1 = [l.strip() for l in open(HASH_ON1) if l.strip()]
    on2 = [l.strip() for l in open(HASH_ON) if l.strip()]
    check("on_binaries_equal", on1 == on2,
          f"build2rows={len(on1)} build5rows={len(on2)}")
except OSError as e:
    check("on_binaries_equal", False, f"unreadable: {e}")

verdict = "OTHER"
reason = "not-evaluated"
# B trigger: sample/address/word differs while the write is observed.
# (tap0 addr, tap0 word RGB, texel RGB are the sample/address/word.)
b_fields = [n for n in ("tap0_addr", "tap0_word_rgb", "texel_rgb",
                        "dst_old_raw", "dst_new_raw")
            if n in [r[0] for r in rows]]
b_fail = next((r[0] for r in rows if r[0] in
               ("tap0_addr", "tap0_word_rgb", "texel_rgb",
                "dst_old_raw", "dst_new_raw") and not r[1]), None)
first_fail = next((r[0] for r in rows if not r[1]), None)
if first_fail is None:
    verdict, reason = "A", "all-match"
elif b_fail is not None:
    verdict, reason = "B", f"first-diff={b_fail}"
else:
    verdict, reason = "OTHER", f"first-mismatch={first_fail}"

print("check\tpass\tdetail")
for name, passed_, detail in rows:
    print(f"{name}\t{'PASS' if passed_ else 'FAIL'}\t{detail}")
print(f"RESULT {verdict} reason={reason}")
