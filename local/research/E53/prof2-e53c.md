GameThread samples: 6714 (1 ms interval, 10 s)

| # | function (GameThread) | self samples | share |
|---|---|---|---|
| 1 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)::$_0::ope` | 1104 | 16.4% |
| 2 | `VU1Interpreter::commitReadyPipelines()` | 1031 | 15.4% |
| 3 | `GSCpuBackend::WritePixel(GSDrawState const&, int, int, int, unsigned char, unsigned char, unsigned char, unsig` | 789 | 11.8% |
| 4 | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | 538 | 8.0% |
| 5 | `GSCpuBackend::Submit(GSPrimitiveBatch const&)` | 439 | 6.5% |
| 6 | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 311 | 4.6% |
| 7 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)` | 255 | 3.8% |
| 8 | `VU1Interpreter::execUpper(unsigned int)` | 176 | 2.6% |
| 9 | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | 130 | 1.9% |
| 10 | `__vfprintf` | 127 | 1.9% |
| 11 | `std::__function::__func<unsigned int (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned in` | 115 | 1.7% |
| 12 | `VU1Interpreter::calculateFmacExactResult(unsigned int, long double&) const` | 110 | 1.6% |
| 13 | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | 80 | 1.2% |
| 14 | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 79 | 1.2% |
| 15 | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | 68 | 1.0% |
| 16 | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | 66 | 1.0% |
| 17 | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | 63 | 0.9% |
| 18 | `VU1Interpreter::progressXgkick()` | 62 | 0.9% |
| 19 | `GSMem::ReadCT32(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 58 | 0.9% |
| 20 | `ps2_mpg_src_trace::lookupPay(unsigned char const*, unsigned int&, int&, unsigned int&, unsigned int&)` | 52 | 0.8% |
| 21 | `_platform_memmove` | 50 | 0.7% |
| 22 | `GSMem::ReadP4(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 47 | 0.7% |
| 23 | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | 38 | 0.6% |
| 24 | `__ultoa` | 33 | 0.5% |
| 25 | `std::__function::__func<void (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int, unsig` | 31 | 0.5% |

Inclusive under executeVU0Microprogram: 225 of 6714 = 3.4%

| direct callee of executeVU0Microprogram | inclusive samples | share of thread |
|---|---|---|
| `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned ` | 216 | 3.2% |
| `VU1Interpreter::resetScheduler()` | 8 | 0.1% |
| `fprintf` | 1 | 0.0% |
