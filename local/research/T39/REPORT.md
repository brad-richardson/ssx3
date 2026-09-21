# T39 report — no-hold control run at a matched race phase: dense series with NO input (bytesize, no lease)

Brief: T39 (T38's G1(a): no-hold control). Tables, no verdicts. One boot
ran on bytesize (R1: chain reproduced to live gameplay, sham window with
NO input at a matched race phase, PRE-sham pair + DENSE 10-snap post-sham
series mapped with rider-pixel tracking + T38 refinements); laptop-side
work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T38/REPORT.md` (all of it: R1
reproduced the chain to LIVE gameplay, ONE 1037.3 ms D-pad Left HOLD
@T+504.54 on a live race (pre-pair 00:01:25 2ND/6 40% / 00:01:31 2ND/6 44%),
dense 10-snap post-hold series to 00:02:12 6TH/6 58% with NO separable hold
response — position decays 2ND→6TH distributed post-hold with no
hold-coincident step, RDC gated out 10/12, SCPS120 still rails ±120 on 7/11
hops incl. the no-input pre-pair gap and the hold hop; race clock ~1.4× wall
under turbo; G1 proposes (a) no-hold control, (b) sub-second exposures —
this brief takes option (a)). This brief executes T38's G1(a).

Experiment contract (up front): hypothesis — the position decay, SCPS
rail-class shifts, and RDC validity floods observed in T36 (tap), T37
(tap), and T38 (hold) are the race's own input-free progression, so a
dense 10-snap series with NO input at a matched race phase reproduces the
same behavior class (position volatility, rail rates, gate-out rates);
observable — pre-sham pair = live race (race clock + position/progress HUD
read off the viewed snaps), the sham row (proven no-input 1 s wall gap +
phase match vs T38's hold window), dense 10-snap series + per-snap HUD +
tracking metrics + per-hop whole diffs; screen content read off viewed
snaps; alternatives — control series shows QUAINTLY QUIET behavior (stable
position, resolved SCPS, valid RDC) while input runs did not (→ input
contribution separable after all → table the exact control distribution +
recipe for the discriminating metric), run provably never reached live
gameplay at a matched phase (→ ONE bounded re-attempt allowed); stop —
table the exact observed control distribution + control-vs-input comparison
+ recipe, zero steering inputs, never blind multi-presses.

## T39-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T39; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T39]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H26/H27 before R1):

| Item | T4 value | T39 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Steering binding | — | no steering input issued this session (no binding read needed; sham issues no xdotool) | n/a |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T38 reference snaps present | — | all 12 sizes reproduce T38 §chain (`npre1/2` 64346/56884, `d-post1..10` 54298/58301/58560/65319/66326/60148/54031/62294/56039/59312) | yes |
| Free space | — | WSL `/` 874 G pre; C: 4.5 G pre (100%); laptop `/` 4.3 Gi avail; SSD 281 Gi free | yes |
| Live trace pre-run | — | `emulog.txt` sha `1180c368…73609a3` = T38 R1 (preserved at R1 boot) | yes |

Phase-match targets (tabled BEFORE the run — T38 R1's hold window, match
PHASE not seed; AI lineup/RNG differ run to run):

| Item | T38 hold-window value | T39 sham-window target |
|---|---|---|
| Sham/hold slot | T+504.54 (hold keydown) | ≈T+505 (same script slot) |
| Pre-pair race clocks | 00:01:25 / 00:01:31 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 2ND/6 / 2ND/6 | lead-pack (1ST–3RD/6) |
| Pre-pair progress | 40% / 44% | ≈40–45% (±5 pp) |
| Series span | 10 snaps over +26 s wall / +41 s race | same cadence, same span |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×2 (once on VM-H26, once on VM-H27 after a mid-staging restart — only the H27 mount was live at R1) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t39-{auto,analyze,vcount,cropdiff}.sh/.py`, `t39-{r1-census,samples}.txt` (via analyze), `t39-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t39-*.txt` (rotation chain, see trace table), `boot-t39.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t39*` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | pre-run section below; ZERO in-window (see WSL session log) |

Script receipts (frozen BEFORE the run):

| Item | Value |
|---|---|
| `t39-cropdiff.py` | byte-identical to T38's (`cmp` clean), sha `ac114212…0826a53` |
| `t39-track.py` | byte-identical to T38's (`cmp` clean), sha `58afa004…91c108` (T38's frozen value) |
| `t39-vcount.sh` | byte-identical to T38's (`cmp` clean), sha `105cd092…39107d76` |
| `t39-analyze.sh` | differs only in output names (`t39-census/samples`), sha `f91f9472…e2ab33d` |
| `t39-auto.sh` | T38 copy + T39 renames + sham window (ONLY deliberate change), sha `ac7232db…cdfe3a`; `bash -n` clean |
| Staged shas | all 4 WSL-staged shas match local (auto `ac7232db…`, analyze `f91f9472…`, vcount `105cd092…`, cropdiff `ac114212…`) |
| PPM self-check | panel ref 0.0000/0 pre-run |
| T38 originals | untouched (`git status` clean before staging; T39 dir is new) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 10:05:25–10:06:42 | VM-H25 teardown (T38's post-everything VM, after T38's session) | eventlog-pre (IDs 71/69/233/234/234 @06:06:42) |
| 2 | 10:39:30 ([0] VM-H26) | VM-H26 started fresh ~2 s before first ssh | btime `…170`, eventlog-pre head (IDs 292/67/291/233/232/102/291/102/291/291 @06:39:30) |
| 3 | 10:39:32–10:42:1x | Pre-run checks (all ssh exit 0) + C:-staging + WSL-staging (shas match local) + X11 mount + PPM self-check 0.0000/0, all on VM-H26 | `t39-dmesg-vmH26-pre.txt` (0 AcceptAsync, 440 lines, 23 `Ioctl failed` — captured at uptime ~2 s, before dxg queries) |
| 4 | 10:42:12 | VM-H26 teardown → VM-H27 create (mid-staging restart, NOT by me) | btime `…331`, eventlog-post (create IDs @06:42:12) |
| 5 | 10:42:12–10:42:46 | X11 re-mount + staging re-verify (sha match) + dmesg on VM-H27, no restart between re-mount and R1 (btime re-verified `…331`, uptime 34) | `t39-dmesg-vmH27-pre.txt` (0 AcceptAsync, 441 lines, 23 `Ioctl failed`) |
| 6 | 10:43:01–10:52:23 ([49]→[611] H27) | R1 single-shot exit 0, `T39_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage — kernel quiet after uptime 49.06, no restart in-window; ZERO Volsnap/Hyper-V entries in-window) | exit 0, 61 snaps, trace sha |
| 7 | 10:52:23–~10:56 | R1 dmesg read (IMMEDIATELY after run ssh) + analyze (exit 0) + vcount + all R1 fetches (exit 0) on VM-H27 | `t39-dmesg-vmH27-post.txt` (442 lines, 0 AcceptAsync — full R1-window coverage) |
| 8 | 10:56:03 | VM-H27 teardown (post-everything restart, NOT by me) | eventlog-post head (IDs 71/69/233/234/234 teardown @06:56:03) |
| 9 | 11:02:40–~11:07 (VM-H28) | VM-H28 fresh: identity + dmesg + NVM/trace/preserved-sha re-verifies + trace head/tail slices + SSD stream + df-final (exit 0) | `t39-dmesg-vmH28-post.txt` (448 lines, 1 AcceptAsync [16.98], boot coverage) |
| 10 | event log | Newest-30 reads (pre/post): head moves H26-create 06:39:30 → H27-teardown 06:56:03; boundaries H25-teardown 06:06:42, H26-create 06:39:30, H27-create 06:42:12, H27-teardown 06:56:03, H28-create 07:02:40; in-window (06:43:01–06:52:23 local) entries: ZERO of any kind — userland kills would leave no Windows trace (T17–T38 precedent stands); the nearest entry is a benign Time-Service NTP notice (ID 37) at 06:52:33, +10 s post-window | `t39-eventlog-{pre,post,final}.txt` |
| 11 | dmesg noise | `Ioctl failed` lines 23/23/23/23 across the 4 files (boot/GPU-query noise; this run adds zero new dxg lines — post-R1 file is pre2 +1 hv_balloon line); kill-pattern grep (`killed process\|out of memory\|panic\|oops\|segfault`) matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R1
window (T_BOOT uptime 49 → end 611, all on VM-H27):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t39-dmesg-vmH26-pre.txt` | 440 | 0 | — | earlier VM, pre-window; outside |
| `t39-dmesg-vmH27-pre.txt` | 441 | 0 | — | same VM, pre-window; outside |
| `t39-dmesg-vmH27-post.txt` | 442 | 0 | — | same VM, full R1-window coverage (kernel quiet after uptime 49.06 — last line [49.055765]); ZERO in-window |
| `t39-dmesg-vmH28-post.txt` | 448 | 1 | [16.980290] | different VM (post-everything, no run); outside |

## T39-1. Sham selection + series shape + tracking method (frozen BEFORE the run) + LIVE calibration

Tool: `t39-cropdiff.py` (copy of T38's, byte-identical; `cmp` clean;
`t39-vcount.sh` byte-identical to T38's; `t39-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-check pre-run: panel ref 0.0000/0.

Sham selection (tabled BEFORE the run, per brief — the ONLY deliberate
change vs T38):

| Item | Value |
|---|---|
| Control | NONE (no keydown, no keyup, not even a windowfocus) |
| Window | 1 s wall gap (`sleep 1` between `SHAMSTART_WALL` / `SHAMEND_WALL` stamps) |
| Slot | Same script slot the T38 hold occupied (≈T+505, after the pre-pair) |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (deep in live gameplay per T35's/T36's/T37's/T38's race shape) |

Series-shape choice (tabled BEFORE the run, per brief — pick ONE):

| Option | Shape | Choice |
|---|---|---|
| Dense (T37's/T38's) | 1 s cadence × 10 s post-sham series | CHOSEN — identical shape to T38 so the control distribution compares hop-for-hop (same ~3 s exposure gaps under turbo, same rail exposure) |
| Sparse (T36's) | +1/+3/+8/+15/+25/+40 tail | rejected pre-run (shape must match T38 for a control; span buys nothing) |

Tracking method (tabled BEFORE the run, per brief — frozen in committed
`t39-track.py`, byte-identical to T38's, sha `58afa004…91c108`):

| Metric | Definition (fixed) | Rationale |
|---|---|---|
| RDCX/RDCY | T37-frozen: centroid (0.1 px) of dark pixels (luminance < 80) inside rider ROI x[150,540] y[100,460]. Reports cx/cy/npix/dark-fraction; npix is the validity channel | Rider outfit is near-black against bright snow; a Left carve displaces the rider sprite laterally before the chase cam re-centers |
| RDC gate | VALID iff 200 ≤ npix ≤ 6000 (rider-scale band; T37 calibration: valid snaps npix 1299–3786, mixed 8595–12177, flooded ≥ 18624; T36 npre rider-clean 2462). Gated-out snaps print INVALID and their cx/cy must not be used for deltas | T37 recipe: validity-gated RDC (skip snaps with npix ≫ rider-scale) |
| SCPS40 | T37-frozen: snow column-profile shift (integer lag px in [−40,+40]) between consecutive snaps over x[150,540] of rows y[380,460], normalized xcorr best lag (+ = scene moved right). Reports lag + peak corr; corr is the validity channel | Under a chase cam the world rotates around the rider, so a heading change reads as background lateral shift even when the rider stays centered |
| SCPS120 | Same normalized-xcorr column-profile shift over lag in [−120,+120] (3× the T37 window) | T37 recipe: wider SCPS lag window (motion exceeded ±40 px at ~3 s exposure gaps under turbo — T37/T38 railed nearly every step incl. the no-input pre-pair gap) |

Noise-floor note: in T39 the ENTIRE dense phase is no-input, so every
hop is a noise-floor sample — the pre-pair gap (npre1→npre2), the sham
hop (npre2→d-post1), and all 10 post-sham hops form the control
distribution against which T36's tap, T37's tap, and T38's hold hops are
judged.

LIVE calibration (T36's, reused unchanged; T35 R1 receipts; no new
calibration run — the gate is a proxy, the criterion is HUD-read):

| Leg | T35 R1 receipt | Bar | Margin |
|---|---|---|---|
| Panel→countdown departure hop (pppre→x-post1) | 14.18–14.19 | > 5.0 (DEPARTED) | 2.8× |
| X-snaps vs-panel-ref | 12.98–21.27 | > 5.0 (NONPP) | 2.6× |
| Late-tail motion hops (x-post15→x-post25, x-post25→x-post40) | 11.52, 9.51 | > 5.0 (DEPARTED) | 1.9× |
| All 66 X-pair hops | 7.97–20.23 (never static) | — | static gate cannot fire |

LIVE-LIKE proxy gate (as frozen pre-run): in-script sham criterion =
decisively left the panel (pppre→x-post1 hop > 5.0) AND arrival non-panel
(x-post40 vs-pp > 5.0) AND motion ×2 (x-post15→x-post25, x-post25→x-post40
hops > 5.0). The TRUE live-race criterion — race clock advancing +
position/progress HUD present — is read off VIEWED snaps post-hoc, not
whole-frame scores (T35 G1 gate note: gate on the HUD, not the frame).
Every proxy leg carries ≥1.9× margin on the T35 receipts.

Script deltas vs `t38-auto.sh` (committed originals untouched; `t39-auto.sh`
is the adapted copy):

| Area | T38 script | T39 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + pre-pair + hold + dense d-post1..10 + 11 per-hop whole diffs | identical through the LIVE-LIKE gate; sham phase identical except the input |
| Sham input | ONE `press_hold Left` (1 s `sleep`) | ONE `sham_window` (1 s `sleep`, NO xdotool of any kind) — the ONLY deliberate change; label `SHAM`; pre-pair + dense d-post1..10 + 11 per-hop whole diffs unchanged |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-LIVE-PARK` | unchanged (still clean shutdown + `T39_DONE`, trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
batch port of `t39-cropdiff.py` (`/tmp/t39-batch.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical)
against the committed tool on 4 diverse pairs (same 4-pair protocol as
T38; pairs + scores tabled in §T39-2). Any score reproduces with the
committed `t39-cropdiff.py`, slower. The 9 ref PPMs were reused from
`/tmp/t36-refs/` for post-hoc scoring (all 9 shas re-verified, match
§T39-0).

## T39-2. R1 — race reproduced, sham window (NO input) + dense control series on live gameplay

Run: `t39-auto.sh`, ONE fresh boot, T_BOOT wall 1789987381 (uptime 49,
VM-H27), 10:43:01–10:52:23 UTC (uptime 49→611 = 562 s; 202 s over the
≤6 min guidance — the X phase + dense tail; full dmesg coverage, zero
flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 / T33 R1 / T33 R2 /
T34 R1 / T35 R1 / T36 R1 / T37 R1 / T38 R1), exit 0, `T39_DONE`, clean
SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (chain advanced to the
sham, dense series mapped). No bounded re-attempt run (pre-sham = racing
at a matched phase — re-attempt condition not met, brief stops here).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4329/6 remote / 0.0468/1 PIL (T38 R1: 0.4337/6 / 0.0453/0 — same detector reading, near-identical frame, see xrun) | Cross 536.3 ms @T+98.29 (attract-skip) + Start 535.3 ms @T+101.56 (on title, ≤1.8 s after exposure) | Main Menu by +5 s; menu-like gate (non-title + whole-static 0.0389/0.0167) + post25-vs-menu 0.3002/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R1 cross-run frame identities (T39 R1 vs T38 R1, full sha256)

| Frame | T39 R1 sha | T38 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `6e3d747fd514…` (cp-identical, pair 0.0000/0) 58374 B | `4a9c7cf6b67d…` 58388 B | differ; pair 0.0249/0 max 44 (title snowflake shimmer) |
| a1-post3 | differ | differ | whole pair 0.0403/0 max 51 |
| a1-post8 | differ | differ | whole pair 0.0392/0 max 53 |
| a1-post15 | `4c56f8159c76…` 49634 B | `4c56f8159c76…` 49634 B | BIT-IDENTICAL (`cmp` clean; 5th run — also T35/T36/T37/T38 R1) |
| a1-post25 | `4680fcd0480a…` 49786 B | `4680fcd0480a…` 49786 B | BIT-IDENTICAL (`cmp` clean; newly identical vs T38) |
| menupre | differ | differ | whole pair 0.0021/0 max 13 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.144/3, 0.189/5, 0.147/3, 0.098/2 |
| scpre | differ | differ | whole pair 0.2568/6 |
| zc-post1/3/8 | differ | differ | whole pairs 0.101/1, 0.164/5, 0.146/3 |
| ccpre | differ | differ | whole pair 0.1734/5 |
| sp-post1/3/8 | differ | differ | whole pairs 0.082/1, 0.075/1, 0.002/0 |
| sppre | differ | differ | whole pair 0.1252/1 |
| pc-post1/3/8 | differ | differ | whole pairs 0.048/0, 0.009/0, 0.066/1 |
| smpre | differ | differ | whole pair 0.0108/0 |
| rc-post1/3 | differ | differ | whole pairs 0.0004/0, 0.0043/0 (near-identical; snowflake shimmer breaks bit-equality) |
| rc-post8 | differ | differ | whole pair 0.1126/1 (snowflake shimmer) |
| sepre | differ | differ | whole pair 0.0106/0 |
| sj-post1 | `c03cef15a536…` 58893 B | `c03cef15a536…` 58893 B | BIT-IDENTICAL (`cmp` clean) |
| sj-post3 | differ | differ | whole pair 0.0156/0 max 42 |
| sj-post8 | `0db3d3080272…` 59006 B | `0db3d3080272…` 59006 B | BIT-IDENTICAL (`cmp` clean) |
| mrpre vs T38 `mrpre` | `ef224808715b…` | `6cedfa418439…` | whole pair 0.0077/0 |
| mr-post1 (load) | `de707d1d5ed5…` 66795 B | `7466eb3a972d…` 66766 B | differ; pair 0.5772/17 (both 18% Loading) |
| mr-post3 (load) | `5b524bce2a92…` 67359 B | `7a583908e39d…` 67123 B | differ; pair 1.5300/60 (both 98% Loading) |
| mr-post8 | `84f5ce2e1252…` 54859 B | `48e97cac1997…` 54557 B | differ; pair 4.2642/87 (both race-intro cinematic, different phase/track: Deep End Utah Saints Remix Swollen Members Balance vs Way Away Yellowcard Ocean Ave) |
| mr-post15/25/40 | differ | differ | whole pairs 0.2292/4, 0.2413/4, 0.4301/13 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | differ | differ | whole pairs 0.5478/18, 0.3096/7 (both pre-race panel; lineup differs) |
| pppre vs T38 `pppre` | `7c834e5465a1…` 60157 B | `c8e3c1b2a9c9…` 60067 B | whole pair 0.3013/6; whole-vs-panel-ref 0.1430/2 PIL |
| x-post1 (countdown) | `076eebd03f44…` 69714 B | `9e6da142acbc…` 69253 B | differ; pair 1.3242/44 (both countdown `2` gates — near-frozen) |
| x-post3 | differ | differ | whole pair 2.7826/51 (similar gate exit: 5TH/4TH at 00:00:02, 1%, 39 MPH) |
| x-post8/15/25/40 | differ | differ | whole pairs 11.57/148, 9.29/136, 13.87/143, 9.91/112 (gameplay lottery) |
| npre1/2 | differ | differ | whole pairs 12.82/157, 10.65/150 (gameplay lottery) |
| d-post1..10 | differ | differ | whole pairs 11.43/147, 12.31/121, 16.03/175, 15.16/172, 15.10/127, 13.35/150, 12.38/123, 16.10/172, 11.90/145, 11.80/134 (gameplay lottery) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789987479.294 → 1789987479.830 | 536.3 ms | T+98.29→98.83 | 147→148 | `a1-now` attract (26.4178/161 remote; 26.4193/161 PIL — viewed) | `a1-poll01` TITLE (0.4329/6; 0.0468/1 — viewed) |
| A1 Start (Return) | 1789987482.564 → 1789987483.099 | 535.3 ms | T+101.56→102.09 | 150→151 | `a1-pre` ≡ `a1-poll01` (sha `6e3d747fd514`, TITLE) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1789987521.707 → 1789987522.242 | 535.5 ms | T+140.70→141.24 | 189→190 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2150/106; vs-sc 0.4321/7; titleband 12.5512/164) |
| ZOE Cross (K) | 1789987561.622 → 1789987562.158 | 536.3 ms | T+180.62→181.15 | 229→230 | `scpre` Select Character, Zoe selected (vs-sc 0.6069/9 remote; 0.2621/5 PIL; vs-menu 10.1966/105; vs-title 12.6723/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.2252/100; vs-zc 0.5200/9; titleband 15.9235/128) |
| CONT Cross (K) | 1789987590.291 → 1789987590.828 | 536.6 ms | T+209.29→209.82 | 258→259 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4185/7 remote; 0.1822/4 PIL; vs-sc 7.2779/100; vs-title 15.7993/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.5001/154; vs-sp 0.4058/6; titleband 23.1259/171) |
| PEAK Cross (K) | 1789987619.009 → 1789987619.544 | 535.2 ms | T+238.00→238.54 | 287 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4304/6 remote; 0.0848/0 PIL; vs-zc 9.5279/154; vs-title 23.1279/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.3753/121; vs-sm 0.4155/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789987648.300 → 1789987648.836 | 536.0 ms | T+267.30→267.83 | 316→317 | `smpre` Select Mode, Race highlighted (vs-sm 0.3917/6 remote; 0.0408/0 PIL; se-tag 14.3278/89 remote / 14.1390/88 PIL; vs-sp 5.3514/121; vs-title 26.3170/183 — viewed) | `rc-post1` Select Event (vs-sm 0.8074/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789987679.500 → 1789987680.036 | 535.8 ms | T+298.49→299.03 | 347→348 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4078/6, 0.0373/0; vs-sm 0.8121/11; vs-sp 5.4519/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6628/143; vs-mr 0.4297/7; titleband 9.8238/136) |
| ENTER Cross (K) | 1789987708.116 → 1789987708.652 | 536.4 ms | T+327.11→327.65 | 376 | `mrpre` My Rules, Continue highlighted (vs-mr 0.4001/7 remote; 0.0800/0 PIL; vs-se 10.6337/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 18% (vs-mr 12.4898/148; vs-pp 21.0617/169; titleband 17.2808/168 — viewed) |
| XCROSS (K) | 1789987813.430 → 1789987813.966 | 536.6 ms | T+432.42→432.96 | 481→482 | `pppre` pre-race panel, X Continue (vs-pp 0.4488/6 remote; 0.1430/2 PIL — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.3264/153; titleband 19.7214/176 — viewed) |
| SHAM (no key) | 1789987885.621 → 1789987886.625 (SHAMSTART→SHAMEND, NO xdotool) | 1003.7 ms gap | T+504.62→505.62 | 553→554 | `npre2` live race 00:01:29 4TH/6 38% (vs-pp 13.0214/125 remote; 13.0023/125 PIL; vs-title 27.8581/177 — viewed) | `d-post1` live race 00:01:35 4TH/6 40% (vs-pp 17.6005/152; titleband 24.1689/135 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.8 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.6 s; MenuCross-keyup →
ZoeCross-keydown 39.4 s; ZoeCross-keyup → ContCross-keydown 28.1 s;
ContCross-keyup → PeakCross-keydown 28.2 s; PeakCross-keyup →
RaceCross-keydown 28.8 s; RaceCross-keyup → SnowJamCross-keydown 30.7 s;
SnowJamCross-keyup → EnterCross-keydown 28.1 s; EnterCross-keyup →
XCross-keydown 104.8 s (panel settling + PP gate); XCross-keyup →
Sham-start 71.7 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 56779B / `144478da32a8` | 36.0713/191 | 20.1115/172 | 18.5225/164 | 19.6796/158 | 15.8333/164 | 16.0201/166 | 16.1181/166 | 17.3356/144 | 10.7183/136 | 67.8656/172 | Attract |
| a1-now (T+97, pre-Cross) | 57983B / `1ef0f86b628e` | 26.4193/161 | 16.8327/184 | 16.2913/154 | 17.2187/167 | 15.8657/158 | 15.6733/153 | 15.7391/155 | 15.7466/147 | 13.4396/139 | 94.9251/220 | Attract (viewed) |
| a1-poll01 (T+100, pre-Start) | 58374B / `6e3d747fd514` | 0.0468/1 T | 14.1347/151 | 11.3076/152 | 12.2567/146 | 15.3703/156 | 16.1499/158 | 16.2477/160 | 9.7681/142 | 22.1508/183 | 106.6172/205 | TITLE (viewed) |
| a1-pre (T+100) | 58374B / `6e3d747fd514` | 0.0468/1 | 14.1347/151 | 11.3076/152 | 12.2567/146 | 15.3703/156 | 16.1499/158 | 16.2477/160 | 9.7681/142 | 22.1508/183 | 106.6172/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 50085B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | 10.1367/105 | 6.9271/93 | 10.4114/170 | 10.9394/177 | 10.9548/177 | 10.1028/96 | 19.3220/178 | 26.1710/106 | Main Menu (viewed) |
| a1-post8 (T+110) | 50006B / `88ae592f89f5` | 16.2984/139 | 0.0678/1 | 10.1178/105 | 6.9227/93 | 10.3936/170 | 10.9196/177 | 10.9446/177 | 10.0933/96 | 19.3354/178 | 26.1728/106 | Main Menu |
| a1-post15 (T+118) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu (bit-identical to T35/T36/T37/T38 R1) |
| a1-post25 (T+129) | 49786B / `4680fcd0480a` | 16.2622/138 | 0.0451/0 | 10.1195/105 | 6.9113/93 | 10.3911/170 | 10.9242/177 | 10.9320/177 | 10.0871/96 | 19.3018/178 | 26.1708/106 | Main Menu (bit-identical to T38 R1) |
| menupre (T+139, pre-MCross) | 49618B / `9543989c151e` | 16.2622/138 | 0.0276/0 | 10.1076/105 | 6.9078/93 | 10.3848/170 | 10.9177/177 | 10.9427/177 | 10.0751/96 | 19.2994/178 | 26.1473/106 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70264B / `b6201cb70fb0` | 12.4795/163 | 10.1467/105 | 0.0709/1 | 7.2467/101 | 11.3763/158 | 11.8436/158 | 11.9124/158 | 5.6424/117 | 19.4451/172 | 26.5701/90 | Select Character, Zoe |
| mc-post3 (T+146) | 70525B / `09ca73293af6` | 12.4827/163 | 10.1603/107 | 0.0849/1 | 7.2651/100 | 11.4029/158 | 11.8678/157 | 11.9364/157 | 5.6644/117 | 19.4711/172 | 26.5700/90 | Select Character |
| mc-post8 (T+154) | 70313B / `88dc3f55b2cc` | 12.4587/163 | 10.1460/105 | 0.2590/5 | 7.2161/100 | 11.3567/158 | 11.8206/157 | 11.8961/157 | 5.6295/117 | 19.4419/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 69999B / `0cd8f03e7528` | 12.4587/163 | 10.1276/105 | 0.0720/1 | 7.2157/100 | 11.3487/158 | 11.8126/157 | 11.8816/157 | 5.6117/117 | 19.4162/172 | 26.6090/90 | Select Character |
| scpre (T+177, pre-ZCross) | 70172B / `fe8abaf28701` | 12.5949/163 | 10.1285/105 | 0.2621/5 | 7.2290/100 | 11.3395/158 | 11.8196/157 | 11.8912/157 | 5.6276/117 | 19.4526/172 | 26.5695/90 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51477B / `5b60671ad1d8` | 15.9006/129 | 6.9275/93 | 7.1969/100 | 0.2881/7 | 9.3648/153 | 10.1328/164 | 10.2439/164 | 7.0454/103 | 20.1883/164 | 15.2998/91 | Setup Character, Zoe |
| zc-post3 (T+186) | 51639B / `9fee6e64f72b` | 15.7979/128 | 6.9114/92 | 7.2689/101 | 0.2411/6 | 9.3480/153 | 10.1093/165 | 10.2220/165 | 7.0492/103 | 20.1859/164 | 15.3155/91 | Setup Character |
| zc-post8 (T+194) | 51209B / `05166783810a` | 15.8302/128 | 6.9262/92 | 7.1046/100 | 0.2433/6 | 9.3737/153 | 10.1265/164 | 10.2358/164 | 7.0808/103 | 20.1580/164 | 15.3228/91 | Setup Character |
| ccpre (T+206, pre-ContCross) | 51452B / `f6e18735adb6` | 15.7837/128 | 6.8971/93 | 7.2520/100 | 0.1822/4 | 9.3475/153 | 10.0997/164 | 10.2134/165 | 7.0457/103 | 20.1742/165 | 15.3195/91 | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+210) | 65460B / `7f2ae25e5640` | 23.1244/171 | 10.4592/170 | 11.3825/158 | 9.4198/153 | 0.0631/0 | 5.2405/121 | 5.3670/122 | 9.8460/138 | 16.5962/158 | 14.0027/89 | Select Peak, Peak 1 |
| sp-post3 (T+215) | 65481B / `b5d6cec1ce56` | 23.1259/171 | 10.4395/170 | 11.3796/158 | 9.3878/153 | 0.0494/0 | 5.2495/121 | 5.3339/121 | 9.8695/138 | 16.5780/157 | 14.0026/89 | Select Peak |
| sp-post8 (T+223) | 65238B / `7ecfbf7f0e6a` | 23.1233/171 | 10.4069/170 | 11.3495/158 | 9.3721/153 | 0.0054/0 | 5.2082/121 | 5.3108/121 | 9.8364/138 | 16.5437/157 | 14.0026/89 | Select Peak |
| sppre (T+235, pre-PeakCross) | 65741B / `26807a3a8024` | 23.1259/171 | 10.4817/170 | 11.4269/158 | 9.4497/153 | 0.0848/0 | 5.2867/121 | 5.3828/121 | 9.9148/138 | 16.5620/157 | 14.0026/89 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+239) | 67682B / `f5de86862c6e` | 26.3046/183 | 10.9391/178 | 11.8257/157 | 10.1256/164 | 5.2088/121 | 0.0673/0 | 0.5297/10 | 10.4858/143 | 16.4244/160 | 14.1509/88 | Select Mode, Race |
| pc-post3 (T+244) | 67446B / `b183a68e3e37` | 26.3046/183 | 10.9142/178 | 11.8034/157 | 10.1009/164 | 5.1814/121 | 0.0400/0 | 0.5115/9 | 10.4628/143 | 16.4133/160 | 14.1472/88 | Select Mode |
| pc-post8 (T+251) | 67675B / `b29efe3b1385` | 26.3335/183 | 10.9468/178 | 11.8147/157 | 10.1304/164 | 5.2167/121 | 0.0634/1 | 0.5458/12 | 10.4516/143 | 16.4459/161 | 14.1686/88 | Select Mode |
| smpre (T+264, pre-RaceCross) | 67471B / `761b0593af9f` | 26.3046/183 | 10.9146/178 | 11.8047/157 | 10.1032/164 | 5.1822/121 | 0.0408/0 | 0.5123/9 | 10.4660/143 | 16.4142/160 | 14.1390/88 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+268) | 69432B / `d86c39d523f9` | 26.1964/183 | 10.9382/178 | 11.8584/157 | 10.2158/164 | 5.2819/121 | 0.5095/9 | 0.0312/0 | 10.5897/144 | 16.4267/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+273) | 69450B / `b0fbcf1c124d` | 26.1994/183 | 10.9402/178 | 11.8582/157 | 10.2159/164 | 5.2825/121 | 0.5130/9 | 0.0347/0 | 10.5896/144 | 16.4271/160 | 0.0094/0 | Select Event |
| rc-post8 (T+280) | 69757B / `ac52d55f7252` | 26.1964/183 | 10.9707/178 | 11.8911/157 | 10.2498/164 | 5.3196/121 | 0.5467/12 | 0.0703/0 | 10.6210/144 | 16.4378/160 | 0.0094/0 | Select Event |
| sepre (T+294, pre-SnowJamCross) | 69541B / `68bd6a67b190` | 26.1964/183 | 10.9436/178 | 11.8638/157 | 10.2210/164 | 5.2880/121 | 0.5156/10 | 0.0373/0 | 10.5950/144 | 16.4321/160 | 0.0094/0 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+300) | 58893B / `c03cef15a536` | 9.7989/135 | 10.1065/96 | 5.6283/117 | 7.0700/104 | 9.8474/137 | 10.4564/143 | 10.6203/143 | 0.1129/1 | 19.5572/153 | 26.4126/92 | My Rules, Continue (bit-identical to T38 R1) |
| sj-post3 (T+304) | 58515B / `6bb4e3c8924b` | 9.8145/135 | 10.0857/96 | 5.6138/117 | 7.0547/104 | 9.8219/137 | 10.4310/143 | 10.5944/143 | 0.0867/1 | 19.5301/152 | 26.4816/92 | My Rules |
| sj-post8 (T+312) | 59006B / `0db3d3080272` | 9.8162/135 | 10.1056/98 | 5.6532/117 | 7.0847/104 | 9.8677/137 | 10.4769/143 | 10.6408/143 | 0.1460/2 | 19.5867/153 | 26.4136/92 | My Rules (bit-identical to T38 R1) |
| mrpre (T+324, pre-EnterCross) | 58502B / `ef224808715b` | 9.8145/135 | 10.0798/96 | 5.6084/117 | 7.0490/104 | 9.8166/137 | 10.4257/143 | 10.5897/143 | 0.0800/0 | 19.5253/152 | 26.4129/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+328) | 66795B / `de707d1d5ed5` | 17.2333/167 | 15.2283/157 | 14.2067/157 | 13.6711/152 | 14.7146/153 | 15.0815/152 | 15.2094/153 | 12.4617/148 | 21.0504/169 | 83.2100/222 | Loading 18% (viewed) |
| mr-post3 (T+333) | 67359B / `5b524bce2a92` | 17.5930/170 | 15.2502/157 | 14.1898/157 | 13.6726/152 | 14.7263/153 | 15.0955/152 | 15.2227/153 | 12.4348/147 | 20.9991/168 | 76.7401/216 | Loading 98% (viewed) |
| mr-post8 (T+340) | 54859B / `84f5ce2e1252` | 28.3364/237 | 21.2175/218 | 20.7598/200 | 20.9520/191 | 20.5850/218 | 21.2995/218 | 21.2013/218 | 20.1952/197 | 19.3328/190 | 45.3828/162 | Race intro cinematic, nightclub, EA RADIO BIG / Deep End / Utah Saints Remix / Swollen Members / Balance (viewed) |
| mr-post15 (T+350) | 60179B / `52398f9ce7aa` | 34.5135/184 | 19.3165/178 | 19.4116/172 | 20.1662/164 | 16.5379/157 | 16.4294/160 | 16.4279/160 | 19.5807/153 | 0.1425/2 | 50.7398/131 | Pre-race panel |
| mr-post25 (T+363) | 60222B / `bdd4fea7d726` | 34.5123/184 | 19.3851/178 | 19.4732/172 | 20.2354/164 | 16.5935/157 | 16.4869/161 | 16.4853/160 | 19.6484/153 | 0.1801/3 | 50.7398/131 | Pre-race panel |
| mr-post40 (T+381) | 60071B / `28c6b52d3a85` | 34.5157/184 | 19.2453/178 | 19.3500/172 | 20.1015/164 | 16.4956/157 | 16.3661/160 | 16.3648/160 | 19.5186/153 | 0.2134/5 | 50.7398/131 | Pre-race panel |
| mr-stab1 (T+404) | 59732B / `6e0a2d4ce497` | 34.5184/184 | 18.9980/177 | 19.1320/172 | 19.8691/162 | 16.3542/157 | 16.1646/159 | 16.1638/159 | 19.2949/153 | 0.4754/18 | 50.7398/131 | Pre-race panel |
| mr-stab2 (T+417) | 60267B / `18d0340cf409` | 34.5191/184 | 19.3901/179 | 19.4772/172 | 20.2385/164 | 16.5946/157 | 16.4910/161 | 16.4894/160 | 19.6524/153 | 0.1812/4 | 50.7398/131 | Pre-race panel |
| pppre (T+429, pre-XCross) | 60157B / `7c834e5465a1` | 34.5102/184 | 19.3190/178 | 19.4141/172 | 20.1655/164 | 16.5354/157 | 16.4363/160 | 16.4349/160 | 19.5802/153 | 0.1430/2 | 50.7398/131 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+433) | 69714B / `076eebd03f44` | 19.7177/175 | 16.1911/165 | 14.1057/137 | 16.0357/154 | 15.7618/156 | 15.8448/157 | 15.9208/158 | 13.5883/131 | 14.2790/153 | 93.2604/175 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+437) | 68085B / `52c7b3e76826` | 21.7366/143 | 12.9046/144 | 12.6262/130 | 12.0795/135 | 12.1485/136 | 12.0576/137 | 12.1382/137 | 11.4895/112 | 16.2623/145 | 31.0237/119 | 5TH/6, 00:00:02, 1%, 39 MPH (viewed) |
| x-post8 (T+444) | 68371B / `6ad08a34b07b` | 12.5829/121 | 16.0965/144 | 13.0640/144 | 14.1435/154 | 15.3706/157 | 16.2137/156 | 16.3497/158 | 11.4568/116 | 21.1609/165 | 95.7122/181 | 5TH/6, 00:00:10, 5%, 51 MPH (viewed) |
| x-post15 (T+453) | 63871B / `69d5ddcf528a` | 15.8039/140 | 21.2267/172 | 16.6924/163 | 18.3216/167 | 19.7141/175 | 20.2315/176 | 20.3357/178 | 15.4181/134 | 25.0502/182 | 124.8909/211 | 3RD/6, 00:00:23, 11%, 51 MPH (viewed) |
| x-post25 (T+465) | 68572B / `dc93778c0bf4` | 12.2270/166 | 16.8707/137 | 13.9503/145 | 15.9517/139 | 18.1485/162 | 18.6170/158 | 18.6970/160 | 13.4126/129 | 22.4441/187 | 117.7281/205 | 1ST/6, 00:00:39, 21%, 50 MPH, 410 pts (viewed) |
| x-post40 (T+481) | 72684B / `8d2c38db4239` | 10.4604/116 | 14.2053/133 | 11.7154/134 | 13.1115/130 | 15.5907/156 | 16.0986/160 | 16.2156/161 | 10.4365/122 | 18.9326/162 | 86.3392/166 | 3RD/6, 00:01:01, 27%, 45 MPH, 410 pts (viewed) |
| npre1 (T+498, pre-sham pair) | 49082B / `ec1ca6fcc162` | 23.9156/161 | 17.7447/156 | 16.5113/165 | 15.8381/162 | 18.2648/173 | 18.2890/174 | 18.4155/175 | 15.1895/151 | 26.1992/181 | 96.9431/177 | 4TH/6, 00:01:24, 36%, 64 MPH, 1520 pts (viewed) |
| npre2 (T+502, pre-sham) | 62601B / `f74c876a80bf` | 27.8207/177 | 15.0881/174 | 15.3876/133 | 15.2726/156 | 14.2481/164 | 14.2628/166 | 14.3330/166 | 15.0404/121 | 13.0023/125 | 32.3488/110 | 4TH/6, 00:01:29, 38%, 67 MPH, 1520 pts (viewed) |
| d-post1 (T+506) | 58956B / `17a62a2f60ab` | 24.1791/135 | 18.9373/160 | 16.2380/145 | 15.9870/147 | 15.7219/158 | 16.4886/163 | 16.5844/163 | 15.0167/132 | 17.5771/152 | 51.5565/164 | 4TH/6, 00:01:35, 40%, 30 MPH, 1520 pts (viewed) |
| d-post2 (T+509) | 49671B / `af52bf979a73` | 17.4746/109 | 12.0102/145 | 12.7191/122 | 12.1256/119 | 12.9454/142 | 13.3875/146 | 13.4329/146 | 11.9020/110 | 13.5463/113 | 26.3452/106 | 5TH/6, 00:01:39, 42%, 57 MPH, 1520 pts (viewed) |
| d-post3 (T+512) | 61062B / `bfed1ad7f187` | 18.9160/142 | 12.1735/142 | 12.9520/119 | 12.0112/131 | 12.9122/135 | 12.8003/129 | 12.8315/129 | 11.4409/103 | 16.1209/142 | 44.1285/125 | 4TH/6, 00:01:43, 44%, 27 MPH, 1520 pts (viewed) |
| d-post4 (T+515) | 61678B / `68e318caf4c3` | 21.1001/129 | 17.1378/175 | 15.1854/140 | 14.8241/155 | 15.4195/160 | 15.8123/162 | 15.9031/162 | 13.6149/132 | 18.8678/162 | 49.5817/129 | 4TH/6, 00:01:47, 47%, 44 MPH, 1520 pts (viewed) |
| d-post5 (T+518) | 54200B / `ef09f01c760d` | 19.0752/108 | 13.7434/124 | 11.8871/123 | 11.3184/114 | 12.6568/127 | 13.1042/128 | 13.2050/129 | 10.4801/105 | 16.1723/122 | 42.5832/122 | 4TH/6, 00:01:51, 49%, 49 MPH, 1520 pts (viewed) |
| d-post6 (T+521) | 60878B / `496a3444809a` | 21.7671/152 | 13.7613/144 | 15.4004/163 | 14.4029/135 | 16.2775/158 | 15.5024/148 | 15.5435/148 | 15.7395/145 | 16.5915/160 | 25.4037/97 | 5TH/6, 00:01:54, 50%, 30 MPH, 1520 pts + 400 popup (viewed) |
| d-post7 (T+523) | 59677B / `b9edb699f821` | 12.7485/106 | 13.5113/108 | 11.2718/128 | 11.0205/115 | 14.7059/140 | 14.9944/142 | 15.0747/144 | 9.7384/105 | 20.0976/147 | 83.3617/166 | 5TH/6, 00:01:58, 52%, 51 MPH, 3590 pts, FS Rail (viewed) |
| d-post8 (T+526) | 56302B / `a10f473d599f` | 19.6070/110 | 15.2312/134 | 14.6272/132 | 14.2298/135 | 15.2404/133 | 15.6554/137 | 15.6735/137 | 13.7541/130 | 13.5434/120 | 42.0259/121 | 6TH/6, 00:02:01, 53%, 47 MPH, 3590 pts (viewed) |
| d-post9 (T+529) | 70901B / `95ec491d2dbb` | 19.7691/157 | 17.9785/167 | 14.8816/153 | 16.2700/158 | 16.4596/167 | 16.9392/168 | 17.0770/170 | 13.5733/131 | 20.9248/166 | 110.5706/206 | 6TH/6, 00:02:05, 54%, 39 MPH, 3590 pts (viewed) |
| d-post10 (T+532) | 53087B / `4d3d507250bc` | 19.4257/171 | 16.5272/150 | 15.7256/126 | 16.2194/131 | 15.4920/152 | 16.1786/159 | 16.2674/159 | 14.5431/117 | 12.8086/130 | 71.9305/152 | 6TH/6, 00:02:10, 55%, 11 MPH, 3590 pts (viewed) |

In-script (remote) vs PIL agreement: ≤0.06 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. npre2 band 27.8581 vs
27.8207; npre2 vs-pp 13.0214 vs 13.0023; d-post1 band 24.1689 vs 24.1791);
the known ~5–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.4001/7 remote vs 0.0800/0 PIL ≈ 5×; sepre vs-se 0.4078/6
vs 0.0373/0 ≈ 11× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR / T35 / T36 / T37 / T38 precedent); hops ≤0.05
(max Δ 0.033 on npre1→npre2 20.5945 vs 20.6163; dense hops ≤0.03).
Vs-panel remote receipt reads 0.45–0.77/p99 6–18 on panel-side PIL
0.14–0.48 (≈2.0–3.4× inflation at the ~0.2 scale — T35/T36/T37/T38 receipt
re-confirmed), so the < 2.0 whole bar holds even remotely (worst
remote 0.7660, 2.6× margin). The TAG crop gap re-confirmed at ~280×
(2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated
in PIL transfer to remote with single-digit inflation near zero and ~1×
at scale ≥5; text-dense crops need remote receipts or generous bars.

Batch-scorer bit-exact validation (committed `t39-cropdiff.py` vs numpy
batch port, mean/p99/max/npix identical 4/4): panel-panel
(`mr-stab2`→`pppre`) 0.1010/4/103; gameplay-motion (`d-post1`→`d-post2`)
11.5010/102/246; title-vs-ref (`a1-poll01`) 0.0468/1/31; SE-vs-ref
(`sepre`) 0.0373/0/45.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1197 | 10.1263/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1085 | 0.1358/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2982 | 0.3235/8 | same screen |
| post8 → post15 (mc) | 0.2224 | 0.2444/5 | same screen |
| post15 → scpre (park span) | — | 0.2473/4 | same screen |
| scpre → zc-post1 | 7.2416 | 7.2642/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.3042 | 0.3275/9 | arrival settling |
| post3 → post8 (zc) | 0.2956 | 0.3162/7 | same screen |
| post8 → ccpre (park span) | — | 0.2911/7 | same screen |
| ccpre → sp-post1 | 9.3520 | 9.3878/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0979 | 0.1060/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0427 | 0.0476/0 | same screen |
| post8 → sppre (park span) | — | 0.0825/0 | same screen |
| sppre → pc-post1 | 5.2460 | 5.2703/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0352 | 0.0381/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0420 | 0.0487/0 | same screen |
| post8 → smpre (park span) | — | 0.0494/0 | same screen |
| smpre → rc-post1 | 0.4560 | 0.4814/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0022 | 0.0035/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0381 | 0.0428/0 | same screen |
| post8 → sepre (park span) | — | 0.0426/0 | same screen |
| sepre → sj-post1 | 10.5789 | 10.6023/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0523 | 0.0565/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0817 | 0.0885/0 | same screen |
| post8 → mrpre (park span) | — | 0.0822/0 | same screen |
| mrpre → mr-post1 | 12.4585 | 12.4208/148 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.1515 | 1.1747/45 | loading progress 18% → 98% |
| post3 → post8 (mr) | 25.1805 | 25.1952/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 19.3254 | 19.3148/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.0874 | 0.0935/3 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.1649 | 0.1688/7 | same screen |
| post40 → stab1 (mr) | 0.2764 | 0.2840/13 | same screen |
| stab1 → stab2 (mr) | 0.4323 | 0.4365/20 | same screen |
| stab2 → pppre (park span) | — | 0.1010/4 | same screen |
| pppre → x-post1 | 14.2972 | 14.2805/153 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 13.9107 | 13.8992/133 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 13.9607 | 14.0032/127 | live gameplay motion |
| post8 → post15 (x) | 9.6800 | 9.7225/134 | live gameplay motion |
| post15 → post25 (x) | 11.4305 | 11.4651/162 | live gameplay motion |
| post25 → post40 (x) | 11.2629 | 11.2905/139 | live gameplay motion |
| post40 → npre1 (span) | — | 15.5917/160 | live gameplay motion |
| npre1 → npre2 | 20.5945 | 20.6163/179 | live gameplay motion (PRE-sham pair, NO input between) |
| npre2 → d-post1 | 12.2181 | 12.2130/143 | live gameplay motion (sham window lands inside this hop; NO input) |
| d1 → d2 | 11.4983 | 11.5010/102 | live gameplay motion |
| d2 → d3 | 9.0483 | 9.0679/105 | live gameplay motion |
| d3 → d4 | 10.8402 | 10.8491/144 | live gameplay motion |
| d4 → d5 | 8.5642 | 8.5766/122 | live gameplay motion |
| d5 → d6 | 13.7544 | 13.7716/124 | live gameplay motion |
| d6 → d7 | 16.5086 | 16.5191/147 | live gameplay motion |
| d7 → d8 | 13.5048 | 13.4971/159 | live gameplay motion |
| d8 → d9 | 16.9794 | 16.9465/159 | live gameplay motion |
| d9 → d10 | 14.3680 | 14.3564/150 | live gameplay motion |

### R1 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t39r1-mr-post1.jpg` @T+328 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 18% Loading…; `mr-post3` @T+333: same screen, 98% Loading…; `mr-post8` @T+340: race intro cinematic, nightclub (`EA RADIO BIG / Deep End / Utah Saints Remix / Swollen Members / Balance` overlay, `Press X to skip`); `mr-post15` @T+350: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+350→T+429 (79 s) |
| Whole-frame pairwise (PIL) | 0.0226–0.4365/p99 ≤20 across all 15 pairs (panel shimmer/animation; min post15–pppre 0.0226/0, max stab1–stab2 0.4365/20; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.14–0.48/p99 2–18 across all 6 (all under the 2.0 gate; margins 4.2–14.0×) |
| Vs-MR (whole) | 19.29–19.65/p99 153 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.16–16.49/p99 159–161 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.16–16.49/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.35–16.59/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.87–20.24/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.13–19.48/p99 172–179 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.00–19.39/p99 177–179 across all 6 (not menu) |
| Vs-title (band) | 34.51–34.52/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 50.7398/131 identical across all 6 (tagline band static within run; T38's run read 49.4844/132, T37's 48.2320/132, T36's 48.5186/132, T35's 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Marisol / Viggo / Nate / Allegra / Moby` (AI lineup differs run to run — T38: `Zoe/Seeiah/Elise/Viggo/Kaori/Moby`, T37: `Zoe/Viggo/Eddie/Allegra/Kaori/Nate`, T36: `Zoe/Moby/Nate/Luther/Griff/Marty`, T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 79 s (all 6 snaps pre-race panel) |

### R1 arrival (countdown → live gameplay; input-free throughout)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+433, +0.0 s after XCROSS keyup) | 00:00:00 | gates | 0% | 0 MPH | 0 | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+437) | 00:00:02 | 5TH/6 | 1% | 39 MPH | 0 | leaving the gate, start straight, gondola |
| x-post8 (T+444) | 00:00:10 | 5TH/6 | 5% | 51 MPH | 0 | open slope, jump ramp ahead |
| x-post15 (T+453) | 00:00:23 | 3RD/6 | 11% | 51 MPH | 0 | banked turn, chevron fence |
| x-post25 (T+465) | 00:00:39 | 1ST/6 | 21% | 50 MPH | 410 | groomed run, `OUT OF BOUNDS` banner at edge, SSX arch |
| x-post40 (T+481) | 00:01:01 | 3RD/6 | 27% | 45 MPH | 410 | rail grind along blue rail, forest |

Race-clock vs wall-clock (wall since XCROSS keyup 1789987813.966; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.0 | 0 | — (countdown) |
| x-post3 | 4.0 | 2 | 0.50 |
| x-post8 | 11.0 | 10 | 0.91 |
| x-post15 | 20.0 | 23 | 1.15 |
| x-post25 | 32.0 | 39 | 1.22 |
| x-post40 | 48.0 | 61 | 1.27 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 9.53–18.08/p99 ≤182 (live gameplay motion; min
x-post8–x-post40 9.5275/126, max x-post3–x-post15 18.0840/163; JPEG shas
distinct). Vs-panel-ref 14.28–25.05 across all 6 (decisively non-panel);
vs-MR 10.44–15.42 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R1 sham (NO input on live gameplay + dense control series + tracking)

Sham row (proven no-input gap / phase match / delivery):

| Item | Value |
|---|---|
| Control | NONE — `sham_window` issues no `keydown`, no `keyup`, not even a `windowfocus` (poll log lines 145–146 are pure wall stamps; `grep -c keydown` on the dense-phase script path = 0 by construction) |
| SHAMSTART wall | 1789987885.621424303 (T+504.62, uptime 553) |
| SHAMEND wall | 1789987886.625135629 (T+505.62, uptime 554) |
| Gap duration | 1003.7 ms (same 1 s wall slot the T38 hold occupied; T38's hold: 1037.3 ms incl. ~37 ms xdotool overhead) |
| Pre-sham pair | `npre1` @T+498 (6.6 s before SHAMSTART) + `npre2` @T+502 (2.6 s before SHAMSTART), NO input between |
| Last input before sham | XCROSS keyup @T+432.96 — 71.7 s of input-free racing before SHAMSTART |

Phase match (sham window vs T38's hold window — match PHASE, not seed):

| Item | T38 hold window | T39 sham window | Δ |
|---|---|---|---|
| Slot | T+504.54 (hold keydown) | T+504.62 (SHAMSTART) | +0.08 s |
| Pre-pair race clocks | 00:01:25 / 00:01:31 | 00:01:24 / 00:01:29 | −1 s / −2 s |
| Pre-pair positions | 2ND/6 / 2ND/6 | 4TH/6 / 4TH/6 | mid-pack vs lead-pack (AI lineup/RNG differ run to run) |
| Pre-pair progress | 40% / 44% | 36% / 38% | −4 pp / −6 pp |
| Series span | 10 snaps, +26 s wall / +41 s race | 10 snaps, +26 s wall / +41 s race | identical span |

Pre-sham HUD (read off the viewed `npre1`/`npre2` snaps):

| Item | npre1 | npre2 |
|---|---|---|
| Race clock | 00:01:24 | 00:01:29 |
| Position | 4TH/6 | 4TH/6 |
| Progress | 36% | 38% |
| Speed | 64 MPH | 67 MPH |
| Score | 1520 pts | 1520 pts |
| Scene | Airborne off jump, snowy peaks, sun glare | Forest section, two riders, groomed run |

Dense post-sham HUD series (read off viewed snaps; wall since sham
end 1789987886.625; race advanced = race clock minus npre2 89 s; wall
span = exposure wall minus npre2 wall 1789987883; nominal 1 s cadence =
`sleep 1` + ~2 s in-script scoring per snap):

| Snap (wall T+) | Wall + | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre1 (T+498) | −7.6 s (pre) | 00:01:24 (−5) | 4TH/6 | 36% | 64 MPH | 1520 | pre-sham baseline, airborne |
| npre2 (T+502) | −3.6 s (pre) | 00:01:29 (+0) | 4TH/6 | 38% | 67 MPH | 1520 | pre-sham baseline, forest |
| d-post1 (T+506) | +0.4 s | 00:01:35 (+6) | 4TH/6 | 40% | 30 MPH | 1520 | carving by tree, ice rail |
| d-post2 (T+509) | +3.4 s | 00:01:39 (+10) | 5TH/6 | 42% | 57 MPH | 1520 | open blue slope, rider mid-distance |
| d-post3 (T+512) | +6.4 s | 00:01:43 (+14) | 4TH/6 | 44% | 27 MPH | 1520 | forest rail/log section |
| d-post4 (T+515) | +9.4 s | 00:01:47 (+18) | 4TH/6 | 47% | 44 MPH | 1520 | icy banked turn, chevron post |
| d-post5 (T+518) | +12.4 s | 00:01:51 (+22) | 4TH/6 | 49% | 49 MPH | 1520 | open groomed slope, chevron banners |
| d-post6 (T+521) | +15.4 s | 00:01:54 (+25) | 5TH/6 | 50% | 30 MPH | 1520 + `400` popup | grinding rail/log |
| d-post7 (T+523) | +17.4 s | 00:01:58 (+29) | 5TH/6 | 52% | 51 MPH | 3590, `FS Rail` banner | carving groomed slope |
| d-post8 (T+526) | +20.4 s | 00:02:01 (+32) | 6TH/6 | 53% | 47 MPH | 3590 | rider down/sliding by red chevron barrier |
| d-post9 (T+529) | +23.4 s | 00:02:05 (+36) | 6TH/6 | 54% | 39 MPH | 3590 | carving icy chute between trees |
| d-post10 (T+532) | +26.4 s | 00:02:10 (+41) | 6TH/6 | 55% | 11 MPH | 3590 | slow carve by rock wall |

Race-advance vs wall-span (race-advanced-since-npre2 / wall-since-npre2):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| d-post1 | 6 | 4 | 1.50 |
| d-post2 | 10 | 7 | 1.43 |
| d-post3 | 14 | 10 | 1.40 |
| d-post4 | 18 | 13 | 1.38 |
| d-post5 | 22 | 16 | 1.38 |
| d-post6 | 25 | 19 | 1.32 |
| d-post7 | 29 | 21 | 1.38 |
| d-post8 | 32 | 24 | 1.33 |
| d-post9 | 36 | 27 | 1.33 |
| d-post10 | 41 | 30 | 1.37 |

Rider-pixel tracking series (committed `t39-track.py`, byte-identical to
T38's; RDC = rider dark-centroid + validity gate; SCPS40 = T37-frozen
±40 window; SCPS120 = wide ±120 window; whole hop = PIL per-hop from
§hops):

| Snap | RDC cx/cy (px) | RDC npix (frac) + gate | SCPS40 lag (corr) into this snap | SCPS120 lag (corr) into this snap | Whole hop into this snap |
|---|---|---|---|---|---|
| npre1 | 446.2 / 351.0 | 3061 (0.022) VALID | — | — | — |
| npre2 | 365.9 / 218.4 | 38471 (0.274) INVALID (forest floods ROI) | −24 (0.08) no match | +120 (0.25) RAIL | 20.6163/179 |
| d-post1 | 399.5 / 176.9 | 30689 (0.219) INVALID (trees/shade) | +40 (−0.14) rail, no match | −120 (0.16) RAIL | 12.2130/143 |
| d-post2 | 243.0 / 214.6 | 7080 (0.050) INVALID (over gate) | −40 (−0.45) rail, no match | −120 (0.78) RAIL | 11.5010/102 |
| d-post3 | 304.1 / 201.0 | 29000 (0.207) INVALID (trees/log) | −22 (0.87) resolved | −22 (0.87) resolved | 9.0679/105 |
| d-post4 | 356.4 / 170.5 | 21796 (0.155) INVALID (bank/trees) | +36 (−0.15) no match | +120 (0.30) RAIL | 10.8491/144 |
| d-post5 | 326.9 / 251.2 | 2179 (0.016) VALID | −40 (0.38) rail, weak | −108 (0.70) resolved | 8.5766/122 |
| d-post6 | 291.1 / 314.4 | 44223 (0.315) INVALID (rail/log fills ROI) | +38 (0.54) resolved | +38 (0.54) resolved | 13.7716/124 |
| d-post7 | 350.1 / 166.3 | 5694 (0.041) VALID | +40 (−0.11) rail, no match | +99 (0.63) resolved | 16.5191/147 |
| d-post8 | 266.5 / 176.6 | 36434 (0.260) INVALID (barrier/shade) | −40 (0.78) RAIL | −60 (0.85) resolved | 13.4971/159 |
| d-post9 | 463.5 / 230.4 | 21309 (0.152) INVALID (trees/chute) | +27 (0.67) resolved | +27 (0.67) resolved | 16.9465/159 |
| d-post10 | 355.4 / 205.6 | 78940 (0.562) INVALID (rock wall fills frame) | +35 (0.35) weak | +35 (0.35) resolved | 14.3564/150 |

Control distribution (the ENTIRE dense phase is no-input — all 11 hops
are control samples):

| Metric | Control value (this run) |
|---|---|
| HUD position | 4 swaps + net decay 4TH→6TH across 12 snaps with ZERO input (4→4 pre-pair; 4→4 sham hop; 4→5→4→4→4→5→5→6→6→6 post-sham) |
| HUD progress/clock | monotonic 36% → 55%, +41 s race over +30 s wall (~1.4×, matches turbo) |
| RDC gate | gated OUT on 9/12 snaps (npix ≫ rider-scale: forest/trees/log/rock/barrier flood the ROI); only npre1 (3061), d-post5 (2179), d-post7 (5694) VALID — non-adjacent, so no gated delta exists anywhere in the series |
| SCPS40 | rails ±40 on 5/11 hops (incl. the sham hop npre2→d-post1 at +40 @ −0.14) |
| SCPS120 | rails ±120 on 4/11 hops incl. the pre-pair gap (+120 @ 0.25) and the sham hop (−120 @ 0.16); resolves 7/11 (−22 @ 0.87, −108 @ 0.70, +38 @ 0.54, +99 @ 0.63, −60 @ 0.85, +27 @ 0.67, +35 @ 0.35) |
| Whole hops | 8.58–20.62 dense (motion-class throughout) |

Observed behavior characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | Yes — four times, with ZERO input anywhere: 4TH→5TH at d1→d2, 5TH→4TH at d2→d3, 4TH→5TH at d5→d6, 5TH→6TH at d7→d8; the sham hop itself (npre2→d1) holds 4TH→4TH and the pre-pair gap holds 4TH→4TH. Net decay 4TH→6TH distributed across the 26 s tail |
| Did progress change? | Advances monotonically 36% → 55% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +41 s race over +30 s wall (~1.4×, matches turbo) |
| Did speed change? | Varies 64→67→30→57→27→44→49→30→51→47→39→11 MPH — ordinary race-speed excursions distributed across the series (11 MPH @d10 rock-wall carve), none sham-coincident |
| Did score change? | 1520 flat through d-post6 (with a `400` popup @d6), then 3590 from d-post7 (`FS Rail` banked, +2070) — a scoring event occurs mid-series with no input |
| Did heading change (rider pixels)? | RDC gated OUT on 9/12 snaps (forest/trees/log/rock/barrier flood the ROI); only 3 VALID snaps, non-adjacent, so no gated delta exists. SCPS40 rails ±40 on 5/11 hops; SCPS120 rails ±120 on 4/11 hops incl. the pre-pair gap and the sham hop — rail-class background shifts occur with no input at ~3 s exposure gaps under turbo. The 7 SCPS120-resolved hops are distributed across the series |
| Any HUD discontinuity at the sham? | None — position/speed show no sham-coincident step (4TH→4TH across the sham); progress/clock monotonic; no freeze, no menu, no reclaim |
| Isolation note | Single control run, no same-seed pairing (AI lineup/RNG differ run to run); the control distribution is compared against T36/T37/T38 input runs below |
| Recipe (one variant per attempt) | T38 G1(b), still open: exposure gaps closer to true 1 s (score post-hoc, not in-script) so SCPS stops railing and a gated RDC pair can straddle the input; tracking note: the ±120 window resolves ~2/3 of hops here (7/11) vs ~1/3 in T38 (4/11) — resolution is scene-lottery-dependent, and a steer-discriminating window still needs sub-second exposures, not wider lags |

Control-vs-input comparison (T36 tap / T37 tap / T38 hold windows vs
this no-input control; T36/T37 values from their reports):

| Item | T36 (338.6 ms tap) | T37 (338.2 ms tap) | T38 (1037.3 ms hold) | T39 control (NO input) |
|---|---|---|---|---|
| Pre-input baseline | single `npre` 00:01:18 6TH/6 30% (no pair; sparse shape) | pair 00:01:26 / 00:01:31 | pair 00:01:25 / 00:01:31 | pair 00:01:24 / 00:01:29 |
| Pre-pair positions | 6TH/6 (single) | 2ND / 3RD (swap in gap) | 2ND / 2ND | 4TH / 4TH |
| Series-end position | 6TH/6 @00:02:29 59% (sparse +1/+3/+8/+15/+25/+40) | 3RD/6 @00:02:11 60% | 6TH/6 @00:02:12 58% | 6TH/6 @00:02:10 55% |
| Position swaps in series | 0 (6TH throughout sparse tail) | 2ND↔3RD swaps with and without tap | 3 swaps, decay 2ND→6TH | 4 swaps, decay 4TH→6TH |
| Input-hop position step? | none separable | none separable | none (2ND→2ND) | none (4TH→4TH) |
| RDC gate-out rate | n/a (no tracking in T36) | validity-flooded 6/12 | gated out 10/12 | gated out 9/12 |
| Gated RDC delta anywhere? | n/a | no | no (non-adjacent valids) | no (non-adjacent valids) |
| SCPS40 rail rate | n/a (no tracking in T36) | rails nearly every step | rails 6/11 | rails 5/11 |
| SCPS120 rail rate | n/a (T38+ metric) | n/a (T38+ metric) | rails 7/11 | rails 4/11 |
| Sham/input hop SCPS120 | n/a | n/a | −120 @ 0.15 RAIL | −120 @ 0.16 RAIL |
| Whole-hop range (dense) | n/a (sparse shape) | X+D 8.48–20.26 (dense subset incl. 8.48 tap hop) | 10.07–22.33 | 8.58–20.62 |
| Clock ratio (race/wall) | ~1.35× | ~1.4× | ~1.4× | ~1.4× |

Post-sham frame motion (whole-frame PIL): all 66 D pairs 6.36–20.62/p99
≤179 (min d-post2–d-post5 6.3629/75, max npre1–npre2 20.6163/179;
JPEG shas distinct). Motion throughout — no static frame, no freeze, no
menu/panel reclaim in the 34 s tail. Vs-panel-ref 12.81–26.20 across all 12
(decisively non-panel).

### R1 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.4585 | > 5.0 | yes |
| Arrival static p25→p40 | 0.1649 | < 1.0 | yes |
| Arrival static p40→s1 | 0.2764 | < 1.0 | yes |
| Arrival static s1→s2 | 0.4323 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.6623/153 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.4486/6, 0.4838/6, 0.5089/7 | (not a leg — receipt) | tabled (≈2.4–3.1× vs PIL 0.14–0.21; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.7660/18, 0.4835/7 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 0.4488/6 | (not a leg — receipt) | tabled (≈3.1× vs PIL 0.1430) |

### R1 LIVE gate legs (in-script proxy, remote)

| Gate leg | Value | Bar | Margin | Pass? |
|---|---|---|---|---|
| Departure pppre→x-post1 | 14.2972 | > 5.0 | 2.9× | yes |
| Non-panel (x-post40 vs-pp) | 18.9506/162 | > 5.0 | 3.8× | yes |
| Motion (x-post15→x-post25) | 11.4305 | > 5.0 | 2.3× | yes |
| Motion (x-post25→x-post40) | 11.2629 | > 5.0 | 2.3× | yes → `LIVE-LIKE`, pre-sham pair + sham window + dense series |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Live race reproduced at a matched phase (HUD advancing, phase-match tabled) | countdown `2` at +0.0 s, live gameplay from +4.0 s, race 6TH/6 at 55% by +99 s wall with zero steering input; clock/progress advance monotonically, all X+D hops 8.58–20.62 (motion); sham window @T+504.62 vs T38's hold @T+504.54, clocks −1/−2 s, progress −4/−6 pp (positions 4TH/4TH vs 2ND/2ND — mid-pack vs lead-pack, AI lottery) |
| Sham window with proven no-input gap | SHAMSTART→SHAMEND 1003.7 ms wall gap, zero xdotool calls (no keydown/keyup/focus); 71.7 s input-free before, full dense series input-free after |
| Dense 10-snap control series (HUD + tracking + hops) | 12-snap HUD series above (position 4 swaps + decay 4TH→6TH distributed, progress 36→55%, clock +41 s, speed excursions + `FS Rail` score event @d7 distributed, score 1520→3590) + RDC/SCPS40/SCPS120 per-snap table + control distribution (RDC gated out 9/12, SCPS40 rails 5/11, SCPS120 rails 4/11) + comparison + recipe |
| Control-vs-input comparison table (T36/T37/T38 windows vs this control) | tabled above (position volatility, rail rates, gate-out rates WITHOUT any input match the input runs' behavior class hop-for-hop) |
| Full input log (proving NO input) + trace sha | `t39r1-poll.log` (157 lines: every score + press + sham stamps, walls + uptimes; zero `keydown` after XCROSS) + trace `749b8c93…74249` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34/T35/T36/T37/T38 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725,
first vblank L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks
397 frozen (all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not
changed`; clean tail @552.5259. Census: EE 12,393,674 (52, set-identical
to T38 R1) · IOP 20,063,952 (155, set-identical to T38 R1 — sham + dense
series + gameplay adds no new called API) · `libsd.006: sceSdGetParam` 24610
(T38: 24547); `sceSdGetAddr` 4,001,328 (T38: 4,025,424).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate → X Cross → LIVE-LIKE proxy gate) |
| Cross on X Continue? | YES (XCROSS @T+432.42 R1, pre-press = pre-race panel, X Continue) |
| Live race reached at matched phase? | YES (countdown `2` @T+433 → live gameplay by T+437 → race at 55%, 6TH/6 @T+532, still running; sham window phase-matched to T38's hold window within −2 s clock / −6 pp progress) |
| Sham with NO input on live gameplay? | YES (SHAM 1003.7 ms gap @T+504.62, zero xdotool, pre-sham pair = racing 00:01:24 4TH/6 36% / 00:01:29 4TH/6 38%) |
| Control distribution tabled? | YES — dense HUD + RDC/SCPS40/SCPS120 control series + control-vs-input comparison: position volatility (4 swaps + 4TH→6TH decay), rail-class shifts (SCPS40 5/11, SCPS120 4/11 incl. pre-pair + sham hops), and RDC floods (9/12) all occur WITHOUT any input, matching the T36/T37/T38 input runs' behavior class |
| Bounded re-attempt? | none run (pre-sham = racing at a matched phase — re-attempt condition not met; brief stops at R1 + recipe) |
| 1200 s cap | Not reached — R1 ≈ T+562; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (6TH/6, 55%, 00:02:10) after a no-input sham window + dense 10-snap control series; race not yet finished at capture end |

## T39-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t39 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay → pre-sham pair → sham window (NO input) → dense 10-snap series, T+~562) | 45,232,651 / 2,898,445,035 | `749b8c93dcb961ec047f5e0d506aedf11e92041c9f751a47ab6f3f3be1744249` (analyze-sha on H27 = post-restart re-verify on H28 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t39r1.txt`, same size+sha (match; streamed via `wsl cat`, no C: staging — C: at 4.5 G falling to 1.4 G) + committed head/tail 2000+2000 (`t39r1-trace-head.txt` 149019 B sha `76bc8871fdec…`, `t39r1-trace-tail.txt` 131823 B sha `e2ce2e40b1f8…`) |
| `emulog-pre-t39-20260921T104301Z.txt` = t38 R1 (preserved at R1 boot) | — / 2,903,385,415 | `1180c368852527a5ce33201470fb4a656ad320a6a9b3736dbce78283973609a3` (re-verified post-run: matches T38) | bytesize-only (T38 precedent; SSD holds T38's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 12,393,674 (52
distinct, set-identical to T38 R1) · IOP 20,063,952 (155, set-identical
to T38 R1) · vblanks 397. Committed: `t39r1-census.txt` (11866 B sha
`829f68d77481…`), `t39r1-samples.txt` (5859 B sha `9ea45c98ab98…`),
`t39r1-poll.log` (157 lines, 9629 B sha `56d1e2b94b40…`),
`t39r1-stdout.txt` (438 lines, 28693 B),
`t39r1-stderr.txt` (full `set -x` shell trace, 2547 lines, 141054 B),
`t39r1-trace-head.txt` / `t39r1-trace-tail.txt`.
Trace-head note: same 149019 B as T34/T35/T36/T37/T38 R1 heads but sha differs
(`76bc8871…` vs `3a28d99d…`) — timestamp-stripped content differs across
timing/wall-clock/shader-cache lines (same standing pattern).

## T39-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); one `wsl` call per ssh):

```
# reuse verification (pipe-free; one wsl call per ssh)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H26 …170 (fresh, up 2 s)
ssh bytesize 'wsl dmesg' > /tmp/t39-dmesg-pre.txt                     # 440 lines, 0 AcceptAsync (H26)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t39-eventlog-pre.txt  # head H26-create 06:39:30
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/…100909.nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t35-ref-panel.ppm'    # all 9 refs reproduce
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c'                         # 874G / C: 4.5G
ssh bytesize 'wsl ls …/logs/; ls -la …/logs/emulog.txt'                # 24 emulogs + live = T38 R1
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 1180c368… T38R1 live
# T38 ref snaps (local): 12/12 sizes reproduce T38 §chain
# freeze t39 scripts (copies of T38; sham_window replaces press_hold; bash -n; cmp-identical cropdiff/track/vcount)
# staging (T25 recipe: scp to C: then wsl cp)
scp t39-auto.sh t39-analyze.sh t39-vcount.sh t39-cropdiff.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t39-… /home/brad/pcsx2-t4/; sha256sum …'  # staged shas match local
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H26
ssh bytesize 'wsl python3 …/t39-cropdiff.py …REFPP …; date -u; cat /proc/uptime; grep btime /proc/stat'  # 0.0000/0 PPM, H27 …331 up 17 (mid-staging restart H26→H27, not by me)
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix'  # re-mount on VM-H27
ssh bytesize 'wsl sha256sum …/t39-auto.sh'                            # ac7232db… staging survived restart
ssh bytesize 'wsl dmesg' > /tmp/t39-dmesg-pre2.txt                    # 441 lines, 0 AcceptAsync (H27)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # H27 …331 up 34, no restart before R1
# R1 (ONE ssh; exit 0; LIVE-LIKE → PRE-PAIR → SHAM (no input) → dense 10)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t39-auto.sh' > /tmp/t39r1-run-stdout.txt 2>/tmp/t39r1-run-stderr.txt  # T39_DONE, up 49→611
ssh bytesize 'wsl dmesg' > /tmp/t39-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 442 lines, 0 AcceptAsync (H27, full R1 coverage)
ssh bytesize 'wsl bash …/t39-analyze.sh'                              # 749b8c93…, 45232651 L
ssh bytesize 'wsl bash …/t39-vcount.sh'                               # 397 frozen
ssh bytesize 'wsl wc -l …/t39-poll.log'                               # 157
ssh bytesize 'wsl ls …/t39-*.jpg'                                     # 61 JPGs
ssh bytesize 'wsl cp <30 chain jpg> /mnt/c/…'                         # (explicit list, one wsl call)
ssh bytesize 'wsl cp <31 d/mr/x jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t39-…" /tmp/t39-fetch/                         # 61 jpg + logs (r1-prefixed local)
# R1 post-hoc (local batch scorer, 4/4 bit-exact): chain panel, hops, 15 panel pairs, 15 X pairs, 66 D pairs, xrun, census set-compare, t39-track.py dense series
ssh bytesize 'wevtutil …' > /tmp/t39-eventlog-post.txt                # head H27-teardown 06:56:03; ZERO in-window entries of any kind (nearest: ID 37 NTP @06:52:33, +10 s post-window)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H28 …560 (fresh, created by this call)
ssh bytesize 'wsl dmesg' > /tmp/t39-dmesg-post.txt                   # 448 lines, 1 AcceptAsync [16.98] (H28)
ssh bytesize 'wsl sha256sum …100909.nvm'                               # da021d2a… untouched
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 749b8c93… re-verified
ssh bytesize 'wsl ls …/logs/'                                         # 26 emulogs incl. emulog-pre-t39-20260921T104301Z.txt
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t39-20260921T104301Z.txt'  # 1180c368… T38R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t39r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t39r1-trace-tail.txt         # 2000 lines, clean tail @552.5259
ssh bytesize 'wsl grep -c LoadStartModule …/logs/emulog.txt'           # 18
# SSD copy (COPYFILE_DISABLE=1; streamed via wsl cat — no C: staging — then shasum re-verify)
ssh bytesize 'wsl cat <trace>' > "/Volumes/Extreme SSD/ps2x-t4/emulog-t39r1.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t39r1.txt"         # 749b8c93… match
ssh bytesize 'wsl df -h / /mnt/c'                                     # 871G / C: 1.4G
ssh bytesize 'wsl du -sh …/logs/'                                     # 40G
ssh bytesize 'wevtutil qe System /c:12 /rd:true /f:text' > /tmp/t39-eventlog-final.txt  # H27-teardown 06:56:03, H28-create 07:02:40
# report (chunks; receipts include tail -3)
cp /tmp/t39-dmesg-*.txt /tmp/t39-eventlog-*.txt /tmp/t39r1-run-stdout.txt … local/research/T39/  # renamed per §evidence
tail -3 local/research/T39/REPORT.md
git add -f local/research/T39/<81 files by name>                      # ignored dir, forced
git commit -m "[T39] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T39-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (steering characterization) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → Cross on X Continue → LIVE-LIKE proxy gate (departed + non-panel + motion ×2) → ≤3 attempts) → live gameplay; then a sham window with NO input acts on nothing (R1: pre-sham pair 00:01:24 4TH/6 36% / 00:01:29 4TH/6 38%, dense 10-snap series to 00:02:10 6TH/6 55% showing the control distribution — 4 position swaps + decay 4TH→6TH distributed with no sham-coincident step, RDC gated out 9/12 snaps, SCPS40 rails ±40 on 5/11 hops, SCPS120 rails ±120 on 4/11 hops including the pre-pair gap and the sham hop; race clock ~1.4× wall under turbo). The control shows the same decay/rails/floods behavior class as T36's tap, T37's tap, and T38's hold — tabled in the control-vs-input comparison. Next, ONE variant per attempt: T38 G1(b), still open — exposure gaps closer to true 1 s (score post-hoc, not in-script) so SCPS stops railing and a gated RDC pair can straddle the input. Tracking note: the ±120 window resolves 7/11 hops here vs 4/11 in T38 — resolution is scene-lottery-dependent; a steer-discriminating window needs sub-second exposures, not wider lags. Gate note: the sham→gameplay whole-frame hop is large (~8.58–20.62 dense) because the race never stops moving — gate on the HUD (clock/position/progress/speed/score), not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | Zero in-window flaps this session + 2 pre-session/mid-staging + 1 post-everything restart (all not by me) | 0 userland kills on any VM this session; AcceptAsync exact counts 0/0/0/1 across the 4 committed dmesg files, all outside the run window (H26-pre 0; H27-pre 0; H27-post 0 with full R1-window coverage — kernel quiet after uptime 49.06; H28-post 1×[16.98] post-everything VM) + 1 pre-session VM restart between T38 and T39 (H25→H26; T38: 1 pre-session restart) + 1 mid-staging restart (H26→H27 @10:42:12, between X11 mount and R1 — re-mounted + re-verified on H27 before the run) + 1 post-everything VM restart (H27→H28 @10:56:03, after all fetch WSL calls — proven by H28's 1.93 s uptime at the 11:02:42 identity check; only final state reads ran on H28). ZERO Volsnap/Hyper-V entries in-window (newest-30 shows zero entries of any kind inside 06:43:01–06:52:23 local; nearest entry is a benign Time-Service NTP notice ID 37 at 06:52:33, +10 s post-window). R1 completed exit 0 with T39_DONE + all 61 snaps + clean trace tail, i.e. effects-verified per the T27 §4 rule (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: ZERO in-window entries; boundaries bound all restarts | Newest-30 reads (pre/post): H25 teardown 06:06:42 → H26 create 06:39:30 → H26 teardown/H27 create 06:42:12 → H27 teardown 06:56:03; inside the R1 window 06:43:01–06:52:23 (local): ZERO entries of any kind (no Volsnap, no Hyper-V-VmSwitch — precedent stands). Final newest-12: H27 teardown 06:56:03 → H28 create 07:02:40. `wevtutil` local-as-Z (+4 h → UTC) stands |
| G4 | Hold count 119/119 (534 ms-class) + 2/2 steering taps (300 ms-class) + 1/1 steering hold (1 s) + 1/1 sham (no input) | 534 ms-class holds register 119/119 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35+T36+T37+T38+T39 (T39 R1: 536.3/535.3/535.5/536.3/536.6/535.2/536.0/535.8/536.4/536.6 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect. Separately: the 300 ms-class steering tap delivered 2/2 (T36/T37), the 1 s steering hold delivered 1/1 (T38), and the no-input sham delivered 1/1 (1003.7 ms wall gap, zero xdotool) — different input classes, not bisections |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on title/SE + MR; panel animation + lineup lottery on arrival; countdown near-frozen; gameplay lottery | Title text-band near-frozen across showings (0.0468/1 R1 vs 0.0453/0 T38 — snowflake shimmer breaks bit-equality, pair 0.0249/0); R1's 4 frames bit-identical to T38 R1's run (a1-post15 — now identical across FIVE runs T35/T36/T37/T38/T39 — plus a1-post25, sj-post1, sj-post8); menu whole-frame ≤0.07/p99 ≤1 cross-run; SC cross-run 0.10–0.26/p99 1–6; ZC cross-run 0.10–0.17/p99 1–5; SP cross-run ≤0.13/p99 ≤1; SM cross-run 0.009–0.07/p99 0–1; Select Event ≤0.12/p99 ≤1 cross-run except rc-post8 snowflake animation (rc-post1/3 near-identical 0.0004/0.0043 but NOT bit-identical — shimmer phase); My Rules ≤0.09/p99 ≤2 cross-run (sj-post1/8 bit-identical this time); pre-race panel ≤0.44/p99 ≤20 within run over 79 s (panel shimmer/animation) + AI rider lineup differs run to run (T39 `Zoe/Marisol/Viggo/Nate/Allegra/Moby` vs T38 `Zoe/Seeiah/Elise/Viggo/Kaori/Moby` vs T37 `Zoe/Viggo/Eddie/Allegra/Kaori/Nate` vs T36 `Zoe/Moby/Nate/Luther/Griff/Marty` vs T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (50.7398/131 vs T38's 49.4844/132 vs T37's 48.2320/132 vs T36's 48.5186/132 vs T35's 48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T39: 98% @+5, cinematic @+8, panel @+15 — same shape as T35/T36/T37/T38, different cinematic track: Deep End Utah Saints Remix Swollen Members Balance vs Way Away Yellowcard Ocean Ave) — the settled-panel gate handled all timings; countdown-`2` gate frame near-frozen cross-run (1.3242/44); gate-exit x-post3 close cross-run again (2.7826/51 — similar 5TH/4TH @00:00:02 starts); live gameplay never static (9.53–18.08 X, 6.36–20.62 D). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the sham run | `WaitVblankStart` stops after log ≤90 in T39 R1 including countdown + live gameplay + pre-pair + sham window + dense series (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T38-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count shifts on audio) | Like prior arrivals, sham + dense series + gameplay adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T38 R1; counts shift (`GetThreadId` 5.06M→5.12M, EE total 12.32M→12.39M; IOP 20.15M→20.06M; `sceSdGetParam` 24547→24610, `sceSdGetAddr` 4.03M→4.00M — race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts + C: pressure CRITICAL | `…/logs/` now holds ~40 GB across 26 emulogs (T17→T39 chain, all preserved); C: 1.4 G avail final (4.5 G pre-run — staging + trace growth consumed ~3.1 G; T38 final was 4.6 G). C: still at 100% and now under 1.5 G — next session should clear `C:\Users\bradr\pcsx2-t4\` staging (owner's call; left in place per precedent). T39 R1 full trace SSD-copied + sha-verified (2.90 GB: `emulog-t39r1.txt`, streamed via `wsl cat` to avoid C: staging); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T39 brief cites `t38-auto.sh`, `t38-cropdiff.py`, `t38-track.py`, `t38-analyze.sh`, `t38-vcount.sh` — all 5 exist in `local/research/T38/` and were copied (not modified) for T39. T28 G9 lesson holds |
| G10 | Session wall + run durations | ~105 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T39). R1 wall 562 s — 202 s over the ≤6 min guidance (X-phase scoring + dense tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount needed twice (mid-staging restart), harmless | The `/tmp/.X11-unix` tmpfs mount landed first on VM-H26, then re-landed on VM-H27 after the mid-staging H26→H27 restart (not by me); no restart between the H27 re-mount and R1; R1 started Xvfb :99 cleanly (exit 0 + 61 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 – T38 G11 stand) |
| G12 | Remote-vs-PIL gap receipted again on the panel whole bar: ~2.0–3.4×, bar holds even remotely | R1's in-script vs-pp receipt reads 0.45–0.77/p99 6–18 on panel-side PIL 0.14–0.48 (≈2.0–3.4× inflation at the ~0.2 scale — T35's 1.3–1.6× / T36's 1.4–1.8× / T37's 1.3–1.6× / T38's 1.5–2.8× receipts re-confirmed on a new run), so the < 2.0 whole bar holds even as an in-script leg (2.6× margin on the worst remote 0.7660). The TAG-crop gap re-confirmed at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t39-auto.sh`,
`t39-cropdiff.py` (T38 logic, byte-identical),
`t39-track.py` (frozen rider-pixel tracker: RDC + validity gate + SCPS40 + SCPS120, byte-identical),
`t39-analyze.sh`, `t39-vcount.sh` (output-name deltas only; vcount
byte-identical);
R1: `t39r1-start.jpg`, `t39r1-a1-now.jpg`, `t39r1-a1-poll01.jpg`,
`t39r1-a1-pre.jpg`, `t39r1-a1-post{3,8,15,25}.jpg`, `t39r1-menupre.jpg`,
`t39r1-mc-post{1,3,8,15}.jpg`, `t39r1-scpre.jpg`,
`t39r1-zc-post{1,3,8}.jpg`, `t39r1-ccpre.jpg`,
`t39r1-sp-post{1,3,8}.jpg`, `t39r1-sppre.jpg`,
`t39r1-pc-post{1,3,8}.jpg`, `t39r1-smpre.jpg`,
`t39r1-rc-post{1,3,8}.jpg`, `t39r1-sepre.jpg`,
`t39r1-sj-post{1,3,8}.jpg`, `t39r1-mrpre.jpg`,
`t39r1-mr-post{1,3,8,15,25,40}.jpg`, `t39r1-mr-stab{1,2}.jpg`,
`t39r1-pppre.jpg`, `t39r1-x-post{1,3,8,15,25,40}.jpg`,
`t39r1-npre{1,2}.jpg`, `t39r1-d-post{1,2,3,4,5,6,7,8,9,10}.jpg` (61 snaps),
`t39r1-census.txt`, `t39r1-samples.txt`, `t39r1-poll.log`,
`t39r1-stdout.txt`, `t39r1-stderr.txt`, `t39r1-trace-head.txt` / `t39r1-trace-tail.txt`;
flaps: `t39-dmesg-vmH26-pre.txt` (0 AcceptAsync on H26, pre-run) /
`t39-dmesg-vmH27-pre.txt` (0 AcceptAsync on H27, pre-run) /
`t39-dmesg-vmH27-post.txt` (0 AcceptAsync; full R1-window
coverage, zero in-window) / `t39-dmesg-vmH28-post.txt` (1 AcceptAsync
[16.98] on H28, fresh boot),
`t39-eventlog-pre.txt` / `t39-eventlog-post.txt` / `t39-eventlog-final.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t39r1.txt`
(2,898,445,035 B `749b8c93…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T38 R1
`…-20260921T104301Z.txt` `1180c368…`.


