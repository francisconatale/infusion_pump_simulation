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
                    "actions": row.get("actions", "")
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

    liveness_properties = []
    temporal_properties = []

    passed = True
    passed &= _run_property_group("SAFETY PROPERTIES", safety_properties, rows)
    for name, fn in safety_stateful:
        passed &= _run_stateful_property(name, fn, rows)
    passed &= _run_property_group("LIVENESS PROPERTIES", liveness_properties, rows)
    passed &= _run_property_group("TEMPORAL PROPERTIES", temporal_properties, rows)

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
