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
import hashlib
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

    # P6M3: excluded-cache pre/post walk. list_tree must omit excluded
    # entries, an excluded cache change racing an included file's two-read
    # phase must NOT fail the snapshot, and an included-file change in the
    # same phase must still fail.
    spec3 = importlib.util.spec_from_file_location("source_manifest_p6m3", str(TOOL))
    assert spec3 is not None and spec3.loader is not None
    mod3 = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(mod3)  # type: ignore[union-attr]
    tree = mod3.list_tree(str(fork))
    tree_leaked = sorted(k for k in tree
                         if any(c in k.split("/") for c in mod3.EXCLUDE_NAMES))
    row("list_tree_omits_excluded",
        tree_leaked == [] and "build/ignored.o" not in tree and "README.md" in tree,
        f"leaked={tree_leaked} keys={len(tree)}")
    roots3 = {"fork": str(fork), "parallel": str(parallel),
              "codegen": str(codegen), "jni": str(jni)}
    caps3 = {"max_files": 100000, "max_bytes": 10_000_000_000}
    excl_victim = fork / "build/ignored.o"
    excl_orig = excl_victim.read_bytes()
    orig_read_twice = mod3.read_file_twice
    raced = {"n": 0}

    def excl_race_read(path, *a, **k):
        if raced["n"] == 0:
            raced["n"] += 1
            excl_victim.write_bytes(excl_orig + b"\n// cache churn\n")
        return orig_read_twice(path, *a, **k)

    mod3.read_file_twice = excl_race_read  # type: ignore[attr-defined]
    try:
        man_race = mod3.build_manifest(roots3, dict(caps3))
        excl_race_ok = True
        excl_race_detail = f"aggregate={man_race['aggregate_sha256'][:16]}"
    except mod3.SnapshotError as e:
        excl_race_ok = False
        excl_race_detail = f"SnapshotError: {e}"
    finally:
        mod3.read_file_twice = orig_read_twice  # type: ignore[attr-defined]
        excl_victim.write_bytes(excl_orig)
    row("excluded_race_does_not_fail", excl_race_ok, excl_race_detail)

    incl_victim = fork / "ps2xRuntime/src/lib/gs/gs_frontend.cpp"
    incl_orig = incl_victim.read_bytes()
    raced2 = {"n": 0}
    orig_read_twice2 = mod3.read_file_twice

    def incl_race_read(path, *a, **k):
        # Mutate a not-yet-read included file while the first file
        # (fork README.md) is read: two reads stay consistent, but the
        # pre/post lstat comparison must still catch it.
        if raced2["n"] == 0 and str(path).endswith("README.md"):
            raced2["n"] += 1
            incl_victim.write_bytes(incl_orig + b"\n// included churn\n")
        return orig_read_twice2(path, *a, **k)

    mod3.read_file_twice = incl_race_read  # type: ignore[attr-defined]
    try:
        mod3.build_manifest(roots3, dict(caps3))
        incl_race_ok = False
        incl_race_detail = "snapshot unexpectedly succeeded"
    except mod3.SnapshotError as e:
        incl_race_ok = "source root changed during snapshot" in str(e)
        incl_race_detail = f"SnapshotError: {e}"[:220]
    finally:
        mod3.read_file_twice = orig_read_twice2  # type: ignore[attr-defined]
        incl_victim.write_bytes(incl_orig)
    row("included_race_still_fails", incl_race_ok, incl_race_detail)

    # P6M4: exact upstream stub permitted; anything else under the runner
    # dir, or any byte change to the stub, fails on both snapshot and
    # verify. Runs after the P6M3 rows so their fixture bytes are
    # unchanged; the stub file is removed afterwards.
    spec4 = importlib.util.spec_from_file_location("source_manifest_p6m4", str(TOOL))
    assert spec4 is not None and spec4.loader is not None
    mod4 = importlib.util.module_from_spec(spec4)
    spec4.loader.exec_module(mod4)  # type: ignore[union-attr]
    STUB_REL = "ps2xRuntime/src/runner/register_functions.cpp"
    STUB_BYTES = (b'#include "ps2_runtime.h"\n'
                  b'#include "runtime/ps2_memory.h"\n'
                  b'\n'
                  b'extern const uint32_t g_ps2RecompiledFunctionTableBase = 0x00000000u;\n'
                  b'extern const uint32_t g_ps2RecompiledFunctionTableEnd = 0x01000000u;\n'
                  b'extern const uint32_t g_ps2RecompiledFunctionTableSlotCount = (g_ps2RecompiledFunctionTableEnd - g_ps2RecompiledFunctionTableBase) >> 2;\n'
                  b'PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable[g_ps2RecompiledFunctionTableSlotCount] = {};')
    row("runner_stub_bytes_match_pinned",
        len(STUB_BYTES) == mod4.RUNNER_STUB_SIZE
        and hashlib.sha256(STUB_BYTES).hexdigest() == mod4.RUNNER_STUB_SHA256,
        f"len={len(STUB_BYTES)} sha={hashlib.sha256(STUB_BYTES).hexdigest()[:16]}")
    stub_path = fork / STUB_REL
    write(stub_path, STUB_BYTES)
    rc, out = run_tool("snapshot", *base, "--out", str(tmp / "stub.json"))
    stub_entry_ok = False
    stub_detail = f"rc={rc}"
    if rc == 0:
        try:
            sm = json.loads((tmp / "stub.json").read_text())
            hits = [e for e in sm["entries"]
                    if (e["scope"], e["path"]) == ("fork", STUB_REL)]
            stub_entry_ok = (len(hits) == 1 and hits[0]["kind"] == "file"
                             and hits[0]["size"] == mod4.RUNNER_STUB_SIZE
                             and hits[0]["sha256"] == mod4.RUNNER_STUB_SHA256)
            stub_detail = (f"rc={rc} kind={hits[0]['kind'] if hits else None} "
                           f"size={hits[0]['size'] if hits else None} "
                           f"sha={(hits[0]['sha256'][:16] + '…') if hits else None}")
        except (json.JSONDecodeError, KeyError, OSError) as ex:
            stub_detail = f"rc={rc} parse-error={ex}"
    row("runner_stub_snapshot_passes", rc == 0 and stub_entry_ok, stub_detail)

    rc, out = run_tool("verify", "--manifest", str(tmp / "stub.json"), *base)
    row("runner_stub_verify_matches", rc == 0 and '"status": "match"' in out, f"rc={rc}")

    # Extra generated file alongside the exact stub fails both modes.
    write(fork / "ps2xRuntime/src/runner/gen.cpp", "// generated\n")
    rc, out = run_tool("snapshot", *base, "--out", str(tmp / "stub-extra.json"))
    row("runner_extra_with_stub_snapshot_fails",
        rc != 0 and "ps2xRuntime/src/runner" in out,
        f"rc={rc} last={out.strip().splitlines()[-1] if out.strip() else ''}"[:220])
    rc, out = run_tool("verify", "--manifest", str(tmp / "stub.json"), *base)
    row("runner_extra_with_stub_verify_fails",
        rc != 0 and "ps2xRuntime/src/runner" in out,
        f"rc={rc} last={out.strip().splitlines()[-1] if out.strip() else ''}"[:220])
    (fork / "ps2xRuntime/src/runner/gen.cpp").unlink()

    # Changed stub bytes fail both modes.
    stub_path.write_bytes(STUB_BYTES + b"\n// changed\n")
    rc, out = run_tool("snapshot", *base, "--out", str(tmp / "stub-changed.json"))
    row("runner_stub_changed_snapshot_fails",
        rc != 0 and "runner stub changed" in out,
        f"rc={rc} last={out.strip().splitlines()[-1] if out.strip() else ''}"[:220])
    rc, out = run_tool("verify", "--manifest", str(tmp / "stub.json"), *base)
    row("runner_stub_changed_verify_fails",
        rc != 0 and "runner stub changed" in out,
        f"rc={rc} last={out.strip().splitlines()[-1] if out.strip() else ''}"[:220])
    stub_path.unlink()

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
