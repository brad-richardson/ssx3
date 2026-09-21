#!/usr/bin/env python3
# G11b: second bounded read-only hunk (H4) on gs/gs_interface.cpp, LOGI-only.
# In flush_render_pass, before renderer.flush_rendering(rp): log the recorded
# batch identity -- prims, per-instance draw-target FRAME (FBP/FBW/PSM), and
# per-texture TEX0 (TBP0/TBW/PSM/CBP). Decides the feedback link DIRECTLY:
# a FRAME FBP=112 pass sampling TEX0 TBP0=0 proves the on-screen composite
# reads the deferred off-screen sprite batch (the one-vsync lag mechanism).
import sys

PATH = "/Volumes/Extreme SSD/parallel-gs-g7/gs/gs_interface.cpp"
FIND = "\t\trenderer.flush_rendering(rp);\n"
REPL = """\t\t{
\t\t\t// G11b local experiment hook (not upstream): recorded-batch identity.
\t\t\tLOGI("G11: record prims=%u inst=%u tex=%u tex0=%u\\n", rp.num_primitives,
\t\t\t     rp.num_instances, rp.num_textures, (unsigned)render_pass.tex0_infos.size());
\t\t\tfor (uint32_t g11_i = 0; g11_i < rp.num_instances; g11_i++)
\t\t\t\tLOGI("G11:   inst %u FRAME FBP=%u FBW=%u PSM=%u\\n", g11_i,
\t\t\t\t     (unsigned)rp.instances[g11_i].fb.frame.desc.FBP,
\t\t\t\t     (unsigned)rp.instances[g11_i].fb.frame.desc.FBW,
\t\t\t\t     (unsigned)rp.instances[g11_i].fb.frame.desc.PSM);
\t\t\tfor (uint32_t g11_j = 0; g11_j < render_pass.tex0_infos.size(); g11_j++)
\t\t\t\tLOGI("G11:   tex %u TBP0=%u TBW=%u TPSM=%u CBP=%u\\n", g11_j,
\t\t\t\t     (unsigned)render_pass.tex0_infos[g11_j].TBP0,
\t\t\t\t     (unsigned)render_pass.tex0_infos[g11_j].TBW,
\t\t\t\t     (unsigned)render_pass.tex0_infos[g11_j].PSM,
\t\t\t\t     (unsigned)render_pass.tex0_infos[g11_j].CBP);
\t\t}
\t\trenderer.flush_rendering(rp);
"""

def main():
    src = open(PATH).read()
    c = src.count(FIND)
    assert c == 1, f"H4: count={c}"
    open(PATH, "w").write(src.replace(FIND, REPL))
    print("H4 applied")

if __name__ == "__main__":
    main()
