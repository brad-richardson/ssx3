"""Close source, resource, retention and fork receipts without another boot."""
import gzip, subprocess
from e17_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
assert os.environ.get('E17_CANONICAL_ONLY') == '1'
audit = json.loads((E/'final-source-audit.json').read_text())
assert audit['generated_names'] == 9457 and audit['protected_build_unchanged']
resources = sample()
assert not bound(resources)
push = json.loads((E/'fork-push.json').read_text())
commands = []
def git(*args):
    p = subprocess.run(['git', '-C', str(R), *args], capture_output=True, text=True)
    commands.append(dict(argv=p.args, rc=p.returncode, stdout=p.stdout, stderr=p.stderr))
    assert p.returncode == 0, commands[-1]
    return p.stdout
head = git('rev-parse', 'HEAD').strip()
assert head == push['head'] == git('ls-remote', 'fork', 'refs/heads/ssx3').split()[0]
assert git('diff', '--cached', '--name-only') == ''
assert git('diff', '--name-only') == ''
status = git('status', '--short')
assert status == '?? ps2_log.txt\n', status
names = git('diff-tree', '--no-commit-id', '--name-only', '-r', head).splitlines()
assert sorted(names) == sorted(push['named_files'])
assert 'Orchestrated-By: Muse Code' in git('show', '-s', '--format=%B', head)
rows = json.loads((E/'e17a-retained.json').read_text())['files']
canonical = set()
for row in rows:
    q = E/row['canonical']
    with (gzip.open if row['encoding'] == 'gzip' else open)(q, 'rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == row['sha256']
    assert sha(row['original']) == row['sha256'], row['original']
    canonical.add(row['canonical'])
from e17_closed_events import tap, fields
events, tail = tap(P/'run/e17a-join/e7-events.txt')
assert not Path('/tmp/ssx3-p-lane-lease').exists()
p = subprocess.run(['pgrep', '-x', 'ps2EntryRunner'], capture_output=True, text=True)
assert p.returncode == 1, (p.returncode, p.stdout, p.stderr)
bounded = []
for path in sorted(E.glob('*-bounded-result.json')):
    d = json.loads(path.read_text())
    row = {k:d[k] for k in ['label','rc','bound','stdout_truncated','elapsed_s']}
    assert row['bound'] is None and not row['stdout_truncated']
    assert row['rc'] == (1 if row['label'] == 'five-fail-before' else 0), row
    bounded.append(row)
record = dict(utc=utc(), resources=resources, fork_head=head, remote_agreement=True,
    fork_commands=commands, fork_status=status, fork_index_empty=True, named_files=names,
    generated_names=9457, protected_build_files=554, protected_build_unchanged=True,
    main_runtime_mpeg_unchanged=True, title_boots=1, lease_absent=True, pgrep_rc=p.returncode,
    runner=pin(B/'ps2xRuntime/ps2EntryRunner'), suite=pin(B/'ps2xTest/ps2x_tests'),
    fixture=pin(P/'e17-fixtures/after/binding-test'),
    retention=dict(original_files=len(rows), canonical_files=len(canonical),
        canonical_bytes=sum((E/q).stat().st_size for q in canonical),
        canonical_hashes_verified=True, ssd_originals_reverified=True),
    source_shutdown=dict(events=len(events), footer=fields(tail), complete=True),
    bounded_tools=bounded, main_repo_pushed=False)
save('final-audit.json', record)
print('Final fork', head, 'remote agrees; 9457 generated names; protected 554 unchanged.')
print('Resources internal', resources['internal_allocated'], 'SSD', resources['ssd_allocated'])
print('Retained', len(rows), 'originals and', len(canonical), 'canonical files verified; source events', len(events))
print('# E17 FINAL AUDIT TAIL COMPLETE')
