#!/usr/bin/env python3
"""M9 replay-fidelity table from probe JSONLs (superset of M8 analyze.py).

Usage: analyze.py LABEL=path/to/probe.jsonl [LABEL=path ...]
Prints M8's tables unchanged, then M8 sections, then M9 sections: m9_meta
lines, VAT path tables, texgen enablement timelines, per-texgen type tables,
shared-reach histograms, xdiff distribution rows for delta runs.
Missing keys (earlier steps) print as n/a. No verdicts.
"""
import json
import re
import struct
import sys
from statistics import median


def f32(hexstr):
    try:
        return struct.unpack("<f", struct.pack("<I", int(hexstr, 16)))[0]
    except (ValueError, struct.error):
        return float("nan")


def pct(values, q):
    if not values:
        return float("nan")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


def load(path):
    rows, events = [], []
    with open(path, errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("{") or not line.endswith("}"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("event") != "replay":
                continue
            (rows if obj.get("action") == "capacity" else events).append(obj)
    return rows, events


def kv(detail, key, default=None):
    m = re.search(r"(?:^|\s)%s=([^\s]+)" % re.escape(key), detail or "")
    return m.group(1) if m else default


def summarise(label, path):
    rows, events = load(path)
    by_action = {}
    for e in events:
        by_action.setdefault(e["action"], []).append(e)
    first = lambda a: (by_action.get(a) or [{}])[0]
    recorded = first("recorded")
    done = first("done")
    changed = first("watched_window_changed")
    wall = [r["wall_ms"] for r in rows]
    cpu = [r["cpu_ms"] for r in rows if r.get("cpu_ms", -1) >= 0]
    phases = {}
    for key in ("mem_ms", "cp_ms", "pre_ms", "run_ms", "sync_ms"):
        got = [r[key] for r in rows if key in r]
        if got:
            phases[key] = (median(got), pct(got, 0.95))
    deltas = {}
    for key in ("dtex", "dpend", "dframe", "dafter", "dafter_live", "dpres", "dimx",
                "trig_imx", "xdiff", "xdmax", "xdmean", "pediff", "vidiff"):
        got = [r[key] for r in rows if key in r]
        if got:
            deltas[key] = (min(got), max(got))
    halves = {}
    for flag in (0, 1):
        got = [r["wall_ms"] for r in rows if r.get("xform") == flag]
        run = [r["run_ms"] for r in rows if r.get("xform") == flag and "run_ms" in r]
        if got:
            halves[flag] = {"n": len(got), "med": median(got), "p95": pct(got, 0.95),
                            "run_med": median(run) if run else None}
    trig = {}
    for r in rows:
        if "trig_imx" in r:
            trig[r["trig_imx"]] = trig.get(r["trig_imx"], 0) + 1
    out = {
        "label": label,
        "replays": len(rows),
        "wall_median": median(wall) if wall else None,
        "wall_p95": pct(wall, 0.95) if wall else None,
        "wall_min": min(wall) if wall else None,
        "wall_max": max(wall) if wall else None,
        "cpu_median": median(cpu) if cpu else None,
        "cpu_p95": pct(cpu, 0.95) if cpu else None,
        "frame_bytes": recorded.get("bytes"),
        "memory_updates": recorded.get("memory_updates"),
        "done": bool(done),
        "watched_window_changed": bool(changed),
        "seq_wall_ms": (done or changed or {}).get("detail", ""),
        "restored_detail": first("restored").get("detail", ""),
        "counters_detail": first("counters_summary").get("detail", ""),
        "events": [e["action"] for e in events],
        "phases": phases,
        "deltas": deltas,
        "xfb_equal": sum(1 for r in rows if r.get("xfb_equal") == 1),
        "xfb_scratch": sum(1 for r in rows if r.get("xfb_scratch") == 1),
        "has_xfb": any("xfb_equal" in r for r in rows),
        "has_scratch": any("xfb_scratch" in r for r in rows),
        "record_starts": [e.get("detail", "") for e in by_action.get("record_start", [])],
        "resume_xfbs": [e.get("detail", "") for e in by_action.get("resume_xfb", [])],
        "present_traces": [e.get("detail", "") for e in by_action.get("present_trace", [])],
        "xform_stats": [e.get("detail", "") for e in by_action.get("xform_stats", [])],
        "m8_metas": [e.get("detail", "") for e in by_action.get("m8_meta", [])],
        "m8_writes": [e.get("detail", "") for e in by_action.get("m8_writes", [])],
        "m8_reads": [e.get("detail", "") for e in by_action.get("m8_reads", [])],
        "m8_draws": [e.get("detail", "") for e in by_action.get("m8_draws", [])],
        "m8_expr": [[e.get("detail", "") for e in by_action.get(f"m8_expr{k}", [])]
                    for k in range(9)],
        "m9_metas": [e.get("detail", "") for e in by_action.get("m9_meta", [])],
        "m9_paths": [e.get("detail", "") for e in by_action.get("m9_path", [])],
        "m9_texens": [e.get("detail", "") for e in by_action.get("m9_texen", [])],
        "m9_texeps": [e.get("detail", "") for e in by_action.get("m9_texep", [])],
        "m9_vats": [e.get("detail", "") for e in by_action.get("m9_vat", [])],
        "m9_textypes": [e.get("detail", "") for e in by_action.get("m9_textype", [])],
        "m9_reachp": [e.get("detail", "") for e in by_action.get("m9_reachp", [])],
        "m9_reach": [[e.get("detail", "") for e in by_action.get(f"m9_reach{k}", [])]
                    for k in range(8)],
        "m9_survs": [e.get("detail", "") for e in by_action.get("m9_surv", [])],
        "m10_orders": [e.get("detail", "") for e in by_action.get("m10_order", [])],
        "m10_loads": [e.get("detail", "") for e in by_action.get("m10_loads", [])],
        "m10_conss": [e.get("detail", "") for e in by_action.get("m10_cons", [])],
        "m10_matrixs": [e.get("detail", "") for e in by_action.get("m10_matrix", [])],
        "m10_copys": [e.get("detail", "") for e in by_action.get("m10_copy", [])],
        "m10_occs": [e.get("detail", "") for e in by_action.get("m10_occ", [])],
        "m10_nops": [e.get("detail", "") for e in by_action.get("m10_nop", [])],
        "m10_rams": [e.get("detail", "") for e in by_action.get("m10_ram", [])],
        "m10_ref2s": [e.get("detail", "") for e in by_action.get("m10_ref2", [])],
        "m11_idxs": [e.get("detail", "") for e in by_action.get("m11_idx", [])],
        "m11_nops": [e.get("detail", "") for e in by_action.get("m11_nop", [])],
        "xdiff_rows": [(r.get("replay"), r.get("xdiff"), r.get("xdmax"), r.get("xdmean"))
                      for r in rows if "xdiff" in r],
        "halves": halves,
        "trig": trig,
        "record_flag_set": bool(by_action.get("record_flag_set")),
    }
    return out


def fmt(value, nd=3):
    return "n/a" if value is None else f"{value:.{nd}f}"


def main():
    results = []
    for arg in sys.argv[1:]:
        label, _, path = arg.partition("=")
        results.append(summarise(label or path, path))
    print("| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) "
          "| Frame B / updates | done | seq wall |")
    print("| --- | ---: | --- | --- | --- | :-: | --- |")
    for r in results:
        print(f"| {r['label']} | {r['replays']} | "
              f"{fmt(r['wall_median'])} / {fmt(r['wall_p95'])} / "
              f"{fmt(r['wall_min'])} / {fmt(r['wall_max'])} | "
              f"{fmt(r['cpu_median'])} / {fmt(r['cpu_p95'])} | "
              f"{r['frame_bytes']} / {r['memory_updates']} | "
              f"{'YES' if r['done'] else 'no'} | {r['seq_wall_ms']} |")
    print()
    print("| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) "
          "| sync_ms med | run_ms p95 |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in results:
        p = r["phases"]
        cell = lambda k, i=0: fmt(p[k][i]) if k in p else "n/a"  # noqa: E731
        print(f"| {r['label']} | {cell('mem_ms')} | {cell('cp_ms')} | {cell('pre_ms')} "
              f"| {cell('run_ms')} | {cell('sync_ms')} | {cell('run_ms', 1)} |")
    print()
    print("| Arm | xfb_copies | efb_total (non-XFB) | xfb range (addr, bytes) | ref_ok | "
          "scratch_ok (addr, patched) | xfb_equal | xfb_equal_scratch | live_xfb_untouched |")
    print("| --- | ---: | --- | --- | :-: | --- | --- | --- | :-: |")
    for r in results:
        rd, dd = r["restored_detail"], r["seq_wall_ms"]
        total, xfb = kv(rd, 'efb_total'), kv(rd, 'xfb_copies')
        try:
            nonx = str(int(total) - int(xfb))
        except (TypeError, ValueError):
            nonx = "n/a"
        print(f"| {r['label']} | {xfb or 'n/a'} | "
              f"{total or 'n/a'} ({nonx}) | "
              f"{kv(rd, 'xfb_addr', 'n/a')}, {kv(rd, 'xfb_bytes', 'n/a')} B | "
              f"{kv(rd, 'xfb_ref_ok', 'n/a')} | "
              f"{kv(rd, 'xfb_scratch_ok', 'n/a')} "
              f"({kv(rd, 'xfb_scratch_addr', 'n/a')}, {kv(rd, 'xfb_patch_n', 'n/a')}) | "
              f"{r['xfb_equal']}/{r['replays']} | "
              f"{r['xfb_scratch']}/{r['replays']} | "
              f"{kv(dd, 'live_xfb_untouched', 'n/a')} |")
    print()
    print("| Arm | counter | min | max |")
    print("| --- | --- | ---: | ---: |")
    for r in results:
        if r["deltas"]:
            for key in ("dtex", "dpend", "dframe", "dafter", "dafter_live", "dpres", "dimx",
                         "trig_imx", "xdiff", "xdmax", "xdmean", "pediff", "vidiff"):
                if key in r["deltas"]:
                    lo, hi = r["deltas"][key]
                    print(f"| {r['label']} | {key} | {lo} | {hi} |")
        else:
            print(f"| {r['label']} | (no delta keys) | n/a | n/a |")
    print()
    print("| Arm | xform=0 n | xform=0 wall med / p95 (ms) | xform=1 n "
          "| xform=1 wall med / p95 (ms) | xform=0 run_ms med | xform=1 run_ms med |")
    print("| --- | ---: | --- | ---: | --- | ---: | ---: |")
    for r in results:
        h = r["halves"]
        c0 = h.get(0, {})
        c1 = h.get(1, {})
        print(f"| {r['label']} | {c0.get('n', 'n/a')} | "
              f"{fmt(c0.get('med'))} / {fmt(c0.get('p95'))} | "
              f"{c1.get('n', 'n/a')} | "
              f"{fmt(c1.get('med'))} / {fmt(c1.get('p95'))} | "
              f"{fmt(c0.get('run_med'))} | {fmt(c1.get('run_med'))} |")
    print()
    print("| Arm | trig_imx=-1 | trig_imx=0 | trig_imx=1 |")
    print("| --- | ---: | ---: | ---: |")
    for r in results:
        t = r["trig"]
        if t:
            print(f"| {r['label']} | {t.get(-1, 0)} | {t.get(0, 0)} | {t.get(1, 0)} |")
        else:
            print(f"| {r['label']} | n/a | n/a | n/a |")
    print()
    for r in results:
        print(f"{r['label']}: events={r['events']}")
        if r["restored_detail"]:
            print(f"{r['label']}: restored detail = {r['restored_detail']}")
        if r["counters_detail"]:
            print(f"{r['label']}: counters_summary = {r['counters_detail']}")
        for d in r["record_starts"]:
            print(f"{r['label']}: record_start detail = {d}")
        for d in r["resume_xfbs"]:
            print(f"{r['label']}: resume_xfb detail = {d}")
        for d in r["present_traces"]:
            print(f"{r['label']}: present_trace detail = {d}")
        for d in r["xform_stats"]:
            print(f"{r['label']}: xform_stats detail = {d}")
        for d in r["m8_metas"]:
            print(f"{r['label']}: m8_meta detail = {d}")
        for d in r["m9_metas"]:
            print(f"{r['label']}: m9_meta detail = {d}")
        for d in r["m9_paths"]:
            print(f"{r['label']}: m9_path detail = {d}")
        for d in r["m9_texens"]:
            print(f"{r['label']}: m9_texen detail = {d}")
        for d in r["m9_texeps"]:
            print(f"{r['label']}: m9_texep detail = {d}")
        for d in r["m9_survs"]:
            print(f"{r['label']}: m9_surv detail = {d}")
        for d in r["m10_orders"]:
            print(f"{r['label']}: m10_order detail = {d}")
        for d in r["m10_loads"]:
            print(f"{r['label']}: m10_loads detail = {d}")
        for d in r["m10_conss"]:
            print(f"{r['label']}: m10_cons detail = {d}")
        for d in r["m10_matrixs"]:
            print(f"{r['label']}: m10_matrix detail = {d}")
        for d in r["m10_copys"]:
            print(f"{r['label']}: m10_copy detail = {d}")
        for d in r["m10_occs"]:
            print(f"{r['label']}: m10_occ detail = {d}")
        for d in r["m10_nops"]:
            print(f"{r['label']}: m10_nop detail = {d}")
        for d in r["m10_rams"]:
            print(f"{r['label']}: m10_ram detail = {d}")
        for d in r["m10_ref2s"]:
            print(f"{r['label']}: m10_ref2 detail = {d}")
        for d in r["m11_idxs"]:
            print(f"{r['label']}: m11_idx detail = {d}")
        for d in r["m11_nops"]:
            print(f"{r['label']}: m11_nop detail = {d}")
        if r["record_flag_set"]:
            print(f"{r['label']}: RECORD_FLAG_SET (sequence stopped early)")
        if r["watched_window_changed"]:
            print(f"{r['label']}: WATCHED WINDOW CHANGED")
    print()
    for r in results:
        if r["m8_writes"] or r["m8_reads"] or r["m8_draws"]:
            w = [int(x) for x in (r["m8_writes"] or [""])[0].split(",")] if r["m8_writes"] else [0] * 64
            rd = [int(x) for x in (r["m8_reads"] or [""])[0].split(",")] if r["m8_reads"] else [0] * 64
            dr = [int(x) for x in (r["m8_draws"] or [""])[0].split(",")] if r["m8_draws"] else [0] * 64
            n = r["replays"] or 1
            print(f"{r['label']}: slot census (writes/reads = sequence totals over "
                  f"{r['replays']} replays; draws = per-frame epoch attribution)")
            print("| slot | writes (tot) | writes/replay | reads (tot) | draws-affected |")
            print("| ---: | ---: | ---: | ---: | ---: |")
            zeros = 0
            for s in range(64):
                if w[s] == 0 and rd[s] == 0 and dr[s] == 0:
                    zeros += 1
                    continue
                print(f"| {s} | {w[s]} | {w[s] / n:.2f} | {rd[s]} | {dr[s]} |")
            print(f"{r['label']}: {zeros} slots all-zero (writes=reads=draws=0)")
            print(f"{r['label']}: writes total={sum(w)} reads total={sum(rd)} "
                  f"draws total={sum(dr)} (draws double-count multi-slot epochs)")
            names = ["PosNormal", "Tex0", "Tex1", "Tex2", "Tex3",
                     "Tex4", "Tex5", "Tex6", "Tex7"]
            for k in range(9):
                if r["m8_expr"][k]:
                    h = [int(x) for x in r["m8_expr"][k][0].split(",")]
                    nz = [(s, h[s]) for s in range(64) if h[s]]
                    cells = " ".join(f"{s}:{c}" for (s, c) in nz) or "(all zero)"
                    print(f"{r['label']}: expr {names[k]} draws by slot: {cells}")
            print()
    for r in results:
        if r["m9_paths"]:
            d = r["m9_paths"][0]
            ps, pi = kv(d, "pos_shared", "?"), kv(d, "pos_indexed", "?")
            print(f"{r['label']}: VAT path table (draws; shared vs indexed per expression)")
            print("| expr | shared | indexed | enabled | shared+enabled |")
            print("| --- | ---: | ---: | ---: | ---: |")
            tsh = (kv(d, "tex_shared", "") or "").split(",")
            tih = (kv(d, "tex_indexed", "") or "").split(",")
            ten = (kv(d, "tex_enabled", "") or "").split(",")
            tse = (kv(d, "tex_shared_enabled", "") or "").split(",")
            print(f"| Pos | {ps} | {pi} | n/a | n/a |")
            for i in range(8):
                gs = lambda a: a[i] if i < len(a) else "?"  # noqa: E731
                print(f"| Tex{i} | {gs(tsh)} | {gs(tih)} | {gs(ten)} | {gs(tse)} |")
            print()
        if r["m9_vats"]:
            print(f"{r['label']}: vat_hist draws per vat 0..7 = {r['m9_vats'][0]}")
            print()
        if r["m9_textypes"]:
            cells = [int(x) for x in r["m9_textypes"][0].split(",")]
            print(f"{r['label']}: texgen types per texgen (Regular/EmbossMap/Color0/Color1)")
            print("| texgen | Regular | EmbossMap | Color0 | Color1 |")
            print("| --- | ---: | ---: | ---: | ---: |")
            for t in range(8):
                row = cells[t * 4:(t + 1) * 4] if len(cells) >= (t + 1) * 4 else ["?"] * 4
                print(f"| Tex{t} | {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
            print()
        if r["m9_reachp"]:
            h = [int(x) for x in r["m9_reachp"][0].split(",")]
            nz = [(s, h[s]) for s in range(64) if h[s]]
            cells = " ".join(f"{s}:{c}" for (s, c) in nz) or "(all zero)"
            print(f"{r['label']}: shared-pos reach draws by slot: {cells}")
            print(f"{r['label']}: shared-pos reach total={sum(h)}")
            print()
        for t in range(8):
            if r["m9_reach"][t]:
                h = [int(x) for x in r["m9_reach"][t][0].split(",")]
                nz = [(s, h[s]) for s in range(64) if h[s]]
                cells = " ".join(f"{s}:{c}" for (s, c) in nz) or "(all zero)"
                print(f"{r['label']}: tex{t} shared+enabled reach draws by slot: {cells}")
        if r["m9_survs"]:
            d = r["m9_survs"][0]
            print(f"{r['label']}: survival trichotomy (post-replay values vs first-hit "
                  f"before/after; n={kv(d, 'n', '?')})")
            print("| sample | perturbed (==after) | pristine (==before) | other |")
            print("| --- | ---: | ---: | ---: |")
            for name, a, b, o in (("live xfmem", "xf_after", "xf_before", "xf_other"),
                                  ("per-vertex snapshot", "pv_after", "pv_before", "pv_other"),
                                  ("shared-pos snapshot", "pos_after", "pos_before", "pos_other"),
                                  ("shared-tex snapshot", "tex_after", "tex_before", "tex_other")):
                print(f"| {name} | {kv(d, a, '?')} | {kv(d, b, '?')} | {kv(d, o, '?')} |")
            print(f"{r['label']}: shared residency: pos_res={kv(d, 'pos_res', '?')} "
                  f"tex_res={kv(d, 'tex_res', '?')} dirty_post={kv(d, 'dirty_post', '?')} "
                  f"zfreeze={kv(d, 'zfreeze', '?')}")
        print()
    for r in results:
        if r["m10_orders"]:
            d = r["m10_orders"][0]
            print(f"{r['label']}: hit/draw order table")
            print("| field | value |")
            print("| --- | --- |")
            for key in ("slot", "word", "draws", "verts", "idx_loads", "covering",
                        "idx_cover", "direct_cover", "arr12", "arr13", "arr14",
                        "arr15", "first_load_draw", "first_load_off",
                        "first_load_kind", "last_load_draw", "last_load_off",
                        "cons_pos", "cons_tex", "cons_any", "first_cons",
                        "last_cons", "cons_before_first", "cons_at_after_first",
                        "loads_before_first", "loads_first_to_lastcons",
                        "seam_hits", "seam_per_replay", "walk", "benign",
                        "walk_ok"):
                print(f"| {key} | {kv(d, key, '?')} |")
            print()
        if r["m10_loads"]:
            cells = r["m10_loads"][0].split(",") if r["m10_loads"][0] else []
            trunc = cells[-1] if cells and cells[-1].startswith("TRUNC=") else None
            vals = cells[:-1] if trunc else cells
            print(f"{r['label']}: covering-load draw clocks n={len(vals)}"
                  + (f" ({trunc})" if trunc else ""))
            print(f"{r['label']}: first 30 = {','.join(vals[:30])}")
            if len(vals) > 30:
                print(f"{r['label']}: last 10 = {','.join(vals[-10:])}")
            print()
        if r["m10_conss"]:
            cells = r["m10_conss"][0].split(",") if r["m10_conss"][0] else []
            trunc = cells[-1] if cells and cells[-1].startswith("TRUNC=") else None
            vals = cells[:-1] if trunc else cells
            print(f"{r['label']}: consuming draw indices n={len(vals)}"
                  + (f" ({trunc})" if trunc else ""))
            print(f"{r['label']}: first 30 = {','.join(vals[:30])}")
            if len(vals) > 30:
                print(f"{r['label']}: last 10 = {','.join(vals[-10:])}")
            print()
        if r["m10_matrixs"]:
            d = r["m10_matrixs"][0]
            lists = {}
            for tag in ("before", "after", "live", "snap"):
                raw = kv(d, tag, "")
                lists[tag] = raw.split(",") if raw else []
            try:
                w0 = int(kv(d, "slot", "0")) * 4
            except ValueError:
                w0 = 0
            print(f"{r['label']}: 12-word matrix table (slot {kv(d, 'slot', '?')} "
                  f"words {w0}..{w0 + 11}; done={kv(d, 'done', '?')} "
                  f"snap_which={kv(d, 'snap_which', '?')} "
                  f"snap_ti={kv(d, 'snap_ti', '?')} n={kv(d, 'n', '?')} "
                  f"mm_live={kv(d, 'mm_live', '?')} mm_snap={kv(d, 'mm_snap', '?')})")
            print("| i | word | before hex | before float | after hex | after float "
                  "| post-live hex | post-live float | post-snap hex | post-snap float |")
            print("| ---: | ---: | --- | ---: | --- | ---: | --- | ---: | --- | ---: |")
            for i in range(12):
                row = []
                for tag in ("before", "after", "live", "snap"):
                    hx = lists[tag][i] if i < len(lists[tag]) else "?"
                    row += [hx, f"{f32(hx):.6g}" if hx != "?" else "?"]
                print(f"| {i} | {w0 + i} | {row[0]} | {row[1]} | {row[2]} | {row[3]} "
                      f"| {row[4]} | {row[5]} | {row[6]} | {row[7]} |")
            print()
    for r in results:
        if r["m10_copys"]:
            d = r["m10_copys"][0]
            print(f"{r['label']}: EFB-copy table (compared xfb={kv(d, 'xfb', '?')})")
            print("| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |")
            print("| ---: | ---: | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |")
            body = d.split(" ", 2)
            recs = body[2].split(";") if len(body) > 2 and body[2] else []
            for i, rec in enumerate(recs):
                g = lambda k: kv(rec.replace(",", " "), k, "?")  # noqa: E731
                print(f"| {i} | {g('draw')} | {g('dest')} | {g('bytes')} | "
                      f"{g('xfb')} | {g('clear')} | {g('tl')} | {g('w')} | {g('h')} "
                      f"| {g('ovl')} |")
            print()
        if r["m10_occs"]:
            d = r["m10_occs"][0]
            print(f"{r['label']}: occlusion/render-target class table "
                  f"(cons={kv(d, 'cons', '?')} all={kv(d, 'all_draws', '?')} "
                  f"ncopy={kv(d, 'ncopy', '?')})")
            print("| class | consuming draws |")
            print("| --- | ---: |")
            for key in ("culled", "outrange", "inrange"):
                print(f"| {key} | {kv(d, key, '?')} |")
            print(f"{r['label']}: cull reasons (consuming; non-disjoint): "
                  f"cull_all={kv(d, 'cull_all', '?')} "
                  f"scis_empty={kv(d, 'scis_empty', '?')} "
                  f"znever={kv(d, 'znever', '?')}")
            print(f"{r['label']}: cull reasons (all draws): "
                  f"all_cull={kv(d, 'all_cull', '?')} "
                  f"all_scis={kv(d, 'all_scis', '?')} "
                  f"all_znever={kv(d, 'all_znever', '?')}")
            ep = (kv(d, "epoch_cons", "") or "").split(",")
            clocks = []
            if r["m10_copys"]:
                body = r["m10_copys"][0].split(" ", 2)
                recs = body[2].split(";") if len(body) > 2 and body[2] else []
                for rec in recs:
                    try:
                        clocks.append(int(kv(rec.replace(",", " "), "draw", "0")))
                    except ValueError:
                        clocks.append(0)
            try:
                total = int(kv(r["m10_orders"][0], "draws", "0")) if r["m10_orders"] else 0
            except ValueError:
                total = 0
            print(f"{r['label']}: epoch table (draw ranges from copy clocks + draws={total})")
            print("| epoch | draw range | cons draws | closing copy |")
            print("| ---: | --- | ---: | --- |")
            prev = 0
            for e in range(len(clocks) + 1):
                cur = clocks[e] if e < len(clocks) else total
                cell = ep[e] if e < len(ep) else "?"
                close = f"copy {e}" if e < len(clocks) else "tail (none)"
                print(f"| {e} | {prev + 1}..{cur} | {cell} | {close} |")
                prev = cur
            print()
        if r["m10_nops"]:
            d = r["m10_nops"][0]
            print(f"{r['label']}: NOP-collective receipt: nop={kv(d, 'nop', '?')} "
                  f"ok={kv(d, 'ok', '?')} draws={kv(d, 'draws', '?')} "
                  f"bytes={kv(d, 'bytes', '?')}")
            print()
        if r["m10_rams"]:
            d = r["m10_rams"][0]
            print(f"{r['label']}: RAM-copy flag receipt: ram={kv(d, 'ram', '?')} "
                  f"skipx_pre={kv(d, 'skipx_pre', '?')} "
                  f"skipe_pre={kv(d, 'skipe_pre', '?')} "
                  f"defer_pre={kv(d, 'defer_pre', '?')} "
                  f"skipx_post={kv(d, 'skipx_post', '?')} "
                  f"skipe_post={kv(d, 'skipe_post', '?')} "
                  f"defer_post={kv(d, 'defer_post', '?')}")
            print()
        if r["m10_ref2s"]:
            d = r["m10_ref2s"][0]
            print(f"{r['label']}: true-delta (ref2) table: ref={kv(d, 'ref', '?')} "
                  f"kref={kv(d, 'kref', '?')} refok={kv(d, 'refok', '?')} "
                  f"refhash={kv(d, 'refhash', '?')}")
            print("| field | value |")
            print("| --- | --- |")
            for key in ("n2", "gt0", "uniform2", "xd2min", "xd2max",
                        "xdmax2max", "xdmean2min", "xdmean2max", "samp"):
                print(f"| {key} | {kv(d, key, '?')} |")
            print()
        if r["m11_idxs"]:
            d = r["m11_idxs"][0]
            print(f"{r['label']}: indexed-path decode table (slot {kv(d, 'slot', '?')})")
            print("| field | value |")
            print("| --- | --- |")
            for key in ("idx_pos_draws", "idx_pos_verts", "exp_draws",
                        "exp_verts", "tex_draws", "tex_exp_draws"):
                print(f"| {key} | {kv(d, key, '?')} |")
            print()
        if r["m11_nops"]:
            d = r["m11_nops"][0]
            print(f"{r['label']}: M11 partition-NOP receipt: shr={kv(d, 'shr', '?')} "
                  f"idx={kv(d, 'idx', '?')} text={kv(d, 'text', '?')} "
                  f"ok={kv(d, 'ok', '?')} "
                  f"draws={kv(d, 'draws', '?')} bytes={kv(d, 'bytes', '?')}")
            print()
    for r in results:
        if r["xdiff_rows"]:
            nz = [(rp, xd, xm, xn) for (rp, xd, xm, xn) in r["xdiff_rows"] if (xd or 0) > 0]
            print(f"{r['label']}: xdiff>0 replays = {len(nz)}/{len(r['xdiff_rows'])}")
            for (rp, xd, xm, xn) in nz[:20]:
                print(f"{r['label']}: replay {rp}: xdiff={xd} xdmax={xm} xdmean={xn}")
            if len(nz) > 20:
                print(f"{r['label']}: ... and {len(nz) - 20} more differing replays")


if __name__ == "__main__":
    main()
