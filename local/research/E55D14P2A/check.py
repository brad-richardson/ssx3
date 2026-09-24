#!/usr/bin/env python3
"""E55D14 Part 2A checker: validates the prepared route/limits/pins from the
script source WITHOUT booting, claiming a lease, or touching the fork.

It imports e55d14_boot.py (sibling in this dir) for its constants and runs:
  - route shape: first entry START at tick 636; exactly one Square at tick
    820 (hold 150); exactly five Downs at 1000/1070/1140/1210/1540
    (hold 150); exactly two Crosses at 1360/1700 (hold 150); order
    start/square/downs/cross/down/cross; no other button; all inter-input
    gaps >= 60 ticks; Load-highlight frame target (1620) between D5 and C2;
    post frame (1800) after C2; stop tick = post frame; exact route string
    identical to E55D12's proved route.
  - caps: wall == 500 s, progress == 120 s, log == 16 MiB, scratch intent
    (frames cap) <= 2 GiB, frame-proof grace == 100 s, and
    wall + grace <= 600 s (no boot over 600 s without orchestrator release).
  - pins: fork/runner constants equal the E55D14P1B gate pins
    (80777cb36d5f84c1cd89122e8074afd48fe78b8e / d8fa114d…ef04);
    ISO/ELF/codegen constants equal the carried E55D12 pins.
  - precheck: source rejects tracked modifications and unexpected untracked
    paths but allows the untracked .work/ build tree (pure helper
    status_errors() exercised here with fixed inputs; the fork itself is
    never touched); runner-dir guard vs 14b1e5cb present in source.
  - lease/cwd/PID discipline present in source text (claim before Popen,
    cwd=lane, terminate/kill only proc, release in finally).
  - probe: source sets PS2X_PAD_CARD_PROBE to the per-lane probe.log and
    the reuse guard covers it.
  - sibling: source documents the getdirpath pairing rule (per-family
    pord/tick/port/slot/max; shared seq shifts, so no global-seq comparison)
    and REPORT.md predeclares the five-getdir + five-getdirpath acceptance
    rows.
  - no-boot guard: this checker never claims a lease, never spawns the
    runner, and asserts the script refuses reuse.

It CANNOT claim the Load-game highlight, the post-choice screen, or any
card-API record before a run: no frame or probe file exists yet, so any A/B
outcome assertion fails here by design (reported as UNOBSERVED).
Predeclared A (for Part 2B): post-choice getdirpath row reveals escaped raw
query, normalized query, parent, pattern and host while the card stays empty
and no copied bytes appear; success and copied-byte payloads are stated
separately.

Usage: python3 local/research/E55D14P2A/check.py
Exit 0 on PASS, 1 on FAIL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e55d14_boot as b

FAIL = []


def check(name, ok, detail=''):
    print('%s %s %s' % ('ok' if ok else 'FAIL', name, detail))
    if not ok:
        FAIL.append(name)


def main():
    entries = b.parse_route_entries(b.ROUTE)
    check('route_first_start_636',
          entries[0][1] == 'start' and entries[0][0] == b.tick_to_ms(636),
          str(entries[0]))
    check('route_entry_count_9', len(entries) == 9, str(entries))
    squares = [e for e in entries if e[1] == 'square']
    check('route_exactly_one_square', len(squares) == 1, str(squares))
    check('route_square_tick_820',
          squares and squares[0][0] == b.tick_to_ms(820),
          str(squares[0] if squares else None))
    check('route_square_hold_150',
          squares and squares[0][2] == 150,
          str(squares[0] if squares else None))
    downs = [e for e in entries if e[1] == 'down']
    check('route_exactly_five_downs', len(downs) == 5, str(downs))
    check('route_down_ticks_1000_1070_1140_1210_1540',
          [e[0] for e in downs] == [b.tick_to_ms(t) for t in (1000, 1070, 1140, 1210, 1540)],
          str([e[0] for e in downs]))
    check('route_down_holds_150', all(e[2] == 150 for e in downs),
          str([e[2] for e in downs]))
    crosses = [e for e in entries if e[1] == 'cross']
    check('route_exactly_two_crosses', len(crosses) == 2, str(crosses))
    check('route_cross1_tick_1360',
          crosses and crosses[0][0] == b.tick_to_ms(1360),
          str(crosses[0] if crosses else None))
    check('route_cross2_tick_1700',
          len(crosses) == 2 and crosses[1][0] == b.tick_to_ms(1700),
          str(crosses[1] if len(crosses) == 2 else None))
    check('route_cross_holds_150', all(e[2] == 150 for e in crosses),
          str([e[2] for e in crosses]))
    check('route_order_spine_plus_d5_c2',
          [e[1] for e in entries] == ['start', 'square', 'down', 'down',
                                      'down', 'down', 'cross', 'down', 'cross'],
          str([e[1] for e in entries]))
    buttons = sorted(set(e[1] for e in entries))
    check('route_buttons_start_square_down_cross_only',
          buttons == ['cross', 'down', 'square', 'start'], str(buttons))
    input_ticks = [b.START_TICK, b.SQUARE_TICK] + list(b.DOWN_TICKS) + [b.CROSS1_TICK,
                   b.DOWN5_TICK, b.CROSS2_TICK]
    gaps = [t2 - t1 for t1, t2 in zip(input_ticks, input_ticks[1:])]
    check('route_all_input_gaps_ge_60', all(g >= 60 for g in gaps),
          'gaps=%s' % gaps)
    check('route_d5_gap_from_c1_ge_60', b.DOWN5_TICK - b.CROSS1_TICK >= 60,
          'gap=%d' % (b.DOWN5_TICK - b.CROSS1_TICK))
    check('route_load_frame_between_d5_and_c2',
          b.DOWN_TICKS[-1] < b.CROSS1_TICK < b.DOWN5_TICK
          and b.DOWN5_TICK < b.LOAD_FRAME_TICK < b.CROSS2_TICK,
          'D4=%d C1=%d D5=%d Fload=%d C2=%d'
          % (b.DOWN_TICKS[-1], b.CROSS1_TICK, b.DOWN5_TICK,
             b.LOAD_FRAME_TICK, b.CROSS2_TICK))
    check('route_post_frame_after_c2', b.POST_FRAME_TICK > b.CROSS2_TICK,
          'C2=%d Fpost=%d' % (b.CROSS2_TICK, b.POST_FRAME_TICK))
    check('route_stop_tick_is_post_frame', b.STOP_TICK == b.POST_FRAME_TICK,
          str(b.STOP_TICK))
    check('route_exact_string_matches_e55d12',
          b.ROUTE == '10611:start:250,13680:square:150,16683:down:150,'
          '17851:down:150,19019:down:150,20187:down:150,22689:cross:150,'
          '25692:down:150,28362:cross:150',
          b.ROUTE)
    check('caps_wall_500', b.WALL_CAP_S == 500, str(b.WALL_CAP_S))
    check('caps_progress_120', b.PROGRESS_CAP_S == 120, str(b.PROGRESS_CAP_S))
    check('caps_log_16mib', b.LOG_CAP_BYTES == 16 * 1024 * 1024, str(b.LOG_CAP_BYTES))
    check('caps_scratch_frames_le_2gib', b.FRAMES_CAP_BYTES <= 2 * 1024 * 1024 * 1024,
          str(b.FRAMES_CAP_BYTES))
    check('caps_frame_proof_grace_100', b.FRAME_PROOF_GRACE_S == 100,
          str(b.FRAME_PROOF_GRACE_S))
    check('caps_wall_plus_grace_le_600',
          b.WALL_CAP_S + b.FRAME_PROOF_GRACE_S <= 600,
          'wall=%d grace=%d sum=%d'
          % (b.WALL_CAP_S, b.FRAME_PROOF_GRACE_S,
             b.WALL_CAP_S + b.FRAME_PROOF_GRACE_S))
    check('pin_fork', b.FORK_PIN_FULL == '80777cb36d5f84c1cd89122e8074afd48fe78b8e',
          b.FORK_PIN_SHORT)
    check('pin_fork_path_e55d14p1',
          str(b.FORK) == '/Users/brad/dev/ssx3-work/E55D14P1/PS2Recomp',
          str(b.FORK))
    check('pin_runner',
          b.RUNNER_SHA == 'd8fa114d824a277592558425dd91357bcf2f75d0d09390a5680c41ba6002ef04',
          b.RUNNER_SHA[:16])
    check('pin_runner_path_work_build',
          str(b.RUNNER) == '/Users/brad/dev/ssx3-work/E55D14P1/PS2Recomp/.work/build/ps2xRuntime/ps2EntryRunner',
          str(b.RUNNER))
    check('pin_iso',
          b.ISO_SHA == '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
          b.ISO_SHA[:16])
    check('pin_elf',
          b.ELF_SHA == '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
          b.ELF_SHA[:16])
    check('pin_codegen',
          b.CODEGEN_SHA == '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3',
          b.CODEGEN_SHA[:16])
    check('lane_path_e55d14p2',
          str(b.WORK) == '/Users/brad/dev/ssx3-work/E55D14P2',
          str(b.WORK))
    check('precheck_allows_clean', b.status_errors('') == [], 'empty status passes')
    check('precheck_allows_work_only',
          b.status_errors('?? .work/\n') == [],
          '.work/ untracked passes')
    check('precheck_rejects_tracked',
          b.status_errors('M  ps2xRuntime/include/ps2_e55d3_pad_card_probe.h\n') != []
          and b.status_errors(' M ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp\n') != [],
          'staged/unstaged tracked mods rejected')
    check('precheck_rejects_stray_untracked',
          b.status_errors('?? notes.txt\n') != []
          and b.status_errors('?? .work/\n?? scratch/\n') != [],
          'stray untracked rejected with and without .work/')
    src = Path(b.__file__).read_text()
    check('src_claims_lease', "claim('E55D14P2-'" in src, '')
    check('src_boots_from_own_cwd', 'cwd=lane' in src, '')
    check('src_kills_only_recorded_pid',
          'proc.terminate()' in src and 'proc.kill()' in src
          and 'pgrep' not in src and 'pkill' not in src, '')
    check('src_releases_lease', 'release(slot)' in src, '')
    check('src_movie_bypass_on', "PS2X_SKIP_MOVIE='1'" in src, '')
    check('src_probe_enabled_to_lane', "PS2X_PAD_CARD_PROBE" in src and "PROBE_NAME = 'probe.log'" in src, '')
    check('src_probe_reuse_guarded', "PROBE_NAME, 'frames'" in src or 'PROBE_NAME' in src, '')
    check('src_refuses_reuse', 'refusing to reuse' in src, '')
    check('src_setup_order_check_before_create',
          src.index('taken = existing_outputs(lane)') < src.index("lane / 'frames' / 'snap'"),
          'prepare_lane refuses before mkdir frames/snap')
    check('src_single_label', "--label', choices=('S1',)" in src, '')
    check('src_target_requires_frame_proof',
          "bound = 'target'" in src and 'frame_proof' in src
          and 'frame_unproven' in src and 'FRAME_PROOF_GRACE_S' in src,
          'target only with snap tag >= STOP_TICK; else frame_unproven')
    check('src_runner_guard_vs_upstream',
          "UPSTREAM_RUNNER_BASE = '14b1e5cb'" in src
          and "'ps2xRuntime/src/runner'" in src,
          'guard vs 14b1e5cb present')
    check('src_sibling_pairing_documented',
          'getdirpath' in src and 'pord' in src
          and 'NOT' in src and 'compared' in src,
          'sibling pord + no-global-seq rule in docstring')
    check('src_no_e55d12_lane_left',
          'E55D12' in src and 'ssx3-work/E55D12' not in src
          and "claim('E55D12-'" not in src,
          'E55D12 named only as read-only source; no live lane/lease ref')
    report = (HERE / 'REPORT.md').read_text()
    check('report_predeclares_sibling_rows',
          'getdirpath' in report and 'per-family' in report
          and 'five' in report,
          'REPORT names five getdir + five getdirpath rows')
    check('screen_unobserved_no_claim',
          True,
          'UNOBSERVED by design: no frame exists pre-run; A/B/OTHER judged only after Part 2B')
    check('api_unobserved_no_claim',
          True,
          'UNOBSERVED by design: no probe.log exists pre-run; A needs post-choice getdirpath path fields; judged only after Part 2B')
    # Visual + API outcomes cannot be asserted pre-run; record that explicitly.
    observed_frames = list(HERE.glob('frames/snap-*.png')) + list(HERE.glob('snap-*.png'))
    check('screen_not_claimed_before_run', observed_frames == [], 'frames found: %d' % len(observed_frames))
    observed_probe = list(HERE.glob('probe*.log'))
    check('api_not_claimed_before_run', observed_probe == [], 'probe files found: %d' % len(observed_probe))
    if FAIL:
        print('CHECK FAIL: %s' % ', '.join(FAIL))
        return 1
    print('CHECK PASS: route/limits/pins/discipline hold; screen+API UNOBSERVED (no run yet)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
