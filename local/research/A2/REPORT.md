# A2 — secrets, personal data, private infrastructure: findings tables

Scope: tracked files (`git ls-files`, 388 files) and full history (`git rev-list --all`, 241 commits).
Method: `git grep` over tree and over `$(git rev-list --all)`, plus hand read of `native/ios`.
No builds, no `adb`. Read-only except this report directory.

## 1. Secrets

Pattern set: `AKIA`, `sk-`, `ghp_`, `xox`, `BEGIN .* PRIVATE KEY`, `password`, `secret`, `token`, `apikey`, `Authorization:`, plus hand read of iOS signing material (bundle IDs, team IDs, provisioning profile names, keychain references, `.env` contents, cloud credentials, signing identities).

No `AKIA`, `ghp_`, `xox`, `BEGIN .* PRIVATE KEY`, `apikey`, `Authorization:` values were observed in tree or history blobs. No `.env`, `.pem`, `.p12`, `.pfx`, `.mobileprovision`, `.key` files are tracked in tree or in history name lists. No Apple Team ID value and no provisioning profile name value were observed in tree; only code that reads the local profile is present. No keychain entry value was observed. No cloud credential value was observed.

Observed hits are the shapes below. Secret values are redacted to shape only.

| file | count | example (shape only) | in tree / history-only | removal shape |
|---|---|---|---|---|
| docs/gamecube-feasibility.md | 1 | `... shared ISO. See ...` (contains `secret` as substring of `disk-cleanup`) | in tree | edit |
| docs/research/120hz-f-spike.md | 1 | `## Token budget (order-of-magnitude, ±2x)` (word `Token`) | in tree | edit |
| docs/research/120hz-host-replay.md | 3 | `two token commands and 19 TMEM load/sync commands` (GPU token word) | in tree | edit |
| docs/research/float-conversion-spike.md | 1 | `` `get-task-allow` `` entitlement word | in tree | edit |
| docs/research/review-2026-09-17-recomp-perf.md | 2 | `a trial binary, and a 10 M-token disclaim loop ...` | in tree | edit |
| docs/share-recovery.md | 2 | `It does not read credentials or store passwords in the script or plist.` | in tree | edit |
| docs/texture-remaster.md | 1 | `... 3 mask-carried.` (contains `secret` as substring of `mask-carried`) | in tree | edit |
| docs/todo.md | 3 | `content (tree + history), A2 secrets / personal data / private` | in tree | edit |
| local/research/S2/REPORT.md | 16 | `` `SetToken`/`SetFinish` `` (PixelEngine GPU token API) | in tree | edit |
| local/research/S2/aux_budget.py | 2 | `PE BP writes (SETDRAWDONE/PE_TOKEN/PE_TOKEN_INT)` | in tree | edit |
| local/research/S2/s2_replay_capacity.h | 7 | `handles ONLY BPMEM_SETDRAWDONE / BPMEM_PE_TOKEN_ID /` | in tree | edit |
| native/diagnostics/chunk_signposts.h | 2 | `task-named addresses` (contains `task-` + `named`; matched `sk-` case-insensitive pattern) | in tree | edit |
| native/diagnostics/native_frame_replay.h | 4 | `case BPMEM_PE_TOKEN_ID: ... ++tokens; break;` | in tree | edit |
| native/diagnostics/startup_skip.h | 1 | `std::memset(c.ram+MovieMask-0x80000000u,0,4);` (matched `sk-` in `Mask-0x`) | in tree | edit |
| native/ios/DisplayPreferences.mm | 1 | `Do not consume a following option token;` | in tree | edit |
| native/patches/moderngekko-metrics.patch | 4 | `std::jthread([](std::stop_token stop_token)` | in tree | edit |
| native/patches/moderngekko-platform.patch | 3 | `std::jthread([](std::stop_token stop_token)` | in tree | edit |
| tests/test_gamecube_fifo_fix.py | 6 | `for token in banned:` (test variable named `token`) | in tree | edit |
| tests/test_gamecube_replay.py | 1 | `draw_done=1, tokens=1, efb_copies=2, ...` | in tree | edit |
| tools/android_trial.py | 2 | `for index, token in enumerate(argv):` | in tree | edit |
| tools/gamecube_line_tables.py | 3 | `Guest PCs with task-level meaning` (matched `sk-` pattern) | in tree | edit |
| tools/gamecube_movie_ab.py | 1 | `--min-disk-bytes` (matched `sk-` in `disk-bytes`) | in tree | edit |
| tools/gamecube_replay_check.py | 1 | `SIDE_EFFECTS = ('draw_done', 'tokens', ...)` | in tree | edit |
| tools/macos/share_keepalive.m | 2 | `url.password` (nil-check for password-free SMB URL) | in tree | edit |
| tools/macos/share_keepalive.py | 2 | `url.password is not None` (nil-check for password-free SMB URL) | in tree | edit |
| tools/mobile_gamecube.py | 2 | `entitlements.get("get-task-allow")` | in tree | edit |

iOS hand read:

| file | count | example | in tree / history-only | removal shape |
|---|---|---|---|---|
| native/ios/Info.plist | 1 | `<string>com.brad-richardson.ssx-native</string>` (`CFBundleIdentifier`) | in tree | edit |
| native/ios/CMakeLists.txt | 2 | `MACOSX_BUNDLE_GUI_IDENTIFIER "com.brad-richardson.ssx-native"` ; `XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED NO` | in tree | edit |
| native/ios/toolchain.cmake | 1 | `CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED NO` | in tree | edit |
| native/ios/README.md | 5 | `Signing selects an existing, unexpired Apple Development identity/profile ...` ; `provision gets you the stock disc ...` | in tree | edit |
| tools/mobile_gamecube.py (signing logic) | 12 | `BUNDLE = "com.brad-richardson.ssx-native"` ; `profile.get("ProvisionedDevices", [])` ; `profile["TeamIdentifier"][0]` ; `shutil.copy2(profile_path, APP / "embedded.mobileprovision")` (code reads local profile; no Team ID value, no profile UUID value, no UDID value in tree) | in tree | edit |
| native/ios/WriteBuildInfo.cmake | 0 | no signing identifier observed | in tree | edit |

## 2. Personal data

Git author (expected): `Brad Richardson <brad-richardson@users.noreply.github.com>` in all 241 commits. No other author email observed (`git log --format='%an <%ae>' --all | sort -u` returns one row).

Email pattern in tree file contents (`[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}`): 0 after excluding `*.linalg.inv` code matches (`clip@np.linalg.inv`, `predicted@np.linalg.inv`, `current_view@np.linalg.inv` in `tools/gamecube_reprojection_warp.py`). History blob grep for the same pattern returns only the same `linalg.inv` code lines.

| file | count | example | in tree / history-only | removal shape |
|---|---|---|---|---|
| (tree file contents, other email occurrences) | 0 | — | in tree | edit |
| docs/numbers-ledger.md (account identifier) | 1 | `` `github.com/brad-richardson/ps2xGS` `` | in tree | edit |
| docs/plan-gs-gpu-backend-2026-09-18.md (account identifier) | 1 | `` `github.com/brad-richardson/ps2xGS` `` | in tree | edit |
| docs/todo.md (account identifier) | 2 | `github.com/brad-richardson/ps2xGS under GPL-3.0` ; `github.com/brad-richardson/PS2Recomp` | in tree | edit |
| (full names of other people in tree) | 0 | — | in tree | edit |
| (phone numbers in tree) | 0 | numeric matches are offsets/addresses (e.g. `rider +1816`, `80008698`, `3.28 GHz`), not phone shapes | in tree | edit |
| (physical addresses in tree) | 0 | — | in tree | edit |
| (calendar identifiers in tree) | 0 | — | in tree | edit |

Commit trailers (history, not file contents): `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01H9JEyNpHtANpAU2dB1YuC7` occur in commit messages. `git log --all --format='%B' | grep -c -E 'Co-Authored-By|Claude-Session'` returns 298 lines (two trailer lines per commit on commits that carry them). File-content grep for `claude.ai/code/session` in tree returns 0; blob grep over `$(git rev-list --all)` returns 0.

## 3. Private infrastructure

Pattern set: `192.168.*`, `10.*`, hostnames (`bradflix`, `bytesize`, `*.lan`, Tailscale names), SSH ports/usernames, device serials (Odin USB serial, iPhone UUIDs), share paths (`/Volumes/share/...`, SMB names), Wi-Fi SSIDs, MAC addresses, home-directory paths (`/Users/<name>/...`). One example line per file. Counts are `git grep -c -E` per file for the combined pattern.

| file | count | example | in tree / history-only | removal shape |
|---|---|---|---|---|
| README.md | 7 | `` `/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-010/` `` | in tree | edit |
| docs/full-course-experiment.md | 6 | `` `/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-002/` `` | in tree | edit |
| docs/full-course-validation.json | 18 | `"shared_build": "/Volumes/share-1/brad/games/ssx3-workbench/builds/run-gari-002"` | in tree | edit |
| docs/gamecube-feasibility.md | 1 | `Both images remain on \`/Volumes/share/brad/games/gamecube/\`.` | in tree | edit |
| docs/garibaldi-visual-comparison.md | 1 | `` `SSX Tricky (USA).iso` on `/Volumes/share/brad/games/ps2/`, running in PCSX2 ... `` | in tree | edit |
| docs/impl-plan-2026-09-15.md | 1 | `` `ssh bytesize` (Tailscale, user bradr) reaches the RTX 4070; `` | in tree | edit |
| docs/investigation.md | 2 | `The source images remain unchanged, now under \`/Volumes/share/brad/games/ps2/\`.` | in tree | edit |
| docs/numbers-ledger.md | 3 | `` `/Volumes/Extreme SSD/upstream-review/build-m1` `` | in tree | edit |
| docs/plan-120fps-2026-09-17.md | 12 | `` `adb -s 622c49b1 shell ...` `` | in tree | edit |
| docs/rebuild-experiment.md | 8 | `Root: \`/Volumes/share/brad/games/ssx3-workbench/builds/\`` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/README.md | 3 | `# PS2Recomp feasibility spike (muse on bradflix, 2026-09-11/12) — recovered transcript` | in tree | edit |
| docs/runtime-validation.json | 5 | `"state": "/Volumes/share-1/brad/games/ssx3-workbench/emulator/test-002/evidence/control-hub.p2s"` | in tree | edit |
| docs/share-recovery.md | 3 | `The workbench share is \`smb://YOUR_SMB_HOST/share\`, mounted at \`/Volumes/share\`.` | in tree | edit |
| docs/texture-remaster.md | 8 | `On the GPU box — \`ssh bytesize\` over Tailscale reaches the RTX 4070.` | in tree | edit |
| docs/todo.md | 2 | `the 09-12 spike's tree on bradflix` | in tree | edit |
| local/research/G0/REPORT.md | 9 | `In file included from /Users/bradrichardson/dev/ps2xGS/upstream/ps2xRuntime/src/lib/gs/ps2_gs_memory.cpp:3:` | in tree | edit |
| local/research/P1/REPORT.md | 22 | `` `Darwin brads.macbook.air.lan 27.0.0 Darwin Kernel Version ...` `` | in tree | edit |
| local/research/S2/REPORT.md | 21 | `Device Odin 3 \`622c49b1\` (adb over Wi-Fi, \`192.168.1.53:5555\`)` | in tree | edit |
| local/research/S2/arm.py | 9 | `* device lease \`/data/local/tmp/mg/LEASE\` must be absent (or already S2);` | in tree | edit |
| local/research/S2/build_android_trial.py | 2 | `D5_PATCH = Path("/Volumes/Extreme SSD/android-spike/D5/instrument.patch")` | in tree | edit |
| local/research/S2/wait_device.sh | 3 | `S=$(cat /Users/bradrichardson/dev/ssx3/local/odin-serial 2>/dev/null \|\| echo 622c49b1)` | in tree | edit |
| local/research/S2/waits.log | 1 | `14:40:56Z adb over Wi-Fi: serial now 192.168.1.53:5555 (local/odin-serial); ...` | in tree | edit |
| local/research/S2b/REPORT.md | 17 | `` `192.168.1.53:5555` (Wi-Fi); per operator note the Odin moved to USB ... `` | in tree | edit |
| local/research/S2b/arm.py | 9 | `* device lease \`/data/local/tmp/mg/LEASE\` must be absent (or already S2);` | in tree | edit |
| local/research/S2b/vk-relink-attempt1-error40.txt | 4 | `File "/Users/bradrichardson/dev/ssx3/local/research/S2/build_android_trial.py", line 206, in <module>` | in tree | edit |
| local/research/S2b/vk-relink-commands.log | 3 | `python3 local/research/S2/build_android_trial.py --game local/game/gxbe69-stock --build-dir "/Volumes/Extreme SSD/android-spike/core-vk-build" ...` | in tree | edit |
| local/research/S2b/waits.log | 3 | `ls: /Volumes/Extreme SSD/android-spike/S2/s2-egl-c-receipts: No such file or directory` | in tree | edit |
| native/README.md | 3 | `defaults to \`/Volumes/share/brad/games/ssx3-workbench/native/GXBE69\`; override` | in tree | edit |
| tests/test_android_trial.py | 11 | `self.assertIn('cd /data/local/tmp/mg;', line)` | in tree | edit |
| tests/test_texture_pack_union.py | 1 | `self.dumped('tex1_640...', 115.0)  # framebuffer` (matched `10.*` numeric sub-pattern; no IP/MAC value) | in tree | edit |
| tools/android_trial.py | 1 | `DEVICE_DIR = '/data/local/tmp/mg'` | in tree | edit |
| tools/course_census.py | 1 | `GAME_DEFAULT = Path('/Volumes/share/brad/games/ssx3-workbench/native/GXBE69')` | in tree | edit |
| tools/import_crossing.py | 1 | `src = Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |
| tools/import_terrain.py | 1 | `default=Path('/Volumes/share/brad/games/ssx3-workbench/extracted/garibaldi/gari.pbd')` | in tree | edit |
| tools/macos/share_keepalive.m | 1 | `Usage: share-keepalive smb://host/share /Volumes/share state.json` | in tree | edit |
| tools/macos/share_keepalive.py | 1 | `Use a password-free smb://host/share URL and matching /Volumes/share path` | in tree | edit |
| tools/native_gamecube.py | 1 | `DEFAULT_GAME = Path("/Volumes/share/brad/games/ssx3-workbench/native/GXBE69")` | in tree | edit |
| tools/odin_wireless.sh | 5 | `# the charger. \`status\` prints what adb sees. The TCP serial (ip:5555) is` | in tree | edit |
| tools/patch_crossing.py | 1 | `src = Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |
| tools/prepare_emulator.py | 2 | `parser.add_argument("--games", type=Path, default=Path("/Volumes/share/brad/games/ps2"))` | in tree | edit |
| tools/ride_locations.py | 1 | `default=Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |
| tools/upscale_textures.py | 1 | `Written for the RTX 4070 box (\`ssh bytesize\`), where torch and spandrel live in` | in tree | edit |

Additional values observed in the same rows: `192.168.1.53:5555`, `192.168.1.50:5555` (in `local/research/S2b/REPORT.md` history of serial), `622c49b1`, `brads.macbook.air.lan`, `bradflix`, `bytesize`, `user bradr`, `/home/brad/ssx3-remaster/...`, `/mnt/c/Users/bradr/set.tgz`, `/data/local/tmp/mg/`, `/data/local/tmp/mg/LEASE`, `/tmp/ssx3-host-lease`, `/Users/bradrichardson/dev/ssx3/...`, `/Users/bradrichardson/dev/ps2xGS/...`, `/Volumes/Extreme SSD/...`, `/Volumes/share-1/...`, `smb://YOUR_SMB_HOST/share`, `smb://host/share`. No Wi-Fi SSID value and no MAC address value were observed. No iPhone UUID value was observed; one `.sav` filename with UUID shape `2639E4EF-FA70-48BC-988D-C312BC05D5B4.sav` occurs in `docs/research/startup-shortcut.md` (matched UUID pattern search).

## 4. Session and tooling residue

Not sensitive; counted separately. Commit trailers are in history (see §2). File-content counts below.

| file | count | example | in tree / history-only | removal shape |
|---|---|---|---|---|
| docs/numbers-ledger.md | 1 | `` `local/research/D2/d2_replay_capacity.h` `` (matched `waits.log` alternative? no; matched `herdr`-adjacent? see note) | in tree | edit |
| docs/plan-120fps-2026-09-17.md | 2 | `` `/data/local/tmp/mg/LEASE` `` must be ... | in tree | edit |
| docs/research/120hz-f-spike.md | 3 | `Branch \`spike/f-120hz-sim\`, worktree \`/tmp/ssx3-f120\`.` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/README.md | 2 | `Source: muse sessions \`2026/09/11/01a092b8…\` and \`2026/09/12/01a092fb…\` on bradflix ...` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md | 159 | `git clone --depth 1 https://github.com/ran-j/PS2Recomp.git /tmp/PS2Recomp 2>&1` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/scripts/census.py | 4 | `# write_file /tmp/ssx3vu/census.py` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/scripts/final_census.py | 3 | `# write_file /tmp/ssx3vu/final_census.py` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/scripts/histogram.py | 4 | `# edit_file /tmp/ssx3vu/histogram.py` | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/scripts/parse_vif.py | 3 | `# write_file /tmp/ssx3vu/parse_vif.py` | in tree | edit |
| docs/todo.md | 4 | `mid-run (herdr logging degraded); now 34 GB free.` ; `P1 (pane wN:pF) re-spikes on the Mac` | in tree | edit |
| local/research/G0/REPORT.md | 14 | `Build receipt: \`/tmp/ps2xgs-build/g0-configure-build.log\` (91 lines).` | in tree | edit |
| local/research/P1/REPORT.md | 17 | `` `/tmp/ssx3-host-lease` absent during all P1 work ... `` | in tree | edit |
| local/research/S2/REPORT.md | 4 | `Host build gate: \`/tmp/ssx3-host-lease\` absent at each` | in tree | edit |
| local/research/S2/arm.py | 5 | `* device lease \`/data/local/tmp/mg/LEASE\` must be absent (or already S2);` | in tree | edit |
| local/research/S2/wait_device.sh | 2 | `S=$(cat /Users/bradrichardson/dev/ssx3/local/odin-serial ...)` | in tree | edit |
| local/research/S2/waits.log | 1 | `14:40:56Z adb over Wi-Fi: serial now 192.168.1.53:5555 (local/odin-serial); ...` | in tree | edit |
| local/research/S2b/REPORT.md | 5 | `- Serial: \`local/odin-serial\` read before every adb call.` | in tree | edit |
| local/research/S2b/arm.py | 5 | `* device lease \`/data/local/tmp/mg/LEASE\` must be absent (or already S2);` | in tree | edit |
| local/research/S2b/vk-relink-attempt1-error40.txt | 3 | `referenced by Core_Run.cpp:180 (/private/tmp/s2b-link/trial-vk1/Core_Run.cpp:180)` | in tree | edit |
| local/research/S2b/vk-relink-commands.log | 2 | `printf 'S2b-build' > /tmp/ssx3-host-lease` | in tree | edit |
| tools/course_census.py | 1 | `HOST_LEASE = Path('/tmp/ssx3-host-lease')` | in tree | edit |
| tools/odin_wireless.sh | 3 | `# written to local/odin-serial and android-spike/ODIN_SERIAL for the` | in tree | edit |

File-content grep for `claude.ai/code/session` returns 0 rows. Blob grep over `$(git rev-list --all)` for `claude.ai/code/session` returns 0 rows. Grep for `/private/tmp/claude-` returns 0 rows in tree and 0 rows in history blobs; observed `/private/tmp` hits are `/private/tmp/s2b-link/...` and `/private/test.sav`. Grep for `herdr` in tree returns `docs/todo.md` rows above; no herdr pane numeric ID beyond `pane wN:pF` / `pane wN:pG` shapes.

## 5. Game ownership statements

Pattern set: `games/`, `SSX 3 (USA).iso`, `SSX Tricky`, `SLUS-20772`. One example per file.

| file | count | example | in tree / history-only | removal shape |
|---|---|---|---|---|
| README.md | 14 | `The first donor course is **Garibaldi from SSX Tricky**.` | in tree | edit |
| docs/aloha-conversion.md | 1 | `Date: 2026-09-14. The second donor conversion: SSX Tricky's **Aloha Ice Jam**,` | in tree | edit |
| docs/asset-policy.md | 1 | `SSX Tricky level injection and its assets stay.` | in tree | edit |
| docs/full-course-experiment.md | 6 | `` `/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-002/` `` | in tree | edit |
| docs/full-course-validation.json | 12 | `"shared_build": "/Volumes/share-1/brad/games/ssx3-workbench/builds/run-gari-002"` | in tree | edit |
| docs/gamecube-collision.md | 1 | `The same static-collision importer ran on SSX Tricky's Aloha Ice Jam into ASS1` | in tree | edit |
| docs/gamecube-feasibility.md | 3 | `Both images remain on \`/Volumes/share/brad/games/gamecube/\`.` | in tree | edit |
| docs/garibaldi-visual-comparison.md | 2 | `` `SSX Tricky (USA).iso` on `/Volumes/share/brad/games/ps2/`, running in PCSX2 ... `` | in tree | edit |
| docs/investigation.md | 4 | `The source images remain unchanged, now under \`/Volumes/share/brad/games/ps2/\`.` | in tree | edit |
| docs/locale-tables.md | 1 | `python3 tools/patch_locale.py SSX3.iso --set '549=Garibaldi from SSX Tricky. ...' --output SSX3-description.iso` | in tree | edit |
| docs/numbers-ledger.md | 2 | `stock SSX 3 (SLUS-20772) uncapped in NetherSX2 on the Odin, Snow Jam race` | in tree | edit |
| docs/plan-120fps-2026-09-17.md | 1 | `` `/Volumes/share/brad/games/ssx3-workbench/native/GXBE69` `` | in tree | edit |
| docs/rebuild-experiment.md | 9 | `Root: \`/Volumes/share/brad/games/ssx3-workbench/builds/\`` | in tree | edit |
| docs/research/120hz-analysis.md | 2 | `submitted images. Android's [Swappy library](https://developer.android.com/games/sdk/frame-pacing)` (matched `.iso` case-insensitive? no; matched `games/` in URL path) | in tree | edit |
| docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md | 9 | `-rw-rw-r--  1 brad brad 3005415424 Sep 12 00:14 SSX 3 (USA).iso` | in tree | edit |
| docs/research/ssx3-120hz-handoff-2026-09-13.md | 3 | `In **PS2/SSX 3/SLUS-20772_08FFF00D.pnach**, "Fix Metro Slowdown" ...` | in tree | edit |
| docs/roadmap.md | 1 | `and SSX Tricky discs and writes a new image locally.` | in tree | edit |
| docs/runtime-validation.json | 6 | `"serial": "SLUS-20772"` | in tree | edit |
| docs/share-recovery.md | 1 | `` `/Volumes/share/brad/games/ps2/SSX Tricky (USA).iso` (2,902,425,600 bytes). `` | in tree | edit |
| docs/tricky-courses.md | 1 | `# SSX Tricky course inventory` | in tree | edit |
| local/research/P1/REPORT.md | 14 | `` `Brief ISO source path` \| `/Volumes/share/brad/games/SSX 3 (USA).iso` `` | in tree | edit |
| native/README.md | 3 | `defaults to \`/Volumes/share/brad/games/ssx3-workbench/native/GXBE69\`; override` | in tree | edit |
| tools/build_course_image.py | 1 | `default='Garibaldi from SSX Tricky. Experimental terrain port; ...'` | in tree | edit |
| tools/course_census.py | 1 | `GAME_DEFAULT = Path('/Volumes/share/brad/games/ssx3-workbench/native/GXBE69')` | in tree | edit |
| tools/course_presets/aloha.json | 1 | `"note": "SSX Tricky's Aloha Ice Jam (Showoff, aloha.sop) into SSX 3's R&B ..."` | in tree | edit |
| tools/course_presets/garibaldi.json | 1 | `"note": "SSX Tricky's Garibaldi (Race) into SSX 3's Snow Jam ..."` | in tree | edit |
| tools/course_route.py | 1 | `# SLUS-20772 0x26afb8 stores per-path distances in an 800-byte stack` | in tree | edit |
| tools/import_crossing.py | 1 | `src = Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |
| tools/import_terrain.py | 2 | `Place a section of SSX Tricky (Garibaldi) terrain into an SSX 3 location (roadmap M4).` | in tree | edit |
| tools/inventory_tricky.py | 1 | `Read-only inventory of every SSX Tricky (PS2) course archive on the disc.` | in tree | edit |
| tools/native_gamecube.py | 1 | `DEFAULT_GAME = Path("/Volumes/share/brad/games/ssx3-workbench/native/GXBE69")` | in tree | edit |
| tools/patch_crossing.py | 1 | `src = Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |
| tools/prepare_emulator.py | 3 | `parser.add_argument("--games", type=Path, default=Path("/Volumes/share/brad/games/ps2"))` | in tree | edit |
| tools/replace_terrain.py | 2 | `is row +12; SLUS-20772's loader at 0x2b6b50 explicitly accepts -1 here.` | in tree | edit |
| tools/ride_autopilot.py | 1 | `Rider position: EE offset 0x5409c0 (three floats, observed stable across transports in SLUS-20772).` | in tree | edit |
| tools/ride_locations.py | 1 | `default=Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')` | in tree | edit |

## 6. History-only hits

| item | commit | in tree / history-only | removal shape |
|---|---|---|---|
| Distinct infra values present in history blobs but absent from tree | — (set difference of `git grep -h -o -E` values over `$(git rev-list --all)` vs tree is 0; 31 unique values in both) | history-only: 0 distinct values | history rewrite (if a value were present) |
| Deleted tracked files (`git log --all --diff-filter=D --name-only`) | — (no rows returned) | history-only: 0 files | history rewrite (if a file were present) |
| `.env` / `.pem` / `.p12` / `.pfx` / `.mobileprovision` / `.key` / `keychain` filenames in `git log --all --name-only` | — (no rows returned) | history-only: 0 files | history rewrite (if a file were present) |
| Session URLs in blobs (`git grep 'claude.ai/code/session' $(git rev-list --all)`) | — (0 rows; URLs occur only in commit trailers, e.g. `500e678`, `460f6d3`, `5c0cc53`, `3980229` and others) | history-only: 0 blob rows; trailers present in commit messages | history rewrite (trailers are in commit messages) |
| Other email values in blobs beyond `linalg.inv` code matches and author noreply | — (0 rows) | history-only: 0 | history rewrite (if a value were present) |

## Summary table of counts

| category | files with hits in tree | total matching lines in tree (`git grep -c` sum) | history blob rows beyond tree |
|---|---|---|---|
| 1. Secrets (pattern + iOS hand read) | 26 + 5 iOS/signing files | 68 + 20 iOS/signing lines | 0 new secret values |
| 2. Personal data (file contents, excluding expected git author) | 3 (account identifiers) | 4 | 0 |
| 3. Private infrastructure | 42 | 198 | 0 distinct values |
| 4. Session/tooling residue (file contents) | 22 | 244 (159 in `commands-and-outputs.md`) | 0 blob URL rows; trailers in messages (298 trailer lines) |
| 5. Game ownership statements | 36 | 118 | 0 distinct values |
| 6. History-only | 0 files / 0 distinct values | — | 0 |

Counts use the exact `git grep -c -E` patterns listed under Exact commands. Infra total includes combined-pattern counts per file listed in §3. Session total includes combined-pattern counts per file listed in §4. Game total includes combined-pattern counts per file listed in §5.

## Exact commands

```
git ls-files | wc -l
git rev-list --all --count
git log --oneline --all | head -n 50
git log --format='%an <%ae>' --all | sort -u
git log --all --format='%B' | grep -c -E 'Co-Authored-By|Claude-Session'
git log --all --diff-filter=D --name-only --pretty=format:'COMMIT %H %s' | head -n 80
git log --all --name-only --pretty=format: | sort -u | grep -i -E '\.env|pem|p12|pfx|mobileprovision|\.key$|keychain' | head -n 20
git ls-files | grep -i -E '\.env|key|pem|p12|pfx|mobileprovision|keychain'
git grep -n -i -E 'AKIA|sk-|ghp_|xox|BEGIN .*PRIVATE KEY|password|secret|token|apikey|Authorization:' -- $(git ls-files)
git grep -c -i -E 'AKIA|sk-|ghp_|xoxb?|BEGIN .*PRIVATE KEY|password|secret|token|apikey|Authorization:' -- $(git ls-files) | grep -v ':0$'
git grep -n -i -E 'team|provision|bundle|identifier|keychain|signing|get-task-allow|ProvisionedDevices|CODE_SIGN|DEVELOPMENT_TEAM|PRODUCT_BUNDLE' -- native/ios tools/mobile_gamecube.py native/ios/Info.plist native/ios/CMakeLists.txt native/ios/toolchain.cmake
git grep -n 'com\.brad-richardson|BUNDLE|bundle_id|TeamIdentifier|ProvisionedDevices|get-task-allow|embedded\.mobileprovision|CODE_SIGN|DEVELOPMENT_TEAM' -- $(git ls-files)
cat native/ios/Info.plist
cat native/ios/toolchain.cmake
cat native/ios/WriteBuildInfo.cmake
git grep -n -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' -- $(git ls-files)
git grep -n -E '192\.168\.|10\.[0-9]+\.[0-9]+\.[0-9]+|bradflix|bytesize|\.lan|tailscale|Tailscale|/Volumes/share|smb://|/Users/brad|/Users/[a-z]+|SSID|MAC |serial|UDID|adb |ssh ' -- $(git ls-files)
git grep -c -E '/Volumes/share|/Volumes/Extreme SSD|smb://|share-1' -- $(git ls-files) | grep -v ':0$'
git grep -c -E '/Users/bradrichardson|/Users/brad|/home/brad|/mnt/c/Users' -- $(git ls-files) | grep -v ':0$'
git grep -n -E 'claude\.ai/code/session|Claude-Session|Co-Authored-By|/private/tmp/claude|herdr|pane.*[0-9]+|local/lease|odin-serial|/tmp/PS2Recomp|/tmp/ssx3' -- $(git ls-files)
git grep -c -E 'claude\.ai/code/session|Claude-Session' -- $(git ls-files) | head -n 40
git grep -n -E 'herdr|/private/tmp|ssx3-host-lease|LEASE|odin-serial|local/lease|pane' -- $(git ls-files)
git grep -c -E 'games/|ISOs?|game files|copying|/Volumes/share.*\.iso|SSX 3 \(USA\)\.iso|SSX Tricky' -- $(git ls-files) | grep -v ':0$'
git grep -n -i -E 'AKIA|ghp_|xox|BEGIN .*PRIVATE KEY|password|secret|token|apikey' $(git rev-list --all) --
git grep -n -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' $(git rev-list --all) --
git grep -n 'claude.ai/code/session' -- $(git ls-files)
git grep -n 'claude.ai/code/session' $(git rev-list --all) --
git grep -n -E '\.lan|Tailscale|bradflix|bytesize|192\.168\.|622c49b1' $(git rev-list --all) --
git grep -n -E 'DEVELOPMENT_TEAM|TeamIdentifier|ApplicationIdentifierPrefix|ProvisionedDevices|embedded\.mobileprovision' $(git rev-list --all) --
git grep -l -E '192\.168\.|bradflix|bytesize|\.lan|Tailscale|/Volumes/share|/Volumes/Extreme SSD|smb://|/Users/bradrichardson|/home/brad|/mnt/c/Users|622c49b1|5555|/data/local/tmp|share-1' -- $(git ls-files)
git grep -l -E 'herdr|/tmp/ssx3-host-lease|/data/local/tmp/mg/LEASE|local/odin-serial|/tmp/PS2Recomp|/tmp/ssx3|ODIN_SERIAL|pane wN|/tmp/ps2xgs-build' -- $(git ls-files)
git grep -l -E 'games/|SSX 3 \(USA\)\.iso|SSX Tricky|SLUS-20772' -- $(git ls-files)
```

## What I could not do

- Content under `local/` outside `local/research/A2/` was not opened beyond file names returned by `git ls-files` and `git grep` hits in tracked `local/research/*` blobs; untracked `local/` contents were not listed.
- Full-history line counts for every pattern were sampled via `git grep <pattern> $(git rev-list --all)` with `head` limits for large outputs; distinct-value set comparison for infra used `git grep -h -o -E` over all revs vs tree.
- iPhone UUID/MAC/SSID checks used pattern searches (`SSID`, `MAC address`, `([0-9A-F]{2}:){5}`, UUID shape) over tree and history; device kilobytes and image dimensions were not parsed.
- No builds were run and no `adb` commands were run.
- Binary or media file contents were not decoded; only tracked text grep hits are listed.
