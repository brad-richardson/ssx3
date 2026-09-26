rows=1569 covered=67.44%
| Stage | Self % |
|---|---|
| Vulkan driver CPU (Turnip) | 41.05% |
| libc/kernel/vdso | 11.29% |
| scheduler/sync/waits | 5.31% |
| VU1 generated pairs | 2.96% |
| profiler unwind overhead | 1.70% |
| __bzero/__memset zeroing | 1.18% |
| VU1 interpreter/other | 0.85% |
| guest code | 0.69% |
| other | 0.45% |
| VU1 issue/hazard | 0.33% |
| paraLLEl CPU submit | 0.32% |
| EE runtime helpers | 0.28% |
| PLT | 0.27% |
| GIF/GS packet handling | 0.26% |
| VIF1/DMA | 0.24% |
| PS2 runtime other | 0.23% |
| SND/audio | 0.03% |

| Self % | Thread | Symbol | Stage |
|---|---|---|---|
| 3.31 | GsWorker | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 1.58 | GsWorker | `scudo::HybridMutex::unlock()` | scheduler/sync/waits |
| 1.17 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::allocate(unsigned long, scudo::Chunk::Origin, unsigned long, bool)` | libc/kernel/vdso |
| 1.14 | GsWorker | `__memset_aarch64_nt` | __bzero/__memset zeroing |
| 1.10 | GsWorker | `libvulkan_freedreno.so[+b40d34]` | Vulkan driver CPU (Turnip) |
| 1.07 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 1.05 | GameThread | `libunwind::findUnwindSectionsByPhdr(dl_phdr_info*, unsigned long, void*)` | profiler unwind overhead |
| 0.97 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.87 | GsWorker | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.65 | GsWorker | `libvulkan_freedreno.so[+b40d68]` | Vulkan driver CPU (Turnip) |
| 0.61 | GsWorker | `malloc` | libc/kernel/vdso |
| 0.49 | GameThread | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.47 | GsWorker | `libvulkan_freedreno.so[+b489b8]` | Vulkan driver CPU (Turnip) |
| 0.47 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.45 | GsWorker | `libvulkan_freedreno.so[+b40d74]` | Vulkan driver CPU (Turnip) |
| 0.44 | GsWorker | `__aarch64_cas4_acq` | libc/kernel/vdso |
| 0.44 | GsWorker | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.41 | GsWorker | `libvulkan_freedreno.so[+b40d3c]` | Vulkan driver CPU (Turnip) |
| 0.40 | com.ps2x.runner | `clock_gettime` | libc/kernel/vdso |
| 0.40 | GsWorker | `libvulkan_freedreno.so[+b40f60]` | Vulkan driver CPU (Turnip) |
| 0.39 | GameThread | `[linker]do_dl_iterate_phdr(int (*)(dl_phdr_info*, unsigned long, void*), void*)` | profiler unwind overhead |
| 0.33 | GsWorker | `[kernel.kallsyms][+ffffffe760d65040]` | libc/kernel/vdso |
| 0.33 | GameThread | `VU1Interpreter::commitReadyPipelines()` | VU1 issue/hazard |
| 0.32 | GsWorker | `libvulkan_freedreno.so[+c1d314]` | Vulkan driver CPU (Turnip) |
| 0.31 | com.ps2x.runner | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.30 | GsWorker | `libvulkan_freedreno.so[+b489ac]` | Vulkan driver CPU (Turnip) |
| 0.29 | GsWorker | `libvulkan_freedreno.so[+b6b8ac]` | Vulkan driver CPU (Turnip) |
| 0.28 | GsWorker | `__aarch64_ldadd4_rel` | libc/kernel/vdso |
| 0.27 | GsWorker | `libvulkan_freedreno.so[+c1d0dc]` | Vulkan driver CPU (Turnip) |
| 0.26 | GsWorker | `libvulkan_freedreno.so[+b40f9c]` | Vulkan driver CPU (Turnip) |
| 0.26 | GameThread | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 0.24 | GsWorker | `libvulkan_freedreno.so[+b6b8d0]` | Vulkan driver CPU (Turnip) |
| 0.24 | GameThread | `PS2Memory::processVIF1DataImpl(unsigned char const*, unsigned int)` | VIF1/DMA |
| 0.23 | GsWorker | `libvulkan_freedreno.so[+c1d11c]` | Vulkan driver CPU (Turnip) |
| 0.23 | GsWorker | `@plt` | PLT |
| 0.23 | GameThread | `VU1Interpreter::execUpper(unsigned int)` | VU1 interpreter/other |
| 0.22 | GsWorker | `libvulkan_freedreno.so[+b48538]` | Vulkan driver CPU (Turnip) |
| 0.22 | GsWorker | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.21 | GsWorker | `libvulkan_freedreno.so[+c1cf58]` | Vulkan driver CPU (Turnip) |
| 0.20 | GsWorker | `scudo_malloc` | libc/kernel/vdso |
| 0.20 | GsWorker | `libvulkan_freedreno.so[+c1d100]` | Vulkan driver CPU (Turnip) |
| 0.18 | GsWorker | `libvulkan_freedreno.so[+b419a8]` | Vulkan driver CPU (Turnip) |
| 0.17 | GsWorker | `libvulkan_freedreno.so[+c656ac]` | Vulkan driver CPU (Turnip) |
| 0.17 | GsWorker | `libvulkan_freedreno.so[+b482dc]` | Vulkan driver CPU (Turnip) |
| 0.17 | GsWorker | `[kernel.kallsyms][+ffffffe760d8565c]` | libc/kernel/vdso |
| 0.17 | GameThread | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.16 | GsWorker | `void scudo::releaseFreeMemoryToOS<scudo::RegionReleaseRecorder<scudo::MemMapLinux>, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::releaseToOSMaybe(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, scudo::ReleaseToOS)::'lambda'(unsigned long)>(scudo::PageReleaseContext&, scudo::RegionReleaseRecorder<scudo::MemMapLinux>&, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::releaseToOSMaybe(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, scudo::ReleaseToOS)::'lambda'(unsigned long))` | libc/kernel/vdso |
| 0.16 | GsWorker | `libvulkan_freedreno.so[+c658b8]` | Vulkan driver CPU (Turnip) |
| 0.16 | GsWorker | `libvulkan_freedreno.so[+b6d648]` | Vulkan driver CPU (Turnip) |
| 0.16 | GsWorker | `libvulkan_freedreno.so[+b48510]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+c1c670]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+b6b86c]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `free` | libc/kernel/vdso |
| 0.15 | GameThread | `sub_00376938_0x376938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.15 | GameThread | `VU1Interpreter::progressXgkick()` | VU1 interpreter/other |
| 0.14 | GsWorker | `scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::drain(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::PerClass*, unsigned long)` | libc/kernel/vdso |
| 0.14 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocks(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, unsigned int*, unsigned int)` | libc/kernel/vdso |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+c658a4]` | Vulkan driver CPU (Turnip) |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+b6d64c]` | Vulkan driver CPU (Turnip) |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+b482c8]` | Vulkan driver CPU (Turnip) |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+aa12b8]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+c65898]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+c1d000]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+c1cf48]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+c1c68c]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+b41974]` | Vulkan driver CPU (Turnip) |
| 0.13 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `PS2Memory::advanceEeTimers(unsigned long)` | EE runtime helpers |
| 0.12 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned int, bool)` | libc/kernel/vdso |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c65b38]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c65348]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+b6bfb4]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+b6bfa4]` | Vulkan driver CPU (Turnip) |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `EeScheduler::accountCycles(unsigned int)` | scheduler/sync/waits |
| 0.11 | com.ps2x.runner | `!!!0000!a0d82c13dd4b4e4f31b6cd30a2cb0d!a9ee82cd83!` | other |
| 0.11 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<false, false, false, 3u>()` | paraLLEl CPU submit |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+c65b80]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+c657a0]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+c3f644]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+b6b87c]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+b40be8]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+ae57b4]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+aa0e38]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c65b8c]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c65a7c]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c631e8]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c1d4d0]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c19210]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+b6c370]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+b6b968]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+b40d8c]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+aa1274]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `[kernel.kallsyms][+ffffffe760a21680]` | libc/kernel/vdso |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c65984]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c656a0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c632b0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c631f0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c3e908]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c1f254]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b89918]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b6b994]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b48524]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b47350]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b41998]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+ae6884]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+ab04d8]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+aa1324]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+aa12c0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GameThread | `sub_0019D250_0x19d250(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.09 | GameThread | `libunwind::LocalAddressSpace::getEncodedP(unsigned long&, unsigned long, unsigned char, unsigned long)` | profiler unwind overhead |
| 0.09 | GameThread | `__vfprintf` | libc/kernel/vdso |
| 0.09 | GameThread | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.09 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `PS2Runtime::dispatchGuestBranch(unsigned char*, R5900Context*, unsigned int, unsigned int, unsigned int, PS2Runtime::GuestBranchKind, char const*)` | EE runtime helpers |
| 0.08 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::popBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned short)` | libc/kernel/vdso |
| 0.08 | GsWorker | `ps2x_gs_parallel::(anonymous namespace)::GSParallelBackend::Present(GSPresentationRequest const&)` | paraLLEl CPU submit |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65970]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65670]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c653d0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65394]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65324]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c6508c]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c41678]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1d094]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1c638]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1ac24]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+bcaccc]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+bcac90]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b89aec]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b85914]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b7abc0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b419d0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b40e04]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b40bd8]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+ab04a8]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `bool scudo::PageReleaseContext::markFreeBlocksInRegion<scudo::TransferBatch<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::markFreeBlocks(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, unsigned long, unsigned long, scudo::SinglyLinkedList<scudo::BatchGroup<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>>&)::'lambda'(unsigned int)>(scudo::IntrusiveList<scudo::TransferBatch<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>> const&, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::markFreeBlocks(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, unsigned long, unsigned long, scudo::SinglyLinkedList<scudo::BatchGroup<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>>&)::'lambda'(unsigned int), unsigned long, unsigned long, unsigned long, bool)` | libc/kernel/vdso |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe760d65384]` | libc/kernel/vdso |
| 0.08 | GameThread | `sub_0037E120_0x37e120(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.08 | GameThread | `ps2DiagWatchEnabled()` | other |
| 0.08 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c6b86c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65cd0]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65c40]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65b64]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c6592c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c658bc]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65334]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c60650]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c38b7c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c2929c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1f2c0]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1f014]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1d490]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1d40c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1d108]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1d030]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1994c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+b88898]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+b484e8]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+b40f70]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+ae4d48]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+ab06b8]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+ab04c8]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+aa1264]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760d917d0]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760d35864]` | libc/kernel/vdso |
| 0.07 | GsWorker | `GS::writeRegisterPacked(unsigned char, unsigned long, unsigned long)` | GIF/GS packet handling |
| 0.07 | GameThread | `sub_003B49D0_0x3b49d0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GsWorker | `scudo_free` | libc/kernel/vdso |
| 0.06 | GsWorker | `scudo::HybridMutex::lock()` | scheduler/sync/waits |
| 0.06 | GsWorker | `madvise` | other |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65b54]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65b50]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65b44]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ae4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ae0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ac0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65aa4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65aa0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c659a8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65988]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65964]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658dc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658cc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658c8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c6578c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c653c0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65358]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c631d0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c60378]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c6030c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f2d8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f2cc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d334]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d110]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d0fc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d0a4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d064]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1cfbc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1cf28]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c19908]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c18d40]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c17690]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+bb389c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b89af4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b85cf4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b7b648]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b6c350]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b6b898]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b48a50]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b4899c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b473f4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b41968]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b41958]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b4158c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+af0b98]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+ae678c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+ae66dc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa1290]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa11bc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa0e20]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe7611d4f98]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c84]` | libc/kernel/vdso |
| 0.06 | GsWorker | `GS::vertexKick(bool)` | GIF/GS packet handling |
| 0.06 | GsWorker | `GS::buildDrawBatch(int) const` | GIF/GS packet handling |
| 0.06 | GameThread | `sub_00398A60_0x398a60(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `__emutls_get_address` | other |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `EeScheduler::checkpointDue(unsigned int)` | scheduler/sync/waits |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6b8c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65b94]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65ac4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c659c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c658d0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6588c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c656b8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65544]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c653b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65240]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c650e8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c650a8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6506c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6322c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c60678]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c60344]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c5f67c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c440c0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c419b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c3e940]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c28b68]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1e6b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d4bc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d328]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d0c4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cff4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cf50]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cf40]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c19928]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c18d20]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c18798]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c173c4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+bcb098]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+bcad14]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+bb3888]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b888b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b7a978]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b6c344]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b6b918]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b6b8f4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b48804]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b487c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b473f8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b459a4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b40e38]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b40da4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b40d5c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b40bd0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae67e0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae67b8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae4d8c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ab82e8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ab0698]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ab04b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+aa12cc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+a96c58]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e614]` | libc/kernel/vdso |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe760d625bc]` | libc/kernel/vdso |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe760a21688]` | libc/kernel/vdso |
| 0.05 | GameThread | `std::__ndk1::pair<std::__ndk1::__hash_iterator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, void*>*>, bool> std::__ndk1::__hash_table<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::__unordered_map_hasher<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::hash<unsigned int>, std::__ndk1::equal_to<unsigned int>, true>, std::__ndk1::__unordered_map_equal<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::equal_to<unsigned int>, std::__ndk1::hash<unsigned int>, true>, std::__ndk1::allocator<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>>>::__emplace_unique_key_args<unsigned int, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>, std::__ndk1::tuple<>>(unsigned int const&, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>&&, std::__ndk1::tuple<>&&)` | PS2 runtime other |
| 0.05 | GameThread | `pthread_mutex_lock` | scheduler/sync/waits |
| 0.05 | GameThread | `libunwind::LocalAddressSpace::getULEB128(unsigned long&, unsigned long)` | profiler unwind overhead |
| 0.05 | GameThread | `libunwind::CFI_Parser<libunwind::LocalAddressSpace>::parseFDEInstructions(libunwind::LocalAddressSpace&, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::FDE_Info const&, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::CIE_Info const&, unsigned long, int, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::PrologInfo*)` | profiler unwind overhead |
| 0.05 | GameThread | `__sfvwrite` | libc/kernel/vdso |
| 0.05 | GameThread | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0718(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0710(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0690(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0680(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0678(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0658(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0648(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0640(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0638(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0630(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GsWorker | `void ParallelGS::GSInterface::packed_XYZ<false, true, (ParallelGS::PRIMType)4>(void const*)` | paraLLEl CPU submit |
| 0.04 | GsWorker | `scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::refill(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::PerClass*, unsigned long, unsigned short)` | libc/kernel/vdso |
| 0.04 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::releaseToOSMaybe(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, scudo::ReleaseToOS)` | libc/kernel/vdso |
| 0.04 | GsWorker | `scudo::MemMapLinux::releaseAndZeroPagesToOSImpl(unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6b8e4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6b8b8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c65bb8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c658d4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c658c4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c658c0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c65890]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c657b0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6577c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6576c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6575c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c6574c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c653c8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c653a4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c65224]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c65100]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c650b4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c64b80]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c63748]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c631b0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c609f4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c606b0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c60658]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c60638]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c5f670]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c44114]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c41ddc]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c3f5dc]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c3f5a4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c3e934]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c3e928]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1e664]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1d324]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1d0e8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1cff8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1cfec]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c1c678]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c18d34]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+c17b60]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+bcafb8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+bcacac]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b888d0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b86264]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b857ec]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b7a94c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b7a824]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b7a810]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b6d5a4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b6c3f8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b6c1c4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b6bdac]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b6b8b8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b48a58]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b48964]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b48948]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b48900]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b47d48]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b47d2c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b47338]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b47330]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b47320]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b469a4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b4159c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b41594]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b40d94]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+b40d58]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+af0b88]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+af0b80]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aed324]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aed1ac]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aed17c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ae6528]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ae6198]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ae5d20]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ab84e0]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ab82c8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ab81f4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+ab06a8]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aa12ec]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aa1220]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aa11c4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+aa1178]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+a96cd4]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `libvulkan_freedreno.so[+a96c9c]` | Vulkan driver CPU (Turnip) |
| 0.04 | GsWorker | `__memcmp_aarch64` | libc/kernel/vdso |
| 0.04 | GsWorker | `[kernel.kallsyms][+ffffffe7611d5040]` | libc/kernel/vdso |
| 0.04 | GsWorker | `[kernel.kallsyms][+ffffffe760b45f2c]` | libc/kernel/vdso |
| 0.04 | GsWorker | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.04 | GsWorker | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.04 | GameThread | `sub_003E6574_0x3e6574(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `__memset_aarch64_nt` | __bzero/__memset zeroing |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0700(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 0.03 | com.ps2x.runner | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.03 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.03 | com.ps2x.runner | `WaitTime` | scheduler/sync/waits |
| 0.03 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::popBlocks(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, unsigned int*, unsigned short)` | libc/kernel/vdso |
| 0.03 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::hasChanceToReleasePages(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, unsigned long, scudo::ReleaseToOS)` | libc/kernel/vdso |
| 0.03 | GsWorker | `ps2_gfx_stats::detail::ensureInit()` | PS2 runtime other |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c6b8dc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c6b8c4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c6abe0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65bec]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65b9c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65b90]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65b2c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65ad4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65ad0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65a8c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65a5c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c659f0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c659e4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c659c4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c659a4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c657b4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65784]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65774]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65764]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65760]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65754]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c653b8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65398]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65378]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65338]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65128]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c650a4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c65098]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c64be0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c643c0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c643a0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c631cc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c60834]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c60744]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c606a0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c60688]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c603e4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c60358]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c60330]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c565dc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c41dd8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c41798]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c416e0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c3f5e0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c38c94]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c28b78]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c28994]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c28988]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c28940]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1ef30]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1ef2c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1e65c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1e654]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d498]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d330]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d31c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d118]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d0f8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1d058]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1cf38]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1cf30]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1cf20]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1cbb0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c1c3fc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+c198f8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bcc4cc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bcbd90]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bcbd5c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bcafb4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bb60bc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bb5d38]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bb5cfc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+bb3890]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b88860]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b859b0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b7b64c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b7a808]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b788b0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b78678]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6e43c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6c458]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6c1e0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6bfb0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6be7c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6be54]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6bd6c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6b9a8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6b94c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6b8a8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b6915c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b4b850]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b4b7c8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48a48]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48a3c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48a08]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b489ec]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48998]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b4897c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48970]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b48954]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b488ec]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b488e0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b488ac]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b487e4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b47d18]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b47368]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b4596c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b45490]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b415c8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b415a4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b41018]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40fc0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40fa8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40f90]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d9c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d64]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d60]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d54]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d4c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d1c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+b40d04]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+af0b90]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed270]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed250]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed230]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed204]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed1cc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed15c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aed13c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae6de8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae680c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae5d3c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae5d04]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae4bc8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae4ba0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae4b6c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ae4608]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab8474]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab82d8]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab81ac]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab342c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab06ac]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab069c]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab04e0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+ab04ac]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa11f0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa11d0]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa1194]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa1168]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa0e88]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+aa0e28]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+a96cdc]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `libvulkan_freedreno.so[+a96cc4]` | Vulkan driver CPU (Turnip) |
| 0.03 | GsWorker | `clock_gettime` | libc/kernel/vdso |
| 0.03 | GsWorker | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760d86994]` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760d35018]` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760be4d3c]` | libc/kernel/vdso |
| 0.03 | GsWorker | `ParallelGS::GSInterface::update_color_feedback_state()` | paraLLEl CPU submit |
| 0.03 | GameThread | `sub_003CB540_0x3cb540(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `ps2_e44_trace::storeArmed(unsigned int, unsigned int)` | PS2 runtime other |
| 0.03 | GameThread | `libunwind::DwarfInstructions<libunwind::LocalAddressSpace, libunwind::Registers_arm64>::stepWithDwarf(libunwind::LocalAddressSpace&, unsigned long, unsigned long, libunwind::Registers_arm64&, bool&, bool)` | profiler unwind overhead |
| 0.03 | GameThread | `__cxxabiv1::readEncodedPointer(unsigned char const**, unsigned char, unsigned long)` | other |
| 0.03 | GameThread | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3168(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3118(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ae8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0698(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0688(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0670(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1Interpreter::recordViWriteForBranch(unsigned char, int)` | VU1 interpreter/other |
| 0.03 | GameThread | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 0.03 | GameThread | `PS2Runtime::eeCheckpointDue(unsigned int)` | PS2 runtime other |
| 0.03 | GameThread | `PS2Memory::translateAddress(unsigned int)` | EE runtime helpers |
| 0.02 | com.ps2x.runner | `@plt` | PLT |
| 0.02 | GsWorker | `void ParallelGS::GSInterface::drawing_kick<(ParallelGS::PRIMType)4>(bool)` | paraLLEl CPU submit |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+cc8978]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6ac70]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6abac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c66320]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65d78]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65c44]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65c00]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65bf4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65bc4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b84]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b74]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b60]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b5c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b4c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b40]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b34]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b30]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b28]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65b24]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65abc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65ab4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65ab0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a88]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a84]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a80]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a4c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a20]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65a10]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c659d8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c659d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c659b8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c659b4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65998]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65994]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65980]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65948]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6593c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c658f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c658e4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c658b0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c658ac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c658a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c657bc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c657b8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c657a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65788]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65780]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65770]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65768]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65750]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65748]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c656a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65694]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c653bc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c653ac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c653a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6539c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65388]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65384]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65374]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65368]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65364]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6535c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65340]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65300]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c65234]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c651f8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c64be4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c64bb4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c643d8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c643cc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c63880]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c63850]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c63814]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c63718]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6119c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60b1c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60ae8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60ac8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60aac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60a8c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60a04]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c608e8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6081c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c606f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c606e8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60670]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6045c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c603b0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60398]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60394]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60374]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60370]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c60340]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c6032c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c5fa0c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c4426c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c4412c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c44088]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c41d18]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c41d08]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c418c0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c41830]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c41764]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c416f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c416ec]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c416e4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c416d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3fbfc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3f744]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3f5c8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3e938]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3e3b8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3e398]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c3b754]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38f70]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38f60]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38c90]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38c80]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38c78]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38c74]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c38be4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c292a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c289a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c289a4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c28984]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c28980]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1f2d0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1e64c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1e644]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d49c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d494]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d488]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d404]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d32c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d320]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d240]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d218]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d1f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d114]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d10c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d104]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d0f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d0f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d0ec]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d0e0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d0b4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d044]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1d004]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cffc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cff0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cfe4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cf60]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cf44]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cf3c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cf34]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cf2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cbf0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cb64]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cb4c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1cb1c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c8fc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c6a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c69c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c66c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c664]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c654]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c40c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1c408]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c19944]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c19924]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c1990c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c19904]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c19900]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c198f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c19834]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d3c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d30]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d28]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d24]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c18d14]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c17b20]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c175f8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c17518]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c166b8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+c16628]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bd0b50]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bd0b20]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcd3f8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcc4dc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcc4ac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcbe64]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcacd4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcacb8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bcacb4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bc9ca4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bb5d30]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bb4fc8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bb387c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+bb3874]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b9b858]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b89ae4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b8991c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b863e8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b863e0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b863d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b862d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b86274]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b8568c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b8542c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b81668]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f728]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f720]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f710]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f6f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f6cc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7f5f8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7aa98]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a96c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a93c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a91c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a900]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a800]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a7f8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b7a7f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b74bd8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6d674]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6d640]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6d5b0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6d5a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c4f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c418]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c408]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c360]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c354]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c328]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c214]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6c1e4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6be9c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6bc14]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6bc04]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b9b8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b8e4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b894]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b85c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b414]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b3e4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6b0f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6a7ec]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6a19c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b69fdc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6894c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b6892c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b8c4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b8b0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b8a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b8a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b898]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b888]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4b7d8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48c34]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48aa4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48a8c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48a54]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48a18]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b489a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b489a4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48994]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4896c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48960]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48950]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48920]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48910]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4890c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b488fc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b488f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b488a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4886c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4882c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48550]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b48540]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b482e8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b482d8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b482d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b47404]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4732c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b47318]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b46d90]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b4685c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b459a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b45980]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b454a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b45480]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b45474]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b41994]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b41978]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b415a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b410f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b410dc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b41010]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b41008]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40ffc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40fdc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f94]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f8c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f88]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f80]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f3c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40f08]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40ee8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40ec8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40eb8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40ea8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40e9c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40e80]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40dac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d98]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d90]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d88]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d84]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d70]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d6c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d44]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d28]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d24]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40d08]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40cf0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40cd8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40cd4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+b40be4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+afe1ac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+afbb8c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+afbb74]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+afbb6c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+af96f4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+af26e8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+af0b8c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed34c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed284]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed274]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed214]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed1f0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aed004]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aecf20]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aecc64]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aec734]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aea3a8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae6dfc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae6c80]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae6994]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae6938]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae655c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae62d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae61c4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae5d2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae5c6c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae5c48]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae5c24]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae4edc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae4e84]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae4db0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae4d98]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ae4bac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab858c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab84d0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab846c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab82ec]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab82dc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab82cc]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab8268]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab822c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab81c4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab81a0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab810c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab3a48]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab3a2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab3414]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab06d8]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab04d4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+ab04c4]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aa1268]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aa0e2c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aa0e24]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+aa0df0]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+a96cac]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e664]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e544]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760dd75d4]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c20]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760dcf690]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760d892a0]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760d76044]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760d625d0]` | libc/kernel/vdso |
| 0.02 | GsWorker | `GS::recordDrawDebugEventUnlocked(int)` | GIF/GS packet handling |
| 0.02 | GameThread | `sub_003CCA08_0x3cca08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003A3280_0x3a3280(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0037A430_0x37a430(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00375A08_0x375a08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00363490_0x363490(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.02 | GameThread | `pthread_getspecific` | scheduler/sync/waits |
| 0.02 | GameThread | `ps2_snd_spike::mixTickLocked(ps2_snd_spike::State&, unsigned char const*, unsigned char const*)` | SND/audio |
| 0.02 | GameThread | `ps2_e44_trace::detail::ensureInit()` | PS2 runtime other |
| 0.02 | GameThread | `ps2_e15::Trace::end(unsigned long, bool)` | PS2 runtime other |
| 0.02 | GameThread | `ps2_e15::Trace::Trace(char const*, unsigned long, unsigned char const*, R5900Context const*, unsigned int, unsigned int, int)` | PS2 runtime other |
| 0.02 | GameThread | `libunwind::EHHeaderParser<libunwind::LocalAddressSpace>::findFDE(libunwind::LocalAddressSpace&, unsigned long, unsigned long, unsigned int, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::FDE_Info*, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::CIE_Info*)` | profiler unwind overhead |
| 0.02 | GameThread | `libunwind::CFI_Parser<libunwind::LocalAddressSpace>::parseCIE(libunwind::LocalAddressSpace&, unsigned long, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::CIE_Info*)` | profiler unwind overhead |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3170(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3100(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ec8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0af0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ae0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ad8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0aa8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1548(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1538(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1530(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1520(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0708(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0668(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0660(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0650(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1Interpreter::resetScheduler()` | VU1 interpreter/other |
| 0.02 | GameThread | `VU1Interpreter::readBranchVi(unsigned char) const` | VU1 interpreter/other |
| 0.02 | GameThread | `VU1Interpreter::queueQ(float, unsigned int, unsigned int)` | VU1 interpreter/other |
| 0.02 | GameThread | `VU1Interpreter::advanceTo(unsigned long)` | VU1 interpreter/other |
| 0.02 | GameThread | `PS2Runtime::lookupFunction(unsigned int)` | PS2 runtime other |
| 0.02 | GameThread | `PS2Memory::writeIORegister(unsigned int, unsigned int)` | EE runtime helpers |
| 0.02 | GameThread | `@plt` | PLT |
| 0.02 | GameThread | `(anonymous namespace)::inRange(unsigned int, unsigned long, unsigned long, char const*, unsigned int)` | other |
| 0.01 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.01 | com.ps2x.runner | `!!!0000!58c4cf89d3544eaf0d40972d4ff12d!a9ee82cd83!` | other |
| 0.01 | GsWorker | `void ParallelGS::GSInterface::packed_STQRGBAXYZ<true, (ParallelGS::PRIMType)4, 1>(void const*, unsigned int)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `scudo::getMonotonicTimeFast()` | libc/kernel/vdso |
| 0.01 | GsWorker | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.01 | GsWorker | `pthread_mutex_lock` | scheduler/sync/waits |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c66838]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65d0c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65d04]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65cf0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65ce8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65c64]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65c60]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65c5c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65c50]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65bf0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65b7c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65b70]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65b58]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65b48]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65b3c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65ae8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65adc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65ad8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65acc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65ac8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65ab8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65aac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65aa8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65a94]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65a90]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65a6c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65a40]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65a04]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659dc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659b0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c659a0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6599c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65990]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6598c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6597c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65974]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6596c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65968]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65944]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65940]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65938]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65934]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c658ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c658e8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c658e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c658b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c658a8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65894]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c657a4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6534c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6532c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6531c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c652d4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65228]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65218]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65208]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c65108]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c650ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6509c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c64e28]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c64b94]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c64b70]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c643c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c63768]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c632b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c63294]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c63288]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c631c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c631bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c631b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c61250]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c61140]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60a00]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60788]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60730]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6071c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60718]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60714]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c606fc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c606d4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60698]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60674]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c6063c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c603d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c603a8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60384]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60350]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60324]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60320]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60314]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c60310]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c5f9e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c5f734]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c5f644]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c5658c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c441c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c44118]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c44110]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c440a4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c429a8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c417bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c417a0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c41794]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c41780]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c416dc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c41690]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3fbe8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3f5d8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3f5d4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3f5d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3b3ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3ac08]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3ab5c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c3a258]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c38f6c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c38f68]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c38f64]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c38bf0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c38bd8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c35d48]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c35a50]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c28d24]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c2899c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c28960]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c27a3c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c27504]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c258ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1f2c4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1f264]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1e63c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d4c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d3e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d338]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d318]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d224]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0d4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0b0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d0a8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1d020]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1cf4c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1ceb0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1cc00]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1c690]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1c674]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1c1f8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c198fc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17b80]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17b70]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17b5c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17b3c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17b38]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c176ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17530]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1752c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1750c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c174bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17444]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1743c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c1738c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+c17070]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bd1b70]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bd1b08]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bd1784]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bd0b60]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bd0b5c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcfba4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcd3f4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcc484]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcc464]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcbe68]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcbd88]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcb0ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcacc8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcacc4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bcab04]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bc9c68]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb60c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb5d18]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb4fa8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb4f98]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb4f50]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb3a24]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb38dc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb38a8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bb3884]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bae400]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+bae3e8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b9c6f0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b9c6d8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b9b430]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b98018]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b8c938]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b89b08]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b8887c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b86360]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b862c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b862b0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b86294]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b8627c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b8626c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b85dbc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b85cd0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b85668]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b81ee0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7f73c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7f5e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7f588]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7f4d8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7f4c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7cdb8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a9c4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a95c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a948]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a940]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a7fc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b7a028]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b79f64]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b79f1c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b79bd8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b78c50]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b78a8c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b789e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b76e78]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6d5ac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c5fc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c5ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c5e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c5cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c504]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c4ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c4bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c37c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c364]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c35c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c34c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c348]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c210]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c1d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6c1c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6bfac]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6be74]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6be6c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6baa4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b9a4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b964]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b95c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b954]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b8e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6b840]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6a63c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b6a0bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b68958]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b68940]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b64d8c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4b8e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4b7e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48c44]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48c3c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48aa8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a9c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a68]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a44]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a40]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a14]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48a0c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b489f8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b489cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b489b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4892c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4891c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b488e4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4889c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4888c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48870]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b487f8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b487c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48508]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48504]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b484b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b484a0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48484]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b48474]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b482d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b482cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47d38]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47d28]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47d24]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47d10]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47658]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47414]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4740c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47408]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47314]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4730c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b47284]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46d84]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46d60]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46d50]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46948]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46884]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46460]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46408]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b46390]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b459b0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b45994]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4544c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b419c8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41990]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b415a0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41598]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41590]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41020]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4101c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41014]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b4100c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b41000]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40fec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40fa0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f98]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f7c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f78]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f54]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f48]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40f30]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40ed8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40e8c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40da0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d80]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d48]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d40]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d18]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d10]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40d00]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40cf8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40ce8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40ce0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40be0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b40bdc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+b3cac0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+afe2f0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+afe1e8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+afcb0c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+afb17c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+af9744]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+af2704]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+af0bd8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+af0bc8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+af0b94]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aee300]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aee2e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aee2c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed258]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed220]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed1f4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed1e0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed16c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aed14c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aecefc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aecec0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aec9d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aebba8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae9038]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae8d14]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae67ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae6780]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae6550]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae63b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae633c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae6338]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae6334]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae6324]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae62fc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae621c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4e04]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4d5c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4b94]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4684]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae467c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4678]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ae4668]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+add99c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+add970]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ac0b3c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab84f4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab84f0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab84ec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab84e8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab849c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8494]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab848c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8488]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8470]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8228]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8214]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8208]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8180]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8160]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab8138]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab68b0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab36bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab340c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab1790]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab1784]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab1780]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab1774]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab06d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab06b4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab06a4]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab063c]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04dc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04d0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04cc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04c0]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04bc]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+ab04b8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aa12d8]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aa0e74]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+aa0e30]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+a9f778]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+a9ddec]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+a96d00]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+a96c94]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `libvulkan_freedreno.so[+a96c60]` | Vulkan driver CPU (Turnip) |
| 0.01 | GsWorker | `__vfprintf` | libc/kernel/vdso |
| 0.01 | GsWorker | `__emutls_get_address` | other |
| 0.01 | GsWorker | `__aarch64_ldadd8_relax` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe761a5db58]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760dd7868]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760d89040]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760d70f00]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760d35238]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760b46310]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760aed210]` | libc/kernel/vdso |
| 0.01 | GsWorker | `ParallelGS::triangle_is_parallelogram_candidate(ParallelGS::VertexPosition const*, ParallelGS::VertexAttribute const*, muglm::tvec2<int> const&, muglm::tvec2<int> const&, ParallelGS::PRIMBits const&, muglm::tvec3<int>&)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::compute_page_rect(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::GSInterface::gif_transfer(unsigned int, void const*, unsigned long)` | paraLLEl CPU submit |
| 0.01 | GameThread | `vsnprintf` | other |
| 0.01 | GameThread | `void std::__ndk1::__introsort<std::__ndk1::_ClassicAlgPolicy, EeScheduler::publishSnapshot()::$_1&, EeSemaphoreSnapshot*, false>(EeSemaphoreSnapshot*, EeSemaphoreSnapshot*, EeScheduler::publishSnapshot()::$_1&, std::__ndk1::iterator_traits<EeSemaphoreSnapshot*>::difference_type, bool)` | scheduler/sync/waits |
| 0.01 | GameThread | `sub_003921F0_0x3921f0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0038B0F8_0x38b0f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00382AF0_0x382af0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00362DE8_0x362de8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0032E100_0x32e100(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002BCBD0_0x2bcbd0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0022A830_0x22a830(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `std::__ndk1::mutex::lock()` | scheduler/sync/waits |
| 0.01 | GameThread | `std::__ndk1::deque<GsCommand, std::__ndk1::allocator<GsCommand>>::push_back(GsCommand&&)` | other |
| 0.01 | GameThread | `scudo::HybridMutex::unlock()` | scheduler/sync/waits |
| 0.01 | GameThread | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 0.01 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.01 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::allocate(unsigned long, scudo::Chunk::Origin, unsigned long, bool)` | libc/kernel/vdso |
| 0.01 | GameThread | `ps2_e15::enabled()` | PS2 runtime other |
| 0.01 | GameThread | `__vsnprintf_chk` | other |
| 0.01 | GameThread | `__gxx_personality_v0` | other |
| 0.01 | GameThread | `[linker]get_tls_module(unsigned long)` | other |
| 0.01 | GameThread | `[kernel.kallsyms][+ffffffe761a6b788]` | libc/kernel/vdso |
| 0.01 | GameThread | `VU1RecompImage<62934506637816249ul>::f0628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3110(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3108(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ee0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ea8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ea0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ad0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ac8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ac0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1528(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1518(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1500(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0720(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0560(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0540(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0530(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1Interpreter::queueViWrite(unsigned char, int, unsigned int)` | VU1 interpreter/other |
| 0.01 | GameThread | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | VU1 interpreter/other |
| 0.01 | GameThread | `VU1Interpreter::queueClip(unsigned int)` | VU1 interpreter/other |
| 0.01 | GameThread | `PS2Memory::write128(unsigned int, __Int64x2_t)` | EE runtime helpers |
| 0.01 | GameThread | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.01 | GameThread | `(anonymous namespace)::e37AppendVif(char const*, unsigned char, char const*, char const*, char const*, unsigned int, unsigned int, char const*, unsigned int const*, unsigned char const*, unsigned int, bool, unsigned int, char const*)` | other |
| 0.01 | AAudio_1 | `ma_linear_resampler_process_pcm_frames` | other |
| 0.01 | AAudio_1 | `(anonymous namespace)::audioCallback(void*, unsigned int)` | SND/audio |
