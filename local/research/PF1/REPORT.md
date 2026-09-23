# PF1 report — clean performance baseline (Odin); first native race attempt

Brief `local/muse/prompts/PF1.md` + Mini-resume scope change (launch 6 = Happiness
race, 900 s cap; Mac Mission 2 removed to a post-E32 brief). Tables + receipts;
the orchestrator decides.

## Headline

- **Clean-build speed on the Odin: title ~21.5 guest vsyncs/s (35.9% of 59.94),
  menus 1–25/s, My Rules ~25/s.** GameThread saturated (~93–99%) in all runs.
- **Launch 6 (first Odin native race attempt): NO race.** The Mac-timed e31l
  script desyncs on slower Odin menus: all 13 inputs delivered, chain advanced
  title → … → Select Event (Happiness selected) → My Rules, where the script
  ended one cross short of loading. No race HUD, no timer. Ends at My Rules.
- **Focus incident:** a system "Use USB for" dialog covered the app t+0–~330.
  Presents were suppressed (1 dump line) while the guest advanced silently
  (tick 0→6116). One BACK dismissed it; ticks resumed in logcat. No void:
  the guest never paused (pad clock + ticks prove it).

## Pins

| Item | Value |
|---|---|
| APK (N3 release, aggressive logs OFF) | `69a79e29a0955b31c50771367ca0847f706e36cfacc71b7cab8b4814ab16e466` — SSD ×2 + internal copy all agree |
| Launch-6 env on device | `936bec468c4d9b65c2b8ee06bf402e9202dc2f9c5b508d1f150fa3eb40212119` == local copy |
| e31l script reconstruction | entry-for-entry exact: device `[padscript]` press at/hold/buttons match all 13 log lines (see table) |
| ISO on device | `SSX3.iso` 3005415424 B (staged by N3/PF1; not re-pushed) |
| No-race pin | final `r6-25.png` = My Rules @t+900 (SSD mirror); no race-HUD frame exists |

## Launch table (all PF1 launches)

| Launch | Env / script | Wall | Result |
|---|---|---|---|
| 1 | clean (CD+SKIP only) | ~310 s | VALID title baseline: presents ~60/s, guest 21.54/s (35.9%), GameThread 99.3% |
| 2 | clean | ~310 s | VALID, same: presents 60.4/s, same thread shape |
| 3 | e31h Snow Jam path | — | VOID (backgrounded ~15:13) |
| 4 | e31h Snow Jam path | — | VOID (lockscreen `showing=true` paused app) |
| 5 | e31h Snow Jam path | ~175 s | main menu by t+30, killed by orchestrator pause; app force-stopped |
| 6 | e31l Happiness path (reconstructed) | 908 s | chain reaches My Rules; script exhausted; NO race |

## Launch 6 reconstruction receipt (e31l from `boot-e31l-1.log` press lines)

Masks verified vs `Pad.cpp`: start=1<<3=0x0008, down=1<<6=0x0040, cross=1<<14=0x4000.
Device log confirms each entry's at/hold/buttons (i=9 cross@470, i=10 down@470+120s,
i=11 cross@505, i=12 cross@540 — exact match to the pushed string, `armed n=13`).

`25000:start:5000,50000:cross:5000,75000:cross:5000,100000:cross:5000,`
`125000:cross:5000,150000:cross:5000,172000:down:12000,195000:cross:5000,`
`220000:cross:5000,470000:cross:5000,470000:down:120000,505000:cross:5000,`
`540000:cross:5000` (+ `FRAME_DUMP_DIR`, full env in `scripts/ps2x-launch6.env`)

## Launch 6 timeline (t0=00:49:05Z, pid 22528)

| Wall | Observable |
|---|---|
| t+0–~330 | USB dialog covers app; 1 dump line (seq=0 tick=0); padscript i=0..~7 fire on schedule; guest ticks silently to 6116 |
| ~t+330 | BACK dismisses dialog (`showing=false` throughout after) |
| t+352 | first game screencap (r6-10) |
| t+360 | Select Event, Snow Jam highlighted (r6-dlg) |
| t+490 | Select Event, **Happiness highlighted** (r6-13; "A battle against your rival", Rival badge) |
| t+505/540 | i=11/i=12 cross (confirm Happiness → My Rules) |
| t+545/590 | script exhausted (i=12, down-tuck releases) |
| t+730, t+900 | My Rules, static (r6-20, r6-25). Force-stop, lease released, `/data/local/tmp/pf1` removed |

Desync vs Mac e31l: Mac reached My Rules ~233 s, loading ~255 s, race HUD ~570 s.
Odin reached Select Event ~360 s, My Rules ~600+ s — **~280 s slower through menus**,
so the 540 s final cross landed on event-confirm instead of pre-race Continue.

## Speed table (guest vsyncs/s from tick-gated `[frame:dump]`; % = ÷59.94)

| Phase | Odin (launch 6 / runs 1-2) | Mac E31 (ref) |
|---|---|---|
| Title | 21.54/s, 35.9% (runs 1-2; launch 6 title unseen behind dialog) | ~23/s |
| 3D menus (mixed) | ~1/s (t+300–359, screen unseen) … 20.9–23.2/s (Select Event) | 1–3/s |
| My Rules | 24.9–25.6/s sustained (t+540–900) = **~42.6%** | — |
| Loading | not reached | 8–17/s |
| In-race | not reached | (e31l timer advanced) |
| Presents (SF --latency, correct layer) | 27.6/s menu phase (635 unique/23 s) vs ~60/s title (runs 1-2) | — |

Per-minute tick bins: `logs/run6-tickbins.txt`. Full 44,431-line log + 27 screencaps:
SSD `/Volumes/Extreme SSD/pf1/pf1-run6/`; log + padscript lines mirrored to share
`/Volumes/share/ssx3/pf1-run6/`.

## Thread + thermal + battery (launch 6)

| Item | Value |
|---|---|
| GameThread | R 100% inst both snapshots; TIME+ 13:11/855 s = **~92.5%** (mid: 7:08/430 s) |
| main | 50% inst mid (TIME+ 0:37 ≈ 8.6%); end snapshot missed main line |
| Shape | same as runs 1-2 (GameThread ~saturated, app ~1.1 cores) |
| CPU-ms/guest frame | ~36 ms (My Rules 25.5/s); title runs 1-2 ~46 ms |
| Thermal max zone | 103.9 °C sustained pre→end (runs 1-2 band 80–104 °C) |
| Battery | 95→93→92% while AC-charging (status=3): **charger can't keep up** |
| Crash buffer | 0 FATAL/tombstone; filtered log 0 fatal/exception; no unimplemented-stub lines |

## Profiling status (unchanged from checkpoint)

simpleperf BLOCKED device-wide (`perf_event_open: Permission denied`, user build,
non-profileable APK, no root). Perfetto traced_perf accepted config, 0 samples.
No Odin symbols without an N-lane profileable/debuggable build. Component rollup
(guest vs VU1 vs GS rasterizer vs present) is **not measurable on device** —
recommendation below is from thread-level data only.

## Recommendation (orchestrator decides)

1. **Race attempt needs an Odin-paced script, not the Mac-timed e31l.** Odin menus
   lag Mac by ~280 s; a script with crosses at ~750/800/850 s (one per settled
   screen, verified by screencap before each) reaches loading from My Rules.
   That is a new brief (tuning loop prohibited here).
2. **Dismiss the USB dialog before every launch** (BACK after `am start`, verify
   by screencap byte-size change): unfocused presents are silently suppressed
   while the guest runs — future tick curves would otherwise misread.
3. **Threading:** GameThread saturation at 36–46 ms/guest-frame vs 16.7 ms budget
   (1×) / 8.3 ms (2× sim) says the main thread must shed roughly half (1×) to
   three-quarters (2×) of its per-vsync work. Candidates in order: GS CPU
   rasterizer, VU1 interpreter, present/upload — but the split needs symbols
   (profileable build) or Mac-side sampling; device data can't rank them.
4. **Diagnostics cost:** unmeasured on device. N3 build already compiles out
   aggressive logs; frame-dump sidecars cost one present-thread write per vsync
   (PNG export fails on Android, txt succeeds). No number to quote.
5. **Battery:** 3% net drain over 15 min while "charging" — long Odin sessions
   need a higher-wattage charger or shorter runs.

## Gaps

- Title-phase screencaps for launch 6 don't exist (dialog); title rate rests on
  runs 1-2. Loading/in-race rates on Odin unmeasured (never reached).
- Slowest menu (~1/s @t+300–359) screen unidentified (no screencap).
- Presents 27.6/s (menus) vs 60/s (title): mechanism unnamed (present thread
  possibly gated on guest pace); needs a paired tick+latency run to explain.
- simpleperf/Perfetto blocked (see above); no per-component rollup.

## Receipts

- Repo text: `logs/run6-{tickbins,padscript,logcat-head,top-thermal,lat}.txt`,
  `scripts/ps2x-launch6.env`. Brief rule = text only in repo (no PNGs).
- SSD `/Volumes/Extreme SSD/pf1/pf1-run6/`: logcat6.txt (44,431 lines),
  27 screencaps, 5 latency polls, env + derived tables.
- Share `/Volumes/share/ssx3/pf1-run6/`: logcat6.txt + padscript lines.
- Leases: Odin claimed 00:58Z label (actual ~00:49Z), released after force-stop;
  `/data/local/tmp/pf1` removed. P-lane lease never held. No source edits, no
  push. Prior checkpoint items (runs 1-5) verified from CHECKPOINT.md + logs.
