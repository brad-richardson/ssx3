# N2 transfer manifest (Mac SSD ↔ bytesize; generated guest code never to GitHub)

## C17 codegen set → bytesize

| Item | Value |
|---|---|
| Source | `/Volumes/Extreme SSD/ps2x-i17/codegen-output` (read-only census ×2: 9,455 `.cpp`, 2 headers, 265,956,572 B, 9,457 entries) |
| Tarball | `/Volumes/Extreme SSD/n2-scratch/c17-codegen.tar`, 273,988,608 B, 9,458 entries (9,457 + top dir), zero `._*` members (`COPYFILE_DISABLE=1`) |
| Tarball sha | `6b2332b6860b7bc90f9deb750d1c0f8356008e569f1269773d23394430e63c51` — 2 matching SSD reads, matched again on bytesize (Windows landing + ext4 copy) |
| Post-untar census | 9,455 / 2 / 9,457 / 265,956,572 B — exact match |
| Post-untar header shas | functions.h `e2fa11e8…` ✓, stubs.h `dbeee2f5…` ✓ |

## Staged headers (Mission-1 recovery, subset of the above)

`ps2_recompiled_functions.h` (794,469 B, `e2fa11e8…`) +
`ps2_recompiled_stubs.h` (14,976 B, `dbeee2f5…`): 2 SSD reads, scp,
bytesize sha-checked, staged into the clone's gitignored
`ps2xRuntime/include/` (repo-designated slot, `.gitignore:16-17`).

## H1 source reads (E-lane SSD clone, `git show` only, no checkout)

`eb3fb1636db953545f3e2794ac26b5542f8f80c2` (I10, +22) and
`193451a7040c42adbc60ae3ac34e78198c96cc4a` (I21 drop ext) applied by hand
onto `3adc0478` on bytesize-local branch `n2-android` (`695b96e`, never
pushed). Full port diff: `logs/m2b-full-diff.txt` (+29 CMakeLists, +2/−1
build.gradle). `ssx3` ref verified unmoved (`3adc0478`) after the commit.

## APK → Mac SSD

`/Volumes/Extreme SSD/n2-android/app-release.apk`, 270,957,997 B,
sha `21a9230c…` — bytesize build tree, bytesize stage, and Mac SSD ×2
reads all agree. NOT installed.
