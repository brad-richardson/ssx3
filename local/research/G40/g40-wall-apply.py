#!/usr/bin/env python3
# G40: apply the ONE observation-only wall hunk (O1..O5 + O3b/O4m support rows).
# Usage: g40-wall-apply.py [--dry] <clone>
# Asserts every anchor exactly once; single write per file. No transcription:
# anchors are quoted from the tree (verified by --dry before apply).
import sys

DRY = len(sys.argv) > 1 and sys.argv[1] == "--dry"
CLONE = sys.argv[2] if DRY else sys.argv[1]
T = "\t"
NL = "\n"


def edit(path, pairs):
    with open(path, "r") as f:
        src = f.read()
    for i, (find, repl) in enumerate(pairs):
        n = src.count(find)
        assert n == 1, f"{path} edit{i}: anchor x{n}, want x1:\n{find[:220]}"
        src = src.replace(find, repl, 1)
    if not DRY:
        with open(path, "w") as f:
            f.write(src)
    return len(pairs)


IFACE = CLONE + "/gs/gs_interface.cpp"
RHP = CLONE + "/gs/gs_renderer.hpp"
RCP = CLONE + "/gs/gs_renderer.cpp"

# ---- gs_interface.cpp: include ----
e_inc = [(f'#include "gs_registers_debug.hpp"{NL}',
          f'#include "gs_registers_debug.hpp"{NL}#include <cstdlib> // G40: std::getenv{NL}')]

# ---- gs_interface.cpp: file-static G40 block ----
g40_statics = (
    f"namespace ParallelGS{NL}{{{NL}"
    f"// G40 local diagnostic (not upstream): sub-vsync A->B observation wall at{NL}"
    f"// boundary 1 (composite-flush ordinal 1 == pass 0, vsync #1, phase 0).{NL}"
    f"// Env-gated (PGS_G40_WALL=1), default silent, observation-only: kick/tex{NL}"
    f"// counters + LOGI + VRAM/staging reads + ONE forced submit+wait per probe{NL}"
    f"// firing (composite ordinals {{0,1}}; ordinal 0 is the load-control).{NL}"
    f"// Unset: one cached getenv branch per hook, zero lines, zero submits.{NL}"
    f"static bool g40_enabled(){NL}{{{NL}"
    f"{T}static bool en = std::getenv(\"PGS_G40_WALL\") != nullptr;{NL}"
    f"{T}return en;{NL}}}{NL}"
    f"static unsigned g40_next_flush_ord = 0;{NL}"
    f"static unsigned g40_next_comp_ord = 0;{NL}"
    f"static bool g40_busy = false;{NL}"
    f"static unsigned g40_k_seen = 0;{NL}"
    f"static unsigned g40_k_adc = 0;{NL}"
    f"static unsigned g40_k_deg = 0;{NL}"
    f"static unsigned g40_k_bb = 0;{NL}"
    f"static unsigned g40_k_fuse = 0;{NL}"
    f"static unsigned g40_k_acc = 0;{NL}"
    f"static unsigned g40_tex_reuse = 0;{NL}"
    f"static bool g40_tex_created = false;{NL}"
    f"static uint64_t g40_tex_hash = 0;{NL}"
    f"static unsigned g40_tex_tbp0 = 0;{NL}"
    f"static unsigned g40_tex_tbw = 0;{NL}"
    f"static unsigned g40_tex_psm = 0;{NL}"
    f"static unsigned g40_tex_levels = 0;{NL}"
    f"static unsigned g40_tex_samples = 0;{NL}"
    f"static bool g40_tex_longterm = false;{NL}"
    f"static bool g40_last_valid = false;{NL}"
    f"static unsigned g40_last_ford = 0;{NL}"
    f"static uint64_t g40_last_f = 0;{NL}"
    f"static uint32_t g40_last_z = 0;{NL}"
    f"static uint8_t g40_last_head[8] = {{ 0, 0, 0, 0, 0, 0, 0, 0 }};{NL}"
    f"static void g40_fnv(const uint8_t *p, size_t n, uint64_t &fnv, uint32_t &nz){NL}{{{NL}"
    f"{T}fnv = 1469598103934665603ull; // G29-E1 truncated basis (comparability){NL}"
    f"{T}nz = 0;{NL}"
    f"{T}for (size_t i = 0; i < n; i++){NL}{T}{{{NL}"
    f"{T}{T}fnv ^= p[i];{NL}{T}{T}fnv *= 1099511628211ull;{NL}{T}{T}nz += p[i] != 0;{NL}{T}}}{NL}}}{NL}"
    f"static const char *g40_reason_str(FlushReason r){NL}{{{NL}"
    f"{T}switch (r){NL}{T}{{{NL}"
    f"{T}case FlushReason::FBPointer:{NL}{T}{T}return \"FBPointer\";{NL}"
    f"{T}case FlushReason::Overflow:{NL}{T}{T}return \"Overflow\";{NL}"
    f"{T}case FlushReason::TextureHazard:{NL}{T}{T}return \"TextureHazard\";{NL}"
    f"{T}case FlushReason::CopyHazard:{NL}{T}{T}return \"CopyHazard\";{NL}"
    f"{T}case FlushReason::SubmissionFlush:{NL}{T}{T}return \"SubmissionFlush\";{NL}"
    f"{T}case FlushReason::PressureFlush:{NL}{T}{T}return \"PressureFlush\";{NL}"
    f"{T}case FlushReason::HostAccess:{NL}{T}{T}return \"HostAccess\";{NL}"
    f"{T}default:{NL}{T}{T}return \"?\";{NL}{T}}}{NL}}}{NL}"
    f"GSInterface::GSInterface(){NL}"
)
e_statics = [(f"namespace ParallelGS{NL}{{{NL}GSInterface::GSInterface(){NL}", g40_statics)]

# ---- O1: kick_primitive ----
e_kick = [(
    f"{T}if (vertex_queue.count < num_vertices){NL}{T}{T}return;{NL}{NL}"
    f"{T}if (!adc){NL}{T}{{{NL}"
    f"{T}{T}if (!draw_is_degenerate()){NL}"
    f"{T}{T}{T}drawing_kick_append<list_primitive, fan_primitive, quad, num_vertices>();{NL}"
    f"{T}{T}else{NL}{T}{T}{T}TRACE(\"Degenerate Draw\", DummyBits{{}});{NL}{T}}}{NL}",
    f"{T}if (vertex_queue.count < num_vertices){NL}{T}{T}return;{NL}{NL}"
    f"{T}if (g40_enabled()) // G40 O1{T}{NL}{T}{{{NL}"
    f"{T}{T}g40_k_seen++;{NL}{T}{T}g40_k_adc += adc ? 1 : 0;{NL}{T}}}{NL}"
    f"{T}if (!adc){NL}{T}{{{NL}"
    f"{T}{T}if (!draw_is_degenerate()){NL}"
    f"{T}{T}{T}drawing_kick_append<list_primitive, fan_primitive, quad, num_vertices>();{NL}"
    f"{T}{T}else{NL}{T}{T}{{{NL}"
    f"{T}{T}{T}if (g40_enabled()) // G40 O1{NL}{T}{T}{T}{T}g40_k_deg++;{NL}"
    f"{T}{T}{T}TRACE(\"Degenerate Draw\", DummyBits{{}});{NL}{T}{T}}}{NL}{T}}}{NL}")]

# ---- O1: BB#1 / fuse / BB#2 / accept ----
e_bb1 = [(
    f"{T}// Check for degenerate BB. Can happen if primitive is clipped away completely by scissor.{NL}"
    f"{T}if (bb.z < bb.x || bb.w < bb.y){NL}{T}{{{NL}"
    f"{T}{T}TRACE(\"Degenerate BB\", bb);{NL}{T}{T}return;{NL}{T}}}{NL}",
    f"{T}// Check for degenerate BB. Can happen if primitive is clipped away completely by scissor.{NL}"
    f"{T}if (bb.z < bb.x || bb.w < bb.y){NL}{T}{{{NL}"
    f"{T}{T}if (g40_enabled()) // G40 O1{NL}{T}{T}{T}g40_k_bb++;{NL}"
    f"{T}{T}TRACE(\"Degenerate BB\", bb);{NL}{T}{T}return;{NL}{T}}}{NL}")]
e_fuse = [(
    f"{T}{T}{T}render_pass.last_triangle_is_parallelogram_candidate = false;{NL}"
    f"{T}{T}{T}TRACE(\"Promote Parallelogram\", DummyBits{{}});{NL}"
    f"{T}{T}{T}return;{NL}",
    f"{T}{T}{T}render_pass.last_triangle_is_parallelogram_candidate = false;{NL}"
    f"{T}{T}{T}if (g40_enabled()) // G40 O1{NL}{T}{T}{T}{T}g40_k_fuse++;{NL}"
    f"{T}{T}{T}TRACE(\"Promote Parallelogram\", DummyBits{{}});{NL}"
    f"{T}{T}{T}return;{NL}")]
e_bb2 = [(
    f"{T}{T}if (bb.z < bb.x){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}TRACE(\"Degenerate BB\", bb);{NL}{T}{T}{T}return;{NL}{T}{T}}}{NL}",
    f"{T}{T}if (bb.z < bb.x){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}if (g40_enabled()) // G40 O1{NL}{T}{T}{T}{T}g40_k_bb++;{NL}"
    f"{T}{T}{T}TRACE(\"Degenerate BB\", bb);{NL}{T}{T}{T}return;{NL}{T}{T}}}{NL}")]
e_acc = [(
    f"{T}render_pass.primitive_count++;{NL}"
    f"{T}// Commit this here as well. Need to do it after flushing state, since that may reset any tracking state.{NL}",
    f"{T}render_pass.primitive_count++;{NL}"
    f"{T}if (g40_enabled()) // G40 O1{NL}{T}{T}g40_k_acc++;{NL}"
    f"{T}// Commit this here as well. Need to do it after flushing state, since that may reset any tracking state.{NL}")]

# ---- O4m: texture resolve metadata ----
e_texa = [(
    f"{T}if (!get_and_clear_dirty_flag(STATE_DIRTY_TEX_BIT)){NL}{T}{{{NL}"
    f"{T}{T}assert(state_tracker.last_texture_index != UINT32_MAX);{NL}"
    f"{T}{T}assert(state_tracker.last_texture_index_valid_at_texflush == state_tracker.texflush_counter);{NL}"
    f"{T}{T}return state_tracker.last_texture_index;{NL}{T}}}{NL}",
    f"{T}if (!get_and_clear_dirty_flag(STATE_DIRTY_TEX_BIT)){NL}{T}{{{NL}"
    f"{T}{T}assert(state_tracker.last_texture_index != UINT32_MAX);{NL}"
    f"{T}{T}assert(state_tracker.last_texture_index_valid_at_texflush == state_tracker.texflush_counter);{NL}"
    f"{T}{T}if (g40_enabled()) // G40 O4m{NL}{T}{T}{T}g40_tex_reuse++;{NL}"
    f"{T}{T}return state_tracker.last_texture_index;{NL}{T}}}{NL}")]
e_texb = [(
    f"{T}if (state_tracker.last_texture_index != UINT32_MAX &&{NL}"
    f"{T}    !render_pass.tex_infos.empty() &&{NL}"
    f"{T}    state_tracker.last_texture_descriptor == desc){NL}{T}{{{NL}"
    f"{T}{T}state_tracker.last_texture_index_valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}{T}if (cached_index && cached_index->valid){NL}"
    f"{T}{T}{T}cached_index->valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}{T}return state_tracker.last_texture_index;{NL}{T}}}{NL}",
    f"{T}if (state_tracker.last_texture_index != UINT32_MAX &&{NL}"
    f"{T}    !render_pass.tex_infos.empty() &&{NL}"
    f"{T}    state_tracker.last_texture_descriptor == desc){NL}{T}{{{NL}"
    f"{T}{T}state_tracker.last_texture_index_valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}{T}if (cached_index && cached_index->valid){NL}"
    f"{T}{T}{T}cached_index->valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}{T}if (g40_enabled()) // G40 O4m{NL}{T}{T}{T}g40_tex_reuse++;{NL}"
    f"{T}{T}return state_tracker.last_texture_index;{NL}{T}}}{NL}")]
e_texc = [(
    f"{T}if (cached_index && cached_index->valid){NL}{T}{{{NL}"
    f"{T}{T}texture_index = cached_index->index;{NL}{T}}}{NL}",
    f"{T}if (cached_index && cached_index->valid){NL}{T}{{{NL}"
    f"{T}{T}texture_index = cached_index->index;{NL}"
    f"{T}{T}if (g40_enabled()) // G40 O4m{NL}{T}{T}{T}g40_tex_reuse++;{NL}{T}}}{NL}")]
e_texd = [(
    f"{T}uint32_t texture_index;{NL}",
    f"{T}uint32_t texture_index;{NL}{T}bool g40_tex_made = false; // G40 O4{NL}")]
e_texe = [(
    f"image = renderer.create_cached_texture(desc);{NL}",
    f"image = renderer.create_cached_texture(desc);{NL}{T}{T}{T}g40_tex_made = true; // G40 O4{NL}")]
e_texf = [(
    f"{T}state_tracker.last_texture_descriptor = desc;{NL}"
    f"{T}state_tracker.last_texture_index = texture_index;{NL}"
    f"{T}state_tracker.last_texture_index_valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}state_tracker.texflush_counter_pending = false;{NL}"
    f"{T}return texture_index;{NL}",
    f"{T}if (g40_enabled()) // G40 O4: full-resolve snapshot (first use of a texture per pass){NL}{T}{{{NL}"
    f"{T}{T}g40_tex_created = g40_tex_made;{NL}"
    f"{T}{T}g40_tex_hash = hasher.get();{NL}"
    f"{T}{T}g40_tex_tbp0 = desc.tex0.desc.TBP0;{NL}"
    f"{T}{T}g40_tex_tbw = desc.tex0.desc.TBW;{NL}"
    f"{T}{T}g40_tex_psm = desc.tex0.desc.PSM;{NL}"
    f"{T}{T}g40_tex_levels = desc.rect.levels;{NL}"
    f"{T}{T}g40_tex_samples = desc.samples;{NL}"
    f"{T}{T}g40_tex_longterm = long_term_cache_texture;{NL}{T}}}{NL}"
    f"{T}state_tracker.last_texture_descriptor = desc;{NL}"
    f"{T}state_tracker.last_texture_index = texture_index;{NL}"
    f"{T}state_tracker.last_texture_index_valid_at_texflush = state_tracker.texflush_counter;{NL}"
    f"{T}state_tracker.texflush_counter_pending = false;{NL}"
    f"{T}return texture_index;{NL}")]

# ---- flush_render_pass entry ----
e_entry = [(
    f"void GSInterface::flush_render_pass(FlushReason reason){NL}{{{NL}"
    f"{T}ParallelGS::RenderPass rp = {{}};{NL}",
    f"void GSInterface::flush_render_pass(FlushReason reason){NL}{{{NL}"
    f"{T}// G40 wall entry: snapshot only (no map: a pre-read would recurse into{NL}"
    f"{T}// mark_submission_timeline and consume the pending prims in an inner{NL}"
    f"{T}// flush. O2 pre-bytes come from the O2x post-flush chain, see end.).{NL}"
    f"{T}// Inner (recursive) calls see g40_busy and skip all G40 work.{NL}"
    f"{T}bool g40_outer = !g40_busy && g40_enabled();{NL}"
    f"{T}unsigned g40_ford = 0;{NL}"
    f"{T}bool g40_is_comp = false;{NL}"
    f"{T}int g40_cord = -1;{NL}"
    f"{T}unsigned g40_entry_prims = 0;{NL}"
    f"{T}Vulkan::ImageHandle g40_tex_hold;{NL}"
    f"{T}uint32_t g40_tex_w = 0;{NL}"
    f"{T}uint32_t g40_tex_h = 0;{NL}"
    f"{T}if (g40_outer){NL}{T}{{{NL}"
    f"{T}{T}g40_ford = g40_next_flush_ord++;{NL}"
    f"{T}{T}g40_entry_prims = render_pass.primitive_count;{NL}"
    f"{T}{T}if (render_pass.primitive_count){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}for (uint32_t g40_i = 0; g40_i < render_pass.num_instances; g40_i++){NL}"
    f"{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}if (render_pass.instances[g40_i].frame.desc.FBP == 112){NL}"
    f"{T}{T}{T}{T}{T}g40_is_comp = true;{NL}"
    f"{T}{T}{T}}}{NL}{T}{T}}}{NL}"
    f"{T}{T}if (g40_is_comp){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}g40_busy = true;{NL}"
    f"{T}{T}{T}g40_cord = int(g40_next_comp_ord++);{NL}"
    f"{T}{T}{T}if (!render_pass.held_images.empty() && !render_pass.tex_infos.empty() && render_pass.held_images[0]){NL}"
    f"{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}g40_tex_hold = render_pass.held_images[0];{NL}"
    f"{T}{T}{T}{T}g40_tex_w = render_pass.held_images[0]->get_width();{NL}"
    f"{T}{T}{T}{T}g40_tex_h = render_pass.held_images[0]->get_height();{NL}"
    f"{T}{T}{T}}}{NL}"
    f"{T}{T}}}{NL}{T}}}{NL}"
    f"{T}ParallelGS::RenderPass rp = {{}};{NL}")]

# ---- flush_render_pass end ----
e_end = [(
    f"{T}renderer.reserve_primitive_buffers(MaxPrimitivesPerFlush);{NL}"
    f"{T}render_pass.positions = renderer.get_reserved_vertex_positions();{NL}"
    f"{T}render_pass.attributes = renderer.get_reserved_vertex_attributes();{NL}"
    f"{T}render_pass.prim = renderer.get_reserved_primitive_attributes();{NL}}}{NL}",
    f"{T}renderer.reserve_primitive_buffers(MaxPrimitivesPerFlush);{NL}"
    f"{T}render_pass.positions = renderer.get_reserved_vertex_positions();{NL}"
    f"{T}render_pass.attributes = renderer.get_reserved_vertex_attributes();{NL}"
    f"{T}render_pass.prim = renderer.get_reserved_primitive_attributes();{NL}"
    f"{T}if (g40_outer) // G40 wall end: O1/O5/O4m every flush, O3/O3b/O4 at cord {{0,1}}{NL}{T}{{{NL}"
    f"{T}{T}LOGI(\"G40: O1 ford=%u cord=%d prims=%u submitted=%u inst=%u tex=%u seen=%u adc=%u deg=%u bb=%u fuse=%u acc=%u.\\n\",{NL}"
    f"{T}{T}     g40_ford, g40_cord, g40_entry_prims, (unsigned)rp.num_primitives,{NL}"
    f"{T}{T}     (unsigned)rp.num_instances, (unsigned)rp.num_textures,{NL}"
    f"{T}{T}     g40_k_seen, g40_k_adc, g40_k_deg, g40_k_bb, g40_k_fuse, g40_k_acc);{NL}"
    f"{T}{T}g40_k_seen = 0;{NL}{T}{T}g40_k_adc = 0;{NL}{T}{T}g40_k_deg = 0;{NL}"
    f"{T}{T}g40_k_bb = 0;{NL}{T}{T}g40_k_fuse = 0;{NL}{T}{T}g40_k_acc = 0;{NL}"
    f"{T}{T}if (g40_is_comp){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}LOGI(\"G40: O5 ford=%u cord=%d reason=%s label=%u states=%u tex=%u fbmode=%u tilelog2=%u.\\n\",{NL}"
    f"{T}{T}{T}     g40_ford, g40_cord, g40_reason_str(reason), (unsigned)rp.label_key,{NL}"
    f"{T}{T}{T}     (unsigned)rp.num_states, (unsigned)rp.num_textures, (unsigned)rp.feedback_mode,{NL}"
    f"{T}{T}{T}     (unsigned)rp.coarse_tile_size_log2);{NL}"
    f"{T}{T}{T}for (uint32_t g40_i = 0; g40_i < rp.num_instances; g40_i++){NL}"
    f"{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}LOGI(\"G40: O5 ford=%u cord=%d inst=%u FBP=%u FBW=%u PSM=%u FBMSK=%08x ZBP=%u ZMSK=%u opq=%08x chshuf=%u zsens=%u zwr=%u ssx=%u ssy=%u base=%u,%u ctiles=%ux%u.\\n\",{NL}"
    f"{T}{T}{T}{T}     g40_ford, g40_cord, g40_i,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.frame.desc.FBP,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.frame.desc.FBW,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.frame.desc.PSM,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.frame.desc.FBMSK,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.z.desc.ZBP,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].fb.z.desc.ZMSK,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].opaque_fbmask,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].channel_shuffle,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].z_sensitive,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].z_write,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].sampling_rate_x_log2,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].sampling_rate_y_log2,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].base_x, (unsigned)rp.instances[g40_i].base_y,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].coarse_tiles_width,{NL}"
    f"{T}{T}{T}{T}     (unsigned)rp.instances[g40_i].coarse_tiles_height);{NL}"
    f"{T}{T}{T}}}{NL}"
    f"{T}{T}{T}LOGI(\"G40: O4m ford=%u cord=%d texdims=%ux%u created=%u longterm=%u tbp0=%u tbw=%u psm=%u lv=%u smp=%u reuse=%u hash=%016llx.\\n\",{NL}"
    f"{T}{T}{T}     g40_ford, g40_cord, g40_tex_w, g40_tex_h,{NL}"
    f"{T}{T}{T}     (unsigned)g40_tex_created, (unsigned)g40_tex_longterm,{NL}"
    f"{T}{T}{T}     g40_tex_tbp0, g40_tex_tbw, g40_tex_psm, g40_tex_levels, g40_tex_samples,{NL}"
    f"{T}{T}{T}     g40_tex_reuse, (unsigned long long)g40_tex_hash);{NL}"
    f"{T}{T}{T}g40_tex_reuse = 0;{NL}"
    f"{T}{T}{T}if (g40_cord == 0 || g40_cord == 1){NL}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}// G40 O2: literal pre-composite B from the O2x chain (B is{NL}"
    f"{T}{T}{T}{T}// untouched between flushes: scenes are single-inst FBP0{NL}"
    f"{T}{T}{T}{T}// (G11) and vpage excludes 112..223 except via composite).{NL}"
    f"{T}{T}{T}{T}if (g40_last_valid){NL}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O2 ford=%u cord=%d B pre-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x srcford=%u.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}     g40_ford, g40_cord, (unsigned long long)g40_last_f, (unsigned)g40_last_z,{NL}"
    f"{T}{T}{T}{T}{T}     g40_last_head[0], g40_last_head[1], g40_last_head[2], g40_last_head[3],{NL}"
    f"{T}{T}{T}{T}{T}     g40_last_head[4], g40_last_head[5], g40_last_head[6], g40_last_head[7],{NL}"
    f"{T}{T}{T}{T}{T}     g40_last_ford);{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}else{NL}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O2 ford=%u cord=%d B pre=load (no prior flush; eea04488c453e75b/149721 receipted).\\n\",{NL}"
    f"{T}{T}{T}{T}{T}     g40_ford, g40_cord);{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}// G40 probe: record GPU-side copies, force full submit + wait,{NL}"
    f"{T}{T}{T}{T}// then read host B (O3), gpu B (O3b) and texture bytes (O4).{NL}"
    f"{T}{T}{T}{T}bool g40_rec = renderer.g40_record_probes(g40_tex_hold.get(), g40_tex_w, g40_tex_h);{NL}"
    f"{T}{T}{T}{T}uint64_t g40_tl = tracker.mark_submission_timeline(FlushReason::HostAccess);{NL}"
    f"{T}{T}{T}{T}renderer.flush_submit(g40_tl);{NL}"
    f"{T}{T}{T}{T}renderer.wait_timeline(g40_tl);{NL}"
    f"{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}const size_t g40_base = 112 * 8192;{NL}"
    f"{T}{T}{T}{T}{T}const size_t g40_n = 112 * 8192;{NL}"
    f"{T}{T}{T}{T}{T}const uint8_t *g40_vram = static_cast<const uint8_t *>(map_vram_read(g40_base, g40_n));{NL}"
    f"{T}{T}{T}{T}{T}if (g40_vram){NL}{T}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}{T}uint64_t g40_f = 0;{NL}"
    f"{T}{T}{T}{T}{T}{T}uint32_t g40_z = 0;{NL}"
    f"{T}{T}{T}{T}{T}{T}g40_fnv(g40_vram, g40_n, g40_f, g40_z);{NL}"
    f"{T}{T}{T}{T}{T}{T}LOGI(\"G40: O3 ford=%u cord=%d rec=%u B post-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}{T}     g40_ford, g40_cord, (unsigned)g40_rec,{NL}"
    f"{T}{T}{T}{T}{T}{T}     (unsigned long long)g40_f, (unsigned)g40_z,{NL}"
    f"{T}{T}{T}{T}{T}{T}     g40_vram[0], g40_vram[1], g40_vram[2], g40_vram[3],{NL}"
    f"{T}{T}{T}{T}{T}{T}     g40_vram[4], g40_vram[5], g40_vram[6], g40_vram[7]);{NL}"
    f"{T}{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}{T}else{NL}{T}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}{T}LOGI(\"G40: O3 ford=%u cord=%d rec=%u map failed.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}{T}     g40_ford, g40_cord, (unsigned)g40_rec);{NL}"
    f"{T}{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}uint64_t g40_tfnv = 0;{NL}"
    f"{T}{T}{T}{T}{T}uint64_t g40_gfnv = 0;{NL}"
    f"{T}{T}{T}{T}{T}uint32_t g40_tnz = 0;{NL}"
    f"{T}{T}{T}{T}{T}uint32_t g40_gnz = 0;{NL}"
    f"{T}{T}{T}{T}{T}uint8_t g40_thead[8] = {{ 0, 0, 0, 0, 0, 0, 0, 0 }};{NL}"
    f"{T}{T}{T}{T}{T}uint8_t g40_ghead[8] = {{ 0, 0, 0, 0, 0, 0, 0, 0 }};{NL}"
    f"{T}{T}{T}{T}{T}bool g40_fin = renderer.g40_finish_probes(g40_tfnv, g40_tnz, g40_thead,{NL}"
    f"{T}{T}{T}{T}{T}                                          g40_gfnv, g40_gnz, g40_ghead);{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O3b ford=%u cord=%d fin=%u gpuB-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}     g40_ford, g40_cord, (unsigned)g40_fin,{NL}"
    f"{T}{T}{T}{T}{T}     (unsigned long long)g40_gfnv, (unsigned)g40_gnz,{NL}"
    f"{T}{T}{T}{T}{T}     g40_ghead[0], g40_ghead[1], g40_ghead[2], g40_ghead[3],{NL}"
    f"{T}{T}{T}{T}{T}     g40_ghead[4], g40_ghead[5], g40_ghead[6], g40_ghead[7]);{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O4 ford=%u cord=%d fin=%u tex-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x dims=%ux%u.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}     g40_ford, g40_cord, (unsigned)g40_fin,{NL}"
    f"{T}{T}{T}{T}{T}     (unsigned long long)g40_tfnv, (unsigned)g40_tnz,{NL}"
    f"{T}{T}{T}{T}{T}     g40_thead[0], g40_thead[1], g40_thead[2], g40_thead[3],{NL}"
    f"{T}{T}{T}{T}{T}     g40_thead[4], g40_thead[5], g40_thead[6], g40_thead[7],{NL}"
    f"{T}{T}{T}{T}{T}     g40_tex_w, g40_tex_h);{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}}}{NL}"
    f"{T}{T}{T}g40_busy = false;{NL}"
    f"{T}{T}}}{NL}"
    f"{T}{T}else if (g40_entry_prims > 0){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}// G40 O2x: inter-flush B at scene-flush end (safe: prims reset;{NL}"
    f"{T}{T}{T}// busy-guarded against recursion). Pure read expected (A-only{NL}"
    f"{T}{T}{T}// work leaves no B writes pending); the bytes self-report.{NL}"
    f"{T}{T}{T}g40_busy = true;{NL}"
    f"{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}const size_t g40_base = 112 * 8192;{NL}"
    f"{T}{T}{T}{T}const size_t g40_n = 112 * 8192;{NL}"
    f"{T}{T}{T}{T}const uint8_t *g40_vram = static_cast<const uint8_t *>(map_vram_read(g40_base, g40_n));{NL}"
    f"{T}{T}{T}{T}if (g40_vram){NL}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}uint64_t g40_f = 0;{NL}"
    f"{T}{T}{T}{T}{T}uint32_t g40_z = 0;{NL}"
    f"{T}{T}{T}{T}{T}g40_fnv(g40_vram, g40_n, g40_f, g40_z);{NL}"
    f"{T}{T}{T}{T}{T}g40_last_valid = true;{NL}"
    f"{T}{T}{T}{T}{T}g40_last_ford = g40_ford;{NL}"
    f"{T}{T}{T}{T}{T}g40_last_f = g40_f;{NL}"
    f"{T}{T}{T}{T}{T}g40_last_z = g40_z;{NL}"
    f"{T}{T}{T}{T}{T}for (unsigned g40_b = 0; g40_b < 8; g40_b++){NL}"
    f"{T}{T}{T}{T}{T}{T}g40_last_head[g40_b] = g40_vram[g40_b];{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O2x ford=%u B postflush-fnv=%016llx nz=%u head=%02x%02x%02x%02x%02x%02x%02x%02x.\\n\",{NL}"
    f"{T}{T}{T}{T}{T}     g40_ford, (unsigned long long)g40_f, (unsigned)g40_z,{NL}"
    f"{T}{T}{T}{T}{T}     g40_vram[0], g40_vram[1], g40_vram[2], g40_vram[3],{NL}"
    f"{T}{T}{T}{T}{T}     g40_vram[4], g40_vram[5], g40_vram[6], g40_vram[7]);{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}{T}else{NL}{T}{T}{T}{T}{{{NL}"
    f"{T}{T}{T}{T}{T}LOGI(\"G40: O2x ford=%u map failed.\\n\", g40_ford);{NL}"
    f"{T}{T}{T}{T}}}{NL}"
    f"{T}{T}{T}}}{NL}"
    f"{T}{T}{T}g40_busy = false;{NL}"
    f"{T}{T}}}{NL}"
    f"{T}}}{NL}}}{NL}")]

# ---- gs_renderer.hpp ----
e_hpub = [(
    f"{T}// Readback stage.{NL}"
    f"{T}void flush_readback(const uint32_t *page_indices, uint32_t num_indices);{NL}",
    f"{T}// Readback stage.{NL}"
    f"{T}void flush_readback(const uint32_t *page_indices, uint32_t num_indices);{NL}{NL}"
    f"{T}// G40 wall (env-gated PGS_G40_WALL; called only when enabled).{NL}"
    f"{T}// Record GPU-side probe copies into the open direct command buffer,{NL}"
    f"{T}// then map staging and hash bytes after the caller's submit+wait.{NL}"
    f"{T}// Observation-only: transfer copies + barriers; texture layout restored.{NL}"
    f"{T}bool g40_record_probes(const Vulkan::Image *tex_image, uint32_t tex_w, uint32_t tex_h);{NL}"
    f"{T}bool g40_finish_probes(uint64_t &tex_fnv, uint32_t &tex_nz, uint8_t tex_head[8],{NL}"
    f"{T}                       uint64_t &gpu_fnv, uint32_t &gpu_nz, uint8_t gpu_head[8]);{NL}")]
e_hpriv = [(
    f"{T}Vulkan::CommandBufferHandle binning_cmd;{NL}",
    f"{T}Vulkan::CommandBufferHandle binning_cmd;{NL}"
    f"{T}// G40 wall probe staging (one-shot per firing; reassigned only after GPU wait).{NL}"
    f"{T}Vulkan::BufferHandle g40_tex_staging;{NL}"
    f"{T}Vulkan::BufferHandle g40_gpu_staging;{NL}"
    f"{T}uint32_t g40_tex_pw = 0;{NL}"
    f"{T}uint32_t g40_tex_ph = 0;{NL}"
    f"{T}bool g40_tex_pvalid = false;{NL}")]

# ---- gs_renderer.cpp ----
g40_impl = (
    f"static void g40_fnv_hash(const uint8_t *p, size_t n, uint64_t &fnv, uint32_t &nz, uint8_t head[8]){NL}{{{NL}"
    f"{T}fnv = 1469598103934665603ull; // G29-E1 truncated basis (comparability){NL}"
    f"{T}nz = 0;{NL}"
    f"{T}for (size_t i = 0; i < n; i++){NL}{T}{{{NL}"
    f"{T}{T}fnv ^= p[i];{NL}{T}{T}fnv *= 1099511628211ull;{NL}{T}{T}nz += p[i] != 0;{NL}{T}}}{NL}"
    f"{T}for (unsigned i = 0; i < 8 && i < n; i++){NL}{T}{T}head[i] = p[i];{NL}}}{NL}{NL}"
    f"bool GSRenderer::g40_record_probes(const Vulkan::Image *tex_image, uint32_t tex_w, uint32_t tex_h){NL}{{{NL}"
    f"{T}if (!device || !direct_cmd){NL}{T}{T}return false;{NL}"
    f"{T}auto &cmd = *direct_cmd;{NL}"
    f"{T}g40_tex_pvalid = false;{NL}"
    f"{T}g40_tex_pw = 0;{NL}"
    f"{T}g40_tex_ph = 0;{NL}{NL}"
    f"{T}// Order vs all prior storage/transfer writes (shading wrote gpu-B earlier in this stream).{NL}"
    f"{T}cmd.barrier(VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_2_TRANSFER_BIT,{NL}"
    f"{T}            VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT | VK_ACCESS_2_TRANSFER_WRITE_BIT,{NL}"
    f"{T}            VK_PIPELINE_STAGE_2_TRANSFER_BIT, VK_ACCESS_2_TRANSFER_READ_BIT);{NL}{NL}"
    f"{T}// Probe 1: gpu-side B pages (112..223) -> staging.{NL}"
    f"{T}{{{NL}"
    f"{T}{T}Vulkan::BufferCreateInfo info = {{}};{NL}"
    f"{T}{T}info.size = VkDeviceSize(112) * VkDeviceSize(PageSize);{NL}"
    f"{T}{T}info.domain = Vulkan::BufferDomain::CachedHost;{NL}"
    f"{T}{T}info.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;{NL}"
    f"{T}{T}g40_gpu_staging = device->create_buffer(info);{NL}"
    f"{T}{T}if (!g40_gpu_staging){NL}{T}{T}{T}return false;{NL}"
    f"{T}{T}// NOTE: not copy_blocks (it copies VRAM offset -> same offset, but the{NL}"
    f"{T}{T}// staging buffer is compact: B pages land at staging offset 0).{NL}"
    f"{T}{T}cmd.begin_region(\"g40-gpuB\");{NL}"
    f"{T}{T}cmd.copy_buffer(*g40_gpu_staging, 0, *buffers.gpu,{NL}"
    f"{T}{T}                VkDeviceSize(112) * VkDeviceSize(PageSize),{NL}"
    f"{T}{T}                VkDeviceSize(112) * VkDeviceSize(PageSize));{NL}"
    f"{T}{T}cmd.end_region();{NL}"
    f"{T}}}{NL}{NL}"
    f"{T}// Probe 2: composite texture image (level/layer 0) -> staging.{NL}"
    f"{T}if (tex_image && tex_w && tex_h){NL}{T}{{{NL}"
    f"{T}{T}VkDeviceSize n = VkDeviceSize(tex_w) * VkDeviceSize(tex_h) * 4;{NL}"
    f"{T}{T}Vulkan::BufferCreateInfo info = {{}};{NL}"
    f"{T}{T}info.size = n;{NL}"
    f"{T}{T}info.domain = Vulkan::BufferDomain::CachedHost;{NL}"
    f"{T}{T}info.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;{NL}"
    f"{T}{T}g40_tex_staging = device->create_buffer(info);{NL}"
    f"{T}{T}if (!g40_tex_staging){NL}{T}{T}{T}return false;{NL}"
    f"{T}{T}cmd.begin_region(\"g40-tex\");{NL}"
    f"{T}{T}cmd.image_barrier(*tex_image, VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,{NL}"
    f"{T}{T}                  VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT, VK_ACCESS_2_SHADER_SAMPLED_READ_BIT,{NL}"
    f"{T}{T}                  VK_PIPELINE_STAGE_2_TRANSFER_BIT, VK_ACCESS_2_TRANSFER_READ_BIT);{NL}"
    f"{T}{T}VkImageSubresourceLayers sub = {{}};{NL}"
    f"{T}{T}sub.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;{NL}"
    f"{T}{T}sub.mipLevel = 0;{NL}"
    f"{T}{T}sub.baseArrayLayer = 0;{NL}"
    f"{T}{T}sub.layerCount = 1;{NL}"
    f"{T}{T}VkOffset3D off = {{}};{NL}"
    f"{T}{T}VkExtent3D ext = {{ tex_w, tex_h, 1 }};{NL}"
    f"{T}{T}cmd.copy_image_to_buffer(*g40_tex_staging, *tex_image, 0, off, ext, 0, 0, sub);{NL}"
    f"{T}{T}cmd.image_barrier(*tex_image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL,{NL}"
    f"{T}{T}                  VK_PIPELINE_STAGE_2_TRANSFER_BIT, VK_ACCESS_2_TRANSFER_READ_BIT,{NL}"
    f"{T}{T}                  VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT, VK_ACCESS_2_SHADER_SAMPLED_READ_BIT);{NL}"
    f"{T}{T}cmd.end_region();{NL}"
    f"{T}{T}g40_tex_pw = tex_w;{NL}"
    f"{T}{T}g40_tex_ph = tex_h;{NL}"
    f"{T}{T}g40_tex_pvalid = true;{NL}"
    f"{T}}}{NL}{NL}"
    f"{T}// Make staging writes visible to host reads after the wait.{NL}"
    f"{T}cmd.barrier(VK_PIPELINE_STAGE_2_TRANSFER_BIT, VK_ACCESS_2_TRANSFER_WRITE_BIT,{NL}"
    f"{T}            VK_PIPELINE_STAGE_2_HOST_BIT, VK_ACCESS_2_HOST_READ_BIT);{NL}"
    f"{T}return true;{NL}}}{NL}{NL}"
    f"bool GSRenderer::g40_finish_probes(uint64_t &tex_fnv, uint32_t &tex_nz, uint8_t tex_head[8],{NL}"
    f"                                   uint64_t &gpu_fnv, uint32_t &gpu_nz, uint8_t gpu_head[8]){NL}{{{NL}"
    f"{T}tex_fnv = 0;{NL}{T}tex_nz = 0;{NL}{T}gpu_fnv = 0;{NL}{T}gpu_nz = 0;{NL}"
    f"{T}for (unsigned i = 0; i < 8; i++){NL}{T}{T}tex_head[i] = gpu_head[i] = 0;{NL}"
    f"{T}if (!device || !g40_gpu_staging){NL}{T}{{{NL}"
    f"{T}{T}LOGE(\"G40: gpu staging missing.\\n\");{NL}{T}{T}return false;{NL}{T}}}{NL}"
    f"{T}auto *gpu = static_cast<const uint8_t *>(device->map_host_buffer(*g40_gpu_staging, Vulkan::MEMORY_ACCESS_READ_BIT));{NL}"
    f"{T}if (!gpu){NL}{T}{{{NL}"
    f"{T}{T}LOGE(\"G40: gpu staging map failed.\\n\");{NL}{T}{T}return false;{NL}{T}}}{NL}"
    f"{T}g40_fnv_hash(gpu, size_t(112) * PageSize, gpu_fnv, gpu_nz, gpu_head);{NL}"
    f"{T}if (g40_tex_pvalid && g40_tex_staging){NL}{T}{{{NL}"
    f"{T}{T}auto *tex = static_cast<const uint8_t *>(device->map_host_buffer(*g40_tex_staging, Vulkan::MEMORY_ACCESS_READ_BIT));{NL}"
    f"{T}{T}if (!tex){NL}{T}{T}{{{NL}"
    f"{T}{T}{T}LOGE(\"G40: tex staging map failed.\\n\");{NL}{T}{T}{T}return false;{NL}{T}{T}}}{NL}"
    f"{T}{T}g40_fnv_hash(tex, size_t(g40_tex_pw) * size_t(g40_tex_ph) * 4, tex_fnv, tex_nz, tex_head);{NL}"
    f"{T}}}{NL}"
    f"{T}return true;{NL}}}{NL}{NL}"
)
e_impl = [(
    f"void GSRenderer::flush_readback(const uint32_t *page_indices, uint32_t num_indices){NL}{{{NL}",
    g40_impl + f"void GSRenderer::flush_readback(const uint32_t *page_indices, uint32_t num_indices){NL}{{{NL}")]

if __name__ == "__main__":
    n = 0
    n += edit(IFACE, e_inc + e_statics + e_kick + e_bb1 + e_fuse + e_bb2 + e_acc +
              e_texa + e_texb + e_texc + e_texd + e_texe + e_texf + e_entry + e_end)
    n += edit(RHP, e_hpub + e_hpriv)
    n += edit(RCP, e_impl)
    print(("DRY-OK " if DRY else "APPLIED ") + str(n) + " edits")
