#!/usr/bin/env python3
# G41-R2: repair the ford=3 clip poison (Mac-diagnosed via R1 cend-dump:
# scissor cache (63,63) stale, everything else live). Root cause: the
# resumed trigger-kick (scene#2 q1) consumed SCISSOR_BIT pre-flush (cache
# recomputed from live regs), suspended inside check_frame_buffer_state,
# and resumes post-canary WITHOUT recomputing (already consumed) -- so it
# uses the canary's (63,63) cache for its prim, and the strip cascade
# rejects the rest (bb=198). Fix: save/restore the 4 scissor-cache words
# directly (struct assign), bypassing the handler round-trip. ofx/ofy are
# proven clean by the cend-dump (handler round-trip works); untouched.
# Usage: g41-r2-apply.py [--dry] <clone>. Anchors exact-once. Single write.
import sys

DRY = len(sys.argv) > 1 and sys.argv[1] == "--dry"
CLONE = sys.argv[2] if DRY else sys.argv[1]


def edit(path, pairs):
    with open(path, "r") as f:
        src = f.read()
    for i, (find, repl) in enumerate(pairs):
        n = src.count(find)
        assert n == 1, "%s edit%d: anchor x%d, want x1:\n%s" % (path, i, n, find[:220])
        src = src.replace(find, repl, 1)
    if not DRY:
        with open(path, "w") as f:
            f.write(src)
    return len(pairs)


IFACE = CLONE + "/gs/gs_interface.cpp"

e0_anchor = '\t\t\t\t\tauto g41_saved_porder = render_pass.last_triangle_parallelogram_order;\n'
e0_repl = (e0_anchor
           + '\t\t\t\t\tivec2 g41_saved_scilo = render_pass.scissor_lo;\n'
           + '\t\t\t\t\tivec2 g41_saved_scihi = render_pass.scissor_hi;\n'
           + '\t\t\t\t\tint g41_saved_scixfb = render_pass.scissor_hi_x_fb;\n'
           + '\t\t\t\t\tbool g41_saved_wrap = render_pass.can_fb_wraparound;\n')

e1_anchor = '\t\t\t\t\trender_pass.last_triangle_parallelogram_order = g41_saved_porder;\n'
e1_repl = (e1_anchor
           + '\t\t\t\t\trender_pass.scissor_lo = g41_saved_scilo;\n'
           + '\t\t\t\t\trender_pass.scissor_hi = g41_saved_scihi;\n'
           + '\t\t\t\t\trender_pass.scissor_hi_x_fb = g41_saved_scixfb;\n'
           + '\t\t\t\t\trender_pass.can_fb_wraparound = g41_saved_wrap;\n')

n = 0
n += edit(IFACE, [(e0_anchor, e0_repl)])
n += edit(IFACE, [(e1_anchor, e1_repl)])
print(("DRY-OK " if DRY else "APPLIED ") + str(n) + " edits")
