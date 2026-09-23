# X3 — orchestrator check (2026-09-23)

Spot-checked with `local/tooling/ee/ee-at`. The key rows are correct: the
16 jal sites, the back-edge `bnel` at 0x317190 → 0x317128, the limit load
`lw $v0,0x20($s0)` at 0x317188, the counter `$s1`, and the loop body
calls (vtable steps and `func_317530` with f12 = 10.0).

Nuance X3 missed: the patch-site increment `addiu $s1,$s1,1` at
**0x317184 is the delay slot of `jal func_317328` (cAppMan_checkHalt) at
0x317180**, so the counter increments once per checkHalt call on that
path. The "60 FPS 2 Players" patch (0x26310002) makes each pass count 2,
so it halves the passes per frame.

Metro sites: 0x230704 = `bc1t` (skip) after `c.lt.s $f1,$f0`;
0x230710 = `sw $v1(=0),0x34($v0)` with v0 = `*(gp+0x2A74)`. The published
patch zeroes both (a nop for the branch and a nop for the store of 0), so
the frame-skip flag at `[*(gp+0x2A74)+0x34]` is never cleared on that path.

Verdict: usable as the 120 Hz scoping map. Worker quality after the 09-23
thinking-budget fix: accurate and cited, with one missed delay-slot
relationship.
