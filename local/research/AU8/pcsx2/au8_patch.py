# AU8: env-gated SPU2 tap + tag-1 path redirect (PCSX2_AU8_DIR). Run on bytesize.
from pathlib import Path
G = Path('/home/brad/pcsx2-g7/pcsx2/pcsx2')
p = G / 'R5900OpcodeImpl.cpp'
s = p.read_text()
old = 'au4_file = std::fopen(std::getenv("PCSX2_AU6_CAPTURE") ? "/home/brad/au6/pcsx2-tag1.bin" : "/home/brad/au4/pcsx2-tag1.bin", "ab");'
new = ('au4_file = std::fopen(std::getenv("PCSX2_AU8_DIR") ? (std::string(std::getenv("PCSX2_AU8_DIR")) + "/pcsx2-tag1.bin").c_str() : '
       'std::getenv("PCSX2_AU6_CAPTURE") ? "/home/brad/au6/pcsx2-tag1.bin" : "/home/brad/au4/pcsx2-tag1.bin", "ab");')
assert s.count(old) == 1, 'tag path'
p.write_text(s.replace(old, new))

m = G / 'SPU2/Mixer.cpp'
s = m.read_text()
inc = '#include "common/Assertions.h"\n'
assert s.count(inc) == 1
s = s.replace(inc, inc + '\n#include "common/Console.h"\n#include <cstdio>\n#include <cstdlib>\n#include <string>\n')
a1 = '\tspu2M_WriteFast(0xA00 + OutPos, Ext.Right);\n'
assert s.count(a1) == 1, 'ext'
s = s.replace(a1, a1 + '\tconst StereoOut32 au8_ext0 = Ext;\n')
a2 = '\tspu2Output(Out);\n'
assert s.count(a2) == 1, 'out'
tap = r'''
	// AU8: env-gated raw SPU2 tap (PCSX2_AU8_DIR). Per 48 kHz output sample, 16 s16:
	// in0 in1 (core inputs after InpVol), dry0 dry1 wet0 wet1 (voice mixes), ext0 (core0 out), out.
	{
		static int au8_state = -1;
		static FILE* au8_f = nullptr;
		static size_t au8_n = 0;
		if (au8_state < 0)
		{
			au8_state = 0;
			if (const char* d = std::getenv("PCSX2_AU8_DIR"))
			{
				au8_f = std::fopen((std::string(d) + "/spu2-tap.bin").c_str(), "wb");
				au8_state = au8_f ? 1 : 0;
				Console.WriteLn("AU8_SPU_OPEN ok=%d", au8_state);
			}
		}
		if (au8_state == 1)
		{
			const StereoOut32* v[8] = {&InputData[0], &InputData[1], &VoiceData[0].Dry, &VoiceData[1].Dry,
				&VoiceData[0].Wet, &VoiceData[1].Wet, &au8_ext0, &Out};
			s16 rec[16];
			for (int i = 0; i < 8; i++)
			{
				rec[2 * i] = static_cast<s16>(std::clamp<s32>(v[i]->Left, -32768, 32767));
				rec[2 * i + 1] = static_cast<s16>(std::clamp<s32>(v[i]->Right, -32768, 32767));
			}
			std::fwrite(rec, sizeof(rec), 1, au8_f);
			if (++au8_n >= 48000u * 600u)
			{
				std::fclose(au8_f);
				au8_f = nullptr;
				au8_state = 2;
				Console.WriteLn("AU8_SPU_CAP_REACHED");
			}
		}
	}
'''
s = s.replace(a2, a2 + tap)
m.write_text(s)
print('patched')
