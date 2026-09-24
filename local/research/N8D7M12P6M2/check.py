#!/usr/bin/env python3
"""N8D7M12P6M2 acceptance checker: fixture-only snapshot/verify cases.

Builds a tiny temporary four-root fixture (nested Granite file, two codegen
files, a fake JNI binary, a symlink, excluded cache dirs) and drives
local/tooling/orch/source_manifest.py through the meaningful cases:
two snapshots + verify match; mutate one file -> verify fails naming it;
add + remove -> verify reports exact paths; cache exclusions absent;
generated runner file fails; JSON determinism; two-read mismatch path.
Writes check-result.json. No real-root scan, no build, no device action.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "../../tooling/orch/source_manifest.py"
TOOL = TOOL.resolve()

rows = []
fails = []


def row(name, ok, detail=""):
    rows.append({"check": name, "pass": bool(ok), "detail": detail})
    if not ok:
        fails.append(name)


def run_tool(*argv):
    p = subprocess.run(
        [sys.executable, str(TOOL), *argv],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=120,
    )
    return p.returncode, p.stdout


def write(path, data: object = b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode()
    path.write_bytes(data)  # type: ignore[arg-type]


def main():
    tmp = Path(tempfile.mkdtemp(prefix="p6m2-fixture-"))
    fork = tmp / "fork"
    parallel = tmp / "parallel"
    codegen = tmp / "codegen"
    jni = tmp / "jni"

    # Fixture contents.
    write(fork / "README.md", "fork readme\n")
    write(fork / "ps2xRuntime/src/lib/gs/gs_frontend.cpp", "int f(){return 1;}\n")
    write(parallel / "gs/gs_interface.hpp", "#pragma once\n")
    write(parallel / "Granite/vulkan/memory_allocator.cpp", "// granite nested\n")
    write(codegen / "register_functions.cpp", "void reg(){}\n")
    write(codegen / "sub_0001.cpp", "void s1(){}\n")
    write(jni / "arm64-v8a/libvulkan_freedreno.so", b"\x7fELF-fake-turnip")
    (fork / "link_to_readme").symlink_to("README.md")
    # Excluded cache/control names (must not appear in the manifest).
    write(fork / "build/ignored.o", "obj")
    write(parallel / ".git/objects/x", "gitobj")
    write(codegen / "__pycache__/p.pyc", "pyc")
    write(jni / ".cxx/cache.txt", "cxx")
    write(parallel / ".gradle/state.bin", "gradle")

    man_a = tmp / "a.json"
    man_b = tmp / "b.json"
    base = ["--fork", str(fork), "--parallel", str(parallel),
            "--codegen", str(codegen), "--jni", str(jni)]

    rc, out = run_tool("snapshot", *base, "--out", str(man_a))
    row("snapshot_a_ok", rc == 0, out.strip().splitlines()[-1] if out.strip() else f"rc={rc}")
    rc, out = run_tool("snapshot", *base, "--out", str(man_b))
    row("snapshot_b_ok", rc == 0, out.strip().splitlines()[-1] if out.strip() else f"rc={rc}")
    if not (man_a.exists() and man_b.exists()):
        row("fixture_aborted", False, "a snapshot failed; see rows above")
        return finish()

    a = json.loads(man_a.read_text())
    b = json.loads(man_b.read_text())

    rc, out = run_tool("verify", "--manifest", str(man_a), *base)
    row("verify_match", rc == 0 and '"status": "match"' in out, f"rc={rc}")

    # Determinism: everything except created_utc and git must be identical.
    def stable(m):
        m = dict(m)
        m.pop("created_utc", None)
        m.pop("git", None)
        return m
    row("json_deterministic", stable(a) == stable(b),
        f"aggregate={a.get('aggregate_sha256')}")
    row("aggregate_present", bool(a.get("aggregate_sha256")), a.get("aggregate_sha256", ""))

    # Excluded cache dirs absent; symlink recorded by target.
    paths = {(e["scope"], e["path"]) for e in a["entries"]}
    leaked = sorted(f"{s}:{p}" for (s, p) in paths
                    if any(c in p.split("/") for c in ("build", ".git", ".cxx", ".gradle", "__pycache__")))
    row("exclusions_absent", leaked == [], f"leaked={leaked}")
    row("exclusions_listed", a.get("exclusions", {}).get("names") == sorted(a["exclusions"]["names"])
        and sum(a["exclusions"]["skipped"].values()) == 5,
        json.dumps(a.get("exclusions", {}).get("skipped")))
    links = [e for e in a["entries"] if e["kind"] == "symlink"]
    row("symlink_recorded", len(links) == 1 and links[0]["target"] == "README.md"
        and (links[0]["scope"], links[0]["path"]) == ("fork", "link_to_readme"),
        json.dumps(links[0]) if links else "no symlink entry")

    # Mutate one file -> verify fails naming exactly it.
    target = codegen / "sub_0001.cpp"
    orig = target.read_bytes()
    target.write_bytes(orig + b"\n// mutated\n")
    rc, out = run_tool("verify", "--manifest", str(man_a), *base)
    try:
        rep = json.loads(out)
    except json.JSONDecodeError:
        rep = {}
    row("mutate_fails_naming_file",
        rc != 0 and rep.get("changed") == ["codegen:sub_0001.cpp"],
        f"rc={rc} changed={rep.get('changed')}")
    target.write_bytes(orig)

    # Add + remove -> verify reports those exact paths.
    write(fork / "ADDED.txt", "new\n")
    (parallel / "gs/gs_interface.hpp").unlink()
    rc, out = run_tool("verify", "--manifest", str(man_a), *base)
    try:
        rep = json.loads(out)
    except json.JSONDecodeError:
        rep = {}
    row("add_remove_exact_paths",
        rc != 0 and rep.get("added") == ["fork:ADDED.txt"]
        and rep.get("missing") == ["parallel:gs/gs_interface.hpp"],
        f"rc={rc} added={rep.get('added')} missing={rep.get('missing')}")
    (fork / "ADDED.txt").unlink()
    write(parallel / "gs/gs_interface.hpp", "#pragma once\n")

    # Generated runner file fails the snapshot.
    write(fork / "ps2xRuntime/src/runner/gen.cpp", "// generated\n")
    rc, out = run_tool("snapshot", *base, "--out", str(tmp / "c.json"))
    row("runner_file_fails", rc != 0 and "ps2xRuntime/src/runner" in out,
        f"rc={rc} last={out.strip().splitlines()[-1] if out.strip() else ''}")
    (fork / "ps2xRuntime/src/runner/gen.cpp").unlink()

    # Two-read mismatch path: feed different bytes on successive opens.
    spec = importlib.util.spec_from_file_location("source_manifest", str(TOOL))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    real_open = open
    calls = {"n": 0}

    class Flip:
        def __init__(self, data):
            self._data = data
            self._pos = 0

        def read(self, n=-1):
            if n is None or n < 0:
                out = self._data[self._pos:]
                self._pos = len(self._data)
                return out
            out = self._data[self._pos:self._pos + n]
            self._pos += len(out)
            return out

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def flip_open(path, mode="r", *a, **k):
        if str(path).endswith("victim.bin") and "b" in mode:
            calls["n"] += 1
            return Flip(b"version-A" if calls["n"] % 2 == 1 else b"version-B")
        return real_open(path, mode, *a, **k)

    import builtins
    builtins.open = flip_open
    try:
        mod.read_file_twice(tmp / "victim.bin")
        two_read_ok = False
    except mod.SnapshotError as e:
        two_read_ok = "two-read mismatch" in str(e)
    finally:
        builtins.open = real_open
    row("two_read_mismatch_handled", two_read_ok, "read_file_twice raises SnapshotError on flip")

    # Caps: a wrongly pointed root stops early.
    rc, out = run_tool("snapshot", *base, "--out", str(tmp / "d.json"), "--max-files", "3")
    row("cap_stops_flood", rc != 0 and "cap exceeded" in out, f"rc={rc}")

    return finish()


def finish():
    verdict = "A" if not fails else "B"
    out = {"verdict": verdict, "rows": rows, "failing": fails,
           "note": "Fixture-only source-snapshot checks; no real-root scan, build, device, or package/GPU verdict."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    sys.exit(0 if verdict == "A" else 1)


if __name__ == "__main__":
    main()
