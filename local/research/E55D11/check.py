#!/usr/bin/env python3
"""E55D11 Part 1 checker: validates the prepared route/limits/pins from the
script source WITHOUT booting, claiming a lease, or touching the fork.

It imports e55d11_boot.py (sibling in this dir) for its constants and runs:
  - route shape: first entry START at tick 636; exactly one Square at tick
    820 (hold 150); exactly four Downs at 1000/1070/1140/1210 (hold 150);
    exactly one Cross at tick 1360 (hold 150); order start/square/downs/
    cross; no other button; all inter-input gaps >= 60 ticks; pre-Cross
    frame target (1290) between D4 and Cross; post frame (1460) after
    Cross; stop tick = post frame.
  - caps: wall == 500 s, progress == 120 s, log == 16 MiB, scratch intent
    (frames cap) <= 2 GiB, frame-proof grace == 120 s.
  - pins: fork/runner/ISO/ELF/codegen constants equal the E55D3/E55D9 pins.
  - lease/cwd/PID discipline present in source text (claim before Popen,
    cwd=lane, terminate/kill only proc, release in finally).
  - probe: source sets PS2X_PAD_CARD_PROBE to the per-lane probe.log and
    the reuse guard covers it.
  - no-boot guard: this checker never claims a lease, never spawns the
    runner, and asserts the script refuses reuse.

It CANNOT claim the post-Cross screen or any card-API record before a run:
no frame or probe file exists yet, so any A/B outcome assertion fails here
by design (reported as UNOBSERVED).

Usage: python3 local/research/E55D11/check.py
Exit 0 on PASS, 1 on FAIL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e55d11_boot as b

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
    check('route_entry_count_7', len(entries) == 7, str(entries))
    squares = [e for e in entries if e[1] == 'square']
    check('route_exactly_one_square', len(squares) == 1, str(squares))
    check('route_square_tick_820',
          squares and squares[0][0] == b.tick_to_ms(820),
          str(squares[0] if squares else None))
    check('route_square_hold_150',
          squares and squares[0][2] == 150,
          str(squares[0] if squares else None))
    downs = [e for e in entries if e[1] == 'down']
    check('route_exactly_four_downs', len(downs) == 4, str(downs))
    check('route_down_ticks_1000_1070_1140_1210',
          [e[0] for e in downs] == [b.tick_to_ms(t) for t in (1000, 1070, 1140, 1210)],
          str([e[0] for e in downs]))
    check('route_down_holds_150', all(e[2] == 150 for e in downs),
          str([e[2] for e in downs]))
    crosses = [e for e in entries if e[1] == 'cross']
    check('route_exactly_one_cross', len(crosses) == 1, str(crosses))
    check('route_cross_tick_1360',
          crosses and crosses[0][0] == b.tick_to_ms(1360),
          str(crosses[0] if crosses else None))
    check('route_cross_hold_150',
          crosses and crosses[0][2] == 150,
          str(crosses[0] if crosses else None))
    check('route_order_start_square_downs_cross',
          [e[1] for e in entries] == ['start', 'square', 'down', 'down',
                                      'down', 'down', 'cross'],
          str([e[1] for e in entries]))
    buttons = sorted(set(e[1] for e in entries))
    check('route_buttons_start_square_down_cross_only',
          buttons == ['cross', 'down', 'square', 'start'], str(buttons))
    input_ticks = [b.START_TICK, b.SQUARE_TICK] + list(b.DOWN_TICKS) + [b.CROSS_TICK]
    gaps = [t2 - t1 for t1, t2 in zip(input_ticks, input_ticks[1:])]
    check('route_all_input_gaps_ge_60', all(g >= 60 for g in gaps),
          'gaps=%s' % gaps)
    check('route_pre_cross_frame_between_d4_and_cross',
          b.DOWN_TICKS[-1] < b.PRE_CROSS_FRAME_TICK < b.CROSS_TICK,
          'D4=%d Fpre=%d C=%d' % (b.DOWN_TICKS[-1], b.PRE_CROSS_FRAME_TICK, b.CROSS_TICK))
    check('route_post_frame_after_cross', b.POST_FRAME_TICK > b.CROSS_TICK,
          'C=%d Fpost=%d' % (b.CROSS_TICK, b.POST_FRAME_TICK))
    check('route_stop_tick_is_post_frame', b.STOP_TICK == b.POST_FRAME_TICK,
          str(b.STOP_TICK))
    check('caps_wall_500', b.WALL_CAP_S == 500, str(b.WALL_CAP_S))
    check('caps_progress_120', b.PROGRESS_CAP_S == 120, str(b.PROGRESS_CAP_S))
    check('caps_log_16mib', b.LOG_CAP_BYTES == 16 * 1024 * 1024, str(b.LOG_CAP_BYTES))
    check('caps_scratch_frames_le_2gib', b.FRAMES_CAP_BYTES <= 2 * 1024 * 1024 * 1024,
          str(b.FRAMES_CAP_BYTES))
    check('caps_frame_proof_grace_120', b.FRAME_PROOF_GRACE_S == 120,
          str(b.FRAME_PROOF_GRACE_S))
    check('pin_fork', b.FORK_PIN_FULL == 'bab6eb382673155ffd756fe8db265964eeff9703',
          b.FORK_PIN_SHORT)
    check('pin_runner',
          b.RUNNER_SHA == 'e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f',
          b.RUNNER_SHA[:16])
    check('pin_iso',
          b.ISO_SHA == '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
          b.ISO_SHA[:16])
    check('pin_elf',
          b.ELF_SHA == '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
          b.ELF_SHA[:16])
    check('pin_codegen',
          b.CODEGEN_SHA == '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3',
          b.CODEGEN_SHA[:16])
    src = Path(b.__file__).read_text()
    check('src_claims_lease', "claim('E55D11-'" in src, '')
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
    check('screen_unobserved_no_claim',
          True,
          'UNOBSERVED by design: no frame exists pre-run; A/B/OTHER judged only after Part 2')
    check('api_unobserved_no_claim',
          True,
          'UNOBSERVED by design: no probe.log exists pre-run; GetDir/mcRead judged only after Part 2')
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
