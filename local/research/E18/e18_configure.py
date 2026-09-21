import subprocess
from e18_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert not NEWB.exists()
argv=['cmake','-S',str(R),'-B',str(NEWB),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang','-DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++','-DCMAKE_OSX_ARCHITECTURES=arm64','-DPS2X_BUILD_STUDIO=OFF','-DPS2X_BUILD_RUNTIME=ON','-DPS2X_BUILD_TEST=ON','-DPS2X_ENABLE_RUNTIME_LOGS=ON','-DPS2X_ENABLE_AGRESSIVE_LOGS=ON','-DPS2X_ENABLE_IOP_RPC_TRACE=ON','-DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF','-DPS2X_ENABLE_FFMPEG=ON']
save('configure-command.json',dict(argv=argv,source='Exact E17 flags with a fresh E18 build directory; no code generator',jobs=2))
raise SystemExit(subprocess.call(argv))
