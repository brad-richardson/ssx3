# I31 Part 1 — Brad's save + manual-play default on iOS (done)

Worker: Muse. Brief: `local/muse/prompts/I31.md` Part 1 only. No fork
edits, no push, no upstream contact. **iPhone: copy/install only, never
launched.** Brad's save files are private: names + SHAs only below.
Repo `main` @ `c150f207` at write time. Fork `~/dev/PS2Recomp` @
`f949ff0` (= `fork/ssx3`); the env-loader files cited are byte-identical
in the installed I30 build's pin `d711506` (diff empty).

Outcome: **deployed + verified.** Both devices hold bit-exact copies of
Brad's 6 save files under `Documents/mc0/` plus a 496-byte
`Documents/ps2x.env` that clears the bundled pad script (manual play),
with reinstall-safe re-apply via `deploy-ios.sh`. The single iPad
launch proves the game autoloaded the save (Select Character defaults
to Mac, Brad's rider, where the empty card defaults to Zoe) and proves
the test-override route (`-e PS2X_PAD_SCRIPT` wins). Two literals are
NOT observed (one-launch cap): stat VALUES (portrait crop hides them)
and the zero-env no-fire run (mechanism proven by the repo's own unit
test instead). Details + gaps below.

## 1. Loader semantics (no-rebuild route exists; no fork change needed)

File:line citations on fork `ssx3` (also true of the `d711506` build):

- `ps2xRuntime/src/lib/ps2_ios_runtime.mm:53-94` (`prepareEnvironment`):
  launcher env (`devicectl launch -e`) keys starting `PS2X_` are
  collected as protected (`:55-64`); layers merge bundle `ps2x.env`
  then `Documents/ps2x.env` (`:84-85`, later wins); each merged key is
  `setenv`'d (`:86-90`); launcher keys are kept and logged (`:91-94`).
  So precedence is **launcher `-e` > Documents > bundle**.
- `ps2xRuntime/include/ps2_env_file.h:43-44`: an empty value is kept and
  "clears a key set by an earlier layer, e.g. `PS2X_PAD_SCRIPT=`".
  `:114-135` (`mergeEnvLayers`): later layers override, protected
  (launcher) keys are dropped.
- `ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp:543-547`: `PS2X_PAD_SCRIPT`
  unset OR empty = no script (early return). So Documents
  `PS2X_PAD_SCRIPT=` (empty) fully disables the bundled I26-FAST
  script, and tests re-arm per launch with `-e` (which wins).
- Also: Settings Auto-route off would `unsetenv` the script
  (`ps2_ios_runtime.mm:96-100`), but unset (never opened) = on, so the
  Documents file is the robust route. The loader `mkdir`s `mc0`/`mc1`
  under `PS2X_MC_ROOT` (`:110-117`); bundled `PS2X_MC_ROOT` is
  `${DOCUMENTS}/mc0`, so the save goes in `Documents/mc0/`.
- The repo's own suite pins this: `ps2xTest/src/ps2_env_file_tests.cpp:35-44`
  ("later layers override, launcher keys win, empty clears",
  `m.at("PS2X_PAD_SCRIPT") == ""`). Built standalone + ran on the mini:
  **3/3 pass** (`envtest.log`). This is the manual-play mechanism proof.

Deployed `Documents/ps2x.env` (SHA
`306a0de0…f33658`, 496 B): comments + one line, `PS2X_PAD_SCRIPT=`.
All other bundled keys (BOOT_ELF, CD_IMAGE, MC_ROOT, SKIP_MOVIE,
DEINTERLACE, SOUND) inherit unchanged.

## 2. What was copied where (both devices, verified exact)

Source `~/dev/ssx3-work/E55D16/mc0/` (two SHA reads match; prefixes
match E55D16's pins; full SHAs in `source-shas.txt`).

| Destination | mc0 files | ps2x.env | Verify |
| --- | --- | --- | --- |
| iPad `00008112…A01E` | 6/6, exact sizes | 496 B | `info files` JSON + post-run copy-back SHAs match |
| iPhone `00008140…3001C` | 6/6, exact sizes | 496 B | `info files` JSON + env copy-back SHA matches |

Sizes: 39777/964/73144 (GAM0001 data/icon.sys/ssx1.ico),
3276/964/73144 (SET0001). Full table in `verify.txt`.
iPad: reinstalled the I30 signed app first (SHA `ae99bc45…`,
matches I30's `signed-binary-sha.txt`; reinstall preserves Documents —
`mc1` from 9/23 survived), then copied. iPhone: copy only, never
launched, not reinstalled (standing always-install rule covers Odin +
iPad). Post-run iPad `mc0` copy-back is bit-identical: the game wrote
nothing (read-only at title/menus), and the deployment survived the run.
Device mtimes are copy-time (devicectl sets none); the game accepted
the card anyway, so card-faithful mtimes are unnecessary.

Future installs: `local/research/I31/deploy-ios.sh ipad|iphone`
(idempotent: skips items already present with exact sizes, verifies
after; tested SKIP path on both devices, exit 0).

## 3. The one iPad launch (S1): design + console proof

One-launch tension, resolved by design: reaching Select Character needs
input, and the only input route is the pad script — so a literal
zero-press run cannot also show the save. S1 passes a **minimal 8-press
seeded script** via `-e` (first press at guest 15015ms = tick 900,
*after* the bundled start@10611): `15015:start:250,20854:cross:250,`
`27527:down:150,28695:down:150,29863:down:150,31031:down:150,`
`32199:down:150,35869:cross:250`, plus `-e PS2X_VSYNC_RATE_LOG=1`.
Script: `~/dev/ssx3-work/I31/ipad-run.sh`. 240 s, 18 screenshots,
console 642349 B (< 7.5 MB cap), terminated after (cleanup pid 18347).
Full key lines in `ipad-key-lines.txt`.

Console proves: `read …/Documents/ps2x.env` (deployed file found);
`PS2X_MC_ROOT=…/Documents/mc0` (game looks where the save is);
`launcher kept PS2X_PAD_SCRIPT` (test override wins);
`[padscript] armed n=8 source=env clock=vsync` (my 8, not the bundled
31); exactly 8 presses i=0..7 at my timings (i=6 one quantum late,
32215 vs 32199; all released); last tick 3829; `[snd-output] stream
rate=36000 channels=2 bits=16` from the bundled env, overflows=0.

## 4. Save autoload: proven by default rider + title timing

- **Default rider (strong leg).** S1 shot-0060 (tick 1384): Select
  Character shows MAC (outfit + bio match E55D16's seeded shot), with
  ZERO roster-nav presses before it (only start@900t, cross@1250t).
  Empty-card baseline: ROUTES.md pins #2 cross → "Select Character:
  Zoe" (Mac + Sim), and I30's unseeded iPad shot shows Zoe — same
  device/build/screen/path. Same screen + same press shapes → different
  default rider; the only differing input is card content, and both
  seeded runs (E55D16 Conquer path, I31 Single-Event path) agree on
  Mac. The game read Brad's save and defaulted to his rider.
- **Title timing (corroboration).** Shot-0025 (tick 719): logo, NO
  Press START; start@900t worked (menu at 911t). Prompt window
  (719, 900] matches seeded ~836t (E55D16) and excludes empty ~570t
  (ROUTES.md). Tick lines print ~every 5 s (±~100t frame skew; the
  bracket holds).
- **Not observed:** stat VALUES (2.9/3.0–4.0) — the portrait window
  crops bars + numbers (labels visible, values off-screen). The brief's
  literal parenthetical is therefore unmet; rider identity stands in.

Flow notes: start@900t → Main Menu (5 rows: Single Event highlighted,
Conquer, Multi…, Pre…, Onl…); cross@1250t → Select Character (Mac);
downs left Mac selected; cross@2150t → Setup Character, "Continue to
peak selection" (parked). No profile prompt on this path.

## 5. Findings for other lanes

- **I26-FAST derails on seeded cards.** ROUTES.md requires an empty card
  (prompt ~570t); on seeded (+266t) its start@636 is eaten and every
  press mislands (same class as E55D16's E55D12 cascade). Automated runs
  on Brad's devices must use an empty card via `PS2X_MC_ROOT` (as Part 2
  plans) or a seeded retime. The minimal-8 prefix here (all 8 landed as
  designed) is a validated retime seed.
- Brad's home-screen launches now get: manual play, his save, sound on,
  movie skipped. His first play doubles as the zero-env confirmation.

## 6. Gaps

- G1: stat values unreadable (portrait crop, I28's business). Rider +
  timing used instead.
- G2: literal zero-env run (`set PS2X_PAD_SCRIPT=` + zero padscript
  lines + static title) outstanding — one-launch cap spent on the
  instrumented run. Mechanism proven by unit test 3/3 + code. Close
  with one ~60 s zero-env iPad launch, or Brad's first-play report.
- G3: tick-line lag (~5 s) makes frame↔tick ±~100t; I30's shot-0035
  tick (740) vs ROUTES.md select@884 is a receipt-timing curiosity,
  immaterial (empty baseline verified on 3 runs).
- G4: `armed n=8` + press log prove the override, not the default
  clear, in-run (launcher key protected the bundled value by design).

Recommended next action: Part 2 (Odin) when the orchestrator says go;
optional G2-closing zero-env iPad launch (~5 min).

## 7. Commands, budget, receipts

```sh
# pins: fork f949ff0 (=fork/ssx3), I30 app ae99bc45… (matches I30 log)
xcrun devicectl device install app --device $IPAD …/I30/staged/ps2EntryRunner.app
xcrun devicectl device copy to --device $DEV --domain-type appDataContainer \
  --domain-identifier org.ps2x.ps2entryrunner --source <mc0|ps2x.env> --destination Documents/<mc0|ps2x.env>
xcrun devicectl device info files --device $DEV … --subdirectory Documents  # names + exact sizes (JSON)
bash ~/dev/ssx3-work/I31/ipad-run.sh   # the single launch (240 s, terminated after)
bash local/research/I31/deploy-ios.sh ipad|iphone   # idempotent re-apply
c++ -std=c++17 -Ips2xTest/include -Ips2xRuntime/include mini-main.cpp ps2_env_file_tests.cpp  # 3/3
```

Budget: 1 iPad install, 4 copies, 1 iPad launch, read-only
verifications; ~40 min of 45. No P-lane lease (no host boots), no
diagnostic build. iPhone never launched.
Committed text: `REPORT.md`, `deploy-ios.sh`, `ipad-key-lines.txt`,
`source-shas.txt`, `verify.txt`, `envtest.log`, `shots-viewed.txt`.
Scratch (private): `~/dev/ssx3-work/I31/` (console.log, 18 PNGs,
copybacks, install/copy/verify logs, ipad-run.sh, staging).
Base `c150f207`. Part 2 untouched (TL1 holds the Odin).

## Orchestrator gate (Part 1)

**Pass.** Checked myself:
- `shot-0060s.png` (scratch, iPad): Select Character on Mac ("Always riding to the beat of his own soundtrack") with no roster presses before it, where the empty card defaults to Zoe (I30). The save autoloads.
- Both devices list the 6 save files at the E55D16 sizes plus the 496 B `ps2x.env` (`verify.txt`); the iPhone env copy-back holds just `PS2X_PAD_SCRIPT=` plus comments. The iPhone was copy-only and never launched.
- Only names, sizes and SHAs of the save files are committed; no card bytes.
- G2 (a zero-env launch) stays open; Brad's first home-screen launch closes it.
- Part 2 (Odin) waits until TL1 releases the Odin; tests there use an empty `mc0-test` (I26-FAST derails on a seeded card, §5).

---

# I31 Part 2 — Brad's save + manual-play default on the Odin (done)

Worker: Muse. Brief Part 2, released after TL1. APK
`~/dev/ssx3-work/TL1/app-release.apk` (SHA
`aeb60d4d5e0c8418…d1e34220` ×2 match, 153,720,348 B; fork `f949ff0` +
parallel-gs `963cb57` per TL1). No fork edits, no push. Save files
private: names + SHAs only. `tl1.gs` (1.1 GB) + TL1 hashes/frames left
untouched.

Outcome: **deployed + verified, all observables met.** `files/mc0/`
holds bit-exact copies (device SHAs match source); device default
`ps2x.env` is Brad's manual-play env (SHA `9fb46f85…`, verified after
restore); the single launch reached Select Character showing Mac with
all 8 stats exactly matching E55D16 (2.9/4.0/3.0/3.0/3.0/3.0/1.0/3.0)
with the 36 kHz sound stream running, zero FATAL; force-stop, lease
released.

## 8. Env provenance (pulled first, saved to scratch)

Device orig (SHA `176eff84…` = N9/N10 orig, 1022 B, scratch
`odin/ps2x.env.orig`) holds: parallel backend, Turnip, CD image,
SKIP_MOVIE, I26-FAST script + vsync clock, VSYNC_RATE_LOG — **plus a
capture/dump block**: `PS2X_N8D5_TILE_CAPTURE=1`,
`PS2X_N8D7F_SELECTED_CAPTURE=1`, `PS2X_N8D7L_ORACLE=1`,
`PS2X_GS_CAPTURE=…/n8d7m6.gs`, `PS2X_GS_CAPTURE_STOP_TICK=2050`,
`PS2X_FRAME_DUMP_DIR=…`, `PS2X_FRAME_DUMP_ONCE_TICKS=…`. Those would
write GBs and cost speed on every play, so Brad's default drops them.

Brad's default (`odin/ps2x.env.brad`, SHA `9fb46f85…`, 472 B; embedded
in `deploy-odin.sh`): `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`,
`PS2X_CD_IMAGE=…/files/SSX3.iso` (required: `cdImage` has no default,
`main.cpp:325-333`), `PS2X_SKIP_MOVIE=1`, `PS2X_SOUND=1`
(`ps2_runtime.cpp:1116`, same key as iOS). No pad script, no clock key
(inert without a script), no rate log (tests add their own), no
capture/dump keys. No `PS2X_MC_ROOT`: default `files/mc0/` is where
the save lives (`main.cpp:337-345` + `ps2_runtime.cpp:394`). No
`PS2X_BOOT_ELF` on Android (baked `PS2X_DEFAULT_BOOT_ELF`,
`main.cpp:176-187`); env shim reads single `files/ps2x.env`
(`ps2_android_runtime.cpp:12-41`, keys logged as `ps2x.env: set …`).

Test-launcher contract (documented in `deploy-odin.sh`): automated
runs set `PS2X_MC_ROOT` to an empty `files/mc0-test/` (I26-FAST
derails on seeded cards, §5) and restore Brad's env after.

## 9. The one Odin launch (S1)

Preflight green: lease `LEASE_FREE TL1 done` → claimed `I31 odin
deploy`, keyguard `showing=false`, AC `true`, 72 %, app not running.
`adb install -r` Success (APK SHA ×2 pre-verified). Brad env pushed +
verified; save pushed (device two-reads match per file); temp launch
env (Brad's + `15015:start:250,20854:cross:250` + clock + rate log,
SHA `c16cc08b…`) pushed. Driver `~/dev/ssx3-work/I31/odin-run.py`
(N10/odin_replay recipe): logcat `-c`, `am start`, BACK at 6 s +
screencap confirm, tick-gated caps at 1400/1700/2100 + periodic,
300 s wall / 20 MB logcat caps. STOP tick 2430 ≥ 2400 at ~116 s
(~21/s in menus). Force-stop (`pidof` empty), Brad env restored +
SHA-verified, lease `LEASE_FREE I31 done`, battery 72→72 %.

Logcat (`odin-key-lines.txt`): all 8 launch keys `ps2x.env: set …`;
`[padscript] armed n=2`, 2 presses exactly at 15015/20854ms +
releases; `[snd-output] stream rate=36000 channels=2 bits=16`
(underruns 1230288, overflows 0 — guest under 1×, same shape as iOS);
`[gs-path] … subgroup_hier=wave64-fixed … desc=buffer … gpu=Adreno
(TM) 830` (parallel backend on Turnip); zero FATAL.

Screens (`odin-shots.txt`, PNGs in scratch): sc00 shows the PS2
"Checking for memory card (PS2) in MEMORY CARD slot 1" screen (card
path live; no USB dialog). sc01 (tick~1412): Select Character, Mac,
all 8 stats readable and **exactly equal to E55D16**: 2.9 / 4.0 /
3.0 / 3.0 / 3.0 / 3.0 / 1.0 / 3.0 (unseeded ≈ 1.0). sc04 (tick~2430):
same screen parked. **Autoload + sound confirmed on the device.**
Visible horizontal combing (no deinterlace key; N-lane's area).

## 10. Correction, gaps, receipts

- Correction: Part 1 `shots-viewed.txt` mis-transcribed E55D16's
  Stability as 4.0; re-crop confirms **3.0** (fixed in this commit).
  The E55D16 gate's "3.0–4.0" range still holds; all 8 Odin stats now
  match E55D16 exactly.
- G6 (new): no audible check of the Odin 36 kHz stream (logcat only);
  Brad's play is the audible test. G2 (iOS zero-env run) still open.
- Driver wart (cosmetic): the pid-after check used check=True so
  `pidof` rc=1 logged "force-stop FAILED"; verified separately the
  app is not running.
- `deploy-odin.sh` (committed): idempotent re-apply, SKIP path tested
  on-device (exit 0).

```sh
bash local/research/I31/deploy-odin.sh [SERIAL] [SAVE_SRC]  # save + env, no install/launch
```

Budget: 1 install, 1 launch (~116 s), read-only verifications; ~35
min of 45. Committed: this section, `deploy-odin.sh`,
`odin-key-lines.txt`, `odin-verify.txt`, `odin-shots.txt`, plus the
`shots-viewed.txt` one-line fix. Scratch: `~/dev/ssx3-work/I31/odin/`
(driver, logcat, 5 PNGs, envs, driver.log).

## Orchestrator gate (Part 2)

**Pass.** I viewed `sc01-tick1400.png` (scratch): Select Character on Mac with Brad's stats
(2.9 / 4.0 / 3.0 / 3.0 / 3.0 / 3.0 / 1.0 / 3.0), "Load game" offered. APK `aeb60d4d…` (TL1 gate).
Logcat shows the 36 kHz sound stream and the wave64 `[gs-path]`, zero FATAL. Brad's default env
(`9fb46f85…`) drops the stale N8D5/N8D7 capture and dump keys that were in the device env, which
is good for his play; any lane that used to inherit the device env must now write its own full
env and restore `9fb46f85…` after. Horizontal combing is the known Odin stripe item (N lane).
Closes the save-seed follow-up; G2 (iOS zero-env) and G6 (audible Odin check) close on Brad's play.
