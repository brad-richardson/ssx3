# E60 — VU0 sky-state differential

Worker: Codex. Brief: `local/muse/prompts/E60.md`. The orchestrator decides.

## Pins and budget

| Item | Value |
| --- | --- |
| Fork base / worktree | `13cac7fdfa8f3554c2afef25982fcc0e7da269f7` (`fork/ssx3`, fetched at start), `~/dev/ssx3-work/E60/PS2Recomp` branch `e60-sky` |
| PCSX2 source / binary SHA-256 ×2 | Source `9056c08349cc29ad02a6d1a3a4133259019195af` plus preexisting T/AU hunks and E60 `Interpreter.cpp` hunk (receipt diff SHA `ef5ac65f21389c0bc2af3c4da9348db899d0cd92c4057f70e3566fe15da17006`). qt `6a1bc8b63266d7a467b820037ed642624c2e2637075cdb4a4cb20df352d86e85`; gsrunner `e0b86cc28cd205e7f90d40aa605997a38cd438c0cb4a0f9967bd70922e0b1cbf`; two matching reads. |
| PCSX2 pre-E60 preservation | `/home/brad/pcsx2-g7/pre-e60/Interpreter.cpp` SHA `21a32f0629cb84f632ed985f199049b1210b1538ff26b017d26916d804d5a863`; `pcsx2-qt` SHA `a0bb7b27032d231771ce8138c649933bcf8d9661bd67debaf3616c6de3a77de5`. Private DAT INI matches the T48 input byte-for-byte (SHA `d56ee08678f591ad09e3531b08800f097ba9971d89c9ede9d0b4b2c46147b7e8`). |
| Mini runner / ELF / ISO SHA-256 ×2 | Race-tick tap runner `859d5cc35fd4c3182ff7ab89de88f6f8c910effbb1594bf3b01dbb7447d6702c`; boot-global tap runner `3dd3e40e2f20c4c083488989f6fd73f497bac17628ad5bc426f1c58fc7920581`; ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`; ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`; all two matching reads in `receipts/`. |
| Builds, captures, boots, disk | Local build 1 failed on missing `EeScheduler` include; one fix build passed; third build widened the tap to the whole boot and passed. Local boot 1 passed I26-FAST to tick 2110 in 111.873 s, slot 2, PID 40088; boot 2 passed to tick 2116 in 152.196 s, slot 1, PID 41839. Both bounded target exits; no VU0 read record. PCSX2 build 1 failed on missing `VU0` include; one fix build passed. Both PCSX2 captures passed the route gates and recorded no read. E60 mini work dir 788 MB (<8 GB cap); bytesize E60 dir 3.3 GB before, 685 MB after closed-log compression (<8 GB). Overall mini workstreams 102.3/200 GB after work. |

## `sceVu0MemReadQ` callers and uses

| Caller | Race use | Evidence |
| --- | --- | --- |
| `0x3fed6c` at labeled `sceDevVu1GetTpc` (`0x3fed60`) | Calls with VU0 qword index `0x43a`; low half of returned qword becomes `v0` (`0x3fed74`). | `ee-label 0x3fed60`; `ee-xref 0x3feb78`; `ee-at 0x3fed60` |
| `0x3fee04` after labeled `sceDevVu1GetCnd` entry (`0x3fed88`) | Loop reads 32 qwords, indices `0x400..0x41f`, and writes them to `[s2+0..0x1ff]`. | `ee-label 0x3fed88`; `ee-at 0x3fed60`; loop at `0x3fedf8..0x3fee1c` |
| `0x3fee24`, `0x3fee40`, `0x3fee54`, `0x3fee68`, `0x3fee7c`, `0x3fee90`, `0x3feea4` | Reads VU0 indices `0x430..0x432`, `0x434..0x437`; low word becomes `[s2+0x200..0x218]`. | `ee-at 0x3fed60` |
| `0x3feec4` | Loop reads 16 qwords, indices `0x420..0x42f`; low half becomes 16 halfwords at `[s2+0x21c..0x23a]`. | `ee-at 0x3fed60` |

All ten static call sites are in one generated containing function, but two labeled entry routines. `ee-xref 0x3fed60` shows a call at `0x3fec64` from `sub_003FEBC0`, conditional on VU0 `vi29` status. `ee-xref 0x3fed88` and `ee-xref 0x3fec38` find no static callers, so live frequency still needs the tap. The reader masks VU0 byte offsets to 4 KiB, so indices `0x400..0x43a` wrap to qwords `0x00..0x3a` (`ps2xRuntime/include/ps2_runtime_macros.h`, `Ps2Vu0DataAt`).

## First-call VU0 differential and writer

| Datum / qword | Ours | PCSX2 | Writer class and evidence |
| --- | --- | --- | --- |
| First local race call after tick 1600 | **No call observed through tick 2110.** Tap file absent, though the race boot reached target. | not found | not found; `~/dev/ssx3-work/E60/run/vu0-first/result.json`, `boot.log` |
| First local call from boot | **No call observed through tick 2116.** Tap file absent with the tick gate removed. | not found | not found; `~/dev/ssx3-work/E60/run/vu0-global/result.json`, `boot.log` |
| First PCSX2 race call | not found | **No call observed** for 60 s after the race-entry gate; the arm file was present, `pcsx2-vu0.bin` was absent, and emulog had no `E60_VU0` line. T48 route gates passed (TITLE poll1, SC settled mean 0.4610, Happiness identity mean 0.0187, Rules retry 2 departed/animated, race-entry mean 11.6030). | no qword to classify; `~/dev/ssx3-work/E60/pcsx2-capture-ssh.log`, `/home/brad/e60/e60b-poll.log` |
| First PCSX2 call from boot | not found | **No call observed from boot through race** with the same hook armed before launch. Route gates again passed (TITLE poll1, SC settled mean 0.4829, Happiness identity mean 0.0349, Rules retry 2 departed/animated, race-entry mean 11.5821); final `pcsx2-vu0.bin` absent and emulog had **0** `E60_VU0` lines. | no qword to classify; `~/dev/ssx3-work/E60/pcsx2-capture-boot-ssh.log`, `receipts/boot-route-gates.txt`, `receipts/vu0-absence.txt`, `receipts/e60-hook-line-count.txt` |

## Candidate fix and validation

| Check | Result | Receipt |
| --- | --- | --- |
| Unit test | Not run: no differing read or single writer mechanism was found. | — |
| Fix-validation race boot and frame viewing | Not run: no candidate fix. The two diagnostic race boots are listed above. | — |
| New sky-packet ALPHA/CBP comparison | Not run: no candidate fix. E59's existing packet discrepancy remains. | — |

## Commands and gaps

From `~/dev/ssx3`, fork setup was `git fetch fork ssx3`, then `git worktree add -b e60-sky ~/dev/ssx3-work/E60/PS2Recomp fork/ssx3` (both escalated). The fork worktree stayed clean; `git diff --stat 14b1e5cb e60-sky -- ps2xRuntime/src/runner` was empty. No fork push or commit.

Local diagnostic source was an E60-only copy of `codegen-ssx3` with one default-off `PS2X_E60_TAP` at generated `sub_003FEB78_0x3feb78.cpp`. `instrument_codegen.py` wrote the initial tap, which snapshots 4 KiB plus `vi1`, caller, tick and qword, at most 16 records. The first build (`zsh ~/dev/ssx3-work/E60/build_diag.sh`) failed because `EeScheduler` was forward-declared; one include fix and `cmake --build ~/dev/ssx3-work/E60/build --target ps2EntryRunner -j8` passed. After boot 1 had no race read, removing the tick gate and rebuilding the same target passed (build 3). `instrument_codegen_final.py` reproduces the final tap from a fresh E60 codegen copy. Boot commands were `python3 ~/dev/ssx3-work/E60/e60_boot.py --label vu0-first --target 2100 --wall 500` and `python3 ~/dev/ssx3-work/E60/e60_boot.py --label vu0-global --target 2100 --wall 500`, both escalated. The script claims/releases one mini slot, uses I26-FAST, has a 64 MiB log cap, 120 s no-progress cap, and PID-specific termination.

PCSX2 setup was `ssh bytesize 'wsl -d Ubuntu -- bash -s' < ~/dev/ssx3-work/E60/pcsx2_setup.sh`. The first `pcsx2_apply_build.sh` build failed because `Interpreter.cpp` lacked `VU.h`; one include fix and `pcsx2_fix_build.sh` passed. Both targeted `pcsx2-qt pcsx2-gsrunner -j2`. The E60-only hunk is in `receipts/pcsx2-hunk.diff`; `pre-e60/Interpreter.cpp` and `pre-e60/pcsx2-qt` preserve the prior bytes. `pcsx2_replay.sh` passed the T65 G13 preservation replay: all 7 PNG MD5 pins and exact HWSTAT (791 draws, 37 passes, 0 barriers, 14 copies, 320 uploads, 6 readbacks), with zero E60 lines when disarmed (`receipts/replay-*`). `pcsx2_cap.sh` and `pcsx2_cap_boot.sh` ran the T48/T65 route with a 560 s wall cap, arming at race entry and from boot respectively. Both logged zero calls. Exact invocations: `ssh bytesize 'wsl -d Ubuntu -- bash -s' < ~/dev/ssx3-work/E60/<script>.sh`, each redirected to its own `~/dev/ssx3-work/E60/pcsx2-*-ssh.log`.

The PCSX2 ISO and BIOS trio have two matching SHA-256 reads in `receipts/input-sha-read1.txt` and `input-sha-read2.txt`; these were read **after** both captures (T65 had pinned the same ISO earlier). The PCSX2 ISO hash matches the mini ISO hash. Both PCSX2 capture scripts wrote under `/home/brad/e60/`, used a private PCSX2 DAT tree, ended the runner by recorded PID, and stopped Xvfb. No mini P-lane lease was used on bytesize.

The two closed PCSX2 emulogs were compressed with `gzip -1`, leaving one canonical `.gz` copy of each; their SHA-256 hashes are in `receipts/emulog-sha.txt`. Captured game data, binaries, large logs and screenshots remain outside git.

No `sceVu0MemReadQ` qword was captured on either side from boot through the sampled race, so no 4 KiB differential or writer class can be assigned. VIF0 UNPACK/MPG/STCYCL stream comparison, a unit test, a candidate fix, frame comparison, and new ALPHA/CBP packet check depend on that differential and were not run. The current VIF0 UNPACK implementation (`ps2_vif1_interpreter.cpp:299`) handles only `vl == 0`, but no observed read ties that to this sky state; this is a code observation, not a diagnosis.

## Recommended next action for the orchestrator

The observed route does not exercise `sceVu0MemReadQ`, even though E59's generated-code isolation made its VLQI the best remaining instruction lead. Gate the E59 full-a versus combined variant with deterministic same-scene frames and raw packet state, then trace the first ALPHA/CBP divergence back to its EE/VU/VIF writer. Do not change VU0 read semantics on this evidence. The orchestrator decides the next brief.
