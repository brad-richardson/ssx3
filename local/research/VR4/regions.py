"""VR4: issuePair source-line regions (ps2_vu1_step_impl.h at fork 5d5c382)."""
RANGES = [(229, 269, 'stall/scoreboard'), (270, 299, 'direct-map setup'),
          (300, 340, 'old VF/ACC/VI snapshot'), (341, 372, 'exec dispatch'),
          (373, 391, 'post-exec clears'), (392, 450, 'revert+commit writes'),
          (451, 454, 'markPairWrites'), (455, 460, 'vf0/vi0 constants'),
          (461, 510, 'pc/branch/halt'), (511, 511, 'advanceOneCycle'),
          (512, 527, 'counters/return')]
def issue_region(line):
    for lo, hi, name in RANGES:
        if lo <= line <= hi: return name
    return 'issuePair:%d' % line
def region(chain):
    names = [f['FunctionName'] for f in chain]
    for i, n in enumerate(names):
        if n.startswith('issuePair'):
            r = issue_region(chain[i]['Line'])
            if i == 0: return r
            if r == 'exec dispatch':
                return 'exec > ' + ('execUpperImpl (FMAC core)' if 'execUpperImpl' in names else names[i - 1])
            return r + ' > ' + names[i - 1]
    return 'glue: ' + (names[0] if names else '?')
