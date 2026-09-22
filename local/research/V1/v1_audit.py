"""V1 audit passes: read-only stat+sha256 over every Mission-1 path, twice in time.

Usage: python3 v1_audit.py pass1|pass2|compare|worktrees <tag>|tarlist
PASS1 and PASS2 must be separated in time (target >=20 min gap on critical bytes).
"""
import sys, time
from pathlib import Path
from v1_common import (E, REPO, SSD, SHARE, LIVE, pin_file, save, load, run,
                       gnu_build_id, elf_magic, list_plain, utc)

E25_SSD = SSD / 'ps2recomp-spike/P1/e25-snapshot'

def build_sets():
    sets = {}
    # E25 snapshot + share + live (two binaries + tar)
    sets['e25'] = {
        'tar_ssd': E25_SSD / 'e18-mpeg-link.tar',
        'runner_ssd': E25_SSD / 'ps2EntryRunner',
        'suite_ssd': E25_SSD / 'ps2x_tests',
        'runner_share': SHARE / 'e25-restore/ps2EntryRunner',
        'suite_share': SHARE / 'e25-restore/ps2x_tests',
        'runner_live': LIVE / 'ps2xRuntime/ps2EntryRunner',
        'suite_live': LIVE / 'ps2xTest/ps2x_tests',
    }
    # G binaries
    gb = {}
    for g in (33, 34, 35, 36, 37):
        gb[f'g{g}_bin'] = SSD / f'parallel-gs-g{g}-android-build/tools/parallel-gs-replayer'
    sets['g_bin'] = gb
    # G13 dump dir (all non-sidecar files)
    g13 = {}
    vis, _ = list_plain(SSD / 'ps2x-g13')
    for n in vis:
        g13[f'g13/{n}'] = SSD / 'ps2x-g13' / n
    sets['g13'] = g13
    # G mirrors ssd+share
    gm = {}
    for g in (33, 34, 35, 36, 37):
        for side, root in (('ssd', SSD / f'ps2x-g{g}'), ('share', SHARE / f'ps2x-g{g}')):
            vis, _ = list_plain(root)
            for n in vis:
                gm[f'g{g}_{side}/{n}'] = root / n
    sets['g_mirror'] = gm
    # I24 logs ssd+share + signed-app + W binary/lib
    i24 = {}
    for side, root in (('ssd', SSD / 'ps2x-i24/logs'), ('share', SHARE / 'ps2x-i24/logs')):
        vis, _ = list_plain(root)
        for n in vis:
            i24[f'i24_logs_{side}/{n}'] = root / n
    app = SSD / 'ps2x-i24/signed-app/ps2EntryRunner.app'
    for p in sorted(app.rglob('*')):
        if p.is_file() and not p.name.startswith('._'):
            i24[f'i24_signed/{p.relative_to(app)}'] = p
    i24['w_bin'] = SSD / 'ps2x-i23/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app/ps2EntryRunner'
    i24['w_lib'] = SSD / 'ps2x-i23/ios-runtime-device/ps2xRuntime/Release-iphoneos/libps2_game_objects.a'
    sets['i24'] = i24
    # E boot inputs adjacent: spike ISO + P1/cd
    ein_ = {'iso_spike': SSD / 'ps2recomp-spike/SSX 3 (USA).iso'}
    vis, _ = list_plain(SSD / 'ps2recomp-spike/P1/cd')
    for n in vis:
        ein_[f'p1cd/{n}'] = SSD / 'ps2recomp-spike/P1/cd' / n
    sets['e_inputs'] = ein_
    # T4 mirrors
    t4 = {}
    for side, root in (('ssd', SSD / 'ps2x-t4'), ('share', SHARE / 'ps2x-t4')):
        vis, _ = list_plain(root)
        for n in vis:
            t4[f't4_{side}/{n}'] = root / n
    sets['t4'] = t4
    # Live tree per E25 manifest (paths absolute in manifest)
    man = load('../E25/snapshot-manifest.json') if False else None
    return sets

def manifest_entries():
    m = load('../E25/snapshot-manifest.json')
    return m['entries']

def do_pass(tag):
    out = {'tag': tag, 'sets': {}, 'utc_start': utc(), 'sidecars_skipped': {}}
    total_b = 0
    sets = build_sets()
    order = ['e25', 'g_bin', 'g13', 'g_mirror', 'i24', 'e_inputs', 'live', 't4']
    # live entries resolved lazily (7342 files)
    for sname in order:
        if sname == 'live':
            items = {f"live/{r['path']}": Path(r['path']) for r in manifest_entries()}
        else:
            items = sets[sname]
        srec = {'files': {}, 'n': 0, 'bytes': 0}
        t0 = time.time()
        for key, p in items.items():
            try:
                row = pin_file(p)
            except FileNotFoundError:
                row = {'present': False}
            except OSError as e:
                row = {'present': False, 'error': f'{type(e).__name__}: {e}'}
            if sname == 'g_bin' and row.get('sha256'):
                row['build_id'] = gnu_build_id(p)
                row['magic'] = elf_magic(p)
            srec['files'][key] = row
            srec['n'] += 1
            srec['bytes'] += row.get('bytes', 0)
            total_b += row.get('bytes', 0)
        srec['elapsed_s'] = round(time.time() - t0, 1)
        out['sets'][sname] = srec
        print(f'{tag} {sname}: {srec["n"]} files {srec["bytes"]} B in {srec["elapsed_s"]} s', flush=True)
    # sidecar census (counted, never hashed)
    for d in [E25_SSD, SSD / 'ps2x-g13', SSD / 'ps2recomp-spike/P1/cd',
              SSD / 'ps2x-i24/logs', SHARE / 'ps2x-i24/logs',
              SHARE / 'e25-restore', SSD / 'ps2x-t4', SHARE / 'ps2x-t4'] + \
             [SSD / f'ps2x-g{g}' for g in (33, 34, 35, 36, 37)] + \
             [SHARE / f'ps2x-g{g}' for g in (33, 34, 35, 36, 37)]:
        try:
            _, n = list_plain(d)
        except OSError:
            n = -1
        out['sidecars_skipped'][str(d)] = n
    out['utc_end'] = utc()
    out['total_bytes'] = total_b
    save(f'audit-{tag}.json', out)
    print(f'{tag}: {total_b} B total, {out["utc_start"]} -> {out["utc_end"]}', flush=True)

def do_worktrees(tag):
    repos = [
        ('fork_ps2recomp', SSD / 'ps2recomp-spike/PS2Recomp'),
        ('clone_parallel_gs', SSD / 'parallel-gs-g7'),
        ('fork_wt_i10', SSD / 'ps2x-i10/fork-wt'),
        ('fork_wt_i11', SSD / 'ps2x-i11/fork-wt'),
    ]
    wl = run(['git', '-C', str(REPO), 'worktree', 'list', '--porcelain'])
    for chunk in wl['stdout'].split('\n\n'):
        for line in chunk.splitlines():
            if line.startswith('worktree '):
                repos.append(('ssx3_wt:' + line.split(' ', 1)[1], Path(line.split(' ', 1)[1])))
    rec = {'tag': tag, 'utc': utc(), 'repos': {}}
    for name, path in repos:
        head = run(['git', '-C', str(path), 'rev-parse', 'HEAD'])
        st = run(['git', '-C', str(path), 'status', '--short'])
        br = run(['git', '-C', str(path), 'rev-parse', '--abbrev-ref', 'HEAD'])
        rec['repos'][name] = {
            'path': str(path),
            'head': head['stdout'].strip(), 'head_rc': head['returncode'] if 'returncode' in head else head['rc'],
            'branch': br['stdout'].strip(),
            'status_short': st['stdout'][:2000], 'status_rc': st['rc'],
            'status_stderr_head': st['stderr'][:500],
        }
        print(f"{name}: {rec['repos'][name]['head'][:12]} {rec['repos'][name]['branch']} status_bytes={len(st['stdout'])}", flush=True)
    save(f'worktrees-{tag}.json', rec)

def do_tarlist():
    r = run(['tar', '-tf', str(E25_SSD / 'e18-mpeg-link.tar')])
    members = r['stdout'].splitlines()
    files = [m for m in members if not m.endswith('/')]
    rec = {'utc': utc(), 'rc': r['rc'], 'stderr_head': r['stderr'][:300],
           'members_total': len(members), 'members_files': len(files)}
    save('tarlist.json', rec)
    print(rec, flush=True)

def do_compare():
    p1 = load('audit-pass1.json')
    p2 = load('audit-pass2.json')
    pins = load('v1_pins.json')
    cmp_ = {'utc': utc(), 'rows': {}, 'mismatch': [], 'agree': 0, 'pinned_match': 0,
            'pinned_mismatch': [], 'unpinned': [], 'keyset_only_pass1': [], 'keyset_only_pass2': []}
    for sname in p1['sets']:
        k1, k2 = set(p1['sets'][sname]['files']), set(p2['sets'][sname]['files'])
        cmp_['keyset_only_pass1'].extend(sorted(f'{sname}:{k}' for k in k1 - k2))
        cmp_['keyset_only_pass2'].extend(sorted(f'{sname}:{k}' for k in k2 - k1))
    for sname, s1 in p1['sets'].items():
        s2 = p2['sets'][sname]
        for key, r1 in s1['files'].items():
            r2 = s2['files'].get(key, {})
            stable = (r1.get('sha256') == r2.get('sha256') and r1.get('bytes') == r2.get('bytes')
                      and r1.get('sha256') is not None)
            row = {'bytes1': r1.get('bytes'), 'bytes2': r2.get('bytes'),
                   'sha1': (r1.get('sha256') or '')[:16], 'sha2': (r2.get('sha256') or '')[:16],
                   'stable': stable, 'gap_s': None}
            try:
                import datetime as dt
                t1 = dt.datetime.fromisoformat(r1['t1'])
                t2 = dt.datetime.fromisoformat(r2['t0'])
                row['gap_s'] = round((t2 - t1).total_seconds(), 1)
            except (KeyError, ValueError):
                pass
            pin = pins['pins'].get(key)
            if pin and r1.get('sha256'):
                if pin.get('size_only'):
                    ok = r1.get('bytes') == pin.get('bytes')
                    row['pin'] = 'SIZE-match' if ok else 'PIN-MISMATCH'
                elif pin.get('sha256'):
                    ok = r1['sha256'] == pin['sha256'] and r1.get('bytes') == pin.get('bytes')
                    row['pin'] = 'FULL-match' if ok else 'PIN-MISMATCH'
                else:
                    ok = (r1['sha256'].startswith(pin.get('sha_prefix', '@'))
                          and r1['sha256'].endswith(pin.get('sha_tail', '@'))
                          and r1.get('bytes') == pin.get('bytes'))
                    row['pin'] = 'PREFIX-match' if ok else 'PIN-MISMATCH'
                if ok:
                    cmp_['pinned_match'] += 1
                else:
                    cmp_['pinned_mismatch'].append(key)
            elif r1.get('sha256'):
                cmp_['unpinned'].append(key)
            if stable:
                cmp_['agree'] += 1
            else:
                cmp_['mismatch'].append(key)
            cmp_['rows'][key] = row
    # BuildID vs pin (G binaries carry build_id in pass rows)
    for key in ('g33_bin', 'g34_bin', 'g35_bin', 'g36_bin', 'g37_bin'):
        pin = pins['pins'].get(key, {})
        got = p1['sets']['g_bin']['files'].get(key, {}).get('build_id')
        want = pin.get('build_id')
        cmp_['rows'][key]['build_id_got'] = got
        cmp_['rows'][key]['build_id_pin'] = (want[:12] + '…') if want else None
        cmp_['rows'][key]['build_id_match'] = (got == want) if (got and want) else None
        if got and want and got != want:
            cmp_['pinned_mismatch'].append(key + ':build-id')
    gaps = [r['gap_s'] for r in cmp_['rows'].values() if r['gap_s'] is not None]
    cmp_['gap_min_s'] = min(gaps) if gaps else None
    cmp_['gap_max_s'] = max(gaps) if gaps else None
    # Cross-copy agreement (SSD<->share<->live), both passes
    agree_sets = {'e25_runner': ['runner_ssd', 'runner_share', 'runner_live'],
                  'e25_suite': ['suite_ssd', 'suite_share', 'suite_live'],
                  'elf': ['p1cd/SLUS_207.72', 'i24_signed/SLUS_207.72'],
                  'iso': ['iso_spike', 'i24_signed/SSX3.iso']}
    agr = {'groups': {}, 'disagree': []}
    for gname, keys in agree_sets.items():
        shas = {k: (p1['sets']['e25' if k.startswith(('runner', 'suite')) else
                         ('i24' if k.startswith('i24') else 'e_inputs')]['files'][k].get('sha256'),
                    p2['sets']['e25' if k.startswith(('runner', 'suite')) else
                         ('i24' if k.startswith('i24') else 'e_inputs')]['files'][k].get('sha256')) for k in keys}
        ok = len({s for pair in shas.values() for s in pair}) == 1 and None not in {s for pair in shas.values() for s in pair}
        agr['groups'][gname] = {'agree': ok, 'keys': keys}
        if not ok:
            agr['disagree'].append(gname)
    for sname, prefix, sides in (('g_mirror', 'g', None), ('i24', 'i24_logs', None), ('t4', 't4', None)):
        pass  # pair agreement computed below by filename stem
    pairs = {}
    for sname in ('g_mirror', 'i24', 't4'):
        for key in p1['sets'][sname]['files']:
            if '/t4_' in key or key.startswith('t4_'):
                stem = key.split('/', 1)[1]
                grp = f't4:{stem}'
            elif key.startswith('g3'):
                parts = key.split('/', 1)
                grp = parts[0].rsplit('_', 1)[0] + ':' + parts[1]  # g33_ssd/share -> g33
            elif key.startswith('i24_logs_'):
                grp = 'i24:' + key.split('/', 1)[1]
            else:
                continue
            pairs.setdefault(grp, []).append((sname, key))
    for grp, members in pairs.items():
        vals = set()
        for sname, key in members:
            vals.add(p1['sets'][sname]['files'][key].get('sha256'))
            vals.add(p2['sets'][sname]['files'][key].get('sha256'))
        ok = len(vals) == 1 and None not in vals
        agr['groups'][grp] = {'agree': ok, 'n_copies': len(members)}
        if not ok:
            agr['disagree'].append(grp)
    # Rotation identities (pre-tN == t(N-1) bytes by lane design; bonus check)
    for pre, base in [('t4_ssd/emulog-pre-t34-20260921T062214Z.txt', 't4_ssd/emulog-t33r2.txt'),
                      ('t4_ssd/emulog-pre-t35-20260921T065839Z.txt', 't4_ssd/emulog-t34r1.txt'),
                      ('t4_ssd/emulog-pre-t36-20260921T074342Z.txt', 't4_ssd/emulog-t35r1.txt'),
                      ('t4_ssd/emulog-pre-t37-20260921T084313Z.txt', 't4_ssd/emulog-t36r1.txt'),
                      ('t4_ssd/emulog-pre-t38-20260921T094255Z.txt', 't4_ssd/emulog-t37r1.txt'),
                      ('t4_ssd/emulog-pre-t39-20260921T104301Z.txt', 't4_ssd/emulog-t38r1.txt'),
                      ('t4_ssd/emulog-pre-t40-20260921T114358Z.txt', 't4_ssd/emulog-t39r1.txt'),
                      ('t4_share/emulog-t45r2-variant.txt', 't4_share/emulog-pre-t44-20260922T005924Z.txt')]:
        a = p1['sets']['t4']['files'].get(pre, {}).get('sha256')
        b = p1['sets']['t4']['files'].get(base, {}).get('sha256')
        if a is None or b is None:
            agr['groups'][f'rotation:{pre}'] = {'agree': None, 'note': 'not in mirrors'}
        else:
            agr['groups'][f'rotation:{pre}'] = {'agree': a == b}
            if a != b:
                agr['disagree'].append(f'rotation:{pre}')
    cmp_['agreement'] = agr
    save('audit-compare.json', cmp_)
    print(f"stable={cmp_['agree']} mismatch={len(cmp_['mismatch'])} "
          f"pinned_match={cmp_['pinned_match']} pinned_mismatch={len(cmp_['pinned_mismatch'])} "
          f"unpinned={len(cmp_['unpinned'])} gap=[{cmp_['gap_min_s']},{cmp_['gap_max_s']}]", flush=True)
    for k in cmp_['mismatch'][:30]:
        print('  UNSTABLE', k, cmp_['rows'][k], flush=True)
    for k in cmp_['pinned_mismatch'][:30]:
        print('  PIN-MISMATCH', k, cmp_['rows'][k], flush=True)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'pass1':
        do_pass('pass1')
    elif cmd == 'pass2':
        do_pass('pass2')
    elif cmd == 'compare':
        do_compare()
    elif cmd == 'worktrees':
        do_worktrees(sys.argv[2])
    elif cmd == 'tarlist':
        do_tarlist()
    else:
        raise SystemExit('unknown cmd')
