rows=302 covered=50.14%
| Stage | Self % |
|---|---|
| Vulkan driver CPU (Turnip) | 20.24% |
| libc/kernel/vdso | 16.50% |
| scheduler/sync/waits | 4.76% |
| VU1 hazard bookkeeping | 3.50% |
| VU1 execute | 2.98% |
| profiler unwind overhead | 0.76% |
| PLT | 0.59% |
| guest code | 0.39% |
| other | 0.25% |
| EE runtime helpers | 0.12% |
| VIF1/DMA | 0.05% |

| Self % | Thread | Symbol | Stage |
|---|---|---|---|
| 3.18 | GsWorker | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 1.99 | GameThread | `VU1Interpreter::commitReadyPipelines()` | VU1 hazard bookkeeping |
| 1.59 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 1.47 | GsWorker | `scudo::HybridMutex::unlock()` | scheduler/sync/waits |
| 1.22 | GameThread | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | VU1 hazard bookkeeping |
| 1.17 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e860]` | libc/kernel/vdso |
| 1.13 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::allocate(unsigned long, scudo::Chunk::Origin, unsigned long, bool)` | libc/kernel/vdso |
| 1.10 | GsWorker | `__memset_aarch64_nt` | libc/kernel/vdso |
| 1.03 | GsWorker | `libvulkan_freedreno.so[+b40d34]` | Vulkan driver CPU (Turnip) |
| 0.98 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.91 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.86 | GsWorker | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.70 | GsWorker | `[kernel.kallsyms][+ffffffe760a47efc]` | libc/kernel/vdso |
| 0.67 | GameThread | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 0.63 | GsWorker | `libvulkan_freedreno.so[+b40d68]` | Vulkan driver CPU (Turnip) |
| 0.59 | GsWorker | `malloc` | libc/kernel/vdso |
| 0.55 | GameThread | `libunwind::findUnwindSectionsByPhdr(dl_phdr_info*, unsigned long, void*)` | profiler unwind overhead |
| 0.44 | GsWorker | `libvulkan_freedreno.so[+b489b8]` | Vulkan driver CPU (Turnip) |
| 0.42 | GsWorker | `libvulkan_freedreno.so[+b40d74]` | Vulkan driver CPU (Turnip) |
| 0.42 | GsWorker | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.42 | GsWorker | `[kernel.kallsyms][+ffffffe760a21688]` | libc/kernel/vdso |
| 0.40 | GsWorker | `libvulkan_freedreno.so[+b40d3c]` | Vulkan driver CPU (Turnip) |
| 0.40 | GsWorker | `[kernel.kallsyms][+ffffffe760a21680]` | libc/kernel/vdso |
| 0.39 | GameThread | `VU1Interpreter::execUpper(unsigned int)` | VU1 execute |
| 0.38 | GsWorker | `libvulkan_freedreno.so[+b40f60]` | Vulkan driver CPU (Turnip) |
| 0.37 | GameThread | `VU1Interpreter::normalizeOperand(float) const` | VU1 execute |
| 0.36 | GameThread | `VU1Interpreter::calculateFmacExactResult(unsigned int, double&) const` | VU1 execute |
| 0.35 | GsWorker | `__aarch64_cas4_acq` | libc/kernel/vdso |
| 0.35 | GsWorker | `[kernel.kallsyms][+ffffffe760cfb750]` | libc/kernel/vdso |
| 0.34 | GameThread | `@plt` | PLT |
| 0.31 | GsWorker | `libvulkan_freedreno.so[+c1d314]` | Vulkan driver CPU (Turnip) |
| 0.30 | com.ps2x.runner | `clock_gettime` | libc/kernel/vdso |
| 0.30 | GsWorker | `libvulkan_freedreno.so[+b489ac]` | Vulkan driver CPU (Turnip) |
| 0.29 | GsWorker | `libvulkan_freedreno.so[+b6b8ac]` | Vulkan driver CPU (Turnip) |
| 0.29 | GameThread | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | VU1 hazard bookkeeping |
| 0.28 | GameThread | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | VU1 execute |
| 0.27 | GsWorker | `libvulkan_freedreno.so[+c1d0dc]` | Vulkan driver CPU (Turnip) |
| 0.26 | GsWorker | `[kernel.kallsyms][+ffffffe760d65040]` | libc/kernel/vdso |
| 0.25 | GsWorker | `libvulkan_freedreno.so[+b40f9c]` | Vulkan driver CPU (Turnip) |
| 0.25 | GsWorker | `[kernel.kallsyms][+ffffffe760d2cbf8]` | libc/kernel/vdso |
| 0.25 | GsWorker | `@plt` | PLT |
| 0.23 | com.ps2x.runner | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.23 | GsWorker | `libvulkan_freedreno.so[+b6b8d0]` | Vulkan driver CPU (Turnip) |
| 0.23 | GsWorker | `__aarch64_ldadd4_rel` | libc/kernel/vdso |
| 0.23 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a0]` | libc/kernel/vdso |
| 0.22 | GsWorker | `libvulkan_freedreno.so[+c1d11c]` | Vulkan driver CPU (Turnip) |
| 0.22 | GameThread | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | VU1 execute |
| 0.21 | GsWorker | `libvulkan_freedreno.so[+c1cf58]` | Vulkan driver CPU (Turnip) |
| 0.21 | GsWorker | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.21 | GsWorker | `[kernel.kallsyms][+ffffffe760a2168c]` | libc/kernel/vdso |
| 0.21 | GameThread | `[linker]do_dl_iterate_phdr(int (*)(dl_phdr_info*, unsigned long, void*), void*)` | profiler unwind overhead |
| 0.20 | com.ps2x.runner | `!!!0000!a0d82c13dd4b4e4f31b6cd30a2cb0d!a9ee82cd83!` | other |
| 0.20 | GsWorker | `libvulkan_freedreno.so[+c1d100]` | Vulkan driver CPU (Turnip) |
| 0.20 | GsWorker | `libvulkan_freedreno.so[+b48538]` | Vulkan driver CPU (Turnip) |
| 0.20 | GameThread | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 0.19 | GsWorker | `[kernel.kallsyms][+ffffffe760d8565c]` | libc/kernel/vdso |
| 0.18 | GsWorker | `scudo_malloc` | libc/kernel/vdso |
| 0.18 | GsWorker | `libvulkan_freedreno.so[+b419a8]` | Vulkan driver CPU (Turnip) |
| 0.18 | GameThread | `__memset_aarch64_nt` | libc/kernel/vdso |
| 0.17 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c84]` | libc/kernel/vdso |
| 0.17 | GameThread | `sub_00376938_0x376938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.17 | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | VU1 execute |
| 0.16 | GsWorker | `void scudo::releaseFreeMemoryToOS<scudo::RegionReleaseRecorder<scudo::MemMapLinux>, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::releaseToOSMaybe(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, scudo::ReleaseToOS)::'lambda'(unsigned long)>(scudo::PageReleaseContext&, scudo::RegionReleaseRecorder<scudo::MemMapLinux>&, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::releaseToOSMaybe(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, scudo::ReleaseToOS)::'lambda'(unsigned long))` | libc/kernel/vdso |
| 0.16 | GsWorker | `libvulkan_freedreno.so[+c656ac]` | Vulkan driver CPU (Turnip) |
| 0.16 | GsWorker | `libvulkan_freedreno.so[+b6d648]` | Vulkan driver CPU (Turnip) |
| 0.16 | GameThread | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.15 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocks(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, unsigned int*, unsigned int)` | libc/kernel/vdso |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+c658b8]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+c658a4]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+b6b86c]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `libvulkan_freedreno.so[+b482dc]` | Vulkan driver CPU (Turnip) |
| 0.15 | GsWorker | `free` | libc/kernel/vdso |
| 0.15 | GameThread | `sub_0019D250_0x19d250(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.15 | GameThread | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | VU1 execute |
| 0.14 | GsWorker | `scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::drain(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>::PerClass*, unsigned long)` | libc/kernel/vdso |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+c1c670]` | Vulkan driver CPU (Turnip) |
| 0.14 | GsWorker | `libvulkan_freedreno.so[+b48510]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+c1d000]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+b6d64c]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+b6bfb4]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+b482c8]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `libvulkan_freedreno.so[+aa12b8]` | Vulkan driver CPU (Turnip) |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe7611d5040]` | libc/kernel/vdso |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c65b38]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c65898]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c657a0]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c65348]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c1cf48]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+c1c68c]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `libvulkan_freedreno.so[+b41974]` | Vulkan driver CPU (Turnip) |
| 0.12 | GsWorker | `[kernel.kallsyms][+ffffffe761a79608]` | libc/kernel/vdso |
| 0.12 | GsWorker | `[kernel.kallsyms][+ffffffe760b99edc]` | libc/kernel/vdso |
| 0.12 | GsWorker | `[kernel.kallsyms][+ffffffe760b98830]` | libc/kernel/vdso |
| 0.11 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned int, bool)` | libc/kernel/vdso |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+b6bfa4]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+b6b87c]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `libvulkan_freedreno.so[+b40be8]` | Vulkan driver CPU (Turnip) |
| 0.11 | GsWorker | `[kernel.kallsyms][+ffffffe760a15520]` | libc/kernel/vdso |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c65b8c]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c65b80]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c631f0]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c631e8]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c3f644]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+c1d4d0]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+b6b994]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+b6b968]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+ae57b4]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `libvulkan_freedreno.so[+aa0e38]` | Vulkan driver CPU (Turnip) |
| 0.10 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c20]` | libc/kernel/vdso |
| 0.10 | GameThread | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.10 | GameThread | `VU1Interpreter::progressXgkick()` | VU1 execute |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c65a7c]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c65984]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c656a0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c65394]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c632b0]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c3e908]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c1f254]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+c19210]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b6c370]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b47350]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b41998]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+b40bd8]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+ae6884]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+ab04d8]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+aa1324]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `libvulkan_freedreno.so[+aa1274]` | Vulkan driver CPU (Turnip) |
| 0.09 | GsWorker | `[kernel.kallsyms][+ffffffe761a79580]` | libc/kernel/vdso |
| 0.09 | GsWorker | `[kernel.kallsyms][+ffffffe760a21684]` | libc/kernel/vdso |
| 0.08 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::popBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned short)` | libc/kernel/vdso |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c6b86c]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65cd0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c653d0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c65324]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c41678]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1d40c]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1d094]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1ac24]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+c1994c]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+bcaccc]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+bcac90]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b89aec]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b89918]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b85914]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b7abc0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b48524]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b419d0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b40e04]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+b40d8c]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+ab04a8]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `libvulkan_freedreno.so[+aa12c0]` | Vulkan driver CPU (Turnip) |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe7611d4f98]` | libc/kernel/vdso |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe760d35864]` | libc/kernel/vdso |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65c40]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65b64]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c658bc]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c65670]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c6508c]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c60378]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1d0fc]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+c1c638]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+b89af4]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+b484e8]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `libvulkan_freedreno.so[+ab06b8]` | Vulkan driver CPU (Turnip) |
| 0.07 | GsWorker | `bool scudo::PageReleaseContext::markFreeBlocksInRegion<scudo::TransferBatch<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::markFreeBlocks(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, unsigned long, unsigned long, scudo::SinglyLinkedList<scudo::BatchGroup<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>>&)::'lambda'(unsigned int)>(scudo::IntrusiveList<scudo::TransferBatch<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>> const&, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::markFreeBlocks(scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned long, unsigned long, unsigned long, scudo::SinglyLinkedList<scudo::BatchGroup<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>>&)::'lambda'(unsigned int), unsigned long, unsigned long, unsigned long, bool)` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e6e0]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e614]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760d65384]` | libc/kernel/vdso |
| 0.07 | GameThread | `sub_00398A60_0x398a60(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | VU1 execute |
| 0.06 | GsWorker | `scudo_free` | libc/kernel/vdso |
| 0.06 | GsWorker | `scudo::HybridMutex::lock()` | scheduler/sync/waits |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65b54]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ae4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ae0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65ac4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65aa4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65aa0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c659a8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65988]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65970]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65964]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c6592c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658dc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658cc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c658c8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65358]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c65334]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c631d0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c60650]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c6030c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c38b7c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c2929c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f2d8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f2cc]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f2c0]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1f014]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d490]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d110]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d108]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d0a4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1d064]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c1cf28]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c19908]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+c18d40]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+bb3888]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b88898]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b85cf4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b7b648]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b7a978]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b6c350]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b6b898]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b4899c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b473f4]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b41958]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b4158c]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+b40f70]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+af0b98]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+ae4d48]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+ab0698]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+ab04c8]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa1290]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa1264]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `libvulkan_freedreno.so[+aa0e20]` | Vulkan driver CPU (Turnip) |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a7ae44]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a8]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a79560]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760d917d0]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760d86994]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760855968]` | libc/kernel/vdso |
| 0.06 | GameThread | `PS2Runtime::dispatchGuestBranch(unsigned char*, R5900Context*, unsigned int, unsigned int, unsigned int, PS2Runtime::GuestBranchKind, char const*)` | EE runtime helpers |
| 0.06 | GameThread | `PS2Memory::advanceEeTimers(unsigned long)` | EE runtime helpers |
| 0.05 | GsWorker | `madvise` | other |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6b8c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65b94]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65b50]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65b44]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65ac0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c659c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6578c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6575c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c6574c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c656b8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65544]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c653c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c653c0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c653b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c65240]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c650e8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c650b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c650a8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c60678]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c60344]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c44114]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c440c0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c419b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c3f5dc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c3e928]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1e6b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1e664]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d334]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d328]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d0e8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d0c4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1d030]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cff4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cfbc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cf50]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c1cf40]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c19928]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c18d20]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c18798]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c17690]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+c173c4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+bcad14]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+bb389c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b888b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b7a810]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b48a50]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b48948]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b48804]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b487c8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b473f8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b459a4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b41968]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+b40d5c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae67e0]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae67b8]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae678c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae66dc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae5d20]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ae4d8c]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+ab04b4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+aa12cc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+aa11c4]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+aa11bc]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+aa1178]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `libvulkan_freedreno.so[+a96c58]` | Vulkan driver CPU (Turnip) |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe760cf8c1c]` | libc/kernel/vdso |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.05 | GameThread | `PS2Memory::processVIF1Data(unsigned char const*, unsigned int)` | VIF1/DMA |
| 0.05 | GameThread | `EeScheduler::accountCycles(unsigned int)` | scheduler/sync/waits |
