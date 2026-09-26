# Task T1 — quiet the per-frame iOS render log (small C++ edit)

You are working in a git clone of a PS2 static-recompilation runtime at /work (C++20). You have no network except
the model API, no other repos, and no devices. Work only inside /work.

## Problem
`ps2xRuntime/src/lib/ps2_runtime.cpp`, inside an `#if defined(PS2X_IOS)` block (search for `[ios-render]`), prints a
line to stderr on **every presented frame** (~60 lines/second). That console spam costs time and makes iOS speed
measurements noisy. The information is still useful when the window size changes (the iPad can resize the app).

## Change
Print the `[ios-render]` line only (a) the first time this code runs and (b) whenever any of the four values
(screen width/height, render width/height) differs from the last printed values. Keep the exact same line format.
Keep `ps2x::ios::syncWindowSize();` where it is, called every frame as today. Use function-local `static` state in
the style of the surrounding code (the file already uses `static` locals for this kind of state). No new env vars,
no other files, no behaviour change outside that `#if defined(PS2X_IOS)` block.

## Verify (you cannot build for iOS here)
1. `git diff --stat` shows only `ps2xRuntime/src/lib/ps2_runtime.cpp`, and every changed line is inside the
   `#if defined(PS2X_IOS)` … `#endif` block around the log.
2. Extract your new block into a tiny standalone C++ file with stub functions (`GetScreenWidth()` etc. returning
   values you control, and a no-op `syncWindowSize`), compile it with `clang++ -std=c++20 -Wall -Wextra`, and run it
   through a sequence of sizes (same, same, changed, same, changed back) showing it prints exactly 3 lines. Put that
   test at `/work/t1_check.cpp` and its output at `/work/t1_check.txt`.
3. Write `/work/T1_REPORT.md`: what you changed (quote the final block), the check output, anything you were unsure of.

Do not commit. Do not touch any other file. Stop when done.
