// Diagnostic-only injection after the VertexManagerBase includes.
// Compiled into isolated players by tools/gamecube_draw_trace.py.
#pragma once

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <unordered_set>

static std::string TraceHex(const void* data, size_t size)
{
  static constexpr char digits[] = "0123456789abcdef";
  const auto* bytes = static_cast<const unsigned char*>(data);
  std::string result(size * 2, '0');
  for (size_t i = 0; i < size; ++i)
  {
    result[2 * i] = digits[bytes[i] >> 4];
    result[2 * i + 1] = digits[bytes[i] & 15];
  }
  return result;
}

static void TraceDraw(const std::string& textures, const u8* vertices, size_t length)
{
  static const char* path = std::getenv("SSX3_DRAW_TRACE");
  if (!path)
    return;
  static const auto start = std::chrono::steady_clock::now();
  static unsigned poll = 0;
  static bool enabled = false;
  if (++poll % 120 == 0)
  {
    std::error_code error;
    enabled = std::filesystem::exists(std::string(path) + ".enable", error);
  }
  if (!enabled)
    return;
  static std::unordered_set<std::string> seen;
  if (seen.size() >= 4096)
    return;
  const unsigned stages = bpmem.genMode.numtevstages.Value() + 1;
  // Sample the first draw of each texture/combiner/order combination. Matrix,
  // vertex and animated uniform changes do not create new samples.
  auto key = textures + TraceHex(&bpmem.genMode, sizeof(bpmem.genMode)) +
             TraceHex(bpmem.combiners, stages * sizeof(TevStageCombiner)) +
             TraceHex(bpmem.tevorders, ((stages + 1) / 2) * sizeof(TwoTevStageOrders));
  if (!seen.insert(key).second)
    return;
  static FILE* file = std::fopen(path, "wx");
  if (!file)
    return;  // Preserve existing captures; choose a fresh path for every run.
  static_assert(sizeof(BPMemory) == 1024);
  const auto& declaration = VertexLoaderManager::GetCurrentVertexFormat()->GetVertexDeclaration();
  const auto& constants = Core::System::GetInstance().GetPixelShaderManager().constants;
  const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::steady_clock::now() - start).count();
  auto line = fmt::format(
      "{{\"schema\":1,\"id\":{},\"elapsed_ms\":{},\"textures\":[{}],\"bp\":\"{}\","
      "\"xf\":\"{}\",\"colors\":\"{}\",\"konst\":\"{}\",\"declaration\":\"{}\","
      "\"vertices\":\"{}\"}}\n",
      seen.size(), elapsed, textures, TraceHex(&bpmem, sizeof(bpmem)),
      TraceHex(&xfmem, sizeof(xfmem)), TraceHex(&constants.colors, sizeof(constants.colors)),
      TraceHex(&constants.kcolors, sizeof(constants.kcolors)),
      TraceHex(&declaration, sizeof(declaration)), TraceHex(vertices, std::min(length, size_t(512))));
  std::fwrite(line.data(), 1, line.size(), file);
  std::fflush(file);
}
