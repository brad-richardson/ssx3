#!/usr/bin/env python3
"""E55D14P2B narrow checker: receipt counts/pairing and caps for the one S1 run.

Reads the private lane ~/dev/ssx3-work/E55D14P2/run/S1 plus committed paths.
Asserts: exact 9-pulse pad route, five getdir status rows + five getdirpath
siblings paired by per-family ordinal/tick/port/slot/max (NOT global seq),
post-choice path fields, zero mcread, empty cards unchanged, frame proof,
and log/frames caps. Exits nonzero on any FAIL.
"""
import json
import os
import re
import sys

LANE = "/Users/brad/dev/ssx3-work/E55D14P2/run/S1"
PASS = 0
FAIL = 0


def check(name, cond, detail: object = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"ok {name} {detail}")
    else:
        FAIL += 1
        print(f"FAIL {name} {detail}")


rj = json.load(open(os.path.join(LANE, "result.json")))
check("result_bound_target", rj.get("bound") == "target", rj.get("bound"))
check("result_last_tick_ge_1800", rj.get("last_hash_tick", 0) >= 1800,
      rj.get("last_hash_tick"))
fp = rj.get("frame_proof", {})
check("frame_proof_tick_ge_1800", fp.get("tick", 0) >= 1800, fp)
check("frame_proof_file_exists",
      os.path.isfile(os.path.join(LANE, "frames", "snap", fp.get("file", ""))),
      fp.get("file"))
check("route_exact_nine",
      rj.get("route") == "10611:start:250,13680:square:150,16683:down:150,"
      "17851:down:150,19019:down:150,20187:down:150,22689:cross:150,"
      "25692:down:150,28362:cross:150", "")
check("cards_empty_unchanged",
      rj.get("card_initial_files") == {"mc0": [], "mc1": []}
      and rj.get("card_final_files") == {"mc0": [], "mc1": []}
      and rj.get("card_initial_sha256") == rj.get("card_final_sha256")
      == "f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce",
      rj.get("card_final_sha256"))
check("caps_wall_plus_grace_le_600",
      rj.get("wall_cap_s") == 500 and rj.get("frame_proof_grace_s") == 100, "")
check("caps_log_bytes", rj.get("log_bytes", 2 ** 99) <= 16777216,
      rj.get("log_bytes"))
check("caps_frames_bytes", rj.get("frames_bytes", 2 ** 99) <= 2147483648,
      rj.get("frames_bytes"))
check("caps_probe_bytes", rj.get("probe_bytes", 2 ** 99) <= 16777216,
      rj.get("probe_bytes"))
for key, pin in {
        "runner": "d8fa114d824a277592558425dd91357bcf2f75d0d09390a5680c41ba6002ef04",
        "iso": "3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5",
        "elf": "1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc",
        "codegen": "8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3",
}.items():
    got = (rj.get("sha_reads") or [{}, {}])[0].get(
        {"runner": rj["runner"], "iso": rj["iso"], "elf": rj["elf"],
         "codegen": rj["codegen"]}[key], "")
    check(f"pin_{key}", got == pin, got[:12])
    got2 = (rj.get("sha_reads") or [{}, {}])[1].get(
        {"runner": rj["runner"], "iso": rj["iso"], "elf": rj["elf"],
         "codegen": rj["codegen"]}[key], "")
    check(f"pin_{key}_second_read", got2 == pin, got2[:12])

boot = open(os.path.join(LANE, "boot.log")).read().splitlines()
presses = [l for l in boot if "[padscript] press" in l]
releases = [l for l in boot if "[padscript] release" in l]
check("pad_nine_presses", len(presses) == 9, len(presses))
check("pad_nine_releases", len(releases) == 9, len(releases))
m = [re.search(r"buttons=(0x[0-9a-fA-F]+)", l) for l in presses]
check("pad_masks_all_present", all(m), "")
masks = [x.group(1) for x in m if x]
check("pad_order_masks", masks == ["0x0008", "0x8000", "0x0040", "0x0040",
                                   "0x0040", "0x0040", "0x4000", "0x0040",
                                   "0x4000"], masks)
check("pad_armed_once",
      sum(1 for l in boot if "[padscript] armed n=9" in l) == 1, "")

probe = open(os.path.join(LANE, "probe.log")).read().splitlines()
gd = [l for l in probe if l.startswith("getdir ")]
gp = [l for l in probe if l.startswith("getdirpath ")]
mc = [l for l in probe if l.startswith("mcread ")]
check("probe_getdir_five", len(gd) == 5, len(gd))
check("probe_getdirpath_five", len(gp) == 5, len(gp))
check("probe_mcread_zero", len(mc) == 0, len(mc))


def fields(line):
    return dict(re.findall(r"(\w+)=(\"[^\"]*\"|\S+)", line))


for i, (a, b) in enumerate(zip(gd, gp), 1):
    fa, fb = fields(a), fields(b)
    check(f"pair{i}_ord_pord", fa.get("ord") == fb.get("pord") == str(i),
          f"ord={fa.get('ord')} pord={fb.get('pord')}")
    for k in ("vsync", "port", "slot", "max"):
        check(f"pair{i}_{k}", fa.get(k) == fb.get(k),
              f"getdir={fa.get(k)} path={fb.get(k)}")
    check(f"pair{i}_status_empty",
          fa.get("ok") == "0" and "empty" in fa.get("reason", ""), a[:90])

early_ticks = [fields(l).get("vsync") for l in gd[:4]]
check("early_ticks_118_122_126_223", early_ticks == ["118", "122", "126", "223"],
      early_ticks)
post = fields(gd[4])
check("post_tick_1740", post.get("vsync") == "1740", post.get("vsync"))
check("post_addr_distinct",
      post.get("addr") == "0x00ba5b20"
      and all(fields(l).get("addr") == "0x00b85660" for l in gd[:4]),
      post.get("addr"))
pp = fields(gp[4])
check("post_path_raw", pp.get("raw") == '"BASLUS-20772-GAM*"', pp.get("raw"))
check("post_path_query", pp.get("query") == '"/BASLUS-20772-GAM*"',
      pp.get("query"))
check("post_path_parent", pp.get("parent") == '""', pp.get("parent"))
check("post_path_pattern", pp.get("pattern") == '"BASLUS-20772-GAM*"',
      pp.get("pattern"))
check("post_path_host_mc0", (pp.get("host") or "").strip('"').endswith(
    "/E55D14P2/run/S1/mc0"), pp.get("host"))
for j in range(4):
    q = fields(gp[j])
    check(f"early{j + 1}_has_path_fields",
          all(q.get(k) for k in ("raw", "query", "pattern", "host")), "")

print(f"{PASS} PASS, {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
