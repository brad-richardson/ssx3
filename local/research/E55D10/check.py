#!/usr/bin/env python3
"""E55D10 Part 1 checker: validates the prepared route/limits/pins from the
script source WITHOUT booting, claiming a lease, or touching the fork.

It imports e55d10_boot.py (sibling in this dir) for its constants and runs:
  - route shape: first entry START at tick 636; exactly one Square at tick
    820 (hold 150); no Down, no Cross, no other button; menu frame (760)
    before Square; post frame (920) after Square; stop tick = post frame.
  - caps: wall == 500 s, progress == 120 s, log == 16 MiB, scratch intent
    (frames cap) <= 2 GiB, frame-proof grace == 120 s.
  - pins: fork/runner/ISO/ELF/codegen constants equal the E55D3/E55D9 pins.
  - lease/cwd/PID discipline present in source text (claim before Popen,
    cwd=lane, terminate/kill only proc, release in finally).
  - no-boot guard: this checker never claims a lease, never spawns the
    runner, and asserts the script refuses reuse.

It CANNOT claim the post-Square screen before a run: no frame exists yet,
so any A/B outcome assertion fails here by design (reported as UNOBSERVED).

Usage: python3 local/research/E55D10/check.py
Exit 0 on PASS, 1 on FAIL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e55d10_boot as b

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
    check('route_entry_count_2', len(entries) == 2, str(entries))
    squares = [e for e in entries if e[1] == 'square']
    check('route_exactly_one_square', len(squares) == 1, str(squares))
    check('route_square_tick_820',
          squares and squares[0][0] == b.tick_to_ms(820),
          str(squares[0] if squares else None))
    check('route_square_hold_150',
          squares and squares[0][2] == 150,
          str(squares[0] if squares else None))
    buttons = sorted(set(e[1] for e in entries))
    check('route_buttons_start_square_only', buttons == ['square', 'start'], str(buttons))
    check('route_no_cross', all(e[1] != 'cross' for e in entries), '')
    check('route_no_down', all(e[1] != 'down' for e in entries), '')
    check('route_menu_frame_before_square', b.MENU_FRAME_TICK < b.SQUARE_TICK,
          'F0=%d S=%d' % (b.MENU_FRAME_TICK, b.SQUARE_TICK))
    check('route_post_frame_after_square', b.POST_FRAME_TICK > b.SQUARE_TICK,
          'S=%d F1=%d' % (b.SQUARE_TICK, b.POST_FRAME_TICK))
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
    check('src_claims_lease', "claim('E55D10-'" in src, '')
    check('src_boots_from_own_cwd', 'cwd=lane' in src, '')
    check('src_kills_only_recorded_pid',
          'proc.terminate()' in src and 'proc.kill()' in src
          and 'pgrep' not in src and 'pkill' not in src, '')
    check('src_releases_lease', 'release(slot)' in src, '')
    check('src_movie_bypass_on', "PS2X_SKIP_MOVIE='1'" in src, '')
    check('src_no_pad_card_probe', 'PS2X_PAD_CARD_PROBE' not in src, '')
    check('src_no_cross_in_route_source', True, 'covered by route_no_cross')
    check('src_no_down_in_route_source', True, 'covered by route_no_down')
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
    # A/B outcome cannot be asserted pre-run; record that explicitly.
    observed = list(HERE.glob('frames/snap-*.png')) + list(HERE.glob('snap-*.png'))
    check('screen_not_claimed_before_run', observed == [], 'frames found: %d' % len(observed))
    if FAIL:
        print('CHECK FAIL: %s' % ', '.join(FAIL))
        return 1
    print('CHECK PASS: route/limits/pins/discipline hold; screen UNOBSERVED (no run yet)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
