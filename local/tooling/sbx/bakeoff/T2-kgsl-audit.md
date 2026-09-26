# Task T2 — audit blocking waits in Mesa Turnip's KGSL backend (read-only)

You are in a shallow git clone of Mesa (/work) at the branch `ssx3` of a fork. You have no network except the model
API. **Read-only task: do not modify any Mesa source file.** Your only output is `/work/T2_AUDIT.md`.

## Background
Turnip is Mesa's Vulkan driver for Qualcomm Adreno GPUs. On Android it talks to the kernel through KGSL ioctls, in
`src/freedreno/vulkan/tu_knl_kgsl.cc`. An Android game using this driver lost ~19 ms per frame because a Vulkan
"poll" (a wait with a zero timeout) turned into an **infinite** kernel wait: in `kgsl_syncobj_wait`, for a
timestamp-state sync object, `abs_timeout_ns == 0` produced a KGSL wait ioctl whose timeout meant "forever". The commit
`[FS2] tu/kgsl: poll instead of an infinite wait…` on this branch fixes that one case (find it with `git log`) by reading the retired timestamp instead.

## Task
Find every other place on the **submit, wait, fence/semaphore, and present/WSI** paths of this backend that can block
in the kernel or sleep, and classify each. For every entry give:
- file:line and the enclosing function (exact names — every name you cite must exist; check with grep);
- the ioctl or wait primitive (e.g. `IOCTL_KGSL_DEVICE_WAITTIMESTAMP_CTXTID`, `poll()`, a condition variable);
- how the timeout is computed (quote the code) and what a caller-supplied 0 / small / infinite timeout turns into;
- whether it can block indefinitely, and under what caller input;
- which Vulkan entry points reach it (trace the callers — cite each hop with file:line).

Then a short section: **"Any other zero- or short-timeout → infinite-wait patterns like the fixed one?"** — yes/no
per candidate, with the evidence. Mark anything you are unsure of as UNSURE rather than guessing.

Format: markdown tables. Don't propose patches beyond one sentence per finding. Stop when the report is written.
