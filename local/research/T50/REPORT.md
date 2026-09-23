# T50 REPORT — PCSX2: dest-0 MPG payload sources + D1 kick sites (E40 redirect x2)

Brief `local/muse/prompts/T50.md` + orchestrator redirect #1 (drop tag-write
watch; EE read watch on 0x4349b8/0x435bf8) + redirect #2 (reads are DMA-only;
log MPG-imm0 payload source + D1 reg writes instead). Tables + receipts; the
orchestrator decides. Read first: `AGENTS.md`, `local/research/T49/REPORT.md`,
`local/muse/prompts/E40.md`.

## T50-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Bounded log-only patch(es), same tree | DONE — hook1 (srcread, 9 hunks, 1 file) + hook2 (mpgpay/dmareg/free-gate, 8 hunks, 5 files) |
| 2 | Build ≤2 | DONE — 2/2, both clean first try |
| 3 | Capture over settled SC (T49 route/point) | DONE — boot1 (rec, route verbatim, F1 state, dump, F8) + boot3 (interp, statefile, free-gate, F8) |
| 4 | mpgpay table: dest-0 payload src per upload | DONE — 2000 lines, 2 distinct src, cap at vsync 1396 |
| 5 | dmareg table: D1 writes with pc/regs | DONE — 256 lines, TADR+CHCR only, cap at vsync 1127 |
| 6 | srcread on 0x4349b8/0x435bf8 | DONE — 0 hits, gate proven open (convergent with E40: DMA-only) |
| 7 | Preservation as T48/T49 | DONE — replay 7/7 + HWSTAT exact; ref-identity + populations |
| 8 | Receipts + `[T50]` commit, no push | DONE (this file) |

Headline for the E-brief: PCSX2's dest-0 MPG payloads come from **two** live
regions, **src=0x00435be0 (tag 0x435bd0, x1334)** and **src=0x004349a0 (tag
0x434990, x666)** — each exactly **0x18 below** the two E40 addresses
(0x435bf8, 0x4349b8). The +24 B head is VIF packet header; microcode starts
+24. No EE load touches either window (srcread=0, gate live). D1 is kicked
from pc **0x382a08** / **0x382adc** (ra 0x382938 / 0x3827e8), TADR-only +
CHCR=0x185 (chain/STR/TIE, TTE=0); MADR/QWC are tag-driven, never EE-written.

## T50-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T49-end, + T50 hooks below |
| Pre-T50 SHAs | RI `a5da8976…8000`; (hook2 pre) RI `99f4fb14…`, V1D `681d80c6…`, VC `ab0d5a86…`, MF `1e742bde…`, DM `93761abc…` |
| Build-1 bins | qt `55448a12…`, gsrunner `b31c284a…` (1 TU, no warnings) |
| Build-2 bins | qt `e537bd71…`, gsrunner `fd394458…` (5 TUs, no warnings) |
| Patch | `t50-patch.diff` 350 lines, sha256 `c3ce63a7…87e27` (5 files, all log-only) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t48` (T48 verbatim); `dat-t50` = dat-t48 + `EnableEE=false` (34 MB trimmed) |
| State | `SLUS-20772 (08FFF00D).01.p2s`, 6,896,106 B, saved at settled SC in boot1 |
| boot1 (rec) | `T48_DUMP_QUEUED vsync=19026`, dump `.gs.zst` 1,266,474 B, F8 201,565 B, emulog 1,158,633,030 B |
| boot3 (interp) | free-gate PATHS 1455..1985 (1986 lines), F8 202,094 B, emulog 85,460,105 B |
| boot3 trace | `t50c-trace.txt` 261,076 B sha256 `919e6f14…25e5be`: mpgpay 2000 + dmareg 256 + srcread 0 + 2 CAPs, 0 rejects |

Builds 2/2. Boots: boot1-fail (F1-path bug, pre-trigger) + boot1 + boot2
(failed, §T50-6) + boot3 — 4 boots, overrun declared; redirects authorized
the extra logging + recapture. Bytesize new bytes ≈ 1.6 GB of 5 GB cap.

## T50-2. The patch (hook1 + hook2)

Hook sites (all log-only, all gated):

| Hunk | File:anchor | What |
| --- | --- | --- |
| T50-D0/LW/LWU/LWL/LWR/LD/LDL/LDR/LQ | `R5900OpcodeImpl.cpp` EE interp loads | `t50_read_watch(addr, 4/8/16)` after the memRead; srcread on overlap with the two 16 B windows, first 64 hits per region |
| T50b-RI0/RI1 | same file, hook-1 gate | `/tmp/t50-free` fallback: armed + free ⇒ open (no winstart needed) |
| T50b-VD0 | `Vif1_Dma.cpp` | decls + gate + `t50b_tag_tap` + `t50b_mpg` + `t50b_dmareg` |
| T50b-VD1 | same, after `VIF1 Tag` log | silent chain-tag tap `(tadr, ID, MOD)` per tag setup |
| T50b-VC0/VC1 | `Vif_Codes.cpp` MPG pass1 | `if (idx==1) t50b_mpg(code)` where transfer proceeds |
| T50b-MF0 | `Vif1_MFIFO.cpp` | same tap at the MFIFO tag site (drain path not distinguished, §T50-7.2) |
| T50b-DM0 | `Dmac.cpp` past `allow_write` | `t50b_dmareg(mem, value)` on applied writes; D1 addrs only |

Line formats (emulog channel, `%08x` GPR low 32, `vsync` decimal):
`mpgpay vsync=<n> imm=0 num=<raw byte, 0⇒512 words> src=0x<raw>&0x<masked>
mode=<chain:id|normal> tag_at=<0x...|->` (raw = vif1ch.madr at command).
`dmareg vsync=<n> reg=<D1_CHCR|D1_MADR|D1_QWC|D1_TADR> value=0x<> pc=0x<>
ra=0x<> a0=%08x … s7=%08x`. `srcread` same GPR list + `addr=0x<phys unit>
size=<4|8|16> fn=-`. Gate: `/tmp/t50-arm` + (free file OR (T48 window +
winstart)). Caps: mpgpay 2000, dmareg 256, srcread 64/region (all +CAP once).

Derivation notes. src is the DMA fetch pointer at MPG pass1: at command
time madr sits at/just past the MPG code word (prefetch/FIFO overshoot at
most hundreds of bytes); the payload follows immediately, so src locates
the ~2 KB payload region — the two candidate bases are 0x1240 apart with
disjoint payloads, and D1_TADR/tag arrays (§T50-5) anchor exact bases
independently. mode/tag_at come from the tap (sequential single-threaded
processing: a tag's stream, incl. its MPG pass1, completes before the next
setup; NORMAL-mode MPGs print `normal/-` via the MOD check). pc/ra/GPRs are
exact under the EE interpreter (boot3 `EnableEE=false`).

## T50-3. Patch proof

hook1: 9/9 anchors asserted first try; 1-TU build, no warnings; 151-line
diff. hook2: applier validates all 8 anchors before writing (all count==1
first try); 5-TU build, no warnings. Full diff 350 lines,
`t50-patch.diff` sha256 `c3ce63a7…87e27`, generated as tree-minus-base for
exactly the 5 touched files. Pre-patch SHAs in §T50-1. No renderer, EE,
timing or content change: counters + gated `Console.WriteLn` only; interp
hooks never execute under the recompiler.

## T50-4. Preservation (two legs, as T48/T49)

Leg 1 — deterministic replay (build-2 gsrunner on the G13 rich dump):
**7/7 PNG md5s match the T48 §T48-1 pins exactly** (`b7a3e8db a7929218
bb8b1d85 817e934f ×2 85cf3599 ×2`) **and HWSTAT matches exactly** (791
draws / 37 passes / 0 barriers / 14 copies / 320 uploads / 6 readbacks).
Zero T50 lines in the replay emulog.

Leg 2 — live frames: boot1 SC F8 (build-1, rec) and boot3 SC F8 (build-2,
interp, PATHS-gated endpoint); ref-identity vs T47 SC (boot1 SCPRE 0.5878–
0.6045, boot3 LOADED 0.5255–0.5455, all < 2.0). Content: T48_VU1 = 5499 in
boot1 (== T49 run-2 exactly); T49 3 BEGINs re-fire with byte-identical
vi-entry; interp PATHS census == T48 exactly (603 pkts / 724,128 B,
p2 = p3 = p0 = 0). No same-binary armed/unarmed pair (capture budget;
hooks are gate-latched + interp-only, replay + populations cover it).

## T50-5. The traces

boot1 (rec): srcread = 0 (hooks silent, as designed); T48_VU1 5499;
T49 BEGINs 0x257 @19027 + 0x2/0x8 @19028, vi-entry identical to T49.

boot3 (interp, free-gate, PATHS 1455..1985): `t50c-trace.txt` holds 2000
mpgpay + 256 dmareg + 0 srcread + 2 CAPs, 0 grammar rejects.

| src (masked) | tag_at | mode | num | n | share |
| --- | --- | --- | --- | --- | --- |
| 0x00435be0 | 0x435bd0 | chain:6 | 0 | 1334 | 2/3 |
| 0x004349a0 | 0x434990 | chain:6 | 0 | 666 | 1/3 |

src == tag_at + 0x10 on all 2000 lines (payload follows the 16 B chain
entry). 6/vsync steady (4 + 2), mirror-vsyncs 1063..1396 (334), cap at
1396. 1328/2000 are adjacent duplicates (same vsync/src/tag: pass1 re-fire
on the waitforvu stall path — same stream position, not two MPGs).

| reg | values x n | pc | ra |
| --- | --- | --- | --- |
| D1_TADR | 0x7091e0 x32, 0x63c560 x32 | 0x382a08 | 0x382938 |
| D1_TADR | 0x7096f0 x32, 0x63ca70 x32 | 0x382adc | 0x3827e8 |
| D1_CHCR | 0x185 x128 (64 + 64) | 0x382a10 / 0x382ae0 | 0x382938 / 0x3827e8 |

No D1_MADR/D1_QWC writes anywhere (chain mode: tag-driven). 4/vsync
(2 TADR + 2 CHCR), vsyncs 1063..1126 (64), cap at 1127. Full GPRs on every
line in the trace (e.g. TADR kick: v0 = written value, s1 = 0x10009000,
s4 = 0x10009030).

srcread = 0 with the gate verifiably open (mpgpay + dmareg fired under the
same gate in the same run) — convergent with E40 Part 2 (zero EE loads of
the heads in the recomp): the bytes reach VIF by DMA only.

## T50-6. boot2 failure forensics (no data)

boot2 (interp, statefile) verified SC (LOADED 0.5455) then died in the
dump-queue poll with zero gated lines. Two independent causes: (a) the GS
trigger requires `!g8_dump_queued`, and the G13 auto-dump fires on the
first heavy post-load frames, consuming the one-shot — the script trigger
is ignored by design (starvation, not timing); boot3's free-gate
+ PATHS-gating was built for exactly this. (b) The ssh transport died
mid-poll (orphaned session, remote tree reaped: no emulator/Xvfb, emulog
ends 148.5 s wall, 5200 ungated PATHS, zero gated lines). Lesson: touch
arm/free files pre-boot AND gate F8 on ungated PATHS numbers, never on the
dump one-shot under statefile.

## T50-7. Gaps, overruns, lessons

1. Builds 2/2. Boots 4 (fail + boot1 + boot2 + boot3) vs ≤2 captures —
   declared overrun; both redirects authorized new logging + recapture.
2. Caps truncate the window (mpgpay 2000 @1396, dmareg 256 @1127); the
   FREE window runs to PATHS 1985. Distinct counts (2 srcs, 4 TADR values)
   are stable across the logged span, but a wider window needs a recapture.
3. EE mirror vsync = PATHS index − 392, same ~21/s rate, constant all run
   (artifact of the statefile boot, not chased; ordering intact).
4. Chain vs MFIFO drain not distinguished in `mode=` (one shared tap flag;
   id 6 = PCSX2 TAG_RET, E40 labels it CALL).
5. srcread covers LW/LWU/LWL/LWR/LD/LDL/LDR/LQ only (no byte/halfword, no
   COP loads); physical = addr & 0x1FFFFFFF (kseg0/raw; TLB-mapped access
   would miss — E40's independent zero agrees).
6. dmareg covers applied D1 writes only; CHCR/MADR/QWC/TADR scope (MADR/QWC
   never EE-written in chain mode — expected).
7. No mpgsrc lines (redirect dropped them after E40's inline finding).
8. Bytesize new bytes ≈ 1.6 GB of 5 GB; mini/lane budgets clean.

## T50-8. Exact commands

Bytesize (single-quote pattern; scripts via scp to `pcsx2-t4/t50stage/`,
run from `/home/brad/pcsx2-g7/`): `t50-hook.py` → `t50-apply.sh` →
`t50-build.sh` → `t50-replay.sh` → `t50-capA.sh` (route + F1 + dump + F8)
→ `t50-setup.sh` (dat-t50, EnableEE=false) + `t50-trim.sh` → `t50-capB.sh`
(failed, §T50-6) → `t50-hook2.py` → `t50-apply2.sh` → `t50-build2.sh` →
replay → `t50-capC.sh` (free-gate + PATHS F8) → `t50-extract.sh <emulog>
<trace>` → `t50-analyze.py <trace>`. Full patch: tree-minus-base over the
5 files. No P-lane lease (bytesize-only lane); bytesize idle at each heavy
step; never push.

## T50-9. E40 cross-check (read ~05:40, after §0–8)

E40 Part 3/4 (same formats, E33-route ticks 1300–1319) vs T50 boot3:

| Fact | E40 (1300–1319) | T50 boot3 | Join |
| --- | --- | --- | --- |
| dest-0 srcs | one: 0x435bf8 | 0x435be0 x1334 + 0x4349a0 x666 | T50.src + 0x18 == E40.src (their walker skips 24 B VIF headers; 0x4349a0 + 0x18 == 0x4349b8 exactly) |
| tag | 0x435bd0, chain:6 | 0x435bd0 + 0x434990, chain:6 | same tag for the 0x435b uploader |
| kick fn / ra | sub_382760 / 0x382938 | same fn, ra 0x382938 + 0x3827e8 | same uploader |
| store pcs | 0x382a04/0c + 0x382ad8/dc | 0x382a08/10 + 0x382adc/e0 | systematic −4 (anchor convention; fn+ra+values identical) |
| TADR values | 4 rotating slots | 4 rotating slots, other values | arenas rotate per frame; same regions |
| EE loads | 0 | 0 | DMA-only confirmed both lanes |

Open: (a) E40 sees only the 0x435b source (4/vsync) where T50 sees 0x435b
+ 0x4349 (4+2/vsync) — screen/time (their ticks vs settled SC) or filter
difference; (b) the uniform pc −4 needs one codegen look, not a capture.

## T50-10. Receipt paths + recommendation

Repo (this commit): `local/research/T50/` — REPORT.md, `t50-patch.diff`
(350 lines, exact), hook/apply/build/setup/cap/replay/extract/analyze
scripts, traces (boot1: trace + vu1 + t49retrace + F8 + poll; boot2 poll
only; boot3: trace + F8 + poll). Workdir `~/dev/ssx3-work/T50/` holds the
same + probes. Share mirror `/Volumes/share/ssx3/ps2x-t50/`: REPORT +
patch + boot3 trace + both F8s. Bytesize residue under cap: hooks, caps,
`dat-t50` (34 MB), dumps/emulogs/states, `t50-frames` (replay PNGs).

Recommended next action (orchestrator): join on T50.src + 0x18 == E40.src
(0x435be0→0x435bf8, 0x4349a0→0x4349b8), kick pcs into sub_382760 (T50 pcs
are the HW-store `sw`s; E40's −4 are the adjacent `lw`s — same kicks),
tag arrays rotate per frame (re-key per boot). No further T-lane work
queued by this brief.