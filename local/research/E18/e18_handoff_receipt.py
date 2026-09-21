from e18_common import *
m=json.loads((E/'e18a-mpeg.json').read_text());c=json.loads((E/'e18a-observation-closure.json').read_text());g=json.loads((E/'e18a-graphics.json').read_text());end=json.loads((E/'e18a-result.json').read_text())
assert c['source_footer'] and not c['missing_pair_ids'] and not c['mismatched_pairs']
assert len(m['objects'])==1;o=m['objects'][0];assert len(o['callbacks'])==len(o['selections'])==len(o['add_bs'])==1
assert o['callbacks'][0]['thread_matches'] and o['callbacks'][0]['stack_matches']
assert len(o['callbacks'][0]['add_bs_inside_observed_scope'])==1
assert o['requested_bytes']==o['returned_add_bs_bytes']==5040 and not o['completion_events']
main=next(t for t in m['park']['threads'] if t['id']==1);assert main['pc']=='0x3b1028' and main['wait_reason_name']=='Mpeg'
logs=[r for r in m['boot_observations'] if '[MPEG:' in r['text']]
assert any('parsed=5040 packets=0 newFrames=0 totalFrames=0' in x['text'] for x in logs)
assert any('ended=0 failed=0 sawInput=1' in x['text'] for x in logs)
r=dict(utc=utc(),boot_count=1,result=end,closure=c['closure'],shutdown=c['shutdown'],source_count_match=True,dynamic_mpeg=o['mpeg'],callback_delivery=1,add_bs_delivery_bytes=5040,callback_return_v0=o['callbacks'][0]['callback']['exit']['v0'],valid_no_input_returns=0,completion_events=0,main=main,graphics_guard=g['object_guard'],graphics_join=g['positive_packet_source_display_present_join'],
 first_missing_edge='Accepted initial input -> complete parser packet / decoded frame -> GetPicture wake: 5040 bytes consumed, 0 packets, 0 frames, no second callback/input/completion observed; request remains in typed MPEG wait.',
 first_edge_evidence=logs,
 distinction='FFmpeg-enabled host parser buffered the initial input; decoderFailed=0. No decode-error or EOF claim. Callback delivery is observed; completion is absent.',
 stop='No second behavior change, decoder edit, EOF inference, scheduler change, or guest-gate bypass after this observation.',
 followup='Name the initial-input / further-input request dependency before implementing another fix. Preserve valid-no-input wait and callback v0-discard ABI. I-lane S9 rebuild/reinstall/90s probe remains their separate brief.',
 payload_limit='E15 retained first64 bytes and FNV64 over all5040 input bytes; complete guest payload was not separately dumped.')
save('boot-analysis-summary.json',r)
print('STOP EDGE RECEIPT COMPLETE: callback1/AddBs5040/packets0/frames0/completion0; source counters close')
