"""Log the rider position (EE 0x5409c0) at ~10 Hz to a JSONL file for N seconds.

Usage: track_position.py LOG.jsonl [SECONDS]
"""
import sys, time, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pine import Pine
ADDR=0x5409c0; TARGET=(-103508.68,37805.40,-220359.04)
out=open(sys.argv[1],'a'); seconds=float(sys.argv[2]) if len(sys.argv)>2 else 30
p=Pine(); t0=time.time()
while time.time()-t0<seconds:
    x,y,z=p.read_floats(ADDR,3)
    d=math.dist((x,y),TARGET[:2])
    out.write(json.dumps(dict(t=round(time.time()-t0,2),x=round(x,1),y=round(y,1),z=round(z,1),dxy=round(d,1)))+'\n'); out.flush()
    time.sleep(0.1)
