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
struct MaskStats {
  u32 consumed = 0;
  u32 masked = 0;
  u32 display_lists = 0;
  u32 indexed = 0;
  u32 indexed_bytes = 0;  // aux-buffer payload popped per replay (the 2 MiB budget)
  u32 dl_bytes = 0;
  u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
  u32 unknown = 0;
};
class PeMaskWalk final : public OpcodeDecoder::Callback {
public:
  PeMaskWalk(u8* base, const u32* cp_mem, MaskStats& stats)
      : m_base(base), m_cp(cp_mem), m_stats(stats) {}
  void OnXF(u16, u8, const u8*) override {}
  void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
  void OnBP(u8 command, u32) override { m_bp_reg = int(command); }
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
    }
  }
  CPState& GetCPState() override { return m_cp; }

private:
  u8* m_base;
  CPState m_cp;
  MaskStats& m_stats;
  int m_bp_reg = -1;
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
    Event("record_start");
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

  const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
  const std::vector<u8> prelude = Prelude(file);
  ApplyMemory(system, file);
  Run(prelude);
  CopyPreprocessCPStateFromMain();
  VertexLoaderManager::MarkAllDirty();
  {
    char detail[256];
    std::snprintf(detail, sizeof(detail),
                  "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u",
                  int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                  mask.display_lists, mask.dl_bytes, mask.indexed,
                  mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                  mask.unknown, mask.benign_unknown);
    Event("restored", detail);
  }
  auto* const saved_transform = XFReplay::g_transform;
  g_ActiveConfig.bImmediateXFB = false;
  const double seq_start = Now();
  for (replays = 0; replays < kReplays; ++replays) {
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
    if (deterministic) RunPre(frame_pre);
    const double t_pre = Now();
    Run(frame);
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
    std::fprintf(Output(),
                 "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                 "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                 "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                 "\"sync_ms\":%.3f,\"xform\":%d,\"render_execution\":true}\n",
                 wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                 (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                 (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom));
    std::fflush(Output()); // every row survives a post-loop death.
  }
  const double seq_end = Now();
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
  char done_detail[64]; // whole-200 wall time on the done event.
  std::snprintf(done_detail, sizeof(done_detail), "seq_wall_ms=%.3f",
                (seq_end - seq_start) * 1000.0);
  Event(window_ok ? "done" : "watched_window_changed", done_detail);
  phase = Phase::Done;
}
} // namespace NativeReplay
