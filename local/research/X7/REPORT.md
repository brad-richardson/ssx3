# X7 dense Qwen source-table trial — incomplete (orchestrator audit)

This is an orchestrator record, not a worker verdict. The dense
Qwen3.8-27B opencode worker in w2:p2N ran for 12 minutes. It spent
7m35s reasoning after reading its brief, then wrote a placeholder
report with every predicate marked “not found.” It began reading the
correct source after a queued pin correction but did not complete a
table, LSP check or commit before the cap. The pane was closed. No
source edit, build, boot or device use came from X7.

The initial brief pointed to stale `~/dev/PS2Recomp` at `eac6cba`.
The orchestrator corrected it to the read-only E54D worktree at
`89bec9b` in the brief and prompt. No X7 conclusion from the stale
checkout is accepted.

## Orchestrator source check (not Qwen output)

At pinned `89bec9b`, `ps2xRecomp/src/lib/control_flow_emitter.cpp`
lines 407–425 emits `GPR_S32` for all four sign-branch families and
their likely/link cases. `ps2xRuntime/include/ps2_runtime_macros.h`
lines 1290–1293 shows `GPR_S32` extracts low 32 bits and `GPR_S64`
extracts low 64 bits. The table gives **current / mathematical signed
64-bit** truth values; the 64-bit behavior is the review hypothesis,
not a new PCSX2 oracle check.

| Family | Current source | `0x0000000180000000` | `0xffffffff00000000` | `0` |
| --- | --- | --- | --- | --- |
| BLTZ (+L/AL/ALL) | `GPR_S32 < 0`, line 420 | true / false | false / true | false / false |
| BGEZ (+L/AL/ALL) | `GPR_S32 >= 0`, line 425 | false / true | true / false | true / true |
| BLEZ (+L) | `GPR_S32 <= 0`, line 409 | true / false | true / true | true / true |
| BGTZ (+L) | `GPR_S32 > 0`, line 412 | false / true | false / false | false / false |

The source supports a 32-versus-64-bit disagreement on these vectors.
Hardware/PCSX2 oracle and game-site reach still need an E54 gate.
The trial indicates that lowering `thinking_budget` or supplying a
prewritten table skeleton is worth testing before another dense read.
