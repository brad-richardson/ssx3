GameThread samples: 6361 (1 ms interval, 10 s)

| # | function (GameThread) | self samples | share |
|---|---|---|---|
| 1 | `VU1Interpreter::commitReadyPipelines()` | 1122 | 17.6% |
| 2 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)::$_0::ope` | 844 | 13.3% |
| 3 | `GSCpuBackend::WritePixel(GSDrawState const&, int, int, int, unsigned char, unsigned char, unsigned char, unsig` | 633 | 10.0% |
| 4 | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | 595 | 9.4% |
| 5 | `GSCpuBackend::Submit(GSPrimitiveBatch const&)` | 446 | 7.0% |
| 6 | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 321 | 5.0% |
| 7 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)` | 191 | 3.0% |
| 8 | `VU1Interpreter::execUpper(unsigned int)` | 190 | 3.0% |
| 9 | `VU1Interpreter::calculateFmacExactResult(unsigned int, long double&) const` | 145 | 2.3% |
| 10 | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | 134 | 2.1% |
| 11 | `__vfprintf` | 129 | 2.0% |
| 12 | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 101 | 1.6% |
| 13 | `ps2_mpg_src_trace::lookupPay(unsigned char const*, unsigned int&, int&, unsigned int&, unsigned int&)` | 83 | 1.3% |
| 14 | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | 80 | 1.3% |
| 15 | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | 76 | 1.2% |
| 16 | `VU1Interpreter::progressXgkick()` | 70 | 1.1% |
| 17 | `std::__function::__func<unsigned int (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned in` | 65 | 1.0% |
| 18 | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | 59 | 0.9% |
| 19 | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | 56 | 0.9% |
| 20 | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | 50 | 0.8% |
| 21 | `_platform_memmove` | 49 | 0.8% |
| 22 | `__sfvwrite` | 45 | 0.7% |
| 23 | `__bzero` | 42 | 0.7% |
| 24 | `GSMem::ReadCT32(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 33 | 0.5% |
| 25 | `PS2Memory::processVIF1Data(unsigned char const*, unsigned int)` | 28 | 0.4% |

Inclusive under executeVU0Microprogram: 186 of 6361 = 2.9%

| direct callee of executeVU0Microprogram | inclusive samples | share of thread |
|---|---|---|
| `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned ` | 169 | 2.7% |
| `VU1Interpreter::resetScheduler()` | 12 | 0.2% |
| `fprintf` | 2 | 0.0% |
