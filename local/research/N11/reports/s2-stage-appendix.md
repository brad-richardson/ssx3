rows=98 covered=92.11%
| Stage | Self % |
|---|---|
| VU1 hazard bookkeeping | 40.92% |
| VU1 execute | 28.17% |
| libc/kernel/vdso | 14.53% |
| PLT | 4.94% |
| GIF/GS packet handling | 0.80% |
| scheduler/sync/waits | 0.60% |
| EE runtime helpers | 0.53% |
| guest code | 0.38% |
| paraLLEl CPU submit | 0.36% |
| VIF1/DMA | 0.30% |
| other | 0.30% |
| profiler unwind overhead | 0.14% |
| PS2 runtime other | 0.14% |

| Self % | Thread | Symbol | Stage |
|---|---|---|---|
| 24.96 | GameThread | `VU1Interpreter::commitReadyPipelines()` | VU1 hazard bookkeeping |
| 12.73 | GameThread | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | VU1 hazard bookkeeping |
| 7.34 | GameThread | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 4.84 | GameThread | `@plt` | PLT |
| 3.80 | GameThread | `VU1Interpreter::execUpper(unsigned int)` | VU1 execute |
| 3.46 | GameThread | `VU1Interpreter::normalizeOperand(float) const` | VU1 execute |
| 3.23 | GameThread | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | VU1 hazard bookkeeping |
| 2.44 | GameThread | `VU1Interpreter::calculateFmacExactResult(unsigned int, double&) const` | VU1 execute |
| 2.28 | GameThread | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 2.02 | GameThread | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | VU1 execute |
| 1.87 | GameThread | `__memset_aarch64_nt` | libc/kernel/vdso |
| 1.66 | GameThread | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | VU1 execute |
| 1.50 | GameThread | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | VU1 execute |
| 1.33 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e860]` | libc/kernel/vdso |
| 1.31 | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | VU1 execute |
| 1.23 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 1.13 | GameThread | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | VU1 execute |
| 1.12 | GameThread | `VU1Interpreter::progressXgkick()` | VU1 execute |
| 0.99 | com.ps2x.runner | `clock_gettime` | libc/kernel/vdso |
| 0.79 | GameThread | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | VU1 execute |
| 0.78 | GsWorker | `[kernel.kallsyms][+ffffffe760a47efc]` | libc/kernel/vdso |
| 0.75 | com.ps2x.runner | `__kernel_clock_gettime` | libc/kernel/vdso |
| 0.50 | GsWorker | `[kernel.kallsyms][+ffffffe760a21688]` | libc/kernel/vdso |
| 0.48 | GsWorker | `[kernel.kallsyms][+ffffffe760cfb750]` | libc/kernel/vdso |
| 0.45 | GsWorker | `[kernel.kallsyms][+ffffffe760a21680]` | libc/kernel/vdso |
| 0.41 | GameThread | `PS2Memory::advanceEeTimers(unsigned long)` | EE runtime helpers |
| 0.30 | GameThread | `[kernel.kallsyms][+ffffffe760a2784c]` | libc/kernel/vdso |
| 0.30 | GameThread | `PS2Memory::processVIF1Data(unsigned char const*, unsigned int)` | VIF1/DMA |
| 0.28 | GameThread | `VU1Interpreter::applyFmacDestAcc(float*, unsigned char)` | VU1 execute |
| 0.27 | GsWorker | `[kernel.kallsyms][+ffffffe760d2cbf8]` | libc/kernel/vdso |
| 0.26 | GameThread | `EeScheduler::accountCycles(unsigned int)` | scheduler/sync/waits |
| 0.25 | GsWorker | `[kernel.kallsyms][+ffffffe760a2168c]` | libc/kernel/vdso |
| 0.25 | GameThread | `VU1Interpreter::applyFmacDest(float*, float*, unsigned char)` | VU1 execute |
| 0.23 | GsWorker | `GS::buildDrawBatch(int) const` | GIF/GS packet handling |
| 0.22 | GameThread | `sub_00416810_0x416810(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.21 | GsWorker | `void ParallelGS::GSInterface::drawing_kick_append<false, false, false, 3u>()` | paraLLEl CPU submit |
| 0.21 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a0]` | libc/kernel/vdso |
| 0.20 | GameThread | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.19 | GsWorker | `GS::writeRegisterPacked(unsigned char, unsigned long, unsigned long)` | GIF/GS packet handling |
| 0.19 | GsWorker | `GS::vertexKick(bool)` | GIF/GS packet handling |
| 0.19 | GameThread | `VU1Interpreter::applyDest(float*, float const*, unsigned char)` | VU1 execute |
| 0.17 | GameThread | `[kernel.kallsyms][+ffffffe761a8e664]` | libc/kernel/vdso |
| 0.16 | GameThread | `__vfprintf` | libc/kernel/vdso |
| 0.16 | GameThread | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.16 | GameThread | `VU1Interpreter::queueAccWrite(unsigned char, float const*, unsigned int)` | VU1 execute |
| 0.14 | GameThread | `libunwind::findUnwindSectionsByPhdr(dl_phdr_info*, unsigned long, void*)` | profiler unwind overhead |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe761a79608]` | libc/kernel/vdso |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe760b99edc]` | libc/kernel/vdso |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe760b98830]` | libc/kernel/vdso |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe760a21684]` | libc/kernel/vdso |
| 0.13 | GsWorker | `[kernel.kallsyms][+ffffffe760a15520]` | libc/kernel/vdso |
| 0.13 | GameThread | `VU1Interpreter::broadcast(float const*, unsigned char)` | VU1 execute |
| 0.12 | GameThread | `__emutls_get_address` | other |
| 0.12 | GameThread | `PS2Runtime::dispatchGuestBranch(unsigned char*, R5900Context*, unsigned int, unsigned int, unsigned int, PS2Runtime::GuestBranchKind, char const*)` | EE runtime helpers |
| 0.11 | com.ps2x.runner | `!!!0000!a0d82c13dd4b4e4f31b6cd30a2cb0d!a9ee82cd83!` | other |
| 0.11 | GameThread | `[kernel.kallsyms][+ffffffe760ad37c0]` | libc/kernel/vdso |
| 0.11 | GameThread | `VU1Interpreter::readBranchVi(unsigned char) const` | VU1 execute |
| 0.11 | GameThread | `EeScheduler::checkpointDue(unsigned int)` | scheduler/sync/waits |
| 0.10 | GsWorker | `[kernel.kallsyms][+ffffffe7611d5040]` | libc/kernel/vdso |
| 0.10 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c84]` | libc/kernel/vdso |
| 0.10 | GsWorker | `GS::processGIFPacket(unsigned char const*, unsigned int)` | GIF/GS packet handling |
| 0.10 | GsWorker | `@plt` | PLT |
| 0.10 | GameThread | `sub_0037E120_0x37e120(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.10 | GameThread | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.10 | GameThread | `__sfvwrite` | libc/kernel/vdso |
| 0.09 | GsWorker | `void ParallelGS::GSInterface::packed_XYZ<false, true, (ParallelGS::PRIMType)4>(void const*)` | paraLLEl CPU submit |
| 0.09 | GsWorker | `GS::recordDrawDebugEventUnlocked(int)` | GIF/GS packet handling |
| 0.09 | GameThread | `VU1Interpreter::decodeLowerUsage(unsigned int) const` | VU1 execute |
| 0.08 | GsWorker | `ps2_gfx_stats::detail::ensureInit()` | PS2 runtime other |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe761a8e6e0]` | libc/kernel/vdso |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe761a7ae44]` | libc/kernel/vdso |
| 0.08 | GsWorker | `[kernel.kallsyms][+ffffffe761a79580]` | libc/kernel/vdso |
| 0.08 | GameThread | `[kernel.kallsyms][+ffffffe760bcd1b4]` | libc/kernel/vdso |
| 0.08 | GameThread | `VU1Interpreter::resetScheduler()` | VU1 execute |
| 0.08 | GameThread | `VU1Interpreter::queueStore(unsigned int, unsigned int const*, unsigned char)` | VU1 execute |
| 0.07 | com.ps2x.runner | `WaitTime` | scheduler/sync/waits |
| 0.07 | GsWorker | `__emutls_get_address` | other |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760dd6c20]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760a277ec]` | libc/kernel/vdso |
| 0.07 | GsWorker | `[kernel.kallsyms][+ffffffe760855968]` | libc/kernel/vdso |
| 0.07 | GameThread | `[kernel.kallsyms][+ffffffe761a6b788]` | libc/kernel/vdso |
| 0.07 | GameThread | `VU1Interpreter::decodeUpperUsage(unsigned int) const` | VU1 execute |
| 0.06 | GsWorker | `void ParallelGS::GSInterface::drawing_kick<(ParallelGS::PRIMType)4>(bool)` | paraLLEl CPU submit |
| 0.06 | GsWorker | `pthread_mutex_unlock` | scheduler/sync/waits |
| 0.06 | GsWorker | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a83a5c]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe761a79560]` | libc/kernel/vdso |
| 0.06 | GsWorker | `[kernel.kallsyms][+ffffffe760cf8c1c]` | libc/kernel/vdso |
| 0.06 | GameThread | `sub_00376938_0x376938(unsigned char*, R5900Context*, PS2Runtime*)` | guest code |
| 0.06 | GameThread | `std::__ndk1::pair<std::__ndk1::__hash_iterator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, void*>*>, bool> std::__ndk1::__hash_table<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::__unordered_map_hasher<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::hash<unsigned int>, std::__ndk1::equal_to<unsigned int>, true>, std::__ndk1::__unordered_map_equal<unsigned int, std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>, std::__ndk1::equal_to<unsigned int>, std::__ndk1::hash<unsigned int>, true>, std::__ndk1::allocator<std::__ndk1::__hash_value_type<unsigned int, ps2_park::ParkHotPcEntry>>>::__emplace_unique_key_args<unsigned int, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>, std::__ndk1::tuple<>>(unsigned int const&, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<unsigned int const&>&&, std::__ndk1::tuple<>&&)` | PS2 runtime other |
| 0.06 | GameThread | `VU1Interpreter::pipelinesPending() const` | VU1 execute |
| 0.05 | com.ps2x.runner | `__memcpy_aarch64_nt` | libc/kernel/vdso |
| 0.05 | com.ps2x.runner | `[kernel.kallsyms][+ffffffe761a8e810]` | libc/kernel/vdso |
| 0.05 | GsWorker | `__aarch64_ldadd8_relax` | libc/kernel/vdso |
| 0.05 | GsWorker | `[kernel.kallsyms][+ffffffe761a795a8]` | libc/kernel/vdso |
| 0.05 | GameThread | `scudo::Allocator<scudo::AndroidNormalConfig, &scudo_malloc_postinit>::quarantineOrDeallocateChunk(scudo::Options const&, void*, scudo::Chunk::UnpackedHeader*, unsigned long)` | libc/kernel/vdso |
| 0.05 | GameThread | `VU1Interpreter::queueClip(unsigned int)` | VU1 execute |
| 0.05 | GameThread | `VU1Interpreter::decodeInstructionPair(unsigned char const*, unsigned int) const` | VU1 execute |
