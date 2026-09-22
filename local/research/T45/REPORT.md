# T45 report — R2 re-drive as VARIANT-NULLSINK (crash-confounded hold; healthy series untouched)

Brief: T45 (re-drive T44-R2 on the next audio-healthy VM with the
CORRECTED baselines, T44 §T44-4 recipe carried; T44 gated PASS-stall,
committed). Audio gate ran FIRST: 2 demand-boots (H59, H60) + one
~7-min stopped wait, all DOWN (8th consecutive down boot H53–H60,
~2h40m outage, post-host-reboot) → orchestrator-authorized NULL-SINK
VARIANT executed instead (brief step 1). Tables, no verdicts.

Variant contract (from the brief): every output labeled
`VARIANT-NULLSINK`; PARALLEL variant distributions started (variant
runs NEVER appended to the healthy ROI/gradient/hold series); STOP
after ONE live variant run; the healthy-series re-drive stays queued
for recovery; host-side recovery never attempted.

CORRECTED baselines carried (T44-E1 erratum; T42 §T42-6 + T43 §T43-5,
gate-verified; T45 re-verified each value against the REPORTs —
§T45-0; the ONLY baseline; append-only; no re-tune):

- ROI no-input floor n=3: T42 npre1npre2 −0.7/−22.2; T43 d5d6
  +2.8/−12.7, d9d10 −4.5/−7.0
- Gradient no-input floor n=7: T42 +1.8/+4.8, +0.0/+10.6, +2.7/−3.9,
  −2.1/−4.2; T43 d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7
- Hold-step ROI n=1 crash-confounded: T42 +11.2/−39.5 (crash inside);
  T43 0 (hold ungated)
- Hold-step gradient n=1 crash-confounded: T42 −4.4/−24.1 (crash
  inside); T43 0 (hold ungated)
- d7-class intruder: lock-QA-gated, never auto-counted (T42
  rider-mixed, T43 off-rider under both)

Experiment contract (up front): hypothesis — under the null-sink
variant, cubeb negotiates against a local null sink (no audio modal),
the T44-shape run reaches live, and post-hoc scoring banks quarantined
variant pairs; observable — socket receipts, daemon/sink receipts,
cubeb trace lines, modal census, run chain, hold row, blind 10-snap
series + per-snap HUD + all-three-tracker scoring + lock-QA per VALID
pair; alternatives — a modal appears despite the sink (→ abort the
run, variant failed, report + STOP), the hold crashes (→ full 3-row
crash receipts, report + STOP — no R3 under the variant cap), the run
never reaches live (→ environment NO-PARK per T27 §4); stop — ONE
live variant run scored + REPORT, or variant failure.

## T45-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + box package only) |
| `adb` | Not used |
| Installs | pulseaudio 1:16.1+dfsg1-2ubuntu10.1 via apt as root (VARIANT box change, receipted §T45-2; no other installs) |
| Copyrighted downloads | None (inputs already staged) |
| ssx3 HEAD at commit | Below (`[T45]`, trailer `Orchestrated-By: Muse Code`, NO push per lane instruction) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; disk
pins taken on VM-H60, VM-independent across turnover):

| Item | T4 value | T45 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (Left) | `Left = Keyboard/Left` | `PCSX2.ini:576` (the hold key; re-verified) | yes |
| 9 refs present | shas reproduce T27–T35 | b964856a/8f34385f/dd7e4716/212b0970/1a8b1ed9/e724021c/4baec4bc/069b1113/192e0472 (first-8) | yes |
| T43 reference snaps present | — | on-box `t43-npre1.jpg` 59433 B = committed size (61 `t43-*.jpg` intact; 116 `t42-*.jpg` intact, `t42-npre1.jpg` 53597 B) | yes |
| Free space | — | WSL `/` 901 G avail pre; C: 281 G pre (was 23 G at T44 — user cleanup/compact; GATE ~5 GB+ PASSES) | yes |
| Live trace pre-run | — | `emulog.txt` 1218493615 B = T44 R1's partial (mtime Sep 21 18:01; rotated at R2 boot, §T45-3) | yes |
| Staged scripts | T44 shas | all 5 WSL-staged shas match local (auto `a3acb2d6…`, analyze `bf966f02…`, vcount `105cd092…`, cropdiff `ac114212…`, dialogwatch2 `d9c7a4c1…`) → REUSED, zero `t45-*` script copies (no edits needed) | yes |
| WSLg audio pre-run | — | socket ABSENT H59+H60 (immediate + delayed; §T45-2) → variant path; behavioral gate at boot (modal census, §T45-3) | gate |

Baseline re-verification (T45 vs T42 §T42-6 + T43 §T43-5 — every
corrected value re-read from the REPORTs this session):

| Distribution | T45 brief line | REPORT text | Match |
|---|---|---|---|
| ROI floor T42 | npre1npre2 −0.7/−22.2 | T42 §T42-6 deltas row + T43 §T43-5 `npre1npre2 −0.7/−22.2` | yes |
| ROI floor T43 | d5d6 +2.8/−12.7, d9d10 −4.5/−7.0 | T43 §T43-5 `d5d6 +2.8/−12.7, d9d10 −4.5/−7.0` | yes |
| Gradient floor T42 | +1.8/+4.8, +0.0/+10.6, +2.7/−3.9, −2.1/−4.2 | T43 §T43-1b calib + §T43-5 `npre1npre2 +1.8/+4.8, d5d6 +0.0/+10.6, d6d7 +2.7/−3.9, d7d8 −2.1/−4.2` | yes |
| Gradient floor T43 | d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7 | T43 §T43-5 `d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7` | yes |
| Hold ROI / gradient | T42 +11.2/−39.5 / −4.4/−24.1 crash inside; T43 0 | T42 §T42-6 hold row + T43 §T43-5 `0 (hold ungated)` ×2 | yes |

Phase-match targets (tabled BEFORE the run — T42 R3's hold window via
T43 R1's; match PHASE not seed):

| Item | Hold-window value (T42 R3 / T43 R1) | T45 hold-window target |
|---|---|---|
| Hold slot | T+502.49 / T+509.34 (keydown) | ≈T+502.5–509.5 (same script slot) |
| Pre-pair race clocks | 00:01:27-ish / 00:01:27 / 00:01:27 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | back-of-pack / front-of-pack | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36–37% / 43–44% | ≈36–44% ±5 pp |
| Series span | 10 snaps over +7.37–7.40 s wall / +10–11 s race | 10 snaps over ≈+7.4 s wall (same `sleep 0.5` blind capture) |

Same-shape record (tabled BEFORE the run — the deliberate NON-change;
variant changes ONLY the audio sink + its env pointer):

| Item | T43 R1 (`sleep 0.5`) | T45 (this run) |
|---|---|---|
| Dense-phase shape | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls | identical (staged `t44-auto.sh` reused byte-identical, sha-verified) |
| Pre-pair gap | `sleep 0.5`, no scoring | identical call |
| Hold | ONE `press_hold Left` (1 s `sleep`, T38's body) | identical call, same slot (wall width 1682.9 ms observed — VM scheduling lag, §T45-3) |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) | identical calls |
| Audio sink | WSLg PulseServer socket | local pulseaudio null sink via `PULSE_SERVER` env (variant deviation, §T45-2) |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log + census + samples + boot logs | scp via C: staging (T25 recipe) | `t45r2-variant-*.jpg`, `t45r2-variant-poll.log/census/samples/boot` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t44-cropdiff.py`, bit-exact validated 4/4 (T39–T43 protocol); committed tool reproduces any score | screen chain table + xrun frame identities |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking, CONTROL | committed `t41-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. Dense 12-snap tracking, ROI | committed `t42-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 6. Dense 12-snap tracking, GRADIENT | committed `t44-track.py` (§T44-1a variant) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 7. View snaps | local reads | HUD per dense snap (clock/position/progress/speed/score) + chain anchors |
| 8. Lock-QA every VALID pair | marked-crop montage method (T42) | on/borderline/off + named intruder per snap; variant on→on sets |
| 9. Distribution tables | — | PARALLEL variant distributions (quarantined; healthy series untouched) |

## T45-1. Session log (H59 → H60 → H61)

Clocks: WSL `date -u` true UTC; `wevtutil` renders local-as-Z (+4 h →
UTC); H-numbers continue T44's H58. WSL fully Stopped at session start.

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 00:45:44 (up 1.75) | H59 demand-boot (btime 1790037943) | boot clocks |
| 2 | 00:45:48 (up 5.71) | H59 audio IMMEDIATE: DOWN (no PulseServer, no `runtime-dir/pulse/`, no user pulse dir) | socket checks |
| 3 | 00:46:24 (up 41.35) | H59 audio DELAYED: DOWN (full T41 signature: no PulseServer, no `runtime-dir/pulse/`, no pulseaudio.log; `/mnt/wslg/` = distro/doc/run/runtime-dir/stderr.log/versions.txt/weston.log/wlog.log) | socket checks |
| 4 | ~00:47 | H59 dmesg (466 lines, 1 AcceptAsync [20.74] p9io-cancel) + WSLg ps (weston/Xwayland/pulseaudio all absent from user distro — system-distro procs not visible there) | `t45-dmesg-h59-audiodown.txt` |
| 5 | 00:47 | `wsl --shutdown` BY ME (clean, rc=0); WSL fully Stopped | `wsl -l -v` |
| 6 | 00:47–00:54 | Stopped wait ~7 min + local work (T44 script shas 6/6 reproduce; frozen tracker shas 3/3 reproduce; corrected-baseline re-verification §T45-0; script survey) | this file |
| 7 | 00:54:43 (up 1.93) | H60 demand-boot (btime 1790038481) | boot clocks |
| 8 | 00:54:43 / 00:55:23 (up 41.40) | H60 audio immediate + delayed: DOWN (full T41 signature) — 8th consecutive down boot H53–H60 | socket checks |
| 9 | 00:55–00:59 | NULL-SINK VARIANT setup (§T45-2): apt update OK → pulseaudio 16.1 installed → daemon started → auto_null sink receipted | install + daemon + pactl outputs |
| 10 | 00:58–00:59 | Pins (§T45-0 table) + eventlog-pre (59474 B) + H60 dmesg-pre (481 lines, 2 AcceptAsync [16.96, 56.95]) | `t45-eventlog-pre.txt`, `t45-dmesg-h60-pre.txt` |
| 11 | ~00:59 | R1's on-box boot logs fetched FIRST (4231/210 B, shas `5c0edb0b…`/`360108bc…` — T44 gap CLOSED); C: cleaned | `t45r1-boot.log/.stdout` |
| 12 | ~00:59 | X11 tmpfs mount (root, rw 10240k) + PPM 0.0000/0 | mount + cropdiff outputs |
| 13 | 00:59:18–01:08:06 | R2-VARIANT-NULLSINK: background launch (T_BOOT 1790038764) → v2a @T+59 → census @T+109 → live → dense → `T44_DONE`, exit 0 (§T45-3) | stdout 426 lines, stderr 2551 lines |
| 14 | ~01:10:04 | H60→H61 turnover (NOT by me — idle reaper ~2 min after DONE) → H61 (btime 1790039403; second read …404 = 1 s quantization, same boot by uptime math); H60 post-run dmesg MISSED (T44-H52-class gap) | btime/uptime; `t45-dmesg-h61-boot.txt` (440 lines, 0 AcceptAsync) |
| 15 | 01:10–01:13 | Analyze overlap across turnover (H60 run killed mid-census + H61 re-run 01:11:25→01:12:48 clean, 56-line log); census 11700 B + samples 5876 B verified by content | `t45r2-variant-analyze.txt/census/samples` |
| 16 | 01:10:55 | H61 PulseServer PRESENT (socket; informational ONLY — T42 lesson; behavioral health unprobed, no authority spent) | `ls -la` + delayed recheck 01:12:22 |
| 17 | 01:13–01:15 | Post-run receipts (NVM FULL sha unchanged, C: 281 G, vcount 397 all ≤90, cubeb full-run 8/0/0) + 66-file fetch → renamed `t45r2-variant-*` + C: cleaned (962 pre-existing remain) | files below; §T45-3/5 |
| 18 | 01:15–01:21 | Refs fetch (9 × 3932177 B, shas reproduce; /tmp use, NOT committed) + batch scorer (bit-exact 4/4) + 3 trackers + 15 snap views + montage + share stream (2679800948 B + sha MATCH) + eventlog-final + H61-final dmesg | `/tmp/t45-batch.py`, `/tmp/t45-montage.py`, share `emulog-t45r2-variant.txt` |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| Package install | pulseaudio 1:16.1+dfsg1-2ubuntu10.1 + deps via `wsl -u root apt-get` (VARIANT deviation; persists on distro disk) |
| Pulse daemon | user daemon (brad) on H60, socket `/run/user/1000/pulse/native`, sink auto_null; dead with H60 (nothing to clean) |
| `/tmp/.X11-unix` | tmpfs `mode=1777` (as root, T4 recipe) on H60 pre-run; does not persist reboot |
| Xvfb | `:99 -screen 0 1280x1024x24`, started by the script itself (`setsid nohup`, log `/tmp/xvfb-t44.log`); dead with H60 |
| Dirs/files created | `…/logs/emulog-pre-t44-20260922T005924Z.txt` (R1's 1218493615 B partial, rotated at R2 boot), `t44-*.jpg/.ppm/.log/.txt` (R2-variant set: 61 JPGs + poll + census + samples), `C:\Users\bradr\pcsx2-t4\t44*/boot-t44*/t*-ref-*` staging (removed after each batch) |
| Dirs/files OVERWRITTEN | `t44-*.jpg` (R1's 17 abort names ⊂ R2's 61, overwritten by the run), `t44-poll.log`, `logs/boot-t44.log`/`.stdout` (R1's content fetched FIRST, §T45-3), `t44-census.txt`, `t44-samples.txt` |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20), T42/T43 rotations, `emulog-pre-t44-20260921T215827Z.txt` (T43R1's trace) |
| Restarts by me | 1× `wsl --shutdown` (clean rc=0, pre-wait; tabled, justified — T42 precedent) |
| VM restarts (not by me) | H60→H61 turnover (idle gap ~01:10) |

## T45-2. Outage extension + VARIANT-NULLSINK setup (receipt every step)

Outage table (T44's H53–H58 carried; H59–H60 this session; H61 informational):

| VM | btime | Socket checks | dmesg | Note |
|---|---|---|---|---|
| H53–H58 | (T44) | absent ×6 | 6 files | T44 outage, ~36 min |
| H59 | 1790037943 | absent (immediate up 5.71 + delayed up 41.35; full T41 signature) | 466 lines, 1 AcceptAsync | post-Stopped demand-boot |
| H60 | 1790038481 | absent (immediate + delayed up 41.40; full T41 signature) | 481 lines, 2 AcceptAsync | post-7-min-stopped demand-boot |
| H61 | 1790039403 | PRESENT (socket `srwxrwxrwx`, @up 51 + recheck up 137) | boot 440/0, final 449/1 | post-turnover; INFORMATIONAL only |

Variant setup receipts (H60, in order):

| # | Step | Command (one `wsl` call per ssh) | Result |
|---|---|---|---|
| 1 | Recon | `which pulseaudio; pulseaudio --version; which pactl; which paplay; echo PULSE_SERVER=$PULSE_SERVER` | pulseaudio/pactl/paplay ALL ABSENT; `PULSE_SERVER=unix:/mnt/wslg/PulseServer` (points at the absent socket — the cubeb failure) |
| 2 | Privilege recon | `sudo -n id; dpkg -l pulseaudio; ls apt sources` | sudo needs a password (no passwordless); pulseaudio `un` (not installed); noble sources present; Ubuntu 24.04.1; DNS resolves archive.ubuntu.com |
| 3 | apt update | `wsl -u root apt-get update` | EXIT=0 (noble + updates + backports + security fetched) |
| 4 | Install | `wsl -u root apt-get install -y pulseaudio` | EXIT=0; `pulseaudio (1:16.1+dfsg1-2ubuntu10.1)` + deps (gstreamer/libav/jack/vdpau/glib-networking/asound-plugins/soup/snapd-glib) |
| 5 | Daemon start | `unset PULSE_SERVER; pulseaudio --start --exit-idle-time=-1` | `DAEMON_RC=0`, `pulseaudio 16.1` |
| 6 | Sink proof | `pactl info; pactl list sinks short` (PULSE_SERVER unset) | Server `/run/user/1000/pulse/native`, Default Sink `auto_null`, `0 auto_null module-null-sink.c s16le 2ch 44100Hz IDLE` — the null sink, auto-loaded (no hardware), zero extra config |
| 7 | Launch env | `export PULSE_SERVER=unix:/run/user/1000/pulse/native; cd … && stdbuf -oL -eL ./t44-auto.sh` | ONE env var; ZERO script edits (staged `t44-*` reused byte-identical) |
| 8 | cubeb proof (live trace) | `grep -a -i cubeb emulog.txt` (+ `pactl list sink-inputs/clients`) | 5 init/negotiation lines [0.6574–0.6612] + `pcsx2-qt` client with sink-input `float32le 2ch 48000Hz` on the null sink; full-run 8/0/0 in §T45-3 |
| 9 | Modal gate | v2a + window census | R3-pattern (no modal) + game-only census (details §T45-3) |

## T45-3. R2-VARIANT-NULLSINK — full live run, tree crash in hold hop (crash-confounded)

R2-variant booted on VM-H60 (T_BOOT 1790038764, uptime 279;
00:59:18 UTC) under the null sink (cubeb-pulse negotiated
[0.6574/0.6604/0.6610/0.6612], zero null-fallback/CUBEB_ERROR lines
in the full 2.68 GB trace, clean stop/destroy at shutdown
[500.91/500.95]; TRUE TITLE viewed on a1-poll01 with no modal; v2a
R3-pattern + game-only census) and ran the full chain through the
pre-race panel into the live race, where the hold hop caught a tree
(npre2 22 MPH → d-post1 2 MPH, rider pressed to trunk). `T44_DONE`,
exit 0, clean shutdown at uptime ~790 (T+522). 426-line stdout /
2551-line stderr. WID 2097159 (same as T31–T44). Poll log 168 lines
(T44 plan's `poll 168` exact).

| Item | Value |
|---|---|
| R2-variant window | 00:59:18–01:08:06 UTC (T+0–522), VM-H60 uptime 279→~790 |
| Dialogwatch v2 | ROUND:1 @T+59.3: SKIP-ROOT 511 + SKIP-GAME 2097159 (`SSX 3 [Devel]` 640x480) + DISMISS 2097162 `pcsx2-qt` 640x480 + DISMISSED-EXIT (main-window, inert — R3 pattern; NO modal existed to dismiss; window census @T+109: game-only, no `Error`) → no v2b |
| Title detect | A1 `poll01` remote 0.4331/6 (PIL post-hoc 0.0465/1) — parked FIRST attempt (a2/a3 never ran); TRUE TITLE viewed |
| ZC park | `zc-post1` vs-zc 0.2878/7 PARKED at +1 s (viewed: Zoe + Continue/Equip Gear/Rider Details/Music) — R1's slow-load refusal (p1-p3 1.7110) absent here (p1-p3 0.3299) |
| cubeb full-run | 8 lines: create [0.6574] + negotiate [0.6604/0.6610] + init/start [0.6610/0.6612] + stop ×2 [500.91/500.95] + destroy [500.95]; null-fallback 0, CUBEB_ERROR 0; `pcsx2-qt` sink-input `float32le 2ch 48000Hz` on auto_null |
| Presses | 10 menu/Start/X Cross (all 533.3–535.6 ms) + ONE Left hold 1682.9 ms; ZERO other game inputs (22 KEYDOWN/KEYUP lines in the 168-line poll log) |

### R2-variant press log (poll-log walls; T+ = wall − 1790038764)

| Press | Keydown wall (T+) | Keyup wall (T+) | Width |
|---|---|---|---|
| A1 Cross (attract-skip) | 1790038864.771 (T+100.77) | 1790038865.306 (T+101.31) | 535.3 ms |
| A1 Start (on title) | 1790038868.020 (T+104.02) | 1790038868.554 (T+104.55) | 534.7 ms |
| MENU Cross (Single Event) | 1790038908.464 (T+144.46) | 1790038909.998 (T+145.00) | 533.7 ms |
| ZOE Cross | 1790038948.387 (T+184.39) | 1790038948.922 (T+184.92) | 534.7 ms |
| CONT Cross | 1790038977.344 (T+213.34) | 1790038977.879 (T+213.88) | 535.0 ms |
| PEAK Cross | 1790039005.660 (T+241.66) | 1790039006.193 (T+242.19) | 533.4 ms |
| RACE Cross | 1790039035.142 (T+271.14) | 1790039035.676 (T+271.68) | 534.9 ms |
| SNOWJAM Cross | 1790039066.464 (T+302.46) | 1790039066.999 (T+303.00) | 535.0 ms |
| ENTER Cross | 1790039095.388 (T+331.39) | 1790039095.922 (T+331.92) | 533.3 ms |
| XCROSS (race start) | 1790039200.896 (T+436.90) | 1790039201.432 (T+437.43) | 535.6 ms |
| HOLD Left | 1790039268.953 (T+504.95) | 1790039270.636 (T+506.64) | 1682.9 ms |

Hold-width note (tabled, no verdict): the slot matches the contract
(keydown T+504.95 vs target T+502.5–509.5; T42 R3 T+502.49, T43 R1
T+509.34) but the wall width is 1682.9 ms vs the ≈1037 ms class
(T41 R4 1038.4, T42 R3 1036.5, T40 R2 1038.0). Same `press_hold`
call (`sleep 1` + xdotool round-trips): HELD→KEYUP alone spans
1663.9 ms, so the `sleep 1` ran ~1.66 s under loaded-VM scheduling
(trace streaming + game + new daemon). Series span absorbs it:
npre1→d-post10 +7.99 s wall (target ≈+7.4 s; +0.65 s ≈ the excess
hold width).

### R2-variant chain panel (post-hoc PIL; titleband vs title-ref, whole vs each ref, setag vs se-ref)

| Snap | titleband | Best whole ref (mean/p99) | Identity |
|---|---|---|---|
| start | 14.35/142 | mr 14.16/124 | attract |
| a1-now | 16.66/122 | mr 13.70/137 | attract |
| a1-poll01 | 0.0465/1 | title 0.0351/0 | TRUE TITLE (viewed) |
| a1-pre | 0.0465/1 | title 0.0351/0 | = poll01 (cp-identical size 58339) |
| a1-post3/8/15/25 | 16.26–16.30/138–139 | menu 0.03–0.08/0–1 | Main Menu |
| menupre | 16.26/138 | menu 0.0279/0 | Main Menu |
| mc-post1/3/8/15 | 12.46–12.49/163 | sc 0.08–0.19/1–3 | Select Character |
| scpre | 12.48/163 | sc 0.1861/4 | Select Character |
| zc-post1/3/8 | 15.82–15.86/128–129 | zc 0.19–0.29/4–7 | Setup Character PARKED (zc-post1 viewed: Zoe present at +1 s) |
| ccpre | 15.83/128 | zc 0.2471/7 | Setup Character |
| sp-post1/3/8 | 23.12/171 | sp 0.008–0.04/0 | Select Peak |
| sppre | 23.13/171 | sp 0.0093/0 | Select Peak |
| pc-post1/3/8 | 26.30/183 | sm 0.04–0.06/0 | Select Mode |
| smpre | 26.30/183 | sm 0.0515/0 | Select Mode |
| rc-post1/3/8 | 26.20–26.21/183 | se 0.03–0.07/0–1, setag 0.009–0.06/0–2 | Select Event |
| sepre | 26.21/183 | se 0.0668/1, setag 0.0530/2 | Select Event |
| sj-post1/3/8 | 9.81–9.87/135–136 | mr 0.09–0.16/1–2 | My Rules |
| mrpre | 9.86/136 | mr 0.1456/2 | My Rules |
| mr-post1/3 | 17.23/167, 18.01/171 | title 11.59/127, 11.67/128 | transition (mid-fade, no ref) |
| mr-post8 | 26.92/237 | panel 19.26/190 | panel arriving |
| mr-post15/25/40, stab1/2, pppre | 34.52–34.53/184 | panel 0.41–0.68/7–15 | pre-race panel |
| x-post1/3/8/15/25/40 | 11.85–26.23 | none ≤10.76 (gameplay, no ref) | live race (x-post1 viewed: start gate, countdown 2, 00:00:00, 0 MPH) |
| npre1/2, d-post1–10 | (dense §below) | none (gameplay, no ref) | live race Snow Jam |

### R2-variant transition hops (whole-frame, post-hoc PIL)

chain: start→a1-now 14.19, a1-now→a1-poll01 14.61, poll01→a1-pre
0.0000, a1-pre→a1-post3 14.13, post3→8 0.10, 8→15 0.04, 15→25
0.02, post25→menupre 0.02, menupre→mc-post1 10.12, mc1→3 0.14,
3→8 0.18, 8→15 0.16, 15→scpre 0.16, scpre→zc-post1 7.21,
zc1→3 0.33, 3→8 0.16, 8→ccpre 0.23, ccpre→sp-post1 9.43,
sp1→3 0.04, 3→8 0.03, 8→sppre 0.04, sppre→pc-post1 5.18,
pc1→3 0.02, 3→8 0.05, 8→smpre 0.04, smpre→rc-post1 0.53
(T32-G1 small SM→SE hop class), rc1→3 0.05, 3→8 0.02, 8→sepre
0.04, sepre→sj-post1 10.63, sj1→3 0.16, 3→8 0.09, 8→mrpre 0.09,
mrpre→mr-post1 12.46, mr1→3 2.06, 3→8 25.96, 8→15 19.24,
15→25 0.35, 25→40 0.33, 40→stab1 0.05, stab1→2 0.11, 2→pppre
0.16, pppre→x-post1 14.68, x1→3 13.17, 3→8 14.51, 8→15 9.56,
15→25 11.54, 25→40 11.00, x40→npre1 11.50.
dense: npre1→npre2 8.25, HOLD npre2→d-post1 15.08 (crash hop,
largest), d1→d2 8.12, d2→d3 7.68, d3→d4 6.78, d4→d5 7.22,
d5→d6 13.47, d6→d7 10.20, d7→d8 12.88, d8→d9 7.87, d9→d10
7.40. Dense range 6.78–15.08 (T42 R3: 5.07–18.39 — same motion
class).

### R2-variant dense HUD (all 12 viewed; score 230 const)

| Snap | Clock | Pos | Prog | MPH | Note |
|---|---|---|---|---|---|
| npre1 | 00:01:29 | 2ND/6 | 44% | 18 | rider mid-frame in spray, trunks left + log right |
| npre2 | 00:01:29 | 2ND/6 | 44% | 22 | rider center-left by red-banded tree; NO banner, speeds rising |
| d-post1 | 00:01:32 | 2ND/6 | 45% | 2 | TREE CRASH: rider pressed sideways to trunk, 22→2 MPH |
| d-post2 | 00:01:33 | 2ND/6 | 45% | 20 | rider upright center, recovering |
| d-post3 | 00:01:34 | 2ND/6 | 45% | 35 | clean cruise, red rock left edge |
| d-post4 | 00:01:35 | 2ND/6 | 46% | 43 | rider center-left, dark red rock fills left ~1/4 |
| d-post5 | 00:01:35 | 2ND/6 | 46% | 43 | clean cruise, trees both sides |
| d-post6 | 00:01:36 | 2ND/6 | 47% | 43 | clean cruise, chevron sign background |
| d-post7 | 00:01:37 | 2ND/6 | 47% | 43 | clean cruise, blue-glow track right |
| d-post8 | 00:01:38 | 2ND/6 | 47% | 48 | rider center-left, red rock top-left intruder |
| d-post9 | 00:01:39 | 2ND/6 | 48% | 45 | clean cruise, tree center-background |
| d-post10 | 00:01:40 | 2ND/6 | 48% | 48 | clean cruise, chevron arch top |

Phase-match read: pre-pair 00:01:29 (target ≈00:01:2x–3x) /
2ND racing pack / 44% (target ≈36–44% ±5) / race span +11 s
00:01:29→00:01:40 — all inside the target envelope.

### R2-variant crash forensics (the hold hop)

| Hop / snap | Value | Leg |
|---|---|---|
| npre1→npre2 whole | 8.2478 | pre-pair: motion, no crash (18→22 MPH rising, no banner) |
| npre2→d-post1 whole | 15.0783 | HOLD: crash inside (22→2 MPH, trunk contact at d-post1) |
| d-post1→d-post2 whole | 8.1235 | recovery (2→20 MPH, rider upright, no contact) |
| d-post1 SCPS40/SCPS120 | +40 @ −0.76 RAIL / +120 @ 0.26 RAIL | hold hop rails both windows (neg-corr 40-rail) |
| Hold pair gated? | NO under all three (npre2 ROI-flood + gradient-under-count; d-post1 both-flood) | no hold-step sample exists (T43-R1 class outcome, T42-R3 crash site) |

## T45-4. R2-variant tracking (all three trackers on all 12 dense snaps) + lock-QA + variant distributions

### R2-variant RDC + SCPS table (control = frozen `t41-track.py`; ROI = frozen `t42-track.py`; gradient = `t44-track.py`; SCPS 22/22 bit-identical across all three tools, `cmp` clean)

| Snap | Control cx/cy/npix | C-gate | ROI cx/cy/npix | R-gate | Gradient cx/cy/npix | G-gate |
|---|---|---|---|---|---|---|
| npre1 | 264.0/168.1, 22843 | INVALID | 263.9/197.6, 2307 | VALID | 247.0/196.3, 165 | INVALID |
| npre2 | 323.7/201.2, 21572 | INVALID | 274.9/217.8, 7525 | INVALID | 307.1/212.4, 415 | INVALID |
| d-post1 | 433.7/263.3, 69946 | INVALID | 358.0/268.4, 18653 | INVALID | 320.3/287.7, 3316 | INVALID |
| d-post2 | 328.9/190.4, 46826 | INVALID | 306.5/244.0, 12451 | INVALID | 317.7/282.0, 2861 | VALID |
| d-post3 | 232.4/158.9, 14055 | INVALID | 300.7/262.7, 1937 | VALID | 304.6/269.1, 1228 | VALID |
| d-post4 | 282.6/205.5, 31793 | INVALID | 284.9/259.5, 7975 | INVALID | 302.9/276.9, 1967 | VALID |
| d-post5 | 308.8/176.2, 19902 | INVALID | 284.9/263.6, 3282 | VALID | 280.3/256.4, 2000 | VALID |
| d-post6 | 291.6/159.6, 12379 | INVALID | 291.8/234.0, 3000 | VALID | 299.4/271.1, 1058 | VALID |
| d-post7 | 261.4/153.6, 12210 | INVALID | 295.0/237.4, 2141 | VALID | 301.3/267.5, 948 | VALID |
| d-post8 | 230.8/174.8, 21784 | INVALID | 260.1/231.8, 5799 | VALID | 290.7/271.5, 905 | VALID |
| d-post9 | 249.2/169.5, 18169 | INVALID | 300.2/255.9, 1898 | VALID | 301.6/262.6, 1233 | VALID |
| d-post10 | 254.4/179.5, 4017 | VALID | 309.6/301.6, 1351 | VALID | 309.9/301.5, 974 | VALID |

Gate counts: control 1/12 VALID (d-post10 singleton — 11/12 flood
REPEATS T41/T42/T43); ROI 8/12 VALID; gradient 9/12 VALID.

| Hop | SCPS40 (all three tools) | SCPS120 (all three tools) |
|---|---|---|
| npre1→npre2 (pre-pair) | +24 @ 0.91 | +24 @ 0.91 |
| npre2→d-post1 (HOLD) | +40 @ −0.76 RAIL | +120 @ 0.26 RAIL |
| d-post1→d-post2 | −40 @ −0.46 RAIL | −120 @ 0.50 RAIL |
| d-post2→d-post3 | +4 @ 0.71 | +4 @ 0.71 |
| d-post3→d-post4 | +3 @ 0.77 | +3 @ 0.77 |
| d-post4→d-post5 | −14 @ 0.18 | +120 @ 0.21 RAIL |
| d-post5→d-post6 | −18 @ 0.46 | −18 @ 0.46 |
| d-post6→d-post7 | +20 @ 0.86 | +20 @ 0.86 |
| d-post7→d-post8 | +40 @ 0.27 RAIL | +82 @ 0.66 |
| d-post8→d-post9 | +40 @ −0.60 RAIL | +120 @ 0.11 RAIL |
| d-post9→d-post10 | +40 @ 0.42 RAIL | +95 @ 0.84 |

SCPS rails: SCPS40 5/11 (hold +40, d1d2 −40, d7d8/d8d9/d9d10
+40); SCPS120 4/11 strict ±120 (hold +120, d1d2 −120, d4d5 +120,
d8d9 +120).

### R2-variant lock-QA (marked-crop montage `/tmp/t45-lockqa.png`, T42 method; yellow = ROI box, red = ROI centroid, lime = gradient centroid)

| Snap | ROI lock | Gradient lock | Named intruder |
|---|---|---|---|
| npre1 | off (trunk top, ~140 px from rider) — VALID but excluded | — (INVALID-low 165) | tree trunks |
| npre2 | — (INVALID-flood 7525) | — (INVALID-low 415) | red-banded tree base + log |
| d-post1 | — (INVALID-flood 18653) | — (INVALID-flood 3316; centroid on crashed rider, gated out by count — the documented bark gate hole) | crash trunk |
| d-post2 | — (INVALID-flood 12451) | on (legs/board) | trunk top (ROI) |
| d-post3 | on (torso) | on (mid-body) | red rock left edge (outside locks) |
| d-post4 | — (INVALID-flood 7975) | on (legs) | dark red rock left ~1/4 (ROI) |
| d-post5 | on (legs/left side) | on (torso) | none in locks |
| d-post6 | borderline-on (~17 px above head, open snow) | on (torso) | none in locks (chevron sign above) |
| d-post7 | borderline-on (~15 px above head, open snow) | on (torso) | none in locks |
| d-post8 | off (~45 px left on red rock face; npix 5799 near ceiling) | on (torso) | red rock top-left (ROI) |
| d-post9 | on (torso) | on (torso) | none in locks |
| d-post10 | on (legs/board) | on (legs/board) | none in locks |

### R2-variant VALID-pair deltas (with per-pair lock QA; NO-INPUT cruise — zero inputs after the hold per poll log)

ROI (5 VALID pairs, 1 on→on):

| Pair | Δcx/Δcy | Lock QA | SCPS40 / SCPS120 |
|---|---|---|---|
| d-post5→d-post6 | +6.9 / −29.6 | on→borderline | −18 @ 0.46 / −18 @ 0.46 |
| d-post6→d-post7 | +3.2 / +3.4 | borderline→borderline | +20 @ 0.86 / +20 @ 0.86 |
| d-post7→d-post8 | −34.9 / −5.6 | borderline→off (rock bias) | +40 @ 0.27 RAIL / +82 @ 0.66 |
| d-post8→d-post9 | +40.1 / +24.1 | off→on (rock bias) | +40 @ −0.60 RAIL / +120 @ 0.11 RAIL |
| d-post9→d-post10 | +9.4 / +45.7 | on→on | +40 @ 0.42 RAIL / +95 @ 0.84 |

Gradient (8 VALID pairs, 8 on→on):

| Pair | Δcx/Δcy | Lock QA | SCPS40 / SCPS120 |
|---|---|---|---|
| d-post2→d-post3 | −13.1 / −12.9 | on→on (recovery-adjacent: crash+1, 20→35 MPH) | +4 @ 0.71 / +4 @ 0.71 |
| d-post3→d-post4 | −1.7 / +7.8 | on→on (recovery-adjacent: crash+2, 35→43 MPH) | +3 @ 0.77 / +3 @ 0.77 |
| d-post4→d-post5 | −22.6 / −20.5 | on→on | −14 @ 0.18 / +120 @ 0.21 RAIL |
| d-post5→d-post6 | +19.1 / +14.7 | on→on | −18 @ 0.46 / −18 @ 0.46 |
| d-post6→d-post7 | +1.9 / −3.6 | on→on | +20 @ 0.86 / +20 @ 0.86 |
| d-post7→d-post8 | −10.6 / +4.0 | on→on | +40 @ 0.27 RAIL / +82 @ 0.66 |
| d-post8→d-post9 | +10.9 / −8.9 | on→on | +40 @ −0.60 RAIL / +120 @ 0.11 RAIL |
| d-post9→d-post10 | +8.3 / +38.9 | on→on | +40 @ 0.42 RAIL / +95 @ 0.84 |

Cross-tracker agreement (shared on→on pair d9d10): cx +9.4 vs +8.3
(Δ1.1, T43-class) / cy +45.7 vs +38.9 (Δ6.8).

### Variant distributions (PARALLEL, quarantined — healthy series NOT appended)

| Distribution | Tracker | Variant pairs (this run) | Variant n |
|---|---|---|---|
| No-input (clean cruise) | ROI | 1 on→on (d9d10 +9.4/+45.7) | 1 |
| No-input (clean cruise) | Gradient | 8 on→on (d2d3 −13.1/−12.9, d3d4 −1.7/+7.8, d4d5 −22.6/−20.5, d5d6 +19.1/+14.7, d6d7 +1.9/−3.6, d7d8 −10.6/+4.0, d8d9 +10.9/−8.9, d9d10 +8.3/+38.9; d2d3/d3d4 recovery-adjacent) | 8 |
| Hold-step | ROI | 0 (hold ungated, crash inside) | 0 |
| Hold-step | Gradient | 0 (hold ungated, crash inside) | 0 |
| Pre-pair | both | 0 (ungated under all three — NOT a crash: 18→22 MPH rising, no banner; ROI trunk-flood + gradient under-count) | 0 |

Healthy series (unchanged): ROI floor n=3, gradient floor n=7,
hold-step n=1 crash-confounded ×2 — exactly the §T45-0 corrected
baseline. Crash-lottery read: hold-window crashes now 3/3 runs at
this phase (T42 hold-crash, T43 pre-pair+hold-crash, T45-variant
hold-crash).

## T45-5. R2-variant census + trace + forensics

| Item | Value |
|---|---|
| Census | `t45r2-variant-census.txt` (11700 B; lines=41756303, ts_span=0.1384..500.9776; T42 R3: 42967628/0.1271..508.62; T43 R1: 43623520/0.1213..515.92 — same class) |
| EE | 11170359 calls, distinct=52 (top: GetThreadId 4526689, WaitSema 2009300, SignalSema 1766469, sceSifGetReg 1260327 — the 1260327 count IDENTICAL to T42/T43) |
| IOP | 18617002 calls, distinct=155 (top: sceSdGetAddr 3695088, QueryIntrContext 3372161, CpuSuspendIntr 3153330, CpuResumeIntr 2134885 — same top-4 as T42/T43) |
| libsd (audio initialized) | sceSdGetAddr top IOP call + `pcsx2-qt` Pulse client (agrees with cubeb proof) |
| MARK | ERROR NONE; Error = `cdvdRead06(Error)` L574864 (also present 1× in T43 R1's census — benign class marker, not a variant artifact); `Failed to` = patches.zip warning (same as prior runs); VSync = DVD NTSC mode change |
| Samples | `t45r2-variant-samples.txt` (5876 B; source lines=41756303; EE.Bios FIRST 50 from L138603 RFU060) |
| Vblank stream | first `WaitVblankStart` L417043 [1.2926] (T41/T42: L417043 — same line); 397 total, ALL ≤90 (LE90/110/140/350 all 397 — IDENTICAL to T41/T42) |
| UpdateVSyncRate | Mode Changed to DVD NTSC, count 15 |
| Live trace | `emulog.txt` 2679800948 B sha `27483c1eb6ba1f1584927d3dc49416e2417a5e611d7882908c9522b299e9445d` (R1's partial preserved via `emulog-pre-t44-20260922T005924Z.txt`) |
| Rotation | T42 R3 + T43 R1 + T44 R1 + live variant chain on bytesize; all prior rotations untouched |
| Share stream (SSD ABSENT) | `/Volumes/share/ssx3/ps2x-t4/emulog-t45r2-variant.txt` size+sha MATCH (2679800948 B, `27483c1e…9445d`); head/tail 30-line slices committed (`t45r2-variant-emulog-head/tail.txt`, shas `12935c2a…`/`81c117e0…`) |
| Boot logs | `t45r2-variant-boot.log` 4231 B (DIFFERS from R1's — own content) + `t45r2-variant-boot.stdout` 210 B (byte-identical to R1's: same DRI3 warnings + CTRL+C graceful shutdown — deterministic) |
| R1 boot logs (T44 gap) | `t45r1-boot.log` 4231 B sha `5c0edb0b…` + `t45r1-boot.stdout` 210 B sha `360108bc…` (fetched BEFORE R2 overwrote) |
| NVM post-run | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961` FULL sha — UNCHANGED (T44's first-16 gap closed) |
| C: post-run | 281 G avail (unchanged across the run; WSL `/` 901→898 G, ~3 GB trace+rotation drain) |
| Analyze | `t45r2-variant-analyze.txt` (56-line clean log, H61 re-run 01:11:25→01:12:48; H60 first attempt killed mid-census by turnover — outputs deterministic over the static trace) |

Forensics (observed events, tables only — no verdicts): hold-hop
tree crash (d-post1 2 MPH trunk contact, 2ND held throughout —
position never decayed); pre-pair is tracking-ungated but NOT a
crash (18→22 MPH, no banner); red-rock ROI intrusions (d4 flood,
d8 off-lock); d6/d7 ROI borderline-above-head pair (snow
centroids, gradient torso-locked same snaps); v2a R3-pattern +
game-only census (no modal under the null sink); H60→H61 idle
turnover post-run; H61 PulseServer present (informational).

### R2-variant snap sizes (61, on-box bytes)

start 53990, a1-now 54827, a1-poll01 58339, a1-pre 58339,
a1-post3 50107, a1-post8 50006, a1-post15 49634, a1-post25 49786,
menupre 49646, mc-post1 70245, mc-post3 70628, mc-post8 70147,
mc-post15 69995, scpre 70202, zc-post1 51228, zc-post3 51763,
zc-post8 50974, ccpre 51710, sp-post1 65621, sp-post3 65261,
sp-post8 65445, sppre 65342, pc-post1 67365, pc-post3 67482,
pc-post8 67528, smpre 67434, rc-post1 69684, rc-post3 69506,
rc-post8 69444, sepre 69671, sj-post1 59154, sj-post3 58907,
sj-post8 58541, mrpre 58976, mr-post1 66795, mr-post3 67421,
mr-post8 55308, mr-post15 59686, mr-post25 60058, mr-post40 59728,
mr-stab1 59769, mr-stab2 59866, pppre 59987, x-post1 69597,
x-post3 66982, x-post8 67988, x-post15 63204, x-post25 69750,
x-post40 61347, npre1 57912, npre2 60555, d-post1 52664,
d-post2 51627, d-post3 53123, d-post4 52689, d-post5 66294,
d-post6 63968, d-post7 58181, d-post8 56861, d-post9 59885,
d-post10 55859.

## T45-6. Exact commands (reproduce-from-scratch)

Pre-run pins (one `wsl` call per ssh; single-quote outer,
double-quote inner — the remote shell is PowerShell: bare `$`
expands (NEVER use shell variables in the remote string — use
`cd` + relative paths), nested double-quotes break pipes (quoteless
pipes inside `bash -c` are fine)):
`ssh bytesize 'wsl bash -c "…"'` for date/uptime/btime (boot),
`sha256sum` + `stat` (binary), `git -C pcsx2 rev-parse HEAD` +
`status --short` (tree), `ls -la inputs/`, `sha256sum` + `stat`
(live NVM), `grep -n Cross/Left` (bindings), 9-ref `sha256sum`,
T43/T42 snap `ls` (spot size + counts), live-trace `ls`, `df -h /`
+ `/mnt/c`, `ls /mnt/wslg/PulseServer` + `runtime-dir/pulse/` +
`pulseaudio.log` (audio gate, immediate + delayed @uptime ≥30),
dmesg (`wsl dmesg` → local), eventlog (`wevtutil qe System
/c:120 /rd:true /f:text` → local).
Variant setup: `wsl -u root apt-get update` → `wsl -u root
apt-get install -y pulseaudio` → `unset PULSE_SERVER; pulseaudio
--start --exit-idle-time=-1` → `pactl info` + `pactl list sinks
short` (PULSE_SERVER unset).
X11: `wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs
/tmp/.X11-unix`. PPM: `wsl python3 t44-cropdiff.py t35-ref-panel.ppm
t35-ref-panel.ppm` → `mean=0.0000 p99=0`.
R1 logs first: `wsl cp logs/boot-t44.* /mnt/c/…` → `scp
'bytesize:C:/Users/bradr/pcsx2-t4/boot-t44*'` → rename `t45r1-*` →
`wsl rm`.
Run: `ssh bytesize 'wsl bash -c "export
PULSE_SERVER=unix:/run/user/1000/pulse/native; cd
/home/brad/pcsx2-t4 && stdbuf -oL -eL ./t44-auto.sh"'` (local
redirect, managed background) → local `sleep 35` → `wsl
t44-dialogwatch2.sh` (local redirect) → window census
(`DISPLAY=:99 xdotool search --onlyvisible --name SSX/Error`) →
live-trace cubeb grep + `pactl list sink-inputs/clients` (proof).
Fetch (full set): `wsl cp` 61 JPGs + poll + census + samples +
boot logs → C: → `scp` globs → rename `t44-*` → `t45r2-variant-*`
→ `wsl rm`. Refs: same recipe (9 PPMs, /tmp use, shas verified,
NOT committed).
Post-hoc (local): `/tmp/t45-batch.py` (panel + hops; bit-exact 4/4
vs committed), `t41/t42/t44-track.py` (dense 12),
`/tmp/t45-montage.py` (lock-QA), viewed snaps (dense 12 + 3 chain
anchors), `grep` (press walls, cubeb, census rows).
Trace: `COPYFILE_DISABLE=1 ssh … "wsl cat …/emulog.txt" >
/Volumes/share/ssx3/ps2x-t4/emulog-t45r2-variant.txt` → size+sha
verify + head/tail slices (share tier — SSD unmounted).

Gaps (tabled, none load-bearing for the variant report): H60
post-run dmesg MISSED (turnover before capture — T42-R2-class
receipt gap; H61-boot file relabeled honestly); H61 audio health
unprobed behaviorally (socket-present is informational only —
healthy re-drive stays queued); x-post2–40 HUD per scores only
(x-post1 viewed; chain screens gate-verified); interpolated T+ on
chain snaps (±1 s; scored anchors exact); healthy hold-step
distribution still n=1 crash-confounded (no healthy run banked);
healthy no-input floors still ROI n=3 / gradient n=7 (no healthy
run banked); variant pre-pair n=0 (ungated, non-crash);
`pulseaudio` package persists on the distro disk (variant
deviation; future healthy runs unaffected — WSLg socket takes
precedence when present, and nothing in the scripts references the
user daemon).

## T45-7. Tail receipt (truncated tail FAILS the gate)

T45 executed the variant path end-to-end: audio gate (2
demand-boots H59/H60 + ~7-min stopped wait, all DOWN with full T41
signatures — 8th consecutive down boot; H61 socket-present noted
informational) + variant setup (pulseaudio 16.1 installed as root,
user daemon + auto_null sink receipted, ONE-env-var launch, zero
script edits) + pins (binary/tree/inputs/NVM/bindings/refs/snaps/
trace/space all reproduce; staged shas 5/5 match → T44 scripts
reused, no `t45-*` copies) + R1 boot logs fetched first (T44 gap
closed) + R2-VARIANT-NULLSINK (T44_DONE exit 0: TRUE TITLE
first-attempt, full chain, XCROSS @T+436.90, ONE Left hold @T+504.95
×1682.9 ms, dense 10 @T+507–512; cubeb negotiated 8/0/0 with a live
sink-input; v2a R3-pattern + game-only census = no modal) +
tracking (control 1/12, ROI 8/12, gradient 9/12; SCPS 3-way 22/22
identical; lock-QA montaged: hold ungated all three with a tree
crash inside 22→2 MPH, pre-pair ungated non-crash) + variant
distributions (ROI no-input n=1 on→on; gradient no-input n=8 on→on
incl. 2 recovery-adjacent; hold n=0; healthy series untouched) +
trace (2.68 GB + sha MATCH on share tier, SSD absent; NVM FULL sha
unchanged; vcount 397 all ≤90). Evidence: `local/research/T45/`
(REPORT + R1 boot logs + 61 variant JPGs + poll/census/samples/
analyze/stdout/stderr/dialogwatch/boot/emulog-slices + dmesg ×4 +
eventlog pre/final; no `t45-*` scripts — none needed). Commit
`[T45]` with trailer `Orchestrated-By: Muse Code`, NO PUSH per lane
instruction. END-OF-REPORT.
