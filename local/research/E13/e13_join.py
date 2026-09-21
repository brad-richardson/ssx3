#!/usr/bin/env python3
"""Join the repaired live leaf/flag/state path and the observed graphics limits."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
from e13_closed_events import tap
from e13_io import read_capture
E=Path(__file__).resolve().parent;RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
def put(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    events,tail=tap(RUN/'e13a-join/e7-events.txt')
    summary=json.loads((E/'e13a-summary.json').read_text())
    card=json.loads((E/'e13a-card.json').read_text())
    frames=json.loads((E/'e13a-frame.json').read_text())
    progress=json.loads((E/'e13a-progress.json').read_text())
    assert len(summary['singleton'])==1 and summary['singleton'][0]['value']==0x61ba60
    c=summary['counter'];assert c['continuous'] and c['pre_matches'] and set(c['M'])=={'1'} and set(c['G'])=={'0'}
    assert set(c['pairs'])=={'(0, 112, 0, 112)'}
    assert card['query_calls']==card['query_returns'] and not card['unmatched_returns'] and not card['unclosed_calls'] and not card['nonreturn_exits']
    assert card['leaf_calls']==142 and all(p['exit']['v0']==1 for p in card['leaf_pairs'])
    assert all(p['exit']['v0']==0 for p in card['predicate_pairs'])
    assert not progress['damaged_missing'] and not progress['function_mismatches'] and not progress['function_live_stack']
    assert not any(r['target'] in ('0x2c5140','0x2c5300','0x2c5358') for r in progress['missing_groups'])
    stores=[r for r in card['ui_flag_writes'] if r['pc']==0x241d10]
    calculators=[p for p in card['flag_pairs'] if p['call']['target']==0x241b20]
    flagjoins=[]
    for p in calculators:
        a,b=p['call'],p['exit'];assert b['v0']==0 and p['guest_return']
        wrappers=[w for w in card['wrapper_pairs'] if a['seq']<w['call']['seq']<w['exit']['seq']<b['seq'] and w['call']['source']==0x241c3c]
        assert len(wrappers)==1;w=wrappers[0];assert w['exit']['v0']==1 and w['exit']['pc']==0x241c44
        leaves=[l for l in card['leaf_pairs'] if w['call']['seq']<l['call']['seq']<l['exit']['seq']<w['exit']['seq']]
        assert len(leaves)==1 and leaves[0]['exit']['v0']==1 and leaves[0]['exit']['pc']==0x2d3830
        store=next(s for s in stores if s['seq']>b['seq']);assert store['tick']==b['tick'] and store['old']==store['value']==0
        flagjoins.append(dict(tick=a['tick'],leaf=leaves[0],wrapper=w,calculator=p,store=store))
    assert len(flagjoins)==len(stores)==6
    route=next(p for p in card['state_routes'] if p['call']['source']==0x23e7e4)
    assert route['call']['target']==route['call']['uiRouteTarget']==0x23cf38 and route['call']['a1']==6
    assert route['call']['a0']==route['call']['UI'] and route['call']['uiState']==3 and route['exit']['uiState']==6 and route['guest_return']
    six=next(r for r in card['ui_state_writes'] if r['old']==3 and r['value']==6)
    assert route['call']['seq']<six['seq']<route['exit']['seq'] and six['pc']==0x23d3a0
    twenty_nine=next(r for r in card['ui_state_writes'] if r['old']==6 and r['value']==29)
    assert twenty_nine['pc']==0x23d54c
    copies=[]
    all_dma=[r for r in events if r['kind']=='gif-dma']
    for i,a in enumerate(all_dma):
        if a['source']!=0x4ffcc0:continue
        limit=all_dma[i+1]['seq'] if i+1<len(all_dma) else len(events)+1
        gs=[r for r in events if a['seq']<r['seq']<limit and r['kind']=='gs-enter' and r['bytes']==a['bytes'] and r['fnv64']==a['fnv64']]
        assert len(gs)==1 and a['bytes']==1696 and a['mask']==a['queued']==gs[0]['mask']==gs[0]['queued']==0
        copies.append(dict(dma=a,gs=gs[0]))
    assert len(copies)==206 and copies[-1]['dma']['tick']==248
    assert not summary['packets'] and not summary['boundary_events']
    arm=read_capture(RUN/'e13a-1/e4-vram-arm.bin');freeze=read_capture(RUN/'e13a-1/e4-vram-freeze.bin');assert arm==freeze
    assert frames['display']['rgb_nonblack']==frames['producer']['rgb_nonblack']==0
    assert frames['field_present_matches'] and all(r['matches'] for r in frames['field_present_matches']) and frames['host_latest_equals_expected_display_field']
    put('e13a-copy-content-join.json',dict(early_packet_hash_pairs=copies,consumed=206,
        early_packet_bytes_retained=False,boundary_packet_count=0,boundary_draw_count=0,
        full_content_join='unavailable: source/copy phase ended before fixed599..603 packet window; no new content claim',
        late_arm_equals_freeze=True,late_vram_sha256=hashlib.sha256(freeze).hexdigest(),
        late_source_and_display_black=True,late_field_present_exact=True,limits='Do not infer an early content join from identical packet FNV values or the later black image.'))
    put('e13a-request-join.json',dict(api_pairs=card['api_pairs'],api_counts=Counter(hex(p['call']['target']) for p in card['api_pairs']),pending_writes=card['pending_writes']))
    put('e13a-join.json',dict(dynamic_query_pairs=card['query_calls'],dynamic_predicate_pairs=card['predicate_calls'],dynamic_leaf_pairs=card['leaf_calls'],
        dynamic_wrapper_pairs=len(card['wrapper_pairs']),flagjoins=flagjoins,state6_route=route,state6_write=six,state29_write=twenty_nine,
        leaf_missing=0,query_missing=0,predicate_missing=0,copy_pairs=206,copy_last_tick=248,
        source_content_join_available=False,late_display_rgb_nonblack=0,late_present_exact=True,
        runtime_footer_present=False,observed_tail=tail,function_lines=progress['function_lines'],function_stack_closed=True))
    print('live leaf142/wrapper141; six exact leaf→wrapper→flags→store joins; state3→6→29')
    print('early packet→GS206/206; no fixed-boundary packet/content join; late black VRAM→Present exact')
    print('# E13 JOIN TAIL COMPLETE; absent footer/content retained as explicit limits')
if __name__=='__main__':main()
