# SSX Tricky course inventory

Date: 2026-09-10. Output of `tools/inventory_tricky.py` over the NTSC-U Tricky
disc (`DATA/MODELS/*.BIG`). Slope is the average of an elevation-slice path;
drop is the Z extent. Full per-course detail (members by extension, texture and
lightmap references, surface types) is in the JSON report the tool writes;
it is not checked in because it embeds disc-derived tables.

```text
ALASKA     5504042 stored   9317419 decoded; 3449 patches, drop 259545, slope 55.5 deg
ALOHA      4938572 stored   9201467 decoded; 2871 patches, drop 118272, slope 49.2 deg
ELYSIUM    5034732 stored  10750797 decoded; 4268 patches, drop 253960, slope 43.5 deg
GARI       4382471 stored  10302926 decoded; 3885 patches, drop 274144, slope 49.7 deg
MEGAPLE    2867274 stored   5589502 decoded; 730 patches, drop 51984, slope 27.6 deg
MERQUER    5004270 stored  11127521 decoded; 2731 patches, drop 249662, slope 31.4 deg
MESA       4461956 stored   9602063 decoded; 2448 patches, drop 154767, slope 44.7 deg
PIPE       2514707 stored   5127511 decoded; 2332 patches, drop 30633, slope 33.3 deg
SNOW       3906605 stored   8298749 decoded; 1653 patches, drop 135941, slope 33.9 deg
UNTRACK    3288310 stored   6437061 decoded; 4117 patches, drop 297681, slope 53.7 deg
TRICK      1041929 stored   2166991 decoded; 351 patches, drop 44576, slope 38.6 deg
SSXFE      3621224 stored   5912578 decoded; 546 patches, drop 18619, slope 53.7 deg
```

Notes:

- Nine courses plus `UNTRACK` (Untracked, the race-only variant) are real
  courses; `TRICK` (351 patches) and `SSXFE` (546) are the trick-tutorial and
  front-end scenes.
- Every course has between 730 and 4,268 patches. At 440 bytes per SSX 3
  record the largest is 1.9 MB of terrain, under a fifth of an SSX 3 race
  location's ~11 MB decoded budget (docs/location-anatomy.md). Textures (each
  course decodes to 5–11 MB in Tricky's own formats) will dominate, not terrain.
- All ten courses in SSX 3's 17 event slots is therefore a data-size fit; the
  open work is content conversion (docs/peaks-and-locations.md).
