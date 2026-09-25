# Shared boot driver + cached det baselines (RS2)

Boot every run with `ssx3_boot.py` (promoted from F5's driver; adds
only `--out DIR`). Never copy the driver into a lane dir again.

One control run per fork tip lives in
`~/dev/ssx3-work/baselines/<key>/` (runner + receipts + frames).
Key = readable pins prefix + 8 hex of the canonical pins JSON.

A brief names its control pins file; the worker runs:

    base=$(python3 local/tooling/boot/baseline.py get --pins PINS)
    # MISSING <key> (rc=2)? create it once, then boot only the candidate:
    python3 local/tooling/boot/baseline.py make --pins PINS --runner R
    python3 local/tooling/boot/ssx3_boot.py --mode det ... --out CANDIR
    python3 local/tooling/boot/baseline.py compare --key KEY --cand CANDIR

Subcommands: `put` (store a run), `get` (print dir; verifies SHAs,
two reads for the runner), `list`, `compare` (gb8 hashdiff +
snd/coverage guest fields; host underrun counters ignored), `make`
(boot the control if absent, then put; det only, one mini slot).

Pins: fork, codegen x2, vu1_images (sha256 of sorted vu1gen .sha
lines), parallel_gs (+granite), build, route, stop_tick, sound,
backend, ssaa/hires/pipeline, iso/elf SHAs; optional dump_ticks,
hash_every, coverage_tick, vu1_stats. Example:
`local/research/RS2/pins-a3efbfe-det.json`.
