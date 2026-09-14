// Research-only GPU-thread capture. No CPU camera side channel or presentation changes.
#pragma once
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>
#include "Core/System.h"
#include "VideoCommon/AbstractGfx.h"
#include "VideoCommon/AbstractTexture.h"
#include "VideoCommon/AbstractStagingTexture.h"
#include "VideoCommon/FramebufferManager.h"
#include "VideoCommon/VertexShaderManager.h"
#include "VideoCommon/VideoCommon.h"
#include "VideoCommon/VideoConfig.h"
#include "VideoCommon/XFMemory.h"
#include "VideoCommon/CPMemory.h"
#include "VideoCommon/BPMemory.h"

namespace ReprojectionCapture {
// All hooks execute on the video decoder thread, including indexed matrix loads.
inline unsigned frame = 0, captured = 0, draws = 0, perspective = 0, ortho = 0;
inline unsigned late_perspective = 0, camera_loads = 0;
inline bool active = false, split = false, camera_valid = false;
inline std::array<float,12> camera{};
inline std::array<float,16> projection{};
inline std::array<float,6> viewport{};
inline std::array<float,4> correction{};
inline unsigned camera_base = 0;
inline std::array<float,2> scissor_offset{};
inline bool vertex_depth_range=false;
inline std::string prefix;
inline FILE* metadata = nullptr;
inline const auto start = std::chrono::steady_clock::now();
inline double Now() { return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count(); }
inline const char* Directory() { static const char* p = std::getenv("SSX_REPROJECTION_CAPTURE"); return p; }
// Host wall time differs between two runs of the same movie, so a paired
// capture must arm on the guest's own XFB frame counter instead.
inline bool Armed() {
  if (!Directory() || captured >= 8) return false;
  if (const char* from = std::getenv("SSX_REPROJECTION_FROM_FRAME")) return frame >= std::strtoul(from,nullptr,0);
  const char* begin = std::getenv("SSX_REPROJECTION_AFTER");
  return Now() >= (begin ? std::atof(begin) : 140.0);
}
// A known constant background under the HUD tail. Two runs of one movie over
// two such backgrounds determine the tail's alpha exactly; one run cannot.
inline bool HudClear(u32* color) {
  const char* value = std::getenv("SSX_REPROJECTION_HUD_CLEAR");
  if (!value) return false;
  *color = 0xff000000u | (u32(std::strtoul(value,nullptr,16)) & 0xffffffu);
  return true;
}
inline void Floats(FILE* f, const float* data, size_t count) {
  std::fputc('[',f);
  for (size_t i=0;i<count;++i) std::fprintf(f,"%s%.9g",i?",":"",data[i]);
  std::fputc(']',f);
}
inline void Indexed(CPArray array, u32 index, u16 address, u8 size) {
  // Game's graphics palette slot zero is its view matrix. Capture what the GPU
  // actually consumed, not RAM that the CPU may already have updated again.
  if (array != CPArray::XF_A || index != 0 || size != 12 || address + 12 > 256 ||
      g_main_cp_state.array_strides[array] != 48) return;
  std::copy_n(xfmem.posMatrices + address,12,camera.begin());
  camera_base=g_main_cp_state.array_bases[array];
  camera_valid=true;
  ++camera_loads;
}
inline bool Save(bool depth, const std::string& suffix) {
  auto* texture = depth ? g_framebuffer_manager->ResolveEFBDepthTexture(
      g_framebuffer_manager->GetEFBDepthTexture()->GetRect(),true) :
      g_framebuffer_manager->ResolveEFBColorTexture(
      g_framebuffer_manager->GetEFBColorTexture()->GetRect());
  auto config=texture->GetConfig();
  config.layers=1; config.levels=1; config.samples=1; config.flags=0;
  if (depth && config.format==AbstractTextureFormat::D32F) config.format=AbstractTextureFormat::R32F;
  if ((depth && config.format!=AbstractTextureFormat::R32F) ||
      (!depth && config.format!=AbstractTextureFormat::RGBA8 && config.format!=AbstractTextureFormat::BGRA8)) return false;
  auto staging=g_gfx->CreateStagingTexture(StagingTextureType::Readback,config);
  if (!staging) return false;
  staging->CopyFromTexture(texture,0,0);
  staging->Flush();
  if (!staging->Map()) return false;
  FILE* file=std::fopen((prefix+suffix).c_str(),"wx");
  if (!file) { staging->Unmap(); return false; }
  for (unsigned y=0;y<config.height;++y)
    std::fwrite(staging->GetMappedPointer()+y*staging->GetMappedStride(),4,config.width,file);
  std::fclose(file); staging->Unmap();
  std::fprintf(metadata,"{\"event\":\"image\",\"file\":\"%s\",\"width\":%u,\"height\":%u,\"format\":%u}\n",
      std::filesystem::path(prefix+suffix).filename().c_str(),config.width,config.height,unsigned(config.format));
  return true;
}
inline void Draw() {
  if (!Directory()) return;
  if (!draws && Armed()) {
    active=true;
    std::filesystem::create_directories(Directory());
    prefix=std::string(Directory())+"/frame-"+std::to_string(frame);
    metadata=std::fopen((prefix+".jsonl").c_str(),"wx");
    if (!metadata) active=false;
  }
  ++draws;
  const bool persp=xfmem.projection.type==ProjectionType::Perspective;
  if (persp) ++perspective; else ++ortho;
  if (!active) return;
  if (persp && split) ++late_perspective;
  if (!persp && perspective && !split) {
    split=true;
    // Before this draw has uploaded vertices or changed GPU pipeline bindings.
    const bool color_ok=Save(false,"-world.rgba");
    const bool depth_ok=Save(true,"-depth.f32");
    std::fprintf(metadata,"{\"event\":\"split\",\"draw\":%u,\"color_ok\":%s,\"depth_ok\":%s,\"camera_valid\":%s,\"camera_base\":%u,\"view\":",
      draws,color_ok?"true":"false",depth_ok?"true":"false",camera_valid?"true":"false",camera_base);
    Floats(metadata,camera.data(),12);
    std::fputs(",\"projection\":",metadata);Floats(metadata,projection.data(),16);
    std::fputs(",\"viewport\":",metadata);Floats(metadata,viewport.data(),6);
    std::fputs(",\"scissor_offset\":",metadata);Floats(metadata,scissor_offset.data(),2);
    std::fprintf(metadata,",\"vertex_depth_range\":%s",vertex_depth_range?"true":"false");
    std::fputs(",\"pixel_center_correction\":",metadata);Floats(metadata,correction.data(),4);
    std::fprintf(metadata,",\"reversed_depth\":%s",g_backend_info.bSupportsReversedDepthRange?"true":"false");
    const PixelFormat format=bpmem.zcontrol.pixel_format;
    std::fprintf(metadata,",\"efb_pixel_format\":%u",unsigned(format));
    u32 clear=0;
    if (HudClear(&clear)) {
      // Colour and alpha only: the tail still depth-tests against real scenery.
      g_framebuffer_manager->ClearEFB(MathUtil::Rectangle<int>(0,0,int(EFB_WIDTH),int(EFB_HEIGHT)),
          true,true,false,clear,0,format);
      std::fprintf(metadata,",\"hud_clear\":%u}\n",clear&0xffffffu);
    } else {
      std::fputs(",\"hud_clear\":null}\n",metadata);
    }
  }
  if (persp && !split) {
    auto& constants=Core::System::GetInstance().GetVertexShaderManager().constants;
    std::memcpy(projection.data(),constants.projection.data(),16*sizeof(float));
    std::memcpy(viewport.data(),&xfmem.viewport,6*sizeof(float));
    scissor_offset={float(bpmem.scissorOffset.x*2),float(bpmem.scissorOffset.y*2)};
    vertex_depth_range=VertexShaderManager::UseVertexDepthRange();
    std::memcpy(correction.data(),constants.pixelcentercorrection.data(),4*sizeof(float));
  }
  std::fprintf(metadata,"{\"event\":\"draw\",\"id\":%u,\"perspective\":%s,\"camera_loads\":%u,\"z_write\":%s}\n",
      draws,persp?"true":"false",camera_loads,bpmem.zmode.update_enable?"true":"false");
}
inline void Xfb(u32 address, const MathUtil::Rectangle<int>& rectangle) {
  if (!Directory()) return;
  if (active) {
    u32 ignored=0;
    const bool cleared=HudClear(&ignored);
    // Under a clear this file is the tail over that constant, not the real frame.
    const bool final_ok=Save(false,"-final.rgba");
    std::fprintf(metadata,"{\"event\":\"frame\",\"schema\":1,\"frame_id\":%u,\"wall_seconds\":%.6f,\"xfb_address\":%u,\"xfb_rect\":[%d,%d,%d,%d],\"draws\":%u,\"perspective\":%u,\"ortho\":%u,\"late_perspective\":%u,\"camera_loads\":%u,\"final_ok\":%s,\"hud_cleared\":%s,\"hud_alpha_layer\":false,\"timing_representative\":false}\n",
        frame,Now(),address,rectangle.left,rectangle.top,rectangle.right,rectangle.bottom,
        draws,perspective,ortho,late_perspective,camera_loads,final_ok?"true":"false",
        cleared?"true":"false");
    std::fclose(metadata);metadata=nullptr;++captured;
  }
  ++frame;draws=perspective=ortho=late_perspective=camera_loads=0;
  active=split=camera_valid=false;
}
}
