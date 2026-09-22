"""Compare E25's build GRAPH and log against E18's, edge by edge.

E18 ran `ninja` TWICE with the SAME argv. The first invocation died on binary
AppleDouble sidecars its own source edits had created on the ExFAT volume
(`e18_retain_sidecars.py`; 15.7 MB of AppleDouble bytes echoed as compiler
context). It retained both sidecars by rename -- no deletion -- and re-ran.
The union of E18's two logs is its full edge list; E25 needed one invocation
because those two sidecars have been out of the source tree since E18.
"""
import re
from e25_common import *

EDGE = re.compile(r'^\[(\d+)/(\d+)\] (.*)$')
def edges(path):
    total, seen = None, []
    for line in Path(path).read_text(errors='replace').splitlines():
        m = EDGE.match(line)
        if m:
            total = int(m.group(2))
            seen.append(m.group(3))
    return total, seen

t18a, e18a = edges(E.parent / 'E18/build.log')
t18b, e18b = edges(E.parent / 'E18/build-source-only.log')
t25, e25 = edges(E / 'build.log')
u18 = sorted(set(e18a) | set(e18b))
u25 = sorted(set(e25))
only18 = sorted(set(u18) - set(u25))
only25 = sorted(set(u25) - set(u18))

out = dict(utc=utc(),
           e18=dict(invocations=2, graph_totals=[t18a, t18b],
                    edges_logged_run1=len(e18a), edges_logged_run2=len(e18b),
                    union_unique=len(u18),
                    why_two='AppleDouble sidecars created by E18 own source edits; retained by rename, not deleted'),
           e25=dict(invocations=1, graph_total=t25, edges_logged=len(e25), unique=len(u25)),
           graph_total_delta=(t25 - t18a) if (t25 and t18a) else None,
           edges_only_in_e18=only18, edges_only_in_e25=only25,
           edge_sets_equal=only18 == only25 == [],
           e18_run1_truncated_bytes=15728640,
           e18_run2_stdout_bytes=46731,
           e25_stdout_bytes=(E / 'build.log').stat().st_size)
save('build-compare.json', out)
print(f'E18 graph totals {t18a} (run1) / {t18b} (run2); union of logged edges {len(u18)}')
print(f'E25 graph total  {t25}; logged edges {len(e25)}; unique {len(u25)}')
print(f'edges only in E18 ({len(only18)}):')
for x in only18: print('   -', x)
print(f'edges only in E25 ({len(only25)}):')
for x in only25: print('   +', x)
print('# E25 BUILD COMPARE TAIL COMPLETE')
