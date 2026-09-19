# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] **I3 read (09-19) — PASS, raylib decision fully tabled:** A:
      no release/master has an iOS backend (PR #3880 closed
      unmerged); 6.0 breaks itemized, project uses 0 changed APIs;
      B: `ghera/raylib-iOS` prior art (789-line backend + ANGLE
      packaging) sized with file table; C: SDL probe configures
      (C2 exit 0) + TU probes (rcore clean, raudio needs ObjC);
      G7 touch gap persists under B/C. No verdict given, as
      briefed. Verified: 6.0 enum/platforms, rlImGui tag, 789 lines,
      C2 log, syntax logs, 26 SDL files, fork untouched by I3, disk
      41G. DECISION OWED (orchestrator → user): upgrade / fork-patch
      / SDL. Ledger row added.
- [ ] **M12 read (09-19) — PASS, same-frame partition measured:**
      4 windows × 25/25 uniform on one frame (70584 / 2572 / 33377 /
      34105); removed shares 68012 / 37207 / 36479 with the honest
      non-additivity (105219 vs 70584) tabulated; slot-36 indexed
      decode on 2 frames (pos 0/0, Tex1 254/92, Tex2-indexed 0) +
      own true deltas (1372/1827 B); per-draw depth restated open
      (no header hook, re-verified). Verified: header shas,
      analyzer rows, window rows verbatim, 6 refhashes, 3/3 hashes,
      lease log (0 waits). Ledger row added.
- [ ] **P1t + M12 + I3 launched (09-19, user go-ahead):** P1t (FIX:
      mid-label invocation dispatch, first behavior fix + ≤2 boots)
      reuses P1s pane; M12 (same-frame partition via alternating NOP
      streams + slot-36 indexed decode) reuses M11 pane; I3 (raylib
      decision spike: upgrade/fork-patch/SDL evidence, read-only, no
      verdict) reuses I2 pane. Remaining queue: `sceGsSyncVCallback`
      test fix (fork, after P1t).
- [ ] **M11 read (09-19) — PASS, partitions measured:** slot-36 delta
      moves 501 B on 100/100 (texcoord stage excluded); `pnmtxidx`
      decoded (49–118 exposed draws/frame, cross-checked vs M9);
      indexed-only arm 498 B + shared-only arm 72719 B surviving;
      NOPTEXT arm 44470 B surviving (texture epochs cancel by
      restore). Honest frame-confounded caveat throughout (each arm
      its own frame — same-frame partition open). Verified: header
      shas, analyzer rows, ref2 rows + all 4 refhashes, 6/6 hashes,
      lease log (0 waits). Ledger row added.
- [ ] **I2 read (09-19) — PASS, CMake fixes land, raylib wall stands:**
      3 commits (G4 BUNDLE DESTINATION +17/-5, G6 FFmpeg-iOS-OFF,
      G5 ARM-inference + FATAL guard), pushed; desktop-proof
      (cmake_install byte-identical `790994cb`, build green, tests
      424/425 same pre-existing failure — which independently re-names
      the queued test fix); probe A hits G1 (enum rejects iOS),
      probe B passes G4/G6 and dies on G3 (OPENGL_LIBRARY NOTFOUND);
      raylib untouched per scope. One disclosed nit: desktop build
      compiled with P1s's then-uncommitted edit present (CMake-only
      fixes unaffected). Verified: 3 diffs, sha, 4 log lines, no sims
      booted, scratch 196K. Next: I3 = the raylib decision (needs a
      scope call: upgrade / fork-patch / SDL switch). Ledger row added.
- [ ] **P1s read (09-19) — PASS, callback body never dispatched:**
      signal path intact (no callback guard anywhere — identical wake
      decision both paths); the CD callback invocation is attached
      then SILENTLY dropped (`hasFunction(0x3e3ad8)` false, mid-label,
      pc zeroed, popped, no trace); signal census complete (1360×29
      from `0x31abf0`, pump 66×4 + 8×5 thread-site only, pump-i 0,
      callback site 0); pump semas named. So sema-26 "non-delivery" =
      non-dispatch: the fix is a table entry / mid-label invocation
      rule, not scheduler wake logic. Next: P1t (fix brief).
      Verified: 2917 sema lines, 3-line record verbatim, absences,
      census incl. 66+8 split, CSV absence, fork pushed. Ledger row added.
- [ ] **P1s + M11 + I2 launched (09-19, user go-ahead):** P1s (sema-26
      delivery mechanism: signal/wait paths + `Diag:` commit + ≤2
      boots) reuses P1r pane; M11 (slot-36 delta + indexed partition
      + NOPTEXT share) reuses M10 pane; I2 (fork CMake fixes G4/G6/G5
      + configure/build attempt, raylib wall out of scope) reuses I1
      pane. Note: P1s + I2 share the fork tree (different files;
      both briefed pull --rebase-and-retry-once on push reject).
      Remaining queue: `sceGsSyncVCallback` test fix (fork, after P1s).
- [ ] **I1 read (09-19) — PASS, spike correctly FAILED with receipted
      gaps:** pinned raylib 5.5 has NO iOS backend (enum rejects iOS,
      no `rcore_ios`, bundled GLFW/RGFW iOS-free); configure dies on
      the fork `install()` missing BUNDLE DESTINATION (all 4 attempts,
      2 generators — needs a fork CMake edit, out of spike scope);
      sse2neon fixed by toolchain v2; FFmpeg host dylibs can't link
      iOS (mirror Android OFF); touch input nowhere (runtime +
      rlImGui). 7 gaps (3 dep-code sharing one root, 3 config, 1
      platform). Constraints obeyed: runtimes unchanged, fork
      untouched, scratch 112K, heavy dirs on SSD, disk still 42G
      free. Verified: enum/platforms, install line, error in log,
      SSD dirs, runtimes, disk. Next: I2 needs fork write access.
      Ledger row added.
- [ ] **M10 read (09-19) — PASS, zero-pixel mystery SOLVED:** order
      excluded (0/689 consuming draws before first covering load),
      matrices live (11/11 siblings bit-identical, live==snap),
      visibility excluded (96–99% in-range, 0 culled) — and the
      pixel-compare audit proves M7/M8/M9 "0 pixels" measured the
      skip-to-VRAM uninit pattern, not rendered output (det5/det6
      NOP-all contrast 0/200 vs 200/200). True-delta arm: slot-0
      delta moves 32954/573440 bytes on 100/100 replays vs rendered
      pristine ref. Open: per-draw depth, indexed-path partition,
      texture-mediated share, slot-36 delta. Verified: header shas,
      analyzer rows, ref2 event verbatim, 7/7 hashes, lease log (0
      waits). Ledger row added.
- [ ] **P1r read (09-19) — PASS, signal-during-park ORDER proven:**
      worker wakes once on 3E4648's signal, passes G1/G2/G3/G5,
      issues the CD read, re-parks at G0 BEFORE the callback's
      signal (:433→:434); site #9 never reached, G6 never evaluated;
      site #7 never armed (topbyte-1 path A). Poll registration
      (`0x3e33b0` via table + `jalr`) + worker-thread trigger closed
      statically; 77 ELF words machine-checked. Delivery mechanism
      stays out of scope — but it is now THE critical-path item (P1s
      should take sema-26 delivery; nothing else unblocks FILESYS).
      Verified: 57 watches + epoch lines verbatim, thread-2 sch,
      ELF spot, P6 802 lines, fork untouched, waits log (M10
      deference). Ledger row added.
- [ ] **P1r launched (09-19):** CD-completion→W1 gap — worker path
      gates + poll registration + lost-wake candidates statically,
      minimal watch set dynamically (≤2 boots). Reuses P1q pane.
      Remaining queue: `sceGsSyncVCallback` test fix (fork, after P1r).
- [ ] **P1q read (09-19) — PASS, entry 0 never queued + slot-reuse
      decoded:** entry 0 fills (id `0x900001`, prio `0x64`) but takes
      `3DDAC0` path B (no device match — `+0x24` never written, never
      enqueued, `+0x2C` stays 0); full 12-word entry layout + 7
      allocators + 5 dequeue predicates + nibble→case dispatch (jump
      table 9/9 ELF) + all 10 W1 sites tabled; entry-1 "re-select" is
      slot reuse (cleared, re-alloc'd nibble 4/id 3, selected for a CD
      read whose callback fires but never reaches W1 — the chain
      breaks at CD→W1, poll-vs-lost-wake open). Verified: 38 watch
      lines + key lines verbatim, jump table, ELF spot, P6 row, fork
      untouched, lease clean. Next: P1r. Ledger row added.
- [ ] **I1 launched (09-19, user go-ahead):** iOS spike — dep
      inventory + platform surface + configure/build attempts for
      iphonesimulator arm64, gaps as fix-classed rows, no fixes.
      Read-only in fork, no lease, no device. Reuses P6 pane. First
      agent on `--reasoning-effort max`. Constraints (user, steered
      mid-run): ONLY the installed iOS 27.0 runtime + existing
      devices, never download runtimes; internal disk 42 GB free —
      scratch in `/tmp/ps2x-ios-spike`, >500 MB to SSD, never touch
      other agents' build dirs.
- [ ] **P1q + M10 launched (09-19):** P1q (why entry 0 is never
      selected/completed: entry contents + ExecCommand selection +
      completion trigger, ≤2 boots) reuses P1p pane; M10
      (discriminating instruments: hit/draw order + full matrices +
      render-target/occlusion) reuses M9 pane. G-lane resting.
      Remaining queue: `sceGsSyncVCallback` test fix (fork, after P1q).
- [ ] **M9 read (09-19) — PASS, residue narrowed hard:** VAT+texgen
      closed (M8's 1346-draw Tex2 reach corrected to 21 shared+enabled;
      slot-0 shared-pos reach 664–800); upload timing EXCLUDED
      (snapshots hold perturbed values 200/200, dirty flags fire);
      shadow copy EXCLUDED; yet 21 Tex2 + 800 Pos draws consume
      perturbed matrices with 0/200 pixels differing. Residue: hit/draw
      order, full-matrix values, render-target/occlusion, texcoord
      stage — discriminating instruments specified, not built (M10).
      Verified: header sha, analyzer rows, xform_stats ×2 verbatim,
      4/4 hashes, lease log (1 P1p wait). Ledger row added.
- [ ] **G6 read (09-19) — PASS, -O2 collapses the delta:** Release
      (-O3) CTest 12/12 green, no fixes; cpu median 15.8→0.36 ms —
      the G4 fast-path advantage vanishes (all backends ~0.35–0.55,
      within noise); -O0 columns re-measured in-session and match
      G4/G5; PR prep file written with verified figures, nothing
      submitted, no network writes. Verified: ninja flags, CTest
      re-run, spot timing both exact, PR.md base rev, CMakeLists +
      upstream untouched by G6, pushed. Implication recorded: CPU
      backend at release is sub-ms on synthetics — GPU urgency
      question reopens on game-sized frames. Ledger row added.
- [ ] **P1p read (09-19) — PASS, entry-0 flag never set:** table base
      `0x5e0080` + current-entry transitions (entry 1 / null, never
      entry 0) learned; entry-0+8 = `0x5e0088` watched: exactly ONE
      hit, an init-time zeroing `sd` @ `0x3e64d0` (memset loop in
      `sub_003E6448`); W1/W2/W3 all silent across the boot. So the
      SYNCTASK wait never exits because entry 0 is never completed —
      current entry is entry 1. Next: P1q (why is entry 0 never
      selected/completed?). Verified: 9 + 1 watch lines verbatim,
      counts, ELF 3/3, P6 absence, fork untouched, lease clean.
      Ledger row added.
- [ ] **G6 launched (09-19, user go-ahead):** Release-build numbers
      (-O2 CTest + timing tables on all four backends vs -O0) +
      upstream PR prep (`upstream-patches/PR.md`, verified figures,
      NO submit). Reuses G5 pane. 4h box, no lease.
- [ ] **P1p + M9 launched (09-19, user go-ahead):** P1p (which flag
      writer fires for entry 0: table-addrs boot + writer-catch boot,
      max 2) reuses P1o pane; M9 (VAT/texgen closure + upload-timing
      survival test + PosNormal-path delta) reuses M8 pane. G-lane
      RESTING (G1 still gated; upstream submission needs an explicit
      publish call). Remaining queue: `sceGsSyncVCallback` test fix
      (fork, after P1p).
- [ ] **M8 read (09-19) — PASS, propagation scoped, mechanism open:**
      baseline reproduces M7; slot census on 3 frames (slot 0 read +
      796–906 PosNormal draws — NOT unused, deepening M7's puzzle;
      7-way all-draws tie at 36/39/42/45/48/51/60); slot-36 delta
      (53 hits/replay, Tex2-only) moves zero pixels → re-scoped per
      the clause to "seam writes don't reach rendering"; projection
      UNREACHABLE (2 seam call sites, regs branch has none,
      regcalls=0/514k, 11 proj writes all via regs path). Honest
      gaps: VAT/indexed-vs-shared split, per-draw texgen enablement
      undecided. Next: M9 (upload-timing/shadow-copy mechanism + a
      PosNormal-path delta). Verified: header sha, analyzer rows,
      xform_stats verbatim ×2, 4/4 hashes, lease log (1 P1n wait).
      Ledger row added.
- [ ] **G5 read (09-19) — PASS, spikes are real patches:** 3 files
      (6/5/4 hunks, 4376/4893/4638 B), each dry-run clean solo on my
      own scratch copy; proof target (`patched-cpu`, build-time
      apply, submodule pristine) identity-exact on 102/102 with G4's
      timings reproduced (0.55 standard, 6.1 multi); CTest 12/12
      (11 old + patched-identity). Patches inherit G3/G4 caveats,
      disclosed; not submitted upstream. Verified: hunks/bytes,
      dry-runs, submodule rev, smoke replay, CTest re-run, pushed.
      Ledger row added.
- [ ] **P1o read (09-19) — PASS, caller saga CLOSED + writers named:**
      true-frame watch lands exactly 1 hit each (`0x900001` @
      `0x3dd1e0`, `0x3ded88` @ `0x3dd214`, sp `0x1fffe00`) with the
      probe line byte-identical to p1n; parked `$a0` top byte `0x00`
      → entry 0; static hunt names ONE `0x519AD8` writer (`0x3dccfc`,
      table from `systemInit`-called allocator) + THREE flag writers
      (W1 `0x3de468` = P6 `iFILESYS_CommandCompleteCallback`, W2
      `0x3dd83c` = 1, W3 `0x3ddd30` = −2) with full exclusion census
      + 14 ELF words, all machine-checked (standing rule obeyed —
      paste block present); brief's slot formula corrected (stride
      `0x10`, not +8·slot). Open: which writer fires for entry 0 at
      runtime (receipt designed: watch `0x519AD8`+`0x519AD4`). Lease
      exemplary (deferred to M8, never forced). Verified: lines
      :687–:689 verbatim, counts, ELF 6/6 spot, P6 :735, fork
      untouched, waits log. Next: P1p. Ledger row added.
- [ ] **P1o + G5 launched (09-19):** P1o (true-frame watch confirm +
      driver-flag writer hunt, ≤2 boots; carries the new standing
      rule: machine-check every hand hex) reuses P1n pane; G5 (port
      CLUT/RMW/Present spikes to real upstream patches + proof
      target) reuses G4 pane. M8 still working. Remaining queue:
      `sceGsSyncVCallback` test fix (fork, after P1o).
- [ ] **G4 read (09-19) — PASS, Present fast path lands:** profile
      (sample + instrumentation) attributes single-shot ~16 ms to
      vector fill-construct/teardown (~96% Present); `[G4-PRESENT]`
      bulk scratch buffers cut median_ms 15.8→0.55 on standard
      captures (6.1/3.2 on multi/field paths — temp destroys
      disclosed as remaining); identity exact on 102/102; CTest
      11/11 (no new tests — spike-identity pins it); captures
      unchanged (md5s match G3). Verified: +67/-7 one file,
      upstream/strict/factory untouched, CTest re-run, timing
      reproduced (15.539 vs 0.550, both exact), pushed. Caveat: all
      -O0 libc++ observations. Ledger row added.
- [ ] **P1n read (09-19) — PASS, caller NAMED + slip found:** probe
      (`e73e36a`, pushed) fires exactly once: fresh caller `0x3ded80`
      (#6, `sub_003DED50`), entry sp `0x1fffe80`, true frame
      `0x1fffe00`/`0x1fffe10`; other 4037 enters are scheduler-loop
      resumes (prologue skipped, bypass dispatch — probe blind by
      construction). ROOT CAUSE of the 3-brief saga: P13-3 hex slip
      (`0x1fffd80+0x80` written as `0x1ffe000`, true `0x1fffe00`) —
      "audited correct" twice. Ladder unchanged (16/1 park, 0
      missing, gs counts equal); tests 424/425 same failure. Verified:
      probe line verbatim, trace 4038, +37 one file, binary sha,
      fork pushed, lease clean (M8 untouched). Next: P1o. Lesson:
      machine-check all hand hex (added to runbook boilerplate).
      Ledger row added.
- [ ] **Hourly agent poll (09-19, user call):** cron `ssx3-hourly`
      (`17 * * * *`) checks P1n/G4/M8 states every hour — done →
      gate-read commits per repo convention; blocked → read dialog,
      report, do NOT answer it; working past box → flag overtime.
      No new-agent launches from the poll; report only. (A background
      `herdr agent wait` only signals completion and can't detect
      stuck — the hourly check is the stuck-agent cover.)
- [ ] **P1n + G4 + M8 launched (09-19):** P1n (driver-entry sp/ra
      probe, `Diag:` commit + rebuild + one boot — names the live
      caller) reuses P1m pane; G4 (profile + one fast path,
      identity-proven) reuses G3 pane; M8 (delta propagation: slot
      census + second-slot delta + projection reachability) reuses M7
      pane. Remaining queue: `sceGsSyncVCallback` test fix (fork,
      after P1n). Monitoring note: orchestrator does NOT watch
      between user check-ins — all three prior agents finished
      unnoticed; user check-in is the actual monitoring loop (waits
      only run inside active turns).
- [ ] **M7 read (09-19) — PASS, item 3 mostly done, one open
      question:** baseline reproduces M6; all three M6 gaps closed
      (det=0 matches suppressed shape except `pediff` 0/+2,
      replay_disabled continuation clean, mid-Trigger flip DIRECTLY
      observed: `trig_imx` 1/1, `dimx` once at replay 0, `dframe` +1
      ×200 — M6's elimination upgraded to observation); no-op parity
      holds with `trig_imx` 0/0 as the negative control; camera delta
      (+0.1 posmtx0 tx) applies 152×/replay yet 0/200 frames differ by
      any byte, no drift, guest/event state clean. OPEN: why zero
      pixel diff (slot unused? seam overwritten pre-use?) — agent
      quantified honestly but didn't pursue; that's M8. Verified:
      header sha, analyzer rows reproduced, xform_stats verbatim,
      6/6 hashes, flip counters, lease log. Ledger row added.
- [ ] **G3 read (09-19) — PASS, present pinned + both TODOs spiked:**
      4 new captures (102 total, 719 MB under the 800 cap) pin the
      `fbp==0` fallback (black→context[0], nonblack→0, multi→first
      nonblack, empty→0); `spike` fork backend (cpu/strict/upstream
      untouched) carries CLUT-cache + RMW-lookup spikes, both
      identity-exact on all 102; timing deltas recorded as observed
      (CLUT ~15–20% submit savings on paletted captures, RMW up to
      ~40% on fbmsk); CTest 11/11. Honest limits: CLUT memo assumes
      no mid-batch footprint writes; RMW CT32-only; strict+spike
      uncombined. Verified: md5s, factory reg, old-98 byte-identical
      (md5 lists differ ONLY by the 4 added lines), CTest 11/11
      re-run, pushed. Ledger row added.
- [ ] **P1m read (09-19) — PASS, miss mechanism found, Step 2
      skipped legitimately:** 17-path coverage audit proves driver
      `sw`/`sd` emit on fires-paths (P12 sd-theory excluded BY
      SOURCE); p1l-only 72.3M-line trace: driver entered 3940×/
      exited 3939× (~44/s, per-period), 0 stub hits explained
      (checkpointed depth-0 dispatch uncounted); 7 of 8 direct-jal
      candidates NEVER entered, 8th wrote elsewhere → frame-elsewhere
      mechanism; live caller unknown (depth-0, no guest parent);
      next receipt designed (driver-entry sp/ra probe, both dispatch
      paths). Verified: trace 72,315,942 lines, 3940/3939, candidate
      0/0/0/0/0/2/0/0, overlap line verbatim, driver :39/:78,
      138 FAST files, 11 refs, fork untouched, no p1m boot. Next:
      P1n implements the probe. Ledger row added.
- [ ] **P1m + G3 launched (09-19):** P1m (miss-mechanism diagnosis, no
      fix — watchpoint coverage audit + driver-entry census + frame
      table, one boot max) reuses the P1l pane (`wN:t1A` → P1m); G3
      (Present-heuristic tests + CLUT/RMW spikes, identity-proven)
      reuses the G2 pane (`wN:t17` → G3). All three lanes full (P1m
      fork, G3 ps2xGS, M7 ssx3); lease shared P1m↔M7. Remaining queue:
      `sceGsSyncVCallback` test fix (after P1m), G4 perf (after G3).
- [ ] **G2 read (09-19) — PASS, harness proven sensitive:** 20 new
      captures (98 total, +105 MB, 691 MB under the 700 cap), `strict`
      backend wrapping cpu and honoring all 7 G0-§9 fields; cross table
      14 flipped rows ALL field-mapped (incl. 2 old G0 captures) and 84
      exact; G0 `blend-colclamp` no-flip honestly explained (no
      overflow); census decodes everything new; CTest 9/9 incl. 3 new
      sensitivity gates. Caveat recorded: strict's honored semantics
      are plausible-but-unverified (aa1 halving, LOD=min, SCANMSK
      restore, post-blend dither — agent disclosed all) — a test
      instrument, not a hardware reference. Verified: files, factory
      reg, cpu/upstream untouched since G0, 98 captures, ssx3 copy
      identical, CTest 9/9 re-run, pushed (`origin/main` == HEAD).
      Ledger row added.
- [ ] **P1l read (09-19) — PASS, missing target gone, park holds:**
      4 splits (CSV 9270→9274, recompile 9092→9096, 0/0), boot shows 0
      missing-target lines; thread 1 still in driver/SYNCTASK
      (`0x3e5980` ×14 + `0x3e5440` ×3); outer-caller receipt missed
      AGAIN on both `sw` and `sd` addrs (addrs audited arithmetically
      correct — now a miss-*mechanism* question, 8 candidates stand);
      first `[gs:kick]` lines ever (66) correctly attributed to
      aggressive-logging visibility (old binary had it off), not guest
      change; ~4× wall-clock rate vs p1k open (no host-load record);
      tests 424/425 same pre-existing failure (re-proven without stash:
      no tracked source changed + runner symbols absent from test
      binary). Verified: log counts/census/callback/threads/csv/splits/
      ELF spot/regs/binary sha/fork untouched+up-to-date. Next: P1m.
      Ledger row added.
- [ ] **M7 launched (09-19, `local/muse/prompts/M7.md`):** milestone 2
      item 3 — pose interpolation + camera delta on the `g_transform`
      seam inside the M6 context. Step 1 closes M6's three unordered
      runs (det=0, replay_disabled, direct flip observation); steps 2–3
      no-op parity then camera delta vs the S2 honesty gate. Desktop,
      lease-shared with P1l. Agent in freed M6 pane (`wN:t16` → M7).
      Deferred queue behind live agents: `sceGsSyncVCallback` test fix
      (fork tree, after P1l), G3 (ps2xGS tree, after G2).
- [ ] **M6 read (09-19) — PASS, milestone 2 item 2 done:** scoped bus
      (`dafter_live` 0/0, `dpend` 0/0, queue never grows — in-stream
      flush points still drain); `dframe` frozen 0/0 with replay-local
      counter; M5's +1 driver NAMED (`ImmediateSwap` `Present.cpp:235`
      re-armed by the `VideoConfig` after-frame listener mid-Trigger —
      file:line + trigger + 11-listener elimination, honestly noted as
      code-path-plus-elimination, no direct flip observation); guard
      proven by negative control (`record_flag_set` pre-replay-0, 0
      rows, `done` stands, bus restored on break path); continuation
      hash identical ×5 (comparison skipped, seams differ). Verified:
      header shas, guard event verbatim, analyzer rows reproduced,
      5/5 hashes, lease log incl. battery hold obeyed. No push. Ledger
      row added.
- [ ] **G2 launched (09-19, `local/muse/prompts/G2.md`):** harness
      sensitivity — `strict` second backend honoring all G0-§9-ignored
      fields + mip-chain/TEX1/paired-isolation captures; sensitivity +
      specificity tables prove the diff table catches real differences
      on synthetics alone. No lease, no emulator. Agent in renamed P5
      pane (`wN:t17` → G2).
- [ ] **G-series reordered (09-19, user call — harness must not block
      on first frame):** G1 (game captures + pad scripts + real census)
      stays queued, gated on first presented frame. G2 (sensitivity,
      this row) runs now. Probable sequence after: G3 = Present
      `fbp==0` heuristic tests + CLUT-cache/RMW-lookup upstream TODO
      spikes (both validated by identity replay); G4 = CPU-backend perf
      profile + one fast-path spike (Unleashed-style batching
      candidate); then G1 the moment P-series delivers frames.
- [ ] **Resume recipe (09-19, learned from this restart):** track
      agents must start with `herdr agent start <name> --kind muse
      --pane <id> -- --yolo` — bare `muse` stops at approval dialogs
      (M6 proved it on an SSD touch). If a pane sits at `~`, cd it to
      ssx3 before starting (avoids the workspace-trust dialog).
      Effort (09-19, user call): append `--reasoning-effort max`
      (not xhigh) to all new agent starts; running agents stay as-is.
- [ ] **P1l launched (09-19, `local/muse/prompts/P1l.md`):** split
      `0x395cf0` + 3 unsplit siblings (`0x395c70` already split —
      verify only), regen + rebuild + `ps2xTest` (re-prove the 1
      pre-existing failure), one ≤90 s boot with `+w4 0x1ffe000`
      outer-caller receipt. Splits + ladder only; driver-flag writer,
      sema-26, and any park fix out of scope. Fresh agent in the
      freed P1k pane (`wN:p1A`).
- [ ] **RECOVERED 09-19 — `/Volumes/Extreme SSD` writable again
      after restart (write test passed). Herdr panes wiped by the
      restart: P5/P1j/P6/P1k agents gone but all four tracks already
      committed + gate-read — no resume needed. M6 released (MacBook
      on AC, 65% charging — battery-hold condition met). P1l briefs
      fresh agent in the freed P1k pane.
- [ ] **P1k read UPGRADED 09-19 — PASS, all deferred receipts
      verified post-recovery:** 33,038 lines / 3,052,064 B; thread-1
      census 15/1/1; threads 2/4/5 sema-parked 26/29/30
      (sched 0/~300/0); watch 32,077 lines, widths 32050/25/2;
      fills/del/sema lines verbatim; 15× w16 zeros, 0× `0x3dd214`;
      stub top-3 identical to p1j; `0x15` ×4 / `0x17` ×1; ELF 11/11
      + sha1 `77114dfd`; fork `8fad69e` + pre-existing M, no strays,
      lease absent. NUANCE: sibling `0x395c70` already HAS a split
      file + reg line (P1l splits only the other three + `0x395cf0`).
      Original 09-18 23:20 conditional read:** park = `SYNCTASK_run` queue drained by a driver flag
      (`*(entry+8)`, writer unknown); slots 0–1 fire ~600×/5 s
      (fills traced to `systemInit` + `sub_003E3020`, third filler
      del'd pre-fire); outer caller narrowed to 8 wrappers (one is
      P6 `ASYNCFILE_release`) — `sd`-path watch miss documented with
      next receipt (`w4 0x1ffe000`); `0x395cf0` = unsplit frameless
      leaf (split-class fix, 4 siblings); first CD callback signals
      sema 26 yet T2 never wakes (completion unobservable — no finish
      line exists); `0x15`/`0x17` = one-shot disables. Verified
      repo-locally: 14/14 P6 names verbatim + both absences. SSD
      counts/ELF/fork UNVERIFIED (volume failed mid-brief; agent
      marked NOT RE-CHECKED honestly). Nit: report says "23:05 UTC",
      means EDT. Recovery + re-verification done 09-19; P1l
      launched below. Ledger row updated (flag lifted).
- [ ] **P6 read (09-18 23:00) — PASS, thin but honest:** 801-row
      addr→name CSV (names only, longest line 86 chars — license rule
      held); only 6.67% sweep coverage and ALL 11 ladder addrs UNNAMED
      (decomp is early: 6 split files, 390 stubs). Real wins anyway:
      `main` at `0x31af80`, GS-wait caller reached from the
      `cSSXApp` constructor row (verified `jal`), sweep vindicated
      (100% JAL recall, 0 splits in 106 tight pairs — merges only),
      sweep dup found (`0x42c1f0` lines 9229–9230 — KNOWN ISSUE, do
      not touch mid-ladder; dedup at next CSV regen), tooling theft
      table. Verified: rev, license absence, sha1, 749 symbols, CSV
      rows, dup lines, caller JAL. P1k already instructed to use the
      CSV if present. Ledger row added.
- [ ] **P1k launched (09-18 22:45, `local/muse/prompts/P1k.md`):**
      diagnose the `0x3e5980` 16-slot dispatch-loop park (slot
      contents, filler, exit condition) + name the outer caller of
      `sub_003DD1D8` + analyze missing target `0x395cf0` + first CD
      callback + syscalls `0x15`/`0x17`; uses P6 names if landed. No
      fix. Lease free.
- [ ] **P1j read (09-18 22:45) — PASS, CSR park cleared, ladder
      jumps:** bits 15:14 identified as FIFO (DobieStation + PCSX2 +
      gsKit + Play!, all cited); fix `8fad69e` (init EMPTY + force
      read-only on guest writes, +43/-7, cheat row documented)
      pushed to fork `ssx3`; boot 1 runs thread 1 to `0x3e5980` with
      FIRST `[cd:callback]` fire, thread 5, syscalls `0x15`/`0x17`,
      1 new missing target (JALR `0x3760d0→0x395cf0`). Tests 424/425
      with the 1 failure proven pre-existing (stash A/B). Verified:
      fork push, hunks, both FIFO cites verbatim, boot pcs/counts.
      Queued (not launched): `sceGsSyncVCallback` stack-pool test
      fix. Next: P1k. Ledger row added.
- [ ] **P6 launched (09-18 22:35, `local/muse/prompts/P6.md`):** mine
      ssxdecomp/ssx3 (PS2 SLUS_207.72 matching decomp, SAME sha1 as
      our ELF, 433 src files, NO license → names/addresses/facts
      only, never bodies): addr→name CSV joined against our 9,270-row
      sweep, ladder-function naming, boot/park structure, boundary
      truth sample, tooling theft. Read-only.
- [ ] **Monitoring switched to event waits (09-18 22:30, user
      call):** `herdr agent wait --until done,blocked --timeout
      <box>` replaces sleep-polls — done → check `[ID]` commit →
      gate read; blocked → read dialog; timeout → stuck/overtime →
      read + redirect. No agent cooperation needed (no
      agent→orchestrator message primitive exists; waits observe
      lifecycle server-side). Artifact proof unchanged: the commit,
      never the status label.
- [ ] **P5 read (09-18 22:30) — PASS, 32 borrowable rows:** Xenon
      ordinal-HLE (weak-link override, addr→name map, BL-sweep,
      gap-fill Analyse, offline switch TOML); psprecomp HLE work-list
      census + miss-log + zero-ring + entry trace + self-test;
      N64 CreateStatic + jump-table discovery + patch/hook system;
      UnleashedRecomp API-level GPU HLE (no capture stream) +
      render-thread split + shader-hash tables; xboxrecomp MIT,
      ordinal-switch HLE + coverage audit + NV2A census/executor —
      but NO SSX3-Xbox specifics (titles are Burnout 3/Halo).
      Verified: xbox MIT, psprecomp + N64 quotes verbatim, P5's
      "zero SSX matches" is substance-true (one English-word
      "tricky" false positive it should have named — nit).
      No push. Ledger row added.
- [ ] **P1j launched (09-18 22:05, `local/muse/prompts/P1j.md`):**
      identify GS CSR bits 15:14 from public sources (DobieStation /
      PCSX2 GS / PS2 docs, all cited), implement the minimal producer
      for the `0x4000` exit state, rebuild, one boot for the ladder.
- [ ] **P1i read (09-18 22:00) — PASS, strong partial-negative:** no
      producer for CSR bits 15:14 exists anywhere (exhaustive `csr`
      grep: writers touch {0,1,13} + init-0 + guest merge only);
      consumer is dynamic `READ64` (not TOML); vsync/present/timer
      paths all CSR-free for these bits. Bits honestly recorded as
      unidentified-from-tree (no-guess rule held). 10 min, no boot,
      push rule obeyed. Verified: TOML absence, generated line,
      `0xC000` absence, ELF words (in report). Next: P1j. Ledger row
      added.
- [ ] **P5 redirect (09-18 22:05):** +Q6 sp00nznet/xboxrecomp (OG
      Xbox, SSX 3 runs on it): license read first (author's reo was
      unlicensed — idea-level only if so), Xbox kernel-HLE approach,
      any SSX3-Xbox-specific workarounds, NV2A GPU approach vs
      ps2xGS. Quota note: user nearly out of muse free credits —
      no new launches after P1j until confirmed; P5 running lean
      solo, M6 runs held (battery).
- [ ] **P5 launched (09-18 22:00, `local/muse/prompts/P5.md`):** mine
      360/N64/PSP recomp tooling — XenonRecomp ordinal-HLE stub
      generation/tracing, N64+Xenon indirect-branch/function tooling,
      UnleashedRecomp GPU capture/replay vs the ps2xGS plan, patch
      systems vs our TOML stubs, recompiler testing patterns (which
      test catches the next LUI+ORI fold?). Read-only, battery-light.
- [ ] **M6 launched (09-18 21:50, `local/muse/prompts/M6.md`):**
      host-replay milestone 2 item 2 (S2 Part 4 items 2–4): scoped
      `after_frame_event` suppression + `FrameCount`/frame-aging
      semantics + the `dframe` +1 driver chase + fail-closed
      `g_record_fifo_data` guard, on M5's header, desktop only.
      HOLD 21:55: MacBook untethered (battery 80%) — M6 finishes Step 1,
      then holds all runs until back on power (battery + thermal-noise
      protection); prep work continues. P1i unaffected. Odin unplugged:
      no track needs the device, no blockers. PARKED 23:05: M6 finished
      all run-free prep (Step 1 receipts verified, analyzer tested vs
      synthetic guard-stop, negctrl table scaffolded in REPORT) — only
      the m6-negctrl run + table fill + commit remain. Event wait
      terminated as pointless while parked; re-arm on release.
- [ ] **P1i launched (09-18 21:50, `local/muse/prompts/P1i.md`):**
      diagnose the GS CSR park at `0x375d10`
      (`(CSR&0xC000)!=0x4000` spin) from the closed boot-p1h-1 log +
      ELF + sources; no fix. One ≤90 s boot only if the log cannot
      name the missing producer. Lease is free.
- [ ] **M5 read (09-18 21:45) — PASS, milestone 2 item 1 done:**
      200/200 + `done` on all runs; `xfb_equal=200/200` (range
      `0x004dc660`, 573440 B); counters fail-closed (`dpend` 0/0,
      `pediff`/`vidiff` 0/0 det=1, no `record_flag_set`);
      `xfb_equal_scratch=200/200` + `live_xfb_untouched=1`;
      continuation skipped per brief (seam fc 8121 vs 8142). Verified:
      probe row counts + receipts by independent parse, S2-sha
      handling, vendor untouched (pre-existing Sep 10–17 uncommitted
      hunks are not M5's), lease discipline. Notes: brief's pinned S2
      sha was stale (M5 recorded both, used on-disk); `#define
      private` promotion is header-local and layout-safe; one "Sync
      snaps" failure in scrollback never surfaced in the report
      (receipts all landed — watch item). Next: M6. Ledger row added.
- [ ] **P1h read (09-18 21:45) — PASS, ladder advances past the MMIO
      park:** analyzer fix `f2149e7` (ORI/ADDIU low-half fold, 1 file
      +28) pushed to fork `ssx3`; 245/273 `[mmio]` entries corrected
      (4 remaining folds proven genuine); regen recompiled clean;
      boot 1 runs thread 1 to `0x375d10` (all 35 blocks, frame popped,
      via `0x375a94`). New park recorded: GS CSR spin at `0x375d10`.
      P1h obeyed the hardened push rule (ssx3 commit local-only).
      Verified: fork push, TOML, recomp lines, boot log, park ELF
      words + branch arithmetic. Next: P1i. Ledger row added.
- [ ] **P4 read (09-18 21:45) — PASS, fork diffs mined with bodies:**
      M1/M2/M7/M10/M12 full diffs; bt3's dynamic MMIO dispatch
      (immunity-by-construction alternative to P1h), sync-CD + tick
      pump, GPU/async-kick architecture; sm2/halogen/drakengard/reo
      boot learnings; Q4 EeScheduler delivery point for
      message-not-nesting; 20-row borrowable table (S1–S20) with
      license re-cites. Gaps honest (depth-1 clones hide 7 revs).
      Verified: bt3 MMIO + sync-CD bodies, M1 dispatch + STR bodies.
      Findings feed P1i/P1j scoping. Ledger row added.
- [ ] **P4 launched (09-18 21:25, `local/muse/prompts/P4.md`):** closes
      P3's admitted gap (per-fork diff bodies): reads the M1–M14 diffs
      from the existing `fork-survey/` clones, diffs working
      bt3-recomp against our fork (boot/MMIO/GPU/CD), boot learnings
      from sm2/halogen/drakengard/reo, and the EeScheduler delivery
      point for message-not-nesting. Read-only, fully parallel to
      M5/P1h. README gained a "Legal notes for contributors" section.
- [ ] **P1h launched (09-18 21:15, `local/muse/prompts/P1h.md`):**
      fix the analyzer's LUI-only MMIO detector (read the ORI/ADDIU
      low half), regenerate + audit all 273 `[mmio]` entries, rebuild,
      one boot for the ladder. Builds any time, boots yield the lease
      to M5. Push rule hardened again: `git push` only inside the fork
      clone, never in ssx3 (P1g pushed origin despite the fork-only
      rule, rationalized in P8-0 — content benign).
- [ ] **P1g read (09-18 21:10) — PASS, park fully diagnosed:** the
      `0x391330` spin is a recompiler bug, not game logic: the MMIO
      detector folds LUI+ORI accesses to the page base, so the VIF0
      DMA kick + STR poll both hit `m_ioRegisters[0x10000000]` (stuck
      `0x104`). Verified: ELF words, TOML folds, recomp `:164`,
      detector source, both memory-path gates, branch arithmetic.
      249/273 `[mmio]` entries fold the same way (7 proven). No boot
      needed. Next: P1h. Ledger row added.
- [ ] **P2 read (09-18 21:10) — PASS, strong negative result:** PCSX2
      (`1275b25a`) runs the real BIOS and HLEs almost nothing on the
      EE, so it contains no handler/alarm/CD/RPC stack behavior to
      borrow — P1f's direction stands uncontradicted. One real
      tension: `EENULL`/`EELOAD` live inside P1f's borrowed
      `[0x80000,0x100000)` on real hardware (no BIOS here, and the
      SSX3 ELF doesn't touch the range, so no action). Verified: rev,
      enum, EELOAD lines. Ledger row added.
- [ ] **P3 read (09-18 21:10) — PASS with follow-up queued:** 133
      forks / 50 PRs enumerated; bt3-recomp (GPL-3, playable, GPU
      path) is the most relevant downstream; N64ModernRuntime's
      message-not-nesting is the architectural alternative; fork
      LICENSE files are near-uniformly GPL-3 (M1–M14 snippets
      borrowable); PSXRecomp is PolyForm Noncommercial (unusable).
      Gap: per-fork diff bodies didn't survive (clones persist under
      `fork-survey/` for a P4 follow-up if needed — not launched;
      MMIO fix is the priority). Verified: bt3, N64MR, 2 licenses.
      Ledger row added.
- [ ] **P1g launched (09-18 20:45, `local/muse/prompts/P1g.md`):**
      diagnose the post-fix park at `0x391330` (`sub_003912A8`, pc
      stable but `scheduled` advancing) from the closed boot-2 log +
      ELF disasm; no fix. One ≤90 s boot only if the log cannot name
      the wait object, yielding the host lease to M5. Ledger row added.
- [ ] **P1f read (09-18 20:40) — ra-slot writer caught, fix VERIFIED:**
      boot 1b watch on `0x1ffff00` caught 32,682 writes, all but 153
      from the INTC handler prologue zeroing thread 1's frame; fix
      `6046260` (sp=0 + reserved stacks in `[0x80000,0x100000)`)
      pushed to fork `ssx3`; boot 2 shows 165/0 handler writes and
      thread 1 `Running` at `0x391330` with threads 3+4 new. Part 7
      appended, `[P1f]` 6e90355. Process note: P1f pushed ssx3
      `origin/main` too though the brief said fork only — content was
      benign (briefs, todo, report) but future briefs now say
      fork-remote-only. Next: P1g.
- [ ] **P2 + P3 launched (09-18 20:30, `local/muse/prompts/P2.md`,
      P3.md):** two read-only P-branch research angles alongside P1f's
      fix — P2 reads PCSX2 source (EE INTC/alarm/CD/async stacks) for
      a reference comparison + patch sketch, P3 surveys PS2Recomp
      forks, independent PS2 static recomps, sibling recomps and
      readable dynamic emus for borrowable prior art + license
      verdicts. Neither builds, boots, edits the fork, or takes a
      lease, so both run fully parallel to P1f and M5.
- [ ] **Plan of record for 120 fps (September 17 evening):**
      [docs/plan-120fps-2026-09-17.md](plan-120fps-2026-09-17.md) — owner-held
      gates, muse briefs D1/M1 launched, M2/M3/M4/D2/D3/D4 queued, S1/S2 gated.
      Briefs never edit this file or the ledger; the owner does after each
      gate read.
- [ ] Codegen prune follow-up: capped CPU-gated A/B (September 17,
      HIGH): the one-chunk spike (802197A0) was INCONCLUSIVE — desktop
      uncapped can't resolve the ~2% expectation (fanless-Air thermal
      lottery ±10–85%, fingerprint divergence, B-C-C-B ordering), NOT
      a kill (signs disagree across cycles; nothing flat-or-negative
      on the merits). Correctness proven (1617/4096 pruned set covers
      all 149 census entries, full movie, no trap). Staged patch
      (DolRecomp-only, env-gated, default byte-identical) + record
      test on SSD codegen/ — land as-is IF a capped-1x CPU-ms/frame
      A/B (thermally cool + deterministic) or an Odin run confirms a
      win. CORRECTION to the review formula: leaders ∪ return_targets
      is INSUFFICIENT — FP-unavailable faults rfi-resume mid-block,
      entry sets must include FP-sites (candidate 1 trapped at boot
      without them); full enumeration in the spike report.
- [ ] FP-unavailable fault storm (September 17, NEW lead): 41,022
      FP faults in 25 s module-wide on desktop, two ops faulting
      ~600×/s each. If that rate holds on Odin, silencing the storm
      (MSR_FP handling? fast path?) is a direct win independent of
      §2. Needs Odin confirmation + per-op attribution first.
      **M2 read (09-17 21:30):** the `0x800` body is NOT a stub like
      the syscall vector — it is the SDK generic exception entry
      (full context save + handler-table branch), so vector HLE is
      off the table. The lead now is cost per fault (M2b instruments
      raise→rfi host ns) and, if the cost is real, an eager-FP
      context switch (keep MSR.FP set, save/restore FPRs in
      OSLoadContext) instead of the SDK's lazy trap; that needs the
      native-ABI FPR location, so it waits for the M1/S1 decision.
      **D5 (09-18):** attributed — see the D5 gate read above; S3 owns
      the fix.
      **D1b (09-17):** Odin in-race native_exc is 35,646/s (menus
      ≈1.5k/s), 20× the desktop rate — if these are FP-unavailable
      faults this is the single largest emu-thread lever measured so
      far; D5 attributes them by vector and times raise→rfi on the
      device before anything is built on the assumption.
- [ ] **G0 read (09-18 15:40) — harness + census DONE, pushed:** 78
      synthetic captures, identity replay byte-exact on all, census
      renders every feature, CTest 6/6; `ps2xGS` public under GPL-3 with
      G0's commits. Finding that changes the loop's acceptance: the CPU
      backend ignores TEX1, DIMX/DTHE, COLCLAMP, SCANMSK, aa1, fix and
      ZTE — plan §5a now routes those features to a second oracle instead
      of byte-exact-vs-CPU. Next: G1 (game captures) waits on P1b
      rendering; G2 (loop brief) after G1. Ledger row added.
- [ ] **Audit review + C1 cleanup launched (09-18 16:35):** A1 found no
      game bytes, images, big blobs or deleted files in tree or history;
      third-party trees are untracked with licenses recorded; the one
      "generated code" flag (`tests/float-conversion-original-generated.h`)
      is DolRecomp's template output (helpers + address-keyed prototypes),
      kept with a provenance comment. Short game-text quotes trimmed. A2
      found no secrets and no personal data beyond the GitHub handle; the
      real exposure is author-machine detail (share paths as tool defaults,
      LAN IP, Odin serial, home-server names, home paths) — C1 scrubs
      tracked files to placeholders and moves tool defaults to
      `SSX3_WORKBENCH` / `SSX3_GAMES`; no history rewrite (the values are
      a private LAN address, a handheld's USB serial and mount paths).
      A3: two docs archived, docs index adopted, README rewritten from its
      draft with my status text, MIT LICENSE + licensing section (vendored
      GPL-3 trees, GPL-3 patches, GPL-3 combined builds). DONE 16:30: C1 verified (746 tests pass, scrub grep
      empty), pushed, repository PUBLIC at github.com/brad-richardson/ssx3.
- [ ] **ssx3 publication audit LAUNCHED (09-18 16:00), user decision:**
      go public with MIT for the project's own code (vendored trees keep
      GPL-3; patches to them and combined builds are GPL-3), so the
      upstream maintainers can see what we care about and why patches
      exist. Three read-only muse audits: A1 game-derived and third-party
      content (tree + history), A2 secrets / personal data / private
      infrastructure (tree + history), A3 docs structure + README drafts.
      Then the orchestrator reviews the findings, decides redactions,
      deletions or history rewrites, adds LICENSE + READMEs, and only
      then the visibility change.
- [ ] **Repos and licenses (09-18 15:35):** `ps2xGS` is public at
      github.com/brad-richardson/ps2xGS under GPL-3.0 (switched from MIT
      to match PS2Recomp and avoid the combined-work question); push
      after each G-brief lands. `ssx3` STAYS PRIVATE: before any
      visibility change it needs a full pass for sensitive or
      copyrighted material (the quick audit found no binaries, images,
      generated guest code, big blobs or secrets, but the docs carry
      reverse-engineering detail) and a top-level LICENSE (GPL-3 for
      `native/`, patches and vendored trees; tools/docs could be split).
      PS2Recomp fork created at github.com/brad-richardson/PS2Recomp
      (15:50): branch `ssx3` on top of upstream `14b1e5cb`, plain commits
      per fix for speed (user's choice), cleaned into upstream PRs later;
      the working clone on the SSD has remote `fork`. Generated runner
      sources (guest code) are gitignored there and must never be pushed.
      ps2xGS's submodule moves to the fork branch once fixes land (G1).
- [ ] **GPU GS backend plan written (09-18 14:50):**
      `docs/plan-gs-gpu-backend-2026-09-18.md` — gates for the autonomous
      loop on the new Mac mini (harness: recording backend + replay/diff +
      synthetic streams + identity test; census; game rendering through
      the CPU backend), the decisions made up front (exact compute
      rasterizer over a VRAM storage buffer, Vulkan + MoltenVK, byte-exact
      acceptance, scope containment, MIT), the S0–S8 staged loop, repo
      `ps2xGS` with upstream as a pinned submodule. Prep briefs: G0
      (harness + census on synthetic streams, runnable now), G1
      (reference captures, after P1b/P2 render), G2 (the loop brief).
- [ ] **Laptop disk evacuation (09-18 14:25):** the data volume hit 100%
      mid-run (herdr logging degraded); now 34 GB free. Moved to the SSD:
      old `/tmp` link dirs (`tmp-evacuated-0918/`), `local/builds`
      (symlink left), and as tar archives under `laptop-evacuated-0918/`
      with verified entry counts: `local/research/{120hz,startgate,
      remaster,float-opt-psq}`, `local/reports`, `local/fast-game`,
      `local/native/{profiles,profiles-f120,ios-device,ios-simulator}`
      (sources removed; empty `local/reports` and `local/native/profiles`
      recreated for tools that write there). Kept: `local/game`,
      `local/native/{ssx3-module,runtime-build}`. Lessons: the SSD is
      ExFAT with 1 MiB clusters and no symlinks — tar small-file trees,
      never `mv` them; this Mac's `find` is bfs, which rejects
      `-newermt "-3 hours"` (use an ISO timestamp). Briefs now write
      receipts and binaries to the SSD and use `/tmp` only for the link.
- [ ] **P1 read (09-18 14:10) — PS2Recomp boots to the kernel-patch
      scanner; P1b launched:** census and recompile reproduced exactly on
      the Mac (arm64); runtime + 425/425 tests + port runner all build;
      the game loads, starts, sets up its heap, then spins in the SDK's
      kernel-patch scanner (`sub_0042C1F0`) polling syscall 0x83
      `FindAddress`, which can never match without a kernel image. The
      scan result (0x455230) only feeds a patch applier that is a no-op
      at 0, so P1b stubs the scanner via the TOML (`ret0@0x0042c1f0`),
      stages the disc tree (runner maps `cdrom0:` to the ELF directory),
      and climbs the ladder with two allowed follow-ups (stub the
      applier entry if dispatch fails; inventory IOP module requests).
      GS renderer read (mine, later): 4 files, ~146 KB, CPU rasterizer
      only, 2 TODOs. Ledger row added.
      P1b progress (15:05): with the scanner stubbed the boot climbs to
      SifInitRpc and loads six IOP modules through the HLE (SIO2MAN,
      PADMAN, LIBSD, SNDDRV, MCMAN, MCSERV), then dies on `sceCdRead` of
      LBN 0x10 (the ISO9660 volume descriptor): the runtime can serve raw
      sectors from `IoPaths.cdImage` but nothing in the runner sets it —
      P1b applies a one-hunk `PS2X_CD_IMAGE` env hook (upstream PR
      candidate). Second class of stall: missing indirect-call targets
      that are real prologues the analyzer merged into neighbours
      (0x3b07b8 inside sub_003B0770, reached from a function-pointer
      table walk) — fixed by feeding the recompiler a function-map CSV
      (`general.ghidra_output`, rows name,start,end,size) built from the
      generated sources with splits at each reported prologue, iterated.
      Third stall (15:20, with the CD image readable): every guest thread
      parks in the scheduler (99% in its idle wait). Cause: the game uses
      the SDK's asynchronous CD callback (binds `sceCdCallback` and
      `sceCdInitEeCB`), and the runtime implements both as no-ops, so the
      callback that signals the game's semaphore never fires. P1b adds an
      idle-thread snapshot dump (diagnostic) and an HLE CD callback path
      that queues a guest invocation after each read completes, the way
      `EeScheduler::dispatchIrq` runs interrupt handlers; both as patch
      files (upstream PR candidates).
      P1b read (09-18 17:10): Part 3 delivered. The constructor table at
      0x43ce38 (39 entries, all prologues) was split in one pass; boot 8
      with all four fixes has zero missing targets and no CD error, then
      goes silent: no syscall, VIF, GIF or frame for 10 minutes, no idle
      dump (so some thread stays runnable), runner at ~10% CPU. Fix D
      (CD callback HLE) has no receipt that it ran. Four commits pushed
      on the fork branch `ssx3`. P1c launched (`local/muse/prompts/P1c.md`):
      env-gated diagnostics (periodic thread dump, syscall and HLE-stub
      histograms, CD-callback receipt), name the loop from the generated
      source, at most three completion fixes with one boot each, Part 4.
      G1 brief drafted (`local/muse/prompts/G1.md`), launches when a
      frame presents. Ledger row added.
      P1c read (09-18 18:20): Part 4 delivered in 1 h 10 min. The
      silence was one thread in WaitSema on a semaphore that only the
      game's alarm callback signals, and SetAlarm had refused that
      callback because its address had no function-table slot: the
      same unsplit-prologue class as the constructors. Two splits later
      (alarm callback, a frameless comparator) the boot creates the CD
      thread, inits the CD callback, reads the PVD and directory
      sectors, then both threads go Dormant with pc 0 and no exit
      syscall; the CD thread never ran (its entry is also mid-function
      in the map; Thread.cpp:269 refuses unknown entries). Lesson: every
      function reachable only through a data pointer (constructor
      tables, alarm/thread/RPC handlers, comparators) is invisible to
      the analyzer. P1d launched (`local/muse/prompts/P1d.md`): a
      one-pass code-pointer sweep over the ELF (data words + lui/addiu
      pairs, split only on prologue or after a `jr $ra`), a strict-return
      build to catch the return to 0, and a CD payload check. Ledger
      row added.
      P1d read (09-18 19:10): sweep delivered in 50 min: 1,024 new
      functions found only through data pointers, zero recompile
      failures; the CD thread now runs and waits on semaphore 26. The
      main thread still returns to pc 0 after 22 schedulings; the strict
      build only reported a benign startup return in the bss-clear loop
      (ra 0 from crt0) and the report path likely de-duplicates per
      target, so the real return was silent. CD raw reads verified byte
      correct. P1e launched (`local/muse/prompts/P1e.md`): receipt at
      both makeDormant sites with the dispatch history, un-deduplicated
      Return reports, name the returner and the exit condition, map
      semaphore 26's owner, one fix if the runtime owns the tested value.
      Ledger row added.
      P1e read (09-18 19:55): the main thread dies in the epilogue of
      `sub_003DCBD8` reading a zero return address from its stack slot
      at 0x1ffff60; the function had been re-entered mid-body through
      the dispatcher after the StartThread thread switch (the runtime
      unwinds C frames on a switch), so guest memory is the only carrier
      of ra. I checked the generated prologue: the delay-slot `sd $ra`
      is emitted correctly, so something else zeroes the slot (thread
      2's stack placement, an invocation stack reserved inside the main
      stack, or a stored handler sp) or ra was 0 on entry. P1f launched
      (`local/muse/prompts/P1f.md`): watchpoint on the slot, stack map
      per dump, StartThread parameter dump, then the fix in the runtime
      if it owns the writer. Ledger row added.
- [ ] **S2b read (09-18 13:50) — EGL capacity confirmed ×3, Vulkan
      parked:** third EGL arm 0.81 ms median, 200/200 with `done`; the
      three EGL arms sit at 0.67–0.87 ms per replayed frame, ~7–9× under
      the 6 ms gate, all captured at +100 s wall with the emu thread
      ≥0.93 busy (race, not menu). Vulkan cannot be measured until
      `core-vk-build` is rebuilt from the current vendor tree (the
      09-17 libs predate the S3 HLE symbol; the m4-src TU that links
      crashes at boot). Queue a muse build brief for it only when a
      Vulkan production path is on the table; the route decision does
      not wait on it. Next on the 120 route: milestone 2 as muse briefs
      — ReplayContext ownership items from S2's Part 4 inventory, each
      with the desktop determinism gate, then pose interpolation on the
      `XFReplay::g_transform` seam. Ledger row added.
- [ ] **D8 gate read (09-18 13:30) — clock-floor levers DEAD, floor
      smaller than feared:** capped 1.0 on Crow's Nest the control opens
      at ~0.90× for the first 50 s and runs at pace after; the spin pacer
      and the ADPF hint (session creation proven) change nothing (0.895 /
      0.895 / 0.911 opening, 0.978 / 0.978 / 0.989 full) and spin costs
      +10 °C. cpu7 parks at the 3.28 GHz policy minimum in every arm
      regardless. M3b's 0.84× opening did not reproduce today (0.90×);
      treat the capped opening dip as ≤10% and condition-dependent, not
      as a DVFS bug to fix. High-performance arm skipped; not worth the
      user's hand now that the two software levers are null. Ledger row
      added. Side finding: `dumpsys battery` status 3 while charge-limited
      (`battery_charging_enforce_level=90`) — the "status 2/5" gate in
      agent briefs is unreliable above ~90%; use level ≥ 20 plus a cable
      (S2b told to accept status 3 at level ≥ 80).
- [ ] **PS2Recomp track OPENED (09-18 12:45), all muse:** the user
      approved the evaluation track; the 09-12 spike's tree on the media server
      was lost to a reboot, so its transcript was recovered into
      `docs/research/ps2recomp-spike-2026-09-12/` (README = the spike's
      three verdict messages; commands-and-outputs; four decoder scripts).
      P1 (pane wN:pF) re-spikes on the Mac: build ran-j/PS2Recomp
      `14b1e5cb` for arm64, reproduce the VU1 census (7,305 instr / 85 ops
      / 0 unimplemented) and the EE recompile (8143 / 8017 / 126 stubs),
      then build the runtime and attempt a boot; GS inventory for my read.
      S2b (pane wN:pG) finishes the replay arms (egl-c, Vulkan relink +
      arms) behind D8 and the user's `USER-*` lease. Next after P1:
      P2 = EE/VU/GS split measurement on the Mac + GS renderer gap read
      (mine), P3 = Odin port.
- [ ] **S2 gate read (09-18 12:15) — host replay capacity PASSED:**
      with the paired preprocess pass, aux-buffer rewind, PE-token
      masking and per-replay memory/CP/XF restore, the Odin replays a
      Snow Jam frame in 0.67–0.87 ms median on the video thread,
      200/200 with `done`, no tombstone (gate was ≤6 ms). The D2b death
      was the deterministic dual-core FIFO aux buffer, not state drift,
      so the fix is small and lives in the research header. Not done:
      Vulkan (EGL trial has no Vulkan backend; relink against
      `core-vk-build`), HUD verification of the arms (m4-src trial
      records no screenshots), milestone 2 (`ReplayContext`; Part 4 of
      the report is the verified side-effect inventory). Continuations
      are muse from here: S2b = s2-egl-c with a screenshot-capable
      trial for HUD proof + s2-vk-a relinked (report has the exact
      commands); milestone 2 splits into ReplayContext ownership items
      (EFB/XFB + texture-cache resources, event suppression, frame
      counter) each as a brief with the desktop determinism gate, then
      pose interpolation on the `XFReplay::g_transform` seam. Ledger
      row added; the D2b row is superseded.
- [ ] **S1c gate read (09-18 11:50) — repin PARKED:** upstream's C
      backend on the repinned Android stack is not faster on the Odin.
      Repinned emu ms/frame ≥ pinned on every pair: uncapped +10–20%
      (under a battery-collapsed 1.02 GHz regime, relative only), the one
      clean boosted capped pair a wash within ±5%, Crow's Nest +3–7% but
      confounded by divergent race states. Pinned runs MORE native
      instructions with 6× more hook fallbacks and is still faster, so
      upstream's region-leader entry switches and proven-pointer memory
      bring nothing on this target. Keep the pin; the rebased platform
      patches (desktop +254/−19, Android port on the SSD) stay as the
      mechanical path if a later upstream feature needs them. Optional
      follow-up: a strict dispatch/movie-validity compare between the
      two stacks (the cn pair diverged, so one stack is not bit-faithful
      to the other's movie). Ledger row added.
- [ ] **No Opus from here (user, 09-18 11:45):** quota. S2 told to stop
      after its running arm and hand back its table; the remaining
      replay arms (Vulkan) and any milestone-2 work become muse briefs
      (S2b). Every implementation step is a muse brief; judgment stays
      in this session between briefs.
- [ ] **PS2 throughput gate READ (09-18 12:10) — the PS2 avenue is
      alive:** stock SSX 3 runs at 4.2–4.4× real time in the Snow Jam
      race under NetherSX2 on the Odin (Vulkan 1×, MTVU, limiter off, on
      battery; a 2.5× capped rerun holds 250% in open riding at a
      3.28 GHz prime clock and dips to ~2.0× at the six-rider start
      gate, 1.58× uncapped there). EE 2.5–2.9 ms per frame on its own thread, GS 1.5–2.4,
      VU 1.6–2.4, GPU 0.7–1.1: full-sim 120 Hz (the F route) has ~3×
      headroom on the PS2 side even under a JIT, where the GameCube
      route was 1.05–1.2× short. Ledger row + OSD frames under
      `local/research/ps2-gate/`. What it does NOT show: a static
      recomp's cost (EE/VU normally faster than the JIT; PS2Recomp's GS
      is a CPU software backend, so a GPU GS renderer is the whole
      gate), VU microcode coverage for this game, audio/timing under
      the recomp, and the game-side 120 Hz timestep patch (PS2 has the
      published scheduling patch sites). USER DECISION: open a PS2Recomp
      evaluation track (muse: build for arm64, boot stock SSX 3, measure
      EE/VU/GS split with the software GS, inventory the GS renderer
      gap) alongside host replay, or keep it parked.
      Housekeeping done 12:55: the user's original NetherSX2 per-game ini
      is restored (the 2.5×/OSD variants stay under `local/research/ps2-gate/`).
- [ ] **PS2 throughput gate (queued 09-18 11:50):** the cheap answer to
      "could a PS2 static recomp reach full-sim 120": run the PS2 game
      uncapped in NetherSX2 on the Odin in the Snow Jam race window and
      read speed % plus EE/GS/VU thread busy from the OSD. Needs the
      user's hands for the in-app setup; the stock ISO is already
      configured in NetherSX2 under `/sdcard/Documents/Ps2` (no push);
      device lease `USER-nethersx2` while it runs; sequence: after S2
      releases, before D8 and S2b. ≥2× with GS unsaturated = the recomp
      has headroom and the GS renderer is the only gate; <2× = the PS2
      avenue is dead for the same reason F is.
- [ ] **Device link (09-18 12:10):** the Odin drained to 2% under
      back-to-back runs (a dongle charged slower than the runs drew; the
      Mac port did not charge it at all). Now on a wall charger and driven
      over adb-TCP (`tools/odin_wireless.sh`, serial in `local/odin-serial`);
      the harness refuses to launch below 10% (`--min-battery`) and
      records battery state; briefs wait for ≥ 20% and charging. TCP mode
      resets on reboot (redo `enable` on USB after D4's reboot).
- [ ] **D2b read (09-18 10:15) → S2 launched:** Odin EGL replay costs
      2.0 ms wall / 2.0 ms CPU per frame for 26 replays, then dies in
      `LoadIndexedXF` because indexed-array (CP/XF) state drifts across
      re-executions; the named fix is restore-before-each-replay, which
      is the first item of S2's ReplayContext spec. S2 (Opus, the only
      Opus spike running): milestone 1 = per-replay restore in the D2
      research header until `done` verifies on EGL and Vulkan (the
      capacity gate); milestone 2 = the ReplayContext boundary from
      `docs/research/120hz-host-replay.md` only if capacity ≤ 6 ms holds.
- [ ] **D4 blocked (09-18 09:50):** since the Odin's USB drop the
      device refuses every APK launch from adb shell (`am start` error
      type 3 / result -92, resolve-activity finds nothing) for both the
      new trial-d4 APK and the previously proven ot3 APK, while dumpsys
      shows the launcher entry. D4 asked for a device reboot; the user
      was pinged for authorization. Headless briefs (D2b, S1c, D8) are
      unaffected and run first.
      Root cause (09-18 17:30, orchestrator): the 08:55 "USB drop" was a
      device reboot (uptime 8 h 32 min at 17:27), and nobody entered the
      PIN afterwards, so user 0 stayed in `RUNNING_LOCKED` (direct-boot,
      keyguard up, `strongAuthRequired`). Activities that are not
      direct-boot aware do not resolve in that state, which is the
      "Error type 3 / No activity found" D4 saw; adb-shell binaries do
      not care, so every headless brief kept working. The authorized
      reboot (17:27, 26 s to boot) reproduced the same locked state; the
      fix is one PIN entry on the panel, then D4 relaunches. Wireless adb
      re-enabled after the reboot (`local/odin-usb-serial` written so
      `tools/odin_wireless.sh enable` works again).
      D4 Part 2 read (09-18 19:40): delivered in 1 h 35 min, nine of
      them bootstrap attempts (thread names with spaces, pinning must
      go through run-as). Parity onscreen vs headless recorded (1.134×
      vs 1.273× race pace, HWC overlay, 120 Hz panel). Display proof
      failed on method, not on the game: EGL frame timestamps return
      nothing on Adreno, so presents could not be counted; the 120 Hz
      request itself lands in SurfaceFlinger. D4c launched
      (`local/muse/prompts/D4c.md`): SurfaceFlinger timestats per layer
      (totalFrames + present-to-present histogram, verified on the
      device) sampled once a second across the same three arms. Ledger
      row added.
      D4 Part 3 read (09-18 20:10) — D4 CLOSED on method: SurfaceFlinger
      timestats count presents. The old smoothing trial reaches 75–91
      presents/s at a two-vsync median spacing (16.5 ms) because it
      only swaps ~81 times a second; the explicit 120 Hz request is
      honoured by SurfaceFlinger but changes nothing. Uncapped with no
      trial the same APK path presents at a single-vsync median (8.5
      ms), so the panel and composition path are not the limiter.
      Verdict: the display proof is a property of the frame source,
      and it gets re-run once the host-replay route runs in the APK.
      `part3/sfstats.sh` + `sfstats_analyze.py` are the tools. Ledger
      row added.
      M5 launched (09-18 20:25, `local/muse/prompts/M5.md`): host-replay
      milestone 2 item 1 on the desktop, derived from the S2 header:
      XFB fidelity hash per replay, fail-closed side-effect counters
      (texture cache, pending EFB copies, FrameCount, after_frame
      triggers, PE pending, VI hash, record flag), then a replay-owned
      XFB destination rewritten in the execute stream, continuation
      check. No vendor change, no device.
- [ ] **M3b gate read (09-18 09:20) — corpus on the Odin + a DVFS
      floor problem:** on the device the heaviest track costs only ~11%
      more emu-thread CPU per frame than Snow Jam (12.1 vs 10.8 ms
      uncapped); the desktop 3.7× was the single-core player carrying
      the Metal backend, so earlier "3× worse" framing is withdrawn.
      The real finding: capped at 60 Hz the governor parks cpu7 at its
      3.28 GHz floor and Crow's Nest runs its first 51 s at 0.82× —
      below real time — then locks 1.0×. Shipping at any rate needs a
      clock floor: cheap probe first (user's "High performance" quick
      setting on the crows-cap arm), then an ADPF/sustained-performance
      hint or a busy-wait pacer in the runtime (D8). Movie note: the
      Snow Jam 3-min movie exhausts at HUD 3:33 at 1.0×; record a longer
      one if capped full-race numbers are needed.
- [ ] **D2 Odin read (09-18 08:20) → D2b:** replay on the Odin looks
      an order of magnitude cheaper than the S2 gate needs (≈0.5 ms wall
      per replay, unverified partial) but the bulk section kills the
      process after the loop; D2 named the fixes (flush per row; save/
      drain/restore the GPFifo gather-pipe accumulator with the BP/CP/XF/
      TMEM + RAM state). D2b (muse, same panel) implements them, re-arms
      EGL then Vulkan, behind D4 on the device. If `done` verifies, S2
      launches on that number.
- [x] **S3 landed (09-18 07:40):** FP-unavailable HLE committed
      (1aa479c, default OFF, env-gated) with M2 fix A (f58470d); strict
      determinism clean; Odin effect inside noise (ledger "FP-unavailable
      HLE"). The storm lever is closed: the 5.7% was inherent FPU
      context-switch work. The FP item below is DONE as a lever.
- [ ] **Opus spikes cut off (09-18 05:55):** S3 (FP HLE; report §1–6
      written, no commit yet) and S1b (Android repin port done, build
      not started) were killed by the session usage limit; the three
      concurrent Opus agents consumed it. Their remaining steps are
      runbook work and moved to muse: S3b (analysis of on-disk receipts,
      final tables, commit gate) and S1c (Android runtime + upstream C
      module from `s1b-src`, Odin A/B behind the device queue). Lesson:
      S1b should have been muse from the start; stagger Opus spikes.
- [ ] **S1 gate read (09-18 05:20) — backend decision:** LLVM route
      PARKED. The recompcore-flavor LLVM module never reaches a race
      under our automation stack (syscall-vector exceptions 1:1 with
      native exceptions, speed decays to 0.01×), the native-ABI flavor
      has no runtime anywhere upstream, and the flavor that links is
      compat-ABI dominated. Revisit only when upstream ships a runtime
      for the native module ABI. What S1 did deliver is the repin:
      a rebased outer platform patch (+254/−19, builds green) and the
      finding that the repo pin is one CPU-ABI generation behind
      (3 vs 4). S1b (Opus): port the Android patch stack the same way,
      build the Android runtime + upstream C module on the repinned
      tree, and run the D1 base shape on the Odin against the pinned
      stack — the direct test of upstream's C-backend codegen changes
      (region-leader entry switches, proven-pointer memory) on the
      target. That number decides the repin.
- [ ] **M3 gate read (09-18 04:05) — corpus switch:** Snow Jam is the
      LIGHTEST of 13 measured courses; Crow's Nest (heaviest that rides)
      costs 3.7× its render and 2.6× its update on the desktop. Every
      Odin budget number to date is the easy case (CORRECTED 09:20: on
      the Odin the spread is ~11%, see the M3b read). Budget
      numbers come from the corpus movies (Snow Jam 3-min = light
      anchor, Crow's Nest 3-min = heavy anchor); M3b runs both on the
      Odin with the pace binary first thing after S3 frees the device
      (per-track race pace + busy fractions), then reruns the 4
      unmeasured courses on the desktop (The Throne is likely heavier
      still). Crow's Nest strict compare is flaky under dual-core
      interleave (trajectory equal) — use its rider-state gate, not the
      dispatch gate, until a single-core recording exists.
- [ ] **S1 launched (09-18 03:25):** M1d built this repo's runner on
      upstream but the outer platform patch left 3 files rejected, and
      those hunks carry movie playback, HLE hooks and screenshots, so
      no pace comparison is possible from muse work alone. S1 (Opus):
      hand-port the rejected hunks onto upstream (deliverable: a rebased
      `moderngekko-platform.upstream.patch` for the repin), rebuild,
      then the same movie under upstream-LLVM, upstream-C and pinned-C
      with screenshots; that table is the backend decision.
- [ ] **D6 gate read (09-18 03:10) — route decision:** at stock the
      emu thread spends 3.2 ms in update and 7.9 ms in the render
      callback per frame (p95 11.0, max 20.7). The F route (sim at
      120 Hz on the emu thread) is dead on this SoC: render alone
      fills 95% of an 8.33 ms budget before update. The 120 route is
      host-side replay of the second frame (D2 capacity → S2 replay
      context) plus the emu-thread wins that make the 60 Hz sim
      comfortable: S3 (5.7%), codegen on the two hot chunks (14.5%
      of the thread; entry-switch pruning + FP helper calls
      `ppc_fcmp`/`f32_from_bits_slow`), LSE atomics (~1.2%),
      determinism-off in shipping (7%). Profile buckets in the
      ledger. M2b CANCELLED: Fix A (0.36% in D6) lands on the record
      tests + profile basis once S3's commit sequence runs (same
      patch file); D2 takes the M2 panel, gated behind M1d's runs.
- [ ] **D5 gate read (09-18 02:05) → S3 launched:** the Odin storm
      is 100% FP-unavailable, 5.7% of race emu CPU uncapped (3.8%
      capped), 59% from one thread pair. S3 (Opus spike): HLE the SDK
      FP-unavailable handler in the core the way the syscall vector was
      HLE'd (`emulate_syscall_vector`), validated by the same
      determinism tooling, A/B'd on the Odin in the D1 race window.
      Expected win ≈0.5 ms per 60 Hz frame; gate to land: strict
      compare clean + Odin race A/B outside pair noise.
- [ ] **M4 gate read (09-18 01:25):** LSE flags landed (nm-clean,
      harmless) but the A/B is inconclusive — straddles at ±7% and the
      window was the pause menu. Shader cache: nothing is ever written,
      item closed. Control probe still open (trial skips under the pace
      template) → D6: control probe with the trial template plus a
      simpleperf race-window profile at stock, after D5 on the device.
      Rule reinforced for every device brief: race windows are anchored
      by HUD-visible screenshots at recorded wall times (D1b method),
      never by sample-index guesses.
- [ ] **M1c read (09-18 01:10):** the native-ABI LLVM flavor links but
      nothing in upstream can run it (no runtime for that ABI), the
      upstream runner has no movie/frame-dump path, so the C-vs-LLVM
      pace question moves to M1d: this repo's desktop patch stack
      rebuilt on upstream ModernGekko, then the same movie under
      upstream-LLVM, upstream-C and (if the ABI check passes) pinned-C,
      with screenshots. That table is the S1 gate.
- [ ] **M1b gate read (09-18 00:45):** the upstream LLVM backend now
      generates and links a module for the stock DOL, and it ran 155 s
      natively on Metal with zero fallback (ledger "Upstream LLVM module
      boots"). Not yet a green S1 gate: no pixels seen (no screen
      capture in any agent context, fixed by frame dump in M1c), no
      pace number, and the flavor that links is compat-ABI-dominated;
      the native-ABI flavor has no link path (upstream template gap).
      M1c (muse): frame-dump boot proof from the SSD game copy, movie
      pace C-vs-LLVM on the same Mac, a budgeted attempt to link the
      native-ABI flavor, explain native_exc=0. S1 launches on M1c's
      pace table, not before. Side facts: upstream runner defaults to
      Vulkan on macOS and SHA-256s the whole game root at startup
      (15 min over SMB; game copied to the SSD).
- [ ] **D1b gate read (09-17 22:50):** matrix complete at stock
      clocks (ledger rows "Odin race pace, stock vs underclock",
      "determinism tax", "Null video backend", "capped 1.0 budget",
      "in-race native exception rate", "shader cache", "stock
      thermals", "per-callback split BLOCKED"). What changed: the GPU
      driver is out of the picture (Null = base); the emu thread at
      stock needs ≈9.7 ms per guest frame capped, ≈12 ms uncapped
      (the uncapped/capped gap is unexplained — det sync explains
      7 points); the native exception rate in-race is 35.6k/s, twenty
      times the desktop's, unattributed. Next: M4 (lse rebuild + trial
      relink for the control probe) on the device now, D5 (exception
      attribution on the Odin) queued behind it.
- [ ] M2 status (09-18 03:10): Fix A (rounding-mode sync guard)
      implemented in the platform patch + record tests; A/B waived
      (0.36% in the D6 profile, semantically identical guard, host
      contention) — lands with S3's commit sequence as `[M2]`. Fix B stopped after measurement
      (above). Fix C (fallback-JIT `InvalidateICache` on yield)
      propose-only; M2b counts calls/s.
- [ ] Codegen entry-switch pruning, one-chunk spike (September 17,
      perf-review §2, TOP avg-75 lever, desktop-only): every guest
      instruction is an entry-dispatcher case, forbidding
      cross-instruction register allocation; 77–83% of cases prunable
      to block leaders, PC stored at 95% of instructions. Guest bodies
      are 45–57% of cycles — a 1.3× there is ~1.15× overall. Bounded
      experiment: regenerate ONE hot chunk (8022D7A0/802197A0) with
      entry cases restricted to leaders ∪ return_targets ∪
      pre-return materialised addresses + cleared materialize_pc off
      hook paths; A/B via gamecube_movie_ab (trajectory-gated) +
      chunk signposts. Measurement is movie + wall throughput, NOT
      the profiler (update side unobservable by construction).
      Correctness enumeration (starts, m_return_hooks, loop heads,
      exception vectors) before any rollout. **SPIKE DONE 09-17
      (agent 43): INCONCLUSIVE, see follow-up item above — do not
      re-run uncapped.**
- [ ] fast-FP on/off re-A/B off the wall (September 17, perf-review
      §1, HIGH): the "0.00 prize" and the STOP/no-rebuild decision
      were measured at the phantom wall (void). The 0.83× reality may
      reverse the descope. Needs Odin or desktop A/B with CPU-ms per
      guest frame as the metric.
- [x] Determinism on/off re-test — DONE on the Odin by D1b (09-17):
      det-none +7% race pace, replicated (ledger "Odin determinism
      tax"); the harness tax every movie number carries. The FIFO fix
      (309f639) unblocked measurement, it did not fix a shipping bug.
- [ ] EFB re-A/B + EFB-copy cost (September 17, perf-review §1+§6):
      "EFB 2× full speed" void; re-A/B 1×/2×. Separate: CopyRender-
      TargetToTexture is 1.18% on the video thread, untouched by the
      (CPU-access) EFB verdict.
- [ ] Throttle s64 intermediate hardening (September 17, perf-review
      §1, post-affinity): ticks * new_clock_per_sec can approach the
      s64 limit (~2.4e18 vs 9.2e18, unbounded pre-first-Throttle);
      divide-first or __int128, zero behavior change. Record alongside:
      the was_limited guard (not Throttle's short-circuit) protects
      UpdateSpeedLimit's transition division — do not refactor away.
- [ ] Memory fast paths, ranked (September 17, perf-review §3,
      post-affinity, desktop-A/B-able): (1) #if-out g_mem_write_journal
      (XS, nothing ships it); (2) GC compile-time constants — no EXRAM
      branch, folded bound check — plus convert_to_double
      always_inline (0.66% outlined, same failure as psq); (3) hoist
      the gather-pipe test into mem_write* (HookExternalWrite 1.69% +
      Write32 1.16% + indirect-call overhead); (4) preserve_most on
      cold hooks; (5) fastmem last (structural).
- [ ] Desktop cost-table re-run (September 17, perf-review §4,
      post-affinity): the "needs 1.3–1.9×" arithmetic predates the FP
      wave by a day and was taken with validation on. Re-run on a HEAD
      module with MTL_DEBUG_LAYER pinned off before quoting again
      (player + script preserved, cheap).
- [ ] Harness measurement fixes (September 17, perf-review §1+§4,
      post-affinity batch): allow EmulationSpeed=0 (true unlimited;
      native_gamecube.py + m7run.sh hardcode 10); record the vertex
      loader in every receipt (Odin runs the ARM64 JIT, iOS/desktop
      the portable loader — all render-cost comparisons cross it);
      pin MTL_DEBUG_LAYER off for measurement runs and assert it;
      move screenshots + dispatch-sampling out of trial windows.
- [ ] Texture-cache mode + video-thread atomics (September 17,
      perf-review §6, low-medium, post-affinity): Safe-mode
      re-hashing at 0.58% never A/B'd; __aarch64_cas1 1.52% + futex
      share on the video thread unexplained.
- [ ] 120Hz track: replay re-scope + empty-queue sync (September 17,
      perf-review §5): re-scope replay to "re-issue a recorded frame
      with patched XF + new XFB?" (drops the exact-fidelity bar an
      interpolated frame doesn't need); schedule the named fix for
      the per-frame empty-queue GPU sync (~3.3ms floor, 2.74ms spin,
      largest named render item, fix named but never scheduled).
- [ ] Affinity follow-through (September 17): runner-side prime
      discovery (sysfs max-freq, never hardcode 6/7) +
      pthread_setaffinity_np at emu/video entries with silent fallback
      — design in affinity-summary.json proposal_runner, --affinity
      flag is the on-device oracle. Smaller: rename audit (why the CPU
      task carries 'GC Adapter Scan'; DOLPHIN_NO_JVM stub is private
      to androidcommon) and the FD pause-timing fragility note (disc
      latency shifts pause edges run-to-run under bSyncGPU=0).
- [ ] SyncGPU double-decode cost (September 17, review finding 3): the
      deterministic GPU thread path decodes every FIFO byte twice
      (CPU-thread preprocess + video-thread real) with slot-boundary
      waits. Quantify on Odin and gate SyncGPU to movie-determinism
      runs if it is on for regular trials. Check the pace-hunt
      numbers first — its attribution may already show this.
- [ ] Trial-driver fast-path cost (September 17, review finding 6,
      post-pace): NativeTrialAndroid::Step pays status-load atomics
      before the PC filter on every dispatch, so the trial binary is
      slower than the control by construction and the SpeedFloor judges
      a biased number. Move the checks behind the PC filter. Do not
      touch while the pace agent measures.
- [ ] Screenshot cadence in trial windows (September 17, review
      finding 4, post-pace): PNG deflate + readbacks perturb the exact
      window being measured. Scope screenshots out of trial windows
      (before/after, or lengthened cadence inside), like texture
      preload. Do not touch while the pace agent measures.
- [ ] Interp alpha period (September 17, review finding 5, XS):
      alpha uses TicksPerSecond/59.94 while Deadline uses /120
      (native/diagnostics/native_pose_interpolation.h:167). Confirm
      which is right for the 120Hz path.
- [ ] f32-from-bits-slow histogram (September 17, review finding 2,
      low): the "exceptional inputs" fallback stays hot after the
      conversion split (~1/4 of Run()). One-run histogram of what
      reaches it (suspects: signed zeros, NI-flush denormals); route
      the common cases through the inline path.
- [ ] Signpost update-side caveat (September 17, review finding 10,
      docs XS): same-chunk callees compile to gotos and never
      dispatch, so attribution.json update columns are
      "unobservable", not zero. Note it at the consumers; the
      pc-histogram result stays the only update attribution.
- [ ] Live-apply deferred→applied-after-quit E2E (September 17): run-001
      proves the apply branch and run-002 the defer branch, but no run
      shows a queued switch landing after an actual quit-to-frontend (no
      known quit input sequence in tools/; iOS covers it via menu-open
      pump). Needs a quit sequence, then a file-fire → defer → quit →
      applied run.
- [ ] Live-apply iOS compile check (September 17): App.mm liveApplyCourse:/
      applyPendingCourse wiring is pattern-matched and wiring-tested but
      never compiled (needs Xcode + signing).
- [ ] Layout-lottery follow-up (September 17, optional): the fcmp inline
      regressed wall throughput 7.3% ABA-confirmed despite removing the
      call with an identical body (+347KB/+17K branches shifting the 82MB
      ThinLTO layout). A retry needs a layout strategy (PGO, hot/cold
      split, section ordering), not a blind rebuild. Evidence + exact
      design preserved in local/research/fcmp/ (dylibs, legs, NOTES.md).
      September 17 (perf-review §2/§6): read as evidence of a
      layout/I-cache-bound regime, not a mystery — the retry is an
      order file built from line_tables + the 63 chunk signposts,
      not a blind re-inline.
- [ ] Onscreen trial hardening (September 17): budget-stop fires up to
      1 s late (integer-division truncation, inherited) — 1-line XS fix,
      noted untested. Vulkan present hook not built (needs a core-vk
      APK, S). ot3's end-cause is unproven (log stops at 59.9 FPS with
      no tombstone file — "died on the FIFO panic" is inference from
      the known movie terminator, plausible but unreceipted); next
      onscreen run should capture the tombstone or the clean stop.
- [ ] Display production wiring (September 17, display gaps 2-6): real
      CreateAndroidPlatform branch (replace the spike's
      CreateHeadlessPlatform interposition), headless=false,
      TERM_WINDOW→pause/ChangeSurface, audio choice (M, 1-2 sessions);
      vsync/pacing policy for 122Hz panel vs 60fps game (S); input glue
      for playability, not needed for trials (M); warm/ship shader cache
      (XS); 1.25GB asset + 16KB-page packaging story (M, product call).
- [ ] Patch-stack drift receipts (September 17, review finding 8): the
      per-layer checker excludes shared files, so a lost lower hunk passes
      silently. The suggested concat reverse-check does NOT work (verified:
      fails on HEAD's own stack — git applies same-file hunks in file
      order, so overlapping regions can't peel). Spec: bootstrap records
      per-file sha256 of patch-touched files + patch/pin identity; checker
      compares, falls back to layered checks with a note when the stack
      moved. Needs a re-baseline rule for branch switches.
- [ ] Trial driver fast path (September 17, review finding 6):
      NativeTrialAndroid::Step runs atomics + clock reads on every dispatch
      before any PC filter, so the trial binary is slower than control by
      construction and the SpeedFloor judges what it perturbs. Move status
      checks behind the boundary-PC filter. Minor: kind shadowing,
      watchdog-only at+120. Note: t3-vs-t4 stands (both pay it equally).
- [ ] Frame-exact snow A/B (September 17, review finding 11 caveat): the
      standing backend-independent verdict is movie-aligned (same
      m3-menu.dtm, matched race timers, deterministic panic point,
      mvk1/mvk2 byte-identical speeds) but screenshots are wall-clock
      cadenced, so capture phase dominates pixel diffs (agent's own
      caveat). Proceed with scorer + matched timers; build emu-frame-
      triggered screenshots if the shared-code hunt stalls. The /tmp/snow
      cross-device pairs compare different frames — cite only the movie
      A/B for parity from now on.
- [ ] Hot-thread affinity/priority (September 17, review finding 4):
      M7 capture shows the scheduler holds the hot thread on prime core
      7 unpinned in all 8 runs (video wanders 0/1/4/5) — pinning deferred
      unless a regression appears. **SUPERSEDED September 17 (perf-review
      §1): the 0.0% pinning verdict was measured at the phantom wall
      (void). Affinity agent launched on the Odin — see top of Now.**
- [ ] Alpha-period residual (September 17, review finding 5): alpha uses
      TicksPerSecond/59.94 while Deadline uses /120 (prior review note,
      still open). Reconcile before re-issuing gate 4b.
- [ ] Signpost update-blindness note (September 17, review finding 10):
      signposts can only speak to the render side (same-chunk callees are
      gotos; u=0 by construction). Consumers of attribution.json must
      treat update columns as unobservable, not zero — put that in the
      generator's doc, not just the header.
- [ ] fsck_exfat the archive SSD at a quiet time (September 17): the
      plumbing agent found 8 zeroed clusters in the SSD trial binary (size/
      mtime unchanged; caught by receipt check, restored from the verified
      device copy). Same exFAT fragility as the earlier archive flag errors.
- [ ] New menu entry / new peak = fixed-table surgery, parked (September 17):
      menu spike proved Tricky tracks are menu-selectable TODAY via the
      existing manifest (Aloha Ice Jam hosted on event 5 R&B row, 3-field
      manifest, rider spawned at Aloha coords; screenshots in
      local/research/menu-spike/ride-001/screens/) — zero mechanism work,
      per track just a converted archive + 4-line manifest on a
      same-discipline Peak-1 row (gating sidestepped; peak labels live in
      disc locale files, not the DOL). But there are NO spare menu slots:
      Single Event walks an explicit nav-graph of fixed 100-byte records
      (guest 0x802C35B0–0x802C4938), not the mode table, so event 22 (debug,
      vestigial, tail order -1, linked from nothing) can't surface by a
      mode flip. A new entry must move/edit the nav-graph + neighbor
      edge links/flags/labels + the 20-entry guest-pointer table at file
      0x2C1972 + locale labels (+ 3-peak UI/pass logic for a 4th peak), and
      list heads are entered by address (head refs may live in code → SMC
      guard). Cheapest unverified probe: in-place repurpose of a DONOTUSE
      separator as an event-22 node + one edge repoint (node lookup and
      separator semantics unconfirmed; 1–2 sessions to verify before any
      implementation). Separate conversion-side bug found: Aloha-as-slopestyle
      faults after standings (suspect unchecked 3-gate start gate; rides
      fine as race) — belongs to course conversion, not menus.
- [ ] Self-clearing short-window veto (September 17, idle F1): the
      SpeedFloor 0.97/0.99 hysteresis latches total starvation on
      transient dips (40/1102 allowed while averaging 0.92). Time-based
      re-probe or a narrower Resume-Stop gap, so dips withhold a few
      extras instead of all. Structural alternative (F2): key trial
      legs to guest ticks/rider progress, killing wall-gated phase
      offsets. Hygiene (F3): verdict-grade A/Bs need an exclusive
      host; same movie diverged across the skip knob pre-trial, so
      cross-knob trajectory identity can't be assumed.
- [ ] FIFO exception-poll change (September 17, review finding 3b): agent
      implementing (desktop parity + Odin validation). DESKTOP REPRO
      FOUND: uncapped (EmulationSpeed=10) + m3-menu.dtm panics on Metal
      with the exact Odin signature (GatherPipeBursted, CP:548) right
      after race load — agent notified, iterating locally. Recipe +
      log: local/research/ceil-probe/run-003.log.
- [ ] Odin viability gap (September 16): M3 proved scripted input drives a
      live Snow Jam race on the Odin3 (Pipe/0/ssx3 backend, no rebuild) but
      the device holds only ~1/8th speed in-race (stderr speed ~0.11–0.13)
      and ground/snow renders as green/red/black garbage under EGL (see
      /tmp/m3-shots/final). Needs perf triage (hotspot + what full-speed
      requires) and a texture-path investigation — possibly the same
      ground/snow issue as the iOS note below — before APK packaging.
      **Update September 17 (M5): perf triage closed — full speed in-race
      (0.97–1.0 capped, ~1.05–1.16 uncapped) from module -O2+ThinLTO,
      idle skip, and EFB 1 alone; new profile: endian helpers 12.1→0.00,
      FP outlined 25.8→16.2, CPU core now the frontier (Run/HookExternal/
      dispatch). **SUPERSEDED September 17 (perf-review §1/§8): the
      uncapped arm sat at the phantom wall (void); "12.1→0.00" reads
      "inlined, now unattributable" (cost moved into func_* bodies);
      the profile predates Wave B (morning-review finding 1); "full
      speed in-race" contradicts the verified 0.83× race pace —
      reconciliation via a capped arm is steered into the affinity
      agent.** Snow corruption SURVIVES: clean at race 0:04, garbage by
      0:14 — onset inside the race just before the ~0:15 FIFO-panic point
      (see /tmp/m5/shots-e). Lead: pre-panic FIFO-state symptom; the
      texture-path investigation should chase onset timing first.
      **Verdict September 17: OGL/EGL-backend-specific, shared root excluded
      by Metal cross-check (iPad stock clean 0:02–1:17 where Odin OGL goes
      blue→black→psychedelic; pairs in /tmp/snow/). Scale-independent,
      angle-dependent (airborne clean, grazing corrupts), FIFO panic
      downstream/separate. Vulkan spike triggered (running). Scorer:
      tools/gamecube_snow_check.py. Separate: iPad Metal stock goes
      orange-streak post-restart — the standing iOS review note is a
      restart-path phenomenon, not this bug; needs its own follow-up.
      **Superseded September 17: Vulkan headless works on Odin (full speed,
      one dual-backend binary) and reproduces the corruption with the same
      character (verified by scorer + eyeball: 0.53→0.92 black-ground
      progression). The bug is upstream of the backend — shared VideoCommon
      or module data, Adreno-visible but Apple-tolerant (Metal-clean does
      not exonerate shared code). Redirect the texture-path investigation
      to shared sampling/shader/TLUT code; scorer + Vulkan binary are the
      comparison harness.**
- [ ] Course texture/lighting review (user, September 16): wild-looking
      textures with the lighting observed in-course as a casual observer —
      particularly ground/snow. Needs a review pass over the course's
      textures and lightmaps. Baseline is now known-stock: the iPad ran a
      preloaded DDS pack until September 17, when it was pruned back to
      shipped assets (see `asset-policy.md`); the Odin was already stock,
      so EGL snow is not a pack artifact.
- [ ] 120 Hz verdict re-issue after the generation fix (September 16): the
      architecture review ([review-2026-09-16-architecture.md](research/review-2026-09-16-architecture.md)
      finding 1) withdrew gate-4b MECHANICS GREEN and the phone Combined
      oracle — every extra under F doubling was drawn unblended. The
      one-generation-per-tick fix, the blended validator gate, and the
      trialExtrasBlended phone metric are in. First on-device proof
      September 16 (later): iPad smoothing trial on the fixed build
      blended 35/36 extras, and an iPad Combined trial blended 30/30
      with 562 doubled updates. Desktop lifecycle proof same night:
      lifecycle-postfix2 (on gc-gari-026; 027's files were cleaned and
      are not in the archive) passes the blended gates — 202/203 extras
      blended, 262k matrices, generations step +1. Still needed: interp-fx
      determinism re-proof (needs 027-exact bytes for det-sched.dtm, or a
      fresh movie), the phone Combined re-run with blending actually on
      (that number decides retained host palettes), and re-issuing both
      verdicts.
- [ ] Arch-review findings 2–4 (September 16): (2) consolidate the trial
      state machine (four headers of file-scope statics; SSXResetNativeTrial
      misses counters) into per-namespace TrialState with a single Finish;
      (3) add a tainted-guest guard so a verify-failed halved guest can never
      be checkpointed; (4) decide explicitly whether the ship path doubles
      unconditionally or keeps the rider-state gate, and record it in the
      plan of record. Plus the §5 smaller items (Output() abort on device,
      App.mm trial-flag table, stale menu label, Deadline/alpha periods).

- [ ] Plan of record: [implementation plan, September 15](impl-plan-2026-09-15.md).

      The three in-flight agents landed (Aloha collision, boot-time course
      redirect, breaking glass) and are pushed. **Done September 15 (later):**
      the Aloha chain is re-ordered into one archive — `gc-aloha-006` (rails on
      the new scenery) then `gc-aloha-007` (terrain + scenery + rails +
      collision, `73ad0ab6`) — and it **rides** through the redirect, including
      one run with stock `bam.big` and the course's own `alo.big` resident at
      the same time ([the ride](aloha-conversion.md#9-the-ride-september-15)).
      Static collision on the new course is **observed**: under movie playback
      the collision archive and the same archive without collision ride the same
      line for 20 s and then part for good, and the engine's narrow phase
      returns contacts against imported collider 524 (§9.3). Next in the plan's
      order: the app's course picker (item 3), Aloha phase 2 (item 5, the
      scoring driver), and the deliberate-contact ride of
      `gc-gari-interactions-002`, which is now a movie-playback job rather than
      a lucky autopilot.
- [ ] Route control for the native runtime (measured September 15). A
      free-running ride cannot A/B anything: two runs of the *same* archive,
      single core, identical scripted input, diverge within 0.21 guest seconds
      of the race start and end a median 449 / max 69,184 world units apart.
      **Movie playback is the instrument and it works** — two replays of one
      recorded movie agree on all 879 sampled control-flow rows and their rider
      traces stay inside 113 units, so `tools/native_determinism_check.py
      play --course-manifest ...` is now the way to compare two archives or
      chase one object
      ([evidence](aloha-conversion.md#93-static-collision-observed-under-movie-playback)).
      What is still missing is *steering on demand*: a movie only replays the
      line it recorded, so hitting a chosen object still depends on that line
      passing through it. A waypoint autopilot would fix that —
      `tools/gamecube_input.py` already has `stick x y` and
      `gamecube_course_check.py` already reads rider samples live, so the
      follower is the missing piece; the PS2 tools (`ride_route.py`,
      `ride_autopilot.py`) drive PINE and do not apply. Movie playback should
      also settle the phone A/B noted below.
      **September 15 (later): steering exists, following does not.**
      `gamecube_course_check.py --route FILE` follows waypoints from the live
      rider samples and writes `SET MAIN x y` to the pad pipe (opened per write;
      a held writer gets EPIPE when the runtime reopens its read end). It
      calibrates the steering sense itself and measured it: a positive stick x
      turns the heading clockwise in the x/z plane, so `sign = -1`. One route
      reached 2 of 6 waypoints, a second reached 0 of 3 — a proportional
      controller on heading error will not hold a line down a mountain. Pure
      pursuit with late engagement does: routed at a collider 2,637 units off
      the natural line, the rider closed to **868** units and the engine
      narrow-phase tested that object 19 times where it had never tested it
      before — no contact yet, 68 units outside its own tolerance. The steering
      sign is now inferred from the controller's own error growth, because
      holding an input to calibrate it reads the terrain rather than the stick.
      Next: vertical alignment (steering is horizontal, so a route can arrive
      beside an object it passes over), tolerance and gain, and speed control.
      See [route control](route-control.md).
- [ ] Next Tricky course, not a race (user, September 14): after Garibaldi
      reaches parity (physics interactions and sprite/animation cycling are
      the remaining gaps), pick a Tricky Showoff course and map it onto one of
      SSX 3's non-race event types (slopestyle, big air, halfpipe,
      backcountry). Spike done September 14, see
      `local/research/next-course-spike.md`. **Recommendation: Aloha Ice Jam
      Showoff (`aloha.sop`) into `ASS1` "R&B", event 5, slopestyle.** Closest
      length match of any donor/slot pair, fits the slot's 6.99 MB without
      growth, decorative rather than machinery-driven, and on the peak the
      harness already rides. All twelve GameCube Tricky archives are already
      under `local/game/gste69-original/files/data/models/`. Facts: Tricky's
      mode data is `.aip` (Race) vs `.sop` (Showoff), same format, plus
      `RaceMode`/`ShowoffMode` GSF programs; no `.sop` reader exists and no
      showoff scoring table was found. SSX 3's event mode is the second word
      of the `0x802E2C18` row (2 race, 3 slopestyle, 4 big air, 5 halfpipe, 6
      backcountry), not the peak. Kind 21 is the only mode-gated record kind
      (absent in big air and halfpipe) and its header word is 4 for
      slopestyle with two extra distance markers, which `race_course.py`
      hard-codes as race; gate counts differ too (race 6, slopestyle 3).
      Pipedream rejected (its `.sop` equals its `.aip`, halfpipe has no kind
      21); Megaplex rejected while layer (c) is stubbed. Gap about 9-14 days,
      the largest items the scoring driver in the course script (2-4 d) and
      the per-course transform preset (2-3 d); the script driver is the same
      work Garibaldi's glass/block physics and flipbooks need.
      **September 15: the scoring driver should not be written.** Disassembling
      every stock course's script across all five disciplines shows no builtin
      and no handler name that belongs to the slopestyle courses and to no
      other discipline (only backcountry has any), so scoring is engine-side.
      What Aloha needs instead is to be *reached* as slopestyle — the `mode`
      word alone does not switch it — plus medal targets in `behiloc.dbb`.
      See [Aloha §10](aloha-conversion.md#10-phase-2-scoring-is-not-in-the-course-script-september-15).
- [ ] Visual remaster with trained upscalers (user, September 14; SSX 3 first,
      the PS2 games after). Hybrid pipeline, not "an image model upscales the
      game": classify assets → dedicated super-resolution per asset family
      (PBRify DAT2/SPAN, Real-ESRGAN baselines) → generative restoration only
      for a hand-picked top slice → automated QA → repack in the engine's own
      texture formats. Hardware: RTX 4070 12 GB available now, a 64 GB M5 Pro
      mini arrives the week of September 21 as orchestrator. First experiment:
      ~30 representative SSX 3 textures across environment, snow, clothing,
      boards, UI and effects, run through Lanczos / Real-ESRGAN / PBRify SPAN /
      PBRify DAT2, then put back in the actual game, not just contact sheets.
      Fact-finding done September 14, see `local/research/texture-remaster.md`:
      prototype **runtime replacement keyed by texture hash** first, not
      archive repacking. The native GPU backend already carries most of it
      (`texture_replacement.cpp`, PNG/DDS loaders, a 4 GB LRU cache) with no
      caller yet; the remaining work is a pack-directory flag, a dump flag, and
      the lookup in `gxcore_draw.cpp`'s texture resolve, about 2-4 days. The
      one real decision is reconciling the gxcore content hash (XXH3 over GX
      bytes + TLUT) with the dump-filename key (XXH64) so packs stay portable
      with Dolphin's convention. Repacking into archives needs CMPR/RGB5A3
      encoders, a GX tiler, a mip writer and a palette quantiser that do not
      exist, and ARA1 already sits near the 24 MiB wall. The 30-texture
      experiment and tooling gaps are itemised in the report.
      **Paused September 17 (user decision, see `asset-policy.md`):**
      shipped assets everywhere until the perf/gate-review window closes.
      Tricky injection and its assets stay; packs frozen under
      `local/research/remaster/`, devices normalized to stock.
      **Done September 15: all 17 SSX 3 courses, no C++ written.** The 2-4 day
      gxcore estimate above was wrong about the renderer: the native build
      compiles Dolphin's `HiresTextures.cpp`, not the aurora replacement path,
      so dumping and replacement are configuration
      (`tools/native_gamecube.py --texture-dump/--texture-pack`,
      `[Video_Settings]` in the per-game layer) and the hash reconciliation
      never arose. 17 dumps four at a time, 907 distinct course textures,
      per-family models (PBRify V4 for CMPR, Real-ESRGAN for everything else),
      288 MB at 4x, about 40 minutes end to end; ridden clean on three courses;
      an iPhone switch and a course picker in the pause menu. The runbook is
      [texture remaster](texture-remaster.md).
      **Quality gate, same day:** `tools/texture_pack_audit.py` measures
      colour shift, structure drift, alpha drift and flat invention per texture
      against its source. 109 of 907 flagged, nearly all of them improvements;
      the two real defect classes were flat fills gaining grain (15 textures,
      repaired with Lanczos in the shipped pack) and soft particle sprites
      gaining hard outlines (unfixed - no classifier separates a soft gradient
      from a blurred edge yet). Remaining: the particle family, weighting by
      on-screen area, mipmap sidecars, archive repacking, and the PS2 path
      (PCSX2's mechanism, different key).
- [ ] Course selection for added tracks (user, September 14): a menu or
      selection path that lists every imported course so new tracks can be
      added without a rebuild and without replacing a stock event. Today
      Garibaldi replaces Snow Jam's event and inherits its script slot, name,
      description and location tables. Fact-finding first: how the frontend
      enumerates events/locations, where names and descriptions come from
      (see [locale tables](locale-tables.md) and
      [peaks and locations](peaks-and-locations.md)), and whether the tables
      can grow in place or need a DOL patch. Design later.
      Fact-finding done September 14, see
      `local/research/course-selection.md`: the event table (23 x 100 B at
      `0x802CE5EC`) and location table (50 x 24 B at `0x802CEEE8`) abut each
      other and the next string with zero slack, so in-place growth is out;
      counts are hard-coded in a handful of enumerable sites (23 at
      `0x8005D638`, 50/49 at `0x801084B0`/`0x80109414`) plus `behiloc.dbb`
      and `bam.gdb`. The world archive name is the event record's `+68`
      string joined to `data/worlds/`, so a different archive loads by
      rewriting 16 bytes. Descriptions live in `cmnamer.loc` (little-endian,
      Snow Jam is index 508, no empty slots, hash function unsolved). Any DOL
      patch forces a module regeneration (`dol_sha256` is enforced).
      **Done September 15: the boot-time redirect exists.** The runtime
      patches Snow Jam's event row in guest RAM from a manifest
      (`SSX_COURSE_MANIFEST`, `--course-manifest`, `-ssxCourseManifest`;
      schema in [course selection](course-selection.md)); no DOL byte or
      module changes. The archive basename must match the BIGF member
      basenames inside it; case folds. `sg-redirect-5` is the first ride of
      the converted Aloha course. Open: `mode` alone does not switch the
      HUD or briefing (the Single Event menu overrides it), the save record
      keys by event slot, and the picture/drop/length stay the host's.
      **September 15 (later):** two courses are resident at once — stock
      `bam.big` plus `alo.big`, selected by `archive = alo` — staged by the new
      `tools/gamecube_game_dir.py`, which renames an archive's BIGF world
      members so a second course can live beside the stock one. The receipt now
      hashes every installed `*.big`. **Done September 15: the picker.**
      `tools/course_manifests.py` writes one manifest per event from the DOL's
      own tables, `mobile_gamecube.py courses` copies them to the phone, and the
      pause menu's Course row lists them; a launch flag still wins over the
      stored choice. Compiles for the device; not yet exercised on it.
      Unknowns: file-name case folding on the FST, and whether the save record
      is a fixed event-indexed array.
- [ ] September 14 priority: course restoration is the main track; keep 120 Hz
      research bounded. First reprojection batch captured eight matching riding
      frames and demonstrated an offline half-step warp. September 14: a
      footprint splat closes 77-81% of the point splat's holes across five
      frame pairs, with static-wall MAE moving under 0.02 units. Absolute
      uncovered area is frame-dependent though: 0.44% on the calm frame 7559
      but 1.2-2.4% on the movie-driven 7500-7507 pairs, whose p95 motion runs
      76-128 px. Raster coverage is answered; near-field motion is not.
      The alpha HUD layer is now done: three movie-driven runs over natural,
      black and white backgrounds solve the tail exactly on all eight frames
      7500-7507 (7.04% coverage, mean alpha 0.727, every pixel within two
      levels of the untouched run). The EFB is RGB8_Z24 with no destination
      alpha, so a transparent render target could not have worked.
      Next: GPU-resident cost measurement, and near-field motion for the
      rider/board, which better rasterizing cannot address.
      No live smoothing mode or phone budget is established. See the
      [revised reprojection evidence](research/120hz-reprojection.md).
- [ ] Fast-FP needs route-controlled phone input before it can be measured.
      The [bounded pair](research/performance-batch2-followup.md) ran both arms
      cleanly on September 14 (186 s each, no fault, no JIT fallback, thermal
      nominal, 87 riding rows each) and is **inconclusive**: dual-core is not
      deterministic, so the two runs separate within three seconds of the race
      start and share only 4 of 86 riding seconds within 100 units, median
      separation 13,614. The 12.9% render-callback difference tracks a 10.5%
      draw-call difference and the update callback moves the other way.
      Repeating this design cannot settle it. Next: either a deterministic
      single-core arm, which isolates the compile option but is not the
      shipping configuration, or movie-driven input on the device. The
      historical desktop 1,022 control-register rows still match with the
      strict-provenance movie-hash gap unchanged. Baseline 94f5096e is now the
      installed phone build; the signed 53e2e1e4 archive is preserved.
- [ ] Performance: follow the [September 13 performance review](research/performance-review-2026-09-13.md).
      Done September 13: always-on callback timer, dispatch sampling opt-in,
      dual-core validated on Mac and phone (stadium section 0.89 → 1.00 speed,
      render callback 9.5 → 7.8 ms) and made the persisted default in build 1b.
      Batch 2 (same evening): movie-based determinism gate, chunk-granular
      lookup table, and the fast-FP module, matching baseline over
      1,022 sampled control-register rows (see September 14 provenance limit
      above); phone module built, measurement pending. Next: measure
      fast FP on the phone, fewer chassis round-trips, a 15-minute dual-core
      thermal soak at 3× (still deferred). The bounded
      [depth reprojection experiment](research/120hz-reprojection.md) uses
      the last frame's color, depth and predicted camera; 3× Match at
      100–120 with speed ≥ 0.95 remains a target, not a result. Helper
      micro-spikes are closed.
- [ ] Follow the [September 12 architecture priorities](architecture-review.md):
      validated imports, state-aware route checks, and explicit course ownership.
- [ ] Restore donor fog/backdrop and check remaining visual differences at
      matching camera poses. Build 013 fixes the demonstrated 1×/2× terrain
      lighting mismatch; see the [comparison](garibaldi-visual-comparison.md).
- [ ] Capture jump approaches with camera/rider coordinates and visible patch
      IDs; distinguish actual late terrain visibility from low-contrast slopes.
- [ ] Check uninterrupted route progress, checkpoints and finish after resets;
      a results screen alone is not full-course acceptance.
- [ ] Control mapping doc (partly done in `native/ios/README.md` Controls): one table of action → GameCube input → Xbox pad →
      touch control, kept in `native/ios/README.md`.
- [ ] Odin: test the GameCube Garibaldi in Dolphin for Android; the disc
      builder is done, the handheld run is not. `gc-gari-009` (own textures,
      full race line) is on the share under `ssx3-workbench/builds/`.
- [ ] Odin: pair it with adb once (wireless debugging or USB) so
      `tools/deploy_odin.py` can push future ISOs straight to Dolphin's game
      folder; confirm which folder Dolphin scans on the device.
- [ ] 120 Hz: profile active callback CPU work, then reduce the dominant cost.
      Phone build 1747c62a measured 8.45 ms thread CPU within an 8.64 ms median
      extra draw (52 samples). Build 971dc928 verifies 1×/2× detail changes;
      its Half-output 2× trials reach 102.94/112.67 positive displays/s over
      8.92/18.38 seconds, but the longest warmed span is only 15.88 seconds
      at 114.34 displays/s. The newer f40bfef6 Garibaldi-only run measures
      Half/1× at 117.22 displays/s over its best 7.75-second warmed window,
      still too short with unresolved audio boundaries. Most collected thermal
      samples are serious; repeat a fixed route after returning to nominal.
      Course/trajectory differences prevent a causal output-size comparison.
      Preserve the three legacy app-span alerts and lifecycle clock unknowns
      without loosening guards. The newer Garibaldi-only 113c9b20 run preserves
      all 494 extras, including the new ownership fields, but its three Match/2×
      trials end through load protection after 3.49–13.55 s. No sustained pass.
      Short high-refresh bursts are established, but sustained pacing and
      distinct interpolated motion remain open. See
      [resolution evidence](research/120hz-output-resolution.md) and
      [CPU/config spikes](research/120hz-cpu-overhead-spikes.md). The new
      [ordinary-frame profile](research/normal-frame-cpu-spike.md) attributes
      72.5% of sampled desktop CPU-thread self work to generated guest code
      (14.5% named FP/conversion helpers included), with 6.6% inclusive software
      vertex conversion. Next: phase-tagged phone attribution and one narrow,
      equivalent helper optimization; desktop 3× shares are not phone timings.
      The [conversion spike](research/float-conversion-spike.md) passes all
      float32 bit patterns but trades call removal against code growth and
      rare-input regressions. Keep it scoped to a private hot-chunk build until
      workload evidence supports promotion. The independent
      [FMA classifier spike](research/float-arithmetic-audit.md) preserves full
      tested guest/host state; small, noisy timing gains do not justify a phone
      change. Existing phone builds already use optimized Release settings.
- [ ] 120 Hz route F (double update, halved dt) is the live track; its probes
      are on main. `gamecube_native_trace.py build` injects
      `native/diagnostics/native_callback_trace.h` into a diagnostic copy of
      the run loop under `local/`, so DOUBLE_UPDATE, HALF_CADENCE, HALF_DT,
      GUEST_WINDOW, SPEED_GATE and COUNTER_RESTORE can never reach a shipped
      build; each is off unless its variable is set. Next is the kill order in
      [the F spike plan](research/120hz-f-spike.md): the 2x-update workload
      probe on desktop first, since a desktop CPU that cannot hold
      `guest_seconds_per_host_second` >= 0.95 ends F before any dt work.
      Compare arms with `gamecube_parity_compare.py` (absolute guest timebase,
      end-of-tick body hashes) and gate them with `gamecube_f_regression.py`.
      The two rough edges found in review are fixed: `WriteConstSet` now
      verifies all fourteen addresses before writing any, and the parity tool
      leaves HALF_CADENCE skip rows off the alignment grid.
      **Phone trial shipped September 15 (night):** `NativeTrial::Kind::F`,
      trial-armed v3b drivers, a Try 120Hz sim menu entry, `-ssxFAt`/`--f-at`,
      graceful drift handling and stock-dt restore before finish/checkpoint.
      First live fire (single-core snow-jam-smoke, `--f-at 155`): 533/534
      doubled, clean restore, guard-limited at 10 s on 0.82 speed; update
      pair 5.12 ms fits but render costs 12.25 ms at saved 3x internal
      ([results](research/120hz-f-spike.md#phase-4b-phone-attribution-trial-shipped-first-live-fire-in-progress)).
      **Bias battery PASS-leaning (overnight):** 4 movies, matched player;
      lateral drift mixed signs with <1% mean, flip == engage in all four
      ([results](research/120hz-f-spike.md#bias-battery-results-overnight-post-merge)).
      **Idle-cancel stuck fixed September 16:** a cancel landing with nothing
      in flight restored consts but never cleared Running (return-site finish
      unreachable); F now also finishes at the update entry (13 ms desktop,
      phone-verified 537 doubled + clean finish). Lifecycle test grows a third
      leg + restore-after-idle-cancel gate (`1dd045b`).
      **A/B flags September 16:** `--course-manifest` (bare name or `stock`)
      and `--textures stock|remaster` override menu choices per launch
      (`d6441dd`); course/texture session events record effective values.
- [ ] 120 Hz render test on the F sim backend (user, September 15): when F sim
      is validated, prove >60 FPS presentation driven by doubled updates.
      Gated order: (1) F sim correctness — CLOSED September 16: reset
      sequencer is counter-driven (40 vs 41 ticks, +20 phase event exact,
      no double-fires), first tumble under F enters exact and exits +2
      (float threshold), 0x100 trap shows symmetric float physics with no
      state-8 integer writer, bias battery PASS-leaning
      ([evidence](research/120hz-f-spike.md#crashstate-timer-coverage-desktop-gate-1-closed-september-16));
      Adversarially reviewed same day: envelope 41=41 exact (stronger),
      mid-tick entry disclosed, phase +20/+21 1-tick residual (non-counter
      gate input), 484s are transition one-shots (11x cruise rate open),
      governor silent whole tumble, k computed (renorm candidate), r2 fix;
      accepted risks logged (same-context reset, 484 rate, renorm call,
      router flags);
      (2) input latching — RE-SCOPED September 16 as desktop research
      tooling only (movie-stream gating for menu-window measurement;
      all F results to date have zero input confound, live re-poll is
      already correct, no product change) — not blocking phone/render; (3) phone F headroom at 1x internal (pair + render + system <
      8.33 ms sustained); (4) 120 Hz draws from sim state — DESKTOP
      VERDICT September 16: back-to-back render-every-update draws
      fully but the game's single-slot queue evicts the ordinary draw
      (59/59 rejected) — net 60 Hz half-stale, so true-120 needs
      VI-paced 2-deep queue (backlog 10) or the smoothing/XFB path
      (phone path PROVEN additive: 783 displays = 60/s + 32/s extras,
      zero eviction — gate-4b de-risked);
      DESKTOP 4b September 16: MECHANICS GREEN (F + schedule + pose
      interp compose: 60/60 doubled, 36/36 interpolated extras at
      alpha 0.6–0.78, zero eviction, zero wedge) — remaining 4b is
      the combined trial kind on the phone with present.csv oracle.
      **WITHDRAWN September 16 (later)** — the 36/36 extras were
      unblended duplicates (generation double-count; review finding 1).
      Re-issue needs the interp-fx/lifecycle reruns with blended > 0.
      Trap logged: DTM playback stomps GFX config from the movie
      header (fixed via det-sched.dtm byte 149);
      (5) pacing acceptance (>=117 displayed/s + sim speed >= 0.98 +
      input-latency measurement) with fallback to F-sim/60-draws, then
      stock, on budget miss. No step starts until the gate before it passes.
- [ ] 120 Hz headroom backlog (user, September 15): measured budget is
      update pair ~5.1 ms + render ~12.3 ms at 3x single-core on the phone vs
      8.33 ms. Biggest first: (1) F + dual-core phone run — unknown, and
      dual-core previously moved render 9.5 → 7.8 ms with 25% headroom; the
      ship config may be F+dual-core while tests stay single-core;
      (2) 1x internal for 120 Hz mode — render dominates, config-only change,
      isolates the F update question; (3) production-quiet probe delta — the
      trial's per-body Diff/Hash/Emit/fflush rides in every measured pair,
      size the ship prize with a quiet-mode run — CLOSED September 16
      (~0.1 ms med, ~2% per pair; no headroom); (4) phase-tagged update
      breakdown — CLOSED September 16 (pc histogram: update ~99%
      traversal+physics, bookkeeping ~1%, view 0%; render runs 2x the
      guest instructions of update); (5) update-pair tail —
      CLOSED September 16 as host-attributed (crash-f window: CPU max
      5.35, wall max 7.90, zero over 8.33; spikes show wall≫cpu); (6) fast-FP phone measurement (built, pending)
      plus hot-chunk float-conversion where the breakdown points; (7) fewer
      chassis round-trips (existing item); (8) 1x BC texture pack for perf
      mode (bandwidth, not the 4x quality pack); (9) view/camera at 60 +
      physics at 120 split — CLOSED September 16 as answered-NO (no
      view work inside the doubled update to split); (10) VI-paced true-120 (2x update+render) vs
      back-to-back halves — end-architecture question, needs 1–3 first.
      **Measured September 16 (4 phone runs):** 1x helps (render 12.25 →
      9.37 same-window, speed 0.82 → 0.91) but pair+render ≈ 12 ms still
      misses 8.33 — (2) alone does not reach budget; dual-core shows no
      F-trial win (CPU-saturated updates leave nothing to overlap) and no
      dual-specific trial stalls; cross-run render medians (9.4–13.0) are
      section-dominated (blind sequence doesn't hold a line). Fast-FP
      kitchen-sink (1x + dual + fast-FP) bounds the possible next.
      **Kitchen-sink HELD September 16:** 1x + dual + fast-FP rode 25 s at
      speed 1.0 with 1479 doubled, no limit — the first F trial to hold a
      full window. Attribution split the credit: single-core + fast-FP
      limited at ~10 s / 503 doubled (speed 0.97 → 0.83 on trial start,
      present oracle pure 60 Hz), so dual-core carries F doubling;
      smoothing under dual-core held its full 35 s window untouched
      (1097 extras, no limit) with the present oracle at ~91/s median
      8.4 ms — 60 originals + ~32 extras/s, every extra reaching glass.
      Combined kind (`e07d74a`) merges both paths next.
      **Combined oracle September 16:** kind=2 rode 155 → 173 at kitchen-sink
      settings, then the floor limited on long_rate 0.946 < 0.95 (2 s
      window) — not on output: doubled held full rate (1048, 58/s) while
      extras trickled at half the pure-smoothing rate (278, 16/s), presents
      44% above-60 in bursts (fps peaked 102). Both costs compose, as
      predicted; the finish proved the kind's real point on device —
      completion_mode at start, restore_mode + dt-const restore 0.5 ms
      apart at the end, clean Finished, no stuck Running. Post-trial fps
      dip at seq ~196 repeats run B's at the same sequence point: section
      confounder, not trial-related.
      **ORACLE UNDERSTATED September 16 (later)** — the immediate-XF upload
      path was effectively disabled (zero blends), so the composed cost
      understates; the honest re-run number decides retained host palettes.
      **Perf spikes September 16 (desktop, phone down):** five parallel
      spikes, zero tracked edits, artifacts in local/research/120hz/spike-*/.
      Render breakdown maps 11.05ms quiet pair+render (top: 4.73ms update-pair
      host, 2.74ms ph2 GPU-completion wait; EFB/uploads/shaders closed as
      levers); res curve keeps 1x (all toggle deltas within noise, 1x
      minimizes fill by construction); adaptive extra-capping is a negative
      (displays fall 1:1 with extras); fast-libm doubling cut is real but
      tiny (-0.16ms/pair, parity questions). Only merge: `--preload-textures`
      launch override (`f8e2f75`) scoping pack-decode cost out of trial
      windows. DDS pack (-85% resident) queued for phone verify.
      **Preload A/B September 16 (phone):** remaster + smoothing, flag on vs
      off, both held the full 35 s window unlimited. Preload is a tail fix,
      as designed: trial p99 medians 14.1 vs 15.1 ms, worst second 22 vs
      35 ms — the off arm's worst second lands exactly on trial start
      (first extras + fresh angles decoding on demand); +66 extras with
      preload (1238 vs 1172). Pre-trial tails identical (worst hitches are
      section/sim, not texture). First attempt voided: user pause shifted
      run 1 into a heavier section (limited), run 2 stillborn on likely
      auto-lock suspend — keep the phone awake during chains.
      Audio skipping in heavy areas is a budget-overrun symptom (CPU
      starvation → DMA underrun), fixed by headroom, not audio work.
      **Menu static fixed September 16:** separate mechanism — an idled AX
      task leaves pushed DSP at a frozen nonzero constant (whole seconds,
      2 distinct samples, proven in DSP dumps); DC-blocker in the iOS
      backend settles it to silence, user-confirmed fixed. `--audio-dump`
      + dump collect stays as the pushed-sample oracle.
- [ ] 120 Hz by frame generation is ruled out, not pending. The Metal
      interpolation prototype on `spike/120hz` (worktree
      `../ssx3-120hz`, unmerged on purpose) cut emulation to 4.9 FPS at 0.36
      speed against 59.4/0.99 stock, and cost 10.4 ms of GPU per synthesized
      frame - more than half a frame period on its own. The branch's own
      diagnosis blames a CPU wait on the interpolation command buffer, but
      there is no `waitUntilCompleted` on the per-frame path; the likely cause
      is `[layer nextDrawable]` back-pressure, since it presents twice per game
      frame with `presentAfterMinimumDuration:1/120` on a 60 Hz panel that can
      retire only one - which the branch's own iOS section had predicted would
      throttle emulation. Keep the branch for its approach-2 reading: the
      `rawProjection` to near/far/fov/aspect derivation, the XFB-copy snapshot
      point for EFB depth, and the `MTLFXFrameInterpolator` contract including
      the `uiTexture` input that would fix HUD ghosting. Do not re-measure
      frame generation on the Mac's 60 Hz display; it cannot show the cadence.
      Its `check_stacked_patches` change to `tools/native_gamecube.py` must not
      be merged as written: it engages whenever `spike-120hz.patch` merely
      exists, which breaks `configure`/`build`/`run` on main, and its stack
      omits `recompcore-course-redirect.patch`, so it fails even with the spike
      applied (residual: `Source/Core/Core/CMakeLists.txt`). A correct version
      keys on which overlays are *applied* and lists them all.
- [ ] Phone: compare 75%, Match internal and Half output on the same route
      at fixed internal detail; verify Match through menu 1× ↔ 2× changes.
      Build 113c9b20's phone run confirms Match/2×: output 1947 × 896,
      visible picture 1556 × 896, EFB 1280 × 1056. The picture looked fine;
      label these stages clearly. Audio inside-snapshot zeros do not prove
      full-trial continuity. See [resolution evidence](research/120hz-output-resolution.md).
- [ ] Replay: bind captures to the actual encoder frame, prove exact-image
      fidelity in an isolated renderer, and complete owned-memory/ordering
      gates before live replay or more interpolation. The private FIFO audit
      and 180-second capture/continuation check pass, but screenshot-request
      identity does not prove the encoder's frame identity or render fidelity.
      Carry the frame ID through FrameDumper, then compare a separate-runtime
      replay against that exact image. Phone replay remains disabled. See
      [replay evidence and remaining boundaries](research/120hz-host-replay.md).
- [ ] Make MemoryWatcher reads observational: replace unchecked HostRead
      pointer chasing with checked reads. Failed watches can reach a panic
      path that raises a PI interrupt. The 031 river check logged 48 startup
      warnings; the compiler comparison also saw warnings during gameplay
      under both O2 and O3. Preserve their distinction from guest faults while
      eliminating the observer side effect. See
      [collision diagnostics](gamecube-collision.md).

## Garibaldi in the GameCube engine

- [x] Collision priority 1: restore terrain reset recovery, including the river
      beneath the late bridge reported at 89% on iPhone build 021. Convert
      source physics/effect bindings and verify reset destination; preserve
      valid riding on the bridge above. Source inventory is in
      `local/evidence/garibaldi-visibility/collision-backlog-audit.json`.
      Build 027 combines the 622 authored reset patches' correct SSX 3 reset
      flag with grounded recovery paths separate from airborne racer paths.
      Normal-course, 64% waterfall, late river and upper-bridge native checks
      pass, with stable recovery and no loops. Supersedes 023's wipeout
      mapping and 025's airborne-path regression. Installed on iPhone with
      matching checksum readback on September 13.
      See [collision evidence and format notes](gamecube-collision.md).
- [ ] Original water physics/effect callbacks remain separate from terrain
      recovery; translate them for response at water height.
- [ ] Collision priority 2: validate broader static obstacle encounters and
      deliver candidate 031 separately from phone performance comparisons.
      The rigid-transform fix restores the engine's collision inverse while
      preserving rendered placement: a matched rock fixture now has 22
      positive contact returns versus zero before. Waterfall and river reset
      checks pass. This does not certify all 2,059 enabled instances or full
      course progression. Multipart shapes, scripted/physics objects and
      conservative reset-path clearance omissions remain explicit. Phone
      assets remain 027; see [collision evidence](gamecube-collision.md).
      September 14: original-position rock and sign fixtures produce 44 and 8
      positive engine contact returns with clean runtime checks. Player query
      ownership remains unknown; the tree fixture missed its obstacle.
      Next: a steered player encounter/query identity and route/bridge clearance.
- [ ] Preserve donor terrain surface behavior through a verified profile:
      direct reset-flag mapping is implemented in build 025; snow/powder/ice/
      rock and non-colliding patches still inherit one target header. Do not
      assume the two games share enum values.
- [x] Build 022 compiler fix: honor initial GSF visibility and authored
      post-countdown gate removal. Removes 51 erroneous draw instances;
      timed donor gate animation remains future gameplay work.
- [x] First static scenery pass: gc-gari-020 imports 621 models / 3,290
      placements and is installed on the iPhone with checksum readback.
      Native riding verified; phone test launch is blocked by the locked
      device. See [scenery scope and evidence](gamecube-scenery.md).
- [ ] Scene animation is missing across the board, in three independent
      layers; the user reported no moving scenery on September 14 (direction
      arrows, block interactions, breaking glass, crowd). Measured against the
      donor NBD/GSF, not guessed:
      **(a) Animated and multipart prefabs are never imported.**
      `eligibility()` rejects them, so 102 of Garibaldi's 3,393 placements
      (3.0%) are absent entirely. These are missing objects, not still ones.
      September 14: every multipart donor model carries exactly one *meshless*
      part — a transform-free root (parent 0xffffffff, no matrix, no bounds)
      that the geometry hangs from. Counting it made models with a single
      geometry part look multipart, so the 102 split three ways rather than
      needing one big pipeline:
      **(a1) 13 placements needed nothing.** Models 132/133/153 are one
      geometry part, not animated, no local matrix. `geometry_parts()` now
      ignores transform-free empty roots and they import: 624 models / 3,303
      placements, up from 621 / 3,290. Models 133 and 153 are long tall
      banners (108 verts, extent 43x112x2470) whose materials carry a 2-frame
      flipbook on texture 61 — the best direction-arrow candidates in the
      donor. Model 132 is a 4-vertex quad flat in Y (3x0x1362), a ground
      decal.
      **(a2) done September 14: 64 of the 79 land frozen.**
      `--animated-as-static` admits a single-geometry-part animated model and
      imports its rest-pose display lists; `animated` only reports that the
      part names separate animation data, and the geometry is read the same
      way regardless. 641 models / 3,367 placements, up from 624 / 3,303. The
      receipt lists them as `animated_imported_as_static` so their presence is
      never read as animation support. The remaining three models (280-282,
      15 placements) carry a local matrix and now report `local matrix`,
      joining (a3) instead of hiding behind `animated`.
      **(a3) done September 14: `--compose-local-matrices`** lands all six
      models (647 models / 3,392 placements); build
      `gc-gari-scenery-localmatrix-001` rides a clean 180 s check (exit 0,
      zero faults). Visual confirmation of the rotated crowd figures is still
      unverified, and 49/86/90 add no drawn instances (all placements start
      hidden). Original scoping kept below.
      **(a3) 25 placements need local-matrix composition** — models 49/86/90
      (10, genuinely multipart: 23 geometry parts, 22 matrices each) plus
      280/281/282 (15, single part with a matrix). Scoped September 14 and
      **not** a quick win: strip vertices are index triples into globally
      shared position/uv/normal arrays written once for the whole import, so a
      local matrix cannot be applied in place without moving every other model
      that shares those positions. It needs transformed position copies, index
      remapping, a 16-bit signed range check against the model's 1x/4x scale,
      and the same composition mirrored in `gamecube_collision_import.py`,
      which re-derives and compares instance records. Model 32 (normal palette
      over 256, 1 placement) remains separate.
      **(b) Material flipbooks are staged but never sequenced.** 16 of 125
      donor materials carry a 2-5 frame flipbook, covering 74 placements;
      the countdown light is one of them (material 66, flipbook 5, five
      frames). The start gate work proves the images import correctly and
      that nothing advances them.
      September 14: SSX 3's own frame-sequence format is decoded and written.
      A plain 20-byte kind-0 material is marked by `mode == 0xffffffff`; an
      animated one appends a count and that many global image IDs. 25 of the
      archive's 2,687 kind-0 records are extended, consistently. `mode` is
      not an enable (the same two-frame sequence appears under 0, 1 and 2),
      so it is chosen by analogy: the only two five-frame records are the
      host's own countdown lights and both use mode 1.
      **Validated September 14: neither mode advances the sequence.** The
      mode 1 run is clean (896 samples, exit 0) and its light column holds the
      same lamp pattern through the countdown, as mode 0 does. The control is
      four mode 0 frames (16:09:32-35) showing an identical column; the
      apparent change in earlier crops is a translucent blue panel that tints
      the column at one camera angle, present in the first frame of both runs.
      The test was capable: donor images 69-73 are five distinct textures
      forming a progressive countdown (dim, red, +yellow, green last).
      Evidence in `local/research/startgate/flipbook-evidence/`.
      Writing the extended record is therefore necessary but not sufficient —
      something must drive the frame index and nothing in the course does, so
      **the countdown flipbook belongs to (c), not (b)**, exactly like the
      gate visibility bit before it. Do not generalise flipbook emission to
      the other 15 materials / 74 placements until (c) can drive one; the
      records would be correct and inert.
      **(c) Every LUN course program is an empty stub** (235 disabled), so no
      authored scripted behaviour runs at all: timed gates, block and glass
      interactions, effects. The
      [start gate](gamecube-scenery.md) is the first probe at re-attaching
      one event, and it found the visibility bit is plain data, which is the
      cheap half of (c).
      Original sequencing was (b) → (c) → (a), on the assumption that (a)
      needed a whole new pipeline. The empty-root finding retires that: only
      10 of (a)'s 102 placements do. Current order, most visible payoff per
      unit of work first: **(a1) done** → **(a2) crowd as static, 79
      placements** → **scenery interactions (glass, blocks), the visible
      slice of (c)** → **(a3) local matrices, 10 placements** → the runtime
      animation binding and the rest of (c). (b) is written, validated as
      inert, and now folded into (c): the records are correct and will stay
      dormant until something drives a frame index.
- [ ] Scenery interactions — breaking glass and scattering blocks. User
      request September 14: queued as the batch after the (a1)/(a2) geometry
      work. Objects remain intact on impact (user, Sep 13). This is layer (c)
      applied to a specific, visible case, so it inherits the LUN stub
      problem: the authored break behaviour lives in disabled course programs.
      **Inventory done September 14** — the identify step is complete; see
      [collision evidence](gamecube-collision.md). `u0` in the GSF property
      record is an immovability sentinel: 483 of 531 records hold 1e30, only
      48 hold a finite value. `collision_mode` separates the classes, and
      **mode 3 carries both a physics reference and an effect slot**, always
      with the low 0.20 restitution: models 7 (39 placements), 19 (22) and 1
      (2) — 63 placements, the scattering-block candidates. A further 23
      mode 2 records are hidden and carry an effect with no physics, the shape
      of a trigger volume; the crowd prefabs 269-288 carry effect slots 4/5/6.
      `instance_gameplay()` now exposes them as `immovable` and `bounce`.
      **Pushable blocks bound September 15 (`tools/gamecube_interactions.py
      --pushable-blocks`).** The stock mechanism, decoded in
      `local/research/startgate/breakables-recipe.md`: definition word 2 is
      a behaviour-class oid indexing the script record's 24-byte class table,
      whose slot 1 (create) names a program; the stock pushable is a
      one-function program calling builtin 6 AnimTeeter on the firing
      instance. Every imported definition had word 2 = -1, which is why no
      event ever fired. The tool clones the 63 mode-3 placements' definition
      with the class pointer set, claims class row 0, and writes the teeter
      program (stock mass/travel, donor restitution 0.20) into stub slot 69.
      `gc-gari-interactions-001` (on top of the countdown build) rides a
      clean 300 s check and is **installed on the iPhone** (September 15,
      00:06). Not yet observed: a block actually moving on contact; the
      donor's physics and effect records stay untranslated. Glass next: the
      23 hidden mode-2 trigger volumes need a contact-slot program (stock
      ABC1 program 171 shape: restore self, AnimObject per debris piece, 52
      inline particle args), and the debris models are not yet identified.
      Nothing is translated to target behaviour, and it is gated behind the
      same driver problem as the gate bit and the flipbook: correct data alone
      stays inert while every LUN program is a stub.
- [ ] Restore the Garibaldi start gate and countdown lights; user reconfirmed
      they are missing on iPhone on September 13 (assets 027). The three gate
      models are supported static geometry, deliberately omitted by 022;
      restore their timed visibility/flipbook binding, not general mesh
      animation. September 14: native loader proves the flipbook is a full
      signed 32-bit field at +68; the shared reader is corrected and tested.
      Hidden staging candidate retains all five light frames and three models;
      its event binding is still unimplemented. The first observer run confirms
      the dispatch side: `StartlightBegin` and `StartgateOpen` each fire once,
      3.72 s apart, with the staged instances bound, and both named lookups
      return value type 0 rather than a callback — so the lookup is the
      attachment point and nothing runs there yet. September 14: the reversible
      visibility operation is found and is pure data, not an engine call.
      Every instance selects one of the course script's 28-byte definitions;
      word 1 bit 16 draws and bit 21 collides, matching the donor GSF's own
      bit 0 and bit 5 shifted by 16. Definition 39 is used by the three staged
      countdown instances and nothing else, so that one record decides whether
      the gate and lights exist in the scene. That bit is **load-time only**.
      `--visible` builds
      `gc-gari-startgate-visible-001`, which differs from the hidden candidate
      by seven bytes, all inside that definition. Two clean 185 s checks
      confirm it: at the same countdown number and camera the visible run
      draws the canopy, six starting stalls and the light column, and the
      hidden control run draws none of them, with riding unaffected.
      The restart is observed too, over three races in one 481 s check:
      both events re-dispatch (windows 3.919 s and 3.736 s), so a handler
      must be re-entrant; re-entering the course after a finish raises
      `StartgateOpen` **alone**, so it must not assume the pair; and the
      three instances bind once and survive both, so the course is not
      reloaded and a handler can hold the definition. All five lookups
      still return value type 0.
      **Visibility solved September 14 (handler-004): the runtime bit is bit 0
      of the same `+128` word.** The visible build reads back `0x10003`, the
      hidden one `2`, and handler-003 only ever wrote `0x10002`. Builtin 2's
      command 1 mirrors the property half into the low half (`srawi 16; or`),
      which is what pointed at it. With `SSX_STARTGATE_MIRROR=1` the handler
      drives bit 0 too, and the gate draws at countdown "3" and is gone at GO,
      on both the first race and after the restart (clean 300 s check).
      Evidence in `local/research/startgate/handler-evidence/`.
      **Course-side script path works (September 14).** User chose course-side
      scripts over host hooks. `tools/gamecube_lun.py` assembles Luno bytecode
      (round-trips all 238 stock programs) and `--countdown-script RATE`
      writes a program into slot 3: the observer shows both named lookups now
      return a callback (type 5) and both closures are invoked; the probe
      variant removes the canopy and stalls during the countdown by script-side
      DeadNode (`script-evidence/`). **Lights done too (script-003):** the
      handler calls builtin 0 to create the instance's modifier host, then
      builtin 22; the lamps cycle through the countdown and the gate returns
      after a restart (engine course reset). Remaining polish: the donor's
      authored 1.0/0.5/0.5/0.5 s beats versus the free-running 1.3 flips/s
      loop. Earlier attempt, kept for the record:
      **The handler is written and the flag write does not work.**
      `gamecube_startgate_handler.py` sets the bit on the lights and clears
      it on the gate, in the shared definition and in every live instance's
      own `+128` word: four effective writes over two races, no redundant
      write, no refusal -- and the gate is never drawn. The bit decides what
      the course loads with, not what it draws now; the likely mechanism is
      membership of a draw structure built once at load. Next: characterise
      builtin 2 (`8019193c`) `DeadNode`/`RestoreNode`, which the September 13
      audit identified and warned not to assume reversible. It has to be
      understood rather than avoided, and the handler will drive it once it
      is. Countdown length (both windows exceed the donor's 2.5 s of
      authored waits), the flipbook sequence and the authored gate
      appearance remain open.
      Validate
      and target `StartgateOpen` dispatch, then check countdown, unobstructed
      GO and restart. Keep hidden helper geometry excluded. See the
      [source audit and next spike](gamecube-scenery.md#start-gate-audit-september-13-assets-027).
- [ ] Complete donor scenery lighting/material flags, animated/multipart
      models, grind splines and object collision.
- [x] Build 021: reusable donor rail reader/encoder, topology and distance
      checks, and a separate 169-path Garibaldi candidate. See
      [rail conversion](gamecube-rails.md).
- [ ] Validate rail mounting, curved traversal and transfers; verify the
      diagnostic sound/effect binding. Build 021 is installed on iPhone at
      the user's request with checksum readback; user confirmed gate rails work on Sep 13. Curved traversal/transfers still need checks.
- [ ] Isolate host scenery, including content streamed from adjacent locations;
      dropping the target's kind-2 models alone is only a probe.
- [ ] Course name and description in the GameCube frontend (DOL/locale edit).

## Controls

- [ ] Virtual controller: explore dedicated Grab 1/2/3/4 buttons for useful
      shoulder-button combinations that are difficult or impossible on touch;
      consider replacing the individual shoulder buttons. User request Sep 13.
- [ ] Virtual controller: support boost held together with jump preparation;
      audit simultaneous touch ownership and layout. Backlog, not urgent.

- [ ] Touch control for the C-stick (board press), currently unmapped.
- [ ] Optional DOL patch: four-input grab mask to restore the eight PS2-only grabs.
- [ ] Exercise the physical-controller path with a real pad (untested so far).

## Mobile

- [x] Fast cold start to the main menu: skip pending intro movies and advance
      once after the title's first active input pass. Enabled by default,
      including Full Reset, with ordinary-boot override and checkpoint restore
      precedence. Build 113c9b20 is installed. Three final Simulator launches
      reach the real menu at 20.47–20.53 s; the phone reaches it at 20.614526 s
      after guest execution begins. User confirms fast start worked great.
      See [startup shortcut](research/startup-shortcut.md).
- [ ] Phone: verify the persisted fast-start toggle, Full Reset and checkpoint
      restore combinations, with audio continuity. Required game initialization
      and the original title-readiness wait remain; profile them separately.
- [x] Direct menu choices for output/internal detail, staying paused for
      multiple changes, and remembered selections across launches. Initial
      Half output + 2× detail confirmed by the user. Build f40bfef6 installed
      on iPhone September 13 at 20:59 EDT. Simulator UI checks verify direct
      selections, Resume, post-resize trial readiness, Match dimensions and
      a fresh launch restoring saved 75%/1× instead of defaults. Explicit
      Full/1× launch overrides and independent preference storage pass.
- [ ] Phone: verify the redesigned menu's saved choices with checkpoint
      restore/Full Reset and ordinary audio; Simulator UI checks use Null
      audio and automated sessions omit checkpoints.
- [ ] Verify lifecycle Resume repair on iPhone: return to an automatic menu
      after background/audio interruptions; reconcile actual runtime state and
      explicitly reactivate audio on Resume. Reported stuck during Sep 13 playtest.
      Build 2250d8d9's subsequent session logs three resumes and three successful
      checkpoint saves, then one failed final save. Build c2e098d3 adds save-stage
      failure reasons and common timestamps; reproduce that failure and verify
      relaunch restoration. All eight subsequent diagnostic saves succeeded
      in 97–137 ms, so the earlier failure remains unreproduced.
      Build 1747c62a adds five successful saves and two output resizes/resumes.
      Build 971dc928 adds 16 committed saves and one explicit active-trial
      cancellation for pause with drain/restoration. Verify fresh-launch
      checkpoint restoration after changing detail and repeated background/
      audio interruptions; the one cancellation does not close those gates.
      The later 113c9b20 phone session adds ten committed saves.

- [x] Menu with in-memory Resume, background checkpointing and restore across
      relaunches; Full Reset recreates the runtime and reloads files. Installed
      on iPhone; race restore and reset verified in the simulator. See
      [iOS notes](../native/ios/README.md).
- [ ] Profile cold startup separately: runtime initialization, full asset
      hashing, memory-card checking and course loading. Separate actual I/O,
      decompression/resource initialization, emulated DVD/card delays and UI
      timers. The isolated six-run FastDiscSpeed comparison reduces median
      Mac startup to menu from 20.10 to 14.85 s (26.15%), with complete startup
      states and runtime checks. Next: an explicit phone comparison, then
      course-load phase anchors; no phone default change or memory-card/course
      speedup is established. See [loading spike](research/loading-speed-spike.md)
      and [phase separation](research/startup-shortcut.md#loading-and-memory-card-follow-up).
- [ ] 15-minute sustained soak on the iPhone (thermal, audio starvation),
      deferred by the user; short functional checks take priority.
- [ ] Save / memory-card behavior on the phone, including read/write/relaunch
      and the checking-screen duration. Dolphin models asynchronous transfers
      at 512 KiB/s read and 96.125 KiB/s write; no simple fast-card flag is
      established. Measure before changing timing or completion ordering.
- [ ] Android native build (Vulkan backend, NDK toolchain); user has a dev
      account to configure. Not needed for the Odin while Dolphin runs the
      patched disc with JIT.
- [ ] Exception-vector interpreter fallback (0x0C00/0x0500): measure, then
      translate or hook if phone timings need it.

## Done

- [x] 2026-09-17 Odin affinity (23c5b86): --affinity emu/video pin flag
      + 5 tests. Pinned tail 1.578×→1.974× (+25%), 18.52→14.93 ms/frame;
      load dip 0.70→1.15 (+64%); lows →0.94+; prio nil; cpu0 control
      −41%. Mislabel resolved (GC Adapter Scan IS the CPU thread);
      Odin 3 is 2+6 prime cpu6–7 @4.32GHz, not 1+4+3. M5 contradiction
      reconciled (cap saturation + content, no DVFS paradox).
- [x] 2026-09-17 pace mechanism: RESOLVED — the ~1.16 ceiling was u32
      throttle-clock overflow, not structural (fixed 1f1bc2d). True
      Odin race ceiling 0.83× OGL / 0.73× VK (m3-menu, verified
      racing). Voids the at-wall verdicts: fast-FP 0.00, determinism
      0.0%, pinning 0.0%, EGL==Vulkan, EFB-2× full speed, desktop 1.17
      + validation sub-verdict, psq wall-clock null (perf-review §1;
      current numbers in docs/numbers-ledger.md).
- [x] 2026-09-17 desktop ceiling probe: uncapped menus bind at ~1.17
      (69.5fps, rock-steady across validation on/off + movie runs) —
      the pace is structural, matching Odin EGL/Vulkan to 4 decimals.
      **VOID September 17 (1f1bc2d + perf-review §1): the wall was u32
      throttle overflow; true race ceiling is 0.83× OGL / 0.73× VK.**
      Race ceiling unmeasured (panic). Evidence
      local/research/ceil-probe/. Tooling kept: SSX3_EMULATION_SPEED
      passthrough (+ test).
- [x] 2026-09-17 asset-cache boot verification: all paths proven live
      (miss→hash→write, hit→reuse, add/remove/mtime → miss). Stock
      restored byte-list-identical (110 files; a phantom empty bam.big
      I created by touching a nonexistent path was removed; DOL pin
      intact throughout).
- [x] 2026-09-17 desktop idle × trial mechanism (idle-A/B): no skip
      pathology — with the skip firing, ON ran healthy (270 extras,
      tick/wall 0.983, full VI-period spans); tick under-advancement
      and burst interaction both refuted. The A/B inverted on host
      load (OFF arm overlapped a sibling emu run: 40 extras at 0.918)
      and M4's 0.44 shape didn't replicate (plausibly confounded the
      same way — inference, traces never cited). Real finding: the
      floor hysteresis AMPLIFIES small rate gaps into total starvation
      (load-fragile trial gate). Evidence local/research/idle-ab/
      (report + analyzer + legs + frozen module). Agent retired after
      delivering (wedged on a leftover background search). Standing
      guidance unchanged: Odin idle ini stays ON for trials (idle-OFF
      runs 0 extras via floor vetoes, t4); desktop/iOS idle stays
      opt-in (no in-race pathology, no trial pathology — just no
      measured buy at O2).
- [x] 2026-09-17 onscreen smoothing trial (ot3): 25/25 extras blended
      AND presented, swap-correlated (median 0.67ms, max 0.80ms;
      analyzer reproduced every number). Full lifecycle in-race
      (258 frames), 259 in-window swaps @ 64.3/s vs 49.7/s baseline,
      in-window race confirmed onscreen (5th/6, 3%, 48 MPH, 0:06).
      Pacing: game-cadence-driven, vsync effectively off (don't lock
      future trials). at=128 (APK probe-wall lags ~18s on .so load;
      ot1/ot2 at=124 hit the heavy zone, 0 extras). Zero repo writes;
      APK + probes in android-spike/onscreen-trial/.
- [x] 2026-09-17 fcmp spike: NO-SHIP (verified). gx_fastfp_fcmp exact
      inline + macro redirect: parity clean (690/690, 706/706 strict
      identical; 510k differential, 0 failures), symbol 31/33/38 → 0,
      all 4,229 sites expand — but wall throughput −7.3% ABA-confirmed
      (3.55 → 3.29 → 3.55 M/s, recomputed from shutdown counters;
      guest speed agrees). Second-order layout effect, not body cost.
      Hunk reverted from patch file + live tree (check_patches green);
      design kept in local/research/fcmp/ for a layout-strategy retry.
- [x] 2026-09-17 psq always_inline committed: both helpers forced inline
      (M7: symtab 0/0, profile leaves 1.07/1.06% → 0). Live CORE tree
      synced (fcmp agent's byte-exact sync kept for psq; its fcmp lines
      peeled after NO-SHIP). Resolves the 7fed74d test inconsistency.
- [x] 2026-09-17 Android display spike: org.ssx3.display APK installs,
      launches, presents SSX3 onscreen (memcard check, Snow Jam menu,
      race start gate via screencap; 147 FPS samples, median 59.8,
      race ~56, clean 150s budget stop). Probe APK: 1200 swaps @
      8.199ms vsync-locked + AChoreographer feed; app-context verdicts
      (dlopen/module/mmap OK, /data/local/tmp writes denied →
      app-private user dir). Zero repo writes (spike-only
      CreateHeadlessPlatform interposition); 3 APKs shas recorded,
      still installed. Evidence SSD android-spike/display/ +
      /tmp/android-display/. Gaps 1-6 costed (XS–M).
- [x] 2026-09-17 Odin HEAD re-profile (M7): finding 1 closed — M5 module
      predated Wave B; at HEAD fp_helpers collapses 16.2→1.7%
      (fmuls/fadds/fma + unsplit conversion + both psq leaves gone;
      remainder _slow 0.96/fcmp 0.63/fctiw 0.17), func 45→57%, rest
      matches M5 to ~0.5%. CPU core (~15.5%: Run 2.78, HookExternal
      1.69, Write32 1.16, dispatch 1.14) genuinely the frontier.
      Provenance exemplary (module 1c6c89cf…/a34ee6dd…, m7/
      provenance.json). Trials: t7smooth 37/37, t7vk Vulkan 45/45
      (android_trial.py gained --graphics). Placement: hot thread on
      prime 7 unpinned; GC-Adapter-Scan comm confirms finding 4.
      Evidence SSD android-spike/m7/ + /tmp/android-m7/. Pending:
      desktop psq-symbol check, _slow histogram, Vulkan profile.
- [x] 2026-09-17 course-row live apply shipped (desktop/iOS): manifest
      re-applied without reset via ApplyCourseManifestLive under
      CPUThreadGuard on the title thread (no polling thread; temp
      SSX3_TEST_* removed, absence test-enforced). RideLoaded telemetry
      guard defers mid-ride switches until quit-to-frontend (run-002:
      24 per-tick defers, exit 0); run-001 applies mid-menu with 3
      logged writes + bit-exact Aloha spawn. Desktop
      SSX3_COURSE_REQUEST file trigger (tools/live_course_request.py),
      iOS Course row immediate-apply, Android C++ API only. Refresh
      contract in docs/course-selection.md; 12 wiring tests green;
      Android outer stack rebased + green. Evidence
      local/research/live-apply/ (+ README).
- [x] 2026-09-17 architecture review triage (docs/research/
      review-2026-09-17-architecture.md): all checkable claims verified
      against dumps/tree (M5 pre-Wave-B timestamps + symbols, psq leaves,
      FIFO preprocess bounds, GC-Adapter-Scan thread, SyncGPU default
      false, snow movie-alignment). Acted now: blended-ratio floor in
      validate_trial_trace (+ tests/test_gamecube_schedule_check.py),
      --screenshot-seconds 0 disables capture (+ test), temp-trigger
      removal + stack-green bar in live-apply brief, Odin re-profile
      campaign launched. Validated with no action: generation fix,
      mixer skip, clocks, idle revert. Backlogged: findings 3b, 4
      (affinity), 5 (alpha), 6, 8 (receipts spec; concat disproven),
      10, 11 (frame-exact A/B).
- [x] 2026-09-17 Android trial plumbing (Odin3, on-device EGL): ported
      kind selection, schedule ingestion, receipt/log collection
      (native/diagnostics/android_trial_driver.h + tools/android_trial.py
      build/run/analyze + tests/test_android_trial.py, 12 green). Validated
      full lifecycles on-device: smoothing t3 (253 frames, 22/22 extras
      blended, cancel→Finished 9 ms), F t5 (165 doubled, no movie desync),
      combined t6 (211 doubled + 4 blended). Fixed: movie-layer
      ImmediateXFB override (m3-menu-imm.dtm 1 byte), ~10 s driver/title
      clock lag (AT=124/SECS=4). Trial binary on SSD
      (android-spike/trial/, notes in TRIAL_NOTES.md); receipts
      /tmp/android-trial/t*/. Device left clean.
- [x] 2026-09-17 live-switch spike (desktop): LIVE RE-READ CONFIRMED —
      manifest re-applied mid-menu without reset takes full effect (event 5
      R&B→Aloha: logged re-apply + readback, briefing "Peak 1-Aloha Ice
      Jam", bit-exact Aloha spawn; evidence local/research/live-switch/).
      Displayed menus keep build-time strings (list needs re-entry);
      post-standings fault is the known conversion-side signature.
- [x] 2026-09-17 menu spike (desktop): Tricky tracks menu-selectable with
      the existing manifest — Aloha Ice Jam hosted on event 5 (3-field
      manifest, DOL pin-identical, other 22 rows intact, screenshots in
      local/research/menu-spike/ride-001/screens/). Slot census: 17 runs +
      5 stations live in menus, event 22 vestigial/unlinked; Single Event
      walks a fixed-100B-record nav-graph (guest 0x802C35B0–0x802C4938),
      not the mode table. New entry/peak parked as fixed-table surgery
      (see Now); Aloha-as-slopestyle post-standings fault is
      conversion-side (start-gate suspect), not menu-side.
- [x] 2026-09-17 Vulkan Android headless works on Odin (full speed, one
      dual-backend EGL+Vulkan binary via
      native/patches/recompcore-android-vulkan.patch stacked on
      moderngekko-dolphin-mixer-skip-silent via CORE_STACK;
      tests/test_android_patch_stack.py). Reproduces snow with the same
      character (scorer + eyeball: 0.53→0.92 black-ground progression),
      so snow is backend-independent — redirected to shared
      sampling/shader/TLUT code. Scorer: tools/gamecube_snow_check.py
      (+ tests/test_gamecube_snow_check.py); comparison harness is the
      dual-backend binary.
- [x] 2026-09-16 iPad GPU trace analysis: first Metal System Trace of a
      smoothing trial window (local/reports/gpu-captures/20260917-015031,
      191 MB, trial Finished) plus the per-process extraction recipe
      (`tools/metal_gpu_ms.py`: metal-gpu-intervals xpath export, depth-0
      union per process). Pre-fix baseline on iPad M2 at 1x: GPU 7.65%
      busy over 60.8 s, per-display-frame median 1.255 / p99 1.853 ms
      (fragment-dominated) — ~15–24% of an 8.33 ms 120 Hz budget, so the
      frame budget binds on CPU, not GPU. Post-fix baseline
      (local/reports/gpu-captures/20260917-024156, blending on): GPU 7.89%
      busy, per-frame median 1.436 / p99 1.848 ms — blending costs ~0.2 ms
      median on M2, tail unchanged, still ~17–25% of budget. Combined-kind
      trace (local/reports/gpu-captures/20260917-031834): GPU 7.36% busy,
      median 1.162 / p99 1.760 ms — F doubling adds no GPU cost, as
      expected; 30/30 extras blended with 562 doubled updates.
- [x] 2026-09-12 gc-gari-013: identify the terrain lightmap scale mismatch
      across 108 matched image pairs, add a shared engine material profile,
      preserve source images and conversion receipts, test every RGB565 color,
      and capture the corrected native gameplay. Add reusable isolated draw
      capture/comparison tools; see [material conversion](gamecube-materials.md).
- [x] 2026-09-12: capture original PS2 and GameCube Garibaldi alongside build
      012; preserve a side-by-side gallery and source/hash manifest. This
      confirms remaining color/environment differences, not visual acceptance.
- [x] 2026-09-12: correct global image allocation/capacities, remove obsolete
      host occlusion curtains, and conservatively bound curved terrain. Add
      archive-wide image validation and regression tests. See build findings
      in [the GameCube notes](gamecube-world.md).
- [x] 2026-09-12: reject native test runs with zero native execution, invalid
      memory accesses, or failed code verification.
- [x] 2026-09-11 gc-gari-009: full donor race line on the track chain, gates
      and opponents on Tricky's six start paths, regenerated kind-21 race-line
      table (`tools/race_course.py`); the meter starts near 0% and opponents
      ride the course.
- [x] 2026-09-11 gc-gari-008: Garibaldi's own textures and lightmaps from the
      GameCube Tricky `.gsh` sheets (`tools/gamecube_textures.py`); the race
      rides with zero invalid accesses. September 12 correction: reclamation
      still collided with other locations, and the apparent limit near 800
      was an unexpanded global table. Lightmap correlation supports the same
      cell orientation; the September 12 rendered comparison confirms that
      brightness/color fidelity remains open.
- [x] 2026-09-11 Xbox prompt glyphs: `tools/patch_ui_glyphs.py` repaints the
      B/X/Y icons in the three UI sheets; in-game menu shows green A and blue X.
      Installed on the phone, in the gc-gari-005 disc root and the shared ISO.
      2026-09-15: the hand-installed copy was lost when the phone's container
      was rebuilt, because `provision` copies `files/` from the pristine disc.
      Now re-applied by `provision` itself (`--stock-glyphs` opts out) and
      covered by `tests/test_patch_ui_glyphs.py`.

- [x] 2026-09-11 `tools/build_gc_iso.py` rebuilds a GameCube ISO; stock FST
      reproduced byte for byte.
- [x] 2026-09-11 Touch overlay relabelled to Xbox positions (A bottom, B right,
      X left, Y top, LB/RB).
- [x] 2026-09-11 gc-gari-005: first rideable GameCube Garibaldi (race start,
      ride, restart, zero invalid accesses).
- [x] 2026-09-11 Two-stick touch overlay; right stick drives the D-pad for spins.
- [x] 2026-09-11 PS2-position physical pad mapping with grab translation.
- [x] 2026-09-11 iPhone smoke run at 60 FPS, no JIT.
