| E21 contract | Observable / bound |
|---|---|
| Time box | Start2026-09-21T21:14:22Z; deadline2026-09-22T05:14:22Z;8 hours |
| Required reads | E19 REPORT124 lines, NEXT-BRIEF17 lines, E18 NEXT-BRIEF41 lines, E20 prompt104 lines, E21 prompt68 lines read fully, including tails, before work; verbatim local copies. E20 partial landing commit`51d786c` (`local/research/E20/`) read as reference; never edited |
| Resume state | Fork`3adc0478` triple-verified post-remount; 9,457 generated + 1,725 protected hashes equal (`reconnection.json`, 20:37Z). Checkpoint regression AFTER remount rc=0: suite 458, closure 6, E15 rc0s, boot 0 (`checkpoint-complete.json`, 20:39Z). Observer forwarding repair EDITED but UNPROVEN: `e20_parser_observer.c/.h`. E21 copies to `e21_*` and proves from there |
| Hypothesis | Direct imports in the interposing image retain the real backend binding; RTLD_NEXT lookup can return an interposed result. E20 chose direct imports; E21 verifies the claim locally, not by inheritance |
| Mechanism gate | Compare direct binding / RTLD_NEXT / explicit-handle lookup addresses and image provenance without invoking an unsafe candidate. Select a verified original backend; exactly one backend entry and return per observer call |
| Isolation proof | Minimal non-title harness; compare uninstrumented and observer-loaded calls on identical input, packet bytes, frame planes/metadata and return behavior. Prove real _Exit final counters separately before full suite |
| Ordered work | Checkpoint→forwarding/closure isolation proof→observer-loaded full regression→Q1 thresholds→Q2 demand audit→Q3 one guarded demand-watch boot |
| Q1 | Re-verify E19's retained first64 and authored cases against hashes; no re-encoding. Marks5040/8192/16384 and bytewise packet1 threshold. Only bytes actually fed support results; no full E18 replay or universal threshold claim |
| Q2 | Static demand path plus inherited E18 post-input silence; name who requests more and with what signal, or establish its absence. Opens only after Q1 receipts |
| Q3 | One title boot maximum with fresh T13, shared lease, REPORT_ALL and extended parser observations; opens only after Q2 receipts. Lease occupied→table and stop, never wait |
| Alternatives / stop | Transparent observation or forwarding/closure gap; complete packet boundary or insufficient input; caller/guest re-request or undrained buffer/missing signal. Any regression red→table and stop; occupied lease→stop without waiting |
| Target fix gate | Exactly one demonstrated target edge plus a minimal ABI-preserving fix and its own fail-before/full regression. Guest needs X→name exact signal and stop; no policy/decoder/EOF invention, fabricated frames, stacked fix or game regeneration |
| ABI carry | Caller-owned synchronous HleCall; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside MPEG mutex; AddBs re-entry; delete/reset cancellation; stream behavior retained |
| Failed artifacts | E19 dylib and E20's unproven repair state are retained evidence only; never loaded into E21 suite/title. The E21 observer must pass isolation first. E20 dir is read-only reference |
| Observer rename | `e21_parser_observer.c/.h` is the E20 repair with identifiers/paths renamed E20→E21 (`E21ParserStats`, `e21_parser_snapshot/mark`, `PS2X_E21_PARSER_DIR`, `PS2X_E21_PROOF`, `# E21 PARSER CLOSURE`). Wire schema stays2 (format unchanged); the rename is mechanical and the isolation proof re-establishes forwarding from zero |
| Internal budget |3 GiB: optional isolated runtime build2 GiB, evidence512 MiB, observer/scratch256 MiB, reserve256 MiB including main Git64 MiB. Admission plus2.5 GiB floor/guard=5,905,580,032 B; stop owned2.75 GiB or free≤2.5 GiB |
| SSD budget |16 GiB: tooltmp8 GiB, fixtures2 GiB, probe1.5 GiB, possible fork source/Git1 GiB, reserve3.5 GiB. Admission plus2.5 GiB floor/guard=19,864,223,744 B; stop owned15.5 GiB or free≤2.5 GiB. Owned paths `e21-*` (+ `._e21-*`); may reuse read-only `e20-*` fixtures after re-hash |
| Admission | `initial-admission.json`, sampled and checked before E21 creation; fresh remaining-reservation checks before each tool. SSD flapped twice today — re-run admission/hash checks before trusting anything on it |
| Accounting | st_blocks×512 including ExFAT directories/AppleDouble, owned E21 paths, shared function log and positive fork source/Git growth. COPYFILE_DISABLE=1; no bytesize/WSL; no deletion/reclaim |
| Protected | /tmp/p1-link, /tmp/e17-map-link, /tmp/e18-mpeg-link and DerivedData; also preserve E19/E20 partial artifacts. Reuse read-only; any E21 runtime build isolated |
| Build/tool caps | Host jobs2; single direct compiler/linker is1 job and tabled. Configure1800/build7200/link1200s with15s reserve; stdout16 MiB/reserve1; tooltmp8 GiB/reserve512 MiB; fixtures2 GiB/reserve64 MiB |
| Isolation/fixture caps | Minimal harness120s/4 MiB stdout; authored input≤64 KiB/case; aggregate Q1 raw64 MiB; suite60s/4 MiB stdout/32 MiB scratch; backend parser EOF is never fabricated to create packet1 |
| Observer caps |12 MiB event text plus2 MiB retained API input, with source counters/pending/truncation/I/O checks and genuine _Exit closure; pending diagnostic write guards do not alter backend results |
| Probe caps |≤1 launch;90s wall/TERM75s;1M syscall lines; aggregate1.5 GiB logical/allocated. boot256 MiB, trace96 MiB, function1 GiB; E4 12/64 MiB, park32/128, frames32/64, E7 8/64, parser16/64;8 MiB reserve; no E19/E18 tick540 early stop |
| Lease/T13 | Atomic /tmp/ssx3-p-lane-lease, never wait; fresh process/binary/ELF/aligner/suite/hash/space preclaims. A lease held by another lane stops Q3 |
| Publication | Diagnosis-only zero fork commits. Gated single behavior fix named files only, fork push/ls-remote. Standalone E21 force-add evidence, [E21], Orchestrated-By: Muse Code; verify-then-push |

| E21 CONTRACT TAIL COMPLETE | Declared and admitted before compilation or source edits. |
|---|---|
