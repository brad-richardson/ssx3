# N8C1 — Turnip app-namespace dependency and call-path audit

Worker: Codex. Brief: `local/muse/prompts/N8C1.md`. Date: 2026-09-24. Read-only diagnosis; no source edit, build, install, launch, or push. Tables and one Part-2 candidate for the orchestrator, not a gate verdict.

## Pins and method

| Input | Pin / observation |
| --- | --- |
| Turnip v36 | `~/dev/ssx3-work/G43/inputs/libvulkan_freedreno.so`, 14,188,488 bytes, ELF64 AArch64; SHA-256 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` on two independent `shasum -a 256` reads before analysis. Dynamic flags include `BIND_NOW` and `NOW`. [ELF receipt](elf-audit.txt); [N8A pin](../N8A/REPORT.md). |
| Prior app observation | N8B2 APK SHA-256 `1096a28e2e343fbcfc1d28390ea72a8e3d2aee32f3c40b81102e773c50b190da`. Its one app launch located bundled Turnip, then `dlopen` failed on `libhardware.so` in `clns-7`, before HMI. [N8B2 report](../N8B2/REPORT.md), [same-PID log](../N8B2/logcat-pid.txt). |
| Odin read | Serial `622c49b1`, Android SDK 35. Claimed `/data/local/tmp/mg/LEASE` as `N8C1 read-only audit` before inspection; released and verified `LEASE_FREE N8C1 done`. Seven small system ELFs copied to `~/dev/ssx3-work/N8C1/inputs/` (1.5 MiB total), outside Git. Every copied SHA matched two device reads. [Device receipt](device-audit.txt). |

## Direct driver dependencies and required symbol

The driver has exactly eight `DT_NEEDED` entries. The Odin `/system/etc/public.libraries.txt` lists all but `libhardware.so`. [ELF receipt](elf-audit.txt), [device receipt](device-audit.txt). “Present” means on disk, not available to the app namespace.

| Turnip `DT_NEEDED` | Public app list? | Odin presence |
| --- | --- | --- |
| `libhardware.so` | No | `/system/lib64/libhardware.so` (also distinct vendor and VNDK copies); N8B2 proved it unavailable in app namespace. |
| `liblog.so` | Yes | `/system/lib64/liblog.so` |
| `libnativewindow.so` | Yes | `/system/lib64/libnativewindow.so` |
| `libsync.so` | Yes | `/system/lib64/libsync.so` |
| `libm.so` | Yes | `/system/lib64/libm.so`, symlink to runtime APEX |
| `libz.so` | Yes | `/system/lib64/libz.so` |
| `libdl.so` | Yes | `/system/lib64/libdl.so`, symlink to runtime APEX |
| `libc.so` | Yes | `/system/lib64/libc.so`, symlink to runtime APEX |

The driver's **only strong undefined `hw_` symbol** is unversioned `hw_get_module` (dynsym 2117), with `R_AARCH64_JUMP_SLOT` relocation at `0xd8ce08`. The copied system `libhardware.so` exports unversioned `hw_get_module` at `0x4568` (16-byte wrapper) and `hw_get_module_by_class` at `0x4020`. `libhardware.so` imports `property_get` from `libcutils.so` and `android_load_sphal_library@LIBVNDKSUPPORT` from `libvndksupport.so`; the latter is exported as `@@LIBVNDKSUPPORT` at `0x4060`. [ELF receipt](elf-audit.txt); `llvm-readelf --dyn-syms --version-info -r`.

## Nonpublic static dependency closure

The table recursively follows `DT_NEEDED` from the **system** `/system/lib64/libhardware.so`. All seven names are absent from the Odin public app library list and present on the device. Hashes are two matching device `sha256sum` reads; every pulled copy matched its device hash. Public dependencies deeper in the chain are `liblog`, `libc`, `libm`, and `libdl`. [ELF receipt](elf-audit.txt), [device receipt](device-audit.txt).

| Nonpublic ELF / Odin SHA-256 | Own `DT_NEEDED` | Relevant symbol / implication |
| --- | --- | --- |
| `libhardware.so` — `1184f1203eadb78eeb1499c5481c1da96a79f9a17fef3eaedad0c52b40cb14fa` | `libcutils`, `liblog`, `libvndksupport`, `libc++`, `libc`, `libm`, `libdl` | Exports `hw_get_module`; imports `android_load_sphal_library@LIBVNDKSUPPORT`. |
| `libcutils.so` — `1cf4a17b4b0a8077c24aa04d34a88f8d3dcd96192f7b1587c333bf174c316ec8` | `liblog`, `libbase`, `libc++`, `libc`, `libm`, `libdl` | Exports unversioned `property_get` at `0xd950`. |
| `libvndksupport.so` — `63c932c8d244562d59502d2f6a64c82f999ba2175663e2ea5d7024e5828d44c3` | `libdl_android`, `liblog`, `libc++`, `libc`, `libm`, `libdl` | Exports `android_load_sphal_library@@LIBVNDKSUPPORT`; later vendor HAL loading may add dependencies. |
| `libc++.so` — `794eb8fafd7be35da3725e9ec0b15189c6f4f2544f5b78afd8a647dde5b69195` | `libc`, `libm`, `libdl` | Distinct from public `libstdc++.so`. |
| `libbase.so` — `08a388dcf0016d07d0f6ac04c736bca65cd5c9637bd36b8bf43e970e9f166e9c` | `liblog`, `libc++`, `libc`, `libm`, `libdl` | Reached through `libcutils`. |
| `libdl_android.so` — `10370703f28cb1aebc12f30cec1e6e3940e65975495e01c69642f29195b31adc` | `ld-android.so` | `/system/lib64` symlink to runtime APEX; weak undefined `__loader_android_*` namespace symbols. |
| `ld-android.so` — `599ae148e0abc4a93d0d20915338c494a2cbb5df5ba28257f0ac84e6f0e3447a` | None | Exports `__loader_android_dlopen_ext` at `0x4000`; private linker behavior untested in app namespace. |

This is the **static** closure. Dynamic `dlopen`/HAL calls can add more libraries; copying seven ELFs does not establish runtime sufficiency.

## Stripped-driver call path

No pinned Mesa driver source/build tree was found in the named G43 or N8B1 inputs. Bounded disassembly and four literal reads are in the [call-path receipt](call-path.txt). `.rodata` at `0x58207` is `gralloc`; all four sites pass that ID in `x0` and an output pointer at object offset `0x28` in `x1`.

| `hw_get_module` site | Observed condition / behavior | Limit |
| --- | --- | --- |
| `0xc92d50` in `0xc92d28` | On nonzero result logs “No gralloc hwmodule detected (video buffers won't be supported)” and still returns an object. On zero, reads module callback at offset `0x120`. | Later callbacks may require the module despite the nonnull object. |
| `0xc933f8` in `0xc933d0` | On nonzero result cleans up and returns null. On zero, checks metadata and callback at `0x118`. | Exact Vulkan trigger unresolved. |
| `0xc93758` in `0xc93730` | On nonzero result cleans up and returns null. On success checks metadata and calls `0xc92d28` at `0xc937ec`. | Exact Vulkan trigger unresolved. |
| `0xc938f8` in `0xc938c8` | On nonzero result cleans up and returns null. Success path checks gralloc metadata/callbacks and later calls `0xc92d28` at `0xc93aa8`. | Exact Vulkan trigger unresolved. |
| Selector `0xc92a8c` | Numeric choices 2, 3, 4, 5 call respective constructors; 0 tries several in sequence. | The stripped binary does **not** establish which choice normal SSX 3 rendering makes, or at which Vulkan call. |

`BIND_NOW` and the undefined symbol make `libhardware.so` a **load-time** requirement even if these gralloc paths never execute. N8B2 stopped at that stage. HAL lookup, Vulkan initialization, driver identity, and frames are later gates. A shim returning an error might pass loading; its gameplay behavior is unproved.

## Remedy comparison and one Part-2 candidate

| Remedy | Evidence | Cost / risk | Discriminating one-launch observation |
| --- | --- | --- | --- |
| **(a) App-local `libhardware.so` compatibility implementation** | One strong `hw_` import, unversioned `hw_get_module`; four gralloc call sites above. | One AArch64 ELF and one required ABI function. A `-ENOENT`/null response is only a **probe hypothesis**; `0xc92d28` shows it may cause later failure. Working gralloc callbacks could require a larger follow-up. | Record mapped shim path, calls/returns, loader progress, identity, and frame; distinguish no calls from a gralloc-path failure. |
| **(b) Package Odin system library plus closure** | Seven present, pinned private ELFs totaling 1.5 MiB and static graph above. | Seven binaries and coherent versions; `libvndksupport` → `libdl_android` → `ld-android` involves private linker behavior. A HAL could still be inaccessible. | Record first `dlerror`, mapped paths, `hw_get_module` return, then identity/frame. A new namespace/private linker failure refutes packaging sufficiency. |

**Smallest defensible one-candidate Part-2 build to test:** (a), as a narrow loader/use-path probe. Package one app-local `libhardware.so` exporting the required `int hw_get_module(const char *, const hw_module_t **)` ABI, returning documented `-ENOENT` with null output and logging call count. This is **not** a claim that error-return gralloc supports gameplay. Pin source and binary SHA, keep the shim and Turnip outside Git, and package both AArch64 APK members. Do not add a system-library fallback or second candidate to that build. No driver-source relink route is proposed: matching pinned Mesa source and build inputs were not found.

Part-2 gate: one build and, after APK member and two-read SHA checks, **one** Odin install/launch under lease using N8B2 stock inputs and I26-FAST, with battery/keyguard checks, 600 s cap, and force-stop cleanup. Record same-PID `dlopen`/`dlerror`, `dladdr(HMI)` and mapped shim identity, shim call count/return, HMI HAL ops, Granite GPU/API/driver, parallel `init ok` and nonzero GIF/present counts, and one visible stock race frame. [G43](../G43/REPORT.md) pins Turnip identity as Adreno 830, API 1.4.359, driver 26.2.99. System Vulkan, CPU fallback, no frame, gralloc error/crash, or a new dependency error refutes the corresponding path. Stop at the first definitive failure and hand back its stage. This diagnostic run yields no speed claim.

## Exact commands and gaps

Local: `shasum -a 256 ~/dev/ssx3-work/G43/inputs/libvulkan_freedreno.so` twice; `/opt/homebrew/opt/llvm/bin/llvm-readelf -d|--dyn-syms|--version-info|-r <ELF>`; `/opt/homebrew/opt/llvm/bin/llvm-objdump -d --no-show-raw-insn --start-address=0x… --stop-address=0x… <Turnip ELF>`. Exact bounded `-d` and disassembly invocations are in the [ELF](elf-audit.txt) and [call-path](call-path.txt) receipts. Exact lease, device SHA, pull and release commands with observed values are in the [device receipt](device-audit.txt). Copied ELFs are under 100 MiB; text receipts under 2 MiB.

Unknown: exact Vulkan call that selects gralloc, whether normal SSX 3 rendering uses it, app namespace lookup of packaged `libhardware.so`, error-response tolerance, private linker behavior after packaging system ELFs, dynamic vendor HAL closure, and driver-source relink feasibility without matching Mesa source/build recipe. No Part-1 observation resolves these.
