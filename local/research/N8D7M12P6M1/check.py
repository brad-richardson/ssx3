#!/usr/bin/env python3
"""N8D7M12P6M1 acceptance checker: manifest-plan completeness, no build/device.

Reads REPORT.md in this dir. Verdict A = all rows pass. Writes
check-result.json. No device action.
"""
from pathlib import Path
import json
import re
import sys

here = Path(__file__).resolve().parent
report = here / "REPORT.md"
rows = []
fails = []

def row(name, ok, detail=""):
    rows.append({"check": name, "pass": bool(ok), "detail": detail})
    if not ok:
        fails.append(name)

text = report.read_text(errors="replace") if report.exists() else ""
if not report.exists():
    row("report_present", False, "REPORT.md missing")
else:
    row("report_present", True, f"{len(text)} chars")

PIN = "84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645"
APK = "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512"
RUNNER = "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d"
BID = "65ce162abca08d664223a362824b70c86aea6f4f"

row("p3_backend_pin_exact", PIN in text, "84a13a80…a4645 full SHA")
row("predecessor_disclaimed", "c6135b3c" in text and ("NOT" in text or "not" in text), "c6135b3c named as predecessor, not package source")
row("apk_pin", APK in text, "caa11102… member of table §1")
row("runner_pin", RUNNER in text, "329e44db… §1")
row("build_id_pin", BID in text, "65ce16… §1")

# Named categories from the brief
cats = {
    "cat_apk_native": [r"native-member|native member|libps2EntryRunner"],
    "cat_pinned_paths": [r"Currently pinned source paths|pinned source"],
    "cat_missing_glob": [r"Missing or ambiguous|missing/ambiguous"],
    "cat_link_evidence": [r"Enters link|enters the Android link|enters link: evidence"],
    "cat_next_action": [r"Next-build action|next.build|action needed"],
    "cat_fork": [r"gs_frontend|gs_worker|ps2_gs_parallel_backend|fork core"],
    "cat_renderer": [r"gs_renderer|gs_interface"],
    "cat_page_tracker": [r"page_tracker"],
    "cat_shaders": [r"shader|slangmosh|n8d5_tile"],
    "cat_granite": [r"Granite|memory_allocator"],
    "cat_flags": [r"Build flags|CMakeCache|build flag"],
    "cat_turnip_hal": [r"Turnip|jniLibs|libhardware|HAL"],
    "cat_graph": [r"Artifact graph|proven/planned/unknown|PROVEN|PLANNED|UNKNOWN"],
}
for name, pats in cats.items():
    ok = all(re.search(p, text, re.I) for p in pats)
    row(name, ok, " / ".join(pats))

# Exact-path / bounded-glob evidence for key missing inputs
for label, pat in [
    ("path_interface_cpp", r"gs/gs_interface\.cpp"),
    ("path_page_tracker", r"page_tracker\.cpp"),
    ("path_frontend", r"gs_frontend\.cpp"),
    ("path_worker", r"gs_worker\.cpp"),
    ("path_android_tu", r"ps2_android_runtime\.cpp"),
    ("path_kernel_glob", r"Kernel/\*\.cpp"),
    ("path_codegen_glob", r"GAME_CODEGEN_DIR/\*\.cpp|codegen.*GLOB|PS2X_GAME_SOURCES"),
    ("path_shader_glob", r"shaders/\*"),
]:
    row(label, re.search(pat, text) is not None, pat)

# No blanket historical-equivalence claim: report must carry an explicit denial
denial = re.search(r"No old APK is claimed to match|no blanket historical\s*equivalence", text, re.I)
row("no_blanket_equivalence_claim", denial is not None, "explicit denial present")
# And must not contain a positive equivalence assertion
bad = re.search(r"(matches|equals|identical to) (the |current )?(working )?trees?( build)?\b.{0,40}(apk|package)", text, re.I)
row("no_positive_equivalence_sentence", bad is None, bad.group(0) if bad else "none found")

out = {"verdict": "A" if not fails else "B", "rows": rows, "failing": fails,
       "note": "Manifest plan only; no build, device, or causal verdict."}
(here / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
sys.exit(0 if out["verdict"] == "A" else 1)
