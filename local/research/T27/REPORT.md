# T27 report — press-on-title within dwell: first menu reached (bytesize, no lease)

Brief `local/muse/prompts/T27.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
4 h; session wall ~22:32–23:09 UTC 2026-09-20 (~37 min + report/commit).

Stale-reading guard: `local/research/T25/REPORT.md` (all: Phase 1 fresh boot
SKIPS to attract with NVM `da021d2a` untouched; Phase 2 `t25-auto.sh` drove
attract → TITLE 3× but attract reclaims in ≤10/≤20/≤80 s so no press ever
acted ON title; G1 proposes press-on-title within dwell; G2 WSL precautions:
single-shot scripts, runs ≤6 min, preserve emulogs first, re-check dmesg +
btime + init age, UNFILTERED `dmesg` + Windows event log around flaps, 534 ms
holds 12/12 do NOT bisect, `;` chains only INSIDE one `wsl` call, one `wsl`
call per ssh, no pipes inline).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a pure-Python PPM text-band detector (`t27-cropdiff.py`, no PIL on
bytesize) scored TITLE against T25's references with threshold band-mean
< 2.0 AND p99 ≤ 10 (title-title ≤ 0.10/≤1 local, 0.40–0.44/5–6 remote
lossless-vs-JPEG; attract ≥ 12.73/≥ 107 over 11 screens). Three single-shot
runs: R1's detector scored nothing (xwdtopnm emits maxval-65535 PPM, parser
took 255-only; empty scores misfired as title) → 3 blind Start presses on
attract, title by +3 s 3/3, no menu; R2's detector scored start/now but no
poll (snap() clobbered the loop variable) → 3 Cross presses + 54 unscored
polls, post-hoc titles at polls 01–07/08 each (dwell ≈ 15–17 s); R3 with both
fixes detected TITLE at poll01 (0.4331/6) and pressed Start ≤ 0.73 s after
the title exposure → Main Menu by +3 s, stable across 10 snaps / 91 s
(whole-frame pairwise 0.027–0.086, p99 0–2). 6 WSL flaps + 3 VM restarts this
session; all runs completed exit 0 in flap-free windows (R3's window
effects-verified: dmesg coverage lost to the third restart); all traces +
NVM re-verified post-restart, NVM `da021d2a` untouched throughout. R3's trace
carries one R3-only guest call (`libsd.006: sceSdGetParam` ×412); EE sets
identical (52), IOP 154 → 155.

## T27-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T27; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T27]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T27 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Title refs present | — | `t25-post-p1a/p2a/p2d.jpg` shas `0183a72d…`/`234c7cf4…`/`120f688b…` reproduce T25 | yes |
| Free space | — | WSL `/` 914 G avail; C: 58 G avail (836 G); laptop `/` 20 Gi avail; SSD 466 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×3 (VM-B pre-R1, VM-C pre-R2/live-test, VM-C pre-R3); reverted by the VM-B→C restart, VM-C flap #5 (@470.86), and the VM-C→D restart (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached per run by the scripts (`pkill` + `setsid nohup`); plus one manual pre-R2 live-test instance (PID 440, reaped by R2's `pkill`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t27-{auto,analyze,vcount,cropdiff}.sh/.py`, `t27-ref-title.ppm` (3,932,177 B, sha `b964856a…e94f59`), `t27-{r1,r2,r3}-census/samples.txt`, `t27-*.jpg/.ppm/.log`, `t27-livetest.xwd`, `…/logs/emulog-pre-t27-*.txt` (rotation chain, see trace table), `boot-t27.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t27*` + `emulog-t27r{1,2,3}.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20, re-verified ×4 incl. post-all-runs) |
| VM restarts (not by me) | 3 mid-session WSL VM restarts (A→B 18:37:38, B→C 18:45:03, C→D 19:00:22 local-rendered = +4 h UTC); cause unknown (no `wsl --shutdown` from this session; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on all four btimes:
18:32:50→`1789943570`, 18:37:38→`1789943857`, 18:45:03→`1789944303`,
19:00:22→`1789945222`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 22:32:50 ([0] VM-A) | VM-A started fresh on first ssh | btime `…570`, eventlog-pre head 18:32:50 |
| 2 | 22:33:29–22:34:39 ([38.93],[55.37]) | Flaps #1–#2 on VM-A (kill→remount 0.2/53.3 s); pre-run, pre-mount; one transient `wsl` launcher error (`cannot find the path specified`) between them | `t27-dmesg-vmA.txt` |
| 3 | 22:37:38 | VM-A→VM-B restart (NIC create 18:37:38 rendered); mount ssh landed on VM-B (fresh dmesg); staged files + NVM re-verified | btime `…857`, eventlog-pre2 head |
| 4 | 22:38:25–22:41:24 ([47,226] VM-B) | Quiet: R1 single-shot exit 0, `T27_DONE`, clean shutdown; zero `AcceptAsync` in window | exit 0, snaps, trace tail |
| 5 | 22:41:39 ([241.42]) | Flap #3 on VM-B (kill→remount 27.0 s); post-R1 (evidence home, trace re-verified) | `t27-dmesg-vmB.txt` |
| 6 | 22:45:03 | VM-B→VM-C restart (teardown 18:44:42 + create 18:45:03 rendered in post log) | btime `…303`, eventlog-post |
| 7 | 22:46:46 ([102.43]) | Flap #4 on VM-C (kill→remount 1.2 s); 8 s pre-R2-boot | `t27-dmesg-vmC.txt` |
| 8 | 22:46:53–22:50:33 ([110,330] VM-C) | Quiet: R2 single-shot exit 0, `T27_DONE`, clean shutdown; zero `AcceptAsync` in window | exit 0, 58 snaps, trace tail |
| 9 | 22:50:49 ([345.77]) | Flap #5a on VM-C (kill→remount 26.3 s); post-R2 | `t27-dmesg-vmC.txt` |
| 10 | 22:52:53 ([470.86]) | Flap #5b on VM-C (kill→remount 34.5 s); pre-R3 (X11 mount reverted; re-mounted, R1 trace re-verified `dd788742` match) | `t27-dmesg-vmC.txt`, sha re-verify |
| 11 | 22:53:52–22:57:13 ([529,730] VM-C) | R3 single-shot exit 0, `T27_DONE`, clean shutdown; NO dmesg coverage (VM-D restarted before capture) — flap-free effects-verified (exit 0 + monotonic uptime 529→730 + clean trace tail; a mid-run kill would have killed the ssh-held script) | exit 0, snaps, trace tail |
| 12 | 23:00:22 | VM-C→VM-D restart (teardown 18:59:31 + create 19:00:22 rendered); all 4 traces re-verified post-restart bit-identical (R1/R2/R3 + preserved T25) | btime `…222`, eventlog-post, 4/4 sha match |
| 13 | event log | Newest-30 reads (pre/pre2/post): VM-boundary VmSwitch sequences only (creates 18:32:50 / 18:37:38 / 18:45:03 / 19:00:22; teardowns 18:44:42 + 18:59:31 with IDs 71/69/233/234); ZERO entries at any of the 6 flap kills — userland kills leave no Windows trace (T17/T21/T23/T25 precedent stands) | `t27-eventlog-{pre,pre2,post}.txt` |

## T27-1. Detector + calibration (thresholds, match scores)

Tool: `t27-cropdiff.py` (committed, dual-mode). Text-band crop
(380,200,1180,480) abs-diff stats (mean/p99/max) vs reference. PIL path on
the laptop (JPEG or PPM); pure-Python P6 path on bytesize (no PIL, no
ImageMagick, no pip in WSL — `which` empty, `ModuleNotFoundError: PIL`).
Grayscale `(R+G+B)/3` in both paths; PPM path bit-matches PIL
(0.0586/1/36 and 32.2992/222/241 identical to 4 decimals). Reference:
`t27-ref-title.ppm` (3,932,177 B, sha
`b964856ae947fd073dde593f02a5e9cbdc5e92873ce69ab452682e3eae94f59`),
derived from T25's `t25-post-p1a.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T27-6).

Calibration matrix (candidate vs T25 `p1a`, PIL mode unless noted):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| p1a vs p2a | 0.0586 | 1 | 36 | title-title (T25: 0.06/p99 0 — rounding) |
| p1a vs p2d | 0.0381 | 0 | 44 | title-title (T25: 0.04/p99 0) |
| p2a vs p2d | 0.0968 | 1 | 44 | title-title |
| start vs p1a | 25.8325 | 171 | 214 | title-attract |
| p1b vs p1a | 25.7385 | 177 | 200 | title-attract |
| p2b vs p1a | 32.2992 | 222 | 241 | title-attract |
| p2c vs p1a | 20.6369 | 172 | 244 | title-attract |
| p2e vs p1a | 29.8074 | 208 | 237 | title-attract |
| nvm-park vs p1a | 26.7412 | 173 | 224 | title-attract |
| nvm-park2 vs p1a | 20.5503 | 172 | 225 | title-attract |
| R1 a1-now vs p1a | 16.6749 | 112 | 202 | title-attract (run-observed min-mean region) |
| R2 a3-now vs p1a | 12.7315 | 107 | 163 | title-attract (run-observed minimum both) |
| whole-frame title pair (p1a/p2a) | 0.0421 | 0 | 36 | same-screen animated (snowfall) |
| whole-frame attract pair (start/p1b) | 15.5802 | 142 | 245 | scene change |

Remote-path confirmation on real 16-bit game PPMs (R1 snaps vs ref, PPM
mode): attract `t27-start.ppm` 25.8521/171 (PIL JPEG: 25.8325/171 —
lossless-vs-JPEG gap negligible); title frames 0.3998–0.4428/p99 5 stable
across 5 frames (`a1-post3/post8/post15`, `a2-post3`, `a3-post8`).

Thresholds (frozen before R1, unchanged all runs):

| Gate | Rule | Title-side margin | Attract-side margin |
|---|---|---|---|
| TITLE | band mean < 2.0 AND p99 ≤ 10 | worst title 0.44/5–6 → 4.5×/1.7× | best attract 12.73/107 → 6.4×/10.7× |
| STATIC | whole mean < 1.0 | still pairs 0.02–0.09 → 11×+ | scene change 15.58 → 15× |

Script variants across runs (committed files = R3/final; diffs tabled):

| Run | `t27-auto.sh` | `t27-cropdiff.py` | Detector behaviour |
|---|---|---|---|
| R1 | no `is_num`, no SELF_TEST, `snap N` global | maxval-255-only (rejects 65535) | every score empty → empty misfired as title (3 blind Starts, no polls) |
| R2 | `+is_num` fail-closed, `+SELF_TEST`/`SELF_WHOLE`, `snap N` global | + maxval-65535 branch (scale `/257`) | start/now scored; all 54 poll scores empty (`t27-aN-poll<t27-aN-pollNN>.ppm` missing — 54 `No such file`) → 3 Crosses, no-title outcomes |
| R3 | `+local N` in `snap()`/`press()` (committed) | unchanged (committed) | fully working: detect at poll01, Start ≤ 0.73 s after exposure, menu-like gate → stability series |

## T27-2. R1 — blind Starts (detector scored nothing)

Run: R1-variant `t27-auto.sh`, ONE fresh boot (skip re-confirmed: T+90
attract), T_BOOT wall 1789943904 (uptime 47, VM-B), 22:38:25–22:41:24 UTC
(uptime 47→226), WID 2097159, exit 0, `T27_DONE`, clean SIGTERM shutdown.
In-script scores all empty (`ValueError: need maxval 255, got 65535` —
xwdtopnm emits 16-bit PPM from the game visual; black-root live-test PPM was
maxval 255, size 3,932,177 B); empty misfired as title → `TITLE-ALREADY`
×3, no Cross, no polls.

### R1 press table (three timed inputs, all on attract)

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Uptime | Pre-press snap (score vs p1a) | Screen by +3 s |
|---|---|---|---|---|---|---|
| A1 Start | 1789943995.325085882 → 1789943995.859861971 | 534.8 ms | T+91 | 137→138 | attract (16.6749/112) | TITLE (0.0349/0) |
| A2 Start | 1789944021.623751052 → 1789944022.159281160 | 535.5 ms | T+117→118 | 163→164 | attract (16.1595/140) | TITLE (0.0000/0) |
| A3 Start | 1789944047.917873168 → 1789944048.453751462 | 535.9 ms | T+143→144 | 190 | attract (19.8562/151) | TITLE (0.0037/0) |

Single down/up pair each, exit 0 each; method `windowfocus --sync` +
`keydown`/`sleep 0.5`/`keyup` (T25 recipe).

### R1 screen chain (post-hoc PIL scores vs p1a; T = title by gate)

| Snap | Size / sha12 | mean/p99 | Content |
|---|---|---|---|
| start (T+91) | 53792 B / `353c7ea91258` | 25.8325/171 | Attract night halfpipe — BIT-IDENTICAL to T25 `t25-start.jpg` (full sha match) |
| a1-now (pre) | 53844 B / `23f8a8b5…` | 16.6749/112 | Attract night halfpipe (viewed) |
| a1-post3 | 58437 B / `99c1f219…` | 0.0349/0 T | TITLE (viewed: logo + `Press START button`) |
| a1-post8 | 58453 B / `77d14ac0…` | 0.0560/0 T | TITLE |
| a1-post15 | 58147 B / `d06b633b…` | 0.0000/0 T | TITLE (band pixel-identical to p1a decode, max 0) |
| a1-post25 | 58102 B / `b52b8201…` | 29.3249/210 | Attract |
| a2-now (pre) | 53889 B / `b329e42d…` | 16.1595/140 | Attract |
| a2-post3 | 58037 B / `86649948…` | 0.0000/0 T | TITLE |
| a2-post8 | 58315 B / `14d0c672…` | 0.0003/0 T | TITLE |
| a2-post15 | 44516 B / `5c323e23…` | 18.5299/164 | Attract |
| a2-post25 | 90204 B / `41f40665fd28` | 21.9262/160 | Attract — BIT-IDENTICAL to a3-post25 (full sha match; attract loop same frame 26 s apart) |
| a3-now (pre) | 85343 B / `c3c611c6…` | 19.8562/151 | Attract |
| a3-post3 | 58314 B / `311d357c…` | 0.0037/0 T | TITLE |
| a3-post8 | 58656 B / `afb2736e…` | 0.0070/0 T | TITLE |
| a3-post15 | 44799 B / `8bcb3220…` | 18.6149/165 | Attract |
| a3-post25 | 90204 B / `41f40665fd28` | 21.9262/160 | Attract (identical file to a2-post25) |

R1 dwell observed (Start-on-attract → title persistence): A1 title +3→+15
s (attract by +25); A2/A3 title +3→+8 s (attract by +15). Chain end: no
press on title (all 3 presses acted on attract); first menu not reached.

Guest/trace side (R1): boot prefix line-identical to T25 Phase 1 (BIOS L2,
ExecPS2 L142330/142426, ReBootStart L142725, first vblank L417043, first
UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen (all ≤90);
LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean tail @169.09.

## T27-3. R2 — Crosses + 54 polls (poll scores empty)

Run: R2-variant `t27-auto.sh`, ONE fresh boot, T_BOOT wall 1789944414
(uptime 110, VM-C), 22:46:53–22:50:33 UTC (uptime 110→330), WID 2097159,
exit 0, `T27_DONE`, clean shutdown. SELF_TEST passed (0.0000/0);
START/now scores numeric; all 54 poll scores empty (global-N bug) →
fail-closed no-title ×3, post series skipped (`continue`), no stability.

### R2 press table (three Cross attract-skips; no Start pressed)

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Uptime | Pre-press snap (score) | Poll01 by +2.5 s (post-hoc) |
|---|---|---|---|---|---|---|
| A1 Cross | 1789944506.343550700 → 1789944506.880014823 | 536.5 ms | T+92 | 202→203 | attract (17.6449/150 in-script; 17.6511/150 PIL) | TITLE (0.0465/1) |
| A2 Cross | 1789944545.908237365 → 1789944546.444274066 | 536.0 ms | T+131→132 | 242 | attract (38.1344/181; 38.1088/180) | TITLE (0.0442/0) |
| A3 Cross | 1789944585.488993818 → 1789944586.024769164 | 535.8 ms | T+171→172 | 281→282 | attract (12.7617/107; 12.7315/107) | TITLE (0.0000/0) |

In-script vs PIL agreement on now-scores: ≤0.03 mean (lossless-vs-JPEG
path gap negligible).

### R2 dwell observed (post-hoc PIL p99 per poll; TITLE = p99 ≤ 10 AND mean < 2.0)

| Attempt | poll01–07/08 (title) | poll08/09–18 (attract) | Boundary means |
|---|---|---|---|
| A1 (Cross @T+92) | polls 01–08 title (p99 0–10) | polls 09–18 attract (p99 152–216) | poll02 0.2706/10; poll08 0.0567/0 |
| A2 (Cross @T+131) | polls 01–07 title (p99 0–3) | polls 08–18 attract (p99 140–213) | poll03 0.1309/3 |
| A3 (Cross @T+171) | polls 01–07 title (p99 0–10) | polls 08–18 attract (p99 147–213) | poll03 0.2786/10; poll07 0.0792/1 |

Poll cadence ~2.2 s (poll01 ≈ +2.5 s … poll18 ≈ +40 s post-Cross). Title
present from the first poll after every Cross and persisting through
poll07/08 (≈ +17–19 s) → observed dwell ≈ 15–17 s per Cross press; the
detector would have fired at poll01 all 3 attempts. All 54 polls committed
(`r2polls/`); per-attempt now/start snaps at top level. Chain end: no
press on title (detector blind); first menu not reached.

Guest/trace side (R2): same prefix/census shape (×15 modes, 397 frozen,
18 LoadStartModule, 0 ERROR, `NVRAM has not changed`, tail @210.00).

## T27-4. R3 — press-on-title within dwell: first menu reached

Run: final `t27-auto.sh` (committed), ONE fresh boot, T_BOOT wall 1789944832
(uptime 529, VM-C), 22:53:52–22:57:13 UTC (uptime 529→730), WID 2097159,
exit 0, `T27_DONE`, clean shutdown. SELF_TEST 0.0000/0, SELF_WHOLE 0.0000.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (menu-like gate fired).

### R3 attempt table (detect time, dwell, press, outcome)

| Attempt | Detect (menu-wall) | Dwell observed | Press | Outcome |
|---|---|---|---|---|
| A1 | TITLE at poll01 @T+96, score 0.4331/6 (remote) / 0.0465/1 (PIL) | title present +2.5 s post-Cross; R2-measured persistence 15–17 s; press ≤ 0.73 s after exposure | Cross 535.0 ms @T+92 (attract-skip) + Start 536.1 ms @T+96 (on title) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0403/0.0245) → stability series |
| A2–A3 | not run (gate fired) | — | — | — |

### R3 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789944924.826128297 → 1789944925.361110082 | 535.0 ms | T+92→93 | 621 | `a1-now` attract (16.5923/148 remote; 16.5945/148 PIL) | `a1-poll01` TITLE (0.4331/6; 0.0465/1) |
| A1 Start (Return) | 1789944928.086754775 → 1789944928.622885819 | 536.1 ms | T+96 | 624→625 | `a1-pre` ≡ `a1-poll01` (sha `769c641d640f`, TITLE, viewed) | `a1-post3` Main Menu (16.2540/139; 16.2551/138) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.726 s; poll01 snap
exposure → Start-keydown ≤ 0.73 s (snap starts ≥ T+95.36 post-`sleep 2`,
keydown T+96.09); observed title persistence 15–17 s (R2) ⇒ press inside
the window with an order of magnitude to spare. Pre-press snap is the
matching poll frame itself (copied to `a1-pre`), so "press lands on title"
is exposure-proven, not inferred.

### R3 screen chain (snap sha + diff scores per hop; PIL vs p1a)

| Snap (T+) | Size / sha12 | mean/p99 | Content |
|---|---|---|---|
| start (T+92) | 57758 B / `91394ba3abac` | 22.9832/121 | Attract (remote 22.9911/121) |
| a1-now (T+92, pre-Cross) | 58404 B / `67b2f7f9c20a` | 16.5945/148 | Attract |
| a1-poll01 = a1-pre (T+96, pre-Start) | 58339 B / `769c641d640f` | 0.0465/1 T | TITLE (viewed) |
| a1-post3 (T+100) | 50107 B / `d76dc057a28a` | 16.2551/138 | Main Menu (viewed: Single Event highlighted) |
| a1-post8 (T+105) | 50028 B / `624cf85c1f54` | 16.2867/138 | Main Menu |
| a1-post15 (T+112) | 49634 B / `4c56f8159c76` | 16.2622/138 | Main Menu |
| a1-post25 (T+122) | 49839 B / `de8a60455071` | 16.2622/138 | Main Menu |
| menu-stab1 (T+138) | 49926 B / `42ac85486a91` | 16.3871/140 | Main Menu |
| menu-stab2 (T+149) | 49605 B / `f9bd37450a39` | 16.2610/139 (in-script) | Main Menu |
| menu-stab3 (T+159) | 49814 B / `378b1161ebc5` | 16.2610/139 (in-script) | Main Menu |
| menu-stab4 (T+170) | 50067 B / `d602a697704a` | 16.2561/139 (in-script) | Main Menu |
| menu-stab5 (T+181) | 50077 B / `314fe7367cce` | 16.2991/139 (in-script) | Main Menu |
| menu-stab6 (T+191) | 49928 B / `c45d8b3679da` | 16.3011/138 | Main Menu (viewed: still Single Event) |

Menu items visible: Single Event (highlighted), Conquer The Mountain,
Multi Play, Previews, Online; footer `× Select`, `△ Previous`, `○ Options`.

### R3 first-menu arrival (snap + stability N)

| Item | Value |
|---|---|
| Arrival snap | `t27r3-a1-post3.jpg` @T+100 (+3 s after Start-on-title) |
| Stability N | 10 snaps (post3/8/15/25 + stab1–6) spanning T+100→T+191 (91 s) |
| Whole-frame pairwise (PIL) | post8-post15 0.0460/p99 0; post15-post25 0.0271/p99 0; stab1-stab6 0.0552/p99 1; post3-stab6 0.0862/p99 2 (snowfall shimmer only; JPEG shas distinct) |
| In-script whole scores | whole815 0.0403, whole1525 0.0245 (both < 1.0 STATIC gate) |
| Attract reclaim after menu? | none observed in 91 s (all 10 snaps menu, scores 16.25–16.39/138–141) |

### R3 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| TITLE detected by snap | poll01 0.4331/6 remote (gate < 2.0/≤ 10), 0.0465/1 PIL re-score |
| Press lands on title | pre-press `a1-pre` = title frame (viewed), exposure-to-keydown ≤ 0.73 s |
| First menu reached | `a1-post3` Main Menu (viewed), +3 s after Start |
| Menu stable across N | N = 10 over 91 s, pairwise whole ≤ 0.0862/p99 ≤ 2 |
| Full input log + trace sha | `t27r3-poll.log` (every score + press, walls + uptimes) + trace `31d8209c…e501` |

Guest/trace side (R3): ×15 modes; vblanks 397 frozen (all ≤90);
LoadStartModule 18; ERROR 0; `NVRAM has not changed`; tail @191.09. New
vs R1/R2: IOP distinct 155 (R3-only `libsd.006: sceSdGetParam` ×412); EE
sets identical (52). Census: EE 3,477,595 / IOP 8,780,577 syscalls.

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Title detected in-script? | YES (R3 poll01; R1/R2 post-hoc only) |
| Press on title? | YES (R3 Start @T+96, ≤ 0.73 s after exposure) |
| First menu? | YES (Main Menu @T+100, stable 91 s) |
| 1200 s cap | Not reached — longest run R2 ≈ T+220; the 1200 s alternative unexercised (T25 precedent) |
| Chain end | Main Menu, Single Event highlighted, awaiting input |

## T27-5. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t27 R3 (Cross + Start-on-title → menu, T+~200) | 18,555,095 / 1,213,776,079 | `31d8209c…e501` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t27r3.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t27r3-trace-head.txt` 149019 B sha `d6e381d031de…`, `t27r3-trace-tail.txt` 134429 B sha `c888bcb1db0d…`) |
| `emulog-pre-t27-20260920T224654Z.txt` = t27 R1 (3 blind Starts, T+~170) | 18,316,314 / 1,194,941,663 | `dd788742…eda4de` | SSD `…/emulog-t27r1.txt`, same size+sha (match) + committed head/tail (`t27r1-trace-head.txt` 149019 B `a6644132976c…`, `t27r1-trace-tail.txt` 133742 B `6988a1ab3079…`) |
| `emulog-pre-t27-20260920T225352Z.txt` = t27 R2 (3 Crosses + 54 polls, T+~220) | 23,186,595 / 1,516,867,318 | `13e41a85…09dac` | SSD `…/emulog-t27r2.txt`, same size+sha (match) + committed head/tail (`t27r2-trace-head.txt` 149019 B `84b0d78c8534…`, `t27r2-trace-tail.txt` 129379 B `8d4a8e601045…`) |
| `emulog-pre-t27-20260920T223824Z.txt` = t25 Phase 2 (preserved at R1 boot) | 37,793,425 / 2,482,598,052 | `1ba568cc…e15e` (re-verified post-restart: matches T25) | bytesize-only (T25 precedent; SSD holds T25's own copies) |

Channel census (T4 `t4-census.py`, same script): R1 EE 3,395,302 (52
distinct) · IOP 8,319,461 (154) · vblanks 397; R2 EE 3,939,421 (52) · IOP
10,598,848 (154) · vblanks 397; R3 EE 3,477,595 (52, set-identical to R1)
· IOP 8,780,577 (155: +`libsd.006: sceSdGetParam` ×412, R3-only) ·
vblanks 397. Committed per run: `t27r{N}-census.txt`, `t27r{N}-samples.txt`,
`t27r{N}-poll.log`, `t27r{N}-stdout.txt` (full `set -x` shell trace).

## T27-6. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-A …570
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C … rev-parse HEAD; git -C … status --short'   # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; …; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl df -h / /tmp; …'                                    # 914G avail
ssh bytesize 'wsl which python3 xdotool xwd xwdtopnm pnmtojpeg'       # all present
ssh bytesize 'wsl python3 -c "import PIL; …"'                         # ModuleNotFoundError: PIL
ssh bytesize 'wsl which convert compare magick pip3 pip; python3 --version'  # none; 3.12.3
ssh bytesize 'wsl df -h /mnt/c'                                       # C: 58G avail
ssh bytesize 'wsl du -sh …/dat/PCSX2/logs/'                           # 6.8G
# baselines (F3 rec 18): 2 flaps already on VM-A
ssh bytesize 'wsl dmesg' > /tmp/t27-dmesg-pre.txt                     # KILL @38.93/@55.37
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t27-eventlog-pre.txt  # head 18:32:50
# calibration (local; t27-cropdiff.py committed)
python3 t27-cropdiff.py ../T25/t25-post-p1a.jpg ../T25/t25-post-p2a.jpg  # 0.0586/1 (T25: 0.06/0)
python3 t27-cropdiff.py <7 attract> ../T25/t25-post-p1a.jpg              # 20.55–32.30 / 171–222
python3 -c "Image.open(p1a).convert('RGB').save('/tmp/t27-ref-title.ppm')"  # ref 3932177 B b964856a…
# (16-bit + gates verified locally; see §T27-1)
# staging (T25 recipe: scp to C: then wsl cp)
scp t27-auto.sh t27-analyze.sh t27-vcount.sh t27-cropdiff.py /tmp/t27-ref-title.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t27-… /home/brad/pcsx2-t4/'  # + sha re-verify b964856a…
ssh bytesize 'wsl python3 …/t27-cropdiff.py …/t27-ref-title.ppm …/t27-ref-title.ppm'  # 0.0000/0 PPM mode
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-B (restart)
ssh bytesize 'wsl dmesg' > /tmp/t27-dmesg-pre2.txt                     # (VM-B fresh; superseded)
ssh bytesize 'wevtutil …' > /tmp/t27-eventlog-pre2.txt                 # head 18:37:38 (VM-B start)
# R1 (ONE ssh; exit 0; detector blind — maxval bug)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t27-auto.sh' > /tmp/t27-run-stdout.txt  # T27_DONE, up 47→226
ssh bytesize 'wsl bash …/t27-analyze.sh'                              # dd788742…, 18316314 L, census+samples
ssh bytesize 'wsl bash …/t27-vcount.sh'                               # 397 frozen; + counts ×15/0/18; tail
ssh bytesize 'wsl cp …/t27-census.txt …/t27r1-census.txt; …; cp <16 jpg + poll.log + r1 files> /mnt/c/…'
scp "bytesize:pcsx2-t4/t27-…" local/research/T27/t27r1-…              # 16 jpg + log + census/samples
ssh bytesize 'wsl dmesg' > /tmp/t27-dmesg-postr1.txt                  # VM-B flap #3 @241.42 (post-R1)
# R1 post-hoc (local PIL): chain scores, bit-identities (start≡T25, a2-post25≡a3-post25)
# fix 1 (16-bit branch + is_num + SELF_TEST) → re-stage auto+cropdiff; VM-B→VM-C restart (btime …303)
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # dd788742… post-restart match
ssh bytesize 'wsl -u root mount …'                                    # re-mounted on VM-C
# live-fire: Xvfb + xwd + remote 16-bit scoring of R1 PPMs (25.8521/171 attract, 0.40–0.44/5 title ×5)
ssh bytesize 'wsl export DISPLAY=:99; setsid nohup Xvfb :99 …' ; ssh bytesize 'wsl pgrep -a Xvfb'  # PID 440
ssh bytesize 'wsl DISPLAY=:99 xwd -root -out …/t27-livetest.xwd'
ssh bytesize 'wsl python3 …/t27-cropdiff.py …/t27-start.ppm …/t27-ref-title.ppm'      # 25.8521/171
ssh bytesize 'wsl python3 …/t27-cropdiff.py …/t27-a1-post3.ppm …/t27-ref-title.ppm'   # 0.4280/5 (+3 more)
# R2 (ONE ssh; exit 0; global-N bug → 54 polls unscored)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t27-auto.sh' > /tmp/t27r2-run-stdout.txt  # up 110→330
ssh bytesize 'wsl bash …/t27-analyze.sh; …/t27-vcount.sh; counts; tail'  # 13e41a85…, 23186595 L
ssh bytesize 'wsl cp <R2 set incl. 54 polls> /mnt/c/…'; scp … r2polls/ + t27r2-…     # 58 jpg + logs
# R2 post-hoc: 54-poll scores → dwell 15–17 s (table in §T27-3)
# fix 2 (local N) → re-stage auto; VM-C flap @470.86 reverted mount → re-mount; dmesg → prer3
ssh bytesize 'wsl dmesg' > /tmp/t27-dmesg-prer3.txt                    # VM-C flaps @102.43/@345.77/@470.86
ssh bytesize 'wsl -u root mount …'                                    # re-mounted pre-R3
# R3 (ONE ssh; exit 0; TITLE at poll01 → Start → Main Menu)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t27-auto.sh' > /tmp/t27r3-run-stdout.txt  # up 529→730
ssh bytesize 'wsl bash …/t27-analyze.sh; …/t27-vcount.sh; counts; tail'  # 31d8209c…, 18555095 L
ssh bytesize 'wsl cp <R3 14 jpg + poll.log + census/samples> /mnt/c/…'; scp … t27r3-…
# post (VM-C→VM-D restart before dmesg; R3 window effects-verified)
ssh bytesize 'wsl dmesg' > /tmp/t27-dmesg-post.txt                     # VM-D fresh (no R3-window coverage)
ssh bytesize 'wsl ls -la …/logs/; sha256sum …/bios/….nvm'              # rotation chain; da021d2a…
ssh bytesize 'wsl sha256sum <R3 + R1 + R2 + T25 traces>'               # 4/4 post-restart match
ssh bytesize 'wevtutil …' > /tmp/t27-eventlog-post.txt                # C→D + B→C boundaries
ssh bytesize 'wsl head/tail -n 2000 <each trace>' > t27r{N}-trace-{head,tail}.txt     # 6 slices
# SSD copies (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify ×3)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t27rN.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t27rN.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t27rN.txt"         # 3/3 match
# report (chunks; receipts include tail -3)
cp /tmp/t27-dmesg-pre.txt local/research/T27/t27-dmesg-vmA.txt; … (vmB/vmC/vmD, eventlogs, stdouts)
tail -3 local/research/T27/REPORT.md
git add -f local/research/T27/<~119 files by name>                    # ignored dir, forced
git commit -m "[T27] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T27-7. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Main Menu park) | Boot fresh (NVM skips to attract by ≤90 s), Cross attract-skip → detector-TITLE → Start within dwell (R3 recipe, ≤3 attempts) → Main Menu with Single Event highlighted; then a single 534 ms Cross (× Select) to enter Single Event, screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The menu is static (91 s, no reclaim) so no dwell pressure on menu→submenu presses |
| G2 | WSL killer + restarts accelerating (6 flaps + 3 VM restarts) | 6 userland `AcceptAsync` kills this session across 3 VMs + 3 full VM restarts in ~28 min (T25: 7 flaps + 1 restart in 23 min — restart rate 3×). Kill-to-remount 0.2/53.3/27.0/1.2/26.3/34.5 s (0.2 s new minimum; = time-to-next-`wsl`-use per T21). Every run still completed exit 0 in a flap-free window; precautions stand. No toolchain switch made (brief forbids mid-brief); recommendation for a Windows-native-Devel path is tabled, not acted on: if restart/flap rate keeps rising, a native Windows pcsx2-t4 build (no WSL-Xvfb-xdotool chain) would remove the kill surface entirely — needs its own bring-up brief (input injection + capture equivalents) |
| G3 | Windows event log: zero flap entries; boundaries bound all 3 restarts | Newest-30 reads (pre/pre2/post): VM-boundary VmSwitch sequences only across all 6 flaps (precedent stands); creates bound all 4 VM starts, teardown ID sets (71/69/233/234) bound the B→C (18:44:42) and C→D (18:59:31) restarts. `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on all 4 btimes |
| G4 | Hold count 20/20; detector-driven Start first use | 534 ms-class holds register 20/20 across T17c+T19+T21+T23+T25+T27 (12 + 8: R1 534.8/535.5/535.9, R2 536.5/536.0/535.8, R3 535.0/536.1 ms; R3 Start = first detector-driven press-on-title). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title band frozen; menu near-frozen; attract loops | Title text-band pixel-identical across showings (max 0 in 3 run pairs); menu whole-frame ≤ 0.0862/p99 ≤ 2 over 91 s; attract FMV loops (R1 a2-post25 ≡ a3-post25 bit-identical 26 s apart; R1 start ≡ T25 start bit-identical across boots). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the menu run | `WaitVblankStart` stops after log ≤90 in all three T27 runs including the menu-reaching R3 (397 total — menu arrival changes nothing: counts, `LoadStartModule` 18, and EE name sets all R1-identical). The attract/title/menu sync mechanism differs from the menu loop's of T4–T23 — still unmapped (T25 G6 stands) |
| G7 | Menu guest-side correlate: `sceSdGetParam` ×412 (R3-only) | Only called-API delta of menu arrival: IOP set 154 → 155 via `libsd.006: sceSdGetParam` ×412 (sound-param queries, plausibly menu audio init). EE sets identical (52). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~11 GB across 14 emulogs (T17→T27 chain, all preserved); C: 58 G avail. All three T27 full traces SSD-copied + sha-verified (3.9 GB total: `emulog-t27r{1,2,3}.txt`); committed slices only (6 × 2000-line head/tail) |
| G9 | Two detector bugs found by runs, both fixed in-session | (1) maxval-65535 16-bit PPM from game visual (black root was 255) + empty-misfires-as-title → fail-closed `is_num` + 16-bit branch + SELF_TEST; (2) `snap()` global `N` clobbering poll loop → `local`. R3 ran the fixed pair end-to-end. Lesson for followers: SELF_TEST through the real scoring path is necessary but not sufficient — it used the 8-bit ref and could not catch a live-16-bit regression; the R1-PPM remote re-score closed that hole |
| G10 | Session wall | ~37 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T27) |

## Evidence files

`REPORT.md` (this file),
scripts: `t27-auto.sh` (final/R3), `t27-cropdiff.py` (final),
`t27-analyze.sh`, `t27-vcount.sh`;
R1: `t27r1-start.jpg`, `t27r1-a{1,2,3}-now.jpg`,
`t27r1-a{1,2,3}-post{3,8,15,25}.jpg` (16 snaps), `t27r1-census.txt`,
`t27r1-samples.txt`, `t27r1-poll.log`, `t27r1-stdout.txt`,
`t27r1-trace-head.txt` / `t27r1-trace-tail.txt`;
R2: `t27r2-start.jpg`, `t27r2-a{1,2,3}-now.jpg`, `r2polls/t27-a{1,2,3}-poll{01…18}.jpg`
(54 dwell polls), `t27r2-census.txt`, `t27r2-samples.txt`, `t27r2-poll.log`,
`t27r2-stdout.txt`, `t27r2-trace-head.txt` / `t27r2-trace-tail.txt`;
R3: `t27r3-start.jpg`, `t27r3-a1-now.jpg`, `t27r3-a1-poll01.jpg`,
`t27r3-a1-pre.jpg`, `t27r3-a1-post{3,8,15,25}.jpg`,
`t27r3-menu-stab{1…6}.jpg` (14 snaps), `t27r3-census.txt`,
`t27r3-samples.txt`, `t27r3-poll.log`, `t27r3-stdout.txt`,
`t27r3-trace-head.txt` / `t27r3-trace-tail.txt`;
flaps: `t27-dmesg-vmA.txt` (flaps #1–#2) / `t27-dmesg-vmB.txt` (flap #3 +
R1 window) / `t27-dmesg-vmC.txt` (flaps #4–#5b + R2 window) /
`t27-dmesg-vmD.txt` (fresh; R3 window effects-verified),
`t27-eventlog-pre.txt` / `t27-eventlog-pre2.txt` / `t27-eventlog-post.txt`.
Full traces: `/Volumes/Extreme SSD/ps2x-t4/emulog-t27r{1,2,3}.txt`
(1,194,941,663 B `dd788742…` / 1,516,867,318 B `13e41a85…` /
1,213,776,079 B `31d8209c…`, all sha-verified, NOT in git) + bytesize
originals `…/logs/emulog-pre-t27-20260920T224654Z.txt`,
`…-225352Z.txt`, `emulog.txt` (same, re-verified post-restart 4/4 with
preserved T25 `…-223824Z.txt` `1ba568cc…`).
