## e49b: park hot_pc
| pc | role | count | first_ra | last_ra |
|---|---|---|---|---|
| `0x3b1050` | next-picture (vt+0x1c) | 1 | `0x3b0664` | `0x3b0664` |
| `0x402b38` | end check (sceMpegIsEnd shape) | 1 | `0x3b1094` | `0x3b1094` |
| `0x3b0fb8` | fetch (alloc + GetPicture) | 0 (absent) | | |
| `0x3b10d0` | alloc | 1 | `0x3b0fd0` | `0x3b0fd0` |
| `0x402a10` | sceMpegGetPicture | 1 | `0x3b1028` | `0x3b1028` |
| `0x3b0600` | picture fetch caller | 1 | `0x3ae5f8` | `0x3ae5f8` |
| `0x254c48` | SetPicture | 0 (absent) | | |
| `0x254dc0` | release caller | 0 (absent) | | |
| `0x3b0680` | release thunk | 0 (absent) | | |
| `0x3b1140` | release (breaker) | 0 (absent) | | |
| `0x3b0c58` | Open | 1 | `0x3b0528` | `0x3b0528` |
| `0x3b09a0` | Close | 0 (absent) | | |
| `0x3b0b40` | Open caller (Create/Init) | 1 | `0x3b0b30` | `0x3b0b30` |

log lines 108254, max frame tick 18001

## missing-target lines by target
none (0 lines)

## MPC CD reads (tick = last frame dump before the line)
- t247 lbn `0x13ba33`

## codec watch timeline, ticks < 400 (collapsed per tick+event)
- t247 codec ctor: 12 store(s) [0x587b18=0x3@0x3b0954, 0x587b1c=0x3@0x3b0960, 0x587b18=0x587b18@0x3b0968, 0x587b1c=0x587b18@0x3b0970 …]
- t247 node ctor: 5 store(s) [0x54884c=0x3@0x3b0820, 0x548848=0x3@0x3b0828, 0x548840=0x2@0x3b0830, 0x548850=0x0@0x3b0838 …]
- t247 open push free: 4 store(s) [0x587b20=0x548848@0x3b0e7c, 0x587b24=0x548848@0x3b0e80, 0x548848=0x587b20@0x3b0e84, 0x54884c=0x587b20@0x3b0e8c]
- t247 alloc: 9 store(s) [0x587b20=0x587b20@0x3b10f8, 0x587b24=0x587b20@0x3b1100, 0x54884c=0xb@0x3b1108, 0x548848=0xb@0x3b1110 …]

## frame-hash runs (first 40)
- t0..t41 `af249dc5`
- t45..t45 `c367a9cb`
- t46..t46 `d6efbd2d`
- t47..t47 `dc9d1299`
- t48..t48 `dc5c97a2`
- t49..t49 `a49d55bc`
- t50..t50 `e64aa57f`
- t52..t52 `5085a57d`
- t53..t53 `aa552c96`
- t54..t54 `8ef1b8dd`
- t55..t55 `6ad0033d`
- t56..t56 `7fb4b50`
- t59..t59 `4be0b824`
- t60..t60 `2f710822`
- t62..t62 `f9891032`
- t64..t64 `503c3ec7`
- t65..t65 `9e2f90a`
- t66..t66 `e0ceb839`
- t67..t67 `54d1361a`
- t69..t70 `b8e01365`
- t71..t74 `ac76bd05`
- t76..t77 `b8e01365`
- t78..t78 `9ea347e8`
- t79..t79 `54d1361a`
- t80..t80 `e0ceb839`
- t81..t81 `9e2f90a`
- t82..t82 `503c3ec7`
- t83..t83 `92d4972a`
- t84..t84 `97c5c48f`
- t85..t85 `8315e439`
- t87..t87 `b18001ca`
- t88..t88 `dc4fdae9`
- t89..t89 `c423e410`
- t90..t90 `7a56a2a2`
- t91..t91 `f6aff50d`
- t92..t92 `c31de20`
- t93..t93 `6debc162`
- t94..t111 `fd889dc5`
- t112..t112 `a74847b5`
- t113..t113 `a7d22a63`
(total runs 70)
