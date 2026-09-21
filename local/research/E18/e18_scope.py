import gzip,subprocess,sys
from e18_common import *
label=sys.argv[1]
mp=R/'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp';tp=R/'ps2xTest/src/ps2_runtime_expansion_tests.cpp'
before=gzip.decompress((E/'sources/before-MPEG.cpp.gz').read_bytes()).decode();after=mp.read_text()
def segment(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
checks=[]
for start,end in [('        std::vector<MpegRegisteredCallback> matchingStreamCallbacks(', '        void queueStreamCallbackEvent('),('        void dispatchGuestStreamCallback(', '        void dispatchStreamCallbacks(')]:
    original=segment(before,start,end)
    # New non-stream helpers are adjacent to, never edits within, either stream helper.
    first='        std::vector<MpegRegisteredCallback> matchingNonStreamCallbacks(' if 'matchingStream' in start else '        void dispatchGuestNonStreamCallback('
    retained=segment(after,start,first)
    assert original==retained
    checks.append(dict(start=start.strip(),byte_equal=True,bytes=len(original.encode()),sha256=hashlib.sha256(original.encode()).hexdigest()))
oldtest=gzip.decompress((E/'sources/before-ps2_runtime_expansion_tests.cpp.gz').read_bytes()).decode()
assert oldtest==tp.read_text().replace((E/'e18_test_helpers.cpp').read_text(),'').replace((E/'e18_test_cases.cpp').read_text(),'')
allowed=[str(mp.relative_to(R)),str(tp.relative_to(R))]
changed=subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).splitlines();assert sorted(changed)==sorted(allowed),changed
fixed=[]
for p in json.loads((E/'checkpoint.json').read_text())['inputs_sources']:
    if p['path'] not in (str(mp),str(tp)):assert sha(p['path'])==p['sha256'],p['path'];fixed.append(p['path'])
save(label+'-scope.json',dict(utc=utc(),changed=changed,stream_implementation=checks,all_prior_test_bytes_equal=True,unchanged_pinned_inputs=fixed,source=[pin(mp),pin(tp)],allocation=sample()))
print('SCOPE COMPLETE: MPEG.cpp + expansion tests only; stream functions and old tests byte-identical')
