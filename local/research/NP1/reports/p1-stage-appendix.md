rows=122 covered=87.04%
| Stage | Self % |
|---|---|
| VU1 execute | 39.13% |
| libc/kernel/vdso | 23.61% |
| VU1 hazard bookkeeping | 15.99% |
| PLT | 2.73% |
| GIF/GS packet handling | 1.23% |
| guest code | 1.18% |
| paraLLEl CPU submit | 0.83% |
| VIF1/DMA | 0.55% |
| other | 0.48% |
| scheduler/sync/waits | 0.47% |
| profiler unwind overhead | 0.35% |
| EE runtime helpers | 0.32% |
| PS2 runtime other | 0.17% |

| Self % | Thread | Symbol | Stage |
|---|---|---|---|
| 10.42 | GameThread | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 8.98 | GameThread | `VU1Interpreter::commitReadyPipelines()` | VU1 hazard bookkeeping |
| 6.35 | GameThread | `VU1Interpreter::execUpper(unsigned int)` | VU1 execute |
| 5.25 | GameThread | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | VU1 hazard bookkeeping |
| 3.89 | GameThread | `__memset_aarch64_nt` | libc/kernel/vdso |
| 3.60 | GameThread | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 3.58 | GameThread | `VU1Interpreter::calculateFmacExactResults(unsigned char, double*) const` | VU1 execute |
| 3.43 | GameThread | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | VU1 execute |
| 2.73 | GameThread | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | VU1 execute |
| 2.58 | GameThread | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 2.57 | GameThread | `@plt` | PLT |
| 2.48 | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | VU1 execute |
| 2.25 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e860]` | libc/kernel/vdso |
| 2.16 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 1.76 | GameThread | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | VU1 hazard bookkeeping |
| 1.39 | GameThread | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | VU1 execute |
| 1.31 | GsWorker | `[kernel.kallsyms][+ffffffe760a47efc]` | libc/kernel/vdso |
| 1.15 | com.ps2x.runner | `clock_gettime` | libc/kernel/vdso |
| 1.15 | GameThread | `VU1Interpreter::broadcast(float const*, unsigned char)` | VU1 execute |
| 1.00 | GameThread | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | VU1 execute |
| 0.93 | GsWorker | `[kernel.kallsyms][+ffffffe760cfb750]` | libc/kernel/vdso |
| 0.85 | com.ps2x.runner | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.75 | GsWorker | `[kernel.kallsyms][+ffffffe760a21688]` | libc/kernel/vdso |
| 0.73 | GsWorker | `[kernel.kallsyms][+ffffffe760a21680]` | libc/kernel/vdso |
| 0.70 | GameThread | `VU1Interpreter::applyDest(float*, float const*, unsigned char)` | VU1 execute |
| 0.61 | GsWorker | `[kernel.kallsyms][+ffffffe760d2cbf8]` | libc/kernel/vdso |
| 0.55 | GameThread | `PS2Memory::processVIF1DataImpl(unsigned char const*, unsigned int)` | VIF1/DMA |
| 0.43 | GameThread | `VU1Interpreter::progressXgkick()` | VU1 execute |
| 0.42 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a0]` | libc/kernel/vdso |
| 0.40 | GameThread | `VU1Interpreter::applyFmacDest(float*, float*, unsigned char)` | VU1 execute |
| 0.39 | GameThread | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.39 | GameThread | `VU1Interpreter::applyFmacDestAcc(float*, unsigned char)` | VU1 execute |
| 0.38 | GsWorker | `[kernel.kallsyms][+ffffffe760a2168c]` | libc/kernel/vdso |
| 0.37 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<false, false, false, 3u>()` | paraLLEl CPU submit |
| 0.37 | GameThread | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.34 | GsWorker | `GS::writeRegisterPacked(unsigned char, unsigned long, unsigned long)` | GIF/GS packet handling |
| 0.31 | GsWorker | `[kernel.kallsyms][+ffffffe760b99edc]` | libc/kernel/vdso |
| 0.29 | GameThread | `__vfprintf` | libc/kernel/vdso |
| 0.27 | GsWorker | `GS::vertexKick(bool)` | GIF/GS packet handling |
| 0.26 | GsWorker | `[kernel.kallsyms][+ffffffe760b98830]` | libc/kernel/vdso |
| 0.26 | GsWorker | `GS::buildDrawBatch(int) const` | GIF/GS packet handling |
| 0.26 | GameThread | `libunwind::findUnwindSectionsByPhdr(dl_phdr_info*, unsigned long, void*)` | profiler unwind overhead |
| 0.25 | GsWorker | `[kernel.kallsyms][+ffffffe761a79608]` | libc/kernel/vdso |
| 0.25 | GameThread | `sub_0037E120_0x37e120(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.25 | GameThread | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.22 | GameThread | `[kernel.kallsyms][+ffffffe761a8e664]` | libc/kernel/vdso |
| 0.22 | GameThread | `VU1Interpreter::decodeLowerUsage(unsigned int) const` | VU1 execute |
| 0.21 | GameThread | `VU1Interpreter::queueStore(unsigned int, unsigned int const*, unsigned char)` | VU1 execute |
| 0.20 | GsWorker | `[kernel.kallsyms][+ffffffe760a15520]` | libc/kernel/vdso |
| 0.19 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c84]` | libc/kernel/vdso |
| 0.19 | GsWorker | `[kernel.kallsyms][+ffffffe760a21684]` | libc/kernel/vdso |
| 0.17 | com.ps2x.runner | `!!!0000!a0d82c13dd4b4e4f31b6cd30a2cb0d!a9ee82cd83!` | other |
| 0.17 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e6e0]` | libc/kernel/vdso |
| 0.17 | GsWorker | `[kernel.kallsyms][+ffffffe7611d5040]` | libc/kernel/vdso |
| 0.16 | GsWorker | `@plt` | PLT |
| 0.16 | GameThread | `VU1Interpreter::decodeUpperUsage(unsigned int) const` | VU1 execute |
| 0.15 | GsWorker | `[kernel.kallsyms][+ffffffe761a79580]` | libc/kernel/vdso |
| 0.15 | GameThread | `__sfvwrite` | libc/kernel/vdso |
| 0.14 | GsWorker | `void ParallelGS::GSInterface::packed_XYZ<false, true, (ParallelGS::PRIMType)4>(void const*)` | paraLLEl CPU submit |
| 0.14 | GsWorker | `[kernel.kallsyms][+ffffffe761a7ae44]` | libc/kernel/vdso |
| 0.14 | GsWorker | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.14 | GameThread | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.14 | GameThread | `VU1Interpreter::resetScheduler()` | VU1 execute |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c20]` | libc/kernel/vdso |
| 0.13 | GsWorker | `GS::recordDrawDebugEventUnlocked(int)` | GIF/GS packet handling |
| 0.13 | GsWorker | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.13 | GameThread | `sub_00376938_0x376938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.12 | GsWorker | `[kernel.kallsyms][+ffffffe761a79560]` | libc/kernel/vdso |
| 0.12 | GsWorker | `[kernel.kallsyms][+ffffffe760855968]` | libc/kernel/vdso |
| 0.12 | GameThread | `sub_0032E100_0x32e100(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.12 | GameThread | `__emutls_get_address` | other |
| 0.11 | GameThread | `sub_002E8938_0x2e8938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.11 | GameThread | `std::__ndk1::pair<std::__ndk1::__hash_iterator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, void*>*>, bool> std::__ndk1::__hash_table<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::__unordered_map_hasher<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::hash<unsigned int>, std::__ndk1::equal_to<unsigned int>, true>, std::__ndk1::__unordered_map_equal<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::equal_to<unsigned int>, std::__ndk1::hash<unsigned int>, true>, std::__ndk1::allocator<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>>>::__emplace_unique_key_args<unsigned int, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>, std::__ndk1::tuple<>>(unsigned int const&, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>&&, std::__ndk1::tuple<>&&)` | PS2 runtime other |
| 0.11 | GameThread | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.11 | GameThread | `VU1Interpreter::decodeInstructionPair(unsigned char const*, unsigned int) const` | VU1 execute |
| 0.10 | GsWorker | `void ParallelGS::GSInterface::drawing_kick<(ParallelGS::PRIMType)4>(bool)` | paraLLEl CPU submit |
| 0.10 | GsWorker | `__emutls_get_address` | other |
| 0.10 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a8]` | libc/kernel/vdso |
| 0.10 | GameThread | `sub_0022ADD8_0x22add8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.10 | GameThread | `[kernel.kallsyms][+ffffffe761a6b788]` | libc/kernel/vdso |
| 0.10 | GameThread | `VU1Interpreter::readBranchVi(unsigned char) const` | VU1 execute |
| 0.10 | GameThread | `PS2Memory::advanceEeTimers(unsigned long)` | EE runtime helpers |
| 0.09 | com.ps2x.runner | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.09 | GsWorker | `[kernel.kallsyms][+ffffffe760cf8c1c]` | libc/kernel/vdso |
| 0.09 | GsWorker | `ParallelGS::GSInterface::update_color_feedback_state()` | paraLLEl CPU submit |
| 0.09 | GameThread | `ps2DiagWatchEnabled()` | other |
| 0.09 | GameThread | `[linker]do_dl_iterate_phdr(int (*)(dl_phdr_info*, unsigned long, void*), void*)` | profiler unwind overhead |
| 0.09 | GameThread | `[kernel.kallsyms][+ffffffe760bcd1b4]` | libc/kernel/vdso |
| 0.09 | GameThread | `PS2Runtime::dispatchGuestBranch(unsigned char*, R5900Context*, unsigned int, unsigned int, unsigned int, PS2Runtime::GuestBranchKind, char const*)` | EE runtime helpers |
| 0.08 | com.ps2x.runner | `WaitTime` | scheduler/sync/waits |
| 0.08 | GsWorker | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.08 | GameThread | `sub_001E9A30_0x1e9a30(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.08 | GameThread | `pthread_mutex_lock` | scheduler/sync/waits |
| 0.08 | GameThread | `VU1Interpreter::microAddressMask() const` | VU1 execute |
| 0.08 | GameThread | `PS2Runtime::executeVU0Microprogram(unsigned char*, R5900Context*, unsigned int)` | EE runtime helpers |
| 0.08 | GameThread | `EeScheduler::accountCycles(unsigned int)` | scheduler/sync/waits |
| 0.07 | GsWorker | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe761a83a5c]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760dd7868]` | libc/kernel/vdso |
| 0.07 | GsWorker | `ParallelGS::GSInterface::gif_transfer(unsigned int, void const*, unsigned long)` | paraLLEl CPU submit |
| 0.07 | GameThread | `sub_0038B0F8_0x38b0f8(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `sub_0037A430_0x37a430(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `sub_002BCBD0_0x2bcbd0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `sub_0013D818_0x13d818(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.07 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.07 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::deallocate(void*, scudo::Chunk::Origin, unsigned long, unsigned long)` | libc/kernel/vdso |
| 0.06 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.06 | GsWorker | `void ParallelGS::GSInterface::packed_STQRGBAXYZ<true, (ParallelGS::PRIMType)4, 1>(void const*, unsigned int)` | paraLLEl CPU submit |
| 0.06 | GsWorker | `ps2_gfx_stats::detail::ensureInit()` | PS2 runtime other |
| 0.06 | GsWorker | `__aarch64_ldadd8_relax` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e614]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a79558]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe7611d4f98]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760d86994]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.06 | GameThread | `sub_0022A830_0x22a830(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int, unsigned int, unsigned int, unsigned int)` | VU1 execute |
| 0.05 | GsWorker | `GS::recordRegisterDebugEventUnlocked(unsigned char, unsigned long)` | GIF/GS packet handling |
| 0.05 | GameThread | `sub_0030F2B0_0x30f2b0(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.05 | GameThread | `scudo::HybridMutex::tryLock()` | scheduler/sync/waits |
| 0.05 | GameThread | `PS2Memory::translateAddress(unsigned int)` | EE runtime helpers |
| 0.05 | GameThread | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
