# Persistent share connection on macOS

The workbench share is `smb://YOUR_SMB_HOST/share`, mounted at `/Volumes/share`.
The PS2 source disc is
`/Volumes/share/brad/games/ps2/SSX Tricky (USA).iso` (2,902,425,600 bytes).
On September 12 the server was reachable but the volume was unmounted;
macOS reconnected successfully with its saved authentication.

A per-user LaunchAgent is installed as
`~/Library/LaunchAgents/com.ssx3.share-keepalive.plist`. Its compiled helper is
in `~/Library/Application Support/SSX3/ShareKeepalive/`. It runs at login and
each minute while this user is logged in. The calendar schedule coalesces
missed checks after sleep. It does not keep the computer awake.

The helper reads the kernel's mount table and asks NetFS to reconnect a
missing share using saved macOS authentication. It suppresses authentication
dialogs, limits each check to 25 seconds, and retries on the next scheduled
run. An already mounted share must match both the expected server/share and
the expected path; a conflicting filesystem or duplicate path is reported.
It does not read credentials or store passwords in the script or plist.

Regular checks do not browse the volume: macOS requires separate privacy
consent for background file reads, and those reads are unnecessary for
reconnecting a missing mount. macOS handles reconnection of existing SMB
sessions. A mount that remains registered but is stuck or busy is not
forcibly detached; this helper cannot repair the server or a changed password.

From the project directory:

```sh
# Show launchd state and the most recent check result.
python3 tools/macos/share_keepalive.py status

# Disable automatic reconnection; leave the current mount alone.
python3 tools/macos/share_keepalive.py uninstall
```

To recreate the setup or change the server address:

```sh
python3 tools/macos/share_keepalive.py prepare \
  --url smb://YOUR_SMB_HOST/share --mount /Volumes/share
python3 tools/macos/share_keepalive.py install
```

Preparation compiles against the installed macOS SDK and writes reviewable
files under ignored `local/macos/share-keepalive/`. Installation uses a fresh
executable inode and a local code signature, then loads the per-user agent.
The installed helper works independently of the repository checkout and
does not need Python to run on its schedule. The status file is replaced on
each check, so it does not grow over time.

If authentication changes, reconnect once through Finder → Go → Connect to
Server and save the updated credential in Keychain. Reserve the server's IP
address in the router's DHCP settings, or configure the job with a stable
hostname, so it continues reaching the same server after network restarts.
No router settings were changed by this setup.

Apple documents server connections as login items in
[Open items automatically when you log in](https://support.apple.com/en-au/guide/mac-help/-mh15189/mac).
The recurring retry uses a per-user agent as described in
[Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html).
The installed `launchd.plist(5)` manual is authoritative for calendar/wake
behavior; its `NetworkState` option is no longer implemented.

Validation on September 12: the helper compiled with warnings treated as
errors, passed existing-mount/conflicting-mount/invalid-URL checks, and the
installed calendar job restored an intentionally unmounted share in 46.2
seconds without a manual reconnect. The Tricky ISO was opened and read
after recovery. The local receipt is
`local/macos/share-keepalive/recovery-test.json`. Reboot/wake behavior is
configured through launchd; the Mac was not rebooted or put to sleep for
this test.
