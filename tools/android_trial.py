#!/usr/bin/env python3
"""Android smoothing/interpolation trial port: build, run, analyze.

Ports the trial infrastructure (native/diagnostics/trial_control.h,
native_callback_trace.h, native_render_schedule.h,
native_pose_interpolation.h) into the Android headless build by relinking
the EGL runner with a trial-instrumented StaticRecompCore TU, the same
shape as the desktop isolated players (tools/gamecube_native_trace.py
build --scheduler --interpolation) and the iOS CMake TU swap
(native/ios/CMakeLists.txt). The headless driver is
native/diagnostics/android_trial_driver.h: env-scheduled, no UI.

  build    TU relink on the SSD (never in the repo); writes build.json
  run      push, seed configs, launch on the Odin over adb, pull receipts
  analyze  lifecycle/schedule/extras acceptance over a pulled probe trace

Receipts per run: probe JSONL (android_trial lifecycle, schedule rows,
interpolation rows), stderr (metrics speeds, FIFO panic marker),
screenshots (race timers), pre/post GFX.ini (clobber check).
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))
from native_gamecube import CORE_STACK  # noqa: E402

DIAG = ROOT / 'native/diagnostics'
PINS = json.loads((ROOT / 'native/dependencies.json').read_text())
DOL_SHA256 = 'b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce'
TU_RELATIVE = 'Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
HEADERS = ('trial_control.h', 'native_callback_trace.h', 'callback_timing.h',
           'render_deadline.h', 'native_render_schedule.h', 'pose_history.h',
           'native_pose_interpolation.h', 'android_trial_driver.h')
INCLUDE_ORDER = ('native_callback_trace.h', 'native_render_schedule.h',
                 'native_pose_interpolation.h', 'android_trial_driver.h')
INCLUDES_MARKER = 'namespace\n{'
DISPATCH_MARKER = '          const u32 runtime_dispatch_address = m_guest.pc;'
STEP_CALL = '          NativeTrialAndroid::Step(m_guest);\n'
TRIAL_DEFINE = '#define SSX_NATIVE_TRIAL_APP 1\n'
# Bottom-to-top inner-tree stack the EGL runner was built from: desktop
# CORE_STACK first, then the Android bring-up layers (no Vulkan: the trial
# binary relinks the EGL runner and validates on EGL first).
INNER_ANDROID_STACK = tuple(CORE_STACK) + (
    'recompcore-android-headless.patch',
    'recompcore-android-egl.patch',
)
DEVICE_DIR = '/data/local/tmp/mg'
TRIAL_BINARY = 'moderngekko-run-trial'
SAMPLER_SCRIPT = 'odin_sampler.sh'
SAMPLER_INTERVAL = 1
SAMPLER_MARGIN_SECS = 180
PANIC_MARKERS = ('FIFO is overflowed by GatherPipe', 'GatherPipeBursted')
# TrialControl Status order (Idle, Waiting, Running, Finished, Unavailable).
STATUS_RUNNING, STATUS_FINISHED, STATUS_UNAVAILABLE = 2, 3, 4
# TrialControl Kind order (Smoothing, F, Combined).
KIND_NAMES = {'smoothing': 0, 'f': 1, 'combined': 2}
METRICS_RE = re.compile(r'\[ssx3-metrics\] sample=(\d+) fps=([\d.]+) vps=([\d.]+) speed=([\d.]+)')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trial_env(at=None, kind='smoothing', secs=0):
    """Trial driver env; unset at means a control run (no request)."""
    if kind not in KIND_NAMES:
        raise ValueError(f'Trial kind must be one of {sorted(KIND_NAMES)}')
    env = {}
    if at is not None:
        env['SSX_ANDROID_TRIAL_AT'] = str(float(at))
    env['SSX_ANDROID_TRIAL_KIND'] = kind
    env['SSX_ANDROID_TRIAL_SECS'] = str(float(secs))
    if float(env['SSX_ANDROID_TRIAL_SECS']) < 0:
        raise ValueError('Trial secs must be >= 0')
    if at is not None and float(env['SSX_ANDROID_TRIAL_AT']) < 0:
        raise ValueError('Trial at must be >= 0')
    return env


def screenshot_env(seconds):
    """Screenshot env; 0 disables capture for unperturbed trial windows.

    The runner keys capture off the presence of SSX3_SCREENSHOTS (a 0
    cadence would fall back to its 15 s default), so disabling means
    omitting the variable, not zeroing it. PNG deflate + readbacks run
    beside the trial, so profile-grade runs should pass 0."""
    if seconds == 0:
        return {}
    if seconds < 0:
        raise ValueError('Screenshot seconds must be >= 0')
    return {'SSX3_SCREENSHOTS': '1', 'SSX3_SCREENSHOT_SECONDS': str(seconds)}


def seed_gfx_ini(text, immediate=True):
    """Set [Hacks] ImmediateXFBEnable/CapImmediateXFB, preserving other lines.

    The smoothing schedule requires the immediate-XFB copy path (the probe
    reports invalid_immediate_copy_setup without it). GFX.ini is seeded
    before launch like the iOS app and gamecube_schedule_check.py do; the
    run pulls it back afterward to prove it survived.
    """
    want = {'immediatexfbenable': 'True' if immediate else 'False',
            'capimmediatexfb': 'False'}
    names = {'immediatexfbenable': 'ImmediateXFBEnable',
             'capimmediatexfb': 'CapImmediateXFB'}
    lines = text.splitlines()
    found, in_hacks, hacks_seen, insert_at = set(), False, False, None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            if in_hacks and insert_at is None:
                insert_at = index
            in_hacks = stripped.lower() == '[hacks]'
            hacks_seen |= in_hacks
            continue
        if in_hacks and not stripped.startswith(('#', ';')) and '=' in line:
            key = line.split('=', 1)[0].strip().lower()
            if key in want:
                lines[index] = f'{line.split("=", 1)[0].rstrip()} = {want[key]}'
                found.add(key)
    missing = [names[k] for k in want if k not in found]
    if missing:
        addition = [f'{name} = {want[name.lower()]}' for name in missing]
        if hacks_seen:
            at = len(lines) if insert_at is None else insert_at
            lines[at:at] = addition
        else:
            lines += ['[Hacks]'] + addition
    return '\n'.join(lines) + '\n'


def generate_trial_source(source, header_dir):
    """Instrument a TU copy with the trial headers and driver step call."""
    for marker in (INCLUDES_MARKER, DISPATCH_MARKER):
        if source.count(marker) != 1:
            raise ValueError(f'Android trial injection point changed: {marker!r}')
    includes = ''.join(f'#include "{Path(header_dir) / name}"\n' for name in INCLUDE_ORDER)
    source = TRIAL_DEFINE + source
    source = source.replace(INCLUDES_MARKER, includes + INCLUDES_MARKER)
    return source.replace(DISPATCH_MARKER, STEP_CALL + DISPATCH_MARKER)


def adapt_compile_command(command, source, output):
    """Retarget a compile_commands.json command at a TU copy (no depfiles)."""
    args = shlex.split(command)
    args[args.index('-c') + 1] = str(source)
    args[args.index('-o') + 1] = str(output)
    for flag in ('-MF', '-MT'):
        if flag in args:
            position = args.index(flag)
            del args[position:position + 2]
    return args


def parse_link_command(commands_text):
    """Pick the moderngekko-run link argv out of `ninja -t commands` output."""
    for line in commands_text.splitlines():
        for segment in line.split('&&'):
            if ' -o ' not in f' {segment} ' or '-c' in segment.split():
                continue
            argv = shlex.split(segment)
            if '-o' in argv and argv[argv.index('-o') + 1].endswith('moderngekko-run'):
                return argv
    raise ValueError('No moderngekko-run link command in ninja output')


def adapt_link_command(argv, obj, output):
    """Retarget a link at a new binary with the trial TU ahead of archives.

    Explicit objects link unconditionally while archive members are pulled
    only for undefined symbols, so the trial TU ahead of the first archive
    shadows the original TU member the same way the desktop relink does.
    """
    argv = list(argv)
    argv[argv.index('-o') + 1] = str(output)
    for index, token in enumerate(argv):
        if token.endswith('.a'):
            argv.insert(index, str(obj))
            return argv
    raise ValueError('No archive in link command to shadow the trial TU against')


def reconstruct_tu(runner=None):
    """Pristine TU source plus the EGL stack, independent of live-tree drift.

    Builds a throwaway worktree at the pinned revision, applies the inner
    Android stack in order, and reads StaticRecompCore_Run.cpp back. The
    live tree may carry sibling-agent or iOS layers; the trial TU must be
    the exact source the EGL runner compiled.
    """
    runner = runner or (lambda argv, **kw: subprocess.run(argv, check=True, capture_output=True,
                                                         text=True, **kw))
    core = ROOT / 'third_party/ModernGekko/vendor/dolphin'
    work = Path(tempfile.mkdtemp(prefix='android-trial-tu-')) / 'tree'
    try:
        runner(['git', '-C', str(core), 'worktree', 'add', '--detach', str(work),
                PINS['recompcore_revision']])
        for name in INNER_ANDROID_STACK:
            runner(['git', '-C', str(work), 'apply', str(ROOT / 'native/patches' / name)])
        return (work / TU_RELATIVE).read_text()
    finally:
        runner(['git', '-C', str(core), 'worktree', 'remove', '--force', str(work)])
        shutil.rmtree(work.parent, ignore_errors=True)


def build(args):
    game = args.game.resolve()
    if ((game / 'sys/boot.bin').read_bytes()[:6] != b'GXBE69' or
            sha(game / 'sys/main.dol') != DOL_SHA256):
        raise ValueError('Trial callback addresses require the pinned GXBE69 executable')
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        raise ValueError('Android trial builds must live outside the repo (Extreme SSD)')
    out.mkdir(parents=True, exist_ok=False)
    build_dir = args.build_dir.resolve()
    production = build_dir / 'moderngekko-run'
    receipt = dict(schema=1, dol_sha256=DOL_SHA256, game=str(game),
                   build_dir=str(build_dir), stack=list(INNER_ANDROID_STACK),
                   production_runner_sha256=sha(production), commands=[])
    for name in HEADERS:
        (out / name).write_bytes((DIAG / name).read_bytes())
        receipt[f'{name}_sha256'] = sha(out / name)
    source = reconstruct_tu()
    receipt['original_tu_sha256'] = hashlib.sha256(source.encode()).hexdigest()
    trial_source = out / 'Core_Run.cpp'
    trial_source.write_text(generate_trial_source(source, out))
    entries = [e for e in json.loads((build_dir / 'compile_commands.json').read_text())
               if e['file'].endswith('StaticRecompCore_Run.cpp')]
    if len(entries) != 1:
        raise ValueError('Expected exactly one StaticRecompCore_Run.cpp compile entry')
    trial_obj = out / 'trial.o'

    def run(command, **kw):
        receipt['commands'].append(command if isinstance(command, str) else ' '.join(command))
        subprocess.run(command, cwd=build_dir, check=True, **kw)

    run(adapt_compile_command(entries[0]['command'], trial_source, trial_obj))
    ninja = args.ninja or shutil.which('ninja')
    if not ninja:
        raise ValueError('ninja is required to read the runner link command')
    commands = subprocess.run([ninja, '-C', str(build_dir), '-t', 'commands',
                               'moderngekko-run'], check=True, capture_output=True, text=True)
    trial_binary = out / TRIAL_BINARY
    run(adapt_link_command(parse_link_command(commands.stdout), trial_obj, trial_binary))
    if sha(production) != receipt['production_runner_sha256']:
        raise RuntimeError('Production runner changed during trial build')
    receipt['trial_object_sha256'] = sha(trial_obj)
    receipt['trial_binary_sha256'] = sha(trial_binary)
    if shutil.which('file'):
        kind = subprocess.run(['file', str(trial_binary)],
                              capture_output=True, text=True).stdout.strip()
        receipt['trial_binary_file'] = kind
        if 'aarch64' not in kind:
            raise RuntimeError(f'Trial binary is not aarch64: {kind}')
    (out / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(trial_binary)
    return receipt


def adb(args, serial=None, check=True, timeout=None):
    cmd = ['adb'] + (['-s', serial] if serial else []) + args
    return subprocess.run(cmd, check=check, capture_output=True, text=True, timeout=timeout)


def resolve_serial(explicit):
    attached = [line.split()[0] for line in adb(['devices']).stdout.splitlines()[1:]
                if line.strip() and line.split()[1] == 'device']
    if explicit:
        if explicit not in attached:
            raise ValueError(f'Device {explicit} is not attached: {attached}')
        return explicit
    if len(attached) != 1:
        raise ValueError(f'Need exactly one attached device, pass --serial: {attached}')
    return attached[0]


def remote_exists(serial, path):
    return adb(['shell', 'test', '-e', path], serial, check=False).returncode == 0


def ensure_idle(serial, user, idle_on):
    """Assert (on) or remove (off) the idle-skip line in a device user dir.

    Remote one-liners go as a single argv element: adb re-splits multiple
    args on the device shell, which breaks patterns containing spaces.
    """
    dolphin_ini = f'{DEVICE_DIR}/{user}/Config/Dolphin.ini'
    if idle_on:
        idle = adb(['shell', f"grep '^StaticRecompIdlePC = ' {dolphin_ini}"],
                   serial, check=False).stdout.strip()
        if not idle:
            raise ValueError(f'{user} has no idle-skip line for --idle on')
        return
    adb(['shell', f"sed -i '/^StaticRecompIdlePC = /d' {dolphin_ini}"], serial)
    if adb(['shell', 'grep', '-c', 'StaticRecompIdlePC', dolphin_ini],
           serial, check=False).stdout.strip() != '0':
        raise ValueError('Idle-skip line survived its removal')


def launch_command(tag, env, user, module, timeout, binary=TRIAL_BINARY,
                   graphics='OGL'):
    """One remote shell line: env-prefixed bounded run, backgrounded, prints PID.

    `cd X; ... &` (never `cd X && ... &`) so adb returns instantly instead
    of hanging on the session fds until the run ends. The --graphics flag
    overrides the template's GFXBackend, so Vulkan trials need no ini edit.
    """
    assignments = ' '.join(f'{key}={value}' for key, value in env.items())
    return (f'cd {DEVICE_DIR}; {assignments} timeout {timeout} ./{binary} --headless '
            f'--graphics {graphics} --game {DEVICE_DIR}/game --user-dir {DEVICE_DIR}/{user} '
            f'--module {DEVICE_DIR}/{module} >{tag}.out 2>{tag}.err & echo $!')


def await_exit(serial, pid, deadline, interval=5):
    """Poll until the remote PID is gone; False on deadline (device left alone)."""
    while time.time() < deadline:
        probe = adb(['shell', f'test -d /proc/{pid} && echo yes || echo no'], serial)
        if probe.stdout.strip() == 'no':
            return True
        time.sleep(interval)
    return False


# Thread roles for --affinity. The emu role matches the CPU thread's comm,
# which is currently the mislabeled 'GC Adapter Scan' (affinity hunt: the
# thread running StaticRecompCore::Run carries that comm; a separate scan
# thread was never observed on device). Keep this mapping beside the
# evidence (android-spike/affinity/) and update it if Dolphin renames it.
AFFINITY_ROLES = {'emu': 'GC Adapter Scan', 'video': 'Video thread'}


def affinity_spec(value):
    """Parse --affinity 'emu=80,video=40' into ((role, mask), ...) in order.

    Masks are bare hex (toybox taskset form, no 0x); 80 pins cpu7, 40 cpu6.
    """
    specs = []
    for chunk in value.split(','):
        role, eq, mask = chunk.partition('=')
        role, mask = role.strip(), mask.strip().lower().removeprefix('0x')
        if not eq or role not in AFFINITY_ROLES or not mask:
            raise ValueError(
                f'Affinity must be role=hexmask with roles {sorted(AFFINITY_ROLES)}: {chunk!r}')
        try:
            bits = int(mask, 16)
        except ValueError:
            raise ValueError(f'Affinity mask must be hex: {chunk!r}') from None
        if bits <= 0 or bits > 0xffffffff:
            raise ValueError(f'Affinity mask out of range: {chunk!r}')
        specs.append((role, mask))
    if not specs:
        raise ValueError('Affinity is empty')
    return tuple(specs)


def resolve_tids(listing, specs):
    """Map affinity specs to TIDs from a [(tid, comm)] listing.

    First comm match wins (short-lived Video/FrameDumping threads share
    names); raises when a role's thread has not appeared yet.
    """
    by_comm = {}
    for tid, comm in listing:
        by_comm.setdefault(comm, tid)
    resolved = {}
    for role, _ in specs:
        want = AFFINITY_ROLES[role]
        if want not in by_comm:
            raise ValueError(f'Thread {want!r} (role {role}) not found')
        resolved[role] = by_comm[want]
    return resolved


def child_pid(serial, wrapper_pid, runner=adb):
    """Real trial PID under the `timeout` wrapper recorded at launch."""
    out = runner(['shell', 'ps', '-A', '-o', 'PID,PPID,ARGS'], serial).stdout
    for line in out.splitlines():
        parts = line.split(None, 2)
        if (len(parts) == 3 and parts[1] == str(wrapper_pid)
                and TRIAL_BINARY in parts[2] and 'timeout' not in parts[2]):
            return parts[0]
    raise ValueError(f'No trial child under wrapper pid {wrapper_pid}')


def apply_affinity(serial, pid, specs, tag, runner=adb, timeout=30):
    """Pin threads by role via taskset; returns the manifest record.

    Polls for the threads (boot spawns them seconds after launch), pins each
    role, verifies the mask read back, and notes the metrics sample at
    intervention time so the race window can prove the pins predated it.
    Raises when a role never appears: a silently unpinned run would poison
    an A/B.
    """
    deadline = time.time() + timeout
    tids = None
    while time.time() < deadline:
        out = runner(['shell', f'grep . /proc/{pid}/task/*/comm'], serial).stdout
        listing = []
        for line in out.splitlines():
            path, _, comm = line.partition(':')
            parts = path.split('/')
            if len(parts) >= 5 and comm:
                listing.append((parts[4], comm))
        try:
            tids = resolve_tids(listing, specs)
        except ValueError:
            time.sleep(1)
            continue
        break
    if tids is None:
        raise ValueError(f'Affinity threads did not appear under pid {pid}')
    record = {}
    for role, mask in specs:
        tid = tids[role]
        set_out = runner(['shell', f'taskset -p {mask} {tid}'], serial).stdout
        if 'new affinity mask' not in set_out:
            raise ValueError(f'taskset {mask} on {role} tid {tid} failed: {set_out.strip()}')
        got = runner(['shell', f'taskset -p {tid}'], serial).stdout
        record[role] = dict(tid=tid, mask=mask,
                            verified=got.strip().split()[-1].lower() == mask)
    sample = runner(['shell', f"grep -o 'sample=[0-9]*' {DEVICE_DIR}/{tag}.err | tail -1"],
                    serial).stdout.strip()
    record['sample'] = sample or None
    return record


def launch_env(args, probe):
    """Remote env for a run: metrics, movie, probe, screenshots, trial."""
    env = dict(STATICRECOMP_VERBOSE='1', SSX3_RUNTIME_METRICS='1',
               SSX3_MOVIE_PLAY=f'{DEVICE_DIR}/{args.movie}', SSX_NATIVE_PROBE=probe,
               **screenshot_env(args.screenshot_seconds),
               **trial_env(args.trial_at, args.trial_kind, args.trial_secs))
    if args.probe_quiet:
        env['SSX_NATIVE_QUIET'] = '1'
    return env


def sampler_command(tag, pid, nticks, interval=SAMPLER_INTERVAL):
    """One remote shell line: background the odin sampler against a live PID.

    The sampler appends ticks to <tag>-sampler.log until nticks elapse or
    the PID exits; `cd X; ... &` (never `cd X && ... &`) so adb returns
    instantly instead of hanging on the session fds.
    """
    return (f'cd {DEVICE_DIR}; sh ./{SAMPLER_SCRIPT} {pid} '
            f'{tag}.err {tag}-sampler.log {nticks} {interval} '
            f'>sampler-{tag}.out 2>&1 & echo $!')


def run(args):
    serial = resolve_serial(args.serial)
    if 'moderngekko-run' in adb(['shell', 'ps', '-A'], serial).stdout:
        raise ValueError('A trial binary is already running on the device')
    dol = adb(['shell', 'sha256sum', f'{DEVICE_DIR}/game/sys/main.dol'], serial).stdout.split()[0]
    if dol != DOL_SHA256:
        raise ValueError(f'Device game DOL {dol} is not the pinned executable')
    binary = args.binary.resolve()
    digest = sha(binary)
    if args.build_json:
        receipt = json.loads(Path(args.build_json).read_text())
        if receipt.get('trial_binary_sha256') != digest:
            raise ValueError('Trial binary does not match its build receipt')
    tag, user = args.tag, f'user-{args.tag}'
    if remote_exists(serial, f'{DEVICE_DIR}/{user}'):
        raise ValueError(f'Preserving existing device dir {user}')
    probe = f'{DEVICE_DIR}/{tag}-probe.jsonl'
    if remote_exists(serial, probe):
        raise ValueError(f'Preserving existing device probe {probe}')
    print(f'pushing {binary.name} ({binary.stat().st_size} bytes)', flush=True)
    subprocess.run(['adb', '-s', serial, 'push', str(binary),
                    f'{DEVICE_DIR}/{TRIAL_BINARY}'], check=True)
    adb(['shell', 'chmod', '755', f'{DEVICE_DIR}/{TRIAL_BINARY}'], serial)
    pushed = adb(['shell', 'sha256sum', f'{DEVICE_DIR}/{TRIAL_BINARY}'], serial).stdout.split()[0]
    if pushed != digest:
        raise ValueError(f'Trial binary hash mismatch on device: {pushed} != {digest}')
    template = f'{DEVICE_DIR}/user-{args.template}'
    adb(['shell', 'cp', '-r', template, f'{DEVICE_DIR}/{user}'], serial)
    # The template carries its own screenshots; clear them so every pulled
    # shot belongs to this run.
    adb(['shell', 'rm', '-rf', f'{DEVICE_DIR}/{user}/ScreenShots'], serial)
    ensure_idle(serial, user, args.idle)
    with tempfile.TemporaryDirectory(prefix='android-trial-gfx-') as tmp:
        local_gfx = Path(tmp) / 'GFX.ini'
        subprocess.run(['adb', '-s', serial, 'pull', f'{DEVICE_DIR}/{user}/Config/GFX.ini',
                        str(local_gfx)], check=True, capture_output=True)
        seeded = seed_gfx_ini(local_gfx.read_text(), immediate=not args.no_immediate_xfb)
        local_gfx.write_text(seeded)
        subprocess.run(['adb', '-s', serial, 'push', str(local_gfx),
                        f'{DEVICE_DIR}/{user}/Config/GFX.ini'], check=True, capture_output=True)
    env = launch_env(args, probe)
    pid = adb(['shell', launch_command(tag, env, user, args.module, args.timeout,
                                       graphics=args.graphics)],
              serial).stdout.strip()
    print(f'launched pid {pid}: {tag} (trial_at={args.trial_at} kind={args.trial_kind})', flush=True)
    affinity_record = None
    real_pid = None
    if args.affinity:
        specs = affinity_spec(args.affinity)
        real_pid = child_pid(serial, pid)
        affinity_record = apply_affinity(serial, real_pid, specs, tag)
        print(f'affinity {affinity_record}', flush=True)
    sampler_record = None
    if args.sampler:
        if real_pid is None:
            real_pid = child_pid(serial, pid)
        subprocess.run(['adb', '-s', serial, 'push',
                        str(ROOT / 'tools' / SAMPLER_SCRIPT),
                        f'{DEVICE_DIR}/{SAMPLER_SCRIPT}'], check=True)
        pushed_sampler = adb(
            ['shell', 'sha256sum', f'{DEVICE_DIR}/{SAMPLER_SCRIPT}'],
            serial).stdout.split()[0]
        if pushed_sampler != sha(ROOT / 'tools' / SAMPLER_SCRIPT):
            raise ValueError('Sampler script hash mismatch on device')
        nticks = args.timeout + SAMPLER_MARGIN_SECS
        sampler_pid = adb(['shell', sampler_command(tag, real_pid, nticks)],
                          serial).stdout.strip()
        sampler_record = dict(pid=sampler_pid, nticks=nticks,
                              interval=SAMPLER_INTERVAL,
                              sha256=pushed_sampler)
        print(f'sampler {sampler_record}', flush=True)
    exited = await_exit(serial, pid, time.time() + args.timeout + 120)
    manifest = dict(schema=1, tag=tag, pid=pid, serial=serial, trial_binary_sha256=digest,
                    device_dol_sha256=dol, template=args.template, idle=bool(args.idle),
                    immediate_xfb=not args.no_immediate_xfb, env=env, timeout=args.timeout,
                    affinity=affinity_record, sampler=sampler_record,
                    exited=exited)
    out_dir = args.output.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    pulls = [(f'{tag}.out', f'{tag}.out'), (f'{tag}.err', f'{tag}.err'),
             (f'{tag}-probe.jsonl', f'{tag}-probe.jsonl'),
             (f'{user}/Config/GFX.ini', f'{tag}-GFX-post.ini'),
             (f'{user}/Config/Dolphin.ini', f'{tag}-Dolphin-post.ini')]
    if args.sampler:
        pulls.append((f'{tag}-sampler.log', f'{tag}-sampler.log'))
    for remote, local in pulls:
        result = subprocess.run(['adb', '-s', serial, 'pull', f'{DEVICE_DIR}/{remote}',
                                 str(out_dir / local)],
                                capture_output=True, text=True)
        manifest.setdefault('pulls', {})[local] = result.returncode == 0
        if result.returncode and local.endswith(('.out', '.err')):
            raise RuntimeError(f'Could not pull {remote}: {result.stderr.strip()}')
    shots = subprocess.run(['adb', '-s', serial, 'pull', f'{DEVICE_DIR}/{user}/ScreenShots',
                            str(out_dir / 'shots')], capture_output=True, text=True)
    manifest['pulls']['shots'] = shots.returncode == 0
    (out_dir / 'run.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: manifest[k] for k in ('tag', 'pid', 'exited')}, indent=2))
    if not exited:
        raise SystemExit(f'{tag} still running after its bound; receipts pulled anyway')
    return manifest


def guest_clean(rows):
    """Extras must not change watched guest state (desktop acceptance rule)."""
    return [r for r in rows
            if r.get('same_rider') != 1 or r.get('same_view') != 1 or
            r.get('state_before') != r.get('state_after') or
            r.get('rng_changed') != 0 or r.get('position_changed') != 0 or
            any(r.get(k) != [] for k in ('body_offsets', 'app_offsets', 'view_offsets'))]


def analyze_probe(rows, stderr_text='', shots=0):
    """Lifecycle/schedule/extras verdict over a pulled trial trace."""
    trial = [r for r in rows if r.get('event') == 'android_trial']
    actions = [r.get('action') for r in trial]
    assert_ordered = all(b.get('wall', 0) >= a.get('wall', 0)
                         for a, b in zip(trial, trial[1:]))
    configured = next((r for r in trial if r.get('action') == 'configured'), {})
    kind = configured.get('kind', 0)
    request_wall = next((r['wall'] for r in trial if r.get('action') == 'request'), None)
    complete_wall = next((r['wall'] for r in trial if r.get('action') == 'complete'), None)
    status_to = [r.get('to') for r in trial if r.get('action') == 'status']
    reached_running = STATUS_RUNNING in status_to
    finished = STATUS_FINISHED in status_to
    unavailable = STATUS_UNAVAILABLE in status_to
    limited = any(r.get('limited') == 1 for r in trial)
    final = next((r for r in reversed(trial)
                  if r.get('action') in ('complete', 'status')), {})
    schedule = {}
    for r in rows:
        if r.get('event') == 'schedule':
            schedule[r.get('action')] = schedule.get(r.get('action'), 0) + 1
    extras = [r for r in rows if r.get('event') == 'render' and r.get('repeat') and
              r.get('result', 0) & 255 and r.get('view_matrix_calls') and
              r.get('frame_end_calls')]
    blended = [r for r in rows if r.get('event') == 'interpolation' and r.get('repeat') and
               r.get('blended', 0) > 0]
    dirty = guest_clean(extras)
    patched = [r['wall'] for r in rows if r.get('event') == 'f_trial' and
               r.get('action') == 'patched']
    restored = [r['wall'] for r in rows if r.get('event') == 'f_trial' and
                r.get('action') == 'restored']
    consts_ok = bool(patched) and bool(restored) and min(restored) > min(patched)
    doubled = [r for r in rows if r.get('event') == 'update' and r.get('repeat') == 1 and
               (not patched or not restored or min(patched) < r.get('wall', 0) < min(restored))]
    speeds = [(int(m.group(1)), float(m.group(4))) for line in stderr_text.splitlines()
              if (m := METRICS_RE.match(line))]
    window = [s for sample, s in speeds
              if request_wall is not None and sample >= request_wall - 5 and
              (complete_wall is None or sample <= complete_wall + 5)]
    issues = []
    if not assert_ordered:
        issues.append('Lifecycle rows out of wall order')
    if request_wall is None:
        issues.append('Trial was never requested')
    if not reached_running:
        issues.append('Trial never reached Running')
    if unavailable or schedule.get('invalid_immediate_copy_setup'):
        issues.append('Immediate-XFB copy path missing (GFX knob did not take effect)')
    needs_extras, needs_doubled = kind != 1, kind != 0
    if needs_extras and not extras:
        issues.append('No complete injected draw observed')
    if needs_extras and not blended:
        issues.append('No blended extra draw observed')
    if dirty:
        issues.append(f'{len(dirty)} extra draws changed watched guest state')
    if needs_doubled and not doubled:
        issues.append('No clean doubled update observed')
    if needs_doubled and not consts_ok:
        issues.append('F consts were never patched then restored in order')
    result = dict(kind=kind, lifecycle=actions, request_wall=request_wall,
                  complete_wall=complete_wall, reached_running=reached_running,
                  finished=finished, limited=limited, unavailable=unavailable,
                  schedule=schedule, complete_extras=len(extras),
                  blended_extras=len(blended), dirty_extras=len(dirty),
                  doubled_updates=len(doubled), consts_ok=consts_ok,
                  final_counters={k: final.get(k) for k in
                                  ('frames', 'extras', 'doubled', 'blended')},
                  trial_window_speeds=dict(n=len(window),
                                           min=min(window) if window else None,
                                           mean=sum(window) / len(window) if window else None),
                  panic=any(m in stderr_text for m in PANIC_MARKERS),
                  screenshots=shots, issues=issues)
    result['pass'] = reached_running and not dirty and (
        (not needs_extras or bool(extras)) and (not needs_doubled or bool(doubled)))
    return result


def analyze(args):
    rows = [json.loads(line) for line in args.probe.read_text().splitlines() if line.strip()]
    stderr_text = args.stderr.read_text() if args.stderr else ''
    shots = sum(1 for p in args.shots.rglob('*') if p.is_file()) if args.shots else 0
    result = analyze_probe(rows, stderr_text, shots)
    result.update(probe=str(args.probe.resolve()))
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')
    if not result['pass']:
        raise SystemExit(1)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--game', type=Path, required=True, help='Local GXBE69 extraction (pin check)')
    p.add_argument('--build-dir', type=Path, required=True, help='Android EGL build dir (SSD)')
    p.add_argument('--output', type=Path, required=True, help='Trial build dir (SSD, fresh)')
    p.add_argument('--ninja', help='ninja binary (default: PATH)')
    p = sub.add_parser('run')
    p.add_argument('--binary', type=Path, required=True, help='Trial binary from build')
    p.add_argument('--build-json', type=Path, help='Verify the binary against its receipt')
    p.add_argument('--tag', required=True, help='Run tag (device files + user-<tag>)')
    p.add_argument('--output', type=Path, required=True, help='Local receipts dir (fresh)')
    p.add_argument('--template', default='m6h', help='Device user dir template (default m6h)')
    p.add_argument('--movie', default='m3-menu.dtm')
    p.add_argument('--module', default='gGXBE69_recomp.so')
    p.add_argument('--graphics', choices=('OGL', 'Vulkan', 'Null'), default='OGL',
                   help='GPU backend for the run (default OGL)')
    p.add_argument('--idle', choices=('on', 'off'), default='on')
    p.add_argument('--no-immediate-xfb', action='store_true',
                   help='Negative control: leave ImmediateXFBEnable off')
    p.add_argument('--trial-at', type=float, help='Request wall seconds (unset: control run)')
    p.add_argument('--trial-kind', choices=sorted(KIND_NAMES), default='smoothing')
    p.add_argument('--trial-secs', type=float, default=0,
                   help='Cancel N seconds after Running (0: natural end)')
    p.add_argument('--timeout', type=int, default=240)
    p.add_argument('--affinity',
                   help="Pin threads by role right after launch, e.g. "
                        "'emu=80,video=40' (bare hex masks: 80 pins cpu7, "
                        "40 cpu6 on the Odin 3)")
    p.add_argument('--sampler', action='store_true',
                   help='Push tools/odin_sampler.sh, start it at launch '
                        'against the real PID with a 1 s interval, and pull '
                        'its log into the receipts')
    p.add_argument('--probe-quiet', action='store_true',
                   help='Set SSX_NATIVE_QUIET=1 for control-probe runs')
    p.add_argument('--screenshot-seconds', type=int, default=2,
                   help='Capture cadence in seconds (default 2; 0 disables '
                        'capture for unperturbed trial windows)')
    p.add_argument('--serial', help='adb device serial when more than one is attached')
    p = sub.add_parser('analyze')
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--stderr', type=Path)
    p.add_argument('--shots', type=Path)
    p.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        build(args)
    elif args.command == 'run':
        if args.idle == 'on':
            args.idle = True
        else:
            args.idle = False
        run(args)
    else:
        analyze(args)


if __name__ == '__main__':
    main()
