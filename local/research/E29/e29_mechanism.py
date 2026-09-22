"""E29 Mission 1 -- the bypass MECHANISM, named precisely and checked, not recalled.

Static only. No lease, no build, no branch, no worktree mutation. Read-only on
the fork. The brief forbids building blind: if any anchor this tool quotes is
absent from the file, it REFUSES rather than continuing, and the lane tables
and stops.

Standing SSD rule: MPEG.cpp is read TWICE (the caller separates the passes in
time) and is independently corroborated against its own git object -- it is a
TRACKED file on the fork, so unlike the generated guest sources it has a
content-addressed record that does not live on the SSD.
"""
import subprocess, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'

REL = 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'
SRC = R / REL
PASS = sys.argv[1] if len(sys.argv) > 1 else '1'

text = SRC.read_text()
lines = text.splitlines()

def line_of(needle, *, unique=True):
    """1-based line numbers carrying `needle`. Refuses if absent."""
    hits = [i + 1 for i, l in enumerate(lines) if needle in l]
    assert hits, f'ANCHOR ABSENT: {needle!r}'
    if unique:
        assert len(hits) == 1, f'ANCHOR NOT UNIQUE ({len(hits)}): {needle!r}'
    return hits

# ---------------------------------------------------------------- the anchors
# Every one is grepped out of the file. A missing anchor stops the lane.
A = {}
A['getMpegPicture_decl'] = line_of('static void getMpegPicture(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime, bool requestInput)\n'.rstrip(), unique=False)
A['dispatch_guard'] = line_of('if (requestInput && !delivery && playback.decodedFrames.empty() &&')
A['dispatch_guard_2'] = line_of('!g_mpeg_stub_state.currentCdStreamEofSeen && !playback.streamEnded && !playback.decoderFailed)')
A['wait_block_lock'] = line_of('std::unique_lock<std::mutex> lock(g_mpeg_stub_mutex);')
A['wait_playback_ref'] = line_of('MpegPlaybackState &playback = getPlaybackState(mpegAddr);', unique=False)
A['wait_guard_l1'] = line_of('if (playback.decodedFrames.empty() &&')
A['wait_guard_l2'] = line_of('!g_mpeg_stub_state.currentCdStreamEofSeen &&', unique=False)
A['wait_guard_l3'] = line_of('!playback.streamEnded &&', unique=False)
A['wait_guard_l4'] = line_of('!playback.decoderFailed)', unique=False)
A['getpicture_trace'] = line_of('if (g_mpeg_stub_state.getPictureWaitTraceCount < 32u)')
A['getpicture_trace_str'] = line_of('"[MPEG:GetPicture] waiting for frames, mpeg=0x"')
A['waitExternal'] = line_of('runtime->eeScheduler().waitExternal(')
A['wait_reason'] = line_of('EeWaitReason::Mpeg,')
A['wait_type'] = line_of('kMpegPictureWaitType,', unique=False)
A['lambda_captures_delivery'] = line_of('[rdram, runtime, delivery](R5900Context &resumeContext)', unique=False)
A['oncomplete_reentry'] = line_of('getMpegPicture(rdram, &parent, runtime, false);')
A['latch_comment'] = line_of('// One caller-owned request, retained by its invocation/wait continuations.')
A['state_streamEnded'] = line_of('bool streamEnded = false;')
A['state_isEndTraceCount'] = line_of('uint32_t isEndTraceCount = 0u;', unique=False)
A['reset_isEndTraceCount'] = line_of('g_mpeg_stub_state.isEndTraceCount = 0u;', unique=False)
A['real_setter_finish'] = line_of('void finishPlaybackStream(uint32_t mpegAddr, MpegPlaybackState &playback)')
A['real_setter_progend'] = line_of('if (streamId == kMpegProgramEnd)')

# The three trace-cap facts the checkpoint rests on, read out of the sources.
CAPS = {}
def cap(path, needle):
    t = (R / path).read_text()
    hits = [i + 1 for i, l in enumerate(t.splitlines()) if needle in l]
    assert hits, f'CAP ANCHOR ABSENT: {path}:{needle!r}'
    return dict(path=path, line=hits[0], text=needle)
CAPS['gs_prim_cap_64'] = cap('ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp', 'if (primitiveIndex < 64u)')
CAPS['gs_kick_cap_96'] = cap('ps2xRuntime/src/lib/gs/gs_frontend.cpp', 'the [gs:kick] line below caps at 96')
CAPS['frame_upload_cap_128_or_change'] = cap('ps2xRuntime/src/lib/ps2_runtime.cpp', 'if (s_uploadDebugCount < 128u ||')
CAPS['getpicture_wait_cap_32'] = dict(path=REL, line=A['getpicture_trace'][0],
                                      text='if (g_mpeg_stub_state.getPictureWaitTraceCount < 32u)')

# ------------------------------------------------ corroboration, not one read
git = subprocess.run(['git', '-C', str(R), 'show', f'{BASE_SHA}:{REL}'],
                     capture_output=True)
git_object_sha = hashlib.sha256(git.stdout).hexdigest()
on_disk_sha = sha(SRC)

# The env-flag name must be NEW: a collision would silently reuse someone's flag.
env_names = subprocess.run(
    ['grep', '-rho', '-E', 'PS2X_[A-Z0-9_]+', str(R / 'ps2xRuntime/src')],
    capture_output=True, text=True).stdout.split()
flag_is_new = 'PS2X_SKIP_MOVIE' not in set(env_names)

row = dict(utc=utc(), pass_id=PASS, mission='1 -- mechanism, static',
           file=REL, bytes=SRC.stat().st_size, lines=len(lines),
           sha256_on_disk=on_disk_sha, sha256_git_object=git_object_sha,
           git_rc=git.returncode,
           corroborated_by_git_object=(on_disk_sha == git_object_sha),
           anchors={k: v for k, v in A.items()}, anchors_found=len(A),
           anchors_missing=0,
           trace_caps=CAPS,
           flag='PS2X_SKIP_MOVIE', flag_name_is_new=flag_is_new,
           distinct_PS2X_env_names_in_runtime=len(set(env_names)))
save(f'mission-1-mechanism-pass-{PASS}.json', row)
print(json.dumps({k: v for k, v in row.items() if k not in ('anchors', 'trace_caps')}, indent=2))
print('anchors:', ' '.join(f'{k}@{v[0] if isinstance(v, list) else v}' for k, v in A.items()))
assert row['corroborated_by_git_object'], 'MPEG.cpp DIFFERS FROM ITS GIT OBJECT'
assert flag_is_new, 'PS2X_SKIP_MOVIE COLLIDES WITH AN EXISTING FLAG'
print('# E29 MECHANISM TAIL COMPLETE pass=' + PASS)
