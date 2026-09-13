// Host replay correctness prerequisite. Capture one original frame, then
// decode its FIFO against private memory and register state. RunFifo<false>
// is intentionally unavailable here: it mutates live PE/timing/RAM/GPU state.
// No replay rendering or camera transform is enabled by this diagnostic.
#pragma once
#include "replay_plan.h"
#include "Core/FifoPlayer/FifoDataFile.h"
#include "Core/FifoPlayer/FifoRecorder.h"
#include "VideoCommon/OpcodeDecoding.h"
#include "VideoCommon/XFMemory.h"
#include "VideoCommon/BPMemory.h"
#include "VideoCommon/CPMemory.h"
#include "VideoCommon/TextureDecoder.h"
#include "VideoCommon/VideoEvents.h"
#include "VideoCommon/VideoConfig.h"
#include <array>
#include <cstring>
#include <vector>

namespace NativeReplay {
using namespace NativeProbe;
enum class Phase { Idle, Recording, Done };
static Phase phase = Phase::Idle;
static double record_wall = 0;
static unsigned frame_boundaries = 0;
static bool reference_requested = false;
static u64 reference_frame = 0, reference_present = 0;
static Common::EventHook frame_hook, present_hook;
static bool Enabled() {
  static const bool on = [] {
    const char* value = std::getenv("SSX_NATIVE_REPLAY");
    return value && std::strcmp(value, "1") == 0;
  }();
  return on;
}
static void Event(const char* action, const char* reason = "") {
  std::fprintf(Output(), "{\"event\":\"replay\",\"schema\":2,\"action\":\"%s\","
      "\"wall\":%.6f,\"reason\":\"%s\",\"frame_boundaries\":%u,"
      "\"reference_frame\":%llu,\"reference_present\":%llu,\"render_execution\":false}\n",
      action, Now(), reason, frame_boundaries, (unsigned long long)reference_frame,
      (unsigned long long)reference_present);
  std::fflush(Output());
}

// The template decoder only computes command lengths and calls these methods.
// These callbacks never call Dolphin's hardware/video execution callbacks.
class Audit final : public OpcodeDecoder::Callback {
public:
  Audit(FifoDataFile& file, ReplayResearch::ShadowMemory& shadow)
      : cp(file.GetCPMem()), memory(shadow), address_mask(file.GetIsWii() ? 0x1fffffffu : 0x03ffffffu) {
    std::copy_n(file.GetBPMem(), bp.size(), bp.begin());
    std::copy_n(file.GetCPMem(), cp_words.size(), cp_words.begin());
    std::copy_n(file.GetXFMem(), FifoDataFile::XF_MEM_SIZE, xf.begin());
    std::copy_n(file.GetXFRegs(), FifoDataFile::XF_REGS_SIZE,
                xf.begin() + FifoDataFile::XF_MEM_SIZE);
    tmem.assign(file.GetTexMem(), file.GetTexMem() + FifoDataFile::TEX_MEM_SIZE);
  }
  void OnXF(u16 address, u8 count, const u8* data) override {
    if (size_t(address) + count > xf.size()) { valid = false; return; }
    for (unsigned i = 0; i < count; ++i) xf[address + i] = Common::swap32(data + 4 * i);
    ++xf_loads;
  }
  void OnCP(u8 command, u32 value) override {
    // CPState::LoadCPReg also reports analytics quirks for unsupported/aliased
    // registers. Accept only canonical state writes and construct local state.
    if (command == 0x20 && value == 0) return;
    const auto range = [&](u32 begin, u32 count) { return command >= begin && command < begin + count; };
    if (command != MATINDEX_A && command != MATINDEX_B && command != VCD_LO && command != VCD_HI &&
        !range(CP_VAT_REG_A, CP_NUM_VAT_REG) && !range(CP_VAT_REG_B, CP_NUM_VAT_REG) &&
        !range(CP_VAT_REG_C, CP_NUM_VAT_REG) && !range(ARRAY_BASE, CP_NUM_ARRAYS) &&
        !range(ARRAY_STRIDE, CP_NUM_ARRAYS)) { valid = false; return; }
    cp_words[command] = range(ARRAY_BASE, CP_NUM_ARRAYS) ? value & address_mask :
        range(ARRAY_STRIDE, CP_NUM_ARRAYS) ? value & 0xff : value;
    const CPState fresh(cp_words.data());
    static_assert(std::is_trivially_copyable_v<CPState>);
    std::memcpy(&cp, &fresh, sizeof(cp));
  }
  void OnBP(u8 command, u32 value) override {
    const u32 mask = bp[BPMEM_BP_MASK];
    bp[command] = (bp[command] & ~mask) | (value & mask);
    if (command != BPMEM_BP_MASK) bp[BPMEM_BP_MASK] = 0xffffff;
    switch (command) {
    case BPMEM_SETDRAWDONE: ++draw_done; break;
    case BPMEM_PE_TOKEN_ID: case BPMEM_PE_TOKEN_INT_ID: ++tokens; break;
    case BPMEM_TRIGGER_EFB_COPY:
      ++efb_copies;
      if (bp[command] & (1u << 14)) ++xfb_copies;
      break;
    case BPMEM_LOADTLUT1: case BPMEM_PRELOAD_MODE: ++tmem_loads; break;
    case BPMEM_CLEARBBOX1: case BPMEM_CLEARBBOX2: ++bbox_writes; break;
    default: break;
    }
  }
  void OnIndexedLoad(CPArray array, u32 index, u16 address, u8 size) override {
    // Match the pinned decoder's u32 address arithmetic, then reject any
    // resulting range outside the private bank before reading it.
    const u32 source = cp.array_bases[array] + cp.array_strides[array] * index;
    const u8* data = memory.Resolve(source, size_t(size) * sizeof(u32));
    if (!data) { valid = false; return; }
    OnXF(address, size, data);
    indexed_bytes_hash ^= Hash(data, size_t(size) * sizeof(u32));
    indexed_bytes_hash *= 1099511628211ull;
    ++indexed_loads;
  }
  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8, u32, u16, const u8*) override {
    ++primitives;
  }
  void OnDisplayList(u32, u32) override {
    // FifoRecorder inlines display lists. Never fall back to live guest RAM.
    valid = false;
  }
  void OnNop(u32) override {}
  void OnUnknown(u8 opcode, const u8*) override {
    if (opcode != u8(OpcodeDecoder::Opcode::GX_CMD_INVL_VC) &&
        opcode != u8(OpcodeDecoder::Opcode::GX_CMD_UNKNOWN_METRICS)) valid = false;
  }
  void OnCommand(const u8*, u32) override { ++commands; }
  CPState& GetCPState() override { return cp; }
  bool Decode(const std::vector<u8>& fifo, size_t start, size_t end) {
    while (start < end && valid) {
      // RunCommand asserts on malformed XF headers. Reject those before the
      // pinned decoder sees them, rather than crashing an audit process.
      if (fifo[start] == u8(OpcodeDecoder::Opcode::GX_LOAD_XF_REG) && end - start >= 5 &&
          (Common::swap32(fifo.data() + start + 1) >> 16) >= 16) return false;
      const u32 size = OpcodeDecoder::RunCommand(fifo.data() + start, u32(end - start), *this);
      if (!size) return false;
      start += size;
    }
    return valid && start == end;
  }
  CPState cp;
  ReplayResearch::ShadowMemory& memory;
  const u32 address_mask;
  std::array<u32, FifoDataFile::BP_MEM_SIZE> bp{};
  std::array<u32, FifoDataFile::CP_MEM_SIZE> cp_words{};
  std::array<u32, FifoDataFile::XF_MEM_SIZE + FifoDataFile::XF_REGS_SIZE> xf{};
  std::vector<u8> tmem;
  u64 indexed_bytes_hash = 14695981039346656037ull;
  unsigned commands = 0, primitives = 0, xf_loads = 0, indexed_loads = 0;
  unsigned draw_done = 0, tokens = 0, efb_copies = 0, xfb_copies = 0, tmem_loads = 0, bbox_writes = 0;
  bool valid = true;
};

static void Analyze(FifoDataFile& file, Core::System& system) {
  const auto& frame = file.GetFrame(0);
  auto& live_memory = system.GetMemory();
  // GameCube still reports the configured MEM2 size, but has no allocated
  // EXRAM. Use allocation presence for audit banks and whole-bank checks.
  const size_t ram_size = ReplayResearch::AllocatedBankSize(live_memory.GetRAM(), live_memory.GetRamSize());
  const size_t exram_size = ReplayResearch::AllocatedBankSize(live_memory.GetEXRAM(), live_memory.GetExRamSize());
  std::vector<ReplayResearch::MemoryUpdate> updates;
  for (const auto& update : frame.memoryUpdates)
    updates.push_back({update.fifoPosition, update.address, update.data});
  // Zero matches the recorder's initial shadow memory, not a claim that EFB
  // copy destinations can be reproduced without executing the missing copies.
  ReplayResearch::ShadowMemory memory(ram_size, live_memory.GetRamMask(),
                                      exram_size, live_memory.GetExRamMask());
  const auto before_ram = Hash(live_memory.GetRAM(), ram_size);
  const auto before_exram = Hash(live_memory.GetEXRAM(), exram_size);
  for (unsigned pass = 0; pass < 3; ++pass) {
    memory.Reset();
    Audit audit(file, memory); // Fresh CP/BP/XF/TMEM before every audit pass.
    std::string error;
    const bool ok = ReplayResearch::DecodeOrdered(frame.fifoData.size(), updates, memory,
        [&](size_t start, size_t end) { return audit.Decode(frame.fifoData, start, end); }, error);
    std::fprintf(Output(), "{\"event\":\"replay\",\"schema\":2,\"action\":\"audit\","
        "\"wall\":%.6f,\"pass\":%u,\"ok\":%s,\"reason\":\"%s\",\"commands\":%u,"
        "\"primitives\":%u,\"indexed_loads\":%u,\"indexed_bytes_hash\":\"%016llx\","
        "\"draw_done\":%u,\"tokens\":%u,\"efb_copies\":%u,\"xfb_copies\":%u,"
        "\"tmem_loads\":%u,\"bbox_writes\":%u,\"initial_state_reset\":true,"
        "\"private_memory\":true,\"render_execution\":false}\n",
        Now(), pass, ok ? "true" : "false", error.c_str(), audit.commands, audit.primitives,
        audit.indexed_loads, (unsigned long long)audit.indexed_bytes_hash, audit.draw_done,
        audit.tokens, audit.efb_copies, audit.xfb_copies, audit.tmem_loads, audit.bbox_writes);
    if (!ok) { std::fflush(Output()); return; }
  }
  const bool ram_equal = before_ram == Hash(live_memory.GetRAM(), ram_size) &&
      before_exram == Hash(live_memory.GetEXRAM(), exram_size);
  Event(ram_equal ? "audit_complete" : "audit_failed", ram_equal ? "" : "live_ram_changed");
  // Even a successful audit does not execute vertices/textures/EFB copies and
  // cannot establish original-frame pixel equivalence or GPU state isolation.
}

static inline void Step(CPUState& c) {
  RefreshNow(c);
  if (!Enabled() || !Output() || phase == Phase::Done) return;
  if (c.pc != 0x801cad24 || c.lr != 0x801cd724) return;
  auto& system = Core::System::GetInstance();
  auto& recorder = system.GetFifoRecorder();
  if (phase == Phase::Idle) {
    if (!ExperimentalWindow()) return;
    // These restrictions make capture identity and the read-only audit's
    // thread ownership explicit. No scheduler or guest-render injection runs.
    if (system.IsDualCoreMode() || !g_ActiveConfig.bImmediateXFB || recorder.IsRecording() ||
        NativeSchedule::ScheduleEnabled() || DoubleEnabled() || WaitEnabled() || SweepEnabled()) {
      Event("blocked", "requires_single_core_immediate_xfb_without_other_experiments");
      phase = Phase::Done;
      return;
    }
    recorder.StartRecording(1, [] {});
    record_wall = Now();
    phase = Phase::Recording;
    // The first boundary arms recording, and the second ends the recorded
    // frame. Register after the recorder so IsRecording() is already updated.
    frame_hook = system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
      if (phase == Phase::Recording) ++frame_boundaries;
    });
    present_hook = system.GetVideoEvents().before_present_event.Register([](PresentInfo& info) {
      if (phase != Phase::Recording || reference_requested || frame_boundaries != 2 ||
          info.reason != PresentInfo::PresentReason::Immediate ||
          Core::System::GetInstance().GetFifoRecorder().IsRecording()) return;
      reference_frame = info.frame_count;
      reference_present = info.present_count;
      Core::SaveScreenShot("native-replay-reference");
      reference_requested = true;
      Event("reference_requested");
    });
    Event("record_start");
    return;
  }
  FifoDataFile* file = recorder.GetRecordedFile();
  if (!recorder.IsRecording() && file && file->GetFrameCount() == 1) {
    frame_hook.reset();
    present_hook.reset();
    const auto& frame = file->GetFrame(0);
    std::fprintf(Output(), "{\"event\":\"replay\",\"schema\":2,\"action\":\"recorded\","
        "\"wall\":%.6f,\"bytes\":%zu,\"memory_updates\":%zu,\"fifo_start\":%u,"
        "\"fifo_end\":%u,\"frame_boundaries\":%u,\"reference_frame\":%llu,"
        "\"reference_present\":%llu,\"render_execution\":false}\n", Now(), frame.fifoData.size(),
        frame.memoryUpdates.size(), frame.fifoStart, frame.fifoEnd, frame_boundaries,
        (unsigned long long)reference_frame, (unsigned long long)reference_present);
    const char* trace_path = std::getenv("SSX_NATIVE_PROBE");
    const std::string capture_path = std::string(trace_path) + ".fifo";
    FILE* reservation = std::fopen(capture_path.c_str(), "wx");
    if (reservation) std::fclose(reservation);
    const bool saved = reservation && file->Save(capture_path);
    if (saved) Event("capture_saved");
    if (!saved || !reference_requested || frame_boundaries != 2) {
      Event("blocked", saved ? "missing_same_frame_reference" : "capture_save_failed");
    } else {
      Analyze(*file, system);
      Event("blocked", "renderer_isolation_and_pixel_fidelity_unimplemented");
    }
    phase = Phase::Done;
  } else if (Now() - record_wall > 2.0) {
    recorder.StopRecording();
    frame_hook.reset();
    present_hook.reset();
    Event("blocked", "record_timeout");
    phase = Phase::Done;
  }
}
} // namespace NativeReplay
