# E54B — GS CSR VSINT acknowledgement and FIELD preservation

Worker: Codex. Brief: `local/muse/prompts/E54B.md`. The orchestrator decides the gate. Remote fork `ssx3` and the new worktree base both pinned at `bc1c70fd08398c4b615fbb34b959aad009dfc7f6` (`git ls-remote fork refs/heads/ssx3`); worktree `~/dev/ssx3-work/E54/PS2Recomp`, local branch `e54-csr`, commit `aa20d4a` (`Orchestrated-By: Codex`). No push.

| Gate | Result | Receipt |
| --- | --- | --- |
| Source diff | One CSR-status candidate in `ps2_memory.cpp`, `EeScheduler.cpp`, and `ps2_gs_tests.cpp` only. 32/64-bit guest CSR writes make SIGNAL, FINISH, VSINT W1C and preserve FIELD; VBlankStart raises VSINT and updates FIELD in one queued atomic operation. | `git show --stat aa20d4a`; fork source diff |
| Focused sequence | Pass: reset `0x4000`; `write64(8)` stays `0x4000`; odd VBlank `0x6008`; `write64(8)` `0x6000`; even VBlank `0x4008`; `write32(8)` `0x4000`; next odd VBlank `0x6008`; `write32(8)` `0x6000`. Also tests writes cannot set FIELD, and existing SIGNAL/FINISH/FIFO cases pass. | `~/dev/ssx3-work/E54/{suite-off.log,suite-on.log}` |
| Taps OFF Release | One configure/build attempt passed, runner and tests built. Suite from fork root: **560/560**, zero failed. Runtime and aggressive logs OFF, taps OFF; canonical E56 codegen. | `~/dev/ssx3-work/E54/{cmake-off.log,build-off.log,suite-off.log,build/CMakeCache.txt}` |
| Taps ON Release | One configure/build attempt passed, tests built. Suite from fork root: **655/655**, zero failed. Runtime and aggressive logs OFF, taps ON; same codegen. | `~/dev/ssx3-work/E54/{cmake-on.log,build-on.log,suite-on.log,build-taps/CMakeCache.txt}` |
| One I26-FAST boot | Pass: `PS2X_SKIP_MOVIE=1` (dev only), `PS2X_PKLOG=1`; slot 1, own PID 68458, target bound, `rc=0`, 112.044 s, last tick 2062 (target ≥2050). Combined boot and PK log 47,138,120 B, below 64 MiB cap. Three bounded frames captured. Runner exited, slot released. | `~/dev/ssx3-work/E54/run/csr-one/{result.json,boot.log,ps2_pklog.txt}`; `csr-site-reads.txt` |
| CSR sites | `0x37c0e0`: tick 40 `0x4000`, bit 3 clear immediately after the guest acknowledge. Poll `0x37c0f8`: tick 40 `0x4000`, tick 41 `0x6008`, bit 3 set by next VBlankStart. `0x396090`: absent; reach unknown. | `csr-site-reads.txt` |
| Frames viewed | Select Character at tick 830 shows Zoe; race tick 1810 shows HUD 00:00:01, 0% progress; race tick 1941 shows HUD 00:00:03, 1% progress. Race advances. Both race frames retain the known large dark GS composite region. | `~/dev/ssx3-work/E54/run/csr-one/{sc-tick830.png,race_early-tick1810.png,race_late-tick1941.png}` |
| Runner-dir check | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty before and after source commit. No generated sources, game data or binaries committed. | Fork command output; clean worktree check |
| Storage | New E54 directory 726 MiB, below 8 GiB. Global ssx3 usage 106.4/200 GB; disk free 137 GiB. | `du -sh ~/dev/ssx3-work/E54`; `local/tooling/disk_budget.sh` |

## Test seam and timing limit

The unit invokes `ps2xGsCsrVBlankStart(PS2Memory&, tick)`, the exact status helper called from `EeScheduler::processEvent(VBlankStart)`. The scheduler has no narrow event-injection API. The helper uses the existing `gsPrivStore` path, so the queue's ordering is retained. Odd-field update is `fetch_or`; even-field update uses a compare-exchange loop to clear FIELD and set VSINT as one atomic step. This tests the CSR status operation, not full scheduler event dispatch.

The event timing is an approximation: PCSX2 raises VSINT and updates FIELD at GS blank, about 3.5 hblanks after VSync start. This fork currently has only VBlankStart; no cycle-parity claim is made. Progressive/interlaced FIELD mode rules also remain outside this candidate.

## Two-read SHA-256 ledger

| Item | SHA-256, both reads matched |
| --- | --- |
| Canonical E56 `codegen-ssx3/register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Stock ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Stock ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| E54B Release runner `build/ps2xRuntime/ps2EntryRunner` | `55bfbbe609cab24b2b8c03bbbc7f0353aefe3be5d176704208c858aab0fdf2cf` |

The ELF/ISO repeated reads are in `~/dev/ssx3-work/E54/input-sha.txt`. Frame SHA-256 values: tick 830 `43ff22a5f005e629a22ea6d8196dc8f79245ea3587713ccd6955e5905e0a65f3`; tick 1810 `e9f450a798ed708cac08d2a3b85f3d8c01a9f528a569efe3bad9aac044078651`; tick 1941 `434b59f2ca5f69c4f5ba4004cb7802d9f3a9d87cbde6281fc175eaef9052b68e`.

## Exact commands

Run from `~/dev/ssx3-work/E54/PS2Recomp` unless noted:

```sh
git ls-remote fork refs/heads/ssx3                 # from ~/dev/PS2Recomp
git worktree add ~/dev/ssx3-work/E54/PS2Recomp -b e54-csr bc1c70f
zsh ~/dev/ssx3-work/E54/build.sh off
../build/ps2xTest/ps2x_tests > ../suite-off.log 2>&1
zsh ~/dev/ssx3-work/E54/build.sh on
../build-taps/ps2xTest/ps2x_tests > ../suite-on.log 2>&1
python3 ~/dev/ssx3-work/E54/e54_boot.py --label csr-one --capture --target 2050 --wall 500
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git commit -m '[E54B] Acknowledge GS VSINT and preserve FIELD on CSR writes' -m 'Raise VSINT with the existing queued VBlankStart status update; keep CSR guest writes atomic and cover the 32/64-bit acknowledge sequence.' -m 'Orchestrated-By: Codex'
```

Gaps: exact PCSX2 GS-blank timing and video-mode FIELD rules; `0x396090` reach unknown. No fixed-tick frame-hash gate was applied. No additional boot, tuning loop, or fork/ssx3 push.
