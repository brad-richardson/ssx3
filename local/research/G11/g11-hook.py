#!/usr/bin/env python3
# G11: bounded read-only instrumentation on gs/gs_interface.cpp (3 exact-match
# hunks, LOGI-only, no behavior change):
#  H1: GSInterface::flush() logs the interface-side primitive accumulator
#      (prims/instances/states/tex) at submit time. Decides interface-side
#      deferred recording (acc > 0 at flush) vs GPU-side cross-submit
#      visibility (acc == 0 yet scanout lags).
#  H2/H3: a_d_FRAME_1/2 log draw-target identity (FBP/FBW/PSM/FBMSK) on change.
#      Decides single-target draws (FRAME.FBP == DISPFB1.FBP == 112, constant)
#      vs draw-target flip.
import sys

PATH = "/Volumes/Extreme SSD/parallel-gs-g7/gs/gs_interface.cpp"

HUNKS = [
("void GSInterface::flush()\n{\n\tflush_pending_transfer(true);",
 """void GSInterface::flush()
{
\t// G11 local experiment hook (not upstream): read-only accumulator
\t// census at submit time. Log-only; no behavior change.
\tLOGI("G11: flush() acc prims=%u instances=%u states=%u tex=%u\\n",
\t     render_pass.primitive_count, render_pass.num_instances,
\t     (unsigned)render_pass.state_vectors.size(), (unsigned)render_pass.tex_infos.size());
\tflush_pending_transfer(true);"""),
("void GSInterface::a_d_FRAME_1(uint64_t payload)\n{\n\tupdate_internal_register(registers.ctx[0].frame.bits, payload,",
 """void GSInterface::a_d_FRAME_1(uint64_t payload)
{
\t// G11 local experiment hook (not upstream): draw-target identity.
\tif (registers.ctx[0].frame.bits != payload)
\t{
\t\tReg64<FRAMEBits> g11_f;
\t\tg11_f.bits = payload;
\t\tLOGI("G11: FRAME_1 FBP=%u FBW=%u PSM=%u FBMSK=%08x\\n",
\t\t     (unsigned)g11_f.desc.FBP, (unsigned)g11_f.desc.FBW,
\t\t     (unsigned)g11_f.desc.PSM, (unsigned)g11_f.desc.FBMSK);
\t}
\tupdate_internal_register(registers.ctx[0].frame.bits, payload,"""),
("void GSInterface::a_d_FRAME_2(uint64_t payload)\n{\n\tupdate_internal_register(registers.ctx[1].frame.bits, payload,",
 """void GSInterface::a_d_FRAME_2(uint64_t payload)
{
\t// G11 local experiment hook (not upstream): draw-target identity.
\tif (registers.ctx[1].frame.bits != payload)
\t{
\t\tReg64<FRAMEBits> g11_f;
\t\tg11_f.bits = payload;
\t\tLOGI("G11: FRAME_2 FBP=%u FBW=%u PSM=%u FBMSK=%08x\\n",
\t\t     (unsigned)g11_f.desc.FBP, (unsigned)g11_f.desc.FBW,
\t\t     (unsigned)g11_f.desc.PSM, (unsigned)g11_f.desc.FBMSK);
\t}
\tupdate_internal_register(registers.ctx[1].frame.bits, payload,"""),
]

def main():
    src = open(PATH).read()
    for i, (find, repl) in enumerate(HUNKS):
        c = src.count(find)
        assert c == 1, f"hunk H{i+1}: count={c}"
        src = src.replace(find, repl)
        print(f"H{i+1} applied")
    open(PATH, "w").write(src)
    print("wrote", PATH)

if __name__ == "__main__":
    main()
