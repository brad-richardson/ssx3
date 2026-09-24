#!/usr/bin/env python3
"""ssx3 source-input snapshot for the next Android package (N8D7M12P6M2).

Records all file bytes in four named clean input roots -- fork PS2Recomp,
parallel-gs (including Granite), external codegen, jniLibs -- and detects a
changed, added or missing file across the transfer.

This is a SOURCE snapshot, not proof that every file compiled or that any
historical APK used current bytes. The package worker separately captures
build-system inputs, flags, native-member SHA, Build ID and APK SHA.

Usage:
  snapshot --fork ROOT --parallel ROOT --codegen ROOT --jni ROOT --out FILE
           [--max-files N] [--max-bytes N]
  verify   --manifest FILE --fork ROOT --parallel ROOT --codegen ROOT --jni ROOT
           [--max-files N] [--max-bytes N]

Rules (all enforced, stdlib only):
  * Deterministic walk; scope-relative POSIX paths; size + SHA-256 from TWO
    separate reads per file; symlinks recorded by target, never followed.
  * Fatal errors (nonzero exit): two-read mismatch, unreadable file, path
    escaping its root, duplicate logical path, any entry under fork
    ps2xRuntime/src/runner/, source-root change during the snapshot
    (pre/post lstat listing compared), file-count/byte cap breach, or any
    non-regular non-symlink entry.
  * Excludes ONLY path components named .git (directory or worktree pointer
    file), build, .cxx, .gradle, __pycache__. Exclusion names and skip
    counts are listed in the output; nothing else is ever skipped silently.
  * Stable aggregate SHA-256 over canonical sorted entries. One concise Git
    HEAD/status/submodule field per Git-backed root, INFORMATIONAL ONLY:
    byte entries remain authority.
  * Manifest written atomically. verify reports added/missing/changed
    entries and exits nonzero on any difference or rescan failure.
  * Manifest JSON is deterministic except `created_utc` and the `git` block
    (both named in `deterministic_except`). No file contents are stored.
"""

import argparse
import datetime
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from typing import NoReturn

FORMAT = "ssx3-source-manifest-v1"
SCOPES = ("fork", "parallel", "codegen", "jni")
EXCLUDE_NAMES = (".git", "build", ".cxx", ".gradle", "__pycache__")
RUNNER_PREFIX = "ps2xRuntime/src/runner"
CHUNK = 1024 * 1024
GIT_TRUNC_CHARS = 65536
GIT_TRUNC_LINES = 200


class SnapshotError(Exception):
    pass


def fail(msg) -> NoReturn:
    raise SnapshotError(msg)


def read_file_twice(path):
    """Return (size, sha256) from two independent full reads; fail on mismatch."""
    digests = []
    sizes = []
    for _ in range(2):
        h = hashlib.sha256()
        n = 0
        try:
            with open(path, "rb") as f:
                while True:
                    part = f.read(CHUNK)
                    if not part:
                        break
                    h.update(part)
                    n += len(part)
        except OSError as e:
            fail(f"unreadable file {path}: {e}")
        digests.append(h.hexdigest())
        sizes.append(n)
    if digests[0] != digests[1] or sizes[0] != sizes[1]:
        fail(f"two-read mismatch (file changed during read): {path}")
    return sizes[0], digests[0]


def read_link_twice(path):
    """Return symlink target via two independent readlink calls; fail on mismatch."""
    try:
        first = os.readlink(path)
        second = os.readlink(path)
    except OSError as e:
        fail(f"unreadable symlink {path}: {e}")
    if first != second:
        fail(f"two-read mismatch (symlink changed during read): {path}")
    return first


def is_excluded(rel_posix):
    return any(part in EXCLUDE_NAMES for part in rel_posix.split("/"))


def list_tree(root):
    """lstat-only listing: {rel_posix: (kind, size, mtime_ns)}; kind in dir/file/link/other."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames + dirnames):
            full = os.path.join(dirpath, name)
            try:
                st = os.lstat(full)
            except OSError as e:
                fail(f"unreadable entry {full}: {e}")
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel.startswith("../") or rel == ".." or os.path.isabs(rel):
                fail(f"path escapes root {root}: {full}")
            if stat.S_ISDIR(st.st_mode):
                kind = "dir"
            elif stat.S_ISLNK(st.st_mode):
                kind = "link"
            elif stat.S_ISREG(st.st_mode):
                kind = "file"
            else:
                kind = "other"
            out[rel] = (kind, st.st_size, st.st_mtime_ns)
    return out


def scan_scope(scope, root, caps):
    entries = []
    skipped = 0
    skipped_samples = []
    scope_bytes = 0
    seen = set()

    pre = list_tree(root)

    def record(rel, kind, size, sha256, target):
        key = (scope, rel)
        if key in seen:
            fail(f"duplicate logical path: {scope}:{rel}")
        seen.add(key)
        entries.append(
            {
                "scope": scope,
                "path": rel,
                "kind": kind,
                "size": size,
                "sha256": sha256,
                "target": target,
            }
        )

    stack = [root]
    # Deterministic manual walk (sorted), never following symlinks.
    while stack:
        cur = stack.pop()
        try:
            names = sorted(os.listdir(cur))
        except OSError as e:
            fail(f"unreadable directory {cur}: {e}")
        # Reverse so pop() yields sorted order.
        for name in reversed(names):
            full = os.path.join(cur, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel.startswith("../") or rel == ".." or os.path.isabs(rel):
                fail(f"path escapes root {root}: {full}")
            try:
                st = os.lstat(full)
            except OSError as e:
                fail(f"unreadable entry {full}: {e}")
            if is_excluded(rel):
                skipped += 1
                if len(skipped_samples) < 50:
                    skipped_samples.append(f"{scope}:{rel}")
                continue
            if stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode):
                stack.append(full)
            elif stat.S_ISLNK(st.st_mode):
                # Two separate readlink reads above are the two-read check;
                # the target bytes are then hashed once for the entry.
                target = read_link_twice(full)
                blob = target.encode("utf-8", "surrogateescape")
                record(rel, "symlink", len(blob), hashlib.sha256(blob).hexdigest(), target)
            elif stat.S_ISREG(st.st_mode):
                size, digest = read_file_twice(full)
                scope_bytes += size
                # Caps are cumulative across all scopes so one wrongly
                # pointed root stops before flooding disk.
                caps["files_seen"] += 1
                caps["bytes_seen"] += size
                if caps["files_seen"] > caps["max_files"]:
                    fail(f"file-count cap exceeded ({caps['max_files']}) at {scope}:{rel}")
                if caps["bytes_seen"] > caps["max_bytes"]:
                    fail(f"byte cap exceeded ({caps['max_bytes']}) at {scope}:{rel}")
                record(rel, "file", size, digest, None)
            else:
                fail(f"unsupported entry (not file/symlink/dir): {full}")

    post = list_tree(root)
    if pre != post:
        added = sorted(set(post) - set(pre))
        removed = sorted(set(pre) - set(post))
        changed = sorted(k for k in set(pre) & set(post) if pre[k] != post[k])
        fail(
            "source root changed during snapshot %s: added=%s removed=%s changed=%s"
            % (root, added[:5], removed[:5], changed[:5])
        )

    entries.sort(key=lambda e: (e["scope"], e["path"]))
    return entries, skipped, sorted(skipped_samples), scope_bytes


def git_info(root):
    """Concise Git HEAD/status/submodule; INFORMATIONAL ONLY, never authority."""

    def run(args):
        try:
            p = subprocess.run(
                ["git", "-C", root] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            text = p.stdout.decode("utf-8", "replace")
            lines = text.splitlines()[:GIT_TRUNC_LINES]
            text = "\n".join(lines)[:GIT_TRUNC_CHARS]
            return p.returncode, text
        except (OSError, subprocess.SubprocessError) as e:
            return 127, f"<unavailable: {e}>"

    rc, toplevel = run(["rev-parse", "--show-toplevel"])
    if rc != 0:
        return {
            "vcs": "none",
            "note": "informational only; byte entries remain authority",
            "detail": (toplevel or "not a git checkout")[:512],
        }
    _, head = run(["rev-parse", "HEAD"])
    _, status = run(["status", "--short"])
    _, submodules = run(["submodule", "status"])
    return {
        "vcs": "git",
        "note": "informational only; byte entries remain authority",
        "head": head.strip()[:128],
        "status_short": status,
        "submodules": submodules,
    }


def aggregate_sha(entries):
    h = hashlib.sha256()
    for e in sorted(entries, key=lambda x: (x["scope"], x["path"])):
        line = "\x00".join(
            [e["scope"], e["path"], e["kind"], str(e["size"]), e["sha256"], e["target"] or ""]
        ) + "\n"
        h.update(line.encode("utf-8", "surrogateescape"))
    return h.hexdigest()


def build_manifest(roots, caps):
    caps = dict(caps, files_seen=0, bytes_seen=0)
    all_entries = []
    exclusions = {"names": sorted(EXCLUDE_NAMES), "skipped": {}, "skipped_samples": {}}
    counts = {}
    for scope in SCOPES:
        entries, skipped, samples, total = scan_scope(scope, roots[scope], caps)
        all_entries.extend(entries)
        exclusions["skipped"][scope] = skipped
        exclusions["skipped_samples"][scope] = samples
        counts[scope] = {"files": len(entries), "bytes": total}
    all_entries.sort(key=lambda e: (e["scope"], e["path"]))

    runner_hits = [
        f"{e['scope']}:{e['path']}"
        for e in all_entries
        if e["scope"] == "fork"
        and (e["path"] == RUNNER_PREFIX or e["path"].startswith(RUNNER_PREFIX + "/"))
    ]
    if runner_hits:
        fail(
            "generated files under fork ps2xRuntime/src/runner/ "
            f"({len(runner_hits)}): {runner_hits[:5]}"
        )

    manifest = {
        "format": FORMAT,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scopes": list(SCOPES),
        "exclusions": exclusions,
        "counts": counts,
        "entries": all_entries,
        "aggregate_sha256": aggregate_sha(all_entries),
        "git": {scope: git_info(roots[scope]) for scope in SCOPES},
        "deterministic_except": ["created_utc", "git"],
        "note": "source snapshot only; not proof of compilation or historical APK provenance",
    }
    return manifest


def cmd_snapshot(args):
    roots = {s: getattr(args, s) for s in SCOPES}
    for scope, root in roots.items():
        if not os.path.isdir(root):
            fail(f"--{scope} is not a directory: {root}")
        if os.path.islink(root):
            fail(f"--{scope} must not itself be a symlink: {root}")
    caps = {"max_files": args.max_files, "max_bytes": args.max_bytes}
    manifest = build_manifest(roots, caps)
    out = args.out
    outdir = os.path.dirname(os.path.abspath(out)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".source-manifest-", suffix=".tmp", dir=outdir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, out)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print(
        json.dumps(
            {
                "status": "ok",
                "out": out,
                "aggregate_sha256": manifest["aggregate_sha256"],
                "counts": manifest["counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def rescan_for_verify(manifest_path, roots, caps):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("format") != FORMAT:
        fail(f"unknown manifest format: {manifest.get('format')!r}")
    old = {(e["scope"], e["path"]): e for e in manifest["entries"]}
    caps = dict(caps, files_seen=0, bytes_seen=0)
    new_entries = []
    for scope in SCOPES:
        entries, _, _, _ = scan_scope(scope, roots[scope], caps)
        new_entries.extend(entries)
    # Runner check applies on verify too: generated files must fail, not diff.
    runner_hits = [
        f"{e['scope']}:{e['path']}"
        for e in new_entries
        if e["scope"] == "fork"
        and (e["path"] == RUNNER_PREFIX or e["path"].startswith(RUNNER_PREFIX + "/"))
    ]
    if runner_hits:
        fail(
            "generated files under fork ps2xRuntime/src/runner/ "
            f"({len(runner_hits)}): {runner_hits[:5]}"
        )
    new = {(e["scope"], e["path"]): e for e in new_entries}
    added = sorted(f"{s}:{p}" for (s, p) in (set(new) - set(old)))
    missing = sorted(f"{s}:{p}" for (s, p) in (set(old) - set(new)))
    changed = sorted(
        f"{s}:{p}"
        for (s, p) in (set(old) & set(new))
        if (
            old[(s, p)]["sha256"] != new[(s, p)]["sha256"]
            or old[(s, p)]["size"] != new[(s, p)]["size"]
            or old[(s, p)]["kind"] != new[(s, p)]["kind"]
            or (old[(s, p)].get("target") or "") != (new[(s, p)].get("target") or "")
        )
    )
    return manifest, new_entries, added, missing, changed


def cmd_verify(args):
    roots = {s: getattr(args, s) for s in SCOPES}
    caps = {"max_files": args.max_files, "max_bytes": args.max_bytes}
    try:
        manifest, new_entries, added, missing, changed = rescan_for_verify(
            args.manifest, roots, caps
        )
    except SnapshotError as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2, sort_keys=True))
        return 1
    actual = aggregate_sha(new_entries)
    ok = not added and not missing and not changed
    print(
        json.dumps(
            {
                "status": "match" if ok else "mismatch",
                "manifest": args.manifest,
                "aggregate_expected": manifest.get("aggregate_sha256"),
                "aggregate_actual": actual,
                "added": added,
                "missing": missing,
                "changed": changed,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("snapshot", "verify"):
        p = sub.add_parser(name)
        if name == "snapshot":
            p.add_argument("--out", required=True)
        else:
            p.add_argument("--manifest", required=True)
        for scope in SCOPES:
            p.add_argument(f"--{scope}", required=True)
        p.add_argument("--max-files", type=int, default=200000)
        p.add_argument("--max-bytes", type=int, default=50_000_000_000)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "snapshot":
            return cmd_snapshot(args)
        return cmd_verify(args)
    except SnapshotError as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2), file=sys.stderr)
        print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
