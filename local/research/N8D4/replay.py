#!/usr/bin/env python3
"""One bounded CPU and paraLLEl replay, after the N8D4 release and device gate."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tarfile
import time

REPO = Path('/Users/brad/dev/ssx3')
FORK = Path('/Users/brad/dev/PS2Recomp')
ROOT = Path('/Users/brad/dev/ssx3-work/N8D4')
SRC = ROOT / 'PS2Recomp'
BUILD = ROOT / 'build'
CAPTURE = ROOT / 'n8d4.gs'
RESULT = ROOT / 'replay-result.json'
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3')
PARALLEL = Path('/Users/brad/dev/ssx3-work/G43/parallel-gs')
VULKAN = Path('/opt/homebrew/lib/libvulkan.1.dylib')
LOG_CAP = 16 * 1024**2
SCRATCH_CAP = 12 * 1024**3


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(data)
    return h.hexdigest()


def usage():
    return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())


def budget():
    subprocess.run([str(REPO / 'local/tooling/disk_budget.sh')], cwd=REPO, check=True)
    size = usage()
    if size > SCRATCH_CAP:
        raise RuntimeError(f'N8D4 scratch cap exceeded: {size}')
    return size


def run(name, command, *, cwd, env=None, timeout=1200):
    log = ROOT / f'{name}.log'
    start = time.monotonic()
    with log.open('wb') as out:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdout=out,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while proc.poll() is None:
                if time.monotonic() - start > timeout or log.stat().st_size > LOG_CAP:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                    raise RuntimeError(f'{name}: time/log cap reached')
                time.sleep(0.5)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
    if proc.returncode or log.stat().st_size > LOG_CAP:
        raise RuntimeError(f'{name}: exit={proc.returncode}, log_bytes={log.stat().st_size}')
    return {'command': command, 'seconds': round(time.monotonic() - start, 3),
            'log_bytes': log.stat().st_size}


def main():
    if RESULT.exists() or SRC.exists() or BUILD.exists():
        raise RuntimeError('N8D4 replay already started; no second build/replay')
    device = json.loads((ROOT / 'result.json').read_text())
    if device['result'] != 'capture and race stages captured':
        raise RuntimeError('device capture gate did not pass')
    subprocess.run(['python3', str(REPO / 'local/research/N8D4/accept.py'), '--capture'],
                   cwd=REPO, check=True)
    if not all(p.exists() for p in (CODEGEN / 'register_functions.cpp', PARALLEL, VULKAN)):
        raise RuntimeError('canonical codegen, paraLLEl source, or Vulkan loader absent')
    budget()
    pin = subprocess.check_output(['git', '-C', str(FORK), 'rev-parse', 'fork/ssx3'], text=True).strip()
    remote = subprocess.check_output(['git', '-C', str(FORK), 'ls-remote', 'fork',
                                      'refs/heads/ssx3'], text=True).split()[0]
    if remote != pin:
        raise RuntimeError(f'fork/ssx3 tracking pin {pin} differs from remote {remote}')
    archive = ROOT / 'source.tar'
    with archive.open('wb') as f:
        subprocess.run(['git', '-C', str(FORK), 'archive', '--format=tar', pin], stdout=f, check=True)
    SRC.mkdir()
    with tarfile.open(archive) as tf:
        tf.extractall(SRC, filter='data')
    archive.unlink()
    receipt = {'fork_pin': pin, 'codegen_register_sha': [sha(CODEGEN / 'register_functions.cpp') for _ in range(2)],
               'capture_sha': [sha(CAPTURE) for _ in range(2)], 'commands': {}, 'status': 'started'}
    RESULT.write_text(json.dumps(receipt, indent=2) + '\n')
    if len(set(receipt['codegen_register_sha'])) != 1 or len(set(receipt['capture_sha'])) != 1:
        raise RuntimeError('codegen or capture SHA pair mismatch')
    try:
        receipt['commands']['configure'] = run('configure', ['cmake', '-S', str(SRC), '-B', str(BUILD),
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', f'-DPS2X_GAME_CODEGEN_DIR={CODEGEN}',
            '-DPS2X_GS_SHADOW_PARALLEL=ON', f'-DPS2X_PARALLEL_GS_SOURCE_DIR={PARALLEL}',
            '-DPS2X_ENABLE_RUNTIME_LOGS=OFF', '-DPS2X_ENABLE_AGRESSIVE_LOGS=OFF'], cwd=ROOT)
        budget()
        receipt['commands']['build'] = run('build', ['nice', '-n', '10', 'cmake', '--build', str(BUILD),
            '--target', 'ps2x_tests', '-j8'], cwd=ROOT, timeout=1800)
        receipt['binary_sha'] = [sha(BUILD / 'ps2xTest/ps2x_tests') for _ in range(2)]
        budget()
        for backend in ('cpu', 'parallel'):
            ppm = ROOT / f'{backend}-ppm'
            ppm.mkdir()
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith('PS2X_GS_REPLAY_') and k not in
                   ('PS2X_GS_BACKEND', 'PS2X_GS_CAPTURE', 'PS2X_GS_CAPTURE_STOP_TICK')}
            env.update(PS2X_GS_REPLAY_CAPTURE=str(CAPTURE), PS2X_GS_REPLAY_PPM_TICKS='2050',
                       PS2X_GS_REPLAY_PPM_DIR=str(ppm), PS2X_GS_REPLAY_STEP='50',
                       PS2X_GS_REPLAY_OUT=str(ROOT / f'{backend}.hashes'))
            if backend == 'parallel':
                env['PS2X_GS_REPLAY_BACKEND'] = 'parallel'
                env['GRANITE_VULKAN_LIBRARY'] = str(VULKAN)
            receipt['commands'][backend] = run(backend, [str(BUILD / 'ps2xTest/ps2x_tests')],
                                               cwd=SRC, env=env, timeout=900)
            receipt['status'] = f'{backend} replay complete'
            RESULT.write_text(json.dumps(receipt, indent=2) + '\n')
            budget()
        receipt['status'] = 'both replays complete'
    except Exception as exc:
        receipt['status'] = 'first failed step: ' + str(exc)
        raise
    finally:
        receipt['scratch_bytes'] = usage()
        RESULT.write_text(json.dumps(receipt, indent=2) + '\n')
        budget()


if __name__ == '__main__':
    if sys.argv[1:] != ['--released-after-i27b']:
        raise SystemExit('N8D4 is prepared only; use --released-after-i27b after explicit orchestrator release')
    main()
