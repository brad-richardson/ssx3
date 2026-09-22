"""E29 -- re-verify the applied bypass diff without re-applying it.

Runs the same audit `e29_apply.py` ends with, plus the DEV-ONLY labelling
audit the brief requires at EVERY layer, and two time-separated reads of the
modified file (standing SSD rule).
"""
import subprocess, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
REL = 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'
SRC = R / REL
PASS = sys.argv[1] if len(sys.argv) > 1 else '1'
text = SRC.read_text()
base = subprocess.run(['git', '-C', str(R), 'show', f'{BASE_SHA}:{REL}'],
                      capture_output=True).stdout.decode()

def g(*a):
    return subprocess.run(['git', '-C', str(R), *a], text=True, capture_output=True).stdout

stat = g('diff', '--numstat').strip()
status = g('status', '--short')
rows = [l for l in stat.splitlines() if l.strip()]
ins, dels, path = (rows[0].split('\t') + ['', '', ''])[:3] if rows else ('', '', '')

checks = dict(
  branch_is_bypass=g('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'e29-movie-bypass',
  head_still_fork_point=g('rev-parse', 'HEAD').strip() == BASE_SHA,
  one_file_changed=len(rows) == 1 and path == REL,
  insertions=ins, deletions=dels, deletions_zero=dels == '0',
  status_is_one_modified_plus_pinned_untracked=(
      sorted(status.splitlines()) == sorted([f' M {REL}', '?? ps2_log.txt'])),
  # the brief: DEV-ONLY at EVERY layer
  layer_flag_name=text.count('std::getenv("PS2X_SKIP_MOVIE")') == 1,
  layer_flag_name_exact_no_variants=all(
      v not in text for v in ('PS2X_MOVIE_SKIP', 'PS2X_SKIPMOVIE', 'PS2X_SKIP_MOVIES')),
  layer_branch_name='e29-movie-bypass' == g('rev-parse', '--abbrev-ref', 'HEAD').strip(),
  layer_code_comments=text.count('DEV-ONLY') >= 2,
  layer_build_dir='e29-movie-bypass-build' in str(NEWB),
  default_off_is_strict=("return env[0] == '1' && env[1] == '\\0';" in text),
  bypass_is_gated_by_the_flag=('if (devSkipMovie() && playback.decodedFrames.empty() '
                               '&& !playback.streamEnded)') in text,
  wait_guard_untouched=('            if (playback.decodedFrames.empty() &&\n'
                        '                !g_mpeg_stub_state.currentCdStreamEofSeen &&\n'
                        '                !playback.streamEnded &&\n'
                        '                !playback.decoderFailed)\n') in text,
  # Measured against the base blob, not against a remembered number: the diff
  # must not add or remove a single decoder-flush call site.
  no_decoder_flush_added=text.count('flushDecoderIfEnded') == base.count('flushDecoderIfEnded'),
  waitExternal_call_count_unchanged=text.count('runtime->eeScheduler().waitExternal(') == 1,
)
green = all(v for v in checks.values() if isinstance(v, bool))
row = dict(utc=utc(), pass_id=PASS, file=REL, sha256=sha(SRC), bytes=SRC.stat().st_size,
           numstat=stat, checks=checks, green=green)
save(f'bypass-verify-pass-{PASS}.json', row)
print(json.dumps(row, indent=2))
print('# E29 VERIFY-DIFF TAIL COMPLETE pass=%s green=%s' % (PASS, '1' if green else '0'))
assert green, checks
