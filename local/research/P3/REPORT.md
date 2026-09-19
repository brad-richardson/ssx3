# P3 REPORT — PS2Recomp fork / downstream scan (compact evidence only)

Source scope: ONLY the compact `Evidence` JSON in the child request plus researcher refs `prior result 4`, `prior result 2`, `prior result 3`, `prior result 1`, `prior result 5`, `prior result 6`.
Prior-result bodies received in this invocation: summaries only (`structured result submitted`), no inspected bodies.
Compact evidence as received was truncated mid-value at `"psx` (see §7).
No code applied; adaptation sketches are function-level prose only.
No verdicts except license verdicts (§4, §3 license-verdict column).

Baseline refs from evidence:
- `REPORT P5-7+P1f.md read: P1f fix 6046260 sp=0 + pool [0x80000,0x100000); boot2 thread1 Running 0x391330` (primary-0 / prior result 4).
- `upstream main=14b1e5cb (#214); 133 forks enumerated via gh (authed); 50 open PRs listed` (primary-0 / prior result 4).

## 1. Project table

| Project | Rev in evidence | Path in evidence | README / status quote in evidence | License-file cite in evidence |
|---|---|---|---|---|
| PS2Recomp (baseline fork) | `6046260df65e` (P1f fix) | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/` | `README.md:1 'PS2Recomp: PlayStation 2 Static Recompiler (Experimental)'` | `LICENSE='GPL-3.0' (Version 3, 29 June 2007)` |
| reo | `73ad3c9f` | `/Volumes/Extreme SSD/q2-recomp-scan/sp00nznet_reo` | `README.md:16 'static recompilation, the same technique behind [Zelda 64: Recompiled]'`; milestones: `title screen rendered natively`, `Phase 3 (menu/gameplay) unchecked` | `no LICENSE file in checkout` |
| sm2 (spider-man-2-ps2-recomp) | `98aef964` | `/Volumes/Extreme SSD/q2-recomp-scan/saltyboosack-blip_spider-man-2-ps2-recomp` | `README.md:9 'The port is not playable yet'`; `based on ran-j/PS2Recomp ... upstream commit f4309cd18c184544f7891058676aaeef64357350 ... preserves its GPL-3.0 license'`; `boots to legal splash, 4/5 TEX0 descriptors` | README claim only: `preserves its GPL-3.0 license`; no LICENSE-file body quoted in evidence |
| bt3-recomp | `4b8a766b` | `/Volumes/Extreme SSD/q2-recomp-scan/z3xox_bt3-recomp` | `README.md:4 'built on PS2Recomp'`; `README.md:168-169 'Playable: boots through logos and title, menus work, and fights render in the GPU path at close to the engine's 30 fps cap'`; `README.md:197-198 'Licensed GPL-3.0'` | `LICENSE confirms GPL-3.0` |
| halogen | `53833285` | `/Volumes/Extreme SSD/q2-recomp-scan/0xjjjjjj_halogen` | `README.md:31 diagram 'PS2Recomp (MIPS R5900 -> C++)'`; `README.md:117 'vendor/PS2Recomp/ # Nested clone of our fork (0xjjjjjj/PS2Recomp)'`; `README.md:62 'halogen-headless binary boots the recompiled C++ successfully ... ~55 FPS ... runFrontEnd (main menu)'` | `LICENSE head 'MIT License, Copyright (c) 2026 0xjjjjjj'` |
| drakengard (sorachi00_ps2recomp-drakengard) | `2f5d48c1` | `/Volumes/Extreme SSD/q2-recomp-scan/sorachi00_ps2recomp-drakengard` | `README.md:1 'Fork of PS2Recomp focused on Drakengard'`; `no status statement in 11-line README`; `tools/drakengard_merged.toml + drakengard.csv present` | `LICENSE confirms GPL-3.0` |
| psx* | truncated | truncated | truncated at `"psx` | truncated |

Additional path/rev detail in evidence:
- reo: `README.md:157 'git clone https://github.com/ran-j/PS2Recomp.git third_party/PS2Recomp'`; `recomp/CMakeLists.txt:13 PS2RECOMP_DIR=third_party/PS2Recomp`.
- Upstream: `main=14b1e5cb (#214)`.

## 2. Mechanism table (primary-0 / prior result 4 only)

| # | Mechanism label (evidence wording) | Source project/rev | File:line in evidence | Compact quote |
|---|---|---|---|---|
| M1 | handler stack from owner SP | TheTharin `rogue-galaxy@7f29bbd` | `EeScheduler.cpp:191-196,1296,1913,1943` | `handler stack=ownerSp-0x800, sp left 0` |
| M2 | handler.sp zero + nesting guard | Sorachi00 `@2f5d48c` | `EeScheduler.cpp:1297`; `EeScheduler.cpp:255-264`; `ee_scheduler.h:103` | `handler.sp->0u + nesting guard :255-264` |
| M3 | fiber pool, N=1, EeScheduler deleted | smmathews `fiber@c7b2edc` | `ps2_runtime.h:272-273` | `pool [0x80000,0x100000); N=1 fibers, EeScheduler deleted` |
| M4 | real CD completion callback queued | phmdacosta `cd-cb@184158a` | `CD.cpp:38-63,352` | `real CD completion callback queued sp=0 (base=HEAD)` |
| M5 | Interrupt invocation-stack-top + no-preempt-active-IRQ guard + probes | hedgeg0d `katamari@3096823` | (no file:line in evidence) | `Interrupt=>invocationStackTop + no-preempt-active-IRQ guard + probes` |
| M6 | callbacks on interrupted SP + fallback | MrCool `@7978365` | `ps2_runtime.cpp:322,2618-2635` | `callbacks on interrupted sp, fallback 0x01FFFC20` |
| M7 | DI-gated preemption | GTT `#222@c4d099b` | (no file:line in evidence) | `DI-gated preemption` |
| M8 | DMAC IRQ delay/coalesce | GTT `#226@1fa97b8` | (no file:line in evidence) | `DMAC IRQ delay/coalesce` |
| M9 | DMA/RPC batch | GTT `#224/#223/#217` | (no file:line in evidence) | `DMA/RPC` |
| M10 | lazy executor bind | hedge `#235@cfcd341` | (no file:line in evidence) | `lazy executor bind` |
| M11 | dispatchIrqNow keeps handler.sp | hedge `#241` | (no file:line in evidence) | `dispatchIrqNow keeps handler.sp` |
| M12 | return-true (closed) | Sinan `#211@8dc8b54` | (no file:line in evidence) | `closed, return-true` |
| M13 | heap-limit layout alternative | TheTharin `#216@7ea9a2c` | (no file:line in evidence) | `heap-limit layout alternatives` |
| M14 | heap reserve layout alternative | phm `heap@9e00466` | (no file:line in evidence) | `reserve 0x10000` |
| M15 | P1f baseline fix | fork `@6046260` | (no file:line in evidence) | `sp=0 + pool [0x80000,0x100000); boot2 thread1 Running 0x391330` |
| M16 | stale pre-#184 bases | dust / phm-timer / smmathews-f04+waitsema / LuisFellp `#181` | (no file:line in evidence) | `bases f49ca4e/#179/#131 = pre-#184 arch, stale` |

## 3. Borrowable-snippet table (sketches NOT applied)

`NOT applied` means: no edit made; prose sketch only.

| Mechanism | Source project/rev/file:line/quote | Adaptation sketch to PS2Recomp (function-level prose, NOT applied) | License verdict for GPL-3 fork |
|---|---|---|---|
| M1 handler stack from owner SP | TheTharin `rogue-galaxy@7f29bbd` / `EeScheduler.cpp:191-196,1296,1913,1943` / `handler stack=ownerSp-0x800, sp left 0` | In `EeScheduler` handler-enqueue/dispatch path, derive the handler stack pointer as owner thread SP minus `0x800`; leave the handler `sp` field `0` on the queued record; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this rev |
| M2 handler.sp zero + nesting guard | Sorachi00 `@2f5d48c` / `EeScheduler.cpp:1297` + `EeScheduler.cpp:255-264` + `ee_scheduler.h:103` / `handler.sp->0u + nesting guard` | In `EeScheduler` dispatch function, zero `handler.sp` at the enqueue site corresponding to `:1297`; add/check the nesting guard corresponding to `:255-264` and the declaration at `ee_scheduler.h:103`; prose sketch only, not applied. | compatible — only if treated as same rev as drakengard `2f5d48c1` whose `LICENSE confirms GPL-3.0`; rev-prefix match (`2f5d48c`) is the only link in evidence, otherwise needs-rewrite pending license-file check |
| M3 fiber pool N=1 | smmathews `fiber@c7b2edc` / `ps2_runtime.h:272-273` / `pool [0x80000,0x100000); N=1 fibers, EeScheduler deleted` | In `ps2_runtime` init types/header around `ps2_runtime.h`, define a single-fiber pool over `[0x80000,0x100000)` with `N=1`; do not delete `EeScheduler` in this sketch; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this rev |
| M4 CD completion callback | phmdacosta `cd-cb@184158a` / `CD.cpp:38-63,352` / `real CD completion callback queued sp=0 (base=HEAD)` | In `CD.cpp` completion path, queue the real completion callback with `sp=0` per `:38-63` and the call site at `:352`, on a HEAD-based tree; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this rev |
| M5 Interrupt stack-top + guard + probes | hedgeg0d `katamari@3096823` / file:line not in evidence / `Interrupt=>invocationStackTop + no-preempt-active-IRQ guard + probes` | In `Interrupt` dispatch, set the stack top from the invocation stack top; guard against preempting an active IRQ; add probes at the same dispatch points; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this rev |
| M6 callbacks on interrupted SP | MrCool `@7978365` / `ps2_runtime.cpp:322,2618-2635` / `callbacks on interrupted sp, fallback 0x01FFFC20` | In `ps2_runtime.cpp` callback path, run callbacks on the interrupted thread SP per `:2618-2635` with the declaration/use at `:322`; fall back to `0x01FFFC20` when no interrupted SP is available; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this rev |
| M7 DI-gated preemption | GTT `#222@c4d099b` / file:line not in evidence / `DI-gated preemption` | In the scheduler/IRQ preemption check, gate preemption on the DI (interrupt-disable) state per `#222`; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this PR rev |
| M8 DMAC IRQ delay/coalesce | GTT `#226@1fa97b8` / file:line not in evidence / `DMAC IRQ delay/coalesce` | In the DMAC IRQ path, delay and coalesce IRQs per `#226`; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this PR rev |
| M9 DMA/RPC | GTT `#224/#223/#217` / file:line not in evidence / `DMA/RPC` | In the DMA/RPC paths covered by `#224/#223/#217`, apply the batched handling described by those PRs; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for these PR revs |
| M10 lazy executor bind | hedge `#235@cfcd341` / file:line not in evidence / `lazy executor bind` | In the executor-bind path, bind the executor lazily per `#235`; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this PR rev |
| M11 dispatchIrqNow keeps handler.sp | hedge `#241` / file:line not in evidence / `dispatchIrqNow keeps handler.sp` | In `dispatchIrqNow`, preserve `handler.sp` across the immediate dispatch; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this PR rev |
| M12 return-true | Sinan `#211@8dc8b54` / file:line not in evidence / `closed, return-true` | In the `#211` hook point, return true per `@8dc8b54`; note evidence marks the PR `closed`; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for this PR rev |
| M13/M14 heap-limit / heap-reserve layouts | TheTharin `#216@7ea9a2c` + phm `heap@9e00466` / file:line not in evidence / `heap-limit layout alternatives` + `reserve 0x10000` | In the heap-layout/init path, choose either a heap-limit layout per `#216` or a `0x10000`-byte reservation per `@9e00466`; prose sketch only, not applied. | needs-rewrite — no license-file cite in evidence for these revs |

Excluded from borrowing: M15 (local P1f baseline `@6046260`, not a borrow); M16 (evidence marks `pre-#184 arch, stale`).

## 4. License verdicts (GPL-3 fork) with license-file cites

| Project/rev | License-file cite in evidence | Verdict for GPL-3 fork |
|---|---|---|
| PS2Recomp baseline `6046260df65e` | `LICENSE='GPL-3.0' (Version 3, 29 June 2007)` | compatible |
| reo `73ad3c9f` | `no LICENSE file in checkout` | needs-rewrite |
| sm2 `98aef964` | README claim only: `preserves its GPL-3.0 license` (upstream `f4309cd18c184544f7891058676aaeef64357350`); no LICENSE-file body quoted | needs-rewrite pending LICENSE-file read (README claim alone is not a license-file cite) |
| bt3-recomp `4b8a766b` | `LICENSE confirms GPL-3.0` + `README.md:197-198 'Licensed GPL-3.0'` | compatible |
| halogen `53833285` | `LICENSE head 'MIT License, Copyright (c) 2026 0xjjjjjj'` | compatible (MIT into GPL-3 fork; retain MIT attribution) |
| drakengard `2f5d48c1` | `LICENSE confirms GPL-3.0` | compatible |
| TheTharin `rogue-galaxy@7f29bbd` | none in evidence | needs-rewrite |
| Sorachi00 `@2f5d48c` | none directly; indirect only via drakengard `2f5d48c1` `LICENSE confirms GPL-3.0` (shared `2f5d48c` prefix) | compatible-if-same-rev, else needs-rewrite (see §3 M2) |
| smmathews `fiber@c7b2edc` | none in evidence | needs-rewrite |
| phmdacosta `cd-cb@184158a` | none in evidence | needs-rewrite |
| hedgeg0d `katamari@3096823` | none in evidence | needs-rewrite |
| MrCool `@7978365` | none in evidence | needs-rewrite |
| GTT `#222@c4d099b`, `#226@1fa97b8`, `#224/#223/#217` | none in evidence | needs-rewrite |
| hedge `#235@cfcd341`, `#241` | none in evidence | needs-rewrite |
| Sinan `#211@8dc8b54` | none in evidence | needs-rewrite |
| TheTharin `#216@7ea9a2c`, phm `heap@9e00466` | none in evidence | needs-rewrite |

No `incompatible` verdict is entered: evidence contains no positively incompatible license text (e.g. proprietary / CC-NC / GPL-incompatible copyleft); all non-compatible rows are `needs-rewrite` for missing license-file cites.

## 5. Clone revs + paths

| Clone | Rev | Path |
|---|---|---|
| PS2Recomp baseline | `6046260df65e` | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/` |
| reo | `73ad3c9f` | `/Volumes/Extreme SSD/q2-recomp-scan/sp00nznet_reo` |
| sm2 | `98aef964` | `/Volumes/Extreme SSD/q2-recomp-scan/saltyboosack-blip_spider-man-2-ps2-recomp` |
| bt3-recomp | `4b8a766b` | `/Volumes/Extreme SSD/q2-recomp-scan/z3xox_bt3-recomp` |
| halogen | `53833285` | `/Volumes/Extreme SSD/q2-recomp-scan/0xjjjjjj_halogen` |
| drakengard | `2f5d48c1` | `/Volumes/Extreme SSD/q2-recomp-scan/sorachi00_ps2recomp-drakengard` |
| upstream PS2Recomp | `14b1e5cb (#214)` | (no path in evidence) |
| TheTharin rogue-galaxy | `7f29bbd` | (no path in evidence) |
| Sorachi00 | `2f5d48c` | (no path in evidence; cf. drakengard path above) |
| smmathews fiber | `c7b2edc` | (no path in evidence) |
| phmdacosta cd-cb | `184158a` | (no path in evidence) |
| hedgeg0d katamari | `3096823` | (no path in evidence) |
| MrCool | `7978365` | (no path in evidence) |
| GTT PRs | `#222@c4d099b`, `#226@1fa97b8`, `#224/#223/#217` | (no paths in evidence) |
| hedge PRs | `#235@cfcd341`, `#241` | (no paths in evidence) |
| Sinan PR | `#211@8dc8b54` | (no paths in evidence) |
| TheTharin PR / phm heap | `#216@7ea9a2c`, `@9e00466` | (no paths in evidence) |
| stale bases | `f49ca4e`, `#179`, `#131` | (no paths in evidence) |

## 6. Exact commands

Only one exact command string appears verbatim in the compact evidence:

| # | Exact command (verbatim from evidence) | Provenance |
|---|---|---|
| C1 | `git clone https://github.com/ran-j/PS2Recomp.git third_party/PS2Recomp` | reo `README.md:157` (primary-1 / prior result 2) |

Commands described but NOT quoted exactly in evidence (so not reproduced as exact):

| Described action | Evidence wording | Why no exact command is listed |
|---|---|---|
| fork enumeration | `133 forks enumerated via gh (authed)` | no CLI string in evidence |
| PR listing | `50 open PRs listed` | no CLI string in evidence |

## 7. What I could not do

| # | Item | Reason (evidence-state) |
|---|---|---|
| 1 | Complete the `psx*` project row and any evidence after it | Compact evidence truncated mid-value at `"psx`; remainder not received |
| 2 | Use prior result 3 / 1 / 5 / 6 bodies | Only summaries received (`structured result submitted`); no inspected bodies carried rev/file:line/quote/license evidence |
| 3 | Use more of prior result 4 / 2 than §§1–6 | Only the compact values quoted above were received; underlying files/diffs not included |
| 4 | Give `compatible`/`incompatible` to fork/PR snippets M1, M3–M14 | No license-file cites for those revs in evidence; entered as `needs-rewrite` |
| 5 | Confirm sm2 license from a LICENSE file | Evidence carries only the README `preserves its GPL-3.0 license` claim + upstream `f4309cd18c184544f7891058676aaeef64357350`; no LICENSE body |
| 6 | Confirm Sorachi00 `@2f5d48c` ≡ drakengard `2f5d48c1` | Only shared `2f5d48c` prefix links them in evidence; no remote URL / full SHA / diff |
| 7 | List exact `gh` / scan / clone commands for §5 revs | No CLI strings in evidence except C1; read-only-except-REPORT.md scope, so no new clones/fetches run |
| 8 | Verify file:line contents or quotes | No source bodies in evidence; this report copies the compact `file:line` + quote strings without re-reading the files |
| 9 | Apply any adaptation sketch | Task requires sketches as prose NOT applied; none applied |
| 10 | Enter non-license verdicts (best/faster/correct) | Task requires tables with no verdicts except license verdicts |

## 8. Parent addendum (post-workflow verification, read-only)

Parent inspected the researcher clones directly (receipts: `git rev-parse --short HEAD` per clone; `head`/`grep` of README/LICENSE/source files below). No new clones, no builds, no edits outside this file.

### 8.1 Verified clone revs (all P3 clones)

| Clone | Rev (`git rev-parse --short HEAD`) | Path |
|---|---|---|
| upstream-baseline | `14b1e5c` | `/Volumes/Extreme SSD/fork-survey/upstream-baseline` |
| thetharin-rogue-galaxy | `7f29bbd` | `/Volumes/Extreme SSD/fork-survey/thetharin-rogue-galaxy` |
| sorachi00-main | `2f5d48c` | `/Volumes/Extreme SSD/fork-survey/sorachi00-main` |
| smmathews-fiber-sched | `c7b2edc` | `/Volumes/Extreme SSD/fork-survey/smmathews-fiber-sched` |
| phmdacosta-ee-timer | `e465b4d` | `/Volumes/Extreme SSD/fork-survey/phmdacosta-ee-timer` |
| hedgeg0d-lazy-bind | `cfcd341` | `/Volumes/Extreme SSD/fork-survey/hedgeg0d-lazy-bind` |
| mrcool-main | `7978365` | `/Volumes/Extreme SSD/fork-survey/mrcool-main` |
| gtteancum-di-preempt | `c4d099b` | `/Volumes/Extreme SSD/fork-survey/gtteancum-di-preempt` |
| sinan-syscall-override | `8dc8b54` | `/Volumes/Extreme SSD/fork-survey/sinan-syscall-override` |
| xjjjjjj-main | `cf8d39e` | `/Volumes/Extreme SSD/fork-survey/xjjjjjj-main` |
| dothack-gsfix | `b525640` | `/Volumes/Extreme SSD/fork-survey/dothack-gsfix` |
| dustindustindustin-main | `0c96995` | `/Volumes/Extreme SSD/fork-survey/dustindustindustin-main` |
| liorv63afk-main | `acd39e3` | `/Volumes/Extreme SSD/fork-survey/liorv63afk-main` |
| maxigasparini-main | `2a2ffa4` | `/Volumes/Extreme SSD/fork-survey/maxigasparini-main` |
| sh2dow-main | `7c95e50` | `/Volumes/Extreme SSD/fork-survey/sh2dow-main` |
| trulio2-iop | `78ecbae` | `/Volumes/Extreme SSD/fork-survey/trulio2-iop` |
| reo | `73ad3c9` | `/Volumes/Extreme SSD/q2-recomp-scan/sp00nznet_reo` |
| sm2 | `98aef96` | `/Volumes/Extreme SSD/q2-recomp-scan/saltyboosack-blip_spider-man-2-ps2-recomp` |
| bt3-recomp | `4b8a766` | `/Volumes/Extreme SSD/q2-recomp-scan/z3xox_bt3-recomp` |
| halogen | `5383328` | `/Volumes/Extreme SSD/q2-recomp-scan/0xjjjjjj_halogen` |
| drakengard | `2f5d48c` | `/Volumes/Extreme SSD/q2-recomp-scan/sorachi00_ps2recomp-drakengard` |
| mstan_psxrecomp | `32831ff` | `/Volumes/Extreme SSD/q2-recomp-scan/mstan_psxrecomp` |
| N64Recomp | `ffb39cd` | `/Volumes/Extreme SSD/q3-siblings/N64Recomp` |
| N64ModernRuntime | `cdf5abb` | `/Volumes/Extreme SSD/q3-siblings/N64ModernRuntime` |
| Zelda64Recomp | `1a9c266` | `/Volumes/Extreme SSD/q3-siblings/Zelda64Recomp` |
| SaturnRecomp | `26c9715` | `/Volumes/Extreme SSD/q3-siblings/SaturnRecomp` |
| psprecomp | `caca759` | `/Volumes/Extreme SSD/q3-siblings/psprecomp` |
| wtf-psp-recomp | `ebaeed4` | `/Volumes/Extreme SSD/q3-siblings/wtf-psp-recomp` |
| XenonRecomp | `ddd128b` | `/Volumes/Extreme SSD/q3-siblings/XenonRecomp` |
| UnleashedRecomp | `cf829a9` | `/Volumes/Extreme SSD/q3-siblings/UnleashedRecomp` |
| psxrecomp (q3 copy) | `32831ff` | `/Volumes/Extreme SSD/q3-siblings/psxrecomp` |
| dobiestation-q4 | `68dd073` | `/Volumes/Extreme SSD/dobiestation-q4` |

Notes: fork-survey revs confirm M-table revs (`7f29bbd`, `2f5d48c`, `c7b2edc`, `cfcd341`, `7978365`, `c4d099b`, `8dc8b54`, `14b1e5c`). `sorachi00-main` short SHA `2f5d48c` equals drakengard `2f5d48c` (same 7-hex prefix; full-SHA/diff comparison not run). phmdacosta checkout is `e465b4d` (ee-timer branch), not the M4 `cd-cb@184158a` rev — M4 license row below rests on the fork-family LICENSE, not that rev. q3 `psxrecomp` and q2 `mstan_psxrecomp` share rev `32831ff` (same upstream).

### 8.2 Truncated `psx*` row completed (resolves §7 #1)

| Project | Rev | Path | README quote | License-file cite |
|---|---|---|---|---|
| PSXRecomp (mstan) | `32831ff` | `/Volumes/Extreme SSD/q2-recomp-scan/mstan_psxrecomp` | `README.md:11-13 'A general-purpose static recompiler for the PlayStation 1.' 'MIPS R3000A translated to C, compiled to x64, linked against a hardware-accurate runtime. Not an emulator'`; titles shipped: Tomba!, Tomba! 2, Ape Escape (`README.md` games table) | `LICENSE:1 'PolyForm Noncommercial License 1.0.0'`, `LICENSE:5 'Copyright (c) 2026 Matthew Stanley'` |

License verdict: **incompatible** — PolyForm Noncommercial bars the commercial-use freedoms GPL-3 requires; snippet cannot land in our GPL-3 fork (idea-level rewrite only).

### 8.3 Q3 sibling licenses (resolves part of §7 #2)

| Project/rev | License-file cite (head read) | Verdict for GPL-3 fork |
|---|---|---|
| N64Recomp `ffb39cd` | `LICENSE:1-3 'The MIT License (MIT)' / 'Copyright (c) 2024 Wiseguy'` | compatible (MIT; retain attribution) |
| N64ModernRuntime `cdf5abb` | `COPYING` present; same ultramodern tree as below (GPL-3 per Zelda64Recomp COPYING v3 text, same project family) | compatible pending full COPYING diff (see note) |
| Zelda64Recomp `1a9c266` | `COPYING:1-2 'GNU GENERAL PUBLIC LICENSE' / 'Version 3, 29 June 2007'` | compatible |
| UnleashedRecomp `cf829a9` | `COPYING:1-2 'GNU GENERAL PUBLIC LICENSE' / 'Version 3, 29 June 2007'` | compatible |
| psprecomp `caca759` | `LICENSE:1-3 'MIT License' / 'Copyright (c) 2026 sp00nznet'` | compatible (MIT; retain attribution) |
| wtf-psp-recomp `ebaeed4` | `LICENSE:1-3 'MIT License' / 'Copyright (c) 2026 sp00nznet'` | compatible (MIT; retain attribution) |
| XenonRecomp `ddd128b` | `LICENSE.md:1-3 '# MIT License' / 'Copyright (c) 2025 hedge-dev and contributors'` | compatible (MIT; retain attribution) |
| SaturnRecomp `26c9715` | no `LICENSE*`/`COPYING*` at top level; no license statement found in `README.md` | needs-rewrite (unlicensed) |
| PSXRecomp `32831ff` | `LICENSE:1 'PolyForm Noncommercial License 1.0.0'` | incompatible |

Note: N64ModernRuntime `COPYING` head was listed but its body text was not re-read line-by-line; it ships inside the Zelda64Recomp GPL-3 family tree. Treat as compatible-with-verification (one `head` away from certain).

### 8.4 Q3 mechanism: N64ModernRuntime message-not-nesting (resolves part of §7 #2)

Repo note: `N64Recomp` (`ffb39cd`) is the recompiler tool only; the async-event runtime lives in `N64ModernRuntime` (`cdf5abb`, `ultramodern/`). Mechanism: dedicated host threads per event source; game code is NEVER invoked on the event thread — completion is delivered as a message into the game's own `OSMesgQueue`, consumed by game threads on their own stacks.

| # | Mechanism | File:line (opened) | Quote |
|---|---|---|---|
| Q3-M1 | VI/AI via dedicated host VI thread → game mesg queue | `N64ModernRuntime/ultramodern/src/events.cpp:187` (`vi_thread_func`), `:247`, `:253` | `:247 'ultramodern::enqueue_external_message_src(cur_state->mq, cur_state->msg, false, ultramodern::EventMessageSource::Vi);'`; `:253 '...EventMessageSource::Ai'` |
| Q3-M2 | host-only VI callback (no game code on VI thread) | `events.cpp:257-259` | `'if (events_callbacks.vi_callback != nullptr) { events_callbacks.vi_callback(); }'` where `vi_callback_t = void()` is a host function (`include/ultramodern/events.hpp:6-13`, `'Called in each VI.'`) |
| Q3-M3 | timer via dedicated detached host thread → game mesg queue + interval reload | `N64ModernRuntime/ultramodern/src/timer.cpp:69` (`timer_thread`), `:133-138`, `:143-145` | `:133 'ultramodern::enqueue_external_message_src(cur_timer->mq, cur_timer->msg, false, ultramodern::EventMessageSource::Timer);'`; `:143-145 'timer_context.thread = std::thread{ timer_thread, PASS_RDRAM1 }; timer_context.thread.detach();'` |
| Q3-M4 | SP/DP (RSP/RDP) completion → game mesg queue | `events.cpp:263-273` (`sp_complete`, `dp_complete`) | `:266 'ultramodern::enqueue_external_message_src(events_context.sp.mq, events_context.sp.msg, false, ultramodern::EventMessageSource::Sp);'` |
| Q3-M5 | registration is host-side only | `include/ultramodern/events.hpp:21`, `include/ultramodern/threads.hpp:23` | `'void set_callbacks(const callbacks_t& callbacks);'` (game threads get host names for debugging, `threads.hpp:11-20`) |

Borrowable-sketch rows (NOT applied, function-level prose):

| Mechanism | Source | Adaptation sketch to PS2Recomp (NOT applied) | License verdict |
|---|---|---|---|
| message-not-nesting (VI/audio/timer/DMA) | N64ModernRuntime `cdf5abb`, files above | In `EeScheduler`/`queueInvocation`, deliver async completion as a queued event consumed at a thread-dispatch point on the owning thread's own stack (PS2 analogue of the game mesg queue), instead of immediately invoking handler bytecode on a borrowed/derived stack; keep any host-side callback (logging/probes) game-code-free as in Q3-M2. Prose sketch only, not applied. | compatible (GPL-3 family; verify N64ModernRuntime COPYING body before landing verbatim lines) |

### 8.5 Q4 DobieStation: no HLE EE-kernel thread model (resolves part of §7 #2)

| Finding | File:line (opened) | Quote |
|---|---|---|
| EE syscall names are a debug-only table; EE runs the Sony kernel (no HLE threading) | `dobiestation-q4/src/core/ee/emotion.cpp:42-46` | `:44-45 '//Taken from PCSX2' '//https://github.com/PCSX2/pcsx2/blob/af3e55af63dd23075c08eb6b181a6fe62793d8c0/pcsx2/R5900OpcodeImpl.cpp#L92'` (URL cited as found in source; PCSX2 source not cloned per runbook rule); table entries e.g. `:58 'CreateThread', 'DeleteThread', 'StartThread', 'ExitThread'` are `const char*` names only |
| host Scheduler is a cycle event queue of `std::function`, not a thread model | `dobiestation-q4/src/core/scheduler.hpp:14-48` | `:45-48 'std::vector<std::function<void(uint64_t)> > registered_funcs;'`, `'std::vector<std::function<void(uint64_t, bool)> > timer_callbacks;'`, `'std::list<SchedulerEvent> events;'` |
| EE timers register host callbacks into that queue | `dobiestation-q4/src/core/ee/timers.cpp:28` | `'scheduler->register_timer_callback('` (single match line; surrounding body not quoted) |
| license | `dobiestation-q4/LICENSE:1-2` | `'GNU GENERAL PUBLIC LICENSE' / 'Version 3, 29 June 2007'` → compatible, but nothing borrowable for the CD-callback thread model |

Q4 conclusion-table row: DobieStation `68dd073` has no EE-kernel/HLE threading and no CD-callback thread model to borrow; CD completion lives behind LLE (core `iop/cdvd/cdvd.cpp` matched `cd.*callback` filename grep but implements device emulation, not EE thread dispatch — file body not opened, recorded as uninspected).

### 8.6 License upgrades from fork LICENSE files (resolves §7 #4–#6)

All ten fork-survey clones below carry a `LICENSE` file headed `GNU General Public License`, and the sampled body reads `_Version 3, 29 June 2007_ / 'This License' refers to version 3 of the GNU General Public License` (`thetharin-rogue-galaxy/LICENSE`, grep-verified; siblings share the same 2-line head).

| Rev (§3 row) | License-file cite | Revised verdict |
|---|---|---|
| TheTharin `7f29bbd` (M1) | `fork-survey/thetharin-rogue-galaxy/LICENSE` head `GNU General Public License`, v3 body | compatible (was needs-rewrite) |
| smmathews `c7b2edc` (M3) | `fork-survey/smmathews-fiber-sched/LICENSE` same head | compatible (was needs-rewrite) |
| hedgeg0d `cfcd341` + `3096823` (M5, M10, M11) | `fork-survey/hedgeg0d-lazy-bind/LICENSE` same head (covers `cfcd341`; `3096823` same-fork inference) | compatible for `cfcd341`; compatible-if-same-fork for `3096823` |
| MrCool `7978365` (M6) | `fork-survey/mrcool-main/LICENSE` same head | compatible (was needs-rewrite) |
| Sorachi00 `2f5d48c` (M2) | `fork-survey/sorachi00-main/LICENSE` same head; short SHA equals drakengard `2f5d48c` | compatible (identity still prefix-level, but BOTH checkouts are GPL-3, so the fork-license question is moot) |
| gtteancum `c4d099b` (M7; M8–M9 same author) | `fork-survey/gtteancum-di-preempt/LICENSE` same head | compatible for `c4d099b`; compatible-if-same-fork for `#226/#224/#223/#217` revs |
| sinan `8dc8b54` (M12) | `fork-survey/sinan-syscall-override/LICENSE` same head | compatible (was needs-rewrite) |
| phmdacosta `184158a` (M4), `9e00466` (M14) | `fork-survey/phmdacosta-ee-timer/LICENSE` same head, but checkout rev is `e465b4d` (ee-timer), not the M4/M14 revs | compatible-if-same-fork (rev not directly inspected) |
| TheTharin `#216@7ea9a2c` (M13) | same fork LICENSE as M1 | compatible-if-same-fork (rev not directly inspected) |
| sm2 `98aef96` (§7 #5) | `q2-recomp-scan/...sm2.../LICENSE:1-4 'GNU General Public License' / '_Version 3, 29 June 2007_'` (file EXISTS; researcher row was wrong) | compatible (was needs-rewrite) |

Remaining `needs-rewrite` (no license-file cite): TheTharin `3096823`-style same-fork inferences above if strictness requires per-rev files; GTT `#226/#224/#223/#217` full revs; phm `184158a`/`9e00466`; hedge `#241` (no rev); SaturnRecomp (unlicensed). Sole `incompatible`: PSXRecomp (PolyForm Noncommercial).

### 8.7 What the parent still could not do

| # | Item |
|---|---|
| P1 | Recover researcher Q1 fork-diff bodies (only M-table compact quotes + clone revs survive; per-fork diffs would need re-reading `fork-survey/*/EeScheduler.cpp` etc.) |
| P2 | Open `dobiestation-q4/src/core/iop/cdvd/cdvd.cpp` body (device-side CD impl; not EE thread dispatch — low value) |
| P3 | Confirm full-SHA identity of `sorachi00-main` vs drakengard checkout (short SHAs match; full `rev-parse HEAD` comparison not run) |
| P4 | Read N64ModernRuntime `COPYING` body line-by-line (listed present; family is GPL-3) |
| P5 | Q2 reo/sm2/bt3/halogen mechanism detail beyond README quotes (clones present for a follow-up) |
