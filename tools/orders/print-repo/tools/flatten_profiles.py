"""Rebuild profiles/process_0xx.json, machine.json and pla_basic.json from a Bambu Studio install.
Only needed when moving to a newer Bambu Studio. Usage: BAMBU_STUDIO_DIR=... python tools/flatten_profiles.py"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bambu3mf import PROFILES, bambu_dir  # noqa: E402

BBL = os.path.join(bambu_dir(), "resources", "profiles", "BBL")
_idx = {}
for sub in ("machine", "process", "filament"):
    for f in glob.glob(os.path.join(BBL, sub, "**", "*.json"), recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if "name" in d:
            _idx[(sub, d["name"])] = d


def flat(sub, name):
    d = _idx[(sub, name)]
    out = dict(flat(sub, d["inherits"])) if d.get("inherits") else {}
    out.update(d)
    return out


def write(sub, name, fn):
    d = flat(sub, name); d["inherits"] = ""; d["from"] = "system"
    json.dump(d, open(os.path.join(PROFILES, fn), "w"), indent=1)


if __name__ == "__main__":
    if not _idx:
        sys.exit("No Bambu profiles found under %s" % BBL)
    write("machine", "Bambu Lab A1 0.4 nozzle", "machine.json")
    write("filament", "Bambu PLA Basic @BBL A1", "pla_basic.json")
    for fn, n in (("process_012.json", "0.12mm Fine @BBL A1"), ("process_016.json", "0.16mm Optimal @BBL A1"),
                  ("process_020.json", "0.20mm Standard @BBL A1")):
        write("process", n, fn)
    print("profiles rebuilt in", PROFILES)
