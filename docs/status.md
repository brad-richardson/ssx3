# Status board (compact, authoritative — updated by the orchestrator each poll)

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on Odin.
Reference: `docs/research/review-2026-09-22-progress-and-parallelization.md`.
History: `docs/todo.md` (Done), `docs/numbers-ledger.md`.

| Lane | Owner state | Pinned rev | Next action | Blocker / lease |
| --- | --- | --- | --- | --- |
| E (PS2 runtime) | E28 gated PASS (guest half closed, X host-side) | fork `3adc0478` | E29: bounded dev-only movie bypass → E30 authored 2-chunk regression + fix eval | P-lane lease (E29 ≤2 boots) |
| G (GS composite) | g38 running: Mac-vs-Odin A→B comparison (redirected lane) | clone `3a66c19` | Gate g38 → G39 adoption package | Odin slot (booked per run) |
| T (host perception) | T46 gated PASS (first clean hold sample both trackers) | bytesize WSL (audio healthy) | T47 queued (healthy series; crash-lottery 3/4) | staffing (slot rotation) |
| V (storage) | v1 running: audit + manifest + smoke + cutover list | — | Gate v1 → mini cutover waits for active leases | corrupt SSD path (16 recurrences) |
| N (Android) | N1 briefed: native prep audit (APK/logcat/FFmpeg/input) | fork `3adc0478` (read-only) | Launch now (slot freed) | — |
| I (iOS) | Parked (I24 P4 closed) | branch `i23-ffmpeg-ios` @`aa73dbc` | Re-probe only on relevant runtime change | needs E-lane X |
| Adreno filing | HELD — content must be REWRITTEN (sampling inference withdrawn) | — | Owner call | Brad decision |

Rules: one live PS2 runtime mutator; E/G ownership distinct; completion-driven
gates with hourly watchdog; no upstream contact; no force-push.
