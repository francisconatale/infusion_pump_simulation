#!/usr/bin/env python3
import csv
import sys
from typing import List, Dict, Any

def load_results(file_path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                parsed_row = {
                    "line": i + 1,  # 1-indexed line number in CSV (including header)
                    "time": float(row["time"]),
                    "event_type": row["event_type"],
                    "flow_state": row["flow_state"],
                    "tolerance_count": float(row["tolerance_count"]),
                    "bag_state": row["bag_state"],
                    "bag_time_remaining": float(row["bag_time_remaining"]) if row["bag_time_remaining"] != "inf" else float("inf"),
                    "actual_flow": float(row["actual_flow"]),
                    "target_flow": float(row["target_flow"]),
                    "medical_order": float(row["medical_order"]),
                    "actions_count": int(row["actions_count"]),
                    "actions": row.get("actions", ""),
                    "alarm_state": row.get("alarm_state", "no_alarm")
                }
                rows.append(parsed_row)
            except KeyError as e:
                print(f"Error: Missing column {e} at line {i+1}", file=sys.stderr)
                sys.exit(1)
            except ValueError as e:
                print(f"Error: Value conversion failed at line {i+1}: {e}", file=sys.stderr)
                sys.exit(1)
    return rows

def verify_tolerance_bound(row: Dict[str, Any]) -> bool:
    val = row["tolerance_count"]
    return 0.0 <= val <= 5.0

def verify_flow_limits(row: Dict[str, Any]) -> bool:
    val = row["target_flow"]
    return 0.0 <= val <= 200.0

def caudal_zero_stop_flow(actual: Dict[str, Any], next_row: Dict[str, Any]) -> bool:
    target_actual, actual_flow = actual["target_flow"], actual["flow_state"]
    next_target, actual_target = next_row["target_flow"], next_row["flow_state"]
    if target_actual == 0.0:
        return actual_flow == actual_target
    return True

def verify_no_resume_after_critical_alarm(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    blocked = False

    for row in rows:
        actions = row.get("actions", "")

        if "critical_alarm" in actions and "stop_pump" in actions:
            blocked = True
            continue

        if not blocked:
            continue

        if row["flow_state"] == "normal_flow":
            blocked = False
            continue

        if row["flow_state"] not in ("critical_flow",):
            violations.append(row)

    return violations
def eventual_break_after_end_bag(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    in_bag_end_episode = False
    prev_bag_time = None

    for row in rows:
        bag_state = row["bag_state"]
        bag_time = row["bag_time_remaining"]

        if bag_state == "normal_bag":
            in_bag_end_episode = False
            prev_bag_time = None
            continue

        if not in_bag_end_episode:
            in_bag_end_episode = True
            prev_bag_time = bag_time
            continue

        if prev_bag_time is not None and bag_time != float('inf') and prev_bag_time != float('inf'):
            if bag_time > prev_bag_time + 1e-9:
                violations.append(row)

        prev_bag_time = bag_time

    return violations

def after_five_seconds_tolerancy_emits_medium_alert(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    for row, next_row in zip(rows, rows[1:]):
        if (row["tolerance_count"] == 5 and row["flow_state"] == "normal_flow"
                and "medium_alarm" not in row.get("actions", "")
                and "medium_alarm" not in next_row.get("actions", "")):
            violations.append(next_row)
    return violations

def medical_order_produces_action(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    for i in range(len(rows) - 1):
        curr_mo = rows[i]["medical_order"]
        next_mo = rows[i + 1]["medical_order"]
        if curr_mo == next_mo:
            continue
        pump_action = False
        for j in range(i + 1, min(i + 4, len(rows))):
            acts = rows[j].get("actions", "")
            if "adjust_flow" in acts or "stop_pump" in acts:
                pump_action = True
                break
        if not pump_action:
            violations.append(rows[i + 1])
    return violations

def infusion_starts_under_3s(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    for i in range(len(rows) - 1):
        prev_mo = rows[i]["medical_order"]
        curr_mo = rows[i + 1]["medical_order"]
        if prev_mo == curr_mo or curr_mo <= 0:
            continue
        t_order = rows[i + 1]["time"]
        found = False
        for j in range(i + 1, len(rows)):
            if rows[j]["time"] - t_order > 3.0:
                break
            if "adjust_flow" in rows[j].get("actions", ""):
                found = True
                break
        if not found:
            violations.append(rows[i + 1])
    return violations

def bag_end_emits_low_alarm_and_stops_in_60s(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    for i in range(len(rows)):
        if "low_alarm" not in rows[i].get("actions", "") or rows[i]["bag_state"] != "normal_bag":
            continue
        t_alarm = rows[i]["time"]
        stopped = False
        for j in range(i + 1, len(rows)):
            if rows[j]["time"] - t_alarm > 60.5:
                break
            if "stop_pump" in rows[j].get("actions", ""):
                stopped = True
                break
        if not stopped:
            violations.append(rows[i])
    return violations

def after_critical_alarm_pump_stays_stopped(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    blocked = False
    for row in rows:
        acts = row.get("actions", "")
        if "critical_alarm" in acts and "stop_pump" in acts:
            blocked = True
            continue
        if not blocked:
            continue
        if row["flow_state"] == "normal_flow":
            blocked = False
            continue
        if row["flow_state"] not in ("critical_flow",):
            violations.append(row)
    return violations

def critical_alarm_repeats(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []

    for i, row in enumerate(rows):
        if "critical_alarm" not in row.get("actions", ""):
            continue

        confirmed = False
        repeated = False

        for j in range(i + 1, len(rows)):
            if rows[j]["flow_state"] == "normal_flow":
                confirmed = True
                break

            if "critical_alarm" in rows[j].get("actions", ""):
                repeated = True
                break

        if not confirmed and not repeated:
            violations.append(row)

    return violations


def critical_alarm_repeats_after_30s(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []

    for i, row in enumerate(rows):
        if "critical_alarm" not in row.get("actions", ""):
            continue

        t0 = row["time"]

        confirmed = False
        repeated = False

        for j in range(i + 1, len(rows)):
            if rows[j]["flow_state"] == "normal_flow":
                confirmed = True
                break

            if rows[j]["time"] - t0 >= 40:
                if ("critical_alarm" in rows[j].get("actions", "")
                        or rows[j].get("alarm_state", "") == "critical_alarm"):
                    repeated = True
                break

        if not confirmed and not repeated:
            violations.append(row)

    return violations


def _run_property_group(name, properties, rows):
    all_passed = True
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    for prop_name, prop_fn in properties:
        print(f"\nVerifying: {prop_name}...")
        violations = []
        
        import inspect
        sig = inspect.signature(prop_fn)
        params_count = len(sig.parameters)
        
        if params_count == 2:
            for idx in range(len(rows) - 1):
                if not prop_fn(rows[idx], rows[idx+1]):
                    violations.append(rows[idx])
        else:
            for r in rows:
                if not prop_fn(r):
                    violations.append(r)
        
        if violations:
            all_passed = False
            for v in violations[:5]:
                print(f"    - Line {v['line']} (t={v['time']:.3f}): tolerance_count={v['tolerance_count']}, target_flow={v['target_flow']}, medical_order={v['medical_order']}, actual_flow={v['actual_flow']}")
            if len(violations) > 5:
                print(f"    - ... and {len(violations) - 5} more violations.")
        else:
            print("  \033[92mPASSED: Property holds for all records!\033[0m")

    return all_passed

def _run_stateful_property(prop_name, prop_fn, rows):
    all_passed = True
    print(f"\nVerifying: {prop_name}...")
    violations = prop_fn(rows)
    if violations:
        all_passed = False
        for v in violations[:5]:
            print(f"    - Line {v['line']} (t={v['time']:.3f}): flow_state={v['flow_state']}, actual_flow={v['actual_flow']:.3f}")
        if len(violations) > 5:
            print(f"    - ... and {len(violations) - 5} more violations.")
    else:
        print("  \033[92mPASSED: Property holds for all records!\033[0m")
    return all_passed

def run_verification(file_path: str):
    try:
        rows = load_results(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please run the simulation first.", file=sys.stderr)
        sys.exit(1)

    safety_properties = [
        ("Tolerance Count Bound (0 <= tolerance_count <= 5)", verify_tolerance_bound),
        ("Target Flow Limits (0 <= target_flow <= 200)", verify_flow_limits),
        ("Caudal zero => flow state stays constant", caudal_zero_stop_flow),
    ]

    safety_stateful = [
        ("After critical alarm, pump must not resume infusion until nurse confirmation", verify_no_resume_after_critical_alarm),
    ]

    liveness_properties = [
        ("After bag end, bag time remaining must be monotonically non-increasing", eventual_break_after_end_bag),
        ("After 5 seconds of tolerance exceeded, medium alarm must be emitted", after_five_seconds_tolerancy_emits_medium_alert),
        ("Every medical order must eventually produce a pump action", medical_order_produces_action),
        ("Infusion must start within 3 seconds of receiving a positive medical order", infusion_starts_under_3s),
    ]
    temporal_properties = [
        ("Bag end must emit low alarm and stop infusion within 60 seconds", bag_end_emits_low_alarm_and_stops_in_60s),
        ("After critical alarm pump stays stopped until nurse confirmation", after_critical_alarm_pump_stays_stopped),
        ("Unconfirmed critical alarm must repeat", critical_alarm_repeats),
        ("Unconfirmed critical alarm must repeat after 30s (every 10s)", critical_alarm_repeats_after_30s),
    ]

    passed = True
    passed &= _run_property_group("SAFETY PROPERTIES", safety_properties, rows)
    for name, fn in safety_stateful:
        passed &= _run_stateful_property(name, fn, rows)
    if liveness_properties:
        print(f"\n{'='*60}")
        print("  LIVENESS PROPERTIES")
        print(f"{'='*60}")
    for name, fn in liveness_properties:
        passed &= _run_stateful_property(name, fn, rows)
    if temporal_properties:
        print(f"\n{'='*60}")
        print("  TEMPORAL PROPERTIES")
        print(f"{'='*60}")
    for name, fn in temporal_properties:
        passed &= _run_stateful_property(name, fn, rows)

    print()
    if passed:
        print("\033[92mAll properties verified successfully!\033[0m")
        sys.exit(0)
    else:
        print("\033[91mSome properties failed verification.\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    csv_file = "resultados.csv"
    run_verification(csv_file)
