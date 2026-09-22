"""E29 Mission 2 step 2 -- apply the Mission-1 block, and NOTHING else.

Four hunks, one file. Every anchor is required to be present and (where the
tool says so) unique; a missing or ambiguous anchor aborts before a byte is
written. The tool is idempotent: run twice, it refuses the second time rather
than double-applying.
"""
import subprocess
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
REL = 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'
SRC = R / REL
BEFORE_SHA = 'f83ed02e21eba7cbbcecf8443740b13f8ee07ecdb77991da571fef38404ef600'

text = SRC.read_text()
assert sha(SRC) == BEFORE_SHA, 'MPEG.cpp is not the pinned 3adc0478 content'
assert 'PS2X_SKIP_MOVIE' not in text, 'already applied -- refusing to double-apply'

HUNK1_ANCHOR = '\n        MpegStubState g_mpeg_stub_state;\n'
HUNK1 = HUNK1_ANCHOR + '''        // DEV-ONLY startup-movie bypass (PS2X_SKIP_MOVIE=1). Default OFF: the
        // value must be exactly "1"; absent, "0", "true" or empty all leave the
        // faithful movie path untouched. Development bring-up scaffolding, NOT
        // a fix -- see local/research/E29. Faithful movie correctness is E30.
        bool devSkipMovie()
        {
            static const bool skip = [] {
                if (const char *env = std::getenv("PS2X_SKIP_MOVIE"))
                {
                    return env[0] == '1' && env[1] == '\\0';
                }
                return false;
            }();
            return skip;
        }
'''

HUNK2_ANCHOR = '\n            uint32_t isEndTraceCount = 0u;\n'
HUNK2 = HUNK2_ANCHOR + '            uint32_t devSkipMovieTraceCount = 0u;\n'

HUNK3A_ANCHOR = '\n            g_mpeg_stub_state.isEndTraceCount = 0u;\n'
HUNK3A = HUNK3A_ANCHOR + '            g_mpeg_stub_state.devSkipMovieTraceCount = 0u;\n'
HUNK3B_ANCHOR = '\n        g_mpeg_stub_state.isEndTraceCount = 0u;\n'
HUNK3B = HUNK3B_ANCHOR + '        g_mpeg_stub_state.devSkipMovieTraceCount = 0u;\n'

HUNK4_ANCHOR = ('\n            MpegPlaybackState &playback = getPlaybackState(mpegAddr);\n'
                '            if (playback.decodedFrames.empty() &&\n'
                '                !g_mpeg_stub_state.currentCdStreamEofSeen &&\n'
                '                !playback.streamEnded &&\n'
                '                !playback.decoderFailed)\n')
HUNK4 = ('\n            MpegPlaybackState &playback = getPlaybackState(mpegAddr);\n'
'''            // DEV-ONLY (PS2X_SKIP_MOVIE=1) startup-movie bypass. NOT a fix, and
            // not on any default path. Bounded to ONE thing: thread 1 does not
            // PARK in the picture wait below. Everything before this point --
            // the non-stream delivery, the producer dispatch, the guest's
            // sceMpegAddBs, the parser feed -- runs exactly as it does with the
            // flag off. Marking the playback ended puts the state machine in the
            // same state finishPlaybackStream() and the program-end path already
            // produce, so the guest takes its OWN end-of-stream exit (the RCMP
            // player's counter-bounded re-ask loop at guest 0x3b1050) instead of
            // blocking on a picture this runtime cannot yet deliver. The decoder
            // is deliberately NOT flushed: the bypass synthesizes no frames.
            if (devSkipMovie() && playback.decodedFrames.empty() && !playback.streamEnded)
            {
                playback.streamEnded = true;
                playback.cdStreamGeneration = g_mpeg_stub_state.cdStreamGeneration;
                if (g_mpeg_stub_state.devSkipMovieTraceCount < 32u)
                {
                    PS2_IF_AGRESSIVE_LOGS({
                        std::cerr << "[MPEG:DEV-SKIP-MOVIE] bypass armed (PS2X_SKIP_MOVIE=1), mpeg=0x"
                                  << std::hex << mpegAddr << std::dec
                                  << " n=" << (g_mpeg_stub_state.devSkipMovieTraceCount + 1u)
                                  << " requestInput=" << requestInput
                                  << " sawInput=" << playback.sawInput
                                  << " served=" << playback.picturesServed << std::endl;
                    });
                    ++g_mpeg_stub_state.devSkipMovieTraceCount;
                }
            }
'''
'            if (playback.decodedFrames.empty() &&\n'
'                !g_mpeg_stub_state.currentCdStreamEofSeen &&\n'
'                !playback.streamEnded &&\n'
'                !playback.decoderFailed)\n')

plan = [('HUNK 1 flag helper', HUNK1_ANCHOR, HUNK1, True),
        ('HUNK 2 trace counter field', HUNK2_ANCHOR, HUNK2, True),
        ('HUNK 3a reset site 1', HUNK3A_ANCHOR, HUNK3A, True),
        ('HUNK 3b reset site 2', HUNK3B_ANCHOR, HUNK3B, True),
        ('HUNK 4 the bypass', HUNK4_ANCHOR, HUNK4, True)]

rows = []
for name, anchor, repl, unique in plan:
    n = text.count(anchor)
    assert n == 1 if unique else n >= 1, f'{name}: anchor count {n}'
    text = text.replace(anchor, repl, 1)
    rows.append(dict(hunk=name, anchor_occurrences=n,
                     anchor_bytes=len(anchor.encode()), replacement_bytes=len(repl.encode()),
                     added_bytes=len(repl.encode()) - len(anchor.encode())))

SRC.write_text(text)
after_sha = sha(SRC)
diff = subprocess.run(['git', '-C', str(R), 'diff', '--', REL], text=True, capture_output=True)
stat = subprocess.run(['git', '-C', str(R), 'diff', '--numstat'], text=True, capture_output=True)
status = subprocess.run(['git', '-C', str(R), 'status', '--short'], text=True, capture_output=True)
(E / 'bypass.diff').write_text(diff.stdout)

numstat_rows = [l for l in stat.stdout.splitlines() if l.strip()]
checks = dict(
  one_file_only=len(numstat_rows) == 1,
  numstat=stat.stdout.strip(),
  status_short=status.stdout,
  status_is_one_modified_plus_pinned_untracked=(
      sorted(status.stdout.splitlines()) == sorted([f' M {REL}', '?? ps2_log.txt'])),
  deletions_zero=bool(numstat_rows) and numstat_rows[0].split('\t')[1] == '0',
  # The flag name appears TWICE by design: the getenv() lookup and the log
  # line that tells a reader of a boot log which flag produced it. Both are
  # required; a third occurrence would mean a variant spelling crept in.
  flag_name_present_exactly_twice=text.count('PS2X_SKIP_MOVIE') == 2,
  flag_getenv_exactly_once=text.count('std::getenv("PS2X_SKIP_MOVIE")') == 1,
  no_flag_name_variants=all(v not in text for v in
      ('PS2X_MOVIE_SKIP', 'PS2X_SKIPMOVIE', 'SKIP_MOVIE=', 'PS2X_SKIP_MOVIES')),
  marker_present_exactly_once=text.count('[MPEG:DEV-SKIP-MOVIE]') == 1,
  dev_only_labelled_in_code=text.count('DEV-ONLY') >= 2,
)
green = all(v for v in checks.values() if isinstance(v, bool))
save('bypass-apply.json', dict(utc=utc(), file=REL, before_sha256=BEFORE_SHA,
                               after_sha256=after_sha, hunks=rows,
                               added_bytes=sum(r['added_bytes'] for r in rows),
                               diff_file='bypass.diff', diff_bytes=len(diff.stdout.encode()),
                               checks=checks, green=green))
print(json.dumps(dict(after_sha256=after_sha, hunks=[r['hunk'] for r in rows],
                      checks={k: v for k, v in checks.items()}), indent=2))
print('# E29 APPLY TAIL COMPLETE green=' + ('1' if green else '0'))
assert green, checks
