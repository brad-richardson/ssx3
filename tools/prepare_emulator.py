#!/usr/bin/env python3
"""Create a separate PCSX2 profile and launchers for the terrain experiments."""

import argparse
import configparser
import hashlib
import json
from pathlib import Path
import shlex
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory on the staging share")
    parser.add_argument("--source-profile", type=Path, default=Path.home() /
                        "Library/Application Support/PCSX2")
    parser.add_argument("--bios-dir", type=Path, default=Path.home() / "Downloads/PS2_BIOS")
    parser.add_argument("--app", type=Path, default=Path("/Applications/PCSX2-v2.8.2.app"))
    parser.add_argument("--games", type=Path, default=Path("/Volumes/share-1/brad/games/ps2"))
    parser.add_argument("--builds", type=Path, default=Path(
        "/Volumes/share-1/brad/games/ssx3-workbench/builds"))
    args = parser.parse_args()
    binary = args.app / "Contents/MacOS/PCSX2"
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    config.read(args.source_profile / "inis/PCSX2.ini")
    bios = args.bios_dir / config["Filenames"]["BIOS"]
    images = {
        "original": args.games / "SSX 3 (USA).iso",
        "control": args.builds / "control-001/SSX3-control.iso",
        "bump": args.builds / "bump-001/SSX3-bump.iso",
    }
    for path in (binary, bios, *images.values()):
        if not path.is_file():
            raise FileNotFoundError(path)
    args.output.mkdir(parents=True, exist_ok=False)
    # macOS PCSX2 appends its application name to the -datapath argument.
    data_root = args.output / "profile"
    profile = data_root / "PCSX2"
    for folder in ("inis", "bios", "memcards", "logs", "snaps", "sstates", "cache"):
        (profile / folder).mkdir(parents=True)
    copies = []
    sources = [bios, *[p for p in (bios.with_suffix(".nvm"), bios.with_suffix(".mec"))
                       if p.is_file()]]
    sources += list((args.source_profile / "memcards").glob("*.ps2"))
    for source in sources:
        folder = "memcards" if source.suffix == ".ps2" else "bios"
        destination = profile / folder / source.name
        shutil.copyfile(source, destination)
        checksum = hashlib.sha256(source.read_bytes()).hexdigest()
        if hashlib.sha256(destination.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Copy verification failed: {destination}")
        copies.append({"source": str(source), "copy": str(destination), "sha256": checksum})
    # Relative paths are resolved against this profile, not the user's profile.
    config["Folders"] = {
        "Bios": "bios", "Snapshots": "snaps", "Savestates": "sstates",
        "MemoryCards": "memcards", "Logs": "logs", "Cheats": "cheats",
        "Patches": "patches", "UserResources": "resources", "Cache": "cache",
        "Textures": "textures", "InputProfiles": "inputprofiles", "Videos": "videos",
        "DebuggerLayouts": "debuggerlayouts", "DebuggerSettings": "debuggersettings",
    }
    config["UI"]["SetupWizardIncomplete"] = "false"
    config["UI"]["StartFullscreen"] = "false"
    config["UI"]["ConfirmShutdown"] = "false"
    config["EmuCore"]["SaveStateOnShutdown"] = "false"
    config["EmuCore"]["EnableCheats"] = "false"
    config["Logging"]["EnableFileLogging"] = "true"
    config["Logging"]["EnableEEConsole"] = "true"
    config["Logging"]["EnableIOPConsole"] = "true"
    # Keyboard menu controls in this test profile; preserve the other bindings.
    for button, key in {"Start": "Return", "Cross": "X", "Circle": "C",
                        "Up": "Up", "Down": "Down", "Left": "Left", "Right": "Right"}.items():
        config["Pad1"][button] = f"Keyboard/{key}"
    config.remove_section("GameList")
    with (profile / "inis/PCSX2.ini").open("x") as stream:
        config.write(stream)
    for name, iso in images.items():
        argv = [str(binary), "-datapath", str(data_root), "-logfile",
                str(profile / "logs" / f"{name}.log"), "-batch", "-nofullscreen",
                "-fastboot", "--", str(iso)]
        launcher = args.output / f"launch-{name}.command"
        launcher.write_text("#!/bin/sh\nexec " + shlex.join(argv) + "\n")
        launcher.chmod(0o755)
    manifest = {"app": str(args.app), "profile": str(profile), "copied_files": copies,
                "images": {name: str(path) for name, path in images.items()},
                "note": "Launch one session at a time. Source memory cards and BIOS are untouched."}
    (args.output / "setup.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
