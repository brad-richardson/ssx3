"""E25 configure: the EXACT E18 recipe, asserted against E18's own receipt.

The argv is not retyped from the report prose -- it is LOADED from
`local/research/E18/configure-command.json` and compared field by field with
the literal list below. If they disagree the tool refuses: a rebuild that does
not use E18's flags is not the E18 recipe, and the brief forbids improvising.
"""
import subprocess
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
# Literal transcription of E18's recipe, kept so a silent edit to the receipt
# cannot pass unnoticed. Both must agree before a single byte is configured.
LITERAL = ['cmake', '-S', str(R), '-B', str(NEWB), '-G', 'Ninja',
           '-DCMAKE_BUILD_TYPE=Release',
           '-DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang',
           '-DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++',
           '-DCMAKE_OSX_ARCHITECTURES=arm64',
           '-DPS2X_BUILD_STUDIO=OFF', '-DPS2X_BUILD_RUNTIME=ON',
           '-DPS2X_BUILD_TEST=ON', '-DPS2X_ENABLE_RUNTIME_LOGS=ON',
           '-DPS2X_ENABLE_AGRESSIVE_LOGS=ON', '-DPS2X_ENABLE_IOP_RPC_TRACE=ON',
           '-DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF', '-DPS2X_ENABLE_FFMPEG=ON']
recorded = json.loads((E.parent / 'E18/configure-command.json').read_text())
assert recorded['argv'] == LITERAL, dict(recorded=recorded['argv'], literal=LITERAL)
assert recorded['jobs'] == 2, recorded

# E18 asserted a FRESH build directory. E25 rebuilds at the same path, which the
# host restart emptied, so the same assertion holds and is kept: configuring
# over a surviving tree would not be the E18 recipe.
assert not NEWB.exists(), f'{NEWB} exists -- refusing to configure over it'

save('configure-command.json', dict(argv=LITERAL, jobs=2,
    source='byte-equal to local/research/E18/configure-command.json; E18 recipe, E18 build directory',
    e18_receipt=recorded, argv_equal_e18=True, fresh_build_dir=True, utc=utc()))
raise SystemExit(subprocess.call(LITERAL))
