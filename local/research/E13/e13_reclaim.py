#!/usr/bin/env python3
"""E13-only oldest-first link-tree reclamation with a retained ownership gate."""
import argparse,datetime,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
E=Path(__file__).resolve().parent;TMP=Path('/private/tmp');W=Path('/Volumes/Extreme SSD/ps2recomp-spike')
ADMISSION=3489660928;TARGET=ADMISSION+512*1024**2
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def cmd(argv):
    p=subprocess.run(argv,capture_output=True,text=True)
    return dict(argv=argv,rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['probe','remove']);ap.add_argument('tree');args=ap.parse_args()
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    checkpoint=json.loads((E/'checkpoint.json').read_text())
    assert checkpoint['matching_generated_names_hashes']==9451 and checkpoint['binding_present_rc']==1
    assert args.tree.endswith('-link') and '/' not in args.tree and args.tree!='p1-link'
    p=TMP/args.tree;assert p.parent==TMP and not p.is_symlink() and p.is_dir() and p.stat().st_uid==os.getuid()
    inventory=json.loads((E/'reclamation-inventory.json').read_text())
    remaining=[r for r in inventory if not r['protected'] and Path(r['path']).exists()]
    assert remaining[0]['path']==str(p),'Must handle oldest remaining eligible tree first'
    if args.mode=='probe':
        rec=dict(tree=str(p),utc=utc(),before_free=shutil.disk_usage(TMP).free,df_before=cmd(['df','-k',str(W),str(TMP)]),target=TARGET,admission=ADMISSION)
        rec['board']=cmd(['herdr','api','snapshot']);assert rec['board']['rc']==0
        snapshot=json.loads(rec['board']['stdout'])['result']['snapshot']
        agents=snapshot['agents'];rec['live_agents']=[{k:r.get(k) for k in ['pane_id','name','agent_status','cwd','foreground_cwd']} for r in agents]
        # Names and cwd are checked independently of fresh peer-pane claims.
        stem=args.tree.removesuffix('-link').lower()
        rec['board_claims']=[r for r in rec['live_agents'] if str(r.get('name') or '').lower()==stem or any(str(p) in str(v) or str(p).replace('/private/tmp','/tmp') in str(v) for v in r.values())]
        rec['peer_claim_files']={}
        for q in sorted(E.glob('board-*.txt')):
            rec['peer_claim_files'][q.name]=dict(sha256=hashlib.sha256(q.read_bytes()).hexdigest(),tree_mentioned=args.tree in q.read_text())
        rec['cache']=(p/'runtime/CMakeCache.txt').read_text()
        rec['cache_identity']=[s for s in rec['cache'].splitlines() if s.startswith(('CMAKE_HOME_DIRECTORY:','CMAKE_CACHEFILE_DIR:','CMAKE_PROJECT_NAME:'))]
        files=allocated=logical=links=0
        for directory,dirs,names in os.walk(p,followlinks=False):
            for name in names:
                q=Path(directory)/name;s=q.lstat();files+=1;allocated+=s.st_blocks*512;logical+=s.st_size;links+=q.is_symlink()
        rec['tree_size']=dict(files=files,logical=logical,allocated=allocated,file_symlinks=links)
        rec['lsof']=cmd(['/usr/sbin/lsof','-nP','+D',str(p)])
        rec['ownership_proved']=not rec['board_claims'] and not any(r['tree_mentioned'] for r in rec['peer_claim_files'].values()) and rec['lsof']['rc']==1 and not rec['lsof']['stdout'] and not rec['lsof']['stderr']
        rec['probe_complete_utc']=utc()
        (E/f'reclaim-{args.tree}-proof.json').write_text(json.dumps(rec,indent=2)+'\n')
        print(json.dumps({k:v for k,v in rec.items() if k not in ['board','cache']},indent=2));assert rec['ownership_proved']
    else:
        rec=json.loads((E/f'reclaim-{args.tree}-proof.json').read_text());assert rec['ownership_proved']
        before=shutil.disk_usage(TMP).free
        if before>=TARGET:
            print('Admission plus headroom already available; no deletion.');return
        # Recheck board identities and handles immediately before the scoped removal.
        board=cmd(['herdr','api','snapshot']);assert board['rc']==0
        now=json.loads(board['stdout'])['result']['snapshot']['agents']
        old=json.loads(rec['board']['stdout'])['result']['snapshot']['agents']
        keys=['pane_id','name','cwd','foreground_cwd'];assert [{k:r.get(k) for k in keys} for r in now]==[{k:r.get(k) for k in keys} for r in old]
        handles=cmd(['/usr/sbin/lsof','-nP','+D',str(p)]);assert handles['rc']==1 and not handles['stdout'] and not handles['stderr']
        result=dict(tree=str(p),utc=utc(),board_recheck=board,lsof_recheck=handles,df_before=cmd(['df','-k',str(W),str(TMP)]),free_before=shutil.disk_usage(TMP).free)
        # No symlink traversal. Explicit, previously proved single tree only.
        shutil.rmtree(p)
        result.update(removed=not p.exists(),free_after=shutil.disk_usage(TMP).free,df_after=cmd(['df','-k',str(W),str(TMP)]),end_utc=utc())
        result['reclaimed_free_delta']=result['free_after']-result['free_before'];result['target_met']=result['free_after']>=TARGET
        (E/f'reclaim-{args.tree}-removal.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='board_recheck'},indent=2))
    print('# E13 RECLAMATION TAIL COMPLETE '+args.mode+' '+args.tree)
if __name__=='__main__':main()
