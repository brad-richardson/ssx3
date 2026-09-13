#!/usr/bin/env python3
"""Prepare, install, inspect or remove a per-user macOS SMB reconnect agent.

Prepare keeps generated configuration and binaries in ignored local/. Install
copies only the prepared files into this user's Library and loads the agent.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'local/macos/share-keepalive'
SUPPORT = Path.home() / 'Library/Application Support/SSX3/ShareKeepalive'
LABEL = 'com.ssx3.share-keepalive'
PLIST = Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')


def prepare(args):
    url = urlsplit(args.url)
    mount = Path(args.mount)
    if (url.scheme != 'smb' or not url.hostname or url.password is not None or
            url.port is not None or url.query or url.fragment or
            len(url.path.split('/')) != 2 or not url.path[1:] or
            mount.parent != Path('/Volumes') or unquote(url.path[1:]) != mount.name):
        raise ValueError('Use a password-free smb://host/share URL and matching /Volumes/share path')
    STAGE.mkdir(parents=True, exist_ok=True)
    subprocess.run(['/usr/bin/clang', '-fobjc-arc', '-Wall', '-Wextra', '-Werror',
                    '-framework', 'Foundation', '-framework', 'NetFS',
                    str(Path(__file__).with_suffix('.m')), '-o', str(STAGE / 'share-keepalive')], check=True)
    subprocess.run(['/usr/bin/codesign', '--force', '--sign', '-', '--identifier', LABEL,
                    str(STAGE / 'share-keepalive')], check=True)
    data = dict(Label=LABEL, ProgramArguments=[str(SUPPORT / 'share-keepalive'), args.url,
                str(mount), str(SUPPORT / 'status.json')],
                RunAtLoad=True, StartCalendarInterval={}, LimitLoadToSessionType='Aqua',
                ProcessType='Background', ThrottleInterval=30)
    (STAGE / PLIST.name).write_bytes(plistlib.dumps(data))
    subprocess.run(['/usr/bin/plutil', '-lint', str(STAGE / PLIST.name)], check=True)
    print(json.dumps(data, indent=2))
    print('Prepared:', STAGE)


def install():
    # Explicit install only; never alter an existing job without checking its owner.
    candidate = plistlib.loads((STAGE / PLIST.name).read_bytes())
    if PLIST.exists():
        current = plistlib.loads(PLIST.read_bytes())
        if current.get('Label') != LABEL or current.get('ProgramArguments', [None])[0] != str(SUPPORT / 'share-keepalive'):
            raise ValueError('An unrelated launch agent occupies the destination')
        subprocess.run(['/bin/launchctl', 'bootout', f'gui/{os.getuid()}', str(PLIST)], check=False)
    SUPPORT.mkdir(parents=True, exist_ok=True)
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    # A fresh inode avoids macOS retaining code-signature pages for an older
    # executable when the agent has already run from this path.
    with tempfile.NamedTemporaryFile(dir=SUPPORT, prefix='.share-keepalive-', delete=False) as temp:
        staged = Path(temp.name)
    try:
        shutil.copyfile(STAGE / 'share-keepalive', staged)
        staged.chmod(0o755)
        os.replace(staged, SUPPORT / 'share-keepalive')
    finally:
        staged.unlink(missing_ok=True)
    PLIST.write_bytes(plistlib.dumps(candidate))
    PLIST.chmod(0o644)
    subprocess.run(['/bin/launchctl', 'bootstrap', f'gui/{os.getuid()}', str(PLIST)], check=True)
    print('Installed:', PLIST)


def uninstall():
    if not PLIST.exists():
        print('Not installed')
        return
    data = plistlib.loads(PLIST.read_bytes())
    if data.get('ProgramArguments', [None])[0] != str(SUPPORT / 'share-keepalive'):
        raise ValueError('Unexpected launch agent; leaving it untouched')
    subprocess.run(['/bin/launchctl', 'bootout', f'gui/{os.getuid()}', str(PLIST)], check=True)
    PLIST.unlink()
    print('Automatic reconnect disabled; the mounted share is retained.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'install', 'status', 'uninstall'])
    parser.add_argument('--url')
    parser.add_argument('--mount')
    args = parser.parse_args()
    if args.command == 'prepare':
        if not args.url or not args.mount:
            parser.error('prepare requires --url and --mount')
        prepare(args)
    elif args.command == 'install':
        install()
    elif args.command == 'uninstall':
        uninstall()
    else:
        subprocess.run(['/bin/launchctl', 'print', f'gui/{os.getuid()}/{LABEL}'], check=True)
        status = SUPPORT / 'status.json'
        print(status.read_text() if status.exists() else 'No completed check recorded yet.')


if __name__ == '__main__':
    main()
