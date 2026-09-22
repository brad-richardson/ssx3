# T46 report — Healthy R3 re-drive on audio-healthy H62 (CORRECTED baselines; variant quarantined)

Brief: T46 (re-drive the HEALTHY series on the next audio-healthy VM;
T45 ran the ONE authorized null-sink variant run and stopped; variant
distributions quarantined, healthy series untouched). Read
`local/research/T45/REPORT.md` first (all of it). T45's dir is READ-ONLY
reference. Tables, no verdicts.

CORRECTED baselines carried (T44-E1 erratum; T42 §T42-6 + T43 §T43-5,
gate-verified; T46 re-verified each value against the REPORTs —
§T46-0; the ONLY baseline; append-only; no re-tune):

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
- Variant-quarantined (NEVER appended, never merged): ROI no-input n=1
  (d9d10 +9.4/+45.7); gradient no-input n=8 (T45 §T45-4, 2
  recovery-adjacent); hold n=0; pre-pair n=0.

Experiment contract (up front): hypothesis — on an audio-healthy VM
the T44-shape run reaches live and banks healthy pairs; observable —
socket receipts, pactl receipts, daemon/sink receipts, cubeb trace
lines, modal census, run chain, hold row, blind 10-snap series +
per-snap HUD + all-three-tracker scoring + lock-QA per VALID pair;
alternatives — the hold crashes (→ full 3-row crash receipts + R4 ONCE;
R4 crash → freeze + STOP), the run never reaches live (→ environment
NO-PARK per T27 §4); stop — first crash-free run scored + REPORT, or
both runs crash-confounded. The variant is NOT re-run under this
brief (one variant run was the authorization).

## T46-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence only) |
| `adb` | Not used |
| Installs | None this session (pulseaudio 16.1 persists on distro disk from T45's variant setup; user daemon auto-started on H62 — receipted §T46-2, holds zero run audio) |
| Copyrighted downloads | None (inputs already staged) |
| ssx3 HEAD at commit | Below (`[T46]`, trailer `Orchestrated-By: Muse Code`, NO push per lane instruction) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; disk
pins taken on VM-H62, VM-independent across turnover):

| Item | T4 value | T46 observed | Match |
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
| Free space | — | WSL `/` 898 G avail pre; C: 280 G pre (GATE ~5 GB+ PASSES) | yes |
| Live trace pre-run | — | `emulog.txt` 2679800948 B = T45 R2-variant's (mtime Sep 21 21:07; rotated at R3 boot, §T46-3) | yes |
| Staged scripts | T44 shas | all 5 WSL-staged shas match local (auto `a3acb2d6…`, analyze `bf966f02…`, vcount `105cd092…`, cropdiff `ac114212…`, dialogwatch2 `d9c7a4c1…`) → REUSED, zero `t46-*` script copies (no edits needed) | yes |
| WSLg audio pre-run | — | socket PRESENT H62 (immediate @up42 + delayed @up151; pactl 35/35 §T46-2) → healthy path; behavioral gate at boot (modal census, §T46-3) | gate |

Baseline re-verification (T46 vs T42 §T42-6 + T43 §T43-5 — every
corrected value re-read from the REPORTs this session):

| Distribution | T46 brief line | REPORT text | Match |
|---|---|---|---|
| ROI floor T42 | npre1npre2 −0.7/−22.2 | T42 §T42-6 L664 `npre1→npre2 −0.7 / −22.2` + T43 §T43-5 L680 | yes |
| ROI floor T43 | d5d6 +2.8/−12.7, d9d10 −4.5/−7.0 | T43 §T43-5 L680 `d5d6 +2.8/−12.7, d9d10 −4.5/−7.0` | yes |
| Gradient floor T42 | +1.8/+4.8, +0.0/+10.6, +2.7/−3.9, −2.1/−4.2 | T43 §T43-5 L681 `npre1npre2 +1.8/+4.8, d5d6 +0.0/+10.6, d6d7 +2.7/−3.9, d7d8 −2.1/−4.2` | yes |
| Gradient floor T43 | d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7 | T43 §T43-5 L681 `d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7` | yes |
| Hold ROI / gradient | T42 +11.2/−39.5 / −4.4/−24.1 crash inside; T43 0 | T42 §T42-6 L665 hold row + T43 §T43-5 L682–683 (`0 (hold ungated)` ×2) | yes |

Phase-match targets (tabled BEFORE the run — T42 R3's hold window via
T43 R1's; match PHASE not seed):

| Item | Hold-window value (T42 R3 / T43 R1) | T46 hold-window target |
|---|---|---|
| Hold slot | T+502.49 / T+509.34 (keydown) | ≈T+502.5–509.5 (same script slot) |
| Pre-pair race clocks | 00:01:27-ish / 00:01:27 / 00:01:27 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | back-of-pack / front-of-pack | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36–37% / 43–44% | ≈36–44% ±5 pp |
| Series span | 10 snaps over +7.37–7.40 s wall / +10–11 s race | 10 snaps over ≈+7.4 s wall (same `sleep 0.5` blind capture) |

Same-shape record (tabled BEFORE the run — the deliberate NON-change):

| Item | T43 R1 (`sleep 0.5`) | T46 (this run) |
|---|---|---|
| Dense-phase shape | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls | identical (staged `t44-auto.sh` reused byte-identical, sha-verified) |
| Pre-pair gap | `sleep 0.5`, no scoring | identical call |
| Hold | ONE `press_hold Left` (1 s `sleep`, T38's body) | identical call, same slot |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) | identical calls |
| Audio sink | WSLg PulseServer socket | identical (default `PULSE_SERVER`, zero env changes — variant deviation NOT carried) |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log + census + samples + boot logs | scp via C: staging (T25 recipe) | `t46r3-*.jpg`, `t46r3-poll.log/census/samples/boot` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t44-cropdiff.py`, bit-exact validated 4/4 (T39–T43 protocol); committed tool reproduces any score | screen chain table + xrun frame identities |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking, CONTROL | committed `t41-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. Dense 12-snap tracking, ROI | committed `t42-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 6. Dense 12-snap tracking, GRADIENT | committed `t44-track.py` (§T44-1a variant) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 7. View snaps | local reads | HUD per dense snap (clock/position/progress/speed/score) + chain anchors |
| 8. Lock-QA every VALID pair | marked-crop montage method (T42) | on/borderline/off + named intruder per snap; on→on sets |
| 9. Distribution tables | — | HEALTHY distributions appended on crash-free (variant stays quarantined) |

## T46-1. Session log (H62 only)

Clocks: WSL `date -u` true UTC; `wevtutil` renders local-as-Z (+4 h →
UTC); H-numbers continue T45's H61. WSL fully Stopped at session start.
A holder (`wsl sleep 7200`) kept H62 alive for the whole run — no
turnover, no `--shutdown`, no reconnect demand-boots after the first.

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 15:16:49 (up 0) | H62 demand-boot (btime 1790090208; first `wsl` call of the session) | boot clocks |
| 2 | 15:17:31 (up 42.56) | H62 audio IMMEDIATE: HEALTHY (PulseServer socket + `runtime-dir/pulse/` native+pid + full `/mnt/wslg/` incl. pulseaudio.log) | socket checks |
| 3 | 15:17:31+ | Holder started (`wsl sleep 7200`); local sha survey (T44 staged 5/5 + frozen trackers 4/4 reproduce) + baseline re-verification + SSD tier check (mounted, 127 G avail → SSD preferred) | this file |
| 4 | 15:19:20 (up 151.71) | H62 audio DELAYED: HEALTHY (socket recheck + `PULSE_SERVER=unix:/mnt/wslg/PulseServer` + pactl 35/35 RDPSink) | `t46-audiogate-h62.txt`, `t46-pactl-h62.txt` |
| 5 | ~15:20 | Pins (§T46-0 table: binary/tree/inputs/NVM/bindings/refs/snaps/trace/space/staged all reproduce) + previous-run boot logs verified = committed T45 shas (gap discipline, no fetch needed) | this file |
| 6 | ~15:20 | X11 tmpfs mount (root, rw 10240k) + PPM 0.0000/0 + eventlog-pre (63300 B) + H62 dmesg-pre (474 lines, 1 AcceptAsync [25.12]) | `t46-dmesg-h62-pre.txt`, `t46-eventlog-pre.txt` |
| 7 | 15:21:03–15:29:39 (T+0–516; script start 15:20:57) | R3-HEALTHY: background launch (T_BOOT 1790090463, uptime 254) → v2a @T+40.6 → census @T+100 → live → dense → `T44_DONE`, exit 0 (§T46-3) | stdout 427 lines, stderr 2551 lines |
| 8 | ~15:32 | Analyze (same boot H62, clean) — census 11702 B + samples 5844 B | `t46r3-analyze.txt/census/samples` |
| 9 | 15:32–15:35 (+ NVM-post primary 15:42:47, held boot) | Post-run receipts (NVM FULL sha unchanged, C: 277 G, vcount 397 all ≤90, cubeb full-run 8/0/0) + 66-file fetch → renamed `t46r3-*` + C: cleaned (962 pre-existing remain) + dmesg-post + eventlog-final | files below; §T46-5 |
| 10 | 15:35–15:43 | Trace stream to SSD tier (2682545633 B + sha MATCH) + refs fetch (9 × 3932177 B, shas reproduce; /tmp use, NOT committed) + batch scorer (bit-exact 4/4) + 3 trackers + 15 snap views + montage + zoom | `/tmp/t46-batch.py`, `/tmp/t46-montage.py`, SSD `emulog-t46r3.txt` |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| Package install | NONE this session (pulseaudio 16.1 persists from T45's variant setup) |
| Pulse daemons | WSLg server (protocol 35, RDPSink — carries the run) + auto-started user daemon (brad PID 309, auto_null, sink-inputs EMPTY during run — holds zero run audio) |
| `/tmp/.X11-unix` | tmpfs `mode=1777` (as root, T4 recipe) on H62 pre-run; does not persist reboot |
| Xvfb | `:99 -screen 0 1280x1024x24`, started by the script itself (`setsid nohup`, log `/tmp/xvfb-t44.log`); dead with H62 |
| Dirs/files created | `…/logs/emulog-pre-t44-20260922T152103Z.txt` (R2-variant's 2679800948 B, rotated at R3 boot), `t44-*.jpg/.ppm/.log/.txt` (R3 set: 61 JPGs + poll + census + samples), `C:\Users\bradr\pcsx2-t4\t44*` staging (removed after each batch) |
| Dirs/files OVERWRITTEN | `t44-*.jpg` (R2-variant's 61, overwritten by the run), `t44-poll.log`, `logs/boot-t44.log`/`.stdout` (R2-variant's content verified = committed T45 shas FIRST, §T46-1 #5), `t44-census.txt`, `t44-samples.txt` |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20), T42/T43 rotations, `emulog-pre-t44-20260922T005924Z.txt` (T44 R1's partial), `emulog-pre-t44-20260921T215827Z.txt` (T43 R1's trace) |
| Restarts by me | 0 |
| VM restarts (not by me) | 0 (holder held H62 throughout) |

## T46-2. Audio gate (HEALTHY first boot; variant NOT run)

| VM | btime | Socket checks | dmesg | Note |
|---|---|---|---|---|
| H62 | 1790090208 | PRESENT (immediate @up42.56 + delayed @up151.71; full T41 signature inverted: PulseServer socket + `runtime-dir/pulse/` native+pid + pulseaudio.log + RDPSink/RDPSource entries) | pre 474 lines, 1 AcceptAsync [25.12] | post-Stopped demand-boot; holder held |

Gate receipts (H62, in order):

| # | Step | Command (one `wsl` call per ssh) | Result |
|---|---|---|---|
| 1 | Immediate sockets | `ls -la /mnt/wslg/PulseServer` + `ls -la /mnt/wslg/runtime-dir/pulse/` + `ls /mnt/wslg/` | `srwxrwxrwx` PulseServer + native socket + pid + full 12-entry dir (incl. pulseaudio.log), @up42.56 |
| 2 | Delayed sockets | same @up151.71 | same, all PRESENT |
| 3 | Launch env | `printenv PULSE_SERVER` | `unix:/mnt/wslg/PulseServer` (default; ZERO env changes — the variant's export is NOT carried) |
| 4 | Behavioral proof | `pactl info` + `pactl list sinks short` (default server) | Server `unix:/mnt/wslg/PulseServer`, Library 35 / Server 35 CONNECTED, pulseaudio 16.1-8-g6f04, Default Sink `RDPSink`, `1 RDPSink module-rdp-sink.c s16le 2ch 44100Hz SUSPENDED` |
| 5 | Null-sink non-involvement | user-daemon `pactl list sink-inputs` during run | EMPTY (auto_null SUSPENDED, zero clients — the T45-persisting daemon carries nothing) |
| 6 | cubeb proof (live trace) | `grep -a -i cubeb emulog.txt` (+ `pactl list sink-inputs/clients`) | 5 init/negotiation lines [0.5533–0.5583] + `pcsx2-qt` PID 632 sink-input `float32le 2ch 48000Hz` protocol 35 on Sink 1 (RDPSink); full-run counts §T46-3 |
| 7 | Modal gate | v2a + window census | R3-pattern (no modal) + game-only census (details §T46-3) |

## T46-3. R3-HEALTHY — full live run, crash-free hold (late d9d10 wall crash)

R3 booted on VM-H62 (T_BOOT 1790090463, uptime 254; 15:21:03 UTC)
under HEALTHY audio (cubeb-pulse negotiated
[0.5533/0.5551/0.5580/0.5580/0.5583], zero null-fallback/CUBEB_ERROR
lines in the full 2.68 GB trace, clean stop/destroy at shutdown
[505.92/505.96]; TRUE TITLE viewed on a1-poll01 with no modal; v2a
R3-pattern + game-only census) and ran the full chain through the
pre-race panel into the live race, where the hold landed clean
(npre2 51 MPH → d-post1 27 MPH, rider upright, no contact, no
banner, no RECOVER) and the dense series ran clean cruise until a
wall crash in the LAST hop (d-post9 49 MPH → d-post10 26 MPH,
tumble + spray + RECOVER meter). `T44_DONE`, exit 0, clean shutdown
at uptime 770 (T+516). 427-line stdout / 2551-line stderr. WID
2097159 (same as T31–T45). Poll log 168 lines (T44 plan's `poll
168` exact).

| Item | Value |
|---|---|
| R3 window | 15:21:03–15:29:39 UTC (T+0–516), VM-H62 uptime 254→770 |
| Dialogwatch v2 | ROUND:1 @T+40.6: SKIP-ROOT 511 + SKIP-GAME 2097159 (`SSX 3 [Devel]` 640x480) + DISMISS 2097162 `pcsx2-qt` 640x480 + DISMISSED-EXIT (main-window, inert — R3 pattern; NO modal existed to dismiss; window census @T+100: game-only, no `Error`) → no v2b |
| Title detect | A1 `poll01` remote 0.4379/5 (PIL post-hoc 0.0442/0) — parked FIRST attempt (a2/a3 never ran); TRUE TITLE viewed |
| ZC park | `zc-post1` vs-zc remote 0.5109/8 (PIL 0.2757/6) PARKED at +1 s (viewed: Zoe + Continue/Equip Gear/Rider Details/Music) — R1's slow-load refusal (p1-p3 1.7110) absent here (p1-p3 0.2959) |
| cubeb full-run | 8 lines: create [0.5533] + negotiate [0.5551/0.5580] + init/start [0.5580/0.5583] + stop ×2 [505.92/505.96] + destroy [505.96]; null-fallback 0, CUBEB_ERROR 0; `pcsx2-qt` PID 632 sink-input `float32le 2ch 48000Hz` protocol 35 on RDPSink |
| Presses | 10 menu/Start/X Cross (all 533.3–536.1 ms) + ONE Left hold 1036.1 ms; ZERO other game inputs (11 KEYDOWN + 11 KEYUP in the 168-line poll log) |

### R3 press log (poll-log walls; T+ = wall − 1790090463)

| Press | Keydown wall (T+) | Keyup wall (T+) | Width |
|---|---|---|---|
| A1 Cross (attract-skip) | 1790090561.718 (T+98.72) | 1790090562.251 (T+99.29) | 533.3 ms |
| A1 Start (on title) | 1790090565.007 (T+102.01) | 1790090565.542 (T+102.54) | 535.6 ms |
| MENU Cross (Single Event) | 1790090604.224 (T+141.22) | 1790090604.758 (T+141.76) | 534.4 ms |
| ZOE Cross | 1790090644.257 (T+181.26) | 1790090644.791 (T+181.79) | 533.9 ms |
| CONT Cross | 1790090672.981 (T+209.98) | 1790090673.517 (T+210.55) | 535.6 ms |
| PEAK Cross | 1790090701.745 (T+238.75) | 1790090702.281 (T+239.32) | 535.3 ms |
| RACE Cross | 1790090731.050 (T+268.05) | 1790090731.585 (T+268.59) | 534.8 ms |
| SNOWJAM Cross | 1790090762.177 (T+299.18) | 1790090762.711 (T+299.71) | 533.9 ms |
| ENTER Cross | 1790090790.806 (T+327.81) | 1790090791.341 (T+328.34) | 534.7 ms |
| XCROSS (race start) | 1790090895.748 (T+432.75) | 1790090896.284 (T+433.28) | 536.1 ms |
| HOLD Left | 1790090962.694 (T+499.69) | 1790090963.730 (T+500.73) | 1036.1 ms |

Hold-width note (tabled, no verdict): the width is the ≈1037 ms
class (T41 R4 1038.4, T42 R3 1036.5, T40 R2 1038.0 — NOT the
1682.9 ms loaded-VM class of T45-variant); keydown T+499.69 sits
2.8 s ahead of the T+502.5–509.5 target slot (menu-phase timing
drift run to run; same script slot). Series span: npre1→d-post10
+7.45 s wall (target ≈+7.4 s).

### R3 chain panel (post-hoc PIL; titleband vs title-ref, whole vs each ref, setag vs se-ref)

| Snap | titleband | Best whole ref (mean/p99) | Identity |
|---|---|---|---|
| start | 24.46/171 | panel 17.41/176 | attract |
| a1-now | 34.95/191 | panel 12.89/147 | attract |
| a1-poll01 | 0.0442/0 | title 0.0347/0 | TRUE TITLE (viewed) |
| a1-pre | 0.0442/0 | title 0.0347/0 | = poll01 (cp-identical size 58424) |
| a1-post3/8/15/25 | 16.24–16.33/138 | menu 0.03–0.09/0–1 | Main Menu |
| menupre | 16.28/138 | menu 0.0582/1 | Main Menu |
| mc-post1/3/8/15 | 12.46–12.50/163 | sc 0.19–0.24/3–4 | Select Character |
| scpre | 12.46/163 | sc 0.3439/9 | Select Character |
| zc-post1/3/8 | 15.83–15.87/128–129 | zc 0.15–0.28/2–7 | Setup Character PARKED (zc-post1 viewed: Zoe present at +1 s) |
| ccpre | 15.83/128 | zc 0.1718/4 | Setup Character |
| sp-post1/3/8 | 23.12/171 | sp 0.005–0.06/0 | Select Peak |
| sppre | 23.13/171 | sp 0.0045/0 | Select Peak |
| pc-post1/3/8 | 26.29–26.30/183 | sm 0.058–0.06/0–1 | Select Mode |
| smpre | 26.33/183 | sm 0.0631/1 | Select Mode |
| rc-post1/3/8 | 26.19–26.20/183 | se 0.03–0.08/0–1, setag 0.009–0.02/0–1 | Select Event |
| sepre | 26.20/183 | se 0.0612/0, setag 0.0567/2 | Select Event |
| sj-post1/3/8 | 9.82–9.83/135 | mr 0.11–0.17/1–2 | My Rules |
| mrpre | 9.87/136 | mr 0.1437/2 | My Rules |
| mr-post1/3 | 17.69/169, 17.85/170 | title 11.54/127, 11.67/127 | transition (mid-fade, no ref) |
| mr-post8 | 28.94/237 | panel 18.90/190 | panel arriving |
| mr-post15/25/40, stab1/2, pppre | 34.49–34.50/184 | panel 0.32–0.68/6–19 | pre-race panel |
| x-post1/3/8/15/25/40 | 10.72–21.61 | none ≤10.19 (gameplay, no ref) | live race (x-post1 viewed: start gate, countdown 2, 00:00:00, 0 MPH) |
| npre1/2, d-post1–10 | (dense §below) | none (gameplay, no ref) | live race Snow Jam |

### R3 transition hops (whole-frame, post-hoc PIL)

chain: start→a1-now 12.79, a1-now→a1-poll01 24.34, poll01→a1-pre
0.0000, a1-pre→a1-post3 14.10, post3→8 0.06, 8→15 0.02, 15→25
0.05, post25→menupre 0.07, menupre→mc-post1 10.14, mc1→3 0.11,
3→8 0.20, 8→15 0.24, 15→scpre 0.26, scpre→zc-post1 7.36,
zc1→3 0.30, 3→8 0.30, 8→ccpre 0.27, ccpre→sp-post1 9.34,
sp1→3 0.01, 3→8 0.06, 8→sppre 0.06, sppre→pc-post1 5.20,
pc1→3 0.05, 3→8 0.06, 8→smpre 0.07, smpre→rc-post1 0.53
(T32-G1 small SM→SE hop class), rc1→3 0.05, 3→8 0.05, 8→sepre
0.03, sepre→sj-post1 10.64, sj1→3 0.18, 3→8 0.11, 8→mrpre 0.10,
mrpre→mr-post1 12.61, mr1→3 1.48, 3→8 25.14, 8→15 18.95,
15→25 0.09, 25→40 0.36, 40→stab1 0.30, stab1→2 0.32, 2→pppre
0.15, pppre→x-post1 14.28, x1→3 13.87, 3→8 14.10, 8→15 9.51,
15→25 7.92, 25→40 9.15, x40→npre1 14.60.
dense: npre1→npre2 7.92, HOLD npre2→d-post1 7.57 (in-band —
NOT the largest), d1→d2 6.65, d2→d3 8.54, d3→d4 11.45,
d4→d5 8.58, d5→d6 8.09, d6→d7 4.59, d7→d8 7.82, d8→d9 11.23,
d9→d10 16.40 (crash hop, largest). Dense range 4.59–16.40
(T42 R3: 5.07–18.39 — same motion class).

### R3 dense HUD (all 12 viewed; score 1050 const)

| Snap | Clock | Pos | Prog | MPH | Note |
|---|---|---|---|---|---|
| npre1 | 00:01:23 | 5TH/6 | 37% | 55 | rider mid-frame in channel, red arch top-right |
| npre2 | 00:01:23 | 5TH/6 | 37% | 51 | rider center, clean cruise, spray behind |
| d-post1 | 00:01:26 | 6TH/6 | 37% | 27 | rider UPRIGHT on channel edge, rival left; NO contact, NO banner, NO recover |
| d-post2 | 00:01:27 | 6TH/6 | 37% | 32 | rider upright center, recovering |
| d-post3 | 00:01:28 | 6TH/6 | 37% | 33 | slope edge, trees left, purple marker |
| d-post4 | 00:01:29 | 6TH/6 | 37% | 38 | along fallen log, dense trees, no contact |
| d-post5 | 00:01:29 | 6TH/6 | 38% | 32 | next to rock wall, dip, upright, no contact |
| d-post6 | 00:01:30 | 6TH/6 | 38% | 48 | clean cruise, ice-cave glow right |
| d-post7 | 00:01:31 | 6TH/6 | 38% | 49 | clean cruise in channel |
| d-post8 | 00:01:33 | 6TH/6 | 39% | 49 | clean cruise, red structure right |
| d-post9 | 00:01:33 | 6TH/6 | 39% | 49 | clean cruise by red structure |
| d-post10 | 00:01:34 | 6TH/6 | 39% | 26 | WALL CRASH: rider tumbling at dark red wall, spray, RECOVER meter, 49→26 MPH |

Phase-match read: pre-pair 00:01:23 (target ≈00:01:2x–3x) /
5TH racing pack / 37% (target ≈36–44% ±5) / race span +11 s
00:01:23→00:01:34 — all inside the target envelope.

### R3 hold-hop forensics (CLEAN) + d9d10 crash forensics

| Hop / snap | Value | Leg |
|---|---|---|
| npre1→npre2 whole | 7.9193 | pre-pair: motion, no crash (55→51 MPH cruise, no banner) |
| npre2→d-post1 whole | 7.5665 | HOLD: CLEAN (51→27 MPH slowdown with 5TH→6TH decay, rider upright, NO contact/banner/RECOVER — input-effect class, not crash class) |
| d-post1→d-post2 whole | 6.6532 | post-hold cruise (27→32 MPH recovering, rider upright) |
| d-post1 SCPS40/SCPS120 | −40 @ −0.13 RAIL / +120 @ 0.44 RAIL | hold hop rails both windows (SCPS rails occur on clean cruise too — cf. T45 d8d9; viewing governs) |
| Hold pair gated? | YES under ROI + gradient (both VALID, both on→on) | first gated CLEAN hold pair since T42 R3 (T43 hold ungated, T45-variant hold ungated) |
| d-post8→d-post9 whole | 11.2264 | clean cruise (49→49 MPH, no event) |
| d-post9→d-post10 whole | 16.3967 | CRASH inside (49→26 MPH, wall tumble + spray + RECOVER meter at d-post10) |
| d9d10 SCPS40/SCPS120 | −40 @ −0.70 RAIL / −120 @ 0.16 RAIL | crash hop rails both windows |
| d9d10 pair gated? | ROI: NO (d-post10 INVALID-flood 20585, auto-excluded); gradient: gated VALID but crash-tainted (centroid on tumbling rider — lock-QA EXCLUDED, never auto-counted) | crash removes ONE no-input pair only; hold + pre-pair + 6 cruise pairs stand |

Disposition (tabled): the crash lottery question is the HOLD —
R3's hold is crash-free, so NO R4 is run (R4 authorized iff R3's
hold crashes; a last-hop wall crash 5 s post-hold does not
confound the hold, pre-pair, or hold-adjacent pairs).

## T46-4. R3 tracking (all three trackers on all 12 dense snaps) + lock-QA + distributions

### R3 RDC + SCPS table (control = frozen `t41-track.py`; ROI = frozen `t42-track.py`; gradient = `t44-track.py`; SCPS 22/22 bit-identical across all three tools, `cmp` clean)

| Snap | Control cx/cy/npix | C-gate | ROI cx/cy/npix | R-gate | Gradient cx/cy/npix | G-gate |
|---|---|---|---|---|---|---|
| npre1 | 349.8/242.1, 8786 | INVALID | 320.7/312.1, 2775 | VALID | 329.3/286.1, 873 | VALID |
| npre2 | 337.6/283.6, 1669 | VALID | 330.7/291.7, 1598 | VALID | 330.8/291.4, 1087 | VALID |
| d-post1 | 233.3/179.7, 9728 | INVALID | 342.5/313.9, 2164 | VALID | 340.6/311.2, 1336 | VALID |
| d-post2 | 256.7/196.0, 16997 | INVALID | 298.4/263.6, 3560 | VALID | 309.6/276.5, 1896 | VALID |
| d-post3 | 269.6/238.7, 29100 | INVALID | 288.4/257.8, 13974 | INVALID | 292.9/266.4, 5490 | INVALID |
| d-post4 | 318.0/252.2, 85221 | INVALID | 321.0/268.9, 26331 | INVALID | 318.0/278.2, 9127 | INVALID |
| d-post5 | 378.2/225.2, 69320 | INVALID | 328.9/266.9, 29866 | INVALID | 321.5/304.9, 3469 | INVALID |
| d-post6 | 406.1/205.3, 20419 | INVALID | 340.5/276.6, 2796 | VALID | 326.9/295.0, 1229 | VALID |
| d-post7 | 386.1/188.2, 4502 | VALID | 323.3/298.6, 1567 | VALID | 324.5/297.0, 1076 | VALID |
| d-post8 | 362.4/203.8, 2584 | VALID | 321.0/280.5, 1424 | VALID | 321.7/279.7, 1058 | VALID |
| d-post9 | 460.3/205.8, 32055 | INVALID | 376.1/235.8, 3621 | VALID | 336.4/275.6, 968 | VALID |
| d-post10 | 384.2/237.5, 83770 | INVALID | 318.1/270.3, 20585 | INVALID | 318.9/323.3, 832 | VALID |

Gate counts: control 3/12 VALID (npre2/d-post7/d-post8 —
9/12 flood REPEATS T41/T42/T43); ROI 8/12 VALID; gradient 9/12
VALID.

| Hop | SCPS40 (all three tools) | SCPS120 (all three tools) |
|---|---|---|
| npre1→npre2 (pre-pair) | +15 @ 0.66 | +15 @ 0.66 |
| npre2→d-post1 (HOLD) | −40 @ −0.13 RAIL | +120 @ 0.44 RAIL |
| d-post1→d-post2 | −19 @ 0.78 | −19 @ 0.78 |
| d-post2→d-post3 | +40 @ 0.66 RAIL | +50 @ 0.67 |
| d-post3→d-post4 | +40 @ 0.52 RAIL | +100 @ 0.79 |
| d-post4→d-post5 | −37 @ 0.74 | −37 @ 0.74 |
| d-post5→d-post6 | −18 @ −0.11 | +120 @ 0.37 RAIL |
| d-post6→d-post7 | +40 @ −0.10 RAIL | −77 @ 0.59 |
| d-post7→d-post8 | −17 @ 0.78 | −17 @ 0.78 |
| d-post8→d-post9 | +40 @ 0.87 RAIL | +54 @ 0.88 |
| d-post9→d-post10 (CRASH) | −40 @ −0.70 RAIL | −120 @ 0.16 RAIL |

SCPS rails: SCPS40 6/11 (hold −40, d2d3/d3d4/d6d7/d8d9 +40,
d9d10 −40); SCPS120 3/11 strict ±120 (hold +120, d5d6 +120,
d9d10 −120).

### R3 lock-QA (marked-crop montage `/tmp/t46-lockqa.png`, T42 method; yellow = ROI box, red = ROI centroid, lime = gradient centroid; zooms `/tmp/t46-zoom.png` for d-post1/d-post2/d-post9)

| Snap | ROI lock | Gradient lock | Named intruder |
|---|---|---|---|
| npre1 | on (legs/board) | on (torso) | none in locks |
| npre2 | on (legs) | on (torso) | none in locks |
| d-post1 | on (hip/legs; 3 px from gradient) | on (hip/legs) | none in locks |
| d-post2 | borderline (~25 px left on open snow) | on (shoulder/arm) | none (near-miss) |
| d-post3 | — (INVALID-flood 13974; centroid on tree, off) | — (INVALID-flood 5490; centroid on torso, gated out by count) | trees left (ROI) |
| d-post4 | — (INVALID-flood 26331; centroid on rider arm, gated out) | — (INVALID-flood 9127; centroid on torso, gated out) | fallen log + dense bark (both) |
| d-post5 | — (INVALID-flood 29866; centroid on rock, off) | — (INVALID 3469; centroid on torso, gated out) | rock wall right (ROI) |
| d-post6 | on (torso) | on (legs) | none in locks (ice glow outside) |
| d-post7 | on | on | none in locks |
| d-post8 | on | on | none in locks (red structure outside) |
| d-post9 | off (~55 px up-right on slope; npix 3621 VALID but excluded) | on (torso) | red-structure pull (ROI) |
| d-post10 | — (INVALID-flood 20585; crash spray) | crash-tainted (VALID 832 on tumbling rider — EXCLUDED) | crash wall + spray |

### R3 VALID-pair deltas (with per-pair lock QA; NO-INPUT cruise — zero inputs after the hold per poll log)

ROI (6 VALID pairs, 4 on→on banked):

| Pair | Δcx/Δcy | Lock QA | SCPS40 / SCPS120 |
|---|---|---|---|
| npre1→npre2 (pre-pair) | +10.0 / −20.4 | on→on | +15 @ 0.66 / +15 @ 0.66 |
| npre2→d-post1 (HOLD) | +11.8 / +22.2 | on→on CLEAN | −40 @ −0.13 RAIL / +120 @ 0.44 RAIL |
| d-post1→d-post2 | −44.1 / −50.3 | on→borderline (tabled, NOT counted) | −19 @ 0.78 / −19 @ 0.78 |
| d-post6→d-post7 | −17.2 / +22.0 | on→on | +40 @ −0.10 RAIL / −77 @ 0.59 |
| d-post7→d-post8 | −2.3 / −18.1 | on→on | −17 @ 0.78 / −17 @ 0.78 |
| d-post8→d-post9 | +55.1 / −44.7 | on→off (tabled, NOT counted) | +40 @ 0.87 RAIL / +54 @ 0.88 |

Gradient (7 VALID pairs, 6 on→on banked, 1 crash-excluded):

| Pair | Δcx/Δcy | Lock QA | SCPS40 / SCPS120 |
|---|---|---|---|
| npre1→npre2 (pre-pair) | +1.5 / +5.3 | on→on | +15 @ 0.66 / +15 @ 0.66 |
| npre2→d-post1 (HOLD) | +9.8 / +19.8 | on→on CLEAN | −40 @ −0.13 RAIL / +120 @ 0.44 RAIL |
| d-post1→d-post2 | −31.0 / −34.7 | on→on (hold-adjacent) | −19 @ 0.78 / −19 @ 0.78 |
| d-post6→d-post7 | −2.4 / +2.0 | on→on | +40 @ −0.10 RAIL / −77 @ 0.59 |
| d-post7→d-post8 | −2.8 / −17.3 | on→on | −17 @ 0.78 / −17 @ 0.78 |
| d-post8→d-post9 | +14.7 / −4.1 | on→on | +40 @ 0.87 RAIL / +54 @ 0.88 |
| d-post9→d-post10 | −17.5 / +47.7 | on→crash-tainted (EXCLUDED — crash inside) | −40 @ −0.70 RAIL / −120 @ 0.16 RAIL |

Cross-tracker agreement: HOLD pair ROI +11.8/+22.2 vs gradient
+9.8/+19.8 (Δ2.0/2.4, tight); pre-pair ROI +10.0/−20.4 vs
gradient +1.5/+5.3 (Δ8.5/25.7, loose — different lock points,
legs vs torso); d6d7 Δ14.8/20.0; d7d8 Δ0.5/0.8 (tight).

### Distributions (HEALTHY APPENDED — crash-free hold banked; variant stays quarantined)

| Distribution | Tracker | Pairs (appended this run in bold) | n |
|---|---|---|---|
| No-input (clean cruise + pre-pair) | ROI | T42 npre1npre2 −0.7/−22.2; T43 d5d6 +2.8/−12.7, d9d10 −4.5/−7.0; **T46 npre1npre2 +10.0/−20.4, d6d7 −17.2/+22.0, d7d8 −2.3/−18.1** | 3 → **6** |
| No-input (clean cruise + pre-pair) | Gradient | T42 +1.8/+4.8, +0.0/+10.6, +2.7/−3.9, −2.1/−4.2; T43 d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7; **T46 npre1npre2 +1.5/+5.3, d1d2 −31.0/−34.7 (hold-adjacent), d6d7 −2.4/+2.0, d7d8 −2.8/−17.3, d8d9 +14.7/−4.1** | 7 → **12** |
| Hold-step | ROI | T42 +11.2/−39.5 (crash inside); **T46 +11.8/+22.2 (CLEAN)**; T43 0 (hold ungated) | 1 crash-confounded → **2 (1 clean)** |
| Hold-step | Gradient | T42 −4.4/−24.1 (crash inside); **T46 +9.8/+19.8 (CLEAN)**; T43 0 (hold ungated) | 1 crash-confounded → **2 (1 clean)** |
| Pre-pair | both | T42+T43 banked in no-input above; **T46 npre1npre2 ROI +10.0/−20.4 / gradient +1.5/+5.3 (clean, 55→51 MPH, no banner)** | stands |

Variant-quarantined (unchanged): ROI no-input n=1 (d9d10
+9.4/+45.7); gradient no-input n=8 (T45 §T45-4, 2
recovery-adjacent); hold n=0; pre-pair n=0. Crash-lottery read:
hold-window crashes now 3/4 runs at this phase (T42 hold-crash,
T43 pre-pair+hold-crash, T45-variant hold-crash, T46 hold CLEAN).

## T46-5. R3 census + trace + forensics

| Item | Value |
|---|---|
| Census | `t46r3-census.txt` (11702 B; lines=41969842, ts_span=0.1236..505.9957; T42 R3: 42967628/0.1271..508.62; T43 R1: 43623520/0.1213..515.92; T45-variant: 41756303/0.1384..500.98 — same class) |
| EE | 11952003 calls, distinct=52 (top: GetThreadId 4958479, WaitSema 2155628, SignalSema 1911865, sceSifGetReg 1260327 — the 1260327 count IDENTICAL to T42/T43/T45) |
| IOP | 18453461 calls, distinct=155 (top: sceSdGetAddr 3714048, QueryIntrContext 3362769, CpuSuspendIntr 3137750, CpuResumeIntr 2117633 — same top-4 as T42/T43/T45) |
| libsd (audio initialized) | sceSdGetAddr top IOP call + `pcsx2-qt` Pulse client on RDPSink (agrees with cubeb proof) |
| MARK | ERROR NONE; Error = `cdvdRead06(Error)` L574864 (also L574864 in T45-variant's census + 1× in T43 R1's — benign class marker, not a run artifact); `Failed to` = patches.zip warning (same as prior runs); VSync = DVD NTSC mode change |
| Samples | `t46r3-samples.txt` (5844 B; source lines=41969842; EE.Bios FIRST 50 from L138603 RFU060) |
| Vblank stream | first `WaitVblankStart` L417043 [1.1810] (T41/T42: L417043 — same line); 397 total, ALL ≤90 (LE90/110/140/350 all 397 — IDENTICAL to T41/T42/T45) |
| UpdateVSyncRate | Mode Changed to DVD NTSC, count 15 |
| Live trace | `emulog.txt` 2682545633 B sha `19c1b583304500581f61db20605befff333d2d262c847a997606cde20364ae84` (R2-variant's preserved via `emulog-pre-t44-20260922T152103Z.txt`) |
| Rotation | T42 R3 + T43 R1 + T44 R1 + T45 R2-variant + live R3 chain on bytesize; all prior rotations untouched |
| SSD stream (SSD MOUNTED) | `/Volumes/Extreme SSD/ps2x-t4/emulog-t46r3.txt` size+sha MATCH (2682545633 B, `19c1b583…ae84`); head/tail 30-line slices committed (`t46r3-emulog-head/tail.txt`, shas `dbd1d5a3…`/`b2579adc…`) |
| Boot logs | `t46r3-boot.log` 4231 B (DIFFERS from R2-variant's — own content) + `t46r3-boot.stdout` 210 B (byte-identical to R2-variant's: same DRI3 warnings + CTRL+C graceful shutdown — deterministic) |
| Previous boot logs (T44 gap) | on-box `logs/boot-t44.*` verified = committed T45 shas (`6e93ff8a…`/`360108bc…`) BEFORE R3 overwrote — nothing lost |
| NVM post-run | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961` FULL sha — UNCHANGED, in committed `t46-nvm-post.txt` (mtime Sep 20 15:20) |
| C: post-run | 277 G avail (280 pre; WSL `/` 898→896 G, ~2 GB trace+rotation drain) |
| Analyze | `t46r3-analyze.txt` (clean log, same-boot H62 run) |
| dmesg post | `t46-dmesg-h62-post.txt` 474 lines, 1 AcceptAsync — BYTE-IDENTICAL to pre (`diff` clean: zero new kernel lines across the run) |
| Eventlog final | `t46-eventlog-final.txt` 63300 B — BYTE-IDENTICAL to pre (`cmp` clean: zero host events during the run) |

Forensics (observed events, tables only — no verdicts): clean
hold (d-post1 27 MPH upright, no contact/banner/RECOVER);
pre-pair clean cruise (55→51 MPH, no banner); textured-bark
ROI/gradient floods d3–d5 (tree/log/rock intruders, gated out);
d-post9 ROI off-lock (VALID 3621, red-structure pull, excluded);
d9d10 wall crash (d-post10 26 MPH tumble + spray + RECOVER —
gradient VALID 832 crash-tainted, excluded); v2a R3-pattern +
game-only census (no modal on WSLg audio); single-boot session
(H62 held throughout, zero restarts).

### R3 snap sizes (61, on-box bytes)

start 51870, a1-now 49894, a1-poll01 58424, a1-pre 58424,
a1-post3 50263, a1-post8 49670, a1-post15 49838, a1-post25 49813,
menupre 50009, mc-post1 70336, mc-post3 70246, mc-post8 70235,
mc-post15 70414, scpre 71244, zc-post1 51305, zc-post3 51311,
zc-post8 51503, ccpre 50968, sp-post1 65236, sp-post3 65237,
sp-post8 65460, sppre 65224, pc-post1 67559, pc-post3 67491,
pc-post8 67563, smpre 67622, rc-post1 69463, rc-post3 69650,
rc-post8 69418, sepre 69642, sj-post1 58984, sj-post3 58974,
sj-post8 58645, mrpre 58884, mr-post1 66912, mr-post3 67247,
mr-post8 54333, mr-post15 60331, mr-post25 60240, mr-post40 59917,
mr-stab1 60192, mr-stab2 59851, pppre 60022, x-post1 68881,
x-post3 67952, x-post8 68179, x-post15 65642, x-post25 62017,
x-post40 67582, npre1 53808, npre2 54444, d-post1 54032,
d-post2 60659, d-post3 64140, d-post4 69796, d-post5 56444,
d-post6 53151, d-post7 50877, d-post8 53095, d-post9 56831,
d-post10 47606.

## T46-6. Exact commands (reproduce-from-scratch)

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
`pactl info` + `pactl list sinks short` (behavioral gate),
dmesg (`wsl dmesg` → local), eventlog (`wevtutil qe System
/c:120 /rd:true /f:text` → local).
Holder (idle-down discipline — WSL stops between ssh sessions):
`ssh bytesize 'wsl sleep 7200'` in managed background for the
whole run; all gate/run/receipt calls join the held boot.
X11: `wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs
/tmp/.X11-unix`. PPM: `wsl python3 t44-cropdiff.py t35-ref-panel.ppm
t35-ref-panel.ppm` → `mean=0.0000 p99=0`.
Previous logs first: on-box `sha256sum logs/boot-t44.*` vs
committed T45 shas (match → R3 overwrite loses nothing).
Run: `ssh bytesize 'wsl bash -c "cd /home/brad/pcsx2-t4 && stdbuf
-oL -eL ./t44-auto.sh"'` (local redirect, managed background;
ZERO env changes — default `PULSE_SERVER`, variant NOT carried) →
local `sleep 35` → `wsl t44-dialogwatch2.sh` (local redirect) →
window census (`DISPLAY=:99 xdotool search --onlyvisible --name
SSX/Error`) → live-trace cubeb grep + `pactl list
sink-inputs/clients` (proof) + user-daemon `pactl list
sink-inputs` (EMPTY — null-sink non-involvement).
Fetch (full set): `wsl cp` 61 JPGs + poll + census + samples +
boot logs → C: → `scp` globs → rename `t44-*` → `t46r3-*`
→ `wsl rm`. Refs: same recipe (9 PPMs, /tmp use, shas verified,
NOT committed).
Post-hoc (local): `/tmp/t46-batch.py` (panel + hops; bit-exact 4/4
vs committed), `t41/t42/t44-track.py` (dense 12),
`/tmp/t46-montage.py` (lock-QA) + `/tmp/t46-zoom.py`-equivalent
(d-post1/2/9 zooms), viewed snaps (dense 12 + 3 chain
anchors), `grep` (press walls, cubeb, census rows).
Trace: `COPYFILE_DISABLE=1 ssh … "wsl cat …/emulog.txt" >
"/Volumes/Extreme SSD/ps2x-t4/emulog-t46r3.txt"` → size+sha
verify + head/tail slices (SSD tier — mounted, preferred).

Gaps (tabled, none load-bearing for the report): d9d10 no-input
pair lost to the wall crash (ROI auto-excluded by flood,
gradient lock-QA-excluded — crash-tainted VALID); d3–d5 pairs
ungated under all trackers (textured-bark floods — non-crash,
speeds rising 32→38); d1d2/d8d9 ROI pairs tabled but uncounted
(borderline/off locks); x-post2–40 HUD per scores only
(x-post1 viewed; chain screens gate-verified); interpolated T+ on
chain snaps (±1 s; scored anchors exact); T45's persisting
`pulseaudio` package + auto-started user daemon remain on the
distro disk (holds zero run audio — receipted EMPTY; WSLg path
proven by pactl 35/35 + cubeb + sink-input).

## T46-7. Tail receipt (truncated tail FAILS the gate)

T46 executed the healthy path end-to-end: audio gate (H62
demand-boot, immediate @up42 + delayed @up151, socket-present +
pactl 35/35 RDPSink — HEALTHY first boot; holder held the boot
for the whole run, zero restarts) + pins (binary/tree/inputs/
NVM/bindings/refs/snaps/trace/space all reproduce; staged shas
5/5 match → T44 scripts reused, no `t46-*` copies) + previous
boot logs verified = committed T45 shas (T44 gap closed by
verification) + R3-HEALTHY (T44_DONE exit 0: TRUE TITLE
first-attempt, ZC parked at +1 s, full chain, XCROSS @T+432.75,
ONE Left hold @T+499.69 ×1036.1 ms, dense 10 @T+501–506; cubeb
negotiated 8/0/0 with a live sink-input on RDPSink; v2a
R3-pattern + game-only census = no modal; user daemon
sink-inputs EMPTY = null-sink non-involvement) + tracking
(control 3/12, ROI 8/12, gradient 9/12; SCPS 3-way 22/22
identical; lock-QA montaged + zoomed: hold on→on CLEAN under
both, pre-pair on→on clean, d9d10 wall crash excluded) +
distributions (HEALTHY APPENDED: ROI floor n=3→6, gradient floor
n=7→12, hold-step n=1→2 with the FIRST CLEAN sample under both
trackers; variant stays quarantined) + trace (2.68 GB + sha MATCH
on SSD tier; NVM FULL sha unchanged in committed file; vcount
397 all ≤90; dmesg/eventlog pre/post byte-identical). Evidence:
`local/research/T46/` (REPORT + 61 R3 JPGs + poll/census/
samples/analyze/stdout/stderr/dialogwatch/boot/emulog-slices +
NVM-post + audiogate/pactl primaries + dmesg ×2 + eventlog
pre/final; no `t46-*` scripts — none needed). Commit `[T46]`
with trailer `Orchestrated-By: Muse Code`, NO PUSH per lane
instruction. END-OF-REPORT.
