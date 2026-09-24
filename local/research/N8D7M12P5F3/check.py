#!/usr/bin/env python3
"""N8D7M12 Part 5F3 checker: SHA pins, rev/dirty, line anchors, table fields, no verdict."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "REPORT.md")
N8D7F = os.path.expanduser("~/dev/ssx3-work/N8D7F/parallel-gs")
N8D7F_FORK = os.path.expanduser("~/dev/ssx3-work/N8D7F/PS2Recomp")
P2 = os.path.expanduser("~/dev/ssx3-work/N8D7M12P2/PS2Recomp")

PINS = {
    os.path.join(N8D7F, "gs/gs_renderer.cpp"):
        "85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e",
    os.path.join(N8D7F, "gs/gs_interface.hpp"):
        "3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d",
    os.path.join(N8D7F, "gs/gs_renderer.hpp"):
        "fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a",
    os.path.join(N8D7F_FORK, "ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"):
        "c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f",
}
REV = "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd"

# (path, line, keyword within +-2 lines)
ANCHORS = [
    (f"{N8D7F}/gs/gs_renderer.cpp", 1052, "wait_timeline"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 1116, "flush_submit"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 1513, "begin_host_vram_access"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 1520, "end_host_write_vram_access"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 1527, "copy_blocks"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 1709, "flush_readback"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 756, "GSRenderer::GSRenderer"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 775, "wait_timeline"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 315, "invalidate_super_sampling_state"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 341, "wait_idle"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 4396, "ScanoutResult GSRenderer::vsync"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 4759, "capture_selected_input"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 4816, "copy_buffer"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 5054, "capture_selected_input"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 5285, "mark_external_write"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 5314, "capture_scanout_stages"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 5319, "vsync_last_fields"),
    (f"{N8D7F}/gs/gs_renderer.cpp", 5354, "flush_submit(0)"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 23, "ScanoutResult"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 257, "GSRenderer(PageTracker"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 314, "flush_submit"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 317, "wait_timeline"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 322, "begin_host_vram_access"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 344, "PageTracker &tracker"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 464, "exhausted_descriptor_pools"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 466, "descriptor_timeline"),
    (f"{N8D7F}/gs/gs_renderer.hpp", 559, "vsync_last_fields"),
    (f"{N8D7F}/gs/gs_interface.hpp", 142, "deterministic_timeline_query"),
    (f"{N8D7F}/gs/gs_interface.hpp", 224, "unsynced_readbacks"),
    (f"{N8D7F}/gs/gs_interface.hpp", 232, "backbuffer_promotion"),
    (f"{N8D7F}/gs/gs_interface.hpp", 247, "synchronization"),
    (f"{N8D7F}/gs/gs_interface.hpp", 269, "gif_transfer"),
    (f"{N8D7F}/gs/gs_interface.hpp", 286, "map_vram_read"),
    (f"{N8D7F}/gs/gs_interface.hpp", 288, "flush();"),
    (f"{N8D7F}/gs/gs_interface.hpp", 301, "vsync"),
    (f"{N8D7F}/gs/gs_interface.hpp", 324, "PageTracker tracker"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5126, "map_vram_read"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5148, "wait_timeline"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5153, "GSInterface::flush"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5163, "deterministic_timeline_query"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5095, "get_host_write_timeline"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5107, "end_vram_write"),
    (f"{N8D7F}/gs/gs_interface.cpp", 4109, "get_host_read_timeline"),
    (f"{N8D7F}/gs/gs_interface.cpp", 4124, "wait_timeline(host_timeline)"),
    (f"{N8D7F}/gs/gs_interface.cpp", 3918, "acquire_host_write"),
    (f"{N8D7F}/gs/gs_interface.cpp", 4007, "mark_transfer_write"),
    (f"{N8D7F}/gs/gs_interface.cpp", 4075, "mark_transfer_copy"),
    (f"{N8D7F}/gs/gs_interface.cpp", 3674, "mark_fb_write"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5191, "gif_transfer"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5576, "renderer.vsync"),
    (f"{N8D7F}/gs/gs_interface.cpp", 5645, "backbuffer_promotion"),
    (f"{N8D7F}/gs/gs_interface.cpp", 232, "flush_render_pass"),
    (f"{N8D7F}/gs/gs_interface.cpp", 1204, "flush_transfer"),
    (f"{N8D7F}/gs/gs_interface.cpp", 1238, "flush_readback"),
    (f"{N8D7F}/gs/page_tracker.cpp", 122, "mark_external_write"),
    (f"{N8D7F}/gs/page_tracker.cpp", 155, "mark_fb_write"),
    (f"{N8D7F}/gs/page_tracker.cpp", 197, "mark_fb_read"),
    (f"{N8D7F}/gs/page_tracker.cpp", 221, "mark_transfer_copy"),
    (f"{N8D7F}/gs/page_tracker.cpp", 621, "mark_transfer_write"),
    (f"{N8D7F}/gs/page_tracker.cpp", 675, "acquire_host_write"),
    (f"{N8D7F}/gs/page_tracker.cpp", 775, "get_host_read_timeline"),
    (f"{N8D7F}/gs/page_tracker.cpp", 815, "get_host_write_timeline"),
    (f"{N8D7F}/gs/page_tracker.cpp", 501, "flush_render_pass"),
    (f"{N8D7F}/Granite/vulkan/device.cpp", 346, "map_host_buffer"),
    (f"{N8D7F}/Granite/vulkan/device.cpp", 2559, "wait_idle"),
    (f"{N8D7F}/Granite/vulkan/device.cpp", 3194, "CachedHost"),
    (f"{N8D7F}/Granite/vulkan/memory_allocator.cpp", 490, "HOST_COHERENT"),
    (f"{N8D7F}/Granite/vulkan/memory_allocator.cpp", 502, "vkInvalidateMappedMemoryRanges"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 359, "Flush"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 363, "Present("),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 384, "m_iface->flush"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 385, "m_iface->vsync"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 534, "wait_idle"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 553, "map_host_buffer"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 652, "map_host_buffer"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 683, "kStride"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 729, "SnapshotVram"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 738, "m_iface->flush"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 739, "map_vram_read"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 759, "RawGifPacket"),
    (f"{N8D7F_FORK}/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp", 763, "gif_transfer"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 25, "fnv"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 84, "privHash"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 239, "PACKET_TRACE"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 366, "noteGifPath"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 384, "processGIFPacket"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 405, "packetTrace"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 436, "kind == 4"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 443, "drainQueue"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 453, "refreshDisplaySnapshot"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 459, "presentForDiagnostics"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 568, "packetTrace"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 642, "drainQueue"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 678, "GB4_REPLAY_SUMMARY"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_replay_core.cpp", 699, "PS2X_GS_REPLAY_OUT"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 178, "drainQueue"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 273, "Fence"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 742, "refreshDisplaySnapshot"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 839, "presentForDiagnostics"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 929, "processGIFPacket"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 947, "m_submitCount"),
    (f"{P2}/ps2xRuntime/src/lib/gs/gs_frontend.cpp", 956, "RawGifPacket"),
    (f"{P2}/ps2xRuntime/include/runtime/gs/gs_frontend.h", 118, "drainQueue"),
    (f"{P2}/ps2xRuntime/include/runtime/gs/gs_frontend.h", 124, "submitCount"),
    (f"{P2}/ps2xRuntime/include/runtime/gs/gs_frontend.h", 140, "noteGifPath"),
]

REQUIRED_FIELDS = [
    "85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e",
    "3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d",
    "fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a",
    "c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f",
    "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd",
    "unpinned to APK",
    "GB4_PKTSEQ",
    "Prediction table",
    "favors **H2**",
    "favors **H1**",
    "tick850",
    "No root-cause verdict",
    "LSP",
]
FORBIDDEN = ["proves H1", "proves H2", "H1 proven", "H2 proven",
             "verdict: H1", "verdict: H2", "root cause is "]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = []
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        results.append({"name": name, "pass": bool(cond), "detail": detail})
        if not cond:
            ok = False

    try:
        report = open(REPORT, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"verdict": "OTHER", "error": str(e)}))
        return 2

    for path, pin in PINS.items():
        try:
            got = sha256(path)
        except OSError as e:
            check(f"sha:{os.path.basename(path)}", False, str(e))
            continue
        check(f"sha:{os.path.basename(path)}", got == pin,
              f"{got[:12]} vs {pin[:12]}")

    import subprocess
    try:
        rev = subprocess.run(["git", "-C", N8D7F, "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        check("rev:3a66c19", rev == REV, rev)
        st = subprocess.run(["git", "-C", N8D7F, "status", "--short"],
                            capture_output=True, text=True).stdout
        dirty = all(s in st for s in
                    ["M gs/gs_renderer.cpp", "M gs/gs_interface.cpp",
                     "M gs/gs_renderer.hpp"])
        check("dirty-noted", dirty, str(st.splitlines()[:12]))
        blobs = {}
        for rel in ["gs/gs_renderer.cpp", "gs/gs_interface.hpp",
                    "gs/gs_renderer.hpp"]:
            p = subprocess.run(["git", "-C", N8D7F, "show", f"HEAD:{rel}"],
                               capture_output=True)
            blobs[rel] = hashlib.sha256(p.stdout).hexdigest()
        headdiff = all(blobs[k] != PINS[os.path.join(N8D7F, k)] for k in blobs)
        check("head-blobs-differ", headdiff,
              str({k: v[:12] for k, v in blobs.items()}))
    except Exception as e:  # noqa: BLE001
        check("git-state", False, str(e))

    for path, line, kw in ANCHORS:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            check(f"anchor:{os.path.basename(path)}:{line}", False, str(e))
            continue
        lo = max(0, line - 3)
        hi = min(len(lines), line + 2)
        window = "".join(lines[lo:hi])
        check(f"anchor:{os.path.basename(path)}:{line}:{kw}",
              kw in window, lines[line - 1].strip()[:100] if line - 1 < len(lines) else "EOF")

    for field in REQUIRED_FIELDS:
        check(f"field:{field[:40]}", field in report)
    for phrase in FORBIDDEN:
        check(f"no-verdict:{phrase}", phrase not in report,
              "forbidden phrase present" if phrase in report else "")

    total = 0
    for fn in ["REPORT.md", "check.py", "check-result.json"]:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            total += os.path.getsize(p)
    check("bytes<512KiB", total < 512 * 1024, str(total))

    verdict = "A" if ok else "OTHER"
    out = {"verdict": verdict, "pass": sum(1 for r in results if r["pass"]),
           "total": len(results),
           "failures": [r for r in results if not r["pass"]]}
    print(json.dumps(out, indent=1)[:2000])
    with open(os.path.join(HERE, "check-result.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
