#!/usr/bin/env python3
# G41: apply the ONE masked-write canary hunk (census + hash breakdown +
# C1..C5 scratch-arena sprites with per-cell save/restore).
# Usage: g41-canary-apply.py [--dry] <clone>
# Asserts every anchor exactly once; single write. No transcription:
# anchors are quoted from the tree (verified by --dry before apply).
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

# ---- 1. file-static G41 block (before the ctor) ----
G41_STATICS = """// G41 local diagnostic (not upstream): masked-write canary at boundary 1
// (composite-flush ordinal 1) + per-flush instance census (scratch-overlap
// proof) + O4m hash-input breakdown. Env-gated (PGS_G41_CANARY=1), default
// silent. The canary kicks small synthetic sprites into scratch VRAM pages
// (492..511, never B) through the live draw path, reads the arena back
// after a forced submit+wait, then RESTORES the saved bytes, so the game
// observes zero perturbation (G31 / G30-vpage / scanouts expected 0-diff).
static bool g41_enabled()
{
\tstatic bool en = std::getenv("PGS_G41_CANARY") != nullptr;
\treturn en;
}
static unsigned g41_next_ford = 0;
static unsigned g41_next_comp_ord = 0;
static bool g41_busy = false;
enum { G41_ARENA_BASE_PAGE = 492, G41_ARENA_NPAGES = 20 };
static void g41_fnv(const uint8_t *p, size_t n, uint64_t &fnv, uint32_t &nz)
{
\tfnv = 1469598103934665603ull; // G29-E1 truncated basis (comparability)
\tnz = 0;
\tfor (size_t i = 0; i < n; i++)
\t{
\t\tfnv ^= p[i];
\t\tfnv *= 1099511628211ull;
\t\tnz += p[i] != 0;
\t}
}
"""

e_statics_anchor = '\tdefault:\n\t\treturn "?";\n\t}\n}\nGSInterface::GSInterface()\n'
e_statics_repl = '\tdefault:\n\t\treturn "?";\n\t}\n}\n' + G41_STATICS + 'GSInterface::GSInterface()\n'

# ---- 2. entry block (independent comp ordinal + census) ----
G41_ENTRY = """\t// G41 entry: independent composite ordinal + per-flush instance census
\t// (FRAME+Z identity, bb page spans, scratch-arena overlap flags).
\t// Inner (recursive) calls see g41_busy and skip all G41 work.
\tbool g41_outer = !g41_busy && g41_enabled();
\tbool g41_is_comp = false;
\tint g41_cord = -1;
\tunsigned g41_ford = 0;
\tunsigned g41_entry_prims = 0;
\tbool g41_has_texinfo = false;
\tTexInfo g41_texinfo = {};
\tunsigned g41_tex_count = 0;
\tif (g41_outer)
\t{
\t\tg41_ford = g41_next_ford++;
\t\tg41_entry_prims = render_pass.primitive_count;
\t\tif (render_pass.primitive_count)
\t\t{
\t\t\tfor (uint32_t g41_i = 0; g41_i < render_pass.num_instances; g41_i++)
\t\t\t{
\t\t\t\tif (render_pass.instances[g41_i].frame.desc.FBP == 112)
\t\t\t\t\tg41_is_comp = true;
\t\t\t}
\t\t\tfor (uint32_t g41_i = 0; g41_i < render_pass.num_instances; g41_i++)
\t\t\t{
\t\t\t\tconst auto &g41_inst = render_pass.instances[g41_i];
\t\t\t\tif (g41_inst.bb.z < 0 || g41_inst.bb.w < 0)
\t\t\t\t\tcontinue;
\t\t\t\tint g41_bx0 = g41_inst.bb.x < 0 ? 0 : g41_inst.bb.x;
\t\t\t\tint g41_by0 = g41_inst.bb.y < 0 ? 0 : g41_inst.bb.y;
\t\t\t\tint g41_bx1 = g41_inst.bb.z < 0 ? 0 : g41_inst.bb.z;
\t\t\t\tint g41_by1 = g41_inst.bb.w < 0 ? 0 : g41_inst.bb.w;
\t\t\t\tunsigned g41_fbp = g41_inst.frame.desc.FBP;
\t\t\t\tunsigned g41_fbw = g41_inst.frame.desc.FBW;
\t\t\t\tunsigned g41_stride = g41_fbw ? g41_fbw : 1;
\t\t\t\tunsigned g41_flo = g41_fbp + unsigned(g41_bx0 >> int(g41_inst.fb_page_width_log2)) +
\t\t\t\t                   unsigned(g41_by0 >> int(g41_inst.fb_page_height_log2)) * g41_stride;
\t\t\t\tunsigned g41_fhi = g41_fbp + unsigned(g41_bx1 >> int(g41_inst.fb_page_width_log2)) +
\t\t\t\t                   unsigned(g41_by1 >> int(g41_inst.fb_page_height_log2)) * g41_stride;
\t\t\t\tunsigned g41_zbp = g41_inst.zbuf.desc.ZBP;
\t\t\t\tunsigned g41_zlo = g41_zbp + unsigned(g41_bx0 >> int(g41_inst.z_page_width_log2)) +
\t\t\t\t                   unsigned(g41_by0 >> int(g41_inst.z_page_height_log2)) * g41_stride;
\t\t\t\tunsigned g41_zhi = g41_zbp + unsigned(g41_bx1 >> int(g41_inst.z_page_width_log2)) +
\t\t\t\t                   unsigned(g41_by1 >> int(g41_inst.z_page_height_log2)) * g41_stride;
\t\t\t\tunsigned g41_fov = (g41_flo < 512 && g41_fhi >= 492) ? 1 : 0;
\t\t\t\tunsigned g41_zov = (g41_inst.z_write && g41_zlo < 512 && g41_zhi >= 492) ? 1 : 0;
\t\t\t\tLOGI("G41: census ford=%u prims=%u inst=%u/%u FBP=%u FBW=%u PSM=%u MSK=%08x ZBP=%u ZPSM=%u ZMSK=%u zwr=%u zsen=%u cwm=%08x bb=%d,%d,%d,%d fpg=%u..%u zpg=%u..%u fov=%u zov=%u reason=%s.\\n",
\t\t\t\t     g41_ford, g41_entry_prims, g41_i, render_pass.num_instances,
\t\t\t\t     g41_fbp, g41_fbw, (unsigned)g41_inst.frame.desc.PSM,
\t\t\t\t     (unsigned)g41_inst.frame.desc.FBMSK,
\t\t\t\t     g41_zbp, (unsigned)g41_inst.zbuf.desc.PSM,
\t\t\t\t     (unsigned)g41_inst.zbuf.desc.ZMSK,
\t\t\t\t     (unsigned)g41_inst.z_write, (unsigned)g41_inst.z_sensitive,
\t\t\t\t     (unsigned)g41_inst.color_write_mask,
\t\t\t\t     g41_inst.bb.x, g41_inst.bb.y, g41_inst.bb.z, g41_inst.bb.w,
\t\t\t\t     g41_flo, g41_fhi, g41_zlo, g41_zhi, g41_fov, g41_zov,
\t\t\t\t     g40_reason_str(reason));
\t\t\t}
\t\t}
\t\tif (g41_is_comp)
\t\t{
\t\t\tg41_busy = true;
\t\t\tg41_cord = int(g41_next_comp_ord++);
\t\t\tif (!render_pass.tex_infos.empty())
\t\t\t{
\t\t\t\tg41_texinfo = render_pass.tex_infos[0].info;
\t\t\t\tg41_has_texinfo = true;
\t\t\t\tg41_tex_count = (unsigned)render_pass.tex_infos.size();
\t\t\t}
\t\t}
\t}
"""

e_entry_anchor = '\tParallelGS::RenderPass rp = {};\n'
e_entry_repl = G41_ENTRY + e_entry_anchor

# ---- 3. end block (cord join + hash breakdown + canary) ----
G41_END = """\tif (g41_outer) // G41 end: cord join + (at cord 1) hash breakdown + canary
\t{
\t\tif (g41_is_comp)
\t\t{
\t\t\tint g41_fire = g40_outer ? g40_cord : g41_cord;
\t\t\tLOGI("G41: cord g41=%d g40=%d ford=%u prims=%u tex=%u.\\n",
\t\t\t     g41_cord, g40_cord, g41_ford, g41_entry_prims, g41_tex_count);
\t\t\tif (g41_fire == 1)
\t\t\t{
\t\t\t\t{
\t\t\t\t\t// G41 (b): O4m hash-input breakdown at cord 1. The last
\t\t\t\t\t// texture resolve before this flush is the composite's
\t\t\t\t\t// (single-texture pass, tex=1); recompute the hash from
\t\t\t\t\t// the same 8 inputs to prove the breakdown is complete.
\t\t\t\t\tconst TextureDescriptor &g41_d = state_tracker.last_texture_descriptor;
\t\t\t\t\tUtil::Hasher g41_h;
\t\t\t\t\tg41_h.u64(g41_d.tex0.bits);
\t\t\t\t\tg41_h.u64(g41_d.tex1.bits);
\t\t\t\t\tg41_h.u64(g41_d.texa.bits);
\t\t\t\t\tg41_h.u64(g41_d.miptbp1_3.bits);
\t\t\t\t\tg41_h.u64(g41_d.miptbp4_6.bits);
\t\t\t\t\tg41_h.u64(g41_d.clamp.bits);
\t\t\t\t\tg41_h.u64(g41_d.palette_bank);
\t\t\t\t\tg41_h.u32(g41_d.samples);
\t\t\t\t\tunsigned g41_lctx = registers.prim.desc.CTXT & 1;
\t\t\t\t\tLOGI("G41: hash inputs tex0=%016llx tex1=%016llx texa=%016llx mb13=%016llx mb46=%016llx clamp=%016llx bank=%u smp=%u recomp=%016llx TBP0=%u TBW=%u TPSM=%u.\\n",
\t\t\t\t\t     (unsigned long long)g41_d.tex0.bits,
\t\t\t\t\t     (unsigned long long)g41_d.tex1.bits,
\t\t\t\t\t     (unsigned long long)g41_d.texa.bits,
\t\t\t\t\t     (unsigned long long)g41_d.miptbp1_3.bits,
\t\t\t\t\t     (unsigned long long)g41_d.miptbp4_6.bits,
\t\t\t\t\t     (unsigned long long)g41_d.clamp.bits,
\t\t\t\t\t     g41_d.palette_bank, g41_d.samples,
\t\t\t\t\t     (unsigned long long)g41_h.get(),
\t\t\t\t\t     (unsigned)g41_d.tex0.desc.TBP0, (unsigned)g41_d.tex0.desc.TBW,
\t\t\t\t\t     (unsigned)g41_d.tex0.desc.PSM);
\t\t\t\t\tLOGI("G41: hash rect x=%u y=%u w=%u h=%u lv=%u ctx=%u rtex0=%016llx rtex1=%016llx rclamp=%016llx rmb13=%016llx rmb46=%016llx rtexa=%016llx.\\n",
\t\t\t\t\t     g41_d.rect.x, g41_d.rect.y, g41_d.rect.width, g41_d.rect.height,
\t\t\t\t\t     g41_d.rect.levels, g41_lctx,
\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].tex0.bits,
\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].tex1.bits,
\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].clamp.bits,
\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].miptbl_1_3.bits,
\t\t\t\t\t     (unsigned long long)registers.ctx[g41_lctx].miptbl_4_6.bits,
\t\t\t\t\t     (unsigned long long)registers.texa.bits);
\t\t\t\t\tif (g41_has_texinfo)
\t\t\t\t\t{
\t\t\t\t\t\tLOGI("G41: hash texinfo n=%u sizes=%.1f,%.1f,%.6f,%.6f region=%.1f,%.1f,%.1f,%.1f bias=%.6f,%.6f arrayed=%d flags=%d.\\n",
\t\t\t\t\t\t     g41_tex_count,
\t\t\t\t\t\t     g41_texinfo.sizes.x, g41_texinfo.sizes.y,
\t\t\t\t\t\t     g41_texinfo.sizes.z, g41_texinfo.sizes.w,
\t\t\t\t\t\t     g41_texinfo.region.x, g41_texinfo.region.y,
\t\t\t\t\t\t     g41_texinfo.region.z, g41_texinfo.region.w,
\t\t\t\t\t\t     g41_texinfo.bias.x, g41_texinfo.bias.y,
\t\t\t\t\t\t     g41_texinfo.arrayed, g41_texinfo.flags);
\t\t\t\t\t}
\t\t\t\t\telse
\t\t\t\t\t{
\t\t\t\t\t\tLOGI("G41: hash texinfo EMPTY n=%u.\\n", g41_tex_count);
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\t// G41 canary: 5 synthetic sprites (C1..C5) into scratch
\t\t\t\t\t// arena pages 492..511 (never B) through the live draw
\t\t\t\t\t// path. Per-cell register + VRAM save/restore; G40 rows
\t\t\t\t\t// suppressed (g40_busy held) so game O-rows stay 0-diff.
\t\t\t\t\tg40_busy = true;
\t\t\t\t\tunsigned g41_s_kseen = g40_k_seen;
\t\t\t\t\tunsigned g41_s_kadc = g40_k_adc;
\t\t\t\t\tunsigned g41_s_kdeg = g40_k_deg;
\t\t\t\t\tunsigned g41_s_kbb = g40_k_bb;
\t\t\t\t\tunsigned g41_s_kfuse = g40_k_fuse;
\t\t\t\t\tunsigned g41_s_kacc = g40_k_acc;
\t\t\t\t\tunsigned g41_s_treuse = g40_tex_reuse;
\t\t\t\t\tbool g41_s_tmade = g40_tex_created;
\t\t\t\t\tuint64_t g41_s_thash = g40_tex_hash;
\t\t\t\t\tunsigned g41_s_ttbp0 = g40_tex_tbp0;
\t\t\t\t\tunsigned g41_s_ttbw = g40_tex_tbw;
\t\t\t\t\tunsigned g41_s_tpsm = g40_tex_psm;
\t\t\t\t\tunsigned g41_s_tlv = g40_tex_levels;
\t\t\t\t\tunsigned g41_s_tsmp = g40_tex_samples;
\t\t\t\t\tbool g41_s_tlt = g40_tex_longterm;
\t\t\t\t\tVertexPosition g41_vq_pos[3];
\t\t\t\t\tVertexAttribute g41_vq_attr[3];
\t\t\t\t\tfor (unsigned g41_vqi = 0; g41_vqi < 3; g41_vqi++)
\t\t\t\t\t{
\t\t\t\t\t\tg41_vq_pos[g41_vqi] = vertex_queue.pos[g41_vqi];
\t\t\t\t\t\tg41_vq_attr[g41_vqi] = vertex_queue.attr[g41_vqi];
\t\t\t\t\t}
\t\t\t\t\tunsigned g41_vq_n = vertex_queue.count;
\t\t\t\t\tStateTracker g41_saved_st = state_tracker;
\t\t\t\t\tconst size_t g41_abase = size_t(G41_ARENA_BASE_PAGE) * 8192;
\t\t\t\t\tconst size_t g41_an = size_t(G41_ARENA_NPAGES) * 8192;
\t\t\t\t\tbool g41_pre_ok = false;
\t\t\t\t\tstd::vector<uint8_t> g41_pre(g41_an, 0);
\t\t\t\t\t{
\t\t\t\t\t\tconst uint8_t *g41_a = static_cast<const uint8_t *>(map_vram_read(g41_abase, g41_an));
\t\t\t\t\t\tif (!g41_a)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tLOGI("G41: canary ABORT arena pre-read map failed.\\n");
\t\t\t\t\t\t}
\t\t\t\t\t\telse
\t\t\t\t\t\t{
\t\t\t\t\t\t\tmemcpy(g41_pre.data(), g41_a, g41_an);
\t\t\t\t\t\t\tg41_pre_ok = true;
\t\t\t\t\t\t\tuint64_t g41_pf = 0;
\t\t\t\t\t\t\tuint32_t g41_pz = 0;
\t\t\t\t\t\t\tg41_fnv(g41_pre.data(), g41_an, g41_pf, g41_pz);
\t\t\t\t\t\t\tLOGI("G41: arena pre-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x vq=%u.\\n",
\t\t\t\t\t\t\t     (unsigned long long)g41_pf, (unsigned)g41_pz,
\t\t\t\t\t\t\t     g41_pre[0], g41_pre[1], g41_pre[2], g41_pre[3],
\t\t\t\t\t\t\t     g41_pre[4], g41_pre[5], g41_pre[6], g41_pre[7],
\t\t\t\t\t\t\t     g41_vq_n);
\t\t\t\t\t\t}
\t\t\t\t\t}
\t\t\t\t\tstatic const unsigned g41_fbp[5] = { 492, 496, 500, 504, 508 };
\t\t\t\t\tstatic const unsigned g41_psm[5] = { 0, 0, 1, 1, 1 };
\t\t\t\t\tstatic const uint32_t g41_msk[5] = { 0, 0xff000000u, 0, 0xff000000u, 0xff000000u };
\t\t\t\t\tfor (unsigned g41_cell = 0; g41_cell < 5 && g41_pre_ok; g41_cell++)
\t\t\t\t\t{
\t\t\t\t\t\tbool g41_c5 = g41_cell == 4;
\t\t\t\t\t\tunsigned g41_lctx = registers.prim.desc.CTXT & 1;
\t\t\t\t\t\tRegisterAddr g41_a_frame = g41_lctx ? RegisterAddr::FRAME_2 : RegisterAddr::FRAME_1;
\t\t\t\t\t\tRegisterAddr g41_a_zbuf = g41_lctx ? RegisterAddr::ZBUF_2 : RegisterAddr::ZBUF_1;
\t\t\t\t\t\tRegisterAddr g41_a_test = g41_lctx ? RegisterAddr::TEST_2 : RegisterAddr::TEST_1;
\t\t\t\t\t\tRegisterAddr g41_a_scis = g41_lctx ? RegisterAddr::SCISSOR_2 : RegisterAddr::SCISSOR_1;
\t\t\t\t\t\tRegisterAddr g41_a_xyof = g41_lctx ? RegisterAddr::XYOFFSET_2 : RegisterAddr::XYOFFSET_1;
\t\t\t\t\t\tRegisterAddr g41_a_fba = g41_lctx ? RegisterAddr::FBA_2 : RegisterAddr::FBA_1;
\t\t\t\t\t\tuint64_t g41_s_prim = registers.prim.bits;
\t\t\t\t\t\tuint64_t g41_s_rgbaq = registers.rgbaq.bits;
\t\t\t\t\t\tuint64_t g41_s_st = registers.st.bits;
\t\t\t\t\t\tuint64_t g41_s_uv = registers.uv.bits;
\t\t\t\t\t\tuint64_t g41_s_frame = registers.ctx[g41_lctx].frame.bits;
\t\t\t\t\t\tuint64_t g41_s_zbuf = registers.ctx[g41_lctx].zbuf.bits;
\t\t\t\t\t\tuint64_t g41_s_test = registers.ctx[g41_lctx].test.bits;
\t\t\t\t\t\tuint64_t g41_s_scis = registers.ctx[g41_lctx].scissor.bits;
\t\t\t\t\t\tuint64_t g41_s_xyof = registers.ctx[g41_lctx].xyoffset.bits;
\t\t\t\t\t\tuint64_t g41_s_fba = registers.ctx[g41_lctx].fba.bits;
\t\t\t\t\t\tuint64_t g41_s_pabe = registers.pabe.bits;
\t\t\t\t\t\tif (!g41_c5)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tReg64<PRIMBits> g41_p;
\t\t\t\t\t\t\tg41_p.bits = 0;
\t\t\t\t\t\t\tg41_p.desc.PRIM = 6;
\t\t\t\t\t\t\tg41_p.desc.CTXT = g41_lctx;
\t\t\t\t\t\t\twrite_register(RegisterAddr::PRIM, g41_p.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::PRMODE, g41_p.bits);
\t\t\t\t\t\t\tReg64<RGBAQBits> g41_c;
\t\t\t\t\t\t\tg41_c.bits = 0;
\t\t\t\t\t\t\tg41_c.desc.R = 0x11;
\t\t\t\t\t\t\tg41_c.desc.G = 0x22;
\t\t\t\t\t\t\tg41_c.desc.B = 0x33;
\t\t\t\t\t\t\tg41_c.desc.A = 0x44;
\t\t\t\t\t\t\tg41_c.desc.Q = 1.0f;
\t\t\t\t\t\t\twrite_register(RegisterAddr::RGBAQ, g41_c.bits);
\t\t\t\t\t\t\twrite_register(g41_a_xyof, uint64_t(0));
\t\t\t\t\t\t\tReg64<SCISSORBits> g41_sc;
\t\t\t\t\t\t\tg41_sc.bits = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAX0 = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAY0 = 0;
\t\t\t\t\t\t\tg41_sc.desc.SCAX1 = 63;
\t\t\t\t\t\t\tg41_sc.desc.SCAY1 = 63;
\t\t\t\t\t\t\twrite_register(g41_a_scis, g41_sc.bits);
\t\t\t\t\t\t\twrite_register(g41_a_test, uint64_t(0));
\t\t\t\t\t\t\twrite_register(g41_a_fba, uint64_t(0));
\t\t\t\t\t\t\twrite_register(RegisterAddr::PABE, uint64_t(0));
\t\t\t\t\t\t\tReg64<FRAMEBits> g41_f;
\t\t\t\t\t\t\tg41_f.bits = 0;
\t\t\t\t\t\t\tg41_f.desc.FBP = g41_fbp[g41_cell];
\t\t\t\t\t\t\tg41_f.desc.FBW = 8;
\t\t\t\t\t\t\tg41_f.desc.PSM = g41_psm[g41_cell];
\t\t\t\t\t\t\tg41_f.desc.FBMSK = g41_msk[g41_cell];
\t\t\t\t\t\t\twrite_register(g41_a_frame, g41_f.bits);
\t\t\t\t\t\t\tReg64<ZBUFBits> g41_z;
\t\t\t\t\t\t\tg41_z.bits = 0;
\t\t\t\t\t\t\tg41_z.desc.ZBP = 511;
\t\t\t\t\t\t\tg41_z.desc.ZMSK = 1;
\t\t\t\t\t\t\twrite_register(g41_a_zbuf, g41_z.bits);
\t\t\t\t\t\t}
\t\t\t\t\t\telse
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
\t\t\t\t\t\treset_vertex_queue();
\t\t\t\t\t\tReg64<XYZBits> g41_v0;
\t\t\t\t\t\tg41_v0.bits = 0;
\t\t\t\t\t\tg41_v0.desc.X = 0;
\t\t\t\t\t\tg41_v0.desc.Y = 0;
\t\t\t\t\t\tg41_v0.desc.Z = 0;
\t\t\t\t\t\tReg64<XYZBits> g41_v1;
\t\t\t\t\t\tg41_v1.bits = 0;
\t\t\t\t\t\tg41_v1.desc.X = 31 << 4;
\t\t\t\t\t\tg41_v1.desc.Y = 31 << 4;
\t\t\t\t\t\tg41_v1.desc.Z = 0;
\t\t\t\t\t\tif (g41_c5)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tReg64<UVBits> g41_u0;
\t\t\t\t\t\t\tg41_u0.bits = 0;
\t\t\t\t\t\t\tg41_u0.desc.U = 0;
\t\t\t\t\t\t\tg41_u0.desc.V = 0;
\t\t\t\t\t\t\tReg64<STBits> g41_s0;
\t\t\t\t\t\t\tg41_s0.bits = 0;
\t\t\t\t\t\t\twrite_register(RegisterAddr::UV, g41_u0.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::ST, g41_s0.bits);
\t\t\t\t\t\t}
\t\t\t\t\t\twrite_register(RegisterAddr::XYZ2, g41_v0.bits);
\t\t\t\t\t\tif (g41_c5)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tReg64<UVBits> g41_u1;
\t\t\t\t\t\t\tg41_u1.bits = 0;
\t\t\t\t\t\t\tg41_u1.desc.U = 511;
\t\t\t\t\t\t\tg41_u1.desc.V = 511;
\t\t\t\t\t\t\tReg64<STBits> g41_s1;
\t\t\t\t\t\t\tg41_s1.bits = 0;
\t\t\t\t\t\t\tg41_s1.desc.S = 511.0f;
\t\t\t\t\t\t\tg41_s1.desc.T = 511.0f;
\t\t\t\t\t\t\twrite_register(RegisterAddr::UV, g41_u1.bits);
\t\t\t\t\t\t\twrite_register(RegisterAddr::ST, g41_s1.bits);
\t\t\t\t\t\t}
\t\t\t\t\t\twrite_register(RegisterAddr::XYZ2, g41_v1.bits);
\t\t\t\t\t\tunsigned g41_acc = render_pass.primitive_count;
\t\t\t\t\t\t{
\t\t\t\t\t\t\tconst auto &g41_kinst = render_pass.instances[render_pass.current_instance];
\t\t\t\t\t\t\tLOGI("G41: C%u kick acc=%u ctx=%u prim=%016llx FBP=%u FBW=%u PSM=%u MSK=%08x ZBP=%u ZMSK=%u bb=%d,%d,%d,%d.\\n",
\t\t\t\t\t\t\t     g41_cell + 1, g41_acc, g41_lctx,
\t\t\t\t\t\t\t     (unsigned long long)registers.prim.bits,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.frame.desc.FBP,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.frame.desc.FBW,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.frame.desc.PSM,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.frame.desc.FBMSK,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.zbuf.desc.ZBP,
\t\t\t\t\t\t\t     (unsigned)g41_kinst.zbuf.desc.ZMSK,
\t\t\t\t\t\t\t     g41_kinst.bb.x, g41_kinst.bb.y, g41_kinst.bb.z, g41_kinst.bb.w);
\t\t\t\t\t\t}
\t\t\t\t\t\tflush_render_pass(FlushReason::SubmissionFlush);
\t\t\t\t\t\tuint64_t g41_tl = tracker.mark_submission_timeline(FlushReason::HostAccess);
\t\t\t\t\t\trenderer.flush_submit(g41_tl);
\t\t\t\t\t\trenderer.wait_timeline(g41_tl);
\t\t\t\t\t\t{
\t\t\t\t\t\t\tconst uint8_t *g41_a = static_cast<const uint8_t *>(map_vram_read(g41_abase, g41_an));
\t\t\t\t\t\t\tif (!g41_a)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tLOGI("G41: C%u verd acc=%u map failed.\\n", g41_cell + 1, g41_acc);
\t\t\t\t\t\t\t}
\t\t\t\t\t\t\telse
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tunsigned g41_nchg = 0;
\t\t\t\t\t\t\t\tunsigned g41_chg0 = 0;
\t\t\t\t\t\t\t\tfor (unsigned g41_pg = 0; g41_pg < G41_ARENA_NPAGES; g41_pg++)
\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\tif (memcmp(g41_a + g41_pg * 8192, &g41_pre[g41_pg * 8192], 8192) != 0)
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tif (g41_nchg == 0)
\t\t\t\t\t\t\t\t\t\t\tg41_chg0 = G41_ARENA_BASE_PAGE + g41_pg;
\t\t\t\t\t\t\t\t\t\tg41_nchg++;
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\tLOGI("G41: C%u verd acc=%u landed=%u nchg=%u chg0=%u fbp=%u.\\n",
\t\t\t\t\t\t\t\t     g41_cell + 1, g41_acc, g41_nchg ? 1 : 0, g41_nchg, g41_chg0,
\t\t\t\t\t\t\t\t     g41_fbp[g41_cell]);
\t\t\t\t\t\t\t\tunsigned g41_shown = 0;
\t\t\t\t\t\t\t\tfor (unsigned g41_pg = 0; g41_pg < G41_ARENA_NPAGES && g41_shown < 8; g41_pg++)
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\tif (memcmp(g41_a + g41_pg * 8192, &g41_pre[g41_pg * 8192], 8192) != 0)
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tuint64_t g41_cf = 0;
\t\t\t\t\t\t\t\t\t\tuint32_t g41_cz = 0;
\t\t\t\t\t\t\t\t\t\tg41_fnv(g41_a + g41_pg * 8192, 8192, g41_cf, g41_cz);
\t\t\t\t\t\t\t\t\t\tconst uint8_t *g41_cp = g41_a + g41_pg * 8192;
\t\t\t\t\t\t\t\t\t\tLOGI("G41: C%u chg page=%u fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x.\\n",
\t\t\t\t\t\t\t\t\t\t     g41_cell + 1, G41_ARENA_BASE_PAGE + g41_pg,
\t\t\t\t\t\t\t\t\t\t     (unsigned long long)g41_cf, (unsigned)g41_cz,
\t\t\t\t\t\t\t\t\t\t     g41_cp[0], g41_cp[1], g41_cp[2], g41_cp[3],
\t\t\t\t\t\t\t\t\t\t     g41_cp[4], g41_cp[5], g41_cp[6], g41_cp[7]);
\t\t\t\t\t\t\t\t\t\tg41_shown++;
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\t{
\t\t\t\t\t\t\tuint8_t *g41_w = static_cast<uint8_t *>(map_vram_write(g41_abase, g41_an));
\t\t\t\t\t\t\tif (!g41_w)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tLOGI("G41: C%u restored=MAPFAIL.\\n", g41_cell + 1);
\t\t\t\t\t\t\t}
\t\t\t\t\t\t\telse
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tmemcpy(g41_w, g41_pre.data(), g41_an);
\t\t\t\t\t\t\t\tend_vram_write(g41_abase, g41_an);
\t\t\t\t\t\t\t\tuint64_t g41_tl2 = tracker.mark_submission_timeline(FlushReason::HostAccess);
\t\t\t\t\t\t\t\trenderer.flush_submit(g41_tl2);
\t\t\t\t\t\t\t\trenderer.wait_timeline(g41_tl2);
\t\t\t\t\t\t\t\tconst uint8_t *g41_v = static_cast<const uint8_t *>(map_vram_read(g41_abase, g41_an));
\t\t\t\t\t\t\t\tunsigned g41_rok = (g41_v && memcmp(g41_v, g41_pre.data(), g41_an) == 0) ? 1 : 0;
\t\t\t\t\t\t\t\tLOGI("G41: C%u restored=%u.\\n", g41_cell + 1, g41_rok);
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\twrite_register(g41_a_frame, g41_s_frame);
\t\t\t\t\t\twrite_register(g41_a_zbuf, g41_s_zbuf);
\t\t\t\t\t\twrite_register(g41_a_test, g41_s_test);
\t\t\t\t\t\twrite_register(g41_a_scis, g41_s_scis);
\t\t\t\t\t\twrite_register(g41_a_xyof, g41_s_xyof);
\t\t\t\t\t\twrite_register(g41_a_fba, g41_s_fba);
\t\t\t\t\t\twrite_register(RegisterAddr::PABE, g41_s_pabe);
\t\t\t\t\t\twrite_register(RegisterAddr::RGBAQ, g41_s_rgbaq);
\t\t\t\t\t\twrite_register(RegisterAddr::ST, g41_s_st);
\t\t\t\t\t\twrite_register(RegisterAddr::UV, g41_s_uv);
\t\t\t\t\t\twrite_register(RegisterAddr::PRIM, g41_s_prim);
\t\t\t\t\t\twrite_register(RegisterAddr::PRMODE, g41_s_prim);
\t\t\t\t\t\treset_vertex_queue();
\t\t\t\t\t}
\t\t\t\t\tstate_tracker = g41_saved_st;
\t\t\t\t\tfor (unsigned g41_vqi = 0; g41_vqi < 3; g41_vqi++)
\t\t\t\t\t{
\t\t\t\t\t\tvertex_queue.pos[g41_vqi] = g41_vq_pos[g41_vqi];
\t\t\t\t\t\tvertex_queue.attr[g41_vqi] = g41_vq_attr[g41_vqi];
\t\t\t\t\t}
\t\t\t\t\tvertex_queue.count = g41_vq_n;
\t\t\t\t\tg40_k_seen = g41_s_kseen;
\t\t\t\t\tg40_k_adc = g41_s_kadc;
\t\t\t\t\tg40_k_deg = g41_s_kdeg;
\t\t\t\t\tg40_k_bb = g41_s_kbb;
\t\t\t\t\tg40_k_fuse = g41_s_kfuse;
\t\t\t\t\tg40_k_acc = g41_s_kacc;
\t\t\t\t\tg40_tex_reuse = g41_s_treuse;
\t\t\t\t\tg40_tex_created = g41_s_tmade;
\t\t\t\t\tg40_tex_hash = g41_s_thash;
\t\t\t\t\tg40_tex_tbp0 = g41_s_ttbp0;
\t\t\t\t\tg40_tex_tbw = g41_s_ttbw;
\t\t\t\t\tg40_tex_psm = g41_s_tpsm;
\t\t\t\t\tg40_tex_levels = g41_s_tlv;
\t\t\t\t\tg40_tex_samples = g41_s_tsmp;
\t\t\t\t\tg40_tex_longterm = g41_s_tlt;
\t\t\t\t\tg40_busy = false;
\t\t\t\t}
\t\t\t}
\t\t\tg41_busy = false;
\t\t}
\t}
"""

e_end_anchor = ('\t\t\tg40_busy = false;\n\t\t}\n\t}\n}\n\n'
                'void GSInterface::flush(PageTrackerFlushFlags flags, FlushReason reason)\n')
e_end_repl = '\t\t\tg40_busy = false;\n\t\t}\n\t}\n' + G41_END + '}\n\nvoid GSInterface::flush(PageTrackerFlushFlags flags, FlushReason reason)\n'

n = 0
n += edit(IFACE, [(e_statics_anchor, e_statics_repl)])
n += edit(IFACE, [(e_entry_anchor, e_entry_repl)])
n += edit(IFACE, [(e_end_anchor, e_end_repl)])
print(("DRY-OK " if DRY else "APPLIED ") + str(n) + " edits")

