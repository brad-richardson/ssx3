# X18B — DeepSeek Flash Go vector boundary repair

Host-only. Narrow follow-up to X18: preserve exactly **one** comma
separator across every continuation boundary of the saved N8D6C
`sampled`/`raw` 896-word `_tile_counts=` vectors. The released
`local/research/N8D6C/launch.py` and `local/tooling/orch/check_x18.py`
are unchanged.

## Deliverable

| File | Bytes |
| --- | --- |
| `local/tooling/orch/tile_vector_v2.py` | 1986 |
| `local/research/X18B/REPORT.md` | this file |

## Exact commands and results

```
$ python3 -m py_compile local/tooling/orch/tile_vector_v2.py
PYCOMPILE_OK

$ python3 local/tooling/orch/check_x18.py
PASS saved sampled/raw 896-word vectors and synthetic continuation/negative cases
EXIT=0
```

## Boundary table (expanded checker `check_x18.py`)

| Case | Construction | Expected | Observed |
| --- | --- | --- | --- |
| one comma before split | `first + ','` + tail without leading `,` | valid | valid (sha match) |
| one comma after split | `first` + tail leading `,` | valid | valid (sha match) |
| two across boundary | `first + ','` + tail leading `,` | reject | `None` |
| zero across boundary | `first` + tail without leading `,` | reject | `None` |
| double trailing comma | `first + ',,'` + tail without leading `,` | reject | `None` |
| double leading comma | `first` + tail with `,,` | reject | `None` |
| saved N8D6C log, `sampled` | same-PID 471+425 fields | valid 896 | `words=896`, `occupied=5894`, `active=39`, sha `3f06a5…81ba5` |
| saved N8D6C log, `raw` | same-PID 471+425 fields | valid 896 | `words=896`, `occupied=5894`, `active=39`, sha `3f06a5…81ba5` |
| nondecimal field | tail `,x,` | reject | `None` |
| incomplete (<896) | marker line only | reject | `None` |
| interrupted by new prefix | `raw_summary` line | reject | `None` |
| extra fields after 896 | `first, tail, ,999` | 896 (early return) | `words=896` |

The saved-log boundary is marker line with no trailing comma + continuation
leading with one comma (`logcat-all.txt.gz`, same-PID lines for 17446),
which now sums `pending(0) + leading(1) == 1`.

## Change

Replaced the blind `rstrip(',')` + single leading-comma strip with a
boundary-count check. Each segment records `trailing` commas stripped
(rejected if `> 1`) into `pending`; each continuation counts `leading`
commas and requires `pending + leading == 1` before stripping exactly that
one separator. Return schema (`words`, `occupied`, `active`, `sha256`,
`values`), the 896-word cap, same-PID prefix handling and the saved-log
positive result are unchanged.

## Failures

None in X18B. The first X18B edit was the final one; no retry was needed.
The prior X18 `hashlib` object-vs-hexdigest failure is recorded in
`local/research/X18/REPORT.md` and is not repeated here.

## Elapsed / context

Elapsed and context are not instrumented in the worker pane; wall was a
few minutes and context stayed under the <18k target as observed.

## Gaps

- Host-only: no device, build, boot, GS run or web access. No cause
  concluded beyond the parser boundary change above.
- Multi-line (>2 segment) vectors are handled by the same per-boundary
  rule but are not exercised by the checker; the saved log wraps once.
- The marker-line branch does not check a leading comma (none occurs in
  the saved log or checker inputs).

Orchestrated-By: opencode
