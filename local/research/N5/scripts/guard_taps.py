#!/usr/bin/env python3
"""N5: compile-time guard for the guest-memory watch taps in ps2_runtime_macros.h.

PS2X_ENABLE_DIAG_TAPS=1 (desktop default): macros call the real E40-E44 trace
namespaces through aliases. =0 (Android default): the aliases point at constexpr
stubs, so every `if (false) ...` tap and its arguments compile to nothing.
Run from the PS2Recomp worktree root.
"""
import re, sys

MAC = 'ps2xRuntime/include/ps2_runtime_macros.h'
CML = 'ps2xRuntime/CMakeLists.txt'
NS = {'ps2_mpg_src_trace': 'ps2x_tap_mpg', 'ps2_e41_trace': 'ps2x_tap_e41',
      'ps2_e43_trace': 'ps2x_tap_e43', 'ps2_e44_trace': 'ps2x_tap_e44'}

s = open(MAC).read()
used = {ns: sorted(set(re.findall(ns + r'::(?:detail::)?([A-Za-z_][A-Za-z_0-9]*)', s))) for ns in NS}
includes = ''.join(f'#include "{ns}.h"\n' for ns in NS)
assert includes in s, 'include block not found as expected'


def stub(ns):
    preds, notes, scoped = [], [], []
    for name in used[ns]:
        if name.startswith('Scoped'):
            scoped.append(name)
        elif name.startswith('note'):
            notes.append(name)
        else:
            preds.append(name)
    lines = [f'namespace {NS[ns]}', '{']
    for n in preds:
        lines.append(f'template <class... A> constexpr bool {n}(A &&...) noexcept {{ return false; }}')
    for n in notes:
        lines.append(f'template <class... A> inline void {n}(A &&...) noexcept {{}}')
    if scoped:
        lines.append('namespace detail')
        lines.append('{')
        for n in scoped:
            lines.append(f'struct {n} {{ constexpr explicit {n}(bool) noexcept {{}} }};')
        lines.append('} // namespace detail')
    lines.append(f'}} // namespace {NS[ns]}')
    return '\n'.join(lines)


guard = ['// N5: compile-time switch for the E40-E44 guest-memory watch taps below.',
         '// PS2X_ENABLE_DIAG_TAPS=0 swaps the trace namespaces for constexpr stubs, so',
         '// the taps (and their __func__/argument setup) compile to nothing in every',
         '// generated function. CMake option of the same name; default ON off-Android.',
         '#ifndef PS2X_ENABLE_DIAG_TAPS',
         '#define PS2X_ENABLE_DIAG_TAPS 1',
         '#endif',
         '#if PS2X_ENABLE_DIAG_TAPS',
         includes.rstrip('\n')]
guard += [f'namespace {alias} = ::{ns};' for ns, alias in NS.items()]
guard += ['#else'] + [stub(ns) for ns in NS] + ['#endif // PS2X_ENABLE_DIAG_TAPS', '']
s = s.replace(includes, '\n'.join(guard), 1)
head, sep, body = s.partition('#endif // PS2X_ENABLE_DIAG_TAPS\n')
for ns, alias in NS.items():
    body = body.replace(ns + '::', alias + '::')
s = head + sep + body
left = re.findall(r'ps2_(?:e41|e43|e44|mpg_src)_trace::', body)
assert not left, f'{len(left)} unreplaced refs'
open(MAC, 'w').write(s)

c = open(CML).read()
anchor = 'if(PS2X_ENABLE_AGRESSIVE_LOGS)\n'
assert c.count(anchor) == 1
block = '''# N5: E40-E44 guest-memory watch taps in ps2_runtime_macros.h. OFF compiles
# them out of every generated function (speed builds); desktop dev keeps them.
if(ANDROID)
    set(PS2X_ENABLE_DIAG_TAPS_DEFAULT OFF)
else()
    set(PS2X_ENABLE_DIAG_TAPS_DEFAULT ON)
endif()
option(PS2X_ENABLE_DIAG_TAPS "Compile the E40-E44 guest-memory watch taps into the READ/WRITE macros" ${PS2X_ENABLE_DIAG_TAPS_DEFAULT})
if(PS2X_ENABLE_DIAG_TAPS)
    target_compile_definitions(ps2_runtime PUBLIC PS2X_ENABLE_DIAG_TAPS=1)
else()
    target_compile_definitions(ps2_runtime PUBLIC PS2X_ENABLE_DIAG_TAPS=0)
endif()

'''
c = c.replace(anchor, block + anchor, 1)
open(CML, 'w').write(c)
print('stubbed:', {NS[k]: v for k, v in used.items()})
