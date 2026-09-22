#!/usr/bin/env python3
# G41-R1: repair hunk on the R0-applied tree (Mac-diagnosed, pre-device).
# (a) Kick-time composite register snapshot (C5 fix: live regs at flush-end
#     already belong to the next pass; R0's C5 ran scene state PSM0/MSK0).
# (b) State-dump logging (ofx/ofy, scissor cache, dirty, sampling, key regs)
#     at every cord-join + canary edges (names the ford=3 clip poison word).
# (c) Hygiene restores (potential_feedback, parallelogram order).
# Usage: g41-r1-apply.py [--dry] <clone>. Asserts every anchor exactly once.
# ORDER: E7 before E8 (overlapping anchors). Single write.
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

# ---- E0. R1 statics (after the R0 statics, before the ctor) ----
R1_STATICS = """// G41-R1: kick-time composite register snapshot (C5 replays the composite's
// exact draw state; live regs at flush-end already belong to the next pass).
static RegisterState g41_snap_regs = {};
static bool g41_snap_valid = false;
"""

e0_anchor = '\t\tnz += p[i] != 0;\n\t}\n}\nGSInterface::GSInterface()\n'
e0_repl = '\t\tnz += p[i] != 0;\n\t}\n}\n' + R1_STATICS + 'GSInterface::GSInterface()\n'

# ---- E1. snapshot hook at the top of drawing_kick_append ----
R1_HOOK = """\tif (g41_enabled() && ctx.frame.desc.FBP == 112)
\t{
\t\tg41_snap_regs = registers;
\t\tg41_snap_valid = true;
\t}
"""

e1_anchor = ('void GSInterface::drawing_kick_append()\n{\n'
             '\tauto &prim = registers.prim;\n'
             '\tauto &ctx = registers.ctx[prim.desc.CTXT];\n')
e1_repl = e1_anchor + R1_HOOK

# ---- E2. state-dump lambda (after the g41_fire decl) ----
R1_LAMBDA = """\t\t\tauto g41_dump_state = [this](const char *g41_tag, int g41_cord_tag) {
\t\t\t\tLOGI("G41: st %s cord=%d ofx=%d ofy=%d scilo=%d,%d scihi=%d,%d scixfb=%d wrap=%u dirty=%08x ss=%u,%u prim=%016llx frame0=%016llx scis0=%016llx xyof0=%016llx test0=%016llx zbuf0=%016llx tex0_0=%016llx alpha0=%016llx ac=%u.\\n",
\t\t\t\t     g41_tag, g41_cord_tag,
\t\t\t\t     render_pass.ofx, render_pass.ofy,
\t\t\t\t     render_pass.scissor_lo.x, render_pass.scissor_lo.y,
\t\t\t\t     render_pass.scissor_hi.x, render_pass.scissor_hi.y,
\t\t\t\t     render_pass.scissor_hi_x_fb, (unsigned)render_pass.can_fb_wraparound,
\t\t\t\t     (unsigned)state_tracker.dirty_flags,
\t\t\t\t     sampling_rate_x_log2, sampling_rate_y_log2,
\t\t\t\t     (unsigned long long)registers.prim.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].frame.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].scissor.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].xyoffset.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].test.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].zbuf.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].tex0.bits,
\t\t\t\t     (unsigned long long)registers.ctx[0].alpha.bits,
\t\t\t\t     (unsigned)registers.prmodecont.desc.AC);
\t\t\t};
"""

e2_anchor = '\t\t\tint g41_fire = g40_outer ? g40_cord : g41_cord;\n'
e2_repl = e2_anchor + R1_LAMBDA

# ---- E3. cord-join call (after the cord LOGI) ----
e3_anchor = ('\t\t\tLOGI("G41: cord g41=%d g40=%d ford=%u prims=%u tex=%u.\\n",\n'
             '\t\t\t     g41_cord, g40_cord, g41_ford, g41_entry_prims, g41_tex_count);\n')
e3_repl = e3_anchor + '\t\t\tg41_dump_state("cord", g41_fire);\n'

# ---- E4. canary-start call + hygiene saves ----
e4_anchor = '\t\t\t\t\tStateTracker g41_saved_st = state_tracker;\n'
e4_repl = (e4_anchor
           + '\t\t\t\t\tauto g41_saved_pf = render_pass.potential_feedback;\n'
           + '\t\t\t\t\tauto g41_saved_porder = render_pass.last_triangle_parallelogram_order;\n'
           + '\t\t\t\t\tg41_dump_state("cstart", 1);\n')

# ---- E5. canary-end call + hygiene restores ----
e5_anchor = '\t\t\t\t\tstate_tracker = g41_saved_st;\n'
e5_repl = (e5_anchor
           + '\t\t\t\t\trender_pass.potential_feedback = g41_saved_pf;\n'
           + '\t\t\t\t\trender_pass.last_triangle_parallelogram_order = g41_saved_porder;\n'
           + '\t\t\t\t\tg41_dump_state("cend", 1);\n')

# ---- E6. g41_void decl (before the per-cell setup if/else) ----
e6_anchor = '\t\t\t\t\t\tif (!g41_c5)\n'
e6_repl = '\t\t\t\t\t\tbool g41_void = false;\n' + e6_anchor

# ---- E7. void skip (before the per-cell reset_vertex_queue; BEFORE E8) ----
e7_anchor = ('\t\t\t\t\t\t\t     (unsigned long long)g41_s_pabe);\n'
             '\t\t\t\t\t\t}\n'
             '\t\t\t\t\t\treset_vertex_queue();\n')
e7_repl = ('\t\t\t\t\t\t\t     (unsigned long long)g41_s_pabe);\n'
           '\t\t\t\t\t\t}\n'
           '\t\t\t\t\t\tif (g41_void) continue;\n'
           '\t\t\t\t\t\treset_vertex_queue();\n')

# ---- E8. C5 setup from the kick-time snapshot (replaces live-reg setup) ----
e8_anchor = """\t\t\t\t\t\telse
\t\t\t\t\t\t{
\t\t\t\t\t\t\tReg64<FRAMEBits> g41_f;
\t\t\t\t\t\t\tg41_f.bits = g41_s_frame;
\t\t\t\t\t\t\tg41_f.desc.FBP = g41_fbp[g41_cell];
\t\t\t\t\t\t\twrite_register(g41_a_frame, g41_f.bits);
\t\t\t\t\t\t\twrite_register(g41_a_xyof, uint64_t(0));
\t\t\t\t\t\t\tReg64<SCISSORBits> g41_sc;
\t\t\t\t\t\t\tg41_sc.bits = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAX0 = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAY0 = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAX1 = 63;
\t\t\t\t\t\t\tg41_sc.desc.SCAY1 = 63;
\t\t\t\t\t\t\twrite_register(g41_a_scis, g41_sc.bits);
\t\t\t\t\t\t\tReg64<RGBAQBits> g41_rq;
\t\t\t\t\t\t\tg41_rq.bits = g41_s_rgbaq;
\t\t\t\t\t\t\tg41_rq.desc.Q = 1.0f;
\t\t\t\t\t\t\twrite_register(RegisterAddr::RGBAQ, g41_rq.bits);
\t\t\t\t\t\t\tLOGI("G41: C5 live prim=%016llx test=%016llx zbuf=%016llx tex0=%016llx alpha=%016llx fba=%016llx pabe=%016llx.\\n",
\t\t\t\t\t\t\t     (unsigned long long)g41_s_prim,
\t\t\t\t\t\t\t     (unsigned long long)g41_s_test,
\t\t\t\t\t\t\t     (unsigned long long)g41_s_zbuf,
\t\t\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].tex0.bits,
\t\t\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].alpha.bits,
\t\t\t\t\t\t\t     (unsigned long long)g41_s_fba,
\t\t\t\t\t\t\t     (unsigned long long)g41_s_pabe);
\t\t\t\t\t\t}
"""

R1_C5 = """\t\t\t\t\t\telse
\t\t\t\t\t\t{
\t\t\t\t\t\t\t// G41-R1: C5 replays the composite's kick-time
\t\t\t\t\t\t\t// registers (last FBP112 append), redirected to
\t\t\t\t\t\t\t// scratch (FBP) + fixed geometry.
\t\t\t\t\t\t\tunsigned g41_sctx = g41_snap_regs.prim.desc.CTXT & 1;
\t\t\t\t\t\t\tif (!g41_snap_valid)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tLOGI("G41: C5 NO-SNAPSHOT (void).\\n");
\t\t\t\t\t\t\t\tg41_void = true;
\t\t\t\t\t\t\t}
\t\t\t\t\t\t\telse if (g41_sctx != g41_lctx)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tLOGI("G41: C5 ctxt-mismatch snap=%u live=%u (void).\\n", g41_sctx, g41_lctx);
\t\t\t\t\t\t\t\tg41_void = true;
\t\t\t\t\t\t\t}
\t\t\t\t\t\t\telse
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tconst RegisterState &g41_src = g41_snap_regs;
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::PRIM, g41_src.prim.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::PRMODE, g41_src.prim.bits);
\t\t\t\t\t\t\t\tReg64<RGBAQBits> g41_rq;
\t\t\t\t\t\t\t\tg41_rq.bits = g41_src.rgbaq.bits;
\t\t\t\t\t\t\t\tg41_rq.desc.Q = 1.0f;
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::RGBAQ, g41_rq.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::ST, g41_src.st.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::UV, g41_src.uv.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::FOG, g41_src.fog.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::PRMODECONT, g41_src.prmodecont.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::TEXCLUT, g41_src.texclut.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::TEXA, g41_src.texa.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::FOGCOL, g41_src.fogcol.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::DIMX, g41_src.dimx.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::DTHE, g41_src.dthe.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::COLCLAMP, g41_src.colclamp.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::PABE, g41_src.pabe.bits);
\t\t\t\t\t\t\t\twrite_register(RegisterAddr::SCANMSK, g41_src.scanmsk.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::TEX0_2 : RegisterAddr::TEX0_1, g41_src.ctx[g41_sctx].tex0.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::TEX1_2 : RegisterAddr::TEX1_1, g41_src.ctx[g41_sctx].tex1.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::CLAMP_2 : RegisterAddr::CLAMP_1, g41_src.ctx[g41_sctx].clamp.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::MIPTBP1_2 : RegisterAddr::MIPTBP1_1, g41_src.ctx[g41_sctx].miptbl_1_3.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::MIPTBP2_2 : RegisterAddr::MIPTBP2_1, g41_src.ctx[g41_sctx].miptbl_4_6.bits);
\t\t\t\t\t\t\t\twrite_register(g41_sctx ? RegisterAddr::ALPHA_2 : RegisterAddr::ALPHA_1, g41_src.ctx[g41_sctx].alpha.bits);
\t\t\t\t\t\t\t\twrite_register(g41_a_test, g41_src.ctx[g41_sctx].test.bits);
\t\t\t\t\t\t\t\twrite_register(g41_a_fba, g41_src.ctx[g41_sctx].fba.bits);
\t\t\t\t\t\t\t\tReg64<FRAMEBits> g41_f;
\t\t\t\t\t\t\t\tg41_f.bits = g41_src.ctx[g41_sctx].frame.bits;
\t\t\t\t\t\t\t\tg41_f.desc.FBP = g41_fbp[g41_cell];
\t\t\t\t\t\t\t\twrite_register(g41_a_frame, g41_f.bits);
\t\t\t\t\t\t\t\twrite_register(g41_a_zbuf, g41_src.ctx[g41_sctx].zbuf.bits);
\t\t\t\t\t\t\t\twrite_register(g41_a_xyof, uint64_t(0));
\t\t\t\t\t\t\t\tReg64<SCISSORBits> g41_sc;
\t\t\t\t\t\t\t\tg41_sc.bits = 0;
\t\t\t\t\t\t\t\tg41_sc.desc.SCAX0 = 0;
\t\t\t\t\t\t\t\tg41_sc.desc.SCAY0 = 0;
\t\t\t\t\t\t\t\tg41_sc.desc.SCAX1 = 63;
\t\t\t\t\t\t\t\tg41_sc.desc.SCAY1 = 63;
\t\t\t\t\t\t\t\twrite_register(g41_a_scis, g41_sc.bits);
\t\t\t\t\t\t\t\tLOGI("G41: C5 snap prim=%016llx frame=%016llx test=%016llx zbuf=%016llx tex0=%016llx alpha=%016llx fba=%016llx pabe=%016llx.\\n",
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.prim.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].frame.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].test.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].zbuf.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].tex0.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].alpha.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.ctx[g41_sctx].fba.bits,
\t\t\t\t\t\t\t\t     (unsigned long long)g41_src.pabe.bits);
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
"""

# ---- E9. whole-register live copy (for the C5 extra restore) ----
e9_anchor = '\t\t\t\t\t\tuint64_t g41_s_pabe = registers.pabe.bits;\n'
e9_repl = e9_anchor + '\t\t\t\t\t\tRegisterState g41_live_all = registers;\n'

# ---- E10. C5 extra restore (before the shared restore) ----
R1_C5RESTORE = """\t\t\t\t\t\tif (g41_c5 && !g41_void)
\t\t\t\t\t\t{
\t\t\t\t\t\t\twrite_register(RegisterAddr::FOG, g41_live_all.fog.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::PRMODECONT, g41_live_all.prmodecont.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::TEXCLUT, g41_live_all.texclut.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::TEXA, g41_live_all.texa.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::FOGCOL, g41_live_all.fogcol.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::DIMX, g41_live_all.dimx.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::DTHE, g41_live_all.dthe.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::COLCLAMP, g41_live_all.colclamp.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::SCANMSK, g41_live_all.scanmsk.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::TEX0_2 : RegisterAddr::TEX0_1, g41_live_all.ctx[g41_lctx].tex0.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::TEX1_2 : RegisterAddr::TEX1_1, g41_live_all.ctx[g41_lctx].tex1.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::CLAMP_2 : RegisterAddr::CLAMP_1, g41_live_all.ctx[g41_lctx].clamp.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::MIPTBP1_2 : RegisterAddr::MIPTBP1_1, g41_live_all.ctx[g41_lctx].miptbl_1_3.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::MIPTBP2_2 : RegisterAddr::MIPTBP2_1, g41_live_all.ctx[g41_lctx].miptbl_4_6.bits);
\t\t\t\t\t\t\twrite_register(g41_lctx ? RegisterAddr::ALPHA_2 : RegisterAddr::ALPHA_1, g41_live_all.ctx[g41_lctx].alpha.bits);
\t\t\t\t\t\t}
"""

e10_anchor = '\t\t\t\t\t\twrite_register(g41_a_frame, g41_s_frame);\n'
e10_repl = R1_C5RESTORE + e10_anchor

# ORDER: E7 before E8 (overlapping anchors).
n = 0
n += edit(IFACE, [(e0_anchor, e0_repl)])
n += edit(IFACE, [(e1_anchor, e1_repl)])
n += edit(IFACE, [(e2_anchor, e2_repl)])
n += edit(IFACE, [(e3_anchor, e3_repl)])
n += edit(IFACE, [(e4_anchor, e4_repl)])
n += edit(IFACE, [(e5_anchor, e5_repl)])
n += edit(IFACE, [(e6_anchor, e6_repl)])
n += edit(IFACE, [(e7_anchor, e7_repl)])
n += edit(IFACE, [(e8_anchor, R1_C5)])
n += edit(IFACE, [(e9_anchor, e9_repl)])
n += edit(IFACE, [(e10_anchor, e10_repl)])
print(("DRY-OK " if DRY else "APPLIED ") + str(n) + " edits")
