import json,sys
def rate(path,lo=1800,hi=2400):
    pts=[json.loads(l) for l in open(path)]
    def t_at(tick):
        # linear interpolate wall at tick
        prev=None
        for p in pts:
            if p["tick"]>=tick:
                if prev is None or p["tick"]==prev["tick"]: return p["wall_s"]
                f=(tick-prev["tick"])/(p["tick"]-prev["tick"])
                return prev["wall_s"]+f*(p["wall_s"]-prev["wall_s"])
            prev=p
    a,b=t_at(lo),t_at(hi)
    return (hi-lo)/(b-a)
for d in sys.argv[1:]:
    r=rate(d+"/trace.jsonl"); print(f"{d}: race t1800-2400 {r:.2f} vsyncs/s = {r/59.94:.3f}x")
