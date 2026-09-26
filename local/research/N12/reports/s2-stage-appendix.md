rows=1514 covered=83.44%
| Stage | Self % |
|---|---|
| VU1 generated pairs | 38.01% |
| libc/kernel/vdso | 12.57% |
| guest code | 8.14% |
| VU1 interpreter/other | 7.91% |
| VU1 issue/hazard | 3.19% |
| paraLLEl CPU submit | 2.81% |
| GIF/GS packet handling | 2.68% |
| scheduler/sync/waits | 1.94% |
| other | 1.88% |
| VIF1/DMA | 1.12% |
| PS2 runtime other | 0.95% |
| profiler unwind overhead | 0.88% |
| EE runtime helpers | 0.72% |
| __bzero/__memset zeroing | 0.29% |
| PLT | 0.14% |
| SND/audio | 0.13% |
| VU0 | 0.06% |
| Vulkan driver CPU (Turnip) | 0.02% |

| Self % | Thread | Symbol | Stage |
|---|---|---|---|
| 4.72 | GameThread | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 3.19 | GameThread | `VU1Interpreter::commitReadyPipelines()` | VU1 issue/hazard |
| 2.52 | GameThread | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 2.42 | GameThread | `VU1Interpreter::execUpper(unsigned int)` | VU1 interpreter/other |
| 1.17 | com.ps2x.runner | `clock_gettime` | libc/kernel/vdso |
| 1.12 | GameThread | `PS2Memory::processVIF1DataImpl(unsigned char const*, unsigned int)` | VIF1/DMA |
| 0.90 | com.ps2x.runner | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.89 | GameThread | `VU1Interpreter::progressXgkick()` | VU1 interpreter/other |
| 0.86 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<false, false, false, 3u>()` | paraLLEl CPU submit |
| 0.68 | GameThread | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.66 | GsWorker | `GS::writeRegisterPacked(unsigned char, unsigned long, unsigned long)` | GIF/GS packet handling |
| 0.62 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.62 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.61 | GameThread | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.57 | GameThread | `__vfprintf` | libc/kernel/vdso |
| 0.56 | GameThread | `libunwind::findUnwindSectionsByPhdr(dl_phdr_info*, unsigned long, void*)` | profiler unwind overhead |
| 0.55 | GsWorker | `GS::buildDrawBatch(int) const` | GIF/GS packet handling |
| 0.55 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.54 | GsWorker | `GS::vertexKick(bool)` | GIF/GS packet handling |
| 0.50 | GameThread | `sub_0037E120_0x37e120(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.47 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.46 | GameThread | `__emutls_get_address` | other |
| 0.41 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.38 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.34 | GameThread | `__sfvwrite` | libc/kernel/vdso |
| 0.33 | GameThread | `[kernel.kallsyms][+ffffffe761a8e664]` | libc/kernel/vdso |
| 0.32 | GameThread | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.32 | GameThread | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 0.31 | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | VU1 interpreter/other |
| 0.30 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.30 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0638(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.30 | GameThread | `VU1Interpreter::readBranchVi(unsigned char) const` | VU1 interpreter/other |
| 0.29 | GsWorker | `void ParallelGS::GSInterface::packed_XYZ<false, true, (ParallelGS::PRIMType)4>(void const*)` | paraLLEl CPU submit |
| 0.29 | GsWorker | `ps2_gfx_stats::detail::ensureInit()` | PS2 runtime other |
| 0.29 | GameThread | `[kernel.kallsyms][+ffffffe761a6b788]` | libc/kernel/vdso |
| 0.29 | GameThread | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.29 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0710(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.29 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0678(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.28 | GsWorker | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.28 | GameThread | `sub_00376938_0x376938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.28 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.27 | GameThread | `ps2DiagWatchEnabled()` | other |
| 0.27 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0690(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.27 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0680(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.27 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0640(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.27 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.27 | GameThread | `VU1Interpreter::recordViWriteForBranch(unsigned char, int)` | VU1 interpreter/other |
| 0.26 | GameThread | `pthread_mutex_lock` | scheduler/sync/waits |
| 0.25 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0718(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0648(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.25 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0630(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.24 | GameThread | `sub_0032E100_0x32e100(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.24 | GameThread | `__memset_aarch64_nt` | __bzero/__memset zeroing |
| 0.24 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.24 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0658(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.23 | GsWorker | `ps2x_gs_parallel::(anonymous namespace)::GSParallelBackend::Present(GSPresentationRequest const&)` | paraLLEl CPU submit |
| 0.23 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.23 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0700(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.22 | GsWorker | `__emutls_get_address` | other |
| 0.22 | GameThread | `sub_002E8938_0x2e8938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.21 | GsWorker | `void ParallelGS::GSInterface::drawing_kick<(ParallelGS::PRIMType)4>(bool)` | paraLLEl CPU submit |
| 0.21 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.20 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.20 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.20 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.20 | GameThread | `VU1Interpreter::resetScheduler()` | VU1 interpreter/other |
| 0.19 | GsWorker | `ParallelGS::GSInterface::update_color_feedback_state()` | paraLLEl CPU submit |
| 0.19 | GameThread | `sub_0022ADD8_0x22add8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.19 | GameThread | `std::__ndk1::pair<std::__ndk1::__hash_iterator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, void*>*>, bool> std::__ndk1::__hash_table<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::__unordered_map_hasher<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::hash<unsigned int>, std::__ndk1::equal_to<unsigned int>, true>, std::__ndk1::__unordered_map_equal<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::equal_to<unsigned int>, std::__ndk1::hash<unsigned int>, true>, std::__ndk1::allocator<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>>>::__emplace_unique_key_args<unsigned int, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>, std::__ndk1::tuple<>>(unsigned int const&, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>&&, std::__ndk1::tuple<>&&)` | PS2 runtime other |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3118(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0af0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ae8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1538(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0698(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.19 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0670(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.18 | GsWorker | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.18 | GameThread | `[linker]do_dl_iterate_phdr(int (*)(dl_phdr_info*, unsigned long, void*), void*)` | profiler unwind overhead |
| 0.18 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3170(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.18 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3168(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.18 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ec8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `sub_0038B0F8_0x38b0f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.17 | GameThread | `sub_0037A430_0x37a430(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.17 | GameThread | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.17 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0aa8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1548(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.17 | GameThread | `VU1Interpreter::advanceTo(unsigned long)` | VU1 interpreter/other |
| 0.17 | GameThread | `PS2Memory::advanceEeTimers(unsigned long)` | EE runtime helpers |
| 0.16 | com.ps2x.runner | `!!!0000!a0d82c13dd4b4e4f31b6cd30a2cb0d!a9ee82cd83!` | other |
| 0.16 | GsWorker | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.16 | GsWorker | `GS::recordDrawDebugEventUnlocked(int)` | GIF/GS packet handling |
| 0.16 | GameThread | `sub_002BCBD0_0x2bcbd0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.16 | GameThread | `sub_0022A830_0x22a830(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.16 | GameThread | `sub_001E9A30_0x1e9a30(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.16 | GameThread | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 0.16 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3100(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.16 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ee0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.16 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.16 | GameThread | `PS2Runtime::dispatchGuestBranch(unsigned char*, R5900Context*, unsigned int, unsigned int, unsigned int, PS2Runtime::GuestBranchKind, char const*)` | EE runtime helpers |
| 0.15 | GameThread | `sub_0013D818_0x13d818(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.15 | GameThread | `__aarch64_cas2_acq` | libc/kernel/vdso |
| 0.15 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.15 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.15 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.14 | GsWorker | `ParallelGS::GSInterface::gif_transfer(unsigned int, void const*, unsigned long)` | paraLLEl CPU submit |
| 0.14 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1530(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.14 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1520(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.14 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.14 | GameThread | `EeScheduler::accountCycles(unsigned int)` | scheduler/sync/waits |
| 0.13 | GameThread | `__aarch64_swp2_rel` | libc/kernel/vdso |
| 0.13 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ae0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1518(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.13 | GameThread | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ea8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f14a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f14a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1498(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1470(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1528(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.12 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.11 | GsWorker | `void ParallelGS::GSInterface::packed_STQRGBAXYZ<true, (ParallelGS::PRIMType)4, 1>(void const*, unsigned int)` | paraLLEl CPU submit |
| 0.11 | GsWorker | `__aarch64_ldadd8_relax` | libc/kernel/vdso |
| 0.11 | GsWorker | `[kernel.kallsyms][+ffffffe761a83a5c]` | libc/kernel/vdso |
| 0.11 | GameThread | `sub_0030F2B0_0x30f2b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.11 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.11 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.11 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ac8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.11 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0708(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.11 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0688(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GsWorker | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.10 | GameThread | `sub_00386DD0_0x386dd0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2f30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ed8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ec0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ea0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ad8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ad0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1500(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0660(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0650(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.10 | GameThread | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | VU1 interpreter/other |
| 0.10 | GameThread | `VU1Interpreter::queueQ(float, unsigned int, unsigned int)` | VU1 interpreter/other |
| 0.10 | GameThread | `VU1Interpreter::queueClip(unsigned int)` | VU1 interpreter/other |
| 0.10 | GameThread | `PS2Memory::writeIORegister(unsigned int, unsigned int)` | EE runtime helpers |
| 0.09 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.09 | GsWorker | `std::__ndk1::deque<GsCommand, std::__ndk1::allocator<GsCommand>>::pop_front()` | other |
| 0.09 | GsWorker | `pthread_mutex_lock` | scheduler/sync/waits |
| 0.09 | GsWorker | `GS::recordRegisterDebugEventUnlocked(unsigned char, unsigned long)` | GIF/GS packet handling |
| 0.09 | GameThread | `sub_0020EDA0_0x20eda0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.09 | GameThread | `sub_00174848_0x174848(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.09 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3110(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1458(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1508(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0668(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.09 | GameThread | `PS2Memory::translateAddress(unsigned int)` | EE runtime helpers |
| 0.08 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.08 | GsWorker | `ParallelGS::compute_page_rect(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int)` | paraLLEl CPU submit |
| 0.08 | GameThread | `sub_003CB540_0x3cb540(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.08 | GameThread | `sub_00389CB8_0x389cb8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.08 | GameThread | `sub_0032B6E0_0x32b6e0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.08 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ee8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.08 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1488(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.08 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1460(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.08 | GameThread | `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int, unsigned int, unsigned int, unsigned int)` | VU1 interpreter/other |
| 0.08 | GameThread | `@plt` | PLT |
| 0.08 | GameThread | `(anonymous namespace)::e37AppendVif(char const*, unsigned char, char const*, char const*, char const*, unsigned int, unsigned int, char const*, unsigned int const*, unsigned char const*, unsigned int, bool, unsigned int, char const*)` | other |
| 0.07 | com.ps2x.runner | `WaitTime` | scheduler/sync/waits |
| 0.07 | GsWorker | `__aarch64_cas2_acq` | libc/kernel/vdso |
| 0.07 | GsWorker | `ParallelGS::triangle_is_parallelogram_candidate(ParallelGS::VertexPosition const*, ParallelGS::VertexAttribute const*, muglm::tvec2<int> const&, muglm::tvec2<int> const&, ParallelGS::PRIMBits const&, muglm::tvec3<int>&)` | paraLLEl CPU submit |
| 0.07 | GsWorker | `ParallelGS::PageTracker::mark_fb_write(ParallelGS::PageRect const&)` | paraLLEl CPU submit |
| 0.07 | GsWorker | `GsCommand::operator=(GsCommand&&)` | other |
| 0.07 | GameThread | `sub_0011E150_0x11e150(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3350(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3120(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3108(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2f38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ef8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ef0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1450(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ac0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ab8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1440(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0738(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0720(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0608(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0540(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0538(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.07 | GameThread | `GsWorker::enqueue(GsCommand)` | scheduler/sync/waits |
| 0.06 | com.ps2x.runner | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.06 | GsWorker | `scudo::HybridMutex::unlock()` | scheduler/sync/waits |
| 0.06 | GsWorker | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 0.06 | GsWorker | `__aarch64_swp2_rel` | libc/kernel/vdso |
| 0.06 | GsWorker | `ParallelGS::PageTracker::register_accessed_fb_pages(unsigned int)` | paraLLEl CPU submit |
| 0.06 | GsWorker | `ParallelGS::GSInterface::drawing_kick_update_state(ParallelGS::GSInterface::FBFeedbackMode, muglm::tvec4<int> const&, muglm::tvec4<int> const&)` | paraLLEl CPU submit |
| 0.06 | GsWorker | `ParallelGS::GSInterface::check_frame_buffer_state()` | paraLLEl CPU submit |
| 0.06 | GsWorker | `GsWorker::threadMain()` | GIF/GS packet handling |
| 0.06 | GameThread | `vsnprintf` | other |
| 0.06 | GameThread | `sub_00382AF0_0x382af0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_0037D090_0x37d090(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_0033CCF8_0x33ccf8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_0033B748_0x33b748(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_002E3AF8_0x2e3af8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_002DD0B8_0x2dd0b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `sub_0013D1B8_0x13d1b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `std::__ndk1::mutex::lock()` | scheduler/sync/waits |
| 0.06 | GameThread | `pthread_cond_signal` | scheduler/sync/waits |
| 0.06 | GameThread | `libunwind::LocalAddressSpace::getEncodedP(unsigned long&, unsigned long, unsigned char, unsigned long)` | profiler unwind overhead |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f31a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3178(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2eb8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2eb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2de8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1540(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1510(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1468(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1430(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1428(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0750(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f06a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0618(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0598(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0568(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0560(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0558(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0548(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.06 | GameThread | `PS2Runtime::executeVU0Microprogram(unsigned char*, R5900Context*, unsigned int)` | VU0 |
| 0.06 | GameThread | `EeScheduler::checkpointDue(unsigned int)` | scheduler/sync/waits |
| 0.06 | AAudio_1 | `ma_linear_resampler_process_pcm_frames` | other |
| 0.05 | GsWorker | `ParallelGS::PageTracker::register_accessed_readback_page(unsigned int)` | paraLLEl CPU submit |
| 0.05 | GsWorker | `ParallelGS::GSInterface::update_optimized_gif_handler(unsigned int)` | paraLLEl CPU submit |
| 0.05 | GsWorker | `GS::noteConsumedCommand(GsCommand const&)` | GIF/GS packet handling |
| 0.05 | GameThread | `sub_003905E8_0x3905e8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_00375A08_0x375a08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_00374D00_0x374d00(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_00363490_0x363490(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_0034DBA8_0x34dba8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_002F39C8_0x2f39c8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_002E02B8_0x2e02b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_0021D1A0_0x21d1a0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_0015EE00_0x15ee00(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_0015E668_0x15e668(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `sub_0011F3D8_0x11f3d8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `scudo::HybridMutex::unlock()` | scheduler/sync/waits |
| 0.05 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::allocate(unsigned long, scudo::Chunk::Origin, unsigned long, bool)` | libc/kernel/vdso |
| 0.05 | GameThread | `pthread_getspecific` | scheduler/sync/waits |
| 0.05 | GameThread | `ps2_vu1_trace::detail::ensureInit()` | PS2 runtime other |
| 0.05 | GameThread | `ps2_e44_trace::storeArmed(unsigned int, unsigned int)` | PS2 runtime other |
| 0.05 | GameThread | `__vsnprintf_chk` | other |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3198(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3180(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ed0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2990(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1490(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1468(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0ab0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2dd0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2dc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2860(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2850(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2848(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2838(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2800(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2378(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1480(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1478(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1418(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0740(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0730(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0728(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0610(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0588(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0580(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0550(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0530(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.05 | GameThread | `VU1Interpreter::queueViWrite(unsigned char, int, unsigned int)` | VU1 interpreter/other |
| 0.05 | GameThread | `(anonymous namespace)::inRange(unsigned int, unsigned long, unsigned long, char const*, unsigned int)` | other |
| 0.04 | GsWorker | `std::__ndk1::mutex::unlock()` | scheduler/sync/waits |
| 0.04 | GsWorker | `ParallelGS::GSInterface::drawing_kick_update_texture(ParallelGS::GSInterface::FBFeedbackMode, muglm::tvec4<int> const&, muglm::tvec4<int> const&)` | paraLLEl CPU submit |
| 0.04 | GameThread | `syscall` | libc/kernel/vdso |
| 0.04 | GameThread | `sub_003CD878_0x3cd878(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_0038EC40_0x38ec40(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00387EC0_0x387ec0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_0036B158_0x36b158(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00368660_0x368660(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00334888_0x334888(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002F0548_0x2f0548(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002EDB20_0x2edb20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002ED490_0x2ed490(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002E5920_0x2e5920(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002DF920_0x2df920(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00292B48_0x292b48(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_002306A8_0x2306a8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_0022A128_0x22a128(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00229FC8_0x229fc8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_0016D320_0x16d320(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00166F90_0x166f90(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_001635F8_0x1635f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00162568_0x162568(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `sub_00122898_0x122898(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.04 | GameThread | `std::__ndk1::deque<GsCommand, std::__ndk1::allocator<GsCommand>>::push_back(GsCommand&&)` | other |
| 0.04 | GameThread | `std::__ndk1::__wrap_iter<unsigned char*> std::__ndk1::vector<unsigned char, std::__ndk1::allocator<unsigned char>>::__insert_with_size[abi:ne190000]<unsigned char const*, unsigned char const*>(std::__ndk1::__wrap_iter<unsigned char const*>, unsigned char const*, unsigned char const*, long)` | other |
| 0.04 | GameThread | `ps2_vu1_entry_trace::detail::ensureInit()` | PS2 runtime other |
| 0.04 | GameThread | `ps2_snd_spike::mixTickLocked(ps2_snd_spike::State&, unsigned char const*, unsigned char const*)` | SND/audio |
| 0.04 | GameThread | `ps2_e15::Trace::end(unsigned long, bool)` | PS2 runtime other |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3358(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f31c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f31b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f31a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2998(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2988(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2940(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2500(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1dd0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<17692172933381506641ul>::f14b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2dd8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2dc8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2840(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2810(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2400(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1560(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1558(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1490(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1470(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1448(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1410(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1390(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0778(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0578(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0520(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0518(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0510(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1738(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1638(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1620(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1618(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1610(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1608(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.04 | GameThread | `VU1Interpreter::lookupRecompProgram(unsigned char const*, unsigned int, PS2Memory*)` | VU1 interpreter/other |
| 0.04 | GameThread | `PS2Runtime::lookupFunction(unsigned int)` | PS2 runtime other |
| 0.04 | GameThread | `EeScheduler::run()` | scheduler/sync/waits |
| 0.04 | AAudio_1 | `(anonymous namespace)::audioCallback(void*, unsigned int)` | SND/audio |
| 0.03 | com.ps2x.runner | `@plt` | PLT |
| 0.03 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned int, bool)` | libc/kernel/vdso |
| 0.03 | GsWorker | `ps2x_gs_parallel::(anonymous namespace)::GSParallelBackend::ensureInit()` | paraLLEl CPU submit |
| 0.03 | GsWorker | `__memset_aarch64_nt` | __bzero/__memset zeroing |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe761a6b670]` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760bc8534]` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.03 | GsWorker | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.03 | GsWorker | `Vulkan::CommandBuffer::allocate_descriptor_offset(unsigned int, unsigned int&, unsigned int&)` | other |
| 0.03 | GsWorker | `ParallelGS::GSInterface::a_d_PRIM(unsigned long)` | paraLLEl CPU submit |
| 0.03 | GsWorker | `GS::updatePreferredDisplaySourceForDraw(GSPrimitiveBatch const&)` | GIF/GS packet handling |
| 0.03 | GsWorker | `GS::executeQueuedCommand(GsCommand&)` | GIF/GS packet handling |
| 0.03 | GsWorker | `@plt` | PLT |
| 0.03 | GameThread | `sub_0041CA70_0x41ca70(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003CE410_0x3ce410(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003CD590_0x3cd590(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003CCA08_0x3cca08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003C85D0_0x3c85d0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003B55F0_0x3b55f0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00397DF8_0x397df8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0038CA70_0x38ca70(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00386128_0x386128(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00368970_0x368970(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00364CD0_0x364cd0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_003645B8_0x3645b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00363C20_0x363c20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00362DE8_0x362de8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00333EF8_0x333ef8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0031A490_0x31a490(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00312C20_0x312c20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002F4DB8_0x2f4db8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002DDAB8_0x2ddab8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002DC168_0x2dc168(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002DABC8_0x2dabc8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002D8EA8_0x2d8ea8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002D4C08_0x2d4c08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002C0408_0x2c0408(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002B7908_0x2b7908(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002425C0_0x2425c0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0022C410_0x22c410(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0022A408_0x22a408(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_002200C0_0x2200c0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0021E1B0_0x21e1b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00162C78_0x162c78(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00129160_0x129160(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_0011EB98_0x11eb98(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00117FE0_0x117fe0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `sub_00100348_0x100348(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.03 | GameThread | `std::__ndk1::mutex::unlock()` | scheduler/sync/waits |
| 0.03 | GameThread | `ps2_e44_trace::detail::ensureInit()` | PS2 runtime other |
| 0.03 | GameThread | `ps2_e43_trace::h394CallArmed(unsigned int, unsigned int)` | PS2 runtime other |
| 0.03 | GameThread | `ps2_e15::enabled()` | PS2 runtime other |
| 0.03 | GameThread | `ps2_e15::Trace::Trace(char const*, unsigned long, unsigned char const*, R5900Context const*, unsigned int, unsigned int, int)` | PS2 runtime other |
| 0.03 | GameThread | `malloc` | libc/kernel/vdso |
| 0.03 | GameThread | `libunwind::LocalAddressSpace::getULEB128(unsigned long&, unsigned long)` | profiler unwind overhead |
| 0.03 | GameThread | `__strlen_chk` | other |
| 0.03 | GameThread | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.03 | GameThread | `__aarch64_swp2_acq` | libc/kernel/vdso |
| 0.03 | GameThread | `__aarch64_ldadd8_relax` | libc/kernel/vdso |
| 0.03 | GameThread | `[kernel.kallsyms][+ffffffe760bcd1b4]` | libc/kernel/vdso |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f31b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2f48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2f40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2aa8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2980(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2938(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2930(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2928(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2920(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2910(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2508(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1dc8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1be8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1938(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f17e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f16b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1688(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1480(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1478(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1348(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2df8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2df0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2db8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2830(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2820(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2808(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2398(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2390(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2388(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2370(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2368(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0c18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0c10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f20f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1550(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1458(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1450(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1420(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1400(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1398(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1388(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ec0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ea0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0788(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0770(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0760(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0620(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0600(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0508(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0500(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0490(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0330(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0188(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0180(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0168(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0158(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1730(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1708(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1700(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1698(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1690(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1688(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1680(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1678(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1658(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1630(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1600(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1588(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1580(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.03 | GameThread | `Ps2FastWrite32(unsigned char*, unsigned int, unsigned int)` | other |
| 0.03 | GameThread | `Ps2FastWrite128(unsigned char*, unsigned int, __Int64x2_t)` | other |
| 0.03 | GameThread | `PS2Memory::writeIORegister(unsigned int, unsigned int)::$_2::operator()(unsigned int, unsigned int) const` | EE runtime helpers |
| 0.03 | GameThread | `PS2Memory::submitGifPacket(GifPathId, unsigned char const*, unsigned int, bool, bool)` | EE runtime helpers |
| 0.03 | GameThread | `EeScheduler::publishSnapshot()` | scheduler/sync/waits |
| 0.02 | com.ps2x.runner | `__memset_aarch64_nt` | __bzero/__memset zeroing |
| 0.02 | GsWorker | `void ParallelGS::GSInterface::packed_XYZF<false>(void const*)` | paraLLEl CPU submit |
| 0.02 | GsWorker | `std::__ndk1::condition_variable::notify_all()` | scheduler/sync/waits |
| 0.02 | GsWorker | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::pushBlocks(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, unsigned int*, unsigned int)` | libc/kernel/vdso |
| 0.02 | GsWorker | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.02 | GsWorker | `pthread_getspecific` | scheduler/sync/waits |
| 0.02 | GsWorker | `libvulkan_freedreno.so[+9b5f7c]` | Vulkan driver CPU (Turnip) |
| 0.02 | GsWorker | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.02 | GsWorker | `__aarch64_swp2_acq` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e614]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760b0ef7c]` | libc/kernel/vdso |
| 0.02 | GsWorker | `[kernel.kallsyms][+ffffffe760829a08]` | libc/kernel/vdso |
| 0.02 | GsWorker | `ParallelGS::PageTracker::garbage_collect_texture_masked_handles(std::__ndk1::vector<ParallelGS::CachedTextureMasked, std::__ndk1::allocator<ParallelGS::CachedTextureMasked>>&)` | paraLLEl CPU submit |
| 0.02 | GsWorker | `ParallelGS::PageTracker::flush_if_memory_pressure()` | paraLLEl CPU submit |
| 0.02 | GsWorker | `ParallelGS::GSRenderer::emit_copy_vram(Vulkan::CommandBuffer&, unsigned int const*, unsigned int, bool)` | paraLLEl CPU submit |
| 0.02 | GsWorker | `ParallelGS::GSInterface::draw_is_degenerate()` | paraLLEl CPU submit |
| 0.02 | GsWorker | `NonPI::MutexLockWithTimeout(pthread_mutex_internal_t*, bool, timespec const*)` | scheduler/sync/waits |
| 0.02 | GsWorker | `GS::writeRegisterUnlocked(unsigned char, unsigned long)` | GIF/GS packet handling |
| 0.02 | GsWorker | `GS::recordGifTagDebugEventUnlocked(unsigned int, unsigned int, unsigned char, unsigned int)` | GIF/GS packet handling |
| 0.02 | GameThread | `sub_003E5928_0x3e5928(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003CBB78_0x3cbb78(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003AA028_0x3aa028(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003A8668_0x3a8668(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00395288_0x395288(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00394ED0_0x394ed0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00391CB0_0x391cb0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0038D968_0x38d968(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0038D690_0x38d690(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0038CE20_0x38ce20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003889F0_0x3889f0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003885E0_0x3885e0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0037D968_0x37d968(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00374B38_0x374b38(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0036C790_0x36c790(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0036AE20_0x36ae20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00368170_0x368170(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_003668F8_0x3668f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00364050_0x364050(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0035FE10_0x35fe10(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00356198_0x356198(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00353AC0_0x353ac0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0034FED8_0x34fed8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00335960_0x335960(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00332DB8_0x332db8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00326EB0_0x326eb0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00325450_0x325450(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00321298_0x321298(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0031B310_0x31b310(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00316F00_0x316f00(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00311318_0x311318(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00310948_0x310948(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00310640_0x310640(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00310200_0x310200(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002F5400_0x2f5400(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002F1A08_0x2f1a08(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002F00A0_0x2f00a0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002E4F50_0x2e4f50(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002E3478_0x2e3478(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002E1A80_0x2e1a80(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002E1120_0x2e1120(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002DDD30_0x2ddd30(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002AB6B0_0x2ab6b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002A4E88_0x2a4e88(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00293DC0_0x293dc0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00293740_0x293740(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00285930_0x285930(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_002429B0_0x2429b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0022C1B0_0x22c1b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0021ED48_0x21ed48(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_001F1B30_0x1f1b30(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00176DA8_0x176da8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_001668B8_0x1668b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_001662A0_0x1662a0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00165938_0x165938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0013F178_0x13f178(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0013CCF0_0x13ccf0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0013C948_0x13c948(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00131620_0x131620(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00128AF0_0x128af0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00127848_0x127848(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_001211F8_0x1211f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00120378_0x120378(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0011FA10_0x11fa10(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0011B3F8_0x11b3f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00117C28_0x117c28(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00112338_0x112338(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_0010F560_0x10f560(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `sub_00107888_0x107888(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.02 | GameThread | `std::__ndk1::condition_variable::notify_one()` | scheduler/sync/waits |
| 0.02 | GameThread | `snprintf(char*, unsigned long pass_object_size1, char const*, ...)` | other |
| 0.02 | GameThread | `scudo_malloc` | libc/kernel/vdso |
| 0.02 | GameThread | `scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::popBlocksImpl(scudo::SizeClassAllocatorLocalCache<scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>>*, unsigned long, scudo::SizeClassAllocator64<scudo::PrimaryConfig<scudo::AndroidNormalConfig>>::RegionInfo*, unsigned int*, unsigned short)` | libc/kernel/vdso |
| 0.02 | GameThread | `ps2_uv1_vif_fmt::note(unsigned long, unsigned char, bool, unsigned int, unsigned int, unsigned int, bool, unsigned char)` | PS2 runtime other |
| 0.02 | GameThread | `ps2_uv1_dma_stall::noteTag(unsigned long, unsigned int, unsigned int)` | PS2 runtime other |
| 0.02 | GameThread | `ps2_snd_spu::Spu::mixVoice(ps2_snd_spu::Voice&, int&, int&)` | SND/audio |
| 0.02 | GameThread | `ps2_e44_trace::trackLastWriter(unsigned char const*, R5900Context const*, unsigned int, unsigned int, char const*, char const*)` | PS2 runtime other |
| 0.02 | GameThread | `operator new(unsigned long)` | other |
| 0.02 | GameThread | `libunwind::CFI_Parser<libunwind::LocalAddressSpace>::parseFDEInstructions(libunwind::LocalAddressSpace&, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::FDE_Info const&, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::CIE_Info const&, unsigned long, int, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::PrologInfo*)` | profiler unwind overhead |
| 0.02 | GameThread | `libunwind::CFI_Parser<libunwind::LocalAddressSpace>::parseCIE(libunwind::LocalAddressSpace&, unsigned long, libunwind::CFI_Parser<libunwind::LocalAddressSpace>::CIE_Info*)` | profiler unwind overhead |
| 0.02 | GameThread | `free` | libc/kernel/vdso |
| 0.02 | GameThread | `__cxxabiv1::readEncodedPointer(unsigned char const**, unsigned char, unsigned long)` | other |
| 0.02 | GameThread | `[kernel.kallsyms][+ffffffe761a8e614]` | libc/kernel/vdso |
| 0.02 | GameThread | `[kernel.kallsyms][+ffffffe760d8565c]` | libc/kernel/vdso |
| 0.02 | GameThread | `[kernel.kallsyms][+ffffffe760b0d798]` | libc/kernel/vdso |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3bb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3ba0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3288(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3280(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3278(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3068(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3058(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3020(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3000(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ff8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2fb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2fa8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2df8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2dc8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2db8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2db0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2d70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ad0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ac8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ac0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ab8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ab0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2978(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2970(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2918(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2908(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f26f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2648(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2638(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2630(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2608(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2590(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2578(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2570(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2540(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2510(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f24b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2498(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2160(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2158(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2130(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2118(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2100(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f20f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f20f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1e20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1e18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1c10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1bf0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1ab8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1960(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1940(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1808(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f17c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1730(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1720(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1710(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f16d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f16a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1440(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1428(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1388(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1350(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1340(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1330(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1328(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0be0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0af8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0940(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0928(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0920(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<17692172933381506641ul>::f08e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3b00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f39b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3870(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3748(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3740(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2de0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2db0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2da8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2da0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2cf8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2ca0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2c88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2c80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2c78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2878(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2858(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2828(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2818(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2798(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2790(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2780(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2778(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2758(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2740(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2738(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2730(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2710(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2638(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f23a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2380(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2360(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0c20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2448(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2428(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f22f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2260(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2240(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2108(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1fb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1ee0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1890(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f14a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1488(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1460(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1408(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ec8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0eb8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0de8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0dc8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0dc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f07b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f07b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f07a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f07a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0798(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0780(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0768(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0758(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0748(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0590(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0528(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0498(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0488(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0470(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0458(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0328(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0318(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0218(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0210(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0208(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0200(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f01b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0198(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0190(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0178(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0170(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0160(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0100(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1800(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1780(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1748(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1740(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1728(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1710(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f16b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1660(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1650(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1598(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1590(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.02 | GameThread | `VU1Interpreter::directFlagMap(unsigned char const*, unsigned int, bool)` | VU1 interpreter/other |
| 0.02 | GameThread | `PS2Runtime::hasFunction(unsigned int) const` | PS2 runtime other |
| 0.02 | GameThread | `PS2Runtime::eeCheckpointDue(unsigned int)` | PS2 runtime other |
| 0.02 | GameThread | `PS2Runtime::Store128(unsigned char*, R5900Context*, unsigned int, __Int64x2_t)` | EE runtime helpers |
| 0.02 | GameThread | `PS2Memory::write64(unsigned int, unsigned long)` | EE runtime helpers |
| 0.02 | GameThread | `PS2Memory::write128(unsigned int, __Int64x2_t)` | EE runtime helpers |
| 0.02 | GameThread | `PS2Memory::read32(unsigned int)` | EE runtime helpers |
| 0.02 | GameThread | `GifArbiter::submit(GifPathId, unsigned char const*, unsigned int, bool)` | GIF/GS packet handling |
| 0.02 | GameThread | `GifArbiter::drain()` | GIF/GS packet handling |
| 0.02 | GameThread | `GS::noteGifPath(GifPathId)` | GIF/GS packet handling |
| 0.02 | GameThread | `EeScheduler::processDueDeadlines()` | scheduler/sync/waits |
| 0.02 | AAudio_1 | `aaudio::flowgraph::Limiter::onProcess(int)` | SND/audio |
| 0.01 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.01 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe760829a08]` | libc/kernel/vdso |
| 0.01 | com.ps2x.runner | `!!!0000!58c4cf89d3544eaf0d40972d4ff12d!a9ee82cd83!` | other |
| 0.01 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<true, false, true, 2u>()` | paraLLEl CPU submit |
| 0.01 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<false, true, false, 3u>()` | paraLLEl CPU submit |
| 0.01 | GsWorker | `void ParallelGS::GSInterface::drawing_kick<(ParallelGS::PRIMType)5>(bool)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `syscall` | libc/kernel/vdso |
| 0.01 | GsWorker | `std::__ndk1::recursive_mutex::unlock()` | scheduler/sync/waits |
| 0.01 | GsWorker | `std::__ndk1::mutex::lock()` | scheduler/sync/waits |
| 0.01 | GsWorker | `ps2_e7::packet(unsigned long, char const*, unsigned char const*, unsigned int, bool, unsigned long, unsigned int)` | PS2 runtime other |
| 0.01 | GsWorker | `__aarch64_cas4_acq` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe7611d4f98]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760be4d3c]` | libc/kernel/vdso |
| 0.01 | GsWorker | `[kernel.kallsyms][+ffffffe760bc81dc]` | libc/kernel/vdso |
| 0.01 | GsWorker | `Vulkan::CommandBuffer::flush_compute_state(bool)` | other |
| 0.01 | GsWorker | `ParallelGS::PageTracker::register_short_term_cached_texture(ParallelGS::PageRect const*, unsigned int, unsigned long)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::PageTracker::register_accessed_cache_pages(unsigned int)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::GSRenderer::flush_rendering(ParallelGS::RenderPass const&)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::GSRenderer::create_cached_texture(ParallelGS::TextureDescriptor const&)` | paraLLEl CPU submit |
| 0.01 | GsWorker | `ParallelGS::GSInterface::flush(unsigned int, ParallelGS::FlushReason)` | paraLLEl CPU submit |
| 0.01 | GameThread | `sub_00418EF8_0x418ef8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00411FD8_0x411fd8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003E6574_0x3e6574(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003D7EC8_0x3d7ec8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003D5508_0x3d5508(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003D5128_0x3d5128(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003CDE68_0x3cde68(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003CD518_0x3cd518(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003CD2B0_0x3cd2b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003CD260_0x3cd260(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003CCF90_0x3ccf90(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003C9E50_0x3c9e50(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003C2A50_0x3c2a50(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003C25E0_0x3c25e0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003C1638_0x3c1638(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003BAA00_0x3baa00(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003A9D60_0x3a9d60(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003A9258_0x3a9258(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0039ECB0_0x39ecb0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00389840_0x389840(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00382760_0x382760(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00371688_0x371688(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003710D0_0x3710d0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0036AC00_0x36ac00(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00334680_0x334680(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003309D8_0x3309d8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00329DC8_0x329dc8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0031B178_0x31b178(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0031A6B8_0x31a6b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00317348_0x317348(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003135B0_0x3135b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00312490_0x312490(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_003123C0_0x3123c0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002F6518_0x2f6518(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002F03C8_0x2f03c8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002EF950_0x2ef950(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002EF6D0_0x2ef6d0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002EECF0_0x2eecf0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002ED1D0_0x2ed1d0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E66B8_0x2e66b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E4678_0x2e4678(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E39D8_0x2e39d8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E3130_0x2e3130(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E1F70_0x2e1f70(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002E1598_0x2e1598(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002DE058_0x2de058(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002B4C38_0x2b4c38(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002AFC88_0x2afc88(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002AEFA8_0x2aefa8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002AC868_0x2ac868(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002AB958_0x2ab958(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002AB828_0x2ab828(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002A43B8_0x2a43b8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00293168_0x293168(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0028C8C8_0x28c8c8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002898A8_0x2898a8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_002883B0_0x2883b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0026F4A8_0x26f4a8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0026A638_0x26a638(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00244880_0x244880(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0022C078_0x22c078(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0022A5A0_0x22a5a0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0022A368_0x22a368(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00229530_0x229530(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_001F1840_0x1f1840(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_001A39F0_0x1a39f0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00164878_0x164878(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_001641C0_0x1641c0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00163010_0x163010(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00161AB0_0x161ab0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0015E460_0x15e460(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0014DC80_0x14dc80(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00125B18_0x125b18(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00125228_0x125228(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00121950_0x121950(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00120F20_0x120f20(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00115D48_0x115d48(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00112FB0_0x112fb0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_001125C0_0x1125c0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_0010DBF0_0x10dbf0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00106F78_0x106f78(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00104E70_0x104e70(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_00101B60_0x101b60(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `sub_001013A8_0x1013a8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.01 | GameThread | `std::__ndk1::pair<std::__ndk1::__hash_iterator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<unsigned int, unsigned int>, void*>*>, bool> std::__ndk1::__hash_table<std::__ndk1::__hash_value_type<unsigned int, unsigned int>, std::__ndk1::__unordered_map_hasher<unsigned int, std::__ndk1::__hash_value_type<unsigned int, unsigned int>, std::__ndk1::hash<unsigned int>, std::__ndk1::equal_to<unsigned int>, true>, std::__ndk1::__unordered_map_equal<unsigned int, std::__ndk1::__hash_value_type<unsigned int, unsigned int>, std::__ndk1::equal_to<unsigned int>, std::__ndk1::hash<unsigned int>, true>, std::__ndk1::allocator<std::__ndk1::__hash_value_type<unsigned int, unsigned int>>>::__emplace_unique_key_args<unsigned int, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>, std::__ndk1::tuple<>>(unsigned int const&, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>&&, std::__ndk1::tuple<>&&)` | other |
| 0.01 | GameThread | `scudo::MapAllocatorCache<scudo::SecondaryConfig<scudo::AndroidNormalConfig>::CacheConfig>::retrieve(scudo::Options, unsigned long, unsigned long, unsigned long, scudo::LargeBlock::Header**, bool*)` | libc/kernel/vdso |
| 0.01 | GameThread | `ps2_stubs::(anonymous namespace)::canCopyAddressRange(unsigned char const*, unsigned int, unsigned int)` | PS2 runtime other |
| 0.01 | GameThread | `ps2_rr1::ev(unsigned long, char const*, ...)` | PS2 runtime other |
| 0.01 | GameThread | `libunwind::DwarfInstructions<libunwind::LocalAddressSpace, libunwind::Registers_arm64>::stepWithDwarf(libunwind::LocalAddressSpace&, unsigned long, unsigned long, libunwind::Registers_arm64&, bool&, bool)` | profiler unwind overhead |
| 0.01 | GameThread | `clock_gettime` | libc/kernel/vdso |
| 0.01 | GameThread | `__aarch64_ldadd4_rel` | libc/kernel/vdso |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3ba8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3b48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f32a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3270(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f30c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3080(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3078(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3060(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3050(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f3018(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2fa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2f18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2e18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2de8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2dc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2d80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2d78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2d60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ae8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ae0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2ad8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f29b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2968(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2960(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2950(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2708(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f26f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f26e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f26e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2640(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2620(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2600(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f25a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2598(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2588(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2580(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2568(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2560(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2558(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2530(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2478(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2428(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2360(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2320(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f22e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2168(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2148(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2140(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2138(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2128(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2120(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f2110(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1f58(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1e10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1e00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1df8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1de0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1dc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1db8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1ce0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1cc8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1cc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1ca8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1c98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1c70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1c08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1bf8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1bd8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1b18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1ab0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1aa8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f19a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1958(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1948(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1928(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1920(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f18a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1890(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1800(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f17e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f17d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1788(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1778(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1768(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1728(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1718(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f16f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1698(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1690(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1680(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1668(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1630(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1448(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1438(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1430(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1408(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f13a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1398(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1390(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1338(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f1320(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f12f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0c80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0c70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0b00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f09a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0998(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0970(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0960(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0958(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0950(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0938(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0930(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0918(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0910(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f0908(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<17692172933381506641ul>::f08f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3e00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3df0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3db0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3cf8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3c70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3c60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3c50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3c48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3be0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3bb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3b20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3b18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3b08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3aa0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3a98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3a80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3a30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3a18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f39e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f39d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f39c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3998(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3930(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3928(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f38f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f38e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3898(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3878(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3858(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3850(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f37c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3750(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3728(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3708(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f30a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f30a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f3090(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2f28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2eb0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2e50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2d00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2c98(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2c70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2870(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f27a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2768(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2748(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f26a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2680(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2628(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f2620(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0c28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0c08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12951700169819473931ul>::f0660(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2440(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2438(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2410(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f23f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2300(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f22f8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2250(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2238(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2230(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2228(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2220(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21c8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21a8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f21a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2198(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2120(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2118(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2100(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2068(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2060(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2030(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2018(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f2010(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1fd8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1fd0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1fc0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1fb8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1f00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1ef8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1ef0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1ec8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e80(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1e00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1dd8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1dd0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1da8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d88(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1d10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b68(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1b10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a60(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a48(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a18(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1a00(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1978(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1968(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1958(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f18d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f18b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f18b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1888(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1808(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1800(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f17e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f15a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1590(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1570(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1568(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1498(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1438(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f13e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1380(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1378(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1370(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f1368(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f0b28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<12499688582289950957ul>::f0ae0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ee8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ee0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ed0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0ea8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e78(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e50(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e40(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e38(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e30(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e20(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0e08(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0db8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0d90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0d70(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a28(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0a10(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f09f0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0968(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0938(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0790(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f05d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0570(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f04b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0480(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0478(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0468(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0460(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0448(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0310(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0238(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0150(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0140(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0128(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f0120(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f00e8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f00c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11917748289753363281ul>::f00b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f18d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f18d0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f18c0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1828(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17e0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17d8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17b0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f17a0(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1770(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1768(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1758(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1718(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1668(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1648(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1640(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f15b8(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f1578(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1RecompImage<11679184380082170532ul>::f0b90(VU1Interpreter&, VU1Interpreter::RunContext&)` | VU1 generated pairs |
| 0.01 | GameThread | `VU1Interpreter::startXgkick(unsigned int)` | VU1 interpreter/other |
| 0.01 | GameThread | `VU1Interpreter::queueFcset(unsigned int)` | VU1 interpreter/other |
| 0.01 | GameThread | `Ps2FastWrite64(unsigned char*, unsigned int, unsigned long)` | other |
| 0.01 | GameThread | `PS2Runtime::Store32(unsigned char*, R5900Context*, unsigned int, unsigned int)` | EE runtime helpers |
| 0.01 | GameThread | `PS2Runtime::Load32(unsigned char*, R5900Context*, unsigned int)` | EE runtime helpers |
| 0.01 | GameThread | `PS2Runtime::Load128(unsigned char*, R5900Context*, unsigned int)` | EE runtime helpers |
| 0.01 | GameThread | `PS2Memory::write32(unsigned int, unsigned int)` | EE runtime helpers |
| 0.01 | GameThread | `PS2Memory::releaseOneMaskedPath3Packet()` | EE runtime helpers |
| 0.01 | GameThread | `PS2Memory::read128(unsigned int)` | EE runtime helpers |
| 0.01 | GameThread | `GsWorker::endBatch()` | other |
| 0.01 | GameThread | `EeScheduler::processPendingEvents()` | scheduler/sync/waits |
| 0.01 | AAudio_1 | `aaudio::flowgraph::FlowGraphPortFloatOutput::pullData(long, int)` | SND/audio |
