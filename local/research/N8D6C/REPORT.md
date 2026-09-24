# N8D6C — one Odin scanout-stage run

**State:** Released for one install and launch. The first failed brief step was the tick-2100 stop without a complete receipt; cleanup completed. The orchestrator owns frame inspection and any causal verdict.

## Fixed inputs and release hold

| Field | Predeclared pin or plan | Observed |
| --- | --- | --- |
| Odin | Serial `622c49b1`; lease `/data/local/tmp/mg/LEASE` | online; lease free before claim and released after run |
| APK | `/Users/brad/dev/ssx3-work/N8D6B/app-release.apk`; SHA-256 `6839a0a48ed1b55affb6e6bd952a269ba3736200255bb6628270bb11a874a611`, two reads | matched on two local reads |
| Packaged runner | SHA-256 `4e6c056dc48683ab725e16792748b83a122421d865f523d6d37c4bbb27fa0efd`; Build ID `8d19e78d5e5eb7cb547be96b9ebb1a72b31a99f0` | SHA matched on two APK reads; Build ID from N8D6B package gate |
| Packaged Turnip | SHA-256 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | matched on two APK reads |
| Packaged HAL shim | SHA-256 `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | not found |
| Installed ELF | SHA-256 `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`, two device reads | not found |
| Installed ISO | SHA-256 `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`, two device reads | not found |
| Launcher | `local/research/N8D6C/launch.py`; SHA-256 `58beb05fbdb7d57015e12b528645ca598c84fd77ae4a4fcfc473686201edad1d` (two matching reads) | prepared |
| Run budget | One install, one launch; no second run | 1 install, 1 launch, no retry |

The launcher requires `--released-sha <reviewed SHA-256>` and refuses a changed file or reused scratch receipt. Intended command from `/Users/brad/dev/ssx3`: `python3 -u local/research/N8D6C/launch.py --released-sha 58beb05fbdb7d57015e12b528645ca598c84fd77ae4a4fcfc473686201edad1d`. The orchestrator released this exact SHA before any device action; the one run followed the SHA-gated command.

## Preregistered gate

All categories require the same first aligned frame: tick 2050, FBP 112, PMODE `ff21`, frontend 512×448; circuit1 and pre-deinterlace merged each 512×224 and 448 tiles; final 512×448 and 896 tiles; all three stage controls 128; old final control `128 expected=128 PASS`; sampled and raw summaries each 896 tiles; both continued vectors decode to exactly 896 little-endian u32 counts, each vector sum and active count match its summary, and vectors equal at all 896 positions. The final stage occupied and active counts must match sampled summary. A same-run tick-2050 PNG and metadata must identify 512×448, display/source FBP 112/112, fallback 0 and PMODE `0xff21`. No probe or pipeline error. Active means a 16×16 tile has at least 32 qualifying pixels.

| Category | Additional active-count thresholds |
| --- | --- |
| A | circuit1 ≤100/448; merged ≤100/448; final sampled/raw ≤100/896 |
| B | circuit1 ≥250/448; merged ≤100/448; final sampled/raw ≤100/896 |
| C | circuit1 ≥250/448; merged ≥250/448; final sampled/raw ≤100/896 |
| OTHER | Every other observation, including missing or failed gate data |

These are observation labels only. The Mac replay and Odin routes are not byte-identical GS streams.

## Intended device procedure and stop rules

Preflight before install: online serial, free lease, keyguard `showing=false`, charging or full battery ≥20%, and ≥1 GiB free. Claim lease; install even if already installed; double-read installed APK, ELF and ISO; require empty `mc0` and unique empty frame directory. Recheck unlock and battery immediately before launch. Set `PS2X_GS_BACKEND=parallel`, Turnip, dev movie bypass, installed ISO, I26-FAST vsync pad route, `PS2X_N8D5_TILE_CAPTURE=1`, one frame dump at tick 2050, and progress-only vsync log. Capture same-PID logcat to a 16 MiB cap and send BACK once after six seconds for the USB dialog.

Stop at first complete alignment, three stage summaries, control, sampled/raw vectors and tick-2050 PNG/metadata; first fatal or process exit; tick 2100 without complete receipt; 180 s below tick 1700; or 300 s wall. Force-stop, verify PID gone and release lease on success or error. Pull only tick-2050 PNG/txt and compare two device plus two local SHA reads. Compress the closed full log in Mac scratch. Mac scratch cap 500 MiB; committed text/image cap 8 MiB; global mini ssx3 cap 200 GB.

## Run receipt

| Field | Observation |
| --- | --- |
| Script SHA and environment SHA | `58beb05fbdb7d57015e12b528645ca598c84fd77ae4a4fcfc473686201edad1d` (two prelaunch reads); env `4f975acc6c28c47ad0d1326df7d6ccd10850d53decab149824bfa564031ec994` matched local/device read. |
| Device preflight | Online `device`, free lease, keyguard `false`, battery 100% and full (`status=5`), 25,915,441,152 bytes free. Immediately before launch: held lease, keyguard `false`, battery 100%/full, 25,760,276,480 bytes free. |
| Install and input pins | One `adb install -r`: `Success`. Installed APK, ELF, ISO each matched its stated SHA on two device reads. Local APK and packaged runner/Turnip/HAL each matched on two reads. `mc0` empty; unique empty dump dir created. |
| Launch and stop | One launch, PID `17446`; one BACK at six seconds; elapsed 125.549 s; last progress tick 2136. Stop: `tick 2100 without complete receipt`. No second run. |
| Alignment | Tick 2050, FBP 112, PMODE `ff21`, frontend 512×448. |
| Circuit1 | 512×224; 448 tiles; occupied 3046; active 21; control 128. |
| Pre-deinterlace merged | 512×224; 448 tiles; occupied 3046; active 21; control 128. |
| Final | 512×448; 896 tiles; occupied 5894; active 39; control 128. |
| Old final control and summaries | `128 expected=128 PASS`; sampled `896/5894/39`; raw `896/5894/39` (tiles/occupied/active). |
| Sampled/raw vectors | Launcher returned null for both, so its complete-receipt gate did not pass. Offline parsing of the captured same-PID log found two segments per vector, 896 u32 words each, sum 5894, active ≥32 count 39, exact equality 896/896, packed little-endian SHA `3f06a58ad6805c695a01c305fe06b52cc0d92198a6fb699aeee0c4ea09681ba5` for both. See [vector-audit.json](vector-audit.json). The continuation begins with a comma after a preceding segment ends in a digit; the released parser treats that leading comma as an empty field. |
| PNG and metadata | Log says `[frame:dump] seq=0 tick=2050 size=512x448 fbp=112/112 fallback=0 fnv1a=5da9eba2`. The launcher stopped before pull. Device/local SHA, metadata, and viewed frame path: not found. |
| Probe/pipeline error | None in the same-PID captured log or parser result. |
| First failed brief step | Preregistered tick-2100 stop without a complete receipt. Launcher exit code 1; `RuntimeError('tick 2100 without complete receipt')`. |
| Cleanup | `am force-stop` completed, PID absent, lease `LEASE_FREE N8D6C done`; closed full log compressed. |
| Handoff category | **OTHER**, because the released launcher did not complete the vector and PNG/metadata gate. No causal verdict. |

## Exact command and bounded receipts

The reviewed command was run once from `/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D6C/launch.py --released-sha 58beb05fbdb7d57015e12b528645ca598c84fd77ae4a4fcfc473686201edad1d
```

[launcher.diff](launcher.diff) is the exact reviewed diff from N8D5G; `launch.py` was not edited after release. Bounded committed receipts: [result.json](result.json), [driver.log](driver.log), [tile-excerpt.txt](tile-excerpt.txt), [vector-audit.json](vector-audit.json), and [ps2x.env](ps2x.env). The single closed full log remains at `/Users/brad/dev/ssx3-work/N8D6C/logcat-all.txt.gz` (5454 bytes, SHA-256 `7d7548c2246130d3471f3f7f59e963d872e3a049fe0fadfbd703d6c4869516f9`); same-PID log SHA `87ddf748abb6c6d976c91aefce0d401808c446b6719d5e28871668e3107701df`. Scratch is 52 KiB, report directory 108 KiB, global mini ssx3 usage 138.7/200 GB.

## Gaps

No tick-2050 PNG/txt was pulled after the first failed brief step. Its device and local hashes, metadata, and visual appearance remain unobserved. The offline vector audit is a receipt from the existing log and does not revise the preregistered `OTHER` category. No extra device action, second install/launch, source/build/fork change, push, iOS action, upstream contact, speed claim, or causal verdict.
