#!/usr/bin/env python3
# T52 applier: validate-all-then-write. Log-only CD-read + transition-mark hooks.
# Usage on bytesize: python3 t52-hook.py  (aborts unless every anchor count==1)
import sys

CDVD = "/home/brad/pcsx2-g7/pcsx2/pcsx2/CDVD/CDVD.cpp"
GS = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GS.cpp"

T = "\t"
NL = "\n"

T52_INCLUDE = "#include <atomic> // T52" + NL

T52_DECL = (
    NL
    + "// T52: whole-boot CD-read log (log-only). seq + GS-mirror vsync per N-data-read." + NL
    + "extern std::atomic<int> g_t48_vsync; // T52: defined in GS/GS.cpp (T48 vsync mirror)." + NL
    + "static std::atomic<int> g_t52_seq{0}; // T52" + NL
    + "static void t52_cdread(const char* t52kind) // T52" + NL
    + "{ // T52" + NL
    + T + 'Console.WriteLn("T52_CDREAD seq=%d vsync=%d kind=%s lbn=%d sectors=%d blocksize=%d speed=%dx spindle=%s readmode=0x%x dest=-", // T52' + NL
    + T + T + "g_t52_seq.fetch_add(1, std::memory_order_relaxed), g_t48_vsync.load(std::memory_order_relaxed), t52kind, // T52" + NL
    + T + T + 'cdvd.SeekToSector, cdvd.SectorCnt, cdvd.BlockSize, cdvd.Speed, (cdvd.SpindlCtrl & CDVD_SPINDLE_CAV) ? "CAV" : "CLV", cdvd.ReadMode); // T52' + NL
    + "} // T52" + NL
)

T52_MARKS = (
    T + T + "// T52: script-driven transition marks (log-only): /tmp/t52-mark-<label> -> T52_MARK at exact vsync." + NL
    + T + T + "{ // T52" + NL
    + T + T + T + 'static const char* t52_paths[] = {"/tmp/t52-mark-title", "/tmp/t52-mark-menu", "/tmp/t52-mark-scentry", "/tmp/t52-mark-scsettled"}; // T52' + NL
    + T + T + T + 'static const char* t52_labels[] = {"title", "menu", "scentry", "scsettled"}; // T52' + NL
    + T + T + T + "for (int t52i = 0; t52i < 4; t52i++) // T52" + NL
    + T + T + T + "{ // T52" + NL
    + T + T + T + T + "FILE* t52f = fopen(t52_paths[t52i], \"r\"); // T52" + NL
    + T + T + T + T + "if (t52f) // T52" + NL
    + T + T + T + T + "{ // T52" + NL
    + T + T + T + T + T + "fclose(t52f); // T52" + NL
    + T + T + T + T + T + "remove(t52_paths[t52i]); // T52" + NL
    + T + T + T + T + T + 'Console.WriteLn("T52_MARK vsync=%d label=%s", g8_vsync_index, t52_labels[t52i]); // T52' + NL
    + T + T + T + T + "} // T52" + NL
    + T + T + T + "} // T52" + NL
    + T + T + "} // T52" + NL
)

# (anchor, replacement, kind-label) for CDVD.cpp verbose statements
CDVD_SITES = [
    (
        T * 4 + 'Console.WriteLn(Color_Gray, "CDRead: Reading Sector %07d (%03d Blocks of Size %d) at Speed=%dx(%s) Spindle=%x",' + NL
        + T * 5 + 'cdvd.SeekToSector, cdvd.SectorCnt, cdvd.BlockSize, cdvd.Speed, (cdvd.SpindlCtrl & CDVD_SPINDLE_CAV) ? "CAV" : "CLV", cdvd.SpindlCtrl);',
        T * 4 + 't52_cdread("CD"); // T52',
    ),
    (
        T * 4 + 'Console.WriteLn(Color_Gray, "CdAudioRead: Reading Sector %07d (%03d Blocks of Size %d) at Speed=%dx(%s) Spindle=%x",' + NL
        + T * 5 + 'cdvd.CurrentSector, cdvd.SectorCnt, cdvd.BlockSize, cdvd.Speed, (cdvd.SpindlCtrl & CDVD_SPINDLE_CAV) ? "CAV" : "CLV", cdvd.SpindlCtrl);',
        T * 4 + 't52_cdread("CDDA"); // T52',
    ),
    (
        T * 4 + 'Console.WriteLn(Color_Gray, "DvdRead: Reading Sector %07d (%03d Blocks of Size %d) at Speed=%dx(%s) SpindleCtrl=%x",' + NL
        + T * 5 + 'cdvd.SeekToSector, cdvd.SectorCnt, cdvd.BlockSize, cdvd.Speed, (cdvd.SpindlCtrl & CDVD_SPINDLE_CAV) ? "CAV" : "CLV", cdvd.SpindlCtrl);',
        T * 4 + 't52_cdread("DVD"); // T52',
    ),
]

A_INCLUDE = "#include <memory>"
A_DECL = "u32 PSXCLK = 36864000;"
A_GS = T + T + "g_t48_vsync.store(g8_vsync_index, std::memory_order_relaxed);"


def main():
    with open(CDVD) as f:
        c = f.read()
    with open(GS) as f:
        g = f.read()

    # validate
    checks = [
        ("cdvd-include", c.count(A_INCLUDE), 1),
        ("cdvd-decl", c.count(A_DECL), 1),
        ("gs-mirror", g.count(A_GS), 1),
    ]
    for anchor, _ins in CDVD_SITES:
        checks.append(("cdvd-site-" + anchor.split('"')[1].split(":")[0], c.count(anchor), 1))
    ok = True
    for name, n, want in checks:
        print("anchor %s count=%d want=%d" % (name, n, want))
        if n != want:
            ok = False
    if T52_INCLUDE.strip() in c or "t52_cdread" in c or "t52-mark-title" in g:
        print("T52 already applied?")
        ok = False
    if not ok:
        print("T52_HOOK_ABORT")
        sys.exit(1)

    # apply
    c = c.replace(A_INCLUDE, A_INCLUDE + NL + T52_INCLUDE, 1)
    c = c.replace(A_DECL, A_DECL + T52_DECL, 1)
    for anchor, ins in CDVD_SITES:
        c = c.replace(anchor, anchor + NL + ins, 1)
    g = g.replace(A_GS, A_GS + NL + T52_MARKS, 1)

    with open(CDVD, "w") as f:
        f.write(c)
    with open(GS, "w") as f:
        f.write(g)
    print("T52_HOOK_DONE")


main()
