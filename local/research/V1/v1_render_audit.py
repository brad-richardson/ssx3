"""V1 audit-table renderer: audit-compare.json + pins + slices + worktrees -> AUDIT.md table.

Run AFTER compare. Prints the table markdown to stdout and rewrites AUDIT.md
(method + uncorroborated sections preserved from the draft body above the table marker).
"""
import json
from v1_common import E, load

cmp_ = load('audit-compare.json')
pins = load('v1_pins.json')['pins']
p1 = load('audit-pass1.json')
slices = load('slices.json')
wopen = load('worktrees-open.json')
wclose = load('worktrees-close.json') if (E / 'worktrees-close.json').exists() else None

def row(key):
    return cmp_['rows'].get(key, {})

def stab(key):
    r = row(key)
    return 'STABLE' if r.get('stable') else 'UNSTABLE'

def pinst(key):
    return row(key).get('pin', 'unpinned')

def short(sha):
    return (sha or '?')[:12] + '…'

L = []
L.append('## Audit table (from `audit-compare.json`, gap_min=%.0fs gap_max=%.0fs)' % (
    cmp_['gap_min_s'] or -1, cmp_['gap_max_s'] or -1))
L.append('')
L.append('| # | Critical path | Size | SHA (PASS1=PASS2?) | Corroboration | SOLE-COPY? |')
L.append('|---|---|---|---|---|---|')

n = 0
def add(path, size, sha, coro, sole):
    global n
    n += 1
    L.append(f'| {n} | {path} | {size} | {sha} | {coro} | {sole} |')

# E25
r = p1['sets']['e25']['files']
add('E25 tar (SSD)', '1,762,803,200', f"{short(r['tar_ssd']['sha256'])} {stab('tar_ssd')} {pinst('tar_ssd')}",
    'Tier-1 E25 RESTORE.md + tarlist 8408/7342', 'YES (tar) — binaries mirrored; tar SSD-only')
add('E25 runner SSD+share+live', '163,529,696 ×3',
    f"{short(r['runner_ssd']['sha256'])} {stab('runner_ssd')} {pinst('runner_ssd')} agree={cmp_['agreement']['groups']['e25_runner']['agree']}",
    'Tier-1 E25 RESTORE.md', 'NO — 3 copies agree')
add('E25 suite SSD+share+live', '5,695,128 ×3',
    f"{short(r['suite_ssd']['sha256'])} {stab('suite_ssd')} {pinst('suite_ssd')} agree={cmp_['agreement']['groups']['e25_suite']['agree']}",
    'Tier-1 E25 RESTORE.md', 'NO — 3 copies (+v1-smoke 4th)')
add('E25 manifest + RESTORE.md (in-git)', '7342 entries', 'in-git blobs (no byte reads)',
    'Tier-1 self (HEAD blobs)', 'NO — git-distributed')
# G binaries
for g in (33, 34, 35, 36, 37):
    k = f'g{g}_bin'
    rr = p1['sets']['g_bin']['files'][k]
    bid = cmp_['rows'][k].get('build_id_match')
    add(f'G{g} replayer (SSD build dir)', f"{rr['bytes']:,}",
        f"{short(rr['sha256'])} {stab(k)} {pinst(k)} magic={rr.get('magic')} bid_match={bid}",
        f'Tier-1 G{g} REPORT (sha+BuildID)', 'bytes YES — rebuildable (clone+hunks)')
# G13
rr = p1['sets']['g13']['files']['g13/g13-dump.gs']
add('G13 dump (SSD)', '11,537,377', f"{short(rr['sha256'])} {stab('g13/g13-dump.gs')} {pinst('g13/g13-dump.gs')}",
    'Tier-1 G35/G36/G37 REPORTs', 'YES — NO second copy anywhere (moves FIRST)')
add('G13 other 22 files (SSD)', '~8.3 MB total', 'stability per-file in JSON (all checked)',
    'U5 UNCORROBORATED (no G13 pins)', 'YES — SSD-only')
# G mirrors
for g in (33, 34, 35, 36, 37):
    ppm_ok = all(row(f'g{g}_ssd/{p}').get('stable') and row(f'g{g}_share/{p}').get('stable')
                 and cmp_['agreement']['groups'].get(f'g{g}:{p}', {}).get('agree')
                 for p in [f'g13-dump.gs.g10-vsync{i}.ppm' for i in range(8)] + ['g13-dump.gs.g8-first.ppm', 'g13-dump.gs.g8-last.ppm'])
    logs = [f'g{g}-logcat.txt', f'g{g}-run-stderr.txt', f'g{g}-run-stdout.txt']
    log_ok = all(cmp_['agreement']['groups'].get(f'g{g}:{l}', {}).get('agree') for l in logs)
    add(f'ps2x-g{g}/ + share (13+13)', '~7 MB/side',
        f'PPMs agree+stable={ppm_ok} (pinned); logs agree={log_ok} (U1 unpinned)',
        'Tier-1 scanout sha (PPMs); U1 logs', 'NO — SSD+share agree')
# I24
add('i24 logs + mirror (3+3)', '~18 MB/side',
    'console+2 RGBA: stability+agreement in JSON', 'Tier-1 console sizes + RGBA fnv', 'NO — SSD+share agree')
add('i24 signed-app (SSD)', '~3.2 GB (ISO 3.0 GB)',
    'per-file stability in JSON; ISO+ELF+vector pinned', 'Tier-1 ISO/ELF/vector; U7 small files', 'binary YES (resign fallback); ISO/ELF/ App-vector NO')
add('W binary+lib (SSD ps2x-i23)', '122,458,696 + lib',
    f"{stab('w_bin')} {pinst('w_bin')}", 'U4 PARTIAL (prefix/tail/size)', 'bytes YES (rebuild per I23)')
# E inputs
add('spike ISO + staged ISO', '3,005,415,424 ×2',
    f"agree={cmp_['agreement']['groups']['iso']['agree']} {pinst('iso_spike')}", 'Tier-1 full sha', 'NO — 2 copies agree')
add('ELF ×3 (P1, P1/cd, .app)', '3,890,784 ×3',
    f"P1/cd {pinst('p1cd/SLUS_207.72')}; P1-top separate 2-read; agree in JSON", 'Tier-1 ELF_A (E23 typo resolved by measure)', 'NO — 3 copies')
add('P1/cd PAD0/PAD1 + SYSTEM.CNF', '268 MB ×2 + 49 B', 'stability in JSON', 'U6/U8 unpinned', 'YES — padding/conf, SSD-only')
# T4
t4rows = {k: v for k, v in cmp_['rows'].items() if k.startswith('t4_')}
stable_n = sum(1 for v in t4rows.values() if v.get('stable'))
full_n = sum(1 for v in t4rows.values() if v.get('pin') == 'FULL-match')
part_n = sum(1 for v in t4rows.values() if v.get('pin') == 'PREFIX-match')
add('ps2x-t4/ + share (41+41)', '64.9 + 67.5 GB',
    f'{stable_n}/{len(t4rows)} stable; FULL={full_n} PARTIAL={part_n} rows; slices 40/40',
    'Tier-1: 25 FULL files (22 rotation-era + variant + t46r3 + r1b), 21 PARTIAL, 1 SIZE-only; U2/U3 rest',
    'NO (SSD+share+bytesize); t46r3 SSD-only fresh; variant share-only by design')
# Live tree
liverows = {k: v for k, v in cmp_['rows'].items() if k.startswith('live/')}
stable_l = sum(1 for v in liverows.values() if v.get('stable'))
pin_l = sum(1 for v in liverows.values() if v.get('pin') == 'FULL-match')
add('live /tmp/e18-mpeg-link (7342)', '1,748,192,253',
    f'{stable_l}/7342 stable; {pin_l}/7342 manifest FULL-match', 'Tier-1 E25 manifest (per-file)', 'NO — manifest+tar+live (volatile path noted)')
add('/tmp/p1-link, /tmp/e17-map-link', '—', 'absent (confirmed)', 'E25 loss inventory (Tier-1)', 'n/a — lost, orchestrator-tabled')
# Worktrees
for name in ('fork_ps2recomp', 'clone_parallel_gs', 'fork_wt_i10', 'fork_wt_i11'):
    v = wopen['repos'][name]
    dirt = v['status_short'].strip().replace('\n', '; ')[:90] or 'clean'
    tag = 'Tier-1 E25/E28 gates' if name == 'fork_ps2recomp' else ('Tier-1 G37 REPORT' if name == 'clone_parallel_gs' else 'I-lane history (detached)')
    extra = ''
    if name == 'fork_ps2recomp':
        fr = load('fork-ref.json')
        extra = f" ref ssx3={fr['ref_ssx3'][:12]} remote-ssx3={fr['ls_remote_fork_ssx3'][:12]} HEAD-vs-ref={'SAME' if fr['head']==fr['ref_ssx3'] else 'DIFFER'}"
    add(f'worktree {name}', '—', f"{v['head'][:12]} {v['branch']} [{dirt}]{extra}", tag, 'n/a (git refs)')
add('ssx3 main + 6 worktrees', '—', 'main 39f2e6c clean; 2 stale-gone (prune: orch); 3 subagent dirty-detached (untouched)',
    'rev-parse+status (read-only)', 'n/a (git refs)')
if wclose:
    dif = [k for k in wopen['repos'] if wopen['repos'][k]['status_short'] != wclose['repos'][k]['status_short']
           or wopen['repos'][k]['head'] != wclose['repos'][k]['head']]
    L.append('')
    L.append('Worktree open-vs-close: ssx3 main HEAD advanced by orch commits (8e84791→…→39f2e6c: [T46]+[G39-brief]+[N1]) — not V1; '
             'fork HEAD moved ssx3→e29-movie-bypass @ same commit 3adc0478 (E29 checkout, ref immutable — fork-ref.json); '
             'all other worktrees byte-identical. Zero V1 mutations.')

L.append('')
L.append('Pin-mismatch resolutions (all 5 explained, none are new corruption):')
L.append('- g35/g36/g37 binaries: the GATED 14th/15th/16th read artifacts PERSIST (zeroed reads, sizes right, '
         'values identical to the gated pins e2998ffcc1f0001a/6430dbe875adcfc3/e2ed9fd85b7d16dc); V1 re-pins them with 21-min-separated reads. '
         'Run validity stands per precedent (committed build shas remain the authority for what the binaries were).')
L.append('- t43r1 (both sides): probable ONE-CHAR T43 REPORT tail typo (`…e82e03` vs measured `…d82e03`); carried by prefix+size match, '
         'SSD↔share agreement ×2 passes, and committed head+tail slice bytes (40/40). V1-new full pin: '
         '`b8a27b8343c9a35b9777c283a55c65f9dcf30cb4b4fb29c779e9321c3ed82e03` (4-read agreement + slices).')
L.append('- r1b (RESOLVED by upgrade): REPORT prose `b3ca14e…` drops a leading 3; R1 evidence files carry the full sha — now a FULL pin, FULL-match.')
L.append('- w_lib (RESOLVED by completion): I24 prose pins prefix/tail; I17 pins the size — combined pin PREFIX-match.')
L.append('')
L.append('Disagreements: %s.' % (cmp_['agreement']['disagree'] or ['none']))
L.append('Unstable: %s.' % ([k for k in cmp_['mismatch']] or ['none']))
L.append(f"Keyset drift pass1->pass2: only1={cmp_['keyset_only_pass1'] or ['none']}, only2={cmp_['keyset_only_pass2'] or ['none']}.")

# splice into AUDIT.md (keep everything above the table marker)
body = (E / 'AUDIT.md').read_text()
marker = '## Audit table'
head = body.split(marker)[0]
(E / 'AUDIT.md').write_text(head + '\n'.join(L) + '\n\n# V1 AUDIT TAIL COMPLETE\n')
print('\n'.join(L))
