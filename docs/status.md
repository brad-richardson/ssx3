# Status board (compact, authoritative — updated by the orchestrator each poll)

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on Odin.
Reference: `docs/research/review-2026-09-22-progress-and-parallelization.md`.
History: `docs/todo.md` (Done), `docs/numbers-ledger.md`.

| Lane | Owner state | Pinned rev | Next action | Blocker / lease |
| --- | --- | --- | --- | --- |
| E (PS2 runtime) | e28 running: guest-half confirmation boot | fork `3adc0478` | Gate e28 → E29 bounded dev-only movie bypass to menu/race → E30 authored 2-chunk regression + fix eval | P-lane lease (e28 holds during boot) |
| G (GS composite) | G37 gated PASS; REDIRECTED (mis-sampling withdrawn, positive controls) | clone `3a66c19` | G38: Mac-vs-Odin first-composite-pass A→B comparison | Odin slot (booked per run) |
| T (host perception) | t46 running: healthy R3 series | bytesize WSL (audio healthy) | Gate t46 → re-evaluate T staffing vs storage/Android | bytesize WSLg audio (healthy since restart) |
| V (storage) NEW | V1 queued: durable verified storage cutover + restore smoke | — | Launch after G38 brief; mini cutover waits for active leases | corrupt SSD path (16 recurrences) |
| N (Android) NEW | N1 queued: native prep audit (APK/logcat/FFmpeg/input) | fork `3adc0478` (read-only) | Launch when a worker slot frees | staffing (4th worker) |
| I (iOS) | Parked (I24 P4 closed) | branch `i23-ffmpeg-ios` @`aa73dbc` | Re-probe only on relevant runtime change | needs E-lane X |
| Adreno filing | HELD — content must be REWRITTEN (sampling inference withdrawn) | — | Owner call | Brad decision |

Rules: one live PS2 runtime mutator; E/G ownership distinct; completion-driven
gates with hourly watchdog; no upstream contact; no force-push.
