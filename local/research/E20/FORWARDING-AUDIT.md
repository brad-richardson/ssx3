| Mechanism audit | Source evidence / pending local proof |
|---|---|
| RTLD_NEXT | Selects the dependency-search mode; the exported-symbol result subsequently passes through generic interposition before dlsym returns it. This accounts for E19 receiving its replacement address and recursively calling itself. [Apple Loader.cpp](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/dyld/Loader.cpp#L3356) |
| Explicit dlopen handle | Narrows the symbol search but also uses exported-symbol lookup; it does not by itself prove bypass of generic interposition. An address comparison may demonstrate this safely without calling an unsafe candidate. [Apple DyldAPIs.cpp](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/dyld/DyldAPIs.cpp) |
| Selected repair to prove | Use the observer image's directly linked imports of the original functions. Image-specific interposition entries preserve that image's original binding; generic replacements apply elsewhere. [Apple RuntimeState](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/dyld/DyldRuntimeState.cpp), [image-specific lookup](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/dyld/Loader.cpp#L3530) |
| Version limit | These are pinned public-source explanations, not a claim that the installed macOS27.0/26A428 dyld is byte-identical. The local isolation address/call/output proof must establish actual host behavior. |
| Required local proof | Backend addresses belong to the intended libavcodec/libSystem images; observer enter/backend/return counts1:1; identical arguments, return codes and packet/frame bytes versus an uninstrumented process; nonrecursive real _Exit closure. |
| Current gate | Fork/generated/protected hashes verified. SSD detached before baseline suite launch; no baseline child, isolation build/run, full loaded regression or title boot has started. |
| Retention | `reference-sources.json` pins the Apple commit and full source gzip hashes; `carried-inputs.json` verifies E19's eight retained/authored data files unchanged, without copying/loading its failed dylib. |

| E20 FORWARDING AUDIT TAIL COMPLETE | Source mechanism only; local execution proof remains required. |
|---|---|
