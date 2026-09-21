# E7 — CPU VIF1 ingress joins production, display VRAM, and Present

**Selected outcome (i): the guarded values confirm J2a-fixed, and the
missing CPU VIF1 FIFO ingress is the demonstrated copy-consumption gap.**
The generic ingress fix reaches the requested meaningful-frame boundary:
the same P→D packet enters the GS, fbp112 contains the producer's
memory-card-check message, and Present returns that D surface faithfully
under the guest-selected field mode. Three of four authorized boots used;
no further boot or second fix. This is an E-lane finding, not a claim of
menu/gameplay completion or a panel gate decision.

Review the actual [host frame](e7c-upload-latest.png), the independently
decoded [D surface](e7c-display.png), and [P surface](e7c-producer.png).
The complete compact join is [e7-join-receipt.txt](e7-join-receipt.txt).

## 1. Contract, hypotheses, and stop rules

[CONTRACT.md](CONTRACT.md) records the initial contract before E7a and
the subsequent authorized reframe before E7b. EF was committed first as
`c8727de` and gated/pushed by the orchestrator. E6 `57e1afb` was read in
full. E7a had already completed under the original address-discovery
brief when the copy/FIFO-first reframe arrived. The later scope expansion
explicitly authorized runtime implementation and up to four total boots.
Timebox began by 04:13:16Z on 2026-09-21; deadline 10:13:16Z.

| Hypothesis | Observable / discriminator | Action selected by observation |
|---|---|---|
| H-S / H-fixed | Same-run singleton at 0x4a289c; M=1, A=P=0, B=D=112, continuous C, writer-attributed G. | Accept candidate fields only after same-run S guard. Unexpected values select (ii), E6 §8 residual; stop implementation. |
| H-copy | The display call builds P→D and reaches helper 0x371940 / return 0x383740 with a complete packet. | Join guest call to FIFO command, DMA bytes, and actual GS entry. |
| H-FIFO | A decoded VIF stream leaves mask=1; CPU unmask fails to change it; identified copy enters retained PATH3 queue. | If confirmed, implement generic ingress. Mask=false throughout falsifies H-FIFO: stop and follow the first demonstrated missing edge. |
| H-fix | CPU unmask reaches the interpreter; same packet reaches GS; D holds expected content; Present reads D. | Stop at this boundary. If copy still unconsumed after ingress, table it without stacking fixes. |
| H-measurement | Complete reserved boundary, singleton guard, burst ordinal, packet identity and tails. | Unalignable/truncated observation selects (iii): repair measurement only. |

Every boot required the shared P-lane lease; release followed process exit
and an O(1) rename protecting the closed default function log. Analysis
and compression ran lease-free. No regeneration, adb, upstream push, or
generated-runner staging. `COPYFILE_DISABLE=1` was set on SSD steps.

## 2. Preflight, caps, and boot accounting

The T13 pre-claim shape is retained in `e7{a,b,c}-preflight.json`: lease
absent, `pgrep -x ps2EntryRunner` exit 1 before and after checks, binary
hash/size pinned, ISO/ELF sizes, both ELF hashes, SSD/internal free space,
wait-log tails, trace-aligner selftest, and suite green before claiming.
There were no lease waits. [e7-waits.log](e7-waits.log) contains all three
claims/releases; [e7-final-state.json](e7-final-state.json) confirms the
lease absent and runner absent after E7c.

| Boot | Fork / suite | SSD / internal free | Claim → release (UTC) | Runtime / binding condition |
|---|---|---|---|---|
| E7a | a13b66a / 448 of 448 | 436 / 15 GiB | 04:21:10.400 → 04:21:32.971 | 22.554 s; span+10 s; SIGTERM; rc=0 |
| E7b | 8480800 / 449 of 449 | 425 / 13 GiB | 04:39:40.959 → 04:40:06.705 | 25.702 s; span+10 s; SIGTERM; rc=0 |
| E7c | 4acc59f / 452 of 452 | 424 / 11 GiB | 04:58:49.654 → 04:59:32.021 | 42.245 s; span+10 s; SIGTERM; rc=0 |

Trace-aligner selftest: 35 checks / ALL PASS before each boot. ISO size
3,005,415,424 bytes; both ELF copies 3,890,784 bytes, SHA256
`1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`.

| Bound (per boot) | Limit | E7a at binding poll | E7b | E7c |
|---|---:|---:|---:|---:|
| Wall | 600 s; TERM at 585 if needed | 21.938 s | 25.531 s | 41.720 s |
| Progress | 1,000,000 syscall lines | 73,594 | 81,741 | 53,022 |
| Boot log | 838,860,800 B | 3,466,991 | 6,958,659 | 4,369,353 |
| Syscall trace | 67,108,864 B | 4,402,630 | 4,889,500 | 3,169,271 |
| Function log | 536,870,912 B | 207,920,888 | 221,491,786 | 173,549,965 |
| E4 directory | 12,582,912 B | 8,483,975 | 8,484,282 | 8,503,174 |
| Frame directory | 33,554,432 B | 118,272 | 118,277 | 132,726 |
| Park directory | 33,554,432 B | 0 | 0 | 0 |
| E7 tap directory | 8,388,608 B | absent | 925,651 | 1,122,456 |
| Aggregate | 1,073,741,824 B | 224,392,756 | 242,868,155 | 190,846,945 |

Polling was 250 ms; liveness/bytes every 5 s. No wall, progress, or byte
cap bound. Per-boot `*-liveness.txt` and `*-result.json` retain the stop
poll and cleanup. Closed raw sizes/hashes are in `*-retained.json`; the
small termination tail is included (largest closed function log:
221,686,492 B). No fourth boot was needed.

| Runner | Bytes | SHA256 |
|---|---:|---|
| E5/E7a baseline | 160,817,056 | e21ab7077496cdb312cdefa147da4fb6afadd52dba1f6f0cee709d75bb026330 |
| E7b observation | 161,313,936 | e7e95d7dcc380752c19697ba0948eaf1b01504220d2c03143c4e3eb33e61c3f4 |
| E7c fixed | 161,313,936 | 4f02b144a8de09622f66aa81533097d5b7777eaf63ffab3abe80f8e73fafa290 |

## 3. S identity, field values, G sequence, and E5 burst join

The factory writes **S=0x61ba60** to global **0x4a289c** at PC
**0x22697c**, thread 1, RA=0x226978, in all three runs. Each run has one
identified singleton store and no teardown-null store. Raw boot lines:
E7a 186; E7b 223; E7c 196. Candidate field addresses were guarded by that
same-run publication in both E7b and E7c.
S is the `PS2GraphicsMan` heap object identified by E6's factory trace;
E7 validates its numeric address without changing allocation or fields.

| Field | Address | E7b / E7c value receipt |
|---|---|---|
| A, S+0x5a78 | 0x6214d8 | 0; initialized at 0x37c004 |
| B, S+0x5a7c | 0x6214dc | 112; initialized at 0x37c018 |
| P, S+0x5a84 | 0x6214e4 | 0; display writer 0x382b64 |
| D, S+0x5a88 | 0x6214e8 | 112 after first pick; writer 0x382b68 |
| C, S+0x5a74 | 0x6214d4 | 561 consecutive increments 1..561; pre-value+1 equals store value |
| G, S+0xf44 | 0x61c9a4 | 0 at all 561 display entries; constructor store 0 at 0x369370 |
| M, S+0x59e8 | 0x621448 | initialization 1 at 0x375fbc; 1 at all 561 display entries |

The first pre-increment snapshot at tick 41 has D=0 before the first
display pick; this is initialization, not a value surprise. All 560
subsequent entry snapshots have `(A,B,P,D)=(0,112,0,112)`. H-pair holds.
Calls 2..561 occur once per tick 44..603. At ticks 599..603, calls
557..561 all have G=0 and M=1, so each picks P=0/D=112. No observed G=1
writer follows singleton publication in the complete tap interval.
This measures zero skip decisions; it does not establish a unique
fp-user entry rate. G has multiple possible setters, and a routine could
enter without reaching its G store.

| Series | Total grouped DISPFB1 bursts | Boundary burst | Value / PC / RA / thread | Matching complete display/helper entries and exits |
|---|---:|---:|---|---:|
| E5 | 1,466 | 558 (line 8886; approximate tick 597) | 0x9070 / 0x382cf0 / 0x382824 / 5 | See E5 receipts |
| E7a | 1,244 | 558 (line 8611) | same | 1,244 each |
| E7b | 1,395 | 558 (line 21345) | same | 1,395 each |
| E7c | 862 | 558 (line 21551) | same | 862 each |

E7b/c call 558 is exactly tick 600 in the ordered tap. E5's `tick~` is a
nearby diagnostic stamp; the join key is burst ordinal, not that stamp.
All runs re-match the five written display fields: PMODE steady 0xff21,
SMODE2=1, DISPFB1=0x9070, DISPLAY1=0x1bfa0002032281, BGCOLOR=0. DISPFB2
and DISPLAY2 have no writes in these series. The boot PMODE is 0xff20.
Different total burst counts reflect different run durations/progress.

P1f eight-byte watch windows overlap and some MMIO stores emit twice.
`e7_mine.py` retains multiplicity; it does not call every emitted line a
guest store. Whole-console damaged lines are 14/100/20 for a/b/c; **zero
damaged lines fall inside any 600→601 window**. Separate ordered taps
have consecutive sequence IDs and complete, untruncated tails. The
function-log census independently matches every total above.

## 4. H-FIFO forcing receipt before the fix

The display function loads M at 0x382e78 and gates its copy prefix at
0x382e7c; submission calls 0x371940 at 0x383738. This M!=0 copy tail is
live. E7b identifies the
last interpreted mask setter at **seq 1544, tick 118**, command
0x06008000, old=0/new=1, stream offset 1388. Earlier boot clears had
flushed 77 packets in total; the claim is not that no packet ever flushed.
No further interpreted clear occurs through the complete tick-603 tail.

| E7b tick-600 seq | Interface | Receipt |
|---:|---|---|
| 10235–10237 | Display call 558 | C=557→558; G=0/M=1; P:=0; D:=112 |
| 10238 | CPU SQ at 0x3719a4, RA=0x383740 | FIFO 0x10005000 payload `[06000000,0,0,0]`; mask=1 |
| 10239–10240 | FIFO memory before/after | mask remains 1; queue remains 481 |
| 10241 | GIF start | MADR=0x4ffcc0; QWC=106; CHCR=0x101; mask=1 |
| 10242–10243 | DMA / PATH3 queue | 1,696 identical bytes; FNV64=0x767aae0fde3c567f; retained |
| 10244 | DMA completion | STR=0/QWC=0, while queue grows to 482 |
| same window | GS entry / history | No matching 1,696-byte packet; no FRAME2 suffix; zero draws to D |

The same missing GS delivery is observed for all five copies at ticks
599..603. Other GS packets arrive, so the observation distinguishes
this copy from a general lack of GS activity.

| Decoded packet item | Receipt, identical before and after fix |
|---|---|
| Packet identity | 1,696 B; SHA256 `79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31`; parse consumes all bytes |
| Prefix | offset 0 tag 0x100000000000000b; 11 packed A+D writes |
| Destination | FRAME1 offset 16 = 0xff00000001080070; FBP112, FBW8, PSMCT24 |
| Source | TEX0 offset 48 = 0x268020000; TBP0, TBW8, PSMCT32 |
| Copy strips | offset 224 tag 0x4400000000000011; 17 sprite pairs |
| Mandatory suffix | offset 784 tag 0x1000000000008010; FRAME1 restore at 800; FRAME2 at 816 |

This closes the causal condition required to implement the ingress fix:
the guest submits the copy and its unmask command, but the CPU FIFO write
falls through generic I/O splitting. DMA completion alone had concealed
retained, unconsumed GS work.

## 5. Generic fix and validation

`PS2Memory::write128` now sends a complete aligned CPU quadword in the
translated physical **0x10005000–0x10005fff VIF1 FIFO aperture** to the
existing VIF1 interpreter once, before generic I/O splitting. Existing
KSEG translation and alignment handling remain in force. The change
contains no SSX3 address, forced mask clear, FBP override, or scheduling
change. The interpreter supplies MSKPATH3 and queue-order behavior.

[ARCHITECTURE.md](ARCHITECTURE.md) defines the width/aperture contract and
records the primary implementation cross-check against PCSX2's
[HwWrite.cpp](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/HwWrite.cpp).
Complete 128-bit stores are the implemented scope; narrower-store
semantics remain unchanged, since the reference itself labels their
zero-fill behavior as an assumption. No reference-emulator code copied.

| Change | Exact fork files |
|---|---|
| Generic ingress implementation | `ps2xRuntime/src/lib/ps2_memory.cpp` |
| Ingress and ordering regressions | `ps2xTest/src/ps2_memory_tests.cpp` |
| Prior observation-only tap | `ps2xRuntime/include/ps2_e7.h`; memory/runtime/VIF1 sources; `ps2xRuntime/src/lib/gs/gs_frontend.cpp`; cap-budget test |

| Test | Before ingress | After ingress |
|---|---|---|
| CPU mask and all four command words in order | fails | passes |
| Interpreted-stream mask → two queued PATH3 packets → CPU unmask → later normal GIF DMA; no replay | fails | passes |
| Full aperture/KSEG aliases; RAM, neighboring FIFO, and display MMIO isolation | fails | passes |
| Entire suite including these three tests | 449 passed / 3 failed (452 total) | 452 passed / 0 failed |

Builds used `-j4`, targets `ps2x_tests ps2EntryRunner`; no regeneration.
The fresh E7c preflight re-ran the 452-test suite successfully. Retained
`e7-ingress-{before,after}-{build,suite}.txt` and source/patch receipts
make the fail-before/pass-after comparison reviewable. No additional
runtime fix was applied after this one.

## 6. E7c: packet → D VRAM → faithful Present

| E7c tick-600 seq | Interface | Receipt |
|---:|---|---|
| 12313–12315 | Display call 558 | Same guarded C/G/M/A/B/P/D values as E7b |
| 12316–12317 | CPU SQ / FIFO before | Same unmask command; mask=1, queue=0 |
| 12318–12319 | Interpreter / FIFO after | MSKPATH3 old=1/new=0; route=interpreter; queue=0 |
| 12320–12322 | GIF start / DMA / PATH3 send | Same MADR/QWC/CHCR and same 1,696 bytes; mask=0 |
| 12323 | GS entry | Same byte count, FNV64, and leading tag |
| 12324 | DMA completion | STR=0/QWC=0, queue=0 |
| 12325–12328 | Following worker CPU mask | 0x382980 command 0x06008000 now correctly sets mask=1 |

Five-of-five boundary copies reach GS: tick 599 seq 12273; 600 seq 12323;
601 seq 12373; 602 seq 12423; 603 seq 12473. All five saved packet files
are byte-identical to the corresponding E7b files. The full trace still
contains 862 completed display calls and copy helpers.

| Boundary observation | E7b before | E7c after |
|---|---:|---:|
| Complete E4 history events | 228 | 287 |
| GIF tag events (not packet count) | 46 | 52 |
| Register events | 59 | 80 |
| Draw events / draws to fbp112 | 122 / 0 | 155 / 17 |
| FRAME2 suffix events | 0 | 1 |
| P nonblack RGB pixels, 512×448 | 12,563 | 12,563 |
| D nonblack RGB pixels, 512×448 | 0 | 12,358 |
| Latest host nonblack RGB pixels | 0 | 12,398 |

E7c history seq 1 is the copy's 11-loop tag; seq 2 sets FRAME1 to 112;
seq 3 sets TEX0 to P; seq 13..29 are its 17 strips. Thus D's content is
joined to the intended source and packet, rather than merely inferred
from a changed host image. Independent VRAM decoding shows the same
memory-card-check text in P and D. The measured D RGB image equals
P(x+1,y+1), black outside the source, with **zero differing pixels over
the full 512×448 result**. Packet geometry carries half-pixel endpoints;
the measured sampling offset is recorded, not asserted to be hardware
pixel-perfect. This task does not change rasterization or text layout.

The raw D image is not equal to an interlaced host upload. Captured
PMODE=0xff21 selects CRT1; DISPFB1=0x9070 selects FBP112/FBW8/PSMCT24;
SMODE2=1 selects field presentation. Applying its even/odd row-pair
selection to the independently decoded D gives these exact receipts:

| Output | Receipt |
|---|---|
| Frozen VRAM SHA256 | `532288fdaa9cf5e2aa43f628dd9975b4f7cdecf12ac8beac7fdd8897ac4c78e5` (arm and freeze equal) |
| Raw D RGBA SHA256 | `4a7d98177597f60731c8b0ab5ce83f9c412f2d5f871c1f196526ef599b033243` |
| Odd field | FNV32 0xf818f78d; matches uploads at ticks 599, 601, 603 |
| Even field | FNV32 0xa9301e2d; matches upload at tick 602 |
| Latest host, tick 904 | decoded RGBA equals predicted even field **byte-for-byte**; SHA256 `dcf04c111bad677bfaa1805ce142cfa05d5fd9c87179816d0b34684f3820080d` |
| Host PNG file SHA256 | `548e60a2478052255c33e03b7338f495f8a1b91d539daf20cf63b1ea02743aa5` |
| Host selection | displayFbp=112, sourceFbp=112, preferred=0, fallback=0 |

The latest PNG is a later retained upload, not labeled as the tick-601
file. Both boundary parity hashes and the full later pixel comparison
agree with the frozen surface. [e7c-frame.json](e7c-frame.json) retains
the raw mismatch as well as the correctly field-transformed match.

## 7. Parking answer, challenged premises, and one next action

| Question / premise | Finding and forcing receipt |
|---|---|
| What should clear M? | Nothing needs to clear M for this join. M=1 is a fixed-pair copy mode; it both picks A/B and enables the copy tail. It remains 1 in the successful run. |
| What should re-fire the blit? | The guest already re-fires it on each completed display call. Full function counts and packet records establish this directly. |
| Where was work parked? | In the emulator's masked PATH3 queue after a real interpreted mask setter. CPU SQ unmask was lost before VIF decoding; E7b queue 481→482 despite DMA completion. |
| Is D stuck at 112 the black-screen cause? | Fixed D persists after the frame appears. The missing edge was packet consumption, not compulsory buffer alternation. |
| Does this reopen raster/Present? | The intended packet now draws D, and Present exactly matches D with selected field processing. No additional raster/Present fix follows. |
| Does the memory-card message prove a SIF/CD dependency? | No. It identifies visible guest content only; no storage/scheduler cause is promoted from this image. |

Exactly one outcome is selected: **(i)**, values confirmed and parking
named, with the additionally authorized implementation and complete
join demonstrated. Outcome (ii) was not selected: M/pairs did not
surprise. Outcome (iii) was not selected: the causal window and ordered
tails are complete despite identified non-boundary console interleaving.

**One next action:** orchestrator gate this E7 evidence with fork
`4acc59f` as the demonstrated P→D→Present baseline. E7 stops here;
further guest progression requires a separately scoped next brief.

## 8. Commits, reproduction, retention, and limits

| Repository | Commit | Disposition |
|---|---|---|
| Fork, observation taps | `8480800d475ffa9ffc3f651cd42663f00cf6a0be` | pushed to `fork/ssx3` |
| Fork, generic fix + regressions | `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2` | pushed to `fork/ssx3`; remote SHA verified |
| ssx3, E7 evidence | enclosing `[E7]` commit | no ssx3 push; orchestrator owns gate/push |

Fork remote is `https://github.com/brad-richardson/PS2Recomp.git`.
The preexisting modified generated `register_functions.cpp` was left
unstaged. Fork status after both commits contains only that existing
change. Git emitted warnings for a preexisting AppleDouble pack-index
sidecar, but commit/push/remote verification all exited 0; no broad
sidecar cleanup was performed. Build logs retain the duplicate-library
link warning. Neither condition blocked the verified artifacts.

Exact capture/build entry commands (historical; **do not re-run boots**):

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E7/e7_capture.py a
cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4
python3 -B local/research/E7/e7_capture.py b --s 0x61ba60
cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4
python3 -B local/research/E7/e7_capture.py c --s 0x61ba60
```

The second build line represents the final ingress rebuild; the retained
before-fix test build is also in `e7-ingress-before-build.txt`. Test binary
is `/tmp/p1-link/runtime/ps2xTest/ps2x_tests`, run from the fork root.
`e7{a,b,c}-config.json` records exact runner argv, working directory,
watch list, all PS2X variables, and caps. `*-build.json` / preflight
records pin each executable, including test SHA/size.

Offline reproduction from retained evidence (rewrites derived receipts):

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E7/e7_mine.py a
python3 -B local/research/E7/e7_mine.py b
python3 -B local/research/E7/e7_mine.py c
python3 -B local/research/E7/e7_frame.py b
python3 -B local/research/E7/e7_frame.py c
python3 -B local/research/E7/e7_join.py
```

`e7_retain.py` compressed closed logs and moved receipts only after lease
release, verified SHA256 before removing originals, and records canonical
paths. Identical baseline VRAM references the existing single E4 gzip;
new E7c VRAM has one content-addressed gzip in `raw/`. The E7c miners
reproduce byte-identical summaries after retention. All raw logs, packet
snapshots, source/patch receipts, images, masks, fields, tests, configs,
and complete tap tails needed for the finding are retained.

Limits: taps cover boot through tick603, not the entire later run;
literal/static writer scans do not exclude all pointer aliases; G
snapshots do not prove unique fp-user entries; 128-bit FIFO ingress does
not implement narrower stores; the visible message is not menu/gameplay
progress or a hardware-perfect raster claim. No observation supports
stacking another fix in this brief.

---
**Tail receipt: E7 §§1–8 complete. Three boots used, all caps respected,
all owned leases released; final runner absent. Guarded S and field
values confirmed; E5 burst 558 joined; H-FIFO observed before fix;
five-of-five boundary packets consumed after fix; D content and both
Present fields joined, latest host RGBA exact. Suite 452/452; three new
regressions failed before and passed after. Fork commits pushed only to
fork; E7 evidence committed without ssx3 push. No regen, adb, generated
staging, fourth boot, or stacked fix. Ordered tap tails: E7b 10418 events,
E7c 12512 events, all three truncation flags zero.**
