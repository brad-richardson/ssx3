# X18 — DeepSeek V4.1 Flash Go parser repair pilot

Host-only repair of the N8D6C logcat vector parser. The released
`local/research/N8D6C/launch.py` is unchanged (evidence).

## Deliverable

| File | Bytes |
| --- | --- |
| `local/tooling/orch/tile_vector_v2.py` | 1718 |
| `local/research/X18/REPORT.md` | this file |

## Exact commands and results

```
$ python3 -m py_compile local/tooling/orch/tile_vector_v2.py
PYCOMPILE_OK

$ python3 local/tooling/orch/check_x18.py
PASS saved sampled/raw 896-word vectors and synthetic continuation/negative cases
EXIT=0
```

Checker gate (`local/tooling/orch/check_x18.py`), all assertions passed:
saved N8D6C log, kinds `sampled` and `raw` → `words=896`,
`len(values)=896`, `occupied=5894`, `active=39`,
`sha256=3f06a58ad6805c695a01c305fe06b52cc0d92198a6fb699aeee0c4ea09681ba5`
(equal to `EXPECTED_SHA` and to an independent `struct.pack` re-hash), plus
the synthetic 896-word continuation, double-comma, nondecimal, interrupted,
arbitrary-prefix and post-896-extra cases.

## Changed behavior

Copied the pure `tile_vector(lines, kind)` from
`local/research/N8D6C/launch.py:168-195`. One parsing change: in the
continuation branch, a single leading `,` on the payload is removed before
`rstrip(',').split(',')`:

```python
payload = match.group(1)
if payload.startswith(','):
    payload = payload[1:]
```

This accepts the saved comma-led continuation
(`... I ps2x : ,0,0,...,13,...`) while still rejecting a double comma
(`startswith(',')` strips one, the empty first field then fails
`isdecimal()`), nondecimal fields, missing words (loop ends < 896 →
`None`), overflow past 896, an interrupted continuation, and non-vector
prefix text (no prefix match / `[`-led payload → `break`). Return schema
(`words`, `occupied`, `active`, `sha256`, `values`) and the 896-word cap are
unchanged. `sha256` is kept as the hexdigest helper the released schema
uses.

## Failed attempt

First clean run after the leading-comma change still failed:

```
  File "local/tooling/orch/check_x18.py", line 28, in <module>
    assert result['sha256'] == EXPECTED_SHA
AssertionError
```

Diagnosed through the checker (the checker passes the log lines into the
module): the parsed values were already correct — the marker line carries
471 fields and the comma-led continuation 425 (471+425=896), and the packed
digest was `3f06a5…81ba5`. The mismatch was the module returning the
`hashlib` hash *object* (`from hashlib import sha256; sha256(packed)`)
while the checker compares `result['sha256']` to a hex *string*. Restored
the released parser's `sha256` hexdigest helper; the checker then passed.

## Gaps / notes

- `sha256` helper semantics inferred from the checker's string comparison
  and `vector-audit.json` `packed_sha256`; `launch.py` lines 125-195 were
  the only source read, so the helper's exact upstream definition was not
  inspected.
- The released `local/research/N8D6C/launch.py` was not edited.
- Host-only; no device, build, boot or GS run. No cause concluded beyond the
  parser change above.

Orchestrated-By: opencode
