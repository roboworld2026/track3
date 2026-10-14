"""Pack the evaluation outputs of the 80 track routes into a CodaBench submission.

    python tools/pack_submission.py \
        --carla-f ../safedrive-vla/work_dirs/track3/carla_f \
        --b2d-c ../safedrive-vla/work_dirs/track3/b2d_c \
        -o submission.zip

Each input is an output directory of ``tools/run_distributed_eval.py`` (or of
``scripts/eval.sh``) of the SafeDriveVLA repository:

    <dir>/res/<route>_res.json             leaderboard record of each route
    <dir>/viz/<route>/.../metric_info.json per-tick ego state of each attempt

The zip holds, for every route, the record and the per-tick ego state of its
latest attempt (the lexicographically last ``metric_info.json``):

    carla_f/res/<route>_res.json    carla_f/viz/<route>/metric_info.json    (40 routes)
    b2d_c/res/<route>_res.json      b2d_c/viz/<route>/metric_info.json      (40 routes)

The script refuses to pack while a route is missing or unfinished; pass
``--allow-incomplete`` to submit anyway (such routes count as failed).
Requires Python >= 3.7 and no other package.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

TRACK_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = (("carla_f", "CARLA-F"), ("b2d_c", "B2D-C"))
INFRA_FAILURES = ("Simulation crashed", "Agent's sensors were invalid", "Agent couldn't be set up", "Agent crashed")
SIM_DT_S = 0.05


def check_route(out_dir, name, route_id):
    """(res path, metric_info path, problem or None) of one route."""
    res = out_dir / "res" / ("%s_res.json" % name)
    viz = out_dir / "viz" / name
    runs = sorted(viz.rglob("metric_info.json"), key=lambda p: p.relative_to(viz).as_posix()) if viz.is_dir() else []
    info = runs[-1] if runs else None
    if not res.is_file():
        return None, info, "no result file"
    try:
        checkpoint = json.loads(res.read_text())["_checkpoint"]
        progress, records = checkpoint["progress"], checkpoint.get("records", [])
    except Exception:
        return res, info, "unreadable result file"
    if len(progress) < 2 or progress[0] < progress[1] or not records:
        return res, info, "route not finished"
    status = records[-1].get("status", "")
    if any(token in status for token in INFRA_FAILURES):
        return res, info, "infrastructure failure (%s); rerun the route" % status
    if not records[-1].get("route_id", "").startswith("RouteScenario_%s" % route_id):
        return res, info, "record of another route (%s)" % records[-1].get("route_id")
    if info is None:
        return res, None, "no metric_info.json; save get_metric_info() every tick"
    try:
        ticks = sorted(int(k) for k in json.loads(info.read_text()))
    except Exception:
        return res, info, "unreadable metric_info.json"
    if any(b - a != 1 for a, b in zip(ticks[:-1], ticks[1:])):
        return res, info, "metric_info.json skips ticks; save get_metric_info() every tick"
    duration = float(records[-1].get("meta", {}).get("duration_game", -1))
    if abs(len(ticks) * SIM_DT_S - duration) > 0.5:
        return res, info, ("metric_info.json covers %.1f s but the route ran %.1f s; is it from another attempt?"
                           % (len(ticks) * SIM_DT_S, duration))
    return res, info, None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--carla-f", type=Path, required=True, help="output directory of the CARLA-F routes")
    parser.add_argument("--b2d-c", type=Path, required=True, help="output directory of the B2D-C routes")
    parser.add_argument("--routes-dir", type=Path, default=TRACK_ROOT / "routes", help="routes/ of the track3 repository")
    parser.add_argument("-o", "--output", type=Path, default=Path("submission.zip"))
    parser.add_argument("--allow-incomplete", action="store_true", help="pack even if routes are missing (they count as failed)")
    args = parser.parse_args()

    entries, problems = [], []
    for key, title in BENCHMARKS:
        out_dir = getattr(args, key)
        xmls = sorted((args.routes_dir / key).glob("*.xml"))
        if not xmls:
            sys.exit("no route files in %s" % (args.routes_dir / key))
        ok = 0
        for xml in xmls:
            route_id = ET.parse(str(xml)).getroot().find(".//route").attrib["id"]
            res, info, problem = check_route(out_dir, xml.stem, route_id)
            if problem:
                problems.append("%s %s: %s" % (title, xml.stem, problem))
            else:
                ok += 1
            if res is not None:
                entries.append((res, "%s/res/%s" % (key, res.name)))
            if info is not None:
                entries.append((info, "%s/viz/%s/metric_info.json" % (key, xml.stem)))
        print("%-8s %d / %d routes complete  (%s)" % (title, ok, len(xmls), out_dir))
    if problems:
        print("\n".join("  " + p for p in problems))
        if not args.allow_incomplete:
            sys.exit("Not packed: fix the routes above, or pass --allow-incomplete (they count as failed).")
    with zipfile.ZipFile(str(args.output), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src, arcname in entries:
            z.writestr(arcname, json.dumps(json.loads(src.read_text()), separators=(",", ":")))
    print("wrote %s (%.1f MB, %d files)" % (args.output, args.output.stat().st_size / 1e6, len(entries)))


if __name__ == "__main__":
    main()
