# AU9: env-gated (PCSX2_AU9_DIR) SND/SPU2 characterization hooks on top of the AU8 tree. Run on bytesize.
# Files written into $PCSX2_AU9_DIR:
#   tagbuf.bin : per EE SetDma of the SND tag buffer (src 0x512b80): 'TAGB' u32 vsync u32 ns u32 size, size bytes, 0x240 bytes of EE status 0x50b740
#   sifdma.bin : every other EE SetDma descriptor: 'DMA0' vsync ns src dst size attr ra, then min(size,0x20000) bytes
#   spureg.bin : every SPU2write: u32 ns, u32 rmem, u32 value
#   spudma.txt : non-ADMA SPU2 DMA writes: ns core TSA size(u16 units)
#   spuram-<k>.bin : 2 MiB SPU RAM every 20 s of 48 kHz output (k = ns / 960000)
# ns = count of 48 kHz SPU2 output samples since boot (guest time).
from pathlib import Path
G = Path('/home/brad/pcsx2-g7/pcsx2/pcsx2')

def patch(path, old, new, count=1):
    s = path.read_text()
    assert s.count(old) == count, (path, old[:60], s.count(old))
    path.write_text(s.replace(old, new))

HELP = r'''
#include <cstdio>
#include <cstdlib>
#include <string>
extern unsigned long long g_au9_ns;
static inline FILE* au9_file(const char* name, const char* mode)
{
	const char* d = std::getenv("PCSX2_AU9_DIR");
	if (!d) return nullptr;
	return std::fopen((std::string(d) + "/" + name).c_str(), mode);
}
'''

# Mixer.cpp: sample counter + SPU RAM dumps
m = G / 'SPU2/Mixer.cpp'
patch(m, '#include "common/Console.h"\n', '#include "common/Console.h"\n' + HELP) # Mixer.cpp is multi-ISA: define the counter in spu2.cpp
patch(m, '\tspu2Output(Out);\n', '''\tspu2Output(Out);
	// AU9: guest-time sample counter + SPU RAM dump every 20 s (PCSX2_AU9_DIR).
	{
		static int au9_on = -1;
		if (au9_on < 0) au9_on = std::getenv("PCSX2_AU9_DIR") ? 1 : 0;
		g_au9_ns++;
		if (au9_on && (g_au9_ns % 960000ull) == 0 && g_au9_ns <= 960000ull * 40)
		{
			char nm[64];
			std::snprintf(nm, sizeof(nm), "spuram-%03llu.bin", g_au9_ns / 960000ull);
			if (FILE* f = au9_file(nm, "wb")) { std::fwrite(_spu2mem, 1, 0x200000, f); std::fclose(f); }
		}
	}
''')

# spu2.cpp: register-write log
s2 = G / 'SPU2/spu2.cpp'
patch(s2, '#include "SPU2/Debug.h"\n', '#include "SPU2/Debug.h"\nunsigned long long g_au9_ns = 0; // AU9\n' + HELP)
patch(s2, '''	TimeUpdate(psxRegs.cycle);

	if (rmem >> 16 == 0x1f80)''', '''	TimeUpdate(psxRegs.cycle);

	{ // AU9: SPU2 register-write log (PCSX2_AU9_DIR)
		static int au9_on = -1;
		static FILE* au9_f = nullptr;
		static unsigned long long au9_n = 0;
		if (au9_on < 0) { au9_f = au9_file("spureg.bin", "wb"); au9_on = au9_f ? 1 : 0; }
		if (au9_on && au9_n < 40000000ull)
		{
			const u32 rec[3] = {static_cast<u32>(g_au9_ns), rmem, value};
			std::fwrite(rec, sizeof(rec), 1, au9_f);
			if ((++au9_n & 0xffff) == 0) std::fflush(au9_f);
		}
	}

	if (rmem >> 16 == 0x1f80)''')

# Dma.cpp: non-ADMA DMA writes
d = G / 'SPU2/Dma.cpp'
patch(d, '#include "Config.h"\n', '#include "Config.h"\n' + HELP)
patch(d, '''	else
	{
		PlainDMAWrite(pMem, size);
		Regs.STATX &= ~0x80;''', '''	else
	{
		{ // AU9: log plain (voice) DMA writes
			static int au9_on = -1;
			static FILE* au9_f = nullptr;
			if (au9_on < 0) { au9_f = au9_file("spudma.txt", "w"); au9_on = au9_f ? 1 : 0; }
			if (au9_on) { std::fprintf(au9_f, "%llu %d %05x %u\\n", g_au9_ns, Index, ActiveTSA, size); std::fflush(au9_f); }
		}
		PlainDMAWrite(pMem, size);
		Regs.STATX &= ~0x80;''')

# R5900OpcodeImpl.cpp: SetDma capture (independent of AU4)
r = G / 'R5900OpcodeImpl.cpp'
patch(r, 'extern u32 g_t65_ee_vsync;', 'extern unsigned long long g_au9_ns; // AU9\nextern u32 g_t65_ee_vsync;')
patch(r, '''		case Syscall::sceSifSetDma:
			// AU4: read-only EE tag-1 capture.''', '''		case Syscall::sceSifSetDma:
			// AU9: full SND tag buffer + status per tick, and every other SIF DMA (PCSX2_AU9_DIR).
			{
				static int au9_on = -1;
				static FILE* au9_tag = nullptr;
				static FILE* au9_dma = nullptr;
				static unsigned long long au9_dma_bytes = 0;
				if (au9_on < 0)
				{
					const char* d = std::getenv("PCSX2_AU9_DIR");
					if (d)
					{
						au9_tag = std::fopen((std::string(d) + "/tagbuf.bin").c_str(), "wb");
						au9_dma = std::fopen((std::string(d) + "/sifdma.bin").c_str(), "wb");
					}
					au9_on = (au9_tag && au9_dma) ? 1 : 0;
					Console.WriteLn("AU9_OPEN ok=%d", au9_on);
				}
				const u32 desc = cpuRegs.GPR.n.a0.UL[0];
				const u32 count = cpuRegs.GPR.n.a1.UL[0];
				if (au9_on && count <= 32 && desc < 0x02000000 && (desc & 15) == 0)
				{
					for (u32 i = 0; i < count; i++)
					{
						const u32 src = memRead32(desc + i * 16);
						const u32 dst = memRead32(desc + i * 16 + 4);
						const u32 size = memRead32(desc + i * 16 + 8);
						const u32 attr = memRead32(desc + i * 16 + 12);
						const u32 ns = static_cast<u32>(g_au9_ns);
						if (src == 0x00512b80 && size <= 0x1000)
						{
							const u32 h[4] = {0x42474154u, ::g_t65_ee_vsync, ns, size};
							std::fwrite(h, sizeof(h), 1, au9_tag);
							std::fwrite(PSM(src), 1, size, au9_tag);
							std::fwrite(PSM(0x0050b740), 1, 0x240, au9_tag);
						}
						else if (au9_dma_bytes < (512ull << 20))
						{
							const u32 n = (size & 0x1fffffff) < 0x20000 ? (size & 0x1fffffff) : 0x20000;
							const u32 h[8] = {0x30414d44u, ::g_t65_ee_vsync, ns, src, dst, size, attr, cpuRegs.GPR.r[31].UL[0]};
							std::fwrite(h, sizeof(h), 1, au9_dma);
							const u32 s = src & 0x1fffffff;
							const u8* p = (n && s + n <= 0x02000000) ? static_cast<const u8*>(PSM(s)) : nullptr;
							for (u32 k = 0; k < n; k++) std::fputc(p ? p[k] : 0, au9_dma);
							au9_dma_bytes += 32 + n;
						}
					}
				}
			}
			// AU4: read-only EE tag-1 capture.''')
print('patched')
