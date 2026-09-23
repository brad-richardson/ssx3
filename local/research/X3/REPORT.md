# X3: SSX 3 120 Hz loop map (read-only tables)

Read-only extraction from generated code in `~/dev/ssx3-work/codegen-ssx3/`.
Every row is cited `file:line`. Cells I could not confirm read `not found`.
No interpretation beyond what the instruction stream shows; branch targets are
computed from the emitted offsets.

- mainLoop source: `sub_00316F00_0x316f00.cpp` (2689 lines; instructions
  0x316f00–0x317324; delay-slot comments appear twice per word — first
  occurrence cited).
- Metro source: `sub_002306A8_0x2306a8.cpp` (function spans 0x2306a8–0x230f40).
- preUpdate source: `sub_00227E98_0x227e98.cpp` (0x227e98–0x227f58).
- timerCallback source: `sub_00227F58_0x227f58.cpp` (0x227f58–0x227f80).

---

## Task 1 — cAppMan_mainLoop (0x00316F00) structure

### 1a. Every `jal` (direct call), in address order

| address | instruction | target | cite |
| --- | --- | --- | --- |
| 0x316f50 | jal | func_3E5928 | sub_00316F00_0x316f00.cpp:416 |
| 0x316fd4 | jal | func_317600 | sub_00316F00_0x316f00.cpp:768 |
| 0x316fe4 | jal | func_3175A0 | sub_00316F00_0x316f00.cpp:810 |
| 0x317014 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:937 |
| 0x317034 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1008 |
| 0x317060 | jal | func_319D18 | sub_00316F00_0x316f00.cpp:1111 |
| 0x317068 | jal | func_319D10 | sub_00316F00_0x316f00.cpp:1137 |
| 0x317090 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1216 |
| 0x3170d8 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1388 |
| 0x3170f8 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1459 |
| 0x317150 | jal | func_317530 | sub_00316F00_0x316f00.cpp:1687 |
| 0x317180 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1794 |
| 0x3171bc | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:1916 |
| 0x31724c | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:2260 |
| 0x3172e0 | jal | func_317328 (cAppMan_checkHalt) | sub_00316F00_0x316f00.cpp:2510 |
| 0x317310 | jal | func_317478 | sub_00316F00_0x316f00.cpp:2623 |

16 direct `jal` sites total. 8 of them are `cAppMan_checkHalt` (0x00317328).

### 1b. Every loop back-edge (backward branch), in address order

| address | instruction | branch target | cite |
| --- | --- | --- | --- |
| 0x317190 | bnel $v0,$zero (0x5440ffe5) | 0x317128 | sub_00316F00_0x316f00.cpp:1828 |
| 0x3171d8 | bnel $v0,$zero (0x5440ffe9) | 0x317184 | sub_00316F00_0x316f00.cpp:1983 |
| 0x3172c4 | b (0x1000ff1c) | 0x316f38 | sub_00316F00_0x316f00.cpp:2438 |
| 0x3172e8 | b (0x1000ff14) | 0x316f3c | sub_00316F00_0x316f00.cpp:2536 |

4 back-edges. The two 0x316f38/0x316f3c targets are the two virtual-call
blocks at the top of the outer frame loop (0x316f38–0x316f48 and
0x316f58–0x316f68); 0x3172c4 re-enters the loop head, 0x3172e8 re-enters one
word later.

### 1c. Loads of state+0x20-style limit/counter fields ($s0 = this = state)

| address | instruction | field / target | cite |
| --- | --- | --- | --- |
| 0x317188 | lw $v0, 0x20($s0) | limit, feeds slt at 0x31718c | sub_00316F00_0x316f00.cpp:1820 |

The only constant-offset load of state+0x20. (Other $s0-relative loads in the
function exist — 0x0/0x4/0x8/0x1c/0x2c/0x34/0x58/0x5c and float fields — but
none other at 0x20; see gap note below.)

### 1d. Supplementary: `jalr` (dynamic/virtual call) sites

Targets not statically known (vtable dispatch): not found for each.

| address | instruction | target | cite |
| --- | --- | --- | --- |
| 0x316f2c | jalr $v0 (v0 = *(v1+0x2c), v1 = s0+0x5c) | not found (dynamic) | sub_00316F00_0x316f00.cpp:338 |
| 0x316f48 | jalr $v1 (v1 = *(v0+0x5c), v0 = *(s0+8)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:387 |
| 0x316f68 | jalr $v1 (v1 = *(v0+0x64), v0 = *(s0+8)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:458 |
| 0x316fbc | jalr $v0 (v0 = *(v1+0x54), v1 = *(s0+8)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:703 |
| 0x317004 | jalr $v0 (v0 = *(v1+0x24), v1 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:880 |
| 0x31702c | jalr $v1 (v1 = *(v0+0x1c), v0 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:979 |
| 0x317054 | jalr $v1 (v1 = *(v0+0x0c), v0 = *a2) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1078 |
| 0x317088 | jalr $a1 (a1 = *(v0+0x2c), v0 = *(a0+0), a0 = s0+0x4) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1187 |
| 0x3170a4 | jalr $v0 (v0 = *(v1+0x2c), v1 = s0+0x5c) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1254 |
| 0x3170c8 | jalr $v0 (v0 = *(v1+0x24), v1 = *(s0+8… a1)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1331 |
| 0x3170f0 | jalr $v1 (v1 = *(v0+0x1c), v0 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1430 |
| 0x317118 | jalr $v1 (v1 = *(v0+0x0c), v0 = *a2) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1529 |
| 0x317130 | jalr $v0 (v0 = *(v1+0x2c), v1 = s0+0x5c) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1594 |
| 0x31716c | jalr $v1 (v1 = *(v0+0x4c), v0 = *(s0+8)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1733 |
| 0x3171b4 | jalr $v1 (v1 = *(v0+0x34), v0 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1887 |
| 0x3171d0 | jalr $v0 (v0 = *(v1+0x34), v1 = s0+0x5c) | not found (dynamic) | sub_00316F00_0x316f00.cpp:1954 |
| 0x317208 | jalr $v0 (v0 = *(v1+0x3c), v1 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:2082 |
| 0x31723c | jalr $v0 (v0 = *(v1+0x3c), v1 = *(s0+0)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:2203 |
| 0x3172d8 | jalr $v1 (v1 = *(v0+0x24), v0 = *(s0+8… a1)) | not found (dynamic) | sub_00316F00_0x316f00.cpp:2481 |

### 1e. Gap notes

- The 0x317128–0x3171d8 region is a convergence block: forward branches from
  the state dispatch land on 0x317138, 0x3171bc, 0x3171c0 and 0x3171c8
  (e.g. 0x316f84 beql→0x317138, 0x316f8c b→0x3171c8, 0x316f9c beql→0x3171bc,
  0x316fa4 b→0x3171c8, 0x316fdc b→0x3171c8, 0x316fec b→0x3171c8, 0x31700c
  beql→0x3171c0, 0x3170b4 b→0x3171c8, 0x3170d0 beql→0x3171c8, 0x317138
  b→0x31718c, 0x317140 beql→0x3171c8, 0x317178 b→0x3171c8). The counted loop
  (0x317184↔0x317128) is only entered via the bnel at 0x3171d8.
- Function ends in a tail at 0x317308 (addiu $sp,-0x10; jal func_317478 at
  0x317310) — a separate 16-byte stack frame, not part of the 0x40 frame.

---

## Task 2 — Counted step loop at 0x317184 ("60 FPS 2 Players" patch site)

| property | value | cite |
| --- | --- | --- |
| counter register | $s1 | increment at 0x317184: sub_00316F00_0x316f00.cpp:1800 |
| initial value(s) | 0, set at 3 sites: 0x316f14 (prologue), 0x317064 (delay slot of jal func_319D10), 0x3172c8 (delay slot of back-edge b at 0x3172c4) | sub_00316F00_0x316f00.cpp:314, :1117, :2444 |
| termination comparison | lw $v0, 0x20($s0) (limit); slt $v0, $v0, $s1; bnel $v0,$zero → 0x317128 | sub_00316F00_0x316f00.cpp:1820, :1824, :1828 |
| increment (patch site) | addiu $s1, $s1, 0x1 at 0x317184, original word 0x26310001 (patched to 0x26310002 by the 2-players 60 FPS patch) | sub_00316F00_0x316f00.cpp:1800 |
| second accumulation | addu $s1, $s1, $v0 (delay slot of b at 0x317138) — counter also gains the return value of the step call | sub_00316F00_0x316f00.cpp:1629 |

### What runs per iteration (raw edges, loop body 0x317184 → 0x3171d8)

| address | instruction | role | cite |
| --- | --- | --- | --- |
| 0x317184 | addiu $s1,$s1,1 | counter++ (patch site) | sub_00316F00_0x316f00.cpp:1800 |
| 0x317188 | lw $v0, 0x20($s0) | limit | sub_00316F00_0x316f00.cpp:1820 |
| 0x31718c | slt $v0,$v0,$s1 | limit < counter? | sub_00316F00_0x316f00.cpp:1824 |
| 0x317190 | bnel → 0x317128 (or fall through 0x317198) | loop continue / exit | sub_00316F00_0x316f00.cpp:1828 |
| 0x317128–0x317134 | jalr via vtable[0x28/0x2c] of object at s0+0x5c | step call 1 | sub_00316F00_0x316f00.cpp:1586–1600 |
| 0x317138 | b → 0x31718c; DS: addu $s1,$s1,$v0 | counter += ret; skip to 0x31718c | sub_00316F00_0x316f00.cpp:1623, :1629 |
| 0x317140 | beql $v0,$zero → 0x31718c (taken when ret ≥ 0… not taken when ret < 0) | conditional on step return | sub_00316F00_0x316f00.cpp:1651 |
| 0x317148–0x31714c | lui $at,0x4120; mtc1 $at,$f12 | f12 = 10.0f | sub_00316F00_0x316f00.cpp:1679, :1683 |
| 0x317150 | jal func_317530 (a0 = s0+0x38) | direct call | sub_00316F00_0x316f00.cpp:1687 |
| 0x317158–0x31716c | jalr via vtable[0x48/0x4c] of object at *(s0+8) | step call 2 | sub_00316F00_0x316f00.cpp:1713–1739 |
| 0x317174 | sw $s2, 0x58($s0) | store (s2 = 1) | sub_00316F00_0x316f00.cpp:1762 |
| 0x317178 | b → 0x3171c8 | skips 0x317180–0x3171c4 on this path | sub_00316F00_0x316f00.cpp:1766 |
| 0x317180 | jal func_317328 (cAppMan_checkHalt) | on paths entering via 0x3171d8 | sub_00316F00_0x316f00.cpp:1794 |
| 0x317198–0x3171b0 | lw/addiu/sw of s0+0x1c; load s0+0 | frame counter bump | sub_00316F00_0x316f00.cpp:1859–1883 |
| 0x3171b4 | jalr via vtable[0x30/0x34] of object at s0+0 | step call 3 | sub_00316F00_0x316f00.cpp:1887 |
| 0x3171bc | jal func_317328 (cAppMan_checkHalt) | checkHalt | sub_00316F00_0x316f00.cpp:1916 |
| 0x3171c4–0x3171d0 | jalr via vtable[0x30/0x34] of object at s0+0x5c | step call 4 | sub_00316F00_0x316f00.cpp:1942–1960 |
| 0x3171d8 | bnel $v0,$zero → 0x317184 | loop back-edge | sub_00316F00_0x316f00.cpp:1983 |

Note: the `b` at 0x317178 skips 0x317180–0x3171c4, so the checkHalt at
0x317180 and the 0x317198–0x3171bc block only execute on paths that enter the
0x317184 region via the 0x3171d8 back-edge, not on the 0x317128 → 0x317138 →
0x3171c8 path. Exact per-iteration call count depends on which convergence
path is taken; not resolved here (read-only, no symbols).

---

## Task 3 — "Fix Metro Slowdown" sites (0x00230704 / 0x00230710)

File: `sub_002306A8_0x2306a8.cpp`. Function prologue at 0x2306b8
($s1 = $a0 = this). 10 instructions before / at / after each site, with
original instruction words.

### Site A: 0x230704 (bc1t)

| address | word | instruction | cite |
| --- | --- | --- | --- |
| 0x2306dc | 0x8f832a74 | lw $v1, 0x2A74($gp) (DS of 0x2306d8) | sub_002306A8_0x2306a8.cpp:656 |
| 0x2306e0 | 0x24020001 | addiu $v0, $zero, 0x1 | sub_002306A8_0x2306a8.cpp:678 |
| 0x2306e4 | 0x1000000b | b → 0x2306ec | sub_002306A8_0x2306a8.cpp:682 |
| 0x2306e8 | 0xac620034 | sw $v0, 0x34($v1) (DS of 0x2306e4) | sub_002306A8_0x2306a8.cpp:688 |
| 0x2306ec | 0x0c0bb900 | jal func_2EE400 | sub_002306A8_0x2306a8.cpp:710 |
| 0x2306f0 | 0x24040006 | addiu $a0, $zero, 0x6 (DS of 0x2306ec) | sub_002306A8_0x2306a8.cpp:716 |
| 0x2306f4 | 0xc781ae44 | lwc1 $f1, -0x51BC($gp) | sub_002306A8_0x2306a8.cpp:736 |
| 0x2306f8 | 0x24030001 | addiu $v1, $zero, 0x1 | sub_002306A8_0x2306a8.cpp:740 |
| 0x2306fc | 0x46000834 | c.lt.s $f1, $f0 | sub_002306A8_0x2306a8.cpp:744 |
| 0x230700 | 0x0 | nop | sub_002306A8_0x2306a8.cpp:748 |
| 0x230704 | 0x45010002 | bc1t → 0x230710 | sub_002306A8_0x2306a8.cpp:752 |
| 0x230708 | 0x8f822a74 | lw $v0, 0x2A74($gp) (DS of 0x230704) | sub_002306A8_0x2306a8.cpp:758 |
| 0x23070c | 0x0018002d | daddu $v1, $zero, $zero | sub_002306A8_0x2306a8.cpp:780 |
| 0x230710 | 0xac430034 | sw $v1, 0x34($v0) | sub_002306A8_0x2306a8.cpp:784 |
| 0x230714 | 0x8f84fdfc | lw $a0, -0x204($gp) | sub_002306A8_0x2306a8.cpp:788 |
| 0x230718 | 0x10800003 | beqz $a0 → 0x230728 | sub_002306A8_0x2306a8.cpp:792 |
| 0x230720 | 0x0c095c36 | jal func_2570D8 | sub_002306A8_0x2306a8.cpp:808 |
| 0x230724 | not found | (delay slot of 0x230720; not captured) | sub_002306A8_0x2306a8.cpp:808 |
| 0x230728 | 0x0c09e246 | jal func_278918 | sub_002306A8_0x2306a8.cpp:822 |
| 0x23072c | 0x8f84f7b4 | lw $a0, -0x84C($gp) (DS of 0x230728) | sub_002306A8_0x2306a8.cpp:828 |

### Site B: 0x230710 (sw)

| address | word | instruction | cite |
| --- | --- | --- | --- |
| 0x2306e8 | 0xac620034 | sw $v0, 0x34($v1) (DS) | sub_002306A8_0x2306a8.cpp:688 |
| 0x2306ec | 0x0c0bb900 | jal func_2EE400 | sub_002306A8_0x2306a8.cpp:710 |
| 0x2306f0 | 0x24040006 | addiu $a0, $zero, 0x6 (DS) | sub_002306A8_0x2306a8.cpp:716 |
| 0x2306f4 | 0xc781ae44 | lwc1 $f1, -0x51BC($gp) | sub_002306A8_0x2306a8.cpp:736 |
| 0x2306f8 | 0x24030001 | addiu $v1, $zero, 0x1 | sub_002306A8_0x2306a8.cpp:740 |
| 0x2306fc | 0x46000834 | c.lt.s $f1, $f0 | sub_002306A8_0x2306a8.cpp:744 |
| 0x230700 | 0x0 | nop | sub_002306A8_0x2306a8.cpp:748 |
| 0x230704 | 0x45010002 | bc1t → 0x230710 | sub_002306A8_0x2306a8.cpp:752 |
| 0x230708 | 0x8f822a74 | lw $v0, 0x2A74($gp) (DS) | sub_002306A8_0x2306a8.cpp:758 |
| 0x23070c | 0x0018002d | daddu $v1, $zero, $zero | sub_002306A8_0x2306a8.cpp:780 |
| 0x230710 | 0xac430034 | sw $v1, 0x34($v0) | sub_002306A8_0x2306a8.cpp:784 |
| 0x230714 | 0x8f84fdfc | lw $a0, -0x204($gp) | sub_002306A8_0x2306a8.cpp:788 |
| 0x230718 | 0x10800003 | beqz $a0 → 0x230728 | sub_002306A8_0x2306a8.cpp:792 |
| 0x230720 | 0x0c095c36 | jal func_2570D8 | sub_002306A8_0x2306a8.cpp:808 |
| 0x230724 | not found | (delay slot of 0x230720; not captured) | sub_002306A8_0x2306a8.cpp:808 |
| 0x230728 | 0x0c09e246 | jal func_278918 | sub_002306A8_0x2306a8.cpp:822 |
| 0x23072c | 0x8f84f7b4 | lw $a0, -0x84C($gp) (DS) | sub_002306A8_0x2306a8.cpp:828 |
| 0x230730 | 0x0c08c746 | jal func_231D18 | sub_002306A8_0x2306a8.cpp:848 |
| 0x230734 | 0x0022002d | daddu $a0, $s1, $zero (DS) | sub_002306A8_0x2306a8.cpp:854 |

Context above the sites: 0x2306cc–0x2306e8 first unconditionally writes 1 to
(gp+0x2A74)+0x34 (0x2306e8), then 0x2306f4–0x230710 writes 1 if the global
float at gp-0x51BC ≥ $f0 else 0 into (gp+0x2A74)+0x34. The two patch sites
null out the second (conditional) write pair.

---

## Task 4 — cSSXApp_preUpdate (0x00227E98) + cSSXApp_timerCallback (0x00227F58)

### 4a. Float constants via lui/ori/mtc1

| function | found |
| --- | --- |
| cSSXApp_preUpdate | not found (no lui/ori/mtc1 float-constant sequence in 0x227e98–0x227f58) |
| cSSXApp_timerCallback | not found (function is 8 words: 0x227f58–0x227f7c + trailing nop 0x227f7c) |

### 4b. Global (gp-relative) loads

| address | instruction | cite |
| --- | --- | --- |
| 0x227e9c | lw $v0, -0x850($gp) (preUpdate, first instruction after frame alloc) | sub_00227E98_0x227e98.cpp:37 |
| 0x227ec4 | lw $a0, -0x238($gp) (DS of beqz 0x227ec0) | sub_00227E98_0x227e98.cpp:90 |
| 0x227ecc | lw $a0, 0x300($gp) (DS of beql 0x227ec8) | sub_00227E98_0x227e98.cpp:107 |
| 0x227ed8 | lw $a0, 0x300($gp) | sub_00227E98_0x227e98.cpp:124 |
| 0x227ef0 | lw $a0, -0x850($gp) | sub_00227E98_0x227e98.cpp:156 |
| 0x227f00 | lw $a0, -0x850($gp) | sub_00227E98_0x227e98.cpp:178 |
| 0x227f30 | lw $a0, -0x850($gp) (DS of bnez 0x227f2c) | sub_00227E98_0x227e98.cpp:236 |
| 0x227f5c | lw $a0, -0x850($gp) (timerCallback) | sub_00227F58_0x227f58.cpp:31 |

### 4c. Every call

| address | instruction | target | function | cite |
| --- | --- | --- | --- | --- |
| 0x227eb8 | jal | func_326B48 | preUpdate | sub_00227E98_0x227e98.cpp:68 |
| 0x227ed0 | jal | func_255A20 | preUpdate | sub_00227E98_0x227e98.cpp:115 |
| 0x227ee4 | jal | func_2668E8 | preUpdate | sub_00227E98_0x227e98.cpp:144 |
| 0x227ef8 | jal | func_326CA0 | preUpdate | sub_00227E98_0x227e98.cpp:163 |
| 0x227f0c | jal | func_326CC8 | preUpdate | sub_00227E98_0x227e98.cpp:187 |
| 0x227f20 | jal | func_321298 | preUpdate | sub_00227E98_0x227e98.cpp:211 |
| 0x227f68 | jal | func_326B88 | timerCallback | sub_00227F58_0x227f58.cpp:50 |

preUpdate structure: prologue (0x227e98–0x227eb0, $s2 = this+0xA8); guard
beqz on (-0x850($gp)) at 0x227eb2; loop 0x227eec–0x227f2c with $s1 counter
(increment 0x227f10, termination slti $v0,$s1,2 + bnez at 0x227f28/0x227f2c),
calling func_326CA0/func_326CC8/func_321298 per iteration; tail 0x227f34
(b → 0x227f3c, DS sets v0=1) / 0x227f3c (v0=0); epilogue 0x227f40–0x227f54.
timerCallback: load -0x850($gp), beqz → skip, else jal func_326B88.

---

## Gaps

1. jalr targets in mainLoop are vtable dispatches; no symbols available
   (read-only generated code). Each marked not found (dynamic).
2. Metro 0x230724 (delay slot of jal func_2570D8 at 0x230720) not captured.
3. No float constants in preUpdate/timerCallback — no timing constants live
   in these two functions; any per-frame timing values are inside the called
   functions (func_326B48/326B88/326CA0/326CC8/321298), not mapped here.
