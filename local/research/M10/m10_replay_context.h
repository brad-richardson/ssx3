// S2 replay capacity instrument (research copy under local/research/S2).
//
// Continues D2/D2b. D2b died with SIGSEGV in LoadIndexedXF on replay 27 of
// 200 on the Odin (EGL), on two different frames, while the same header ran
// all 200 on desktop Metal. Diagnosis (see local/research/S2/REPORT.md):
//
//   Android trial builds are dual-core, and the arms play a movie, so
//   Core::UpdateWantDeterminism() -> FifoManager::UpdateWantDeterminism(true)
//   with GPUDeterminismMode::Auto sets m_use_deterministic_gpu_thread = true.
//   In that mode OpcodeDecoder's execute pass does NOT read indexed-XF source
//   data (or display-list bodies) from guest RAM: LoadIndexedXF() takes them
//   from the FIFO aux buffer via FifoManager::PopFifoAuxBuffer(), which is an
//   unchecked bump pointer into a fixed 2 MiB m_fifo_aux_data. The pushes come
//   from the PAIRED preprocess pass (RunFifo<true> -> PreprocessIndexedXF ->
//   PushFifoAuxBuffer). D2b ran RunFifo<false> alone, so every replay popped
//   ~78 KiB that nobody pushed; after ~26 replays the read pointer walked off
//   the end of the 2 MiB array and replay 27 dereferenced unmapped memory.
//   2 MiB / 27 = 77.7 KiB per replay, which is the recorded frame's indexed-XF
//   payload -- hence the identical death count on two different frames.
//   Desktop is single core, so gpu_thread &&= IsDualCoreMode() made the flag
//   false there and LoadIndexedXF read guest RAM: all 200 replays passed.
//
// Fixes in this copy (never in native/diagnostics/):
//   1. Paired preprocess pass. When the deterministic GPU path is active, each
//      replay runs RunFifo<true> over the recorded bytes immediately before
//      RunFifo<false>, so the aux buffer is filled with exactly what the
//      execute pass pops, and FifoManager::SyncGPU(AuxSpace, false) rewinds
//      both aux pointers after each pair (read == write there, so the memmove
//      is zero bytes). When the flag is false (desktop) the preprocess pass is
//      skipped: nothing reads the aux buffer.
//   2. PE event suppression for the preprocess pass. LoadBPRegPreprocess()
//      handles ONLY BPMEM_SETDRAWDONE / BPMEM_PE_TOKEN_ID /
//      BPMEM_PE_TOKEN_INT_ID, and calls PixelEngine::SetFinish/SetToken for
//      them -- i.e. in deterministic mode the preprocess pass is where the PE
//      completion/interrupt signals are raised. A separate masked copy of the
//      stream (those three BP writes rewritten to five GX_NOPs, same byte
//      length, nothing else touched) is used for the preprocess pass, so the
//      pass has no guest-visible effect at all. The execute pass keeps the
//      verbatim stream: its own PE calls are already suppressed by the
//      determinism check in BPStructs, and it still needs the token/draw-done
//      handlers for FlushEFBCopies()/FlushStaleBinds(). The mask is built with
//      Dolphin's own command-size decoder and falls back to verbatim if the
//      walk does not consume the whole stream or sees an unknown opcode.
//   3. Restore before EVERY replay, not once: recorded memory updates + TMEM
//      (ApplyMemory), the recorded CP registers into g_main_cp_state (array
//      bases/strides, VATs, VCD, matrix index), CopyPreprocessCPStateFromMain()
//      so both passes start each replay from identical array setup, and
//      VertexLoaderManager::MarkAllDirty(). The full BP/CP/XF/TMEM prelude is
//      still run once before the loop. Each phase is timed separately in the
//      capacity row so the execute-only cost stays readable.
//
// Kept from D2b: per-row fflush, GPFifo gather-pipe drain/snapshot/restore
// around the bulk section, whole-200 seq_wall_ms on `done`, RAM/EXRAM
// save/restore with a watched-window re-hash that stops the run on mismatch.
// Env-gated on SSX_NATIVE_REPLAY=1 (compile-time on for the Android trial TU).
#pragma once
#include "Common/ChunkFile.h"
#include "Core/FifoPlayer/FifoDataFile.h"
#include "Core/FifoPlayer/FifoRecorder.h"
#include "Core/Core.h"
#include "Core/HW/GPFifo.h"
#include "VideoCommon/DataReader.h"
#include "VideoCommon/OpcodeDecoding.h"
#include "VideoCommon/VertexLoaderManager.h"
#include "VideoCommon/VertexLoaderBase.h"  // M9 step 2: GetVertexComponents for per-draw VAT decode
#include "VideoCommon/NativeVertexFormat.h"  // M9 step 2: VB_HAS_POSMTXIDX / VB_HAS_TEXMTXIDXi
#include "VideoCommon/VertexShaderManager.h"  // M9 step 3: constants snapshot reads
#include "VideoCommon/XFStateManager.h"  // M9 step 3: dirty-flag reads
#include "VideoCommon/XFMemory.h"
#include "VideoCommon/BPMemory.h"
#include "VideoCommon/CPMemory.h"
#include "VideoCommon/TextureDecoder.h"
#include "VideoCommon/AbstractGfx.h"
#include "VideoCommon/Fifo.h"
#include "VideoCommon/VideoConfig.h"
// M5 step 3: side-effect counters. No public accessor exposes the
// texture-cache entry count (m_textures_by_address) or the deferred EFB-copy
// queue length (m_pending_efb_copies), so visibility of TextureCacheBase.h is
// promoted header-locally for this probe TU only (the vendor tree is
// untouched) for passive size reads. Every other counter uses public APIs:
// g_presenter->FrameCount(), our own after_frame_event listener, PE/VI DoState
// snapshots, OpcodeDecoder::g_record_fifo_data.
#define M5_VIS public
#define private M5_VIS
#define protected M5_VIS
#include "VideoCommon/TextureCacheBase.h"
#undef private
#undef protected
#include "VideoCommon/Present.h"
#include "VideoCommon/PixelEngine.h"
#include "Core/HW/VideoInterface.h"
#include "VideoCommon/VideoEvents.h"
#include "Common/HookableEvent.h"
#include <atomic>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <vector>

namespace NativeReplay {
using namespace NativeProbe;

static bool Enabled() {
#ifdef SSX_D2_REPLAY_ALWAYS
  // Android trial TU: the device launch env is fixed (no SSX_NATIVE_REPLAY
  // passthrough), so the device binary enables the instrument at compile
  // time. The desktop player never defines this and stays env-gated.
  return true;
#else
  static const bool on = [] {
    const char* value = std::getenv("SSX_NATIVE_REPLAY");
    return value && std::strcmp(value, "1") == 0;
  }();
  return on;
#endif
}
enum class Phase { Idle, Recording, Measuring, Done };
static Phase phase = Phase::Idle;
static unsigned replays = 0, memory_updates = 0;
static std::vector<u8> frame;      // verbatim recorded stream (execute pass)
static std::vector<u8> frame_pre;  // PE-masked copy (preprocess pass)
static u32 fifo_start = 0, fifo_end = 0;
static double record_wall = 0;
static constexpr unsigned kReplays = 200;
static double replay_wall_ms[kReplays] = {};
static double replay_cpu_ms[kReplays] = {};

// Thread-CPU time of the calling thread in ms (-1 when unavailable). On the
// thread that runs the dispatch this is the decode-and-submit CPU of the
// replay.
static double ThreadCpuMs() {
  struct timespec ts {};
  if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts) != 0) return -1.0;
  return double(ts.tv_sec) * 1000.0 + double(ts.tv_nsec) / 1e6;
}

static u64 RamHash(const u8* data, size_t size) {
  u64 hash = 14695981039346656037ull;
  for (size_t i = 0; i < size; ++i) {
    hash ^= data[i];
    hash *= 1099511628211ull;
  }
  return hash;
}

// --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
static unsigned long long s_after_frame_triggers = 0;
// --- M6 step 2: scoped after_frame_event bus ---------------------------------
//
// HookableEvent's public API is Register/Trigger only: live listeners cannot
// be unregistered (handles are owned by the subscribers) and no gate flag
// exists at either Trigger site (BPStructs.cpp:353 is unconditional;
// Present.cpp:1050 is Presenter::DoState read-mode only, never taken during
// the sequence). The scoped bus uses two more public facts: VideoEvents'
// after_frame_event is a public member (VideoEvents.h), and HookableEvent is
// copyable/assignable through its implicit public special members, with the
// copy sharing the listener storage. So the sequence saves the live bus by
// copy (shares storage, keeps it alive), move-assigns a fresh empty bus into
// the member (live listeners orphaned but intact via weak_ptr), registers the
// header's own counter on the scoped bus, and registers a sentinel on the
// saved bus: any Trigger that somehow reached live storage would move it, so
// per-replay dafter_live=0 proves none did. Restored by copy-assignment after
// the sequence (both the normal and the record_flag_set-break paths). Both
// Trigger sites resolve the member fresh on every call and no subsystem caches
// a reference to it (all vendor-tree uses are Register/Trigger on a fresh
// GetVideoEvents() expression), so nothing bypasses the swap. No vendor
// change, no visibility trick: only public members and public operators.
static unsigned long long s_after_frame_live = 0;
// --- M7 step 1b: unsuppressed-with-tracing gap mode ------------------------------
// Closes M6's unordered unsuppressed run. SSX_M7_NO_SUPPRESS=1 skips the scoped
// bus install (M5 shape: the header probe registers directly on the live bus,
// last, so it fires after the 12 live listeners incl. the config refresh; the
// sentinel also goes on the live bus, so dafter_live=1/1 proves live delivery).
// Unset (default) = exact M6 behavior. In both modes the probe samples
// g_ActiveConfig.bImmediateXFB inside the Trigger (HookableEvent fires in
// registration order); replay 0's fx_before.imxfb=0 vs trig_imx=1 directly
// observes M6's mid-Trigger flag flip.
static int s_m7_trig_imx = -1;
// --- M6 step 3: replay-local frame counter + presenter tracing ----------------
// FrameCount() can no longer age the replay (step 2 suppresses the only
// in-sequence writer path), so the header owns its own frame counter,
// incremented once per emitted capacity row. The presenter tracing names M5's
// unresolved dframe +1/replay writer: before_present_event fires in every
// ViSwap/ImmediateSwap path (even duplicates), after_present_event in every
// non-skipped present, and PresentInfo.reason splits Immediate vs
// VideoInterface vs duplicate. Armed while still live (the recorded original
// frame presents, so a non-empty pre-sequence count is the tracer's positive
// control), snapshotted at sequence start, emitted as present_trace after the
// sequence. Atomics: during the live window the callbacks run on the video
// thread while the sequence reads post-stall; during the sequence the video
// thread is stalled (PauseAndLock) and only this thread's synchronous
// ImmediateSwap path can fire.
static unsigned long long s_m6_frame = 0;
static std::atomic<unsigned long long> s_pres_before{0}, s_pres_after{0};
static std::atomic<unsigned long long> s_pres_imm{0}, s_pres_vi{0}, s_pres_dup{0};
static std::atomic<bool> s_pres_got_imm{false}, s_pres_got_vi{false};
static std::atomic<unsigned long long> s_pres_first_imm_pc{0}, s_pres_first_imm_fc{0};
static std::atomic<unsigned long long> s_pres_first_vi_pc{0}, s_pres_first_vi_fc{0};
static Common::EventHook s_pres_before_hook, s_pres_after_hook;
struct SideFx {
  size_t tex_entries = 0;
  size_t pending = 0;
  int frame_count = -1;
  unsigned long long after_frame = 0;
  unsigned long long after_frame_live = 0;  // M6 step 2: sentinel on saved bus
  unsigned long long present_before = 0;    // M6 step 3: presenter tracing
  int imxfb = -1;                           // M6 step 3: g_ActiveConfig sample
  std::vector<u8> pe_state;
  std::vector<u8> vi_state;
};
static std::vector<u8> DoStateBytes_PE(Core::System& system) {
  std::vector<u8> buf(512, 0);
  u8* w = buf.data();
  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
  system.GetPixelEngine().DoState(pw);
  buf.resize(size_t(w - buf.data()));
  return buf;
}
static std::vector<u8> DoStateBytes_VI(Core::System& system) {
  std::vector<u8> buf(2048, 0);
  u8* w = buf.data();
  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
  system.GetVideoInterface().DoState(pw);
  buf.resize(size_t(w - buf.data()));
  return buf;
}
static SideFx CaptureSideFx(Core::System& system) {
  SideFx s;
  if (g_texture_cache) {
    s.tex_entries = g_texture_cache->m_textures_by_address.size();
    s.pending = g_texture_cache->m_pending_efb_copies.size();
  }
  if (g_presenter) s.frame_count = g_presenter->FrameCount();
  s.after_frame = s_after_frame_triggers;
  s.after_frame_live = s_after_frame_live;
  s.present_before = s_pres_before.load(std::memory_order_relaxed);
  s.imxfb = g_ActiveConfig.bImmediateXFB ? 1 : 0;
  s.pe_state = DoStateBytes_PE(system);
  s.vi_state = DoStateBytes_VI(system);
  return s;
}
static unsigned DiffBytes(const std::vector<u8>& a, const std::vector<u8>& b) {
  unsigned n = 0;
  const size_t len = a.size() > b.size() ? a.size() : b.size();
  for (size_t i = 0; i < len; ++i) {
    const u8 x = i < a.size() ? a[i] : 0;
    const u8 y = i < b.size() ? b[i] : 0;
    if (x != y) ++n;
  }
  return n;
}

// --- M5 step 5: continuation check ------------------------------------------
// After the sequence and the S2 restore, capture the first live XFB copy
// after resume with a one-shot after_frame listener: range from the live BP
// registers, hashed from guest RAM. The same capture arms in the
// sequence-disabled run (SSX_NATIVE_REPLAY=0) at its seam marker, so the
// report can compare the two runs when they reach the seam at the same frame
// (record_start fc equal); otherwise it says so and skips.
static void Event(const char* action, const char* detail);
static Common::EventHook s_resume_hook;
static void ArmResumeXfbCapture(Core::System& system, int disabled) {
  if (s_resume_hook) s_resume_hook.reset();
  s_resume_hook = system.GetVideoEvents().after_frame_event.Register(
      [disabled](Core::System& sys) {
        const u32 hsrc = bpmem.copyTexSrcWH.y;
        const bool invert = bpmem.triggerEFBCopy.scale_invert;
        float yscale = 1.0f;
        if (bpmem.dispcopyyscale != 0) {
          yscale = invert ? (256.0f / float(bpmem.dispcopyyscale))
                          : (float(bpmem.dispcopyyscale) / 256.0f);
        }
        const u32 h = u32(1.0f + float(hsrc) * yscale);
        const u32 addr = bpmem.copyTexDest << 5;
        const u32 stride = bpmem.copyDestStride << 5;
        const u32 bytes = h * stride;
        u64 hash = 0;
        bool ok = false;
        if (bytes > 0) {
          if (u8* ptr = sys.GetMemory().GetPointerForRange(addr, bytes)) {
            hash = RamHash(ptr, bytes);
            ok = true;
          }
        }
        int fc = -1;
        if (g_presenter) fc = g_presenter->FrameCount();
        char d[224];
        std::snprintf(d, sizeof(d),
                      "replay_disabled=%d fc=%d ok=%d xfb_addr=0x%08x xfb_bytes=%u "
                      "xfb_hash=%016llx",
                      disabled, fc, int(ok), addr, bytes,
                      static_cast<unsigned long long>(hash));
        Event("resume_xfb", d);
        s_resume_hook.reset();
      });
}

// Command bytes that restore the recorded initial BP/CP/XF state, mirroring
// FifoPlayer::LoadRegisters (same register exclusions), so draw command sizes
// and matrices decode as they did when the frame was recorded.
static void Put8(std::vector<u8>& v, u32 x) { v.push_back(u8(x)); }
static void Put32(std::vector<u8>& v, u32 x) {
  v.push_back(u8(x >> 24));
  v.push_back(u8(x >> 16));
  v.push_back(u8(x >> 8));
  v.push_back(u8(x));
}
// The CP half on its own: array bases and strides, VCD, VAT and matrix index.
// This is the part that must be identical at the start of every replay, and
// it is cheap (84 register writes) unlike the BP/XF halves.
static void PutCpRegs(std::vector<u8>& v, const u32* cp) {
  auto cpreg = [&](u32 r) {
    Put8(v, 0x08);
    Put8(v, r);
    Put32(v, cp[r]);
  };
  cpreg(MATINDEX_A);
  cpreg(MATINDEX_B);
  cpreg(VCD_LO);
  cpreg(VCD_HI);
  for (u32 i = 0; i < CP_NUM_VAT_REG; ++i) {
    cpreg(CP_VAT_REG_A + i);
    cpreg(CP_VAT_REG_B + i);
    cpreg(CP_VAT_REG_C + i);
  }
  for (u32 i = 0; i < CP_NUM_ARRAYS; ++i) {
    cpreg(ARRAY_BASE + i);
    cpreg(ARRAY_STRIDE + i);
  }
}
// The XF register block (0x1000+) on its own, same exclusions as the full
// prelude. It carries invtxspec, viewport, projection and lighting setup.
// invtxspec must agree with the CP vertex descriptor or the first draw of the
// replay hits CheckCPConfiguration()'s PanicAlertFmt, so the two are always
// restored together.
static void PutXfRegs(std::vector<u8>& v, const u32* regs) {
  for (u32 i = 0; i < FifoDataFile::XF_REGS_SIZE; ++i) {
    const u32 address = i + 0x1000;
    if (address == XFMEM_UNKNOWN_1007 ||
        (address >= XFMEM_UNKNOWN_GROUP_1_START && address <= XFMEM_UNKNOWN_GROUP_1_END) ||
        (address >= XFMEM_UNKNOWN_GROUP_2_START && address <= XFMEM_UNKNOWN_GROUP_2_END) ||
        (address >= XFMEM_UNKNOWN_GROUP_3_START && address <= XFMEM_UNKNOWN_GROUP_3_END))
      continue;
    Put8(v, 0x10);
    Put32(v, (address & 0x0fffu) | 0x1000u);
    Put32(v, regs[i]);
  }
}
// Per-replay restore: CP registers (array bases/strides, VCD, VAT, matrix
// index) plus the XF register block. Cheap next to the full prelude, which
// also rewrites all 4096 XF memory words and the whole BP register file.
static std::vector<u8> CpXfPreludeFrom(const u32* cp, const u32* regs) {
  std::vector<u8> v;
  PutCpRegs(v, cp);
  PutXfRegs(v, regs);
  return v;
}
static std::vector<u8> PreludeFrom(const u32* bp, const u32* cp, const u32* xf,
                                   const u32* regs) {
  std::vector<u8> v;
  for (u32 i = 0; i < FifoDataFile::BP_MEM_SIZE; ++i) {
    switch (i) {
    case BPMEM_SETDRAWDONE:
    case BPMEM_PE_TOKEN_ID:
    case BPMEM_PE_TOKEN_INT_ID:
    case BPMEM_TRIGGER_EFB_COPY:
    case BPMEM_LOADTLUT1:
    case BPMEM_PRELOAD_MODE:
    case BPMEM_PERF1:
      continue;
    default:
      break;
    }
    Put8(v, 0x61);
    Put32(v, ((i << 24) & 0xff000000u) | (bp[i] & 0x00ffffffu));
  }
  PutCpRegs(v, cp);
  for (u32 i = 0; i < FifoDataFile::XF_MEM_SIZE; i += 16) {
    Put8(v, 0x10);
    Put32(v, 0x000f0000u | (i & 0xffffu));
    for (u32 k = 0; k < 16; ++k) Put32(v, xf[i + k]);
  }
  PutXfRegs(v, regs);
  return v;
}
static std::vector<u8> Prelude(FifoDataFile* file) {
  return PreludeFrom(file->GetBPMem(), file->GetCPMem(), file->GetXFMem(), file->GetXFRegs());
}
static void ApplyMemory(Core::System& system, FifoDataFile* file) {
  auto& memory = system.GetMemory();
  std::memcpy(s_tex_mem.data(), file->GetTexMem(), FifoDataFile::TEX_MEM_SIZE);
  for (const auto& update : file->GetFrame(0).memoryUpdates) {
    u8* mem = (update.address & 0x10000000u)
                  ? &memory.GetEXRAM()[update.address & memory.GetExRamMask()]
                  : &memory.GetRAM()[update.address & memory.GetRamMask()];
    std::memcpy(mem, update.data.data(), update.data.size());
  }
}

// --- PE-suppression mask for the preprocess pass -----------------------------
//
// Walks the recorded stream with Dolphin's own command-size decoder and
// rewrites every GX_LOAD_BP_REG whose register is one of the three the
// preprocess BP handler acts on into five GX_NOPs. Byte length is unchanged,
// no aux-buffer command is touched, so the preprocess and execute passes still
// push and pop the same aux payload in the same order.
// --- M5 step 2: XFB fidelity -------------------------------------------------
//
// The same mask walk also decodes the recorded frame's XFB copy destination:
// the EFB-copy BP write (BPMEM_TRIGGER_EFB_COPY 0x52 with the XFB bit, bit 14)
// and the live destination (BPMEM_EFB_ADDR 0x4b), stride (0x4d) and copy
// rectangle (0x49/0x4a, X10Y10) plus y-scale (0x4e) at that trigger. The byte
// range mirrors TextureCacheBase::CopyRenderTargetToTexture for the XFB format
// (block 16x1, 32 bytes/block): bytes_per_row = AlignUp(width,16)/16*32,
// covered = height * stride with height = 1 + WH.y * yScale as in BPStructs.
struct XfbRange {
  bool found = false;
  u32 copies = 0;   // XFB-copy triggers seen in the recorded stream
  u32 addr = 0;     // guest byte address (copyTexDest << 5)
  u32 stride = 0;   // bytes per row (copyDestStride << 5)
  u32 width = 0;    // copyTexSrcWH.x + 1
  u32 height = 0;   // 1 + copyTexSrcWH.y * yScale
  u32 bytes = 0;    // height * stride
};
struct MaskStats {
  u32 consumed = 0;
  u32 masked = 0;
  u32 display_lists = 0;
  u32 indexed = 0;
  u32 indexed_bytes = 0;  // aux-buffer payload popped per replay (the 2 MiB budget)
  u32 dl_bytes = 0;
  u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
  u32 unknown = 0;
  XfbRange xfb;
  // M5 step 4: stream offsets of the BPMEM_EFB_ADDR writes governing each XFB
  // copy (for the replay-owned scratch retarget).
  std::vector<u32> xfb_addr_offsets;
  // M5 step 4 recount: every EFB-copy trigger (XFB or not). Non-XFB copies
  // keep their destinations; non-XFB count = efb_copies_total - xfb.copies.
  u32 efb_copies_total = 0;
};
class PeMaskWalk final : public OpcodeDecoder::Callback {
public:
  PeMaskWalk(u8* base, const u32* cp_mem, MaskStats& stats)
      : m_base(base), m_cp(cp_mem), m_stats(stats) {}
  void OnXF(u16, u8, const u8*) override {}
  void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
  void OnBP(u8 command, u32 value) override {
    m_bp_reg = int(command);
    // M5 step 2: track the XFB-copy destination registers live at each XFB trigger.
    switch (command) {
    case BPMEM_EFB_TL:
      m_tl = value;
      break;
    case BPMEM_EFB_WH:
      m_wh = value;
      break;
    case BPMEM_EFB_ADDR:
      m_dest = value;
      break;
    case BPMEM_EFB_STRIDE:
      m_stride = value;
      break;
    case BPMEM_COPYYSCALE:
      m_yscale = value;
      break;
    case BPMEM_TRIGGER_EFB_COPY:
      ++m_stats.efb_copies_total;
      if ((value >> 14) & 1u) {  // UPE_Copy::copy_to_xfb
        XfbRange& r = m_stats.xfb;
        ++r.copies;
        const u32 w = (m_wh & 0x3ffu) + 1u;
        const u32 hsrc = (m_wh >> 10) & 0x3ffu;
        const bool invert = ((value >> 10) & 1u) != 0;  // UPE_Copy::scale_invert
        float yscale = 1.0f;
        if (m_yscale != 0)
          yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
        // m_yscale == 0 keeps yscale == 1.0f (fallback; real frames set 0x4e).
        const u32 h = u32(1.0f + float(hsrc) * yscale);
        r.addr = m_dest << 5;
        r.stride = m_stride << 5;
        r.width = w;
        r.height = h;
        r.bytes = h * r.stride;
        r.found = (r.bytes > 0 && r.addr != 0);
        // M5 step 4: remember the governing 0x4b write for the scratch retarget.
        if (m_last_addr_off != 0xFFFFFFFFu)
          m_stats.xfb_addr_offsets.push_back(m_last_addr_off);
      }
      break;
    default:
      break;
    }
  }
  void OnIndexedLoad(CPArray, u32, u16, u8 size) override {
    ++m_stats.indexed;
    m_stats.indexed_bytes += u32(size) * 4u;
  }
  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8, u32, u16, const u8*) override {}
  void OnDisplayList(u32, u32 size) override {
    ++m_stats.display_lists;
    m_stats.dl_bytes += size;
  }
  void OnNop(u32) override {}
  // RunCallback::OnUnknown treats GX_CMD_UNKNOWN_METRICS (0x44) and
  // GX_CMD_INVL_VC (0x48) as known, ignored, one-byte commands; only anything
  // else reaches CommandProcessor::HandleUnknownOpcode. Real SSX 3 frames
  // contain one 0x44/0x48, so counting those as a parse failure would disable
  // the mask on every frame.
  void OnUnknown(u8 opcode, const u8*) override {
    if (opcode == 0x44 || opcode == 0x48)
      ++m_stats.benign_unknown;
    else
      ++m_stats.unknown;
  }
  void OnCommand(const u8* data, u32 size) override {
    if (m_bp_reg >= 0) {
      const int reg = m_bp_reg;
      m_bp_reg = -1;
      if (reg == BPMEM_SETDRAWDONE || reg == BPMEM_PE_TOKEN_ID ||
          reg == BPMEM_PE_TOKEN_INT_ID) {
        std::memset(m_base + (data - m_base), 0x00, size);  // size GX_NOPs
        ++m_stats.masked;
      }
      // M5 step 4: offset of the latest 0x4b write (governs the next XFB copy).
      if (reg == BPMEM_EFB_ADDR) m_last_addr_off = u32(data - m_base);
    }
  }
  CPState& GetCPState() override { return m_cp; }

private:
  u8* m_base;
  CPState m_cp;
  MaskStats& m_stats;
  int m_bp_reg = -1;
  // M5 step 2: last-seen XFB destination registers (24-bit BP values).
  u32 m_tl = 0;
  u32 m_wh = 0;
  u32 m_dest = 0;
  u32 m_stride = 0;
  u32 m_yscale = 0;
  // M5 step 4: offset of the latest 0x4b write in the walked stream.
  u32 m_last_addr_off = 0xFFFFFFFFu;
};
static MaskStats BuildMaskedStream(const std::vector<u8>& src, const u32* cp_mem,
                                   std::vector<u8>& out) {
  out = src;
  MaskStats stats;
  if (out.empty()) return stats;
  PeMaskWalk walk(out.data(), cp_mem, stats);
  stats.consumed = OpcodeDecoder::Run(out.data(), u32(out.size()), walk);
  if (stats.consumed != out.size() || stats.unknown != 0) {
    out = src;  // fail closed: preprocess the verbatim stream instead
    stats.masked = 0;
  }
  return stats;
}

// --- M8 step 2: stream-epoch census walk ------------------------------------
// Read-only decode of the verbatim recorded stream (no mutation; own CPState
// seeded from the recorded registers like PeMaskWalk). Counts draws, tracks
// matrix-index epochs through CP and XF writes, attributes draws to the slots
// the live index state references. Deadline-free setup cost (~one decode).
struct M8Census {
  u32 consumed = 0;
  u32 draws = 0;
  u64 verts = 0;
  u32 epochs = 0;  // index-state transitions observed at draws, +1 (0 if no draws)
  u32 matidx_cp = 0;  // CP 0x30/0x40 writes in the stream
  u32 matidx_xf = 0;  // XF 0x1018/0x1019 words in the stream
  u32 direct_xfmem = 0;  // direct XF commands touching words < 0x1000
  u32 direct_pos_words = 0;  // of those, words in the pos-matrix range
  u32 indexed = 0;
  u32 idx_pos = 0;  // indexed loads covering >= 1 pos-matrix word
  u32 idx_reg = 0;  // indexed loads covering regs (expect 0)
  u32 projreg_writes = 0;  // direct XF commands covering 0x1020-0x1026
  u32 numtex_w = 0;  // in-stream writes to XF 0x103f (SETNUMTEXGENS)
  u32 numtex0 = 0;  // recorded frame-start value of XF 0x103f
  u32 idxa0 = 0, idxb0 = 0;  // recorded frame-start CP matrix-index hexes
  u32 benign = 0;  // 0x44 / 0x48 (step-3 fix: step 2 counted these as unknown)
  u32 unknown = 0;
  u64 draws_aff[64] = {};
  // M8 step 3: per-expression draw attribution (0=PosNormal, 1-8=Tex0-7).
  // Each expression attributes its own slot independently (no cross-expression
  // dedupe); draws_aff above keeps the per-draw dedupe.
  u64 expr[9][64] = {};
};
class M8CensusWalk final : public OpcodeDecoder::Callback {
public:
  M8CensusWalk(const u32* cp_mem, M8Census& stats) : m_cp(cp_mem), m_stats(stats) {}
  void OnXF(u16 address, u8 count, const u8* data) override {
    const u32 lo = address, hi = u32(address) + u32(count);
    if (lo < 0x1000) {
      ++m_stats.direct_xfmem;
      const u32 plo = lo < 0x100 ? lo : 0x100;
      const u32 phi = hi < 0x100 ? hi : 0x100;
      if (phi > plo) m_stats.direct_pos_words += phi - plo;
    }
    if (lo <= XFMEM_SETPROJECTION + 6 && hi > XFMEM_SETPROJECTION)
      ++m_stats.projreg_writes;
    for (u32 i = 0; i < u32(count); ++i) {
      const u32 word = lo + i;
      if (word == XFMEM_SETNUMTEXGENS) ++m_stats.numtex_w;
      if (word != XFMEM_SETMATRIXINDA && word != XFMEM_SETMATRIXINDB) continue;
      // Stream words are big-endian; LoadXFReg applies Common::swap32 per word.
      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
      // Mirror the SetTexMatrixChangedA/B write-through to CP state.
      if (word == XFMEM_SETMATRIXINDA)
        m_cp.matrix_index_a.Hex = v;
      else
        m_cp.matrix_index_b.Hex = v;
      ++m_stats.matidx_xf;
    }
  }
  void OnCP(u8 command, u32 value) override {
    m_cp.LoadCPReg(command, value);
    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
  }
  void OnBP(u8, u32) override {}
  void OnIndexedLoad(CPArray, u32, u16 address, u8 size) override {
    ++m_stats.indexed;
    const u32 lo = address, hi = u32(address) + u32(size);
    if (lo < 0x100) ++m_stats.idx_pos;
    if (hi > 0x1000) ++m_stats.idx_reg;
  }
  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8, u32, u16 num_vertices,
                          const u8*) override {
    ++m_stats.draws;
    m_stats.verts += num_vertices;
    const u32 ia = m_cp.matrix_index_a.Hex;
    const u32 ib = m_cp.matrix_index_b.Hex;
    if (m_stats.draws == 1) {
      m_stats.epochs = 1;
    } else if (ia != m_idx_a || ib != m_idx_b) {
      ++m_stats.epochs;
    }
    m_idx_a = ia;
    m_idx_b = ib;
    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
                        (ib >> 18) & 63};
    for (u32 k = 0; k < 9; ++k) {
      ++m_stats.expr[k][idx[k]];  // M8 step 3: per-expression, no dedupe
      bool seen = false;
      for (u32 j = 0; j < k; ++j)
        if (idx[j] == idx[k]) seen = true;
      if (!seen) ++m_stats.draws_aff[idx[k]];
    }
  }
  void OnDisplayList(u32, u32) override {}
  void OnNop(u32) override {}
  void OnUnknown(u8 opcode, const u8*) override {
    // Mirror PeMaskWalk: 0x44/0x48 are known-but-ignored single bytes.
    if (opcode == 0x44 || opcode == 0x48)
      ++m_stats.benign;
    else
      ++m_stats.unknown;
  }
  void OnCommand(const u8*, u32) override {}
  CPState& GetCPState() override { return m_cp; }

private:
  CPState m_cp;
  M8Census& m_stats;
  u32 m_idx_a = 0, m_idx_b = 0;
};
static M8Census RunM8Census(const std::vector<u8>& src, const u32* cp_mem,
                            const u32* xf_regs) {
  M8Census stats;
  stats.numtex0 = xf_regs[0x3f];  // 0x103f - 0x1000
  stats.idxa0 = cp_mem[MATINDEX_A];
  stats.idxb0 = cp_mem[MATINDEX_B];
  if (src.empty()) return stats;
  M8CensusWalk walk(cp_mem, stats);
  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
  return stats;
}

// --- M9 step 2: per-draw VAT + texgen-enablement walk --------------------------
// Closes M8 gaps 1-3 (per-draw VAT path, shared-vs-indexed split, per-draw
// texgen enablement). Read-only decode of the verbatim recorded stream (own
// CPState seeded from recorded registers; own numtex/texinfo state seeded from
// recorded XF regs). Per draw records, via the vendor's own
// VertexLoaderBase::GetVertexComponents (VCD + VAT[vat]): VB_HAS_POSMTXIDX and
// VB_HAS_TEXMTXIDXi path bits; numtex = live XF 0x103f low nibble after
// in-stream writes (XFStructs.cpp:141-144: numTexGens = value & 15); texgen
// types from XF 0x1040-0x1047 (TexMtxInfo.texgentype = bits 4-6); matrix-index
// state via the same CP/XF write-through as M8CensusWalk. Shared reach counts
// only draws that can actually consume the shared slot: position draws with
// the shared path (no enablement gate), texgen draws with shared path AND
// i < numtex. Indexed-path draws are counted per expression as totals only:
// their per-vertex indices are not decoded (residue), so attributing them to
// index-state slots would repeat M8's over-count.
struct M9Census {
  u32 consumed = 0;
  u32 draws = 0;
  u64 verts = 0;
  u32 vcd_lo = 0;   // CP 0x50 writes in the stream
  u32 vcd_hi = 0;   // CP 0x60 writes in the stream
  u32 vat_w = 0;    // CP 0x70-0x97 writes in the stream
  u32 matidx_cp = 0;
  u32 matidx_xf = 0;
  u32 numtex0 = 0;  // recorded frame-start value of XF 0x103f
  u32 numtex_w = 0;
  u32 texinfo_w = 0;  // in-stream writes to XF 0x1040-0x1047
  u32 benign = 0;
  u32 unknown = 0;
  u64 vat_hist[8] = {};      // draws per vat index
  u64 numtex_hist[16] = {};  // draws per live numtex value
  u64 pos_shared = 0, pos_indexed = 0;
  u64 tex_shared[8] = {}, tex_indexed[8] = {};
  u64 tex_enabled[8] = {};         // draws with i < live numtex
  u64 tex_shared_enabled[8] = {};  // draws with shared path AND enabled
  u64 tex_type[8][4] = {};         // draws per texgen per TexGenType (at draw, enabled or not)
  u64 reach_pos[64] = {};          // draws with PosNormalMtxIdx==s AND pos shared
  u64 reach_tex[8][64] = {};       // draws with TexiMtxIdx==s AND tex-i shared AND enabled
  static constexpr u32 kMaxEpochs = 80;
  u32 epoch_draw[80] = {};  // draw index (1-based) where the epoch starts
  u32 epoch_numtex[80] = {};
  u32 epochs = 0;
};
class M9CensusWalk final : public OpcodeDecoder::Callback {
public:
  M9CensusWalk(const u32* cp_mem, const u32* xf_regs, M9Census& stats)
      : m_cp(cp_mem), m_stats(stats) {
    m_numtex = xf_regs[0x3f] & 0xf;
    for (u32 i = 0; i < 8; ++i) m_texhex[i] = xf_regs[0x40 + i];
  }
  void OnXF(u16 address, u8 count, const u8* data) override {
    const u32 lo = address;
    for (u32 i = 0; i < u32(count); ++i) {
      const u32 word = lo + i;
      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
      if (word == XFMEM_SETNUMTEXGENS) {
        ++m_stats.numtex_w;
        m_numtex = v & 0xf;
      } else if (word >= XFMEM_SETTEXMTXINFO && word < XFMEM_SETTEXMTXINFO + 8) {
        ++m_stats.texinfo_w;
        m_texhex[word - XFMEM_SETTEXMTXINFO] = v;
      }
      if (word == XFMEM_SETMATRIXINDA) {
        m_cp.matrix_index_a.Hex = v;
        ++m_stats.matidx_xf;
      } else if (word == XFMEM_SETMATRIXINDB) {
        m_cp.matrix_index_b.Hex = v;
        ++m_stats.matidx_xf;
      }
    }
  }
  void OnCP(u8 command, u32 value) override {
    m_cp.LoadCPReg(command, value);
    if ((command & CP_COMMAND_MASK) == VCD_LO && command == VCD_LO) ++m_stats.vcd_lo;
    if ((command & CP_COMMAND_MASK) == VCD_HI && command == VCD_HI) ++m_stats.vcd_hi;
    const u32 grp = command & CP_COMMAND_MASK;
    if (grp == CP_VAT_REG_A || grp == CP_VAT_REG_B || grp == CP_VAT_REG_C) ++m_stats.vat_w;
    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
  }
  void OnBP(u8, u32) override {}
  void OnIndexedLoad(CPArray, u32, u16, u8) override {}
  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
                          const u8*) override {
    ++m_stats.draws;
    m_stats.verts += num_vertices;
    const u32 v = vat & 7;
    ++m_stats.vat_hist[v];
    ++m_stats.numtex_hist[m_numtex & 15];
    if (m_stats.draws == 1 || (m_numtex & 15) != m_last_numtex) {
      if (m_stats.epochs < M9Census::kMaxEpochs) {
        m_stats.epoch_draw[m_stats.epochs] = m_stats.draws;
        m_stats.epoch_numtex[m_stats.epochs] = m_numtex & 15;
      }
      ++m_stats.epochs;
      m_last_numtex = m_numtex & 15;
    }
    const u32 comp =
        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
    const bool pos_idx = (comp & VB_HAS_POSMTXIDX) != 0;
    if (pos_idx)
      ++m_stats.pos_indexed;
    else
      ++m_stats.pos_shared;
    const u32 ia = m_cp.matrix_index_a.Hex;
    const u32 ib = m_cp.matrix_index_b.Hex;
    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
                        (ib >> 18) & 63};
    if (!pos_idx) ++m_stats.reach_pos[idx[0]];
    for (u32 i = 0; i < 8; ++i) {
      const bool t_idx = (comp & (VB_HAS_TEXMTXIDX0 << i)) != 0;
      if (t_idx)
        ++m_stats.tex_indexed[i];
      else
        ++m_stats.tex_shared[i];
      const bool enabled = i < (m_numtex & 15);
      if (enabled) ++m_stats.tex_enabled[i];
      if (!t_idx && enabled) {
        ++m_stats.tex_shared_enabled[i];
        ++m_stats.reach_tex[i][idx[1 + i]];
      }
      const u32 ty = (m_texhex[i] >> 4) & 7;
      if (ty < 4) ++m_stats.tex_type[i][ty];
    }
  }
  void OnDisplayList(u32, u32) override {}
  void OnNop(u32) override {}
  void OnUnknown(u8 opcode, const u8*) override {
    if (opcode == 0x44 || opcode == 0x48)
      ++m_stats.benign;
    else
      ++m_stats.unknown;
  }
  void OnCommand(const u8*, u32) override {}
  CPState& GetCPState() override { return m_cp; }

private:
  CPState m_cp;
  M9Census& m_stats;
  u32 m_numtex = 0;
  u32 m_last_numtex = 0;
  u32 m_texhex[8] = {};
};
static M9Census RunM9Census(const std::vector<u8>& src, const u32* cp_mem,
                            const u32* xf_regs) {
  M9Census stats;
  stats.numtex0 = xf_regs[0x3f];
  if (src.empty()) return stats;
  M9CensusWalk walk(cp_mem, xf_regs, stats);
  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
  return stats;
}

// --- M10 step 2: hit/draw order stamps + consuming-draw spans -----------------
// One read-only walk over the verbatim recorded stream (own CPState + numtex
// state, same seeding as M9CensusWalk). Records in stream order: every XF
// write covering the delta word (indexed loads via OnIndexedLoad — address is
// the xfmem word address for every array, XFStructs.cpp LoadIndexedXF — plus
// direct XF writes via OnXF below 0x1000), and every draw consuming the slot
// through the shared path (position: shared + PosNormalMtxIdx==slot, no
// enablement gate; texgen i: shared + enabled + TexiMtxIdx==slot). Positions
// come from OnCommand, which the vendor calls immediately after each
// command's specific callback with the command's start pointer and total size
// (OpcodeDecoding.h RunCommand): specific callbacks push pending records, the
// next OnCommand stamps offset/size. Display-list bodies are not decoded by
// the offline Run (the execute pass handles them); mask.dls==0 on these
// frames, and the report carries the count.
struct M10LoadRec {
  u32 draw = 0;   // draws completed before this command (draw clock)
  u32 off = 0;    // stream byte offset of the command
  u32 size = 0;   // command byte size
  u32 kind = 0;   // 0 = indexed load, 1 = direct XF write
  u32 array = 0;  // CPArray id for indexed loads
};
struct M10DrawRec {
  u32 off = 0;
  u32 size = 0;
  u32 cons_pos = 0;
  u32 cons_texmask = 0;  // bit i = consumes the slot via texgen i
  // M10 step 3: rasterizer state at draw time (seeded from recorded BPMem).
  u32 cull = 0;  // GenMode cull_mode (0 none, 1 back, 2 front, 3 all)
  u32 scis_empty = 0;  // scissor TL>BR in 11-bit coords
  u32 scis_tl = 0, scis_br = 0;  // raw BP hexes at draw
  u32 ztest = 0, zfunc = 0, zupdate = 0;  // ZMode at draw
};
// M10 step 3: EFB-copy trigger record (register decoding mirrors PeMaskWalk).
struct M10CopyRec {
  u32 draw = 0;  // draw clock at trigger
  u32 dest = 0;  // guest byte address (copyTexDest << 5)
  u32 bytes = 0;  // height * stride
  u32 is_xfb = 0;
  u32 clear = 0;
  u32 tl = 0;  // copy source-rect top-left raw BP hex (for clear-rect notes)
  u32 w = 0, h = 0;  // copy source rect w/h as decoded
};
struct M10Order {
  u32 consumed = 0;
  u32 draws = 0;
  u64 verts = 0;
  u32 unknown = 0;
  u32 benign = 0;
  u32 slot = 0;
  u32 word = 0;
  u32 idx_loads = 0;  // all indexed loads (any coverage)
  std::vector<M10LoadRec> loads;  // covering loads, stream order
  std::vector<M10DrawRec> drawrec;  // per draw (index d-1), stream order
  std::vector<u32> load_draws;  // draw clock at every indexed load
  std::vector<M10CopyRec> copies;  // EFB-copy triggers, stream order
};
class M10OrderWalk final : public OpcodeDecoder::Callback {
public:
  M10OrderWalk(const u8* base, const u32* cp_mem, const u32* xf_regs,
               const u32* bp_mem, u32 slot, M10Order& stats)
      : m_base(base), m_cp(cp_mem), m_stats(stats) {
    m_stats.slot = slot;
    m_stats.word = slot * 4 + 3;
    m_numtex = xf_regs[0x3f] & 0xf;
    // M10 step 3: BP rasterizer/copy state seeded from recorded BPMem.
    m_gen = bp_mem[BPMEM_GENMODE] & 0xffffffu;
    m_scis_tl = bp_mem[BPMEM_SCISSORTL] & 0xffffffu;
    m_scis_br = bp_mem[BPMEM_SCISSORBR] & 0xffffffu;
    m_zmode = bp_mem[BPMEM_ZMODE] & 0xffffffu;
    m_tl = bp_mem[BPMEM_EFB_TL] & 0xffffffu;
    m_wh = bp_mem[BPMEM_EFB_WH] & 0xffffffu;
    m_dest = bp_mem[BPMEM_EFB_ADDR] & 0xffffffu;
    m_stride = bp_mem[BPMEM_EFB_STRIDE] & 0xffffffu;
    m_yscale = bp_mem[BPMEM_COPYYSCALE] & 0xffffffu;
  }
  void OnXF(u16 address, u8 count, const u8* data) override {
    const u32 lo = address, hi = u32(address) + u32(count);
    if (lo < 0x1000 && lo <= m_stats.word && m_stats.word < hi) {
      M10LoadRec r;
      r.draw = m_stats.draws;
      r.kind = 1;
      m_stats.loads.push_back(r);
      m_pending_load = true;
    }
    for (u32 i = 0; i < u32(count); ++i) {
      const u32 word = lo + i;
      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
      if (word == XFMEM_SETNUMTEXGENS) {
        m_numtex = v & 0xf;
      }
      if (word == XFMEM_SETMATRIXINDA) {
        m_cp.matrix_index_a.Hex = v;
      } else if (word == XFMEM_SETMATRIXINDB) {
        m_cp.matrix_index_b.Hex = v;
      }
    }
  }
  void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
  void OnBP(u8 command, u32 value) override {
    switch (command) {
    case BPMEM_GENMODE:
      m_gen = value;
      break;
    case BPMEM_SCISSORTL:
      m_scis_tl = value;
      break;
    case BPMEM_SCISSORBR:
      m_scis_br = value;
      break;
    case BPMEM_ZMODE:
      m_zmode = value;
      break;
    case BPMEM_EFB_TL:
      m_tl = value;
      break;
    case BPMEM_EFB_WH:
      m_wh = value;
      break;
    case BPMEM_EFB_ADDR:
      m_dest = value;
      break;
    case BPMEM_EFB_STRIDE:
      m_stride = value;
      break;
    case BPMEM_COPYYSCALE:
      m_yscale = value;
      break;
    case BPMEM_TRIGGER_EFB_COPY: {
      M10CopyRec c;
      c.draw = m_stats.draws;
      c.is_xfb = (value >> 14) & 1u;
      c.clear = (value >> 11) & 1u;
      const u32 w = (m_wh & 0x3ffu) + 1u;
      const u32 hsrc = (m_wh >> 10) & 0x3ffu;
      const bool invert = ((value >> 10) & 1u) != 0;
      float yscale = 1.0f;
      if (m_yscale != 0)
        yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
      c.w = w;
      c.h = u32(1.0f + float(hsrc) * yscale);
      c.tl = m_tl;
      c.dest = m_dest << 5;
      c.bytes = c.h * (m_stride << 5);
      m_stats.copies.push_back(c);
      break;
    }
    default:
      break;
    }
  }
  void OnIndexedLoad(CPArray array, u32, u16 address, u8 size) override {
    ++m_stats.idx_loads;
    m_stats.load_draws.push_back(m_stats.draws);
    const u32 lo = address, hi = u32(address) + u32(size);
    if (lo <= m_stats.word && m_stats.word < hi) {
      M10LoadRec r;
      r.draw = m_stats.draws;
      r.kind = 0;
      r.array = static_cast<u32>(array);
      m_stats.loads.push_back(r);
      m_pending_load = true;
    }
  }
  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
                          const u8*) override {
    ++m_stats.draws;
    m_stats.verts += num_vertices;
    const u32 v = vat & 7;
    const u32 comp =
        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
    const u32 ia = m_cp.matrix_index_a.Hex;
    const u32 ib = m_cp.matrix_index_b.Hex;
    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
                        (ib >> 18) & 63};
    M10DrawRec d;
    if ((comp & VB_HAS_POSMTXIDX) == 0 && idx[0] == m_stats.slot) d.cons_pos = 1;
    for (u32 i = 0; i < 8; ++i) {
      const bool enabled = i < (m_numtex & 15);
      if ((comp & (VB_HAS_TEXMTXIDX0 << i)) == 0 && enabled &&
          idx[1 + i] == m_stats.slot) {
        d.cons_texmask |= 1u << i;
      }
    }
    d.cull = (m_gen >> 14) & 3u;
    d.scis_tl = m_scis_tl;
    d.scis_br = m_scis_br;
    const u32 tlx = (m_scis_tl >> 12) & 0x7ffu, tly = m_scis_tl & 0x7ffu;
    const u32 brx = (m_scis_br >> 12) & 0x7ffu, bry = m_scis_br & 0x7ffu;
    d.scis_empty = (tlx > brx || tly > bry) ? 1 : 0;
    d.ztest = m_zmode & 1u;
    d.zfunc = (m_zmode >> 1) & 7u;
    d.zupdate = (m_zmode >> 4) & 1u;
    m_stats.drawrec.push_back(d);
    m_pending_draw = true;
  }
  void OnDisplayList(u32, u32) override {}
  void OnNop(u32) override {}
  void OnUnknown(u8 opcode, const u8*) override {
    if (opcode == 0x44 || opcode == 0x48)
      ++m_stats.benign;
    else
      ++m_stats.unknown;
  }
  void OnCommand(const u8* data, u32 size) override {
    const u32 off = u32(data - m_base);
    if (m_pending_load && !m_stats.loads.empty()) {
      m_stats.loads.back().off = off;
      m_stats.loads.back().size = size;
      m_pending_load = false;
    }
    if (m_pending_draw && !m_stats.drawrec.empty()) {
      m_stats.drawrec.back().off = off;
      m_stats.drawrec.back().size = size;
      m_pending_draw = false;
    }
  }
  CPState& GetCPState() override { return m_cp; }

private:
  const u8* m_base;
  CPState m_cp;
  M10Order& m_stats;
  u32 m_numtex = 0;
  bool m_pending_load = false;
  bool m_pending_draw = false;
  // M10 step 3: live BP rasterizer/copy state (seeded from recorded BPMem).
  u32 m_gen = 0;
  u32 m_scis_tl = 0, m_scis_br = 0;
  u32 m_zmode = 0;
  u32 m_tl = 0, m_wh = 0, m_dest = 0, m_stride = 0, m_yscale = 0;
};
static M10Order RunM10Order(const std::vector<u8>& src, const u32* cp_mem,
                            const u32* xf_regs, const u32* bp_mem, u32 slot) {
  M10Order stats;
  stats.slot = slot;
  stats.word = slot * 4 + 3;
  if (src.empty()) return stats;
  M10OrderWalk walk(src.data(), cp_mem, xf_regs, bp_mem, slot, stats);
  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
  return stats;
}

// Snapshot of the live video registers, restored after the sequence so the
// game's own command stream keeps decoding with the state it expects.
struct LiveState {
  std::vector<u32> bp, cp, xf;
  std::vector<u8> tmem;
};
static LiveState SaveLive() {
  LiveState l;
  l.bp.assign(reinterpret_cast<const u32*>(&bpmem),
              reinterpret_cast<const u32*>(&bpmem) + FifoDataFile::BP_MEM_SIZE);
  l.cp.assign(256, 0);
  g_main_cp_state.FillCPMemoryArray(l.cp.data());
  l.xf.assign(reinterpret_cast<const u32*>(&xfmem),
              reinterpret_cast<const u32*>(&xfmem) +
                  FifoDataFile::XF_MEM_SIZE + FifoDataFile::XF_REGS_SIZE);
  l.tmem.assign(s_tex_mem.begin(), s_tex_mem.end());
  return l;
}
static void Run(const std::vector<u8>& bytes) {
  u32 cycles = 0;
  OpcodeDecoder::RunFifo<false>(
      DataReader(const_cast<u8*>(bytes.data()), const_cast<u8*>(bytes.data()) + bytes.size()),
      &cycles);
}
static void RunPre(const std::vector<u8>& bytes) {
  u32 cycles = 0;
  OpcodeDecoder::RunFifo<true>(
      DataReader(const_cast<u8*>(bytes.data()), const_cast<u8*>(bytes.data()) + bytes.size()),
      &cycles);
}
static void RestoreLive(const LiveState& l) {
  std::memcpy(s_tex_mem.data(), l.tmem.data(), l.tmem.size());
  std::vector<u8> v =
      PreludeFrom(l.bp.data(), l.cp.data(), l.xf.data(), l.xf.data() + FifoDataFile::XF_MEM_SIZE);
  Run(v);
  // The live preprocess CP state is a copy of the live main CP state, which is
  // what the deterministic GPU path expects when the game's own stream resumes.
  CopyPreprocessCPStateFromMain();
  VertexLoaderManager::MarkAllDirty();
}
static void Event(const char* action, const char* detail = "") {
  std::fprintf(Output(),
               "{\"event\":\"replay\",\"schema\":2,\"action\":\"%s\",\"wall\":%.6f,"
               "\"replay\":%u,\"bytes\":%zu,\"memory_updates\":%u,\"detail\":\"%s\","
               "\"render_execution\":true}\n",
               action, Now(), replays, frame.size(), memory_updates, detail);
  std::fflush(Output());
}

// Device (Android trial TU) cannot use ExperimentalWindow(): under
// SSX_NATIVE_TRIAL_APP it means trial-Running, and this runs control (no
// request). Use a wall window inside the 3-minute movie race instead.
static inline bool D2Window() {
#ifdef SSX_D2_REPLAY_ALWAYS
  return Now() >= 100.0 && Now() < 200.0;
#else
  return ExperimentalWindow();
#endif
}
// Desktop validation of the DEVICE code path. The Odin gets
// m_use_deterministic_gpu_thread = true for free (dual core + movie), the
// desktop does not (single core). With `--cpu-thread` plus
// SSX_S2_FORCE_DETERMINISM=1, FifoManager::UpdateWantDeterminism(true) flips
// the same flag on the Mac (GPUDeterminismMode::Auto -> gpu_thread = want,
// then && IsDualCoreMode()), so the paired preprocess pass, the aux buffer,
// the PE mask and the aux rewind are all exercised on the host. Restored to
// the live value after the sequence. Never set on the device build: the
// Android launch env has no passthrough, and the device needs no forcing.
static bool ForceDeterminism() {
#ifdef SSX_D2_REPLAY_ALWAYS
  return false;
#else
  static const bool on = [] {
    const char* value = std::getenv("SSX_S2_FORCE_DETERMINISM");
    return value && std::strcmp(value, "1") == 0;
  }();
  return on;
#endif
}
// LoadIndexedXF early-outs when the indexed data equals what is already in
// xfmem (`bool changed = XFReplay::g_transform != nullptr;` then a word
// compare), so replaying an IDENTICAL frame skips XFMemWritten and the write
// loop from replay 2 onward. A real 120 Hz replay applies a camera delta or a
// pose palette at the XFReplay::g_transform seam, and the hook's presence
// forces `changed = true` unconditionally -- i.e. it pays the full XF write
// and matrix-dirty cost on every indexed load. To measure both, the second
// half of the sequence installs a no-op transform: same rendering, but the
// non-early-out cost a transformed replay would pay. Rows carry `xform`.
static void NoopTransform(u16, u32) {}
static constexpr unsigned kTransformFrom = kReplays / 2;
// --- M7 step 3: camera-delta transform ----------------------------------------
// Recorded choice: +0.1f translation on XF mem word 0x003 (position-matrix
// slot 0, row 0, 4th column = tx; row-major 3x4, VertexShaderManager reads
// slots as posMatrices[idx*4]), applied whenever a seam-covered write includes
// that word. Pure function of (address, current value): each replay reloads
// from identical sources first, so no accumulation across passes or replays.
// The projection matrix lives in XF regs (0x1020+), where LoadXFReg never
// fires the seam, so slot 0's tx is the camera-most word the seam can reach.
static unsigned long long s_m7_xform_calls = 0;
static unsigned long long s_m7_xform_hits = 0;
static void M7DeltaTransform(u16 address, u32 count) {
  ++s_m7_xform_calls;
  if (address <= 0x003 && 0x003 < address + count) {
    float* w = &xfmem.posMatrices[3];
    *w += 0.1f;
    ++s_m7_xform_hits;
  }
}
// --- M8 step 2: slot-usage census -------------------------------------------
// Why M7's 152 seam hits move zero pixels: which XF position-matrix slots
// (0-63, words 0x000-0x0FF) actually feed visible draws? Three instruments,
// all env-gated (SSX_M8_CENSUS=1; unset = exact M7 behavior):
//   (a) seam write counts: M8Transform tallies, per call, every pos slot
//       overlapped by [address, address+count). Mode 1 applies no delta.
//   (b) index-state reads: on each seam call the transform also samples the
//       exact matrix-index expressions VertexShaderManager::SetConstants reads
//       (g_main_cp_state.matrix_index_a/b: PosNormalMtxIdx, Tex0-7MtxIdx;
//       VertexShaderManager.cpp:292,307-310,324-327) and tallies each distinct
//       referenced slot. All nine are 6-bit pos-slot indices (& 0x3f); the
//       normal-matrix (&31) sub-path is not separately tabled.
//   (c) stream-epoch draws: M8CensusWalk (next to PeMaskWalk) decodes the
//       verbatim recorded stream once at setup, tracking matrix-index state
//       through CP 0x30/0x40 writes (CPState::LoadCPReg) and XF 0x1018/0x1019
//       writes (XFStateManager::SetTexMatrixChangedA/B write-through to the
//       same CP state), attributing every primitive command to the slots the
//       live index state references. Per-vertex pnmtxidx (the
//       transformmatrices indexed path) is NOT decoded (see report).
// M8 step 3: the slot/proj delta arms live in this same transform (counting
// stays on in every M8 mode, so each delta run carries its own census).
// Mode 2 (SSX_M8_SLOT=N): the M7 +0.1f tx delta retargeted to slot N's 4th
// column (word N*4+3), same pure-function-of-(address,value) shape (no
// accumulation: each replay reloads from identical sources first).
// Mode 3 (SSX_M8_PROJ=1): a +0.1f delta on the projection words (XF regs
// 0x1020-0x1026), applied IF a seam call ever covers one. LoadXFReg's regs
// branch never fires the seam (XFStructs.cpp:250-262 has no g_transform call),
// so regcalls/hits are expected 0: the run is the attempt plus the proof.
static unsigned long long s_m8_calls = 0;
static unsigned long long s_m8_hits = 0;
static unsigned long long s_m8_regcalls = 0;  // seam calls at addr >= 0x1000
static unsigned long long s_m8_writes[64] = {};
static unsigned long long s_m8_reads[64] = {};
static int s_m8_slot = -1;  // mode-2 target slot, else -1
static int s_m8_proj = 0;   // mode-3 flag
// --- M9 step 3: upload-timing survival sampling -------------------------------
// At each seam hit (a write covering the delta word), records the live xfmem
// word before/after the +0.1 (first-hit hexes + mismatch tallies prove the
// perturbed value existed uniformly, no accumulation) and samples the
// XFStateManager dirty flags set by THIS write (LoadIndexedXF order:
// XFMemWritten -> Flush consumes old flags + InvalidateXFRange sets new ones,
// then the data write, then this seam: XFStructs.cpp:294-301). Post-replay
// sampling in the loop below compares live xfmem against the
// SetConstants-uploaded snapshots. All gated on s_m9_surv (unset = M8 shape).
static int s_m9_surv = 0;
static int s_m9_first_hit = 0;
static u32 s_m9_vbefore = 0, s_m9_vafter = 0;
static unsigned long long s_m9_vb_mm = 0, s_m9_va_mm = 0;
static unsigned long long s_m9_hit_dirty_pos = 0, s_m9_hit_dirty_texa = 0;
static unsigned long long s_m9_hit_dirty_texb = 0, s_m9_hit_dirty_pervtx = 0;
// --- M10 step 2: 12-word matrix capture --------------------------------------
// At the first seam hit covering the delta word, captures the slot's full
// 3x4 matrix (words slot*4..slot*4+11) before and after the +0.1f add;
// post-replay sampling captures live xfmem + the consumed snapshot's 12
// words on replay 0 with mismatch tallies across the sequence. Gated on
// s_m10_cap (M10 mode only); unset = M9 shape.
static int s_m10_cap = 0;
static int s_m10_mat_done = 0;
static u32 s_m10_mat_before[12] = {};
static u32 s_m10_mat_after[12] = {};
static u32 s_m10_post_live[12] = {};
static u32 s_m10_post_snap[12] = {};
static int s_m10_snap_which = 0;  // 0 = none resident, 1 = shared pos, 2 = shared tex
static int s_m10_snap_ti = -1;  // resident texgen for which==2
static unsigned s_m10_mm_live = 0, s_m10_mm_snap = 0;
static int s_m10_post_done = 0;
static void M8Transform(u16 address, u32 count) {
  ++s_m8_calls;
  const u32 lo = address, hi = address + count;  // covered words [lo, hi)
  if (lo >= 0x1000) ++s_m8_regcalls;
  for (u32 s = 0; s < 64; ++s) {
    if (lo < s * 4 + 4 && hi > s * 4) ++s_m8_writes[s];
  }
  const u32 ia = g_main_cp_state.matrix_index_a.Hex;
  const u32 ib = g_main_cp_state.matrix_index_b.Hex;
  const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
                      (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
                      (ib >> 18) & 63};
  for (u32 k = 0; k < 9; ++k) {
    bool seen = false;
    for (u32 j = 0; j < k; ++j)
      if (idx[j] == idx[k]) seen = true;
    if (!seen) ++s_m8_reads[idx[k]];
  }
  if (s_m8_slot >= 0) {
    const u32 w = u32(s_m8_slot) * 4 + 3;
    if (lo <= w && w < hi) {
      float* f = &xfmem.posMatrices[w];
      u32 vb = 0;
      std::memcpy(&vb, f, 4);  // read-only when s_m9_surv == 0
      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: pre-add 12-word capture
        const u32 base = u32(s_m8_slot) * 4;
        for (u32 i = 0; i < 12; ++i)
          std::memcpy(&s_m10_mat_before[i], &xfmem.posMatrices[base + i], 4);
      }
      *f += 0.1f;
      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: post-add 12-word capture
        const u32 base = u32(s_m8_slot) * 4;
        for (u32 i = 0; i < 12; ++i)
          std::memcpy(&s_m10_mat_after[i], &xfmem.posMatrices[base + i], 4);
        s_m10_mat_done = 1;
      }
      ++s_m8_hits;
      if (s_m9_surv) {
        u32 va = 0;
        std::memcpy(&va, f, 4);
        if (!s_m9_first_hit) {
          s_m9_vbefore = vb;
          s_m9_vafter = va;
          s_m9_first_hit = 1;
        } else {
          if (vb != s_m9_vbefore) ++s_m9_vb_mm;
          if (va != s_m9_vafter) ++s_m9_va_mm;
        }
        const auto& xfm = Core::System::GetInstance().GetXFStateManager();
        if (xfm.DidPosNormalChange()) ++s_m9_hit_dirty_pos;
        if (xfm.DidTexMatrixAChange()) ++s_m9_hit_dirty_texa;
        if (xfm.DidTexMatrixBChange()) ++s_m9_hit_dirty_texb;
        if (xfm.GetPerVertexTransformMatrixChanges()[0] >= 0) ++s_m9_hit_dirty_pervtx;
      }
    }
  }
  if (s_m8_proj) {
    for (u32 p = XFMEM_SETPROJECTION; p <= XFMEM_SETPROJECTION + 6; ++p) {
      if (lo <= p && p < hi) {
        float* w = reinterpret_cast<float*>(&((u32*)&xfmem)[p]);
        *w += 0.1f;
        ++s_m8_hits;
      }
    }
  }
}

static inline void Step(CPUState& c) {
  NativeSchedule::Step(c);
  RefreshNow(c);
  // M5 step 5: sequence-disabled run (SSX_NATIVE_REPLAY=0). At the same idle
  // seam, emit a one-shot seam marker and arm the resume-XFB capture so the
  // report can compare it against the sequence run. No recording, no replay.
  if (!Enabled() && Output() && phase == Phase::Idle) {
    if (c.pc == 0x801cad24 && c.lr == 0x801cd724 && !render.pending && !update.pending &&
        D2Window() && !DoubleEnabled() && !WaitEnabled() && !SweepEnabled()) {
      auto& dis_system = Core::System::GetInstance();
      int fc = -1;
      if (g_presenter) fc = g_presenter->FrameCount();
      char d[96];
      std::snprintf(d, sizeof(d), "replay_disabled=1 fc=%d", fc);
      Event("record_start", d);
      ArmResumeXfbCapture(dis_system, 1);
      phase = Phase::Done;
    }
    return;
  }
  if (!Enabled() || !Output() || phase == Phase::Done) return;
  if (c.pc != 0x801cad24 || c.lr != 0x801cd724 || render.pending || update.pending) return;
  if (!D2Window()) return;
  auto& system = Core::System::GetInstance();
  auto& recorder = system.GetFifoRecorder();
  if (phase == Phase::Idle) {
    // Capture runs with normal presentation; only the measurement suppresses it.
    // Dual-core note: Android trial builds always run dual-core (the CPUThread
    // ini/GameINI cannot change it), so dual-core and the structurally-true
    // trial scheduler gate are NOT blocks here. Before the bulk section the
    // loop stalls the video thread with FifoManager::PauseAndLock (the same
    // call Core.cpp makes for savestates) and resumes it with RestoreState
    // after, so the 200 run single-consumer just like single-core; the
    // guest is parked inside this CPU-thread dispatch, WaitForGPUIdle
    // serializes each replay, and the watched-window re-hash verifies RAM
    // afterward. An active experiment (Double/Wait/Sweep) still blocks.
    if (!g_ActiveConfig.bImmediateXFB || recorder.IsRecording() ||
        DoubleEnabled() || WaitEnabled() || SweepEnabled()) {
      char why[160];
      std::snprintf(why, sizeof(why), "dual=%d(implicit-allow) imxfb=%d rec=%d dbl=%d wait=%d sweep=%d",
                    int(system.IsDualCoreMode()), int(g_ActiveConfig.bImmediateXFB),
                    int(recorder.IsRecording()),
                    int(DoubleEnabled()), int(WaitEnabled()), int(SweepEnabled()));
      Event("blocked", why);
      phase = Phase::Done;
      return;
    }
    recorder.StartRecording(1, [] {});
    record_wall = Now();
    phase = Phase::Recording;
    {
      // M5 step 5: seam id (presenter frame count) for the continuation
      // comparison between the sequence run and the sequence-disabled run.
      int fc = -1;
      if (g_presenter) fc = g_presenter->FrameCount();
      char d[64];
      std::snprintf(d, sizeof(d), "fc=%d", fc);
      Event("record_start", d);
    }
    // M6 step 3: arm presenter tracing while still live. The recorded
    // original frame presents, so a non-empty pre-sequence count is the
    // tracer's positive control.
    s_pres_before.store(0, std::memory_order_relaxed);
    s_pres_after.store(0, std::memory_order_relaxed);
    s_pres_imm.store(0, std::memory_order_relaxed);
    s_pres_vi.store(0, std::memory_order_relaxed);
    s_pres_dup.store(0, std::memory_order_relaxed);
    s_pres_got_imm.store(false, std::memory_order_relaxed);
    s_pres_got_vi.store(false, std::memory_order_relaxed);
    s_pres_before_hook =
        system.GetVideoEvents().before_present_event.Register([](PresentInfo& info) {
          s_pres_before.fetch_add(1, std::memory_order_relaxed);
          if (info.reason == PresentInfo::PresentReason::Immediate) {
            s_pres_imm.fetch_add(1, std::memory_order_relaxed);
            bool want = false;
            if (s_pres_got_imm.compare_exchange_strong(want, true,
                                                       std::memory_order_relaxed)) {
              s_pres_first_imm_pc.store(info.present_count, std::memory_order_relaxed);
              s_pres_first_imm_fc.store(info.frame_count, std::memory_order_relaxed);
            }
          } else if (info.reason == PresentInfo::PresentReason::VideoInterface) {
            s_pres_vi.fetch_add(1, std::memory_order_relaxed);
            bool want = false;
            if (s_pres_got_vi.compare_exchange_strong(want, true,
                                                      std::memory_order_relaxed)) {
              s_pres_first_vi_pc.store(info.present_count, std::memory_order_relaxed);
              s_pres_first_vi_fc.store(info.frame_count, std::memory_order_relaxed);
            }
          } else {
            s_pres_dup.fetch_add(1, std::memory_order_relaxed);
          }
        });
    s_pres_after_hook =
        system.GetVideoEvents().after_present_event.Register([](PresentInfo&) {
          s_pres_after.fetch_add(1, std::memory_order_relaxed);
        });
    return;
  }
  if (phase == Phase::Recording) {
    FifoDataFile* file = recorder.GetRecordedFile();
    const bool ready = !recorder.IsRecording() && file && file->GetFrameCount() >= 1;
    if (!ready) {
      if (Now() - record_wall > 2.0) {
        Event("record_failed");
        s_pres_before_hook.reset();  // M6 step 3: never leave tracing armed
        s_pres_after_hook.reset();
        phase = Phase::Done;
      }
      return;
    }
    const FifoFrameInfo& info = file->GetFrame(0);
    frame = info.fifoData;
    memory_updates = unsigned(info.memoryUpdates.size());
    fifo_start = info.fifoStart;
    fifo_end = info.fifoEnd;
    Event("recorded");
    phase = Phase::Measuring;
    return;
  }
  // One seam visit performs the whole 200 with the guest parked, so RAM and
  // video state cannot drift between replays. On dual-core Android the video
  // thread consumes the fifo concurrently, so stall it first with the same
  // savestate-tested PauseAndLock/RestoreState pair Core.cpp uses; the
  // recompiled dispatches execute inline on this CPU thread either way.
  // Flip before PauseAndLock: PauseAndLock itself branches on the flag (the
  // deterministic path skips the WaitYield), so the device ordering is matched.
  const bool forced_determinism = ForceDeterminism() && system.IsDualCoreMode();
  if (forced_determinism) system.GetFifo().UpdateWantDeterminism(true);
  system.GetFifo().PauseAndLock();
  Event("gpu_stall", forced_determinism ? "forced_determinism=1" : "");
  // The CPU-side gather-pipe accumulator (partial 32 B burst + count) is not
  // covered by PauseAndLock. Drain full bursts downstream, snapshot the
  // residual with the public DoState, and restore it after the bulk section so
  // the first live pipe write on resume sees exact state.
  auto& gpfifo = system.GetGPFifo();
  gpfifo.UpdateGatherPipe();
  std::vector<u8> pipe_snap(1024, 0);
  size_t pipe_used = 0;
  {
    u8* wptr = pipe_snap.data();
    PointerWrap w(&wptr, pipe_snap.size(), PointerWrap::Mode::Write);
    gpfifo.DoState(w);
    pipe_used = size_t(wptr - pipe_snap.data());
  }
  Event("pipe_saved");
  FifoDataFile* file = recorder.GetRecordedFile();
  auto& live_memory = system.GetMemory();
  auto& fifo = system.GetFifo();
  const size_t ram_size = live_memory.GetRAM() ? live_memory.GetRamSize() : 0;
  const size_t exram_size = live_memory.GetEXRAM() ? live_memory.GetExRamSize() : 0;
  std::vector<u8> saved_ram(live_memory.GetRAM(), live_memory.GetRAM() + ram_size);
  std::vector<u8> saved_exram(exram_size ? std::vector<u8>(live_memory.GetEXRAM(),
                                                           live_memory.GetEXRAM() + exram_size)
                                         : std::vector<u8>());
  const LiveState live = SaveLive();

  // The deterministic GPU path is the one that consumes the aux buffer. It is
  // true on the Odin (dual core + movie) and false on the desktop (single
  // core); the whole D2b failure lives in that difference.
  const bool deterministic = fifo.UseDeterministicGPUThread();
  // Always built (the counters are the receipt for the aux-budget arithmetic);
  // frame_pre is only executed when the deterministic path is active.
  const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
  // M8 steps 2-3: mode select (parsed early: the stream walk runs at setup).
  // 0 = unset = exact M7 behavior; 1 = census (SSX_M8_CENSUS=1, counts only);
  // 2 = slot delta (SSX_M8_SLOT=N, 0-63); 3 = projection attempt (SSX_M8_PROJ=1).
  // Precedence: SLOT > PROJ > CENSUS. Counting stays on in every M8 mode.
  const int m8_slot = [] {
    const char* v = std::getenv("SSX_M8_SLOT");
    if (!v || !*v) return -1;
    int n = 0;
    for (const char* p = v; *p; ++p) {
      if (*p < '0' || *p > '9') return -1;
      n = n * 10 + (*p - '0');
      if (n > 63) return -1;
    }
    return n;
  }();
  const int m8_proj = [] {
    const char* v = std::getenv("SSX_M8_PROJ");
    return v && std::strcmp(v, "1") == 0 ? 1 : 0;
  }();
  const int m8_mode = m8_slot >= 0 ? 2 : (m8_proj ? 3 : ([] {
                        const char* v = std::getenv("SSX_M8_CENSUS");
                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                      })());
  // M9 steps 2-4: mode select (parsed early: the stream walks run at setup).
  // 0 = unset = M8/M7 behavior; 1 = census (SSX_M9_CENSUS=1: VAT+texgen walk,
  // counts only); 2 = slot delta (SSX_M9_SLOT=N, 0-63: M8 mode-2 delta +
  // VAT+texgen walk). Precedence: SLOT > CENSUS; M9 overrides M8 when set.
  // Counting stays on in every M9 mode, so each delta run carries its own
  // M8 census and its own M9 VAT census.
  // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
  // (all M9 walks + survival receipts ride along as cross-checks) and arms
  // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
  const int m10_slot = [] {
    const char* v = std::getenv("SSX_M10_SLOT");
    if (!v || !*v) return -1;
    int n = 0;
    for (const char* p = v; *p; ++p) {
      if (*p < '0' || *p > '9') return -1;
      n = n * 10 + (*p - '0');
      if (n > 63) return -1;
    }
    return n;
  }();
  const int m10_mode = m10_slot >= 0 ? 2 : 0;
  // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
  // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
  // walked for receipts); =2 replaces EVERY draw (positive control for the
  // patch machinery + xdiff chain). Only in M10 mode 2; the delta is
  // disarmed in NOP modes so xdiff measures pixel contribution alone.
  const int m10_nopcons = m10_mode == 2 ? ([] {
                            const char* v = std::getenv("SSX_M10_NOPCONS");
                            if (v && std::strcmp(v, "2") == 0) return 2;
                            return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                          })()
                                        : 0;
  // M10 step 3: SSX_M10_RAMCOPY=1 forces EFB/XFB copies to RAM for the
  // sequence (default config skips them: GFX_HACK_SKIP_*_TO_RAM default
  // true, XFB dest then filled with the fuchsia uninit pattern).
  // Precedent: the bImmediateXFB flip. Re-applied at every loop top (any
  // mid-sequence config refresh cannot clobber it); restored after.
  // SSX_M10_RAMREF=1 (step-3 true-delta arm, needs nop=0): implies RAMCOPY
  // and splits the sequence at kTransformFrom — replays 0..99 pristine
  // (counting on, delta off), 100..199 delta — storing replay 99's
  // rendered scratch frame as ref2 and diffing replays 100+ against it.
  const int m10_ramcopy = m10_mode == 2 ? ([] {
                            const char* v = std::getenv("SSX_M10_RAMCOPY");
                            const char* r = std::getenv("SSX_M10_RAMREF");
                            const int ref =
                                (r && std::strcmp(r, "1") == 0) ? 1 : 0;
                            return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
                          })()
                                        : 0;
  const int m10_ramref =
      (m10_mode == 2 && m10_nopcons == 0) ? ([] {
        const char* r = std::getenv("SSX_M10_RAMREF");
        return r && std::strcmp(r, "1") == 0 ? 1 : 0;
      })()
                                         : 0;
  const int m9_slot = m10_mode != 0 ? m10_slot : [] {
    const char* v = std::getenv("SSX_M9_SLOT");
    if (!v || !*v) return -1;
    int n = 0;
    for (const char* p = v; *p; ++p) {
      if (*p < '0' || *p > '9') return -1;
      n = n * 10 + (*p - '0');
      if (n > 63) return -1;
    }
    return n;
  }();
  const int m9_mode = m10_mode != 0 ? 2 : (m9_slot >= 0 ? 2 : ([] {
                        const char* v = std::getenv("SSX_M9_CENSUS");
                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                      })());
  // M9 step 3: survival sampling (SSX_M9_SURV=1). Arms only with a slot delta
  // (M9 mode 2); elsewhere parsed but inert.
  const int m9_surv = m9_mode == 2 ? ([] {
                        const char* v = std::getenv("SSX_M9_SURV");
                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                      })()
                                   : 0;
  // M8 step 2: stream-epoch census over the verbatim recorded stream. The XFB
  // scratch patch touches BP dest addresses only, so verbatim and executed
  // streams agree on draws and index state. M9 modes carry their own M8 census.
  const M8Census m8stream = (m8_mode != 0 || m9_mode != 0)
                                ? RunM8Census(frame, file->GetCPMem(), file->GetXFRegs())
                                : M8Census{};
  // M9 step 2: per-draw VAT + texgen-enablement census (same stream).
  const M9Census m9stream = m9_mode != 0 ? RunM9Census(frame, file->GetCPMem(),
                                                       file->GetXFRegs())
                                         : M9Census{};
  // M10 step 2: hit/draw order stamps + consuming-draw spans (same stream).
  // M10 step 3: the same walk also records render-target epochs + per-draw
  // rasterizer state (BP seeded from recorded BPMem).
  const M10Order m10stream =
      m10_mode != 0 ? RunM10Order(frame, file->GetCPMem(), file->GetXFRegs(),
                                  file->GetBPMem(), u32(m10_slot))
                    : M10Order{};

  // M5 step 2: reference hash of the live XFB after the original frame, taken
  // before the first restore. After every replay the same range is hashed
  // again (before the next restore) and compared.
  u64 xfb_ref = 0;
  bool xfb_ref_ok = false;
  if (mask.xfb.found && mask.xfb.bytes > 0) {
    if (u8* ptr = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
      xfb_ref = RamHash(ptr, mask.xfb.bytes);
      xfb_ref_ok = true;
    }
  }
  unsigned xfb_equal_count = 0;

  // M5 step 4: replay-owned XFB destination. Allocated once from the top of
  // the recorded frame's unused guest RAM: 16-byte aligned, 0x100 guard gap
  // above the highest byte used by any recorded RAM memory update or the live
  // XFB, in the same address base as the live XFB, with the scratch XFB (same
  // byte size) fitting below the RAM top. Verified with GetPointerForRange and
  // checked for overlap with the live XFB in offset domain. The scratch lies
  // inside the S2 whole-RAM watched window, but the sequence restores all of
  // RAM/EXRAM afterwards, so the re-hash still verifies. Non-XFB EFB copies
  // (copy_to_vram) keep their destinations; only the 0x4b writes governing
  // XFB copies are retargeted, in the replay copies of both the execute and
  // the preprocess streams (same layout, same offsets).
  u32 xfb_scratch_addr = 0;
  bool xfb_scratch_ok = false;
  bool xfb_patch_bad = false;
  unsigned xfb_patch_n = 0;
  std::vector<u8> frame_exec = frame;
  std::vector<u8> frame_pre_exec = frame_pre;
  if (mask.xfb.found && mask.xfb.bytes > 0 && ram_size > 0) {
    const u32 ram_mask = live_memory.GetRamMask();
    const u32 xfb_off = mask.xfb.addr & ram_mask;
    u32 top_used = xfb_off + mask.xfb.bytes;
    for (const auto& update : file->GetFrame(0).memoryUpdates) {
      if ((update.address & 0x10000000u) == 0) {  // RAM, not EXRAM
        const u32 end = (update.address & ram_mask) + u32(update.data.size());
        if (end > top_used) top_used = end;
      }
    }
    const u32 base = mask.xfb.addr & ~ram_mask;
    const u32 cand_off = (top_used + 0x100u + 15u) & ~15u;
    if (cand_off >= top_used && cand_off + mask.xfb.bytes <= u32(ram_size)) {
      const u32 cand = base | cand_off;
      const bool no_overlap =
          (cand_off + mask.xfb.bytes <= xfb_off || cand_off >= xfb_off + mask.xfb.bytes);
      if (no_overlap && live_memory.GetPointerForRange(cand, mask.xfb.bytes) != nullptr) {
        // Fail closed: every governing 0x4b must be a well-formed 5-byte
        // GX_LOAD_BP_REG at the recorded offset in both copies.
        bool patch_ok = !mask.xfb_addr_offsets.empty();
        std::vector<u32> offs = mask.xfb_addr_offsets;
        // Dedupe (several XFB triggers may share one governing write).
        for (size_t i = 0; i < offs.size(); ++i)
          for (size_t j = i + 1; j < offs.size();) {
            if (offs[j] == offs[i])
              offs.erase(offs.begin() + static_cast<std::vector<u32>::difference_type>(j));
            else
              ++j;
          }
        for (u32 off : offs) {
          for (const std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
            if (off + 5 > s->size() || (*s)[off] != 0x61 || (*s)[off + 1] != BPMEM_EFB_ADDR)
              patch_ok = false;
          }
        }
        if (patch_ok) {
          xfb_scratch_addr = cand;
          xfb_patch_n = unsigned(offs.size());
          const u32 vv = cand >> 5;  // BP value domain (address >> 5)
          for (u32 off : offs) {
            for (std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
              (*s)[off + 2] = u8(vv >> 16);
              (*s)[off + 3] = u8(vv >> 8);
              (*s)[off + 4] = u8(vv);
            }
          }
          xfb_scratch_ok = true;
        } else {
          xfb_patch_bad = true;
        }
      }
    }
  }
  // M10 step 3: NOP-collective arm. Consuming-draw spans come from the M10
  // walk over the verbatim stream; both replay streams share its layout
  // (scratch patch changes BP values, not sizes). Fail closed: any bad span
  // disables the patch and runs verbatim.
  std::vector<u8> frame_nop_exec, frame_nop_pre;
  u32 m10_nop_draws = 0, m10_nop_bytes = 0;
  bool m10_nop_ok = false;
  if (m10_nopcons && m10_mode != 0) {
    frame_nop_exec = frame_exec;
    frame_nop_pre = frame_pre_exec;
    bool patch_ok = !m10stream.drawrec.empty();
    u32 nd = 0, nb = 0;
    for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
      const M10DrawRec& dr = m10stream.drawrec[d];
      const bool hit = m10_nopcons == 2 || dr.cons_pos != 0 ||
                       dr.cons_texmask != 0;
      if (!hit) continue;
      if (dr.size == 0 || dr.off + dr.size > frame_nop_exec.size() ||
          dr.off + dr.size > frame_nop_pre.size()) {
        patch_ok = false;
        break;
      }
      std::memset(frame_nop_exec.data() + dr.off, 0x00, dr.size);
      std::memset(frame_nop_pre.data() + dr.off, 0x00, dr.size);
      ++nd;
      nb += dr.size;
    }
    if (patch_ok && nd > 0) {
      m10_nop_ok = true;
      m10_nop_draws = nd;
      m10_nop_bytes = nb;
    }
  }
  const std::vector<u8>& exec_stream =
      m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
  const std::vector<u8>& pre_stream =
      m10_nop_ok ? frame_nop_pre : (xfb_scratch_ok ? frame_pre_exec : frame_pre);
  unsigned xfb_scratch_count = 0;
  unsigned live_same_count = 0;
  unsigned live_ok_count = 0;
  u64 live_xfb_first = 0;
  bool live_xfb_have = false;

  const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
  const std::vector<u8> prelude = Prelude(file);
  ApplyMemory(system, file);
  Run(prelude);
  CopyPreprocessCPStateFromMain();
  VertexLoaderManager::MarkAllDirty();
  // M7 step 1b: unsuppressed gap mode (default off = M6 behavior).
  const bool m7_no_suppress = [] {
    const char* v = std::getenv("SSX_M7_NO_SUPPRESS");
    return v && std::strcmp(v, "1") == 0;
  }();
  // M7 step 2: transform select. Unset = M6 behavior (no-op from replay 100);
  // SSX_M7_XFORM=full installs the no-op for the full sequence (S2 arm-2
  // shape); SSX_M7_XFORM=delta installs the step-3 camera delta.
  const int m7_xform = [] {
    const char* v = std::getenv("SSX_M7_XFORM");
    if (v && std::strcmp(v, "full") == 0) return 1;
    if (v && std::strcmp(v, "delta") == 0) return 2;
    return 0;
  }();
  {
    char detail[512];
    std::snprintf(detail, sizeof(detail),
                  "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
                  "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d",
                  int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                  mask.display_lists, mask.dl_bytes, mask.indexed,
                  mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                  mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                  xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
                  m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref);
    Event("restored", detail);
  }
  auto* const saved_transform = XFReplay::g_transform;
  const bool m10_skipx_pre = g_ActiveConfig.bSkipXFBCopyToRam;
  const bool m10_skipe_pre = g_ActiveConfig.bSkipEFBCopyToRam;
  const bool m10_defer_pre = g_ActiveConfig.bDeferEFBCopies;
  if (m10_ramcopy) {
    g_ActiveConfig.bSkipXFBCopyToRam = false;
    g_ActiveConfig.bSkipEFBCopyToRam = false;
    g_ActiveConfig.bDeferEFBCopies = false;
  }
  g_ActiveConfig.bImmediateXFB = false;
  // M6 step 2: install the scoped bus; the header's own counter moves to it
  // (still counts every trigger) while the live listeners stay on the saved
  // bus. Each trigger no longer runs TextureCacheBase::OnFrameEnd
  // (FlushEFBCopies + Cleanup): the dpend/dtex receipts below measure the
  // S2 section-A tension (deferred queue growth, frozen eviction).
  s_after_frame_triggers = 0;
  s_after_frame_live = 0;
  s_m7_trig_imx = -1;
  auto& m6_bus = system.GetVideoEvents().after_frame_event;
  auto m6_saved_bus = m6_bus;
  Common::EventHook m6_after_frame_hook, m6_live_sentinel_hook;
  if (m7_no_suppress) {
    // M7 step 1b: M5 shape on the live bus (probe last, sentinel live).
    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
      ++s_after_frame_triggers;
      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
    });
    m6_live_sentinel_hook =
        m6_bus.Register([](Core::System&) { ++s_after_frame_live; });
  } else {
    m6_bus = Common::HookableEvent<Core::System&>();
    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
      ++s_after_frame_triggers;
      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
    });
    m6_live_sentinel_hook =
        m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
  }
  const SideFx fx_base = CaptureSideFx(system);
  // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
  // stalled from here on, so these reads race nothing) + replay-local frame
  // counter reset.
  const unsigned long long pres0_before = s_pres_before.load(std::memory_order_relaxed);
  const unsigned long long pres0_after = s_pres_after.load(std::memory_order_relaxed);
  const unsigned long long pres0_imm = s_pres_imm.load(std::memory_order_relaxed);
  const unsigned long long pres0_vi = s_pres_vi.load(std::memory_order_relaxed);
  const unsigned long long pres0_dup = s_pres_dup.load(std::memory_order_relaxed);
  s_m6_frame = 0;
  // M6 step 4: fail-closed g_record_fifo_data guard (the M5 loop-top check
  // below is kept: sample before every replay, emit record_flag_set and stop
  // the sequence on true). Negative control: SSX_M6_ARM_RECORD=1 arms the
  // sampled flag before replay 0 through the public global (no vendor
  // change), proving the guard fires; restored to false after the sequence so
  // the live session resumes unarmed. FifoRecorder::StartRecording was
  // considered and rejected for the arming: its listener sets the flag from
  // IsRecording() on the next after_frame trigger, which under suppression
  // never reaches the live bus — the flag itself is the guard's sampled
  // condition and the exact hazard (it gates WriteGPCommand/UseMemory).
  const bool m6_arm_record = [] {
    const char* v = std::getenv("SSX_M6_ARM_RECORD");
    return v && std::strcmp(v, "1") == 0;
  }();
  if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = true;
  // Min/max trackers over the per-replay deltas for the summary receipt.
  long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
  long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
  long long min_dafter_live = 0, max_dafter_live = 0;
  long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
  long long min_trigimx = 0, max_trigimx = 0;  // M7 step 1b: in-Trigger flag sample
  long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
  bool fx_first = true;
  // M7 steps 2-3: pre-loop install for full/delta modes (the M6 mid-loop
  // install below now runs in default mode only; same behavior there).
  if (m7_xform == 1) XFReplay::g_transform = &NoopTransform;
  if (m7_xform == 2) {
    s_m7_xform_calls = 0;
    s_m7_xform_hits = 0;
    XFReplay::g_transform = &M7DeltaTransform;
  }
  // M8 steps 2-3: census/slot/proj transform (counting always on; delta
  // arms per mode). Overrides the M7 select above when set; unset = M7 behavior.
  // M9 overrides M8 when set (M9 modes reuse M8Transform + counters: same
  // seam tallies, same slot-delta shape, plus the M9 VAT census at setup).
  // M9 step 3: post-replay survival tallies (live xfmem vs snapshots).
  unsigned m9_xf_after = 0, m9_xf_before = 0, m9_xf_other = 0;
  unsigned m9_pv_after = 0, m9_pv_before = 0, m9_pv_other = 0;
  unsigned m9_pos_res = 0, m9_pos_after = 0, m9_pos_before = 0, m9_pos_other = 0;
  unsigned m9_tex_res = 0, m9_tex_after = 0, m9_tex_before = 0, m9_tex_other = 0;
  unsigned m9_dirty_post = 0;
  s_m9_surv = 0;
  if (m9_mode != 0) {
    s_m8_calls = 0;
    s_m8_hits = 0;
    s_m8_regcalls = 0;
    for (auto& w : s_m8_writes) w = 0;
    for (auto& r : s_m8_reads) r = 0;
    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref) ? m9_slot : -1;
    s_m8_proj = 0;
    s_m9_surv = m9_surv;
    s_m9_first_hit = 0;
    s_m9_vbefore = s_m9_vafter = 0;
    s_m9_vb_mm = s_m9_va_mm = 0;
    s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
    s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref) ? 1 : 0;
    s_m10_mat_done = 0;
    s_m10_post_done = 0;
    s_m10_snap_which = 0;
    s_m10_snap_ti = -1;
    s_m10_mm_live = s_m10_mm_snap = 0;
    for (u32 i = 0; i < 12; ++i)
      s_m10_mat_before[i] = s_m10_mat_after[i] = s_m10_post_live[i] =
          s_m10_post_snap[i] = 0;
    XFReplay::g_transform = &M8Transform;
  } else if (m8_mode != 0) {
    s_m8_calls = 0;
    s_m8_hits = 0;
    s_m8_regcalls = 0;
    for (auto& w : s_m8_writes) w = 0;
    for (auto& r : s_m8_reads) r = 0;
    s_m8_slot = m8_mode == 2 ? m8_slot : -1;
    s_m8_proj = m8_mode == 3 ? 1 : 0;
    XFReplay::g_transform = &M8Transform;
  }
  // M10 step 3: RAMREF ref2 storage + tallies (true-delta arm).
  std::vector<u8> m10_ref2;
  bool m10_ref2_ok = false;
  u64 m10_ref2_hash = 0, m10_hk_hash = 0;
  unsigned m10_n2 = 0, m10_gt0 = 0, m10_uniform2 = 0;
  unsigned m10_xd2_min = 0, m10_xd2_max = 0;
  int m10_xdmax2_max = 0;
  double m10_xdmean2_min = 0, m10_xdmean2_max = 0;
  bool m10_xd2_first = true;
  u32 m10_samp_r[3] = {};
  unsigned m10_samp_xd[3] = {};
  int m10_samp_xm[3] = {};
  double m10_samp_xn[3] = {};
  unsigned m10_samp_n = 0;
  const double seq_start = Now();
  for (replays = 0; replays < kReplays; ++replays) {
    // M5 step 3, fail-closed: the recorder must be idle; a replay that
    // re-arms g_record_fifo_data would corrupt any live capture.
    if (OpcodeDecoder::g_record_fifo_data) {
      char rd[64];
      std::snprintf(rd, sizeof(rd), "replay=%u armed=%d", replays, int(m6_arm_record));
      Event("record_flag_set", rd);
      break;
    }
    const SideFx fx_before = CaptureSideFx(system);
    s_m7_trig_imx = -1;  // M7 step 1b: this replay's in-Trigger sample (or -1)
    const double wall_start = Now();
    const double cpu_start = ThreadCpuMs();
    // Restore before EVERY replay: recorded memory updates and TMEM (the
    // replay's own EFB copies write into guest RAM and can land on recorded
    // vertex/palette regions), then the recorded CP registers into both CP
    // states so the execute and preprocess passes start from identical array
    // bases, strides and VATs.
    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
      XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
    if (replays == kTransformFrom && m10_ramref) {  // M10 step 3: arm delta half
      s_m8_slot = m10_slot;
      s_m10_cap = 1;
    }
    if (m10_ramcopy) {  // M10 step 3: hold the forced-RAM flip every replay
      g_ActiveConfig.bSkipXFBCopyToRam = false;
      g_ActiveConfig.bSkipEFBCopyToRam = false;
      g_ActiveConfig.bDeferEFBCopies = false;
    }
    ApplyMemory(system, file);
    const double t_mem = Now();
    Run(cp_prelude);
    CopyPreprocessCPStateFromMain();
    VertexLoaderManager::MarkAllDirty();
    const double t_cp = Now();
    if (deterministic) RunPre(pre_stream);
    const double t_pre = Now();
    Run(exec_stream);
    if (g_gfx) {
      g_gfx->Flush();
      g_gfx->WaitForGPUIdle();
    }
    const double t_run = Now();
    // M9 step 3: post-replay survival sample (after all Flushes, before the
    // next restore). Compares live xfmem against the SetConstants-uploaded
    // snapshots the shader consumes: transformmatrices[slot] (indexed path),
    // posnormalmatrix[0] when the post-frame PosNormalMtxIdx == slot (shared
    // position), texmatrices[3i] for the lowest-index resident texgen
    // (shared texgen). Values trichotomized against the first-hit
    // before/after hexes (exact u32 compare, no float neighborhood).
    if (m9_surv && s_m9_first_hit) {
      const u32 mw = u32(m9_slot) * 4 + 3;
      u32 xfv = 0;
      std::memcpy(&xfv, &xfmem.posMatrices[mw], 4);
      if (xfv == s_m9_vafter)
        ++m9_xf_after;
      else if (xfv == s_m9_vbefore)
        ++m9_xf_before;
      else
        ++m9_xf_other;
      const auto& vconst = system.GetVertexShaderManager().constants;
      u32 pvv = 0;
      std::memcpy(&pvv, &vconst.transformmatrices[u32(m9_slot)][3], 4);
      if (pvv == s_m9_vafter)
        ++m9_pv_after;
      else if (pvv == s_m9_vbefore)
        ++m9_pv_before;
      else
        ++m9_pv_other;
      const u32 pia = g_main_cp_state.matrix_index_a.Hex;
      const u32 pib = g_main_cp_state.matrix_index_b.Hex;
      if ((pia & 63) == u32(m9_slot)) {
        ++m9_pos_res;
        u32 psv = 0;
        std::memcpy(&psv, &vconst.posnormalmatrix[0][3], 4);
        if (psv == s_m9_vafter)
          ++m9_pos_after;
        else if (psv == s_m9_vbefore)
          ++m9_pos_before;
        else
          ++m9_pos_other;
      }
      const u32 tidx[8] = {(pia >> 6) & 63,  (pia >> 12) & 63, (pia >> 18) & 63,
                           (pia >> 24) & 63, pib & 63,         (pib >> 6) & 63,
                           (pib >> 12) & 63, (pib >> 18) & 63};
      for (u32 ti = 0; ti < 8; ++ti) {
        if (tidx[ti] == u32(m9_slot)) {
          ++m9_tex_res;
          u32 txv = 0;
          std::memcpy(&txv, &vconst.texmatrices[3 * ti][3], 4);
          if (txv == s_m9_vafter)
            ++m9_tex_after;
          else if (txv == s_m9_vbefore)
            ++m9_tex_before;
          else
            ++m9_tex_other;
          break;  // lowest-index resident texgen only
        }
      }
      const auto& xfm = system.GetXFStateManager();
      if (xfm.DidPosNormalChange() || xfm.DidTexMatrixAChange() ||
          xfm.DidTexMatrixBChange() ||
          xfm.GetPerVertexTransformMatrixChanges()[0] >= 0)
        ++m9_dirty_post;
    }
    // M10 step 2: post-replay 12-word sample (live xfmem + the consumed
    // snapshot; replay 0 stored, later replays counted by mismatch).
    if (m10_mode != 0) {
      const u32 m10base = u32(m10_slot) * 4;
      u32 live12[12];
      for (u32 i = 0; i < 12; ++i)
        std::memcpy(&live12[i], &xfmem.posMatrices[m10base + i], 4);
      const auto& m10v = system.GetVertexShaderManager().constants;
      const u32 m10pia = g_main_cp_state.matrix_index_a.Hex;
      const u32 m10pib = g_main_cp_state.matrix_index_b.Hex;
      int m10which = 0, m10ti = -1;
      u32 snap12[12] = {};
      if ((m10pia & 63) == u32(m10_slot)) {
        m10which = 1;
        for (u32 r = 0; r < 3; ++r)
          for (u32 cc = 0; cc < 4; ++cc)
            std::memcpy(&snap12[r * 4 + cc], &m10v.posnormalmatrix[r][cc], 4);
      } else {
        const u32 m10tidx[8] = {(m10pia >> 6) & 63,  (m10pia >> 12) & 63,
                                (m10pia >> 18) & 63, (m10pia >> 24) & 63,
                                m10pib & 63,         (m10pib >> 6) & 63,
                                (m10pib >> 12) & 63, (m10pib >> 18) & 63};
        for (u32 ti = 0; ti < 8; ++ti) {
          if (m10tidx[ti] == u32(m10_slot)) {
            m10which = 2;
            m10ti = int(ti);
            for (u32 r = 0; r < 3; ++r)
              for (u32 cc = 0; cc < 4; ++cc)
                std::memcpy(&snap12[r * 4 + cc],
                            &m10v.texmatrices[3 * ti + r][cc], 4);
            break;
          }
        }
      }
      if (!s_m10_post_done) {
        for (u32 i = 0; i < 12; ++i) {
          s_m10_post_live[i] = live12[i];
          s_m10_post_snap[i] = snap12[i];
        }
        s_m10_snap_which = m10which;
        s_m10_snap_ti = m10ti;
        s_m10_post_done = 1;
      } else {
        for (u32 i = 0; i < 12; ++i) {
          if (live12[i] != s_m10_post_live[i]) {
            ++s_m10_mm_live;
            break;
          }
        }
        for (u32 i = 0; i < 12; ++i) {
          if (snap12[i] != s_m10_post_snap[i]) {
            ++s_m10_mm_snap;
            break;
          }
        }
      }
    }
    // read_ptr == write_ptr after a matched pair, so this compacts zero bytes
    // and rewinds both aux pointers to the base of the 2 MiB buffer.
    if (deterministic) fifo.SyncGPU(Fifo::SyncGPUReason::AuxSpace, false);
    const double cpu_end = ThreadCpuMs();
    const double wall_end = Now();
    replay_wall_ms[replays] = (wall_end - wall_start) * 1000.0;
    replay_cpu_ms[replays] =
        (cpu_start >= 0 && cpu_end >= 0) ? (cpu_end - cpu_start) : -1.0;
    // M5 step 2: hash the XFB destination after this replay, before the next
    // restore. Hashed after wall_end so the hash cost stays out of wall_ms.
    int xfb_equal = 0;
    if (xfb_ref_ok) {
      if (u8* rp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes))
        xfb_equal = (RamHash(rp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
    }
    xfb_equal_count += unsigned(xfb_equal);
    // M5 step 4: scratch compare (hash of the replay-owned region vs the live
    // XFB after the original frame) and the live-XFB-untouched watch (the
    // live range must read the same after every replay of the sequence).
    int xfb_scratch_equal = 0;
    if (xfb_scratch_ok) {
      if (u8* sp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes))
        xfb_scratch_equal = (RamHash(sp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
      if (u8* lp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
        const u64 live_hash = RamHash(lp, mask.xfb.bytes);
        ++live_ok_count;
        if (!live_xfb_have) {
          live_xfb_have = true;
          live_xfb_first = live_hash;
          live_same_count = 1;
        } else if (live_hash == live_xfb_first) {
          ++live_same_count;
        }
      }
    }
    xfb_scratch_count += unsigned(xfb_scratch_equal);
    // M7 step 3: per-replay pixel-diff stats (scratch = this replay's frame,
    // live range = the untouched original). After wall_end, out of wall_ms.
    unsigned xdiff = 0;
    int xdmax = 0;
    double xdmean = 0.0;
    if (xfb_scratch_ok) {
      u8* xdp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
      u8* xlp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes);
      if (xdp && xlp) {
        unsigned long long xdacc = 0;
        for (u32 i = 0; i < mask.xfb.bytes; ++i) {
          const int dd = xdp[i] > xlp[i] ? xdp[i] - xlp[i] : xlp[i] - xdp[i];
          if (dd > 0) {
            ++xdiff;
            xdacc += (unsigned)dd;
            if (dd > xdmax) xdmax = dd;
          }
        }
        if (xdiff > 0) xdmean = double(xdacc) / double(xdiff);
      }
    }
    // M10 step 3: RAMREF ref2 capture + diff (forced-RAM true-delta arm).
    // Replay 99's rendered scratch frame is the pristine reference; replays
    // 100+ (delta) diff against its bytes. After wall_end, out of wall_ms.
    if (m10_ramref && xfb_scratch_ok) {
      u8* r2p = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
      if (r2p) {
        if (replays == kTransformFrom - 1) {
          m10_ref2.assign(r2p, r2p + mask.xfb.bytes);
          m10_ref2_hash = RamHash(r2p, mask.xfb.bytes);
          m10_ref2_ok = true;
        } else if (replays >= kTransformFrom && m10_ref2_ok) {
          ++m10_n2;
          const u64 hh = RamHash(r2p, mask.xfb.bytes);
          if (replays == kTransformFrom) m10_hk_hash = hh;
          if (hh == m10_hk_hash) ++m10_uniform2;
          unsigned x2 = 0;
          int xm2 = 0;
          unsigned long long xa2 = 0;
          for (u32 i = 0; i < mask.xfb.bytes; ++i) {
            const int dd = r2p[i] > m10_ref2[i] ? r2p[i] - m10_ref2[i]
                                               : m10_ref2[i] - r2p[i];
            if (dd > 0) {
              ++x2;
              xa2 += (unsigned)dd;
              if (dd > xm2) xm2 = dd;
            }
          }
          const double xn2 = x2 ? double(xa2) / double(x2) : 0.0;
          if (x2 > 0) {
            ++m10_gt0;
            if (m10_samp_n < 3) {
              m10_samp_r[m10_samp_n] = replays;
              m10_samp_xd[m10_samp_n] = x2;
              m10_samp_xm[m10_samp_n] = xm2;
              m10_samp_xn[m10_samp_n] = xn2;
              ++m10_samp_n;
            }
          }
          if (m10_xd2_first) {
            m10_xd2_min = m10_xd2_max = x2;
            m10_xdmax2_max = xm2;
            m10_xdmean2_min = m10_xdmean2_max = xn2;
            m10_xd2_first = false;
          } else {
            if (x2 < m10_xd2_min) m10_xd2_min = x2;
            if (x2 > m10_xd2_max) m10_xd2_max = x2;
            if (xm2 > m10_xdmax2_max) m10_xdmax2_max = xm2;
            if (xn2 < m10_xdmean2_min) m10_xdmean2_min = xn2;
            if (xn2 > m10_xdmean2_max) m10_xdmean2_max = xn2;
          }
        }
      }
    }
    // M5 step 3: after-state and deltas. Captured after wall_end so the
    // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
    const SideFx fx_after = CaptureSideFx(system);
    const long long dtex =
        static_cast<long long>(fx_after.tex_entries) - static_cast<long long>(fx_before.tex_entries);
    const long long dpend =
        static_cast<long long>(fx_after.pending) - static_cast<long long>(fx_before.pending);
    const long long dframe =
        static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
    const long long dafter =
        static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
    const long long dafter_live = static_cast<long long>(fx_after.after_frame_live) -
                                  static_cast<long long>(fx_before.after_frame_live);
    const long long dpres = static_cast<long long>(fx_after.present_before) -
                            static_cast<long long>(fx_before.present_before);
    const long long dimx =
        static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
    const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
    const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
    const long long trigimx = s_m7_trig_imx;  // M7 step 1b
    if (fx_first) {
      min_dtex = max_dtex = dtex;
      min_dpend = max_dpend = dpend;
      min_dframe = max_dframe = dframe;
      min_dafter = max_dafter = dafter;
      min_dafter_live = max_dafter_live = dafter_live;
      min_dpres = max_dpres = dpres;
      min_dimx = max_dimx = dimx;
      min_trigimx = max_trigimx = trigimx;
      min_pe = max_pe = pediff;
      min_vi = max_vi = vidiff;
      fx_first = false;
    } else {
      if (dtex < min_dtex) min_dtex = dtex;
      if (dtex > max_dtex) max_dtex = dtex;
      if (dpend < min_dpend) min_dpend = dpend;
      if (dpend > max_dpend) max_dpend = dpend;
      if (dframe < min_dframe) min_dframe = dframe;
      if (dframe > max_dframe) max_dframe = dframe;
      if (dafter < min_dafter) min_dafter = dafter;
      if (dafter > max_dafter) max_dafter = dafter;
      if (dafter_live < min_dafter_live) min_dafter_live = dafter_live;
      if (dafter_live > max_dafter_live) max_dafter_live = dafter_live;
      if (dpres < min_dpres) min_dpres = dpres;
      if (dpres > max_dpres) max_dpres = dpres;
      if (dimx < min_dimx) min_dimx = dimx;
      if (dimx > max_dimx) max_dimx = dimx;
      if (trigimx < min_trigimx) min_trigimx = trigimx;
      if (trigimx > max_trigimx) max_trigimx = trigimx;
      if (pediff < min_pe) min_pe = pediff;
      if (pediff > max_pe) max_pe = pediff;
      if (vidiff < min_vi) min_vi = vidiff;
      if (vidiff > max_vi) max_vi = vidiff;
    }
    ++s_m6_frame;  // one emitted capacity row = one replayed frame
    // M7 step 2: tag actual install state (default mode identical to M6).
    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0 ||
                               m9_mode != 0);
    std::fprintf(Output(),
                 "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                 "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                 "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                 "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
                 "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
                 "\"trig_imx\":%d,\"xdiff\":%u,\"xdmax\":%d,\"xdmean\":%.3f,"
                 "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                 wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                 (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                 (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                 (wall_end - t_run) * 1000.0, xform_flag, xfb_equal,
                 dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
                 s_m7_trig_imx, xdiff, xdmax, xdmean, pediff, vidiff,
                 xfb_scratch_equal);
    std::fflush(Output()); // every row survives a post-loop death.
  }
  const double seq_end = Now();
  // M6 step 2: end-state capture, then drop the scoped bus and restore the
  // live bus. Reached on both the normal and the record_flag_set-break paths.
  const SideFx fx_end = CaptureSideFx(system);
  m6_after_frame_hook.reset();
  m6_live_sentinel_hook.reset();
  if (!m7_no_suppress) m6_bus = m6_saved_bus;  // M7 step 1b: bypass never swapped
  if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = false;  // M6 step 4
  // M6 step 3: presenter-tracing receipt (pre = live window from record_start
  // to sequence start; seq = during the sequence), then disarm. Reached on
  // both the normal and the record_flag_set-break paths.
  {
    const unsigned long long e_before = s_pres_before.load(std::memory_order_relaxed);
    const unsigned long long e_after = s_pres_after.load(std::memory_order_relaxed);
    const unsigned long long e_imm = s_pres_imm.load(std::memory_order_relaxed);
    const unsigned long long e_vi = s_pres_vi.load(std::memory_order_relaxed);
    const unsigned long long e_dup = s_pres_dup.load(std::memory_order_relaxed);
    char trace[384];
    std::snprintf(trace, sizeof(trace),
                  "pre_before=%llu pre_after=%llu pre_imm=%llu pre_vi=%llu pre_dup=%llu "
                  "seq_before=%llu seq_after=%llu seq_imm=%llu seq_vi=%llu seq_dup=%llu "
                  "first_imm_pc=%llu first_imm_fc=%llu first_vi_pc=%llu first_vi_fc=%llu",
                  pres0_before, pres0_after, pres0_imm, pres0_vi, pres0_dup,
                  e_before - pres0_before, e_after - pres0_after, e_imm - pres0_imm,
                  e_vi - pres0_vi, e_dup - pres0_dup,
                  s_pres_first_imm_pc.load(std::memory_order_relaxed),
                  s_pres_first_imm_fc.load(std::memory_order_relaxed),
                  s_pres_first_vi_pc.load(std::memory_order_relaxed),
                  s_pres_first_vi_fc.load(std::memory_order_relaxed));
    Event("present_trace", trace);
  }
  s_pres_before_hook.reset();
  s_pres_after_hook.reset();
  // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
  // event. completed = capacity rows actually emitted (record_flag_set stops
  // the sequence early, fail-closed). M6 step 2 adds dafter_live min/max and
  // the end absolutes (texN/pendN/fcN) for the accumulation/growth receipts;
  // M6 step 3 adds dpres/dimx min/max and the imxfb end absolutes.
  {
    char summary[768];
    std::snprintf(summary, sizeof(summary),
                  "completed=%u tex0=%zu pend0=%zu fc0=%d texN=%zu pendN=%zu fcN=%d "
                  "imx0=%d imxN=%d "
                  "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
                  "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
                  "dafter_live_min=%lld dafter_live_max=%lld "
                  "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
                  "trigimx_min=%lld trigimx_max=%lld "
                  "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                  "live_ok=%u live_same=%u",
                  replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
                  fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
                  fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
                  max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
                  min_dpres, max_dpres, min_dimx, max_dimx, min_trigimx, max_trigimx,
                  min_pe, max_pe, min_vi, max_vi, int(xfb_scratch_ok), xfb_scratch_addr,
                  xfb_scratch_count, live_ok_count, live_same_count);
    Event("counters_summary", summary);
  }
  // M7 step 3: seam-application receipt (delta mode only; the bare no-op is
  // uncounted by design). calls = seam invocations during the sequence,
  // hits = writes covering the delta word.
  if (m7_xform == 2) {
    char xs[128];
    std::snprintf(xs, sizeof(xs), "mode=%d calls=%llu hits=%llu", m7_xform,
                  s_m7_xform_calls, s_m7_xform_hits);
    Event("xform_stats", xs);
  }
  // M8 steps 2-3: slot-usage census receipts (every M8 mode: each delta run
  // carries its own census). xform_stats mode 7/8/9 = census/slot/proj;
  // m8_meta carries the stream-epoch census; m8_writes/m8_reads/m8_draws carry
  // the 64-slot CSVs (slot order 0..63); m8_expr0-8 carry the per-expression
  // draw histograms (0=PosNormal, 1-8=Tex0-7).
  if (m8_mode != 0 && m9_mode == 0) {
    char xs[160];
    std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
                  m8_mode == 1 ? 7 : (m8_mode == 2 ? 8 : 9), s_m8_slot, s_m8_calls,
                  s_m8_hits, s_m8_regcalls);
    Event("xform_stats", xs);
  }
  // M9: the M8 stream census rides on M9 runs too (mode = the active mode).
  if (m8_mode != 0 || m9_mode != 0) {
    char meta[448];
    std::snprintf(
        meta, sizeof(meta),
        "mode=%d draws=%u verts=%llu epochs=%u matidx_cp=%u matidx_xf=%u "
        "direct_xfmem=%u direct_pos_words=%u stream_indexed=%u idx_pos=%u idx_reg=%u "
        "projreg_writes=%u numtex0=0x%x numtex_w=%u idxa0=0x%08x idxb0=0x%08x "
        "walk=%u/%zu benign=%u walk_ok=%d",
        m8_mode != 0 ? m8_mode : m9_mode, m8stream.draws,
        (unsigned long long)m8stream.verts, m8stream.epochs,
        m8stream.matidx_cp, m8stream.matidx_xf, m8stream.direct_xfmem,
        m8stream.direct_pos_words, m8stream.indexed, m8stream.idx_pos, m8stream.idx_reg,
        m8stream.projreg_writes, m8stream.numtex0, m8stream.numtex_w, m8stream.idxa0,
        m8stream.idxb0, m8stream.consumed, frame.size(), m8stream.benign,
        int(m8stream.consumed == frame.size() && m8stream.unknown == 0));
    Event("m8_meta", meta);
    char csv[2048];
    int off = 0;
    for (u32 s = 0; s < 64; ++s) {
      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
                           s_m8_writes[s]);
    }
    Event("m8_writes", csv);
    off = 0;
    for (u32 s = 0; s < 64; ++s) {
      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
                           s_m8_reads[s]);
    }
    Event("m8_reads", csv);
    off = 0;
    for (u32 s = 0; s < 64; ++s) {
      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
                           (unsigned long long)m8stream.draws_aff[s]);
    }
    Event("m8_draws", csv);
    for (u32 e = 0; e < 9; ++e) {
      off = 0;
      for (u32 s = 0; s < 64; ++s) {
        if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
        off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
                             (unsigned long long)m8stream.expr[e][s]);
      }
      char ename[16];
      std::snprintf(ename, sizeof(ename), "m8_expr%u", e);
      Event(ename, csv);
    }
  }
  // M9 step 2: VAT + texgen-enablement receipts (every M9 mode: each delta run
  // carries its own M8 census above plus its own M9 VAT census here).
  // xform_stats mode 10/11 = census/slot (same seam counters as M8's 7/8).
  // m9_meta carries the walk summary; m9_path the shared-vs-indexed path table
  // (position + per-texgen); m9_texen the numtex histogram + per-texgen
  // enabled counts; m9_texep the enablement-epoch timeline
  // (draw:numtex,...); m9_vat the vat-index histogram; m9_textype the
  // per-texgen TexGenType histogram (texgen-major, 4 types); m9_reachp the
  // shared-position reach per slot; m9_reach0-7 the shared+enabled texgen
  // reach per slot.
  if (m9_mode != 0) {
    char xs[160];
    std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
                  m9_mode == 1 ? 10 : 11, s_m8_slot, s_m8_calls, s_m8_hits,
                  s_m8_regcalls);
    Event("xform_stats", xs);
    char meta[448];
    std::snprintf(
        meta, sizeof(meta),
        "mode=%d draws=%u verts=%llu vcd_lo=%u vcd_hi=%u vat_w=%u matidx_cp=%u matidx_xf=%u "
        "numtex0=0x%x numtex_w=%u texinfo_w=%u epochs=%u "
        "walk=%u/%zu benign=%u walk_ok=%d",
        m9_mode, m9stream.draws, (unsigned long long)m9stream.verts, m9stream.vcd_lo,
        m9stream.vcd_hi, m9stream.vat_w, m9stream.matidx_cp, m9stream.matidx_xf,
        m9stream.numtex0, m9stream.numtex_w, m9stream.texinfo_w, m9stream.epochs,
        m9stream.consumed, frame.size(), m9stream.benign,
        int(m9stream.consumed == frame.size() && m9stream.unknown == 0));
    Event("m9_meta", meta);
    char path[1024];
    std::snprintf(
        path, sizeof(path),
        "pos_shared=%llu pos_indexed=%llu "
        "tex_shared=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
        "tex_indexed=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
        "tex_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
        "tex_shared_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu",
        (unsigned long long)m9stream.pos_shared, (unsigned long long)m9stream.pos_indexed,
        (unsigned long long)m9stream.tex_shared[0], (unsigned long long)m9stream.tex_shared[1],
        (unsigned long long)m9stream.tex_shared[2], (unsigned long long)m9stream.tex_shared[3],
        (unsigned long long)m9stream.tex_shared[4], (unsigned long long)m9stream.tex_shared[5],
        (unsigned long long)m9stream.tex_shared[6], (unsigned long long)m9stream.tex_shared[7],
        (unsigned long long)m9stream.tex_indexed[0], (unsigned long long)m9stream.tex_indexed[1],
        (unsigned long long)m9stream.tex_indexed[2], (unsigned long long)m9stream.tex_indexed[3],
        (unsigned long long)m9stream.tex_indexed[4], (unsigned long long)m9stream.tex_indexed[5],
        (unsigned long long)m9stream.tex_indexed[6], (unsigned long long)m9stream.tex_indexed[7],
        (unsigned long long)m9stream.tex_enabled[0], (unsigned long long)m9stream.tex_enabled[1],
        (unsigned long long)m9stream.tex_enabled[2], (unsigned long long)m9stream.tex_enabled[3],
        (unsigned long long)m9stream.tex_enabled[4], (unsigned long long)m9stream.tex_enabled[5],
        (unsigned long long)m9stream.tex_enabled[6], (unsigned long long)m9stream.tex_enabled[7],
        (unsigned long long)m9stream.tex_shared_enabled[0],
        (unsigned long long)m9stream.tex_shared_enabled[1],
        (unsigned long long)m9stream.tex_shared_enabled[2],
        (unsigned long long)m9stream.tex_shared_enabled[3],
        (unsigned long long)m9stream.tex_shared_enabled[4],
        (unsigned long long)m9stream.tex_shared_enabled[5],
        (unsigned long long)m9stream.tex_shared_enabled[6],
        (unsigned long long)m9stream.tex_shared_enabled[7]);
    Event("m9_path", path);
    char txe[768];
    int toff = std::snprintf(txe, sizeof(txe), "numtex_hist=");
    for (u32 n = 0; n < 16; ++n) {
      if (toff < 0 || size_t(toff) >= sizeof(txe) - 24) break;
      toff += std::snprintf(txe + toff, sizeof(txe) - size_t(toff), "%s%llu", n ? "," : "",
                            (unsigned long long)m9stream.numtex_hist[n]);
    }
    Event("m9_texen", txe);
    char tep[1024];
    int eoff = 0;
    const u32 nepoch = m9stream.epochs < M9Census::kMaxEpochs ? m9stream.epochs
                                                             : M9Census::kMaxEpochs;
    for (u32 e = 0; e < nepoch; ++e) {
      if (eoff < 0 || size_t(eoff) >= sizeof(tep) - 24) break;
      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), "%s%u:%u", e ? "," : "",
                            m9stream.epoch_draw[e], m9stream.epoch_numtex[e]);
    }
    if (m9stream.epochs > M9Census::kMaxEpochs) {
      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), ",TRUNC=%u",
                            m9stream.epochs);
    }
    Event("m9_texep", tep);
    char vat[256];
    int voff = 0;
    for (u32 i = 0; i < 8; ++i) {
      if (voff < 0 || size_t(voff) >= sizeof(vat) - 24) break;
      voff += std::snprintf(vat + voff, sizeof(vat) - size_t(voff), "%s%llu", i ? "," : "",
                            (unsigned long long)m9stream.vat_hist[i]);
    }
    Event("m9_vat", vat);
    char tty[512];
    int yoff = 0;
    for (u32 t = 0; t < 8; ++t)
      for (u32 ty = 0; ty < 4; ++ty) {
        if (yoff < 0 || size_t(yoff) >= sizeof(tty) - 24) break;
        yoff += std::snprintf(tty + yoff, sizeof(tty) - size_t(yoff), "%s%llu",
                              (t || ty) ? "," : "",
                              (unsigned long long)m9stream.tex_type[t][ty]);
      }
    Event("m9_textype", tty);
    char rcsv[2048];
    int roff = 0;
    for (u32 s = 0; s < 64; ++s) {
      if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
      roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
                            (unsigned long long)m9stream.reach_pos[s]);
    }
    Event("m9_reachp", rcsv);
    for (u32 t = 0; t < 8; ++t) {
      roff = 0;
      for (u32 s = 0; s < 64; ++s) {
        if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
        roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
                              (unsigned long long)m9stream.reach_tex[t][s]);
      }
      char rname[16];
      std::snprintf(rname, sizeof(rname), "m9_reach%u", t);
      Event(rname, rcsv);
    }
    // M9 step 3: survival receipt (armed only in mode 2 with SSX_M9_SURV=1).
    {
      float fb = 0, fa = 0;
      std::memcpy(&fb, &s_m9_vbefore, 4);
      std::memcpy(&fa, &s_m9_vafter, 4);
      char surv[768];
      std::snprintf(
          surv, sizeof(surv),
          "armed=%d slot=%d word=%u hits=%llu first=%d "
          "vbefore=0x%08x vafter=0x%08x fbefore=%g fafter=%g vb_mm=%llu va_mm=%llu "
          "hdirty_pos=%llu hdirty_texa=%llu hdirty_texb=%llu hdirty_pervtx=%llu "
          "n=%u xf_after=%u xf_before=%u xf_other=%u "
          "pv_after=%u pv_before=%u pv_other=%u "
          "pos_res=%u pos_after=%u pos_before=%u pos_other=%u "
          "tex_res=%u tex_after=%u tex_before=%u tex_other=%u "
          "dirty_post=%u zfreeze=%d",
          m9_surv, m9_slot, m9_mode == 2 ? u32(m9_slot) * 4 + 3 : 0, s_m8_hits,
          s_m9_first_hit, s_m9_vbefore, s_m9_vafter, fb, fa, s_m9_vb_mm, s_m9_va_mm,
          s_m9_hit_dirty_pos, s_m9_hit_dirty_texa, s_m9_hit_dirty_texb,
          s_m9_hit_dirty_pervtx, replays, m9_xf_after, m9_xf_before, m9_xf_other,
          m9_pv_after, m9_pv_before, m9_pv_other, m9_pos_res, m9_pos_after,
          m9_pos_before, m9_pos_other, m9_tex_res, m9_tex_after, m9_tex_before,
          m9_tex_other, m9_dirty_post, int(bpmem.genMode.zfreeze));
      Event("m9_surv", surv);
    }
  }
  // M10 step 2: order + matrix receipts (M10 mode only; M9's receipts above
  // ride along as cross-checks). m10_order carries the split counts,
  // m10_loads the covering-load draw clocks, m10_cons the consuming draw
  // indices (1-based), m10_matrix the 12-word captures as u32 hex.
  // Post-sequence copy-flag sample (pre sample at sequence start; the flip
  // is re-applied at every loop top and restored after the receipts).
  const bool m10_skipx_post = g_ActiveConfig.bSkipXFBCopyToRam;
  const bool m10_skipe_post = g_ActiveConfig.bSkipEFBCopyToRam;
  const bool m10_defer_post = g_ActiveConfig.bDeferEFBCopies;
  if (m10_mode != 0) {
    const size_t m10_nload = m10stream.loads.size();
    const size_t m10_ndraw = m10stream.drawrec.size();
    u32 m10_idx_cover = 0, m10_direct_cover = 0;
    u32 m10_arr[16] = {};
    for (const auto& l : m10stream.loads) {
      if (l.kind == 0) {
        ++m10_idx_cover;
        if (l.array < 16) ++m10_arr[l.array];
      } else {
        ++m10_direct_cover;
      }
    }
    u32 m10_cons_pos = 0, m10_cons_tex = 0, m10_cons_any = 0;
    u32 m10_first_cons = 0, m10_last_cons = 0;
    for (size_t d = 0; d < m10_ndraw; ++d) {
      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
                       m10stream.drawrec[d].cons_texmask != 0;
      if (m10stream.drawrec[d].cons_pos) ++m10_cons_pos;
      if (m10stream.drawrec[d].cons_texmask) ++m10_cons_tex;
      if (any) {
        ++m10_cons_any;
        if (m10_first_cons == 0) m10_first_cons = u32(d) + 1;
        m10_last_cons = u32(d) + 1;
      }
    }
    const u32 m10_first_loaddraw =
        m10_nload ? m10stream.loads.front().draw : 0;
    const u32 m10_last_loaddraw = m10_nload ? m10stream.loads.back().draw : 0;
    u32 m10_cons_before = 0;
    for (size_t d = 0; d < m10_ndraw; ++d) {
      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
                       m10stream.drawrec[d].cons_texmask != 0;
      if (any && m10_nload && u32(d) + 1 <= m10_first_loaddraw) ++m10_cons_before;
    }
    u32 m10_loads_before = 0, m10_loads_span = 0;
    for (u32 ld : m10stream.load_draws) {
      if (m10_nload && ld < m10_first_loaddraw) ++m10_loads_before;
      if (m10_nload && m10_cons_any && ld >= m10_first_loaddraw &&
          ld < m10_last_cons)
        ++m10_loads_span;
    }
    char m10o[768];
    std::snprintf(
        m10o, sizeof(m10o),
        "slot=%d word=%u draws=%u verts=%llu idx_loads=%u covering=%zu idx_cover=%u "
        "direct_cover=%u arr12=%u arr13=%u arr14=%u arr15=%u "
        "first_load_draw=%u first_load_off=%u first_load_kind=%u "
        "last_load_draw=%u last_load_off=%u "
        "cons_pos=%u cons_tex=%u cons_any=%u first_cons=%u last_cons=%u "
        "cons_before_first=%u cons_at_after_first=%u loads_before_first=%u "
        "loads_first_to_lastcons=%u seam_hits=%llu seam_per_replay=%llu "
        "walk=%u/%zu benign=%u walk_ok=%d",
        m10_slot, m10stream.word, m10stream.draws,
        (unsigned long long)m10stream.verts, m10stream.idx_loads, m10_nload,
        m10_idx_cover, m10_direct_cover, m10_arr[12], m10_arr[13], m10_arr[14],
        m10_arr[15], m10_first_loaddraw,
        m10_nload ? m10stream.loads.front().off : 0,
        m10_nload ? m10stream.loads.front().kind : 0, m10_last_loaddraw,
        m10_nload ? m10stream.loads.back().off : 0, m10_cons_pos, m10_cons_tex,
        m10_cons_any, m10_first_cons, m10_last_cons, m10_cons_before,
        m10_cons_any - m10_cons_before, m10_loads_before, m10_loads_span,
        s_m8_hits, replays ? s_m8_hits / replays : 0, m10stream.consumed,
        frame.size(), m10stream.benign,
        int(m10stream.consumed == frame.size() && m10stream.unknown == 0));
    Event("m10_order", m10o);
    char m10l[2048];
    int m10loff = 0;
    size_t m10ln = 0;
    for (size_t i = 0; i < m10_nload; ++i) {
      if (m10loff < 0 || size_t(m10loff) >= sizeof(m10l) - 24) break;
      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
                               "%s%u", i ? "," : "", m10stream.loads[i].draw);
      ++m10ln;
    }
    if (m10ln < m10_nload)
      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
                               ",TRUNC=%zu", m10_nload);
    Event("m10_loads", m10l);
    char m10c[8192];
    int m10coff = 0;
    size_t m10cn = 0;
    for (size_t d = 0; d < m10_ndraw; ++d) {
      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
                       m10stream.drawrec[d].cons_texmask != 0;
      if (!any) continue;
      if (m10coff < 0 || size_t(m10coff) >= sizeof(m10c) - 24) break;
      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
                               "%s%u", m10cn ? "," : "", u32(d) + 1);
      ++m10cn;
    }
    if (m10cn < m10_cons_any)
      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
                               ",TRUNC=%u", m10_cons_any);
    Event("m10_cons", m10c);
    char m10m[1024];
    int m10moff = std::snprintf(m10m, sizeof(m10m),
                                "slot=%d word=%u done=%d snap_which=%d snap_ti=%d "
                                "n=%u mm_live=%u mm_snap=%u before=",
                                m10_slot, m10stream.word, s_m10_mat_done,
                                s_m10_snap_which, s_m10_snap_ti, replays,
                                s_m10_mm_live, s_m10_mm_snap);
    const u32* m10lists[4] = {s_m10_mat_before, s_m10_mat_after, s_m10_post_live,
                              s_m10_post_snap};
    const char* m10tags[4] = {"before=", "after=", "live=", "snap="};
    for (u32 l = 0; l < 4; ++l) {
      if (l) {
        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
                                 " %s", m10tags[l]);
      }
      for (u32 i = 0; i < 12; ++i) {
        if (m10moff < 0 || size_t(m10moff) >= sizeof(m10m) - 24) break;
        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
                                 "%s%08x", i ? "," : "", m10lists[l][i]);
      }
    }
    Event("m10_matrix", m10m);
    // M10 step 3: render-target epochs + occlusion classes. Overlap is
    // against the compared XFB range (mask.xfb). A consuming draw is
    // in-range iff an overlapping copy triggers at/after it with no
    // clear-copy between (the copy path copies first, then clears the
    // source rect — BPStructs.cpp "Clear the rectangular region after
    // copying it" — so a draining copy's own clear bit does not
    // disqualify it, while an intervening clear-copy wipes the draw's
    // pixels from EFB); culled iff cull-all, scissor-empty, or
    // depth-test-on with func Never. Buckets are disjoint by priority
    // culled > out-of-range > in-range.
    const size_t m10_ncopy = m10stream.copies.size();
    std::vector<u32> m10_ovl(m10_ncopy, 0);
    for (size_t i = 0; i < m10_ncopy; ++i) {
      const M10CopyRec& cp = m10stream.copies[i];
      const u32 clo = cp.dest, chi = cp.dest + cp.bytes;
      const u32 xlo = mask.xfb.addr, xhi = mask.xfb.addr + mask.xfb.bytes;
      if (mask.xfb.found && mask.xfb.bytes > 0 && cp.bytes > 0 && clo < xhi &&
          xlo < chi)
        m10_ovl[i] = 1;
    }
    u32 m10_culled = 0, m10_outrange = 0, m10_inrange = 0;
    u32 m10_cull_all = 0, m10_scis = 0, m10_znever = 0;
    u32 m10_all_cull = 0, m10_all_scis = 0, m10_all_znever = 0;
    for (size_t d = 0; d < m10_ndraw; ++d) {
      const M10DrawRec& dr = m10stream.drawrec[d];
      const bool culled = dr.cull == 3 || dr.scis_empty != 0 ||
                          (dr.ztest != 0 && dr.zfunc == 0);
      if (dr.cull == 3) ++m10_all_cull;
      if (dr.scis_empty) ++m10_all_scis;
      if (dr.ztest && dr.zfunc == 0) ++m10_all_znever;
      if (dr.cons_pos == 0 && dr.cons_texmask == 0) continue;
      if (dr.cull == 3) ++m10_cull_all;
      if (dr.scis_empty) ++m10_scis;
      if (dr.ztest && dr.zfunc == 0) ++m10_znever;
      if (culled) {
        ++m10_culled;
        continue;
      }
      bool ir = false;
      for (size_t i = 0; i < m10_ncopy; ++i) {
        const M10CopyRec& cp = m10stream.copies[i];
        if (cp.draw < u32(d) + 1) continue;
        if (!m10_ovl[i]) continue;
        bool barrier = false;
        for (size_t j = 0; j < m10_ncopy; ++j) {
          const M10CopyRec& cj = m10stream.copies[j];
          if (cj.clear && cj.draw >= u32(d) + 1 && cj.draw < cp.draw) {
            barrier = true;
            break;
          }
        }
        if (!barrier) {
          ir = true;
          break;
        }
      }
      if (ir)
        ++m10_inrange;
      else
        ++m10_outrange;
    }
    // Consuming draws per render-target epoch (epoch e = draws strictly
    // after copy e-1 up to and including copy e's clock; tail past last).
    std::vector<u32> m10_epoch_cons(m10_ncopy + 1, 0);
    for (size_t d = 0; d < m10_ndraw; ++d) {
      const M10DrawRec& dr = m10stream.drawrec[d];
      if (dr.cons_pos == 0 && dr.cons_texmask == 0) continue;
      size_t e = 0;
      while (e < m10_ncopy && m10stream.copies[e].draw < u32(d) + 1) ++e;
      ++m10_epoch_cons[e];
    }
    char m10cp[1024];
    int m10cpoff = std::snprintf(m10cp, sizeof(m10cp), "n=%zu xfb=0x%08x/%u ",
                                 m10_ncopy, mask.xfb.addr, mask.xfb.bytes);
    for (size_t i = 0; i < m10_ncopy; ++i) {
      const M10CopyRec& cp = m10stream.copies[i];
      if (m10cpoff < 0 || size_t(m10cpoff) >= sizeof(m10cp) - 128) break;
      m10cpoff += std::snprintf(
          m10cp + m10cpoff, sizeof(m10cp) - size_t(m10cpoff),
          "%sdraw=%u,dest=0x%08x,bytes=%u,xfb=%u,clear=%u,tl=0x%06x,w=%u,h=%u,ovl=%u",
          i ? ";" : "", cp.draw, cp.dest, cp.bytes, cp.is_xfb, cp.clear, cp.tl, cp.w,
          cp.h, m10_ovl[i]);
    }
    Event("m10_copy", m10cp);
    char m10oc[1024];
    int m10ocoff = std::snprintf(
        m10oc, sizeof(m10oc),
        "cons=%u culled=%u outrange=%u inrange=%u cull_all=%u scis_empty=%u "
        "znever=%u all_cull=%u all_scis=%u all_znever=%u all_draws=%zu ncopy=%zu "
        "epoch_cons=",
        m10_cons_any, m10_culled, m10_outrange, m10_inrange, m10_cull_all,
        m10_scis, m10_znever, m10_all_cull, m10_all_scis, m10_all_znever,
        m10_ndraw, m10_ncopy);
    for (size_t e = 0; e < m10_ncopy + 1; ++e) {
      if (m10ocoff < 0 || size_t(m10ocoff) >= sizeof(m10oc) - 24) break;
      m10ocoff += std::snprintf(m10oc + m10ocoff, sizeof(m10oc) - size_t(m10ocoff),
                                "%s%u", e ? "," : "", m10_epoch_cons[e]);
    }
    Event("m10_occ", m10oc);
    char m10n[128];
    std::snprintf(m10n, sizeof(m10n), "nop=%d ok=%d draws=%u bytes=%u",
                  m10_nopcons, int(m10_nop_ok), m10_nop_draws, m10_nop_bytes);
    Event("m10_nop", m10n);
    char m10r[192];
    std::snprintf(m10r, sizeof(m10r),
                  "ram=%d skipx_pre=%d skipe_pre=%d defer_pre=%d skipx_post=%d "
                  "skipe_post=%d defer_post=%d",
                  m10_ramcopy, int(m10_skipx_pre), int(m10_skipe_pre),
                  int(m10_defer_pre), int(m10_skipx_post), int(m10_skipe_post),
                  int(m10_defer_post));
    Event("m10_ram", m10r);
    char m10f[512];
    int m10foff = std::snprintf(
        m10f, sizeof(m10f),
        "ref=%d kref=%u refok=%d n2=%u gt0=%u uniform2=%u xd2min=%u xd2max=%u "
        "xdmax2max=%d xdmean2min=%.3f xdmean2max=%.3f refhash=%016llx samp=",
        m10_ramref, kTransformFrom, int(m10_ref2_ok), m10_n2, m10_gt0,
        m10_uniform2, m10_xd2_min, m10_xd2_max, m10_xdmax2_max,
        m10_xdmean2_min, m10_xdmean2_max,
        static_cast<unsigned long long>(m10_ref2_hash));
    for (unsigned s = 0; s < m10_samp_n; ++s) {
      if (m10foff < 0 || size_t(m10foff) >= sizeof(m10f) - 48) break;
      m10foff += std::snprintf(m10f + m10foff, sizeof(m10f) - size_t(m10foff),
                               "%sr%u:%u/%d/%.3f", s ? "," : "", m10_samp_r[s],
                               m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
    }
    Event("m10_ref2", m10f);
  }
  XFReplay::g_transform = saved_transform;
  g_ActiveConfig.bImmediateXFB = true;
  if (m10_ramcopy) {
    g_ActiveConfig.bSkipXFBCopyToRam = m10_skipx_pre;
    g_ActiveConfig.bSkipEFBCopyToRam = m10_skipe_pre;
    g_ActiveConfig.bDeferEFBCopies = m10_defer_pre;
  }
  RestoreLive(live);
  if (ram_size) std::memcpy(live_memory.GetRAM(), saved_ram.data(), ram_size);
  if (exram_size) std::memcpy(live_memory.GetEXRAM(), saved_exram.data(), exram_size);
  gpfifo.ResetGatherPipe(); // discard bulk residue, restore pre-bulk residual.
  {
    u8* rptr = pipe_snap.data();
    PointerWrap r(&rptr, pipe_used, PointerWrap::Mode::Read);
    gpfifo.DoState(r);
  }
  system.GetFifo().RestoreState(true);
  if (forced_determinism) system.GetFifo().UpdateWantDeterminism(Core::WantsDeterminism());
  const bool window_ok =
      RamHash(live_memory.GetRAM(), ram_size) == RamHash(saved_ram.data(), ram_size) &&
      (exram_size == 0 ||
       RamHash(live_memory.GetEXRAM(), exram_size) == RamHash(saved_exram.data(), exram_size));
  // M5 step 4: live_xfb_untouched = every sampled live XFB matched the first
  // sample of the sequence (and every replay produced a sample).
  const int live_xfb_untouched =
      (xfb_scratch_ok && replays > 0 && live_ok_count == replays &&
       live_same_count == replays)
          ? 1
          : 0;
  char done_detail[288]; // whole-200 wall time + M5 XFB counts on the done event.
  std::snprintf(done_detail, sizeof(done_detail),
                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u "
                "xfb_equal_scratch=%u/200 live_xfb_untouched=%d live_same=%u/%u",
                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, mask.xfb.addr,
                mask.xfb.bytes, xfb_scratch_count, live_xfb_untouched, live_same_count,
                replays);
  Event(window_ok ? "done" : "watched_window_changed", done_detail);
  // M5 step 5: arm the first-live-XFB-after-resume capture. The existing
  // watched-window re-hash + done above remain the receipt.
  ArmResumeXfbCapture(system, 0);
  phase = Phase::Done;
}
} // namespace NativeReplay
