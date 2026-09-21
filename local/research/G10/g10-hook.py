#!/usr/bin/env python3
# G10: replayer hook extension (8-scanout series + per-pass stats reset).
# Applies 6 exact-match hunks to tools/gs_dump_replayer.cpp in the SSD clone.
# Local experiment change, uncommitted (G7/G8 pattern); recipe mirrored.
import io, sys

P = "/Volumes/Extreme SSD/parallel-gs-g7/tools/gs_dump_replayer.cpp"
s = io.open(P, encoding="utf-8").read()

def hunk(tag, before, after):
    global s
    assert s.count(before) == 1, (tag, s.count(before))
    s = s.replace(before, after)
    print(f"hunk {tag} ok")

# H1: vector include
hunk("H1-include",
 '#include "timer.hpp"\n#include <stdlib.h>',
 '#include "timer.hpp"\n#include <vector>\n#include <stdlib.h>')

# H2: G10 hook paragraph (G8 comment kept)
hunk("H2-comment",
 "\t// after end_ns. Readback mirrors gs_repro_replayer.cpp (as G7's hook did).\n\tauto save_scanout_ppm",
 "\t// after end_ns. Readback mirrors gs_repro_replayer.cpp (as G7's hook did).\n"
 "\t// G10 local experiment hook (not upstream): bounded last-pass scanout\n"
 "\t// series (one PPM per iterate-true vsync) + per-pass stats resets so\n"
 "\t// cold/warm passes separate (G8's stacked takes are corrected in G10).\n"
 "\t// Loop-body execution count unchanged; PPM I/O stays after end_ns.\n\tauto save_scanout_ppm")

# H3: series stash replaces first-only stash
hunk("H3-stash",
 "\tiface.consume_flush_stats();\n\tScanoutResult g8_first_shot;\n\tbool g8_first_saved = false;\n\tunsigned g8_seq = 0;\n",
 "\tiface.consume_flush_stats();\n\tstd::vector<ScanoutResult> g10_series;\n\tg10_series.reserve(16);\n\tunsigned g8_seq = 0;\n")

# H4: per-pass reset at each pass start
hunk("H4-reset",
 "\t\tg8_seq = 0;\n\t\tfor (;;)\n",
 "\t\tg8_seq = 0;\n\t\t// G10: per-pass reset (restart() rewinds the file, not the stats).\n"
 "\t\tiface.consume_flush_stats();\n\t\tLOGI(\"G10: pass %u stats reset\\n\", iterations);\n\t\tfor (;;)\n")

# H5: per-vsync consume on EVERY pass (pass-tagged) + series stash on last
hunk("H5-consume",
 "\t\t\tif (g8_last_pass)\n\t\t\t{\n"
 "\t\t\t\tFlushStats g8_st = iface.consume_flush_stats();\n"
 "\t\t\t\tLOGI(\"G8: vsync #%u prims=%u passes=%u pal=%u copies=%u copy_threads=%u copy_barriers=%u scratch=%llu img=%llu\\n\",\n"
 "\t\t\t\t     g8_seq, g8_st.num_primitives, g8_st.num_render_passes, g8_st.num_palette_updates,\n"
 "\t\t\t\t     g8_st.num_copies, g8_st.num_copy_threads, g8_st.num_copy_barriers,\n"
 "\t\t\t\t     (unsigned long long)g8_st.allocated_scratch_memory,\n"
 "\t\t\t\t     (unsigned long long)g8_st.allocated_image_memory);\n"
 "\t\t\t\tif (!g8_first_saved)\n\t\t\t\t{\n"
 "\t\t\t\t\tg8_first_shot = parser.consume_vsync_result();\n"
 "\t\t\t\t\tg8_first_saved = true;\n"
 "\t\t\t\t}\n\t\t\t}\n",
 "\t\t\t{\n"
 "\t\t\t\tFlushStats g8_st = iface.consume_flush_stats();\n"
 "\t\t\t\tLOGI(\"G10: pass %u vsync #%u prims=%u passes=%u pal=%u copies=%u copy_threads=%u copy_barriers=%u scratch=%llu img=%llu\\n\",\n"
 "\t\t\t\t     iterations, g8_seq, g8_st.num_primitives, g8_st.num_render_passes, g8_st.num_palette_updates,\n"
 "\t\t\t\t     g8_st.num_copies, g8_st.num_copy_threads, g8_st.num_copy_barriers,\n"
 "\t\t\t\t     (unsigned long long)g8_st.allocated_scratch_memory,\n"
 "\t\t\t\t     (unsigned long long)g8_st.allocated_image_memory);\n"
 "\t\t\t\tif (g8_last_pass)\n"
 "\t\t\t\t\tg10_series.push_back(parser.consume_vsync_result());\n"
 "\t\t\t}\n")

# H6: series + FIRST/LAST saves (copies share the image; read-only use)
hunk("H6-save",
 "\t// G8: save the stashed first-iterate scanout, then the leftover last vsync\n"
 "\t// (G7's last-vsync behavior, kept). After end_ns; timing untouched.\n"
 "\tif (g8_first_saved)\n"
 "\t\tsave_scanout_ppm(std::move(g8_first_shot), dump_path + \".g8-first.ppm\", \"first\");\n"
 "\telse\n"
 "\t\tLOGE(\"G8: no first iterate-true on the last pass; no first-vsync scanout.\\n\");\n"
 "\tsave_scanout_ppm(parser.consume_vsync_result(), dump_path + \".g8-last.ppm\", \"last\");\n",
 "\t// G10: bounded series (last pass, one PPM per iterate-true) + G8's\n"
 "\t// FIRST/LAST saves kept for continuity (series front/back).\n"
 "\t// After end_ns; timing untouched.\n"
 "\tif (!g10_series.empty())\n\t{\n"
 "\t\tfor (size_t g10_i = 0; g10_i < g10_series.size(); g10_i++)\n\t\t{\n"
 "\t\t\tchar g10_tag[32];\n"
 "\t\t\tsnprintf(g10_tag, sizeof(g10_tag), \"vsync%zu\", g10_i);\n"
 "\t\t\tsave_scanout_ppm(g10_series[g10_i], dump_path + \".g10-\" + g10_tag + \".ppm\", g10_tag);\n"
 "\t\t}\n"
 "\t\tsave_scanout_ppm(g10_series.front(), dump_path + \".g8-first.ppm\", \"first\");\n"
 "\t\tsave_scanout_ppm(g10_series.back(), dump_path + \".g8-last.ppm\", \"last\");\n"
 "\t}\n\telse\n"
 "\t\tLOGE(\"G10: no iterate-true on the last pass; no scanout series.\\n\");\n")

io.open(P, "w", encoding="utf-8").write(s)
print("G10_HOOK_OK")
