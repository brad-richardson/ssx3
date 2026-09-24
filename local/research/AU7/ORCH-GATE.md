# AU7 orchestrator gate — stereo image restored; sound HLE folded into fork ssx3 (2026-09-24)

Read REPORT and worker commits `a5da0fa0` (step-1 stop) and `27804e94` (Part 2). Reviewed the two
keep-both conflict resolutions (`receipts/resolve-*.diff`): positional additions only, plus AU3's
own deletion of the AU2 spike call it supersedes. Branch `au7-snd` = `04f3ace` + AU2/AU3/AU5
(`ea2a10c` `812d7b6` `64b2f6d` `959f4ea`), suite 589/589, one leased E33-route boot.

Independent check: `midside.py ~/dev/ssx3-work/AU7/run/tag1-36k.wav` (`8795471e…be820`) vs PCSX2
tag-1: lag 107.552 s; L/R/Mid/Side NCC 1.0000, diff/ref 0.000; Side RMS 381.9 = 381.9 (AU6 was 312.5,
NCC 0.434). Worker's exact-sample read: 0.29% of samples differ, all by 1 LSB.

**Verdict A.** The AU6 side-channel loss (and AU4's ">2 kHz 9% residual") came from the pre-E54C
PINTEH/PINTH lane bug in the EE mixer; the current runtime reproduces PCSX2's tag-1 PCM to rounding.

**Fold (Brad asked, 09-24):** runner-dir diff `14b1e5cb..959f4ea` empty; fast-forward from
`04f3ace`; pushed `fork ssx3` → **`959f4ea`** (ls-remote confirmed). The sound clock now starts by
default when the game registers its cid-1 handler, so shipped builds (Mac/iOS/Android) play sound
and every boot carries the SND HLE work. Speed numbers after this fold are not comparable to the
E58 baseline without re-measuring. `045dd6a` (AU6 snapshot tap) stays off-branch. Clip sent to Brad:
`~/dev/ssx3-work/AU7/AU7-menu-tag1.m4a`.
