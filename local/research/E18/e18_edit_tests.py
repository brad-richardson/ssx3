from e18_common import *
import gzip
assert os.environ.get('COPYFILE_DISABLE')=='1'
p=R/'ps2xTest/src/ps2_runtime_expansion_tests.cpp'
before=p.read_text();assert before==gzip.decompress((E/'sources/before-ps2_runtime_expansion_tests.cpp.gz').read_bytes()).decode()
s=sample();admission(s);save('admission-before-tests.json',s)
helper=(E/'e18_test_helpers.cpp').read_text();payload=(E/'regression-frames.m2v').read_bytes();assert len(payload)==240
rows=['            '+', '.join(f'0x{x:02X}u' for x in payload[i:i+12])+',' for i in range(0,len(payload),12)]
helper=helper.replace('@@FRAMES@@','\n'.join(rows));(E/'e18_test_helpers.cpp').write_text(helper)
marker='    void testRecordMpegStreamCallback('
assert before.count(marker)==1
text=before.replace(marker,helper+marker)
marker='        tc.Run("sceSdRemote isolates voice transfers from block streaming state",'
assert text.count(marker)==1
text=text.replace(marker,(E/'e18_test_cases.cpp').read_text()+marker)
p.write_text(text)
save('test-edit.json',dict(utc=utc(),file=pin(p),added_cases=6,old_source_preserved=before==text.replace(helper,'').replace((E/'e18_test_cases.cpp').read_text(),'')))
print('TEST EDIT COMPLETE 6 cases old source byte-preserved')
