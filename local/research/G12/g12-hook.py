#!/usr/bin/env python3
"""G12 log-only hook: per-draw FBP/TBP trace + present markers in pcsx2-g7.

Applies 6 exact-match hunks (asserts count==1 each, aborts otherwise):
  H1 GSRendererHW::Draw() entry      -> G12_DRAW   (s_n, FRAME FBP/FBW/PSM, TEX0 TBP0/TBW/PSM, TME, PRIM, verts)
  H2 Draw() IsBadFrame early return  -> G12_SKIP   (reason=badframe)
  H3 Draw() black-point early return -> G12_SKIP   (reason=blackpoint)
  H4 GSRendererHW::DrawPrims() entry -> G12_RASTER (s_n, rt/ds/tex target TBP0, tex TBW)
  H5 GSRendererHW::VSync() entry     -> G12_VSYNC  (field, idle, s_n, DISPFB0 FBP)
  H6 GSDumpReplayer VSync packet     -> G12_DUMP_VSYNC (dump_frame)

Log-only: Console.WriteLn only (established G8 channel, emulog-captured).
Idempotent: aborts if G12_DRAW already present.
"""
import sys

HW = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/Renderers/HW/GSRendererHW.cpp"
RP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GSDumpReplayer.cpp"

H1_FIND = "\tm_cached_ctx.FRAME = context->FRAME;\n\tm_cached_ctx.ZBUF = context->ZBUF;\n"
H1_ADD = (
    "\t// G12: per-draw order trace (log-only).\n"
    '\tConsole.WriteLn("G12_DRAW n=%llu FBP=%u FBW=%u FPSM=%u TBP0=%u TBW=%u TPSM=%u TME=%u PRIM=%u verts=%u",\n'
    "\t\tstatic_cast<unsigned long long>(s_n), static_cast<unsigned>(context->FRAME.FBP),\n"
    "\t\tstatic_cast<unsigned>(context->FRAME.FBW), static_cast<unsigned>(context->FRAME.PSM),\n"
    "\t\tstatic_cast<unsigned>(context->TEX0.TBP0), static_cast<unsigned>(context->TEX0.TBW),\n"
    "\t\tstatic_cast<unsigned>(context->TEX0.PSM), static_cast<unsigned>(m_draw_env->PRIM.TME),\n"
    "\t\tstatic_cast<unsigned>(m_draw_env->PRIM.PRIM), vtx_buff.tail - vtx_buff.head);\n"
)

H2_GLINS = '\t\tGL_INS("HW: Warning skipping a draw call (%lld)", s_n);\n'
# H2 anchor includes the just-applied H1 block: this IsBadFrame return is the
# one at Draw() entry (the same GL_INS line appears 2x more, deeper in Draw).
H2_ADD = '\t\tConsole.WriteLn("G12_SKIP n=%llu reason=badframe", static_cast<unsigned long long>(s_n));\n'

H3_FIND = "m_env.PRIM.PRIM != GS_POINTLIST)\n\t\treturn;\n"
# Braced: the bare `if (...) return;` must keep the return conditional.
H3_REPL = ("m_env.PRIM.PRIM != GS_POINTLIST)\n"
           "\t\t{\n"
           '\t\t\tConsole.WriteLn("G12_SKIP n=%llu reason=blackpoint", static_cast<unsigned long long>(s_n));\n'
           "\t\t\treturn;\n"
           "\t\t}\n")

H5_FIND = "void GSRendererHW::VSync(u32 field, bool registers_written, bool idle_frame)\n{\n"
H5_ADD = (
    "\t// G12: HW present-side marker (log-only).\n"
    '\tConsole.WriteLn("G12_VSYNC field=%u idle=%u n=%llu DISPFB0_FBP=%u",\n'
    "\t\tfield, idle_frame ? 1u : 0u, static_cast<unsigned long long>(s_n),\n"
    "\t\tstatic_cast<unsigned>(m_regs->DISP[0].DISPFB.FBP));\n"
)

H4_ADD = (
    "\t// G12: actual-rasterization trace (log-only).\n"
    '\tConsole.WriteLn("G12_RASTER n=%llu rtTBP0=%d dsTBP0=%d texTBP0=%d texTBW=%d",\n'
    "\t\tstatic_cast<unsigned long long>(s_n), rt ? static_cast<int>(rt->m_TEX0.TBP0) : -1,\n"
    "\t\tds ? static_cast<int>(ds->m_TEX0.TBP0) : -1, tex ? static_cast<int>(tex->m_TEX0.TBP0) : -1,\n"
    "\t\ttex ? static_cast<int>(tex->m_TEX0.TBW) : -1);\n"
)

H6_FIND = "s_dump_frame_number++;\n"
H6_ADD_TMPL = '{ind}Console.WriteLn("G12_DUMP_VSYNC dump_frame=%u", s_dump_frame_number);\n'


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, f"{name}: anchor count={n}, want 1"
    return text.replace(find, find + add, 1)


def main():
    hw = open(HW, encoding="utf-8").read()
    assert "G12_DRAW" not in hw, "hook already applied to GSRendererHW.cpp"
    hw = apply_after_once(hw, H1_FIND, H1_ADD, "H1")
    h2_find = H1_ADD + "\n\tif (IsBadFrame())\n\t{\n" + H2_GLINS
    hw = apply_after_once(hw, h2_find, H2_ADD, "H2")
    n = hw.count(H3_FIND)
    assert n == 1, f"H3: anchor count={n}, want 1"
    hw = hw.replace(H3_FIND, H3_REPL, 1)
    # H4: anchor on the full DrawPrims definition signature (another function
    # in this file shares the same parameter-list tail).
    h4_find = "void GSRendererHW::DrawPrims(GSTextureCache::Target* rt, GSTextureCache::Target* ds, GSTextureCache::Source* tex, const TextureMinMaxResult& tmm)\n{\n"
    n = hw.count(h4_find)
    assert n == 1, f"H4: anchor count={n}, want 1"
    hw = hw.replace(h4_find, h4_find + H4_ADD, 1)
    hw = apply_after_once(hw, H5_FIND, H5_ADD, "H5")
    open(HW, "w", encoding="utf-8").write(hw)

    rp = open(RP, encoding="utf-8").read()
    assert "G12_DUMP_VSYNC" not in rp, "hook already applied to GSDumpReplayer.cpp"
    n = rp.count(H6_FIND)
    assert n == 1, f"H6: anchor count={n}, want 1"
    idx = rp.index(H6_FIND)
    bol = rp.rindex("\n", 0, idx) + 1
    ind = rp[bol:idx]
    assert ind.strip() == "", f"H6: unexpected indent {ind!r}"
    rp = rp.replace(H6_FIND, H6_FIND + H6_ADD_TMPL.format(ind=ind), 1)
    open(RP, "w", encoding="utf-8").write(rp)

    print("G12 hook applied: H1-H6 ok")


if __name__ == "__main__":
    main()
