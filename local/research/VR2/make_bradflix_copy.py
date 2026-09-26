#!/usr/bin/env python3
"""VR2: derive bradflix_build_vu1.sh from the current canonical bradflix_build.sh.

Changes only: VU1 image dir from $VR2_VU1_DIR synced to a private remote dir
$VR2_RVU1DIR; REPO pinned (the copy lives outside the repo); sources from a
private `git archive` export (HS1/PS2Recomp-vr2), never the shared checkout;
a paraLLEl pin mismatch on bradflix stops instead of re-cloning the shared dir.
Re-run whenever the canonical script changes (pins move with folds).
"""
import re
s = open('/Users/brad/dev/ssx3/local/tooling/build/bradflix_build.sh').read()
def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)
rep('VU1_DIR=$HOME/dev/ssx3-work/vu1gen-ssx3', 'VU1_DIR=${VR2_VU1_DIR:?set VR2_VU1_DIR}\nRVU1DIR=${VR2_RVU1DIR:?set VR2_RVU1DIR}')
s = s.replace('~/$RROOT/vu1gen', '~/$RROOT/$RVU1DIR')
rep('-DPS2X_VU1_RECOMP_DIR=/work/vu1gen', '-DPS2X_VU1_RECOMP_DIR=/work/$RVU1DIR')
s = re.sub(r'^REPO=.*$', 'REPO=/Users/brad/dev/ssx3  # VR2 copy lives outside the repo', s, flags=re.M)
a = s.index('ssh "$REMOTE" "cd ~/$RROOT/PS2Recomp && git fetch origin ssx3')
b = s.index('echo "remote HEAD: $FULL_SHA"')
s = s[:a] + '''# VR2 copy: a private export (PS2Recomp-vr2, git archive of the SHA, no .git),
# so another lane's checkout in the shared PS2Recomp cannot change sources mid-build.
ssh "$REMOTE" "cd ~/$RROOT/PS2Recomp && git fetch origin ssx3 2>&1 | tail -1; rm -rf ../PS2Recomp-vr2 && mkdir ../PS2Recomp-vr2 && git archive $SHA_IN | tar -C ../PS2Recomp-vr2 -xf -" || exit 1
FULL_SHA="$(ssh "$REMOTE" "git -C ~/$RROOT/PS2Recomp rev-parse $SHA_IN^{commit}")"
case "$FULL_SHA" in *[!0-9a-f]*|"") echo "bad SHA from remote: $FULL_SHA" >&2; exit 2;; esac
[ "${#FULL_SHA}" -eq 40 ] || { echo "bad SHA from remote: $FULL_SHA" >&2; exit 2; }
''' + s[b:]
rep('cmake -S /work/PS2Recomp ', 'cmake -S /work/PS2Recomp-vr2 ')
a = s.index('if [ "$RPGS" != "$PGS_PIN" ] || [ "$RGRAN" != "$GRANITE_PIN" ]; then')
b = s.index('echo "== image $IMAGE')
s = s[:a] + '''if [ "$RPGS" != "$PGS_PIN" ] || [ "$RGRAN" != "$GRANITE_PIN" ]; then
  # VR2 copy: the shared parallel-gs belongs to every lane; never re-clone it here.
  echo "shared parallel-gs is $RPGS / $RGRAN, want $PGS_PIN / $GRANITE_PIN: stop" >&2; exit 2
else echo "-- parallel-gs $RPGS / Granite $RGRAN OK"; fi

''' + s[b:]
# VR2_PGS_PIN: build against the paraLLEl already installed on bradflix (its
# shared dir is moved only by its owner); the mini-side paraLLEl check is then
# skipped, since the mini's canonical checkout follows the canonical pin.
rep('''[ "$(git -C "$PGS_DIR" rev-parse HEAD)" = "$PGS_PIN" ] || { echo "mini PGS mismatch" >&2; exit 2; }''',
    '''if [ -n "${VR2_PGS_PIN:-}" ]; then PGS_PIN=$VR2_PGS_PIN; echo "-- VR2: remote paraLLEl pin override $PGS_PIN (mini check skipped)";
else [ "$(git -C "$PGS_DIR" rev-parse HEAD)" = "$PGS_PIN" ] || { echo "mini PGS mismatch" >&2; exit 2; }; fi''')
open('/Users/brad/dev/ssx3-work/VR2/bradflix_build_vu1.sh', 'w').write(s)
print('ok')
