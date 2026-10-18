"""Check a Track 3 submission zip offline: which routes the server will accept.

    python tools/check_submission.py submission.zip

Runs the same per-route checks as the CodaBench scoring program: the record
(``res/<route>_res.json``) must be a finished leaderboard record of that route,
and it must agree with the per-tick ego state (``viz/<route>/.../metric_info.json``,
the lexicographically last one). A route that fails a check counts as failed
on the server (DS 0 on B2D-C, every instruction failed on CARLA-F). For each
invalid route the script prints the reason the server reports and how to fix it.

It does not compute the scores. Exit status 0 if every scored route is valid,
1 otherwise. Requires Python >= 3.7 and no other package; reads the routes and
their dense routes (``routes/<benchmark>/dense/``) of this repository.
"""

import argparse
import json
import math
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

TRACK_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = (("carla_f", "CARLA-F"), ("b2d_c", "B2D-C"))

# ---------------------------------------------------------------- checks of the scoring program (keep in sync)
INFRA_FAILURES = ("Simulation crashed", "Agent's sensors were invalid", "Agent couldn't be set up", "Agent crashed")
# Not scored: the route turns at a junction that also has a straight exit while the
# active instruction says to keep straight, so the turn is never announced.
EXCLUDED_CARLA_F = (
    "bench2drive_193_language_rebuilt_turn_left",
    "bench2drive_193_language_rebuilt_turn_straight",
    "bench2drive_198_language_rebuilt_turn_right",
    "bench2drive_202_language_rebuilt_turn_left",
    "bench2drive_211_language_rebuilt_lane_follow",
)
PENALTIES = (
    ("collisions_pedestrian", 0.5), ("collisions_vehicle", 0.6), ("collisions_layout", 0.65),
    ("red_light", 0.7), ("stop_infraction", 0.8), ("scenario_timeouts", 0.7),
    ("yield_emergency_vehicle_infractions", 0.7),
)
SIM_DT_S = 0.05
RC_TOLERANCE = 1.0
DURATION_TOLERANCE_S = 0.5
MAX_STEP_M = 2.0
START_TOLERANCE_M = 2.0
EGO_EVENT_TOLERANCE_M = 1.0
SIGN_EVENT_TOLERANCE_M = 30.0
EGO_EVENTS = ("collisions_pedestrian", "collisions_vehicle", "collisions_layout", "route_dev", "vehicle_blocked")
SIGN_EVENTS = ("red_light", "stop_infraction")
LOCATION_RE = re.compile(r"x=(-?[\d.]+), y=(-?[\d.]+), z=(-?[\d.]+)")
PERCENT_RE = re.compile(r"\((-?[\d.]+)% of the completed route\)")


def load_trajectory(viz_dir):
    """(tick ids, ego positions) of the latest attempt (lexicographically last metric_info.json)."""
    if not viz_dir.is_dir():
        return None, "no metric_info.json"
    runs = sorted(viz_dir.rglob("metric_info.json"), key=lambda p: p.relative_to(viz_dir).as_posix())
    if not runs:
        return None, "no metric_info.json"
    try:
        info = json.loads(runs[-1].read_text())
        frames = sorted((int(k), v["location"]) for k, v in info.items())
        ticks = [k for k, _ in frames]
        traj = [(float(l[0]), float(l[1]), float(l[2])) for _, l in frames]
    except Exception as e:  # malformed file
        return None, "unreadable metric_info.json (%s)" % type(e).__name__
    if len(traj) < 2:
        return None, "metric_info.json has fewer than 2 ticks"
    if any(math.isnan(v) or math.isinf(v) for p in traj for v in p):
        return None, "metric_info.json has non-finite positions"
    return (ticks, traj), None


def load_record(res_path, route_id):
    """The leaderboard record of a route, or (None, reason)."""
    if not res_path.is_file():
        return None, "missing %s" % res_path.name
    try:
        data = json.loads(res_path.read_text())
        progress = data["_checkpoint"]["progress"]
        records = data["_checkpoint"].get("records", [])
    except Exception:
        return None, "unreadable %s" % res_path.name
    if len(progress) < 2 or progress[0] < progress[1] or not records:
        return None, "route not finished"
    if any(token in rec.get("status", "") for rec in records for token in INFRA_FAILURES):
        return None, "infrastructure failure: %s" % records[-1].get("status", "")
    expected = "RouteScenario_%s" % route_id
    matching = [r for r in records if r.get("route_id", "") == expected or r.get("route_id", "").startswith(expected + "_rep")]
    if not matching:
        return None, "record is of route %s, expected %s" % (records[-1].get("route_id"), expected)
    return matching[-1], None


def replay_route_completion(dense, traj):
    """RouteCompletionTest.update() of Bench2Drive replayed over the ego positions."""
    acc = [0.0]
    for p, q in zip(dense[:-1], dense[1:]):
        acc.append(acc[-1] + math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 + (q[2] - p[2]) ** 2))
    perc = [a / acc[-1] * 100 for a in acc] if acc[-1] > 0 else [100.0] * len(acc)
    index, value, target = 0, 0.0, dense[-1]
    for x, y, z in traj:
        for i in range(index, min(index + 3, len(dense))):
            r = dense[i]
            if (x - r[0]) * r[3] + (y - r[1]) * r[4] + (z - r[2]) * r[5] > 0:
                index, value = i, perc[i]
        value = round(value, 2)
        if value > 90 and math.sqrt((x - target[0]) ** 2 + (y - target[1]) ** 2 + (z - target[2]) ** 2) < 10:
            return 100.0
    return value


def verify(record, ticks, traj, dense):
    """First inconsistency between the record and the per-tick ego state, or None."""
    if any(b - a != 1 for a, b in zip(ticks[:-1], ticks[1:])):
        return "metric_info.json skips ticks"
    if math.hypot(traj[0][0] - dense[0][0], traj[0][1] - dense[0][1]) > START_TOLERANCE_M:
        return "trajectory does not start at the start of the route"
    step = max(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(traj[:-1], traj[1:]))
    if step > MAX_STEP_M:
        return "trajectory jumps %.1f m in one tick" % step
    duration = float((record.get("meta") or {}).get("duration_game", -1))
    if abs(len(traj) * SIM_DT_S - duration) > DURATION_TOLERANCE_S:
        return "trajectory lasts %.2f s, the record %.2f s" % (len(traj) * SIM_DT_S, duration)
    scores = record.get("scores") or {}
    try:
        score_route, score_penalty, score_composed = (float(scores[k]) for k in ("score_route", "score_penalty", "score_composed"))
    except Exception:
        return "record has no scores"
    replayed = replay_route_completion(dense, traj)
    if abs(replayed - score_route) > RC_TOLERANCE:
        return "route completion is %.2f%% in the trajectory, %.2f%% in the record" % (replayed, score_route)
    infractions = record.get("infractions") or {}
    penalty = 1.0
    for key, factor in PENALTIES:
        penalty *= factor ** len(infractions.get(key) or [])
    for message in infractions.get("outside_route_lanes") or []:
        match = PERCENT_RE.search(str(message))
        if match is None:
            return "outside_route_lanes event without a percentage"
        penalty *= 1 - float(match.group(1)) / 100  # the message rounds p to 0.01
    if abs(round(penalty, 6) - score_penalty) > 2e-4 or abs(round(max(score_route * score_penalty, 0.0), 6) - score_composed) > 1e-3:
        return "scores of the record do not follow from its route completion and infractions"
    num_infractions = sum(len(v or []) for v in infractions.values())
    expected_status = ("Completed" if num_infractions else "Perfect") if score_route >= 100 else "Failed"
    if not str(record.get("status", "")).startswith(expected_status):
        return "status '%s' does not match the record" % record.get("status")
    for key in EGO_EVENTS + SIGN_EVENTS:
        tolerance = EGO_EVENT_TOLERANCE_M if key in EGO_EVENTS else SIGN_EVENT_TOLERANCE_M
        for message in infractions.get(key) or []:
            match = LOCATION_RE.search(str(message))
            if match is None:
                return "%s event without a location" % key
            ex, ey = float(match.group(1)), float(match.group(2))
            if min(math.hypot(p[0] - ex, p[1] - ey) for p in traj) > tolerance:
                return "%s event is not on the trajectory" % key
    return None


def find_submission_root(res_dir):
    """The folder holding carla_f/ and b2d_c/ (the zip root or one level below)."""
    candidates = [res_dir] + sorted(p for p in res_dir.iterdir() if p.is_dir() and not p.name.startswith(("__MACOSX", ".")))
    for c in candidates:
        if (c / "carla_f").is_dir() or (c / "b2d_c").is_dir():
            return c
    for c in sorted(res_dir.rglob("*")):
        if c.is_dir() and c.name in ("carla_f", "b2d_c"):
            return c.parent
    return res_dir


# ---------------------------------------------------------------- how to fix
LOG_EVERY_TICK = ("save self.get_metric_info() at every tick of the run, as _log_metric_info of "
                  "team_code/agent_safedrive.py does, then rerun the route")
RERUN_CLEANLY = ("delete this route's old outputs (res/<route>_res.json and viz/<route>/) and rerun it, "
                 "so that the record and metric_info.json come from the same attempt")
FIXES = (
    ("missing ", "run this route (scripts/eval.sh resumes unfinished routes), then pack again with tools/pack_submission.py"),
    ("unreadable metric_info.json", "the file is damaged; " + RERUN_CLEANLY),
    ("unreadable ", "the record is not valid JSON; " + RERUN_CLEANLY),
    ("route not finished", "the leaderboard stopped before the end of the route; rerun it (the evaluation resumes unfinished routes)"),
    ("infrastructure failure", "CARLA or the agent crashed; " + RERUN_CLEANLY),
    ("record is of route", "this _res.json belongs to another route; check that every route writes its own result file, then pack again"),
    ("no metric_info.json", LOG_EVERY_TICK),
    ("metric_info.json has fewer than 2 ticks", LOG_EVERY_TICK),
    ("metric_info.json has non-finite positions", "the logged ego state contains NaN or inf; " + RERUN_CLEANLY),
    ("metric_info.json skips ticks", "some agent steps were not logged; log at every run_step, including steps that "
                                     "return early (e.g. the braking frames at the start)"),
    ("trajectory does not start", "metric_info.json is from another route, or logging began after the car moved; "
                                  "log from the first tick and " + RERUN_CLEANLY),
    ("trajectory jumps", "every entry must be the ego state of that tick: call get_metric_info() anew at every tick "
                         "(do not reuse or copy a previous entry) and run the agent at every tick, then rerun the route"),
    ("trajectory lasts", "metric_info.json and the record come from different attempts (e.g. an older attempt's "
                         "metric_info.json sorts last); " + RERUN_CLEANLY),
    ("route completion is", "the record does not match the logged trajectory: the files come from different attempts, "
                            "or metric_info.json is not the per-tick ego state; " + RERUN_CLEANLY),
    (" event is not on the trajectory", "an infraction of the record is not on the logged trajectory: the files come from "
                                        "different attempts, or metric_info.json is not the per-tick ego state; " + RERUN_CLEANLY),
)
RECORD_EDITED = ("the record differs from what the leaderboard writes; submit the _res.json written by the leaderboard, "
                 "unmodified (rerun the route if it is damaged)")


def fix_for(reason):
    for prefix, fix in FIXES:
        if reason.startswith(prefix) or (prefix.startswith(" ") and prefix in reason):
            return fix
    return RECORD_EDITED  # scores, status or event messages that do not follow the leaderboard's format


def held_state_note(sub_dir, name):
    """A hint if the ego state is repeated over many ticks (the state was not logged every tick)."""
    loaded, _ = load_trajectory(sub_dir / "viz" / name)
    if loaded is None:
        return None
    traj = loaded[1]
    changes = sum(1 for p, q in zip(traj[:-1], traj[1:]) if p != q)
    if changes and len(traj) / changes >= 5:
        return "the logged position changes only every %.0f ticks on average (%d changes in %d ticks)" % (
            len(traj) / changes, changes, len(traj))
    return None


# ---------------------------------------------------------------- main
def check(sub_dir, routes_dir, key):
    """[(route name, route id, valid, reason)] of every scored route of one benchmark."""
    rows = []
    for xml in sorted((routes_dir / key).glob("*.xml")):
        if key == "carla_f" and xml.stem in EXCLUDED_CARLA_F:
            continue
        route_id = ET.parse(str(xml)).getroot().find(".//route").attrib["id"]
        dense_path = routes_dir / key / "dense" / ("%s.json" % xml.stem)
        if not dense_path.is_file():
            sys.exit("%s not found; update your copy of the track3 repository" % dense_path)
        record, reason = load_record(sub_dir / "res" / ("%s_res.json" % xml.stem), route_id)
        if record is not None:
            loaded, reason = load_trajectory(sub_dir / "viz" / xml.stem)
            if loaded is not None:
                reason = verify(record, loaded[0], loaded[1], json.loads(dense_path.read_text()))
        rows.append((xml.stem, route_id, reason is None, reason))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("submission", type=Path, help="the submission zip")
    parser.add_argument("--routes-dir", type=Path, default=TRACK_ROOT / "routes", help="routes/ of the track3 repository")
    args = parser.parse_args()
    if not zipfile.is_zipfile(str(args.submission)):
        sys.exit("%s is not a zip file" % args.submission)

    with tempfile.TemporaryDirectory(prefix="track3_check_") as tmp:
        with zipfile.ZipFile(str(args.submission)) as z:
            z.extractall(tmp)
        sub = find_submission_root(Path(tmp))
        results, invalid = {}, []
        for key, title in BENCHMARKS:
            if not (sub / key).is_dir():
                print("WARNING: the zip has no %s/ folder; all %s routes count as failed" % (key, title))
            results[key] = check(sub / key, args.routes_dir, key)
            for name, route_id, valid, reason in results[key]:
                if not valid:
                    invalid.append((title, name, route_id, reason, held_state_note(sub / key, name)))

    for key, title in BENCHMARKS:
        rows = results[key]
        note = " (%d more routes are not scored)" % len(EXCLUDED_CARLA_F) if key == "carla_f" else ""
        print("%-8s %d / %d routes valid%s" % (title, sum(r[2] for r in rows), len(rows), note))
    if not invalid:
        print("All scored routes are valid.")
        return 0
    print("\n%d invalid route(s); each counts as failed on the server:" % len(invalid))
    for title, name, route_id, reason, note in invalid:
        print("\n  %s %s  (route id %s)" % (title, name, route_id))
        print("    reason: %s" % reason)
        if note:
            print("            %s" % note)
        print("    fix:    %s" % fix_for(reason))
    return 1


if __name__ == "__main__":
    sys.exit(main())
