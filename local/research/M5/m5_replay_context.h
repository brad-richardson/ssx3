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
struct SideFx {
  size_t tex_entries = 0;
  size_t pending = 0;
  int frame_count = -1;
  unsigned long long after_frame = 0;
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
    return;
  }
  if (phase == Phase::Recording) {
    FifoDataFile* file = recorder.GetRecordedFile();
    const bool ready = !recorder.IsRecording() && file && file->GetFrameCount() >= 1;
    if (!ready) {
      if (Now() - record_wall > 2.0) {
        Event("record_failed");
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
  const std::vector<u8>& exec_stream = xfb_scratch_ok ? frame_exec : frame;
  const std::vector<u8>& pre_stream = xfb_scratch_ok ? frame_pre_exec : frame_pre;
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
  {
    char detail[448];
    std::snprintf(detail, sizeof(detail),
                  "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                  "efb_total=%u xfb_patch_n=%u",
                  int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                  mask.display_lists, mask.dl_bytes, mask.indexed,
                  mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                  mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                  xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                  xfb_patch_n);
    Event("restored", detail);
  }
  auto* const saved_transform = XFReplay::g_transform;
  g_ActiveConfig.bImmediateXFB = false;
  // M5 step 3: count after_frame_event triggers for the duration of the
  // sequence with the header's own listener. Passive: it only increments.
  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
  s_after_frame_triggers = 0;
  Common::EventHook m5_after_frame_hook =
      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
        ++s_after_frame_triggers;
      });
  const SideFx fx_base = CaptureSideFx(system);
  // Min/max trackers over the per-replay deltas for the summary receipt.
  long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
  long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
  long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
  bool fx_first = true;
  const double seq_start = Now();
  for (replays = 0; replays < kReplays; ++replays) {
    // M5 step 3, fail-closed: the recorder must be idle; a replay that
    // re-arms g_record_fifo_data would corrupt any live capture.
    if (OpcodeDecoder::g_record_fifo_data) {
      char rd[64];
      std::snprintf(rd, sizeof(rd), "replay=%u", replays);
      Event("record_flag_set", rd);
      break;
    }
    const SideFx fx_before = CaptureSideFx(system);
    const double wall_start = Now();
    const double cpu_start = ThreadCpuMs();
    // Restore before EVERY replay: recorded memory updates and TMEM (the
    // replay's own EFB copies write into guest RAM and can land on recorded
    // vertex/palette regions), then the recorded CP registers into both CP
    // states so the execute and preprocess passes start from identical array
    // bases, strides and VATs.
    if (replays == kTransformFrom) XFReplay::g_transform = &NoopTransform;
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
    const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
    const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
    if (fx_first) {
      min_dtex = max_dtex = dtex;
      min_dpend = max_dpend = dpend;
      min_dframe = max_dframe = dframe;
      min_dafter = max_dafter = dafter;
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
      if (pediff < min_pe) min_pe = pediff;
      if (pediff > max_pe) max_pe = pediff;
      if (vidiff < min_vi) min_vi = vidiff;
      if (vidiff > max_vi) max_vi = vidiff;
    }
    std::fprintf(Output(),
                 "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                 "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                 "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                 "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
                 "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                 wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                 (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                 (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
    std::fflush(Output()); // every row survives a post-loop death.
  }
  const double seq_end = Now();
  // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
  // event. completed = capacity rows actually emitted (record_flag_set stops
  // the sequence early, fail-closed).
  {
    char summary[640];
    std::snprintf(summary, sizeof(summary),
                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
                  "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
                  "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
                  "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                  "live_ok=%u live_same=%u",
                  replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
                  live_ok_count, live_same_count);
    Event("counters_summary", summary);
  }
  m5_after_frame_hook.reset();
  XFReplay::g_transform = saved_transform;
  g_ActiveConfig.bImmediateXFB = true;
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
