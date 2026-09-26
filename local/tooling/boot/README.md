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

## Save states (SS1): boot from race start instead of power-on

Stored states (scratch only; they hold game RAM): `baseline.py list-states`.
Seeds: FR1-R1 det 1x at t1720 (race HUD) and t2000, guest = fork a3efbfe,
pins `local/research/SS1/pins-state-a3efbfe-fr1r1-1x.json`.

    st=$(python3 local/tooling/boot/baseline.py get-state --pins PINS --tick 1720)
    python3 local/tooling/boot/ssx3_boot.py --mode det ... --load "$st" --out CANDIR
    # det-hash lines start at 1721; compare with --from 1721 (ss1_hashdiff.py)

The candidate runner must include fork `ss1-savestate` (or its fold) and
match every section version; a different runner SHA only warns
(`--strict` refuses). Refused loads name the reason (`[savestate] load
refused: …`) and exit at once. Make a state: `--save-at T --save-path F
--exit-after-save`, then `baseline.py put-state --state F --pins P --tick T`.
The route may differ after the save tick, not before it.
