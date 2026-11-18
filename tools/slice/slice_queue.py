"""Slice the Bambu Studio projects listed in print-files/a1_ready/SLICE_QUEUE.json on a GitHub runner.

SLICE_QUEUE.json: {"jobs": [{"project": "D14_dock/D14_dock_plate1_dock.3mf", "layer": "0.20",
                             "over": {"wall_loops": 4, "sparse_infill_density": "25%"}}, ...]}
Each project is written next to itself as <name>.gcode.3mf (ready to send to the A1), the predicted time and
grams go into print-files/a1_ready/SLICED.json, and the queue is emptied. Uses the print repo's bambu3mf.slice_.
"""
import json, os, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b

A1 = os.path.join(ROOT, "print-files", "a1_ready")
qf = os.path.join(A1, "SLICE_QUEUE.json"); rf = os.path.join(A1, "SLICED.json")
q = json.load(open(qf)); res = json.load(open(rf)) if os.path.exists(rf) else {}
failed = 0
for j in q.get("jobs", []):
    src = os.path.join(A1, j["project"]); out = src[:-4] + ".gcode.3mf"
    r = b.slice_(src, out, j.get("layer", "0.20"), j.get("over", {}))
    r["when"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"); r["layer"] = j.get("layer", "0.20"); r["over"] = j.get("over", {})
    if r.get("ok"): r["hours"] = round(r["time_s"] / 3600, 2); r["file"] = os.path.relpath(out, A1)
    else: failed += 1
    res[j["project"]] = r
    print(j["project"], r, flush=True)
json.dump(res, open(rf, "w"), indent=1)
json.dump({"jobs": []}, open(qf, "w"), indent=1)
sys.exit(0)
