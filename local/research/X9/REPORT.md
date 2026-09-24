# X9 — bounded local sign-branch source table (orchestrator audit)

The dense Qwen3.8-27B worker used per-pane `thinking_budget=512` and
only the pinned 3.7 KiB [`source-excerpts.txt`](source-excerpts.txt)
from fork `1aaed05`. It filled the source table, but its first truth
cells were wrong. After orchestrator feedback it ran a Python signed
arithmetic check and fixed the cells, then wrote incorrect prose about
B and zero. The orchestrator corrected the prose below. No worker
verdict or commit was accepted. The pane closed after about 7 minutes
at 20.5k context against a 20k cap. No source edit, build, boot,
device use or push came from X9.

Values below are **current signed low-32 / mathematical signed low-64**.
The latter is the review hypothesis; the excerpt alone does not prove
PS2 hardware behavior. The orchestrator verified all 12 truth pairs
with a Python signed conversion after the pane closed.

| Family and shared variants | Current emitted predicate | A=`0x0000000180000000` | B=`0xffffffff00000000` | Zero |
| --- | --- | --- | --- | --- |
| BLTZ, BLTZL, BLTZAL, BLTZALL | `GPR_S32 < 0`, emitter line 420 | true / false | false / true | false / false |
| BGEZ, BGEZL, BGEZAL, BGEZALL | `GPR_S32 >= 0`, line 425 | false / true | true / false | true / true |
| BLEZ, BLEZL | `GPR_S32 <= 0`, line 409 | true / false | true / true | true / true |
| BGTZ, BGTZL | `GPR_S32 > 0`, line 412 | false / true | false / false | false / false |

`GPR_S32` extracts low 32 bits and `GPR_S64` low 64 bits (runtime
macro lines 1291,1293). A is `-2147483648` as s32 and
`+6442450944` as s64; B is `0` as s32 and `-4294967296` as s64.
A flips all four predicates. B flips BLTZ and BGEZ; BLEZ and BGTZ
agree for B. Zero agrees in all four families.

`emitConditionalBranch()` calls `conditionalBranchExpression()` at
emitter line 482 and uses that result as `branch_taken_0x<address>`.
Likely and link handling are separate at lines 469–495. The model
cited that connection accurately. Its mathematical prose required two
orchestrator corrections despite a supplied table skeleton and fixed
source excerpt. This is a model-capability result, not an E54 fix gate.
