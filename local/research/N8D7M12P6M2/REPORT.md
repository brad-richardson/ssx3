# N8D7M12 Part 6M2 — reusable source snapshot for the next APK (worker receipt)

Worker receipt. **No build, package, Odin/mini, lease, ssh/network, board/ledger/fork/config edits, or push.
No scan of the large real source roots.** Owns only `local/tooling/orch/source_manifest.py`
and `local/research/N8D7M12P6M2/`. Brief: `local/muse/prompts/N8D7M12P6M2.md`.
Prior: `local/research/N8D7M12P6M1/{REPORT.md,ORCH-GATE.md}`; P3 `source_gate.py`.

Goal: source-input collector for use immediately before/after the next Android source
transfer. Records all file bytes in four named clean input roots (fork `PS2Recomp`,
`parallel-gs` including Granite, external codegen, `jniLibs`) and detects a changed,
added or missing file across the transfer. **Source snapshot only: not proof that every
file compiled, nor that any historical APK used current bytes.** The package worker
separately captures build-system inputs, flags, native-member SHA, Build ID and APK SHA.

## 1. Tool

`local/tooling/orch/source_manifest.py` (stdlib only):

- CLI `snapshot --fork ROOT --parallel ROOT --codegen ROOT --jni ROOT --out FILE`
  [--max-files N] [--max-bytes N]; `verify --manifest FILE --fork ROOT ...`.
- Deterministic walk per root; scope-relative POSIX paths; size + SHA-256 from **two
  separate reads**; symlinks recorded by target without following.
- Fails on: two-read mismatch, unreadable file, path escaping a root, duplicate logical
  path, any generated file under fork `ps2xRuntime/src/runner/`, source-root change
  during snapshot (pre/post lstat listing compared), cap breach, non-regular entry.
- Excludes only `.git` (dir or worktree pointer file), `build`, `.cxx`, `.gradle`,
  `__pycache__` as path components; exclusion names + skip counts listed in output;
  nothing else is ever skipped.
- Stable aggregate SHA over canonical sorted entries; per-root Git HEAD/status/submodule
  recorded as **informational only** (byte entries remain authority).
- Atomic manifest write; verify reports added/missing/changed and exits nonzero.
- JSON deterministic except `created_utc` and the `git` block (named in
  `deterministic_except`).

## 2. Fixture checks (exact commands)

From `~/dev/ssx3` (fixture lives in a temp dir; real roots never scanned):

```sh
python3 local/research/N8D7M12P6M2/check.py   # builds temp four-root fixture, drives the CLI, writes check-result.json
```

`check.py` invokes the tool as (with temp paths substituted for each ROOT):

```sh
python3 local/tooling/orch/source_manifest.py snapshot --fork ROOT --parallel ROOT --codegen ROOT --jni ROOT --out FILE
python3 local/tooling/orch/source_manifest.py verify --manifest FILE --fork ROOT --parallel ROOT --codegen ROOT --jni ROOT
```

Fixture: fork `README.md` + `ps2xRuntime/src/lib/gs/gs_frontend.cpp` + symlink
`link_to_readme -> README.md`; parallel `gs/gs_interface.hpp` + nested Granite
`Granite/vulkan/memory_allocator.cpp`; codegen `register_functions.cpp` +
`sub_0001.cpp`; jni `arm64-v8a/libvulkan_freedreno.so` (fake ELF bytes);
excluded `fork/build/`, `parallel/.git/`, `parallel/.gradle/`,
`codegen/__pycache__/`, `jni/.cxx/`.

## 3. Outcomes (`check.py` 13/13, verdict A)

| Case | Result |
| --- | --- |
| two snapshots + verify match | pass, rc=0, `"status": "match"` |
| mutate one file → verify fails naming it | pass, rc=1, `changed=["codegen:sub_0001.cpp"]` |
| add + remove file → verify reports exact paths | pass, rc=1, `added=["fork:ADDED.txt"]`, `missing=["parallel:gs/gs_interface.hpp"]` |
| excluded cache dirs absent | pass, `leaked=[]`; manifest lists exclusion names + per-scope skip counts (1/2/1/1, 5 total) |
| generated runner file fails snapshot | pass, rc=1 naming `ps2xRuntime/src/runner` |
| JSON determinism (except volatile metadata) | pass, two manifests identical except `created_utc`/`git`; fixture aggregate `27aeddc223b1333ed52ee5f899fed6755a16d7f30a54395e79de8f70ff25345b` |
| two-read mismatch handled in code | pass, injected-open flip makes `read_file_twice` raise `SnapshotError("two-read mismatch …")` |
| cap stops flood (`--max-files 3`) | pass, rc=1 `file-count cap exceeded` (caps cumulative across scopes) |
| symlink recorded by target, not followed | pass, `fork:link_to_readme` kind `symlink` target `README.md` |

## 4. Receipts

- `local/tooling/orch/source_manifest.py`
- `local/research/N8D7M12P6M2/{REPORT.md,check.py,check-result.json}`
- `check.py` builds a temp four-root fixture and runs/records the meaningful cases.

## 5. Gaps (hand-back, no package/GPU verdict)

1. Fixture-only: the large real roots were never scanned per the brief, so
   wall-time/byte cost on a codegen-scale tree (~9.5k files) is unmeasured.
2. Two-read mismatch proven via an injected-open unit path, not a live racing
   writer; the pre/post lstat comparison catches add/remove/size/mtime churn
   during a snapshot, but a change that lands and fully reverts between the
   two listings would rest only on the per-file double-read.
3. Fixture roots are not git checkouts, so the `git` block exercised only the
   `vcs:none` path; the git-backed HEAD/status/submodule path is code-reviewed,
   not fixture-proven. Either way it stays informational: byte entries are
   authority.
4. Exclusion semantics decided as component-name match at **any depth** (mirrors
   P3 `source_gate.py:45`); no input-root-model ambiguity required a stop.
5. The manifest records what is on disk, not what the build system compiles —
   the package worker must still capture the build-system file list, flags,
   native-member SHA, Build ID and APK SHA fresh at the next build (P6M1 §5).
6. No causal graphics verdict is made; no historical APK provenance is claimed.
